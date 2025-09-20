#!/usr/bin/env python3
"""
Configuration Builder for Epistemological Propagation Network

A standalone CLI application that guides users through creating custom
layer.json and template.json configuration files for the EPN system.
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class ReasoningEffort(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class LLMConfig:
    model: str
    temperature: float
    reasoning_effort: str
    max_tokens: int


@dataclass
class NodeConfig:
    name: str
    node_id: str = field(init=False)
    template_id: str = field(init=False)
    description: str = ""
    node_type: str = ""
    llm_config: Optional[LLMConfig] = None

    def __post_init__(self):
        # Convert name to snake_case for IDs
        self.node_id = self._to_snake_case(self.name)
        self.template_id = self.node_id

    @staticmethod
    def _to_snake_case(text: str) -> str:
        """Convert a name to snake_case for use as IDs."""
        # Replace spaces and hyphens with underscores
        text = re.sub(r'[-\s]+', '_', text)
        # Convert camelCase to snake_case
        text = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', text)
        # Remove non-alphanumeric characters except underscores
        text = re.sub(r'[^a-zA-Z0-9_]', '', text)
        # Convert to lowercase and remove multiple underscores
        text = re.sub(r'_+', '_', text.lower())
        # Remove leading/trailing underscores
        return text.strip('_')


@dataclass
class LayerConfig:
    name: str
    description: str = ""
    nodes: List[NodeConfig] = field(default_factory=list)


@dataclass
class TemplateConfig:
    node_epistemic_task: str = ""
    input_context: str = ""
    expected_output: str = ""
    instructions: List[str] = field(default_factory=list)
    template: str = ""


class ConfigBuilder:
    """Main configuration builder class."""

    # Predefined LLM models
    AVAILABLE_MODELS = [
        "openai/gpt-oss-20b",
        "qwen/qwen3-32b",
        "openai/gpt-oss-120b",
        "custom"
    ]

    def __init__(self):
        self.layers: List[LayerConfig] = []
        self.templates: Dict[str, TemplateConfig] = {}
        self.current_step = 0
        self.total_steps = 8  # Approximate number of major steps

    def run(self):
        """Run the configuration builder."""
        self._print_header()

        try:
            self._step_welcome()
            self._step_layer_architecture()
            self._step_node_details()
            self._step_llm_configuration()
            self._step_template_configuration()
            self._step_validation()
            self._step_save_files()
            self._step_completion()
        except KeyboardInterrupt:
            print("\n\n❌ Configuration cancelled by user.")
            sys.exit(1)
        except Exception as e:
            print(f"\n\n❌ Error during configuration: {e}")
            sys.exit(1)

    def _print_header(self):
        """Print the application header."""
        print("🚀 EPN Configuration Builder")
        print("=" * 50)
        print("Create custom layer.json and template.json files")
        print("for your Epistemological Propagation Network")
        print()

    def _step_welcome(self):
        """Welcome step and overview."""
        self.current_step = 1
        print(f"📋 Step {self.current_step}: Welcome")
        print("-" * 30)

        print("The EPN uses a flexible 1-N-1 layered architecture:")
        print("• Layer 1: Input (always 1 node)")
        print("• Layers 2-N: Processing layers (configurable nodes)")
        print("• Final Layer: Output (always 1 node)")
        print()

        if not self._confirm("Ready to begin configuration?"):
            print("❌ Configuration cancelled.")
            sys.exit(0)

        print()

    def _step_layer_architecture(self):
        """Configure the layer architecture."""
        self.current_step = 2
        print(f"📋 Step {self.current_step}: Layer Architecture")
        print("-" * 30)

        # Ask for number of middle layers
        while True:
            try:
                num_middle_layers = int(input("How many middle processing layers? (1-5): "))
                if 1 <= num_middle_layers <= 5:
                    break
                print("Please enter a number between 1 and 5.")
            except ValueError:
                print("Please enter a valid number.")

        # Create layers 
        self.layers = []

        # Layer 1: Input (always present, always 1 node)
        layer1 = LayerConfig(
            name="Input",
            description="Initial input processing and reformulation"
        )
        self.layers.append(layer1)

        # Middle layers (configurable number, each with configurable nodes)
        for i in range(num_middle_layers):
            layer = LayerConfig(
                name=f"Processing layer {i + 2}",
                description=f"Processing layer {i + 2}"
            )
            self.layers.append(layer)

        # Final layer: Output (always present, always 1 node)
        final_layer = LayerConfig(
            name="Output",
            description="Final synthesis and output generation"
        )
        self.layers.append(final_layer)

        print(f"\n✅ Created {len(self.layers)} layers:")
        for i, layer in enumerate(self.layers, 1):
            print(f"  {i}. {layer.name}")
        print()

    def _step_node_details(self):
        """Configure nodes for each layer."""
        self.current_step = 3
        print(f"📋 Step {self.current_step}: Node Configuration")
        print("-" * 30)

        print("You will now name each node in the network.")
        print("Node names will be converted to valid IDs (e.g., 'semantic node' → 'semantic_node')")
        print()

        for i, layer in enumerate(self.layers):
            layer_num = i + 1
            print(f"Layer {layer_num}: {layer.name}")

            if layer_num == 1:
                # First layer always has exactly 1 node
                num_nodes = 1
                print(f"  Layer {layer_num} ({layer.name}) requires exactly 1 node.")
            elif layer_num == len(self.layers):
                # Last layer always has exactly 1 node
                num_nodes = 1
                print(f"  Layer {layer_num} ({layer.name}) requires exactly 1 node.")
            else:
                # Middle layers have configurable number of nodes
                while True:
                    try:
                        num_nodes = int(input(f"  Layer {layer_num} ({layer.name}) - how many nodes? (1-5): "))
                        if 1 <= num_nodes <= 5:
                            break
                        print("  Please enter a number between 1 and 5.")
                    except ValueError:
                        print("  Please enter a valid number.")

            layer.nodes = []
            for j in range(num_nodes):
                if num_nodes == 1:
                    prompt = "  Node name (e.g., 'reformulator node', 'semantic node'): "
                else:
                    prompt = f"  Node {j + 1} of {num_nodes} name (e.g., 'semantic node', 'teleological node'): "

                name = input(prompt).strip()
                if not name:
                    if layer_num == 1:
                        name = "reformulator node"
                    elif layer_num == len(self.layers):
                        name = "synthesis node"
                    else:
                        name = f"node {j + 1}"

                node = NodeConfig(name=name)

                # Set default descriptions and types based on layer position
                if layer_num == 1:
                    node.description = "Initial input processing and reformulation"
                    node.node_type = "input"
                elif layer_num == len(self.layers):
                    node.description = "Final synthesis and output generation"
                    node.node_type = "output"
                else:
                    node.node_type = node.node_id  # Use the snake_case ID as type
                    node.description = f"Processing node {node.node_id}"

                layer.nodes.append(node)

            print()

        print("✅ Node configuration complete:")
        for i, layer in enumerate(self.layers, 1):
            print(f"  Layer {i} ({layer.name}): {len(layer.nodes)} node(s)")
            for node in layer.nodes:
                print(f"    • {node.name} (ID: {node.node_id})")
        print()

    def _step_llm_configuration(self):
        """Configure LLM settings for each node."""
        self.current_step = 4
        print(f"📋 Step {self.current_step}: LLM Configuration")
        print("-" * 30)

        print("Configure LLM settings for each node:")
        print("• Temperature: 0.0 (deterministic) to 1.0 (creative)")
        print("• Reasoning effort: low/medium/high")
        print("• Max tokens: response length limit")
        print()

        for layer in self.layers:
            for node in layer.nodes:
                print(f"\n🔧 {node.name} (Layer: {layer.name})")

                # Model selection
                print("Available models:")
                for i, model in enumerate(self.AVAILABLE_MODELS[:-1], 1):  # Exclude 'custom'
                    print(f"  {i}. {model}")
                print(f"  {len(self.AVAILABLE_MODELS)}. Custom model")

                while True:
                    try:
                        choice = int(input("Select model (1-4): "))
                        if 1 <= choice <= len(self.AVAILABLE_MODELS):
                            if choice == len(self.AVAILABLE_MODELS):
                                model = input("Enter custom model name: ").strip()
                            else:
                                model = self.AVAILABLE_MODELS[choice - 1]
                            break
                        print(f"Please enter a number between 1 and {len(self.AVAILABLE_MODELS)}.")
                    except ValueError:
                        print("Please enter a valid number.")

                # Temperature
                while True:
                    try:
                        temp = float(input("Temperature (0.0-1.0, default 0.8): ") or "0.8")
                        if 0.0 <= temp <= 1.0:
                            break
                        print("Temperature must be between 0.0 and 1.0.")
                    except ValueError:
                        print("Please enter a valid number.")

                # Reasoning effort
                print("Reasoning effort:")
                print("  1. Low (fast, simple tasks)")
                print("  2. Medium (balanced, default)")
                print("  3. High (thorough, complex tasks)")

                while True:
                    try:
                        effort_choice = int(input("Select reasoning effort (1-3, default 2): ") or "2")
                        if 1 <= effort_choice <= 3:
                            efforts = ["low", "medium", "high"]
                            effort = efforts[effort_choice - 1]
                            break
                        print("Please enter a number between 1 and 3.")
                    except ValueError:
                        print("Please enter a valid number.")

                # Max tokens
                while True:
                    try:
                        max_tokens = int(input("Max tokens (1000-16000, default 8192): ") or "8192")
                        if 1000 <= max_tokens <= 16000:
                            break
                        print("Max tokens must be between 1000 and 16000.")
                    except ValueError:
                        print("Please enter a valid number.")

                node.llm_config = LLMConfig(
                    model=model,
                    temperature=temp,
                    reasoning_effort=effort,
                    max_tokens=max_tokens
                )

        print("\n✅ LLM configuration complete for all nodes.\n")

    def _step_template_configuration(self):
        """Configure templates for each node."""
        self.current_step = 5
        print(f"📋 Step {self.current_step}: Template Configuration")
        print("-" * 30)

        print("Configure prompt templates for each node:")
        print("• Epistemic task: What this node does")
        print("• Input context: How to reference previous outputs")
        print("• Expected output: What format to produce")
        print("• Instructions: Step-by-step guidance")
        print()

        # First pass: collect expected outputs for all nodes
        expected_outputs = {}  # template_id -> expected_output
        
        for layer_idx, layer in enumerate(self.layers):
            for node in layer.nodes:
                print(f"\n📝 {node.name} (Layer: {layer.name})")

                template = TemplateConfig()

                # Epistemic task
                print("Describe what this node does (epistemic task):")
                template.node_epistemic_task = input("> ").strip()

                # Expected output
                template.expected_output = input("\nWhat should the output be called? (e.g., semantic_analysis): ").strip()
                expected_outputs[node.template_id] = template.expected_output

                # Instructions
                print("\nEnter instructions (one per line, empty line to finish):")
                instructions = []
                while True:
                    instruction = input(f"{len(instructions) + 1}. ").strip()
                    if not instruction:
                        break
                    instructions.append(instruction)

                template.instructions = instructions
                self.templates[node.template_id] = template

        # Second pass: set input contexts automatically
        print("\n🔄 Setting input contexts automatically...")
        
        for layer_idx, layer in enumerate(self.layers):
            for node in layer.nodes:
                template = self.templates[node.template_id]
                
                if layer_idx == 0:
                    # First layer gets raw user input
                        template.input_context = "{query}"
                        # Default template text uses the epistemic task if user did not supply a full template
                        if not template.node_epistemic_task:
                            template.template = "{query}"
                        else:
                            template.template = template.node_epistemic_task
                else:
                    # Subsequent layers get outputs from previous layer
                    prev_layer = self.layers[layer_idx - 1]
                    prev_outputs = [expected_outputs[prev_node.template_id] for prev_node in prev_layer.nodes]
                    
                    if len(prev_outputs) == 1:
                        template.input_context = f"{{{prev_outputs[0]}}}"
                    else:
                        template.input_context = [f"{{{output}}}" for output in prev_outputs]
                
                print(f"  {node.name} node: input_context = {template.input_context}")

        print("\n✅ Template configuration complete for all nodes.\n")

    def _step_validation(self):
        """Validate the configuration."""
        self.current_step = 6
        print(f"📋 Step {self.current_step}: Validation")
        print("-" * 30)

        print("Validating configuration...")

        errors = self._validate_configuration()

        if errors:
            print("❌ Validation failed:")
            for error in errors:
                print(f"  • {error}")
            print("\nPlease fix these issues and try again.")
            sys.exit(1)

        print("✅ Configuration validation passed!\n")

    def _validate_configuration(self) -> List[str]:
        """Validate the generated configuration.

        Returns:
            List of validation error messages
        """
        errors = []

        # Check basic structure
        if len(self.layers) < 3:
            errors.append("Must have at least 3 layers (reformulation, processing, synthesis)")

        # Check first layer (reformulation)
        if self.layers and len(self.layers[0].nodes) != 1:
            errors.append("First layer (reformulation) must have exactly 1 node")

        # Check last layer (synthesis)
        if self.layers and len(self.layers[-1].nodes) != 1:
            errors.append("Last layer (synthesis) must have exactly 1 node")

        # Check nodes
        all_node_ids = set()
        all_template_ids = set()

        for i, layer in enumerate(self.layers):
            if len(layer.nodes) == 0:
                errors.append(f"Layer {i+1} ({layer.name}) has no nodes")

            for node in layer.nodes:
                # Check node has required fields
                if not node.name.strip():
                    errors.append(f"Node in layer {i+1} has empty name")

                if not node.llm_config:
                    errors.append(f"Node '{node.name}' in layer {i+1} has no LLM configuration")

                # Check for duplicate node IDs
                if node.node_id in all_node_ids:
                    errors.append(f"Duplicate node ID '{node.node_id}'")
                all_node_ids.add(node.node_id)

                # Check template exists
                if node.template_id not in self.templates:
                    errors.append(f"Node '{node.name}' references missing template '{node.template_id}'")
                else:
                    all_template_ids.add(node.template_id)

        # Check templates
        for template_id, template in self.templates.items():
            if not template.node_epistemic_task.strip():
                errors.append(f"Template '{template_id}' missing epistemic task")

            if not template.expected_output.strip():
                errors.append(f"Template '{template_id}' missing expected output")

            # Check for unused templates
            if template_id not in all_template_ids:
                errors.append(f"Template '{template_id}' is not used by any node")

        # Validate LLM configurations
        for layer in self.layers:
            for node in layer.nodes:
                if node.llm_config:
                    llm = node.llm_config

                    # Check temperature range
                    if not (0.0 <= llm.temperature <= 2.0):
                        errors.append(f"Node '{node.name}' temperature {llm.temperature} not in range [0.0, 2.0]")

                    # Check max tokens
                    if llm.max_tokens <= 0:
                        errors.append(f"Node '{node.name}' max_tokens must be > 0")

                    # Check reasoning effort
                    if llm.reasoning_effort not in ['low', 'medium', 'high']:
                        errors.append(f"Node '{node.name}' reasoning_effort '{llm.reasoning_effort}' invalid")

        return errors

    def _step_save_files(self):
        """Save the configuration files."""
        self.current_step = 7
        print(f"📋 Step {self.current_step}: Save Configuration")
        print("-" * 30)

        # Generate layer.json
        layer_data = {"layers": []}
        for layer in self.layers:
            layer_dict = {
                "id": f"layer{self.layers.index(layer) + 1}",
                "name": layer.name,
                "description": layer.description,
                "nodes": []
            }

            for node in layer.nodes:
                node_dict = {
                    "id": node.node_id,
                    "name": node.name,
                    "type": node.node_type,
                    "template_id": node.template_id,
                    "description": node.description,
                    "llm_config": {
                        "model": node.llm_config.model,
                        "temperature": node.llm_config.temperature,
                        "reasoning_effort": node.llm_config.reasoning_effort,
                        "max_tokens": node.llm_config.max_tokens
                    }
                }
                layer_dict["nodes"].append(node_dict)

            layer_data["layers"].append(layer_dict)

        # Generate template.json
        template_data = {"templates": {}}
        for template_id, template in self.templates.items():
                template_dict = {
                    "template": template.template or template.node_epistemic_task,
                    "node_epistemic_task": template.node_epistemic_task,
                    "input_context": template.input_context,
                    "expected_output": template.expected_output,
                    "instructions": template.instructions
                }
                template_data["templates"][template_id] = template_dict

        # Show preview
        print("Configuration preview:")
        print("Layer configuration:")
        print(json.dumps(layer_data, indent=2)[:500] + "..." if len(json.dumps(layer_data, indent=2)) > 500 else json.dumps(layer_data, indent=2))
        print("\nTemplate configuration:")
        print(json.dumps(template_data, indent=2)[:500] + "..." if len(json.dumps(template_data, indent=2)) > 500 else json.dumps(template_data, indent=2))

        if not self._confirm("\nSave these configuration files?"):
            print("❌ Configuration not saved.")
            sys.exit(0)

        # Save files
        layer_path = Path("layer.json")
        template_path = Path("template.json")

        # Backup existing files
        for path in [layer_path, template_path]:
            if path.exists():
                backup_path = path.with_suffix(f".backup.{int(Path.cwd().stat().st_mtime)}")
                path.rename(backup_path)
                print(f"📁 Backed up existing {path.name} to {backup_path.name}")

        # Write new files
        with open(layer_path, 'w', encoding='utf-8') as f:
            json.dump(layer_data, f, indent=2, ensure_ascii=False)

        with open(template_path, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, indent=2, ensure_ascii=False)

        print(f"✅ Configuration saved to {layer_path} and {template_path}")

    def _step_completion(self):
        """Completion step."""
        self.current_step = 8
        print(f"📋 Step {self.current_step}: Complete")
        print("-" * 30)

        print("🎉 Configuration builder completed successfully!")
        print()
        print("Your custom configuration files are ready:")
        print("• layer.json - Layer and node architecture")
        print("• template.json - Prompt templates for each node")
        print()
        print("You can now run the EPN with your custom configuration:")
        print("  python epn_cli.py run \"Your question here\"")
        print()
        print("Or run the simplified runner to inspect prompts and outputs:")
        print("  python scripts/minimal_runner.py \"Your question here\"")

    def _confirm(self, message: str) -> bool:
        """Get user confirmation."""
        while True:
            response = input(f"{message} (y/n): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print("Please enter 'y' or 'n'.")


def main():
    """Main entry point."""
    builder = ConfigBuilder()
    builder.run()


if __name__ == "__main__":
    main()