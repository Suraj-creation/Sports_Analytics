"""Offline supplemental rally reporting using the unchanged benchmark evaluator.

This module has no inference entry point. Its CLI checks a completed inference
frontier before opening annotations. Positive-overlap topology is diagnostic,
not an adjudicated sporting merge/split label. Original inputs remain untouched.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.benchmarking.evaluate_rallies import (  # noqa: E402
    COMPARISON_SCHEMA,
    POLICY,
    Rally,
    evaluate,
    read_csv,
)


def digest(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def distribution(values: list[float | int]) -> dict:
    result = {"count": len(values), "values": values}
    if not values:
        return {**result, **dict.fromkeys(("mean", "median", "minimum", "maximum", "p90", "p95"))}
    array = np.asarray(values, dtype=float)
    return {
        **result,
        "mean": float(array.mean()),
        "median": float(np.median(array)),
        "minimum": float(array.min()),
        "maximum": float(array.max()),
        "p90": float(np.percentile(array, 90)),
        "p95": float(np.percentile(array, 95)),
    }


def interval_inventory(intervals: list[Rally], frame_count: int) -> dict:
    duplicates, overlaps, adjacent, out_of_range, out_of_order = [], [], [], [], []
    seen = {}
    for i, interval in enumerate(intervals, 1):
        key = interval.start_frame, interval.end_frame
        if key in seen:
            duplicates.append([seen[key], i])
        seen.setdefault(key, i)
        if not 0 <= interval.start_frame < interval.end_frame <= frame_count:
            out_of_range.append(i)
        if i > 1 and interval.start_frame < intervals[i - 2].start_frame:
            out_of_order.append(i)
        for j, previous in enumerate(intervals[: i - 1], 1):
            if min(previous.end, interval.end) > max(previous.start, interval.start):
                overlaps.append([j, i])
            elif previous.end == interval.start or interval.end == previous.start:
                adjacent.append([j, i])
    return {
        "count": len(intervals),
        "duplicate_row_pairs": duplicates,
        "positive_overlap_row_pairs": overlaps,
        "adjacent_row_pairs": adjacent,
        "out_of_range_rows": out_of_range,
        "out_of_order_rows": out_of_order,
        "boundary_range_contract": "0 <= start < end <= frame_count; end is a half-open boundary",
    }


def supplement(gt: list[Rally], pred: list[Rally], fps: float, frame_count: int) -> tuple[dict, list[dict]]:
    """Add diagnostics without changing eligibility, assignment or predictions."""
    if type(frame_count) is not int or frame_count <= 0:
        raise ValueError("positive integer frame_count required")
    metrics, rows = evaluate(gt, pred, fps)
    matched = [row for row in rows if row["matching_status"] == "matched"]
    per_gt = [[j + 1 for j, b in enumerate(pred) if min(a.end, b.end) > max(a.start, b.start)] for a in gt]
    per_pred = [[i + 1 for i, a in enumerate(gt) if min(a.end, b.end) > max(a.start, b.start)] for b in pred]
    duration_frames = [row["end_frame_error"] - row["start_frame_error"] for row in matched]
    distributions = {
        "matched_iou": distribution([row["interval_iou"] for row in matched]),
        "start_signed_frames": distribution([row["start_frame_error"] for row in matched]),
        "start_absolute_frames": distribution([row["start_frame_absolute_error"] for row in matched]),
        "end_signed_frames": distribution([row["end_frame_error"] for row in matched]),
        "end_absolute_frames": distribution([row["end_frame_absolute_error"] for row in matched]),
        "duration_signed_frames": distribution(duration_frames),
        "duration_absolute_frames": distribution([abs(value) for value in duration_frames]),
        "duration_signed_seconds": distribution([row["duration_error_sec"] for row in matched]),
    }
    topology = {
        "definition": (
            "Positive half-open interval overlap graph; geometry only, requires source review for semantic errors."
        ),
        "gt_to_predictions": per_gt,
        "prediction_to_gt": per_pred,
        "possible_split_gt_ids": [i + 1 for i, edges in enumerate(per_gt) if len(edges) > 1],
        "possible_merge_prediction_ids": [j + 1 for j, edges in enumerate(per_pred) if len(edges) > 1],
        "predictions_without_gt_overlap": [j + 1 for j, edges in enumerate(per_pred) if not edges],
        "gt_without_prediction_overlap": [i + 1 for i, edges in enumerate(per_gt) if not edges],
        "gt_inventory": interval_inventory(gt, frame_count),
        "prediction_inventory": interval_inventory(pred, frame_count),
        "exact_duplicate_predictions": interval_inventory(pred, frame_count)["duplicate_row_pairs"],
    }
    errors = {
        "early_start_gt_ids": [r["gt_rally"] for r in matched if r["start_frame_error"] < 0],
        "late_start_gt_ids": [r["gt_rally"] for r in matched if r["start_frame_error"] > 0],
        "premature_end_gt_ids": [r["gt_rally"] for r in matched if r["end_frame_error"] < 0],
        "late_end_gt_ids": [r["gt_rally"] for r in matched if r["end_frame_error"] > 0],
        "weak_iou_gt_ids": [r["gt_rally"] for r in matched if r["interval_iou"] < 0.75],
        "significant_definition": "unmatched, matched boundary absolute error >30 frames, or matched IoU <0.75",
    }
    failures = []
    for row in rows:
        significant = (
            row["matching_status"] == "missed"
            or max(row["start_frame_absolute_error"], row["end_frame_absolute_error"]) > 30
            or row["interval_iou"] < 0.75
        )
        if significant:
            failures.append(
                {
                    "case_id": f"gt_{row['gt_rally']:03d}",
                    **row,
                    "positive_overlap_prediction_ids": per_gt[row["gt_rally"] - 1],
                    "source_review_required": True,
                    "causal_classification": "unreviewed",
                }
            )
    for item in metrics["unmatched_predictions"]:
        failures.append(
            {
                "case_id": f"pred_{item['pred_rally']:03d}",
                "matching_status": "unmatched_prediction",
                **item,
                "positive_overlap_gt_ids": per_pred[item["pred_rally"] - 1],
                "source_review_required": True,
                "causal_classification": "unreviewed",
            }
        )
    extra = {
        "schema": "offline-rally-supplement-v1",
        "matching_policy": POLICY,
        "metrics": metrics,
        "distributions": distributions,
        "p95_absolute_error_frames": {
            boundary: distributions[f"{boundary}_absolute_frames"]["p95"] for boundary in ("start", "end")
        },
        "duration_error_frames": {
            "mae": float(np.mean(np.abs(duration_frames))) if duration_frames else None,
            "rmse": float(np.sqrt(np.mean(np.square(duration_frames)))) if duration_frames else None,
            "signed_bias": float(np.mean(duration_frames)) if duration_frames else None,
        },
        "topology": topology,
        "error_categories": errors,
        "failure_cases": failures,
        "no_synthetic_unmatched_boundary_errors": True,
        "component_accuracy_validated": False,
    }
    return extra, rows


def aggregate(videos: dict[str, dict]) -> dict:
    """Pool counts/sufficient statistics; macro metrics are recording means."""
    if not videos:
        raise ValueError("at least one video required")
    metrics = {name: result.get("metrics", result) for name, result in videos.items()}
    sums = {
        key: sum(m["detection"][key] for m in metrics.values())
        for key in ("ground_truth_count", "predicted_count", "true_positives", "false_positives", "false_negatives")
    }
    tp, ng, npred = sums["true_positives"], sums["ground_truth_count"], sums["predicted_count"]
    macro = {
        key: sum(m["detection"][key] for m in metrics.values()) / len(metrics) for key in ("precision", "recall", "f1")
    }
    for key in ("mean_iou", "median_iou", "minimum_iou"):
        available = [m["overlap"][key] for m in metrics.values() if m["overlap"][key] is not None]
        macro[key] = sum(available) / len(available) if available else None
    pooled_boundaries, macro_boundaries = {}, {}
    for key in ("start_frame", "end_frame", "start_time_sec", "end_time_sec", "duration_sec"):
        available = [
            m["boundary_and_duration_errors"][key]["mae"]
            for m in metrics.values()
            if m["boundary_and_duration_errors"][key]["mae"] is not None
        ]
        macro[f"{key}_mae"] = sum(available) / len(available) if available else None
        macro_boundaries[key] = {}
        for statistic in ("mae", "rmse", "median_absolute_error", "mean_signed_error", "p90_absolute_error"):
            values = [
                m["boundary_and_duration_errors"][key][statistic]
                for m in metrics.values()
                if m["boundary_and_duration_errors"][key][statistic] is not None
            ]
            macro_boundaries[key][statistic] = sum(values) / len(values) if values else None
        pooled_boundaries[key] = {}
        for statistic in ("mae", "rmse", "mean_signed_error"):
            weighted = sum(
                m["detection"]["true_positives"]
                * (m["boundary_and_duration_errors"][key][statistic] ** (2 if statistic == "rmse" else 1))
                for m in metrics.values()
                if m["detection"]["true_positives"]
            )
            value = weighted / tp if tp else None
            pooled_boundaries[key][statistic] = math.sqrt(value) if statistic == "rmse" and tp else value
    tolerance = {}
    for boundary in ("start", "end"):
        tolerance[boundary] = []
        for threshold in (1, 3, 5, 10, 15, 30):
            entries = [
                next(r for r in m["boundary_tolerances"][boundary] if r["frames"] == threshold)
                for m in metrics.values()
            ]
            count = sum(row["within_count"] for row in entries)
            conditional = [row["matched_accuracy"] for row in entries if row["matched_accuracy"] is not None]
            all_gt = [row["all_gt_accuracy"] for row in entries if row["all_gt_accuracy"] is not None]
            tolerance[boundary].append(
                {
                    "frames": threshold,
                    "within_count": count,
                    "micro_matched_accuracy": count / tp if tp else None,
                    "micro_all_gt_accuracy": count / ng if ng else None,
                    "macro_matched_accuracy": sum(conditional) / len(conditional) if conditional else None,
                    "macro_all_gt_accuracy": sum(all_gt) / len(all_gt) if all_gt else None,
                }
            )
    pooled_mean_iou = (
        sum(
            m["detection"]["true_positives"] * m["overlap"]["mean_iou"]
            for m in metrics.values()
            if m["detection"]["true_positives"]
        )
        / tp
        if tp
        else None
    )
    return {
        "video_names": list(videos),
        "macro": macro,
        "macro_boundary_statistics": macro_boundaries,
        "micro_matched_boundary_statistics": pooled_boundaries,
        "micro_matched_mean_iou": pooled_mean_iou,
        "boundary_tolerances": tolerance,
        "micro_detection": {
            **sums,
            "precision": tp / npred if npred else 0.0,
            "recall": tp / ng if ng else 0.0,
            "f1": 2 * tp / (ng + npred) if ng + npred else 0.0,
        },
        "limitations": "Descriptive exposed-recording aggregate; does not establish broad generalization.",
    }


def verify_completion(inference: dict, frame_count: int, fps: float) -> None:
    """Check recorded frontier, without claiming this alone proves fresh NN use."""
    media = inference.get("media", {})
    if inference.get("status") not in ("completed", "analysed") or (
        inference.get("frontier_frame") != frame_count - 1
        or media.get("n_frames") != frame_count
        or inference.get("frames_processed", frame_count) != frame_count
        or inference.get("cached_perception_used") is True
    ):
        raise ValueError("completed full-input inference with exact frontier required before labels")
    if not math.isclose(media.get("fps_num", 0) / media.get("fps_den", 1), fps, abs_tol=1e-9):
        raise ValueError("inference FPS differs from evaluation FPS")


def write_artifacts(output: Path, result: dict, rows: list[dict]) -> None:
    output.mkdir(parents=True, exist_ok=False)
    documents = {
        "evaluation_results.json": result["metrics"],
        "supplemental_metrics.json": result,
        "boundary_error_distributions.json": result["distributions"],
        "failure_case_index.json": result["failure_cases"],
        "unmatched_predictions.json": result["metrics"]["unmatched_predictions"],
        "unmatched_ground_truth.json": [row for row in rows if row["matching_status"] == "missed"],
    }
    for name, value in documents.items():
        (output / name).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    with (output / "per_rally_comparison.csv").open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=COMPARISON_SCHEMA)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--inference-json", type=Path, required=True)
    parser.add_argument("--frame-count", type=int, required=True)
    parser.add_argument("--fps", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    inference = json.loads(args.inference_json.read_text())
    verify_completion(inference, args.frame_count, args.fps)
    # The label read is deliberately below the recorded completion checks.
    gt, pred = read_csv(args.ground_truth, args.fps), read_csv(args.predictions, args.fps)
    result, rows = supplement(gt, pred, args.fps, args.frame_count)
    result["provenance"] = {
        str(path.resolve()): digest(path)
        for path in (
            args.ground_truth,
            args.predictions,
            args.inference_json,
            Path(__file__),
            ROOT / "scripts/benchmarking/evaluate_rallies.py",
        )
    }
    result["completion_check_scope"] = (
        "Recorded full-input frontier/FPS only; fresh inference and exact ordered frame coverage "
        "require producer evidence."
    )
    write_artifacts(args.output, result, rows)


if __name__ == "__main__":
    main()
