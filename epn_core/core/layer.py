"""Layer class for managing collections of nodes."""

import asyncio
from typing import Any, Dict, List, Optional
from enum import Enum

from .node import LayerConfig, Node, NodeConfig
from epn_core.core.logging_config import get_logger


class ExecutionMode(Enum):
    """Execution modes for layer processing."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"


class Layer:
    """A layer that manages and orchestrates multiple processing nodes.

    Layers can execute nodes either sequentially or in parallel, and handle
    the flow of data between nodes within the layer.
    """

    def __init__(self, config: LayerConfig, execution_mode: ExecutionMode = ExecutionMode.PARALLEL):
        """Initialize the layer.

        Args:
            config: Layer configuration
            execution_mode: How to execute nodes (sequential or parallel)
        """
        self.config = config
        self.execution_mode = execution_mode
        self.logger = get_logger(f"Layer({config.layer_id})")
        self.nodes: Dict[str, Node] = {}

    def add_node(self, node: Node) -> None:
        """Add a node to this layer.

        Args:
            node: The node to add
        """
        if node.config.node_id in self.nodes:
            raise ValueError(f"Node with id '{node.config.node_id}' already exists in layer {self.config.layer_id}")

        self.nodes[node.config.node_id] = node
        self.logger.debug(f"Added node {node.config.node_id} to layer {self.config.layer_id}")

    def get_node(self, node_id: str) -> Node:
        """Get a node by its ID.

        Args:
            node_id: The node identifier

        Returns:
            The requested node

        Raises:
            KeyError: If node doesn't exist
        """
        if node_id not in self.nodes:
            raise KeyError(f"Node '{node_id}' not found in layer {self.config.layer_id}")
        return self.nodes[node_id]

    async def process(self, input_data: Any) -> Dict[str, Any]:
        """Process input data through all nodes in this layer.

        Args:
            input_data: Input data for the layer

        Returns:
            Dictionary mapping node IDs to their outputs
        """
        self.logger.info(f"Processing layer {self.config.layer_id} with {len(self.nodes)} nodes")

        if self.execution_mode == ExecutionMode.SEQUENTIAL:
            return await self._process_sequential(input_data)
        else:  # PARALLEL
            return await self._process_parallel(input_data)

    async def _process_sequential(self, input_data: Any) -> Dict[str, Any]:
        """Process nodes sequentially, passing data between them.

        Args:
            input_data: Initial input data

        Returns:
            Dictionary of node outputs
        """
        results = {}
        current_data = input_data

        for node_id, node in self.nodes.items():
            self.logger.debug(f"Processing node {node_id} sequentially")
            try:
                output = await node.process(current_data)
                results[node_id] = output
                current_data = output  # Pass output to next node
            except Exception as e:
                self.logger.error(f"Error processing node {node_id}: {e}")
                raise

        return results

    async def _process_parallel(self, input_data: Any) -> Dict[str, Any]:
        """Process all nodes in parallel with the same input data.

        Args:
            input_data: Input data for all nodes

        Returns:
            Dictionary of node outputs
        """
        tasks = []
        node_ids = []

        for node_id, node in self.nodes.items():
            self.logger.debug(f"Creating parallel task for node {node_id}")
            task = asyncio.create_task(node.process(input_data))
            tasks.append(task)
            node_ids.append(node_id)

        # Wait for all tasks to complete
        try:
            outputs = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            self.logger.error(f"Error in parallel processing: {e}")
            raise

        # Build results dictionary
        results = {}
        for node_id, output in zip(node_ids, outputs):
            if isinstance(output, Exception):
                self.logger.error(f"Node {node_id} failed with exception: {output}")
                raise output
            results[node_id] = output

        self.logger.info(f"Layer {self.config.layer_id} completed parallel processing")
        return results

    def validate_layer(self) -> bool:
        """Validate that the layer is properly configured.

        Returns:
            True if valid, raises exception if invalid
        """
        if not self.nodes:
            raise ValueError(f"Layer {self.config.layer_id} has no nodes")

        # Check for duplicate node IDs (shouldn't happen with add_node, but safety check)
        node_ids = [node.config.node_id for node in self.nodes.values()]
        if len(node_ids) != len(set(node_ids)):
            raise ValueError(f"Layer {self.config.layer_id} has duplicate node IDs")

        return True

    def __repr__(self) -> str:
        return f"Layer(id='{self.config.layer_id}', name='{self.config.name}', nodes={len(self.nodes)}, mode={self.execution_mode.value})"