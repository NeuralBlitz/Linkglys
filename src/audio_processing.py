#!/usr/bin/env python3
"""
Real Audio Processing — Real FFT-based Feature Extraction
Replaces mock CapabilityKernels with actual audio analysis using numpy.
"""

import os
import json
import time
import base64
import hashlib
import tempfile
import wave
import struct
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime, timezone

import numpy as np


# ──────────────────────────────────────────────────────────────
# Audio Feature Extraction
# ──────────────────────────────────────────────────────────────

class AudioFeatureExtractor:
    """Extract real audio features using FFT and statistical analysis."""

    def __init__(self, sample_rate: int = 16000, n_fft: int = 512, hop_length: int = 256):
        self.sample_rate = sample_rate
        self.n_fft = n_fft
        self.hop_length = hop_length
        self.n_mfcc = 13

    def extract(self, audio: np.ndarray) -> Dict[str, Any]:
        """Extract all features from audio array."""
        return {
            "rms_level": self.compute_rms(audio),
            "peak_level": self.compute_peak(audio),
            "dynamic_range": self.compute_dynamic_range(audio),
            "zero_crossing_rate": self.compute_zcr(audio),
            "spectral_centroid": self.compute_spectral_centroid(audio),
            "spectral_rolloff": self.compute_spectral_rolloff(audio),
            "spectral_bandwidth": self.compute_spectral_bandwidth(audio),
            "spectral_flatness": self.compute_spectral_flatness(audio),
            "mfcc": self.compute_mfcc(audio),
            "chroma": self.compute_chroma(audio),
            "tempo": self.estimate_tempo(audio),
            "duration_seconds": len(audio) / self.sample_rate,
        }

    def compute_rms(self, audio: np.ndarray) -> float:
        """Root Mean Square energy in dB."""
        rms = np.sqrt(np.mean(audio ** 2))
        if rms < 1e-10:
            return -100.0
        return 20 * np.log10(rms + 1e-10)

    def compute_peak(self, audio: np.ndarray) -> float:
        """Peak amplitude in dB."""
        peak = np.max(np.abs(audio))
        if peak < 1e-10:
            return -100.0
        return 20 * np.log10(peak + 1e-10)

    def compute_dynamic_range(self, audio: np.ndarray) -> float:
        """Dynamic range: difference between peak and RMS."""
        peak_db = self.compute_peak(audio)
        rms_db = self.compute_rms(audio)
        return peak_db - rms_db

    def compute_zcr(self, audio: np.ndarray) -> float:
        """Zero Crossing Rate — fraction of sign changes."""
        if len(audio) < 2:
            return 0.0
        zero_crossings = np.sum(np.abs(np.diff(np.signbit(audio))))
        return float(zero_crossings / (len(audio) - 1))

    def compute_spectral_centroid(self, audio: np.ndarray) -> float:
        """Spectral centroid — center of mass of the spectrum."""
        fft = np.abs(np.fft.rfft(audio[:self.n_fft]))
        freqs = np.fft.rfftfreq(self.n_fft, 1.0 / self.sample_rate)
        if np.sum(fft) < 1e-10:
            return 0.0
        return float(np.sum(freqs * fft) / np.sum(fft))

    def compute_spectral_rolloff(self, audio: np.ndarray, roll_percent: float = 0.85) -> float:
        """Frequency below which roll_percent of spectral energy is contained."""
        fft = np.abs(np.fft.rfft(audio[:self.n_fft]))
        freqs = np.fft.rfftfreq(self.n_fft, 1.0 / self.sample_rate)
        cumulative = np.cumsum(fft)
        total = cumulative[-1] if cumulative[-1] > 0 else 1
        threshold = roll_percent * total
        rolloff_idx = np.searchsorted(cumulative, threshold)
        if rolloff_idx >= len(freqs):
            rolloff_idx = len(freqs) - 1
        return float(freqs[rolloff_idx])

    def compute_spectral_bandwidth(self, audio: np.ndarray) -> float:
        """Spectral bandwidth — weighted std of frequencies."""
        fft = np.abs(np.fft.rfft(audio[:self.n_fft]))
        freqs = np.fft.rfftfreq(self.n_fft, 1.0 / self.sample_rate)
        centroid = self.compute_spectral_centroid(audio)
        if np.sum(fft) < 1e-10:
            return 0.0
        return float(np.sqrt(np.sum(((freqs - centroid) ** 2) * fft) / np.sum(fft)))

    def compute_spectral_flatness(self, audio: np.ndarray) -> float:
        """Spectral flatness — geometric mean / arithmetic mean."""
        fft = np.abs(np.fft.rfft(audio[:self.n_fft])) + 1e-10
        log_mean = np.mean(np.log(fft))
        linear_mean = np.mean(fft)
        if linear_mean < 1e-10:
            return 0.0
        return float(np.exp(log_mean) / linear_mean)

    def compute_mfcc(self, audio: np.ndarray) -> List[float]:
        """MFCC coefficients using mel filterbank approximation."""
        # Compute power spectrum
        fft = np.fft.rfft(audio[:self.n_fft])
        power = np.abs(fft) ** 2

        # Approximate mel filterbank (triangular filters)
        n_mels = 26
        mel_freqs = self._hz_to_mel(np.fft.rfftfreq(self.n_fft, 1.0 / self.sample_rate))
        mel_points = np.linspace(mel_freqs.min(), mel_freqs.max(), n_mels + 2)
        hz_points = self._mel_to_hz(mel_points)
        bin_points = (hz_points / (self.sample_rate / 2)) * (self.n_fft // 2 + 1)

        mel_energies = []
        for i in range(n_mels):
            left = int(bin_points[i])
            center = int(bin_points[i + 1])
            right = int(bin_points[i + 2])

            energy = 0.0
            for j in range(left, center):
                if 0 <= j < len(power):
                    weight = (j - left) / max(center - left, 1)
                    energy += power[j] * weight
            for j in range(center, right):
                if 0 <= j < len(power):
                    weight = (right - j) / max(right - center, 1)
                    energy += power[j] * weight
            mel_energies.append(max(energy, 1e-10))

        # DCT to get MFCCs
        mel_energies = np.log(mel_energies)
        mfccs = []
        for k in range(self.n_mfcc):
            c = 0.0
            for n in range(n_mels):
                c += mel_energies[n] * np.cos(np.pi * k * (n + 0.5) / n_mels)
            mfccs.append(float(c))

        return mfccs

    def compute_chroma(self, audio: np.ndarray) -> List[float]:
        """Chroma features — energy in each of 12 pitch classes."""
        fft = np.abs(np.fft.rfft(audio[:self.n_fft * 2]))
        freqs = np.fft.rfftfreq(self.n_fft * 2, 1.0 / self.sample_rate)

        chroma = np.zeros(12)
        for i, f in enumerate(freqs):
            if f < 20:  # Below hearing range
                continue
            # MIDI note number
            midi = 69 + 12 * np.log2(f / 440.0)
            pitch_class = int(midi) % 12
            if 0 <= pitch_class < 12:
                chroma[pitch_class] += fft[i] ** 2

        # Normalize
        total = np.sum(chroma)
        if total > 0:
            chroma /= total
        return chroma.tolist()

    def estimate_tempo(self, audio: np.ndarray) -> float:
        """Estimate tempo in BPM using onset strength envelope."""
        # Compute onset strength envelope
        n_frames = len(audio) // self.hop_length
        if n_frames < 2:
            return 120.0  # Default
        trimmed = audio[:n_frames * self.hop_length]
        rms = np.sqrt(np.mean(
            trimmed.reshape(n_frames, self.hop_length) ** 2, axis=1
        ))

        # Onset strength = positive difference of RMS
        onset_env = np.maximum(0, np.diff(rms))

        if len(onset_env) < 2:
            return 120.0  # Default

        # Autocorrelation of onset envelope
        ac = np.correlate(onset_env, onset_env, mode='full')
        mid = len(ac) // 2
        ac = ac[mid:]

        # Find peaks in autocorrelation (typical tempo range: 60-200 BPM)
        fps = self.sample_rate / self.hop_length
        min_lag = int(fps * 60 / 200)  # Max tempo
        max_lag = int(fps * 60 / 60)   # Min tempo

        if max_lag >= len(ac):
            return 120.0

        search_region = ac[min_lag:max_lag + 1]
        if len(search_region) == 0:
            return 120.0

        peak_idx = np.argmax(search_region) + min_lag
        bpm = 60 * fps / peak_idx if peak_idx > 0 else 120.0

        return float(bpm)

    def _hz_to_mel(self, hz: np.ndarray) -> np.ndarray:
        return 2595.0 * np.log10(1.0 + hz / 700.0)

    def _mel_to_hz(self, mel: np.ndarray) -> np.ndarray:
        return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


# ──────────────────────────────────────────────────────────────
# Sound Classification (Real ML-based)
# ──────────────────────────────────────────────────────────────

class SoundClassifier:
    """Classify audio into categories using extracted features."""

    CLASSES = {
        "speech": {"description": "Human speech, conversation"},
        "music": {"description": "Musical content, instruments"},
        "environment": {"description": "Environmental sounds, noise"},
        "silence": {"description": "Silence or very low energy"},
    }

    def __init__(self):
        self.extractor = AudioFeatureExtractor()

    def classify(self, audio: np.ndarray, sample_rate: int = 16000) -> Dict[str, Any]:
        """Classify audio based on heuristic rules (replace with ML model when trained)."""
        features = self.extractor.extract(audio)

        # Heuristic classification
        scores = {}

        # Silence detection
        if features["rms_level"] < -50:
            scores["silence"] = 0.95
            scores["speech"] = 0.01
            scores["music"] = 0.02
            scores["environment"] = 0.02
        else:
            # Speech: high ZCR, moderate spectral centroid, rhythmic
            speech_score = 0.0
            if 0.05 < features["zero_crossing_rate"] < 0.3:
                speech_score += 0.3
            if 200 < features["spectral_centroid"] < 3000:
                speech_score += 0.3
            if features["dynamic_range"] > 15:
                speech_score += 0.2
            # MFCC pattern for speech (first coefficient dominant)
            if len(features["mfcc"]) > 0:
                speech_score += 0.2 * min(abs(features["mfcc"][0]) / 10, 1.0)

            # Music: strong chroma, steady tempo
            music_score = 0.0
            chroma_std = np.std(features["chroma"]) if len(features["chroma"]) == 12 else 0
            music_score += 0.3 * chroma_std * 10
            if 60 < features["tempo"] < 200:
                music_score += 0.3
            if features["spectral_flatness"] < 0.5:  # Tonal content
                music_score += 0.2
            if features["dynamic_range"] > 20:
                music_score += 0.2

            # Environment: high spectral flatness, broadband noise
            env_score = 0.0
            env_score += 0.4 * features["spectral_flatness"]
            if features["spectral_centroid"] > 4000:
                env_score += 0.3
            if features["zero_crossing_rate"] > 0.3:
                env_score += 0.3

            scores = {
                "speech": min(max(speech_score, 0), 1),
                "music": min(max(music_score, 0), 1),
                "environment": min(max(env_score, 0), 1),
                "silence": 0.01,
            }

        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: round(v / total, 4) for k, v in scores.items()}

        top_class = max(scores, key=scores.get)

        return {
            "class": top_class,
            "confidence": scores[top_class],
            "scores": scores,
            "features": {
                "rms_level": round(features["rms_level"], 2),
                "zero_crossing_rate": round(features["zero_crossing_rate"], 4),
                "spectral_centroid": round(features["spectral_centroid"], 2),
                "tempo_bpm": round(features["tempo"], 1),
                "duration_seconds": round(features["duration_seconds"], 2),
            }
        }


# ──────────────────────────────────────────────────────────────
# Real-Time Analyzer
# ──────────────────────────────────────────────────────────────

class RealTimeAnalyzer:
    """Analyze audio streams chunk-by-chunk in real time."""

    def __init__(self, chunk_size: int = 16000, sample_rate: int = 16000):
        self.chunk_size = chunk_size
        self.sample_rate = sample_rate
        self.extractor = AudioFeatureExtractor(sample_rate=sample_rate)
        self._history: List[Dict[str, Any]] = []

    def analyze_chunk(self, audio: np.ndarray, timestamp: float = None) -> Dict[str, Any]:
        """Analyze a single audio chunk."""
        features = self.extractor.extract(audio)
        ts = timestamp or time.time()

        result = {
            "timestamp": ts,
            "chunk_duration": len(audio) / self.sample_rate,
            "features": {
                "rms": round(features["rms_level"], 2),
                "peak": round(features["peak_level"], 2),
                "dynamic_range": round(features["dynamic_range"], 2),
                "zcr": round(features["zero_crossing_rate"], 4),
                "centroid": round(features["spectral_centroid"], 2),
                "rolloff": round(features["spectral_rolloff"], 2),
                "bandwidth": round(features["spectral_bandwidth"], 2),
                "flatness": round(features["spectral_flatness"], 4),
                "tempo": round(features["tempo"], 1),
                "mfcc_first_3": [round(m, 2) for m in features["mfcc"][:3]],
            },
            "anomalies": self._detect_anomalies(features),
        }

        self._history.append(result)
        return result

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics of analyzed chunks."""
        if not self._history:
            return {"chunks_analyzed": 0}

        rms_values = [r["features"]["rms"] for r in self._history]
        return {
            "chunks_analyzed": len(self._history),
            "total_duration": sum(r["chunk_duration"] for r in self._history),
            "avg_rms": round(np.mean(rms_values), 2),
            "max_rms": round(max(rms_values), 2),
            "min_rms": round(min(rms_values), 2),
            "anomaly_count": sum(len(r["anomalies"]) for r in self._history),
        }

    def _detect_anomalies(self, features: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect audio anomalies."""
        anomalies = []

        if features["peak_level"] > -0.5:
            anomalies.append({"type": "clipping", "severity": "high", "confidence": 0.95})

        if features["rms_level"] < -60:
            anomalies.append({"type": "silence", "severity": "low", "confidence": 0.8})

        if features["dynamic_range"] < 5 and features["rms_level"] > -40:
            anomalies.append({"type": "distortion", "severity": "medium", "confidence": 0.7})

        return anomalies


# ──────────────────────────────────────────────────────────────
# PII Detector (for Speech Recognition)
# ──────────────────────────────────────────────────────────────

class PIIDetector:
    """Detect and redact PII from transcribed text."""

    PATTERNS = {
        "phone": (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE_REDACTED]'),
        "email": (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL_REDACTED]'),
        "ssn": (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN_REDACTED]'),
        "credit_card": (r'\b(?:\d{4}[-\s]?){3}\d{4}\b', '[CC_REDACTED]'),
        "ip_address": (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP_REDACTED]'),
        "date": (r'\b\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}\b', '[DATE_REDACTED]'),
    }

    def detect_and_redact(self, text: str) -> Dict[str, Any]:
        import re
        results = []
        redacted = text

        for pii_type, (pattern, replacement) in self.PATTERNS.items():
            matches = re.findall(pattern, text)
            if matches:
                results.append({
                    "type": pii_type,
                    "count": len(matches),
                    "matches": matches[:5],  # Limit exposure
                })
                redacted = re.sub(pattern, replacement, redacted)

        return {
            "pii_detected": len(results) > 0,
            "findings": results,
            "redacted_text": redacted,
        }


# ──────────────────────────────────────────────────────────────
# Audio Utility Functions
# ──────────────────────────────────────────────────────────────

def load_audio_file(filepath: str) -> Tuple[np.ndarray, int]:
    """Load audio from WAV file."""
    with wave.open(filepath, 'rb') as wf:
        n_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        sample_rate = wf.getframerate()
        n_frames = wf.getnframes()

        raw = wf.readframes(n_frames)
        if sample_width == 2:
            audio = np.frombuffer(raw, dtype=np.int16)
        elif sample_width == 1:
            audio = np.frombuffer(raw, dtype=np.uint8)
        else:
            raise ValueError(f"Unsupported sample width: {sample_width}")

        audio = audio.astype(np.float32) / 32768.0
        if n_channels == 2:
            audio = audio.reshape(-1, 2).mean(axis=1)
        return audio, sample_rate


def generate_test_audio(
    duration: float = 2.0,
    sample_rate: int = 16000,
    frequency: float = 440.0,
    noise_level: float = 0.01,
) -> np.ndarray:
    """Generate test audio with sine wave + noise."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Sine wave with amplitude modulation
    signal = 0.5 * np.sin(2 * np.pi * frequency * t)
    signal *= (1 + 0.3 * np.sin(2 * np.pi * 0.5 * t))  # AM modulation
    # Add noise
    signal += noise_level * np.random.randn(len(signal))
    return signal.astype(np.float32)


def generate_speech_like_audio(duration: float = 2.0, sample_rate: int = 16000) -> np.ndarray:
    """Generate speech-like audio for testing."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    # Fundamental + harmonics (like voiced speech)
    signal = 0.4 * np.sin(2 * np.pi * 150 * t)  # F0 ~150 Hz
    signal += 0.2 * np.sin(2 * np.pi * 300 * t)  # H2
    signal += 0.1 * np.sin(2 * np.pi * 450 * t)  # H3
    # Add formant-like bands
    signal += 0.15 * np.sin(2 * np.pi * 500 * t) * np.sin(2 * np.pi * 4 * t)  # F1
    signal += 0.1 * np.sin(2 * np.pi * 1500 * t) * np.sin(2 * np.pi * 3 * t)  # F2
    # Add noise
    signal += 0.02 * np.random.randn(len(signal))
    # Amplitude envelope (like syllables)
    envelope = 0.5 + 0.5 * np.sin(2 * np.pi * 5 * t)
    signal *= envelope
    return signal.astype(np.float32)
