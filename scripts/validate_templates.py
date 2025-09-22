#!/usr/bin/env python3
"""Validate template.json and layer.json against JSON Schema and check placeholder presence."""
import json
import sys
from pathlib import Path

try:
    import jsonschema
except Exception:
    print("Please install jsonschema: pip install jsonschema", file=sys.stderr)
    raise


def load(path: Path):
    with open(path) as f:
        return json.load(f)


def unwrap_templates(data, force_unwrap=False):
    """Extract templates from data, handling wrapped and unwrapped formats.

    Args:
        data: Dictionary that may contain templates directly or under
              'templates' key
        force_unwrap: If True, only accept wrapped format; if False,
                      accept both

    Returns:
        Templates dictionary
    """
    has_templates_key = (isinstance(data, dict) and "templates" in data
                         and isinstance(data["templates"], dict))

    if force_unwrap and not has_templates_key:
        return data  # Let caller handle this case
    elif has_templates_key:
        return data["templates"]
    else:
        return data


def validate(schema_path: Path, data_path: Path):
    schema = load(schema_path)
    data = load(data_path)
    # Allow template files that wrap entries under a top-level `templates` key
    if (schema_path.name == "template_schema.json" and
        isinstance(data, dict) and "templates" in data and
        isinstance(data["templates"], dict)):
        jsonschema.validate(instance=data["templates"], schema=schema)
    else:
        jsonschema.validate(instance=data, schema=schema)


def check_placeholders(template_path: Path):
    data = load(template_path)
    # Support either a plain mapping or a wrapper object with 'templates' key
    data = unwrap_templates(data)
    failures = []
    for name, obj in data.items():
        tpl = obj.get("template", "")
        ic = obj.get("input_context", None)
        if ic is None:
            failures.append((name, "missing input_context"))
            continue
        # Enforce canonical brace-delimited input_context (e.g. '{query}').
        ic_str = str(ic).strip()
        if not (ic_str.startswith("{") and ic_str.endswith("}")):
            failures.append((name, f"input_context must be brace-delimited, got: {ic_str}"))
            continue
        # Normalize token name and check that the template contains the placeholder
        token = ic_str[1:-1]
        placeholder = "{" + token + "}"
        if placeholder not in tpl:
            failures.append((name, f"template missing placeholder {placeholder}"))
    return failures


def check_cross_references(template_path: Path, layer_path: Path):
    """Ensure every expected_output referenced in layer.json has template key."""
    tpl = load(template_path)
    tpl = unwrap_templates(tpl)
    layers = load(layer_path)
    # Support layer files that wrap the list under a top-level 'layers' key
    if (isinstance(layers, dict) and "layers" in layers and
            isinstance(layers["layers"], list)):
        layers = layers["layers"]
    tpl_keys = set(tpl.keys())
    missing = []
    for layer in layers:
        for node in layer.get("nodes", []):
            expected = node.get("expected_output")
            if expected and expected not in tpl_keys:
                missing.append((layer.get("name", "<unnamed>"),
                               node.get("id", "<unnamed>"), expected))
    return missing


def main():
    repo = Path.cwd()
    tpl = repo / "template.json"
    lyr = repo / "layer.json"
    schema_dir = repo / "schemas"
    if not tpl.exists() or not lyr.exists():
        print("template.json or layer.json not found in cwd", file=sys.stderr)
        sys.exit(2)

    try:
        validate(schema_dir / "template_schema.json", tpl)
        validate(schema_dir / "layer_schema.json", lyr)
    except jsonschema.ValidationError as e:
        print("Schema validation failed:", e, file=sys.stderr)
        sys.exit(3)

    ph_fail = check_placeholders(tpl)
    if ph_fail:
        print("Placeholder checks failed:")
        for name, msg in ph_fail:
            print(" -", name, msg)
        sys.exit(4)

    # Cross-file validation: ensure layer expected_output tokens map to templates
    cross_fail = check_cross_references(tpl, lyr)
    if cross_fail:
        print("Cross-file validation failed: expected_output tokens missing from template.json")
        for layer_name, node_id, expected in cross_fail:
            print(f" - layer={layer_name} node={node_id} expected_output={expected}")
        sys.exit(5)

    print("Validation OK")


if __name__ == "__main__":
    main()
