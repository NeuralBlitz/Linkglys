"""Tests for OpenCode tool."""

import pytest
from unittest.mock import Mock, patch
from lrs.opencode.opencode_lrs_tool import OpenCodeTool


class TestOpenCodeTool:
    """Test OpenCodeTool class."""

    def test_initialization(self):
        """Test tool initialization"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value=None):
            tool = OpenCodeTool()

            assert tool.name == "opencode_tool"

    def test_initialization_custom_name(self):
        """Test custom name"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value=None):
            tool = OpenCodeTool(name="my_tool")

            assert tool.name == "my_tool"

    @patch("subprocess.run")
    def test_find_opencode_not_found(self, mock_run):
        """Test when opencode is not found"""
        mock_run.side_effect = FileNotFoundError()

        tool = OpenCodeTool()

        assert tool.opencode_path is None

    @patch("subprocess.run")
    def test_find_opencode_found(self, mock_run):
        """Test when opencode is found"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        tool = OpenCodeTool()

        assert tool.opencode_path is not None

    def test_get_without_opencode(self):
        """Test execution when opencode not available"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value=None):
            tool = OpenCodeTool()

            result = tool.get({})

            assert result.success is False

    def test_get_no_task_specified(self):
        """Test execution with no task in belief state"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value="/fake/path"):
            tool = OpenCodeTool()

            result = tool.get({})

            assert result.success is False

    def test_set_updates_state(self):
        """Test set method updates state"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value=None):
            tool = OpenCodeTool()

            state = {"existing": "value"}
            new_state = tool.set(state, "observation")

            assert new_state["existing"] == "value"


class TestOpenCodeToolExecution:
    """Test execution scenarios."""

    def test_search_task(self):
        """Test search task mapping"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value="/fake/opencode"):
            tool = OpenCodeTool()

            result = tool.get({"current_task": "search for files"})

            assert result is not None

    def test_read_task_no_file(self):
        """Test read task without file path"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value="/fake/opencode"):
            tool = OpenCodeTool()

            result = tool.get({"current_task": "read file"})

            assert result is not None

    def test_edit_task(self):
        """Test edit task handling"""
        with patch.object(OpenCodeTool, "_find_opencode", return_value="/fake/opencode"):
            tool = OpenCodeTool()

            result = tool.get({"current_task": "edit file"})

            assert result is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
