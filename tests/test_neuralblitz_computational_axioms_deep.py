"""Deep tests for ComputationalAxioms - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "neuralblitz-v50", "ComputationalAxioms", "python"))

class TestGoldenDAG:
    def test_module_loads(self):
        mod = importlib.import_module("goldendag_core")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2
