# Google Coral TPU — Edge Inference

**Platform:** Google Coral USB Accelerator / Dev Board  
**Framework:** TensorFlow Lite Edge TPU  
**Power:** 2W

---

## Overview

The Google Coral TPU provides **ultra-low-latency INT8 inference** using Google's Edge TPU ASIC. Ideal for image classification, object detection, and semantic segmentation at the edge.

---

## Quick Start

### Hardware Setup

1. Connect Coral USB Accelerator to USB 3.0 port
2. Verify detection: `lsusb | grep 1a6e`
3. Install Edge TPU runtime from [coral.ai](https://coral.ai/docs/accelerator/get-started)

### Software Setup

```bash
# Install TFLite runtime
pip3 install tflite-runtime

# Or full TensorFlow for development
pip3 install tflite-support
```

### Run Inference

```bash
python3 ../../coral_tpu_inference.py \
  --model mobilenet_v2_edgetpu.tflite \
  --labelmap labels.txt \
  --input image.jpg \
  --top_k 5
```

---

## Model Conversion

```bash
# Install compiler
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo "deb https://packages.cloud.google.com/apt coral-edgetpu-stable main" | sudo tee /etc/apt/sources.list.d/coral-edgetpu.list
sudo apt-get update
sudo apt-get install edgetpu-compiler

# Compile model
edgetpu_compiler model.tflite
# Output: model_edgetpu.tflite
```

---

## Performance

| Model | Latency | Power | FPS |
|-------|---------|-------|-----|
| MobileNet V2 | 4ms | 2W | 250 |
| Inception V3 | 10ms | 2W | 100 |
| SSD MobileNet | 15ms | 2W | 67 |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Device not found** | `lsusb | grep 1a6e` — check USB connection |
| **Permission denied** | Add udev rule: `sudo usermod -aG plugdev $USER` |
| **Slow inference** | Verify model is compiled for Edge TPU (has `_edgetpu.tflite` suffix) |
