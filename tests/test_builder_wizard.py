import json
from pathlib import Path
from epn_core.config.builder_utils import build_templates, build_layers


def test_build_templates_simple():
    layers = [
        {"name": "layer1", "description": "first", "nodes": [{"id": "n1", "expected_output": "first_principles", "node_epistemic_task": "Break down problem"}]},
        {"name": "layer2", "description": "second", "nodes": [{"id": "n2", "expected_output": "pareto", "node_epistemic_task": "Find vital few"}]},
    ]
    templates = build_templates(layers)
    assert "first_principles" in templates
    assert "pareto" in templates
    assert "{query}" in templates["first_principles"]["template"]
    assert "{first_principles}" in templates["pareto"]["template"]


def test_build_layers_structure(tmp_path):
    layers = [
        {"name": "layer1", "description": "first", "nodes": [{"id": "n1", "expected_output": "first_principles"}]}
    ]
    out = build_layers(layers)
    assert "layers" in out
    assert out["layers"][0]["nodes"][0]["expected_output"] == "first_principles"
