"""Pytest configuration and fixtures for NeuralBlitz tests."""

import pytest
import sys
import os
from pathlib import Path
from unittest.mock import MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def mock_llm():
    """Mock LLM for testing without API calls."""
    mock = MagicMock()
    mock.invoke.return_value = MagicMock(content="Mock LLM response")
    mock.generate.return_value = "Mock generated text"
    return mock


@pytest.fixture
def sample_belief_state():
    """Sample belief state for testing."""
    return {
        "precision": 0.85,
        "adaptation_count": 5,
        "current_task": "test_task",
        "context": {"domain": "testing"},
    }


@pytest.fixture
def temp_dir(tmp_path):
    """Temporary directory for file operations."""
    return tmp_path


@pytest.fixture
def mock_agent_config():
    """Mock agent configuration."""
    return {
        "name": "test_agent",
        "type": "worker",
        "max_retries": 3,
        "timeout": 30,
    }


@pytest.fixture
def sample_tool_result():
    """Sample tool execution result."""
    return {
        "success": True,
        "result": {"data": "test_data"},
        "prediction_error": 0.1,
    }


@pytest.fixture(autouse=True)
def suppress_import_warnings():
    """Suppress import warnings in tests."""
    import warnings
    warnings.filterwarnings("ignore", category=DeprecationWarning)
