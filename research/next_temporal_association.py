"""Research-only bounded tracklet association for exit/return support.

Hypothesis: a single isolated, unsupported shuttle point can block a coherent
moving upper-image return. A continuation proof may mark that singleton as an
unassociated alternative without removing or altering the actual observation.
All existing positive brackets, context, speed, top-band and gap budgets remain
required. No start, contact, filled position, or hidden future frame is created.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from bai_badminton.events.rally_motion import image_exit_return_supported  # noqa: E402
from bai_badminton.observations import WindowObs  # noqa: E402


def _alternative_window(window: WindowObs, index: int) -> WindowObs | None:
    track = window.shuttle
    observed = track.vis & ~track.interp & np.isfinite(track.x) & np.isfinite(track.y) & ~window.replay
    if observed[index] or window.replay[index]:
        return None
    lo, hi = window.segment_bounds(index)
    left, right = index - 1, index + 1
    while left >= lo and not observed[left]:
        left -= 1
    while right < hi and not observed[right]:
        right += 1

    def isolated(point):
        return lo < point < hi - 1 and observed[point] and not observed[point - 1] and not observed[point + 1]

    candidates = [point for point in (left, right) if isolated(point)]
    if len(candidates) != 1:
        return None
    singleton = candidates[0]
    # Keep every coordinate/confidence/provenance array unchanged. This mask is
    # local to a competing continuity proof and is never emitted as perception.
    associated = track.vis.copy()
    associated[singleton] = False
    return replace(window, shuttle=replace(track, vis=associated))


def associated_exit_return_supported(window: WindowObs, index: int, **options) -> bool:
    """Original cue, or one unassociated singleton between coherent brackets.

    The one-singleton maximum is a conservative research scope, not a learned
    optimal count. Two adjacent observations (even stationary) are never ignored.
    A singleton alone never supports continuation: all original positive moving
    exit AND return bracket requirements must then pass within the supplied
    window. This function only computes support; it does not change the stream.
    """
    if image_exit_return_supported(window, index, **options):
        return True
    alternative = _alternative_window(window, index)
    return alternative is not None and image_exit_return_supported(alternative, index, **options)


def associated_loss_start(window: WindowObs, index: int) -> int:
    """Start of the candidate loss, including its unassociated singleton."""
    alternative = _alternative_window(window, index)
    if alternative is None:
        raise ValueError("no single-singleton alternative exists")
    track = alternative.shuttle
    observed = track.vis & ~track.interp & np.isfinite(track.x) & np.isfinite(track.y) & ~window.replay
    lo, _ = alternative.segment_bounds(index)
    start = index
    while start > lo and not observed[start - 1]:
        start -= 1
    return window.frame0 + start


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--confirmed-only", action="store_true")
    args = parser.parse_args()
    import bai_badminton.engine as engine
    import research.replay_rally_evidence as replay_module
    from bai_badminton.components import _EvidenceRally

    changes = []
    alternatives = {}
    gated = []

    class ConfirmedAssociationRally(_EvidenceRally):
        def step_evidence(self, observation):
            loss_start = alternatives.get(observation.frame)
            start = self.start
            if self.closed is not None:
                start = self.closed.start
            if loss_start is not None and (start is None or loss_start - start < self.params.min_frames):
                gated.append({"frame": observation.frame, "loss_start": loss_start, "provisional_start": start})
                observation = replace(observation, exit_return_supported=False)
            return super().step_evidence(observation)

    if args.confirmed_only:
        replay_module._EvidenceRally = ConfirmedAssociationRally

    def instrumented(window, index, **options):
        original = image_exit_return_supported(window, index, **options)
        associated = associated_exit_return_supported(window, index, **options)
        if original != associated:
            alternatives[window.frame0 + index] = associated_loss_start(window, index)
            changes.append(
                {
                    "frame": window.frame0 + index,
                    "window": [window.frame0, window.frame0 + window.n - 1],
                    "original": original,
                    "associated": associated,
                }
            )
        return associated

    engine.image_exit_return_supported = instrumented
    script_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    replay_module.replay(
        args.source.resolve(),
        args.output.resolve(),
        {"use_reconstruction": False, "motion_guard": False, "use_exit_recovery": True},
        implementation="rally-evidence-v2",
        candidate=True,
    )
    manifest = {
        "mode": "conditional semantic replay; no fresh model inference",
        "intervention": (
            "research-only replacement of engine image-exit support helper "
            "with bounded single-singleton tracklet association"
        ),
        "script_sha256": script_hash,
        "script_unchanged": script_hash == hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "production_source_modified": False,
        "confirmed_only": args.confirmed_only,
        "maturity_rule": (
            "loss_start - interval_start >= existing min_frames; maturity cannot be earned by waiting through this loss"
        ),
        "fixed_controls": {
            "max_gap_s": 2.0,
            "top_fraction": 0.1,
            "minimum_speed": 3.0,
            "maximum_speed": 120.0,
            "anchor_frames": 5,
            "maximum_unassociated_singletons": 1,
        },
        "observation_mutation": (
            "none; local support-mask alternative only; production raw/processed "
            "arrays and all contact inference preserved"
        ),
        "changed_support_calls": changes,
        "blocked_provisional_support_calls": gated,
    }
    (args.output / "association_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps({"changed_support_calls": len(changes), "script_hash": script_hash}), flush=True)


if __name__ == "__main__":
    main()
