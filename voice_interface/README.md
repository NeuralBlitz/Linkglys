# Voice Interface — Speech Interaction System

**Location:** `/home/runner/workspace/voice_interface/`  
**Language:** Python 3.11+  
**Version:** 1.0.0

---

## Overview

The Voice Interface provides **natural language voice interaction** for NeuralBlitz, combining OpenAI Whisper for speech-to-text, rule-based and LLM-powered command parsing, and text-to-speech synthesis via pyttsx3 and OpenAI TTS.

---

## Components

| File | Lines | Purpose |
|------|-------|---------|
| `voice_interface.py` | ~500 | Main voice interface system |
| `test_simple.py` | — | Simple tests |
| `examples.py` | — | Usage examples |
| `REPORT.md` | 434 | Technical report |
| `IMPLEMENTATION_SUMMARY.md` | 372 | Implementation details |
| `QUICKSTART.md` | 176 | Quick start guide |
| `requirements.txt` | — | Dependencies |

---

## Architecture

```
┌───────────────────────────────────────────────────┐
│               VoiceInterface                       │
│  ┌──────────────┐ ┌───────────────────┐           │
│  │ SpeechToText │ │VoiceCommandParser │           │
│  │ (Whisper)    │ │(Rule-based + LLM) │           │
│  └──────┬───────┘ └─────────┬─────────┘           │
│         │                   │                      │
│  ┌──────┴───────┐ ┌─────────┴─────────┐           │
│  │  TextToSpeech│ │  Handler Registry  │           │
│  │(pyttsx3+TTS) │ │(command routing)  │           │
│  └──────────────┘ └───────────────────┘           │
└───────────────────────────────────────────────────┘
```

### Key Components

#### 1. SpeechToText
- **Engine:** OpenAI Whisper
- **Features:**
  - Multi-language support
  - Real-time transcription
  - Confidence scoring
  - Noise robustness
  - Chunk-based processing

#### 2. VoiceCommandParser
- **Rule-Based:** Pattern matching for common commands
- **LLM-Powered:** Natural language understanding for complex commands
- **Command Types:**
  - Agent control (create, start, stop, pause)
  - System queries (status, metrics, health)
  - Data operations (train, predict, analyze)
  - Configuration changes

#### 3. TextToSpeech
- **Engines:**
  - **pyttsx3** — Offline, fast, local voices
  - **OpenAI TTS** — High-quality, natural-sounding voices
- **Features:**
  - Voice selection
  - Speed/pitch control
  - SSML support
  - Streaming output

#### 4. VoiceInterface (Orchestrator)
- **Handler Registration** — Register command handlers
- **VoiceCommandType Enum** — Command categorization
- **VoiceCommand Dataclass** — Command representation
- **VoiceConfig** — Configuration management
- **Interactive Session** — Full voice interaction loop

---

## Quick Start

### Install Dependencies

```bash
pip install openai-whisper pyttsx3 openai numpy soundfile
```

### Basic Usage

```python
from voice_interface.voice_interface import VoiceInterface

# Initialize
vi = VoiceInterface()

# Start interactive session
vi.start_session()

# Or process single command
command = vi.process_voice("Start agent research")
result = vi.execute_command(command)
print(f"Result: {result}")
```

### Voice Command Examples

```python
# Agent control
"Create a new research agent"
"Start the analysis pipeline"
"Pause agent agent-1"

# System queries
"What's the system status?"
"Show me agent metrics"
"Is the system healthy?"

# Data operations
"Train a new model with the latest data"
"Run anomaly detection on the metrics"
"Analyze the current dataset"
```

---

## Configuration

```python
from voice_interface.voice_interface import VoiceConfig

config = VoiceConfig(
    # Speech-to-Text
    stt_engine="whisper",        # whisper, local_model
    whisper_model="base",        # tiny, base, small, medium, large
    stt_language="en",            # Language code
    
    # Text-to-Speech
    tts_engine="pyttsx3",        # pyttsx3, openai
    tts_voice="default",         # Voice name
    tts_rate=150,                 # Words per minute
    
    # Command Processing
    command_engine="hybrid",     # rule-based, llm, hybrid
    confidence_threshold=0.7,     # Minimum confidence
    
    # Audio
    sample_rate=16000,           # Audio sample rate
    chunk_duration=5.0,          # Chunk duration for streaming
)
```

---

## Command Types

```python
from enum import Enum

class VoiceCommandType(Enum):
    AGENT_CREATE = "agent_create"
    AGENT_START = "agent_start"
    AGENT_STOP = "agent_stop"
    AGENT_PAUSE = "agent_pause"
    SYSTEM_STATUS = "system_status"
    SYSTEM_HEALTH = "system_health"
    METRICS_QUERY = "metrics_query"
    MODEL_TRAIN = "model_train"
    MODEL_PREDICT = "model_predict"
    DATA_ANALYZE = "data_analyze"
    CONFIG_SET = "config_set"
    HELP = "help"
```

---

## Integration with NeuralBlitz

The voice interface integrates with the main API:

```
Voice Command → SpeechToText → CommandParser → API Call → Response → TextToSpeech
```

**Example flow:**
1. User says: *"Start agent research"*
2. Whisper transcribes audio to text
3. CommandParser identifies `AGENT_START` command with `research` parameter
4. Handler calls `POST /api/v2/agents` via API
5. Response formatted as speech
6. TTS speaks: *"Agent research started successfully"*

---

## Testing

```bash
# Run simple tests
python voice_interface/test_simple.py

# Run examples
python voice_interface/examples.py

# Test module loading
python -c "
from voice_interface.voice_interface import VoiceInterface, VoiceConfig
config = VoiceConfig()
vi = VoiceInterface(config=config)
print(f'Voice interface initialized: {vi.is_ready}')
"
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **Whisper model not found** | Run `whisper --download model_name` first |
| **No audio input** | Check microphone: `arecord -l` (Linux) or `system_profiler SPAudioDataType` (macOS) |
| **pyttsx3 voice not found** | List available: `python -c "import pyttsx3; e=pyttsx3.init(); print(e.getProperty('voices'))"` |
| **OpenAI API key missing** | Set `export OPENAI_API_KEY=sk-...` |
| **Low transcription accuracy** | Use larger Whisper model: `whisper_model="medium"` |

---

## Related Documentation

- [Voice Interface Report](voice_interface/REPORT.md) — Technical report (434 lines)
- [Implementation Summary](voice_interface/IMPLEMENTATION_SUMMARY.md) — Implementation details
- [Quick Start](voice_interface/QUICKSTART.md) — Quick installation guide
- [neuralblitz_slack_bot/README.md](neuralblitz_slack_bot/README.md) — Slack bot (alternative interface)
- [src/README.md](src/README.md) — Main application
