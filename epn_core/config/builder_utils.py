"""Shared builder utilities for layer/template generation.

Functions here are extracted from `scripts/builder_wizard.py` so multiple
builders (scripts and CLI configurators) can reuse the same logic.
"""
from typing import Dict, List


def sanitize_name(s: str) -> str:
    s = s.strip().lower()
    import re

    s = re.sub(r"[^a-z0-9_]+", "_", s)
    s = re.sub(r"_+", "_", s)
    s = s.strip("_")
    return s or "output"


def build_templates(layers: List[Dict]) -> Dict[str, Dict]:
    out: Dict[str, Dict] = {}
    for layer in layers:
        for node in layer["nodes"]:
            expected = node["expected_output"]
            # simple chaining: template uses previous layer output if exists
            input_ctx = "{query}"
            template_text = "{query}"
            # find previous layer's first node expected token if available
            prev_token = None
            try:
                idx = layers.index(layer)
            except ValueError:
                idx = 0
            if idx > 0:
                prev_layer = layers[idx - 1]
                if prev_layer["nodes"]:
                    prev_token = prev_layer["nodes"][0]["expected_output"]
            if prev_token:
                input_ctx = f"{{{prev_token}}}"
                template_text = f"{{{prev_token}}}"

            task = node.get("node_epistemic_task", "Perform the task")
            template = f"{task}: {template_text}"

            out[expected] = {
                "template": template,
                "input_context": input_ctx,
                "expected_output": expected,
                "instructions": node.get("instructions", []),
            }
    return out


def build_layers(layers: List[Dict]) -> Dict:
    out = {"layers": []}
    for idx, layer in enumerate(layers):
        out["layers"].append(
            {
                "name": layer.get("name", f"layer{idx+1}"),
                "description": layer.get("description", ""),
                "nodes": layer["nodes"],
            }
        )
    return out


def preview(templates: Dict[str, Dict], sample_query: str = "Why are humans prone to conflict?") -> None:
    print("\n--- Preview (rendered prompts using sample query) ---")
    for name, obj in templates.items():
        rendered = obj["template"].replace("{" + obj["input_context"] + "}", sample_query)
        print(f"\n[{name}] -> {rendered}")
    print("\n--- End preview ---\n")
