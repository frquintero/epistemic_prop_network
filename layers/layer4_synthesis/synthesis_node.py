"""Layer 4: Synthesis & Communication - Synthesis Node

This module implements the Synthesis Node agent responsible for integrating
validated insights from all previous layers into holistic narratives with
epistemological rigor.
"""

import os
import re
from typing import Dict, Any, Optional
from datetime import datetime

from core.config import get_config, init_config, NetworkConfig
from core.exceptions import LayerProcessingError, LLMError, ConfigurationError
from core.llm_client import LLMClient
from core.logging_config import get_logger
from core.schemas import Phase3Triple, SynthesisOutput


class SynthesisNode:
    """Synthesis Node agent for Layer 4 Synthesis & Communication.

    The Synthesis Node integrates validated outputs from all previous layers
    into holistic narratives that provide meaning, context, and value,
    culminating in a thesis statement.
    """

    def __init__(self, network_config: Optional[NetworkConfig] = None):
        """Initialize the Synthesis Node agent.

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
                    temperature=0.3,  # Lower temperature for consistent synthesis
                    max_tokens_per_request=4096,  # Higher token limit for comprehensive synthesis
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

    def _build_synthesis_prompt(self, phase3_triple: Phase3Triple) -> str:
        """Build the synthesis prompt for the LLM.

        Args:
            phase3_triple: The validated triple from Layer 3

        Returns:
            str: Complete synthesis prompt
        """
        prompt = f"""You are a master epistemological synthesizer specializing in creating comprehensive, meaningful narratives from complex conceptual frameworks.

Your task is to integrate the validated perspectives below into a holistic epistemological narrative that provides deep understanding, context, and practical value. Focus on creating connections between concepts and disciplines while maintaining rigorous academic standards.

VALIDATED INPUTS FROM PREVIOUS LAYERS:

CORRESPONDENCE VALIDATION (Empirical Alignment):
{phase3_triple.correspondence}

COHERENCE VALIDATION (Logical Consistency):
{phase3_triple.coherence}

PRAGMATIC VALIDATION (Practical Utility):
{phase3_triple.pragmatic}

SYNTHESIS REQUIREMENTS:

1. NARRATIVE INTEGRATION:
   - Weave together the definition, history, function, and validation results into a single coherent story
   - Show meaningful connections between concepts and broader disciplines
   - Provide context for how the concept evolved and relates to human cognition/practice
   - Create interrelationships that reveal deeper insights

2. THESIS FORMATION:
   - Generate a concise thesis statement (1-2 sentences) that encapsulates the core insight
   - Make it memorable and insightful, not just a summary
   - Position it as the central takeaway

3. VALUE DELIVERY:
   - Offer practical insights, knowledge, skills, or inspiration
   - Include validation-based qualifications (limitations, strengths)
   - Provide actionable knowledge for real-world application

4. STRUCTURE YOUR OUTPUT:
   - Start with the integrated narrative (definition → history → function → validation)
   - End with the thesis statement clearly marked
   - Maintain academic rigor while being accessible
   - Keep the total response under 800 words

OUTPUT FORMAT:
Provide a comprehensive epistemological narrative that flows naturally from introduction to conclusion, ending with a clearly marked thesis statement. Focus on creating meaning and connection rather than just listing facts.

SYNTHESIS:"""

        return prompt

    async def process(self, phase3_triple: Phase3Triple) -> SynthesisOutput:
        """Process a Phase 3 triple to generate final synthesis output.

        Args:
            phase3_triple: The validated triple from Layer 3

        Returns:
            SynthesisOutput: Complete synthesis with narrative and thesis

        Raises:
            LayerProcessingError: If synthesis fails
        """
        try:
            self.logger.info("Starting epistemological synthesis")

            # Build synthesis prompt
            prompt = self._build_synthesis_prompt(phase3_triple)

            # Get LLM response
            raw_response = await self._get_llm_client().generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request
            )

            # Return raw synthesis output as originally planned
            synthesis_output = SynthesisOutput(raw_response=raw_response)

            self.logger.info(
                "Epistemological synthesis completed | raw_response_length=%d",
                len(synthesis_output.raw_response)
            )

            return synthesis_output

        except LLMError as e:
            self.logger.warning("LLM synthesis failed | error=%s", e)
            raise LayerProcessingError(f"Synthesis failed: {e}") from e
        except Exception as e:
            self.logger.error("Unexpected error in synthesis | error=%s", e)
            raise LayerProcessingError(f"Synthesis failed: {e}") from e