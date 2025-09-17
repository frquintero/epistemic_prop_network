"""Layer 4: Synthesis & Communication - Synthesis Node

This module implements the Synthesis Node agent responsible for integrating
validated insights from all previous layers into holistic narratives with
epistemological rigor.
"""

import os
import re
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import get_config, init_config, NetworkConfig
from core.exceptions import LayerProcessingError, LLMError, ConfigurationError
from core.llm_client import LLMClient, LLMConfig
from core.logging_config import get_logger
from core.schemas import Phase3Triple, SynthesisOutput
from core.template_manager import get_template_manager


class SynthesisNode:
    """Synthesis Node agent for Layer 4 Synthesis & Communication.

    The Synthesis Node integrates validated outputs from all previous layers
    into holistic narratives that provide meaning, context, and value,
    culminating in a thesis statement.
    """

    def __init__(self, network_config: Optional[NetworkConfig] = None, llm_config: Optional[LLMConfig] = None):
        """Initialize the Synthesis Node agent.

        Args:
            network_config: Optional network configuration. If None, uses default config.
            llm_config: Optional LLM configuration. If provided, used to create LLM client.
        """
        self.logger = get_logger(__name__)
        self.llm_client: Optional[LLMClient] = None
        self.network_config = network_config
        self.llm_config = llm_config
        self._config: Optional[NetworkConfig] = None

    @property
    def config(self):
        """Lazy-load network configuration to avoid premature initialization."""
        if self._config is None:
            try:
                self._config = get_config()
            except RuntimeError as exc:
                # Attempt to initialize configuration lazily using environment defaults
                fallback_key = os.getenv("GROQ_API_KEY", "test_api_key")
                init_config(NetworkConfig(
                    groq_api_key=fallback_key,
                    groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                    max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "1")),
                    temperature=0.3,  # Lower temperature for consistent synthesis
                    max_tokens_per_request=4096,  # Higher token limit for comprehensive synthesis
                    reasoning_effort="medium",
                    enable_structured_logging=True,
                    debug_mode=False,
                    mock_responses=False
                ))
                self._config = get_config()
        return self._config

    def _get_llm_client(self) -> LLMClient:
        """Get or create LLM client instance."""
        if self.llm_client is None:
            if self.llm_config is not None:
                self.llm_client = LLMClient(config=self.llm_config)
            else:
                self.llm_client = LLMClient(network_config=self.config)
        return self.llm_client

    def _build_synthesis_prompt(self, phase3_triple: Phase3Triple) -> str:
        """Build the synthesis prompt for the LLM.

        Args:
            phase3_triple: The validated triple from Layer 3

        Returns:
            str: Complete synthesis prompt
        """
        template_manager = get_template_manager()
        return template_manager.render_template(
            layer="layer4",
            name="synthesis_node",
            phase3_triple_correspondence=phase3_triple.correspondence,
            phase3_triple_coherence=phase3_triple.coherence,
            phase3_triple_pragmatic=phase3_triple.pragmatic
        )

    async def process(self, phase3_triple: Phase3Triple) -> SynthesisOutput:
        """Process a Phase 3 triple to generate final synthesis output.

        Args:
            phase3_triple: The validated triple from Layer 3

        Returns:
            SynthesisOutput: Complete synthesis with narrative and thesis

        Raises:
            LayerProcessingError: If synthesis fails
        """
        try:
            self.logger.info("Starting epistemological synthesis")

            # Build synthesis prompt
            prompt = self._build_synthesis_prompt(phase3_triple)

            # Get LLM response
            raw_response = await self._get_llm_client().generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request
            )

            # Return raw synthesis output as originally planned
            synthesis_output = SynthesisOutput(raw_response=raw_response)

            self.logger.info(
                "Epistemological synthesis completed | raw_response_length=%d",
                len(synthesis_output.raw_response)
            )

            return synthesis_output

        except LLMError as e:
            self.logger.warning("LLM synthesis failed | error=%s", e)
            raise LayerProcessingError(f"Synthesis failed: {e}") from e
        except Exception as e:
            self.logger.error("Unexpected error in synthesis | error=%s", e)
            raise LayerProcessingError(f"Synthesis failed: {e}") from e