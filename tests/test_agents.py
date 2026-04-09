"""Auto-adapting tests for agents - discovers classes dynamically."""
import pytest
import sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def find_class(mod, prefix):
    for name, cls in inspect.getmembers(mod, inspect.isclass):
        if name.startswith(prefix) and cls.__module__ == mod.__name__:
            return cls
    return None

class TestAdvancedAutonomousAgent:
    def test_module_loads(self):
        mod = importlib.import_module("agents.advanced_autonomous_agent_framework")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestAutonomousSelfEvolution:
    def test_module_loads(self):
        mod = importlib.import_module("agents.autonomous_self_evolution_simplified")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestMultiLayeredMultiAgent:
    def test_module_loads(self):
        mod = importlib.import_module("agents.multi_layered_multi_agent_system")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestDistributedMLMAS:
    def test_module_loads(self):
        mod = importlib.import_module("agents.distributed_mlmas")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
