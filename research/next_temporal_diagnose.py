"""Read-only onset/end diagnostics from an interval-exact semantic replay.

Labels group offline evidence only. This tool never generates predictions,
changes inference state, or claims shuttle/contact pixel ground truth.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import msgpack

ROOT = Path(__file__).resolve().parents[1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def verify_trace_cache_identity(metadata: dict, trace: Path, paths: list[Path]) -> dict:
    """Bind a trace to exact cache bytes and input identity, not equal intervals."""
    if not paths or len({path.parent for path in paths}) != 1:
        raise ValueError("one unambiguous perception cache directory is required")
    replay_path = trace.parent / "replay_metadata.json"
    if not replay_path.is_file():
        raise ValueError("the semantic trace needs its own replay provenance manifest")
    replay = json.loads(replay_path.read_text())
    actual = {path.name: sha(path) for path in paths}
    if actual != replay["cache_sha256"]:
        raise ValueError("semantic trace belongs to different perception cache bytes")
    if sha(trace) != replay["trace_sha256"]:
        raise ValueError("semantic trace bytes differ from their replay manifest")
    if replay["video_sha256"] != metadata["source_video_sha256"]:
        raise ValueError("semantic trace belongs to a different original video")
    if replay["ground_truth_sha256"] != metadata["ground_truth_sha256"]:
        raise ValueError("semantic trace and selected run have different label provenance hashes")
    if replay.get("source_unchanged") is not True:
        raise ValueError("semantic executor source changed during the selected replay")
    return actual


def first(rows, predicate):
    return next((row["frame"] for row in rows if predicate(row)), None)


def compact(row, raw):
    evidence = row.get("evidence", {})
    return {
        "frame": row["frame"],
        "raw_xy": raw.get("s"),
        "raw_support": raw.get("c"),
        "view": raw.get("v"),
        "replay_or_excluded": raw.get("r"),
        "shot": raw.get("sh"),
        "calibration": raw.get("cs"),
        "geometry_lost": raw.get("l"),
        "detector_scheduled": raw.get("do"),
        "pose_stride": raw.get("ps"),
        "people": len(raw.get("p", [])),
        "fresh_people": sum(person.get("dm") is True for person in raw.get("p", [])),
        "pose_rows": sum(person.get("k") is not None for person in raw.get("p", [])),
        "perception_diagnostic": raw.get("dg"),
        "exit_proof": row.get("exit_proof"),
        "processed_xy": [row.get("x"), row.get("y")],
        "speed": row.get("speed"),
        "evidence": evidence,
        "before": row["before"],
        "after": row["after"],
        "update": row["update"],
    }


def summarize(start, end, matched_start, matched_end, traces, observations, activity):
    window = [row for row in traces if start <= row["frame"] <= end]
    steps = [row for row in window if row["call"] == "step"]
    candidates = [
        {
            "decision_frame": row["frame"],
            "call": row["call"],
            "start": row["update"]["started"],
        }
        for row in window
        if row["update"]["started"] is not None
    ]
    cancellations = [
        {"decision_frame": row["frame"], "start": row["update"]["cancelled_start"], "closed": row["before"]["closed"]}
        for row in window
        if row["update"]["cancelled_start"] is not None
    ]
    endings = [
        {
            "decision_frame": row["frame"],
            "tentative_end": row["after"]["tentative_end"],
            "reason": row["after"]["end_reason"],
            "kind": row.get("evidence", {}).get("kind"),
            "speed": row.get("speed"),
            "missing_run": row["after"]["invisible_run"],
        }
        for row in window
        if row["before"]["state"] != "ending" and row["after"]["state"] == "ending"
    ]
    invalid = [row["frame"] for row in steps if not row.get("evidence", {}).get("context_valid", True)]
    missing_runs = []
    run = []
    for row in steps:
        if not row.get("visible"):
            run.append(row)
        elif run:
            missing_runs.append(
                [
                    run[0]["frame"],
                    run[-1]["frame"],
                    len(run),
                    any(r.get("evidence", {}).get("exit_return_supported") for r in run),
                ]
            )
            run = []
    if run:
        missing_runs.append(
            [
                run[0]["frame"],
                run[-1]["frame"],
                len(run),
                any(r.get("evidence", {}).get("exit_return_supported") for r in run),
            ]
        )
    active = [
        event
        for event in activity
        if event["frame_end"] >= start
        and event["frame_start"] <= end
        and event["payload"].get("state") == "active_play"
    ]
    terminal = None
    if matched_start is not None:
        finalized = next(
            (
                row
                for row in traces
                if row["update"]["finalized"]
                and row["update"]["finalized"]["start"] == matched_start
                and row["update"]["finalized"]["end"] == matched_end
            ),
            None,
        )
        assert finalized is not None
        proposals = [
            row
            for row in traces
            if row["frame"] <= finalized["frame"]
            and row["before"]["state"] != "ending"
            and row["after"]["state"] == "ending"
            and row["after"]["start"] == matched_start
            and row["after"]["tentative_end"] == matched_end
        ]
        proposal = proposals[-1] if proposals else None
        closed = [
            row
            for row in traces
            if row["frame"] <= finalized["frame"]
            and row["before"]["state"] != "closed"
            and row["after"]["state"] == "closed"
            and row["after"]["closed"]
            and row["after"]["closed"]["start"] == matched_start
            and row["after"]["closed"]["end"] == matched_end
        ]
        terminal = {
            "reason": finalized["update"]["finalized"]["reason"],
            "end_proposal_frame": proposal["frame"] if proposal else None,
            "closed_frame": closed[-1]["frame"] if closed else None,
            "finalization_frame": finalized["frame"],
            "evidence_at_proposal": proposal.get("evidence") if proposal else None,
            "frames_around_endpoint": [
                compact(row, observations[row["frame"]])
                for row in traces
                if row["call"] == "step" and matched_end - 10 <= row["frame"] <= matched_end + 30
            ],
            "physical_landing": "unknown; no reviewed terminal shuttle/landing labels",
        }
    diagnostic_rows = [
        (frame, observations[frame]["dg"]["shuttle"])
        for frame in range(start, end + 1)
        if observations[frame].get("dg") is not None and observations[frame]["dg"].get("shuttle") is not None
    ]
    return {
        "interval": [start, end],
        "matched_interval": [matched_start, matched_end],
        "first_raw_shuttle": next((f for f in range(start, end + 1) if observations[f]["s"] is not None), None),
        "recorded_shuttle_diagnostics": {
            "frames_recorded": len(diagnostic_rows),
            "review_window_frames": end - start + 1,
            "first_recorded_raw_peak_above_inference_threshold": next(
                (frame for frame, diagnostic in diagnostic_rows if diagnostic["raw_peak"] >= diagnostic["threshold"]),
                None,
            ),
            "first_recorded_mask_rejection": next(
                (frame for frame, diagnostic in diagnostic_rows if diagnostic["reason"] == "mask_rejected"), None
            ),
            "decision_counts": {
                reason: sum(diagnostic["reason"] == reason for _, diagnostic in diagnostic_rows)
                for reason in ("accepted", "mask_rejected", "below_threshold", "no_positive_peak")
            },
            "scope": "first recorded diagnostic only; missing acquisition cannot establish physical absence",
        },
        "first_processed_observation": first(steps, lambda r: r.get("visible", False)),
        "first_adjacent_movement_over_start_speed": first(
            steps, lambda r: r.get("speed") is not None and r["speed"] > 3
        ),
        "first_three_sample_moving_confirmation": first(steps, lambda r: r["after"]["moving_run"] >= 3),
        "first_aligned_participant_motion": first(steps, lambda r: r.get("evidence", {}).get("player_motion") is True),
        "first_active_play_interval_overlap": min((max(start, e["frame_start"]) for e in active), default=None),
        "first_accepted_contact": first(window, lambda r: r["call"] == "contact"),
        "candidate_starts": candidates,
        "candidate_cancellations": cancellations,
        "end_proposals": endings,
        "invalid_frames": invalid,
        "missing_runs": missing_runs,
        "matched_terminal_chain": terminal,
        "meaning": (
            "Firsts are within the supplied GT review window; raw means post-provider cached output, "
            "not pre-threshold heatmap peaks. Separately listed heatmap firsts cover recorded diagnostic frames only. "
            "Motion is heuristic support, not reviewed rally truth."
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run, trace, output = args.run.resolve(), args.trace.resolve(), args.output.resolve()
    output.mkdir(parents=True, exist_ok=False)
    traces = [json.loads(line) for line in trace.open()]
    observations = {}
    paths = sorted(run.glob("runtime/sessions/*/perception/*.msgpack"))
    metadata = json.loads((run / "benchmark_metadata.json").read_text())
    verified_cache_hashes = verify_trace_cache_identity(metadata, trace, paths)
    for path in paths:
        record = msgpack.unpackb(path.read_bytes(), raw=False)
        observations.update({row["f"]: row for row in record["frames"]})
    assert set(observations) == set(range(metadata["frame_count"]))
    with (run / "rally_comparison.csv").open() as stream:
        comparison = list(csv.DictReader(stream))
    events = [json.loads(line) for line in (run / "events.jsonl").open()]
    activity = [event for event in events if event["type"] == "activity_interval"]
    inferred = json.loads((run / "inference.json").read_text())["rally_events"]
    reference = sorted((event["start"], event["end"], event["end_reason"]) for event in inferred)
    final = sorted(
        (row["update"]["finalized"]["start"], row["update"]["finalized"]["end"], row["update"]["finalized"]["reason"])
        for row in traces
        if row["update"]["finalized"]
    )
    assert final == reference
    results = []
    for item in comparison:
        start, end = int(item["gt_start_frame"]), int(item["gt_end_frame"])
        matched_start = int(item["pred_start_frame"]) if item["pred_start_frame"] else None
        matched_end = int(item["pred_end_frame"]) if item["pred_end_frame"] else None
        results.append(
            {
                "gt_rally": int(item["gt_rally"]),
                **summarize(start, end, matched_start, matched_end, traces, observations, activity),
            }
        )
    dump(output / "all_onsets_ends.json", results)
    for name, lo, hi in [
        ("gt04", 1760, 2180),
        ("gt22_23", 10530, 11100),
        ("gt27", 12420, 12990),
        ("gt31", 14390, 15190),
    ]:
        selected = [row for row in traces if lo <= row["frame"] <= hi]
        with (output / f"{name}_causal_trace.jsonl").open("w") as stream:
            for row in selected:
                value = compact(row, observations[row["frame"]]) if row["call"] == "step" else row
                stream.write(json.dumps(value, allow_nan=False) + "\n")
    manifest = {
        "mode": "offline grouping of recorded observations and exact semantic trace; no fresh inference",
        "run": str(run),
        "trace": str(trace),
        "trace_sha256": sha(trace),
        "prediction_sha256": sha(run / "predicted_rallies.csv"),
        "script_sha256": sha(Path(__file__)),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_status": subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True),
        "trace_intervals_and_end_reasons_exact": True,
        "trace_cache_bytes_and_source_identity_exact": True,
        "source_video_sha256": metadata["source_video_sha256"],
        "cache_sha256": {str(path.relative_to(ROOT)): sha(path) for path in paths},
        "cache_names_verified_against_replay": verified_cache_hashes,
        "diagnostic_availability": {
            "frames": len(observations),
            "recorded_frame_diagnostics": sum(row.get("dg") is not None for row in observations.values()),
            "recorded_shuttle_diagnostics": sum(
                row.get("dg") is not None and row["dg"].get("shuttle") is not None for row in observations.values()
            ),
            "recorded_player_diagnostics": sum(
                row.get("dg") is not None and row["dg"].get("players") is not None for row in observations.values()
            ),
            "not_recorded": sum(row.get("dg") is None for row in observations.values()),
        },
        "limits": [
            (
                "Bounded heatmap component/rejection evidence exists on selected diagnostic frames; "
                "unrecorded frames remain unavailable"
                if any(row.get("dg") is not None for row in observations.values())
                else "No heatmap component/rejection diagnostics were recorded in these selected caches"
            ),
            "Diagnostic coverage is not physical shuttle recall or localization accuracy",
            "No human onset semantics or pixel/contact labels added",
            "GT used only to group offline evidence",
        ],
    }
    dump(output / "manifest.json", manifest)
    (output / "executor.py").write_bytes(Path(__file__).read_bytes())
    for row in results:
        print(
            row["gt_rally"],
            row["interval"],
            row["matched_interval"],
            "raw",
            row["first_raw_shuttle"],
            "processed",
            row["first_processed_observation"],
            "motion",
            row["first_adjacent_movement_over_start_speed"],
            "contact",
            row["first_accepted_contact"],
            "starts",
            row["candidate_starts"],
            "cancellations",
            row["candidate_cancellations"],
        )


if __name__ == "__main__":
    main()
