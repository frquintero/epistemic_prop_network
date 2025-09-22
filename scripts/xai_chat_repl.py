#!/usr/bin/env python3
"""Interactive REPL for X.AI Grok model (`grok-4-fast-reasoning`).

Requires XAI_API_KEY in the environment. Mirrors the multi-turn pattern
used elsewhere in the repo and supports optional streaming where the SDK
provides chunked output.

Commands:
  /quit    - exit
  /history - print conversation history
  /clear   - clear conversation history (keeps system prompt)
  /stream  - toggle streaming mode

"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, List, Dict

try:
    # this repo uses the OpenAI-compatible X.AI client import pattern
    from openai import OpenAI
    import httpx
except Exception:
    print("Missing dependency: please install the X.AI/OpenAI client (pip install openai httpx)")
    sys.exit(1)


def get_api_key() -> str:
    key = os.getenv("XAI_API_KEY")
    if not key:
        raise RuntimeError(
            "XAI_API_KEY is not set. Export it, e.g.:\n"
            "export XAI_API_KEY=your_key_here"
        )
    return key


def create_client() -> OpenAI:
    key = get_api_key()
    client = OpenAI(api_key=key, base_url="https://api.x.ai/v1", timeout=httpx.Timeout(60.0))
    return client


def extract_text_from_output(output: Any) -> str:
    """Recursively extract human-readable text from X.AI response output.

    The SDK may return nested lists, dicts, or objects with `.text` or
    `.content` attributes. This helper walks the structure and concatenates
    any textual pieces it finds.
    """

    pieces: List[str] = []

    def walk(obj: Any) -> None:
        if obj is None:
            return
        # SDK may provide simple strings
        if isinstance(obj, str):
            pieces.append(obj)
            return
        # plain dicts
        if isinstance(obj, dict):
            # common key names that can hold text
            for k in ("text", "content", "message", "output_text"):
                if k in obj and isinstance(obj[k], (str, list, dict)):
                    walk(obj[k])
            # also recurse through values
            for v in obj.values():
                walk(v)
            return
        # lists/tuples
        if isinstance(obj, (list, tuple)):
            for item in obj:
                walk(item)
            return
        # some SDK objects expose .text or .content
        try:
            txt = getattr(obj, "text", None)
            if isinstance(txt, str):
                pieces.append(txt)
                return
        except Exception:
            pass
        try:
            cont = getattr(obj, "content", None)
            if isinstance(cont, str):
                pieces.append(cont)
                return
        except Exception:
            pass
        # Do NOT fallback to stringifying SDK objects (they are noisy).
        # Only collect explicit textual fields found above.

    walk(output)
    # join pieces with newlines for readability
    return "\n".join(pieces)


def extract_text_from_event(event: Any) -> str:
    """Extract only the human text from a streaming event.

    Streaming events from X.AI will often carry small fields such as
    `delta`, `text`, `content`, or `snapshot`. Return the concatenated
    text or empty string when no plain text is present.
    """
    # Prefer attribute names commonly used in streaming events
    for attr in ("delta", "text", "content", "snapshot"):
        try:
            val = getattr(event, attr, None)
        except Exception:
            val = None
        if isinstance(val, str) and val:
            return val
        # some fields may be lists/dicts
        if isinstance(val, (list, tuple, dict)):
            return extract_text_from_output(val)

    # Some events carry nested objects in `.part` or `.output`
    try:
        if hasattr(event, "part"):
            return extract_text_from_output(getattr(event, "part"))
    except Exception:
        pass

    # No human-readable text found
    return ""


def run_repl(model: str, temperature: float, stream_default: bool) -> None:
    print(f"🤖 X.AI Grok REPL ({model})")
    print("Type '/quit' to exit. Toggle streaming with '/stream'.")

    try:
        client = create_client()
    except Exception as exc:
        print(f"Error creating X.AI client: {exc}")
        sys.exit(1)

    system_prompt = "You are Grok, a helpful assistant inspired by the Hitchhiker's Guide to the Galaxy."

    conversation: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
    streaming = stream_default

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
                    print(f"[{m['role']}] {m['content']}")
                continue
            if cmd == "/clear":
                conversation = [{"role": "system", "content": system_prompt}]
                print("Conversation cleared.")
                continue
            if cmd == "/stream":
                streaming = not streaming
                print(f"Streaming set to {streaming}")
                continue
            print("Unknown command")
            continue

        # Add user message
        conversation.append({"role": "user", "content": user})

        try:
            printed_from_stream = False
            if streaming:
                # Attempt streaming API; event shapes may vary by SDK version.
                # Some SDKs return a ResponseStreamManager that must be used
                # as a context manager or via a specific iterator method. We
                # try common patterns, and if none work we fall back to a
                # non-streaming request so the user still gets a reply.
                try:
                    stream = client.responses.stream(
                        model=model,
                        input=conversation,
                        temperature=temperature,
                    )

                    full = ""

                    # If the returned stream is directly iterable
                    if hasattr(stream, "__iter__"):
                        for event in stream:
                            text = extract_text_from_output(event)
                            if text:
                                print(text, end="", flush=True)
                                full += text
                    else:
                        # Try using it as a context manager
                        used = False
                        try:
                            with stream as s:
                                for event in s:
                                    text = extract_text_from_output(event)
                                    if text:
                                        print(text, end="", flush=True)
                                        full += text
                            used = True
                        except Exception:
                            used = False

                        if not used:
                            # Try other common accessors
                            if hasattr(stream, "events"):
                                for event in stream.events():
                                    text = extract_text_from_output(event)
                                    if text:
                                        print(text, end="", flush=True)
                                        full += text
                            elif hasattr(stream, "get_events"):
                                for event in stream.get_events():
                                    text = extract_text_from_output(event)
                                    if text:
                                        print(text, end="", flush=True)
                                        full += text
                            elif hasattr(stream, "iter_text"):
                                for chunk in stream.iter_text():
                                    print(chunk, end="", flush=True)
                                    full += chunk
                            else:
                                # Unknown stream shape — raise to trigger fallback
                                raise TypeError("Stream object is not directly iterable")

                    print()
                    assistant_text = full
                    printed_from_stream = True

                except Exception as exc:  # streaming failed, fall back to non-stream
                    if os.getenv("DEBUG") == "1":
                        print(f"[DEBUG] streaming error: {exc}")
                        try:
                            print("[DEBUG] stream repr:", repr(stream))
                            print("[DEBUG] stream dir:", dir(stream))
                        except Exception:
                            pass
                    # Fallback: do a normal (non-streaming) request so the user
                    # still receives a response.
                    try:
                        resp = client.responses.create(
                            model=model,
                            input=conversation,
                            temperature=temperature,
                        )
                        assistant_text = extract_text_from_output(getattr(resp, "output", resp))
                        printed_from_stream = False
                    except Exception as exc2:
                        raise
            else:
                resp = client.responses.create(
                    model=model,
                    input=conversation,
                    temperature=temperature,
                )

                # SDK populates resp.output in various shapes; extract human text
                assistant_text = extract_text_from_output(getattr(resp, "output", resp))
                printed_from_stream = False

            if not printed_from_stream:
                print("AI:", assistant_text)
            conversation.append({"role": "assistant", "content": assistant_text})

        except Exception as exc:
            print(f"Error from X.AI API: {exc}")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="X.AI Grok REPL")
    p.add_argument("--model", default="grok-4-fast-reasoning")
    p.add_argument("--temperature", type=float, default=0.6)
    p.add_argument("--stream", action="store_true", help="Start with streaming enabled")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run_repl(model=args.model, temperature=args.temperature, stream_default=args.stream)
