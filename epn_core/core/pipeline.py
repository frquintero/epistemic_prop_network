"""Pipeline class for orchestrating the entire EPN processing flow."""

import asyncio
from typing import Any, Dict, List, Optional
from pathlib import Path

from .layer import Layer, LayerConfig
from .node import Node, NodeConfig, PipelineConfig
from .node import Node, NodeConfig
from .factory import NodeFactory
from ..config.loader import ConfigLoader
from ..config.template_manager import TemplateManager
from ..config.validator import Validator
from epn_core.core.logging_config import get_logger


class Pipeline:
    """Main pipeline orchestrator for the Epistemological Propagation Network.

    The Pipeline manages the flow of data through sequential layers, each containing
    multiple nodes that can process data in parallel or sequentially.

    Configuration is automatically discovered: checks for layer.json/template.json at root,
    falls back to default configs if not found.
    """

    def __init__(self, config: Optional[PipelineConfig] = None, skip_autoload: bool = False):
        """Initialize the pipeline with automatic config discovery.

        Args:
            config: Optional pipeline configuration. If None, auto-discovers config files.
        """
        self.config = config
        self.logger = get_logger("Pipeline")
        self.layers: Dict[str, Layer] = {}
        self.layer_order: List[str] = []  # Maintains processing order

        # Initialize supporting components
        self.config_loader = ConfigLoader()
        self.template_manager = TemplateManager()
        self.validator = Validator()
        self.node_factory: Optional[NodeFactory] = None

        if config:
            self._build_from_config(config)
        else:
            # Auto-discover and load configuration unless caller requests skip
            if not skip_autoload:
                self._auto_load_config()

    def _auto_load_config(self) -> None:
        """Automatically discover and load configuration files.

        Checks for layer.json and template.json at project root.
        Falls back to default configs if root files don't exist.
        """
        layer_file, template_file = self._discover_config_files()

        try:
            self.load_config(layer_file, template_file)
            self.logger.info("Configuration loaded successfully")
        except Exception as e:
            self.logger.error(f"Failed to load configuration: {e}")
            raise

    def _discover_config_files(self) -> tuple[str, str]:
        """Discover configuration files with fallback to defaults.

        Returns:
            Tuple of (layer_file_path, template_file_path)
        """
        root_layer = Path("layer.json")
        root_template = Path("template.json")

        if root_layer.exists() and root_template.exists():
            self.logger.info("Using custom configuration files from project root")
            return str(root_layer), str(root_template)
        else:
            self.logger.info("Using default configuration files")
            return "epn_core/config/default_layer.json", "epn_core/config/default_template.json"

    def load_config(self, layer_file: str, template_file: str, replace_templates: bool = False) -> None:
        """Load pipeline configuration from JSON files.

        Args:
            layer_file: Path to layer configuration file
            template_file: Path to template configuration file
        """
        self.logger.info(f"Loading pipeline config from {layer_file} and {template_file}")

        # Load configurations
        layer_config = self.config_loader.load_layer_config(layer_file)
        template_config = self.config_loader.load_template_config(template_file)

        # Load templates (replace or merge)
        self.template_manager.load_templates(template_config, replace=replace_templates)

        # Validate configuration
        self.validator.validate_complete_config(layer_config, self.template_manager)

        # Create node factory
        self.node_factory = NodeFactory(self.template_manager)

        # Build the pipeline
        self._build_from_config(layer_config)

        self.logger.info("Pipeline configuration loaded and validated successfully")

    def _build_from_config(self, config: PipelineConfig) -> None:
        """Build the pipeline layers from configuration.

        Args:
            config: Pipeline configuration
        """
        if not self.node_factory:
            raise ValueError("Node factory not initialized. Call load_config() first.")

        self.layers = {}
        self.layer_order = []

        for layer_config in config.layers:
            layer = self._build_layer(layer_config)
            self.layers[layer_config.layer_id] = layer
            self.layer_order.append(layer_config.layer_id)

        self.logger.info(f"Built pipeline with {len(self.layers)} layers: {self.layer_order}")

    def _build_layer(self, layer_config: LayerConfig) -> Layer:
        """Build a layer with its nodes.

        Args:
            layer_config: Configuration for the layer

        Returns:
            Constructed Layer instance
        """
        layer = Layer(layer_config)

        for node_config in layer_config.nodes:
            node = self.node_factory.create_node(node_config)
            layer.add_node(node)

        return layer

    def add_layer(self, layer: Layer, position: Optional[int] = None) -> None:
        """Add a layer to the pipeline.

        Args:
            layer: The layer to add
            position: Position to insert at (None = append)
        """
        if layer.config.layer_id in self.layers:
            raise ValueError(f"Layer with id '{layer.config.layer_id}' already exists")

        self.layers[layer.config.layer_id] = layer

        if position is None:
            self.layer_order.append(layer.config.layer_id)
        else:
            self.layer_order.insert(position, layer.config.layer_id)

        self.logger.debug(f"Added layer {layer.config.layer_id} to pipeline")

    def get_layer(self, layer_id: str) -> Layer:
        """Get a layer by its ID.

        Args:
            layer_id: The layer identifier

        Returns:
            The requested layer

        Raises:
            KeyError: If layer doesn't exist
        """
        if layer_id not in self.layers:
            raise KeyError(f"Layer '{layer_id}' not found in pipeline")
        return self.layers[layer_id]

    async def process(self, input_data: Any) -> Any:
        """Process input data through the entire pipeline.

        Args:
            input_data: Initial input data

        Returns:
            Final output after processing through all layers
        """
        if not self.layers:
            raise ValueError("Pipeline has no layers configured")

        self.logger.info(f"Starting pipeline processing with {len(self.layer_order)} layers")

        # Store the original query for use throughout the pipeline
        original_query = input_data

        # Start with the original query as input for layer 1
        current_data = input_data
        layer_outputs = {}

        # Process each layer in order
        for layer_id in self.layer_order:
            layer = self.layers[layer_id]
            self.logger.info(f"Processing layer: {layer_id}")

            try:
                # Debug: show keys in current_data passed to this layer
                try:
                    if isinstance(current_data, dict):
                        self.logger.info(f"Input to layer '{layer_id}' keys: {list(current_data.keys())}")
                    else:
                        self.logger.info(f"Input to layer '{layer_id}' is a raw value of type {type(current_data).__name__}")
                except Exception:
                    pass

                layer_output = await layer.process(current_data)
                layer_outputs[layer_id] = layer_output

                # For the next layer, prepare input that includes both original query and layer output
                current_data = self._prepare_input_for_next_layer(original_query, layer_output, layer_id)

            except Exception as e:
                self.logger.error(f"Pipeline failed at layer {layer_id}: {e}")
                raise

        self.logger.info("Pipeline processing completed successfully")
        return current_data  # Return the final processed data

    def _prepare_input_for_next_layer(self, original_query: str, layer_output: Dict[str, Any], layer_id: str) -> Dict[str, Any]:
        """Prepare the input for the next layer by mapping current layer outputs to next layer's expected inputs.

        This method automatically maps layer outputs to the template placeholders expected by the next layer,
        ensuring consistent behavior regardless of layer count or node configuration.

        Args:
            original_query: The original input query
            layer_output: Output dictionary from the current layer (node_id -> output)
            layer_id: ID of the current layer

        Returns:
            Input data for the next layer as a dictionary matching next layer's template placeholders
        """
        # Find the next layer in the pipeline order; if this is the last layer return result
        try:
            current_index = self.layer_order.index(layer_id)
            if current_index + 1 >= len(self.layer_order):
                return layer_output
            next_layer_id = self.layer_order[current_index + 1]
            next_layer = self.layers[next_layer_id]
        except (ValueError, KeyError):
            # Unknown layer ordering — return a generic input shape
            return {'query': original_query, 'input': layer_output}

        # Prepare strict mapping: placeholders must correspond exactly to keys in layer_output
        next_layer_inputs: Dict[str, Any] = {}

        # Always allow access to the original query
        next_layer_inputs['query'] = original_query

        # Iterate nodes in the next layer and collect required placeholders
        import re
        for node in next_layer.nodes.values():
            input_context = node.template.get('input_context', '')
            node_placeholders: List[str] = []

            if isinstance(input_context, list):
                for context_item in input_context:
                    node_placeholders.extend(re.findall(r'\{([^}]+)\}', context_item))
            else:
                node_placeholders.extend(re.findall(r'\{([^}]+)\}', str(input_context)))

            for placeholder in node_placeholders:
                # Skip if already mapped
                if placeholder in next_layer_inputs:
                    continue

                # Allowed globals
                if placeholder == 'query':
                    next_layer_inputs['query'] = original_query
                    continue
                if placeholder == 'input':
                    # provide the entire previous layer output under 'input'
                    next_layer_inputs['input'] = layer_output
                    continue

                # Strict match: placeholder must be present in layer_output keys
                if isinstance(layer_output, dict) and placeholder in layer_output:
                    next_layer_inputs[placeholder] = layer_output[placeholder]
                    continue

                # If we reach here, placeholder cannot be satisfied — raise descriptive error
                raise ValueError(
                    f"Pipeline configuration error: placeholder '{{{placeholder}}}' required by node '{node.config.node_id}' in layer '{next_layer_id}' "
                    f"is not present in outputs from previous layer '{layer_id}'. Available outputs: {sorted(list(layer_output.keys()))}"
                )

        return next_layer_inputs

    def validate_pipeline(self) -> bool:
        """Validate that the pipeline is properly configured.

        Returns:
            True if valid, raises exception if invalid
        """
        if not self.layers:
            raise ValueError("Pipeline has no layers")

        if not self.layer_order:
            raise ValueError("Pipeline has no layer order defined")

        # Validate each layer
        for layer_id, layer in self.layers.items():
            try:
                layer.validate_layer()
            except Exception as e:
                raise ValueError(f"Layer {layer_id} validation failed: {e}")

        # Check that all layers in order_order exist
        for layer_id in self.layer_order:
            if layer_id not in self.layers:
                raise ValueError(f"Layer '{layer_id}' in order but not in layers dict")

        self.logger.info("Pipeline validation successful")
        return True

    def __repr__(self) -> str:
        layer_info = ", ".join([f"{lid}({len(self.layers[lid].nodes)} nodes)" for lid in self.layer_order])
        return f"Pipeline(layers=[{layer_info}])"