"""Auto-adapting tests for cities - discovers classes dynamically."""
import pytest
import sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

def find_class(mod, prefix):
    for name, cls in inspect.getmembers(mod, inspect.isclass):
        if name.startswith(prefix) and cls.__module__ == mod.__name__:
            return cls
    return None

class TestSmartCityTraffic:
    def test_traffic_module_loads(self):
        mod = importlib.import_module("cities.smart_city_traffic_optimization")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2

class TestSmartCityEnergy:
    def test_energy_module_loads(self):
        mod = importlib.import_module("cities.smart_city_energy_management")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 2

class TestSmartCitySafety:
    def test_safety_module_loads(self):
        mod = importlib.import_module("cities.smart_city_safety_coordination")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
