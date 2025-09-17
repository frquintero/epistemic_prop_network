"""Coherence Validator for Layer 3 - Ensures logical consistency."""

import asyncio
import logging
from typing import Dict, Any, Optional

from core.llm_client import LLMClient
from core.schemas import Phase2Triple, Phase3Triple
from core.config import get_config
from core.logging_config import get_logger
from core.template_manager import get_template_manager

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
        template_manager = get_template_manager()
        return template_manager.render_template(
            layer="layer3",
            name="coherence_validator",
            phase2_triple_semantic=phase2_triple.semantic,
            phase2_triple_genealogical=phase2_triple.genealogical,
            phase2_triple_teleological=phase2_triple.teleological
        )

    def _get_fallback_response(self) -> str:
        """Provide fallback response when validation fails.

        Returns:
            Generic fallback validation response
        """
        return ("Coherence validation encountered an error. The logical consistency of the outputs cannot be assessed at this time. "
                "Manual review of conceptual relationships and logical coherence is recommended.")