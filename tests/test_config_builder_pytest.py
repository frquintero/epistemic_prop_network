import subprocess
import sys
from pathlib import Path


def test_config_builder_creates_files(tmp_path):
    # Prepare inputs similar to original test script
    test_inputs = [
        "y",  # Ready to begin
        "1",  # 1 middle layer
        "reformulator node",  # Node name for layer 1
        "1",  # 1 node in middle layer
        "semantic node",  # Node name for middle layer
        "synthesis node",  # Node name for final layer
        "1",  # Model choice for layer 1 node (openai/gpt-oss-20b)
        "0.8",  # Temperature for layer 1 node
        "2",  # Reasoning effort for layer 1 node (medium)
        "4096",  # Max tokens for layer 1 node
        "1",  # Model choice for middle layer node (openai/gpt-oss-20b)
        "0.8",  # Temperature for middle layer node
        "2",  # Reasoning effort for middle layer node (medium)
        "4096",  # Max tokens for middle layer node
        "1",  # Model choice for final layer node (openai/gpt-oss-20b)
        "0.6",  # Temperature for final layer node
        "3",  # Reasoning effort for final layer node (high)
        "4096",  # Max tokens for final layer node
        "You are an epistemological reformulator",  # Epistemic task for layer 1 node
        "reformulated_question",  # Expected output for layer 1 node
        "Neutralize biases",  # Instruction 1 for layer 1 node
        "Prime for emplotment",  # Instruction 2 for layer 1 node
        "",  # End instructions for layer 1 node
        "You are a semantic epistemologist analyzing meaning and intent",  # Epistemic task for middle layer node
        "semantic_analysis",  # Expected output for middle layer node
        "Analyze deeply",  # Instruction 1 for middle layer node
        "Find patterns",  # Instruction 2 for middle layer node
        "",  # End instructions for middle layer node
        "You are a master synthesizer that weaves ideas together",  # Epistemic task for final layer node
        "comprehensive_synthesis",  # Expected output for final layer node
        "Synthesize insights",  # Instruction 1 for final layer node
        "Create coherent narrative",  # Instruction 2 for final layer node
        "",  # End instructions for final layer node
        "y",  # Save files
    ]

    input_string = "\n".join(test_inputs) + "\n"

    # Run config_builder.py in the temporary directory
    proc = subprocess.run([
        sys.executable, str(Path.cwd() / "config_builder.py")
    ], input=input_string, text=True, capture_output=True, cwd=tmp_path)

    # Check that files were created
    layer_file = tmp_path / "layer.json"
    template_file = tmp_path / "template.json"

    assert proc.returncode == 0
    assert layer_file.exists(), "layer.json should be created"
    assert template_file.exists(), "template.json should be created"
