#!/usr/bin/env python3
"""
Interactive chat REPL for Z.AI glm-4.5

Simple multi-turn conversation interface that maintains conversation history.
Type 'quit' or 'exit' to end the conversation.

Usage:
    export ZAI_API_KEY="your_api_key_here"
    python scripts/chat_repl.py
"""

import os
import sys
from typing import List, Dict

try:
    from zai import ZaiClient
except ImportError:
    print("Error: zai-sdk not installed. Install with:")
    print("pip install zai-sdk")
    sys.exit(1)


def get_api_key() -> str:
    """Get Z.AI API key from environment variable"""
    api_key = os.getenv("ZAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "ZAI_API_KEY is not set. Export it before running:\n"
            "export ZAI_API_KEY=your_key_here"
        )
    return api_key


def main():
    """Main chat REPL loop"""
    print("🤖 Z.AI Chat REPL (glm-4.5)")
    print("Type 'quit' or 'exit' to end the conversation")
    print("-" * 50)

    try:
        # Initialize client
        api_key = get_api_key()
        client = ZaiClient(api_key=api_key)

        # Initialize conversation with system prompt
        conversation: List[Dict[str, str]] = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

        print("AI: Hello! I'm ready to chat with you. What would you like to talk about?")

        while True:
            try:
                # Get user input
                user_input = input("\nYou: ").strip()

                # Check for exit commands
                if user_input.lower() in ("quit", "exit"):
                    print("AI: Goodbye! Have a great day!")
                    break

                # Skip empty input
                if not user_input:
                    continue

                # Add user message to conversation
                conversation.append({"role": "user", "content": user_input})

                # Get AI response
                response = client.chat.completions.create(
                    model="glm-4.5",
                    messages=conversation,
                    temperature=0.6,
                    max_tokens=400
                )

                ai_response = response.choices[0].message.content

                # Display AI response
                print(f"\nAI: {ai_response}")

                # Add AI response to conversation history
                conversation.append({"role": "assistant", "content": ai_response})

            except KeyboardInterrupt:
                print("\n\nAI: Goodbye! Have a great day!")
                break
            except EOFError:
                print("\n\nAI: Goodbye! Have a great day!")
                break
            except Exception as e:
                print(f"\nAI: Sorry, I encountered an error: {e}")
                print("Please try again or type 'quit' to exit.")

    except RuntimeError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()