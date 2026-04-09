"""Deep tests for neuralblitz-v50 integrations layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "neuralblitz-v50"))

class TestIntegrationManager:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.integrations")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 3

class TestLLMConnector:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.integrations.connectors.llm_connector")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2

class TestHuggingFaceConnector:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.integrations.connectors.huggingface_connector")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestWeb3Connector:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.integrations.connectors.web3_connector")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
