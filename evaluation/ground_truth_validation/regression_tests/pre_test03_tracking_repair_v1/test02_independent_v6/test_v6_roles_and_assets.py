"""Focused review gates; all fixtures are synthetic metadata, no run outputs."""

from copy import deepcopy

import pytest
from compare_shuttle_roles import role_observation
from native_completion_gate import frame_role_contract, model_asset_contract, protected_scope_counts


def frame():
    return {
        "s": [572.5, 437.5],
        "c": 0.66,
        "aq": None,
        "sa": {
            "schema": "badminton-shuttle-association:v3",
            "raw_xy": [572.5, 437.5],
            "raw_model_support": 0.66,
            "raw_masked_peak_xy": [572.5, 437.5],
            "selected_xy": [767.5, 90.0],
            "selected_model_support": 0.61,
            "status": "observed",
            "association_status": "tracked",
            "selection_coordinate_source": "current_candidate_peak",
            "selected_candidate_rank": 2,
            "selection_witness_frames": [1, 2, 3],
        },
    }


def config():
    return {
        "expected_association_schema": "badminton-shuttle-association:v3",
        "expected_motion_acquisition_version": "observed-motion-acquisition:v1",
    }


def test_raw_and_associated_coordinates_and_support_remain_separate():
    f = frame()
    frame_role_contract(f, config())
    row = role_observation(f)
    assert row["raw_nn"] == {"xy": [572.5, 437.5], "support": 0.66}
    assert row["associated_selected_nn"] == {"xy": [767.5, 90.0], "support": 0.61}


@pytest.mark.parametrize(
    "change",
    [
        "no_association",
        "old_schema",
        "drop_masked_target",
        "drop_selected_support",
        "raw_xy",
        "raw_support",
        "drop_AQ",
        "wrong_AQ",
    ],
)
def test_new_wire_family_or_provenance_cannot_be_silently_lost(change):
    f = frame()
    if change == "no_association":
        f["sa"] = None
    elif change == "old_schema":
        f["sa"]["schema"] = "badminton-shuttle-association:v2"
    elif change == "drop_masked_target":
        f["sa"].pop("raw_masked_peak_xy")
    elif change == "drop_selected_support":
        f["sa"].pop("selected_model_support")
    elif change == "raw_xy":
        f["sa"]["raw_xy"] = [1, 2]
    elif change == "raw_support":
        f["sa"]["raw_model_support"] = 0.9
    elif change == "drop_AQ":
        f.pop("aq")
    else:
        f["aq"] = {"version": "wrong"}
    with pytest.raises(ValueError):
        frame_role_contract(f, config())


def test_alternative_cannot_borrow_argmax_confidence_when_its_support_is_unknown():
    f = frame()
    f["sa"]["selected_model_support"] = None
    with pytest.raises(ValueError, match="borrow raw support"):
        role_observation(f)


def test_legacy_raw_only_role_keeps_original_support_and_cannot_select_another_point():
    f = frame()
    f["sa"]["schema"] = "badminton-shuttle-association:v2"
    f["sa"]["selected_xy"] = f["s"]
    assert role_observation(f)["associated_selected_nn"]["support"] == 0.66
    f["sa"]["selected_xy"] = [1, 2]
    with pytest.raises(ValueError, match="Legacy"):
        role_observation(f)


def test_unavailable_association_has_no_fake_zero_coordinate_or_model_confidence():
    f = frame()
    f["sa"].update(status="ambiguous", selected_xy=None, selected_model_support=None)
    assert role_observation(f)["associated_selected_nn"] == {"xy": None, "support": None}


def assets():
    return {
        "registry_artifacts": {k: {"sha256": "a" * 64} for k in ["rfdetr_small", "rtmpose_m_body7", "tracknetv3"]},
        "package_ocr_artifacts": {k: {"sha256": "b" * 64} for k in ["det", "cls", "rec"]},
    }


def test_all_six_real_declared_assets_include_package_ocr_and_no_unloaded_model_claim():
    d = assets()
    d["registry_artifacts"]["osnet_ain_x0_25"] = {"status": "unavailable_not_claimed_loaded"}
    assert len(model_asset_contract(d)) == 6


@pytest.mark.parametrize("change", ["missing_OCR", "extra_loaded_model", "invalid_digest"])
def test_partial_or_changed_model_asset_population_refuses_comparability(change):
    d = deepcopy(assets())
    if change == "missing_OCR":
        d["package_ocr_artifacts"].pop("rec")
    elif change == "extra_loaded_model":
        d["registry_artifacts"]["osnet_ain_x0_25"] = {"sha256": "c" * 64}
    else:
        d["package_ocr_artifacts"]["rec"]["sha256"] = "not-a-hash"
    with pytest.raises(ValueError, match="Six actual"):
        model_asset_contract(d)


def test_originals_candidate_copies_and_other_inputs_use_exact_separate_prefixes():
    paths = [
        "/main/Part2/test1.csv",
        "/main/Part2/test2.csv",
        "/candidate/Part2/test2.csv",
        "/main/reports/Part2/notes.json",
    ]
    assert protected_scope_counts(paths, {"main_root": "/main", "native_root": "/candidate"}) == {
        "primary_original_annotations": 2,
        "candidate_test2_annotation_references": 1,
        "other_protected_inputs": 1,
    }


def test_original_population_and_point_helpers_have_exact_unchanged_math_ast():
    import ast
    from pathlib import Path

    here = Path(__file__).resolve().parent
    original = here.parents[1] / "pre_test03_scene_origin_v1/test02_independent_v5"
    for filename, functions in [
        ("review_completed_run.py", {"dist", "iou"}),
        ("audit_acquisition_coverage.py", {"iou", "audit_camera_proofs"}),
    ]:

        def selected(folder, filename=filename, functions=functions):
            return {
                f.name: ast.dump(f, include_attributes=False)
                for f in ast.parse((folder / filename).read_text()).body
                if isinstance(f, ast.FunctionDef) and f.name in functions
            }

        assert selected(here) == selected(original)
