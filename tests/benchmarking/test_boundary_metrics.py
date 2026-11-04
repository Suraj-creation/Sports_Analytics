import pytest

from scripts.benchmarking.evaluate_rallies import Rally, error_stats, evaluate, interval_iou


def test_independent_boundaries_and_duration():
    gt = [Rally(30, 90, 1, 3), Rally(150, 240, 5, 8)]
    pred = [Rally(33, 90, 1.1, 3), Rally(150, 246, 5, 8.2)]
    m, rows = evaluate(gt, pred, 30)
    e = m["boundary_and_duration_errors"]
    assert e["start_frame"]["mae"] == 1.5
    assert e["end_frame"]["mae"] == 3
    assert e["duration_sec"]["mae"] == pytest.approx(0.15)
    assert e["duration_sec"]["mean_signed_error"] == pytest.approx(0.05)
    assert rows[0]["start_frame_error"] == 3
    assert m["boundary_tolerances"]["start"][0]["matched_accuracy"] == 0.5
    assert m["boundary_tolerances"]["start"][1]["matched_accuracy"] == 1
    assert m["boundary_tolerances"]["end"][2]["within_count"] == 1


def test_error_statistics():
    s = error_stats([-3, 0, 3])
    assert s["mae"] == 2
    assert s["median_absolute_error"] == 3
    assert s["rmse"] == pytest.approx(6**0.5)
    assert s["max_absolute_error"] == s["p90_absolute_error"] == 3
    assert s["mean_signed_error"] == 0
    assert s["median_signed_error"] == 0


@pytest.mark.parametrize("fps", [25, 30, 30000 / 1001, 60])
def test_rates_and_explicit_frame_base(fps):
    gt = [Rally(1, 101, 0, 100 / fps)]
    pred = [Rally(0, 100, 0, 100 / fps)]
    m, _ = evaluate(gt, pred, fps, gt_frame_base=1)
    assert m["boundary_and_duration_errors"]["start_frame"]["mae"] == 0
    assert m["boundary_tolerances"]["start"][0]["seconds"] == 1 / fps
    m, _ = evaluate(gt, pred, fps)
    assert m["boundary_and_duration_errors"]["start_frame"]["mae"] == 1


def test_endpoint_semantics_no_inclusive_addition():
    a, b = Rally(0, 30, 0, 1), Rally(0, 31, 0, 31 / 30)
    assert interval_iou(a, b) == pytest.approx(30 / 31)
    assert interval_iou(a, Rally(30, 60, 1, 2)) == 0
    m, _ = evaluate([a], [b], 30)
    assert m["boundary_and_duration_errors"]["duration_sec"]["mae"] == pytest.approx(1 / 30)


def test_misses_remain_in_all_gt_tolerance_denominator():
    gt = [Rally(0, 30, 0, 1), Rally(60, 90, 2, 3)]
    m, _ = evaluate(gt, gt[:1], 30)
    assert m["detection"]["precision"] == 1
    assert m["detection"]["recall"] == 0.5
    assert m["detection"]["f1"] == pytest.approx(2 / 3)
    for tolerance in m["boundary_tolerances"]["start"]:
        assert tolerance["matched_accuracy"] == 1
        assert tolerance["all_gt_accuracy"] == 0.5
