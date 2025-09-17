"""Pragmatic Validator for Layer 3 - Evaluates real-world applicability."""

import asyncio
import logging
from typing import Dict, Any, Optional

from core.llm_client import LLMClient
from core.schemas import Phase2Triple, Phase3Triple
from core.config import get_config
from core.logging_config import get_logger

logger = None


class PragmaticValidator:
    """Validates practical utility and real-world applicability of outputs."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the Pragmatic Validator.

        Args:
            llm_client: Optional LLM client instance. If None, creates a new one.
        """
        self.llm_client = llm_client or LLMClient()
        self.config = get_config()

    async def process(self, phase2_triple: Phase2Triple) -> str:
        """Process Phase 2 triple and validate pragmatic utility.

        Args:
            phase2_triple: The triple containing semantic, genealogical, and teleological outputs

        Returns:
            Validation narrative assessing practical utility
        """
        global logger
        if logger is None:
            logger = get_logger(__name__)
        logger.info("Starting pragmatic validation")

        prompt = self._build_pragmatic_prompt(phase2_triple)

        try:
            response = await self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request,
            )

            logger.info("Pragmatic validation completed | output_length=%d", len(response))
            return response

        except Exception as e:
            logger.error("Pragmatic validation failed | error=%s", str(e))
            return self._get_fallback_response()

    def _build_pragmatic_prompt(self, phase2_triple: Phase2Triple) -> str:
        """Build the pragmatic validation prompt.

        Args:
            phase2_triple: The triple to validate

        Returns:
            Formatted prompt for LLM
        """
        return f"""You are the Pragmatic Validator in an epistemological network. Your task is to assess the practical utility and real-world applicability of the following conceptual framework.

Integrate in a unified narrative the following triple and evaluate the pragmatic value across domains:

SEMANTIC DEFINITION:
{phase2_triple.semantic}

GENEALOGICAL ACCOUNT:
{phase2_triple.genealogical}

TELEOLOGICAL ANALYSIS:
{phase2_triple.teleological}

Provide a detailed pragmatic assessment that:
1. Evaluates utility in practical domains (education, business, technology, policy)
2. Assesses whether the framework enables actionable decision-making
3. Determines if historical insights inform current applications
4. Identifies concrete benefits and real-world applications
5. Evaluates the framework's capacity to solve practical problems

Structure your response as a coherent validation narrative, not a checklist. Focus on practical value and real-world applicability. Consider domains like cognitive science, organizational behavior, education, and technology. Limit response to ~150 words for efficiency."""

    def _get_fallback_response(self) -> str:
        """Provide fallback response when validation fails.

        Returns:
            Generic fallback validation response
        """
        return ("Pragmatic validation encountered an error. The practical utility of the outputs cannot be assessed at this time. "
                "Manual evaluation of real-world applications and practical value is recommended.")