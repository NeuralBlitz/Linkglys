#!/usr/bin/env python3
"""
Coral TPU Edge Inference Engine for NeuralBlitz
Optimized for Google Coral Edge TPU with TensorFlow Lite
"""

import os
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np

try:
    from coralTPU import edgetpu

    EDGETPU_AVAILABLE = True
except ImportError:
    try:
        from edgetpu import runtime

        EDGETPU_AVAILABLE = True
    except ImportError:
        EDGETPU_AVAILABLE = False
        print("Warning: Edge TPU runtime not available")

try:
    import tflite_runtime.interpreter as tflite

    TFLITE_AVAILABLE = True
except ImportError:
    TFLITE_AVAILABLE = False
    print("Warning: TensorFlow Lite not available")

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("CoralTPUInference")


@dataclass
class CoralTPUConfig:
    """Configuration for Coral TPU inference"""

    model_path: str
    device: str = "/dev/apex_0"
    num_threads: int = 4
    enable_edgetpu: bool = True
    delegate_library: Optional[str] = None
    batch_size: int = 1
    warmup_runs: int = 10
    enable_profiling: bool = False


class CoralTPUDevice:
    """Coral TPU device management"""

    def __init__(self, device_path: str = "/dev/apex_0"):
        self.device_path = device_path
        self.available = self._check_device()

    def _check_device(self) -> bool:
        """Check if Coral TPU is available"""
        if not os.path.exists(self.device_path):
            logger.warning(f"Coral TPU device not found at {self.device_path}")
            return False
        return True

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        return {
            "device_path": self.device_path,
            "available": self.available,
            "type": "Coral Edge TPU",
            "performance": "4 TOPS (8-bit)",
            "power": "2W active",
        }


class CoralTPUInterpreter:
    """Edge TPU interpreter wrapper"""

    def __init__(self, model_path: str, enable_edgetpu: bool = True):
        self.model_path = model_path
        self.enable_edgetpu = enable_edgetpu
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self._load_model()

    def _load_model(self):
        """Load TFLite model with Edge TPU delegate"""
        if not TFLITE_AVAILABLE:
            raise RuntimeError("TensorFlow Lite not available")

        self.interpreter = tflite.Interpreter(
            model_path=self.model_path,
            experimental_delegates=[edgetpu.load_delegate('edgetpu.tflite')] if self.enable_edgetpu else [],
        )

        if self.enable_edgetpu and EDGETPU_AVAILABLE:
            try:
                self.interpreter = tflite.Interpreter(
                    model_path=self.model_path,
                    experimental_delegates=[edgetpu.load_delegate()],
                )
                logger.info("Loaded model with Edge TPU delegate")
            except Exception as e:
                logger.warning(f"Failed to load Edge TPU delegate: {e}")

        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def get_input_shape(self) -> Tuple[int, ...]:
        """Get model input shape"""
        return tuple(self.input_details[0]["shape"])

    def get_output_shape(self) -> Tuple[int, ...]:
        """Get model output shape"""
        return tuple(self.output_details[0]["shape"])

    def infer(self, input_data: np.ndarray) -> np.ndarray:
        """Run inference"""
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()
        output = self.interpreter.get_tensor(self.output_details[0]["index"])
        return output


class CoralTPUInferenceEngine:
    """Main Coral TPU inference engine"""

    def __init__(self, config: CoralTPUConfig):
        self.config = config
        self.device = CoralTPUDevice(config.device)
        self.interpreter = None
        self._initialize()

    def _initialize(self):
        """Initialize the inference engine"""
        if not TFLITE_AVAILABLE:
            raise RuntimeError("TensorFlow Lite is required")

        self.interpreter = CoralTPUInterpreter(
            self.config.model_path, self.config.enable_edgetpu
        )

        if self.config.warmup_runs > 0:
            self._warmup()

        logger.info(f"Coral TPU inference engine initialized")

    def _warmup(self):
        """Warmup the model"""
        input_shape = self.interpreter.get_input_shape()
        dummy_input = np.zeros(input_shape, dtype=np.float32)

        for _ in range(self.config.warmup_runs):
            self.interpreter.infer(dummy_input)

        logger.info(f"Warmup completed ({self.config.warmup_runs} runs)")

    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run prediction"""
        start_time = time.perf_counter()

        output = self.interpreter.infer(input_data)

        inference_time = time.perf_counter() - start_time

        return {
            "predictions": output.tolist(),
            "inference_time_ms": inference_time * 1000,
            "device": "Coral Edge TPU",
            "model": self.config.model_path,
        }

    def predict_batch(self, inputs: List[np.ndarray]) -> List[Dict[str, Any]]:
        """Run batch prediction"""
        results = []
        for input_data in inputs:
            results.append(self.predict(input_data))
        return results

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "device": self.device.get_device_info(),
            "model_path": self.config.model_path,
            "input_shape": self.interpreter.get_input_shape(),
            "output_shape": self.interpreter.get_output_shape(),
            "threads": self.config.num_threads,
            "edge_tpu_enabled": self.config.enable_edgetpu,
        }


class CoralTPUModelLoader:
    """Model loading and optimization utilities"""

    @staticmethod
    def compile_model(
        input_model: str, output_model: str, quantize: bool = True
    ) -> bool:
        """Compile model for Edge TPU"""
        try:
            import subprocess

            cmd = [
                "edgetpu_compiler",
                "-o",
                os.path.dirname(output_model),
                "-s" if quantize else "",
                input_model,
            ]
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Model compilation failed: {e}")
            return False

    @staticmethod
    def optimize_for_edge(
        model_path: str, output_path: str, int8_quantization: bool = True
    ) -> bool:
        """Optimize TFLite model for Edge TPU"""
        try:
            import subprocess

            cmd = [
                "tflite_convert",
                "--input_file",
                model_path,
                "--output_file",
                output_path,
                "--inference_type",
                "INT8" if int8_quantization else "FLOAT",
                "--input_arrays",
                "input",
                "--output_arrays",
                "output",
            ]
            result = subprocess.run(cmd, capture_output=True)
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Model optimization failed: {e}")
            return False


def create_engine(model_path: str, **kwargs) -> CoralTPUInferenceEngine:
    """Factory function to create inference engine"""
    config = CoralTPUConfig(model_path=model_path, **kwargs)
    return CoralTPUInferenceEngine(config)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: coral_tpu_inference.py <model_path>")
        sys.exit(1)

    engine = create_engine(sys.argv[1])
    print(f"Engine stats: {json.dumps(engine.get_stats(), indent=2)}")
