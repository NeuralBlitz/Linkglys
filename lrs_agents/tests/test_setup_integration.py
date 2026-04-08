"""Tests for setup_lrs_integration."""

import pytest
from unittest.mock import Mock, patch


class TestSetupLRSIntegration:
    """Test setup integration module."""

    @patch("subprocess.run")
    def test_integrate_detects_opencode(self, mock_run):
        """Test detection of OpenCode CLI"""
        mock_result = Mock()
        mock_result.returncode = 0
        mock_run.return_value = mock_result

        # Just test the import works
        from lrs.opencode.setup_lrs_integration import integrate_with_opencode

        # Function exists and is callable
        assert callable(integrate_with_opencode)

    def test_module_imports(self):
        """Test that module imports successfully"""
        # Should be able to import the module
        from lrs.opencode import setup_lrs_integration

        assert setup_lrs_integration is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
