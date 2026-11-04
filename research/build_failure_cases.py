"""Read-only Test 1 evidence packaging; annotations are used for review only."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.production_inference import digest, dump  # noqa: E402


def build(output, trace_path, overlays):
    import cv2
    import msgpack
    import numpy as np

    baseline = ROOT / "outputs/benchmarking/test1"
    metadata = json.loads((baseline / "benchmark_metadata.json").read_text())
    metrics = json.loads((baseline / "metrics.json").read_text())
    diagnostics = json.loads((baseline / "boundary_diagnostics.json").read_text())
    inference = json.loads((baseline / "inference.json").read_text())
    with (baseline / "rally_comparison.csv").open() as stream:
        comparisons = list(csv.DictReader(stream))
    with (ROOT / metadata["ground_truth_path"]).open() as stream:
        labels = list(csv.DictReader(stream))
    predictions = inference["rally_events"]
    observations = {}
    for path in sorted((baseline / "runtime/sessions/BenchmarkTest1/perception").glob("*.msgpack")):
        record = msgpack.unpackb(path.read_bytes(), raw=False)
        observations.update({f["f"]: f for f in record["frames"]})
    events = [json.loads(line) for line in (baseline / "raw_events.jsonl").open()]
    traces = [json.loads(line) for line in trace_path.open()]
    matched = [r for r in comparisons if r["matching_status"] == "matched"]
    worst_starts = {int(r["gt_rally"]) for r in sorted(matched, key=lambda r: -abs(float(r["start_frame_error"])))[:5]}
    worst_ends = {int(r["gt_rally"]) for r in sorted(matched, key=lambda r: -abs(float(r["end_frame_error"])))[:5]}
    controls = {int(r["gt_rally"]) for r in sorted(matched, key=lambda r: -float(r["interval_iou"]))[:4]}
    output.mkdir(parents=True, exist_ok=False)
    source = ROOT / "data/benchmarking/test1/Test1_Full_rev.mp4"
    capture = cv2.VideoCapture(str(source)) if overlays else None
    index = []
    cases = []
    for i, (label, diag) in enumerate(zip(labels, diagnostics, strict=True), 1):
        tags = ["ground_truth"]
        if diag["matching_status"] == "missed":
            tags.append("missed")
        if len(diag["overlapping_production_segments"]) > 1:
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
        relevant = [e for e in predictions if e["start"] <= hi and e["end"] >= lo]
        nearby_labels = [r for r in labels if int(r["Start_Frame"]) <= hi and int(r["End_Frame"]) >= lo]
        case = {
            "case_id": name,
            "tags": tags,
            "original_frame_range_inclusive": [lo, hi],
            "original_seconds": [lo / 30, hi / 30],
            "source_video": str(source),
            "source_sha256": metadata["source_video_sha256"],
            "ground_truth_sha256": metadata["ground_truth_sha256"],
            "ground_truth_interval": label,
            "nearby_ground_truth_intervals": nearby_labels,
            "predicted_intervals": relevant,
            "baseline_comparison": comparison,
            "observation_file": "observations.msgpack",
            "observations": "raw production proxy pixels (1280x720)",
            "state_trace": "fsm_trace.jsonl; exact interval-parity production semantic replay",
            "contacts": (
                "events.jsonl includes inferred contact candidates/provenance; "
                "these are not manually verified contacts"
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
        (folder / "execution.log").write_bytes((baseline / "execution.log").read_bytes())
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
                    x1, y1, x2, y2 = [round(v * 1.5) for v in person["b"]]
                    cv2.rectangle(image, (x1, y1), (x2, y2), (255, 190, 0), 2)
                    if person["k"] is not None:
                        for x, y, conf in person["k"]:
                            if conf >= 0.3:
                                cv2.circle(image, (round(x * 1.5), round(y * 1.5)), 3, (255, 0, 200), -1)
                if obs["s"] is not None:
                    x, y = (round(v * 1.5) for v in obs["s"])
                    cv2.circle(image, (x, y), 16, (0, 255, 255), 3)
                tile = cv2.resize(image, (768, 432))
                cv2.rectangle(tile, (0, 0), (768, 52), (0, 0, 0), -1)
                cv2.putText(
                    tile,
                    f"{name} frame {frame} t={frame / 30:.3f}s conf={obs['c']:.3f}",
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
        },
    )
    print(f"Packaged {len(index)} cases", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--trace",
        type=Path,
        default=ROOT / "artifacts/benchmarking/investigation/baseline_semantic_replay/fsm_trace.jsonl",
    )
    parser.add_argument("--overlays", action="store_true")
    args = parser.parse_args()
    build(args.output.resolve(), args.trace.resolve(), args.overlays)
