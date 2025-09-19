"""LLM client for EPN using Groq API."""

from dataclasses import dataclass
from typing import Optional
import os

from groq import Groq


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
        self.client = Groq(api_key=os.getenv('GROQ_API_KEY'))

    async def generate(self, prompt: str) -> str:
        """Generate a response from the LLM.

        Args:
            prompt: The prompt to send to the LLM

        Returns:
            The LLM response
        """
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
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": self.config.max_tokens,
        }

        # Add reasoning_format for Qwen models to avoid <think> tags
        if self.config.model.startswith("qwen/"):
            request_params["reasoning_format"] = "hidden"

        response = self.client.chat.completions.create(**request_params)

        return response.choices[0].message.content