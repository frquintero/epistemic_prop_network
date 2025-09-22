#!/usr/bin/env python3
"""Interactive multi-turn REPL for Z.AI (glm-4.5).

This script provides a small chat REPL that preserves conversation
history and supports optional streaming output. Commands:
  /quit    - exit the REPL
  /history - print conversation history
  /clear   - clear conversation history (keeps system prompt)
  /stream  - toggle streaming mode

Set `ZAI_API_KEY` in your environment before running.
"""

from __future__ import annotations

import os
import sys
from typing import List, Dict

try:
    from zai import ZaiClient
except Exception:  # pragma: no cover - helpful message
    print("Missing dependency: install with `pip install zai-sdk`")
    sys.exit(1)


def get_api_key() -> str:
    key = os.getenv("ZAI_API_KEY")
    if not key:
        raise RuntimeError(
            "ZAI_API_KEY is not set. Export it, e.g.:\n"
            "export ZAI_API_KEY=your_key_here"
        )
    return key


def create_client() -> ZaiClient:
    # The client will pick up api_key from env when None,
    # but we pass it explicitly for clarity.
    api_key = get_api_key()
    return ZaiClient(api_key=api_key)


def print_help() -> None:
    print("Commands:")
    print("  /quit    - exit")
    print("  /history - show conversation history")
    print("  /clear   - clear history (keeps system prompt)")
    print("  /stream  - toggle streaming on/off")


def run_repl() -> None:
    print("Z.AI interactive multi-turn REPL (type /quit to exit)")

    try:
        client = create_client()
    except Exception as exc:
        print(f"Error creating client: {exc}")
        sys.exit(1)

    system_prompt = (
        "You are a helpful assistant. Answer concisely and helpfully."
    )

    conversation: List[Dict[str, str]] = [
        {"role": "system", "content": system_prompt}
    ]

    streaming = False

    while True:
        try:
            user = input("You: ")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        cmd = user.strip()
        if not cmd:
            continue

        if cmd.startswith("/"):
            if cmd == "/quit":
                break
            if cmd == "/history":
                for m in conversation:
                    role = m.get("role", "")
                    content = m.get("content", "")
                    print(f"[{role}] {content}")
                continue
            if cmd == "/clear":
                conversation = [{"role": "system", "content": system_prompt}]
                print("Conversation cleared.")
                continue
            if cmd == "/stream":
                streaming = not streaming
                print(f"Streaming set to {streaming}")
                continue
            print_help()
            continue

        # Add user message
        conversation.append({"role": "user", "content": user})

        try:
            if streaming:
                stream = client.chat.completions.create(
                    model="glm-4.5",
                    messages=conversation,
                    stream=True,
                )

                full = ""
                for chunk in stream:
                    # chunk.choices[0].delta.content may be None
                    delta = chunk.choices[0].delta
                    content = getattr(delta, "content", None)
                    if content:
                        print(content, end="", flush=True)
                        full += content
                print()
                assistant_text = full
            else:
                resp = client.chat.completions.create(
                    model="glm-4.5",
                    messages=conversation,
                    temperature=0.6,
                    max_tokens=512,
                )
                assistant_text = resp.choices[0].message.content

            print("AI:", assistant_text)
            conversation.append({"role": "assistant", "content": assistant_text})

        except Exception as exc:  # pragma: no cover - runtime errors depend on env
            print(f"Error from API: {exc}")


if __name__ == "__main__":
    run_repl()