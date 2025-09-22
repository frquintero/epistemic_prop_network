#!/usr/bin/env python3
"""Batch runner for X.AI Grok: send each line from a file as a user turn.

This avoids using the interactive REPL for automated testing and prints
clean assistant text for each prompt.
"""

from __future__ import annotations

import argparse
import os
import sys
from typing import Any, List, Dict

try:
    from openai import OpenAI
    import httpx
except Exception:
    print("Missing dependency: install openai and httpx")
    sys.exit(1)


def get_api_key() -> str:
    key = os.getenv("XAI_API_KEY")
    if not key:
        raise RuntimeError("XAI_API_KEY is not set. Export it before running.")
    return key


def create_client() -> OpenAI:
    key = get_api_key()
    return OpenAI(api_key=key, base_url="https://api.x.ai/v1", timeout=httpx.Timeout(60.0))


def extract_text_from_output(output: Any) -> str:
    # The X.AI responses often contain multiple output items. Return the
    # first assistant-like message by default (to avoid multi-message
    # replies). Use `extract_messages_from_output` to enumerate all
    # message-like strings if callers need them.
    msgs = extract_messages_from_output(output)
    return msgs[0].strip() if msgs else ""


def extract_messages_from_output(output: Any) -> List[str]:
    """Return all assistant-like message strings found in `output` in
    the order they appear. This scans lists/dicts/SDK objects and skips
    'reasoning' items and other metadata."""
    try:
        if hasattr(output, "output"):
            output = getattr(output, "output")
    except Exception:
        pass

    def _find_messages(val: Any) -> List[str]:
        msgs: List[str] = []
        if val is None:
            return msgs
        if isinstance(val, str):
            return [val]
        if isinstance(val, (list, tuple)):
            for it in val:
                msgs.extend(_find_messages(it))
            return msgs
        if isinstance(val, dict):
            # Skip explicit reasoning items
            if val.get("type") == "reasoning":
                return []
            # message pattern
            if val.get("type") == "message" and "content" in val:
                msgs.extend(_find_messages(val["content"]))
                return msgs
            if "content" in val:
                msgs.extend(_find_messages(val["content"]))
            if "text" in val and isinstance(val["text"], str):
                msgs.append(val["text"])
            for v in val.values():
                msgs.extend(_find_messages(v))
            return msgs

        try:
            if hasattr(val, "content"):
                return _find_messages(getattr(val, "content"))
        except Exception:
            pass
        try:
            if hasattr(val, "text"):
                t = getattr(val, "text")
                if isinstance(t, str):
                    return [t]
        except Exception:
            pass
        return msgs

    return [m.strip() for m in _find_messages(output) if m and m.strip()]


def extract_text_from_event(event: Any) -> str:
    # Prefer explicit delta fragments when present (token-level updates).
    try:
        delta = getattr(event, "delta", None)
    except Exception:
        delta = None

    def _extract_from_struct(val: Any) -> str:
        # Handle the common structured shapes returned by the SDK:
        # - string tokens
        # - dicts with 'content' lists containing items with 'text'
        # - lists of such items
        if val is None:
            return ""
        if isinstance(val, str):
            return val
        if isinstance(val, (list, tuple)):
            pieces: List[str] = []
            for it in val:
                pieces.append(_extract_from_struct(it))
            return "".join(pieces)
        if isinstance(val, dict):
            # common pattern: {'content': [{'type': 'message', 'text': '...'}]}
            if "content" in val:
                return _extract_from_struct(val["content"])
            # fallback to scanning values
            pieces: List[str] = []
            for v in val.values():
                pieces.append(_extract_from_struct(v))
            return "".join(pieces)
        # SDK objects with attributes
        try:
            txt = getattr(val, "text", None)
            if isinstance(txt, str):
                return txt
        except Exception:
            pass
        try:
            cont = getattr(val, "content", None)
            if cont is not None:
                return _extract_from_struct(cont)
        except Exception:
            pass
        return ""

    out = _extract_from_struct(delta)
    if out:
        return out

    # Fallbacks: text, content, snapshot, or part
    for attr in ("text", "content", "snapshot"):
        try:
            val = getattr(event, attr, None)
        except Exception:
            val = None
        if val:
            return _extract_from_struct(val)

    try:
        if hasattr(event, "part"):
            return _extract_from_struct(getattr(event, "part"))
    except Exception:
        pass

    return ""


def run(batch_file: str, model: str, temperature: float, stream: bool) -> None:
    debug = os.getenv("DEBUG", "0") == "1"
    client = create_client()
    system_prompt = "You are Grok, a helpful assistant inspired by the Hitchhiker's Guide to the Galaxy."
    conversation: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]

    with open(batch_file, "r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            prompt = line.strip()
            if not prompt:
                continue
            print(f"\n=== Q{i}: {prompt}")
            conversation.append({"role": "user", "content": prompt})

            # Make exactly one API call per prompt and use the first
            # assistant-like message from the response. No fallback or
            # secondary requests are performed (this prevents duplicate
            # replies and extra token usage).
            try:
                resp = client.responses.create(model=model, input=conversation, temperature=temperature)
            except Exception as exc:
                print(f"Request error: {exc}")
                if debug:
                    import traceback

                    traceback.print_exc()
                assistant_text = ""
            else:
                assistant_messages = extract_messages_from_output(getattr(resp, "output", resp))
                assistant_text = assistant_messages[0] if assistant_messages else ""
                print(assistant_text)

            conversation.append({"role": "assistant", "content": assistant_text})


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run X.AI Grok batch file")
    p.add_argument("batch_file")
    p.add_argument("--model", default="grok-4-fast-reasoning")
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--stream", action="store_true")
    p.add_argument("--debug", action="store_true", help="Print raw SDK responses and streaming events")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.debug:
        os.environ["DEBUG"] = "1"
    run(args.batch_file, model=args.model, temperature=args.temperature, stream=args.stream)
