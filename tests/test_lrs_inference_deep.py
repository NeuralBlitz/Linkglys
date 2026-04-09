"""Deep tests for lrs_agents inference layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lrs_agents"))

class TestLLMPolicyGenerator:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.inference.llm_policy_generator")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestHybridGEvaluator:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.inference.evaluator")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestMetaCognitivePrompter:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.inference.prompts")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
