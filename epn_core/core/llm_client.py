"""LLM client for EPN using Groq API."""

from dataclasses import dataclass
from typing import Optional
import os

# Defer import of Groq to runtime to make the module import-safe when
# the groq package isn't installed (tests and dry-runs can monkeypatch).
Groq = None
import json
import logging


@dataclass
class LLMConfig:
    """Configuration for LLM model."""
    model: str
    temperature: float
    reasoning_effort: str  # 'low', 'medium', 'high'
    max_tokens: int


class LLMClient:
    """Client for interacting with LLM APIs."""

    def __init__(self, config: LLMConfig):
        """Initialize the LLM client.

        Args:
            config: LLM configuration
        """
        self.config = config
        # Initialize Groq client lazily if package is present
        try:
            if Groq is None:
                from groq import Groq as _Groq
            else:
                _Groq = Groq
            self.client = _Groq(api_key=os.getenv('GROQ_API_KEY'))
        except Exception:
            # If Groq cannot be imported/initialized (e.g., not installed),
            # set client to None so callers/tests can inject a fake client.
            self.client = None

    async def generate(self, prompt: str) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM response
        """
        # If prompt appears to be raw template followed by JSON metadata, parse it
        rendered_prompt = prompt
        try:
            # If prompt ends with JSON metadata (the node emitted raw_template + metadata),
            # parse it and render a clean prompt string without any JSON or braces.
            split_index = prompt.rfind('\n{')
            if split_index != -1:
                raw_template = prompt[:split_index].rstrip()
                metadata_json = prompt[split_index+1:]
                metadata = json.loads(metadata_json)

                logger = logging.getLogger('LLMClient')
                logger.info("Raw template detected; rendering with metadata")

                # Substitute placeholders using raw_inputs
                raw_inputs = metadata.get('raw_inputs', {}) if isinstance(metadata, dict) else {}
                rendered = raw_template
                if isinstance(raw_inputs, dict):
                    for k, v in raw_inputs.items():
                        # replace occurrences of {key} with its value
                        rendered = rendered.replace(f"{{{k}}}", str(v))

                # Format instructions as hyphenated bullet lines (not JSON)
                instructions = metadata.get('instructions') if isinstance(metadata, dict) else None
                instr_text = ''
                if instructions:
                    if isinstance(instructions, list):
                        # Prepend each instruction on its own line with a hyphen
                        bullet_lines = [f"- {line}" for line in instructions]
                        instr_text = "\n\n" + "\n".join(bullet_lines) + "\n"
                    else:
                        instr_text = "\n\n- " + str(instructions) + "\n"

                # Ensure no leftover braces remain in the rendered prompt
                rendered_prompt = rendered.replace("{", "").replace("}", "") + instr_text
                logger.info(f"Rendered prompt ready (no JSON):\n{rendered_prompt}")
                # Expose the rendered prompt for callers/tests
                self.last_rendered_prompt = rendered_prompt
        except Exception:
            # If any parsing/substitution fails, fall back to original prompt
            rendered_prompt = prompt
        # Map reasoning_effort to appropriate parameters
        if self.config.reasoning_effort == 'low':
            temperature = min(self.config.temperature, 0.3)
        elif self.config.reasoning_effort == 'medium':
            temperature = self.config.temperature
        else:  # high
            temperature = max(self.config.temperature, 0.8)

        # Prepare request parameters
        request_params = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": rendered_prompt}],
            "temperature": temperature,
            "max_tokens": self.config.max_tokens,
        }

        # Add reasoning_format for Qwen models to avoid <think> tags
        if self.config.model.startswith("qwen/"):
            request_params["reasoning_format"] = "hidden"

        # Ensure a client is available (tests may inject a fake client)
        if not hasattr(self, 'client') or self.client is None:
            raise RuntimeError('LLM client is not initialized. Install groq or inject a mock client for testing.')

        response = self.client.chat.completions.create(**request_params)

        return response.choices[0].message.content