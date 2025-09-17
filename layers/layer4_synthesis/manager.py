"""Layer 4: Synthesis & Communication - Manager

This module implements the Layer4SynthesisManager responsible for orchestrating
the final synthesis processing that integrates validated insights into holistic narratives.
"""

import asyncio
import os
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import get_config, init_config, NetworkConfig
from core.exceptions import LayerProcessingError, LLMError, ConfigurationError
from core.logging_config import get_logger
from core.llm_client import LLMConfig
from core.schemas import Phase3Triple, SynthesisOutput

from .synthesis_node import SynthesisNode


class Layer4SynthesisManager:
    """Manager for Layer 4 Synthesis & Communication processing.

    Orchestrates the final synthesis that integrates validated outputs from all
    previous layers into holistic narratives with epistemological rigor.
    """

    def __init__(self, network_config: Optional[NetworkConfig] = None, llm_config: Optional[LLMConfig] = None):
        """Initialize the Layer 4 Synthesis Manager.

        Args:
            network_config: Optional network configuration. If None, uses default config.
            llm_config: Optional LLM configuration for synthesis node.
        """
        self.logger = get_logger(__name__)
        self.network_config = network_config
        self.llm_config = llm_config
        self._config: Optional[NetworkConfig] = None

        # Initialize the synthesis node
        self.synthesis_node = SynthesisNode(network_config=self.config, llm_config=self.llm_config)

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

    async def process(self, phase3_triple: Phase3Triple) -> SynthesisOutput:
        """Process a Phase 3 triple through the synthesis node.

        Args:
            phase3_triple: The validated triple from Layer 3

        Returns:
            SynthesisOutput: Complete synthesis with narrative and thesis

        Raises:
            LayerProcessingError: If synthesis processing fails
        """
        try:
            self.logger.info("Starting Layer 4 synthesis processing")

            start_time = datetime.now()

            # Process through synthesis node
            synthesis_output = await self.synthesis_node.process(phase3_triple)

            processing_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                "Layer 4 synthesis processing completed | processing_time=%.2fs",
                processing_time
            )

            return synthesis_output

        except Exception as e:
            self.logger.error(
                "Layer 4 synthesis processing failed | error=%s",
                str(e)
            )
            raise LayerProcessingError(f"Layer 4 synthesis failed: {e}") from e

    def _handle_processing_error(
        self,
        error: Exception,
        context: str
    ) -> SynthesisOutput:
        """Handle processing errors with fallback synthesis output.

        Args:
            error: The exception that occurred
            context: Context information about where the error occurred

        Returns:
            SynthesisOutput: Fallback synthesis output
        """
        self.logger.warning(
            "Synthesis processing error, generating fallback | context=%s | error=%s",
            context,
            str(error)
        )

        return SynthesisOutput(
            thesis="Due to processing limitations, a complete synthesis could not be generated.",
            definition="Definition component unavailable due to processing error.",
            history="Historical component unavailable due to processing error.",
            function="Functional component unavailable due to processing error.",
            validation_qualifications="Validation component unavailable due to processing error.",
            narrative=f"Synthesis processing encountered an error: {str(error)}. The epistemological network was unable to complete the final integration step."
        )