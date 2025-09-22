import os
import httpx
from openai import OpenAI

key = os.getenv("XAI_API_KEY")
if not key:
    raise RuntimeError("XAI_API_KEY is not set. Export it before running: export XAI_API_KEY=your_key")
client = OpenAI(
    api_key=key,
    base_url="https://api.x.ai/v1",
    timeout=httpx.Timeout(3600.0), # Override default timeout with longer timeout for reasoning models
)

import pprint

response = client.responses.create(
    model="grok-4-fast-reasoning",
    input=[
        {"role": "system", "content": "You are Grok, a chatbot inspired by the Hitchhiker's Guide to the Galaxy."},
        {"role": "user", "content": "What is a mental model?"},
    ],
)

# Try to convert the response into a plain dict for readable printing.
def response_to_plain(obj):
    # openai SDK Response objects often have a to_dict() helper
    if hasattr(obj, "to_dict"):
        return obj.to_dict()
    # some SDK types expose .__dict__
    if hasattr(obj, "__dict__"):
        return {k: response_to_plain(v) for k, v in obj.__dict__.items()}
    # fallback for lists/tuples/dicts
    if isinstance(obj, dict):
        return {k: response_to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [response_to_plain(v) for v in obj]
    return obj

plain = response_to_plain(response)
pp = pprint.PrettyPrinter(depth=4, compact=False)
pp.pprint(plain)

# Print top-level id separately for convenience
try:
    print('\nresponse.id ->', plain.get('id') if isinstance(plain, dict) else getattr(response, 'id', None))
except Exception:
    print('\nresponse.id ->', getattr(response, 'id', None))