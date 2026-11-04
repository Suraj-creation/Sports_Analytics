"""Actual, controlled TrackNet step8/4 component experiment on fixed diagnostic windows.

No rally predictions or localization-accuracy claim: labels only select review cases.
Use CUDA_VISIBLE_DEVICES=1 and the existing GPU environment. Baseline is read only.
"""

from __future__ import annotations

import contextlib
import csv
import hashlib
import importlib.metadata
import json
import os
import sqlite3
import subprocess
import time
from datetime import UTC, datetime
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np
import torch

from bai_badminton.court import REFERENCE_POINTS
from bai_badminton.perception.isolation import flight_mask
from bai_badminton.perception.tracknet import HEIGHT, WIDTH, BackgroundModel, TrackNetV3
from bai_engine.runtime.registry import ModelRegistry

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "outputs/benchmarking/test1"
OUTPUT = ROOT / "artifacts/benchmarking/experiments/tracknet_window_pair"
# Frozen before component inference. Each window lies inside its recorded case package.
WINDOWS = [
    ("gt_02", 960, 1139),
    ("gt_05", 2220, 2399),
    ("gt_19", 8220, 8399),
    ("gt_20", 9480, 9659),
    ("gt_23", 10860, 11039),
    ("gt_25", 11700, 11879),
    ("gt_27", 12720, 12899),
    ("gt_28", 13020, 13199),
    ("gt_29", 13800, 13979),
    ("gt_31", 14610, 14789),
    ("gt_07", 3000, 3179),
    ("gt_32", 15360, 15539),
]


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def array_sha(value):
    return hashlib.sha256(np.ascontiguousarray(value).tobytes()).hexdigest()


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


class FrozenBackground(BackgroundModel):
    """Experimental control: identical immutable RGB median for every strategy/window."""

    def __init__(self, rgb):
        super().__init__()
        self.rgb = rgb.copy()
        self.rgb.flags.writeable = False

    def observe(self, shot, rgb_small):
        pass

    def retain(self, shots):
        pass

    def get(self, shot, fallback):
        return self.rgb


def decode(container, first, last):
    stream = container.streams.video[0]
    target = int(round((first / 30) / float(stream.time_base)))
    container.seek(target, stream=stream, backward=True)
    images = []
    for frame in container.decode(stream):
        idx = round(float(frame.pts * stream.time_base) * 30)
        if idx < first:
            continue
        if idx > last:
            break
        if idx != first + len(images):
            raise ValueError(f"decoded frame mismatch: wanted {first + len(images)}, got {idx}")
        images.append(frame.to_ndarray(format="bgr24"))
    if len(images) != last - first + 1:
        raise ValueError("incomplete diagnostic window decode")
    return images


def gap_runs(visible, first):
    gaps = []
    start = None
    for i, value in enumerate([*visible, True]):
        if not value and start is None:
            start = i
        if value and start is not None:
            gaps.append({"start": first + start, "end": first + i - 1, "length": i - start})
            start = None
    return gaps


def run():
    if os.environ.get("CUDA_VISIBLE_DEVICES") != "1":
        raise RuntimeError("isolate experiment on physical GPU1 using CUDA_VISIBLE_DEVICES=1")
    if not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("one isolated CUDA device is required")
    torch.manual_seed(0)
    torch.cuda.manual_seed_all(0)
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    meta = json.loads((BASE / "benchmark_metadata.json").read_text())
    proxy = BASE / "runtime/media" / meta["source_video_sha256"] / "proxy.mp4"
    if sha(proxy) != meta["proxy_sha256"]:
        raise ValueError("proxy hash mismatch")
    component_files = [
        ROOT / "sports/badminton/src/bai_badminton/perception/tracknet.py",
        ROOT / "sports/badminton/src/bai_badminton/perception/isolation.py",
    ]
    hashes = {str(p.relative_to(ROOT)): sha(p) for p in component_files}
    for path, value in hashes.items():
        if value != meta["production_source_hashes"][path]:
            raise ValueError(f"paired experiment requires unchanged baseline component: {path}")
    case_root = ROOT / "artifacts/benchmarking/investigation/failure_cases"
    cases = {}
    for name, first, last in WINDOWS:
        case_path = case_root / name / "case.json"
        case = json.loads(case_path.read_text())
        lo, hi = case["original_frame_range_inclusive"]
        if not lo <= first <= last <= hi:
            raise ValueError("review window outside original case")
        cases[name] = {"case_json_sha256": sha(case_path), "frames_inclusive": [first, last], "tags": case["tags"]}
    rows = {}
    cache_root = BASE / "runtime/sessions/BenchmarkTest1/perception"
    needed = {i for _, first, last in WINDOWS for i in range(first, last + 1)}
    cache_hashes = {}
    for path in sorted(cache_root.glob("*.msgpack")):
        d = msgpack.unpackb(path.read_bytes(), raw=False)
        if d["end"] < min(needed) or d["start"] > max(needed):
            continue
        selected = [f for f in d["frames"] if f["f"] in needed]
        if selected:
            cache_hashes[path.name] = sha(path)
            rows.update({f["f"]: f for f in selected})
    if set(rows) != needed:
        raise ValueError("incomplete cached mask/camera metadata")
    store = BASE / "runtime/sessions/BenchmarkTest1/events.sqlite"
    with sqlite3.connect(f"file:{store}?mode=ro", uri=True) as connection:
        records = connection.execute("SELECT body FROM events WHERE type='calibration' ORDER BY seq").fetchall()
    if len(records) != 1:
        raise RuntimeError("this control requires the one verified fixed-camera calibration")
    h = np.asarray(json.loads(records[0][0])["payload"]["H"], np.float64)
    corners = np.array([REFERENCE_POINTS[n] for n in ("far_left", "far_right", "near_right", "near_left")])
    reference_poly = cv2.perspectiveTransform(corners.reshape(-1, 1, 2), h).reshape(-1, 2)
    # Source-independent uniform sampling; labels are not consulted for background generation.
    sample_indices = [round((i + 0.5) * 17268 / 24) for i in range(24)]
    with av.open(str(proxy)) as container:
        samples = [
            cv2.cvtColor(
                cv2.resize(decode(container, i, i)[0], (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB
            )
            for i in sample_indices
        ]
    background = np.median(np.stack(samples), axis=0).astype(np.uint8)
    cv2.imwrite(str(OUTPUT / "frozen_background.png"), cv2.cvtColor(background, cv2.COLOR_RGB2BGR))
    manifest = {
        "status": "running",
        "scope": "actual paired component inference only; no full-pipeline benchmark claim",
        "execution_date": datetime.now(UTC).isoformat(),
        "git_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "git_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        "component_source_sha256": hashes,
        "script_sha256": sha(Path(__file__)),
        "source_video_sha256": meta["source_video_sha256"],
        "proxy_sha256": meta["proxy_sha256"],
        "ground_truth_sha256": meta["ground_truth_sha256"],
        "baseline_prediction_sha256": meta["prediction_sha256"],
        "fps": 30,
        "frame_convention": "zero-based CFR proxy and source indices, verified unchanged baseline timeline",
        "physical_gpu": 1,
        "logical_cuda_device": 0,
        "cuda_visible_devices": "1",
        "gpu_name": torch.cuda.get_device_name(0),
        "torch_cuda_version": torch.version.cuda,
        "runtime_versions": {k: importlib.metadata.version(k) for k in ("torch", "numpy", "av", "opencv-python")},
        "config": {
            "model": "tracknetv3",
            "backend": "torch-cuda",
            "precision": "fp16",
            "batch": 4,
            "threshold": 0.5,
            "seq_len": 8,
            "input_size": [512, 288],
            "steps": [8, 4],
        },
        "determinism": {"seed": 0, "cudnn_benchmark": False, "cudnn_deterministic": True},
        "background": {
            "method": "fixed uniform-24-frame RGB median; identical every pair; rolling observation disabled",
            "sample_frame_indices": sample_indices,
            "rgb_array_sha256": array_sha(background),
            "baseline_background_equivalence": False,
        },
        "mask": (
            "production flight_mask on baseline fixed reference court transformed by cached per-frame camera; "
            "zero non-main/lost masks"
        ),
        "cases": cases,
        "cache_sha256": cache_hashes,
        "annotations_usage": "case metadata selects fixed review windows only; no labels/boundaries given to detector",
        "limitations": [
            "No independent shuttle pixel/visibility labels",
            "Different fixed background from original rolling baseline",
            "180-frame component windows differ from original60-frame chunk context",
            "No rally segmentation or F1 improvement claim",
        ],
    }
    dump(OUTPUT / "manifest.json", manifest)
    print(json.dumps({"phase": "load", "cases": len(WINDOWS), "device": manifest["gpu_name"]}), flush=True)
    registry = ModelRegistry(ROOT / "models")
    with registry.open_verified("tracknetv3", fetch=False) as artifact:
        model = TrackNetV3(
            artifact.path,
            backend="torch-cuda",
            threshold=0.5,
            batch=4,
            precision="fp16",
            checkpoint_stream=artifact.stream,
            expected_sha256=artifact.sha256,
        )
    manifest["model_runtime"] = model.runtime
    if model.runtime["actual_backend"] != "torch-cuda" or model.runtime["backend_fallback"]:
        raise RuntimeError("unexpected model backend fallback")
    dump(OUTPUT / "manifest.json", manifest)
    results = []
    all_outputs = {8: [], 4: []}
    with av.open(str(proxy)) as container:
        for number, (name, first, last) in enumerate(WINDOWS):
            images = decode(container, first, last)
            images_hash = hashlib.sha256()
            for image in images:
                images_hash.update(image.tobytes())
            masks = []
            shots = []
            for frame in range(first, last + 1):
                row = rows[frame]
                shots.append(row["sh"])
                if row["v"] == "main" and not row["l"] and row["g"] is not None:
                    g = np.asarray(row["g"], np.float64).reshape(3, 3)
                    polygon = cv2.perspectiveTransform(reference_poly.reshape(-1, 1, 2), g).reshape(-1, 2)
                    masks.append(flight_mask(polygon, (1280, 720), (WIDTH, HEIGHT)))
                else:
                    masks.append(np.zeros((HEIGHT, WIDTH), np.uint8))
            # Warm both strategies once on same first eight images; exclude warm-up from timings.
            if number == 0:
                model.bg = FrozenBackground(background)
                model.detect(images[:8], shots[:8], step=8, masks=masks[:8])
                torch.cuda.synchronize()
            runs = {}
            # Alternate order to reduce systematic warm/cache ordering advantage.
            order = [8, 4] if number % 2 == 0 else [4, 8]
            for step in order:
                model.bg = FrozenBackground(background)
                torch.cuda.reset_peak_memory_stats()
                torch.cuda.synchronize()
                started = time.perf_counter()
                predictions = model.detect(images, shots, step=step, masks=masks)
                torch.cuda.synchronize()
                elapsed = time.perf_counter() - started
                if len(predictions) != len(images):
                    raise ValueError("detector did not output every frame")
                visible = [p is not None for p in predictions]
                runs[step] = {
                    "elapsed_seconds": elapsed,
                    "frames_per_second": len(images) / elapsed,
                    "peak_cuda_allocated_bytes": torch.cuda.max_memory_allocated(),
                    "peak_cuda_reserved_bytes": torch.cuda.max_memory_reserved(),
                    "observed_count": sum(visible),
                    "missing_runs": gap_runs(visible, first),
                    "predictions": predictions,
                }
                for i, prediction in enumerate(predictions):
                    all_outputs[step].append(
                        {
                            "case_id": name,
                            "frame_idx": first + i,
                            "x": None if prediction is None else prediction.x,
                            "y": None if prediction is None else prediction.y,
                            "confidence": None if prediction is None else prediction.conf,
                            "visible": prediction is not None,
                        }
                    )
            shared = [
                (a, b)
                for a, b in zip(runs[8]["predictions"], runs[4]["predictions"], strict=True)
                if a is not None and b is not None
            ]
            distances = [float(np.hypot(a.x - b.x, a.y - b.y)) for a, b in shared]
            a, b = runs[8]["predictions"], runs[4]["predictions"]
            result = {
                "case_id": name,
                "frames_inclusive": [first, last],
                "decoded_frame_bytes_sha256": images_hash.hexdigest(),
                "mask_bytes_sha256": array_sha(np.stack(masks)),
                "inference_order": order,
                "step8": {k: v for k, v in runs[8].items() if k != "predictions"},
                "step4": {k: v for k, v in runs[4].items() if k != "predictions"},
                "step4_only_observed_frames": [first + i for i in range(len(a)) if a[i] is None and b[i] is not None],
                "step8_only_observed_frames": [first + i for i in range(len(a)) if a[i] is not None and b[i] is None],
                "shared_observed_count": len(shared),
                "location_disagreement_proxy_px": {
                    "median": float(np.median(distances)) if distances else None,
                    "maximum": max(distances) if distances else None,
                },
            }
            results.append(result)
            dump(OUTPUT / "case_metrics.json", results)
            print(
                json.dumps(
                    {
                        "phase": "case_complete",
                        "case": name,
                        "step8_observed": runs[8]["observed_count"],
                        "step4_observed": runs[4]["observed_count"],
                        "step8_seconds": runs[8]["elapsed_seconds"],
                        "step4_seconds": runs[4]["elapsed_seconds"],
                    }
                ),
                flush=True,
            )
    for step, output_rows in all_outputs.items():
        with (OUTPUT / f"observations_step{step}.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["case_id", "frame_idx", "x", "y", "confidence", "visible"])
            writer.writeheader()
            writer.writerows(output_rows)
    summary = {"scope": manifest["scope"], "frames_per_strategy": len(all_outputs[8]), "case_count": len(results)}
    for step in (8, 4):
        name = f"step{step}"
        summary[name] = {
            "observed_count": sum(r[name]["observed_count"] for r in results),
            "total_seconds": sum(r[name]["elapsed_seconds"] for r in results),
            "peak_cuda_allocated_bytes": max(r[name]["peak_cuda_allocated_bytes"] for r in results),
            "peak_cuda_reserved_bytes": max(r[name]["peak_cuda_reserved_bytes"] for r in results),
        }
    summary["step4_over_step8_runtime_ratio"] = summary["step4"]["total_seconds"] / summary["step8"]["total_seconds"]
    special = {}
    for name, first, last in [("upper_image_gap", 9526, 9542), ("static_T_cluster", 12748, 12768)]:
        special[name] = {"frames_inclusive": [first, last]}
        for step in (8, 4):
            selected = [r for r in all_outputs[step] if first <= r["frame_idx"] <= last]
            valid = [r for r in selected if r["visible"]]
            special[name][f"step{step}"] = {
                "observed_count": len(valid),
                "observed_frames": [r["frame_idx"] for r in valid],
                "within_10px_of_baseline_T_count": sum(np.hypot(r["x"] - 645, r["y"] - 393) <= 10 for r in valid),
            }
    summary["specific_failure_regions"] = special
    # np.bool_ from the explicit count must become plain integers for strict JSON.
    for value in special.values():
        for step in ("step8", "step4"):
            value[step]["within_10px_of_baseline_T_count"] = int(value[step]["within_10px_of_baseline_T_count"])
    dump(OUTPUT / "metrics.json", summary)
    manifest.update(
        status="completed",
        completed_at=datetime.now(UTC).isoformat(),
        artifact_sha256={p.name: sha(p) for p in OUTPUT.glob("*.csv")},
    )
    if {str(p.relative_to(ROOT)): sha(p) for p in component_files} != hashes:
        raise RuntimeError("shuttle component source changed during experiment")
    dump(OUTPUT / "manifest.json", manifest)
    print(json.dumps(summary, indent=2), flush=True)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=False)
    with (OUTPUT / "execution.log").open("w") as log, contextlib.redirect_stdout(log), contextlib.redirect_stderr(log):
        try:
            run()
        except BaseException as error:
            dump(OUTPUT / "failure.json", {"type": type(error).__name__, "error": str(error)})
            raise
    print(f"Paired actual inference complete: {OUTPUT}")


if __name__ == "__main__":
    main()
