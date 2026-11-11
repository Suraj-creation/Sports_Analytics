"""Synthetic report fixtures exercise completion guards and scalar rendering."""

from __future__ import annotations

import json

import pytest

from evaluation.ground_truth_validation.orchestration import build_test02_matrix as builder
from scripts.benchmarking.evaluate_rallies import Rally, evaluate


def dump(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data))


def test_failed_receipt_never_reaches_source_loader(tmp_path, monkeypatch):
    dump(tmp_path / "baseline_completion.json", {"status": "failed", "frames": 29296})

    def refuse(*args):
        pytest.fail("Failed receipt must not reach completed-run loader")

    monkeypatch.setattr(builder, "load_analysis_input", refuse)
    with pytest.raises(ValueError, match="failed or is incomplete"):
        builder.require_completed(tmp_path)


def test_absent_completion_never_creates_report(tmp_path):
    out = tmp_path / "out"
    with pytest.raises(ValueError, match="explicit completed"):
        builder.build(tmp_path, out)
    assert not out.exists()


def test_raw_arrays_cannot_be_rendered_in_markdown():
    with pytest.raises(ValueError, match="Raw containers"):
        builder.cell([1, 2, 3])


@pytest.fixture
def synthetic_completed_artifacts(tmp_path, monkeypatch):
    root = tmp_path / "synthetic_baseline"
    run = root / "run"
    completion = root / "baseline_completion.json"
    bound = {"media": dict(zip(("width", "height", "fps_num", "fps_den", "n_frames"), builder.MEDIA, strict=True))}
    monkeypatch.setattr(builder, "require_completed", lambda path: (root, completion, bound))
    dump(completion, {"status": "synthetic proof bypass used only by unit test"})
    inference = {"frames_processed": 29296, "proxy_sha256": "proxy", "profile": {}, "execution_backends": {}}
    dump(run / "inference.json", inference)
    interval_metrics, comparison = evaluate([Rally(0, 30, 0, 1)], [Rally(0, 30, 0, 1)], 30)
    references = {
        name: {"role": "synthetic_reference", "metrics": interval_metrics, "invalid_rows": []}
        for name in builder.REFERENCES
    }
    components = {
        "status": "completed_readonly_component_reference_diagnostics",
        "test": 2,
        "source_sha256": builder.TEST2_SHA,
        "run": str(run),
        "all_annotation_files_accounted_for": True,
        "annotations_modified": False,
        "interval_reference_comparisons": references,
        "point_diagnostics": {"coordinate_binding": {"status": "unverified"}, "player_bottom_center_distance_px": None},
        "court_diagnostic": {"reference_frame": 300, "metric": None},
        "actual_cache_component_coverage": {"counts": {}, "categories": {}},
        "event_coverage": {"live_counts": {}},
        "outcome_and_stroke_coverage": {"known_winner_outputs": 0},
        "track_coverage": {},
        "ocr_coverage": {},
        "runtime_resources": {},
        "degraded_components": [],
        "annotation_applicability": [{"file": "synthetic.csv", "role": "test", "status": "synthetic"}],
        "unsupported_metrics": {"pose": {"status": "unavailable", "prerequisite": "reviewed joints"}},
    }
    cd = root / "all_reference_components"
    dump(cd / "component_reference_metrics.json", components)
    dump(cd / "reference_row_comparisons.json", {name: {"comparison": comparison} for name in builder.REFERENCES})
    dump(
        root / "analysis/technical_analysis.json",
        {"run": str(run), "source_sha256": builder.TEST2_SHA, "inputs_unchanged_after_analysis": True},
    )
    dump(root / "protocol/plan.json", {"code_commit": "synthetic-commit", "profile_source_sha256": "config"})
    dump(root / "environment.json", {})
    dump(
        root / "timestamps/timestamp_audit.json",
        {"source_sha256": builder.TEST2_SHA, "frames_decoded": 29296, "source_proxy_full_rational_pts_equal": True},
    )
    dump(
        root / "downstream_exports/export_receipt.json",
        {
            "status": "completed",
            "original_artifacts_unchanged": True,
            "source_completion_sha256": builder.sha(run / "inference.json"),
            "source_run": str(run),
        },
    )
    for name in (
        "analytics",
        "individual_analytics",
        "estimated_individual_analytics",
        "highlights",
        "rally_outcome_records",
        "scoring_outcome_evidence",
    ):
        dump(root / f"downstream_exports/{name}.json", {})
    dump(root / "visual_failure_package/failure_case_index.json", [])
    dump(root / "visual_failure_package/manifest.json", {})
    dump(root / "diagnostic_replay/parity_vs_fresh.json", {})
    return root, tmp_path / "matrix"


def test_complete_synthetic_matrix_preserves_unavailable_and_no_raw_arrays(synthetic_completed_artifacts):
    root, out = synthetic_completed_artifacts
    result = builder.build(root, out)
    markdown = (out / "matrix.md").read_text()
    assert result["status"] == "completed_evidence_matrix"
    assert result["point_diagnostics"]["player_bottom_center_distance_px"] is None
    assert "boundary_tolerances" in markdown
    assert "boundary_and_duration_errors" in markdown
    assert "unavailable" in markdown
    assert "| [] |" not in markdown
    assert "| {} |" not in markdown
    assert result["downstream"]["heatmap_export_available"] is False
    assert result["downstream"]["score_timeline_entries"] == 0
    assert result["inference_performed"] is False
    with pytest.raises(ValueError, match="immutable"):
        builder.build(root, out)


def test_stale_other_run_metrics_are_rejected(synthetic_completed_artifacts):
    root, out = synthetic_completed_artifacts
    path = root / "all_reference_components/component_reference_metrics.json"
    data = json.loads(path.read_text())
    data["run"] = str(root / "another-run")
    dump(path, data)
    with pytest.raises(ValueError, match="not completed Test2 evidence"):
        builder.build(root, out)
    assert not out.exists()


def test_heatmap_summary_does_not_embed_density_grid():
    summarized = builder.compact_heatmaps({"values": [[0, 1], [2, 3]], "total": 6, "player": "anonymous"})
    assert summarized == {"values_count": 2, "total": 6, "player": "anonymous"}
