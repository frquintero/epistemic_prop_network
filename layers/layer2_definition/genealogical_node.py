"""Layer 2: Definition Generation - Genealogical Node

This module implements the Genealogical Node agent responsible for tracing
the historical origin and evolution of concepts.
"""

import os
import re
from datetime import datetime
from typing import Any, Dict, Optional

from core.config import NetworkConfig, get_config, init_config
from core.exceptions import ConfigurationError, LayerProcessingError, LLMError
from core.llm_client import LLMClient, LLMConfig
from core.logging_config import get_logger
from core.schemas import ReformulatedQuestion
from core.template_manager import get_template_manager


class GenealogicalNode:
    """Genealogical Node agent for Layer 2 Definition Generation.

    The Genealogical Node traces the historical development and evolution
    of concepts through intellectual history.
    """

    def __init__(
        self,
        network_config: Optional[NetworkConfig] = None,
        llm_config: Optional[LLMConfig] = None,
    ):
        """Initialize the Genealogical Node agent.

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
                init_config(
                    NetworkConfig(
                        groq_api_key=fallback_key,
                        groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
                        max_concurrent_requests=int(
                            os.getenv("MAX_CONCURRENT_REQUESTS", "1")
                        ),
                        temperature=0.4,  # Moderate temperature for historical analysis
                        max_tokens_per_request=2048,
                        reasoning_effort="medium",
                        enable_structured_logging=True,
                        debug_mode=False,
                        mock_responses=False,
                    )
                )
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

    def _build_genealogical_prompt(self, reformulated_question: str) -> str:
        """Build the genealogical analysis prompt for the LLM.

        Args:
            reformulated_question: The reformulated question to analyze

        Returns:
            str: Complete genealogical analysis prompt
        """
        template_manager = get_template_manager()
        return template_manager.render_template(
            layer="layer2",
            name="genealogical_node",
            reformulated_question=reformulated_question,
        )

    async def process(self, reformulated_question: ReformulatedQuestion) -> str:
        """Process a reformulated question to generate historical account.

        Args:
            reformulated_question: The reformulated question from Layer 1

        Returns:
            str: Historical/genealogical output

        Raises:
            LayerProcessingError: If genealogical analysis fails
        """
        try:
            self.logger.info(
                "Starting genealogical analysis | question=%s",
                (
                    reformulated_question.question[:100] + "..."
                    if len(reformulated_question.question) > 100
                    else reformulated_question.question
                ),
            )

            # Build genealogical analysis prompt
            prompt = self._build_genealogical_prompt(reformulated_question.question)

            # Get LLM response
            raw_response = await self._get_llm_client().generate_text(
                prompt=prompt, max_tokens=self.config.max_tokens_per_request
            )

            # Extract clean historical account
            historical_account = self._extract_historical_account(raw_response)

            self.logger.info(
                "Genealogical analysis completed | output_length=%d",
                len(historical_account),
            )

            return historical_account

        except LLMError as e:
            self.logger.warning("LLM genealogical analysis failed | error=%s", e)
            raise LayerProcessingError(f"Genealogical analysis failed: {e}") from e
        except Exception as e:
            self.logger.error("Unexpected error in genealogical analysis | error=%s", e)
            raise LayerProcessingError(f"Genealogical analysis failed: {e}") from e

    def _extract_historical_account(self, llm_response: str) -> str:
        """Extract the historical account from LLM response.

        Args:
            llm_response: Raw LLM response

        Returns:
            str: Cleaned historical account
        """
        # Remove any prefixes or explanations
        response = llm_response.strip()

        # Remove common LLM artifacts
        response = re.sub(
            r"^(Here is|The historical|Historical|Account is|The account is):\s*",
            "",
            response,
            flags=re.IGNORECASE,
        )

        # Clean up punctuation
        response = response.strip("\"'")

        # Ensure minimum length
        if len(response) < 100:
            response += " (Note: This historical analysis may be incomplete due to response length constraints.)"

        return response
