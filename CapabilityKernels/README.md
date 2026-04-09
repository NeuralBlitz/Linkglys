# Capability Kernels — Audio Processing

**Location:** `/home/runner/workspace/CapabilityKernels/`  
**Language:** Python 3.11+  
**Version:** 1.0.0

---

## Overview

This directory contains **audio processing Capability Kernels** — specialized modules for real-time audio analysis, sound classification, and speech recognition. Each kernel follows the CK Contract Schema with JSON metadata descriptors.

---

## Kernels

### 1. Real-Time Analyzer (`realtime_analyzer_ck.py` / `.json`)

**Purpose:** Real-time audio feature extraction and analysis.

**Features:**
- Real-time FFT-based feature extraction
- RMS energy, peak amplitude, zero-crossing rate
- Spectral centroid, rolloff, bandwidth, flatness
- MFCC (Mel-frequency cepstral coefficients)
- Chroma features
- Tempo detection
- PII (Personally Identifiable Information) detection in audio

**Metadata:** `realtime_analyzer_ck.json` defines the kernel contract with inputs, outputs, and capability descriptions.

### 2. Sound Classifier (`sound_classifier_ck.py` / `.json`)

**Purpose:** Heuristic-based sound classification.

**Features:**
- Multi-class sound classification
- Environmental sound detection
- Music vs speech discrimination
- Noise level assessment
- Event detection (claps, knocks, etc.)

**Metadata:** `sound_classifier_ck.json` — classification schema and label mappings.

### 3. Speech Recognizer (`speech_recognizer_ck.py` / `.json`)

**Purpose:** Speech recognition and transcription.

**Features:**
- Speech activity detection
- Language identification
- Phoneme extraction
- Word-level transcription
- Confidence scoring
- Speaker diarization (basic)

**Metadata:** `speech_recognizer_ck.json` — recognition schema and language support.

---

## Quick Start

### Install Dependencies

```bash
# Audio processing dependencies
pip install librosa numpy scipy soundfile
```

### Use the Real-Time Analyzer

```python
from CapabilityKernels.realtime_analyzer_ck import RealTimeAnalyzer

analyzer = RealTimeAnalyzer()

# Analyze audio file
features = analyzer.analyze_file("audio.wav")
print(f"RMS Energy: {features.rms}")
print(f"Spectral Centroid: {features.spectral_centroid}")
print(f"MFCCs: {features.mfccs.shape}")

# Analyze audio chunk in real-time
chunk = analyzer.process_chunk(audio_data, sample_rate=16000)
print(f"Features extracted: {list(chunk.keys())}")
```

### Use the Sound Classifier

```python
from CapabilityKernels.sound_classifier_ck import SoundClassifier

classifier = SoundClassifier()

# Classify sound
result = classifier.classify(audio_chunk)
print(f"Sound type: {result.label}")
print(f"Confidence: {result.confidence}")
```

---

## CK Contract Schema

Each kernel follows the standard contract:

```json
{
  "name": "kernel_name",
  "version": "1.0.0",
  "description": "Audio processing kernel",
  "inputs": [
    {"name": "audio_data", "type": "numpy.ndarray", "shape": [null, 1]}
  ],
  "outputs": [
    {"name": "features", "type": "dict"}
  ],
  "capabilities": ["realtime_analysis", "feature_extraction"],
  "dependencies": ["librosa", "numpy", "scipy"]
}
```

---

## Integration with Voice Interface

These kernels integrate with the voice interface system:

```
voice_interface/
    │
    ├──→ SpeechToText (OpenAI Whisper)
    │       └──→ speech_recognizer_ck (local fallback)
    │
    └──→ VoiceCommandParser
            └──→ sound_classifier_ck (command detection)
```

---

## Testing

```bash
# Test audio kernels
python -c "
from CapabilityKernels.realtime_analyzer_ck import RealTimeAnalyzer
analyzer = RealTimeAnalyzer()
print('RealTimeAnalyzer loaded successfully')
"

# Test with sample audio
python -c "
import numpy as np
from CapabilityKernels.realtime_analyzer_ck import RealTimeAnalyzer
analyzer = RealTimeAnalyzer()
# Generate test audio (1 second, 16kHz)
test_audio = np.random.randn(16000)
features = analyzer.process_chunk(test_audio, sample_rate=16000)
print(f'Features: {len(features)} extracted')
"
```

---

## Related Documentation

- [src/capabilities/README.md](src/capabilities/README.md) — Other capability kernels
- [voice_interface/README.md](voice_interface/README.md) — Voice interface integration
- [Audio Processing](src/audio_processing.py) — Main audio processing module
