"""Core classes for the Epistemological Propagation Network.

This module contains the fundamental OOP classes that make up the configurable EPN system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass

from epn_core.core.llm_client import LLMClient, LLMConfig
from epn_core.core.logging_config import get_logger


@dataclass
class NodeConfig:
    """Configuration for a processing node."""
    node_id: str
    name: str
    description: str
    node_type: str
    template_id: str
    llm_config: LLMConfig


@dataclass
class LayerConfig:
    """Configuration for a processing layer."""
    layer_id: str
    name: str
    description: str
    nodes: list[NodeConfig]


@dataclass
class PipelineConfig:
    """Configuration for the entire pipeline."""
    layers: list[LayerConfig]


class Node(ABC):
    """Abstract base class for all processing nodes in the EPN.

    A Node represents a single LLM processing unit that takes input,
    applies a prompt template, and returns processed output.
    """

    def __init__(self, config: NodeConfig, template: Dict[str, Any]):
        """Initialize the node.

        Args:
            config: Node configuration with LLM settings
            template: Template dictionary with 'template' and 'placeholders'
        """
        self.config = config
        self.template = template
        self.logger = get_logger(f"{self.__class__.__name__}({config.node_id})")

        # Initialize LLM client
        self.llm_client = LLMClient(config.llm_config)

        # Validate template compatibility
        self._validate_template()

    def _validate_template(self) -> None:
        """Validate that the template is compatible with this node."""
        required_keys = ['node_epistemic_task', 'input_context', 'expected_output']
        for key in required_keys:
            if key not in self.template:
                raise ValueError(f"Template missing '{key}' key for node {self.config.node_id}")

    def _render_prompt(self, variables: Dict[str, Any]) -> str:
        """Render the prompt template with provided variables.

        Args:
            variables: Dictionary of variable names to values

        Returns:
            Rendered prompt string in the format:
            [TASK] ... [CONTEXT] ... [EXPECTED OUTPUT] ... [INSTRUCTIONS] ...
        """
        # Start building the prompt
        prompt_parts = []
        
        # Add TASK section
        prompt_parts.append(f"[TASK] {self.template['node_epistemic_task']}")
        
        # Add CONTEXT section - handle both string and list input_context
        input_context = self.template['input_context']
        
        if isinstance(input_context, list):
            # For lists, process each item and join them
            context_parts = []
            for context_item in input_context:
                processed_item = context_item
                for var_name, var_value in variables.items():
                    processed_item = processed_item.replace(f"{{{var_name}}}", str(var_value))
                context_parts.append(processed_item)
            context = "\n\n".join(context_parts)
        else:
            # For strings, replace placeholders directly
            context = input_context
            for var_name, var_value in variables.items():
                context = context.replace(f"{{{var_name}}}", str(var_value))
        
        prompt_parts.append(f"[CONTEXT] {context}")
        
        # Add EXPECTED OUTPUT section
        prompt_parts.append(f"[EXPECTED OUTPUT] {self.template['expected_output']}")
        
        # Add INSTRUCTIONS section if present - handle as list
        if 'instructions' in self.template and self.template['instructions']:
            if isinstance(self.template['instructions'], list):
                instructions_text = "; ".join(self.template['instructions'])
            else:
                instructions_text = self.template['instructions']
            prompt_parts.append(f"[INSTRUCTIONS] {instructions_text}")
        
        return "\n\n".join(prompt_parts)

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data and return output.

        Args:
            input_data: Input data for this node

        Returns:
            Processed output data
        """
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id='{self.config.node_id}', name='{self.config.name}')"