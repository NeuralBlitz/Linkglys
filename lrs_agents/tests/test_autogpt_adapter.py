"""Tests for AutoGPT adapter."""

import pytest
from unittest.mock import Mock, MagicMock
from lrs.integration.autogpt_adapter import AutoGPTCommand, LRSAutoGPTAgent, convert_autogpt_to_lrs


class TestAutoGPTCommand:
    """Test AutoGPTCommand class."""

    def test_initialization(self):
        """Test command initialization"""

        def sample_func(arg1):
            return f"Result: {arg1}"

        cmd = AutoGPTCommand(
            command_name="test_cmd", command_func=sample_func, description="A test command"
        )

        assert cmd.name == "test_cmd"
        assert cmd.command_func == sample_func
        assert cmd.description == "A test command"

    def test_get_success(self):
        """Test successful command execution"""

        def sample_func(arg1):
            return {"result": "success", "data": "test"}

        cmd = AutoGPTCommand("test_cmd", sample_func, "Test")

        result = cmd.get({"args": {"arg1": "value"}})

        assert result.success is True
        assert result.prediction_error < 0.5

    def test_get_with_error(self):
        """Test command execution with error"""

        def sample_func(arg1):
            return {"error": "Something went wrong"}

        cmd = AutoGPTCommand("test_cmd", sample_func, "Test")

        result = cmd.get({"args": {"arg1": "value"}})

        assert result.success is False
        assert result.prediction_error > 0.5

    def test_get_exception(self):
        """Test command execution with exception"""

        def sample_func(arg1):
            raise ValueError("Test error")

        cmd = AutoGPTCommand("test_cmd", sample_func, "Test")

        result = cmd.get({"args": {"arg1": "value"}})

        assert result.success is False
        assert "Test error" in result.error

    def test_set_updates_state(self):
        """Test state update"""

        def sample_func():
            return "result"

        cmd = AutoGPTCommand("test_cmd", sample_func, "Test")

        state = {"existing": "value"}
        new_state = cmd.set(state, "observation")

        assert "test_cmd_result" in new_state
        assert new_state["existing"] == "value"


class TestLRSAutoGPTAgent:
    """Test LRSAutoGPTAgent class."""

    def test_initialization(self):
        """Test agent initialization"""

        def cmd1():
            return "result"

        mock_llm = Mock()

        agent = LRSAutoGPTAgent(
            name="TestAgent", role="Test assistant", commands={"cmd1": cmd1}, llm=mock_llm
        )

        assert agent.name == "TestAgent"
        assert agent.role == "Test assistant"
        assert len(agent.registry.tools) == 1

    def test_initialization_with_goals(self):
        """Test agent with goals"""

        def cmd1():
            return "result"

        mock_llm = Mock()

        agent = LRSAutoGPTAgent(
            name="TestAgent",
            role="Test assistant",
            commands={"cmd1": cmd1},
            llm=mock_llm,
            goals=["Goal 1", "Goal 2"],
        )

        assert len(agent.goals) == 2

    def test_registry_contains_commands(self):
        """Test commands are registered"""

        def cmd1():
            return "result"

        def cmd2(arg):
            return f"processed {arg}"

        mock_llm = Mock()

        agent = LRSAutoGPTAgent(
            name="TestAgent", role="Test", commands={"cmd1": cmd1, "cmd2": cmd2}, llm=mock_llm
        )

        assert "cmd1" in agent.registry.tools
        assert "cmd2" in agent.registry.tools


class TestConvertAutoGPToLRS:
    """Test convert_autogpt_to_lrs function."""

    def test_conversion(self):
        """Test converting AutoGPT config to LRS agent"""
        config = {
            "name": "TestAgent",
            "role": "Test assistant",
            "commands": {"cmd1": lambda: "result"},
            "goals": ["Test goal"],
        }

        mock_llm = Mock()

        agent = convert_autogpt_to_lrs(config, mock_llm)

        assert isinstance(agent, LRSAutoGPTAgent)
        assert agent.name == "TestAgent"
        assert agent.role == "Test assistant"

    def test_conversion_without_goals(self):
        """Test conversion without goals"""
        config = {
            "name": "TestAgent",
            "role": "Test assistant",
            "commands": {"cmd1": lambda: "result"},
        }

        mock_llm = Mock()

        agent = convert_autogpt_to_lrs(config, mock_llm)

        assert agent.goals == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
