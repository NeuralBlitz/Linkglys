"""Tests for simplified integration."""

import pytest
from unittest.mock import patch
from lrs.opencode.simplified_integration import (
    SimplifiedToolLens,
    OpenCodeTool,
    SimplifiedLRSAgent,
)


class TestSimplifiedToolLens:
    """Test SimplifiedToolLens base class."""

    def test_initialization(self):
        """Test tool initialization"""

        class DummyTool(SimplifiedToolLens):
            def get(self, state):
                return {"result": "ok"}

        tool = DummyTool("test")
        assert tool.name == "test"

    def test_set_updates_state(self):
        """Test set updates belief state"""

        class DummyTool(SimplifiedToolLens):
            def get(self, state):
                return {"result": "ok"}

        tool = DummyTool("test")
        state = {"key": "value"}
        new_state = tool.set(state, "result")

        assert new_state["last_result"] == "result"
        assert new_state["key"] == "value"


class TestOpenCodeToolSimplified:
    """Test OpenCodeTool (simplified version)."""

    def test_initialization(self):
        """Test initialization"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value=None):
            tool = OpenCodeTool()
            assert tool.name == "opencode_tool"

    def test_get_without_opencode(self):
        """Test get without opencode"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value=None):
            tool = OpenCodeTool()

            result = tool.get({})

            assert result["success"] is False

    def test_get_no_task(self):
        """Test get with no task"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value="/fake"):
            tool = OpenCodeTool()

            result = tool.get({})

            assert result["success"] is False


class TestSimplifiedLRSAgent:
    """Test SimplifiedLRSAgent."""

    def test_initialization(self):
        """Test initialization"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value=None):
            tool = OpenCodeTool()
            agent = SimplifiedLRSAgent(tools=[tool])

            assert len(agent.tools) == 1

    def test_initialization_empty_tools(self):
        """Test initialization with no tools"""
        agent = SimplifiedLRSAgent(tools=[])

        assert len(agent.tools) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
