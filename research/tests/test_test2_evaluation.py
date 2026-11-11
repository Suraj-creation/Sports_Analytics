"""Unchanged matching, unmatched accounting and diagnostic topology controls."""

import copy

import pytest

from research.test2_evaluation import aggregate, supplement, verify_completion, write_artifacts
from scripts.benchmarking.evaluate_rallies import Rally, evaluate


def r(start, end):
    return Rally(start, end, start / 30, end / 30)


def test_supplement_retains_exact_existing_evaluation_and_null_missed_boundaries():
    gt, pred = [r(0, 100), r(200, 300)], [r(2, 98), r(400, 500)]
    frozen_metrics, frozen_rows = evaluate(gt, pred, 30)
    result, rows = supplement(gt, pred, 30, 600)
    assert result["metrics"] == frozen_metrics
    assert rows == frozen_rows
    assert rows[1]["start_frame_error"] is None
    assert result["metrics"]["detection"]["false_positives"] == 1
    assert result["metrics"]["detection"]["false_negatives"] == 1
    assert result["distributions"]["start_signed_frames"]["count"] == 1
    assert {item["case_id"] for item in result["failure_cases"]} == {"gt_002", "pred_002"}


def test_graph_topology_exposes_split_merge_overlap_duplicate_and_half_open_adjacency():
    gt = [r(0, 100), r(100, 200)]
    pred = [r(0, 40), r(40, 150), r(40, 150)]
    result, _ = supplement(gt, pred, 30, 200)
    topology = result["topology"]
    assert topology["possible_split_gt_ids"] == [1, 2]
    assert topology["possible_merge_prediction_ids"] == [2, 3]
    assert topology["exact_duplicate_predictions"] == [[2, 3]]
    assert topology["prediction_inventory"]["positive_overlap_row_pairs"] == [[2, 3]]
    assert topology["prediction_inventory"]["adjacent_row_pairs"] == [[1, 2], [1, 3]]
    assert topology["gt_inventory"]["positive_overlap_row_pairs"] == []


def test_large_boundary_error_and_weak_iou_are_cases_and_p95_is_computed_from_matched_rows():
    result, _ = supplement([r(0, 100), r(200, 300)], [r(40, 100), r(202, 298)], 30, 400)
    assert [item["case_id"] for item in result["failure_cases"]] == ["gt_001"]
    assert result["p95_absolute_error_frames"]["start"] == pytest.approx(38.1)
    assert result["duration_error_frames"]["signed_bias"] == -22
    assert result["error_categories"]["late_start_gt_ids"] == [1, 2]
    assert result["error_categories"]["premature_end_gt_ids"] == [2]


def test_empty_prediction_set_keeps_every_gt_and_no_artificial_errors():
    result, rows = supplement([r(0, 100)], [], 30, 100)
    assert result["distributions"]["matched_iou"]["count"] == 0
    assert result["p95_absolute_error_frames"]["start"] is None
    assert result["duration_error_frames"]["mae"] is None
    assert rows[0]["interval_iou"] is None


def test_macro_unweighted_and_micro_counts_do_not_average_counts():
    first, _ = supplement([r(0, 100)], [r(0, 100)], 30, 300)
    second, _ = supplement([r(0, 100), r(200, 300)], [r(0, 100)], 30, 300)
    combined = aggregate({"first": first, "second": second})
    assert combined["macro"]["recall"] == 0.75
    assert combined["micro_detection"]["recall"] == pytest.approx(2 / 3)
    assert combined["micro_detection"]["f1"] == 0.8


def test_pooled_rmse_and_boundary_tolerances_preserve_matched_and_all_gt_denominators():
    first, _ = supplement([r(0, 100)], [r(0, 100)], 30, 500)
    second, _ = supplement([r(200, 300), r(400, 500)], [r(210, 300)], 30, 500)
    combined = aggregate({"first": first, "second": second})
    assert combined["micro_matched_boundary_statistics"]["start_frame"]["rmse"] == pytest.approx(50**0.5)
    assert combined["macro_boundary_statistics"]["start_frame"]["rmse"] == 5
    tolerance5 = next(row for row in combined["boundary_tolerances"]["start"] if row["frames"] == 5)
    assert tolerance5["within_count"] == 1
    assert tolerance5["micro_matched_accuracy"] == 0.5
    assert tolerance5["micro_all_gt_accuracy"] == pytest.approx(1 / 3)


@pytest.mark.parametrize("mutation", ["frontier", "count", "status", "cached", "fps", "processed"])
def test_unfinished_or_incompatible_inference_is_rejected_before_label_read(mutation):
    info = {"status": "analysed", "frontier_frame": 99, "media": {"n_frames": 100, "fps_num": 30, "fps_den": 1}}
    invalid = copy.deepcopy(info)
    if mutation == "frontier":
        invalid["frontier_frame"] = 98
    elif mutation == "count":
        invalid["media"]["n_frames"] = 99
    elif mutation == "status":
        invalid["status"] = "running"
    elif mutation == "cached":
        invalid["cached_perception_used"] = True
    elif mutation == "fps":
        invalid["media"]["fps_num"] = 25
    else:
        invalid["frames_processed"] = 99
    verify_completion(info, 100, 30)
    with pytest.raises(ValueError):
        verify_completion(invalid, 100, 30)


def test_artifacts_cannot_overwrite_historical_output(tmp_path):
    result, rows = supplement([r(0, 100)], [r(0, 100)], 30, 100)
    output = tmp_path / "offline_report"
    write_artifacts(output, result, rows)
    with pytest.raises(FileExistsError):
        write_artifacts(output, result, rows)
    assert (output / "per_rally_comparison.csv").is_file()
