"""Manifest contracts without inference, foreign sources or fabricated labels."""

import copy
import importlib.util
import json
from pathlib import Path

import pytest

SOURCE = Path(__file__).resolve().parents[2] / "orchestration/evaluate_manifest_components.py"
SPEC = importlib.util.spec_from_file_location("manifest_component_evaluator", SOURCE)
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


def entry(name="arbitrary.csv", role="interval_reference"):
    columns = ["start_frame", "end_frame", "label"]
    return {
        "name": name,
        "sha256": "a" * 64,
        "role": role,
        "purpose": "Reviewed timing agreement",
        "ambiguity": "Generated reference, no physicalGT",
        "reference_role": "declared_generated_agreement",
        "partial_positive_only": False,
        "schema": {"format": "csv", "columns": columns, "interval_format": "frames"},
        "field_eligibility": {
            c: {
                "kind": "timing" if c != "label" else "stroke",
                "status": "diagnostic_only",
                "reason": "No adjudicated physical labels",
            }
            for c in columns
        },
    }


def manifest(tmp_path):
    return {
        "schema": "component-evaluation-manifest:v1",
        "source": {
            "sha256": "b" * 64,
            "media": {"width": 100, "height": 100, "fps_num": 30, "fps_den": 1, "n_frames": 3},
        },
        "time_basis": {
            "timeline": "canonical_cfr",
            "frame_origin": 0,
            "offset_seconds": 0,
            "interval_end": "exclusive",
        },
        "annotations": {"directory": str(tmp_path), "files": [entry()]},
    }


@pytest.mark.parametrize(
    "damage", ["source", "media", "time", "role", "eligibility", "duplicate", "unsafe_name", "partial", "schema"]
)
def test_manifest_rejects_undeclared_or_changed_contract(tmp_path, damage):
    value = manifest(tmp_path)
    if damage == "source":
        value["source"]["sha256"] = "wrong"
    if damage == "media":
        value["source"]["media"]["n_frames"] = True
    if damage == "time":
        value["time_basis"]["offset_seconds"] = 1
    if damage == "role":
        value["annotations"]["files"][0]["role"] = "filename_guess"
    if damage == "eligibility":
        del value["annotations"]["files"][0]["field_eligibility"]["label"]
    if damage == "duplicate":
        value["annotations"]["files"] *= 2
    if damage == "unsafe_name":
        value["annotations"]["files"][0]["name"] = "../labels.csv"
    if damage == "partial":
        del value["annotations"]["files"][0]["partial_positive_only"]
    if damage == "schema":
        value["annotations"]["files"][0]["schema"]["format"] = "auto"
    with pytest.raises(ValueError):
        m.validate_manifest(value)


def test_unknown_filename_does_not_define_role_or_partial_policy(tmp_path):
    value = manifest(tmp_path)
    m.validate_manifest(value)
    p = tmp_path / "arbitrary.csv"
    p.write_text("start_frame,end_frame,label\n0,2,smash\n")
    item = value["annotations"]["files"][0]
    result = m.compare_intervals(p, item, [], value["source"]["media"])
    assert result["role"] == "declared_generated_agreement"
    assert result["metrics"]["detection"]["false_negatives"] == 1


def test_partial_positive_policy_preserves_unscored_predictions_and_nulls(tmp_path):
    from scripts.benchmarking.evaluate_rallies import Rally

    value = manifest(tmp_path)
    item = value["annotations"]["files"][0]
    item["partial_positive_only"] = True
    p = tmp_path / "arbitrary.csv"
    p.write_text("start_frame,end_frame,label\n0,1,smash\n")
    result = m.compare_intervals(p, item, [Rally(1, 3, 1 / 30, 0.1)], value["source"]["media"])
    assert all(result["metrics"]["detection"][k] is None for k in ["precision", "f1", "false_positives"])
    assert result["metrics"]["unmatched_predictions"] == []
    assert len(result["unscored_current_predictions"]) == 1


@pytest.mark.parametrize("damage", ["hash", "extra", "missing"])
def test_every_original_file_is_hash_pinned(tmp_path, damage):
    p = tmp_path / "arbitrary.csv"
    p.write_text("start_frame,end_frame,label\n0,1,x\n")
    value = manifest(tmp_path)
    value["annotations"]["files"][0]["sha256"] = m.sha(p)
    if damage == "hash":
        p.write_text("changed")
    if damage == "extra":
        (tmp_path / "support.json").write_text("{}")
    if damage == "missing":
        p.unlink()
    with pytest.raises(ValueError):
        m.inventory(value, {})


@pytest.mark.parametrize("data", ["f,x,y,v\n1,2,3,1\n0,2,3,1\n2,2,3,1\n", "f,x,y,v\n0,2,3,1\n0,2,3,1\n2,2,3,1\n"])
def test_dense_frames_cannot_shift_reorder_or_duplicate(tmp_path, data):
    p = tmp_path / "points.csv"
    p.write_text(data)
    item = {
        "role": "dense_generated_shuttle",
        "schema": {"format": "csv", "columns": ["f", "x", "y", "v"], "frame_column": "f"},
    }
    with pytest.raises(ValueError, match="Dense timeline"):
        m.load_annotation(p, item, manifest(tmp_path)["source"]["media"])


def test_dense_time_alignment_is_explicit(tmp_path):
    p = tmp_path / "points.csv"
    p.write_text("f,t\n0,0\n1,1\n2,2\n")
    item = {
        "role": "dense_generated_players",
        "schema": {"format": "csv", "columns": ["f", "t"], "frame_column": "f", "timestamp_column": "t"},
    }
    with pytest.raises(ValueError, match="timestamps"):
        m.load_annotation(p, item, manifest(tmp_path)["source"]["media"])


def test_exact_schema_prevents_wrong_interval_time_branch(tmp_path):
    item = entry()
    item["schema"]["interval_format"] = "clock"
    p = tmp_path / "x.csv"
    p.write_text("start_frame,end_frame,label\n0,1,x\n")
    with pytest.raises(ValueError, match="convention"):
        m.compare_intervals(p, item, [], manifest(tmp_path)["source"]["media"])


def test_duplicate_generated_tables_are_once_with_explicit_alias():
    first = entry("one.csv", "dense_generated_shuttle")
    other = copy.deepcopy(first)
    other["name"] = "two.csv"
    seen = {}
    assert m.deduplicate(first, seen) is None
    assert m.deduplicate(other, seen) == "one.csv"
    other["schema"]["visibility"] = "other"
    with pytest.raises(ValueError, match="conflicting"):
        m.deduplicate(other, seen)


def test_out_of_image_generated_coordinates_retained_and_not_accuracy(tmp_path):
    item = {
        "role": "dense_generated_shuttle",
        "schema": {"x": "x", "y": "y", "visibility": "v", "visible_values": ["1"]},
    }
    media = manifest(tmp_path)["source"]["media"]
    frames = [{"f": 0, "s": [1.0, 2.0]}]
    rows = [{"x": "999", "y": "-2", "v": "1"}]
    unbound, raw = m.point_rows(item, rows, frames, media, False)
    assert unbound["distance_px"] is None and raw[0]["reference_xy"] == [999.0, -2.0]
    assert unbound["counts"]["out_of_image_reference_points"] == 1
    bound, _ = m.point_rows(item, rows, frames, media, True)
    assert bound["distance_px"]["count"] == 1 and "NOT physical accuracy" in bound["classification"]


def test_foreign_recorded_root_rejected_before_actual_guard(tmp_path, monkeypatch):
    run = tmp_path / "run"
    run.mkdir()
    plan = tmp_path / "plan.json"
    plan.write_text(json.dumps({"source_files_sha256": {"/foreign/sports/badminton/src/bai_badminton/engine.py": "x"}}))
    run.with_suffix(".executor.json").write_text(json.dumps({"command": ["worker", "--plan", str(plan)]}))
    monkeypatch.setattr(m.analysis, "load_analysis_input", lambda *_: pytest.fail("Foreign guard must never execute"))
    with pytest.raises(ValueError, match="Recorded source root"):
        m.native_completion(run)


def test_incomplete_guard_failure_occurs_before_annotation_reads(tmp_path, monkeypatch):
    run = tmp_path / "run"
    run.mkdir()
    path = tmp_path / "manifest.json"
    value = manifest(tmp_path / "originals")
    path.write_text(json.dumps(value))

    def reject(_):
        raise ValueError("incomplete original worker")

    monkeypatch.setattr(m, "native_completion", reject)
    monkeypatch.setattr(m, "inventory", lambda *_: pytest.fail("Labels must not be consumed"))
    with pytest.raises(ValueError, match="incomplete"):
        m.evaluate(run, path, tmp_path / "new")


@pytest.mark.parametrize("which", ["existing", "symlink", "run_overlap"])
def test_previous_outputs_and_original_inputs_are_immutable(tmp_path, which):
    run = tmp_path / "run"
    run.mkdir()
    output = tmp_path / "output"
    if which == "existing":
        output.mkdir()
    if which == "symlink":
        output.symlink_to(tmp_path / "missing")
    if which == "run_overlap":
        output = run / "report"
    with pytest.raises(ValueError):
        m.require_new_output(output, [run])


def test_coordinate_hash_and_semantics_must_match_exact_reference():
    item = {"role": "dense_generated_shuttle", "name": "explicit.csv", "sha256": "a" * 64, "schema": {}}
    contract = {
        "certificate": {"legacy_shuttle_point": "analysis_image_xy", "reference_sha256": {"explicit.csv": "b" * 64}}
    }
    with pytest.raises(ValueError, match="semantics/hash"):
        m.component_bound(item, contract)


@pytest.mark.parametrize("damage", ["none", "sha", "width", "height", "fps_num", "fps_den", "n_frames"])
def test_pairing_checks_all_canonical_fields_preserving_extra_media_metadata(tmp_path, damage):
    source = manifest(tmp_path)["source"]
    bound = {
        "source_sha256": source["sha256"],
        "media": {**source["media"], "codec": "h264", "duration_us": 100000, "has_audio": True},
    }
    if damage == "sha":
        bound["source_sha256"] = "changed"
    elif damage != "none":
        bound["media"][damage] += 1
    if damage == "none":
        m.require_pairing(bound, source)
    else:
        with pytest.raises(ValueError, match="pairing"):
            m.require_pairing(bound, source)


def test_nonfinite_dense_timestamp_never_passes_alignment(tmp_path):
    p = tmp_path / "points.csv"
    p.write_text("f,t\n0,0\n1,nan\n2,0.06666666666666667\n")
    item = {
        "role": "dense_generated_players",
        "schema": {
            "format": "csv",
            "columns": ["f", "t"],
            "frame_column": "f",
            "timestamp_column": "t",
            "timestamp_format": "seconds",
        },
    }
    with pytest.raises(ValueError, match="timestamps"):
        m.load_annotation(p, item, manifest(tmp_path)["source"]["media"])


def test_unknown_visibility_is_unavailable_not_negative(tmp_path):
    item = {
        "role": "dense_generated_shuttle",
        "schema": {"x": "x", "y": "y", "visibility": "v", "visible_values": ["1"], "invisible_values": ["0"]},
    }
    metrics, raw = m.point_rows(
        item,
        [{"x": "2", "y": "3", "v": "unknown"}],
        [{"f": 0, "s": [2.0, 3.0]}],
        manifest(tmp_path)["source"]["media"],
        True,
    )
    assert raw[0]["reference_visible"] is None
    assert metrics["counts"]["visibility_unknown"] == 1
    assert metrics["distance_px"]["count"] == 0


@pytest.mark.parametrize("damage", ["source", "fps", "reviewed", "evidence"])
def test_coordinate_certificate_requires_exact_source_timeline_and_evidence(tmp_path, damage):
    value = manifest(tmp_path)
    evidence = tmp_path / "panel.png"
    evidence.write_bytes(b"controlled-evidence")
    cert = {
        "status": "source_and_coordinate_semantics_verified",
        "source_sha256": value["source"]["sha256"],
        "frame_size": [100, 100],
        "fps_num": 30,
        "fps_den": 1,
        "reviewer_type": "controlled_diagnostic",
        "evidence": [{"path": str(evidence), "sha256": m.sha(evidence)}],
        "reviewed_frames": [0],
    }
    if damage == "source":
        cert["source_sha256"] = "changed"
    if damage == "fps":
        cert["fps_num"] = 25
    if damage == "reviewed":
        cert["reviewed_frames"] = [3]
    if damage == "evidence":
        cert["evidence"][0]["sha256"] = "changed"
    p = tmp_path / "binding.json"
    p.write_text(json.dumps(cert))
    with pytest.raises(ValueError):
        m.coordinate_contract(p, value, {})


@pytest.mark.parametrize("test", [1, 2])
def test_all_saved_test1_test2_interval_metrics_match_unchanged_original_comparator(test):
    run = m.ROOT.parent / f"ground-truth-validation-artifacts-20261110/test_{test:02d}/improved_v1"
    if not (run / "bound_reference_diagnostics/component_reference_metrics.json").exists():
        pytest.skip("Retained original dataset/run comparison fixtures unavailable")
    saved = m.read(run / "bound_reference_diagnostics/component_reference_metrics.json")
    predictions = m.read_csv(run / "run/predicted_rallies.csv", 30.0)
    folder = m.ROOT / f"Part2/dataset/Test{test}_Full"
    explicit = {
        f"Test{test}_Full.csv": ("clock", "coarse_legacy_label_agreement", False),
        f"Test{test}_Full_rally.csv": ("frames_seconds", "legacy_generated_reference_agreement", False),
        "win_predictions.csv": ("frames", "legacy_generated_reference_agreement", False),
    }
    if test == 1:
        explicit.update(
            {
                "Test1_Full2.csv": ("frames_seconds", "partial_mixed_label_candidate", True),
                "Test1_Full_rev_T.csv": ("frames_seconds", "legacy_generated_reference_agreement", False),
                "Test1_Full_rev_T4.csv": ("frames_seconds", "legacy_generated_reference_agreement", False),
            }
        )
    assert set(explicit) == set(saved["interval_reference_comparisons"])
    for name, (fmt, role, partial) in explicit.items():
        columns, _ = m.rows(folder / name)
        declared = {
            "reference_role": role,
            "partial_positive_only": partial,
            "schema": {"columns": columns, "interval_format": fmt},
        }
        result = m.compare_intervals(folder / name, declared, predictions, saved["media"])
        assert result["role"] == role
        assert result["metrics"] == saved["interval_reference_comparisons"][name]["metrics"]
        if partial:
            assert (
                result["unscored_current_predictions"]
                == saved["interval_reference_comparisons"][name]["unscored_current_predictions"]
            )


@pytest.mark.parametrize("convention", [None, "guess"])
def test_optional_timestamp_columns_require_declared_supported_convention(tmp_path, convention):
    p = tmp_path / "points.csv"
    p.write_text("f,t\n0,0\n1,0.03333333333333333\n2,0.06666666666666667\n")
    item = {
        "role": "dense_generated_players",
        "schema": {
            "format": "csv",
            "columns": ["f", "t"],
            "frame_column": "f",
            "timestamp_column": "t",
            "timestamp_format": convention,
        },
    }
    with pytest.raises(ValueError, match="convention"):
        m.load_annotation(p, item, manifest(tmp_path)["source"]["media"])


def test_full_scalar_markdown_from_completed_control_preserves_partial_and_runtime_scope():
    path = Path(__file__).parent / "test01_control_output_v3/component_reference_metrics.json"
    if not path.exists():
        pytest.skip("Completed native control fixture unavailable")
    value = m.read(path)
    rendered = m.render_report(value)
    assert "Unscored partial-reference proposal; not FP" in rendered
    assert "boundary tolerances" in rendered and "Median signed" in rendered
    assert "Actual runtime and resources" in rendered and "Verified actual model artifacts" in rendered
    assert "Recorded pipeline commit" in rendered and "Unavailable physical accuracy" in rendered
    assert "{'" not in rendered and "['" not in rendered
