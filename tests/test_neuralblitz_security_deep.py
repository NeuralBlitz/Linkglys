"""Deep tests for neuralblitz-v50 security layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "neuralblitz-v50"))

class TestAuditLogger:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.security.audit")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestRBACManager:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.security.auth")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 3
