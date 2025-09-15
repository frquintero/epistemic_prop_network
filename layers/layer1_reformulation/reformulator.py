"""Layer 1: Input Reformulation - Reformulator Agent

This module implements the Reformulator agent responsible for purifying
and contextualizing raw user input to eliminate bias and ensure
epistemological clarity.
"""

import re
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.config import get_config
from core.exceptions import LayerProcessingError, LLMError
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
        self.llm_client = llm_client or LLMClient()
        self.config = get_config()

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
                "Starting reformulation",
                request_id=request.request_id,
                original_question=request.original_question
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

            # Step 3: Context enrichment
            enriched_question, context_added = self._enrich_context(reformulated_question)

            # Step 4: Final validation
            validated_question = self._validate_reformulation(enriched_question)

            # Create structured result
            result = ReformulatedQuestion(
                question=validated_question,
                original_question=request.original_question,
                context_added=context_added,
                bias_removed=bias_removed
            )

            self.logger.info(
                "Reformulation completed successfully",
                request_id=request.request_id,
                original_length=len(request.original_question),
                reformulated_length=len(validated_question),
                bias_removed_count=len(bias_removed),
                context_added_count=len(context_added)
            )

            return result

        except Exception as e:
            self.logger.error(
                "Reformulation failed",
                request_id=request.request_id,
                error=str(e),
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
            raw_response = await self.llm_client.generate_text(
                prompt=prompt,
                max_tokens=self.config.max_tokens_per_request,
                temperature=0.1  # Low temperature for consistent, unbiased reformulation
            )

            # Extract the reformulated question from the response
            reformulated = self._extract_reformulated_question(raw_response)

            # For LLM reformulation, we track that bias elimination occurred
            # but can't specify exact words removed
            bias_removed = ["LLM bias elimination applied"]

            return reformulated, raw_response, bias_removed

        except LLMError as e:
            self.logger.warning(
                "LLM reformulation failed, falling back to basic processing",
                error=str(e)
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
- Add neutral factual context without providing answers
- Specify the epistemic lens and relevant perspectives
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
        if not any(indicator in reformulated.lower() for indicator in epistemic_indicators):
            if any(word in reformulated.lower() for word in ['what is', 'what are', 'define']):
                reformulated = f"From an epistemological perspective, {reformulated.lower()}"
                bias_removed.append("added epistemological framing")
            elif any(word in reformulated.lower() for word in ['how', 'why']):
                reformulated = f"From multiple disciplinary perspectives, {reformulated.lower()}"
                bias_removed.append("added multi-perspective framing")

        # Clean up extra spaces
        reformulated = re.sub(r'\s+', ' ', reformulated).strip()

        return reformulated, bias_removed

    def _enrich_context(self, question: str) -> tuple[str, List[str]]:
        """Add neutral factual context to the reformulated question with epistemic framework awareness.

        Args:
            question: Reformulated question

        Returns:
            tuple: (enriched_question, context_added_list)
        """
        context_added = []

        # Enhanced epistemological context markers with epistemic frameworks
        epistemic_frameworks = {
            # Definitional inquiries
            'definition': {
                'context': 'seeking to understand the conceptual definition and semantic boundaries',
                'perspective': 'from a philosophical and conceptual analysis perspective'
            },
            'meaning': {
                'context': 'exploring the semantic and interpretive dimensions',
                'perspective': 'from a hermeneutic and linguistic perspective'
            },

            # Historical inquiries
            'history': {
                'context': 'tracing the historical development and paradigm shifts',
                'perspective': 'from a historical epistemology perspective'
            },
            'origin': {
                'context': 'examining the historical emergence and evolution',
                'perspective': 'from a genealogical and historical perspective'
            },

            # Functional inquiries
            'function': {
                'context': 'analyzing the purpose, utility, and practical applications',
                'perspective': 'from a functional and pragmatic perspective'
            },
            'purpose': {
                'context': 'investigating the teleological dimensions and intended outcomes',
                'perspective': 'from a teleological and systems perspective'
            },
            'role': {
                'context': 'examining the functional role within broader systems',
                'perspective': 'from a systemic and ecological perspective'
            },

            # Evaluative inquiries
            'value': {
                'context': 'assessing the significance and evaluative dimensions',
                'perspective': 'from an axiological and evaluative perspective'
            },
            'impact': {
                'context': 'analyzing the broader implications and consequences',
                'perspective': 'from a consequentialist and impact assessment perspective'
            }
        }

        enriched = question

        # Apply specific epistemic framework if question type is identified
        for key, framework in epistemic_frameworks.items():
            if key in question.lower():
                enriched = f"In the context of {framework['context']}, {question.lower()}"
                context_added.append(f"epistemic framework: {framework['context']}")
                context_added.append(f"disciplinary perspective: {framework['perspective']}")
                break

        # Add general epistemological context if no specific framework found
        if not context_added:
            # Determine question type for appropriate framing
            if any(word in question.lower() for word in ['what is', 'what are', 'define', 'explain']):
                enriched = f"From a conceptual and definitional perspective, {question.lower()}"
                context_added.append("epistemic framing: conceptual analysis")
            elif any(word in question.lower() for word in ['how', 'why', 'what causes']):
                enriched = f"From multiple disciplinary and interpretive perspectives, {question.lower()}"
                context_added.append("epistemic framing: multi-perspective analysis")
            elif any(word in question.lower() for word in ['should', 'ought', 'better', 'worse']):
                enriched = f"From an evaluative and normative perspective, {question.lower()}"
                context_added.append("epistemic framing: evaluative analysis")
            else:
                enriched = f"From an epistemological and interdisciplinary perspective, {question.lower()}"
                context_added.append("epistemic framing: general epistemological")

        return enriched, context_added

    def _validate_reformulation(self, question: str) -> str:
        """Validate the final reformulated question.

        Args:
            question: Question to validate

        Returns:
            str: Validated question

        Raises:
            LayerProcessingError: If validation fails
        """
        # Length validation
        if len(question) < 10:
            raise LayerProcessingError("Reformulated question too short")

        if len(question) > 500:
            raise LayerProcessingError("Reformulated question too long")

        # Content validation
        if not any(word in question.lower() for word in ['what', 'how', 'why', 'when', 'where', 'who', 'definition', 'history', 'function']):
            raise LayerProcessingError("Question does not appear to be epistemological in nature")

        # Neutrality check (basic)
        biased_words = ['stupid', 'dumb', 'ridiculous', 'absurd', 'obviously', 'clearly', 'of course']
        if any(word in question.lower() for word in biased_words):
            self.logger.warning("Potential bias detected in reformulated question", question=question)

        return question

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
            return len(result) > 10

        except Exception as e:
            self.logger.error("Health check failed", error=str(e))
            return False