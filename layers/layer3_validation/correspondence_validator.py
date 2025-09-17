"""Correspondence Validator for Layer 3 - Tests alignment with empirical evidence."""

import asyncio
import logging
from typing import Dict, Any, Optional

from core.llm_client import LLMClient
from core.schemas import Phase2Triple, Phase3Triple
from core.config import get_config
from core.logging_config import get_logger

logger = None


class CorrespondenceValidator:
    """Validates outputs against empirical evidence and observable reality."""

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the Correspondence Validator.

        Args:
            llm_client: Optional LLM client instance. If None, creates a new one.
        """
        self.llm_client = llm_client or LLMClient()
        self.config = get_config()

    async def process(self, phase2_triple: Phase2Triple) -> str:
        """Process Phase 2 triple and validate correspondence with empirical reality.

        Args:
            phase2_triple: The triple containing semantic, genealogical, and teleological outputs

        Returns:
            Validation narrative assessing empirical alignment
        """
        global logger
        if logger is None:
            logger = get_logger(__name__)
        logger.info("Starting correspondence validation")

        prompt = self._build_correspondence_prompt(phase2_triple)

        try:
            response = await self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request,
            )

            logger.info("Correspondence validation completed | output_length=%d", len(response))
            return response

        except Exception as e:
            logger.error("Correspondence validation failed | error=%s", str(e))
            return self._get_fallback_response()

    def _build_correspondence_prompt(self, phase2_triple: Phase2Triple) -> str:
        """Build the correspondence validation prompt.

        Args:
            phase2_triple: The triple to validate

        Returns:
            Formatted prompt for LLM
        """
        return f"""You are the Correspondence Validator in an epistemological network. Your task is to assess whether the following outputs align with observable reality, scientific evidence, historical records, and empirical studies.

Integrate in a unified narrative the following triple and evaluate for empirical correspondance:

SEMANTIC DEFINITION:
{phase2_triple.semantic}

GENEALOGICAL ACCOUNT:
{phase2_triple.genealogical}

TELEOLOGICAL ANALYSIS:
{phase2_triple.teleological}

Provide a detailed validation assessment that:
1. Tests alignment with established scientific facts and empirical evidence
2. Validates historical claims against documented records
3. Assesses functional claims against observed real-world applications
4. Identifies empirically supported aspects vs. speculative claims
5. Provides evidence-based verdicts for each component

Structure your response as a coherent validation narrative, not a checklist. Focus on empirical grounding and evidence-based assessment. Limit response to ~150 words for efficiency."""

    def _get_fallback_response(self) -> str:
        """Provide fallback response when validation fails.

        Returns:
            Generic fallback validation response
        """
        return ("Correspondence validation encountered an error. The outputs cannot be empirically validated at this time. "
                "Manual review of scientific literature and empirical evidence is recommended to assess alignment with observable reality.")