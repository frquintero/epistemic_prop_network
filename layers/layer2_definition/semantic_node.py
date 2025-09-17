"""Layer 2: Definition Generation - Semantic Node

This module implements the Semantic Node agent responsible for generating
precise conceptual definitions with linguistic structure, etymology,
and logical relationships.
"""

import os
import re
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import get_config, init_config, NetworkConfig
from core.exceptions import LayerProcessingError, LLMError, ConfigurationError
from core.llm_client import LLMClient
from core.logging_config import get_logger
from core.schemas import ReformulatedQuestion
from core.template_manager import get_template_manager


class SemanticNode:
    """Semantic Node agent for Layer 2 Definition Generation.

    The Semantic Node focuses on linguistic structure, etymology, and logical
    relationships to produce strict conceptual definitions.
    """

    def __init__(self, network_config: Optional[NetworkConfig] = None):
        """Initialize the Semantic Node agent.

        Args:
            network_config: Optional network configuration. If None, uses default config.
        """
        self.logger = get_logger(__name__)
        self.llm_client: Optional[LLMClient] = None
        self.network_config = network_config
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
                    temperature=0.3,  # Lower temperature for precise definitions
                    max_tokens_per_request=2048,
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
            self.llm_client = LLMClient(network_config=self.config)
        return self.llm_client

    def _build_semantic_prompt(self, question: str) -> str:
        """Build the semantic analysis prompt for the LLM.

        Args:
            question: The reformulated question to analyze

        Returns:
            str: Complete semantic analysis prompt
        """
        template_manager = get_template_manager()
        return template_manager.render_template(
            layer="layer2",
            name="semantic_node",
            question=question
        )

    async def process(self, reformulated_question: ReformulatedQuestion) -> str:
        """Process a reformulated question to generate semantic definition.

        Args:
            reformulated_question: The reformulated question from Layer 1

        Returns:
            str: Semantic definition output

        Raises:
            LayerProcessingError: If semantic analysis fails
        """
        try:
            self.logger.info(
                "Starting semantic analysis | question=%s",
                reformulated_question.question[:100] + "..." if len(reformulated_question.question) > 100 else reformulated_question.question
            )

            # Build semantic analysis prompt
            prompt = self._build_semantic_prompt(reformulated_question.question)

            # Get LLM response
            raw_response = await self._get_llm_client().generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request
            )

            # Extract clean semantic definition
            semantic_definition = self._extract_semantic_definition(raw_response)

            self.logger.info(
                "Semantic analysis completed | output_length=%d",
                len(semantic_definition)
            )

            return semantic_definition

        except LLMError as e:
            self.logger.warning(
                "LLM semantic analysis failed | error=%s",
                e
            )
            raise LayerProcessingError(f"Semantic analysis failed: {e}") from e
        except Exception as e:
            self.logger.error(
                "Unexpected error in semantic analysis | error=%s",
                e
            )
            raise LayerProcessingError(f"Semantic analysis failed: {e}") from e

    def _extract_semantic_definition(self, llm_response: str) -> str:
        """Extract the semantic definition from LLM response.

        Args:
            llm_response: Raw LLM response

        Returns:
            str: Cleaned semantic definition
        """
        # Remove any prefixes or explanations
        response = llm_response.strip()

        # Remove common LLM artifacts
        response = re.sub(r'^(Here is|The semantic|Semantic|Definition is|The definition is):\s*', '', response, flags=re.IGNORECASE)

        # Clean up punctuation
        response = response.strip('"\'')

        # Ensure minimum length
        if len(response) < 50:
            response += " (Note: This semantic analysis may be incomplete due to response length constraints.)"

        return response