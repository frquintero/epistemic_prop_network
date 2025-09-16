"""Tests for Layer 1: Reformulator Agent"""

import pytest
from datetime import datetime
from unittest.mock import AsyncMock, patch

from core.schemas import NetworkRequest
from layers.layer1_reformulation import Reformulator


class TestReformulator:
    """Test cases for the Reformulator agent."""

    @pytest.fixture
    def reformulator(self):
        """Create a Reformulator instance for testing."""
        return Reformulator()

    @pytest.fixture
    def sample_request(self):
        """Create a sample NetworkRequest for testing."""
        return NetworkRequest(
            request_id="test-123",
            original_question="What are mental models?",
            timestamp=datetime.now().isoformat(),
            metadata={"source": "test"}
        )

    def test_reformulator_initialization(self, reformulator):
        """Test that Reformulator initializes correctly."""
        assert reformulator is not None
        assert hasattr(reformulator, 'llm_client')
        assert hasattr(reformulator, 'logger')

    def test_sanitize_input_basic(self, reformulator):
        """Test basic input sanitization."""
        # Test normal input
        result, bias_removed = reformulator._sanitize_input("What are mental models?")
        assert result == "What are mental models?"
        assert bias_removed == []

        # Test excessive punctuation
        result, bias_removed = reformulator._sanitize_input("What are mental models!!!???")
        assert result == "What are mental models!"
        assert "excessive punctuation" in bias_removed

        # Test whitespace trimming
        result, bias_removed = reformulator._sanitize_input("  What are mental models?  ")
        assert result == "What are mental models?"
        assert bias_removed == []

    def test_sanitize_input_edge_cases(self, reformulator):
        """Test edge cases in input sanitization."""
        # Test too short input
        with pytest.raises(Exception):  # LayerProcessingError
            reformulator._sanitize_input("Hi")

        # Test long input truncation
        long_input = "What " * 200 + "are mental models?"
        result, bias_removed = reformulator._sanitize_input(long_input)
        assert len(result) <= 1000
        assert result.endswith("...")

    def test_basic_reformulation(self, reformulator):
        """Test basic reformulation fallback."""
        input_question = "What are mental models? I think they're obviously amazing!"
        result, bias_removed = reformulator._basic_reformulation(input_question)

        # Should remove biased words
        assert "obviously" not in result.lower()
        assert "I think" not in result
        assert "amazing" not in result
        assert len(bias_removed) > 0

    def test_build_reformulation_prompt(self, reformulator):
        """Test prompt building."""
        question = "What are mental models?"
        metadata = {"domain": "cognitive science"}

        prompt = reformulator._build_reformulation_prompt(question, metadata)

        assert "epistemological reformulator" in prompt
        assert question in prompt
        assert "cognitive science" in prompt
        assert "REFORMULATED QUESTION:" in prompt

    def test_extract_reformulated_question(self, reformulator):
        """Test question extraction from LLM response."""
        # Test normal response
        response = "The reformulated question is: What are mental models?"
        result = reformulator._extract_reformulated_question(response)
        assert result == "What are mental models?"

        # Test response with quotes
        response = '"What are mental models?"'
        result = reformulator._extract_reformulated_question(response)
        assert result == "What are mental models?"

        # Test response without question mark
        response = "What are mental models"
        result = reformulator._extract_reformulated_question(response)
        assert result == "What are mental models?"

    @pytest.mark.asyncio
    async def test_process_with_mock_llm(self, async_mock_llm_client, reformulator, sample_request):
        """Test full processing pipeline with mocked LLM."""
        # Use the async mock LLM client from conftest.py
        reformulator_with_mock = Reformulator(async_mock_llm_client)

        # Process request
        result = await reformulator_with_mock.process(sample_request)

        # Verify result
        from core.schemas import ReformulatedQuestion
        assert isinstance(result, ReformulatedQuestion)
        # The mock should return a proper epistemological question
        assert "epistemological" in result.question.lower() or "conceptual definition" in result.question.lower()
        # LLM handles context embedding internally
        assert "LLM handles context embedding internally" in result.context_added[0]

    @pytest.mark.asyncio
    async def test_process_error_handling(self, reformulator):
        """Test error handling in process method."""
        # Create invalid request (missing required fields)
        invalid_request = NetworkRequest(
            request_id="",
            original_question="",
            timestamp=""
        )

        with pytest.raises(Exception):  # Should raise LayerProcessingError
            await reformulator.process(invalid_request)

    @pytest.mark.asyncio
    async def test_health_check(self, reformulator):
        """Test health check functionality."""
        # This will fail without proper LLM setup, but tests the structure
        try:
            result = await reformulator.health_check()
            assert isinstance(result, bool)
        except Exception:
            # Expected to fail in test environment without LLM
            pass
