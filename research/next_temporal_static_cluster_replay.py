"""Observe static-cluster counterfactuals on actual semantic decision windows.

The observer never alters an observation, contact, interval or provider result.
Its frame ranges select diagnostic acquisition only; they do not enter a
prediction rule. All geometric alternatives remain explicitly ambiguous.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import asdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import bai_badminton.engine as engine_module  # noqa: E402
import research.replay_rally_evidence as replay_module  # noqa: E402
from research.next_temporal_static_cluster import static_cluster_exit_counterfactual  # noqa: E402


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--ranges", type=json.loads, required=True, help="Offline diagnostic names to inclusive [first,last] frames"
    )
    parser.add_argument("--heatmap-cell-px", type=float, default=2.5)
    args = parser.parse_args()
    ranges = args.ranges
    if any(type(lo) is not int or type(hi) is not int or not 0 <= lo <= hi for lo, hi in ranges.values()):
        raise ValueError("diagnostic ranges require nonnegative canonical integer bounds")
    if sum(hi - lo + 1 for lo, hi in ranges.values()) > 5000:
        raise ValueError("bounded observer allows at most 5000 selected diagnostic frames")
    active = {}
    reviews = []
    original_advance = engine_module.BadmintonMatchEngine._advance
    original_motion = engine_module.observed_participant_motion

    def tracked_advance(owner, upto):
        previous = active.get("owner")
        active["owner"] = owner
        try:
            return original_advance(owner, upto)
        finally:
            active["owner"] = previous

    def observed_motion(window, frames, index):
        # This is the exact episode window supplied while constructing the
        # current RallyObservation, before step_evidence. It shares the raw
        # engine window's shuttle/context arrays and includes only observations
        # currently available at that semantic frontier.
        answer = original_motion(window, frames, index)
        frame = window.frame0 + index
        names = [name for name, (lo, hi) in ranges.items() if lo <= frame <= hi]
        if not names:
            return answer
        owner = active["owner"]
        closed = owner.fsm.closed
        start = closed.start if closed is not None else owner.fsm.start
        track = window.shuttle
        snapshots = tuple(array.copy() for array in (track.x, track.y, track.vis, track.conf, track.interp))
        review = static_cluster_exit_counterfactual(
            window,
            index,
            frame_height=owner.cfg.frame_height,
            interval_start=start,
            minimum_event_frames=owner.fsm.params.min_frames,
            minimum_speed=owner.fsm.params.start_speed,
            heatmap_cell_px=(args.heatmap_cell_px, args.heatmap_cell_px),
            raw_xy=owner._raw_xy,
        )
        import numpy as np

        for actual, previous in zip((track.x, track.y, track.vis, track.conf, track.interp), snapshots, strict=True):
            np.testing.assert_equal(actual, previous)
        assert review.accepted_continuity is False
        frontier = window.frame0 + window.n - 1
        assert all(max(proof.after_frames) <= frontier for proof in review.counterfactuals)
        reviews.append(
            {
                "frame": frame,
                "case_acquisition_only": names,
                "available_window_half_open": [window.frame0, frontier + 1],
                "interval_start_before_step": start,
                "state_before_step": owner.fsm.state.value,
                "currently_observed": bool(track.vis[index] and not track.interp[index]),
                "raw_observation_arrays_unchanged": True,
                "review": asdict(review),
            }
        )
        return answer

    engine_module.BadmintonMatchEngine._advance = tracked_advance
    engine_module.observed_participant_motion = observed_motion
    try:
        replay_module.replay(
            args.source.resolve(),
            args.output.resolve(),
            {
                "use_reconstruction": False,
                "motion_guard": False,
                "use_exit_recovery": True,
                "use_curve_exit": False,
            },
            implementation="rally-evidence-tracklets-v1",
        )
    finally:
        engine_module.BadmintonMatchEngine._advance = original_advance
        engine_module.observed_participant_motion = original_motion
    out = args.output.resolve()
    metadata = json.loads((out / "replay_metadata.json").read_text())
    if not metadata["baseline_interval_parity"]:
        raise ValueError("observer must preserve the selected source run's predictions exactly")
    (out / "static_cluster_reviews.jsonl").write_text(
        "".join(json.dumps(row, allow_nan=False) + "\n" for row in reviews)
    )
    manifest = {
        "mode": "recorded perception diagnostic observer; no changed event decisions or fresh inference",
        "source": str(args.source.resolve()),
        "ranges_diagnostic_acquisition_only": ranges,
        "heatmap_cell_px": args.heatmap_cell_px,
        "scale_basis": "1280x720 proxy / TrackNet 512x288 heatmap = 2.5 pixels per cell; sensitivity not calibrated",
        "maximum_cluster_radius_cells": 1.0,
        "event_maturity": "existing min_frames reached at last coherent observed exit anchor, before loss",
        "unchanged_original_budgets": {"max_gap_s": 2.0, "top_fraction": 0.1, "anchor_frames": 5},
        "baseline_interval_parity": True,
        "source_unchanged": metadata["source_unchanged"],
        "current_available_window_used": True,
        "accepted_alternative_count": 0,
        "alternative_review_frames": sum(bool(row["review"]["counterfactuals"]) for row in reviews),
        "script_sha256": sha(Path(__file__)),
        "helper_sha256": sha(ROOT / "research/next_temporal_static_cluster.py"),
        "replay_script_sha256": sha(ROOT / "research/replay_rally_evidence.py"),
        "replay_metadata_sha256": sha(out / "replay_metadata.json"),
        "diagnostic_sha256": sha(out / "static_cluster_reviews.jsonl"),
        "limits": [
            "Even a coherent competing trajectory cannot distinguish a real floor stop plus separate launch",
            "Unflagged same-camera edits remain unknown context; no geometric proof authorizes a merge",
            "No raw OBSERVED point is changed to MISSING or filtered from the contact consumer",
            "No human pixel, landing, trajectory or contact ground truth was added",
        ],
    }
    (out / "static_cluster_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    for name in ranges:
        selected = [row for row in reviews if name in row["case_acquisition_only"]]
        positive = [row for row in selected if row["review"]["counterfactuals"]]
        print(name, "review_frames", len(selected), "ambiguous_alternative_frames", len(positive), flush=True)
    for name in ("next_temporal_static_cluster.py", "next_temporal_static_cluster_replay.py"):
        (out / name).write_bytes((ROOT / "research" / name).read_bytes())


if __name__ == "__main__":
    main()
