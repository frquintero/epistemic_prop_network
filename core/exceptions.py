"""Custom exceptions for the Epistemological Propagation Network."""

from typing import Any, Dict, Optional


class EpistemicNetworkError(Exception):
    """Base exception for all network-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} (Details: {self.details})"
        return self.message


class ConfigurationError(EpistemicNetworkError):
    """Raised when there's a configuration-related error."""

    pass


class LLMError(EpistemicNetworkError):
    """Base class for LLM-related errors."""

    pass


class LLMConnectionError(LLMError):
    """Raised when there's a connection error with the LLM service."""

    pass


class LLMTimeoutError(LLMError):
    """Raised when an LLM request times out."""

    pass


class LLMQuotaError(LLMError):
    """Raised when LLM API quota is exceeded."""

    pass


class LLMInvalidResponseError(LLMError):
    """Raised when LLM returns an invalid or malformed response."""

    pass


class ValidationError(EpistemicNetworkError):
    """Raised when data validation fails."""

    pass


class LayerError(EpistemicNetworkError):
    """Base class for layer-specific errors."""

    pass


class LayerProcessingError(LayerError):
    """Raised when a layer fails to process input."""

    pass


class LayerTimeoutError(LayerError):
    """Raised when a layer processing times out."""

    pass


class LayerValidationError(LayerError):
    """Raised when layer output validation fails."""

    pass


class NetworkFlowError(EpistemicNetworkError):
    """Raised when there's an error in the network flow."""

    pass


class SerializationError(EpistemicNetworkError):
    """Raised when there's an error serializing or deserializing data."""

    pass


class SchemaValidationError(ValidationError):
    """Raised when Pydantic schema validation fails."""

    def __init__(self, message: str, validation_errors: Optional[list] = None):
        super().__init__(message, {"validation_errors": validation_errors or []})


class RetryExhaustedError(EpistemicNetworkError):
    """Raised when all retry attempts are exhausted."""

    pass


class MockResponseError(EpistemicNetworkError):
    """Raised when there's an error with mock responses in development."""

    pass


# Error handling utilities


def format_error_details(error: Exception) -> Dict[str, Any]:
    """Format error details for logging and reporting.

    Args:
        error: The exception to format

    Returns:
        Dict containing formatted error information
    """
    if isinstance(error, EpistemicNetworkError):
        return {
            "error_type": type(error).__name__,
            "message": error.message,
            "details": error.details,
        }
    else:
        return {
            "error_type": type(error).__name__,
            "message": str(error),
            "details": {},
        }


def is_retryable_error(error: Exception) -> bool:
    """Determine if an error is retryable.

    Args:
        error: The exception to check

    Returns:
        bool: True if the error is retryable
    """
    retryable_errors = (
        LLMConnectionError,
        LLMTimeoutError,
        ConnectionError,
        TimeoutError,
    )

    return isinstance(error, retryable_errors)


def get_error_category(error: Exception) -> str:
    """Get the category of an error for logging and metrics.

    Args:
        error: The exception to categorize

    Returns:
        str: Error category
    """
    if isinstance(error, (LLMConnectionError, LLMTimeoutError)):
        return "llm_connection"
    elif isinstance(error, LLMQuotaError):
        return "llm_quota"
    elif isinstance(error, LLMInvalidResponseError):
        return "llm_response"
    elif isinstance(error, ValidationError):
        return "validation"
    elif isinstance(error, LayerError):
        return "layer_processing"
    elif isinstance(error, ConfigurationError):
        return "configuration"
    elif isinstance(error, NetworkFlowError):
        return "network_flow"
    elif isinstance(error, SerializationError):
        return "serialization"
    else:
        return "unknown"
