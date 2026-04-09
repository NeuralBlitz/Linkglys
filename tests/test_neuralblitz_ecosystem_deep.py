"""Deep tests for neuralblitz-v50 ecosystem layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "neuralblitz-v50"))

class TestEcosystemProtocol:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.ecosystem.protocol")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 3

class TestServiceBus:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.ecosystem.service_bus")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestOrchestrator:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.ecosystem.orchestrator")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestRealAdapters:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.ecosystem.real_adapters")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
