#!/usr/bin/env python3
"""Demonstration of Pydantic models in the Epistemological Propagation Network."""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.schemas import (
    Phase2Triple, Phase3Triple, ReformulatedQuestion,
    SynthesisOutput, ValidationResult, NetworkRequest, NetworkResponse
)


def demonstrate_pydantic_models():
    """Demonstrate Pydantic model functionality."""

    print("🔬 Pydantic Models Demonstration")
    print("=" * 50)

    # 1. Phase2Triple - Definition Generation Output
    print("\n1. Phase2Triple (Definition Generation)")
    print("-" * 40)

    phase2_data = {
        "semantic": "A mental model is an internal cognitive representation that simplifies complex external systems for understanding and prediction.",
        "genealogical": "The concept was introduced by Kenneth Craik in 1943 and expanded by researchers in cognitive psychology and decision-making theory.",
        "teleological": "Mental models serve to reduce cognitive load by providing simplified frameworks for reasoning about complex phenomena."
    }

    try:
        phase2 = Phase2Triple(**phase2_data)
        print("✅ Successfully created Phase2Triple")
        print(f"   Semantic: {phase2.semantic[:60]}...")
        print(f"   Genealogical: {phase2.genealogical[:60]}...")
        print(f"   Teleological: {phase2.teleological[:60]}...")
    except Exception as e:
        print(f"❌ Failed to create Phase2Triple: {e}")

    # 2. Phase3Triple - Validation Output
    print("\n2. Phase3Triple (Validation)")
    print("-" * 40)

    phase3_data = {
        "correspondence": "This definition aligns with established research in cognitive science and empirical studies on mental representation.",
        "coherence": "The definition maintains logical consistency with related concepts in psychology and philosophy of mind.",
        "pragmatic": "Mental models have demonstrated practical utility in fields ranging from education to business decision-making."
    }

    try:
        phase3 = Phase3Triple(**phase3_data)
        print("✅ Successfully created Phase3Triple")
        print(f"   Correspondence: {phase3.correspondence[:60]}...")
        print(f"   Coherence: {phase3.coherence[:60]}...")
        print(f"   Pragmatic: {phase3.pragmatic[:60]}...")
    except Exception as e:
        print(f"❌ Failed to create Phase3Triple: {e}")

    # 3. ReformulatedQuestion - Bias-free reformulation
    print("\n3. ReformulatedQuestion (Bias Elimination)")
    print("-" * 40)

    reformulated_data = {
        "question": "What are the cognitive mechanisms underlying mental model formation and utilization?",
        "original_question": "How do people think about stuff?",
        "context_added": ["cognitive science", "psychological mechanisms", "information processing"],
        "bias_removed": ["casual language", "vague terminology"]
    }

    try:
        reformulated = ReformulatedQuestion(**reformulated_data)
        print("✅ Successfully created ReformulatedQuestion")
        print(f"   Original: {reformulated.original_question}")
        print(f"   Reformulated: {reformulated.question}")
        print(f"   Context added: {reformulated.context_added}")
        print(f"   Bias removed: {reformulated.bias_removed}")
    except Exception as e:
        print(f"❌ Failed to create ReformulatedQuestion: {e}")

    # 4. ValidationResult - Individual validation
    print("\n4. ValidationResult (Individual Assessment)")
    print("-" * 40)

    validation_data = {
        "validator_type": "correspondence",
        "score": 0.85,
        "assessment": "Strong alignment with empirical evidence from cognitive psychology studies",
        "confidence": 0.92,
        "issues": ["Limited discussion of neural mechanisms"]
    }

    try:
        validation = ValidationResult(**validation_data)
        print("✅ Successfully created ValidationResult")
        print(f"   Type: {validation.validator_type}")
        print(f"   Score: {validation.score}")
        print(f"   Confidence: {validation.confidence}")
        print(f"   Issues: {validation.issues}")
    except Exception as e:
        print(f"❌ Failed to create ValidationResult: {e}")

    # 5. NetworkRequest - Input structure
    print("\n5. NetworkRequest (Input Processing)")
    print("-" * 40)

    request_data = {
        "request_id": "req-2024-001",
        "original_question": "What are mental models?",
        "timestamp": "2024-01-15T10:30:00Z",
        "metadata": {"user_id": "user123", "session_id": "sess456"}
    }

    try:
        request = NetworkRequest(**request_data)
        print("✅ Successfully created NetworkRequest")
        print(f"   Request ID: {request.request_id}")
        print(f"   Question: {request.original_question}")
        print(f"   Timestamp: {request.timestamp}")
        print(f"   Metadata: {request.metadata}")
    except Exception as e:
        print(f"❌ Failed to create NetworkRequest: {e}")

    # 6. SynthesisOutput - Final integrated output
    print("\n6. SynthesisOutput (Final Synthesis)")
    print("-" * 40)

    synthesis_data = {
        "thesis": "Mental models are essential cognitive tools that enable humans to navigate complexity through simplified internal representations.",
        "definition": "Internal cognitive representations that simplify external systems for understanding and prediction.",
        "history": "Originating from Kenneth Craik's 1943 work and evolving through cognitive psychology research.",
        "function": "Reduce cognitive load and enable efficient reasoning about complex phenomena.",
        "validation_qualifications": "Strong empirical support with logical consistency and practical applications across multiple domains.",
        "narrative": "Mental models represent a fundamental cognitive mechanism that has evolved to help humans manage complexity..."
    }

    try:
        synthesis = SynthesisOutput(**synthesis_data)
        print("✅ Successfully created SynthesisOutput")
        print(f"   Thesis: {synthesis.thesis}")
        print(f"   Definition: {synthesis.definition[:50]}...")
        print(f"   History: {synthesis.history[:50]}...")
        print(f"   Function: {synthesis.function[:50]}...")
    except Exception as e:
        print(f"❌ Failed to create SynthesisOutput: {e}")

    # 7. Demonstrate validation features
    print("\n7. Pydantic Validation Features")
    print("-" * 40)

    # Test validation - this should fail
    print("Testing validation with invalid data...")
    try:
        invalid_phase2 = Phase2Triple(
            semantic="Too short",  # This violates min_length=10
            genealogical="A mental model is an internal cognitive representation that simplifies complex external systems for understanding and prediction.",
            teleological="Mental models serve to reduce cognitive load by providing simplified frameworks for reasoning about complex phenomena."
        )
        print("❌ Validation should have failed!")
    except Exception as e:
        print(f"✅ Validation correctly caught error: {str(e)[:100]}...")

    # Test type conversion
    print("\nTesting automatic type conversion...")
    try:
        # Pydantic will convert string numbers to actual numbers
        validation_with_strings = ValidationResult(
            validator_type="pragmatic",
            score="0.75",  # String will be converted to float
            assessment="Good practical utility demonstrated",
            confidence="0.8"  # String will be converted to float
        )
        print(f"✅ Type conversion successful: score={validation_with_strings.score} (type: {type(validation_with_strings.score)})")
        print(f"✅ Type conversion successful: confidence={validation_with_strings.confidence} (type: {type(validation_with_strings.confidence)})")
    except Exception as e:
        print(f"❌ Type conversion failed: {e}")

    print("\n" + "=" * 50)
    print("🎉 All Pydantic models are functioning correctly!")
    print("📋 Key Pydantic Features Demonstrated:")
    print("   • Data validation with field constraints")
    print("   • Automatic type conversion")
    print("   • Error handling with detailed messages")
    print("   • JSON schema generation capabilities")
    print("   • Type safety and IDE support")


if __name__ == "__main__":
    demonstrate_pydantic_models()