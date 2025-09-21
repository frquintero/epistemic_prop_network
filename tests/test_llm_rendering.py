import asyncio
import json

import pytest
import os

from epn_core.core.llm_client import LLMClient, LLMConfig


class FakeChoice:
    def __init__(self, content):
        class Message:
            def __init__(self, content):
                self.content = content

        self.message = Message(content)


class FakeResponse:
    def __init__(self, text):
        self.choices = [FakeChoice(text)]


class FakeChat:
    class Completions:
        @staticmethod
        def create(**kwargs):
            messages = kwargs.get('messages') or []
            content = messages[0]['content'] if messages else ''
            return FakeResponse(content)

    completions = Completions()


class FakeClient:
    def __init__(self):
        self.chat = FakeChat()


@pytest.mark.asyncio
async def test_llm_client_renders_clean_prompt():
    # For live runs, prefer the model defined in repo `layer.json` (first node),
    # else allow override with `LIVE_MODEL`. Default to 'test-model' for unit tests.
    model_name = 'test-model'
    if os.getenv('LIVE_LLM'):
        try:
            from pathlib import Path
            import json

            root = Path(__file__).resolve().parents[1]
            layer_path = root / 'layer.json'
            if layer_path.exists():
                lj = json.loads(layer_path.read_text(encoding='utf-8'))
                # pick the first node's model if present
                first_model = None
                if 'layers' in lj and lj['layers']:
                    for layer in lj['layers']:
                        nodes = layer.get('nodes') or []
                        if nodes:
                            first_model = nodes[0].get('llm_config', {}).get('model')
                            if first_model:
                                break
                if first_model:
                    model_name = first_model
                else:
                    model_name = os.getenv('LIVE_MODEL', model_name)
            else:
                model_name = os.getenv('LIVE_MODEL', model_name)
        except Exception:
            model_name = os.getenv('LIVE_MODEL', model_name)
    cfg = LLMConfig(model=model_name, temperature=0.2, reasoning_effort='low', max_tokens=200)
    client = LLMClient(cfg)

    live_mode = bool(os.getenv('LIVE_LLM'))
    if not live_mode:
        # default unit test behavior: inject fake client that echoes the prompt
        client.client = FakeClient()
    else:
        # In live mode, ensure the client was initialized (groq installed and GROQ_API_KEY present)
        if not hasattr(client, 'client') or client.client is None:
            pytest.skip('LIVE_LLM requested but Groq client or GROQ_API_KEY is unavailable')

    raw_template = "You are a reformulator. Reformulate: {query}\n"
    test_query = os.getenv('TEST_QUERY') or "Are you really listening to me?"
    meta = {
        'expected_output': 'reformulated_question',
        'raw_inputs': {'query': test_query},
        'instructions': [
            "Neutralize biases and eliminate assumptions",
            "Prime for emplotment (e.g., 'temporal evolution of...')",
            "Include narrative potential and multi-aspect integration hints",
            "Output ONLY the reformulated question",
            "End with '?'",
        ],
    }

    prompt = raw_template + json.dumps(meta)

    response = await client.generate(prompt)

    rendered = getattr(client, 'last_rendered_prompt', None)
    assert rendered is not None, "last_rendered_prompt should be set"
    # No braces in rendered prompt
    assert '{' not in rendered and '}' not in rendered

    # Instructions should appear as hyphenated lines
    for instr in meta['instructions']:
        assert f"- {instr}" in rendered

    if live_mode:
        # Live LLMs won't echo the prompt; ensure a non-empty string response.
        # Some live endpoints may occasionally return an empty string — retry a few times.
        if isinstance(response, str) and len(response) == 0:
            import asyncio

            retries = 3
            for i in range(retries):
                await asyncio.sleep(0.5)
                response = await client.generate(prompt)
                if isinstance(response, str) and len(response) > 0:
                    break

        assert isinstance(response, str) and len(response) > 0, "Live LLM returned empty response after retries"
    else:
        # The fake response should echo the rendered prompt
        assert response == rendered
