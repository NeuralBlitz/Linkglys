# IoT Device Mesh Integration System

A comprehensive, production-ready IoT device mesh system with MQTT messaging, automatic device discovery (mDNS + SSDP), rules-based automation engine, and SQLite persistence. Built by NeuralBlitz Systems for managing heterogeneous IoT device fleets at scale.

## Overview

The IoT Mesh System provides a complete infrastructure for connecting, discovering, and automating IoT devices across a local mesh network. It consists of four core modules that work independently or as a unified system:

- **MQTT Broker** — Pub/sub message routing with QoS levels, retained messages, and wildcard subscriptions
- **Device Discovery** — Automatic device discovery via mDNS/Zeroconf and SSDP protocols
- **Automation Engine** — Rules-based automation with condition evaluation and action execution
- **Database Manager** — SQLite persistence for device state, events, and automation history

| Component | File | Lines |
|-----------|------|-------|
| Core system | `iot_mesh_core.py` | ~1,321 |
| Unified mesh | `iot_mesh_unified.py` | ~600 |
| MQTT broker | `mqtt_broker.py` | — |
| Device discovery | `device_discovery.py` | — |
| Automation engine | `automation_engine.py` | — |
| Database layer | `database.py` | — |

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    IoT Mesh Unified System                      │
├─────────────────────────────────────────────────────────────────┤
│  ┌───────────┐  ┌───────────┐  ┌──────────────┐  ┌──────────┐ │
│  │  MQTT     │  │  Device   │  │  Automation  │  │ Database │ │
│  │  Broker   │  │ Discovery │  │   Engine     │  │ Manager  │ │
│  └─────┬─────┘  └─────┬─────┘  └──────┬───────┘  └────┬─────┘ │
│        └──────────────┴───────────────┴───────────────┘        │
│                         Device Registry & State Cache           │
└─────────────────────────────────────────────────────────────────┘
```

## Quick Start

### Prerequisites

- Python 3.11+
- Docker & Docker Compose (for containerized deployment)

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Or with Docker Compose
docker-compose up -d
```

### Minimal Example

```python
from iot_mesh_core import IoTMeshCore

# Initialize the unified system
mesh = IoTMeshCore(
    mqtt_host="localhost",
    mqtt_port=1883,
    discovery_enabled=True,
    automation_enabled=True,
)

# Start all subsystems
mesh.start()

# Register a device
mesh.registry.register_device(
    device_id="light_living_room",
    device_type="smart_light",
    capabilities=["on_off", "brightness", "color"],
)

# Create an automation rule
mesh.automation.add_rule(
    rule_id="lights_on_at_dusk",
    trigger={"type": "time", "value": "18:00"},
    condition={"type": "device_state", "device_id": "light_living_room", "state": "off"},
    actions=[{"type": "device_command", "device_id": "light_living_room", "command": "turn_on"}],
)

# Shut down
mesh.stop()
```

### Docker Compose

The included `docker-compose.yml` spins up:

| Service | Container | Ports | Description |
|---------|-----------|-------|-------------|
| Mosquitto | `iot-mqtt-broker` | 1883, 9001 | MQTT broker with WebSocket support |
| IoT Mesh Core | `iot-mesh-core` | 8000 | Core mesh service (auto-connects to Mosquitto) |
| Dashboard | `iot-dashboard` | 8080 | Web-based device monitoring UI |
| Device Simulator | `iot-device-simulator` | — | Simulated device fleet for testing |

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f iot-mesh-core

# Stop all services
docker-compose down
```

## Architecture & Components

### Core Data Models

**`DeviceType`** (Enum) — Supported device categories:
- `SENSOR`, `ACTUATOR`, `CONTROLLER`, `GATEWAY`, `SMART_LIGHT`, `SMART_THERMOSTAT`,
  `SMART_LOCK`, `SMART_CAMERA`, `SMART_SPEAKER`, `SMART_PLUG`, `WEARABLE`, `HUB`

**`DeviceState`** (Enum) — Device lifecycle states:
- `OFFLINE`, `ONLINE`, `CONNECTING`, `ERROR`, `MAINTENANCE`, `DECOMMISSIONED`

**`IoTDevice`** (Pydantic Model) — Full device representation with:
- Device metadata (ID, name, type, manufacturer, model, firmware)
- Network info (IP, MAC, port, protocol)
- Capabilities list and configuration
- Health monitoring (last_seen, uptime, battery_level)

### MQTT Broker Manager (`mqtt_broker.py`)

Full-featured MQTT client manager with:
- **QoS Levels**: AT_MOST_ONCE (0), AT_LEAST_ONCE (1), EXACTLY_ONCE (2)
- **Wildcard subscriptions**: Single-level (`+`) and multi-level (`#`)
- **Retained messages**: Last-known-value persistence
- **Message history**: Configurable history buffer

**Topic Convention:**

| Topic Pattern | Description |
|---------------|-------------|
| `devices/{device_id}/state` | Device state updates |
| `devices/{device_id}/command` | Device commands |
| `devices/{device_id}/telemetry` | Sensor telemetry |
| `devices/{device_id}/event` | Device events |
| `automation/{automation_id}/trigger` | Automation triggers |
| `scenes/{scene_id}/activate` | Scene activation |

### Device Discovery (`device_discovery.py`)

Automatic network discovery via two protocols:

- **mDNS/Zeroconf**: Uses `zeroconf` library for local service discovery
- **SSDP**: Simple Service Discovery Protocol (UPnP-compatible devices)

Discovered devices are automatically registered in the DeviceRegistry with metadata including IP, port, service type, and TXT records.

### Smart Home Automation (`automation_engine.py`)

Rules-based engine with:

- **Trigger types**: Time-based, device state, sensor threshold, event, cron schedule
- **Condition evaluation**: AND/OR/NOT logic with threshold comparisons
- **Action types**: Device commands, scene activation, notifications, webhooks, rule chaining
- **Execution modes**: Sequential or parallel action execution
- **Rate limiting**: Prevents rule thrashing with configurable cooldowns

### Device Registry with mDNS + SSDP

Central registry maintaining:
- Live device inventory with full metadata
- State cache with last-known values
- Capability indexing for fast lookups
- Health monitoring (heartbeat tracking, stale device detection)

### Database Layer (`database.py`)

SQLite-based persistence with:
- Device registry persistence and restore
- Event logging with configurable retention
- Automation history tracking
- Telemetry data storage
- Backup and restore utilities

## Features

- **Unified system architecture** — Single entry point (`iot_mesh_unified.py`) coordinating all subsystems
- **Multi-protocol device discovery** — mDNS + SSDP with automatic registration
- **Full MQTT pub/sub** — QoS levels, retained messages, wildcard subscriptions
- **Rules-based automation** — Time, state, threshold, event, and cron triggers
- **SQLite persistence** — Device state, events, telemetry, automation history
- **Docker-ready** — Production Docker Compose with Mosquitto, core service, dashboard, and simulator
- **Health monitoring** — Per-device health tracking with heartbeat and uptime metrics
- **Type-safe models** — Pydantic models with full validation
- **Structured logging** — Structured JSON logs via `structlog`
- **Security** — JWT authentication, TLS support, cryptography utilities

## API / Usage Examples

### Publishing Device State

```python
from mqtt_broker import MQTTClientManager, QoSLevel

mqtt = MQTTClientManager("localhost", 1883)
mqtt.start()

mqtt.publish_device_state("light_living_room", {
    "state": "on",
    "brightness": 75,
    "color": "warm_white",
})
```

### Subscribing to Topics

```python
def on_message(topic, payload):
    print(f"Received on {topic}: {payload}")

mqtt.subscribe("devices/+/state", callback=on_message)
mqtt.subscribe("devices/#", callback=on_message)  # All device topics
```

### Creating Automation Rules

```python
# Turn on lights when motion is detected
mesh.automation.add_rule(
    rule_id="motion_lights",
    trigger={"type": "event", "event_type": "motion_detected"},
    condition={"type": "device_state", "device_id": "light_hallway", "state": "off"},
    actions=[
        {"type": "device_command", "device_id": "light_hallway", "command": "turn_on"},
        {"type": "notification", "message": "Motion detected - lights turned on"},
    ],
)

# Temperature-based thermostat control
mesh.automation.add_rule(
    rule_id="temp_control",
    trigger={"type": "sensor", "device_id": "temp_sensor", "threshold": {"operator": ">", "value": 25}},
    actions=[
        {"type": "device_command", "device_id": "thermostat_main", "command": "set_temperature", "params": {"target": 22}},
    ],
)
```

### Querying Devices

```python
# Get all online devices
online_devices = mesh.registry.get_devices_by_state(DeviceState.ONLINE)

# Get devices by type
lights = mesh.registry.get_devices_by_type(DeviceType.SMART_LIGHT)

# Get devices with a specific capability
dimmable = mesh.registry.get_devices_by_capability("brightness")
```

## Testing

```bash
# Run all tests
pytest test_iot_mesh.py -v

# Run with coverage
pytest test_iot_mesh.py --cov=iot_mesh_core --cov-report=html

# Run specific test category
pytest test_iot_mesh.py -v -k mqtt
pytest test_iot_mesh.py -v -k discovery
pytest test_iot_mesh.py -v -k automation
```

The test suite (`test_iot_mesh.py`) covers:
- MQTT broker client management and message routing
- Device discovery via mDNS and SSDP
- Automation rule creation, evaluation, and execution
- Database persistence and restore
- Unified system integration

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `MQTT_HOST` | `localhost` | MQTT broker hostname |
| `MQTT_PORT` | `1883` | MQTT broker port |
| `LOG_LEVEL` | `INFO` | Logging verbosity |
| `DISCOVERY_ENABLED` | `true` | Enable device discovery |
| `AUTOMATION_ENABLED` | `true` | Enable automation engine |

### Mosquitto Configuration

See `config/mosquitto.conf` for MQTT broker settings including:
- Listener ports (1883 TCP, 9001 WebSocket)
- Authentication and ACL rules
- Persistence settings
- Logging configuration

## Related Documentation

- [IOT_MESH_REPORT.md](./IOT_MESH_REPORT.md) — Full structured report with architecture details, code examples, and API reference
- [docker-compose.yml](./docker-compose.yml) — Docker Compose orchestration configuration
- [Dockerfile](./Dockerfile) — Container image definition
- [requirements.txt](./requirements.txt) — Python dependencies
