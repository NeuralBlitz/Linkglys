# Edge Deployment Manager — Unified Orchestration

**Location:** `edge_computing/deployment/`  
**File:** `edge_deployment.py`

---

## Overview

The Edge Deployment Manager provides a **unified interface** for deploying and managing AI models across all supported edge platforms (Jetson Nano, Coral TPU, Raspberry Pi).

---

## Features

- **Platform Abstraction** — Single API for all edge devices
- **Model Deployment** — Push models to remote devices
- **Inference Orchestration** — Run inference on edge devices
- **Health Monitoring** — Check device status, temperature, memory
- **Auto-Scaling** — Distribute load across multiple devices

---

## Usage

```python
from edge_deployment import EdgeDeploymentManager

# Initialize manager
manager = EdgeDeploymentManager()

# Register edge devices
manager.register_device(
    platform="jetson_nano",
    address="192.168.1.100",
    config={"power_mode": "10W"}
)

manager.register_device(
    platform="coral_tpu",
    address="192.168.1.101",
    config={}
)

# Deploy model
deployment = manager.deploy(
    device_id="jetson-1",
    model_path="model.trt",
    version="1.0.0"
)

# Run inference
result = manager.inference(
    device_id="jetson-1",
    input_data=image_bytes
)

# Get health status
health = manager.get_health("jetson-1")
print(f"Status: {health.status}, Temp: {health.temperature}°C")
```

---

## Architecture

```
┌─────────────────────────────────────┐
│      EdgeDeploymentManager           │
│  ┌──────────┐ ┌──────────┐          │
│  │ Jetson   │ │  Coral   │          │
│  │ Adapter  │ │ Adapter  │          │
│  └──────────┘ └──────────┘          │
│  ┌──────────┐ ┌──────────┐          │
│  │ Pi       │ │ Monitor  │          │
│  │ Adapter  │ │ & Health │          │
│  └──────────┘ └──────────┘          │
└─────────────────────────────────────┘
```

---

## Device Adapters

| Adapter | Platform | Communication |
|---------|----------|---------------|
| `JetsonAdapter` | NVIDIA Jetson Nano | SSH + TensorRT API |
| `CoralAdapter` | Google Coral TPU | SSH + TFLite Runtime |
| `PiAdapter` | Raspberry Pi | SSH + ONNX Runtime |

---

## Related Documentation

- [edge_computing/README.md](../README.md) — Edge computing overview
- [ARCHITECTURE.md](../../ARCHITECTURE.md) — System architecture
- [Edge Computing Report](../../docs/EDGE_COMPUTING_REPORT.md) — Detailed report
