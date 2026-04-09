"""Auto-adapting tests for voice_interface - skips if sounddevice unavailable."""
import pytest
import sys, os

# Skip ALL tests if sounddevice unavailable
pytest.importorskip("sounddevice")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "voice_interface"))

class TestVoiceCommandType:
    def test_all_types_exist(self):
        from voice_interface import VoiceCommandType
        assert VoiceCommandType.GREETING.value == "greeting"

class TestVoiceCommand:
    def test_creation(self):
        from voice_interface import VoiceCommand, VoiceCommandType
        cmd = VoiceCommand(raw_text="Hello", command_type=VoiceCommandType.GREETING, intent="greet", confidence=0.9)
        assert cmd.raw_text == "Hello"

    def test_to_dict(self):
        from voice_interface import VoiceCommand, VoiceCommandType
        cmd = VoiceCommand(raw_text="Test", command_type=VoiceCommandType.ACTION, intent="do")
        d = cmd.to_dict()
        assert d["raw_text"] == "Test"
        assert "timestamp" in d

class TestVoiceConfig:
    def test_defaults(self):
        from voice_interface import VoiceConfig
        cfg = VoiceConfig()
        assert cfg.sample_rate == 16000
        assert cfg.min_confidence == 0.6
