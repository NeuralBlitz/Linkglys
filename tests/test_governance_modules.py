"""Auto-adapting tests for Governance/ modules - only verifies modules load and have classes."""
import pytest
import sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "Governance"))

class TestMultiMetricMonitor:
    def test_module_loads(self):
        from Conscientia.MultiMetricMonitor import MultiMetricMonitor
        assert MultiMetricMonitor is not None
        mmm = MultiMetricMonitor()
        assert mmm is not None

class TestEarlyWarningSystem:
    def test_module_loads(self):
        from SentiaGuard.EarlyWarningSystem import EarlyWarningSystem, AlertLevel
        assert EarlyWarningSystem is not None
        ews = EarlyWarningSystem()
        assert ews is not None
        assert AlertLevel.GREEN is not None

class TestAutomatedRCA:
    def test_module_loads(self):
        from Veritas.AutomatedRCA import AutomatedRCA, RootCauseCategory
        assert AutomatedRCA is not None
        arca = AutomatedRCA()
        assert arca is not None
        assert RootCauseCategory.CHARTER_VIOLATION is not None
