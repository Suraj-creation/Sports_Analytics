import pytest

from scripts.benchmarking.evaluate_rallies import Rally, evaluate, match_rallies


def rally(a, b):
    return Rally(a, b, a / 30, b / 30)


@pytest.mark.parametrize(
    "pred,tp,fp,fn",
    [
        ([(30, 90), (150, 240)], 2, 0, 0),
        ([(30, 90)], 1, 0, 1),
        ([(30, 90), (150, 240), (300, 400)], 2, 1, 0),
        ([(30, 90), (30, 90)], 1, 1, 1),
        ([(25, 95), (20, 100), (150, 240)], 2, 1, 0),
        ([(400, 500)], 0, 1, 2),
        ([], 0, 0, 2),
    ],
)
def test_counts(pred, tp, fp, fn):
    metrics, rows = evaluate([rally(30, 90), rally(150, 240)], [rally(*p) for p in pred], 30)
    d = metrics["detection"]
    assert (d["true_positives"], d["false_positives"], d["false_negatives"]) == (tp, fp, fn)
    assert len(rows) == 2
    assert len(metrics["unmatched_predictions"]) == fp


def test_global_assignment_and_order():
    gt = [rally(0, 100), rally(100, 200)]
    pred = [rally(0, 200), rally(0, 90)]
    assert match_rallies(gt, pred) == [(0, 1), (1, 0)]
    assert match_rallies(gt, list(reversed(gt))) == [(0, 1), (1, 0)]


def test_no_matches_safe():
    metrics, _ = evaluate([rally(0, 90)], [], 30)
    assert metrics["boundary_and_duration_errors"]["start_frame"]["mae"] is None
    assert metrics["overlap"]["mean_iou"] is None
    assert metrics["detection"]["f1"] == 0
    assert metrics["no_matches_reason"]
