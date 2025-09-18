"""Tension Validator for Layer 3 - Resolves conflicts across analyses."""

from typing import Optional

from core.config import get_config
from core.llm_client import LLMClient, LLMConfig
from core.logging_config import get_logger
from core.schemas import Phase2Triple
from core.template_manager import get_template_manager

logger = None


class TensionValidator:
    """Identifies and reconciles tensions across semantic, genealogical, and teleological outputs."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        llm_config: Optional[LLMConfig] = None,
    ):
        """Initialize the Tension Validator.

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
        """Process Phase 2 triple and surface conceptual tensions.

        Args:
            phase2_triple: The triple containing semantic, genealogical, and teleological outputs

        Returns:
            Analytical narrative describing tensions and proposed resolutions
        """
        global logger
        if logger is None:
            logger = get_logger(__name__)

        logger.info("Starting tension validation")

        prompt = self._build_tension_prompt(phase2_triple)

        try:
            response = await self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request,
            )

            logger.info(
                "Tension validation completed | output_length=%d", len(response)
            )
            return response

        except Exception as exc:
            logger.error("Tension validation failed | error=%s", str(exc))
            return self._get_fallback_response()

    def _build_tension_prompt(self, phase2_triple: Phase2Triple) -> str:
        """Build the tension validation prompt.

        Args:
            phase2_triple: The triple to analyze for tensions

        Returns:
            Formatted prompt for the LLM
        """
        template_manager = get_template_manager()
        return template_manager.render_template(
            layer="layer3",
            name="tension_validator",
            phase2_triple_semantic=phase2_triple.semantic,
            phase2_triple_genealogical=phase2_triple.genealogical,
            phase2_triple_teleological=phase2_triple.teleological,
        )

    def _get_fallback_response(self) -> str:
        """Provide fallback response when tension analysis fails.

        Returns:
            Generic fallback tension analysis response
        """
        return (
            "Tension analysis encountered an error. The interactions between semantic, genealogical, and "
            "teleological accounts require manual review to identify conflicts and potential resolutions."
        )
