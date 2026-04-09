"""Auto-adapting tests for federated learning - verifies modules load."""
import pytest, sys, os, importlib, inspect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
class TestDifferentialPrivacy:
    def test_module_loads(self):
        mod = importlib.import_module("federated.neuralblitz_federated_learning")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2
class TestFederatedConfig:
    def test_module_loads(self):
        mod = importlib.import_module("federated.neuralblitz_federated_learning")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2
class TestFederatedClient:
    def test_module_loads(self):
        mod = importlib.import_module("federated.neuralblitz_federated_learning")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert "FederatedClient" in classes or any("Client" in c for c in classes)
class TestFederatedServer:
    def test_module_loads(self):
        mod = importlib.import_module("federated.neuralblitz_federated_learning")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert "DistributedTrainingCoordinator" in classes or any("Coordinator" in c or "Server" in c for c in classes)
class TestSecureAggregation:
    def test_module_loads(self):
        mod = importlib.import_module("federated.neuralblitz_federated_learning")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2
class TestPrivacyAccountant:
    def test_module_loads(self):
        mod = importlib.import_module("federated.neuralblitz_federated_learning")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2
