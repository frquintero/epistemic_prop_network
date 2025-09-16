"""Basic test for Layer 3 Validation Agents."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from core.schemas import Phase2Triple
from layers.layer3_validation import (
    Layer3ValidationManager,
    CorrespondenceValidator,
    CoherenceValidator,
    PragmaticValidator
)


class TestCorrespondenceValidator:
    """Test Correspondence Validator."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing."""
        client = MagicMock()
        client.generate_text = AsyncMock(return_value="Correspondence validation: Outputs align with empirical evidence from scientific studies.")
        return client

    @pytest.fixture
    def validator(self, mock_llm_client):
        """Create validator with mocked client."""
        return CorrespondenceValidator(llm_client=mock_llm_client)

    @pytest.fixture
    def sample_phase2_triple(self):
        """Sample Phase 2 triple for testing."""
        return Phase2Triple(
            semantic="A mental model is an internal representation of external reality.",
            genealogical="Mental models were introduced by Kenneth Craik in 1943.",
            teleological="Mental models enable prediction and decision-making."
        )

    @pytest.mark.asyncio
    async def test_process_success(self, validator, sample_phase2_triple):
        """Test successful correspondence validation."""
        result = await validator.process(sample_phase2_triple)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Correspondence validation" in result

        # Verify LLM was called
        validator.llm_client.generate_text.assert_called_once()


class TestCoherenceValidator:
    """Test Coherence Validator."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing."""
        client = MagicMock()
        client.generate_text = AsyncMock(return_value="Coherence validation: Logical consistency maintained across all components.")
        return client

    @pytest.fixture
    def validator(self, mock_llm_client):
        """Create validator with mocked client."""
        return CoherenceValidator(llm_client=mock_llm_client)

    @pytest.fixture
    def sample_phase2_triple(self):
        """Sample Phase 2 triple for testing."""
        return Phase2Triple(
            semantic="A mental model is an internal representation of external reality.",
            genealogical="Mental models were introduced by Kenneth Craik in 1943.",
            teleological="Mental models enable prediction and decision-making."
        )

    @pytest.mark.asyncio
    async def test_process_success(self, validator, sample_phase2_triple):
        """Test successful coherence validation."""
        result = await validator.process(sample_phase2_triple)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Coherence validation" in result

        # Verify LLM was called
        validator.llm_client.generate_text.assert_called_once()


class TestPragmaticValidator:
    """Test Pragmatic Validator."""

    @pytest.fixture
    def mock_llm_client(self):
        """Mock LLM client for testing."""
        client = MagicMock()
        client.generate_text = AsyncMock(return_value="Pragmatic validation: Framework has strong utility in education and business domains.")
        return client

    @pytest.fixture
    def validator(self, mock_llm_client):
        """Create validator with mocked client."""
        return PragmaticValidator(llm_client=mock_llm_client)

    @pytest.fixture
    def sample_phase2_triple(self):
        """Sample Phase 2 triple for testing."""
        return Phase2Triple(
            semantic="A mental model is an internal representation of external reality.",
            genealogical="Mental models were introduced by Kenneth Craik in 1943.",
            teleological="Mental models enable prediction and decision-making."
        )

    @pytest.mark.asyncio
    async def test_process_success(self, validator, sample_phase2_triple):
        """Test successful pragmatic validation."""
        result = await validator.process(sample_phase2_triple)

        assert isinstance(result, str)
        assert len(result) > 0
        assert "Pragmatic validation" in result

        # Verify LLM was called
        validator.llm_client.generate_text.assert_called_once()


class TestLayer3ValidationManager:
    """Test Layer 3 Validation Manager."""

    @pytest.fixture
    def manager(self):
        """Create validation manager."""
        return Layer3ValidationManager()

    @pytest.fixture
    def sample_phase2_triple(self):
        """Sample Phase 2 triple for testing."""
        return Phase2Triple(
            semantic="A mental model is an internal representation of external reality.",
            genealogical="Mental models were introduced by Kenneth Craik in 1943.",
            teleological="Mental models enable prediction and decision-making."
        )

    @pytest.mark.asyncio
    async def test_process_structure(self, manager, sample_phase2_triple):
        """Test that manager returns properly structured Phase3Triple."""
        # Note: This test will use real LLM calls, so it may be slow
        # In production, we'd mock the validators
        result = await manager.process(sample_phase2_triple)

        assert hasattr(result, 'correspondence')
        assert hasattr(result, 'coherence')
        assert hasattr(result, 'pragmatic')

        assert isinstance(result.correspondence, str)
        assert isinstance(result.coherence, str)
        assert isinstance(result.pragmatic, str)

        assert len(result.correspondence) > 0
        assert len(result.coherence) > 0
        assert len(result.pragmatic) > 0