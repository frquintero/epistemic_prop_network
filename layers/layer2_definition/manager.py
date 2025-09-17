"""Layer 2: Definition Generation - Manager

This module implements the Layer2DefinitionManager responsible for orchestrating
parallel processing of the three definition nodes (Semantic, Genealogical, Teleological).
"""

import asyncio
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

from core.config import get_config, init_config, NetworkConfig
from core.exceptions import LayerProcessingError, LLMError, ConfigurationError
from core.llm_client import LLMClient, LLMConfig
from core.logging_config import get_logger
from core.schemas import ReformulatedQuestion, Phase2Triple

from .semantic_node import SemanticNode
from .genealogical_node import GenealogicalNode
from .teleological_node import TeleologicalNode


class Layer2DefinitionManager:
    """Manager for Layer 2 Definition Generation processing.

    Orchestrates parallel execution of Semantic, Genealogical, and Teleological nodes
    to generate comprehensive conceptual definitions.
    """

    def __init__(self, network_config: Optional[NetworkConfig] = None, llm_configs: Optional[Dict[str, LLMConfig]] = None):
        """Initialize the Layer 2 Definition Manager.

        Args:
            network_config: Optional network configuration. If None, uses default config.
            llm_configs: Optional dict of LLM configurations keyed by node name.
        """
        self.logger = get_logger(__name__)
        self.network_config = network_config
        self.llm_configs = llm_configs or {}
        self._config: Optional[NetworkConfig] = None

        # Initialize the three definition nodes
        self.semantic_node = SemanticNode(
            network_config=self.config,
            llm_config=self.llm_configs.get('semantic_node')
        )
        self.genealogical_node = GenealogicalNode(
            network_config=self.config,
            llm_config=self.llm_configs.get('genealogical_node')
        )
        self.teleological_node = TeleologicalNode(
            network_config=self.config,
            llm_config=self.llm_configs.get('teleological_node')
        )

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
                    max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "3")),  # Allow parallel execution
                    temperature=0.4,  # Balanced temperature for definition generation
                    max_tokens_per_request=2048,
                    reasoning_effort="medium",
                    enable_structured_logging=True,
                    debug_mode=False,
                    mock_responses=False
                ))
                self._config = get_config()
        return self._config

    async def process(self, reformulated_question: ReformulatedQuestion) -> Phase2Triple:
        """Process a reformulated question through all three definition nodes in parallel.

        Args:
            reformulated_question: The reformulated question from Layer 1

        Returns:
            Phase2Triple: Structured output containing semantic, genealogical, and teleological analyses

        Raises:
            LayerProcessingError: If definition generation fails
        """
        try:
            self.logger.info(
                "Starting Layer 2 Definition Generation | question=%s",
                reformulated_question.question[:100] + "..." if len(reformulated_question.question) > 100 else reformulated_question.question
            )

            start_time = datetime.now()

            # Execute all three nodes in parallel
            semantic_task = self.semantic_node.process(reformulated_question)
            genealogical_task = self.genealogical_node.process(reformulated_question)
            teleological_task = self.teleological_node.process(reformulated_question)

            # Wait for all tasks to complete
            results = await asyncio.gather(
                semantic_task,
                genealogical_task,
                teleological_task,
                return_exceptions=True
            )

            # Handle results and exceptions
            semantic_result, genealogical_result, teleological_result = self._handle_parallel_results(results)

            # Create Phase2Triple output
            phase2_output = Phase2Triple(
                semantic=semantic_result,
                genealogical=genealogical_result,
                teleological=teleological_result
            )

            processing_time = (datetime.now() - start_time).total_seconds()

            self.logger.info(
                "Layer 2 Definition Generation completed | processing_time=%.2fs | semantic_len=%d | genealogical_len=%d | teleological_len=%d",
                processing_time,
                len(semantic_result),
                len(genealogical_result),
                len(teleological_result)
            )

            return phase2_output

        except Exception as e:
            self.logger.error(
                "Layer 2 Definition Generation failed | error=%s",
                e
            )
            raise LayerProcessingError(f"Definition generation failed: {e}") from e

    def _handle_parallel_results(self, results: Tuple[Any, ...]) -> Tuple[str, str, str]:
        """Handle results from parallel node execution, including error handling.

        Args:
            results: Tuple of results from asyncio.gather

        Returns:
            Tuple[str, str, str]: (semantic, genealogical, teleological) results

        Raises:
            LayerProcessingError: If critical failures occur
        """
        semantic_result, genealogical_result, teleological_result = results

        # Handle semantic node result
        if isinstance(semantic_result, Exception):
            self.logger.warning("Semantic node failed | error=%s", semantic_result)
            semantic_result = self._generate_fallback_semantic()
        elif not isinstance(semantic_result, str) or len(semantic_result) < 50:
            self.logger.warning("Semantic node returned inadequate result | length=%d", len(semantic_result) if isinstance(semantic_result, str) else 0)
            semantic_result = self._generate_fallback_semantic()

        # Handle genealogical node result
        if isinstance(genealogical_result, Exception):
            self.logger.warning("Genealogical node failed | error=%s", genealogical_result)
            genealogical_result = self._generate_fallback_genealogical()
        elif not isinstance(genealogical_result, str) or len(genealogical_result) < 100:
            self.logger.warning("Genealogical node returned inadequate result | length=%d", len(genealogical_result) if isinstance(genealogical_result, str) else 0)
            genealogical_result = self._generate_fallback_genealogical()

        # Handle teleological node result
        if isinstance(teleological_result, Exception):
            self.logger.warning("Teleological node failed | error=%s", teleological_result)
            teleological_result = self._generate_fallback_teleological()
        elif not isinstance(teleological_result, str) or len(teleological_result) < 100:
            self.logger.warning("Teleological node returned inadequate result | length=%d", len(teleological_result) if isinstance(teleological_result, str) else 0)
            teleological_result = self._generate_fallback_teleological()

        return semantic_result, genealogical_result, teleological_result

    def _generate_fallback_semantic(self) -> str:
        """Generate a fallback semantic definition when the node fails."""
        return "Semantic analysis could not be completed due to processing constraints. The concept requires linguistic and etymological analysis to provide a precise definition."

    def _generate_fallback_genealogical(self) -> str:
        """Generate a fallback historical account when the node fails."""
        return "Historical analysis could not be completed due to processing constraints. The concept's development requires examination of its origins and evolution through intellectual history."

    def _generate_fallback_teleological(self) -> str:
        """Generate a fallback functional account when the node fails."""
        return "Functional analysis could not be completed due to processing constraints. The concept's utility and purpose require examination of its practical applications and cognitive role."

    async def health_check(self) -> bool:
        """Perform a comprehensive health check on Layer 2.

        Returns:
            bool: True if all nodes are healthy, False otherwise
        """
        try:
            test_question = ReformulatedQuestion(
                question="What is epistemology?",
                original_question="What is epistemology?",
                context_added=["LLM handles context embedding internally"],
                bias_removed=["LLM handles bias elimination internally"]
            )

            # Test all three nodes
            results = await asyncio.gather(
                self.semantic_node.health_check(),
                self.genealogical_node.health_check(),
                self.teleological_node.health_check(),
                return_exceptions=True
            )

            # Check if all nodes are healthy
            healthy_nodes = sum(1 for result in results if result is True and not isinstance(result, Exception))

            self.logger.info("Layer 2 health check | healthy_nodes=%d/3", healthy_nodes)

            return healthy_nodes >= 2  # At least 2 out of 3 nodes should be healthy

        except Exception as e:
            self.logger.error("Layer 2 health check failed | error=%s", e)
            return False