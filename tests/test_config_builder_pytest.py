#!/usr/bin/env python3
import subprocess
import sys
import json
import shutil
from pathlib import Path


def test_config_builder_generates_canonical_files(tmp_path):
    """Run the config builder non-interactively in an isolated tmp dir and assert files and contract."""
    repo_root = Path(__file__).resolve().parents[1]

    # Copy the new wizard into the temporary directory so it runs isolated
    shutil.copy(repo_root / "scripts" / "builder_wizard.py", tmp_path / "builder_wizard.py")

    # Prepare inputs matching the builder_wizard interactive flow
    test_inputs = []

    # Layer 1
    test_inputs.append("Input")
    test_inputs.append("input layer")
    # Node 1 in layer 1
    test_inputs.append("reformulator_node")
    test_inputs.append("reformulated_question")
    test_inputs.append("You are an epistemological reformulator")
    test_inputs.append("Neutralize biases")
    test_inputs.append("Prime for emplotment")
    test_inputs.append("")  # end instructions
    test_inputs.append("")  # end nodes for this layer

    # Layer 2
    test_inputs.append("Processing")
    test_inputs.append("processing layer")
    test_inputs.append("semantic_node")
    test_inputs.append("semantic_analysis")
    test_inputs.append("You are a semantic epistemologist analyzing meaning and intent")
    test_inputs.append("Analyze deeply")
    test_inputs.append("Find patterns")
    test_inputs.append("")
    test_inputs.append("")

    # Layer 3 (final)
    test_inputs.append("Output")
    test_inputs.append("output layer")
    test_inputs.append("synthesis_node")
    test_inputs.append("comprehensive_synthesis")
    test_inputs.append("You are a master synthesizer that weaves ideas together")
    test_inputs.append("Synthesize insights")
    test_inputs.append("Create coherent narrative")
    test_inputs.append("")
    test_inputs.append("")

    # Finish layers
    test_inputs.append("")

    # Run builder in tmp_path (isolated)
    # run the builder_wizard script with the same inputs; it expects interactive stdin
    proc = subprocess.run(
        [sys.executable, str(tmp_path / "builder_wizard.py")],
        input="\n".join(test_inputs) + "\n",
        text=True,
        capture_output=True,
        cwd=str(tmp_path),
        timeout=60,
    )
    assert proc.returncode == 0, f"Builder failed: {proc.stderr}\n{proc.stdout}"

    layer_file = tmp_path / "layer.json"
    template_file = tmp_path / "template.json"
    assert layer_file.exists(), "layer.json was not created"
    assert template_file.exists(), "template.json was not created"

    # Validate template.json canonical structure
    data = json.loads(template_file.read_text(encoding="utf-8"))
    # normalize: some writers produce {"templates": {...}} while others write {...}
    if "templates" in data and isinstance(data["templates"], dict):
        templates = data["templates"]
    else:
        templates = data

    # Check each template has the canonical keys
    for tid, t in templates.items():
        assert "template" in t, f"template key missing for {tid}"
        assert "input_context" in t, f"input_context missing for {tid}"
        assert "expected_output" in t, f"expected_output missing for {tid}"

    # First-layer template should use {query} as input_context
    reform_id = "reformulator_node"
    if reform_id in templates:
        assert templates[reform_id]["input_context"] == "{query}" or templates[reform_id]["input_context"] == "query"

    # Cleanup created files (but leave backups alone)
    for p in [layer_file, template_file]:
        if p.exists():
            p.unlink()
