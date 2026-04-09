"""Auto-adapting tests for CapabilityKernels - verifies modules load and have classes."""
import pytest
import sys, os, importlib, inspect

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "CapabilityKernels", "Audio"))

class TestRealTimeAnalyzer:
    def test_module_loads(self):
        from realtime_analyzer_ck import RealTimeAnalyzerCK
        assert RealTimeAnalyzerCK is not None
        rack = RealTimeAnalyzerCK()
        assert rack is not None

class TestSoundClassifier:
    def test_module_loads(self):
        from sound_classifier_ck import SoundClassifierCK
        assert SoundClassifierCK is not None
        scc = SoundClassifierCK()
        assert scc is not None

class TestSpeechRecognizer:
    def test_module_loads(self):
        from speech_recognizer_ck import SpeechRecognizerCK
        assert SpeechRecognizerCK is not None
        src = SpeechRecognizerCK()
        assert src is not None

class TestAudioCKContracts:
    def test_schema_files_exist(self):
        import json
        for name in ["realtime_analyzer_ck", "sound_classifier_ck", "speech_recognizer_ck"]:
            path = os.path.join(os.path.dirname(__file__), "..", "CapabilityKernels", "Audio", f"{name}.json")
            assert os.path.exists(path), f"Schema missing: {name}.json"
            with open(path) as f:
                schema = json.load(f)
            assert "kernel" in schema or "properties" in schema
