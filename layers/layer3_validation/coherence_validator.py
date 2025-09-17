"""Coherence Validator for Layer 3 - Ensures logical consistency."""

import asyncio
import logging
from typing import Dict, Any, Optional

from core.llm_client import LLMClient
from core.schemas import Phase2Triple, Phase3Triple
from core.config import get_config
from core.logging_config import get_logger

logger = None


class CoherenceValidator:
    """Validates logical consistency and internal coherence of outputs."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the Coherence Validator.

        Args:
            llm_client: Optional LLM client instance. If None, creates a new one.
        """
        self.llm_client = llm_client or LLMClient()
        self.config = get_config()

    async def process(self, phase2_triple: Phase2Triple) -> str:
        """Process Phase 2 triple and validate logical coherence.

        Args:
            phase2_triple: The triple containing semantic, genealogical, and teleological outputs

        Returns:
            Validation narrative assessing logical consistency
        """
        global logger
        if logger is None:
            logger = get_logger(__name__)
        logger.info("Starting coherence validation")

        prompt = self._build_coherence_prompt(phase2_triple)

        try:
            response = await self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request,
            )

            logger.info("Coherence validation completed | output_length=%d", len(response))
            return response

        except Exception as e:
            logger.error("Coherence validation failed | error=%s", str(e))
            return self._get_fallback_response()

    def _build_coherence_prompt(self, phase2_triple: Phase2Triple) -> str:
        """Build the coherence validation prompt.

        Args:
            phase2_triple: The triple to validate

        Returns:
            Formatted prompt for LLM
        """
        return f"""You are the Coherence Validator in an epistemological network. Your task is to assess the internal logical consistency of the following outputs and verify that they form a coherent conceptual framework.

Integrate in a unified narrative the following triple and evaluate the logical relationships between the components:

SEMANTIC DEFINITION:
{phase2_triple.semantic}

GENEALOGICAL ACCOUNT:
{phase2_triple.genealogical}

TELEOLOGICAL ANALYSIS:
{phase2_triple.teleological}

Provide a detailed coherence assessment that:
1. Checks if the semantic definition logically follows from the historical development
2. Verifies that functional claims are consistent with the conceptual definition
3. Assesses whether historical claims support rather than contradict the definition
4. Identifies logical gaps, inconsistencies, or circular reasoning
5. Evaluates the overall conceptual coherence of the framework

Structure your response as a coherent validation narrative, not a checklist. Focus on logical relationships and conceptual consistency. Limit response to ~150 words for efficiency."""

    def _get_fallback_response(self) -> str:
        """Provide fallback response when validation fails.

        Returns:
            Generic fallback validation response
        """
        return ("Coherence validation encountered an error. The logical consistency of the outputs cannot be assessed at this time. "
                "Manual review of conceptual relationships and logical coherence is recommended.")