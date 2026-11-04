"""Explicitly scoped causal review of hybrid component/semantic evidence.

Fresh shuttle inference and cached other perception are never presented as a
fresh complete pipeline. The component's copied reference rally intervals are
not used: the selected semantic CSV and exact trace define the reviewed events.
Ground truth is used only for offline grouping after predictions exist.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path

import msgpack

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from research.next_temporal_diagnose import compact, summarize  # noqa: E402


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_rows(path):
    with path.open() as stream:
        return list(csv.DictReader(stream))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--perception-run", type=Path, required=True)
    parser.add_argument("--semantic-run", type=Path, required=True)
    parser.add_argument("--reference-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    perception, semantic, reference, output = (
        path.resolve() for path in (args.perception_run, args.semantic_run, args.reference_run, args.output)
    )
    output.mkdir(parents=True, exist_ok=False)
    metadata = json.loads((perception / "benchmark_metadata.json").read_text())
    replay = json.loads((semantic / "replay_metadata.json").read_text())
    assert metadata["reference_rally_intervals_only"] is True
    assert replay["video_sha256"] == metadata["source_video_sha256"]
    observations, cache_hashes = {}, {}
    for path in sorted(perception.glob("runtime/sessions/*/perception/*.msgpack")):
        cache_hashes[path.name] = sha(path)
        record = msgpack.unpackb(path.read_bytes(), raw=False)
        observations.update({row["f"]: row for row in record["frames"]})
    assert cache_hashes == replay["cache_sha256"], "Trace must use these exact hybrid observations"
    assert set(observations) == set(range(metadata["frame_count"]))
    trace_file = semantic / "fsm_trace.jsonl"
    assert sha(trace_file) == replay["trace_sha256"]
    traces = [json.loads(line) for line in trace_file.open()]
    final = sorted(
        (row["update"]["finalized"]["start"], row["update"]["finalized"]["end"])
        for row in traces
        if row["update"]["finalized"]
    )
    predictions = sorted(
        (int(row["Start_Frame"]), int(row["End_Frame"])) for row in read_rows(semantic / "predicted_rallies.csv")
    )
    assert predictions == final
    events = [json.loads(line) for line in (semantic / "events.jsonl").open()]
    superseded = {event["supersedes"] for event in events if event.get("supersedes")}
    current_ends = sorted(
        (event["frame_start"], event["frame_end"])
        for event in events
        if event["type"] == "rally_end" and event["event_id"] not in superseded and event["status"] != "retracted"
    )
    assert current_ends == predictions
    activity = [event for event in events if event["type"] == "activity_interval"]
    comparison = read_rows(semantic / "rally_comparison.csv")
    previous = read_rows(reference / "rally_comparison.csv")
    assert len(comparison) == len(previous)
    rows = []
    for item, old in zip(comparison, previous, strict=True):
        assert item["gt_rally"] == old["gt_rally"]
        start, end = int(item["gt_start_frame"]), int(item["gt_end_frame"])
        matched_start = int(item["pred_start_frame"]) if item["pred_start_frame"] else None
        matched_end = int(item["pred_end_frame"]) if item["pred_end_frame"] else None
        rows.append(
            {
                "gt_rally": int(item["gt_rally"]),
                **summarize(start, end, matched_start, matched_end, traces, observations, activity),
                "v1_matched_interval": [old["pred_start_frame"] or None, old["pred_end_frame"] or None],
                "v1_boundary_errors": [old["start_frame_error"] or None, old["end_frame_error"] or None],
                "boundary_errors": [item["start_frame_error"] or None, item["end_frame_error"] or None],
            }
        )
    (output / "all_onsets_ends.json").write_text(json.dumps(rows, indent=2, allow_nan=False) + "\n")
    for name, lo, hi in [("gt23", 10720, 11100), ("gt27", 12730, 12990), ("gt31", 14390, 14720)]:
        with (output / f"{name}_causal_trace.jsonl").open("w") as stream:
            for row in traces:
                if lo <= row["frame"] <= hi:
                    value = compact(row, observations[row["frame"]]) if row["call"] == "step" else dict(row)
                    value["exit_proof"] = row.get("exit_proof")
                    value["perception_diagnostic"] = observations[row["frame"]].get("dg")
                    stream.write(json.dumps(value, allow_nan=False) + "\n")
    manifest = {
        "mode": "offline causal review of fresh shuttle + cached other perception; NOT fresh full pipeline",
        "perception_run": str(perception),
        "semantic_run": str(semantic),
        "reference_run": str(reference),
        "component_copied_reference_intervals_ignored": True,
        "cache_hashes_exact": True,
        "trace_events_csv_intervals_exact": True,
        "source_video_sha256": metadata["source_video_sha256"],
        "trace_sha256": sha(trace_file),
        "prediction_sha256": sha(semantic / "predicted_rallies.csv"),
        "script_sha256": sha(Path(__file__)),
        "summarizer_sha256": sha(ROOT / "research/next_temporal_diagnose.py"),
        "limitations": [
            "Other perception is frozen from v1",
            "Raw means accepted provider output in first-observation table",
            "No reviewed pixel/contact/onset labels added",
        ],
    }
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (output / "executor.py").write_bytes(Path(__file__).read_bytes())
    for row in rows:
        print(
            row["gt_rally"],
            row["v1_boundary_errors"],
            "->",
            row["boundary_errors"],
            "raw/processed/motion/contact",
            row["first_raw_shuttle"],
            row["first_processed_observation"],
            row["first_adjacent_movement_over_start_speed"],
            row["first_accepted_contact"],
            "starts",
            row["candidate_starts"],
            "cancelled",
            row["candidate_cancellations"],
        )


if __name__ == "__main__":
    main()
