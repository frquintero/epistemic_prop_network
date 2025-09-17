"""Configuration management for the Epistemological Propagation Network."""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, field_validator


class NetworkConfig(BaseModel):
    """Main configuration for the Epistemological Propagation Network."""

    # API Configuration
    groq_api_key: str = Field(..., description="Groq API key")
    groq_model: str = Field(
        default="openai/gpt-oss-120b",
        description="Groq model to use"
    )

    # Performance Settings
    max_concurrent_requests: int = Field(
        default=3,
        description="Maximum concurrent LLM requests",
        ge=1,
        le=10
    )
    request_timeout: float = Field(
        default=120.0,
        description="Request timeout in seconds",
        ge=10.0,
        le=300.0
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed requests",
        ge=0,
        le=5
    )

    # Processing Settings
    temperature: float = Field(
        default=0.9,
        description="LLM temperature for generation (0.9 for creative responses)",
        ge=0.0,
        le=1.0
    )
    max_tokens_per_request: int = Field(
        default=8192,
        description="Maximum tokens per LLM request (matches playground default)",
        ge=1000,
        le=65536
    )
    top_p: float = Field(
        default=1.0,
        description="Top-p sampling parameter",
        ge=0.0,
        le=1.0
    )
    reasoning_effort: str = Field(
        default="medium",
        description="Reasoning effort level (low, medium, high)",
        pattern="^(low|medium|high)$"
    )
    tools: list = Field(
        default_factory=list,
        description="Tools to enable for the LLM (empty for Phase 1)"
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level",
        pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$"
    )
    enable_structured_logging: bool = Field(
        default=True,
        description="Enable structured JSON logging"
    )

    # Development Settings
    debug_mode: bool = Field(
        default=False,
        description="Enable debug mode with additional logging"
    )
    mock_responses: bool = Field(
        default=False,
        description="Use mock responses for testing (development only)"
    )

    @field_validator("groq_api_key", mode="before")
    @classmethod
    def validate_api_key(cls, v):
        """Validate and get API key from environment if not provided."""
        if not v:
            v = os.getenv("GROQ_API_KEY", "")
        if not v:
            raise ValueError("GROQ_API_KEY must be provided either as parameter or environment variable")
        return v

    @field_validator("max_concurrent_requests", mode="before")
    @classmethod
    def validate_max_concurrent_requests(cls, v: int) -> int:
        """Ensure max_concurrent_requests stays within documented bounds."""
        value = int(v)
        if not 1 <= value <= 10:
            raise ValueError("max_concurrent_requests must be between 1 and 10")
        return value

    @field_validator("temperature", mode="before")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Restrict temperature to supported range for tests and docs."""
        value = float(v)
        if not 0.0 <= value <= 1.0:
            raise ValueError("temperature must be between 0.0 and 1.0")
        return value

    @classmethod
    def from_env(cls) -> "NetworkConfig":
        """Create configuration from environment variables."""
        return cls(
            groq_api_key=os.getenv("GROQ_API_KEY", ""),
            groq_model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
            max_concurrent_requests=int(os.getenv("MAX_CONCURRENT_REQUESTS", "3")),
            request_timeout=float(os.getenv("REQUEST_TIMEOUT", "120.0")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            temperature=float(os.getenv("TEMPERATURE", "0.9")),
            max_tokens_per_request=int(os.getenv("MAX_TOKENS_PER_REQUEST", "8192")),
            top_p=float(os.getenv("TOP_P", "1.0")),
            reasoning_effort=os.getenv("REASONING_EFFORT", "medium"),
            tools=json.loads(os.getenv("TOOLS", "[]")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            enable_structured_logging=os.getenv("STRUCTURED_LOGGING", "false").lower() == "true",
            debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
            mock_responses=os.getenv("MOCK_RESPONSES", "false").lower() == "true",
        )

    @classmethod
    def from_file(cls, config_path: str) -> "NetworkConfig":
        """Load configuration from a JSON file."""
        import json

        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_file, 'r') as f:
            config_data = json.load(f)

        return cls(**config_data)


class LayerConfig(BaseModel):
    """Configuration specific to individual layers."""

    enabled: bool = Field(default=True, description="Whether this layer is enabled")
    timeout: Optional[float] = Field(None, description="Layer-specific timeout override")
    max_retries: Optional[int] = Field(None, description="Layer-specific retry override")
    custom_prompts: Dict[str, str] = Field(
        default_factory=dict,
        description="Custom prompts for this layer"
    )


class ValidationConfig(BaseModel):
    """Configuration for validation settings."""

    strict_mode: bool = Field(
        default=True,
        description="Enable strict validation mode"
    )
    min_score_threshold: float = Field(
        default=0.7,
        description="Minimum validation score threshold",
        ge=0.0,
        le=1.0
    )
    enable_partial_results: bool = Field(
        default=True,
        description="Allow partial results when some validations fail"
    )


# Global configuration instance
_config: Optional[NetworkConfig] = None


def get_config() -> NetworkConfig:
    """Get the global configuration instance.

    Returns:
        NetworkConfig: The current configuration

    Raises:
        RuntimeError: If configuration has not been initialized
    """
    global _config
    if _config is None:
        raise RuntimeError("Configuration not initialized. Call init_config() first.")
    return _config


def init_config(config: Optional[NetworkConfig] = None) -> NetworkConfig:
    """Initialize the global configuration.

    Args:
        config: Configuration to use. If None, loads from environment.

    Returns:
        NetworkConfig: The initialized configuration
    """
    from .logging_config import setup_logging

    global _config
    if config is None:
        _config = NetworkConfig.from_env()
    else:
        _config = config

    # Setup logging after configuration is initialized
    setup_logging()

    return _config


def reload_config() -> NetworkConfig:
    """Reload configuration from environment variables.

    Returns:
        NetworkConfig: The reloaded configuration
    """
    global _config
    _config = NetworkConfig.from_env()
    return _config


def is_initialized() -> bool:
    """Check if configuration has been initialized.

    Returns:
        bool: True if configuration is initialized
    """
    global _config
    return _config is not None
