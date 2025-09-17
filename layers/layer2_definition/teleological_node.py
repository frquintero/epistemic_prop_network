"""Layer 2: Definition Generation - Teleological Node

This module implements the Teleological Node agent responsible for analyzing
purpose, utility, and functional role of concepts.
"""

import os
import re
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import get_config, init_config, NetworkConfig
from core.exceptions import LayerProcessingError, LLMError, ConfigurationError
from core.llm_client import LLMClient, LLMConfig
from core.logging_config import get_logger
from core.schemas import ReformulatedQuestion
from core.template_manager import get_template_manager


class TeleologicalNode:
    """Teleological Node agent for Layer 2 Definition Generation.

    The Teleological Node analyzes the functional purpose and practical utility
    of concepts in real-world applications.
    """

    def __init__(self, network_config: Optional[NetworkConfig] = None, llm_config: Optional[LLMConfig] = None):
        """Initialize the Teleological Node agent.

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
                    temperature=0.5,  # Higher temperature for functional analysis
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
            if self.llm_config is not None:
                self.llm_client = LLMClient(config=self.llm_config)
            else:
                self.llm_client = LLMClient(network_config=self.config)
        return self.llm_client

    def _build_teleological_prompt(self, question: str) -> str:
        """Build the teleological analysis prompt for the LLM.

        Args:
            question: The reformulated question to analyze

        Returns:
            str: Complete teleological analysis prompt
        """
        template_manager = get_template_manager()
        return template_manager.render_template(
            layer="layer2",
            name="teleological_node",
            question=question
        )

    async def process(self, reformulated_question: ReformulatedQuestion) -> str:
        """Process a reformulated question to generate functional account.

        Args:
            reformulated_question: The reformulated question from Layer 1

        Returns:
            str: Functional/teleological output

        Raises:
            LayerProcessingError: If teleological analysis fails
        """
        try:
            self.logger.info(
                "Starting teleological analysis | question=%s",
                reformulated_question.question[:100] + "..." if len(reformulated_question.question) > 100 else reformulated_question.question
            )

            # Build teleological analysis prompt
            prompt = self._build_teleological_prompt(reformulated_question.question)

            # Get LLM response
            raw_response = await self._get_llm_client().generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request
            )

            # Extract clean functional account
            functional_account = self._extract_functional_account(raw_response)

            self.logger.info(
                "Teleological analysis completed | output_length=%d",
                len(functional_account)
            )

            return functional_account

        except LLMError as e:
            self.logger.warning(
                "LLM teleological analysis failed | error=%s",
                e
            )
            raise LayerProcessingError(f"Teleological analysis failed: {e}") from e
        except Exception as e:
            self.logger.error(
                "Unexpected error in teleological analysis | error=%s",
                e
            )
            raise LayerProcessingError(f"Teleological analysis failed: {e}") from e

    def _extract_functional_account(self, llm_response: str) -> str:
        """Extract the functional account from LLM response.

        Args:
            llm_response: Raw LLM response

        Returns:
            str: Cleaned functional account
        """
        # Remove any prefixes or explanations
        response = llm_response.strip()

        # Remove common LLM artifacts
        response = re.sub(r'^(Here is|The functional|Functional|Account is|The account is):\s*', '', response, flags=re.IGNORECASE)

        # Clean up punctuation
        response = response.strip('"\'')

        # Ensure minimum length
        if len(response) < 100:
            response += " (Note: This functional analysis may be incomplete due to response length constraints.)"

        return response