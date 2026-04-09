"""Deep tests for lrs_agents autonomous layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lrs_agents"))

class TestAutonomousCodeGeneration:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.autonomous.phase7_autonomous_code_generation")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2

class TestAutonomousDemo:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.autonomous.phase7_demo")
        assert mod is not None

class TestAutonomousWebInterface:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.autonomous.phase7_web_interface")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
