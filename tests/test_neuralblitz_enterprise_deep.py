"""Deep tests for neuralblitz-v50 enterprise layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "neuralblitz-v50"))

class TestGranularMathematics:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.enterprise.granular_mathematics")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2

class TestSheafAttention:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.enterprise.sheaf_attention")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
