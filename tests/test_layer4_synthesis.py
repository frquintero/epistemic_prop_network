"""Unit tests for Layer 4 Synthesis & Communication.

Tests the SynthesisNode and Layer4SynthesisManager.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch
from core.schemas import Phase3Triple, SynthesisOutput
from core.exceptions import LayerProcessingError, LLMError
from layers.layer4_synthesis import (
    Layer4SynthesisManager,
    SynthesisNode
)


class TestSynthesisNode:
    """Test cases for the Synthesis Node."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client for testing."""
        client = AsyncMock()
        client.generate_text.return_value = """Mental models are cognitive tools that simplify complexity, allowing us to navigate the world. Their story begins with Kenneth Craik in 1943, who proposed that the mind builds 'small-scale models' of reality to predict events.

Empirically, neuroscience supports that our brains form such representations, and logically, these models cohere with theories of learning and memory. Pragmatically, they are invaluable for improving decisions.

**Thesis:** Ultimately, mental models are indispensable yet imperfect frameworks that shape our understanding, and mastering their use is key to adaptive thinking in a complex world."""
        return client

    @pytest.fixture
    def synthesis_node(self):
        """Create a SynthesisNode instance for testing."""
        return SynthesisNode()

    @pytest.fixture
    def test_phase3_triple(self):
        """Create a test Phase 3 triple."""
        return Phase3Triple(
            correspondence="The definition is empirically supported by brain imaging studies showing internal representations. The history is accurate per scientific literature.",
            coherence="The definition is logically consistent. The history coherently explains the concept's development. The function aligns with cognitive theories.",
            pragmatic="The concept is highly useful: definitions aid in designing experiments, history helps avoid past mistakes, and functions provide frameworks for improving decision-making."
        )

    def test_initialization(self, synthesis_node):
        """Test that SynthesisNode initializes correctly."""
        assert synthesis_node.logger is not None
        # llm_client is created lazily, so it should be None initially
        assert synthesis_node.llm_client is None
        # But _get_llm_client should create it
        llm_client = synthesis_node._get_llm_client()
        assert llm_client is not None
        assert synthesis_node.llm_client is not None

    @pytest.mark.asyncio
    async def test_process_success(self, synthesis_node, test_phase3_triple, mock_llm_client):
        """Test successful processing of a Phase 3 triple."""
        # Mock the _get_llm_client method to return our mock client
        synthesis_node._get_llm_client = lambda: mock_llm_client

        result = await synthesis_node.process(test_phase3_triple)

        assert isinstance(result, SynthesisOutput)
        assert len(result.narrative) > 0
        assert len(result.thesis) > 0
        assert "mental models" in result.narrative.lower()
        mock_llm_client.generate_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_process_llm_error(self, synthesis_node, test_phase3_triple):
        """Test handling of LLM errors during processing."""
        # Mock the _get_llm_client to raise an error
        mock_client = AsyncMock()
        mock_client.generate_text.side_effect = LLMError("LLM service unavailable")
        synthesis_node._get_llm_client = lambda: mock_client

        with pytest.raises(LayerProcessingError, match="Synthesis failed"):
            await synthesis_node.process(test_phase3_triple)

    def test_build_synthesis_prompt(self, synthesis_node, test_phase3_triple):
        """Test synthesis prompt building."""
        prompt = synthesis_node._build_synthesis_prompt(test_phase3_triple)

        assert isinstance(prompt, str)
        assert len(prompt) > 100
        assert "CORRESPONDENCE VALIDATION" in prompt
        assert "COHERENCE VALIDATION" in prompt
        assert "PRAGMATIC VALIDATION" in prompt
        assert "SYNTHESIS REQUIREMENTS" in prompt
        assert test_phase3_triple.correspondence in prompt
        assert test_phase3_triple.coherence in prompt
        assert test_phase3_triple.pragmatic in prompt

    def test_extract_thesis(self, synthesis_node):
        """Test thesis extraction from response."""
        response_with_thesis = """
        This is a comprehensive narrative about mental models.

        **Thesis:** Mental models are essential cognitive frameworks that shape our understanding of the world.

        This concludes the analysis.
        """

        thesis = synthesis_node._extract_thesis(response_with_thesis)
        assert thesis is not None
        assert "Mental models are essential" in thesis

    def test_extract_thesis_no_marker(self, synthesis_node):
        """Test thesis extraction when no explicit marker is present."""
        response_without_marker = """
        Mental models serve important functions in cognition.
        They help us understand complex systems.
        Ultimately, they are indispensable tools for human reasoning.
        """

        thesis = synthesis_node._extract_thesis(response_without_marker)
        assert thesis is not None
        assert "indispensable tools for human reasoning" in thesis

    def test_extract_synthesis_output(self, synthesis_node, mock_llm_client):
        """Test extraction of synthesis output from LLM response."""
        response = """Mental models are cognitive tools that simplify complexity.

        **Thesis:** Mental models are indispensable frameworks for understanding.

        The definition focuses on internal representations.
        Historically, they were introduced by Kenneth Craik.
        Functionally, they enable prediction and decision-making.
        Validation shows strong empirical support."""

        synthesis_node._get_llm_client = lambda: mock_llm_client
        output = synthesis_node._extract_synthesis_output(response)

        assert isinstance(output, SynthesisOutput)
        assert "Mental models are indispensable" in output.thesis
        assert len(output.narrative) > 0
        assert len(output.definition) > 0
        assert len(output.history) > 0
        assert len(output.function) > 0
        assert len(output.validation_qualifications) > 0


class TestLayer4SynthesisManager:
    """Test cases for the Layer4SynthesisManager."""

    @pytest.fixture
    def manager(self):
        """Create a Layer4SynthesisManager instance."""
        return Layer4SynthesisManager()

    @pytest.fixture
    def test_phase3_triple(self):
        """Create a test Phase 3 triple."""
        return Phase3Triple(
            correspondence="Empirical validation results here.",
            coherence="Logical consistency validation here.",
            pragmatic="Practical utility validation here."
        )

    def test_initialization(self, manager):
        """Test that Layer4SynthesisManager initializes correctly."""
        assert manager.logger is not None
        assert manager.synthesis_node is not None

    @pytest.mark.asyncio
    async def test_process_success(self, manager, test_phase3_triple):
        """Test successful processing through the manager."""
        # Mock the synthesis node's process method
        mock_output = SynthesisOutput(
            thesis="Test thesis statement about mental models and their importance.",
            definition="Test definition of mental models as cognitive frameworks.",
            history="Test history of mental models from Kenneth Craik to modern research.",
            function="Test function of mental models in decision making and problem solving.",
            validation_qualifications="Test validation showing empirical support and practical utility.",
            narrative="This is a comprehensive test narrative that provides detailed information about mental models, their development, and their significance in human cognition. The narrative explores how these cognitive tools help us understand complex systems and make better decisions in various contexts."
        )

        with patch.object(manager.synthesis_node, 'process', return_value=mock_output):
            result = await manager.process(test_phase3_triple)

            assert isinstance(result, SynthesisOutput)
            assert result.thesis == "Test thesis statement about mental models and their importance."
            assert "comprehensive test narrative" in result.narrative

    @pytest.mark.asyncio
    async def test_process_error_handling(self, manager, test_phase3_triple):
        """Test error handling in the manager."""
        with patch.object(manager.synthesis_node, 'process', side_effect=Exception("Processing failed")):
            with pytest.raises(LayerProcessingError, match="Layer 4 synthesis failed"):
                await manager.process(test_phase3_triple)