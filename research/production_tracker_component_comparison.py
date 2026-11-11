"""Standalone common-detector tracker/pose diagnostics; never an accuracy benchmark.

No annotations or production sessions are loaded. Fresh raw RF-DETR outputs from
uniform bounded proxy windows are immutable inputs to every tracker. Pose uses
the same observed person boxes, without target-court or physical identity claims.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import importlib.util
import inspect
import json
import os
import shutil
import sys
import time
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

MEDIA = {
    "test1": ROOT
    / "artifacts/benchmarking/experiments/prod_20261105_fresh_association_scene_v1/runtime/media"
    / "877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6/proxy.mp4",
    "test2": ROOT.parent
    / "test2-runs-20261105/fresh_v1/data/media"
    / "4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a/proxy.mp4",
    "doubles": ROOT / "data/research/pluggable-pipeline-20261103/dshuttlenet-v7/prepared-v1/proxy.mp4",
    "amateur": ROOT / "data/media/90d1f399c05312ede173de2f2c8cd2fee09f1d201df46b476119660a00039ff0/proxy.mp4",
}


def sha(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path: Path, value: Any) -> None:
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write("\n")


def bounded_windows(frame_count: int, length: int = 120) -> list[tuple[int, int]]:
    """Two uniformly positioned disjoint windows; no content/label selection."""
    if type(frame_count) is not int or type(length) is not int or length < 2 or frame_count < 3 * length:
        raise ValueError("need at least three window lengths and positive integer frame counts")
    return [(frame_count * k // 3 - length // 2, frame_count * k // 3 - length // 2 + length) for k in (1, 2)]


def validate_row(row: dict[str, Any]) -> None:
    if row.get("origin") != "fresh_person_detector_postprocess":
        raise ValueError("tracker input must be fresh detector output, never tracked/carried boxes")
    if Fraction(row["pts"]) * Fraction(row["time_base"]) != Fraction(row["frame_idx"]) / Fraction(row["fps"]):
        raise ValueError("canonical frame/PTS mismatch")
    boxes = np.asarray(row["boxes"], dtype=float).reshape(-1, 4)
    scores = np.asarray(row["scores"], dtype=float)
    if len(boxes) != len(scores) or not np.isfinite(boxes).all() or not np.isfinite(scores).all():
        raise ValueError("malformed detector output")
    if np.any(boxes[:, 2:] <= boxes[:, :2]) or np.any((scores < 0) | (scores > 1)):
        raise ValueError("invalid detector boxes/confidences")


def package_receipts() -> dict[str, Any]:
    receipts = {}
    for name in ("trackers", "supervision", "rtmlib", "onnxruntime-gpu"):
        dist = importlib.metadata.distribution(name)
        licenses = [dist.locate_file(p) for p in dist.files or [] if "LICENSE" in str(p)]
        receipts[name] = {
            "version": dist.version,
            "license_metadata": dist.metadata.get("License-Expression") or dist.metadata.get("License"),
            "license_sha256": {str(p): sha(p) for p in licenses},
        }
    return receipts


def frozen_players(output: Path) -> Any:
    source = ROOT / "sports/badminton/src/bai_badminton/perception/players.py"
    snapshot = output / "executed_players_snapshot.py"
    shutil.copyfile(source, snapshot)
    spec = importlib.util.spec_from_file_location("independent_component_players_snapshot", snapshot)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def fresh(output: Path, gpu_index: int, length: int) -> None:
    from research.production_resource_guard import gpu_lease, gpu_uuid
    from research.validate_real_video_runtime import offline_network

    output.mkdir(parents=True, exist_ok=False)
    (output / "frames").mkdir()
    (output / "raw").mkdir()
    allocated = gpu_uuid(gpu_index)
    os.environ["CUDA_VISIBLE_DEVICES"] = allocated
    import av
    import cv2
    import onnxruntime as ort

    player = frozen_players(output)
    detector_path = ROOT / "models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx"
    provider = [("CUDAExecutionProvider", {"device_id": 0}), "CPUExecutionProvider"]
    rows, media_receipts, pose_inputs = [], {}, []
    started = time.perf_counter()
    with gpu_lease(ROOT / "artifacts/benchmarking/experiments/.gpu_leases", allocated), offline_network():
        load = time.perf_counter()
        detector = player.PlayerDetector(detector_path, (512, 512), provider)
        load_seconds = time.perf_counter() - load
        assert detector.tool.session.get_providers()[0] == "CUDAExecutionProvider"
        original_inference = detector.tool.session.run
        raw_outputs: list[np.ndarray] = []
        raw_inputs: dict[str, np.ndarray] = {}

        def capture(names: Any, tensors: dict[str, np.ndarray], *args: Any, **kwargs: Any) -> Any:
            raw_inputs.update({key: value.copy() for key, value in tensors.items()})
            values = original_inference(names, tensors, *args, **kwargs)
            raw_outputs.extend(np.asarray(v).copy() for v in values)
            return values

        detector.tool.session.run = capture
        for recording, path in MEDIA.items():
            source_hash = sha(path)
            with av.open(str(path)) as container:
                stream = container.streams.video[0]
                fps, count = stream.average_rate, stream.frames
                windows = bounded_windows(count, length)
                media_receipts[recording] = {
                    "proxy_path": str(path),
                    "proxy_sha256": source_hash,
                    "fps": str(fps),
                    "frame_count": count,
                    "windows_half_open": windows,
                    "original_source_time_mapping": "not audited; amateur VFR15/proxy30 mapping remains unverified",
                }
                for window_id, (begin, end) in enumerate(windows):
                    segment = f"{recording}_{window_id}"
                    wanted = set(range(begin, end, 2))
                    container.seek(int(Fraction(begin, 1) / fps / stream.time_base), stream=stream, backward=True)
                    seen = []
                    for decoded in container.decode(stream):
                        canonical = decoded.pts * stream.time_base * fps
                        if canonical < begin:
                            continue
                        if canonical >= end:
                            break
                        if canonical.denominator != 1:
                            raise ValueError("noncanonical proxy timestamp")
                        frame = int(canonical)
                        if frame not in wanted:
                            continue
                        image = decoded.to_ndarray(format="bgr24")
                        image_path = output / "frames" / f"{segment}_{frame}.png"
                        assert cv2.imwrite(str(image_path), image)
                        raw_outputs.clear()
                        raw_inputs.clear()
                        tick = time.perf_counter()
                        boxes, scores = detector(image)
                        elapsed = time.perf_counter() - tick
                        raw_path = output / "raw" / f"{segment}_{frame}.npz"
                        np.savez_compressed(
                            raw_path,
                            **{f"tensor_{i}": v for i, v in enumerate(raw_outputs)},
                            **{f"input_{key}": value for key, value in raw_inputs.items()},
                        )
                        row = {
                            "segment": segment,
                            "recording": recording,
                            "frame_idx": frame,
                            "pts": decoded.pts,
                            "time_base": str(stream.time_base),
                            "fps": str(fps),
                            "origin": "fresh_person_detector_postprocess",
                            "boxes": boxes.tolist(),
                            "scores": scores.tolist(),
                            "image_path": str(image_path),
                            "image_sha256": sha(image_path),
                            "bgr24_sha256": hashlib.sha256(image.tobytes()).hexdigest(),
                            "shape": list(image.shape),
                            "raw_path": str(raw_path),
                            "raw_sha256": sha(raw_path),
                            "raw_shapes": [list(v.shape) for v in raw_outputs],
                            "raw_dtypes": [str(v.dtype) for v in raw_outputs],
                            "detector_seconds": elapsed,
                        }
                        row["network_inputs"] = {
                            key: {
                                "shape": list(value.shape),
                                "dtype": str(value.dtype),
                                "sha256": hashlib.sha256(value.tobytes()).hexdigest(),
                            }
                            for key, value in raw_inputs.items()
                        }
                        validate_row(row)
                        rows.append(row)
                        seen.append(frame)
                        if len(seen) == 1 and len(boxes):
                            pose_inputs.append(row)
                    if seen != sorted(wanted):
                        raise ValueError("incomplete bounded source-frame coverage")
                    print(
                        json.dumps(
                            {
                                "segment": segment,
                                "frames": len(seen),
                                "box_count": sum(len(r["boxes"]) for r in rows if r["segment"] == segment),
                            }
                        ),
                        flush=True,
                    )
        poses = {}
        for alias, size, directory in (
            ("rtmpose_m_body7", (192, 256), "extracted-v1"),
            ("rtmpose_x_halpe26", (288, 384), "extracted"),
        ):
            path = next((ROOT / "models/cache" / alias / directory).rglob("end2end.onnx"))
            tick = time.perf_counter()
            model = player.PoseEstimator(path, size, provider)
            model_load = time.perf_counter() - tick
            calls = []
            for row in pose_inputs:
                image = cv2.imread(row["image_path"])
                assert hashlib.sha256(image.tobytes()).hexdigest() == row["bgr24_sha256"]
                indices = np.argsort(-np.asarray(row["scores"]))[:4]
                boxes = [np.asarray(row["boxes"][i]) for i in indices]
                tick = time.perf_counter()
                result = model(image, boxes)
                elapsed = time.perf_counter() - tick
                pose_path = output / "raw" / f"{alias}_{row['segment']}.npz"
                np.savez_compressed(pose_path, **{f"person_{i}": v for i, v in enumerate(result)})
                calls.append(
                    {
                        "segment": row["segment"],
                        "frame_idx": row["frame_idx"],
                        "image_sha256": row["image_sha256"],
                        "detector_indices": indices.tolist(),
                        "boxes": [v.tolist() for v in boxes],
                        "seconds": elapsed,
                        "result_shapes": [list(v.shape) for v in result],
                        "finite": all(np.isfinite(v).all() for v in result),
                        "pose_path": str(pose_path),
                        "pose_sha256": sha(pose_path),
                    }
                )
            poses[alias] = {
                "model_path": str(path),
                "sha256": sha(path),
                "load_seconds": model_load,
                "providers": model.tool.session.get_providers(),
                "inputs": [
                    {"name": v.name, "shape": v.shape, "dtype": v.type} for v in model.tool.session.get_inputs()
                ],
                "outputs": [
                    {"name": v.name, "shape": v.shape, "dtype": v.type} for v in model.tool.session.get_outputs()
                ],
                "calls": calls,
            }
        manifest = {
            "schema": "common-fresh-person-inputs-v1",
            "completed": True,
            "annotations_loaded": False,
            "scope": "standalone raw detector and common-box pose; no production tracker/court/identity output",
            "media": media_receipts,
            "frame_rows": rows,
            "poses": poses,
            "physical_gpu_index": gpu_index,
            "gpu_uuid": allocated,
            "runtime": ort.__version__,
            "detector": {
                "path": str(detector_path),
                "sha256": sha(detector_path),
                "score_threshold": 0.35,
                "providers": detector.tool.session.get_providers(),
                "load_seconds": load_seconds,
            },
            "players_snapshot_sha256": sha(output / "executed_players_snapshot.py"),
            "detector_class_source_sha256": hashlib.sha256(
                inspect.getsource(player.PlayerDetector).encode()
            ).hexdigest(),
            "pose_class_source_sha256": hashlib.sha256(inspect.getsource(player.PoseEstimator).encode()).hexdigest(),
            "script_sha256": sha(Path(__file__)),
            "packages": package_receipts(),
            "total_seconds": time.perf_counter() - started,
        }
        write(output / "inputs_manifest.json", manifest)


def make_tracker(name: str, fps: float) -> tuple[Any, dict[str, Any]]:
    import trackers

    classes = {
        "bytetrack": trackers.ByteTrackTracker,
        "ocsort": trackers.OCSORTTracker,
        "botsort": trackers.BoTSORTTracker,
        "cbiou": trackers.CBIoUTracker,
    }
    params: dict[str, Any] = {
        "frame_rate": fps,
        "lost_track_buffer": 30,
        "minimum_consecutive_frames": 1,
        "high_conf_det_threshold": 0.5,
    }
    if name != "ocsort":
        params["track_activation_threshold"] = 0.4
    if name == "botsort":
        params["enable_cmc"] = False
    return classes[name](**params), params


def compare(inputs: Path, output: Path) -> None:
    import supervision as sv

    manifest = json.loads((inputs / "inputs_manifest.json").read_text())
    if not manifest.get("completed") or manifest.get("annotations_loaded"):
        raise ValueError("need completed label-free input manifest")
    rows = manifest["frame_rows"]
    for row in rows:
        validate_row(row)
        if sha(Path(row["raw_path"])) != row["raw_sha256"]:
            raise ValueError("raw detector evidence changed")
    output.mkdir(parents=True, exist_ok=False)
    result = {}
    segments = sorted({row["segment"] for row in rows})
    for name in ("bytetrack", "ocsort", "botsort", "cbiou"):
        repeats, latencies, receipts = [], [], {}
        for _ in range(3):
            tracks = []
            for segment in segments:
                selected = [row for row in rows if row["segment"] == segment]
                tracker, params = make_tracker(name, float(Fraction(selected[0]["fps"])))
                receipts[segment] = params
                for row in selected:
                    boxes = np.asarray(row["boxes"], dtype=np.float32).reshape(-1, 4)
                    scores = np.asarray(row["scores"], dtype=np.float32)
                    det = sv.Detections(xyxy=boxes.copy(), confidence=scores.copy(), class_id=np.zeros(len(boxes), int))
                    tick = time.perf_counter()
                    got = tracker.update(det, timestamp=float(Fraction(row["frame_idx"]) / Fraction(row["fps"])))
                    latencies.append((time.perf_counter() - tick) * 1000)
                    ids = got.tracker_id.tolist() if got.tracker_id is not None else [-1] * len(got)
                    tracks.append(
                        {
                            "segment": segment,
                            "frame_idx": row["frame_idx"],
                            "tracker_ids": ids,
                            "boxes": got.xyxy.tolist(),
                            "confidence": got.confidence.tolist() if got.confidence is not None else None,
                        }
                    )
            repeats.append(tracks)

        def digest(data: Any) -> str:
            return hashlib.sha256(json.dumps(data, sort_keys=True, allow_nan=False).encode()).hexdigest()

        if len({digest(data) for data in repeats}) != 1:
            raise ValueError(f"{name} tracker replay is not deterministic")
        counts = Counter(len([i for i in r["tracker_ids"] if i >= 0]) for r in repeats[0])
        episodes = {}
        for row in repeats[0]:
            for identifier in row["tracker_ids"]:
                if identifier >= 0:
                    episodes.setdefault((row["segment"], identifier), []).append(row["frame_idx"])
        summary = {
            "tracker": name,
            "params": receipts,
            "input_manifest_sha256": sha(inputs / "inputs_manifest.json"),
            "fresh_input_rows": len(rows),
            "repeat_count": 3,
            "exact_output_replay": True,
            "output_sha256": digest(repeats[0]),
            "output_rows_with_n_tracks": dict(counts),
            "local_track_episode_count": len(episodes),
            "episode_observed_updates": [len(v) for v in episodes.values()],
            "latency_ms": {
                "p50": float(np.percentile(latencies, 50)),
                "p95": float(np.percentile(latencies, 95)),
                "mean": float(np.mean(latencies)),
                "samples": len(latencies),
            },
            "named_identity_accuracy": None,
            "HOTA": None,
            "IDF1": None,
            "limitations": [
                "No dense independently reviewed person/identity ground truth",
                "Counts are anonymous global-image track episodes, not target-court players or ID switches",
                "No ReID or camera-motion compensation; defaults other than declared common params differ",
            ],
        }
        write(output / f"{name}_tracks.json", repeats[0])
        write(output / f"{name}_summary.json", summary)
        result[name] = summary
    write(
        output / "comparison.json",
        {
            "scope": "technical common-input component comparison; no accuracy or promotion",
            "trackers": result,
            "packages": package_receipts(),
            "script_sha256": sha(Path(__file__)),
        },
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    fresh_parser = sub.add_parser("fresh")
    fresh_parser.add_argument("--output", type=Path, required=True)
    fresh_parser.add_argument("--gpu-index", type=int, default=1)
    fresh_parser.add_argument("--window-length", type=int, default=120)
    compare_parser = sub.add_parser("compare")
    compare_parser.add_argument("--inputs", type=Path, required=True)
    compare_parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "fresh":
        fresh(args.output.resolve(), args.gpu_index, args.window_length)
    else:
        compare(args.inputs.resolve(), args.output.resolve())


if __name__ == "__main__":
    main()
