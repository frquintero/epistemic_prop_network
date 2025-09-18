"""Test configuration and fixtures for the Epistemological Propagation Network."""

import asyncio
import os
from typing import Any, AsyncGenerator, Dict
from unittest.mock import AsyncMock, MagicMock

import pytest

from core.config import NetworkConfig, init_config
from core.exceptions import EpistemicNetworkError


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
def setup_test_config():
    """Setup test configuration for all tests."""
    # Create test configuration
    test_config = NetworkConfig(
        groq_api_key="test_api_key",
        groq_model="openai/gpt-oss-120b",
        max_concurrent_requests=1,  # Reduce for testing
        request_timeout=30.0,  # Shorter timeout for tests
        max_retries=1,  # Reduce retries for faster tests
        temperature=0.1,
        max_tokens_per_request=2048,  # Smaller for tests
        log_level="DEBUG",
        enable_structured_logging=False,  # Disable for simpler test output
        debug_mode=True,
        mock_responses=True,  # Use mock responses for tests
    )

    # Initialize global config
    init_config(test_config)
    yield test_config


@pytest.fixture
def mock_llm_response() -> Dict[str, Any]:
    """Mock LLM response for testing."""
    return {
        "semantic": "A mental model is an internal representation of external reality.",
        "genealogical": "The concept originated with Kenneth Craik in 1943.",
        "teleological": "Mental models help individuals understand and predict complex systems.",
    }


@pytest.fixture
def mock_validation_response() -> Dict[str, Any]:
    """Mock validation response for testing."""
    return {
        "correspondence": "This definition aligns with empirical studies on cognitive representations.",
        "coherence": "The definition is logically consistent with established theories.",
        "pragmatic": "This concept has practical applications in decision-making and problem-solving.",
    }


@pytest.fixture
def mock_network_request() -> Dict[str, Any]:
    """Mock network request for testing."""
    return {
        "question": "What are mental models?",
        "context": "Epistemological inquiry into cognitive frameworks",
    }


class MockLLMClient:
    """Mock LLM client for testing."""

    def __init__(self, responses: Dict[str, Any] = None):
        self.responses = responses or {}
        self.call_count = 0
        self.last_call_args = None

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Mock generate_text method."""
        self.call_count += 1
        self.last_call_args = {"prompt": prompt, **kwargs}

        # Return mock response based on prompt content
        if "semantic" in prompt.lower():
            return self.responses.get("semantic", "Mock semantic response")
        elif "genealogical" in prompt.lower():
            return self.responses.get("genealogical", "Mock genealogical response")
        elif "teleological" in prompt.lower():
            return self.responses.get("teleological", "Mock teleological response")
        elif "correspondence" in prompt.lower():
            return self.responses.get("correspondence", "Mock correspondence response")
        elif "coherence" in prompt.lower():
            return self.responses.get("coherence", "Mock coherence response")
        elif "pragmatic" in prompt.lower():
            return self.responses.get("pragmatic", "Mock pragmatic response")
        else:
            # For reformulator prompts, return a proper epistemological question based on the input
            if "reformulate" in prompt.lower() or "epistemological" in prompt.lower():
                if "mental models" in prompt.lower():
                    return "What is the conceptual definition, theoretical basis, and functional role of mental models in cognitive science, and how are they empirically investigated and evaluated?"
                elif "israel" in prompt.lower() or "palestine" in prompt.lower():
                    return "What historical, political, economic, and sociocultural factors have contributed to the prolonged nature of the Israeli-Palestinian conflict, as examined within the disciplines of Middle Eastern studies, international relations, and conflict resolution?"
                elif "politicians" in prompt.lower() or "country" in prompt.lower():
                    return "How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?"
                else:
                    return "What is the conceptual definition and functional role of mental models in cognitive processes, from an epistemological and psychological perspective?"
            return "Mock LLM response"

    def generate_text_sync(self, prompt: str, **kwargs) -> str:
        """Mock synchronous generate_text method."""
        self.call_count += 1
        self.last_call_args = {"prompt": prompt, **kwargs}

        # Return mock response based on prompt content
        if "semantic" in prompt.lower():
            return self.responses.get("semantic", "Mock semantic response")
        elif "genealogical" in prompt.lower():
            return self.responses.get("genealogical", "Mock genealogical response")
        elif "teleological" in prompt.lower():
            return self.responses.get("teleological", "Mock teleological response")
        elif "correspondence" in prompt.lower():
            return self.responses.get("correspondence", "Mock correspondence response")
        elif "coherence" in prompt.lower():
            return self.responses.get("coherence", "Mock coherence response")
        elif "pragmatic" in prompt.lower():
            return self.responses.get("pragmatic", "Mock pragmatic response")
        else:
            # For reformulator prompts, return a proper epistemological question based on the input
            if "reformulate" in prompt.lower() or "epistemological" in prompt.lower():
                if "mental models" in prompt.lower():
                    return "What is the conceptual definition, theoretical basis, and functional role of mental models in cognitive science, and how are they empirically investigated and evaluated?"
                elif "israel" in prompt.lower() or "palestine" in prompt.lower():
                    return "What historical, political, economic, and sociocultural factors have contributed to the prolonged nature of the Israeli-Palestinian conflict, as examined within the disciplines of Middle Eastern studies, international relations, and conflict resolution?"
                elif "politicians" in prompt.lower() or "country" in prompt.lower():
                    return "How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?"
                else:
                    return "What is the conceptual definition and functional role of mental models in cognitive processes, from an epistemological and psychological perspective?"
            return "Mock synchronous LLM response"


@pytest.fixture
def mock_llm_client(mock_llm_response: Dict[str, Any]) -> MockLLMClient:
    """Mock LLM client fixture."""
    return MockLLMClient(mock_llm_response)


class AsyncMockLLMClient:
    """Async mock LLM client for testing."""

    def __init__(self, responses: Dict[str, Any] = None):
        self.responses = responses or {}
        self.call_count = 0
        self.last_call_args = None

    async def generate_text(self, prompt: str, **kwargs) -> str:
        """Async mock generate_text method."""
        await asyncio.sleep(0.01)  # Simulate async operation
        self.call_count += 1
        self.last_call_args = {"prompt": prompt, **kwargs}

        # Return mock response based on prompt content - same logic as MockLLMClient
        if "semantic" in prompt.lower():
            return self.responses.get("semantic", "Mock semantic response")
        elif "genealogical" in prompt.lower():
            return self.responses.get("genealogical", "Mock genealogical response")
        elif "teleological" in prompt.lower():
            return self.responses.get("teleological", "Mock teleological response")
        elif "correspondence" in prompt.lower():
            return self.responses.get("correspondence", "Mock correspondence response")
        elif "coherence" in prompt.lower():
            return self.responses.get("coherence", "Mock coherence response")
        elif "pragmatic" in prompt.lower():
            return self.responses.get("pragmatic", "Mock pragmatic response")
        else:
            # For reformulator prompts, return a proper epistemological question based on the input
            if "reformulate" in prompt.lower() or "epistemological" in prompt.lower():
                if "mental models" in prompt.lower():
                    return "What is the conceptual definition, theoretical basis, and functional role of mental models in cognitive science, and how are they empirically investigated and evaluated?"
                elif "israel" in prompt.lower() or "palestine" in prompt.lower():
                    return "What historical, political, economic, and sociocultural factors have contributed to the prolonged nature of the Israeli-Palestinian conflict, as examined within the disciplines of Middle Eastern studies, international relations, and conflict resolution?"
                elif "politicians" in prompt.lower() or "country" in prompt.lower():
                    return "How do differing interpretations of governmental effectiveness shape public discourse on national progress, from a political sociology perspective?"
                else:
                    return "What is the conceptual definition and functional role of mental models in cognitive processes, from an epistemological and psychological perspective?"
            return "Mock async LLM response"

    async def generate_structured_output(
        self, prompt: str, schema: Any, **kwargs
    ) -> Dict[str, Any]:
        """Async mock generate_structured_output method."""
        await asyncio.sleep(0.01)  # Simulate async operation
        self.call_count += 1
        self.last_call_args = {"prompt": prompt, "schema": schema, **kwargs}
        return self.responses


@pytest.fixture
def async_mock_llm_client(mock_llm_response: Dict[str, Any]) -> AsyncMockLLMClient:
    """Async mock LLM client fixture."""
    return AsyncMockLLMClient(mock_llm_response)


@pytest.fixture
def sample_prompts() -> Dict[str, str]:
    """Sample prompts for testing."""
    return {
        "semantic": "Define the concept of mental models from a semantic perspective.",
        "genealogical": "Trace the historical development of the concept of mental models.",
        "teleological": "Explain the purpose and function of mental models.",
        "correspondence": "Validate the correspondence of mental model theories with empirical evidence.",
        "coherence": "Assess the logical coherence of mental model frameworks.",
        "pragmatic": "Evaluate the practical utility of mental models in real-world applications.",
    }


@pytest.fixture
def test_data_dir(tmp_path) -> str:
    """Create a temporary directory for test data."""
    test_dir = tmp_path / "test_data"
    test_dir.mkdir()
    return str(test_dir)


# Custom test markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "llm: mark test as requiring LLM calls")


# Test utilities
def assert_valid_triple(triple: Dict[str, Any], expected_keys: list) -> None:
    """Assert that a triple has the expected structure."""
    assert isinstance(triple, dict), "Triple must be a dictionary"
    for key in expected_keys:
        assert key in triple, f"Triple missing key: {key}"
        assert isinstance(triple[key], str), f"Triple value for {key} must be string"
        assert len(triple[key]) > 0, f"Triple value for {key} must not be empty"


def assert_error_logged(caplog, error_type: str, message_contains: str = None) -> None:
    """Assert that an error was logged."""
    error_records = [record for record in caplog.records if record.levelname == "ERROR"]
    assert len(error_records) > 0, "No error was logged"

    if message_contains:
        error_messages = [record.message for record in error_records]
        assert any(
            message_contains in msg for msg in error_messages
        ), f"Error message containing '{message_contains}' not found in: {error_messages}"


async def wait_for_condition(
    condition_func, timeout: float = 5.0, interval: float = 0.1
):
    """Wait for a condition to become true."""
    import time

    start_time = time.time()

    while time.time() - start_time < timeout:
        if condition_func():
            return True
        await asyncio.sleep(interval)

    raise TimeoutError(f"Condition not met within {timeout} seconds")


# Environment variable helpers for tests
def set_test_env_vars():
    """Set environment variables for testing."""
    os.environ["GROQ_API_KEY"] = "test_api_key"
    os.environ["GROQ_MODEL"] = "openai/gpt-oss-120b"
    os.environ["MAX_CONCURRENT_REQUESTS"] = "1"
    os.environ["REQUEST_TIMEOUT"] = "30.0"
    os.environ["MAX_RETRIES"] = "1"
    os.environ["TEMPERATURE"] = "0.1"
    os.environ["MAX_TOKENS_PER_REQUEST"] = "2048"
    os.environ["LOG_LEVEL"] = "DEBUG"
    os.environ["STRUCTURED_LOGGING"] = "false"
    os.environ["DEBUG_MODE"] = "true"
    os.environ["MOCK_RESPONSES"] = "true"


def clear_test_env_vars():
    """Clear test environment variables."""
    test_vars = [
        "GROQ_API_KEY",
        "GROQ_MODEL",
        "MAX_CONCURRENT_REQUESTS",
        "REQUEST_TIMEOUT",
        "MAX_RETRIES",
        "TEMPERATURE",
        "MAX_TOKENS_PER_REQUEST",
        "LOG_LEVEL",
        "STRUCTURED_LOGGING",
        "DEBUG_MODE",
        "MOCK_RESPONSES",
    ]

    for var in test_vars:
        os.environ.pop(var, None)
