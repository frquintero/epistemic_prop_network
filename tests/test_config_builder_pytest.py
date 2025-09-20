#!/usr/bin/env python3
import subprocess
import sys
import json
import shutil
from pathlib import Path


def run_builder_with_inputs(inputs, cwd: Path):
    input_str = "\n".join(inputs) + "\n"
    proc = subprocess.run(
        [sys.executable, str(cwd / "config_builder.py")],
        input=input_str,
        text=True,
        capture_output=True,
        cwd=str(cwd),
        timeout=30,
    )
    return proc


def test_config_builder_generates_canonical_files(tmp_path):
    """Run the config builder non-interactively in an isolated tmp dir and assert files and contract."""
    repo_root = Path(__file__).resolve().parents[1]

    # Copy the builder into the temporary directory so it runs isolated
    shutil.copy(repo_root / "config_builder.py", tmp_path / "config_builder.py")

    # Prepare inputs matching the interactive flow used previously (no max_tokens)
    test_inputs = [
        "y",  # Ready to begin
        "1",  # 1 middle layer
        "reformulator node",  # layer 1 node
        "1",  # middle layer node count
        "semantic node",  # middle node name
        "synthesis node",  # final node name
        # LLM config for reformulator node: model, temp, effort
        "1", "0.8", "2",
        # LLM config for semantic node
        "1", "0.8", "2",
        # LLM config for synthesis node
        "1", "0.6", "3",
        # Templates: epistemic tasks and expected outputs and a couple instructions
        "You are an epistemological reformulator",
        "reformulated_question",
        "Neutralize biases",
        "Prime for emplotment",
        "",
        "You are a semantic epistemologist analyzing meaning and intent",
        "semantic_analysis",
        "Analyze deeply",
        "Find patterns",
        "",
        "You are a master synthesizer that weaves ideas together",
        "comprehensive_synthesis",
        "Synthesize insights",
        "Create coherent narrative",
        "",
        "y",  # Save files
    ]

    # Run builder in tmp_path (isolated)
    proc = run_builder_with_inputs(test_inputs, tmp_path)
    assert proc.returncode == 0, f"Builder failed: {proc.stderr}\n{proc.stdout}"

    layer_file = tmp_path / "layer.json"
    template_file = tmp_path / "template.json"
    assert layer_file.exists(), "layer.json was not created"
    assert template_file.exists(), "template.json was not created"

    # Validate template.json canonical structure
    data = json.loads(template_file.read_text(encoding="utf-8"))
    assert "templates" in data and isinstance(data["templates"], dict)

    # Check each template has the canonical keys
    for tid, t in data["templates"].items():
        assert "template" in t, f"template key missing for {tid}"
        assert "input_context" in t, f"input_context missing for {tid}"
        assert "expected_output" in t, f"expected_output missing for {tid}"

    # First-layer template should use {query} as input_context
    reform_id = "reformulator_node"
    if reform_id in data["templates"]:
        assert data["templates"][reform_id]["input_context"] == "{query}"

    # Cleanup created files (but leave backups alone)
    for p in [layer_file, template_file]:
        if p.exists():
            p.unlink()
