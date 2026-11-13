"""Focused provenance and raw/associated distinction guards, without run data."""

import importlib.util
from pathlib import Path

import pytest

OUT = Path(__file__).resolve().parent


def module(name):
    spec = importlib.util.spec_from_file_location(name, OUT / (name + ".py"))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value


@pytest.mark.parametrize(
    "mutation",
    [
        {"new_neural_inference": False},
        {"own_run_semantic_parity": False},
        {"candidate_commit": "foreign"},
        {"frames": 9},
        {"artifact_sha256": {}},
    ],
)
def test_incomplete_or_foreign_completion_cannot_authorize_review(mutation):
    guard = module("native_completion_gate")
    cfg = {"expected_commit": "frozen", "source_sha256": "source", "frame_count": 10}
    row = {
        "status": guard.STATUS,
        "candidate_commit": "frozen",
        "source_sha256": "source",
        "frames": 10,
        "artifact_sha256": {"file": "hash"},
        **{
            key: True
            for key in [
                "new_neural_inference",
                "own_run_semantic_parity",
                "annotations_and_baselines_unchanged",
                "source_helpers_models_profile_frozen",
                "actual_model_identity_equal",
                "no_cleanup",
                "no_test3",
            ]
        },
    }
    row.update(mutation)
    with pytest.raises(ValueError):
        guard.completion_contract(row, cfg)


def test_legacy_selected_support_remains_actual_raw_support():
    audit = module("audit_raw_associated_acquisition")
    row = {
        "sa": {
            "schema": "badminton-shuttle-association:v2",
            "status": "observed",
            "association_status": "tracked",
            "selected_xy": [1, 2],
            "raw_model_support": 0.9,
        }
    }
    result = audit.selected_view(row)
    assert result["support"] == 0.9 and result["source"] == "legacy_raw_coordinate"


def test_current_alternative_support_does_not_become_raw_support():
    audit = module("audit_raw_associated_acquisition")
    row = {
        "s": [500, 400],
        "c": 0.9,
        "sa": {
            "schema": "badminton-shuttle-association:v3",
            "status": "observed",
            "association_status": "tracked",
            "selected_xy": [770, 157.5],
            "raw_model_support": 0.9,
            "selected_model_support": 0.619,
            "selection_coordinate_source": "current_candidate_peak",
        },
    }
    result = audit.selected_view(row)
    assert result["xy"] == [770, 157.5] and result["support"] == 0.619
    assert row["s"] == [500, 400] and row["c"] == 0.9


def test_ambiguous_observation_is_not_counted_as_selected():
    audit = module("audit_raw_associated_acquisition")
    row = {
        "sa": {
            "schema": "badminton-shuttle-association:v3",
            "status": "ambiguous",
            "association_status": "static_candidate",
            "selected_xy": None,
            "raw_model_support": 0.9,
            "selected_model_support": None,
            "selection_coordinate_source": "unavailable",
        }
    }
    result = audit.selected_view(row)
    assert result["xy"] is None and result["support"] is None
