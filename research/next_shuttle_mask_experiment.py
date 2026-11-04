"""Fresh full-video shuttle component with other perception held in recorded caches.

Only the shuttle image mask changes. This is NOT fresh full-pipeline inference:
court/view, player/pose/racket and format evidence remain from the source run.
No annotation values or historical contact/rally events enter inference.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
import resource
import subprocess
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.court import REFERENCE_POINTS  # noqa: E402
from bai_badminton.perception.camera import project  # noqa: E402
from bai_badminton.perception.diagnostics import DiagnosticSelection  # noqa: E402
from bai_badminton.perception.isolation import flight_mask  # noqa: E402
from bai_badminton.perception.tracknet import HEIGHT, WIDTH, TrackNetV3  # noqa: E402
from bai_engine.runtime.registry import ModelRegistry  # noqa: E402
from research.audit_c_paired_inference import decode  # noqa: E402
from research.next_evidence_provenance import (  # noqa: E402
    executor_sources_unchanged,
    file_sha256,
    snapshot_executor,
)

REGION = "vertical_columns_to_image_top_v1"
ORIGINAL_REGION = "bounded_upward_sweep_v1"
SOURCE_SHA256 = "877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6"
MODE = "fresh shuttle component + cached other perception; NOT full-pipeline inference"
DEFAULT_RANGES = [[1770, 1900], [3000, 3119], [10560, 11099], [12420, 12979], [14380, 14719], [15360, 15479]]


def dump(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def mask_for_frame(row: dict, reference_polygon: np.ndarray, *, region: str = REGION) -> np.ndarray:
    """Same recorded view exclusion and image geometry; never a player ROI."""
    if row["r"] or row["v"] != "main" or row["g"] is None:
        return np.zeros((HEIGHT, WIDTH), np.uint8)
    matrix = np.asarray(row["g"], np.float64).reshape(3, 3)
    polygon = project(matrix, reference_polygon)
    return flight_mask(polygon, (1280, 720), (WIDTH, HEIGHT), region=region)


def geometry_controls() -> dict:
    """Synthetic geometry controls, not sporting-accuracy labels."""
    polygon = np.array([[400, 400], [900, 400], [900, 700], [400, 700]], np.float64)
    row = {"r": False, "v": "main", "g": np.eye(3).ravel().tolist()}
    original = mask_for_frame(row, polygon, region=ORIGINAL_REGION)
    ceiling = mask_for_frame(row, polygon)

    def at(mask, x, y):
        return bool(mask[round(y * HEIGHT / 720), round(x * WIDTH / 1280)])

    offscreen = polygon + np.array([1500, 0])
    results = {
        "ordinary_mask_is_not_full_frame": bool(ceiling.any() and not ceiling.all()),
        "old_mask_is_subset": bool(np.all(ceiling >= original)),
        "upper_visible_column_admitted": at(ceiling, 650, 20),
        "old_mask_upper_column_rejected": not at(original, 650, 20),
        "neighbor_floor_column_rejected": not at(ceiling, 200, 500),
        "neighbor_upper_column_rejected": not at(ceiling, 200, 20),
        "legitimate_floor_retained": at(ceiling, 650, 650) and at(original, 650, 650),
        "excluded_view_is_empty": not bool(mask_for_frame({**row, "v": "none"}, polygon).any()),
        "replay_is_empty": not bool(mask_for_frame({**row, "r": True}, polygon).any()),
        "missing_geometry_is_empty": not bool(mask_for_frame({**row, "g": None}, polygon).any()),
        "offscreen_geometry_is_empty": not bool(mask_for_frame(row, offscreen).any()),
        "invalid_geometry_is_empty": not bool(mask_for_frame(row, np.full((4, 2), np.nan)).any()),
    }
    if not all(results.values()):
        raise AssertionError(results)
    return {"scope": "synthetic image-mask contract controls only", "checks": results}


def warm_start(video: Path) -> tuple[list[np.ndarray], list[int]]:
    """Production original-source target-PTS sampling and two spatial resizes."""
    images, indices = [], []
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        if (
            stream.width != 1920
            or stream.height != 1080
            or stream.average_rate != 30
            or stream.base_rate != 30
            or stream.start_time != 0
            or stream.frames != 17268
        ):
            raise ValueError("executor is bound to the verified zero-origin Test1 CFR30 source")
        duration = stream.duration * stream.time_base
        if abs(float(duration) - 575.6) > 1e-9:
            raise ValueError("unexpected source video duration")
        for i in range(24):
            target = int(float(duration) * (i + 0.5) / 24 / stream.time_base)
            container.seek(target, stream=stream, any_frame=False)
            for frame in container.decode(stream):
                if frame.pts is not None and frame.pts < target:
                    continue
                image = cv2.resize(frame.to_ndarray(format="bgr24"), (1280, 720), interpolation=cv2.INTER_AREA)
                images.append(
                    cv2.cvtColor(cv2.resize(image, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
                )
                indices.append(int(round(float(frame.pts * stream.time_base) * 30)))
                break
    if len(images) != 24:
        raise ValueError("incomplete production warm-start sample set")
    return images, indices


def run(args) -> None:
    import torch

    if os.environ.get("CUDA_VISIBLE_DEVICES") != "1" or not torch.cuda.is_available() or torch.cuda.device_count() != 1:
        raise RuntimeError("isolate this component experiment on physical GPU1 using CUDA_VISIBLE_DEVICES=1")
    controls = geometry_controls()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    selection = DiagnosticSelection.parse({"ranges": args.diagnostic_ranges, "top_k": 5, "candidate_floor": 0.1})
    paths = [p for directory in ("engine/src", "sports/badminton/src") for p in (ROOT / directory).rglob("*.py")]
    paths += [
        Path(__file__),
        ROOT / "research/next_evidence_provenance.py",
        ROOT / "research/audit_c_paired_inference.py",
    ]
    executor = snapshot_executor(ROOT, output, paths, Path(__file__))
    dump(output / "geometry_controls.json", controls)
    source = args.run.resolve()
    metadata = json.loads((source / "benchmark_metadata.json").read_text())
    reference = json.loads((source / "inference.json").read_text())
    if (
        metadata["status"] != "completed"
        or metadata["source_video_sha256"] != SOURCE_SHA256
        or metadata["frame_count"] != 17268
        or metadata["video_fps"] != 30
        or reference["media"]["width"] != 1280
        or reference["media"]["height"] != 720
    ):
        raise ValueError("only the verified completed Test1 source run is supported")
    video = ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4"
    proxy = source / "runtime/media" / SOURCE_SHA256 / "proxy.mp4"
    if file_sha256(video) != SOURCE_SHA256 or file_sha256(proxy) != reference["proxy_sha256"]:
        raise ValueError("source or proxy bytes differ from the source run")
    roots = list((source / "runtime/sessions").glob("*/perception"))
    if len(roots) != 1:
        raise ValueError("one unambiguous source cache directory is required")
    caches = sorted(roots[0].glob("*.msgpack"))
    if len(caches) != 288:
        raise ValueError("expected all 288 recorded canonical chunks")
    cache_hashes = {path.name: file_sha256(path) for path in caches}
    source_events_path = source / "events.jsonl"
    source_events = [json.loads(line) for line in source_events_path.open()]
    superseded = {event["supersedes"] for event in source_events if event.get("supersedes")}
    events = [
        event
        for event in source_events
        if event["type"] in {"calibration", "format_decision"}
        and event["status"] != "retracted"
        and event["event_id"] not in superseded
    ]
    calibrations = [event["payload"] for event in events if event["type"] == "calibration"]
    if len(calibrations) != 1:
        raise ValueError("one fixed reference calibration is required")
    h = np.asarray(calibrations[0]["H"], np.float64)
    corners = np.asarray([REFERENCE_POINTS[key] for key in ("far_left", "far_right", "near_right", "near_left")])
    polygon = project(h, corners)
    seed_started = time.perf_counter()
    seed_images, seed_indices = warm_start(video)
    seed_seconds = time.perf_counter() - seed_started
    background = np.median(np.stack(seed_images), axis=0).astype(np.uint8)
    background_sha = hashlib.sha256(background.tobytes()).hexdigest()
    prior_path = ROOT / "artifacts/benchmarking/experiments/next_20261105_shuttle_background_probe/manifest.json"
    prior = json.loads(prior_path.read_text())
    if prior["seed_rgb_sha256"] != background_sha:
        raise ValueError("warm-start median does not match the parity-verified component probe")
    cv2.imwrite(str(output / "startup_background.png"), cv2.cvtColor(background, cv2.COLOR_RGB2BGR))
    profile = copy.deepcopy(reference["effective_profile"])
    choice = profile.get("components", {}).get("shuttle") or profile["shuttle"]
    if (
        choice["model"] != "tracknetv3"
        or choice["backend"] != "torch-cuda"
        or choice["precision"] != "fp16"
        or choice["batch"] != 4
        or choice["params"].get("step", 8) != 8
        or choice["params"].get("threshold", 0.5) != 0.5
    ):
        raise ValueError("shuttle settings differ from the parity-verified reference")
    choice["params"]["flight_region"] = REGION
    registry = ModelRegistry(ROOT / "models")
    with registry.open_verified("tracknetv3", fetch=False) as artifact:
        if artifact.sha256 != reference["execution_backends"]["shuttle"]["checkpoint_sha256"]:
            raise ValueError("checkpoint differs from the reference neural run")
        model = TrackNetV3(
            artifact.path,
            backend="torch-cuda",
            threshold=0.5,
            batch=4,
            precision="fp16",
            checkpoint_stream=artifact.stream,
            expected_sha256=artifact.sha256,
        )
    if model.runtime["actual_backend"] != "torch-cuda" or model.runtime["dtype"] != "torch.float16":
        raise RuntimeError("requested CUDA FP16 component did not execute on the expected backend")
    model.bg.seed(0, seed_images)
    hardware = subprocess.check_output(
        ["nvidia-smi", "--id=1", "--query-gpu=index,uuid,name,driver_version", "--format=csv,noheader"], text=True
    ).strip()
    bindings = {
        "schema": "hybrid-shuttle-mask:v1",
        "mode": MODE,
        "changed_mask": REGION,
        "original_mask": ORIGINAL_REGION,
        "roles": {"shuttle": "fresh_neural_component", "court_view_players_pose_racket": "recorded_source_cache"},
        "recorded_run": str(source),
        "recorded_metadata_sha256": file_sha256(source / "benchmark_metadata.json"),
        "checkpoint_sha256": model.runtime["checkpoint_sha256"],
        "runtime": model.runtime,
    }
    manifest = {
        **bindings,
        "status": "running",
        "executor": executor,
        "started_utc": datetime.now(UTC).isoformat(),
        "source_video_sha256": SOURCE_SHA256,
        "proxy_sha256": reference["proxy_sha256"],
        "source_event_sha256": file_sha256(source_events_path),
        "prior_probe_manifest_sha256": file_sha256(prior_path),
        "source_cache_sha256": cache_hashes,
        "configuration": {
            "flight_region": REGION,
            "step": 8,
            "threshold": 0.5,
            "batch": 4,
            "diagnostics": asdict(selection),
        },
        "seed_frame_indices": seed_indices,
        "seed_rgb_sha256": background_sha,
        "gpu": {"CUDA_VISIBLE_DEVICES": "1", "logical_device": "cuda:0", "physical_gpu_record": hardware},
        "runtime_versions": {
            **{name: importlib.metadata.version(name) for name in ["torch", "numpy", "av"]},
            "opencv": cv2.__version__,
            "python": sys.version,
        },
        "annotation_usage": "no annotation values read; only the parent label digest is copied as provenance",
        "reference_intervals_usage": (
            "copied into inference.json only for downstream replay comparison; not predictions or component input"
        ),
        "limitations": [
            "Other perception and format decisions are cached; this does not include upstream cadence feedback",
            "No independently reviewed pixel-visibility or localization labels",
            "Newly admitted peaks are model observations, not verified shuttle locations",
            "Vertical image columns do not resolve overlapping adjacent-court airborne objects",
        ],
    }
    dump(output / "manifest.json", manifest)
    output_cache = output / "runtime/sessions/HybridShuttleMask/perception"
    output_cache.mkdir(parents=True)
    counters = dict.fromkeys(
        [
            "frames",
            "model_frames",
            "excluded_frames",
            "observed",
            "reference_observed",
            "newly_observed",
            "newly_missing",
            "coordinate_changed",
            "support_changed",
            "diagnostic_frames",
        ],
        0,
    )
    timings = {
        "warm_start_seconds": seed_seconds,
        "decode_seconds": 0.0,
        "shuttle_inference_seconds": 0.0,
        "cache_write_seconds": 0.0,
    }
    output_hashes, chunk_stats = {}, []
    expected_frame = 0
    with (
        av.open(str(proxy)) as container,
        (output / "shuttle_observations.jsonl").open("x") as observations,
        (output / "candidates.jsonl").open("x") as candidates,
    ):
        for path in caches:
            data_bytes = path.read_bytes()
            if hashlib.sha256(data_bytes).hexdigest() != cache_hashes[path.name]:
                raise RuntimeError("source cache changed during component inference")
            data = msgpack.unpackb(data_bytes, raw=False)
            first, last, frames = data["start"], data["end"], data["frames"]
            if data["v"] != 17 or first != expected_frame or last != first + len(frames) - 1:
                raise ValueError("unexpected cache schema or frame range")
            if [row["f"] for row in frames] != list(range(first, last + 1)) or len(frames) != (
                48 if last == 17267 else 60
            ):
                raise ValueError("noncanonical source chunk layout")
            if data["ci"].get("mode") != "lines":
                raise ValueError("the verified Test1 experiment requires recorded court-line geometry")
            expected_frame = last + 1
            masks = [mask_for_frame(row, polygon) for row in frames]
            old_masks = [mask_for_frame(row, polygon, region=ORIGINAL_REGION) for row in frames]
            if not all(np.all(new >= old) for new, old in zip(masks, old_masks, strict=True)):
                raise AssertionError("new image mask is not a superset of the retained original mask")
            indices = {i for i, row in enumerate(frames) if selection.includes(row["f"]) and not row["r"]}
            summaries = [None] * len(frames)
            if all(row["r"] for row in frames):
                predictions = [None] * len(frames)
                inference_seconds = 0.0
            else:
                before = time.perf_counter()
                images = decode(container, first, last)
                timings["decode_seconds"] += time.perf_counter() - before
                torch.cuda.synchronize()
                before = time.perf_counter()
                if indices:
                    predictions, summaries = model.detect_with_diagnostics(
                        images,
                        [row["sh"] for row in frames],
                        step=8,
                        masks=masks,
                        selection=selection,
                        indices=indices,
                    )
                else:
                    predictions = model.detect(images, [row["sh"] for row in frames], step=8, masks=masks)
                torch.cuda.synchronize()
                inference_seconds = time.perf_counter() - before
                timings["shuttle_inference_seconds"] += inference_seconds
                counters["model_frames"] += len(frames)
            for i, row in enumerate(frames):
                if row.get("dg") is not None:
                    raise ValueError("source v17 cache unexpectedly contains diagnostic values")
                prediction = predictions[i] if not row["r"] else None
                point = None if prediction is None else [prediction.x, prediction.y]
                support = 0.0 if prediction is None else prediction.conf
                previous, previous_support = row["s"], row["c"]
                counters["frames"] += 1
                counters["excluded_frames"] += int(row["r"])
                counters["observed"] += int(point is not None)
                counters["reference_observed"] += int(previous is not None)
                counters["newly_observed"] += int(previous is None and point is not None)
                counters["newly_missing"] += int(previous is not None and point is None)
                counters["coordinate_changed"] += int(previous is not None and point is not None and previous != point)
                counters["support_changed"] += int(previous_support != support)
                observations.write(
                    json.dumps(
                        {
                            "frame_idx": row["f"],
                            "canonical_time_sec": row["f"] / 30,
                            "shot_id": row["sh"],
                            "view": row["v"],
                            "analysis_excluded": row["r"],
                            "xy": point,
                            "support": support,
                            "reference_xy": previous,
                            "reference_support": previous_support,
                            "provenance": "fresh_component_observation; uncalibrated_model_support",
                        },
                        allow_nan=False,
                    )
                    + "\n"
                )
                if summaries[i] is not None:
                    counters["diagnostic_frames"] += 1
                    candidates.write(
                        json.dumps(
                            {
                                "frame_idx": row["f"],
                                "shot_id": row["sh"],
                                "view": row["v"],
                                "diagnostic": asdict(summaries[i]),
                            },
                            allow_nan=False,
                        )
                        + "\n"
                    )
                row["s"], row["c"] = point, support
            data["ci"]["hybrid_component_experiment"] = {**bindings, "parent_cache_sha256": cache_hashes[path.name]}
            before = time.perf_counter()
            output_bytes = msgpack.packb(data, use_bin_type=True)
            with (output_cache / path.name).open("xb") as stream:
                stream.write(output_bytes)
            output_hashes[path.name] = hashlib.sha256(output_bytes).hexdigest()
            timings["cache_write_seconds"] += time.perf_counter() - before
            chunk_stats.append({"start": first, "end": last, "shuttle_inference_seconds": inference_seconds})
            if last % 600 < 60 or last == 17267:
                print(
                    json.dumps(
                        {
                            "frame": last,
                            "observed": counters["observed"],
                            "elapsed_seconds": time.perf_counter() - started,
                        }
                    ),
                    flush=True,
                )
    if expected_frame != 17268:
        raise ValueError("full video was not covered")
    with (output / "events.jsonl").open("x") as stream:
        for event in events:
            stream.write(json.dumps(event, allow_nan=False) + "\n")
    source_unchanged = executor_sources_unchanged(ROOT, executor)
    caches_unchanged = all(file_sha256(path) == cache_hashes[path.name] for path in caches)
    if not source_unchanged or not caches_unchanged:
        manifest.update(
            status="invalid_source_changed",
            executor_sources_unchanged=source_unchanged,
            source_caches_unchanged=caches_unchanged,
        )
        dump(output / "manifest.json", manifest)
        raise RuntimeError("source or input caches changed during the component experiment")
    elapsed = time.perf_counter() - started
    fresh_models = {"shuttle": {"model_ref": model.model_ref, "sha256": model.runtime["checkpoint_sha256"]}}
    inference = {
        "status": "hybrid_component_complete",
        "mode": MODE,
        "media": reference["media"],
        "frontier_frame": 17267,
        "effective_profile": profile,
        "effective_profile_scope": "shuttle configuration actual; other stages cached reference settings",
        "models": fresh_models,
        "execution_backends": {"shuttle": model.runtime},
        "proxy_sha256": reference["proxy_sha256"],
        "rally_events": reference["rally_events"],
        "rally_events_role": "UNCHANGED SOURCE REFERENCE ONLY; not inferred from hybrid observations",
        "elapsed_seconds": elapsed,
        "timing_scope": "component hybrid-cache derivation only; NOT full-pipeline latency",
        "per_stage_seconds": timings,
        "counters": counters,
        "resources": {
            "peak_process_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024,
            "torch_peak_allocated_bytes": torch.cuda.max_memory_allocated(),
            "scope": "component process only; Torch allocator excludes decoder/other process allocations",
        },
    }
    dump(output / "inference.json", inference)
    dump(
        output / "benchmark_metadata.json",
        {
            "schema": "hybrid-perception-component-experiment:v1",
            "status": "completed",
            "mode": MODE,
            "git_commit_sha": executor["git_commit"],
            "active_branch": executor["branch"],
            "source_hashes": executor["source_sha256"],
            "source_video_sha256": SOURCE_SHA256,
            "ground_truth_sha256": metadata["ground_truth_sha256"],
            "ground_truth_usage": "digest copied from source metadata only; no annotation values read",
            "video_fps": 30,
            "frame_count": 17268,
            "models": fresh_models,
            "runtime_versions": manifest["runtime_versions"],
            "configuration": manifest["configuration"],
            "reference_run": str(source),
            "reference_metadata_sha256": manifest["recorded_metadata_sha256"],
            "reference_rally_intervals_only": True,
            "reference_calibration_format_events_only": True,
            "component_roles": bindings["roles"],
            "executor": executor,
        },
    )
    manifest.update(
        status="completed",
        completed_utc=datetime.now(UTC).isoformat(),
        elapsed_seconds=elapsed,
        counters=counters,
        per_stage_seconds=timings,
        output_cache_sha256=output_hashes,
        chunk_timings=chunk_stats,
        executor_sources_unchanged=source_unchanged,
        source_caches_unchanged=caches_unchanged,
    )
    dump(output / "manifest.json", manifest)
    print(
        json.dumps({"mode": MODE, "status": "completed", "counters": counters, "elapsed_seconds": elapsed}), flush=True
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "artifacts/benchmarking/experiments/fresh_image_exit_v1")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--diagnostic-ranges", type=json.loads, default=DEFAULT_RANGES)
    parser.add_argument("--check-only", action="store_true")
    args = parser.parse_args()
    if args.check_only:
        print(json.dumps(geometry_controls(), indent=2))
    else:
        run(args)
