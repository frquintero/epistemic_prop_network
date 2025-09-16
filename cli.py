#!/usr/bin/env python3
"""Simple CLI interface for the Epistemological Propagation Network."""

import asyncio
import os
import json
from datetime import datetime

from main import EpistemologicalPropagationNetwork


async def demonstrate_auto_metadata():
    """Demonstrate automatic metadata extraction from user questions."""

    print("🧠 EPN CLI - Automatic Metadata Extraction Demo")
    print("=" * 60)

    # Initialize EPN
    epn = EpistemologicalPropagationNetwork()

    # Test questions with different topics
    test_questions = [
        "What does Tezcatlipoca mean to our current society?",
        "What are mental models in cognitive science?",
        "What is the epistemology of knowledge?",
        "How do neural networks work?",
        "What is the meaning of life?"
    ]

    for i, question in enumerate(test_questions, 1):
        print(f"\n📝 Question {i}: {question}")

        # Extract metadata automatically (this is what happens internally)
        metadata = epn._extract_metadata_from_question(question)
        print(f"🔍 Auto-detected metadata: {json.dumps(metadata, indent=2)}")

        print("-" * 40)


async def interactive_cli():
    """Interactive CLI for processing user questions."""

    print("🧠 Epistemological Propagation Network - Interactive CLI")
    print("=" * 60)
    print("Enter your question (or 'quit' to exit, 'demo' for metadata demo)")
    print()

    # Check API key
    if not os.getenv("GROQ_API_KEY"):
        print("❌ ERROR: GROQ_API_KEY environment variable not found!")
        print("Please set your GROQ API key: export GROQ_API_KEY='your_key_here'")
        return

    # Initialize EPN
    epn = EpistemologicalPropagationNetwork()

    while True:
        try:
            question = input("❓ Your question: ").strip()

            if question.lower() in ['quit', 'q']:
                print("👋 Goodbye!")
                break

            if question.lower() == 'demo':
                await demonstrate_auto_metadata()
                continue

            if not question:
                continue

            print("\n🔄 Processing your question through the EPN...")
            print("(This may take 10-15 seconds)")

            # Process question - metadata is extracted automatically!
            result = await epn.process_question(question)

            if result["success"]:
                print("\n" + "=" * 80)
                print("🎯 RESULT")
                print("=" * 80)
                print(f"� REFORMULATED QUESTION: {result.get('reformulated_question', 'N/A')}")
                print()
                print(f"�📋 THESIS: {result['result']['thesis']}")
                print()
                print(f"🔤 DEFINITION: {result['result']['definition']}")
                print()
                print(f"📚 HISTORY: {result['result']['history']}")
                print()
                print(f"🎯 FUNCTION: {result['result']['function']}")
                print()
                print(f"✅ VALIDATION: {result['result']['validation_qualifications']}")
                print()
                print(f"📖 NARRATIVE: {result['result']['narrative']}")
            else:
                print(f"❌ Error: {result['error']}")

            print("\n" + "-" * 80)

        except EOFError:
            print("👋 Input ended (EOF). Goodbye!")
            break
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    asyncio.run(interactive_cli())