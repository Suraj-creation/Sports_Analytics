"""Versioned, deterministic evaluation of temporal intervals in media seconds.

Intervals are half-open. Matching preserves chronological order, maximizes match
count, then summed IoU. It is one-to-one: merged/duplicate predictions cannot
inflate recall. Missing denominators produce None, never manufactured accuracy.
This module evaluates supplied labels; it does not validate their provenance.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

EVALUATOR_VERSION = "temporal-intervals-v1"


@dataclass(frozen=True)
class Interval:
    start_s: float
    end_s: float
    winner: str | None = None

    def __post_init__(self) -> None:
        if not (math.isfinite(self.start_s) and math.isfinite(self.end_s)):
            raise ValueError("interval timestamps must be finite")
        if self.start_s < 0 or self.end_s <= self.start_s:
            raise ValueError("interval must have nonnegative start and positive duration")


def temporal_iou(left: Interval, right: Interval) -> float:
    overlap = max(0.0, min(left.end_s, right.end_s) - max(left.start_s, right.start_s))
    union = max(left.end_s, right.end_s) - min(left.start_s, right.start_s)
    return overlap / union


def _ratio(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def evaluate_intervals(
    truth: list[Interval],
    predictions: list[Interval],
    *,
    min_iou: float = 0.2,
    boundary_tolerance_s: float = 1.0,
) -> dict[str, Any]:
    """Evaluate every interval; winner accuracy excludes unresolved predictions.

    IoU identifies matched rallies. Start/end boundaries within the independent
    tolerance count as boundary true positives. Split/merge candidates count
    intervals overlapping multiple counterparts above min_iou, not diagnoses.
    Complexity is O(len(truth) * len(predictions)); intended for labelled clips
    or complete matches, not per-frame tracking. Labels must describe the same
    source, media origin, annotated window and split as the predictions.
    """
    if not math.isfinite(min_iou) or not 0 < min_iou <= 1:
        raise ValueError("min_iou must be finite in (0, 1]")
    if not math.isfinite(boundary_tolerance_s) or boundary_tolerance_s < 0:
        raise ValueError("boundary tolerance must be finite and nonnegative")
    gt = sorted(enumerate(truth), key=lambda item: (item[1].start_s, item[1].end_s, item[0]))
    pred = sorted(enumerate(predictions), key=lambda item: (item[1].start_s, item[1].end_s, item[0]))
    n, m = len(gt), len(pred)
    overlap = [[temporal_iou(g, p) for _, p in pred] for _, g in gt]
    # Lexicographic objective; deterministic ties prefer matching, then GT skip.
    score = [[(0, 0.0)] * (m + 1) for _ in range(n + 1)]
    choice = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            best, action = score[i - 1][j], 1
            if score[i][j - 1] > best:
                best, action = score[i][j - 1], 2
            iou = overlap[i - 1][j - 1]
            if iou >= min_iou:
                previous = score[i - 1][j - 1]
                candidate = (previous[0] + 1, previous[1] + iou)
                if candidate >= best:
                    best, action = candidate, 3
            score[i][j], choice[i][j] = best, action
    pairs: list[tuple[int, int]] = []
    i, j = n, m
    while i and j:
        action = choice[i][j]
        if action == 3:
            pairs.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif action == 1:
            i -= 1
        else:
            j -= 1
    pairs.reverse()
    matches = []
    winner_correct = winner_evaluated = winner_unresolved = winner_labelled = 0
    boundaries = 0
    start_errors, end_errors = [], []
    for gi, pi in pairs:
        gidx, g = gt[gi]
        pidx, p = pred[pi]
        start_error, end_error = abs(g.start_s - p.start_s), abs(g.end_s - p.end_s)
        start_errors.append(start_error)
        end_errors.append(end_error)
        boundaries += int(start_error <= boundary_tolerance_s) + int(end_error <= boundary_tolerance_s)
        if g.winner is not None:
            winner_labelled += 1
            if p.winner is None:
                winner_unresolved += 1
            else:
                winner_evaluated += 1
                winner_correct += int(p.winner == g.winner)
        matches.append(
            {
                "truth_index": gidx,
                "prediction_index": pidx,
                "iou": overlap[gi][pi],
                "start_error_s": start_error,
                "end_error_s": end_error,
            }
        )
    count = len(pairs)
    return {
        "evaluator_version": EVALUATOR_VERSION,
        "policy": {
            "min_iou": min_iou,
            "boundary_tolerance_s": boundary_tolerance_s,
            "matching": "chronological_max_cardinality_then_iou",
            "intervals": "half_open_seconds",
        },
        "truth_count": n,
        "prediction_count": m,
        "matched": count,
        "false_positives": m - count,
        "false_negatives": n - count,
        "count_error": m - n,
        "absolute_count_error": abs(m - n),
        "precision": _ratio(count, m),
        "recall": _ratio(count, n),
        "f1": _ratio(2 * count, n + m),
        "start_mae_s": sum(start_errors) / count if count else None,
        "end_mae_s": sum(end_errors) / count if count else None,
        "boundary_true_positives": boundaries,
        "boundary_precision": _ratio(boundaries, 2 * m),
        "boundary_recall": _ratio(boundaries, 2 * n),
        "winner_correct": winner_correct,
        "winner_evaluated": winner_evaluated,
        "winner_unresolved": winner_unresolved,
        "winner_accuracy": _ratio(winner_correct, winner_evaluated),
        "winner_resolution_rate": _ratio(winner_evaluated, winner_labelled),
        "split_candidates": sum(sum(value >= min_iou for value in row) > 1 for row in overlap),
        "merge_candidates": sum(sum(overlap[i][j] >= min_iou for i in range(n)) > 1 for j in range(m)),
        "matches": matches,
    }
