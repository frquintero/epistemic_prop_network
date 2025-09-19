"""Template configurator for creating template.json."""

from typing import Dict, Any, List, Optional

from .base_configurator import Configurator
from ..config.loader import ConfigLoader


class TemplateConfigurator(Configurator):
    """Interactive configurator for prompt templates."""

    def __init__(self, output_file: str = "config/default_template.json",
                 layer_config_file: Optional[str] = None):
        """Initialize the template configurator.

        Args:
            output_file: Path where the template configuration will be saved
            layer_config_file: Path to layer config file to determine required templates
        """
        super().__init__(output_file)
        self.layer_config_file = layer_config_file
        self.required_nodes: List[str] = []

    def run_interactive(self) -> Dict[str, Any]:
        """Run the interactive template configuration wizard.

        Returns:
            Template configuration dictionary
        """
        print("\n📝 Welcome to the EPN Template Configurator!")
        print("Let's define the prompt templates for your pipeline nodes.\n")

        # Load layer config if provided
        if self.layer_config_file:
            self._load_layer_config()
        else:
            print("⚠️  No layer config file provided. You'll need to "
                  "specify nodes manually.")

        # Get basic metadata
        metadata = self._get_metadata()

        # Get template configurations
        templates_data = self._get_templates_config()

        # Build final configuration
        config = {
            "metadata": metadata,
            "templates": templates_data
        }

        print(f"\n✅ Template configuration created with "
              f"{len(templates_data)} templates")
        return config

    def _load_layer_config(self) -> None:
        """Load layer configuration to determine required nodes."""
        try:
            loader = ConfigLoader()
            layer_config = loader.load_layer_config(self.layer_config_file)

            self.required_nodes = []
            for layer in layer_config.layers:
                for node in layer.nodes:
                    self.required_nodes.append(node.node_id)

            print(f"📋 Loaded layer config with "
                  f"{len(self.required_nodes)} required nodes:")
            for node_id in self.required_nodes:
                print(f"  • {node_id}")

        except Exception as e:
            print(f"⚠️  Could not load layer config: {e}")
            print("Continuing with manual node specification...")

    def _get_metadata(self) -> Dict[str, Any]:
        """Get configuration metadata."""
        print("\nConfiguration Metadata:")
        print("-" * 30)

        description = input("Description of these templates: ").strip()
        if not description:
            description = "Custom EPN prompt templates"

        return {
            "version": "1.0.0",
            "description": description,
            "created": "2025-09-18",
            "templates": self.required_nodes.copy() if self.required_nodes else []
        }

    def _get_templates_config(self) -> Dict[str, Any]:
        """Get template configurations through interactive prompts."""
        templates = {}

        # If we have required nodes from layer config, use them
        if self.required_nodes:
            print(f"\n🔧 Configuring templates for {len(self.required_nodes)} nodes...")
            for node_id in self.required_nodes:
                template = self._create_template_for_node(node_id)
                templates[node_id] = template
        else:
            # Manual mode
            print("\n🔧 Manual template creation mode:")
            while True:
                node_id = input("Node ID (or 'done' to finish): ").strip()
                if node_id.lower() == 'done':
                    break

                if not node_id:
                    continue

                if node_id in templates:
                    print(f"⚠️  Template for '{node_id}' already exists. Skipping.")
                    continue

                template = self._create_template_for_node(node_id)
                templates[node_id] = template

        return templates

    def _create_template_for_node(self, node_id: str) -> Dict[str, Any]:
        """Create a template configuration for a specific node."""
        print(f"\n  📝 Template for node: {node_id}")
        print("  " + "=" * (25 + len(node_id)))

        # Template text
        print("  Enter the prompt template. Use {{variable}} for placeholders.")
        print("  Example: 'Process this input: {{input}}'")
        print()

        template_lines = []
        print("  Enter template (press Enter twice to finish):")
        while True:
            line = input("  ")
            if line == "" and template_lines and template_lines[-1] == "":
                # Two consecutive empty lines - finish
                break
            template_lines.append(line)

        # Remove the last empty line if present
        if template_lines and template_lines[-1] == "":
            template_lines.pop()

        template_text = "\n".join(template_lines)

        if not template_text.strip():
            print("  ⚠️  Empty template. Using default.")
            template_text = f"Process input for {node_id}: {{input}}"

        # Extract placeholders from template
        placeholders = self._extract_placeholders(template_text)

        # Get word limit
        word_limit = self._get_word_limit()

        # Get metadata
        purpose = input("  Purpose/description: ").strip()
        if not purpose:
            purpose = f"Processing for {node_id}"

        layer = input("  Layer (e.g., layer1, layer2): ").strip()
        if not layer:
            layer = "custom"

        return {
            "template": template_text,
            "placeholders": placeholders,
            "metadata": {
                "purpose": purpose,
                "layer": layer,
                "word_limit": word_limit
            }
        }

    def _extract_placeholders(self, template_text: str) -> List[str]:
        """Extract placeholder variables from template text."""
        import re

        # Find all {{variable}} patterns
        pattern = r'\{\{([^}]+)\}\}'
        matches = re.findall(pattern, template_text)

        # Remove duplicates while preserving order
        seen = set()
        placeholders = []
        for match in matches:
            var = match.strip()
            if var not in seen:
                seen.add(var)
                placeholders.append(var)

        return placeholders

    def _get_word_limit(self) -> Optional[int]:
        """Get word limit for the template."""
        while True:
            limit_str = input("  Word limit (optional, press Enter to skip): ").strip()

            if not limit_str:
                return None

            try:
                limit = int(limit_str)
                if limit > 0:
                    return limit
                else:
                    print("  Word limit must be positive")
            except ValueError:
                print("  Please enter a valid number or press Enter to skip")
