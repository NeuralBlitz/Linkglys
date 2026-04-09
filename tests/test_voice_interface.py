"""Tests for voice_interface/voice_interface.py - Voice interface system."""

import pytest
from unittest.mock import patch, MagicMock
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "voice_interface"))


@pytest.fixture
def voice_module():
    """Import voice interface module."""
    if "voice_interface" in sys.modules:
        del sys.modules["voice_interface"]

    from voice_interface import (
        VoiceCommandType,
        VoiceCommand,
        VoiceConfig,
    )
    return {
        "VoiceCommandType": VoiceCommandType,
        "VoiceCommand": VoiceCommand,
        "VoiceConfig": VoiceConfig,
    }


class TestVoiceCommandType:
    """Test VoiceCommandType enum."""

    def test_command_types_exist(self, voice_module):
        """Test all expected command types exist."""
        VCT = voice_module["VoiceCommandType"]
        assert VCT.GREETING.value == "greeting"
        assert VCT.QUESTION.value == "question"
        assert VCT.ACTION.value == "action"
        assert VCT.NAVIGATION.value == "navigation"
        assert VCT.SYSTEM.value == "system"
        assert VCT.UNKNOWN.value == "unknown"


class TestVoiceCommand:
    """Test VoiceCommand dataclass."""

    def test_voice_command_creation(self, voice_module):
        """Test VoiceCommand creation."""
        VC = voice_module["VoiceCommand"]
        VCT = voice_module["VoiceCommandType"]

        cmd = VC(
            raw_text="Hello",
            command_type=VCT.GREETING,
            intent="greet_user",
            entities={"user": "test"},
            confidence=0.9,
        )

        assert cmd.raw_text == "Hello"
        assert cmd.command_type == VCT.GREETING
        assert cmd.intent == "greet_user"
        assert cmd.confidence == 0.9

    def test_voice_command_to_dict(self, voice_module):
        """Test VoiceCommand serialization."""
        VC = voice_module["VoiceCommand"]
        VCT = voice_module["VoiceCommandType"]

        cmd = VC(
            raw_text="Play music",
            command_type=VCT.ACTION,
            intent="play_music",
            confidence=0.85,
        )

        result = cmd.to_dict()
        assert isinstance(result, dict)
        assert result["raw_text"] == "Play music"
        assert result["command_type"] == "action"
        assert result["intent"] == "play_music"
        assert result["confidence"] == 0.85
        assert "timestamp" in result
        assert isinstance(result["timestamp"], float)

    def test_voice_command_default_entities(self, voice_module):
        """Test VoiceCommand with default entities."""
        VC = voice_module["VoiceCommand"]
        VCT = voice_module["VoiceCommandType"]

        cmd = VC(
            raw_text="Test",
            command_type=VCT.UNKNOWN,
            intent="test",
        )

        assert cmd.entities == {}

    def test_voice_command_timestamp_auto_generated(self, voice_module):
        """Test VoiceCommand auto-generates timestamp."""
        VC = voice_module["VoiceCommand"]
        VCT = voice_module["VoiceCommandType"]

        before = time.time()
        cmd = VC(
            raw_text="Test",
            command_type=VCT.UNKNOWN,
            intent="test",
        )
        after = time.time()

        assert before <= cmd.timestamp <= after


class TestVoiceConfig:
    """Test VoiceConfig dataclass."""

    def test_default_config(self, voice_module):
        """Test default voice configuration."""
        VConf = voice_module["VoiceConfig"]
        config = VConf()

        assert config.sample_rate == 16000
        assert config.channels == 1
        assert config.dtype == "float32"
        assert config.recording_duration == 5
        assert config.whisper_model == "whisper-1"
        assert config.language == "en"
        assert config.tts_engine == "pyttsx3"
        assert config.min_confidence == 0.6

    def test_custom_config(self, voice_module):
        """Test custom voice configuration."""
        VConf = voice_module["VoiceConfig"]
        config = VConf(
            sample_rate=44100,
            channels=2,
            recording_duration=10,
            language="es",
            min_confidence=0.8,
        )

        assert config.sample_rate == 44100
        assert config.channels == 2
        assert config.recording_duration == 10
        assert config.language == "es"
        assert config.min_confidence == 0.8

    def test_config_openai_api_key_from_env(self, voice_module):
        """Test config reads API key from environment."""
        VConf = voice_module["VoiceConfig"]
        with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key-123"}):
            config = VConf()
            assert config.openai_api_key == "test-key-123"

    def test_config_openai_api_key_override(self, voice_module):
        """Test config API key override."""
        VConf = voice_module["VoiceConfig"]
        config = VConf(openai_api_key="custom-key")
        assert config.openai_api_key == "custom-key"
