"""Bounded TrackNet runtime checks using existing, previously trusted server assets.

Run in the configured GPU-server environment; this script never fetches models or
installs dependencies. The output directory must be new and outside the models
directory. Exit codes: 0 complete, 1 failure, 2 partial (for example a missing
ONNX export dependency). Tensor parity and detection counts do not measure accuracy.
"""

from __future__ import annotations

import argparse
import contextlib
import gc
import hashlib
import importlib.metadata
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

MODEL_NAME = "tracknetv3"
SOURCE = "sports/badminton/src/bai_badminton/perception/tracknet.py"
INPUT_SHAPE = (1, 27, 288, 512)
OUTPUT_SHAPE = (1, 8, 288, 512)
SEED = 20261102


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True, timeout=30
    ).stdout.strip()


def _error(error: BaseException) -> dict[str, Any]:
    missing = []
    current: BaseException | None = error
    seen: set[int] = set()
    while current is not None and id(current) not in seen:
        seen.add(id(current))
        if isinstance(current, ModuleNotFoundError):
            missing.append(current.name or str(current))
        current = current.__cause__ or current.__context__
    return {
        "type": type(error).__name__,
        "message": str(error),
        "missing_dependencies": sorted(set(missing)),
        "traceback": "".join(traceback.format_exception(error)),
    }


def _baseline_module(repo: Path, revision: str, temporary: Path):
    source = subprocess.run(
        ["git", "-C", str(repo), "show", f"{revision}:{SOURCE}"],
        check=True, capture_output=True, timeout=30,
    ).stdout
    path = temporary / "baseline_tracknet.py"
    path.write_bytes(source)
    name = f"_phase2_tracknet_baseline_{revision[:12]}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load baseline TrackNet source")
    module = importlib.util.module_from_spec(spec)
    # Dataclass annotation resolution requires the module during execution.
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module, hashlib.sha256(source).hexdigest()


def _forward(detector: Any, tensor: Any, torch: Any, result: dict[str, Any]):
    import numpy as np

    parameter = next(detector._torch.parameters())
    if parameter.device.type != "cuda" or parameter.dtype != torch.float32:
        raise RuntimeError(f"expected FP32 CUDA parameters, got {parameter.device}/{parameter.dtype}")
    result["runtime"] = dict(detector.runtime)
    result["entrypoint"] = "_torch.forward under torch.inference_mode"
    result["warmup_forwards"] = 1
    result["measured_forwards"] = 1
    torch.cuda.reset_peak_memory_stats()
    with torch.inference_mode():
        warmup = detector._torch(tensor)
        torch.cuda.synchronize()
        del warmup
        start, stop = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
        wall = time.perf_counter()
        start.record()
        output = detector._torch(tensor)
        stop.record()
        stop.synchronize()
        result["forward_wall_ms"] = (time.perf_counter() - wall) * 1000
        result["forward_gpu_ms"] = start.elapsed_time(stop)
        array = output.detach().float().cpu().numpy().copy()
    result.update(
        shape=list(array.shape), dtype=str(array.dtype), finite=bool(np.isfinite(array).all()),
        output_sha256=hashlib.sha256(array.tobytes()).hexdigest(),
        peak_cuda_allocated_bytes=torch.cuda.max_memory_allocated(),
        peak_cuda_reserved_bytes=torch.cuda.max_memory_reserved(),
    )
    if array.shape != OUTPUT_SHAPE or not result["finite"]:
        raise RuntimeError(f"invalid TrackNet heatmaps: shape={array.shape}, finite={result['finite']}")
    result["status"] = "passed"
    return array


def _release_cuda(torch: Any) -> None:
    gc.collect()
    torch.cuda.empty_cache()


def _proxy_diagnostic(detector: Any, proxy: Path, torch: Any) -> dict[str, Any]:
    import cv2
    import numpy as np

    if not proxy.is_file():
        raise FileNotFoundError(f"proxy does not exist: {proxy}")
    capture = cv2.VideoCapture(str(proxy))
    frames = []
    digest = hashlib.sha256()
    wall = time.perf_counter()
    try:
        if not capture.isOpened():
            raise RuntimeError(f"cannot open proxy: {proxy}")
        for _ in range(8):  # Read exactly eight frames, with no ninth-frame probe.
            ok, frame = capture.read()
            if not ok:
                raise RuntimeError(f"proxy supplied only {len(frames)} of the required eight frames")
            digest.update(str(frame.shape).encode("ascii"))
            digest.update(frame.tobytes())
            frames.append(frame)
    finally:
        capture.release()
    decode_ms = (time.perf_counter() - wall) * 1000
    torch.cuda.synchronize()
    wall = time.perf_counter()
    detections = detector.detect(frames, shots=[0] * 8, step=8)
    torch.cuda.synchronize()
    detected = [d for d in detections if d is not None]
    finite = all(np.isfinite([d.x, d.y, d.conf]).all() for d in detected)
    if len(detections) != 8 or not finite:
        raise RuntimeError("proxy detector returned invalid diagnostic output")
    return {
        "status": "passed", "semantics": "diagnostic counts only; no labelled accuracy",
        "path": str(proxy), "file_bytes": proxy.stat().st_size,
        "decoded_frames": len(frames), "decoded_frames_sha256": digest.hexdigest(),
        "decode_wall_ms": decode_ms, "detect_calls": 1,
        "detect_wall_ms": (time.perf_counter() - wall) * 1000,
        "detections": len(detected), "missing": 8 - len(detected), "finite_detections": finite,
    }


def _run(args: argparse.Namespace, report: dict[str, Any]) -> None:
    import numpy as np
    import torch

    from bai_badminton.perception import tracknet as candidate
    from bai_engine.obs import configure_logging
    from bai_engine.runtime.registry import ModelRegistry

    configure_logging()
    repo = Path(__file__).resolve().parents[1]
    if Path(candidate.__file__).resolve() != repo / SOURCE:
        raise RuntimeError("candidate import is not this checkout; set PYTHONPATH to engine/src and sports/badminton/src")
    registry_source = repo / "engine/src/bai_engine/runtime/registry.py"
    if Path(sys.modules[ModelRegistry.__module__].__file__).resolve() != registry_source:
        raise RuntimeError("ModelRegistry import is not this checkout")
    baseline_revision = _git(repo, "rev-parse", "--verify", "--end-of-options", f"{args.baseline_commit}^{{commit}}")
    report["source"] = {
        "baseline_revision": baseline_revision, "candidate_revision": _git(repo, "rev-parse", "HEAD"),
        "candidate_source_sha256": _sha256(repo / SOURCE),
        "candidate_worktree_changes": _git(repo, "status", "--porcelain", "--", SOURCE, "engine/src/bai_engine/runtime"),
        "harness_sha256": _sha256(Path(__file__)),
    }
    versions = {}
    for distribution in ("numpy", "torch", "onnx", "onnxscript", "onnxruntime", "onnxruntime-gpu"):
        try:
            versions[distribution] = importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            versions[distribution] = None
    report["environment"] = {"python": sys.version, "platform": platform.platform(), "packages": versions}
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; refusing a silent CPU parity run")
    properties = torch.cuda.get_device_properties(torch.cuda.current_device())
    report["environment"].update(
        cuda_build=torch.version.cuda, cudnn_version=torch.backends.cudnn.version(),
        gpu_name=properties.name, gpu_compute_capability=list(torch.cuda.get_device_capability()),
        gpu_total_memory_bytes=properties.total_memory, cuda_device=torch.cuda.current_device(),
    )
    torch.manual_seed(SEED)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.allow_tf32 = False
    torch.backends.cuda.matmul.allow_tf32 = False
    array = np.random.default_rng(SEED).random(INPUT_SHAPE, dtype=np.float32)
    tensor = torch.from_numpy(array).cuda()
    report["input"] = {
        "shape": list(INPUT_SHAPE), "dtype": "float32", "seed": SEED,
        "generator": "numpy.default_rng uniform [0,1)", "sha256": hashlib.sha256(array.tobytes()).hexdigest(),
        "cudnn_deterministic": True, "cudnn_benchmark": False, "tf32": False,
    }
    registry = ModelRegistry(args.models_dir)
    spec = registry.get(MODEL_NAME)
    pin = spec.sha256
    if pin in (None, "pin-on-first-fetch"):
        lock = json.loads((args.models_dir / "cache/lock.json").read_text(encoding="utf-8"))
        pin = lock.get(MODEL_NAME)
    if not isinstance(pin, str) or len(pin) != 64 or any(c not in "0123456789abcdef" for c in pin):
        raise RuntimeError("an existing TrackNet SHA256 integrity pin is required; no first-use pin will be written")
    with registry.open_verified(MODEL_NAME, fetch=False) as artifact, tempfile.TemporaryDirectory(
        prefix="baseline-", dir=args.output_dir
    ) as temporary:
        if artifact.sha256 != pin:
            raise RuntimeError("TrackNet registry pin changed during validation setup")
        baseline, source_sha = _baseline_module(repo, baseline_revision, Path(temporary))
        report["source"]["baseline_source_sha256"] = source_sha
        report["checkpoint"] = {"model": spec.ref, "path": str(artifact.path), "sha256": artifact.sha256}
        checkpoint = Path(temporary) / "verified_checkpoint.pt"
        with checkpoint.open("xb") as destination:
            shutil.copyfileobj(artifact.stream, destination, length=1 << 20)
        if _sha256(checkpoint) != artifact.sha256:
            raise RuntimeError("baseline snapshot differs from registry-verified checkpoint")
        detector = None
        try:
            report["baseline"] = {}
            wall = time.perf_counter()
            detector = baseline.TrackNetV3(checkpoint, backend="torch-cuda", precision="fp32")
            report["baseline"]["load_wall_ms"] = (time.perf_counter() - wall) * 1000
            baseline_output = _forward(detector, tensor, torch, report["baseline"])
        finally:
            del detector
            _release_cuda(torch)
        detector = None
        try:
            report["candidate"] = {}
            wall = time.perf_counter()
            artifact.stream.seek(0)
            detector = candidate.TrackNetV3(
                artifact.path, backend="torch-cuda", precision="fp32",
                checkpoint_stream=artifact.stream, expected_sha256=artifact.sha256,
            )
            report["candidate"]["load_wall_ms"] = (time.perf_counter() - wall) * 1000
            candidate_output = _forward(detector, tensor, torch, report["candidate"])
            difference = np.abs(baseline_output - candidate_output)
            report["torch_parity"] = {
                "max_abs_error": float(difference.max()), "mean_abs_error": float(difference.mean()),
                "exact_equal": bool(np.array_equal(baseline_output, candidate_output)),
                "allclose": bool(np.allclose(baseline_output, candidate_output, atol=1e-6, rtol=1e-5)),
                "atol": 1e-6, "rtol": 1e-5, "semantics": "tensor parity only; no accuracy measurement",
            }
            if args.proxy is not None:
                try:
                    report["proxy"] = _proxy_diagnostic(detector, args.proxy, torch)
                except Exception as error:
                    report["proxy"] = {"status": "failed", "error": _error(error)}
                    traceback.print_exc(file=sys.stderr)
            else:
                report["proxy"] = {"status": "not_requested"}
        finally:
            del detector, tensor
            _release_cuda(torch)
        cache = args.output_dir / "onnx-cache"
        cache.mkdir()
        report["onnx_export"] = {"status": "running", "fresh_cache": str(cache)}
        detector = None
        wall = time.perf_counter()
        try:
            artifact.stream.seek(0)
            detector = candidate.TrackNetV3(
                artifact.path, backend="onnx-cpu", onnx_dir=cache, providers=["CPUExecutionProvider"],
                checkpoint_stream=artifact.stream, expected_sha256=artifact.sha256,
            )
            report["onnx_export"].update(status="passed", runtime=dict(detector.runtime))
        except Exception as error:
            detail = _error(error)
            report["onnx_export"].update(
                status="unavailable_dependency" if detail["missing_dependencies"] else "failed", error=detail
            )
            traceback.print_exc(file=sys.stderr)
        finally:
            report["onnx_export"]["wall_ms"] = (time.perf_counter() - wall) * 1000
            report["onnx_export"]["files"] = [
                {"name": p.name, "bytes": p.stat().st_size, "sha256": _sha256(p)}
                for p in sorted(cache.iterdir()) if p.is_file()
            ]
            del detector
            gc.collect()
    if not report["torch_parity"]["allclose"]:
        report["status"] = "failed"
    elif report["onnx_export"]["status"] != "passed" or report["proxy"]["status"] == "failed":
        report["status"] = "partial"
    else:
        report["status"] = "passed"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--baseline-commit", default="27e2a20")
    parser.add_argument("--proxy", type=Path)
    args = parser.parse_args()
    args.models_dir, args.output_dir = args.models_dir.resolve(), args.output_dir.resolve()
    if not (args.models_dir / "manifest.yaml").is_file() or not (args.models_dir / "cache").is_dir():
        parser.error("models-dir must contain the existing manifest.yaml and cache directory")
    if args.output_dir.is_relative_to(args.models_dir) or args.models_dir.is_relative_to(args.output_dir):
        parser.error("output-dir must be outside, and cannot contain, models-dir")
    if args.output_dir.exists():
        parser.error("output-dir must be a fresh path")
    if args.proxy is not None:
        args.proxy = args.proxy.resolve()
    args.output_dir.mkdir(parents=True, exist_ok=False)
    report: dict[str, Any] = {
        "schema": 1, "status": "running", "started_utc": datetime.now(UTC).isoformat(),
        "scope": "trusted cached TrackNet FP32 CUDA parity, bounded proxy diagnostic and fresh ONNX export",
        "accuracy_evaluated": False, "downloads_or_installs": False,
    }
    report_path = args.output_dir / "report.json"
    try:
        with contextlib.redirect_stdout(sys.stderr):
            _run(args, report)
    except Exception as error:
        report.update(status="failed", error=_error(error))
        traceback.print_exc(file=sys.stderr)
    finally:
        report["finished_utc"] = datetime.now(UTC).isoformat()
        report_path.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
        print(f"{report['status']}: {report_path}", file=sys.stderr)
    return {"passed": 0, "failed": 1, "partial": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())
