"""Tests for CLI utilities."""

import pytest
from lrs.cli import BANNER, COMPACT_BANNER


class TestBanner:
    """Test CLI banners."""

    def test_banner_contains_version(self):
        """Banner should contain version placeholder"""
        assert "{version}" in BANNER

    def test_banner_contains_lrs_agents(self):
        """Banner should mention LRS-Agents"""
        assert "LRS-Agents" in BANNER or "Resilient" in BANNER

    def test_banner_contains_features(self):
        """Banner should list features"""
        assert "Features" in BANNER

    def test_banner_contains_quickstart(self):
        """Banner should have quick start guide"""
        assert "Quick Start" in BANNER

    def test_compact_banner_format(self):
        """Compact banner should be properly formatted"""
        assert "{version}" in COMPACT_BANNER
        assert "LRS-Agents" in COMPACT_BANNER or "Resilient" in COMPACT_BANNER


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
