"""Layer 2: Definition Generation - Genealogical Node

This module implements the Genealogical Node agent responsible for tracing
the historical origin and evolution of concepts.
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


class GenealogicalNode:
    """Genealogical Node agent for Layer 2 Definition Generation.

    The Genealogical Node traces the historical origin and evolution of concepts,
    identifying key contributors and paradigm shifts.
    """

    def __init__(self, network_config: Optional[NetworkConfig] = None):
        """Initialize the Genealogical Node agent.

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
                    temperature=0.4,  # Moderate temperature for historical analysis
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

    def _build_genealogical_prompt(self, question: str) -> str:
        """Build the genealogical analysis prompt for the LLM.

        Args:
            question: The reformulated question to analyze

        Returns:
            str: Complete genealogical analysis prompt
        """
        prompt = f"""You are a historical epistemologist specializing in the genealogy of concepts.

Your task is to provide a comprehensive historical account of the concept described in the question below. Trace its origin, evolution, and key contributors.

ANALYSIS FRAMEWORK:
1. ORIGIN: Identify the historical moment and context of emergence
2. EVOLUTION: Trace major developments and paradigm shifts
3. CONTRIBUTORS: Highlight key thinkers, researchers, and movements
4. CONTEXT: Explain how historical events shaped the concept's development

INSTRUCTIONS:
- Provide a chronological historical narrative
- Include specific dates, thinkers, and publications where relevant
- Explain how the concept evolved in response to intellectual and cultural changes
- Connect the concept's development to broader historical movements
- Maintain academic rigor and cite key developments
- Output a coherent historical narrative, not bullet points
- Limit your response to approximately 150 words

QUESTION: {question}

HISTORICAL ACCOUNT:"""

        return prompt

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
                reformulated_question.question[:100] + "..." if len(reformulated_question.question) > 100 else reformulated_question.question
            )

            # Build genealogical analysis prompt
            prompt = self._build_genealogical_prompt(reformulated_question.question)

            # Get LLM response
            raw_response = await self._get_llm_client().generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request
            )

            # Extract clean historical account
            historical_account = self._extract_historical_account(raw_response)

            self.logger.info(
                "Genealogical analysis completed | output_length=%d",
                len(historical_account)
            )

            return historical_account

        except LLMError as e:
            self.logger.warning(
                "LLM genealogical analysis failed | error=%s",
                e
            )
            raise LayerProcessingError(f"Genealogical analysis failed: {e}") from e
        except Exception as e:
            self.logger.error(
                "Unexpected error in genealogical analysis | error=%s",
                e
            )
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
        response = re.sub(r'^(Here is|The historical|Historical|Account is|The account is):\s*', '', response, flags=re.IGNORECASE)

        # Clean up punctuation
        response = response.strip('"\'')

        # Ensure minimum length
        if len(response) < 100:
            response += " (Note: This historical analysis may be incomplete due to response length constraints.)"

        return response