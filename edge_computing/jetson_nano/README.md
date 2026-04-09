# NVIDIA Jetson Nano — GPU-Accelerated Edge

**Platform:** NVIDIA Jetson Nano (4GB)  
**Framework:** TensorRT, CUDA, PyTorch  
**Power:** 5W/10W

---

## Overview

The NVIDIA Jetson Nano provides **GPU-accelerated AI inference** at the edge using TensorRT optimization and CUDA acceleration. Best for computer vision, object detection, and multi-stream processing.

---

## Quick Start

### Hardware Setup

1. Flash JetPack SDK to microSD card
2. Boot Jetson Nano and complete initial setup
3. Connect via SSH: `ssh jetson@<ip>`

### Software Setup

```bash
# JetPack includes CUDA, cuDNN, TensorRT
# Verify installation
python3 -c "import tensorrt; print(tensorrt.__version__)"
```

### Run Inference

```bash
python3 ../../jetson_nano_inference.py \
  --model resnet50.trt \
  --input image.jpg \
  --precision fp16
```

---

## Model Conversion to TensorRT

```bash
# From ONNX
trtexec --onnx=model.onnx \
        --saveEngine=model.trt \
        --fp16 \
        --workspace=4096

# Verify engine
trtexec --loadEngine=model.trt --batch=1
```

---

## Performance

| Model | Precision | Latency | FPS | Power |
|-------|-----------|---------|-----|-------|
| ResNet-50 | FP16 | 15ms | 67 | 10W |
| YOLOv5s | FP16 | 25ms | 40 | 10W |
| MobileNet V2 | INT8 | 5ms | 200 | 5W |

---

## Power Modes

```bash
# 5W mode (2 cores)
sudo nvpmodel -m 1

# 10W mode (4 cores + GPU)
sudo nvpmodel -m 0

# Check current mode
sudo nvpmodel -q
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Out of memory** | Reduce batch size or model precision |
| **Thermal throttling** | Add heatsink/fan, check `tegrastats` |
| **TensorRT build fails** | Ensure JetPack version matches TensorRT version |
