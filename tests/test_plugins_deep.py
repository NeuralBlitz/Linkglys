"""Deep tests for plugin system - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "plugins"))

class TestSampleToolPlugin:
    def test_module_loads(self):
        mod = importlib.import_module("sample_tool_plugin")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestSampleLRSPlugin:
    def test_module_loads(self):
        mod = importlib.import_module("sample_lrs_plugin")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
