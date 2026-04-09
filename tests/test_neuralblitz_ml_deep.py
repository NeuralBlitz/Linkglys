"""Deep tests for neuralblitz-v50 ML layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "neuralblitz-v50"))

class TestIntentClassifier:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.ml.classifier")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestConsciousnessPredictor:
    def test_module_loads(self):
        mod = importlib.import_module("neuralblitz.ml.predictor")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
