"""Diagnostic single-contact removal after unchanged scoring and peak selection.

This is an explicitly labelled causal negative control, never a production rule
or an accuracy candidate. It reads no ground-truth interval values.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from replay_rally_evidence import replay

import bai_badminton.components as components

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--suppressed-frame", type=int, required=True)
    args = parser.parse_args()
    original = components._Contact.detect
    removed = []

    def without_contact(self, window, **kwargs):
        candidates = original(self, window, **kwargs)
        result = []
        for candidate in candidates:
            if candidate.frame == args.suppressed_frame:
                removed.append(
                    {
                        "frame": candidate.frame,
                        "support": candidate.p,
                        "scores": candidate.scores,
                        "xy": candidate.shuttle_xy,
                        "model": candidate.model,
                    }
                )
            else:
                result.append(candidate)
        return result

    components._Contact.detect = without_contact
    flags = {
        "use_reconstruction": False,
        "motion_guard": False,
        "use_exit_recovery": True,
        "use_curve_exit": False,
    }
    replay(
        args.baseline.resolve(),
        args.output.resolve(),
        flags,
        implementation="rally-evidence-tracklets-v1",
        candidate=True,
    )
    if len(removed) != 1:
        raise RuntimeError(f"expected exactly one removed accepted candidate, got {len(removed)}")
    paths = [Path(__file__), ROOT / "research/replay_rally_evidence.py"]
    metadata = {
        "mode": "single-contact causal negative control on cached/hybrid perception; NOT fresh full inference",
        "intervention": "remove one selected contact after unchanged scoring/NMS; no reranking or coordinate edits",
        "suppressed_frame": args.suppressed_frame,
        "removed_candidates": removed,
        "rally_flags": flags,
        "executor_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "script_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
        "ground_truth_usage": "none during replay; evaluator may read labels only after predictions exist",
        "limits": [
            "Manual diagnostic intervention; never a prediction profile or accuracy fix",
            "Other perception and cadence remain conditional on the hybrid recorded inputs",
            "Removing a suspect contact does not classify it as a human-labelled false impact",
        ],
    }
    (args.output / "suppression_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n")
    snapshots = args.output / "executed_scripts"
    snapshots.mkdir()
    for path in paths:
        (snapshots / path.name).write_bytes(path.read_bytes())
    print(json.dumps(metadata, indent=2), flush=True)


if __name__ == "__main__":
    main()
