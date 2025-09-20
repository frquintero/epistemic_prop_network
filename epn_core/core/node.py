"""Core classes for the Epistemological Propagation Network.

This module contains the fundamental OOP classes that make up the configurable EPN system.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import json
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
        # Require the canonical 'template' key for the LLM task text
        if 'template' not in self.template:
            raise ValueError(f"Template missing required 'template' key for node {self.config.node_id}")

        required_keys = ['template', 'input_context', 'expected_output']
        for key in required_keys:
            if key not in self.template:
                raise ValueError(f"Template missing '{key}' key for node {self.config.node_id}")

    def _render_prompt(self, variables: Dict[str, Any]) -> str:
        """Return the raw template text and raw I/O metadata.

        This method intentionally avoids performing any placeholder substitution
        or structural rendering. It returns the bare `template` text followed
        by a compact JSON object that includes `expected_output` and the
        `raw_inputs` dictionary so downstream tools or the LLM client can
        decide how to combine them.

        Args:
            variables: Dictionary of variable names to values

        Returns:
            A string containing the raw template text, two newlines, and a
            compact JSON object with `expected_output` and `raw_inputs`.
        """

        # Raw template text (placeholders kept intact)
        template_text = str(self.template.get('template', ''))

        # Prepare metadata with expected output name and the raw inputs
        metadata = {
            'expected_output': self.template.get('expected_output'),
            'raw_inputs': variables,
            'instructions': self.template.get('instructions')
        }

        try:
            metadata_json = json.dumps(metadata, ensure_ascii=False)
        except Exception:
            metadata_json = str(metadata)

        # Return raw template followed by compact metadata
        return f"{template_text}\n\n{metadata_json}"

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