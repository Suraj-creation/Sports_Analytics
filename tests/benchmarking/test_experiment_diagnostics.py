import json
from pathlib import Path

import pytest

from research.compare_rally_experiments import compare_experiment, validate_disjoint
from scripts.benchmarking.evaluate_rallies import POLICY, Rally, read_csv, save_evaluation, write_predictions


def setup_run(path: Path, labels: Path, intervals):
    path.mkdir()
    write_predictions(path / "predicted_rallies.csv", intervals, 30)
    gt = read_csv(labels, 30)
    pred = read_csv(path / "predicted_rallies.csv", 30)
    save_evaluation(path, gt, pred, 30)


def test_fragmented_fn_and_no_overlap_fp_recovery(tmp_path):
    labels = tmp_path / "labels.csv"
    write_predictions(labels, [(0, 300), (600, 900)], 30)
    baseline, experiment = tmp_path / "baseline", tmp_path / "experiment"
    setup_run(baseline, labels, [(0, 120), (180, 300), (600, 900), (1000, 1100)])
    setup_run(experiment, labels, [(0, 300), (600, 900)])
    report = compare_experiment(experiment, baseline, labels=labels)
    assert report["baseline"]["metrics"]["detection"]["false_negatives"] == 1
    assert report["baseline"]["fragmentation"]["unmatched_gt_with_partial_coverage"] == [1]
    assert report["baseline"]["fragmentation"]["predictions_without_gt_overlap"] == [4]
    assert report["baseline"]["fragmentation"]["predicted_segments_per_gt"] == [2, 1]
    assert report["baseline"]["per_gt"][0]["gt_dependent_union_coverage_fraction"] == pytest.approx(0.8)
    assert report["baseline"]["boundary_arrays_all_gt"]["start_frame_error"] == [None, 0]
    assert report["changes"]["resolved_missed_gt_ids"] == [1]
    assert report["changes"]["interval_overlap_topology"]["merged_interval_count"] == 1
    assert report["changes"]["interval_overlap_topology"]["split_interval_count"] == 0
    assert report["matching_policy"] == POLICY
    assert report["experiment"]["metrics"]["detection"]["f1"] == 1
    assert (experiment / "comparison.json").is_file()
    assert (experiment / "comparison.md").is_file()
    assert not (baseline / "comparison.json").exists()


def test_split_and_new_miss_are_not_hidden_by_empty_error(tmp_path):
    labels = tmp_path / "labels.csv"
    write_predictions(labels, [(0, 300)], 30)
    baseline, experiment = tmp_path / "baseline", tmp_path / "experiment"
    setup_run(baseline, labels, [(0, 300)])
    setup_run(experiment, labels, [(0, 120), (180, 300)])
    report = compare_experiment(experiment, baseline, labels=labels)
    assert report["changes"]["new_missed_gt_ids"] == [1]
    assert report["changes"]["interval_overlap_topology"]["split_interval_count"] == 1
    assert report["experiment"]["distributions"]["matched_iou"]["values"] == []
    assert report["experiment"]["boundary_arrays_all_gt"]["end_frame_error"] == [None]


def test_identical_controls_and_explicit_unavailable_telemetry(tmp_path):
    labels = tmp_path / "labels.csv"
    write_predictions(labels, [(30, 300)], 30)
    baseline, experiment = tmp_path / "baseline", tmp_path / "experiment"
    setup_run(baseline, labels, [(30, 300), (400, 500)])
    setup_run(experiment, labels, [(30, 300), (400, 500)])
    (experiment / "telemetry.json").write_text(json.dumps({"elapsed_seconds": 2.5, "gpu_memory_total": 11264}))
    report = compare_experiment(experiment, baseline, labels=labels)
    assert report["changes"]["resolved_missed_gt_ids"] == []
    assert report["changes"]["false_positive_identity_changes"]["resolved_or_changed_baseline_fp_ids"] == []
    assert len(report["changes"]["false_positive_identity_changes"]["unchanged_fp_intervals"]) == 1
    assert report["experiment"]["telemetry"]["inference_seconds"]["value"] == 2.5
    assert report["experiment"]["telemetry"]["gpu_peak_memory_bytes"] is None
    assert report["experiment"]["telemetry"]["dropped_frames"] is None
    with pytest.raises(FileExistsError):
        compare_experiment(experiment, baseline, labels=labels)


@pytest.mark.parametrize(
    "values",
    [
        [(0, 10), (0, 10)],
        [(0, 20), (10, 30)],
        [(30, 50), (0, 20)],
    ],
)
def test_interval_validation_rejects_invalid_topology(values):
    with pytest.raises(ValueError):
        validate_disjoint([Rally(a, b, a / 30, b / 30) for a, b in values], name="synthetic")


def test_adjacent_half_open_intervals_are_disjoint():
    validate_disjoint([Rally(0, 30, 0, 1), Rally(30, 60, 1, 2)], name="synthetic")


def test_refuse_frozen_baseline_write_and_tampered_protocol(tmp_path):
    labels = tmp_path / "labels.csv"
    write_predictions(labels, [(0, 300)], 30)
    baseline, experiment = tmp_path / "baseline", tmp_path / "experiment"
    setup_run(baseline, labels, [(0, 300)])
    setup_run(experiment, labels, [(0, 300)])
    with pytest.raises(ValueError, match="immutable"):
        compare_experiment(baseline, baseline, labels=labels)
    metrics_file = experiment / "metrics.json"
    metrics = json.loads(metrics_file.read_text())
    metrics["matching_policy"]["minimum_iou"] = 0.4
    metrics_file.write_text(json.dumps(metrics))
    with pytest.raises(ValueError, match="matching_policy"):
        compare_experiment(experiment, baseline, labels=labels)
    assert not (experiment / "comparison.json").exists()


def test_severe_boundary_outliers_and_all_gt_statuses(tmp_path):
    labels = tmp_path / "labels.csv"
    write_predictions(labels, [(0, 300), (600, 900)], 30)
    baseline, experiment = tmp_path / "baseline", tmp_path / "experiment"
    setup_run(baseline, labels, [(60, 300), (600, 840)])
    setup_run(experiment, labels, [(0, 300)])
    report = compare_experiment(experiment, baseline, labels=labels)
    assert report["baseline"]["severe_boundary_gt_ids"] == [1, 2]
    assert report["experiment"]["severe_boundary_gt_ids"] == []
    assert report["changes"]["new_missed_gt_ids"] == [2]
    assert report["changes"]["severe_boundary_gt_resolved"] == [1]
    assert report["changes"]["severe_boundary_gt_newly_unmatched"] == [2]
    assert len(report["experiment"]["per_gt"]) == 2
