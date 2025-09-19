"""Configuration loading and management for the EPN pipeline."""

import json
from typing import Dict, Any

from ..core.node import NodeConfig, LayerConfig, PipelineConfig
from epn_core.core.llm_client import LLMConfig
from epn_core.core.logging_config import get_logger


class ConfigLoader:
    """Loads and validates JSON configuration files for the EPN pipeline."""

    def __init__(self):
        """Initialize the config loader."""
        self.logger = get_logger("ConfigLoader")

    def load_layer_config(self, file_path: str) -> PipelineConfig:
        """Load layer configuration from JSON file.

        Args:
            file_path: Path to the layer configuration JSON file

        Returns:
            PipelineConfig object

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the JSON is invalid or missing required fields
        """
        self.logger.info(f"Loading layer config from {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Layer config file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in layer config file: {e}")

        # Validate the basic structure
        if 'layers' not in data:
            raise ValueError("Layer config missing 'layers' key")

        if not isinstance(data['layers'], list):
            raise ValueError("'layers' must be a list")

        # Build PipelineConfig
        layers = []
        for layer_data in data['layers']:
            layer_config = self._parse_layer_config(layer_data)
            layers.append(layer_config)

        config = PipelineConfig(layers=layers)
        self.logger.info(f"Successfully loaded {len(layers)} layers from config")
        return config

    def _parse_layer_config(self, layer_data: Dict[str, Any]) -> LayerConfig:
        """Parse a single layer configuration.

        Args:
            layer_data: Layer data from JSON

        Returns:
            LayerConfig object
        """
        required_keys = ['id', 'name', 'description', 'nodes']
        for key in required_keys:
            if key not in layer_data:
                raise ValueError(f"Layer config missing required key: {key}")

        if not isinstance(layer_data['nodes'], list):
            raise ValueError(f"Layer '{layer_data['id']}' nodes must be a list")

        # Parse nodes
        nodes = []
        for node_data in layer_data['nodes']:
            node_config = self._parse_node_config(node_data)
            nodes.append(node_config)

        return LayerConfig(
            layer_id=layer_data['id'],
            name=layer_data['name'],
            description=layer_data['description'],
            nodes=nodes
        )

    def _parse_node_config(self, node_data: Dict[str, Any]) -> NodeConfig:
        """Parse a single node configuration.

        Args:
            node_data: Node data from JSON

        Returns:
            NodeConfig object
        """
        required_keys = ['id', 'name', 'description', 'type',
                         'template_id', 'llm_config']
        for key in required_keys:
            if key not in node_data:
                raise ValueError(f"Node config missing required key: {key}")

        llm_config_data = node_data['llm_config']
        llm_config = self._parse_llm_config(llm_config_data)

        return NodeConfig(
            node_id=node_data['id'],
            name=node_data['name'],
            description=node_data['description'],
            node_type=node_data['type'],
            template_id=node_data['template_id'],
            llm_config=llm_config
        )

    def _parse_llm_config(self, llm_data: Dict[str, Any]) -> LLMConfig:
        """Parse LLM configuration from dictionary.

        Args:
            llm_data: LLM config data from JSON

        Returns:
            LLMConfig object
        """
        required_keys = ['model', 'temperature', 'reasoning_effort', 'max_tokens']
        for key in required_keys:
            if key not in llm_data:
                raise ValueError(f"LLM config missing required key: {key}")

        return LLMConfig(
            model=llm_data['model'],
            temperature=llm_data['temperature'],
            reasoning_effort=llm_data['reasoning_effort'],
            max_tokens=llm_data['max_tokens']
        )

    def load_template_config(self, file_path: str) -> Dict[str, Dict[str, Any]]:
        """Load template configuration from JSON file.

        Args:
            file_path: Path to the template configuration JSON file

        Returns:
            Dictionary mapping template IDs to template data

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the JSON is invalid
        """
        self.logger.info(f"Loading template config from {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Template config file not found: {file_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in template config file: {e}")

        if 'templates' not in data:
            raise ValueError("Template config missing 'templates' key")

        templates = data['templates']
        if not isinstance(templates, dict):
            raise ValueError("'templates' must be a dictionary")

        self.logger.info(f"Successfully loaded {len(templates)} templates from config")
        return templates

    def validate_schema(self, config: Dict[str, Any], schema_type: str) -> bool:
        """Perform basic schema validation on configuration data.

        Args:
            config: Configuration dictionary
            schema_type: Type of schema to validate against ('layer' or 'template')

        Returns:
            True if valid

        Raises:
            ValueError: If validation fails
        """
        if schema_type == 'layer':
            return self._validate_layer_schema(config)
        elif schema_type == 'template':
            return self._validate_template_schema(config)
        else:
            raise ValueError(f"Unknown schema type: {schema_type}")

    def _validate_layer_schema(self, config: Dict[str, Any]) -> bool:
        """Validate layer configuration schema."""
        if 'layers' not in config:
            raise ValueError("Layer config missing 'layers' key")

        if not isinstance(config['layers'], list):
            raise ValueError("'layers' must be a list")

        if len(config['layers']) == 0:
            raise ValueError("At least one layer must be defined")

        # Basic validation of each layer
        for i, layer in enumerate(config['layers']):
            if not isinstance(layer, dict):
                raise ValueError(f"Layer {i} must be a dictionary")

            required = ['id', 'name', 'description', 'nodes']
            for key in required:
                if key not in layer:
                    raise ValueError(f"Layer {i} missing required key: {key}")

            if not isinstance(layer['nodes'], list) or len(layer['nodes']) == 0:
                raise ValueError(f"Layer {i} must have at least one node")

        return True

    def _validate_template_schema(self, config: Dict[str, Any]) -> bool:
        """Validate template configuration schema."""
        if 'templates' not in config:
            raise ValueError("Template config missing 'templates' key")

        if not isinstance(config['templates'], dict):
            raise ValueError("'templates' must be a dictionary")

        if len(config['templates']) == 0:
            raise ValueError("At least one template must be defined")

        # Basic validation of each template
        for template_id, template in config['templates'].items():
            if not isinstance(template, dict):
                raise ValueError(f"Template '{template_id}' must be a dictionary")

            required = ['template', 'placeholders',
                        'metadata']
            for key in required:
                if key not in template:
                    raise ValueError(f"Template '{template_id}' missing required key: {key}")

            if not isinstance(template['placeholders'], list):
                raise ValueError(f"Template '{template_id}' "
                                 f"placeholders must be a list")

        return True
