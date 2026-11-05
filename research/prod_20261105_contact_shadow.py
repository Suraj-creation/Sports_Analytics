"""Bounded typed-evidence audit at recorded contact timestamps; no new inference.

Recorded global-max association is not certified temporal tracking. The shadow
assessment retains unknown association/freshness rather than inventing them.
Its separate tracked-assumption trajectory branch is a diagnostic counterfactual.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from collections import Counter
from dataclasses import replace
from pathlib import Path

import numpy as np

from bai_badminton.events.contact import ContactCandidate, ContactMotionReliability, build_contact_evidence
from bai_badminton.events.contact_evidence import assess_contact_evidence
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track

ROOT = Path(__file__).resolve().parents[1]
SOURCES = (
    ROOT / "sports/badminton/src/bai_badminton/events/contact.py",
    ROOT / "sports/badminton/src/bai_badminton/events/contact_evidence.py",
    Path(__file__).resolve(),
)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spatial-sigma-px", type=float, required=True)
    args = parser.parse_args()
    policy = ContactMotionReliability(args.spatial_sigma_px)
    args.output.mkdir(parents=True, exist_ok=False)
    source_bytes = {p: p.read_bytes() for p in SOURCES}
    rows = [json.loads(line) for line in (args.run / "events.jsonl").read_text().splitlines()]
    superseded = {r["supersedes"] for r in rows if r.get("supersedes")}
    live = [
        r for r in rows if r["event_id"] not in superseded and r["status"] != "retracted" and r["type"] == "contact"
    ]
    trace = [json.loads(line) for line in args.trace.read_text().splitlines()]
    steps = {r["frame"]: r for r in trace if r["call"] == "step"}
    boundaries = {r["frame"] for r in trace if r["call"] == "discontinuity"}
    results, velocity_mismatches = [], []
    for event in live:
        frame = event["frame_start"]
        indices = np.arange(max(0, frame - 4), min(max(steps) + 1, frame + 4))
        nearby = [steps[int(f)] for f in indices]
        xy = np.asarray([[r["x"], r["y"]] for r in nearby], dtype=float)
        track = Track.from_arrays(xy[:, 0], xy[:, 1], np.asarray([r["visible"] for r in nearby]))
        track.interp[:] = [r["interpolated"] for r in nearby]
        window = WindowObs(
            int(indices[0]),
            30.0,
            track,
            {},
            replay=np.asarray([r["replay"] for r in nearby]),
            break_before=np.asarray([int(f) in boundaries for f in indices]),
        )
        scores = next(e["scores"] for e in event["evidence"] if e["kind"] == "component_scores")
        candidate = ContactCandidate(
            frame=frame,
            player_id=event["actors"]["player_id"],
            p=event["confidence"],
            scores=scores,
            shuttle_xy=(steps[frame]["x"], steps[frame]["y"]),
            attribution_reason=event["payload"].get("attribution_reason"),
            model=event["provenance"]["model"],
        )
        evidence = build_contact_evidence(window, candidate, motion_reliability=policy)
        if evidence.inputs.motion is not None:
            motion = evidence.inputs.motion
            if (
                abs(motion.speed_before - scores["speed_before"]) > 1e-3
                or abs(motion.speed_after - scores["speed_after"]) > 1e-3
            ):
                velocity_mismatches.append(frame)
        step = steps[frame]
        inputs = replace(
            evidence.inputs,
            observation_status="fresh_observed"
            if step["visible"] and not step["interpolated"]
            else "reconstructed"
            if step["interpolated"]
            else "missing",
            association_status="unknown",
            context_valid=bool(step["evidence"]["context_valid"]),
        )
        conservative = assess_contact_evidence(inputs)
        assumed = assess_contact_evidence(replace(inputs, association_status="tracked"))
        results.append(
            {
                "frame": frame,
                "legacy_support": candidate.p,
                "legacy_model": candidate.model,
                "physical_assessment": conservative.to_payload(),
                "trajectory_under_explicit_tracked_assumption": {
                    "reliability": assumed.trajectory.reliability,
                    "reasons": assumed.trajectory.reasons,
                },
            }
        )
    assert not velocity_mismatches, velocity_mismatches
    assert all(p.read_bytes() == data for p, data in source_bytes.items())
    report = {
        "schema": "badminton-contact-physical-shadow:v1",
        "mode": "same recorded contact timestamps and processed positions; no perception or semantic replay",
        "contact_count": len(results),
        "sigma_px": args.spatial_sigma_px,
        "sigma_semantics": "declared heatmap-cell sensitivity, not calibrated localization covariance",
        "physical_reliability_counts": dict(
            Counter(r["physical_assessment"]["impact"]["reliability"] for r in results)
        ),
        "tracked_assumption_trajectory_counts": dict(
            Counter(r["trajectory_under_explicit_tracked_assumption"]["reliability"] for r in results)
        ),
        "velocity_mismatch_frames": velocity_mismatches,
        "gt27_12766": next(r for r in results if r["frame"] == 12766),
        "limits": [
            "Association and person/pose/racket freshness are unknown in this shadow audit",
            "Tracked assumption is diagnostic only and never fed to inference",
            "No independently reviewed contact or shot labels; counts are not accuracy",
        ],
    }
    (args.output / "contacts.jsonl").write_text("".join(json.dumps(r, allow_nan=False) + "\n" for r in results))
    (args.output / "report.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    snapshots = args.output / "executed_source"
    snapshots.mkdir()
    for path, data in source_bytes.items():
        (snapshots / path.name).write_bytes(data)
    manifest = {
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": {str(p.relative_to(ROOT)): sha(data) for p, data in source_bytes.items()},
        "source_unchanged": True,
        "events_sha256": sha((args.run / "events.jsonl").read_bytes()),
        "trace_sha256": sha(args.trace.read_bytes()),
        "run": str(args.run.resolve()),
        "trace": str(args.trace.resolve()),
        "output_sha256": {name: sha((args.output / name).read_bytes()) for name in ("contacts.jsonl", "report.json")},
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)


if __name__ == "__main__":
    main()
