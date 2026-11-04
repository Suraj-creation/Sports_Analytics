"""Supplementary comparison of frozen rally evaluations; never changes predictions.

Ground-truth-dependent unions and cross-run overlap graphs are diagnostics only.
The production seven-column parser, matching policy and metric evaluator remain
unchanged. Outputs are written exclusively into the new experiment directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.evaluate_rallies import POLICY, Rally, evaluate, read_csv  # noqa: E402

SEVERE_ERROR_FRAMES = 30


def validate_disjoint(intervals: list[Rally], *, name: str) -> None:
    """Require chronological, positive-span, nonduplicate [start,end) intervals."""
    seen = set()
    for i, interval in enumerate(intervals):
        key = interval.start_frame, interval.end_frame
        if key in seen:
            raise ValueError(f"{name}: duplicate interval {key}")
        seen.add(key)
        if interval.end <= interval.start:
            raise ValueError(f"{name}: nonpositive interval")
        if i and intervals[i - 1].end > interval.start:
            raise ValueError(f"{name}: intervals overlap or are out of chronological order")


def _intersection(a: Rally, b: Rally) -> float:
    return max(0.0, min(a.end, b.end) - max(a.start, b.start))


def _distribution(values: list[float | int]) -> dict[str, Any]:
    return {
        "values": values,
        "count": len(values),
        "mean": statistics.mean(values) if values else None,
        "median": statistics.median(values) if values else None,
        "minimum": min(values) if values else None,
        "maximum": max(values) if values else None,
    }


def _union_length(intervals: list[tuple[float, float]]) -> float:
    result, previous_end = 0.0, -math.inf
    for start, end in sorted(intervals):
        result += max(0.0, end - max(start, previous_end))
        previous_end = max(previous_end, end)
    return result


def _telemetry(directory: Path) -> dict[str, Any]:
    fields = {
        "inference_seconds": ("elapsed_seconds", "total_inference_seconds", "total_seconds"),
        "per_stage_seconds": ("per_stage_seconds", "stage_seconds"),
        "gpu_peak_memory_bytes": ("gpu_peak_memory_bytes", "peak_gpu_memory_bytes"),
        "cpu_peak_percent": ("cpu_peak_percent", "peak_cpu_percent"),
        "frames_processed": ("frames_processed", "processed_frames"),
        "dropped_frames": ("dropped_frames",),
        "backend_status": ("perception_runtimes", "execution_backends"),
    }
    result = dict.fromkeys(fields)
    for filename in ("telemetry.json", "runtime_telemetry.json", "inference.json"):
        path = directory / filename
        if not path.is_file():
            continue
        data = json.loads(path.read_text())
        for target, candidates in fields.items():
            if result[target] is None:
                for source_key in candidates:
                    if source_key in data and data[source_key] is not None:
                        result[target] = {"value": data[source_key], "source": filename, "field": source_key}
                        break
    metadata_path = directory / "benchmark_metadata.json"
    metadata = json.loads(metadata_path.read_text()) if metadata_path.is_file() else {}
    result["recorded_resources"] = (
        {"value": metadata["resources"], "source": metadata_path.name, "field": "resources"}
        if metadata.get("resources") is not None
        else None
    )
    result["unavailable"] = [key for key, value in result.items() if value is None]
    result["note"] = (
        "Absent measurements remain null; hardware capacity and camera loss are not peak usage or dropped frames."
    )
    return result


def _run(directory: Path, gt: list[Rally], fps: float) -> tuple[dict[str, Any], list[Rally]]:
    predictions = read_csv(directory / "predicted_rallies.csv", fps)
    validate_disjoint(predictions, name=str(directory))
    metrics, comparison = evaluate(gt, predictions, fps)
    recorded = json.loads((directory / "metrics.json").read_text())
    for key in (
        "matching_policy",
        "fps",
        "detection",
        "boundary_and_duration_errors",
        "overlap",
        "boundary_tolerances",
        "missed_gt_rallies",
        "unmatched_predictions",
    ):
        if recorded.get(key) != metrics[key]:
            raise ValueError(f"{directory}: recorded {key} differs from unchanged evaluator; refusing comparison")
    per_gt = []
    for i, interval in enumerate(gt):
        overlaps = [j for j, p in enumerate(predictions) if _intersection(interval, p) > 0]
        union = _union_length(
            [(max(interval.start, predictions[j].start), min(interval.end, predictions[j].end)) for j in overlaps]
        )
        per_gt.append(
            {
                **comparison[i],
                "positive_overlap_prediction_ids": [j + 1 for j in overlaps],
                "positive_overlap_segment_count": len(overlaps),
                "gt_dependent_union_coverage_seconds": union,
                "gt_dependent_union_coverage_fraction": union / interval.duration,
                "gt_dependent_diagnostic_only": True,
                "severe_boundary_error": comparison[i]["matching_status"] == "matched"
                and max(comparison[i]["start_frame_absolute_error"], comparison[i]["end_frame_absolute_error"])
                > SEVERE_ERROR_FRAMES,
            }
        )
    matched = [row for row in per_gt if row["matching_status"] == "matched"]
    no_overlap = [
        j + 1
        for j, prediction in enumerate(predictions)
        if not any(_intersection(prediction, interval) > 0 for interval in gt)
    ]
    return {
        "directory": str(directory),
        "metrics": metrics,
        "per_gt": per_gt,
        "fragmentation": {
            "gt_with_multiple_predictions": [r["gt_rally"] for r in per_gt if r["positive_overlap_segment_count"] > 1],
            "gt_with_multiple_predictions_count": sum(r["positive_overlap_segment_count"] > 1 for r in per_gt),
            "unmatched_gt_with_partial_coverage": [
                r["gt_rally"]
                for r in per_gt
                if r["matching_status"] == "missed" and r["positive_overlap_segment_count"]
            ],
            "predictions_without_gt_overlap": no_overlap,
            "predictions_without_gt_overlap_count": len(no_overlap),
            "predicted_segments_per_gt": [r["positive_overlap_segment_count"] for r in per_gt],
        },
        "distributions": {
            "matched_iou": _distribution([r["interval_iou"] for r in matched]),
            "ground_truth_duration_seconds": _distribution([r.duration for r in gt]),
            "predicted_duration_seconds": _distribution([r.duration for r in predictions]),
            "matched_duration_signed_errors_seconds": _distribution([r["duration_error_sec"] for r in matched]),
        },
        "boundary_arrays_all_gt": {
            key: [r[key] for r in per_gt]
            for key in (
                "start_frame_error",
                "end_frame_error",
                "start_frame_absolute_error",
                "end_frame_absolute_error",
            )
        },
        "severe_boundary_gt_ids": [r["gt_rally"] for r in per_gt if r["severe_boundary_error"]],
        "telemetry": _telemetry(directory),
    }, predictions


def _cross_run(baseline: list[Rally], candidate: list[Rally]) -> dict[str, Any]:
    before_edges = [
        [j + 1 for j, current in enumerate(candidate) if _intersection(old, current) > 0] for old in baseline
    ]
    after_edges = [
        [i + 1 for i, old in enumerate(baseline) if _intersection(old, current) > 0] for current in candidate
    ]
    merges = [
        {"experiment_prediction_id": j + 1, "baseline_prediction_ids": ids}
        for j, ids in enumerate(after_edges)
        if len(ids) > 1
    ]
    splits = [
        {"baseline_prediction_id": i + 1, "experiment_prediction_ids": ids}
        for i, ids in enumerate(before_edges)
        if len(ids) > 1
    ]
    return {
        "definition": (
            "Positive [start,end) overlap graph between prediction sets; "
            "describes geometry only, not semantic merges/splits."
        ),
        "merged_interval_count": len(merges),
        "split_interval_count": len(splits),
        "merged_intervals": merges,
        "split_intervals": splits,
    }


def _fp_changes(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    old = {(r["start_frame"], r["end_frame"]): r["pred_rally"] for r in before["metrics"]["unmatched_predictions"]}
    new = {(r["start_frame"], r["end_frame"]): r["pred_rally"] for r in after["metrics"]["unmatched_predictions"]}
    return {
        "definition": (
            "Exact unmatched-interval coordinate identity. Removed/changed is not proof of semantic recovery; "
            "row IDs are local to each run."
        ),
        "resolved_or_changed_baseline_fp_ids": sorted(old[key] for key in old.keys() - new.keys()),
        "new_or_changed_experiment_fp_ids": sorted(new[key] for key in new.keys() - old.keys()),
        "unchanged_fp_intervals": [
            {"start_frame": key[0], "end_frame": key[1], "baseline_id": old[key], "experiment_id": new[key]}
            for key in sorted(old.keys() & new.keys())
        ],
    }


def compare_experiment(experiment: Path, baseline: Path, *, labels: Path | None = None) -> dict[str, Any]:
    """Validate/recompute frozen protocol, export supplementary comparison, return it."""
    experiment, baseline = experiment.resolve(), baseline.resolve()
    if experiment == baseline or experiment.is_relative_to(baseline):
        raise ValueError("comparison output must be outside the immutable baseline directory")
    for filename in ("comparison.json", "comparison.md"):
        if (experiment / filename).exists():
            raise FileExistsError(f"refusing to overwrite {experiment / filename}")
    baseline_metrics = json.loads((baseline / "metrics.json").read_text())
    fps = float(baseline_metrics["fps"])
    if labels is None:
        metadata_file = baseline / "benchmark_metadata.json"
        metadata = json.loads(metadata_file.read_text()) if metadata_file.exists() else {}
        labels = Path(metadata.get("ground_truth_path", "Part2/dataset/Test1_Full/Test1_Full_rally.csv"))
        if not labels.is_absolute():
            labels = ROOT / labels
    gt = read_csv(labels, fps)
    validate_disjoint(gt, name="ground truth")
    with labels.open("rb") as stream:
        label_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    bindings = []
    for directory in (baseline, experiment):
        path = directory / "benchmark_metadata.json"
        binding = json.loads(path.read_text()) if path.is_file() else {}
        if binding.get("ground_truth_sha256") and binding["ground_truth_sha256"] != label_hash:
            raise ValueError(f"{directory}: ground-truth hash differs from the supplied evaluation labels")
        bindings.append(binding)
    video_hashes = [m.get("source_video_sha256") for m in bindings]
    if all(video_hashes) and len(set(video_hashes)) != 1:
        raise ValueError("baseline and experiment use different source video hashes")
    before, old = _run(baseline, gt, fps)
    after, current = _run(experiment, gt, fps)
    old_misses, new_misses = set(before["metrics"]["missed_gt_rallies"]), set(after["metrics"]["missed_gt_rallies"])
    report = {
        "schema_version": 1,
        "scope": "supplementary exploratory Test1 development diagnostics",
        "matching_policy": POLICY,
        "labels": str(labels.resolve()),
        "fps": fps,
        "baseline": before,
        "experiment": after,
        "changes": {
            "resolved_missed_gt_ids": sorted(old_misses - new_misses),
            "new_missed_gt_ids": sorted(new_misses - old_misses),
            "false_positive_identity_changes": _fp_changes(before, after),
            "interval_overlap_topology": _cross_run(old, current),
            "severe_boundary_gt_resolved": sorted(
                set(before["severe_boundary_gt_ids"]) - set(after["severe_boundary_gt_ids"]) - new_misses
            ),
            "severe_boundary_gt_newly_unmatched": sorted(set(before["severe_boundary_gt_ids"]) & new_misses),
            "severe_boundary_gt_new": sorted(
                set(after["severe_boundary_gt_ids"]) - set(before["severe_boundary_gt_ids"])
            ),
        },
        "notes": [
            "Primary metrics are recomputed with the unchanged production evaluator and checked against saved metrics.",
            "GT-dependent coverage unions are diagnostic; never input to prediction or interval reconstruction.",
            "Missed-row boundary errors remain null, not zero. "
            "Severe means matched absolute boundary error >30 frames.",
            "A lost match can remove a severe-error flag; "
            "newly unmatched rows are listed separately from recovered outliers.",
            "Cross-run FP IDs and overlap topology describe interval changes, "
            "not independently verified sporting events.",
        ],
    }
    with (experiment / "comparison.json").open("x") as f:
        json.dump(report, f, indent=2, allow_nan=False)
        f.write("\n")
    lines = [
        "# Exploratory rally experiment comparison",
        "",
        "The frozen primary matching protocol is unchanged.",
        "",
        "| Metric | Baseline | Experiment |",
        "| --- | --- | --- |",
    ]
    for key in ("true_positives", "false_positives", "false_negatives", "precision", "recall", "f1"):
        lines.append(f"| {key} | {before['metrics']['detection'][key]} | {after['metrics']['detection'][key]} |")
    for key in ("mean_iou", "median_iou", "minimum_iou"):
        lines.append(f"| {key} | {before['metrics']['overlap'][key]} | {after['metrics']['overlap'][key]} |")
    for key in ("gt_with_multiple_predictions_count", "predictions_without_gt_overlap_count"):
        lines.append(f"| {key} | {before['fragmentation'][key]} | {after['fragmentation'][key]} |")
    for key in ("start_frame", "end_frame", "start_time_sec", "end_time_sec", "duration_sec"):
        for statistic in (
            "mae",
            "rmse",
            "median_absolute_error",
            "mean_signed_error",
            "p90_absolute_error",
            "max_absolute_error",
        ):
            a = before["metrics"]["boundary_and_duration_errors"][key][statistic]
            b = after["metrics"]["boundary_and_duration_errors"][key][statistic]
            lines.append(f"| {key}.{statistic} | {a} | {b} |")
    lines += [
        "",
        "All raw distributions, tolerance results, interval-overlap topology, unmatched IDs and "
        "all-GT rows are in `comparison.json`. GT-dependent unions never generate predictions. "
        "Missed-row errors are unavailable; conditional maxima do not include them as zero.",
        "",
        "| GT row | Baseline status | Experiment status | Baseline start/end frame errors | "
        "Experiment start/end frame errors |",
        "| --- | --- | --- | --- | --- |",
    ]
    for a, b in zip(before["per_gt"], after["per_gt"], strict=True):
        lines.append(
            f"| {a['gt_rally']} | {a['matching_status']} | {b['matching_status']} | "
            f"{a['start_frame_error']} / {a['end_frame_error']} | {b['start_frame_error']} / {b['end_frame_error']} |"
        )
    lines += [
        "",
        "Interval topology and ID changes:",
        "",
        "```json",
        json.dumps(report["changes"], indent=2),
        "```",
        "",
        "Telemetry uses only explicitly recorded measurements; absent measurements remain null. "
        "A hardware memory-capacity field is not peak GPU use. Full telemetry provenance is in comparison.json.",
        "",
    ]
    with (experiment / "comparison.md").open("x") as f:
        f.write("\n".join(lines))
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, default=ROOT / "outputs/benchmarking/test1")
    parser.add_argument("--labels", type=Path)
    args = parser.parse_args()
    report = compare_experiment(args.experiment, args.baseline, labels=args.labels)
    print(json.dumps(report["experiment"]["metrics"]["detection"], indent=2))


if __name__ == "__main__":
    main()
