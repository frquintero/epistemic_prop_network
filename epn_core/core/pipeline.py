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
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        """Initialize the pipeline.

        Args:
            config: Optional pipeline configuration. If None, must be loaded later.
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

    def load_config(self, layer_file: str, template_file: str) -> None:
        """Load pipeline configuration from JSON files.

        Args:
            layer_file: Path to layer configuration file
            template_file: Path to template configuration file
        """
        self.logger.info(f"Loading pipeline config from {layer_file} and {template_file}")

        # Load configurations
        layer_config = self.config_loader.load_layer_config(layer_file)
        template_config = self.config_loader.load_template_config(template_file)

        # Load templates
        self.template_manager.load_templates(template_config)

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
        # Find the next layer in the pipeline order
        try:
            current_index = self.layer_order.index(layer_id)
            if current_index + 1 >= len(self.layer_order):
                # This is the last layer, return final result
                return layer_output
            next_layer_id = self.layer_order[current_index + 1]
            next_layer = self.layers[next_layer_id]
        except (ValueError, KeyError):
            # Fallback for unknown layers
            return {
                'query': original_query,
                'input': layer_output
            }

        # Get the template placeholders expected by the next layer's nodes
        next_layer_inputs = {}

        for node in next_layer.nodes.values():
            # Extract placeholders from input_context instead of deprecated 'placeholders' field
            input_context = node.template.get('input_context', '')
            node_placeholders = []
            
            if isinstance(input_context, list):
                # For synthesis node with list input_context
                for context_item in input_context:
                    import re
                    found_placeholders = re.findall(r'\{(\w+)\}', context_item)
                    node_placeholders.extend(found_placeholders)
            else:
                # For other nodes with string input_context
                import re
                found_placeholders = re.findall(r'\{(\w+)\}', input_context)
                node_placeholders.extend(found_placeholders)

            # Map current layer outputs to next layer placeholders
            for placeholder in node_placeholders:
                if placeholder in next_layer_inputs:
                    continue  # Already mapped

                # Try to find a matching output from current layer
                if placeholder in layer_output:
                    # Direct match (e.g., 'reformulated_question' from layer1)
                    next_layer_inputs[placeholder] = layer_output[placeholder]
                elif len(layer_output) == 1:
                    # Single output, map to any unmatched placeholder
                    next_layer_inputs[placeholder] = list(layer_output.values())[0]
                else:
                    # Multiple outputs, try node-specific mapping
                    # Look for node names that match placeholder patterns
                    for node_id, node_output in layer_output.items():
                        if placeholder.replace('_output', '_node') == node_id:
                            next_layer_inputs[placeholder] = node_output
                            break
                        elif placeholder.replace('_output', '') in node_id:
                            next_layer_inputs[placeholder] = node_output
                            break

        # If no specific mappings found, provide original query as fallback
        if not next_layer_inputs:
            next_layer_inputs = {
                'query': original_query,
                'input': layer_output
            }

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