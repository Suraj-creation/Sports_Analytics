"""Read-only Test 1 evidence packaging; annotations are used for review only."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.production_inference import digest, dump  # noqa: E402

BASELINE = ROOT / "outputs/benchmarking/test1"
BASELINE_TRACE = ROOT / "artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl"


def positive_overlap(start, end, other_start, other_end):
    """Diagnostic interval overlap follows the evaluator's half-open contract."""
    return min(end, other_end) > max(start, other_start)


def verify_trace_binding(inputs, predictions, traces, cache_hashes, trace_sha256, source_video_sha256):
    """Bind new-run state decisions to exactly the observations supplied here.

    Only the frozen original baseline retains the historical interval-only
    compatibility check. A new run can never inherit that exception merely by
    using the same interval coordinates or borrowing the baseline trace.
    """
    finalized = [row["update"]["finalized"] for row in traces if row.get("update", {}).get("finalized") is not None]
    cache_manifest_sha256 = hashlib.sha256(
        json.dumps(cache_hashes, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    evidence = {
        "state_trace_sha256": trace_sha256,
        "observation_cache_manifest_sha256": cache_manifest_sha256,
        "observation_cache_file_count": len(cache_hashes),
        "trace_finalization_count": len(finalized),
        "prediction_count": len(predictions),
    }
    if inputs["run"] == BASELINE.resolve():
        # Preserve the explicit historical evidence path. Its legacy package
        # contract checked interval coordinates, without claiming hash binding
        # or reason/multiplicity verification. New-run packages are stricter.
        intervals = {(row["start"], row["end"]) for row in finalized}
        if sorted(intervals) != sorted((pred["start"], pred["end"]) for pred in predictions):
            raise ValueError("supplied FSM trace intervals differ from the selected run's predictions")
        return {
            **evidence,
            "trace_binding_policy": "historical_frozen_baseline_interval_only_compatibility",
            "trace_interval_parity_verified": True,
            "cache_trace_hash_binding_verified": False,
            "end_reason_and_multiplicity_verified": False,
        }

    replay_metadata_path = inputs["trace"].parent / "replay_metadata.json"
    if not replay_metadata_path.is_file():
        raise ValueError("non-baseline evidence requires replay_metadata.json beside the supplied trace")
    metadata_bytes = replay_metadata_path.read_bytes()
    replay_metadata = json.loads(metadata_bytes)
    if replay_metadata.get("trace_sha256") != trace_sha256:
        raise ValueError("supplied FSM trace SHA256 differs from replay metadata")
    if replay_metadata.get("cache_sha256") != cache_hashes or not cache_hashes:
        raise ValueError("supplied full observation cache SHA256 manifest differs from replay metadata")
    if replay_metadata.get("video_sha256") != source_video_sha256:
        raise ValueError("supplied FSM replay belongs to a different source video")
    try:
        actual = sorted((row["start"], row["end"], row["reason"]) for row in finalized)
        expected = sorted((pred["start"], pred["end"], pred["end_reason"]) for pred in predictions)
    except KeyError as exc:
        raise ValueError("non-baseline finalizations require explicit start/end/end-reason evidence") from exc
    if actual != expected:
        raise ValueError("supplied FSM trace interval/end-reason list differs, including finalization multiplicity")
    return {
        **evidence,
        "trace_binding_policy": "complete_cache_and_trace_sha256_plus_exact_finalization_list_v1",
        "replay_metadata_source": str(replay_metadata_path),
        "replay_metadata_sha256": hashlib.sha256(metadata_bytes).hexdigest(),
        "trace_interval_parity_verified": True,
        "cache_trace_hash_binding_verified": True,
        "end_reason_and_multiplicity_verified": True,
    }


def resolve_inputs(run=BASELINE, cache_source=None, trace_path=None):
    """Choose explicit run evidence; never silently borrow a new run's trace."""
    run = Path(run).resolve()
    cache_source = run if cache_source is None else Path(cache_source).resolve()
    if not run.is_dir():
        raise FileNotFoundError(f"run directory does not exist: {run}")
    if cache_source.name == "perception" and cache_source.is_dir():
        caches = [cache_source]
    else:
        caches = sorted(p for p in cache_source.glob("runtime/sessions/*/perception") if p.is_dir())
    if len(caches) != 1:
        raise ValueError(f"expected exactly one perception cache under {cache_source}, found {len(caches)}")
    if trace_path is None:
        if run != BASELINE.resolve():
            raise ValueError("--trace is required for a non-baseline run; no baseline trace is substituted")
        trace_path = BASELINE_TRACE
    trace_path = Path(trace_path).resolve()
    if not trace_path.is_file():
        raise FileNotFoundError(f"state trace does not exist: {trace_path}")
    event_files = [run / name for name in ("raw_events.jsonl", "events.jsonl") if (run / name).is_file()]
    if len(event_files) != 1:
        raise ValueError(f"expected exactly one raw_events.jsonl or events.jsonl under {run}")
    cache = caches[0]
    conditional = not cache.is_relative_to(run / "runtime/sessions")
    mode = (
        "conditional replay using externally recorded observations"
        if conditional
        else "selected-run recorded observations"
    )
    return {
        "run": run,
        "cache": cache,
        "trace": trace_path,
        "events": event_files[0],
        "observation_mode": mode,
        "conditional": conditional,
    }


def build(output, trace_path=None, overlays=False, *, run=BASELINE, cache_source=None):
    import cv2
    import msgpack
    import numpy as np

    inputs = resolve_inputs(run, cache_source, trace_path)
    run, trace_path = inputs["run"], inputs["trace"]
    output = Path(output).resolve()
    if output.is_relative_to(BASELINE.resolve()):
        raise ValueError("failure-case output cannot modify the frozen baseline directory")
    packager_source = Path(__file__).resolve()
    packager_bytes = packager_source.read_bytes()
    packager_sha256 = hashlib.sha256(packager_bytes).hexdigest()
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    metrics = json.loads((run / "metrics.json").read_text())
    inference = json.loads((run / "inference.json").read_text())
    fps = float(metadata["video_fps"])
    with (run / "rally_comparison.csv").open() as stream:
        comparisons = list(csv.DictReader(stream))
    with (ROOT / metadata["ground_truth_path"]).open() as stream:
        labels = list(csv.DictReader(stream))
    if [int(row["gt_rally"]) for row in comparisons] != list(range(1, len(labels) + 1)):
        raise ValueError("comparison rows must represent every ground-truth interval in order")
    predictions = inference["rally_events"]
    cache_metadata = inputs["cache"].parents[3] / "benchmark_metadata.json"
    if cache_metadata.is_file():
        recorded = json.loads(cache_metadata.read_text())
        if recorded["source_video_sha256"] != metadata["source_video_sha256"]:
            raise ValueError("observation cache belongs to a different source video")
    observations, cache_hashes = {}, {}
    for path in sorted(inputs["cache"].glob("*.msgpack")):
        data = path.read_bytes()
        cache_hashes[path.name] = hashlib.sha256(data).hexdigest()
        record = msgpack.unpackb(data, raw=False)
        for frame in record["frames"]:
            if frame["f"] in observations:
                raise ValueError("observation cache contains duplicate source frame identities")
            observations[frame["f"]] = frame
    if set(observations) != set(range(metadata["frame_count"])):
        raise ValueError("observation cache must cover every original frame without gaps")
    events = [json.loads(line) for line in inputs["events"].open()]
    trace_bytes = trace_path.read_bytes()
    traces = [json.loads(line) for line in trace_bytes.splitlines()]
    trace_binding = verify_trace_binding(
        inputs,
        predictions,
        traces,
        cache_hashes,
        hashlib.sha256(trace_bytes).hexdigest(),
        metadata["source_video_sha256"],
    )
    evidence = {
        "run_directory": str(run),
        "observation_cache_directory": str(inputs["cache"]),
        "observation_mode": inputs["observation_mode"],
        "conditional_observation_replay": inputs["conditional"],
        "state_trace_source": str(trace_path),
        **trace_binding,
        "event_source": str(inputs["events"]),
        "packager_source": str(packager_source),
        "packager_source_sha256": packager_sha256,
        "packager_source_snapshot": str(output / "executed_build_failure_cases.py"),
    }
    matched = [r for r in comparisons if r["matching_status"] == "matched"]
    worst_starts = {int(r["gt_rally"]) for r in sorted(matched, key=lambda r: -abs(float(r["start_frame_error"])))[:5]}
    worst_ends = {int(r["gt_rally"]) for r in sorted(matched, key=lambda r: -abs(float(r["end_frame_error"])))[:5]}
    controls = {int(r["gt_rally"]) for r in sorted(matched, key=lambda r: -float(r["interval_iou"]))[:4]}
    output.mkdir(parents=True, exist_ok=False)
    with (output / "executed_build_failure_cases.py").open("xb") as stream:
        stream.write(packager_bytes)
    source = ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4"
    media = inference["media"]
    width, height = media["width"], media["height"]
    scale_x = media["source_width"] / width
    scale_y = media["source_height"] / height
    capture = cv2.VideoCapture(str(source)) if overlays else None
    index = []
    cases = []
    for i, label in enumerate(labels, 1):
        tags = ["ground_truth"]
        if comparisons[i - 1]["matching_status"] == "missed":
            tags.append("missed")
        overlapping = [
            pred
            for pred in predictions
            if positive_overlap(pred["start"], pred["end"], int(label["Start_Frame"]), int(label["End_Frame"]))
        ]
        if len(overlapping) > 1:
            tags.append("multiple_segments")
        if i in worst_starts:
            tags.append("large_start_error")
        if i in worst_ends:
            tags.append("large_end_error")
        if i in controls:
            tags.append("control")
        cases.append(
            (f"gt_{i:02d}", int(label["Start_Frame"]), int(label["End_Frame"]), label, tags, comparisons[i - 1])
        )
    for pred in metrics["unmatched_predictions"]:
        cases.append(
            (
                f"fp_{pred['pred_rally']:02d}",
                pred["start_frame"],
                pred["end_frame"],
                None,
                ["false_positive_under_fixed_matching"],
                pred,
            )
        )
    for name, start, end, label, tags, comparison in cases:
        folder = output / name
        folder.mkdir()
        lo, hi = max(0, start - 60), min(metadata["frame_count"] - 1, end + 60)
        # Frame-extraction windows are inclusive [lo,hi]; interval comparisons
        # use their equivalent half-open [lo,hi+1) span.
        relevant = [e for e in predictions if positive_overlap(e["start"], e["end"], lo, hi + 1)]
        nearby_labels = [r for r in labels if positive_overlap(int(r["Start_Frame"]), int(r["End_Frame"]), lo, hi + 1)]
        case = {
            "case_id": name,
            "tags": tags,
            "original_frame_range_inclusive": [lo, hi],
            "original_seconds": [lo / fps, hi / fps],
            "source_video": str(source),
            "source_sha256": metadata["source_video_sha256"],
            "ground_truth_sha256": metadata["ground_truth_sha256"],
            "ground_truth_interval": label,
            "nearby_ground_truth_intervals": nearby_labels,
            "predicted_intervals": relevant,
            "baseline_comparison" if run == BASELINE.resolve() else "run_comparison": comparison,
            "evidence_provenance": evidence,
            "observation_file": "observations.msgpack",
            "observations": f"raw production proxy pixels ({width}x{height})",
            "state_trace": f"fsm_trace.jsonl; {trace_binding['trace_binding_policy']}",
            "contacts": (
                "events.jsonl includes inferred contact candidates/provenance; these are not manually verified contacts"
            ),
            "log": (
                "execution.log is the original session log; it lacks per-frame timestamps, "
                "so a per-case log slice cannot be invented"
            ),
        }
        dump(folder / "case.json", case)
        (folder / "observations.msgpack").write_bytes(
            msgpack.packb([observations[f] for f in range(lo, hi + 1)], use_bin_type=True)
        )
        with (folder / "events.jsonl").open("w") as stream:
            for event in events:
                if (
                    event["frame_start"] <= hi
                    and event["frame_end"] >= lo
                    and event["type"]
                    in {
                        "contact",
                        "shuttle_turn",
                        "rally_start",
                        "rally_end",
                        "scene",
                        "activity_interval",
                        "format_decision",
                    }
                ):
                    stream.write(json.dumps(event) + "\n")
        with (folder / "fsm_trace.jsonl").open("w") as stream:
            for row in traces:
                if lo <= row["frame"] <= hi:
                    stream.write(json.dumps(row, allow_nan=False) + "\n")
        (folder / "execution.log").write_bytes((run / "execution.log").read_bytes())
        if capture is not None:
            points = sorted({start, end, *(e["start"] for e in relevant), *(e["end"] for e in relevant)})
            points = [f for f in points if lo <= f <= hi][:8]
            tiles = []
            for frame in points:
                capture.set(cv2.CAP_PROP_POS_FRAMES, frame)
                ok, image = capture.read()
                if not ok:
                    raise RuntimeError(f"cannot decode original frame {frame}")
                obs = observations[frame]
                for person in obs["p"]:
                    x1, y1, x2, y2 = [
                        round(v * scale)
                        for v, scale in zip(person["b"], (scale_x, scale_y, scale_x, scale_y), strict=True)
                    ]
                    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 190, 0), 2)
                    if person["k"] is not None:
                        for x, y, conf in person["k"]:
                            if conf >= 0.3:
                                cv2.circle(image, (round(x * scale_x), round(y * scale_y)), 3, (255, 0, 200), -1)
                if obs["s"] is not None:
                    x, y = (round(v * scale) for v, scale in zip(obs["s"], (scale_x, scale_y), strict=True))
                    cv2.circle(image, (x, y), 16, (0, 255, 255), 3)
                tile = cv2.resize(image, (768, 432))
                cv2.rectangle(tile, (0, 0), (768, 52), (0, 0, 0), -1)
                cv2.putText(
                    tile,
                    f"{name} frame {frame} t={frame / fps:.3f}s conf={obs['c']:.3f}",
                    (8, 23),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (255, 255, 255),
                    1,
                )
                cv2.putText(
                    tile,
                    f"view={obs['v']} calibration={obs['cs']} | model observations, not labels",
                    (8, 46),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.5,
                    (255, 255, 255),
                    1,
                )
                tiles.append(tile)
            while len(tiles) % 2:
                tiles.append(np.zeros((432, 768, 3), dtype=np.uint8))
            montage = np.vstack([np.hstack(tiles[i : i + 2]) for i in range(0, len(tiles), 2)])
            cv2.imwrite(str(folder / "boundary_overlay.jpg"), montage)
        index.append(
            {"case_id": name, "tags": tags, "frame_range": [lo, hi], "manifest_sha256": digest(folder / "case.json")}
        )
    if capture is not None:
        capture.release()
    dump(
        output / "index.json",
        {
            "cases": index,
            "case_count": len(index),
            "controls": sorted(controls),
            "misses": metrics["missed_gt_rallies"],
            "false_positive_count": len(metrics["unmatched_predictions"]),
            "review_only": True,
            "not_prediction_input": True,
            "source_video_sha256": metadata["source_video_sha256"],
            "ground_truth_sha256": metadata["ground_truth_sha256"],
            "evidence_provenance": evidence,
        },
    )
    print(f"Packaged {len(index)} cases", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--run", type=Path, default=BASELINE, help="run whose predictions, metrics and events are reviewed"
    )
    parser.add_argument(
        "--cache-source",
        type=Path,
        help="run root or explicit perception directory; external observations are conditional",
    )
    parser.add_argument(
        "--trace",
        type=Path,
        help="explicit interval-parity FSM trace; required for every non-baseline run",
    )
    parser.add_argument("--overlays", action="store_true")
    args = parser.parse_args()
    build(args.output, args.trace, args.overlays, run=args.run, cache_source=args.cache_source)
