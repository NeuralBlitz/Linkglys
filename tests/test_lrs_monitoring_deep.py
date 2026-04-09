"""Deep tests for lrs_agents monitoring layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lrs_agents"))

class TestStateTracker:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.monitoring.tracker")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestStructuredLogging:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.monitoring.structured_logging")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestDashboard:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.monitoring.dashboard")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
