"""One-variable causal counterfactual on recorded frame-pair photometric errors.

Forward/backward consistency measures reversible correspondence, not appearance
continuity. This experiment removes its multiplicative discount, leaving the
fixed adaptive ratio/intensity/feature/background/context contracts unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import deque
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads((args.source / "manifest.json").read_text())
    assert manifest["source_unchanged"] and manifest["frames"] == 17268
    source = args.source / "scene_hypotheses.jsonl"
    assert sha(source) == manifest["diagnostic_sha256"]
    args.output.mkdir(parents=True, exist_ok=False)
    histories = {}
    proposed = []
    previous_frame = None
    with (args.output / "raw_residual_hypotheses.jsonl").open("x") as stream:
        for line in source.open():
            row = json.loads(line)
            evidence = row["scene"]
            frame = evidence["frame"]
            assert previous_frame is None or frame == previous_frame + 1
            previous_frame = frame
            regions = evidence["regions"]
            if not regions:
                histories.clear()
            current = []
            for region in regions:
                key = region["region"]["key"]
                history = histories.get(key, deque(maxlen=2))
                error = region["median_patch_error"] if region["features"] >= 6 else None
                baseline = sum(history) / len(history) if len(history) == 2 else None
                ratio = error / max(1.0, baseline) if error is not None and baseline is not None else None
                if error is not None:
                    history.append(error)
                else:
                    history.clear()
                histories[key] = history
                current.append(
                    {
                        "key": key,
                        "raw_patch_error": error,
                        "previous_raw_mean": baseline,
                        "raw_adaptive_ratio": ratio,
                        "fb_consistent_fraction": region["consistent_fraction"],
                    }
                )
            keys = {region["region"]["key"] for region in regions}
            histories = {key: value for key, value in histories.items() if key in keys}
            values = [region["raw_patch_error"] for region in current]
            score = sum(values) / len(values) if values and all(value is not None for value in values) else None
            positive = bool(
                score is not None
                and score >= 15
                and evidence["background_features"] >= 6
                and evidence["background_consistent_fraction"] is not None
                and evidence["background_consistent_fraction"] >= 0.5
                and all(
                    region["raw_adaptive_ratio"] is not None and region["raw_adaptive_ratio"] >= 3 for region in current
                )
            )
            if positive:
                proposed.append(frame)
            stream.write(
                json.dumps(
                    {
                        "frame": frame,
                        "hypothesis": positive,
                        "authoritative": False,
                        "discontinuity": score,
                        "regions": current,
                        "weighted_v1_hypothesis": evidence["hypothesis"],
                    },
                    allow_nan=False,
                )
                + "\n"
            )
    result = {
        "mode": "causal scalar counterfactual on exact recorded image pair evidence; no model/event change",
        "variable": "raw median_patch_error replaces median_patch_error * (1 - FB_consistency)",
        "unchanged": [
            "all pixels/regions/photometric normalization/context",
            "prior-only history2",
            "ratio3",
            "intensity floor15",
            "background consistency.5",
            "feature minimum6",
        ],
        "source_manifest_sha256": sha(args.source / "manifest.json"),
        "source_diagnostic_sha256": sha(source),
        "script_sha256": sha(Path(__file__)),
        "hypothesis_frames": proposed,
        "weighted_v1_hypotheses": manifest["hypothesis_frames"],
        "additional_hypotheses": sorted(set(proposed) - set(manifest["hypothesis_frames"])),
        "removed_hypotheses": sorted(set(manifest["hypothesis_frames"]) - set(proposed)),
        "authoritative_decisions": 0,
        "limits": [
            "Not independently reviewed cut accuracy",
            "No threshold selected from rally labels",
            "Multiple occluders and edits can remain ambiguous",
        ],
    }
    (args.output / "manifest.json").write_text(json.dumps(result, indent=2) + "\n")
    (args.output / "executor.py").write_bytes(Path(__file__).read_bytes())
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
