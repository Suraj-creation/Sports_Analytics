"""A cropped baseline must not amplify visible line jitter into a court loss."""
from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.perception import court_lines as court

# Cropped CCTV geometry: the near baseline projects outside the 762x720 image.
LOCKED = np.array([
    [94.1819299646, 3.3033956113, 349.8646279075],
    [14.1980296351, -8.9211936212, 325.0400302578],
    [0.02707171196, 0.08626828036, 1.0],
])
SIZE = (762, 720)


def measured_fit(matrix):
    return court.CourtFit(matrix, 0.8, 4.2, (4, 4), 1.0, None, method='seed', area=0.5)


def test_locked_tracker_accepts_visible_jitter_without_replacing_selected_court(monkeypatch):
    candidate = LOCKED.copy()
    candidate[2, 1] += 0.001
    assert not court._close(candidate, LOCKED, SIZE, tol=15.24)
    monkeypatch.setattr(court, 'refine_court', lambda *args: measured_fit(candidate))
    tracker = court.CourtTracker()
    tracker.lock(LOCKED)
    fit = tracker.track([np.zeros((720, 762, 3), np.uint8)], [False], 0)[0]
    assert fit is not None
    np.testing.assert_array_equal(fit.H, LOCKED)


@pytest.mark.parametrize('shift', [30.0, 1000.0])
def test_locked_tracker_rejects_visible_camera_shift_even_when_candidate_leaves_image(monkeypatch, shift):
    candidate = np.array([[1., 0., shift], [0., 1., 0.], [0., 0., 1.]]) @ LOCKED
    monkeypatch.setattr(court, 'refine_court', lambda *args: measured_fit(candidate))
    tracker = court.CourtTracker()
    tracker.lock(LOCKED)
    assert tracker.track([np.zeros((720, 762, 3), np.uint8)], [False], 0) == [None]


def test_locked_tracker_still_requires_measured_line_support(monkeypatch):
    weak = replace(measured_fit(LOCKED), precision=0.4)
    monkeypatch.setattr(court, 'refine_court', lambda *args: weak)
    tracker = court.CourtTracker()
    tracker.lock(LOCKED)
    assert tracker.track([np.zeros((720, 762, 3), np.uint8)], [False], 0) == [None]


def test_visible_comparison_is_invariant_to_homogeneous_scale():
    assert court._close_in_view(LOCKED * -1e-6, LOCKED * 1e6, SIZE, tol=15.24)


@pytest.mark.parametrize('matrix', [np.zeros((3, 3)), np.full((3, 3), np.nan)])
def test_visible_comparison_rejects_degenerate_or_nonfinite_geometry(matrix):
    assert not court._close_in_view(matrix, LOCKED, SIZE, tol=15.24)


def test_visible_comparison_rejects_horizon_crossing_even_with_finite_corners():
    candidate = np.array([[1., 0., 1.], [0., 1., 1.], [1., 0., 0.1234567]])
    assert not court._close_in_view(candidate, LOCKED, SIZE, tol=1e9)


@pytest.mark.parametrize('shift,want', [(9.0, True), (10.0, False), (11.0, False)])
def test_visible_comparison_preserves_strict_pixel_tolerance(shift, want):
    reference = np.array([[50., 0., 400.], [0., 40., 360.], [0., 0., 1.]])
    moved = np.array([[1., 0., shift], [0., 1., 0.], [0., 0., 1.]]) @ reference
    assert court._close_in_view(moved, reference, (800, 720), tol=10.0) is want


def test_visible_comparison_rejects_zoom_and_neighbour_substitution():
    zoomed = np.diag([1.1, 1.1, 1.]) @ LOCKED
    neighbour = LOCKED @ np.array([[1., 0., 8.], [0., 1., 0.], [0., 0., 1.]])
    assert not court._close_in_view(zoomed, LOCKED, SIZE, tol=15.24)
    assert not court._close_in_view(neighbour, LOCKED, SIZE, tol=15.24)


def test_locked_jitter_does_not_accumulate_across_cuts_and_chunks(monkeypatch):
    candidate = LOCKED.copy()
    candidate[2, 1] += 0.001
    monkeypatch.setattr(court, 'refine_court', lambda *args: measured_fit(candidate))
    tracker = court.CourtTracker(verify_every=0)
    tracker.lock(LOCKED)
    frame = np.zeros((720, 762, 3), np.uint8)
    fits = tracker.track([frame] * 4, [False] * 4, 0)
    fits += tracker.track([frame] * 4, [True, False, False, False], 4)
    assert all(fit is not None for fit in fits)
    for fit in fits:
        np.testing.assert_array_equal(fit.H, LOCKED)
    assert tracker.stats.searches == 0


def test_identical_visible_geometry_is_not_rejected_by_sampled_hull_undercoverage():
    reference = np.array([[50., 0., -108.5], [0., 40., 360.], [0., 0., 1.]])
    assert court.visible_area(reference, (800, 720)) >= court.MIN_AREA
    assert court._close_in_view(reference, reference, (800, 720), tol=16.)
