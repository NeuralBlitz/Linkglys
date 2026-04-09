#!/usr/bin/env python3
"""
Jetson Nano Edge Inference Engine for NeuralBlitz
Optimized for NVIDIA Jetson Nano with TensorRT
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
    import tensorrt as trt

    TENSORRT_AVAILABLE = True
except ImportError:
    TENSORRT_AVAILABLE = False
    print("Warning: TensorRT not available")

try:
    import tflite_runtime.interpreter as tflite

    TFLITE_AVAILABLE = True
except ImportError:
    try:
        import tensorflow.lite as tflite

        TFLITE_AVAILABLE = True
    except ImportError:
        TFLITE_AVAILABLE = False

try:
    import pycuda.driver as cuda

    CUDA_AVAILABLE = True
except ImportError:
    CUDA_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("JetsonNanoInference")


@dataclass
class JetsonNanoConfig:
    """Configuration for Jetson Nano inference"""

    model_path: str
    model_type: str = "onnx"
    input_shape: Tuple[int, int, int, int] = (1, 3, 224, 224)
    max_batch_size: int = 1
    enable_fp16: bool = True
    enable_int8: bool = False
    calibration_cache: Optional[str] = None
    workspace_size: int = 1 << 30
    dla_core: int = -1


class JetsonNanoDevice:
    """Jetson Nano device management"""

    def __init__(self):
        self.device = None
        self.compute_capability = None
        self._initialize()

    def _initialize(self):
        """Initialize CUDA if available"""
        if CUDA_AVAILABLE:
            try:
                cuda.init()
                self.device = cuda.Device(0)
                self.compute_capability = self.device.compute_capability()
                logger.info(
                    f"Jetson Nano initialized: compute {self.compute_capability}"
                )
            except Exception as e:
                logger.warning(f"CUDA initialization failed: {e}")

    def get_device_info(self) -> Dict[str, Any]:
        """Get device information"""
        info = {
            "device": "Jetson Nano",
            "compute_capability": self.compute_capability,
            "cuda_available": CUDA_AVAILABLE,
            "tensorrt_available": TENSORRT_AVAILABLE,
        }

        if os.path.exists("/sys/class/thermal/thermal_zone0/temp"):
            try:
                with open("/sys/class/thermal/thermal_zone0/temp") as f:
                    info["temperature_c"] = int(f.read()) / 1000
            except:
                pass

        return info

    def get_power_usage(self) -> Dict[str, float]:
        """Get power usage information"""
        power = {"current": 0.0, "average": 0.0}

        power_rail = "/sys/class/power_supply/Battery/current_now"
        if os.path.exists(power_rail):
            try:
                with open(power_rail) as f:
                    power["current"] = abs(int(f.read())) / 1000000.0
            except:
                pass

        return power

    def set_performance_mode(self, mode: str = "maxn") -> bool:
        """Set Jetson performance mode"""
        try:
            result = os.system(f"sudo nvpmodel -m {mode if mode == 'maxn' else 0}")
            os.system("sudo jetson_clocks")
            return result == 0
        except:
            return False


class TensorRTEngine:
    """TensorRT engine wrapper"""

    def __init__(self, config: JetsonNanoConfig):
        self.config = config
        self.logger = trt.Logger(trt.Logger.WARNING)
        self.runtime = None
        self.engine = None
        self.context = None
        self.inputs = []
        self.outputs = []
        self.bindings = []

    def build_engine(self) -> bool:
        """Build TensorRT engine from model"""
        if not TENSORRT_AVAILABLE:
            logger.error("TensorRT not available")
            return False

        builder = trt.Builder(self.logger)
        network = builder.create_network(
            1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
        )
        config = builder.create_builder_config()

        config.max_workspace_size = self.config.workspace_size

        if self.config.enable_fp16 and builder.platform_has_fp16:
            config.set_flag(trt.BuilderFlag.FP16)

        if self.config.enable_int8 and builder.platform_has_int8:
            config.set_flag(trt.BuilderFlag.INT8)

        if self.config.model_type == "onnx":
            import onnx

            parser = trt.OnnxParser(network, self.logger)

            with open(self.config.model_path, "rb") as f:
                if not parser.parse(f.read()):
                    logger.error("Failed to parse ONNX model")
                    return False

        elif self.config.model_type == "uff":
            parser = trt.UffParser()
            parser.register_input("input", self.config.input_shape[1:])
            parser.parse(self.config.model_path, network)

        self.engine = builder.build_serialized_network(network, config)

        if self.engine:
            logger.info("TensorRT engine built successfully")
            return True

        return False

    def load_engine(self, engine_path: str) -> bool:
        """Load pre-built TensorRT engine"""
        if not TENSORRT_AVAILABLE:
            return False

        with open(engine_path, "rb") as f:
            self.runtime = trt.Runtime(self.logger)
            self.engine = self.runtime.deserialize_cuda_engine(f.read())

        if self.engine:
            self.context = self.engine.create_execution_context()
            return True
        return False

    def allocate_buffers(self):
        """Allocate GPU buffers"""
        if not self.engine:
            return

        for i in range(self.engine.num_bindings):
            name = self.engine.get_binding_name(i)
            shape = self.engine.get_binding_shape(i)
            dtype = trt.nptype(self.engine.get_binding_dtype(i))

            if self.engine.binding_is_input(i):
                self.inputs.append({"name": name, "shape": shape, "dtype": dtype})
            else:
                self.outputs.append({"name": name, "shape": shape, "dtype": dtype})

        for inp in self.inputs:
            inp_buffer = cuda.memalloc(inp["shape"])

    def infer(self, input_data: np.ndarray) -> np.ndarray:
        """Run inference"""
        if not self.context:
            raise RuntimeError("Engine not loaded")

        h_input = cuda.pagelocked_empty(input_data.size, dtype=np.float32)
        h_output = cuda.pagelocked_empty(self.outputs[0]["shape"], dtype=np.float32)

        d_input = cuda.mem_alloc(h_input.nbytes)
        d_output = cuda.mem_alloc(h_output.nbytes)

        stream = cuda.Stream()

        np.copyto(h_input, input_data.ravel())
        cuda.memcpy_htod_async(d_input, h_input, stream)

        self.context.execute_async_v2(
            bindings=[int(d_input), int(d_output)], stream_handle=stream.handle
        )

        cuda.memcpy_dtoh_async(h_output, d_output, stream)
        stream.synchronize()

        output = h_output.reshape(self.outputs[0]["shape"])
        return output


class JetsonNanoInferenceEngine:
    """Main Jetson Nano inference engine"""

    def __init__(self, config: JetsonNanoConfig):
        self.config = config
        self.device = JetsonNanoDevice()
        self.trt_engine = None
        self.tflite_interpreter = None
        self._initialize()

    def _initialize(self):
        """Initialize the inference engine"""
        if TENSORRT_AVAILABLE and self.config.model_type in ["onnx", "uff"]:
            self.trt_engine = TensorRTEngine(self.config)
            self.trt_engine.build_engine()
            self.trt_engine.allocate_buffers()
            logger.info("Initialized with TensorRT")

        elif TFLITE_AVAILABLE:
            self.tflite_interpreter = tflite.Interpreter(
                model_path=self.config.model_path, num_threads=4
            )
            self.tflite_interpreter.allocate_tensors()
            logger.info("Initialized with TensorFlow Lite")

        else:
            logger.warning("No inference backend available")

    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run prediction"""
        start_time = time.perf_counter()

        if self.trt_engine:
            output = self.trt_engine.infer(input_data)
        elif self.tflite_interpreter:
            self.tflite_interpreter.set_tensor(
                self.tflite_interpreter.get_input_details()[0]["index"], input_data
            )
            self.tflite_interpreter.invoke()
            output = self.tflite_interpreter.get_tensor(
                self.tflite_interpreter.get_output_details()[0]["index"]
            )
        else:
            raise RuntimeError("No inference backend available")

        inference_time = time.perf_counter() - start_time

        return {
            "predictions": output.tolist(),
            "inference_time_ms": inference_time * 1000,
            "device": "NVIDIA Jetson Nano",
            "backend": "TensorRT" if self.trt_engine else "TensorFlow Lite",
        }

    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics"""
        return {
            "device": self.device.get_device_info(),
            "model_path": self.config.model_path,
            "model_type": self.config.model_type,
            "fp16_enabled": self.config.enable_fp16,
            "int8_enabled": self.config.enable_int8,
            "backend": "TensorRT" if self.trt_engine else "TensorFlow Lite",
        }


def create_engine(
    model_path: str, model_type: str = "onnx", **kwargs
) -> JetsonNanoInferenceEngine:
    """Factory function to create inference engine"""
    config = JetsonNanoConfig(model_path=model_path, model_type=model_type, **kwargs)
    return JetsonNanoInferenceEngine(config)


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: jetson_nano_inference.py <model_path> [onnx|tflite]")
        sys.exit(1)

    model_type = sys.argv[2] if len(sys.argv) > 2 else "onnx"
    engine = create_engine(sys.argv[1], model_type)
    print(json.dumps(engine.get_stats(), indent=2))
