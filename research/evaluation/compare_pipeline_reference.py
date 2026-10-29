"""Compare frozen pipeline runs without dropping missed, spurious or unknown events.

Example:
  .venv/bin/python research/evaluation/compare_pipeline_reference.py \
    --baseline data/audit-20261029/evaluation/baseline-0044 \
    --candidate data/audit-20261029/evaluation/candidate-0044 \
    --output data/audit-20261029/evaluation/comparison-0044.json

Only reads completed run outputs. Different source/configuration/evaluation contracts
are rejected rather than combined into a misleading before/after result.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def read(path: Path) -> dict:
    return json.loads(path.read_text())


def load_run(root: Path) -> dict:
    if (root / "failure.json").exists() or (root / "source-changed-during-run.json").exists():
        raise ValueError(f"Run has a recorded failure: {root}")
    return {
        "manifest": read(root / "run-manifest.json"),
        "inference": read(root / "inference.json"),
        "benchmark": read(root / "benchmark.json"),
    }


def compare(baseline: dict, candidate: dict) -> dict:
    for key in ("source_sha256", "annotations_sha256", "profile_sha256", "reference_split"):
        if baseline["manifest"][key] != candidate["manifest"][key]:
            raise ValueError(f"Different {key}; cannot make a controlled comparison")
    for key in ("evaluator_version", "scope", "media_sha256", "tolerance_s", "metric_semantics"):
        if baseline["benchmark"][key] != candidate["benchmark"][key]:
            raise ValueError(f"Different evaluator contract: {key}")
    for run in (baseline, candidate):
        if run["inference"]["status"] != "analysed":
            raise ValueError("Both inference runs must be complete")
    baseline_models = {item["name"]: item for item in baseline["manifest"]["models"] if item["available"]}
    candidate_models = {item["name"]: item for item in candidate["manifest"]["models"] if item["available"]}
    for name, before in baseline_models.items():
        after = candidate_models.get(name)
        if after is None or before["sha256"] != after["sha256"]:
            raise ValueError(f"An existing model artifact changed: {name}")
    left = baseline["benchmark"]["aggregate"]
    right = candidate["benchmark"]["aggregate"]
    if left["contact_detection"]["truth_count"] != right["contact_detection"]["truth_count"]:
        raise ValueError("Reference denominator changed")
    if len(baseline["benchmark"]["rallies"]) != len(candidate["benchmark"]["rallies"]):
        raise ValueError("Reference window population changed")
    for before, after in zip(baseline["benchmark"]["rallies"], candidate["benchmark"]["rallies"], strict=True):
        if before["window_frames"] != after["window_frames"]:
            raise ValueError("Reference windows changed")

    def summary(run: dict) -> dict:
        aggregate = run["benchmark"]["aggregate"]
        family = aggregate["shot_family"]
        return {
            "code_fingerprint": run["manifest"]["code_fingerprint"],
            "contact_detection": aggregate["contact_detection"],
            "known_family_macro_f1": family["known_family"]["macro_f1"],
            "family_macro_f1_including_unknown": family["macro_f1_including_unknown"],
            "unknown_predictions": family["per_class"]["unknown"]["predicted"],
            "unknown_prediction_fraction": family["unknown_prediction_fraction"],
            "family_correct": sum(item["true_positive"] for item in family["known_family"]["per_class"].values()),
            "court_side": aggregate["court_side"],
            "joint": aggregate["joint_contact_family_court_side"],
            "timestamp_mae_s": aggregate["timestamp_mae_s"],
            "inference": run["inference"],
            # Retain the full denominators, confusion matrix and per-class results.
            "aggregate": aggregate,
        }

    return {
        "comparison_version": "pipeline-reference-comparison-v1",
        "source_sha256": baseline["manifest"]["source_sha256"],
        "annotations_sha256": baseline["manifest"]["annotations_sha256"],
        "profile_sha256": baseline["manifest"]["profile_sha256"],
        "reference_split": baseline["manifest"]["reference_split"],
        "labelled_windows": len(baseline["benchmark"]["rallies"]),
        "existing_model_artifacts_unchanged": True,
        "newly_available_artifacts": sorted(candidate_models.keys() - baseline_models.keys()),
        "metric_semantics": baseline["benchmark"]["metric_semantics"],
        "baseline": summary(baseline),
        "candidate": summary(candidate),
        "limitations": [
            "Provider-refined hit anchors at +/-0.2 seconds are not independently verified physical contacts.",
            "Only the fixed labelled rally windows are scored; predictions outside them are excluded.",
            "Unknown and missed predictions remain in the reported denominators.",
            "Pretrained training overlap is unknown; this is not a general accuracy claim.",
            "0046 was reserved for this repair pass, but prior project results exist; it is not never-seen footage.",
            "Elapsed times are recorded, but concurrent machine load was not controlled for a speedup claim.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", required=True, type=Path)
    parser.add_argument("--candidate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    result = compare(load_run(args.baseline), load_run(args.candidate))
    result["baseline_path"] = str(args.baseline.resolve())
    result["candidate_path"] = str(args.candidate.resolve())
    with args.output.open("x") as output:
        output.write(json.dumps(result, indent=2, allow_nan=False) + "\n")
    print(args.output)


if __name__ == "__main__":
    main()
