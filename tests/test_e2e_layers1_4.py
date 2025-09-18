"""End-to-end integration tests for Layers 1-4 of the Epistemological Propagation Network.

Tests the complete flow from raw user input through final synthesis output.
"""

import asyncio
from datetime import datetime
from unittest.mock import patch

import pytest

from core.exceptions import LayerProcessingError
from core.schemas import (
    NetworkRequest,
    Phase2Triple,
    Phase3Triple,
    ReformulatedQuestion,
    SynthesisOutput,
)
from layers.layer1_reformulation import Reformulator
from layers.layer2_definition import Layer2DefinitionManager
from layers.layer3_validation import Layer3ValidationManager
from layers.layer4_synthesis import Layer4SynthesisManager


@pytest.mark.asyncio
async def test_complete_layers1_4_flow():
    """Test the complete end-to-end flow from Layers 1 through 4."""
    # Test input
    original_question = "What are mental models?"
    request = NetworkRequest(
        request_id="test-e2e-123",
        original_question=original_question,
        timestamp=datetime.now().isoformat(),
        metadata={"test": "integration"},
    )

    # Expected outputs for mocking
    mock_reformulated = ReformulatedQuestion(
        question="Provide a comprehensive epistemological account of the concept 'mental models', including its semantic definition, historical origin, and primary functions, acknowledging its use across cognitive psychology, philosophy, and systems engineering.",
        original_question=original_question,
        context_added=["epistemological context", "interdisciplinary relevance"],
        bias_removed=["loaded language eliminated"],
    )

    mock_phase2 = Phase2Triple(
        semantic="A mental model is an internal, simplified cognitive representation of an external system or process, used for understanding, reasoning, and prediction. It serves as a framework for interpreting reality and making decisions.",
        genealogical="The concept was formally introduced by Kenneth Craik in 1943, expanded by Philip Johnson-Laird in human reasoning research, and popularized in decision-making by Charlie Munger. It has roots in cognitive psychology and systems theory.",
        teleological="Mental models enable individuals to simulate outcomes, form explanations, and make decisions efficiently without direct experience. They serve as cognitive tools for navigating complexity and uncertainty.",
    )

    mock_phase3 = Phase3Triple(
        coherence="The definition logically follows from the historical development. The functional claims cohere with established theories of cognition and learning. The framework maintains internal consistency.",
        pragmatic="Mental models are highly practical: they aid in designing experiments, help avoid past mistakes, and provide frameworks for improving decision-making in business, education, and policy contexts.",
        tension="Apparent tensions between historical nuance and functional breadth are resolved through domain-specific framing that preserves conceptual integrity.",
    )

    mock_synthesis = SynthesisOutput(
        raw_response="Mental models are indispensable yet imperfect cognitive frameworks that shape our understanding of complex systems and enable adaptive thinking in an uncertain world. Mental models are internal cognitive representations that simplify external reality for understanding, reasoning, and prediction. Originating with Kenneth Craik in 1943, the concept evolved through cognitive psychology and was popularized in decision-making contexts. They enable simulation of outcomes, formation of explanations, and efficient decision-making without direct experience. Empirically supported by neuroscience, logically consistent with cognitive theories, and highly practical across multiple domains. Mental models represent a cornerstone of cognitive science, bridging the gap between abstract theory and practical application. Their journey from Craik's foundational work to modern applications demonstrates the enduring value of simplified representations in human cognition."
    )

    # Initialize all layer managers
    reformulator = Reformulator()
    layer2_manager = Layer2DefinitionManager()
    layer3_manager = Layer3ValidationManager()
    layer4_manager = Layer4SynthesisManager()

    # Create mock LLM clients
    from unittest.mock import AsyncMock

    mock_reformulator_client = AsyncMock()
    mock_reformulator_client.generate_text.return_value = mock_reformulated.question

    mock_l2_client = AsyncMock()
    mock_l2_client.generate_text.side_effect = [
        mock_phase2.semantic,
        mock_phase2.genealogical,
        mock_phase2.teleological,
    ]

    mock_l3_client = AsyncMock()
    mock_l3_client.generate_text.side_effect = [
        mock_phase3.coherence,
        mock_phase3.pragmatic,
        mock_phase3.tension,
    ]

    mock_l4_client = AsyncMock()
    mock_l4_client.generate_text.return_value = mock_synthesis.raw_response

    # Replace Layer 3 validators with mocked ones
    layer3_manager.coherence_validator.llm_client = mock_l3_client
    layer3_manager.pragmatic_validator.llm_client = mock_l3_client
    layer3_manager.tension_validator.llm_client = mock_l3_client

    # Mock the LLM calls for other layers
    with (
        patch.object(
            reformulator, "_get_llm_client", return_value=mock_reformulator_client
        ),
        patch.object(
            layer2_manager.semantic_node, "_get_llm_client", return_value=mock_l2_client
        ),
        patch.object(
            layer2_manager.genealogical_node,
            "_get_llm_client",
            return_value=mock_l2_client,
        ),
        patch.object(
            layer2_manager.teleological_node,
            "_get_llm_client",
            return_value=mock_l2_client,
        ),
        patch.object(
            layer4_manager.synthesis_node,
            "_get_llm_client",
            return_value=mock_l4_client,
        ),
    ):

        # Execute the complete flow
        print(
            "🧠 Starting Epistemological Propagation Network - Layers 1-4 Integration Test"
        )
        print(f"📝 Original Question: {original_question}")

        # Execute the complete flow
        print(
            "🧠 Starting Epistemological Propagation Network - Layers 1-4 Integration Test"
        )
        print(f"📝 Original Question: {original_question}")

        # Layer 1: Reformulation
        print("\n🔄 Layer 1: Reformulation")
        reformulated = await reformulator.process(request)
        print(f"✅ Reformulated: {reformulated.question[:100]}...")

        # Layer 2: Definition Generation
        print("\n🔄 Layer 2: Definition Generation")
        phase2_result = await layer2_manager.process(reformulated)
        print(f"✅ Semantic: {phase2_result.semantic[:80]}...")
        print(f"✅ Genealogical: {phase2_result.genealogical[:80]}...")
        print(f"✅ Teleological: {phase2_result.teleological[:80]}...")

        # Layer 3: Validation
        print("\n🔄 Layer 3: Validation")
        phase3_result = await layer3_manager.process(phase2_result)
        print(f"✅ Coherence: {phase3_result.coherence[:80]}...")
        print(f"✅ Pragmatic: {phase3_result.pragmatic[:80]}...")
        print(f"✅ Tension: {phase3_result.tension[:80]}...")

        # Layer 4: Synthesis
        print("\n🔄 Layer 4: Synthesis")
        final_result = await layer4_manager.process(phase3_result)
        print(f"✅ Raw Response Length: {len(final_result.raw_response)} characters")

        # Verify the complete flow
        assert isinstance(reformulated, ReformulatedQuestion)
        assert isinstance(phase2_result, Phase2Triple)
        assert isinstance(phase3_result, Phase3Triple)
        assert isinstance(final_result, SynthesisOutput)

        # Verify content quality
        assert len(final_result.raw_response) > 100
        assert len(final_result.raw_response) > 50
        assert "mental models" in final_result.raw_response.lower()

        print("\n🎉 SUCCESS: Complete Layers 1-4 integration test passed!")
        print(f"📊 Final Output Length: {len(final_result.raw_response)} characters")


@pytest.mark.asyncio
async def test_layer4_error_handling():
    """Test Layer 4 error handling and fallback behavior."""
    layer4_manager = Layer4SynthesisManager()

    # Create a valid Phase 3 triple
    phase3_triple = Phase3Triple(
        coherence="Valid coherence validation.",
        pragmatic="Valid pragmatic validation.",
        tension="Valid tension analysis.",
    )

    # Mock a processing error
    with patch.object(
        layer4_manager.synthesis_node,
        "process",
        side_effect=Exception("LLM service unavailable"),
    ):
        with pytest.raises(LayerProcessingError, match="Layer 4 synthesis failed"):
            await layer4_manager.process(phase3_triple)


@pytest.mark.asyncio
async def test_layer4_empty_inputs():
    """Test Layer 4 behavior with minimal input data."""
    layer4_manager = Layer4SynthesisManager()

    # Create minimal Phase 3 triple
    phase3_triple = Phase3Triple(
        coherence="Minimal coherence data for testing.",
        pragmatic="Minimal pragmatic data for testing.",
        tension="Minimal tension data for testing.",
    )

    # Mock successful processing
    mock_output = SynthesisOutput(
        raw_response="Minimal test thesis about the subject matter. Minimal definition extracted from input. Minimal historical context provided. Minimal functional description available. Minimal validation qualifications noted. This is a minimal test narrative that meets the length requirements for validation while demonstrating the synthesis process with limited input data."
    )

    with patch.object(
        layer4_manager.synthesis_node, "process", return_value=mock_output
    ):
        result = await layer4_manager.process(phase3_triple)

        assert isinstance(result, SynthesisOutput)
        assert len(result.raw_response) >= 50
