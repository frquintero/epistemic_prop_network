"""Layer 3 Validation Manager - Orchestrates parallel validation processing."""

import asyncio
from typing import Dict, Any, Optional, Tuple

from core.logging_config import get_logger
from core.llm_client import LLMConfig
from core.schemas import Phase2Triple, Phase3Triple
from .correspondence_validator import CorrespondenceValidator
from .coherence_validator import CoherenceValidator
from .pragmatic_validator import PragmaticValidator

logger = get_logger(__name__)


class Layer3ValidationManager:
    """Manages parallel execution of Layer 3 validation agents."""

    def __init__(self, llm_configs: Optional[Dict[str, LLMConfig]] = None):
        """Initialize the validation manager with all three validators.

        Args:
            llm_configs: Optional dict of LLM configurations keyed by validator name.
        """
        self.llm_configs = llm_configs or {}
        self.correspondence_validator = CorrespondenceValidator(
            llm_config=self.llm_configs.get('correspondence_validator')
        )
        self.coherence_validator = CoherenceValidator(
            llm_config=self.llm_configs.get('coherence_validator')
        )
        self.pragmatic_validator = PragmaticValidator(
            llm_config=self.llm_configs.get('pragmatic_validator')
        )

    async def process(self, phase2_triple: Phase2Triple) -> Phase3Triple:
        """Process Phase 2 triple through all three validation agents in parallel.

        Args:
            phase2_triple: The triple containing semantic, genealogical, and teleological outputs

        Returns:
            Phase3Triple containing validation results from all three validators
        """
        logger.info("Starting Layer 3 Validation | semantic_len=%d | genealogical_len=%d | teleological_len=%d",
                   len(phase2_triple.semantic), len(phase2_triple.genealogical), len(phase2_triple.teleological))

        # Execute all three validators concurrently
        correspondence_task = self.correspondence_validator.process(phase2_triple)
        coherence_task = self.coherence_validator.process(phase2_triple)
        pragmatic_task = self.pragmatic_validator.process(phase2_triple)

        try:
            # Wait for all validations to complete
            results = await asyncio.gather(
                correspondence_task,
                coherence_task,
                pragmatic_task,
                return_exceptions=True
            )

            # Handle results and exceptions
            correspondence_result, coherence_result, pragmatic_result = self._handle_parallel_results(results)

            phase3_triple = Phase3Triple(
                correspondence=correspondence_result,
                coherence=coherence_result,
                pragmatic=pragmatic_result
            )

            processing_time = self._calculate_processing_time()
            logger.info("Layer 3 Validation completed | processing_time=%.2fs | correspondence_len=%d | coherence_len=%d | pragmatic_len=%d",
                       processing_time, len(correspondence_result), len(coherence_result), len(pragmatic_result))

            return phase3_triple

        except Exception as e:
            logger.error("Layer 3 Validation failed | error=%s", str(e))
            # Return fallback triple with error messages
            return Phase3Triple(
                correspondence=self.correspondence_validator._get_fallback_response(),
                coherence=self.coherence_validator._get_fallback_response(),
                pragmatic=self.pragmatic_validator._get_fallback_response()
            )

    def _handle_parallel_results(self, results: Tuple[Any, ...]) -> Tuple[str, str, str]:
        """Handle results from parallel validation execution.

        Args:
            results: Tuple of results from asyncio.gather, may contain exceptions

        Returns:
            Tuple of (correspondence_result, coherence_result, pragmatic_result)
        """
        correspondence_result = results[0]
        coherence_result = results[1]
        pragmatic_result = results[2]

        # Handle correspondence result
        if isinstance(correspondence_result, Exception):
            logger.warning("Correspondence validation failed with exception | error=%s", str(correspondence_result))
            correspondence_result = self.correspondence_validator._get_fallback_response()

        # Handle coherence result
        if isinstance(coherence_result, Exception):
            logger.warning("Coherence validation failed with exception | error=%s", str(coherence_result))
            coherence_result = self.coherence_validator._get_fallback_response()

        # Handle pragmatic result
        if isinstance(pragmatic_result, Exception):
            logger.warning("Pragmatic validation failed with exception | error=%s", str(pragmatic_result))
            pragmatic_result = self.pragmatic_validator._get_fallback_response()

        return correspondence_result, coherence_result, pragmatic_result

    def _calculate_processing_time(self) -> float:
        """Calculate processing time for the validation phase.

        Returns:
            Processing time in seconds (placeholder implementation)
        """
        # In a real implementation, this would track actual timing
        # For now, return a reasonable estimate based on LLM response times
        return 1.5  # Estimated ~1.5 seconds for parallel LLM calls