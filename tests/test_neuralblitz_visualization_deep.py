"""Deep tests for neuralblitz-v50 visualization layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "neuralblitz-v50"))

class TestDashboard:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.visualization.dashboard")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestSimpleDashboard:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.visualization.simple_dashboard")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
