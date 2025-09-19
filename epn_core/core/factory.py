"""Factory for creating nodes dynamically."""

from ..core.node import Node, NodeConfig
from .nodes import BasicLLMNode
from ..config.template_manager import TemplateManager
from epn_core.core.logging_config import get_logger


class NodeFactory:
    """Factory for creating node instances based on configuration and templates."""

    def __init__(self, template_manager: TemplateManager):
        """Initialize the node factory.

        Args:
            template_manager: The template manager with loaded templates
        """
        self.template_manager = template_manager
        self.logger = get_logger("NodeFactory")

        # All nodes use the same BasicLLMNode class - fully dynamic
        self.node_class = BasicLLMNode

    def create_node(self, config: NodeConfig) -> Node:
        """Create a node instance from configuration.

        Args:
            config: Node configuration

        Returns:
            Instantiated node

        Raises:
            ValueError: If template is missing or node type is unknown
        """
        self.logger.debug(f"Creating node: {config.node_id}")

        # Get the template for this node
        try:
            template = self.template_manager.get_template(config.template_id)
        except KeyError:
            raise ValueError(f"No template found for node '{config.node_id}' "
                             f"(template_id: {config.template_id})")

        # Determine node type - use BasicLLMNode for all types (fully dynamic)
        node_class = BasicLLMNode

        self.logger.debug(f"Using node class: {node_class.__name__}")

        # Create and return the node
        try:
            node = node_class(config, template)
            self.logger.info(f"Successfully created node: {config.node_id}")
            return node
        except Exception as e:
            self.logger.error(f"Failed to create node {config.node_id}: {e}")
            raise

    def register_node_type(self, node_id: str, node_class: type) -> None:
        """Register a custom node type.

        Note: The system now uses BasicLLMNode for all node types by default.
        Custom node classes can still be registered for specific use cases.

        Args:
            node_id: The node identifier this class handles
            node_class: The node class to instantiate
        """
        if not issubclass(node_class, Node):
            raise ValueError(f"Node class {node_class} must inherit from Node")

        # For backward compatibility, allow custom node types
        # But the system is designed to work with BasicLLMNode for all types
        self.logger.warning(
            f"Custom node type deprecated. Using BasicLLMNode for {node_id}")
        # Still create the node with the custom class if requested
        # This maintains backward compatibility but encourages using BasicLLMNode

    def get_available_node_types(self) -> list[str]:
        """Get list of available node types.

        Returns:
            Note: All node types are supported dynamically through templates.
            This method returns a sample of common types for reference.
        """
        # Since the system is fully dynamic, return common types as examples
        return ['reformulator', 'semantic', 'genealogical',
                'synthesis', 'validator', 'custom']
