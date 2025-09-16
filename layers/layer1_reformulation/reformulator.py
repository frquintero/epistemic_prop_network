"""Layer 1: Input Reformulation - Reformulator Agent

This module implements the Reformulator agent responsible for purifying
and contextualizing raw user input to eliminate bias and ensure
epistemological clarity.
"""

import os
import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.config import get_config, init_config, NetworkConfig
from core.exceptions import LayerProcessingError, LLMError, ConfigurationError
from core.llm_client import LLMClient
from core.logging_config import get_logger
from core.schemas import NetworkRequest, ReformulatedQuestion


class Reformulator:
    """Reformulator agent for Layer 1 processing.

    The Reformulator accepts raw user questions, eliminates bias and loaded language,
    distills the core epistemological intent, and adds neutral factual context
    without providing answers.
    """

    def __init__(self, llm_client: Optional[LLMClient] = None):
        """Initialize the Reformulator agent.

        Args:
            llm_client: Optional LLM client instance. If None, creates a new one.
        """
        self.logger = get_logger(__name__)
        self.llm_client = llm_client
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
                    request_timeout=float(os.getenv("REQUEST_TIMEOUT", "30.0")),
                    max_retries=int(os.getenv("MAX_RETRIES", "1")),
                    temperature=float(os.getenv("TEMPERATURE", "0.1")),
                    max_tokens_per_request=int(os.getenv("MAX_TOKENS_PER_REQUEST", "2048")),
                    log_level=os.getenv("LOG_LEVEL", "DEBUG"),
                    enable_structured_logging=os.getenv("STRUCTURED_LOGGING", "false").lower() == "true",
                    debug_mode=os.getenv("DEBUG_MODE", "true").lower() == "true",
                    mock_responses=os.getenv("MOCK_RESPONSES", "true").lower() == "true"
                ))
                try:
                    self._config = get_config()
                except RuntimeError as inner_exc:
                    raise ConfigurationError("Network configuration is not initialized") from inner_exc
        return self._config

    def _get_llm_client(self) -> LLMClient:
        """Lazily create or return the configured LLM client."""
        if self.llm_client is None:
            self.llm_client = LLMClient(network_config=self.config)
        return self.llm_client

    async def process(self, request: NetworkRequest) -> ReformulatedQuestion:
        """Process a raw user question through the reformulation pipeline.

        Args:
            request: NetworkRequest containing the raw user question

        Returns:
            ReformulatedQuestion: Structured reformulation result with metadata

        Raises:
            LayerProcessingError: If reformulation fails
        """
        try:
            self.logger.info(
                "Starting reformulation | request_id=%s | original=%s",
                request.request_id,
                request.original_question
            )

            # Step 1: Initial bias detection and sanitization
            sanitized_question, initial_bias_removed = self._sanitize_input(request.original_question)

            # Step 2: LLM-based reformulation
            reformulated_question, raw_llm_response, reformulation_bias_removed = await self._reformulate_with_llm(
                sanitized_question,
                request.metadata
            )

            # Combine bias removal tracking
            bias_removed = initial_bias_removed + reformulation_bias_removed

            # LLM handles all validation internally - trust the reformulated output
            context_added = self._detect_context_markers(reformulated_question)

            # Create structured result
            result = ReformulatedQuestion(
                question=reformulated_question,
                original_question=request.original_question,
                context_added=["LLM handles context embedding internally"],
                bias_removed=["LLM handles bias elimination internally"]
            )

            self.logger.info(
                "Reformulation completed successfully | request_id=%s | original_len=%d | reformulated_len=%d | llm_handled_all_processing=True",
                request.request_id,
                len(request.original_question),
                len(reformulated_question)
            )

            return result

        except Exception as e:
            self.logger.error(
                "Reformulation failed | request_id=%s | error=%s",
                request.request_id,
                e,
                exc_info=True
            )
            raise LayerProcessingError(
                f"Failed to reformulate question: {str(e)}",
                {"request_id": request.request_id, "original_question": request.original_question}
            ) from e

    def _sanitize_input(self, question: str) -> tuple[str, List[str]]:
        """Perform initial sanitization to remove obvious bias indicators.

        Args:
            question: Raw user question

        Returns:
            tuple: (sanitized_question, bias_removed_list)
        """
        bias_removed = []

        # Remove excessive punctuation that might indicate emotional bias
        original = question
        sanitized = re.sub(r'[!?]{2,}', '!', question)
        if sanitized != original:
            bias_removed.append("excessive punctuation")

        # Reset original for next check
        original = sanitized

        # Remove leading/trailing whitespace (this is sanitization, not bias removal)
        sanitized = sanitized.strip()
        # Don't add to bias_removed for normal whitespace trimming

        # Basic length validation
        if len(sanitized) < 3:
            raise LayerProcessingError("Question too short after sanitization")

        if len(sanitized) > 1000:
            # Truncate overly long questions
            sanitized = sanitized[:997] + "..."
            bias_removed.append("truncated long question")

        return sanitized, bias_removed

    async def _reformulate_with_llm(self, question: str, metadata: Dict[str, Any]) -> tuple[str, str, List[str]]:
        """Use LLM to perform sophisticated bias elimination and reformulation.

        Args:
            question: Sanitized input question
            metadata: Additional context from the request

        Returns:
            tuple: (reformulated_question, raw_llm_response, bias_removed_list)
        """
        prompt = self._build_reformulation_prompt(question, metadata)

        try:
            raw_response = await self._get_llm_client().generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request
            )

            # Extract the reformulated question from the response
            reformulated = self._extract_reformulated_question(raw_response)

            # For LLM reformulation, we track that bias elimination occurred
            # but can't specify exact words removed
            bias_removed = ["LLM bias elimination applied"]

            return reformulated, raw_response, bias_removed

        except LLMError as e:
            self.logger.warning(
                "LLM reformulation failed, falling back to basic processing | error=%s",
                e
            )
            # Fallback to basic reformulation if LLM fails
            basic_result, basic_bias = self._basic_reformulation(question)
            return basic_result, "LLM_FAILED_FALLBACK_TO_BASIC", basic_bias

    def _build_reformulation_prompt(self, question: str, metadata: Dict[str, Any]) -> str:
        """Build the reformulation prompt for the LLM.

        Args:
            question: Input question to reformulate
            metadata: Additional context

        Returns:
            str: Complete reformulation prompt
        """
        context_info = ""
        if metadata:
            context_info = f"\nAdditional context: {metadata}"

        prompt = f"""You are an epistemological reformulator specializing in bias elimination and epistemic contextualization.

Your task is to transform biased questions into neutral, epistemologically-grounded inquiries through systematic analysis.

ANALYSIS FRAMEWORK:
1. DECONSTRUCT BIAS: Identify loaded assumptions, leading language, implicit judgments, and emotional framing that could prejudice analysis.

2. DEFINE EPISTEMIC FRAMEWORK: Determine the knowledge basis sought (empirical, interpretive, evaluative) and identify whose perspective is most relevant for a comprehensive understanding.

3. REFORMULATE: Rephrase neutrally with explicit epistemic lens, specify inquiry scope, and ensure the question enables rigorous, multi-perspective analysis.

INSTRUCTIONS:
- Remove biased, loaded, or emotionally charged language
- Eliminate framing effects that might prejudice the analysis
- Distill the core epistemological question (definition, history, function, validation)
- Embed neutral factual context and relevant disciplinary perspectives directly into the question
- Perform your own internal validation so the final question is epistemologically precise, neutral, and ends with a question mark
- Maintain original intent while ensuring neutrality and comprehensiveness
- Output ONLY the reformulated question, no explanations or meta-commentary

EXAMPLES:
Biased: "Why are incompetent politicians making our country worse?"
Reformulated: "How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?"

Biased: "What are mental models? I think they're obviously amazing!"
Reformulated: "What is the conceptual definition and functional role of mental models in cognitive processes, from an epistemological and psychological perspective?"

ORIGINAL QUESTION: {question}{context_info}

REFORMULATED QUESTION:"""

        return prompt

    def _extract_reformulated_question(self, llm_response: str) -> str:
        """Extract the reformulated question from LLM response.

        Args:
            llm_response: Raw LLM response

        Returns:
            str: Cleaned reformulated question
        """
        # Remove any prefixes or explanations
        response = llm_response.strip()

        # Remove common LLM artifacts
        response = re.sub(r'^(Here is|The reformulated|Reformulated|Question is|The question is|The reformulated question is):\s*', '', response, flags=re.IGNORECASE)

        # Clean up punctuation
        response = response.strip('"\'')

        # Ensure it ends with a question mark if it looks like a question
        if not response.endswith('?') and any(word in response.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who']):
            response += '?'

        return response

    def _basic_reformulation(self, question: str) -> tuple[str, List[str]]:
        """Fallback basic reformulation when LLM is unavailable.

        Args:
            question: Input question

        Returns:
            tuple: (reformulated_question, bias_removed_list)
        """
        bias_removed = []

        # Enhanced bias removal patterns with epistemic awareness
        # Focus on simple bias removal - let LLM handle complex restructuring
        patterns = [
            # Emotional and judgmental language
            (r'\b(stupid|dumb|ridiculous|absurd|pathetic)\b', ''),
            (r'\b(obviously|clearly|of course|undoubtedly)\b', ''),
            (r'\b(I think|I believe|in my opinion|personally)\b', ''),
            (r'\b(the best|the worst|amazing|terrible|horrible|wonderful)\b', ''),

            # Remove judgmental adjectives about people/groups
            (r'\b(incompetent|corrupt|stupid|dumb|ridiculous)\b\s+(\bpoliticians?\b|\bleaders?\b|\bgovernment\b)', r'\2'),

            # Simple question transformation (very conservative)
            (r'\bwhy are\b', 'how are'),
            (r'\bwhy do\b', 'how do'),

            # Assumptive question endings
            (r'\b(isn\'?t it|aren\'?t they|don\'?t they)\b', ''),

            # Overly casual or colloquial expressions
            (r'\b(kinda|sorta|like you know|you see)\b', ''),
        ]

        reformulated = question
        for pattern, replacement in patterns:
            original = reformulated
            reformulated = re.sub(pattern, replacement, reformulated, flags=re.IGNORECASE)
            if reformulated != original:
                # Extract the removed word for tracking
                match = re.search(pattern, original, flags=re.IGNORECASE)
                if match:
                    bias_removed.append(f"removed biased term: {match.group(0)}")

        # Add basic epistemic contextualization if no specific context markers exist
        epistemic_indicators = ['definition', 'history', 'function', 'purpose', 'role', 'meaning']
        lowered = reformulated.lower()
        if not any(indicator in lowered for indicator in epistemic_indicators):
            if any(word in lowered for word in ['what is', 'what are', 'define']):
                reformulated = f"From an epistemological perspective, {self._lowercase_first_letter(reformulated.strip())}"
                bias_removed.append("added epistemological framing")
            elif any(word in lowered for word in ['how', 'why']):
                reformulated = f"From multiple disciplinary perspectives, {self._lowercase_first_letter(reformulated.strip())}"
                bias_removed.append("added multi-perspective framing")

        # Clean up extra spaces
        reformulated = re.sub(r'\s+', ' ', reformulated).strip()

        return reformulated, bias_removed

    @staticmethod
    def _lowercase_first_letter(text: str) -> str:
        """Lowercase only the first character while preserving the rest."""
        if not text:
            return text
        return text[0].lower() + text[1:]

    def _detect_context_markers(self, question: str) -> List[str]:
        """Infer context markers embedded by the LLM within the question itself."""
        lowered = question.lower()
        context_added: List[str] = []

        marker_map = [
            ("conceptual and definitional", "epistemic framing: conceptual analysis"),
            ("semantic", "epistemic framing: conceptual analysis"),
            ("historical", "epistemic framing: historical analysis"),
            ("genealogical", "epistemic framing: historical analysis"),
            ("teleological", "epistemic framing: teleological analysis"),
            ("functional", "epistemic framing: functional analysis"),
            ("pragmatic", "epistemic framing: pragmatic analysis"),
            ("evaluative and normative", "epistemic framing: evaluative analysis"),
            ("multiple disciplinary", "epistemic framing: multi-perspective analysis"),
            ("interdisciplinary", "epistemic framing: multi-perspective analysis"),
            ("epistemological perspective", "epistemic framing: general epistemological"),
            ("epistemological and interdisciplinary", "epistemic framing: general epistemological"),
            ("in the context of", "contextual framing embedded in question"),
        ]

        for key, label in marker_map:
            if key in lowered and label not in context_added:
                context_added.append(label)

        return context_added

    async def health_check(self) -> bool:
        """Perform a health check on the Reformulator.

        Returns:
            bool: True if healthy, False otherwise
        """
        try:
            test_request = NetworkRequest(
                request_id="health-check",
                original_question="What is epistemology?",
                timestamp=datetime.now().isoformat()
            )

            result = await self.process(test_request)
            return len(result.question) > 10

        except Exception as e:
            self.logger.error("Health check failed | error=%s", e)
            return False
