"""Small existing-model GPU probe; never exports, downloads or edits a model.

ORT profiling reports executed kernel placement, not provider-registration
labels. Torch hooks report actual tensor/device/dtype metadata. Repeated fixed
inputs and tiny profiled samples are not full-pipeline performance evidence.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import platform
import resource
import statistics
import subprocess
import threading
import time
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def summarize_latencies_ms(values):
    if any(type(v) not in (int, float) or not math.isfinite(v) or v < 0 for v in values):
        raise ValueError("latency values must be finite nonnegative milliseconds")
    if not values:
        return dict(count=0, mean=None, median=None, minimum=None, maximum=None, p95=None)
    ordered = sorted(values)
    index = 0.95 * (len(ordered) - 1)
    low = int(index)
    p95 = ordered[low] + (ordered[min(low + 1, len(ordered) - 1)] - ordered[low]) * (index - low)
    return dict(
        count=len(values),
        mean=statistics.fmean(values),
        median=statistics.median(values),
        minimum=min(values),
        maximum=max(values),
        p95=p95,
    )


def placement_summary(events):
    """Summed profiled kernel durations are not wall-time fractions or GPU busy time."""
    providers, nodes, types = {}, {}, set()
    missing, kernels = 0, 0
    identities = defaultdict(set)
    for event in events:
        if event.get("cat") != "Node" or event.get("ph") != "X" or not event.get("name", "").endswith("_kernel_time"):
            continue
        kernels += 1
        duration = event.get("dur")
        if type(duration) not in (int, float) or not math.isfinite(duration) or duration < 0:
            raise ValueError("profile kernel duration must be finite nonnegative microseconds")
        args = event.get("args", {})
        provider, op, index = args.get("provider"), args.get("op_name", "unknown"), args.get("node_index", "unknown")
        if not provider:
            missing += 1
            continue
        identity = f"{index}:{event['name']}:{op}"
        identities[identity].add(provider)
        key = identity + ":" + provider
        node = nodes.setdefault(
            key,
            {"identity": identity, "provider": provider, "op": op, "executions": 0, "summed_kernel_duration_us": 0.0},
        )
        node["executions"] += 1
        node["summed_kernel_duration_us"] += duration
        record = providers.setdefault(
            provider,
            {
                "kernel_events": 0,
                "unique_nodes": set(),
                "summed_kernel_duration_us": 0.0,
                "compute_events": 0,
                "transfer_events": 0,
                "op_event_counts": Counter(),
            },
        )
        record["kernel_events"] += 1
        record["unique_nodes"].add(identity)
        record["summed_kernel_duration_us"] += duration
        record["transfer_events" if op.startswith("Memcpy") else "compute_events"] += 1
        record["op_event_counts"][op] += 1
        for field in ("input_type_shape", "output_type_shape"):
            metadata = args.get(field, [])
            if isinstance(metadata, str):
                try:
                    metadata = json.loads(metadata)
                except json.JSONDecodeError:
                    metadata = []
            if isinstance(metadata, list):
                for value in metadata:
                    if isinstance(value, dict):
                        types.update(value)
    if not kernels:
        raise ValueError("profile has no executed ORT kernel events; provider placement is unmeasured")
    for value in providers.values():
        value["unique_nodes"] = len(value["unique_nodes"])
        value["op_event_counts"] = dict(sorted(value["op_event_counts"].items()))
    return {
        "kernel_events": kernels,
        "kernel_events_without_provider": missing,
        "providers": providers,
        "observed_nodes": list(nodes.values()),
        "nodes_with_multiple_providers": sorted(key for key, value in identities.items() if len(value) > 1),
        "actual_cuda_kernel_events": providers.get("CUDAExecutionProvider", {}).get("kernel_events", 0),
        "observed_tensor_types": sorted(types),
        "duration_semantics": (
            "Sum of profiled executed-node durations in microseconds; not a critical-path or wall-time fraction."
        ),
        "precision_limit": "Tensor metadata does not prove accumulator precision or hardware execution units.",
    }


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def compute_processes(nvml):
    result = []
    for index in range(nvml.nvmlDeviceGetCount()):
        handle = nvml.nvmlDeviceGetHandleByIndex(index)
        for process in nvml.nvmlDeviceGetComputeRunningProcesses(handle):
            result.append({"gpu_index": index, "pid": process.pid, "gpu_memory_bytes": int(process.usedGpuMemory)})
    return result


def ensure_isolated(nvml, gpu_index):
    foreign = [p for p in compute_processes(nvml) if p["gpu_index"] == gpu_index and p["pid"] != os.getpid()]
    pipeline = []
    for process in Path("/proc").iterdir():
        if not process.name.isdigit() or int(process.name) == os.getpid():
            continue
        try:
            command = (process / "cmdline").read_bytes().split(b"\0")
            if any(
                Path(part.decode(errors="replace")).name == "run_pipeline_experiment.py" for part in command if part
            ):
                pipeline.append(int(process.name))
        except (PermissionError, FileNotFoundError, ProcessLookupError):
            continue
    if foreign or pipeline:
        raise RuntimeError(
            f"probe requires an idle allocated GPU and no full pipeline: foreign={foreign}, pipelines={pipeline}"
        )


class ResourceSampler:
    """Discrete NVML/PID samples; no claim of a continuous resource maximum."""

    def __init__(self, nvml, gpu_index):
        self.nvml, self.gpu_index = nvml, gpu_index
        self.stop = threading.Event()
        self.samples = []

    def _sample(self):
        handle = self.nvml.nvmlDeviceGetHandleByIndex(self.gpu_index)
        processes = compute_processes(self.nvml)
        self.samples.append(
            {
                "elapsed_s": time.perf_counter() - self.started,
                "rss_bytes": int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE"),
                "gpu_device_used_bytes": self.nvml.nvmlDeviceGetMemoryInfo(handle).used,
                "gpu_util_percent": self.nvml.nvmlDeviceGetUtilizationRates(handle).gpu,
                "gpu_power_w": self.nvml.nvmlDeviceGetPowerUsage(handle) / 1000.0,
                "gpu_pid_bytes": max(
                    [
                        p["gpu_memory_bytes"]
                        for p in processes
                        if p["gpu_index"] == self.gpu_index and p["pid"] == os.getpid()
                    ],
                    default=0,
                ),
                "foreign_gpu_pids": [
                    p["pid"] for p in processes if p["gpu_index"] == self.gpu_index and p["pid"] != os.getpid()
                ],
            }
        )

    def _loop(self):
        while not self.stop.wait(0.05):
            self._sample()

    def __enter__(self):
        self.started = time.perf_counter()
        self.cpu_start = resource.getrusage(resource.RUSAGE_SELF)
        self._sample()
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop.set()
        self.thread.join()
        self._sample()
        end = resource.getrusage(resource.RUSAGE_SELF)
        self.summary = {
            "sample_count": len(self.samples),
            "nominal_interval_s": 0.05,
            "scope": "model loading and limited forwards in this process; sampled maxima, not continuous peaks",
            "wall_seconds": time.perf_counter() - self.started,
            "cpu_seconds": end.ru_utime + end.ru_stime - self.cpu_start.ru_utime - self.cpu_start.ru_stime,
            **{
                "sampled_max_" + field: max(s[field] for s in self.samples)
                for field in ("rss_bytes", "gpu_device_used_bytes", "gpu_util_percent", "gpu_power_w", "gpu_pid_bytes")
            },
            "foreign_gpu_pids": sorted({pid for row in self.samples for pid in row["foreign_gpu_pids"]}),
        }


def source_frames(video, start):
    import av

    frames, identities = [], []
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        if float(stream.average_rate) != 30.0:
            raise ValueError("this limited Test1 probe requires the verified 30FPS source")
        container.seek(int(start / 30 / stream.time_base), stream=stream, backward=True)
        for frame in container.decode(stream):
            exact = float(frame.pts * stream.time_base * 30)
            index = int(round(exact))
            if abs(exact - index) > 1e-6:
                raise ValueError("source PTS does not map to the declared CFR source index")
            if index < start:
                continue
            if index >= start + 8:
                break
            frames.append(frame.to_ndarray(format="bgr24"))
            identities.append({"source_frame": index, "pts": frame.pts, "time_base": str(stream.time_base)})
    if [r["source_frame"] for r in identities] != list(range(start, start + 8)):
        raise ValueError("exact eight-frame source window unavailable")
    return frames, identities


def ort_probe(path, data, name, output, warm_count, nvml, gpu_index):
    import onnxruntime as ort

    from bai_engine.runtime.device import ort_providers

    ensure_isolated(nvml, gpu_index)
    options = ort.SessionOptions()
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    options.enable_profiling = True
    options.profile_file_prefix = str(output / (name + "_ort_profile"))
    with ResourceSampler(nvml, gpu_index) as resources:
        started = time.perf_counter()
        session = ort.InferenceSession(str(path), sess_options=options, providers=ort_providers("onnx-cuda"))
        setup_ms = (time.perf_counter() - started) * 1000
        inputs, outputs = session.get_inputs(), session.get_outputs()
        if len(inputs) != 1:
            raise ValueError("probe supports the existing single-input image models only")
        feeds = {inputs[0].name: data}
        times, hashes = [], []
        for _ in range(warm_count + 1):
            ensure_isolated(nvml, gpu_index)
            started = time.perf_counter()
            values = session.run(None, feeds)
            times.append((time.perf_counter() - started) * 1000)
            hashes.append([hashlib.sha256(v.tobytes()).hexdigest() for v in values])
        profile = Path(session.end_profiling())
        result = {
            "name": name,
            "path": str(path),
            "sha256": digest(path),
            "requested_backend": "onnx-cuda",
            "session_providers": session.get_providers(),
            "provider_options": session.get_provider_options(),
            "session_setup_ms": setup_ms,
            "first_forward_ms": times[0],
            "warm_forward_ms": summarize_latencies_ms(times[1:]),
            "all_forward_ms": times,
            "input_dtype": str(data.dtype),
            "input_shape": list(data.shape),
            "graph_inputs": [{"name": v.name, "type": v.type, "shape": v.shape} for v in inputs],
            "graph_outputs": [{"name": v.name, "type": v.type, "shape": v.shape} for v in outputs],
            "output_dtypes": [str(v.dtype) for v in values],
            "output_shapes": [list(v.shape) for v in values],
            "fixed_input_output_hashes_identical": all(value == hashes[0] for value in hashes),
            "output_sha256": hashes,
            "profile_path": str(profile),
            "profile_sha256": digest(profile),
            "placement": placement_summary(json.loads(profile.read_text())),
            "limits": [
                "Profiling and resource-sampling overhead included",
                "Two ORT intra-op threads and one inter-op thread are explicit probe settings",
                "Input preparation, decoding and output postprocessing excluded",
                "First forward is a new-session sample, not a cold machine",
            ],
        }
        del session
        gc.collect()
    result["resources"] = resources.summary
    (output / (name + "_resources.json")).write_text(json.dumps(resources.samples, indent=2) + "\n")
    return result


def torch_probe(path, expected, frames, precision, output, warm_count, nvml, gpu_index):
    import numpy as np
    import torch

    from bai_badminton.perception.tracknet import HEIGHT, WIDTH, TrackNetV3

    ensure_isolated(nvml, gpu_index)
    torch.cuda.reset_peak_memory_stats()
    with ResourceSampler(nvml, gpu_index) as resources:
        started = time.perf_counter()
        model = TrackNetV3(path, backend="torch-cuda", precision=precision, batch=1, expected_sha256=expected)
        torch.cuda.synchronize()
        setup_ms = (time.perf_counter() - started) * 1000
        small = model._prep(frames, [0] * 8)
        background = model.bg.get(0, small[0])
        stack = np.concatenate([background[None], np.stack(small)], axis=0)
        data = np.moveaxis(stack, -1, 1).reshape(1, model.in_dim, HEIGHT, WIDTH).astype(np.float32) / 255.0
        actual = {}

        def tensor_metadata(value):
            return {"dtype": str(value.dtype), "device": str(value.device), "shape": list(value.shape)}

        def before(_module, args):
            actual.setdefault("network_input", tensor_metadata(args[0]))

        def after(_module, _args, value):
            actual.setdefault("network_output", tensor_metadata(value))

        handles = [model._torch.register_forward_pre_hook(before), model._torch.register_forward_hook(after)]
        times, hashes = [], []
        for _ in range(warm_count + 1):
            ensure_isolated(nvml, gpu_index)
            torch.cuda.synchronize()
            started = time.perf_counter()
            value = model._forward(data)
            torch.cuda.synchronize()
            times.append((time.perf_counter() - started) * 1000)
            hashes.append(hashlib.sha256(value.tobytes()).hexdigest())
        for handle in handles:
            handle.remove()
        result = {
            "name": "tracknet_" + precision,
            "path": str(path),
            "sha256": digest(path),
            "runtime": model.runtime,
            "model_setup_ms": setup_ms,
            "first_forward_ms": times[0],
            "warm_forward_ms": summarize_latencies_ms(times[1:]),
            "all_forward_ms": times,
            "parameter_devices": sorted({str(p.device) for p in model._torch.parameters()}),
            "parameter_dtypes": sorted({str(p.dtype) for p in model._torch.parameters()}),
            "buffer_dtypes": sorted({str(p.dtype) for p in model._torch.buffers()}),
            "actual_tensors": actual,
            "exported_array_dtype": str(value.dtype),
            "output_shape": list(value.shape),
            "input_sha256": hashlib.sha256(data.tobytes()).hexdigest(),
            "output_sha256": hashes,
            "fixed_input_output_hashes_identical": len(set(hashes)) == 1,
            "torch_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "torch_peak_reserved_bytes": torch.cuda.max_memory_reserved(),
            "limits": [
                "One eight-frame input with local eight-frame background, not full-context benchmark parity",
                "Actual production _forward includes NumPy-to-device and FP32-array output transfer",
                "Parameter/input/output dtype does not prove accumulator precision or per-op kernel units",
                "No Torch graph conversion or alternative weights",
            ],
        }
        np.save(output / ("tracknet_" + precision + "_heatmaps.npy"), value)
        del model
        gc.collect()
        torch.cuda.empty_cache()
    result["resources"] = resources.summary
    (output / ("tracknet_" + precision + "_resources.json")).write_text(json.dumps(resources.samples, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--gpu-index", type=int, choices=[1], default=1)
    parser.add_argument("--warm-count", type=int, choices=range(1, 11), default=5)
    parser.add_argument("--source-frame", type=int, default=12760)
    args = parser.parse_args()
    original_cuda_visible = os.environ.get("CUDA_VISIBLE_DEVICES")
    os.environ["CUDA_VISIBLE_DEVICES"] = str(args.gpu_index)
    import cv2
    import numpy as np
    import onnxruntime as ort
    import pynvml as nvml
    import torch
    import yaml
    from rtmlib import RFDETR, RTMPose

    args.output = args.output.resolve()
    args.output.mkdir(parents=True, exist_ok=False)
    nvml.nvmlInit()
    ensure_isolated(nvml, args.gpu_index)
    initial_processes = compute_processes(nvml)
    torch.set_num_threads(2)
    torch.cuda.set_device(0)  # Only the allocated physical GPU1 is visible.
    snapshots = [
        Path(__file__),
        ROOT / "models/manifest.yaml",
        ROOT / "models/cache/lock.json",
        ROOT / "sports/badminton/src/bai_badminton/perception/tracknet.py",
        ROOT / "sports/badminton/src/bai_badminton/perception/players.py",
        ROOT / "engine/src/bai_engine/runtime/device.py",
    ]
    source_bytes = {path: path.read_bytes() for path in snapshots}
    lock = json.loads((ROOT / "models/cache/lock.json").read_text())
    registry = yaml.safe_load((ROOT / "models/manifest.yaml").read_text())["models"]
    tracknet = ROOT / "models/cache/tracknetv3/TrackNet_best.pt"
    detector = ROOT / "models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx"
    pose_manifest = next((ROOT / "models/cache/rtmpose_m_body7/extracted-v1").glob("*/manifest.json"))
    pose_metadata = json.loads(pose_manifest.read_text())
    pose = pose_manifest.parent / "files" / pose_metadata["graph"]
    for path, expected in (
        (tracknet, lock["tracknetv3"]),
        (detector, lock["rfdetr_small"]),
        (pose, pose_metadata["files"][pose_metadata["graph"]]),
    ):
        if digest(path) != expected:
            raise ValueError(f"existing model digest mismatch: {path}")
    if pose_metadata["archive_sha256"] != lock["rtmpose_m_body7"]:
        raise ValueError("pose extraction provenance does not match the frozen registry lock")
    video = ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4"
    frames, identities = source_frames(video, args.source_frame)
    image = cv2.cvtColor(frames[0], cv2.COLOR_BGR2RGB)
    det_tool = RFDETR.__new__(RFDETR)
    det_tool.model_input_size = (512, 512)
    det_tool.mean = np.asarray((0.485, 0.456, 0.406), dtype=np.float32)
    det_tool.std = np.asarray((0.229, 0.224, 0.225), dtype=np.float32)
    det_input = np.ascontiguousarray(det_tool.preprocess(image)[0].transpose(2, 0, 1)[None], dtype=np.float32)
    pose_tool = RTMPose.__new__(RTMPose)
    pose_tool.model_input_size = (192, 256)
    pose_tool.mean, pose_tool.std = (123.675, 116.28, 103.53), (58.395, 57.12, 57.375)
    # Fixed original-frame crop, within the authorized video; not a detection label.
    bbox = [770.0, 595.0, 870.0, 870.0]
    pose_input = np.ascontiguousarray(pose_tool.preprocess(image, bbox)[0].transpose(2, 0, 1)[None], dtype=np.float32)
    report = {
        "schema": "existing-model-runtime-probe:v1",
        "mode": "limited real fixed-input model probe, not a complete pipeline benchmark",
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "gpu_index_physical": args.gpu_index,
        "cuda_visible_devices_prior": original_cuda_visible,
        "cuda_visible_devices_probe": os.environ["CUDA_VISIBLE_DEVICES"],
        "initial_compute_processes": initial_processes,
        "environment": {
            "python": platform.python_version(),
            "torch": torch.__version__,
            "torch_cuda": torch.version.cuda,
            "torch_compiled_arches": torch.cuda.get_arch_list(),
            "onnxruntime": ort.__version__,
            "ort_available_providers": ort.get_available_providers(),
            "torch_visible_devices": torch.cuda.device_count(),
            "torch_device": str(torch.cuda.get_device_properties(0)),
            "driver": nvml.nvmlSystemGetDriverVersion(),
            "cudnn": torch.backends.cudnn.version(),
            "cudnn_benchmark": torch.backends.cudnn.benchmark,
            "float32_matmul_precision": torch.get_float32_matmul_precision(),
        },
        "gpus": [
            {
                "index": i,
                "uuid": nvml.nvmlDeviceGetUUID(nvml.nvmlDeviceGetHandleByIndex(i)),
                "name": nvml.nvmlDeviceGetName(nvml.nvmlDeviceGetHandleByIndex(i)),
                "total_bytes": nvml.nvmlDeviceGetMemoryInfo(nvml.nvmlDeviceGetHandleByIndex(i)).total,
            }
            for i in range(nvml.nvmlDeviceGetCount())
        ],
        "input": {
            "video": str(video),
            "video_sha256": digest(video),
            "frames": identities,
            "detector_scope": "whole original image resized by existing RFDETR preprocess; not production court ROI",
            "pose_scope": "one fixed original-image bbox, not reviewed ground truth",
            "pose_bbox": bbox,
            "detector_tensor_sha256": hashlib.sha256(det_input.tobytes()).hexdigest(),
            "pose_tensor_sha256": hashlib.sha256(pose_input.tobytes()).hexdigest(),
        },
        "licenses_from_local_registry": {
            key: registry[key]["license"] for key in ("tracknetv3", "rfdetr_small", "rtmpose_m_body7")
        },
        "license_limit": (
            "Existing locally registered artifacts only; mirror and training-data rights "
            "are not newly audited or expanded by this probe."
        ),
        "models": [],
    }
    report["models"].append(
        ort_probe(detector, det_input, "rfdetr_small", args.output, args.warm_count, nvml, args.gpu_index)
    )
    report["models"].append(
        ort_probe(pose, pose_input, "rtmpose_m", args.output, args.warm_count, nvml, args.gpu_index)
    )
    for precision in ("fp16", "fp32"):
        report["models"].append(
            torch_probe(
                tracknet, lock["tracknetv3"], frames, precision, args.output, args.warm_count, nvml, args.gpu_index
            )
        )
    fp16 = np.load(args.output / "tracknet_fp16_heatmaps.npy")
    fp32 = np.load(args.output / "tracknet_fp32_heatmaps.npy")
    report["precision_diagnostic"] = {
        "same_input": report["models"][2]["input_sha256"] == report["models"][3]["input_sha256"],
        "finite_fp16": bool(np.isfinite(fp16).all()),
        "finite_fp32": bool(np.isfinite(fp32).all()),
        "max_absolute_heatmap_difference": float(np.max(np.abs(fp16 - fp32))),
        "mean_absolute_heatmap_difference": float(np.mean(np.abs(fp16 - fp32))),
        "meaning": "Numeric difference on one fixed model input; no localization or sporting accuracy label",
    }
    report["source_unchanged"] = all(path.read_bytes() == data for path, data in source_bytes.items())
    if not report["source_unchanged"]:
        raise RuntimeError("a probed runtime source changed during execution")
    ensure_isolated(nvml, args.gpu_index)
    (args.output / "runtime_probe.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    copies = args.output / "executed_source"
    copies.mkdir()
    for path, data in source_bytes.items():
        (copies / path.name).write_bytes(data)
    manifest = {
        "source_sha256": {
            str(p.relative_to(ROOT)): hashlib.sha256(data).hexdigest() for p, data in source_bytes.items()
        },
        "output_sha256": {str(p.relative_to(args.output)): digest(p) for p in args.output.iterdir() if p.is_file()},
        "pose_extraction_manifest": str(pose_manifest),
        "pose_extraction_manifest_sha256": digest(pose_manifest),
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(
        json.dumps(
            {
                "models": [
                    {"name": m["name"], "first_ms": m["first_forward_ms"], "warm_ms": m["warm_forward_ms"]}
                    for m in report["models"]
                ],
                "source_unchanged": report["source_unchanged"],
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
