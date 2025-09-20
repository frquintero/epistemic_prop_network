import asyncio
import json

import pytest

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
    cfg = LLMConfig(model='test-model', temperature=0.2, reasoning_effort='low', max_tokens=200)
    client = LLMClient(cfg)
    client.client = FakeClient()

    raw_template = "You are a reformulator. Reformulate: {query}\n"
    meta = {
        'expected_output': 'reformulated_question',
        'raw_inputs': {'query': "Are you really listening to me?"},
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

    # The fake response should echo the rendered prompt
    assert response == rendered
