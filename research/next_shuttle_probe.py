"""Controlled fresh TrackNet diagnostics with recorded scene/mask context.

This replays the background's chronological image inputs, not private perception
state. Neural inference runs only in selected canonical 60-frame chunks. Labels
are not read. Predictions are component observations, never rally predictions.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import av
import cv2
import msgpack
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.court import REFERENCE_POINTS  # noqa: E402
from bai_badminton.perception.diagnostics import DiagnosticSelection  # noqa: E402
from bai_badminton.perception.isolation import flight_mask  # noqa: E402
from bai_badminton.perception.tracknet import HEIGHT, WIDTH, BackgroundModel, TrackNetV3  # noqa: E402
from bai_engine.runtime.registry import ModelRegistry  # noqa: E402
from research.audit_c_paired_inference import decode  # noqa: E402
from research.next_evidence_provenance import executor_sources_unchanged, snapshot_executor  # noqa: E402


def sha(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


class FrozenBackground(BackgroundModel):
    def __init__(self, rgb):
        super().__init__()
        self.rgb = rgb.copy()

    def observe(self, shot, rgb_small):
        pass

    def retain(self, shots):
        pass

    def get(self, shot, fallback):
        return self.rgb


def run(args):
    import torch

    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    selection = DiagnosticSelection.parse({"ranges": args.ranges, "top_k": 5, "candidate_floor": 0.1})
    if not selection.ranges:
        raise ValueError("explicit bounded diagnostic ranges are required")
    source_paths = [p for directory in ("engine/src", "sports/badminton/src") for p in (ROOT / directory).rglob("*.py")]
    source_paths.extend(
        [Path(__file__), ROOT / "research/next_evidence_provenance.py", ROOT / "research/audit_c_paired_inference.py"]
    )
    executor = snapshot_executor(ROOT, output, source_paths, Path(__file__))
    run = args.run.resolve()
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    inference = json.loads((run / "inference.json").read_text())
    variants_requested = list(args.variants)
    if "rolling" not in variants_requested or len(set(variants_requested)) != len(variants_requested):
        raise ValueError("component variants must be unique and include the paired rolling control")
    flight_region = (
        metadata.get("configuration", {})
        .get("shuttle", {})
        .get("params", {})
        .get("flight_region", "bounded_upward_sweep_v1")
    )
    if (
        metadata["frame_count"] != 17268
        or metadata["video_fps"] != 30
        or inference["media"]["width"] != 1280
        or inference["media"]["height"] != 720
    ):
        raise ValueError("this diagnostic executor is explicitly bound to the verified Test1 CFR30/720p source")
    video = ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4"
    proxy = run / "runtime/media" / metadata["source_video_sha256"] / "proxy.mp4"
    if sha(video) != metadata["source_video_sha256"] or sha(proxy) != inference["proxy_sha256"]:
        raise ValueError("source/proxy hashes do not match recorded run")
    roots = list((run / "runtime/sessions").glob("*/perception"))
    if len(roots) != 1:
        raise ValueError("one unambiguous recorded cache is required")
    caches = sorted(roots[0].glob("*.msgpack"))
    events = [json.loads(line) for line in (run / "events.jsonl").open()]
    calibration = next(event["payload"] for event in events if event["type"] == "calibration")
    if sum(event["type"] == "calibration" for event in events) != 1:
        raise ValueError("this controlled probe requires one recorded fixed reference calibration")
    h = np.asarray(calibration["H"], np.float64)
    corners = np.asarray([REFERENCE_POINTS[key] for key in ("far_left", "far_right", "near_right", "near_left")])
    polygon = cv2.perspectiveTransform(corners.reshape(-1, 1, 2), h).reshape(-1, 2)

    # Exactly the production warm-start target-PTS rule, using original pixels
    # followed by the same two spatial resizes. This is not a rally-selected median.
    seed_images, seed_indices = [], []
    with av.open(str(video)) as container:
        stream = container.streams.video[0]
        duration = stream.duration * stream.time_base
        for i in range(24):
            target = int(float(duration) * (i + 0.5) / 24 / stream.time_base)
            container.seek(target, stream=stream, any_frame=False)
            for frame in container.decode(stream):
                if frame.pts is not None and frame.pts < target:
                    continue
                image = cv2.resize(frame.to_ndarray(format="bgr24"), (1280, 720), interpolation=cv2.INTER_AREA)
                seed_images.append(
                    cv2.cvtColor(cv2.resize(image, (WIDTH, HEIGHT), interpolation=cv2.INTER_AREA), cv2.COLOR_BGR2RGB)
                )
                seed_indices.append(int(round(float(frame.pts * stream.time_base) * 30)))
                break
    fixed = np.median(np.stack(seed_images), axis=0).astype(np.uint8)
    cv2.imwrite(str(output / "startup_background.png"), cv2.cvtColor(fixed, cv2.COLOR_RGB2BGR))
    if not torch.cuda.is_available():
        raise RuntimeError("existing CUDA runtime is required for this component experiment")
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
    model.bg.seed(0, seed_images)
    manifest = {
        "schema": "controlled-shuttle-diagnostics:v2",
        "status": "running",
        "execution_date": datetime.now(UTC).isoformat(),
        "executor": executor,
        "scope": "fresh component inference with recorded scene/masks; NOT full pipeline or localization accuracy",
        "configuration": {
            "ranges": args.ranges,
            "step": 8,
            "chunk": "recorded canonical 60-frame chunks",
            "variants": variants_requested,
            "flight_region": flight_region,
            "candidate_floor": 0.1,
            "top_k": 5,
        },
        "source_sha256": sha(video),
        "proxy_sha256": sha(proxy),
        "seed_frame_indices": seed_indices,
        "seed_rgb_sha256": hashlib.sha256(fixed.tobytes()).hexdigest(),
        "runtime": model.runtime,
        "recorded_run": str(run),
        "recorded_metadata_sha256": sha(run / "benchmark_metadata.json"),
        "annotation_usage": "none; explicit frame windows select diagnostics only",
        "limitations": [
            "No independently reviewed pixel/visibility labels",
            "Recorded court/scene observations held fixed",
            "Zero channels ablate the background of a concat checkpoint; not a background-free trained model",
            "Component observations do not include downstream cadence feedback",
        ],
    }
    dump(output / "manifest.json", manifest)
    rows, comparisons, cache_hashes = [], [], {}
    with av.open(str(proxy)) as container:
        for path in caches:
            data = msgpack.unpackb(path.read_bytes(), raw=False)
            first, last = data["start"], data["end"]
            if first > selection.ranges[-1][1]:
                break
            cache_hashes[path.name] = sha(path)
            obs = data["frames"]
            if all(row["r"] for row in obs):
                continue
            images = decode(container, first, last)
            shots = [row["sh"] for row in obs]
            needed = {i for i in range(len(obs)) if selection.includes(first + i)}
            if not needed:
                model.bg.retain(set(shots))
                model._prep(images, shots)
                continue
            masks = []
            for row in obs:
                if row["v"] == "main" and row["g"] is not None:
                    g = np.asarray(row["g"], np.float64).reshape(3, 3)
                    poly = cv2.perspectiveTransform(polygon.reshape(-1, 1, 2), g).reshape(-1, 2)
                    masks.append(flight_mask(poly, (1280, 720), (WIDTH, HEIGHT), region=flight_region))
                else:
                    masks.append(np.zeros((HEIGHT, WIDTH), np.uint8))
            pre_background = copy.deepcopy(model.bg)
            rolling_after = None
            variants = list(variants_requested)
            if first // 60 % 2:
                variants.reverse()
            for variant in variants:
                model.bg = (
                    copy.deepcopy(pre_background)
                    if variant == "rolling"
                    else FrozenBackground(fixed if variant == "fixed_startup" else np.zeros_like(fixed))
                )
                torch.cuda.synchronize()
                started = time.perf_counter()
                predictions, diagnostics = model.detect_with_diagnostics(
                    images, shots, step=8, masks=masks, selection=selection, indices=needed
                )
                torch.cuda.synchronize()
                elapsed = time.perf_counter() - started
                if variant == "rolling":
                    rolling_after = model.bg
                differences = []
                for i in sorted(needed):
                    prediction = predictions[i] if not obs[i]["r"] else None
                    point = None if prediction is None else [prediction.x, prediction.y]
                    row = {
                        "frame_idx": first + i,
                        "variant": variant,
                        "xy": point,
                        "support": prediction.conf if prediction else 0.0,
                        "diagnostic": diagnostics[i].to_dict() if hasattr(diagnostics[i], "to_dict") else None,
                    }
                    # Dataclass conversion stays outside inference and retains raw support.
                    if row["diagnostic"] is None:
                        from dataclasses import asdict

                        row["diagnostic"] = asdict(diagnostics[i]) if diagnostics[i] is not None else None
                    rows.append(row)
                    reference = obs[i]["s"]
                    support = prediction.conf if prediction else 0.0
                    if variant == "rolling" and (
                        (point is None) != (reference is None)
                        or (point is not None and not np.allclose(point, reference, rtol=0, atol=1e-5))
                        or support != obs[i]["c"]
                    ):
                        differences.append(
                            {
                                "frame_idx": first + i,
                                "reference": reference,
                                "actual": point,
                                "reference_support": obs[i]["c"],
                                "actual_support": support,
                                "support_absolute_error": abs(support - obs[i]["c"]),
                            }
                        )
                comparisons.append(
                    {
                        "chunk": [first, last],
                        "variant": variant,
                        "elapsed_seconds": elapsed,
                        "selected_frames": len(needed),
                        "rolling_reference_differences": differences,
                    }
                )
            assert rolling_after is not None
            model.bg = rolling_after
            print(f"component chunk {first}-{last}", flush=True)
    with (output / "candidates.jsonl").open("x") as stream:
        for row in rows:
            stream.write(json.dumps(row, allow_nan=False) + "\n")
    dump(output / "comparisons.json", comparisons)
    manifest.update(
        status="completed",
        cache_sha256=cache_hashes,
        executor_sources_unchanged=executor_sources_unchanged(ROOT, executor),
        selected_frames_per_variant=sum(selection.includes(i) for i in range(selection.ranges[-1][1] + 1)),
    )
    dump(output / "manifest.json", manifest)
    if not manifest["executor_sources_unchanged"]:
        raise RuntimeError("source changed during component experiment")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--ranges", type=json.loads, required=True)
    parser.add_argument(
        "--variants",
        nargs="+",
        choices=["rolling", "fixed_startup", "zero_background"],
        default=["rolling", "fixed_startup", "zero_background"],
    )
    run(parser.parse_args())
