"""Seven-column rally boundary evaluation; never used by the inference worker.

Matching is maximum-cardinality assignment of pairs with temporal IoU >= 0.5,
then maximum total IoU, with boundary proximity as a small tie-break preference.
Intervals are spans between boundary timestamps, [start, end); no extra frame
is added for an inclusive last observed frame. This matches the supplied duration.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
from scipy.optimize import linear_sum_assignment

SCHEMA = ["Start_Frame", "End_Frame", "Start_Time_sec", "End_Time_sec", "Duration_sec", "Start_Time", "End_Time"]
POLICY = {
    "version": "rally-boundaries-v1",
    "minimum_iou": 0.5,
    "assignment": "maximum cardinality, then total IoU + 1e-9/(1 + boundary distance seconds)",
    "intervals": "[start timestamp, end timestamp); duration=end-start; no inclusive-frame addition",
    "tolerance_denominators": "matched pairs and all ground-truth rallies reported separately",
    "zero_denominators": "precision/recall/F1=0; unavailable conditional metrics=null",
}


@dataclass(frozen=True)
class Rally:
    start_frame: int
    end_frame: int
    start: float
    end: float

    @property
    def duration(self):
        return self.end - self.start


def human_time(seconds):
    whole = math.floor(seconds)
    return f"{whole // 60:02d}:{whole % 60:02d}"


def validate_rate(fps):
    if not math.isfinite(fps) or fps <= 0:
        raise ValueError("FPS must be positive and finite")


def read_csv(path, fps, *, frame_base=0, time_origin=0.0):
    """Validate all seven fields; never repair, reorder, or infer missing values."""
    validate_rate(fps)
    if frame_base not in (0, 1) or not math.isfinite(time_origin):
        raise ValueError("invalid frame/time convention")
    rallies = []
    with Path(path).open(newline="", encoding="utf-8-sig") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames != SCHEMA:
            raise ValueError(f"expected exactly {SCHEMA}, got {reader.fieldnames}")
        for line, row in enumerate(reader, 2):
            try:
                if None in row or any(v is None or v == "" for v in row.values()):
                    raise ValueError("missing or extra values")
                sf, ef = int(row[SCHEMA[0]]), int(row[SCHEMA[1]])
                start, end, duration = (float(row[k]) for k in SCHEMA[2:5])
                if not all(math.isfinite(v) for v in (start, end, duration)):
                    raise ValueError("nonfinite timestamp")
                if sf < frame_base or ef <= sf or start < 0 or end <= start:
                    raise ValueError("invalid interval")
                expected = ((sf - frame_base) / fps + time_origin, (ef - frame_base) / fps + time_origin)
                if max(abs(start - expected[0]), abs(end - expected[1]), abs(duration - (end - start))) > 1e-6:
                    raise ValueError("inconsistent frame/time/duration convention")
                if [row[k] for k in SCHEMA[5:]] != [human_time(start), human_time(end)]:
                    raise ValueError("MM:SS must truncate to whole seconds")
                rallies.append(Rally(sf, ef, start, end))
            except (ValueError, TypeError) as exc:
                raise ValueError(f"{path}:{line}: {exc}") from exc
    return rallies


def write_predictions(path, intervals, fps):
    """Production frame boundaries only; deliberately no annotation argument."""
    validate_rate(fps)
    with Path(path).open("x", newline="", encoding="utf-8") as stream:
        writer = csv.writer(stream)
        writer.writerow(SCHEMA)
        for sf, ef in intervals:
            if not isinstance(sf, int) or not isinstance(ef, int) or sf < 0 or ef <= sf:
                raise ValueError("expected integer production frame boundaries with positive span")
            start, end = sf / fps, ef / fps
            writer.writerow([sf, ef, repr(start), repr(end), repr(end - start), human_time(start), human_time(end)])


def interval_iou(a, b):
    intersection = max(0.0, min(a.end, b.end) - max(a.start, b.start))
    return intersection / (a.duration + b.duration - intersection)


def match_rallies(gt, pred, minimum_iou=0.5):
    if not 0 < minimum_iou <= 1:
        raise ValueError("minimum IoU must be in (0, 1]")
    if not gt or not pred:
        return []
    # Dummies permit every interval to be unmatched. Invalid real pairs score 0.
    weights = np.zeros((len(gt), len(pred) + len(gt)))
    cardinality_bonus = 2 * (min(len(gt), len(pred)) + 1)
    eligible = set()
    for i, a in enumerate(gt):
        for j, b in enumerate(pred):
            iou = interval_iou(a, b)
            if iou >= minimum_iou:
                eligible.add((i, j))
                distance = abs(a.start - b.start) + abs(a.end - b.end)
                weights[i, j] = cardinality_bonus + iou + 1e-9 / (1 + distance)
    rows, cols = linear_sum_assignment(weights, maximize=True)
    return [(int(i), int(j)) for i, j in zip(rows, cols, strict=True) if (i, j) in eligible]


def error_stats(signed):
    if not signed:
        return dict.fromkeys(["mae", "median_absolute_error", "rmse", "max_absolute_error", "p90_absolute_error", "mean_signed_error"])
    values = np.asarray(signed, dtype=float)
    absolute = np.abs(values)
    return {
        "mae": float(absolute.mean()), "median_absolute_error": float(np.median(absolute)),
        "rmse": float(np.sqrt(np.mean(values**2))), "max_absolute_error": float(absolute.max()),
        "p90_absolute_error": float(np.percentile(absolute, 90)), "mean_signed_error": float(values.mean()),
    }


def evaluate(gt, pred, fps, minimum_iou=0.5, *, gt_frame_base=0, pred_frame_base=0):
    validate_rate(fps)
    pairs = match_rallies(gt, pred, minimum_iou)
    lookup = dict(pairs)
    used = {j for _, j in pairs}
    errors = {k: [] for k in ("start_frame", "end_frame", "start_time_sec", "end_time_sec", "duration_sec")}
    overlaps, comparison = [], []
    for i, a in enumerate(gt):
        j = lookup.get(i)
        row = {"gt_rally": i + 1, "pred_rally": None if j is None else j + 1,
               "gt_start_frame": a.start_frame, "pred_start_frame": None, "start_frame_error": None,
               "start_frame_absolute_error": None, "start_time_error_sec": None,
               "gt_end_frame": a.end_frame, "pred_end_frame": None, "end_frame_error": None,
               "end_frame_absolute_error": None, "end_time_error_sec": None,
               "gt_duration_sec": a.duration, "pred_duration_sec": None, "duration_error_sec": None,
               "duration_absolute_error_sec": None, "interval_iou": None, "matching_status": "missed"}
        if j is not None:
            b = pred[j]
            # Compare indices after explicit base normalization, never by fitted offset.
            se = (b.start_frame - pred_frame_base) - (a.start_frame - gt_frame_base)
            ee = (b.end_frame - pred_frame_base) - (a.end_frame - gt_frame_base)
            st, et, de = b.start - a.start, b.end - a.end, b.duration - a.duration
            overlap = interval_iou(a, b)
            for key, value in zip(errors, (se, ee, st, et, de), strict=True):
                errors[key].append(value)
            overlaps.append(overlap)
            row.update(pred_start_frame=b.start_frame, start_frame_error=se, start_frame_absolute_error=abs(se),
                       start_time_error_sec=st, pred_end_frame=b.end_frame, end_frame_error=ee,
                       end_frame_absolute_error=abs(ee), end_time_error_sec=et, pred_duration_sec=b.duration,
                       duration_error_sec=de, duration_absolute_error_sec=abs(de), interval_iou=overlap, matching_status="matched")
        comparison.append(row)
    tp, fp, fn = len(pairs), len(pred) - len(pairs), len(gt) - len(pairs)
    tolerance = {}
    for boundary in ("start", "end"):
        values = errors[f"{boundary}_frame"]
        tolerance[boundary] = [{"frames": n, "seconds": n / fps,
                                "within_count": sum(abs(v) <= n for v in values),
                                "matched_accuracy": sum(abs(v) <= n for v in values) / tp if tp else None,
                                "all_gt_accuracy": sum(abs(v) <= n for v in values) / len(gt) if gt else None}
                               for n in (1, 3, 5, 10, 15, 30)]
    metrics = {
        "status": "evaluated", "matching_policy": {**POLICY, "minimum_iou": minimum_iou}, "fps": fps,
        "detection": {"ground_truth_count": len(gt), "predicted_count": len(pred), "matched_count": tp,
                      "true_positives": tp, "false_positives": fp, "false_negatives": fn,
                      "precision": tp / len(pred) if pred else 0.0, "recall": tp / len(gt) if gt else 0.0,
                      "f1": 2 * tp / (len(gt) + len(pred)) if gt or pred else 0.0},
        "boundary_and_duration_errors": {key: error_stats(v) for key, v in errors.items()},
        "overlap": {"mean_iou": float(np.mean(overlaps)) if overlaps else None,
                    "median_iou": float(np.median(overlaps)) if overlaps else None,
                    "minimum_iou": min(overlaps) if overlaps else None,
                    "percent_strictly_exceeding": {str(t): 100 * sum(v > t for v in overlaps) / tp if tp else None
                                                   for t in (0.5, 0.75, 0.9, 0.95)}},
        "boundary_tolerances": tolerance,
        "missed_gt_rallies": [i + 1 for i in range(len(gt)) if i not in lookup],
        "unmatched_predictions": [{"pred_rally": j + 1, **asdict(b)} for j, b in enumerate(pred) if j not in used],
        "conditional_metrics_note": "Boundary/duration/IoU metrics condition on IoU-qualified matches; misses and extras remain in detection metrics.",
        "no_matches_reason": "No pairs satisfy the IoU eligibility threshold (or an input is empty)." if not pairs else None,
    }
    return metrics, comparison


def save_evaluation(output, gt, pred, fps, minimum_iou=0.5, **kwargs):
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    metrics, rows = evaluate(gt, pred, fps, minimum_iou, **kwargs)
    (output / "metrics.json").write_text(json.dumps(metrics, indent=2, allow_nan=False) + "\n")
    with (output / "rally_comparison.csv").open("w", newline="") as stream:
        if rows:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
    lines = ["# Rally boundary metrics", "", "Signed errors are prediction minus ground truth. Null means unavailable.", "",
             "```json", json.dumps(metrics, indent=2, allow_nan=False), "```", ""]
    (output / "metrics.md").write_text("\n".join(lines))
    return metrics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ground-truth", type=Path, required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    parser.add_argument("--fps", type=float, required=True)
    parser.add_argument("--gt-frame-base", type=int, choices=[0, 1], default=0)
    parser.add_argument("--pred-frame-base", type=int, choices=[0, 1], default=0)
    parser.add_argument("--minimum-iou", type=float, default=0.5)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    gt = read_csv(args.ground_truth, args.fps, frame_base=args.gt_frame_base)
    pred = read_csv(args.predictions, args.fps, frame_base=args.pred_frame_base)
    save_evaluation(args.output, gt, pred, args.fps, args.minimum_iou,
                    gt_frame_base=args.gt_frame_base, pred_frame_base=args.pred_frame_base)


if __name__ == "__main__":
    main()
