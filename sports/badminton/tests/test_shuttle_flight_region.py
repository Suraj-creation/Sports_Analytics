"""Airborne image priors retain observed peaks without claiming 3D ownership."""

import json
from pathlib import Path

import numpy as np
import pytest

from bai_badminton.perception.isolation import flight_mask


def test_reviewed_pre_mask_model_peaks_explain_the_legacy_gate():
    fixture = json.loads((Path(__file__).parent / "fixtures/shuttle_mask_review.json").read_text())
    for row in fixture["records"]:
        polygon = np.asarray(row["polygon_proxy_px"])
        legacy = flight_mask(polygon, (1280, 720), (512, 288))
        explicit = flight_mask(polygon, (1280, 720), (512, 288), region="bounded_upward_sweep_v1")
        ceiling = flight_mask(polygon, (1280, 720), (512, 288), region="vertical_columns_to_image_top_v1")
        np.testing.assert_array_equal(legacy, explicit)
        x, y = (round(v / 2.5) for v in row["raw_model_peak_proxy_px"])
        assert not legacy[y, x] and ceiling[y, x]
        assert np.all(legacy <= ceiling)


def test_upper_flight_policy_preserves_horizontal_and_floor_isolation():
    polygon = np.array([[200, 300], [300, 300], [360, 600], [140, 600]], np.float32)
    ceiling = flight_mask(polygon, (800, 720), (800, 720), region="vertical_columns_to_image_top_v1")
    assert ceiling[5, 250]  # high image-space flight above the selected court
    assert not ceiling[5, 550]  # a separate neighboring court's columns
    assert not ceiling[500, 550]
    assert not ceiling[700, 250]  # no extra floor/runoff admission


@pytest.mark.parametrize(
    "polygon", [np.array([[0, 0], [1, 1]]), np.full((4, 2), np.nan), np.array([[900, 900], [950, 900], [950, 950]])]
)
def test_unknown_offscreen_or_invalid_court_never_becomes_full_frame(polygon):
    assert not flight_mask(polygon, (800, 720), (80, 72), region="vertical_columns_to_image_top_v1").any()


def test_offscreen_extrapolation_is_clipped_before_full_height_sweep():
    polygon = np.array([[-1000, 200], [200, 200], [200, 500], [-1000, 500]], np.float32)
    mask = flight_mask(polygon, (800, 720), (800, 720), region="vertical_columns_to_image_top_v1")
    assert mask[10, 100]
    assert not mask[10, 600]


def test_unregistered_flight_policy_is_rejected():
    with pytest.raises(ValueError):
        flight_mask(np.array([[0, 0], [10, 0], [10, 10]]), (100, 100), (50, 50), region="unknown")
