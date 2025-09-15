"""Base LLM client for Groq GPT-OSS-120B integration."""

import asyncio
import json
import os
from typing import Any, Dict, List, Optional, Union
from contextlib import asynccontextmanager

import httpx
import structlog
from groq import AsyncGroq, Groq
from pydantic import BaseModel, ValidationError

from .schemas import NetworkRequest, NetworkResponse


logger = structlog.get_logger(__name__)


class LLMConfig(BaseModel):
    """Configuration for LLM client."""

    api_key: str = ""
    model: str = "openai/gpt-oss-120b"
    temperature: float = 0.9
    max_tokens: int = 8192
    top_p: float = 1.0
    reasoning_effort: str = "medium"
    tools: List[Dict[str, Any]] = []
    timeout: float = 120.0
    max_retries: int = 3
    retry_delay: float = 1.0

    def __init__(self, **data):
        super().__init__(**data)
        if not self.api_key:
            self.api_key = os.getenv("GROQ_API_KEY", "")

    @classmethod
    def from_network_config(cls, network_config) -> "LLMConfig":
        """Create LLMConfig from NetworkConfig for consistency."""
        return cls(
            api_key=network_config.groq_api_key,
            model=network_config.groq_model,
            temperature=network_config.temperature,
            max_tokens=network_config.max_tokens_per_request,
            top_p=network_config.top_p,
            reasoning_effort=network_config.reasoning_effort,
            tools=network_config.tools,
            timeout=network_config.request_timeout,
            max_retries=network_config.max_retries,
        )


class LLMClient:
    """Base LLM client for Groq integration with structured outputs support."""

    def __init__(self, config: Optional[LLMConfig] = None):
        """Initialize the LLM client.

        Args:
            config: LLM configuration. If None, uses default config.
        """
        self.config = config or LLMConfig()
        self._client = None
        self._async_client = None

        if not self.config.api_key:
            raise ValueError("GROQ_API_KEY environment variable must be set")

    @property
    def client(self) -> Groq:
        """Get synchronous Groq client."""
        if self._client is None:
            self._client = Groq(api_key=self.config.api_key)
        return self._client

    @property
    def async_client(self) -> AsyncGroq:
        """Get asynchronous Groq client."""
        if self._async_client is None:
            self._async_client = AsyncGroq(api_key=self.config.api_key)
        return self._async_client

    async def generate_text(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Generate text using the LLM.

        Args:
            prompt: The user prompt
            system_message: Optional system message
            response_format: Optional response format for structured outputs
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "reasoning_effort": self.config.reasoning_effort,
            "timeout": self.config.timeout,
            **kwargs
        }

        # Only add tools if they are provided
        if self.config.tools:
            params["tools"] = self.config.tools

        if response_format:
            params["response_format"] = response_format

        for attempt in range(self.config.max_retries):
            try:
                logger.info("Making LLM request", attempt=attempt + 1)
                response = await self.async_client.chat.completions.create(**params)
                return response.choices[0].message.content or ""

            except Exception as e:
                logger.warning("LLM request failed", attempt=attempt + 1, error=str(e))
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    raise

        return ""

    def generate_text_sync(
        self,
        prompt: str,
        system_message: Optional[str] = None,
        response_format: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> str:
        """Generate text synchronously.

        Args:
            prompt: The user prompt
            system_message: Optional system message
            response_format: Optional response format for structured outputs
            **kwargs: Additional parameters

        Returns:
            Generated text response
        """
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})

        params = {
            "model": self.config.model,
            "messages": messages,
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens,
            "top_p": self.config.top_p,
            "reasoning_effort": self.config.reasoning_effort,
            "timeout": self.config.timeout,
            **kwargs
        }

        # Only add tools if they are provided
        if self.config.tools:
            params["tools"] = self.config.tools

        if response_format:
            params["response_format"] = response_format

        for attempt in range(self.config.max_retries):
            try:
                logger.info("Making synchronous LLM request", attempt=attempt + 1)
                response = self.client.chat.completions.create(**params)
                return response.choices[0].message.content or ""

            except Exception as e:
                logger.warning("LLM request failed", attempt=attempt + 1, error=str(e))
                if attempt < self.config.max_retries - 1:
                    import time
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                else:
                    raise

        return ""

    async def generate_structured(
        self,
        prompt: str,
        schema: Dict[str, Any],
        system_message: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate structured output using JSON Schema mode.

        Args:
            prompt: The user prompt
            schema: JSON Schema for structured output
            system_message: Optional system message
            **kwargs: Additional parameters

        Returns:
            Parsed JSON response matching the schema
        """
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": schema.get("name", "structured_response"),
                "schema": schema
            }
        }

        response_text = await self.generate_text(
            prompt=prompt,
            system_message=system_message,
            response_format=response_format,
            **kwargs
        )

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error("Failed to parse structured response", error=str(e))
            raise ValueError(f"Invalid JSON response: {response_text}")

    def health_check(self) -> bool:
        """Perform a basic health check of the LLM service.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            # Simple test request
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return False

    async def health_check_async(self) -> bool:
        """Perform an asynchronous health check.

        Returns:
            True if service is healthy, False otherwise
        """
        try:
            response = await self.async_client.chat.completions.create(
                model=self.config.model,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
                timeout=10
            )
            return bool(response.choices[0].message.content)
        except Exception as e:
            logger.error("Async health check failed", error=str(e))
            return False


# Global client instance
_default_client: Optional[LLMClient] = None


def get_llm_client(config: Optional[LLMConfig] = None) -> LLMClient:
    """Get the global LLM client instance.

    Args:
        config: Optional configuration override

    Returns:
        LLMClient instance
    """
    global _default_client
    if _default_client is None or config is not None:
        _default_client = LLMClient(config)
    return _default_client


def set_llm_config(config: LLMConfig) -> None:
    """Set the global LLM configuration.

    Args:
        config: New configuration
    """
    global _default_client
    _default_client = LLMClient(config)