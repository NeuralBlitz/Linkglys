#!/usr/bin/env python3
"""
Edge Deployment Manager for NeuralBlitz
Manages deployment of models to edge devices
"""

import os
import json
import time
import logging
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import subprocess

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("EdgeDeployment")


class DeploymentStatus(Enum):
    """Deployment status states"""

    PENDING = "pending"
    DEPLOYING = "deploying"
    RUNNING = "running"
    FAILED = "failed"
    STOPPED = "stopped"


class DeviceType(Enum):
    """Supported edge device types"""

    RASPBERRY_PI = "raspberry_pi"
    CORAL_TPU = "coral_tpu"
    JETSON_NANO = "jetson_nano"
    JETSON_XAVIER = "jetson_xavier"
    GENERIC_ARM64 = "generic_arm64"


@dataclass
class ModelMetadata:
    """Model metadata for deployment"""

    name: str
    version: str
    model_path: str
    model_type: str
    input_shape: List[int]
    output_shape: List[int]
    size_bytes: int
    checksum: str
    created_at: float = field(default_factory=time.time)


@dataclass
class DeploymentConfig:
    """Deployment configuration"""

    device_type: DeviceType
    device_address: str
    device_port: int = 22
    ssh_key: Optional[str] = None
    ssh_user: str = "pi"
    model_path: str = "/home/pi/models"
    runtime_path: str = "/home/pi/neuralblitz"
    environment: Dict[str, str] = field(default_factory=dict)
    autostart: bool = False
    resource_limits: Dict[str, Any] = field(default_factory=dict)


class EdgeDevice(ABC):
    """Abstract base class for edge devices"""

    def __init__(self, config: DeploymentConfig):
        self.config = config
        self.status = DeploymentStatus.PENDING
        self.last_heartbeat = 0.0

    @abstractmethod
    def connect(self) -> bool:
        """Connect to device"""
        pass

    @abstractmethod
    def disconnect(self):
        """Disconnect from device"""
        pass

    @abstractmethod
    def deploy_model(self, model: ModelMetadata) -> bool:
        """Deploy model to device"""
        pass

    @abstractmethod
    def start_inference(self) -> bool:
        """Start inference service"""
        pass

    @abstractmethod
    def stop_inference(self) -> bool:
        """Stop inference service"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, Any]:
        """Get device status"""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Check device health"""
        pass


class SSHDevice(EdgeDevice):
    """SSH-based edge device implementation"""

    def __init__(self, config: DeploymentConfig):
        super().__init__(config)
        self.ssh_client = None

    def _run_ssh_command(self, command: str) -> tuple:
        """Run SSH command"""
        ssh_cmd = [
            "ssh",
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "BatchMode=yes",
        ]

        if self.config.ssh_key:
            ssh_cmd.extend(["-i", self.config.ssh_key])

        ssh_cmd.append(f"{self.config.ssh_user}@{self.config.device_address}")

        ssh_cmd.extend(["--", command])

        try:
            result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=30)
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Command timeout"
        except Exception as e:
            return -1, "", str(e)

    def connect(self) -> bool:
        """Connect to device"""
        code, stdout, stderr = self._run_ssh_command("echo connected")
        if code == 0:
            self.status = DeploymentStatus.RUNNING
            return True
        return False

    def disconnect(self):
        """Disconnect from device"""
        self.status = DeploymentStatus.STOPPED

    def deploy_model(self, model: ModelMetadata) -> bool:
        """Deploy model to device via SCP"""
        self.status = DeploymentStatus.DEPLOYING

        scp_cmd = ["scp", "-o", "StrictHostKeyChecking=no"]

        if self.config.ssh_key:
            scp_cmd.extend(["-i", self.config.ssh_key])

        scp_cmd.extend(
            [
                model.model_path,
                f"{self.config.ssh_user}@{self.config.device_address}:{self.config.model_path}/",
            ]
        )

        try:
            result = subprocess.run(scp_cmd, capture_output=True, timeout=300)
            if result.returncode == 0:
                self.status = DeploymentStatus.RUNNING
                return True
        except Exception as e:
            logger.error(f"Model deployment failed: {e}")

        self.status = DeploymentStatus.FAILED
        return False

    def start_inference(self) -> bool:
        """Start inference service"""
        cmd = f"cd {self.config.runtime_path} && python3 -m inference --model {self.config.model_path} &"
        code, stdout, stderr = self._run_ssh_command(cmd)
        return code == 0

    def stop_inference(self) -> bool:
        """Stop inference service"""
        cmd = "pkill -f 'python3 -m inference'"
        code, stdout, stderr = self._run_ssh_command(cmd)
        return code == 0

    def get_status(self) -> Dict[str, Any]:
        """Get device status"""
        cmd = (
            "uptime && free -m && vcgencmd measure_temp 2>/dev/null || echo 'temp: N/A'"
        )
        code, stdout, stderr = self._run_ssh_command(cmd)

        return {
            "status": self.status.value,
            "device_address": self.config.device_address,
            "device_type": self.config.device_type.value,
            "uptime_info": stdout if code == 0 else "N/A",
            "last_heartbeat": self.last_heartbeat,
        }

    def health_check(self) -> bool:
        """Check device health"""
        code, _, _ = self._run_ssh_command("echo ok")
        if code == 0:
            self.last_heartbeat = time.time()
            return True
        return False


class DeploymentManager:
    """Manages deployments to multiple edge devices"""

    def __init__(self, config_path: Optional[str] = None):
        self.devices: Dict[str, EdgeDevice] = {}
        self.deployments: Dict[str, ModelMetadata] = {}
        self.config_path = config_path

    def register_device(self, device_id: str, device: EdgeDevice):
        """Register an edge device"""
        self.devices[device_id] = device
        logger.info(f"Registered device: {device_id}")

    def unregister_device(self, device_id: str):
        """Unregister an edge device"""
        if device_id in self.devices:
            del self.devices[device_id]
            logger.info(f"Unregistered device: {device_id}")

    def add_device(self, device_id: str, config: DeploymentConfig) -> bool:
        """Add and connect a new device"""
        device = SSHDevice(config)
        if device.connect():
            self.register_device(device_id, device)
            return True
        return False

    def deploy_to_device(self, device_id: str, model: ModelMetadata) -> bool:
        """Deploy model to specific device"""
        if device_id not in self.devices:
            logger.error(f"Device not found: {device_id}")
            return False

        device = self.devices[device_id]

        if not device.health_check():
            logger.error(f"Device health check failed: {device_id}")
            return False

        success = device.deploy_model(model)

        if success:
            self.deployments[device_id] = model

        return success

    def deploy_to_all(self, model: ModelMetadata) -> Dict[str, bool]:
        """Deploy model to all connected devices"""
        results = {}
        for device_id in self.devices:
            results[device_id] = self.deploy_to_device(device_id, model)
        return results

    def start_all_inferences(self) -> Dict[str, bool]:
        """Start inference on all devices"""
        results = {}
        for device_id, device in self.devices.items():
            results[device_id] = device.start_inference()
        return results

    def stop_all_inferences(self) -> Dict[str, bool]:
        """Stop inference on all devices"""
        results = {}
        for device_id, device in self.devices.items():
            results[device_id] = device.stop_inference()
        return results

    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all devices"""
        status = {}
        for device_id, device in self.devices.items():
            status[device_id] = device.get_status()
        return status

    def health_check_all(self) -> Dict[str, bool]:
        """Health check all devices"""
        results = {}
        for device_id, device in self.devices.items():
            results[device_id] = device.health_check()
        return results

    def save_config(self, path: str):
        """Save deployment configuration"""
        config_data = {
            "devices": [
                {
                    "id": device_id,
                    "config": {
                        "device_type": device.config.device_type.value,
                        "device_address": device.config.device_address,
                        "device_port": device.config.device_port,
                        "ssh_user": device.config.ssh_user,
                        "model_path": device.config.model_path,
                        "runtime_path": device.config.runtime_path,
                    },
                }
                for device_id, device in self.devices.items()
            ]
        }

        with open(path, "w") as f:
            json.dump(config_data, f, indent=2)

    def load_config(self, path: str):
        """Load deployment configuration"""
        with open(path, "r") as f:
            config_data = json.load(f)

        for device_config in config_data.get("devices", []):
            config = DeploymentConfig(
                device_type=DeviceType(device_config["config"]["device_type"]),
                device_address=device_config["config"]["device_address"],
                device_port=device_config["config"]["device_port"],
                ssh_user=device_config["config"]["ssh_user"],
                model_path=device_config["config"]["model_path"],
                runtime_path=device_config["config"]["runtime_path"],
            )
            self.add_device(device_config["id"], config)


def create_model_metadata(model_path: str, name: str, version: str) -> ModelMetadata:
    """Create model metadata from file"""
    path = Path(model_path)

    with open(model_path, "rb") as f:
        checksum = hashlib.sha256(f.read()).hexdigest()

    return ModelMetadata(
        name=name,
        version=version,
        model_path=model_path,
        model_type=path.suffix[1:],
        input_shape=[1, 3, 224, 224],
        output_shape=[1, 1000],
        size_bytes=path.stat().st_size,
        checksum=checksum,
    )


if __name__ == "__main__":
    import sys

    manager = DeploymentManager()

    if len(sys.argv) > 1:
        config_file = sys.argv[1]
        if os.path.exists(config_file):
            manager.load_config(config_file)
            print(f"Loaded config from {config_file}")

    print(f"Deployment manager initialized with {len(manager.devices)} devices")
