"""Correspondence Validator for Layer 3 - Tests alignment with empirical evidence."""

import asyncio
import logging
from typing import Dict, Any, Optional

from core.llm_client import LLMClient, LLMConfig
from core.schemas import Phase2Triple, Phase3Triple
from core.config import get_config
from core.logging_config import get_logger
from core.template_manager import get_template_manager

logger = None


class CorrespondenceValidator:
    """Validates outputs against empirical evidence and observable reality."""

    def __init__(self, llm_client: Optional[LLMClient] = None, llm_config: Optional[LLMConfig] = None):
        """Initialize the Correspondence Validator.

        Args:
            llm_client: Optional LLM client instance. If None, creates a new one.
            llm_config: Optional LLM configuration. If provided, used to create LLM client.
        """
        if llm_client is not None:
            self.llm_client = llm_client
        elif llm_config is not None:
            self.llm_client = LLMClient(config=llm_config)
        else:
            self.llm_client = LLMClient()
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
        template_manager = get_template_manager()
        return template_manager.render_template(
            layer="layer3",
            name="correspondence_validator",
            phase2_triple_semantic=phase2_triple.semantic,
            phase2_triple_genealogical=phase2_triple.genealogical,
            phase2_triple_teleological=phase2_triple.teleological
        )

    def _get_fallback_response(self) -> str:
        """Provide fallback response when validation fails.

        Returns:
            Generic fallback validation response
        """
        return ("Correspondence validation encountered an error. The outputs cannot be empirically validated at this time. "
                "Manual review of scientific literature and empirical evidence is recommended to assess alignment with observable reality.")