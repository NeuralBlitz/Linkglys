# Raspberry Pi — Lightweight Edge Inference

**Platform:** Raspberry Pi 4 (4GB+)  
**Framework:** ONNX Runtime, TensorFlow Lite  
**Power:** 5W

---

## Overview

The Raspberry Pi provides **lightweight AI inference** for IoT and edge applications. While less powerful than Jetson or Coral, it's cost-effective and widely available for simple classification and detection tasks.

---

## Quick Start

### Hardware Setup

1. Flash Raspberry Pi OS to microSD card
2. Boot and connect via SSH: `ssh pi@<ip>`
3. Recommended: 4GB+ RAM model

### Software Setup

```bash
sudo apt-get update
sudo apt-get install python3-pip
pip3 install onnxruntime tflite-runtime
```

### Deploy

```bash
# Run deployment script
bash deploy_raspberry_pi.sh

# Or manually
python3 -c "
import onnxruntime as ort
session = ort.InferenceSession('model.onnx')
print('Model loaded successfully')
"
```

---

## Model Conversion

```bash
# Convert TensorFlow to ONNX
python -m tf2onnx.convert \
    --saved-model ./model \
    --output model.onnx \
    --opset 13

# Quantize for Pi (reduces memory)
python -c "
import onnxruntime.quantization as quant
quant.quantize_dynamic('model.onnx', 'model_quant.onnx')
"
```

---

## Performance

| Model | Precision | Latency | FPS | Power |
|-------|-----------|---------|-----|-------|
| MobileNet V2 | FP32 | 120ms | 8 | 5W |
| MobileNet V2 | INT8 | 45ms | 22 | 5W |
| SqueezeNet | FP32 | 80ms | 12 | 5W |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Out of memory** | Use quantized models or increase swap: `sudo dphys-swapfile swapfile_setup` |
| **Slow inference** | Use ONNX Runtime with `--execution-mode parallel` |
| **Import errors** | Ensure correct Python version: `python3 --version` |
