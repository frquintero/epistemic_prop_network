"""Example EPN node wrapper showing how to store `resp.id` and create a chained follow-up

This is a minimal, standalone example that demonstrates the pattern EPN nodes
should follow when integrating with the xAI Responses API. It is not a full
EPN node implementation, just a small helper + example usage to guide
integration.

Usage:
    export XAI_API_KEY=...
    python scripts/epn_xai_node_example.py

"""

import os
import httpx
from openai import OpenAI


def create_client():
    key = os.getenv("XAI_API_KEY")
    if not key:
        raise RuntimeError("XAI_API_KEY not set")
    return OpenAI(api_key=key, base_url="https://api.x.ai/v1", timeout=httpx.Timeout(60.0))


class EPNNodeOutput(dict):
    """Simple container representing what an EPN node might output.

    We include a reserved key `llm_response_id` to hold the xAI response id.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


def format_response_text(response):
    """Extract readable text from a Response object.

    Tries to find message-type blocks with textual content, otherwise falls
    back to any plain 'text' or 'summary' fields in the response output.
    """
    # Try SDK helper
    plain = None
    if hasattr(response, 'to_dict'):
        try:
            plain = response.to_dict()
        except Exception:
            plain = None

    if plain is None and hasattr(response, '__dict__'):
        plain = {k: v for k, v in response.__dict__.items()}

    if not plain:
        return '<no content>'

    out = plain.get('output') or []
    # find message blocks first
    texts = []
    for block in out:
        btype = block.get('type')
        if btype == 'message' and 'content' in block:
            content = block.get('content')
            # content usually a list; try to extract common text fields
            if isinstance(content, list) and content:
                first = content[0]
                if isinstance(first, dict):
                    # common keys: 'text', 'body', 'plain_text'
                    for k in ('text', 'plain_text', 'body'):
                        if k in first:
                            texts.append(first[k])
                            break
                    else:
                        texts.append(str(first))
                else:
                    texts.append(str(first))
        elif btype == 'reasoning' and block.get('summary'):
            # include reasoning summaries if present
            try:
                if isinstance(block.get('summary'), list):
                    texts.extend([str(s) for s in block.get('summary')])
                else:
                    texts.append(str(block.get('summary')))
            except Exception:
                pass

    if texts:
        return '\n\n'.join(texts)

    # fallback: usage of text field
    text_field = plain.get('text')
    if text_field and isinstance(text_field, dict):
        fmt = text_field.get('format', {})
        return f"[text format: {fmt}]"

    return '<no content>'


def run_seed_and_chain():
    client = create_client()
    # We'll run two upstream LLM calls (A and B), then a third call (C)
    # which uses A as previous_response_id and includes B's content in the input.

    node_out = EPNNodeOutput()
    node_out["steps"] = []

    # Upstream call A
    input_a = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "List three practical uses of mental models."},
    ]
    resp_a = client.responses.create(model="grok-4-fast-reasoning", input=input_a)
    text_a = format_response_text(resp_a)
    print("Call A id:", resp_a.id)
    print('\nCall A response:')
    print(text_a)
    node_out["steps"].append({"id": resp_a.id, "input": input_a, "response": text_a})

    # Upstream call B
    input_b = [
        {"role": "system", "content": "You are a concise assistant."},
        {"role": "user", "content": "Give a one-sentence actionable tip for using mental models."},
    ]
    resp_b = client.responses.create(model="grok-4-fast-reasoning", input=input_b)
    text_b = format_response_text(resp_b)
    print("\nCall B id:", resp_b.id)
    print('\nCall B response:')
    print(text_b)
    node_out["steps"].append({"id": resp_b.id, "input": input_b, "response": text_b})
    # Collect previous ids into a list (for testing whether API accepts an array)
    prev_ids = [resp_a.id, resp_b.id]
    print("\nCollected previous ids:", prev_ids)

    # Third call C: prefer passing multiple previous ids if supported by SDK
    followup_input = [
        {"role": "user", "content": (
            "Using the previous answers (ids={ids}), and the short tip below, produce a single concise" \
            " paragraph that synthesizes both into an example use-case.\n\nTip:\n{tip}".format(ids=prev_ids, tip=text_b)
        )},
    ]

    # Try passing the full list to `previous_response_id`; if the API/SDK rejects it,
    # fall back to passing a single previous_response_id and include the other
    # responses' content in the input payload.
    try:
        resp_c = client.responses.create(
            model="grok-4-fast-reasoning",
            previous_response_id=prev_ids,
            input=followup_input,
        )
    except Exception as e:
        print("\nSDK/API did not accept a list for previous_response_id (falling back):", type(e).__name__, e)
        # fallback: use the first id as previous_response_id and embed the other response text
        fallback_input = [
            {"role": "user", "content": (
                "Using the previous answer (id={aid}) and this other answer:\n{other}\n\nNow synthesize both into one concise example.".format(aid=resp_a.id, other=text_b)
            )},
        ]
        resp_c = client.responses.create(
            model="grok-4-fast-reasoning",
            previous_response_id=resp_a.id,
            input=fallback_input,
        )
    text_c = format_response_text(resp_c)
    print("\nCall C id:", resp_c.id)
    print('\nCall C response (synthesis):')
    print(text_c)
    node_out["steps"].append({"id": resp_c.id, "input": followup_input, "response": text_c})

    # for convenience add top-level ids
    node_out["first_id"] = resp_a.id
    node_out["second_id"] = resp_b.id
    node_out["third_id"] = resp_c.id

    return node_out


if __name__ == "__main__":
    out = run_seed_and_chain()
    print("EPN node output:")
    for k, v in out.items():
        print(" - {}: {}".format(k, v))
