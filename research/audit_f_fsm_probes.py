"""Read-only audit of the production rally FSM; controlled probes, not video predictions.

Run after source ../gpu-env.sh. Writes only the auditor's fresh artifact folder.
The original source, labels, baseline and evaluator are never changed.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
from collections import Counter
from dataclasses import asdict
from itertools import pairwise
from pathlib import Path

from bai_badminton.events.rally_fsm import RallyFSM, RallyParams

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts/benchmarking/investigation/audit_f"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def simulate(name, *, missing=(), contacts=(), low=(), stationary_window=10, stationary_count=7):
    """Use the exact public FSM, including the engine's adjacent-observation speed rule."""
    fsm = RallyFSM(RallyParams(fps=30, stationary_window=stationary_window, stationary_count=stationary_count))
    missing, contacts, low = set(missing), set(contacts), set(low)
    transitions, segments, cancelled = [], [], []

    def capture(frame, method, before, update):
        after = (fsm.state.value, fsm.start, fsm.tentative_end, asdict(fsm.closed) if fsm.closed else None)
        if before != after or update.started is not None or update.cancelled_start is not None or update.finalized:
            transitions.append(
                {"frame": frame, "method": method, "before": before, "after": after, "update": asdict(update)}
            )
        if update.finalized:
            segments.append(asdict(update.finalized))
        if update.cancelled_start is not None:
            cancelled.append(update.cancelled_start)

    def before():
        return (fsm.state.value, fsm.start, fsm.tentative_end, asdict(fsm.closed) if fsm.closed else None)

    for frame in range(220):
        visible = frame not in missing
        speed = (0.0 if frame in low else 12.0) if frame > 0 and frame - 1 not in missing and visible else math.nan
        if frame in contacts:
            old = before()
            capture(frame, "contact", old, fsm.on_contact(frame))
        old = before()
        capture(frame, "step", old, fsm.step(frame, visible, speed))
    old = before()
    capture(219, "flush", old, fsm.flush(219))
    return {
        "name": name,
        "parameters": asdict(fsm.params),
        "missing_frames": sorted(missing),
        "accepted_contact_frames": sorted(contacts),
        "low_speed_frames": sorted(low),
        "segments": segments,
        "cancelled_starts": cancelled,
        "transitions": transitions,
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    probes = [
        simulate("continuous moving shuttle; no player evidence can end it"),
        simulate("5-frame temporary loss", missing=range(100, 105)),
        simulate("18-frame temporary loss", missing=range(100, 118)),
        simulate("19-frame temporary loss", missing=range(100, 119)),
        simulate("19-frame loss and synthetic accepted contact on recovery", missing=range(100, 119), contacts=[119]),
        simulate("25-frame loss; interpolated positions remain unobserved", missing=range(100, 125)),
        simulate(
            "seven low-speed observations followed by missing evidence", low=range(70, 77), missing=range(77, 110)
        ),
        simulate("configured stationary_window=15", low=range(70, 220), stationary_window=15, stationary_count=10),
        simulate("configured stationary_window=5", low=range(70, 220), stationary_window=5, stationary_count=3),
        simulate("default stationary_window=10 control", low=range(70, 220)),
    ]
    # Causal assertions are about software behavior, not human rally labels.
    assert len(probes[1]["segments"]) == len(probes[2]["segments"]) == 1
    assert len(probes[3]["segments"]) == 2
    assert len(probes[4]["segments"]) == 1
    assert len(probes[5]["segments"]) == 2
    assert probes[7]["segments"][-1]["reason"] == probes[8]["segments"][-1]["reason"] == "flush"
    assert probes[9]["segments"][0]["reason"] == "stationary"

    baseline = ROOT / "outputs/benchmarking/test1"
    events = [json.loads(line) for line in (baseline / "raw_events.jsonl").open()]
    inference = json.loads((baseline / "inference.json").read_text())
    with (ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv").open() as stream:
        gt = list(csv.DictReader(stream))
    intervals = inference["rally_events"]
    per_gt = []
    for rownum, row in enumerate(gt, 1):
        start, end = int(row["Start_Frame"]), int(row["End_Frame"])
        overlapping = [x for x in intervals if x["start"] < end and x["end"] > start]
        cancelled = [
            e["frame_start"]
            for e in events
            if e["type"] == "rally_start" and e["status"] == "retracted" and start <= e["frame_start"] <= end
        ]
        per_gt.append(
            {
                "gt_row": rownum,
                "start": start,
                "end": end,
                "segments": overlapping,
                "retracted_starts_within_gt": cancelled,
                "first_fragment_start_error": min(x["start"] for x in overlapping) - start if overlapping else None,
                "last_fragment_end_error": max(x["end"] for x in overlapping) - end if overlapping else None,
                "inter_fragment_start_minus_end_gaps": [b["start"] - a["end"] for a, b in pairwise(overlapping)],
            }
        )
    result = {
        "scope": (
            "Actual production FSM synthetic probes and immutable baseline ledger audit; no real inference claimed"
        ),
        "production_fsm_sha256": digest(ROOT / "sports/badminton/src/bai_badminton/events/rally_fsm.py"),
        "baseline_raw_events_sha256": digest(baseline / "raw_events.jsonl"),
        "ground_truth_sha256": digest(ROOT / "Part2/dataset/Test1_Full/Test1_Full_rally.csv"),
        "event_counts": {
            str(k): v
            for k, v in Counter(
                (e["type"], e["status"])
                for e in events
                if e["type"] in {"rally_start", "rally_end", "contact", "shuttle_turn"}
            ).items()
        },
        "synthetic_probes": probes,
        "per_gt_ledger_analysis": per_gt,
    }
    (OUT / "fsm_probe_results.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(
        json.dumps(
            {
                "probe_count": len(probes),
                "per_gt_count": len(per_gt),
                "segments_by_probe": {
                    p["name"]: [(s["start"], s["end"], s["reason"]) for s in p["segments"]] for p in probes
                },
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
