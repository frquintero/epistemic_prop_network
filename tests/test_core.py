"""Basic tests for core components of the Epistemological Propagation Network."""

import os
import pytest
from unittest.mock import patch, MagicMock

from core.config import NetworkConfig, init_config, get_config
from core.exceptions import ConfigurationError, EpistemicNetworkError


class TestNetworkConfig:
    """Test NetworkConfig functionality."""

    def test_config_creation_with_valid_data(self):
        """Test creating config with valid data."""
        config = NetworkConfig(
            groq_api_key="test_key",
            groq_model="openai/gpt-oss-120b",
            max_concurrent_requests=2,
            temperature=0.2
        )

        assert config.groq_api_key == "test_key"
        assert config.groq_model == "openai/gpt-oss-120b"
        assert config.max_concurrent_requests == 2
        assert config.temperature == 0.2

    def test_config_creation_without_api_key_raises_error(self):
        """Test that config creation fails without API key."""
        with patch.dict(os.environ, {"GROQ_API_KEY": ""}):
            with pytest.raises(ValueError, match="GROQ_API_KEY must be provided either as parameter or environment variable"):
                NetworkConfig(groq_api_key="")

    def test_config_validation_bounds(self):
        """Test configuration value bounds validation."""
        # Test max_concurrent_requests bounds
        with pytest.raises(ValueError):
            NetworkConfig(groq_api_key="test", max_concurrent_requests=0)

        with pytest.raises(ValueError):
            NetworkConfig(groq_api_key="test", max_concurrent_requests=15)

        # Test temperature bounds
        with pytest.raises(ValueError):
            NetworkConfig(groq_api_key="test", temperature=-0.1)

        with pytest.raises(ValueError):
            NetworkConfig(groq_api_key="test", temperature=1.5)

    @patch.dict("os.environ", {"GROQ_API_KEY": "env_test_key"})
    def test_config_from_env(self):
        """Test loading config from environment variables."""
        config = NetworkConfig.from_env()

        assert config.groq_api_key == "env_test_key"
        assert config.groq_model == "openai/gpt-oss-120b"  # default
        assert config.max_concurrent_requests == 3  # default

    def test_config_initialization_and_get(self):
        """Test global config initialization and retrieval."""
        config = NetworkConfig(groq_api_key="test_key")
        init_config(config)

        retrieved_config = get_config()
        assert retrieved_config.groq_api_key == "test_key"

    def test_get_config_without_init_raises_error(self):
        """Test that get_config raises error when not initialized."""
        # Reset global config
        import core.config
        core.config._config = None

        with pytest.raises(RuntimeError, match="Configuration not initialized"):
            get_config()


class TestEpistemicNetworkError:
    """Test custom exception classes."""

    def test_base_exception_creation(self):
        """Test base exception creation."""
        error = EpistemicNetworkError("Test message")
        assert str(error) == "Test message"
        assert error.message == "Test message"
        assert error.details == {}

    def test_exception_with_details(self):
        """Test exception with additional details."""
        details = {"code": 500, "url": "http://example.com"}
        error = EpistemicNetworkError("Server error", details)

        assert "Server error" in str(error)
        assert "Details:" in str(error)
        assert error.details == details

    def test_configuration_error(self):
        """Test ConfigurationError."""
        error = ConfigurationError("Invalid config")
        assert isinstance(error, EpistemicNetworkError)
        assert error.message == "Invalid config"


class TestErrorHandlingUtilities:
    """Test error handling utility functions."""

    def test_format_error_details_base_exception(self):
        """Test formatting base exception details."""
        error = ValueError("Test error")
        details = format_error_details(error)

        assert details["error_type"] == "ValueError"
        assert details["message"] == "Test error"
        assert details["details"] == {}

    def test_format_error_details_custom_exception(self):
        """Test formatting custom exception details."""
        details_dict = {"code": 404}
        error = EpistemicNetworkError("Not found", details_dict)
        formatted = format_error_details(error)

        assert formatted["error_type"] == "EpistemicNetworkError"
        assert formatted["message"] == "Not found"
        assert formatted["details"] == details_dict

    def test_is_retryable_error(self):
        """Test retryable error detection."""
        from core.exceptions import LLMConnectionError, LLMTimeoutError, ValidationError

        assert is_retryable_error(LLMConnectionError("Connection failed"))
        assert is_retryable_error(LLMTimeoutError("Request timed out"))
        assert is_retryable_error(ConnectionError("Network error"))
        assert is_retryable_error(TimeoutError("Timeout"))

        assert not is_retryable_error(ValidationError("Invalid data"))

    def test_get_error_category(self):
        """Test error categorization."""
        from core.exceptions import (
            LLMConnectionError, LLMQuotaError, ValidationError,
            LayerError, ConfigurationError
        )

        assert get_error_category(LLMConnectionError("test")) == "llm_connection"
        assert get_error_category(LLMQuotaError("test")) == "llm_quota"
        assert get_error_category(ValidationError("test")) == "validation"
        assert get_error_category(LayerError("test")) == "layer_processing"
        assert get_error_category(ConfigurationError("test")) == "configuration"
        assert get_error_category(ValueError("test")) == "unknown"


# Import the utility functions for testing
from core.exceptions import format_error_details, is_retryable_error, get_error_category