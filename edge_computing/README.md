# Edge Computing — Edge Device Deployments

**Location:** `/home/runner/workspace/edge_computing/`  
**Platforms:** NVIDIA Jetson Nano, Google Coral TPU, Raspberry Pi

---

## Overview

Edge Computing enables **on-device AI inference** for NeuralBlitz, allowing models to run directly on edge hardware for low-latency, privacy-preserving deployments without cloud dependency.

---

## Supported Platforms

| Platform | Device Type | Framework | Best For |
|----------|------------|-----------|----------|
| **NVIDIA Jetson Nano** | GPU-accelerated SBC | TensorRT, CUDA | Computer vision, ML inference |
| **Google Coral TPU** | Edge TPU accelerator | TensorFlow Lite | Image classification, object detection |
| **Raspberry Pi** | ARM single-board computer | ONNX Runtime, TFLite | Lightweight inference, IoT |

---

## Quick Start

### 1. NVIDIA Jetson Nano

**Hardware Requirements:**
- NVIDIA Jetson Nano (4GB recommended)
- microSD card (32GB+)
- Power supply (5V/4A)

**Setup:**
```bash
# Flash JetPack SDK to SD card
# Download from: https://developer.nvidia.com/embedded/jetpack

# SSH to device
ssh jetson@<jetson-ip>

# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip
pip3 install tensorflow tensorrt

# Run inference
python3 edge_computing/jetson_nano_inference.py --model model.trt --input image.jpg
```

**Features:**
- TensorRT optimized models
- CUDA-accelerated inference
- Multi-stream processing
- Power management (5W/10W modes)

### 2. Google Coral TPU

**Hardware Requirements:**
- Google Coral USB Accelerator or Dev Board
- USB 3.0 port
- Linux/macOS host

**Setup:**
```bash
# Install Coral Edge TPU runtime
# Download from: https://coral.ai/docs/accelerator/get-started

# Install Python library
pip3 install tflite-runtime

# Run inference
python3 edge_computing/coral_tpu_inference.py --model model_edgetpu.tflite --input image.jpg
```

**Features:**
- 4 TOPS INT8 inference
- Low power (2W)
- Quantized model support
- USB or PCIe interface

### 3. Raspberry Pi

**Hardware Requirements:**
- Raspberry Pi 4 (4GB+ RAM)
- microSD card (16GB+)
- Power supply (5V/3A USB-C)

**Setup:**
```bash
# Flash Raspberry Pi OS
# Download from: https://www.raspberrypi.com/software/

# SSH to device
ssh pi@<pi-ip>

# Install dependencies
sudo apt-get update
sudo apt-get install python3-pip
pip3 install onnxruntime

# Deploy and run
bash edge_computing/raspberry_pi/deploy_raspberry_pi.sh
```

---

## Unified Edge Deployment Manager

`deployment/edge_deployment.py` provides a unified interface for deploying models across all edge platforms:

```python
from edge_computing.deployment.edge_deployment import EdgeDeploymentManager

manager = EdgeDeploymentManager()

# Deploy model to edge device
deployment = manager.deploy(
    platform="jetson_nano",  # or "coral_tpu", "raspberry_pi"
    model_path="model.trt",
    device_address="192.168.1.100",
    config={"power_mode": "10W"}
)

# Get inference results
result = manager.inference(
    deployment_id=deployment.id,
    input_data=image_bytes
)

# Monitor device health
health = manager.get_health(deployment.id)
print(f"Device status: {health.status}")
print(f"Temperature: {health.temperature}°C")
print(f"Memory usage: {health.memory_usage}%")
```

---

## Performance Benchmarks

| Platform | Model | Latency | Throughput | Power |
|----------|-------|---------|------------|-------|
| **Jetson Nano** | ResNet-50 (FP16) | 15ms | 67 FPS | 10W |
| **Coral TPU** | MobileNet V2 (INT8) | 4ms | 250 FPS | 2W |
| **Raspberry Pi** | MobileNet V2 (FP32) | 120ms | 8 FPS | 5W |

---

## Model Conversion

### TensorRT (Jetson Nano)

```bash
# Convert ONNX to TensorRT
trtexec --onnx=model.onnx \
        --saveEngine=model.trt \
        --fp16 \
        --workspace=4096
```

### Edge TPU (Coral TPU)

```bash
# Convert TFLite to Edge TPU
edgetpu_compiler model.tflite
# Output: model_edgetpu.tflite
```

### ONNX Runtime (Raspberry Pi)

```bash
# Convert model to ONNX
python -m tf2onnx.convert \
    --saved-model ./model \
    --output model.onnx
```

---

## Testing

```bash
# Test module loading
python -c "
from edge_computing.deployment.edge_deployment import EdgeDeploymentManager
manager = EdgeDeploymentManager()
print(f'Supported platforms: {manager.supported_platforms}')
"

# Test on specific platform
python edge_computing/jetson_nano_inference.py --help
python edge_computing/coral_tpu_inference.py --help
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Jetson not booting** | Re-flash JetPack, check SD card |
| **Coral TPU not detected** | `lsusb | grep 1a6e` — should show Google device |
| **Raspberry Pi OOM** | Reduce model size or use swap: `sudo fallocate -l 1G /swapfile` |
| **Slow inference** | Check GPU/TPU utilization: `tegrastats` (Jetson), `dmesg` (Coral) |
| **Model conversion failed** | Verify model compatibility with target platform |

---

## Related Documentation

- [Edge Computing Report](docs/EDGE_COMPUTING_REPORT.md) — Comprehensive edge computing report (2,080 lines)
- [src/README.md](src/README.md) — Main application
- [ARCHITECTURE.md](ARCHITECTURE.md) — Deployment architecture
