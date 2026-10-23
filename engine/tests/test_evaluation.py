"""Regression tests for honest one-to-one temporal evaluation."""

import pytest


def evaluate(truth, predictions, **kwargs):
    from bai_engine.evaluation import Interval, evaluate_intervals

    return evaluate_intervals([Interval(*x) for x in truth], [Interval(*x) for x in predictions], **kwargs)


def test_merged_prediction_cannot_satisfy_two_truth_rallies():
    result = evaluate([(0, 4), (6, 10)], [(0, 10)])
    assert result["matched"] == 1
    assert result["false_negatives"] == 1
    assert result["recall"] == 0.5
    assert result["merge_candidates"] == 1


def test_duplicate_prediction_is_false_positive():
    result = evaluate([(0, 4)], [(0, 4), (0, 4)])
    assert result["matched"] == 1
    assert result["false_positives"] == 1
    assert result["precision"] == 0.5
    assert result["count_error"] == 1


def test_all_rows_contribute_to_winner_and_boundary_metrics():
    truth = [(i * 10, i * 10 + 4, "P1") for i in range(20)]
    predictions = [(i * 10, i * 10 + 4, "P1" if i < 15 else "P2") for i in range(20)]
    result = evaluate(truth, predictions)
    assert result["winner_evaluated"] == 20
    assert result["winner_accuracy"] == 0.75
    assert result["start_mae_s"] == 0


def test_empty_evidence_is_unavailable_not_perfect_or_zero_error():
    result = evaluate([], [])
    assert result["precision"] is None
    assert result["recall"] is None
    assert result["start_mae_s"] is None
    assert result["winner_accuracy"] is None


def test_unresolved_winner_is_separate_from_resolved_accuracy():
    result = evaluate([(0, 4, "P1"), (6, 10, "P2")], [(0, 4), (6, 10, "P2")])
    assert result["winner_evaluated"] == 1
    assert result["winner_unresolved"] == 1
    assert result["winner_accuracy"] == 1
    assert result["winner_resolution_rate"] == 0.5


def test_boundary_tolerance_is_independent_of_overlap_matching():
    result = evaluate([(0, 10)], [(2, 9)], boundary_tolerance_s=1)
    assert result["matched"] == 1
    assert result["start_mae_s"] == 2
    assert result["end_mae_s"] == 1
    assert result["boundary_true_positives"] == 1
    assert result["boundary_recall"] == 0.5


def test_matching_optimizes_cardinality_before_overlap():
    result = evaluate([(0, 4), (5, 9)], [(0, 9), (5, 9)])
    assert result["matched"] == 2


def test_unsorted_input_has_stable_original_index_matches():
    result = evaluate([(10, 14), (0, 4)], [(0, 4), (10, 14)])
    assert [(p["truth_index"], p["prediction_index"]) for p in result["matches"]] == [(1, 0), (0, 1)]


@pytest.mark.parametrize("start,end", [(0, 0), (2, 1), (-1, 1), (float("nan"), 1), (0, float("inf"))])
def test_invalid_intervals_rejected(start, end):
    with pytest.raises(ValueError):
        evaluate([(start, end)], [])


@pytest.mark.parametrize(
    "kwargs", [{"min_iou": 0}, {"min_iou": 2}, {"min_iou": float("nan")}, {"boundary_tolerance_s": -1}]
)
def test_invalid_policy_rejected(kwargs):
    with pytest.raises(ValueError):
        evaluate([], [], **kwargs)
