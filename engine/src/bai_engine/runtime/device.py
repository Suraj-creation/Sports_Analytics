"""Device discovery, ONNX Runtime session factory and GPU telemetry."""

from __future__ import annotations

import functools
import hashlib
import json
import platform
import re
import tempfile
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


def ort_providers(
    backend: str,
    engine_cache: Path | None = None,
    fp16: bool = True,
    *,
    model_digest: str | None = None,
    cache_context: dict[str, Any] | None = None,
) -> list[Any]:
    """Execution providers, with persistent TensorRT caching disabled by default.

    A session owner may supply a complete ``cache_context`` only when it also
    owns native ORT cache build/use serialization. ORT can write engines and
    dynamic-shape profiles during inference; namespacing alone does not make
    those writes atomic. This function never builds or publishes native engines.
    The explicit context is an internal integration contract, not a user flag.
    """
    import onnxruntime as ort

    available = set(ort.get_available_providers())
    providers: list[Any] = []
    if backend == "tensorrt" and "TensorrtExecutionProvider" in available:
        opts: dict[str, Any] = {"trt_fp16_enable": fp16, "trt_max_workspace_size": 2 << 30}
        namespace = _trt_cache_namespace(engine_cache, model_digest, cache_context, opts)
        if namespace is not None:
            opts.update(
                {
                    "trt_engine_cache_enable": True,
                    "trt_engine_cache_path": str(namespace),
                    "trt_timing_cache_enable": True,
                    "trt_timing_cache_path": str(namespace),
                    "trt_force_timing_cache": False,
                }
            )
        else:
            # Explicit false values also override ORT cache-enable defaults or
            # environment settings; an incomplete identity must fail closed.
            opts.update({"trt_engine_cache_enable": False, "trt_timing_cache_enable": False})
        providers.append(("TensorrtExecutionProvider", opts))
    if backend in ("tensorrt", "onnx-cuda") and "CUDAExecutionProvider" in available:
        providers.append(("CUDAExecutionProvider", {"cudnn_conv_algo_search": "HEURISTIC"}))
    providers.append("CPUExecutionProvider")
    if backend in ("tensorrt", "onnx-cuda") and len(providers) == 1:
        log.warning("device.gpu_provider_missing", backend=backend, available=sorted(available))
    return providers


def _trt_cache_namespace(
    root: Path | None,
    model_digest: str | None,
    context: dict[str, Any] | None,
    options: dict[str, Any],
) -> Path | None:
    """Describe compatibility; native cache transaction ownership is external."""
    required = (
        "onnxruntime", "tensorrt", "cuda_runtime", "cuda_driver",
        "gpu_uuid", "gpu_compute_capability", "device_id",
    )
    if (
        root is None
        or model_digest is None
        or re.fullmatch(r"[a-fA-F0-9]{64}", model_digest) is None
        or context is None
        or any(not isinstance(context.get(key), str) or not context[key].strip() for key in required)
    ):
        return None
    contract = {
        "schema": "ort-trt-cache-compatibility-v1",
        "graph_sha256": model_digest.lower(),
        "runtime": context,
        "builder_options": options,
    }
    encoded = json.dumps(contract, sort_keys=True, separators=(",", ":")).encode("utf-8")
    namespace = root / hashlib.sha256(encoded).hexdigest()
    namespace.mkdir(parents=True, exist_ok=True)
    # This is a compatibility record only; it is not a native-engine checksum
    # or a claim that ORT's own files are transactionally published.
    with tempfile.NamedTemporaryFile(mode="wb", prefix=".contract-", dir=namespace, delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(encoded)
    try:
        temporary.replace(namespace / "cache-contract.json")
    finally:
        temporary.unlink(missing_ok=True)
    return namespace


def ort_runtime(backend: str, session: Any) -> dict[str, Any]:
    """Describe the providers actually active after ORT initializes a model."""
    expected = {
        "onnx-cpu": "CPUExecutionProvider",
        "onnx-cuda": "CUDAExecutionProvider",
        "tensorrt": "TensorrtExecutionProvider",
    }
    if backend not in expected:
        raise ValueError(f"unsupported ONNX backend {backend!r}")
    providers = list(session.get_providers())
    return {
        "requested_backend": backend,
        "providers": providers,
        "actual_backend": next(
            (key for key, provider in expected.items() if providers and providers[0] == provider), None
        ),
        "backend_fallback": not providers or providers[0] != expected[backend],
    }


def engine_cache_dir(models_dir: Path) -> Path:
    """Human-readable grouping root; this is not a compatibility namespace."""
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
