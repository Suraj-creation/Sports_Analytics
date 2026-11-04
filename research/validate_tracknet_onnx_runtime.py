"""Validate existing TrackNet ONNX artifacts on the configured GPU server.

No downloads, installs or exports. Requires an existing integrity pin and graph
cache. Exit 0 means runtime parity passed, not labelled detection accuracy.
"""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import json
import os
import sys
import tempfile
import time
import traceback
from datetime import UTC, datetime
from pathlib import Path
from unittest.mock import patch

ATOL, RTOL, SEED = 1e-4, 1e-3, 20261103


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def fingerprint(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    stat = path.stat()
    return {"sha256": digest.hexdigest(), "bytes": stat.st_size, "mtime_ns": stat.st_mtime_ns}


def inventory(root):
    return {str(p.relative_to(root)): fingerprint(p) for p in sorted(root.rglob("*")) if p.is_file()}


def compare(reference, actual):
    import numpy as np

    difference = np.abs(reference - actual)
    return {"allclose": bool(np.allclose(reference, actual, atol=ATOL, rtol=RTOL)),
            "max_abs_error": float(difference.max()), "mean_abs_error": float(difference.mean())}


def proxy_diagnostic(path, detectors):
    import cv2
    import numpy as np

    require(path.is_file(), f"existing local proxy required: {path}")
    capture, frames, digest = cv2.VideoCapture(str(path)), [], hashlib.sha256()
    try:
        require(capture.isOpened(), f"cannot open proxy: {path}")
        for _ in range(8):
            ok, frame = capture.read()
            require(ok, f"proxy supplied only {len(frames)} frames; eight required")
            digest.update(str(frame.shape).encode())
            digest.update(frame.tobytes())
            frames.append(frame)
    finally:
        capture.release()
    results = {}
    for name, detector in detectors.items():
        rows = detector.detect(frames, shots=[0] * 8, step=8)
        require(len(rows) == 8, f"invalid {name} detection count")
        values = [None if row is None else [float(row.x), float(row.y), float(row.conf)] for row in rows]
        require(all(value is None or np.isfinite(value).all() for value in values), "nonfinite detection")
        results[name] = values
    agreement = {}
    for name in ("cpu", "cuda"):
        pairs = list(zip(results["torch"], results[name], strict=True))
        agreement[name] = {"presence_agreement_frames": sum((a is None) == (b is None) for a, b in pairs),
                           "position_confidence_allclose": all((a is None and b is None) or
                               (a is not None and b is not None and np.allclose(a, b, atol=ATOL, rtol=RTOL))
                               for a, b in pairs)}
    return {"path": str(path), "frames": 8, "decoded_sha256": digest.hexdigest(),
            "detections_xy_pixels_confidence": results, "agreement": agreement,
            "semantics": "diagnostic agreement only; no labelled accuracy"}


def run(args, report):
    import numpy as np
    import onnxruntime as ort
    import torch

    from bai_badminton.perception import tracknet
    from bai_engine.runtime.registry import ModelRegistry

    torch.set_num_threads(2)
    torch.set_num_interop_threads(2)
    torch.backends.cuda.matmul.allow_tf32 = False
    torch.backends.cudnn.allow_tf32 = False
    torch.manual_seed(SEED)
    repo = Path(__file__).resolve().parents[1]
    require(Path(tracknet.__file__).resolve() == repo / "sports/badminton/src/bai_badminton/perception/tracknet.py",
            "TrackNet import is not this checkout; set the existing GPU environment PYTHONPATH")
    registry_source = Path(sys.modules[ModelRegistry.__module__].__file__).resolve()
    require(registry_source == repo / "engine/src/bai_engine/runtime/registry.py", "registry is not this checkout")
    report["environment"] = {"python": sys.version, "torch": str(torch.__version__), "numpy": np.__version__,
                             "onnxruntime": ort.__version__, "available_providers": ort.get_available_providers(),
                             "torch_threads": 2, "torch_reference": "CPU FP32",
                             "cuda_visible_devices": os.environ.get("CUDA_VISIBLE_DEVICES")}
    require("CUDAExecutionProvider" in ort.get_available_providers(), "CUDAExecutionProvider unavailable")
    registry = ModelRegistry(args.models_dir)
    spec = registry.get("tracknetv3")
    pin = spec.sha256
    if pin in (None, "pin-on-first-fetch"):
        pin = json.loads((args.models_dir / "cache/lock.json").read_text())["tracknetv3"]
    require(isinstance(pin, str) and len(pin) == 64 and all(c in "0123456789abcdef" for c in pin),
            "existing SHA256 checkpoint pin required; first-use pinning forbidden")
    report["source"] = {"tracknet": fingerprint(Path(tracknet.__file__)), "registry": fingerprint(registry_source),
                        "harness": fingerprint(Path(__file__))}
    original_session, cuda_session = ort.InferenceSession, None

    def session_factory(*values, **keywords):
        nonlocal cuda_session
        # All sessions are real ORT; only thread limits, profiling and fallback policy are added.
        options = keywords.get("sess_options") or ort.SessionOptions()
        options.intra_op_num_threads = options.inter_op_num_threads = 2
        providers = keywords.get("providers", [])
        cuda = bool(providers and isinstance(providers[0], tuple) and providers[0][0] == "CUDAExecutionProvider")
        if cuda:
            options.enable_profiling = True
            options.profile_file_prefix = str(args.output_dir / "cuda-profile")
        keywords["sess_options"] = options
        session = original_session(*values, **keywords)
        session.disable_fallback()
        if cuda:
            cuda_session = session
            require(session.get_providers()[0] == "CUDAExecutionProvider", "CUDA session fell back to CPU")
        return session

    try:
        with registry.open_verified("tracknetv3", fetch=False) as artifact, patch.object(
            tracknet.TrackNetV3, "_publish_onnx", side_effect=RuntimeError("cache miss: export forbidden")
        ), patch.object(ort, "InferenceSession", side_effect=session_factory):
            require(artifact.sha256 == pin, "checkpoint pin changed")
            report["checkpoint"] = {"path": str(artifact.path), "sha256": artifact.sha256, "model": spec.ref}
            checkpoint_before = fingerprint(artifact.path)
            require(checkpoint_before["sha256"] == artifact.sha256, "checkpoint path changed after verification")

            def load(backend, providers=None):
                artifact.stream.seek(0)
                return tracknet.TrackNetV3(artifact.path, backend=backend, precision="fp32", batch=2,
                    onnx_dir=args.onnx_cache, providers=providers, checkpoint_stream=artifact.stream,
                    expected_sha256=artifact.sha256)

            reference = load("torch-cpu")
            reference._torch.float().cpu()
            require(next(reference._torch.parameters()).dtype == torch.float32, "Torch reference is not FP32")
            cpu = load("onnx-cpu", ["CPUExecutionProvider"])
            first_runtime = dict(cpu.runtime)
            del cpu
            cpu = load("onnx-cpu", ["CPUExecutionProvider"])
            require(first_runtime == cpu.runtime, "constructor reuse changed graph provenance")
            cuda = load("onnx-cuda", [("CUDAExecutionProvider", {"device_id": "0", "use_tf32": "0",
                                        "cudnn_conv_algo_search": "HEURISTIC"})])
            report["runtime"] = {"torch": reference.runtime, "cpu": cpu.runtime, "cuda": cuda.runtime}
            report["cuda_provider_options"] = cuda._ort.get_provider_options()
            require(not cpu.runtime["backend_fallback"] and not cuda.runtime["backend_fallback"], "provider fallback")
            require(cpu.runtime["onnx_sha256"] == cuda.runtime["onnx_sha256"], "CPU/CUDA graph digests differ")
            report["cache_reuse"] = {"constructors": 3, "export_forbidden": True,
                                      "same_cpu_provenance": True, "graph_sha256": cpu.runtime["onnx_sha256"]}
            report["batches"] = []
            for batch in (1, 2):
                array = np.random.default_rng(SEED + batch).random((batch, 27, 288, 512), dtype=np.float32)
                row = {"batch": batch, "seed": SEED + batch, "input_shape": list(array.shape),
                       "input_dtype": str(array.dtype), "input_finite": bool(np.isfinite(array).all()),
                       "input_sha256": hashlib.sha256(array.tobytes()).hexdigest(), "outputs": {}}
                report["batches"].append(row)
                outputs = {}
                for name, detector in {"torch": reference, "cpu": cpu, "cuda": cuda}.items():
                    started = time.perf_counter()
                    output = (detector._forward(array) if name == "torch" else
                              detector._ort.run(["heatmaps"], {"frames": array})[0])
                    finite = bool(np.isfinite(output).all())
                    row["outputs"][name] = {"shape": list(output.shape), "dtype": str(output.dtype), "finite": finite,
                                             "wall_ms": (time.perf_counter() - started) * 1000}
                    require(output.shape == (batch, 8, 288, 512) and output.dtype == np.float32 and finite,
                            f"{name} batch {batch} violates heatmap IO contract")
                    outputs[name] = output
                row["comparisons"] = {"torch_cpu": compare(outputs["torch"], outputs["cpu"]),
                    "torch_cuda": compare(outputs["torch"], outputs["cuda"]),
                    "cpu_cuda": compare(outputs["cpu"], outputs["cuda"])}
            if args.proxy:
                report["proxy"] = proxy_diagnostic(args.proxy, {"torch": reference, "cpu": cpu, "cuda": cuda})
            report["checkpoint"]["unchanged"] = checkpoint_before == fingerprint(artifact.path)
            require(report["checkpoint"]["unchanged"], "checkpoint path changed during validation")
            require(all(c["allclose"] for row in report["batches"] for c in row["comparisons"].values()),
                    "heatmap numerical parity exceeds declared tolerance")
    finally:
        if cuda_session is not None:
            try:
                profile = Path(cuda_session.end_profiling())
                events = json.loads(profile.read_text())
                nodes = [dict(name=e.get("name"), provider=e["args"]["provider"], op=e["args"].get("op_name"))
                         for e in events if e.get("cat") == "Node" and e.get("args", {}).get("provider")]
                report["node_placement"] = {"profile": str(profile), "nodes": nodes,
                    "cpu_nodes": [n for n in nodes if n["provider"] == "CPUExecutionProvider"],
                    "note": "CPU shape/control nodes are reported; CUDA compute execution is required"}
                report["cuda_compute_executed"] = any(n["provider"] == "CUDAExecutionProvider" and
                                                     "Conv" in (n["op"] or "") for n in nodes)
            except Exception as error:
                report["profiling_error"] = str(error)
    require(report.get("cuda_compute_executed"), "profiling did not establish actual CUDA convolution execution")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("models-dir", "onnx-cache", "output-dir"):
        parser.add_argument(f"--{name}", type=Path, required=True)
    parser.add_argument("--proxy", type=Path)
    report = {"schema": 1, "status": "failed", "started_utc": datetime.now(UTC).isoformat(),
              "atol": ATOL, "rtol": RTOL, "accuracy_evaluated": False, "downloads_installs_exports": False}
    report_path, before = None, None
    try:
        args = parser.parse_args()
        args.models_dir, args.onnx_cache, args.output_dir = (p.resolve() for p in
            (args.models_dir, args.onnx_cache, args.output_dir))
        if args.proxy:
            args.proxy = args.proxy.resolve()
        require(all(not args.output_dir.is_relative_to(p) and not p.is_relative_to(args.output_dir)
                    for p in (args.models_dir, args.onnx_cache)),
                "output must be separate from existing model/cache trees")
        args.output_dir.mkdir(parents=True, exist_ok=False)
        report_path = args.output_dir / "report.json"
        report["paths"] = {name: str(getattr(args, name)) for name in ("models_dir", "onnx_cache", "output_dir")}
        require((args.models_dir / "manifest.yaml").is_file() and (args.models_dir / "cache").is_dir(),
                "existing models required")
        require(args.onnx_cache.is_dir(), "existing ONNX cache required")
        before = inventory(args.onnx_cache)
        report["cache_before"] = before
        with contextlib.redirect_stdout(sys.stderr):
            run(args, report)
        report["status"] = "passed"
    except BaseException as error:
        if isinstance(error, SystemExit) and error.code == 0:
            report["status"] = "help"
        else:
            report.update(status="failed", error={"type": type(error).__name__, "message": str(error),
                                                  "traceback": traceback.format_exc()})
    finally:
        if before is not None:
            try:
                report["cache_after"] = inventory(args.onnx_cache)
                report["cache_unchanged"] = before == report["cache_after"]
                if not report["cache_unchanged"]:
                    report["status"] = "failed"
            except Exception as error:
                report.update(status="failed", cache_check_error=str(error))
        report["finished_utc"] = datetime.now(UTC).isoformat()
        encoded = json.dumps(report, indent=2, allow_nan=False) + "\n"
        if report_path is None:  # Preserve unsafe/existing output paths while still persisting the failure.
            report_path = Path(tempfile.mkdtemp(prefix="tracknet-onnx-failure-")) / "report.json"
        report_path.write_text(encoded, encoding="utf-8")
        print(f"{report['status']}: {report_path}", file=sys.stderr)
    return 0 if report["status"] in ("passed", "help") else 1


if __name__ == "__main__":
    raise SystemExit(main())
