"""Publication/identity and complete-metric guards; no inference or live inputs."""
import copy
import importlib.util
from pathlib import Path

import pytest


SOURCE = Path(__file__).resolve().parents[2] / "orchestration/build_test02_consolidated_report.py"
SPEC = importlib.util.spec_from_file_location("test02_consolidated_builder", SOURCE)
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def finished():
    info = {"status": "completed", "cached_perception_used": False,
            "frames_processed": 29296, "frontier_frame": 29295,
            "source_sha256": builder.SOURCE_SHA, "proxy_sha256": "proxy",
            "perception_cache_catalog": {"sha256": "catalog", "file_count": 489}}
    executor = {"status": "completed", "worker_exit_code": 0,
                "frozen_source_inputs_unchanged": True, "output_proxy_sha256": "proxy",
                "perception_cache_catalog_verification": {
                    "status": "verified", "frames": 29296, "catalog_sha256": "catalog", "files": 489}}
    return info, executor


@pytest.mark.parametrize("location,key,value", [
    (0, "status", "running"), (0, "cached_perception_used", True),
    (0, "frames_processed", 29295), (0, "frontier_frame", 29294),
    (0, "source_sha256", "different-video"), (1, "status", "running"),
    (1, "worker_exit_code", 1), (1, "frozen_source_inputs_unchanged", False),
    (1, "output_proxy_sha256", "different-proxy"),
    (1, "perception_cache_catalog_verification", {"status": "running"}),
])
def test_incomplete_or_different_worker_cannot_publish(location, key, value):
    pair = finished()
    builder.require_finished_documents(*pair)
    pair[location][key] = value
    with pytest.raises(ValueError):
        builder.require_finished_documents(*pair)


def receipts():
    complete = {"status": "completed_fresh_Test2_improved_and_diagnostics", "frames": 29296,
                "fresh_neural_inference_performed": True, "annotations_unchanged": True,
                "baseline_unchanged": True, "models_unchanged": True, "profile_unchanged": True,
                "own_run_semantic_parity": True}
    diagnosis = {"status": "full_Test2_improved_component_metrics_and_source_diagnostics_complete",
                 "original_annotations_unchanged": True, "baseline_unchanged": True}
    verification = {"status": "completed", "baseline_unchanged": True, "original_annotations_unchanged": True}
    comparison = {"model_checkpoint_identity_equal": True, "profile_equal": True}
    return complete, diagnosis, verification, comparison


@pytest.mark.parametrize("location,key", [
    (0, "own_run_semantic_parity"), (0, "models_unchanged"),
    (0, "annotations_unchanged"), (0, "fresh_neural_inference_performed"),
    (1, "status"), (2, "status"), (2, "baseline_unchanged"),
    (3, "model_checkpoint_identity_equal"), (3, "profile_equal"),
])
def test_worker_completion_alone_is_insufficient(location, key):
    parts = receipts()
    builder.require_final_receipts(*parts)
    del parts[location][key]
    with pytest.raises(ValueError):
        builder.require_final_receipts(*parts)


def reference(predictions=(3, 2)):
    return {"raw_rows": [{"label": "A"}, {"label": "B"}], "comparison": [
        {"reference_data_row": k, "gt_rally": k, "gt_start_frame": 10*k,
         "gt_end_frame": 10*k+5, "matching_status": "matched", "pred_rally": pred}
        for k, pred in enumerate(predictions, 1)]}


def test_reference_rows_survive_prediction_ordinal_churn_and_reordering():
    old, new = reference(), reference((10, 9))
    new["comparison"].reverse()
    result = builder.paired_rows(old, new)
    assert [v["reference_data_row"] for v in result] == [1, 2]
    assert result[0]["baseline"]["pred_rally"] == 3
    assert result[0]["fresh_postfix"]["pred_rally"] == 10
    assert result[0]["source_annotation"] == {"label": "A"}


@pytest.mark.parametrize("damage", ["source", "interval", "missing", "duplicate_row", "duplicate_prediction", "out_of_bounds"])
def test_reference_corruption_rejected(damage):
    old, new = reference(), reference()
    if damage == "source":
        new["raw_rows"][0]["label"] = "changed"
    elif damage == "interval":
        new["comparison"][0]["gt_end_frame"] += 1
    elif damage == "missing":
        old["comparison"].pop()
        new["comparison"].pop()
    elif damage == "duplicate_row":
        new["comparison"][1]["reference_data_row"] = 1
    elif damage == "duplicate_prediction":
        new["comparison"][1]["pred_rally"] = 3
    elif damage == "out_of_bounds":
        new["comparison"][0]["reference_data_row"] = 0
    with pytest.raises(ValueError):
        builder.paired_rows(old, new)


def test_complete_tolerance_denominators_preserved_but_frame_samples_bounded():
    metrics = {"frames": 29296, "boundary_tolerances": {"start": [
        {"frames": 1, "seconds": 1/30, "within_count": 3, "matched_accuracy": .5, "all_gt_accuracy": .3},
        {"frames": 5, "seconds": 5/30, "within_count": 5, "matched_accuracy": 5/6, "all_gt_accuracy": .5}]},
        "raw_rows": [{"long": list(range(1000))}], "shuttle": {"frames": list(range(1000))}}
    flat = builder.flatten(metrics)
    assert flat["frames"] == 29296
    assert flat["boundary_tolerances.start[0].frames"] == 1
    assert flat["boundary_tolerances.start[1].all_gt_accuracy"] == .5
    assert flat["boundary_tolerances.start[1].within_count"] == 5
    assert flat["shuttle.frames.retained_entries"] == 1000
    assert len(flat) == 13
    changed = copy.deepcopy(metrics)
    changed["boundary_tolerances"]["start"][0]["within_count"] = 4
    rows = {r[0]: r[1:] for r in builder.comparisons(metrics, changed)}
    assert rows["boundary_tolerances.start[0].within_count"] == (3, 4, 1)


def test_unavailable_metric_not_zero_or_arithmetic_delta():
    assert builder.comparisons({"metric": None}, {"metric": None}) == [("metric", None, None, None)]
    assert builder.fmt(None) == "Unavailable"
    with pytest.raises(ValueError):
        builder.fmt(float("nan"))


def test_explicit_model_dimensions_and_provider_choices_are_preserved():
    flat = builder.flatten({"input_size": [512, 288], "providers": ["CUDAExecutionProvider", "CPUExecutionProvider"]})
    assert flat == {"input_size[0]": 512, "input_size[1]": 288,
                    "providers[0]": "CUDAExecutionProvider", "providers[1]": "CPUExecutionProvider"}


def test_embedded_links_keep_images_urls_and_anchors(tmp_path):
    source = tmp_path / "original/report.md"
    text = "# Diagnosis\n![frame](frames/a.png) [evidence](../case.json#detail) [web](https://example.org/a) [same](#case)"
    rendered = builder.absolute_markdown(text, source)
    assert rendered.startswith("## Diagnosis")
    assert f"![frame]({source.parent}/frames/a.png)" in rendered
    assert f"[evidence]({tmp_path}/case.json#detail)" in rendered
    assert "[web](https://example.org/a) [same](#case)" in rendered


def test_live_or_missing_run_creates_no_publication_paths(tmp_path):
    root = tmp_path / "artifacts"
    root.mkdir()
    output = tmp_path / "new-reports/consolidated.md"
    with pytest.raises(FileNotFoundError):
        builder.build(root, output)
    assert not output.parent.exists()


def test_existing_records_are_immutable(tmp_path):
    output = tmp_path / "report.md"
    output.write_text("historical report")
    with pytest.raises(ValueError):
        builder.build(tmp_path, output)
    assert output.read_text() == "historical report"


@pytest.mark.parametrize("arm", ["baseline_v1", "improved_v1", "test1_semantic_regression_v1"])
def test_new_reports_cannot_mutate_completed_artifact_catalogues(tmp_path, arm):
    output = tmp_path / arm / "extra/report.md"
    with pytest.raises(ValueError, match="immutable"):
        builder.build(tmp_path, output)
    assert not output.parent.exists()


@pytest.mark.parametrize("damage", ["none", "different_source", "cached", "incomplete", "unsupported_zero", "missing_links", "outer_claim"])
def test_independent_fresh_review_has_separate_source_and_completion_gate(damage):
    review = {"status": "completed_independent_fresh_component_review", "source_sha256": builder.SOURCE_SHA,
              "fresh_cached_perception_used": False, "inputs_unchanged": True}
    receipt = {"status": "completed_independent_fresh_component_review", "all_unsupported_values_null": True,
               "all_local_links_exist": True, "parent_outer_orchestration_completion_claimed": False}
    if damage == "different_source":
        review["source_sha256"] = "other"
    elif damage == "cached":
        review["fresh_cached_perception_used"] = True
    elif damage == "incomplete":
        receipt["status"] = "running"
    elif damage == "unsupported_zero":
        receipt["all_unsupported_values_null"] = False
    elif damage == "missing_links":
        receipt["all_local_links_exist"] = False
    elif damage == "outer_claim":
        receipt["parent_outer_orchestration_completion_claimed"] = True
    if damage == "none":
        builder.require_independent_review(review, receipt)
    else:
        with pytest.raises(ValueError, match="independent"):
            builder.require_independent_review(review, receipt)
