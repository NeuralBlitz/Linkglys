"""Deep tests for lrs_agents opencode layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lrs_agents"))

class TestLightweightLRS:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.opencode.lightweight_lrs")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2

class TestOpenCodeTool:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.opencode.opencode_lrs_tool")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestLRSOpenCodeIntegration:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.opencode.lrs_opencode_integration")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestSimplifiedIntegration:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.opencode.simplified_integration")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
