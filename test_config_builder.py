#!/usr/bin/env python3
"""
Test script for the configuration builder.
"""

import subprocess
import sys
import os
from pathlib import Path

def test_config_builder():
    """Test the configuration builder with automated inputs."""

    # Test inputs for a simple 1-2-1 configuration
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

    # Convert inputs to a single string with newlines
    input_string = "\n".join(str(inp) for inp in test_inputs)

    # Run the config builder
    try:
        result = subprocess.run(
            [sys.executable, "config_builder.py"],
            input=input_string,
            text=True,
            capture_output=True,
            cwd=Path(__file__).parent
        )

        print("STDOUT:")
        print(result.stdout)
        print("\nSTDERR:")
        print(result.stderr)
        print(f"\nReturn code: {result.returncode}")

        # Check if files were created
        layer_file = Path("layer.json")
        template_file = Path("template.json")

        if layer_file.exists() and template_file.exists():
            print("\n✅ Test passed: Configuration files created successfully")

            # Show file contents
            print("\nLayer configuration:")
            with open(layer_file, 'r') as f:
                print(f.read()[:500] + "..." if len(f.read()) > 500 else f.read())

            print("\nTemplate configuration:")
            with open(template_file, 'r') as f:
                content = f.read()
                print(content[:500] + "..." if len(content) > 500 else content)

            return True
        else:
            print("\n❌ Test failed: Configuration files not created")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

if __name__ == "__main__":
    success = test_config_builder()
    sys.exit(0 if success else 1)