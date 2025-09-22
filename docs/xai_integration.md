# xAI REST API Integration Guide

This document describes how to integrate the Epistemological Propagation Network (EPN) with xAI's REST Chat Completions API. It covers authentication, endpoints used, request/response examples, and a simple Python test script to verify connectivity.

## Requirements

- Python 3.10+

- `requests` package (for the example test script)

- An xAI API key with access to the REST Chat Completions API

Set the API key and optional base URL as environment variables:

```bash
export XAI_API_KEY="xai_..."
export XAI_BASE_URL="https://api.x.ai"  # optional if using default
```

### Quick notes from xAI docs

- **Account & keys:** Create an xAI account and generate an API key via the xAI Console. Keep the key secret and monitor usage in the console.

- **Models & capabilities:** Many `grok-*` models support structured outputs and function calling; check the `Models` page for availability. `grok-4-fast-reasoning` (or similar) is suitable for reasoning tasks.

- **Rate limits & usage:** API responses include a `usage` object with token counts; respect rate limits and monitor consumption to avoid errors.

### Endpoints Used

- Create chat completion (response resource):

  - POST `{base_url}/v1/responses`

  - Creates a new response resource (chat completion). Use the returned `id` to retrieve or delete later.

- Retrieve response:

  - GET `{base_url}/v1/responses/{response_id}`

  - Returns the response object and generated content.

- Delete response:

  - DELETE `{base_url}/v1/responses/{response_id}`

  - Deletes the created response resource.

Refer to xAI docs: [API Reference](https://docs.x.ai/docs/api-reference#rest-api-reference)

### Request / Response Patterns

Create (POST) payload example (JSON):

```json
{
  "model": "tiiuae/falcon-1.0",
  "input": "Translate the following English text to French: 'Hello world'"
}
```

Typical create response contains keys like `id`, `object`, `created`, and `output` (or `choices`) depending on model. The `id` is necessary to GET/DELETE the response.

Retrieve (GET) returns the generated content and full response object.

Delete (DELETE) removes the created response resource.

### Python smoke-test script

There is a ready-to-run smoke-test script located at `scripts/xai_smoke_test.py`.
It exercises three capabilities useful for EPN integration:

- **Basic chat completion:** posts a chat-style `messages` payload and prints the returned output.

- **Structured outputs:** asks the model to emit a JSON object and attempts to parse it.

- **Function-calling style:** requests a function-like JSON object to validate model behavior for tool-calling workflows.

The script reads `XAI_API_KEY` (or falls back to `GROQ_API_KEY` for convenience) and optional
`XAI_BASE_URL`. It prints concise diagnostics and exits cleanly if credentials are missing.

Run the script (real API calls require a valid key):

```bash
export XAI_API_KEY="xai_..."
python scripts/xai_smoke_test.py
```

### Security

- Do not commit `XAI_API_KEY` to the repo. Use environment variables or secret managers.

- Limit permissions for the API key where possible.

### Notes: Function calling and structured outputs

- xAI supports structured outputs and function-calling styles. When designing an `LLMClient` wrapper:

  - Allow the EPN node `llm_config` to indicate whether responses should be treated as structured JSON or as plain text.

  - Provide safe parsing helpers that attempt to extract JSON substrings from free-form text and validate against a schema.

  - For function calling, implement a deterministic mapping from the model's returned structure (e.g., an object with `name` and `arguments`) to a local call intent that EPN can handle.

### Recommended next steps

- Review `scripts/xai_smoke_test.py` and run it locally with a valid `XAI_API_KEY` to confirm connectivity.

- Implement `epn_core/core/llm_clients/xai_client.py` following the patterns used by other client implementations in `epn_core/core/llm_clients/`.

- Add unit tests that mock the xAI endpoints (the smoke-test script is useful for manual validation but should not be used in CI without mocking).

## Chained Prompts and `response.id`

xAI returns a persistent `response` resource for each creation request; the top-level `id` field is the unique identifier for that response. You can use this `id` to retrieve, delete, or continue a conversation. In EPN we can use the `response.id` to implement chained-prompt flows where a later request continues or references an earlier response.

Why use `response.id`?

- Referential continuity: referencing a previous response lets the API and the model maintain or recover context without re-sending the entire message history.

- Reproducibility: you can re-fetch the original full response object for auditing, debugging, or replay.

- Chained control flows: use `previous_response_id` to implement multi-step pipelines where the model's intermediate outputs are inputs for downstream steps.

How to chain requests (Python example)

```python
from openai import OpenAI
import httpx, os

client = OpenAI(api_key=os.getenv('XAI_API_KEY'), base_url='https://api.x.ai/v1', timeout=httpx.Timeout(3600.0))

# 1) Create first response (seed step)
resp1 = client.responses.create(
  model='grok-4-fast-reasoning',
  input=[
    {'role': 'system', 'content': 'You are a helpful assistant.'},
    {'role': 'user', 'content': 'Summarize the key ideas of cognitive models in 40 words.'},
  ],
)

print('first id', resp1.id)

# 2) Use the id to continue/clarify (chained prompt)
resp2 = client.responses.create(
  model='grok-4-fast-reasoning',
  previous_response_id=resp1.id,
  input=[
    {'role': 'user', 'content': 'Now expand the second sentence into a short example.'},
  ],
)

print('chained id', resp2.id)
```

Notes and cautions for EPN integration

- Not every SDK version or endpoint supports `previous_response_id` on every method — validate the client version and preferred parameter name in the runtime you ship.

- SDK compatibility note: confirm the exact parameter name and behaviour for your SDK release (for example some SDKs expose `previous_response_id` directly on `responses.create`, others may offer helper methods or different param names). Pin and test the client version you ship with EPN.

- Be explicit about what you expect to be continued: include a short follow-up `input` when creating the chained call; the model will use the prior response as context plus the follow-up prompt.

- Chaining increases statefulness — ensure EPN nodes that create chained flows document and control retention (the response `store` flag and deletion API are useful).

- Consider privacy and data governance: chained responses may include user data from earlier steps. Use metadata and `store=False` where appropriate.

Mapping `response.id` into EPN pipeline nodes

- When a pipeline node invokes an LLM and obtains `resp.id`, store that id in the node output under a reserved key (e.g. `llm_response_id`).

- Downstream nodes that need to continue the conversation should accept `previous_response_id` in their `llm_config` and pass it to the LLM client. This keeps message payloads small and reduces duplication.

- Add unit tests that assert chained flows correctly pass context and that deletion or re-fetching behaves as expected.

Retrieval and replay

- Use GET `/v1/responses/{id}` to retrieve the full response object when you need the original content, usage metadata, or reasoning blocks. This is useful for auditing and building deterministic replay tooling inside EPN.

Example: small helper to continue a response by id

```python
def continue_by_id(client, prev_id, followup_text):
  return client.responses.create(
    model='grok-4-fast-reasoning',
    previous_response_id=prev_id,
    input=[{'role': 'user', 'content': followup_text}],
  )
```

Summary

- Use `response.id` to build chained prompt flows that are smaller, auditable, and easier to reproduce. Add clear retention and privacy controls when storing these ids inside EPN state, and include unit tests to ensure the chained behaviour remains deterministic across SDK versions.
