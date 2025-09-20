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

Refer to xAI docs: https://docs.x.ai/docs/api-reference#rest-api-reference

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

See `tools/xai_test.py` for a ready-to-run script. The script:

- Reads `XAI_API_KEY` and optional `XAI_BASE_URL` from environment.
- Creates a response with a simple prompt.
- Polls or retrieves the response result.
- Deletes the response resource.

Run the script (it exits quickly if `XAI_API_KEY` is not provided):

```bash
python tools/xai_test.py
```

### EPN Integration Notes

- Add a new `LLMClient` implementation that wraps xAI endpoints and follows the existing `LLMClient` interface used by EPN (`generate`, `create_chat`, etc.).
- Ensure request timeouts and retries are applied.
- Map xAI response structure to EPN expected string outputs (e.g., join `output` array items or use the primary choice text).
- Sanitize and validate response content before passing to downstream nodes.

### Security

- Do not commit `XAI_API_KEY` to the repo. Use environment variables or secret managers.
- Limit permissions for the API key where possible.

### Next Steps

- Implement `epn_core/core/llm_clients/xai_client.py` wrapping the endpoints.
- Add configuration options in `layer.json`/`template.json` LLM configs to allow selecting the `xai` client and model names.
- Add tests and CI checks that mock xAI responses.
