#!/usr/bin/env python3
"""Test script to verify Qwen3 reasoning format behavior with Groq API."""

import os

from groq import Groq

# Load API key from environment
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("❌ GROQ_API_KEY environment variable not set")
    exit(1)

client = Groq(api_key=api_key)


def test_reasoning_format(reasoning_format, description):
    """Test a specific reasoning format."""
    print(f"\n{'='*60}")
    print(f"Testing reasoning_format='{reasoning_format}' - {description}")
    print("=" * 60)

    try:
        completion = client.chat.completions.create(
            model="qwen/qwen3-32b",
            messages=[
                {
                    "role": "user",
                    "content": "Explain why fast inference is critical for reasoning models",
                }
            ],
            reasoning_format=(
                reasoning_format if reasoning_format != "default" else None
            ),
            temperature=0.6,
            max_tokens=1000,
            reasoning_effort="default",
            top_p=0.95,
            # top_k=20,  # Might not be supported
            # min_p=0.0,  # Might not be supported
        )

        response = completion.choices[0].message

        print("📝 RESPONSE CONTENT:")
        print("-" * 40)
        print(
            response.content[:500] + "..."
            if len(response.content) > 500
            else response.content
        )
        print("-" * 40)

        # Check for reasoning field
        if hasattr(response, "reasoning") and response.reasoning:
            print("🧠 REASONING FIELD:")
            print("-" * 40)
            print(
                response.reasoning[:500] + "..."
                if len(response.reasoning) > 500
                else response.reasoning
            )
            print("-" * 40)
        else:
            print("🧠 REASONING FIELD: None or empty")

        # Check for <think> tags in content
        if response.content and "<think>" in response.content:
            print("⚠️  WARNING: <think> tags found in content!")
        else:
            print("✅ No <think> tags in content")

    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    """Run all reasoning format tests."""
    print("🔬 Qwen3 Reasoning Format Test")
    print("Testing different reasoning_format options with Groq API")

    # Test parsed format
    test_reasoning_format("parsed", "Separates reasoning into dedicated field")

    # Test hidden format
    test_reasoning_format("hidden", "Returns only final answer")

    # Test raw format
    test_reasoning_format("raw", "Includes reasoning in <think> tags")

    # Test default (no reasoning_format)
    test_reasoning_format("default", "Default behavior (no reasoning_format specified)")

    print(f"\n{'='*60}")
    print("✅ Testing complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
