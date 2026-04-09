"""Auto-adapting tests for src/capabilities/ - verifies modules load and have classes."""
import pytest
import sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def find_class(mod, prefix):
    for name, cls in inspect.getmembers(mod, inspect.isclass):
        if name.startswith(prefix) and cls.__module__ == mod.__name__:
            return cls
    return None

class TestMLAutomatedPipeline:
    def test_module_loads(self):
        mod = importlib.import_module("capabilities.ck_ml_automated_pipeline")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestDataQualityAssessment:
    def test_module_loads(self):
        mod = importlib.import_module("capabilities.ck_data_quality_assessment")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestFeatureEngineering:
    def test_module_loads(self):
        mod = importlib.import_module("capabilities.ck_feature_engineering_automation")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestNeuralBlitzCodeKernels:
    def test_module_loads(self):
        mod = importlib.import_module("capabilities.neuralblitz_code_kernels")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestQuadraticVoting:
    def test_module_loads(self):
        mod = importlib.import_module("capabilities.quadratic_voting_ck")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestNetworkAnomalyDetector:
    def test_module_loads(self):
        mod = importlib.import_module("capabilities.network_anomaly_detector_ck")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestMalwareSignatureAnalyzer:
    def test_module_loads(self):
        mod = importlib.import_module("capabilities.malware_signature_analyzer_ck")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
