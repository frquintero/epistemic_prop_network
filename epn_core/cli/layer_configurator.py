"""Layer configurator for creating layer_conf.json."""

from typing import Dict, Any, List

from .base_configurator import Configurator


class LayerConfigurator(Configurator):
    """Interactive configurator for layer and node structure."""

    def __init__(self, output_file: str = "config/default_layer.json"):
        """Initialize the layer configurator.

        Args:
            output_file: Path where the layer configuration will be saved
        """
        super().__init__(output_file)

    def run_interactive(self) -> Dict[str, Any]:
        """Run the interactive layer configuration wizard.

        Returns:
            Layer configuration dictionary
        """
        print("\n🧠 Welcome to the EPN Layer-Nodes Configurator!")
        print("Let's define your epistemic pipeline structure.\n")

        # Get basic metadata
        metadata = self._get_metadata()

        # Get layer structure
        layers_data = self._get_layers_config()

        # Build final configuration
        config = {
            "metadata": metadata,
            "layers": layers_data
        }

        print(f"\n✅ Layer configuration created with {len(layers_data)} layers")
        return config

    def _get_metadata(self) -> Dict[str, Any]:
        """Get configuration metadata."""
        print("Configuration Metadata:")
        print("-" * 30)

        description = input("Description of this pipeline: ").strip()
        if not description:
            description = "Custom EPN pipeline configuration"

        return {
            "version": "1.0.0",
            "description": description,
            "created": "2025-09-18",
            "structure": "User-defined layer structure"
        }

    def _get_layers_config(self) -> List[Dict[str, Any]]:
        """Get layer configuration through interactive prompts."""
        layers = []

        # First layer is always required (input/reformulation)
        print("\n📝 Layer 1 (Input Layer) - Required")
        layer1 = self._create_input_layer()
        layers.append(layer1)

        # Get intermediate layers
        while True:
            print(f"\n📝 Current layers: {len(layers)}")
            add_more = input("Add another layer? (y/n): ").lower().strip()
            if add_more != 'y':
                break

            layer = self._create_intermediate_layer(len(layers) + 1)
            layers.append(layer)

        # Last layer is always required (output/synthesis)
        print(f"\n📝 Layer {len(layers) + 1} (Output Layer) - Required")
        output_layer = self._create_output_layer(len(layers) + 1)
        layers.append(output_layer)

        return layers

    def _create_input_layer(self) -> Dict[str, Any]:
        """Create the input layer configuration."""
        layer_id = "input"
        name = input("Name for input layer [Input Processing]: ").strip()
        if not name:
            name = "Input Processing"

        description = input("Description [Processes raw user input]: ").strip()
        if not description:
            description = "Processes raw user input"

        # Input layer typically has 1 node
        nodes = []
        print("\n  🔧 Node 1 in Input Layer:")
        node = self._create_node(
            "input_processor", "Input Processor",
            "Processes and reformulates raw input"
        )
        nodes.append(node)

        return {
            "id": layer_id,
            "name": name,
            "description": description,
            "nodes": nodes
        }

    def _create_intermediate_layer(self, layer_num: int) -> Dict[str, Any]:
        """Create an intermediate layer configuration."""
        layer_id = f"layer{layer_num}"
        name = input(f"Name for layer {layer_num}: ").strip()
        if not name:
            name = f"Processing Layer {layer_num}"

        description = input(f"Description for layer {layer_num}: ").strip()
        if not description:
            description = f"Intermediate processing layer {layer_num}"

        # Get nodes for this layer
        nodes = []
        while True:
            node_num = len(nodes) + 1
            print(f"\n  🔧 Node {node_num} in {name}:")

            node_id = input(f"    Node ID [node{node_num}]: ").strip()
            if not node_id:
                node_id = f"node{node_num}"

            node_name = input(f"    Node name [Node {node_num}]: ").strip()
            if not node_name:
                node_name = f"Node {node_num}"

            node_desc = input("    Node description: ").strip()
            if not node_desc:
                node_desc = f"Processing node {node_num}"

            node = self._create_node(node_id, node_name, node_desc)
            nodes.append(node)

            add_more = input(
                "    Add another node to this layer? (y/n): "
            ).lower().strip()
            if add_more != 'y':
                break

        return {
            "id": layer_id,
            "name": name,
            "description": description,
            "nodes": nodes
        }

    def _create_output_layer(self, layer_num: int) -> Dict[str, Any]:
        """Create the output layer configuration."""
        layer_id = "output"
        name = input("Name for output layer [Output Synthesis]: ").strip()
        if not name:
            name = "Output Synthesis"

        description = input("Description [Synthesizes final output]: ").strip()
        if not description:
            description = "Synthesizes final output"

        # Output layer typically has 1 node
        nodes = []
        print("\n  🔧 Node 1 in Output Layer:")
        node = self._create_node(
            "output_synthesizer", "Output Synthesizer",
            "Synthesizes and formats final output"
        )
        nodes.append(node)

        return {
            "id": layer_id,
            "name": name,
            "description": description,
            "nodes": nodes
        }

    def _create_node(self, node_id: str, node_name: str,
                     node_desc: str) -> Dict[str, Any]:
        """Create a node configuration with LLM settings."""
        print(f"    LLM config for {node_name}...")

        # LLM Model selection
        print("    Available models:")
        print("      1. gpt-oss-120b (recommended)")
        print("      2. gpt-oss-20b")
        print("      3. qwen3-32b")

        while True:
            choice = input("    Select model (1-3) [1]: ").strip()
            if not choice:
                choice = "1"

            model_map = {
                "1": "gpt-oss-120b",
                "2": "gpt-oss-20b",
                "3": "qwen3-32b"
            }

            if choice in model_map:
                model = model_map[choice]
                break
            else:
                print("    Invalid choice. Please select 1-3.")

        # Temperature
        while True:
            temp_str = input("    Temperature (0.0-2.0) [0.8]: ").strip()
            if not temp_str:
                temperature = 0.8
                break

            try:
                temperature = float(temp_str)
                if 0.0 <= temperature <= 2.0:
                    break
                else:
                    print("    Temperature must be between 0.0 and 2.0")
            except ValueError:
                print("    Please enter a valid number")

        # Reasoning effort
        print("    Reasoning effort:")
        print("      1. low")
        print("      2. medium (recommended)")
        print("      3. high")

        while True:
            choice = input("    Select reasoning effort (1-3) [2]: ").strip()
            if not choice:
                choice = "2"

            effort_map = {
                "1": "low",
                "2": "medium",
                "3": "high"
            }

            if choice in effort_map:
                reasoning_effort = effort_map[choice]
                break
            else:
                print("    Invalid choice. Please select 1-3.")

        # Max tokens
        while True:
            tokens_str = input("    Max tokens (1-32768) [4096]: ").strip()
            if not tokens_str:
                max_tokens = 4096
                break

            try:
                max_tokens = int(tokens_str)
                if 1 <= max_tokens <= 32768:
                    break
                else:
                    print("    Max tokens must be between 1 and 32768")
            except ValueError:
                print("    Please enter a valid number")

        return {
            "id": node_id,
            "name": node_name,
            "description": node_desc,
            "llm_config": {
                "model": model,
                "temperature": temperature,
                "reasoning_effort": reasoning_effort,
                "max_tokens": max_tokens
            }
        }
