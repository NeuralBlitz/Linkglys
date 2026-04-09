"""Auto-adapting tests for integrations - verifies modules load."""
import pytest, sys, os, importlib, inspect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
class TestPineconeIntegration:
    def test_module_loads(self):
        mod = importlib.import_module("integrations.pinecone_integration")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
class TestChromaDBIntegration:
    def test_module_loads(self):
        mod = importlib.import_module("integrations.chromadb_integration")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
class TestWeaviateIntegration:
    def test_module_loads(self):
        mod = importlib.import_module("integrations.weaviate_integration")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
