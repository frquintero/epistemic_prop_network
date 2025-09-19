"""Configuration validation for the EPN pipeline."""

from ..core.node import PipelineConfig
from .template_manager import TemplateManager
from epn_core.core.logging_config import get_logger


class Validator:
    """Validates EPN pipeline configurations for compatibility and correctness."""

    def __init__(self):
        """Initialize the validator."""
        self.logger = get_logger("Validator")

    def validate_layer_template_compatibility(
        self,
        layer_config: PipelineConfig,
        template_manager: TemplateManager
    ) -> bool:
        """Validate that all nodes in the layer config have corresponding templates.

        Args:
            layer_config: The pipeline configuration
            template_manager: The template manager with loaded templates

        Returns:
            True if compatible

        Raises:
            ValueError: If there are missing or extra templates
        """
        self.logger.info("Validating layer-template compatibility")

        # Collect all required template IDs from the layer config
        required_templates = set()
        for layer in layer_config.layers:
            for node in layer.nodes:
                required_templates.add(node.template_id)

        # Check that all required templates exist
        missing_templates = []
        for template_id in required_templates:
            if not template_manager.has_template(template_id):
                missing_templates.append(template_id)

        if missing_templates:
            raise ValueError(f"Missing templates for template_ids: {missing_templates}")

        # Check for extra templates (templates that don't correspond to any node)
        available_templates = set(template_manager.list_templates())
        extra_templates = available_templates - required_templates

        if extra_templates:
            self.logger.warning(
                f"Found templates for non-existent nodes: {extra_templates}")
            # This is a warning, not an error - extra templates are allowed

        self.logger.info(f"Validated {len(required_templates)} templates")
        return True

    def validate_pipeline_flow(self, layer_config: PipelineConfig) -> bool:
        """Validate that the pipeline data flow is logically sound.

        Args:
            layer_config: The pipeline configuration

        Returns:
            True if flow is valid

        Raises:
            ValueError: If the pipeline flow is invalid
        """
        self.logger.info("Validating pipeline data flow")

        if not layer_config.layers:
            raise ValueError("Pipeline must have at least one layer")

        # Check for duplicate layer IDs
        layer_ids = [layer.layer_id for layer in layer_config.layers]
        if len(layer_ids) != len(set(layer_ids)):
            duplicates = [lid for lid in layer_ids if layer_ids.count(lid) > 1]
            raise ValueError(f"Duplicate layer IDs found: {duplicates}")

        # Check for duplicate node IDs within and across layers
        all_node_ids = []
        for layer in layer_config.layers:
            layer_node_ids = [node.node_id for node in layer.nodes]

            # Check duplicates within layer
            if len(layer_node_ids) != len(set(layer_node_ids)):
                duplicates = [nid for nid in layer_node_ids
                              if layer_node_ids.count(nid) > 1]
                raise ValueError(
                    f"Duplicate node IDs in layer '{layer.layer_id}': {duplicates}")

            all_node_ids.extend(layer_node_ids)

        # Check duplicates across layers
        if len(all_node_ids) != len(set(all_node_ids)):
            duplicates = [nid for nid in all_node_ids if all_node_ids.count(nid) > 1]
            raise ValueError(f"Duplicate node IDs across layers: {duplicates}")

        # Validate layer connectivity (basic checks)
        for i, layer in enumerate(layer_config.layers):
            if len(layer.nodes) == 0:
                raise ValueError(f"Layer '{layer.layer_id}' has no nodes")

            # First layer should be able to accept raw input
            # Last layer should produce final output
            # Intermediate layers should handle data transformation
            # (More sophisticated validation could be added here)

        self.logger.info(f"Validated {len(layer_config.layers)} layers")
        return True

    def validate_llm_configs(self, layer_config: PipelineConfig) -> bool:
        """Validate that all LLM configurations are properly structured.

        Args:
            layer_config: The pipeline configuration

        Returns:
            True if all configs are valid

        Raises:
            ValueError: If any LLM config is invalid
        """
        self.logger.info("Validating LLM configurations")

        for layer in layer_config.layers:
            for node in layer.nodes:
                llm_config = node.llm_config

                # Check required fields
                required_fields = ['model', 'temperature',
                                   'reasoning_effort', 'max_tokens']
                for field in required_fields:
                    if not hasattr(llm_config, field):
                        raise ValueError(
                            f"Node '{node.node_id}' missing LLM config field: {field}")

                # Validate temperature range
                if not (0.0 <= llm_config.temperature <= 2.0):
                    raise ValueError(f"Node '{node.node_id}' temp "
                                     f"{llm_config.temperature} not in [0.0, 2.0]")

                # Validate max_tokens
                if llm_config.max_tokens <= 0:
                    raise ValueError(f"Node '{node.node_id}' max_tokens "
                                     f"{llm_config.max_tokens} must be > 0")

                # Validate reasoning_effort
                valid_efforts = ['low', 'medium', 'high', 'default']
                if llm_config.reasoning_effort not in valid_efforts:
                    raise ValueError(f"Node '{node.node_id}' reasoning_effort "
                                     f"'{llm_config.reasoning_effort}' invalid")

        self.logger.info("LLM configuration validation successful")
        return True

    def validate_complete_config(
        self,
        layer_config: PipelineConfig,
        template_manager: TemplateManager
    ) -> bool:
        """Run all validation checks on a complete configuration.

        Args:
            layer_config: The pipeline configuration
            template_manager: The template manager

        Returns:
            True if all validations pass

        Raises:
            ValueError: If any validation fails
        """
        self.logger.info("Running complete configuration validation")

        # Run all validation checks
        self.validate_pipeline_flow(layer_config)
        self.validate_llm_configs(layer_config)
        self.validate_layer_template_compatibility(layer_config, template_manager)

        self.logger.info("Complete configuration validation successful")
        return True
