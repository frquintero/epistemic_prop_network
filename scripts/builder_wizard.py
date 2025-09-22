"""Interactive builder wizard for canonical templates and layers.

This script is intentionally small and dependency-free so tests can run
non-interactively using heredoc input. It enforces a minimal 1-1-1
(topology of at least three layers with at least one node each),
uses assertive prompts, and provides an opt-in neutral preview
that substitutes '<USER_QUERY>' into templates.
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from epn_core.config.builder_utils import (
    sanitize_name,
    build_templates,
    build_layers,
    preview,
)


def ask(prompt: str, default: str | None = None) -> str | None:
    if default:
        full = f"{prompt} [{default}]: "
    else:
        full = f"{prompt}: "
    try:
        resp = input(full)
    except EOFError:
        # When running non-interactively and stdin exhausted, signal EOF to caller
        return None
    if not resp and default is not None:
        return default
    return resp.strip()


def run_validation(context: str) -> int:
    """Run template validation and return exit code.

    Args:
        context: Description of when validation is running
                 (e.g. "dry-run", "after writing files")

    Returns:
        Exit code from validation (0 for success, non-zero for failure)
    """
    import subprocess
    import sys

    if context == "dry-run":
        print_prefix = "Validation failed (dry-run). Not writing files."
    else:
        print("Running validation on generated files...")
        print_prefix = ("Validation failed after writing files. "
                        "See output above.")

    res = subprocess.run([sys.executable, "scripts/validate_templates.py"],
                         capture_output=True, text=True)
    print(res.stdout)
    if res.returncode != 0:
        print(print_prefix)
        print(res.stderr)
        return res.returncode
    return 0



def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--no-validate", action="store_true", help="Do not run template validation after generation")
    p.add_argument("--timestamped", action="store_true")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument(
        "--preview",
        action="store_true",
        help="Show a rendered preview substituting a neutral '<USER_QUERY>' into templates",
    )
    args = p.parse_args()

    print("Builder wizard — minimal inputs per node. Ctrl-C to abort.")
    print("Goal: author canonical `template.json` and `layer.json` for a minimal 1-1-1 network.")
    print("Rules: you must create at least three layers (input, processing, output). Each layer needs at least one node.")
    print("Behavior: press Enter on an empty node name to finish that layer (only after one node exists).")
    print("Press Enter on an empty layer name to finish authoring only after adding at least three layers.")

    layers: List[Dict] = []
    layer_idx = 0
    existing_expected = set()

    # interactive authoring loop
    try:
        while True:
            layer_idx += 1
            role_hint = "(first/input)" if layer_idx == 1 else "(processing)"
            finish_hint = " (press Enter to finish layers)" if len(layers) >= 3 else ""
            lname = ask(f"Enter Layer {layer_idx} name {role_hint}{finish_hint}")

            # if stdin exhausted, finish if we have >=3 layers else abort
            if lname is None:
                if len(layers) < 3:
                    print("  EOF encountered and fewer than three layers entered — aborting.")
                    return 1
                break

            # enforce minimal 3-layer configuration
            if not lname:
                if len(layers) < 3:
                    print("  At least three layers are required (minimal 1-1-1). Continue adding layers.")
                    layer_idx -= 1
                    continue
                break

            ldesc = ask("Short description for this layer (one line)", "Process and transform input")
            nodes: List[Dict] = []
            node_idx = 0

            while True:
                node_idx += 1
                finish_hint_node = " (press Enter to finish nodes for this layer)" if nodes else ""
                nid = ask(
                    f"Enter Layer {layer_idx} - Node {node_idx} name — short identifier (e.g., 'extract_ideas' or '1a')" + finish_hint_node
                )

                # handle EOF: treat as finishing current layer (only allowed if nodes exist)
                if nid is None:
                    if not nodes:
                        print("  EOF encountered before adding a node to this layer — aborting.")
                        return 1
                    break

                if not nid:
                    if not nodes:
                        print("  A layer must have at least one node. Please add a node.")
                        node_idx -= 1
                        continue
                    break

                suggested = sanitize_name(nid)
                expected_raw = ask(
                    f"  expected_output (single snake_case token) — suggested: {suggested}",
                    suggested,
                )
                if expected_raw is None:
                    print("  EOF encountered while entering node fields — aborting.")
                    return 1
                expected = sanitize_name(expected_raw)
                if expected in existing_expected:
                    print(f"  ⚠️  expected_output '{expected}' already used. Please enter a unique token.")
                    expected = sanitize_name(ask("  expected_output (unique)", suggested + "_1"))

                task = ask("  node_epistemic_task (one-line instruction — describe exactly what this node should produce)")
                if task is None:
                    print("  EOF encountered while entering node fields — aborting.")
                    return 1
                instr: List[str] = []
                instr_idx = 0
                while True:
                    instr_idx += 1
                    i = ask(f"   instruction {instr_idx} — additional guidance (press Enter to stop adding instructions)")
                    if i is None:
                        # EOF while adding instructions — stop adding instructions
                        break
                    if not i:
                        break
                    instr.append(i)

                existing_expected.add(expected)
                nodes.append({
                    "id": nid,
                    "expected_output": expected,
                    "node_epistemic_task": task,
                    "instructions": instr,
                })

            layers.append({"name": lname, "description": ldesc, "nodes": nodes})

    except KeyboardInterrupt:
        print("\nAborted by user.")
        return 130

    if not layers:
        print("No layers entered — exiting.")
        return 1

    templates = build_templates(layers)
    layer_out = build_layers(layers)

    # Convert authoring-shaped outputs to the runtime config shape
    # Runtime templates are keyed by node id (template_id) and include
    # placeholders, metadata and other runtime fields expected by the loader.
    runtime_templates: Dict[str, Dict] = {}
    for layer in layers:
        for node in layer["nodes"]:
            expected = node.get("expected_output")
            # source template produced by build_templates is keyed by expected token
            src = templates.get(expected, {})
            input_ctx = src.get("input_context")
            # normalize placeholders
            if isinstance(input_ctx, list):
                placeholders = [p.strip("{}") for p in input_ctx]
            elif isinstance(input_ctx, str):
                placeholders = [input_ctx.strip("{}")]
            else:
                placeholders = []

            # Key template by the expected token so nodes can reference it via template_id
            if expected:
                runtime_templates[expected] = {
                    "template": src.get("template", ""),
                    "placeholders": placeholders,
                    "metadata": {"purpose": node.get("node_epistemic_task", "")},
                    "input_context": input_ctx,
                    "expected_output": expected,
                    "instructions": src.get("instructions", []),
                }

    # Build runtime-shaped layers list: add layer ids and node runtime fields
    runtime_layers = {"layers": []}
    for idx, layer in enumerate(layers, start=1):
        layer_id = f"layer{idx}"
        runtime_nodes = []
        for node in layer["nodes"]:
            nid = node["id"]
            expected = node.get("expected_output")
            node_type = node.get("type", expected or nid)
            runtime_nodes.append(
                {
                    "id": nid,
                    "name": nid.replace("_", " ").title(),
                    "type": node_type,
                    "template_id": expected or nid,
                    "expected_output": expected,
                    "description": node.get("node_epistemic_task", ""),
                    "llm_config": {
                        "model": "openai/gpt-oss-20b",
                        "temperature": 0.8,
                        "reasoning_effort": "medium",
                        "max_tokens": 8192,
                    },
                }
            )

        runtime_layers["layers"].append(
            {
                "id": layer_id,
                "name": layer.get("name", layer_id),
                "description": layer.get("description", ""),
                "nodes": runtime_nodes,
            }
        )

    if args.preview:
        preview(templates, sample_query="<USER_QUERY>")

    dup = [k for k in templates.keys() if list(templates.keys()).count(k) > 1]
    if dup:
        print("Duplicate expected_output names found:", dup)
        return 2

    repo = Path.cwd()
    tname = repo / "template.json"
    lname = repo / "layer.json"
    if args.dry_run:
        # Show runtime-shaped outputs (wrapped for loader compatibility)
        print(json.dumps({"templates": runtime_templates}, indent=2))
        print(json.dumps(runtime_layers, indent=2))
        # Optionally validate the generated structures even in dry-run mode
        if not args.no_validate:
            # Use the current Python interpreter (sys.executable) so
            # validation runs in the same environment (venv) as this script.
            validation_result = run_validation("dry-run")
            if validation_result != 0:
                return validation_result
        return 0

    if args.timestamped:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M")
        tname = repo / f"template.{ts}.json"
        lname = repo / f"layer.{ts}.json"

    if not args.overwrite and (tname.exists() or lname.exists()):
        confirm = ask("Target files exist. Type 'yes' to overwrite", "no")
        if confirm.lower() != "yes":
            print("Aborting to avoid overwrite.")
            return 3

    with open(tname, "w") as f:
        json.dump({"templates": runtime_templates}, f, indent=2)
    with open(lname, "w") as f:
        json.dump(runtime_layers, f, indent=2)
    print(f"Wrote {tname} and {lname}")

    if not args.no_validate:
        validation_result = run_validation("after writing files")
        if validation_result != 0:
            return validation_result
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

