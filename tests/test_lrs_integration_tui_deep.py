"""Deep tests for lrs_agents TUI layer - dynamic discovery."""
import pytest, sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "lrs_agents"))

class TestTUIBridge:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.bridge")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestTUIStateMirror:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.state_mirror")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestTUIConfig:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.config")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestTUITool:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.tool")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestTUIWebsocket:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.websocket_manager")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestTUIEndpoints:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.rest_endpoints")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestTUIPrecisionMapper:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.precision_mapper")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1

class TestTUIPluginManager:
    def test_module_loads(self):
        mod = importlib.import_module("lrs.integration.tui.plugins")
        classes = [n for n, o in inspect.getmembers(mod, inspect.isclass) if o.__module__ == mod.__name__]
        assert len(classes) >= 1
