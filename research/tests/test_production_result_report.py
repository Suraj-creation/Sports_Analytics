"""A newly matched easy row cannot conceal a worsened or lost previous match."""

import json

import pytest

from research.production_result_report import compare, fmt, interval_topology, read_run


def row(identity, error=None):
    return {
        "gt_rally": str(identity),
        "matching_status": "missed" if error is None else "matched",
        "start_frame_error": "" if error is None else str(error),
        "end_frame_error": "" if error is None else "0",
        "duration_error_sec": "" if error is None else str(-error / 30),
        "pred_start_frame": "" if error is None else str(100 + error),
        "pred_end_frame": "" if error is None else "300",
    }


def test_new_match_cannot_hide_shared_row_regression_or_lost_match():
    reference = {"rows": [row(1, 10), row(2, 100), row(3)]}
    candidate = {"rows": [row(1, 20), row(2), row(3, 0)], "metrics": {}}
    result = compare(reference, candidate)
    assert result["previously_matched_lost"] == [2]
    assert result["newly_matched"] == [3]
    assert result["shared_matched_count"] == 1
    assert result["paired_mae"]["start_frame_error"] == {"reference": 10.0, "candidate": 20.0}
    assert result["per_gt_changes"]["1"]["start"] == "worsened"


def test_no_matches_have_no_fabricated_zero_boundary_error():
    result = compare({"rows": [row(1, 5)]}, {"rows": [row(1)], "metrics": {}})
    assert result["paired_mae"]["start_frame_error"] == {"reference": None, "candidate": None}
    assert result["supplemental_absolute_quantiles"]["start_frame_error"]["p95"] is None
    assert fmt(None) == "unavailable"


def test_unfinished_inference_cannot_be_reported_as_a_fresh_result(tmp_path):
    for filename, value in (
        ("benchmark_metadata.json", {"status": "running"}),
        ("metrics.json", {}),
        ("inference.json", {"status": "analysing"}),
    ):
        (tmp_path / filename).write_text(json.dumps(value))
    (tmp_path / "rally_comparison.csv").write_text("gt_rally,matching_status\n")
    with pytest.raises(ValueError, match="unfinished"):
        read_run(tmp_path, fresh=True)


def test_topology_keeps_tiny_boundary_tails_and_half_open_adjacency():
    result = interval_topology([(1, 10, 30), (2, 40, 60)], [(1, 10, 41), (2, 41, 60), (3, 60, 80)])
    assert result["gt_overlapped_by_multiple_predictions"] == {"2": [1, 2]}
    assert result["predictions_overlapping_multiple_gt"] == {"1": [1, 2]}
    assert [e["overlap_frames"] for e in result["edges"]] == [20, 1, 19]
    assert all(e["prediction"] != 3 for e in result["edges"])


def test_topology_union_never_double_counts_overlapping_predictions():
    result = interval_topology([(1, 10, 30), (2, 50, 60)], [(1, 5, 22), (2, 18, 35)])
    assert result["gt_union_coverage"] == {
        "1": {"covered_frames": 20, "fraction": 1.0},
        "2": {"covered_frames": 0, "fraction": 0.0},
    }


def test_topology_rejects_invalid_intervals():
    with pytest.raises(ValueError, match="invalid predicted"):
        interval_topology([(1, 0, 2)], [(1, 1, 1)])
