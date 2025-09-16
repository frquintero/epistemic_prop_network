"""Unit tests for Layer 2 Definition Generation.

Tests the Semantic, Genealogical, and Teleological nodes along with the Layer2DefinitionManager.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock
from core.schemas import ReformulatedQuestion, Phase2Triple
from core.exceptions import LayerProcessingError, LLMError
from layers.layer2_definition import (
    Layer2DefinitionManager,
    SemanticNode,
    GenealogicalNode,
    TeleologicalNode
)


class TestSemanticNode:
    """Test cases for the Semantic Node."""

    @pytest.fixture
    def mock_llm_client(self):
        """Create a mock LLM client for testing."""
        client = AsyncMock()
        client.generate_text.return_value = "A mental model is an internal representation of external reality used for understanding and prediction."
        return client

    @pytest.fixture
    def semantic_node(self, mock_llm_client):
        """Create a SemanticNode instance with mocked LLM client."""
        return SemanticNode(mock_llm_client)

    @pytest.fixture
    def test_question(self):
        """Create a test reformulated question."""
        return ReformulatedQuestion(
            question="What is a mental model?",
            original_question="What are mental models?",
            context_added=["LLM handles context embedding internally"],
            bias_removed=["LLM handles bias elimination internally"]
        )

    def test_initialization(self, semantic_node):
        """Test that SemanticNode initializes correctly."""
        assert semantic_node.llm_client is not None
        assert semantic_node.logger is not None

    @pytest.mark.asyncio
    async def test_process_success(self, semantic_node, test_question, mock_llm_client):
        """Test successful processing of a question."""
        result = await semantic_node.process(test_question)

        assert isinstance(result, str)
        assert len(result) > 0
        mock_llm_client.generate_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_success(self, semantic_node, mock_llm_client):
        """Test successful health check."""
        result = await semantic_node.health_check()
        assert result is True


class TestLayer2DefinitionManager:
    """Test cases for the Layer2DefinitionManager."""

    @pytest.fixture
    def manager(self):
        """Create a Layer2DefinitionManager instance with individual mocked LLM clients."""
        # Create separate mock clients for each node to avoid side_effect conflicts
        semantic_client = AsyncMock()
        semantic_client.generate_text.return_value = "Epistemology is the study of knowledge and belief."

        genealogical_client = AsyncMock()
        genealogical_client.generate_text.return_value = "Epistemology originated in ancient Greek philosophy with Plato and Aristotle."

        teleological_client = AsyncMock()
        teleological_client.generate_text.return_value = "The purpose of epistemology is to understand the nature and limits of human knowledge."

        manager = Layer2DefinitionManager()
        manager.semantic_node.llm_client = semantic_client
        manager.genealogical_node.llm_client = genealogical_client
        manager.teleological_node.llm_client = teleological_client

        return manager

    @pytest.fixture
    def test_question(self):
        """Create a test reformulated question."""
        return ReformulatedQuestion(
            question="What is epistemology?",
            original_question="What is epistemology?",
            context_added=["LLM handles context embedding internally"],
            bias_removed=["LLM handles bias elimination internally"]
        )

    def test_initialization(self, manager):
        """Test that Layer2DefinitionManager initializes correctly."""
        assert manager.semantic_node is not None
        assert manager.genealogical_node is not None
        assert manager.teleological_node is not None
        assert manager.logger is not None

    @pytest.mark.asyncio
    async def test_process_success(self, manager, test_question):
        """Test successful parallel processing of all nodes."""
        result = await manager.process(test_question)

        assert isinstance(result, Phase2Triple)
        assert isinstance(result.semantic, str)
        assert isinstance(result.genealogical, str)
        assert isinstance(result.teleological, str)
        assert len(result.semantic) > 0
        assert len(result.genealogical) > 0
        assert len(result.teleological) > 0

    def test_fallback_generation(self, manager):
        """Test fallback response generation."""
        semantic_fallback = manager._generate_fallback_semantic()
        genealogical_fallback = manager._generate_fallback_genealogical()
        teleological_fallback = manager._generate_fallback_teleological()

        assert isinstance(semantic_fallback, str)
        assert isinstance(genealogical_fallback, str)
        assert isinstance(teleological_fallback, str)
        assert len(semantic_fallback) > 50
        assert len(genealogical_fallback) > 50
        assert len(teleological_fallback) > 50