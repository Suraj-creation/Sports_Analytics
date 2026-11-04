"""Label-free cached semantic replay with an explicitly experimental contact policy.

This monkeypatch is process-local. It changes no production source, cache or label.
The native heatmap-cell sensitivity scale is a declared assumption, not calibration.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
from next_contact_scene_diagnostics import alternative_terms, velocity_fit
from replay_rally_evidence import replay

import bai_badminton.engine as engine_module
import bai_badminton.events.contact as contact_module

ROOT = Path(__file__).resolve().parents[1]
POLICY_ID = "contact_motion_reliability_v1_experiment"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baseline", type=Path, default=ROOT / "artifacts/benchmarking/experiments/fresh_image_exit_v1"
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--spatial-sigma", type=float, default=2.5 / math.sqrt(12))
    args = parser.parse_args()
    if not math.isfinite(args.spatial_sigma) or args.spatial_sigma <= 0:
        raise ValueError("spatial sigma must be positive and finite")
    baseline_score = contact_module.score_frame
    counts = {"scored": 0, "baseline_above_threshold": 0, "alternative_above_threshold": 0, "unknown_fit": 0}
    bounded_rows = []

    def score(window, index, half=3):
        candidate = baseline_score(window, index, half)
        if candidate is None:
            return None
        counts["scored"] += 1
        lo, hi = contact_module._context_bounds(window, index, half)
        observed = window.shuttle.vis & ~window.shuttle.interp
        xy = np.column_stack((window.shuttle.x, window.shuttle.y))
        before_indices = np.arange(max(lo, index - half), index + 1)
        before_indices = before_indices[observed[before_indices]]
        after_indices = np.arange(index, min(hi, index + half + 1))
        after_indices = after_indices[observed[after_indices]]
        before = velocity_fit(xy, before_indices, args.spatial_sigma)
        after = velocity_fit(xy, after_indices, args.spatial_sigma)
        if before is None or after is None:
            counts["unknown_fit"] += 1
            return None
        alternative = alternative_terms(before, after, candidate.scores)
        old_support = candidate.p
        counts["baseline_above_threshold"] += int(old_support >= contact_module.P_MIN)
        candidate.p = alternative["heuristic_support"]
        counts["alternative_above_threshold"] += int(candidate.p >= contact_module.P_MIN)
        candidate.scores = {
            **candidate.scores,
            "legacy_redirect": candidate.scores["redirect"],
            "legacy_impulse": candidate.scores["impulse"],
            "legacy_support": old_support,
            "redirect": alternative["redirect"],
            "impulse": alternative["impulse"],
            "incoming_direction_reliability": alternative["incoming_direction_reliability"],
            "outgoing_direction_reliability": alternative["outgoing_direction_reliability"],
            "incoming_slope_sigma_sensitivity": before["slope_sigma_sensitivity_px_per_frame"],
            "outgoing_slope_sigma_sensitivity": after["slope_sigma_sensitivity_px_per_frame"],
            "incoming_fit_samples": float(before["sample_count"]),
            "outgoing_fit_samples": float(after["sample_count"]),
            "spatial_sigma_sensitivity_px": args.spatial_sigma,
        }
        frame = window.frame0 + index
        # Debug frames are bounded and selected for diagnosis, never scoring decisions.
        if 12735 <= frame <= 12790 and len(bounded_rows) < 512:
            bounded_rows.append(
                {
                    "frame": frame,
                    "baseline_support": old_support,
                    "support": candidate.p,
                    "components": candidate.scores,
                }
            )
        return candidate

    contact_module.score_frame = score
    # The current engine uses this global label. Override only this diagnostic
    # process so experimental events cannot pretend to be legacy model output.
    engine_module.CONTACT_MODEL = POLICY_ID
    replay(
        args.baseline.resolve(),
        args.output.resolve(),
        {"use_reconstruction": False, "motion_guard": False, "use_exit_recovery": True},
        implementation="rally-evidence-v2",
        candidate=True,
    )
    sources = [
        Path(__file__),
        ROOT / "research/next_contact_scene_diagnostics.py",
        ROOT / "research/replay_rally_evidence.py",
    ]
    metadata = {
        "mode": "CPU cached full-semantic replay; NOT fresh perception inference",
        "policy": POLICY_ID,
        "sigma_sensitivity_px": args.spatial_sigma,
        "sigma_interpretation": "declared sensitivity assumption; not calibrated localization uncertainty",
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "policy_source_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
        "provenance_override": "process-local engine.CONTACT_MODEL=" + POLICY_ID,
        "rally_flags": {"use_reconstruction": False, "motion_guard": False, "use_exit_recovery": True},
        "counts_include_context_rescoring": counts,
        "limitations": [
            "No independent reviewed contact labels",
            "Cadence feedback held fixed by cached perception",
            "CPU overlap with independent fresh control affects runtime comparison",
        ],
    }
    (args.output / "contact_policy_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    (args.output / "contact_policy_bounded_trace.json").write_text(json.dumps(bounded_rows, indent=2) + "\n")
    print(json.dumps(metadata, indent=2))


if __name__ == "__main__":
    main()
