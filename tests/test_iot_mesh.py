"""Tests for iot_mesh_system/iot_mesh_core.py - IoT device mesh."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "iot_mesh_system"))


@pytest.fixture
def iot_module():
    """Import IoT mesh module."""
    if "iot_mesh_core" in sys.modules:
        del sys.modules["iot_mesh_core"]

    from iot_mesh_core import DeviceType, DeviceState, Device, IoTMeshNetwork
    return {
        "DeviceType": DeviceType,
        "DeviceState": DeviceState,
        "Device": Device,
        "IoTMeshNetwork": IoTMeshNetwork,
    }


class TestDeviceType:
    """Test DeviceType enum."""

    def test_device_types_exist(self, iot_module):
        """Test all expected device types exist."""
        DT = iot_module["DeviceType"]
        assert DT.LIGHT is not None
        assert DT.THERMOSTAT is not None
        assert DT.CAMERA is not None
        assert DT.DOOR_LOCK is not None
        assert DT.MOTION_SENSOR is not None
        assert DT.GENERIC is not None


class TestDeviceState:
    """Test DeviceState enum."""

    def test_device_states_exist(self, iot_module):
        """Test device states exist."""
        DS = iot_module["DeviceState"]
        assert DS.ONLINE is not None
        assert DS.OFFLINE is not None


class TestDevice:
    """Test Device dataclass."""

    def test_device_creation(self, iot_module):
        """Test device creation."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]

        device = Device(
            device_id="light_1",
            device_type=DT.LIGHT,
            name="Kitchen Light",
        )

        assert device.device_id == "light_1"
        assert device.device_type == DT.LIGHT
        assert device.name == "Kitchen Light"

    def test_device_to_dict(self, iot_module):
        """Test device serialization."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]

        device = Device(
            device_id="thermo_1",
            device_type=DT.THERMOSTAT,
            name="Thermostat",
        )

        result = device.to_dict()
        assert isinstance(result, dict)
        assert result["device_id"] == "thermo_1"
        assert "name" in result

    def test_device_auto_timestamp(self, iot_module):
        """Test device auto-generates timestamp."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]

        device = Device(
            device_id="sensor_1",
            device_type=DT.MOTION_SENSOR,
            name="Motion Sensor",
        )

        assert device.last_seen is not None or device.created_at is not None


class TestIoTMeshNetwork:
    """Test IoTMeshNetwork class."""

    def test_network_initialization(self, iot_module):
        """Test network initializes correctly."""
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]
        network = IoTMeshNetwork()
        assert network is not None

    def test_network_add_device(self, iot_module):
        """Test adding device to network."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]

        network = IoTMeshNetwork()
        device = Device(
            device_id="test_device",
            device_type=DT.LIGHT,
            name="Test Light",
        )

        network.add_device(device)
        assert "test_device" in network.devices

    def test_network_remove_device(self, iot_module):
        """Test removing device from network."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]

        network = IoTMeshNetwork()
        device = Device(
            device_id="temp_device",
            device_type=DT.THERMOSTAT,
            name="Temp Thermostat",
        )
        network.add_device(device)
        network.remove_device("temp_device")
        assert "temp_device" not in network.devices

    def test_network_get_device(self, iot_module):
        """Test getting device from network."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]

        network = IoTMeshNetwork()
        device = Device(
            device_id="camera_1",
            device_type=DT.CAMERA,
            name="Front Door Camera",
        )
        network.add_device(device)

        retrieved = network.get_device("camera_1")
        assert retrieved is not None
        assert retrieved.device_type == DT.CAMERA

    def test_network_get_unknown_device(self, iot_module):
        """Test getting unknown device returns None."""
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]
        network = IoTMeshNetwork()

        result = network.get_device("nonexistent")
        assert result is None

    def test_network_list_devices(self, iot_module):
        """Test listing all devices."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]

        network = IoTMeshNetwork()
        network.add_device(Device(device_id="d1", device_type=DT.LIGHT, name="Light 1"))
        network.add_device(Device(device_id="d2", device_type=DT.LIGHT, name="Light 2"))

        devices = network.list_devices()
        assert len(devices) >= 2

    def test_network_get_devices_by_type(self, iot_module):
        """Test filtering devices by type."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]

        network = IoTMeshNetwork()
        network.add_device(Device(device_id="l1", device_type=DT.LIGHT, name="Light 1"))
        network.add_device(Device(device_id="l2", device_type=DT.LIGHT, name="Light 2"))
        network.add_device(Device(device_id="t1", device_type=DT.THERMOSTAT, name="Thermostat"))

        lights = network.get_devices_by_type(DT.LIGHT)
        assert len(lights) == 2

    def test_network_device_count(self, iot_module):
        """Test device count."""
        DT = iot_module["DeviceType"]
        Device = iot_module["Device"]
        IoTMeshNetwork = iot_module["IoTMeshNetwork"]

        network = IoTMeshNetwork()
        assert network.device_count() == 0

        network.add_device(Device(device_id="d1", device_type=DT.LIGHT, name="Light"))
        assert network.device_count() == 1
