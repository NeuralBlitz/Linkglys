"""Auto-adapting tests for iot_mesh_system - verifies modules load."""
import pytest, sys, os, importlib, inspect
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "iot_mesh_system"))
class TestIoTDeviceModels:
    def test_module_loads(self):
        from iot_mesh_core import DeviceType, DeviceState, IoTDevice
        assert DeviceType.LIGHT is not None
        assert DeviceState.ONLINE is not None
        assert IoTDevice is not None
class TestDeviceDiscovery:
    def test_module_loads(self):
        from device_discovery import DeviceDiscoveryManager
        assert DeviceDiscoveryManager() is not None
class TestDatabaseManager:
    def test_module_loads(self, tmp_path):
        from database import DatabaseManager
        db = DatabaseManager(str(tmp_path / "test.db"))
        assert db is not None
class TestMQTTBroker:
    def test_module_loads(self):
        from mqtt_broker import MockMQTTBroker
        assert MockMQTTBroker is not None
class TestAutomationEngine:
    def test_module_loads(self):
        from automation_engine import AutomationRuleEngine
        assert AutomationRuleEngine is not None
