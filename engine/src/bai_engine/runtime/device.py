"""Device discovery, ONNX Runtime session factory and GPU telemetry."""

from __future__ import annotations

import functools
import platform
from pathlib import Path
from typing import Any

from bai_engine.obs import GPU_MEM, GPU_POWER, GPU_UTIL, get_logger

log = get_logger(__name__)


@functools.cache
def cuda_available() -> bool:
    try:
        import torch

        return bool(torch.cuda.is_available())
    except Exception:
        return False


def ort_providers(backend: str, engine_cache: Path | None = None, fp16: bool = True) -> list[Any]:
    """Execution providers for an ONNX Runtime session given a profile ``backend``."""
    import onnxruntime as ort

    available = set(ort.get_available_providers())
    providers: list[Any] = []
    if backend == "tensorrt" and "TensorrtExecutionProvider" in available:
        opts: dict[str, Any] = {"trt_fp16_enable": fp16, "trt_max_workspace_size": 2 << 30}
        if engine_cache is not None:
            engine_cache.mkdir(parents=True, exist_ok=True)
            opts.update(
                {
                    "trt_engine_cache_enable": True,
                    "trt_engine_cache_path": str(engine_cache),
                    "trt_timing_cache_enable": True,
                }
            )
        providers.append(("TensorrtExecutionProvider", opts))
    if backend in ("tensorrt", "onnx-cuda") and "CUDAExecutionProvider" in available:
        providers.append(("CUDAExecutionProvider", {"cudnn_conv_algo_search": "HEURISTIC"}))
    providers.append("CPUExecutionProvider")
    if backend in ("tensorrt", "onnx-cuda") and len(providers) == 1:
        log.warning("device.gpu_provider_missing", backend=backend, available=sorted(available))
    return providers


def engine_cache_dir(models_dir: Path) -> Path:
    tag = "cpu"
    try:
        import pynvml

        pynvml.nvmlInit()
        h = pynvml.nvmlDeviceGetHandleByIndex(0)
        name = pynvml.nvmlDeviceGetName(h)
        tag = (name.decode() if isinstance(name, bytes) else name).replace(" ", "_")
    except Exception as e:  # NVML absent (CPU host) → engines are cached under "cpu"
        log.debug("device.nvml_unavailable", error=str(e))
    return models_dir / "engines" / tag


def gpu_snapshot() -> list[dict[str, Any]]:
    """Per-GPU utilisation / memory / power (empty list without NVML)."""
    try:
        import pynvml
    except ImportError:
        return []
    try:
        pynvml.nvmlInit()
        out = []
        for i in range(pynvml.nvmlDeviceGetCount()):
            h = pynvml.nvmlDeviceGetHandleByIndex(i)
            util = pynvml.nvmlDeviceGetUtilizationRates(h)
            mem = pynvml.nvmlDeviceGetMemoryInfo(h)
            power = pynvml.nvmlDeviceGetPowerUsage(h) / 1000.0
            name = pynvml.nvmlDeviceGetName(h)
            name = name.decode() if isinstance(name, bytes) else name
            GPU_UTIL.labels(gpu=str(i)).set(util.gpu)
            GPU_MEM.labels(gpu=str(i)).set(mem.used / 2**20)
            GPU_POWER.labels(gpu=str(i)).set(power)
            out.append(
                {
                    "index": i,
                    "name": name,
                    "util": util.gpu,
                    "mem_used_mb": round(mem.used / 2**20),
                    "mem_total_mb": round(mem.total / 2**20),
                    "power_w": round(power, 1),
                }
            )
        return out
    except Exception:
        return []


def system_info() -> dict[str, Any]:
    import os

    info: dict[str, Any] = {
        "platform": platform.platform(),
        "python": platform.python_version(),
        "cpu_count": os.cpu_count(),
        "cuda": cuda_available(),
        "gpus": gpu_snapshot(),
    }
    try:
        import onnxruntime as ort

        info["onnxruntime"] = {"version": ort.__version__, "providers": ort.get_available_providers()}
    except ImportError:
        info["onnxruntime"] = None
    return info
