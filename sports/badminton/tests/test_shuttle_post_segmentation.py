"""Shuttle post-processing must respect externally supplied temporal boundaries."""

import numpy as np
import pytest

from bai_badminton.perception.shuttle_post import Track, process


def _track(xs: list[float]) -> Track:
    x = np.asarray(xs, dtype=float)
    visible = np.isfinite(x)
    return Track.from_arrays(x, np.where(visible, 100.0, np.nan), visible, np.where(visible, 0.9, 0.0))


def test_gap_spanning_cut_is_not_interpolated() -> None:
    raw = _track([0, 10, 20, np.nan, np.nan, 50, 60, 70])
    boundary = np.zeros(len(raw), dtype=bool)
    boundary[4] = True

    # Without a boundary this is an ordinarily repairable bounded gap.
    baseline = process(raw)
    assert baseline.vis[3:5].all() and baseline.interp[3:5].all()

    result = process(raw, break_before=boundary)
    assert not result.vis[3:5].any()
    assert not result.interp[3:5].any()
    assert np.isnan(result.x[3:5]).all()
    assert (result.conf[3:5] == 0).all()
    np.testing.assert_allclose(result.x[[0, 1, 2, 5, 6, 7]], raw.x[[0, 1, 2, 5, 6, 7]])
    assert not raw.vis[3:5].any()  # post-processing never mutates its input


def test_first_observation_after_cut_is_not_rejected_using_previous_shot() -> None:
    raw = _track([0, 10, 20, 500, np.nan, np.nan])
    boundary = np.zeros(len(raw), dtype=bool)
    boundary[3] = True

    assert not process(raw).vis[3]
    result = process(raw, break_before=boundary)
    assert result.vis[3] and not result.interp[3]
    assert result.x[3] == 500 and result.conf[3] == 0.9
    assert raw.vis[3] and raw.x[3] == 500


def test_internal_gap_is_still_filled_and_marked_as_reconstructed() -> None:
    raw = _track([0, 10, 20, np.nan, 40, 50, 60, 70, 80, 90])
    boundary = np.zeros(len(raw), dtype=bool)
    boundary[7] = True

    result = process(raw, break_before=boundary)
    assert result.vis[3] and result.interp[3]
    assert result.conf[3] == 0.35
    assert result.x[3] == pytest.approx(30)
    assert not raw.vis[3] and not raw.interp[3]


def test_boundaries_preserve_observed_samples_in_replay_segment() -> None:
    raw = _track([0, 10, 20, 30, 40, 50, 60, 70])
    # Enter replay at 2 and leave it at 6. The samples inside are still observations.
    boundary = np.zeros(len(raw), dtype=bool)
    boundary[[2, 6]] = True

    result = process(raw, break_before=boundary)
    np.testing.assert_array_equal(result.vis, raw.vis)
    np.testing.assert_array_equal(result.interp, raw.interp)
    np.testing.assert_array_equal(result.x, raw.x)
    np.testing.assert_array_equal(result.conf, raw.conf)


@pytest.mark.parametrize("xs", [[], [12.0], [0.0, 10.0, np.nan, 30.0, 40.0]])
def test_no_boundaries_matches_default_for_empty_short_and_gap_tracks(xs: list[float]) -> None:
    raw = _track(xs)
    baseline = process(raw)
    mask = np.zeros(len(raw), dtype=bool)
    if len(mask):
        mask[0] = True  # first-frame boundary has no predecessor and is harmless
    result = process(raw, break_before=mask)
    np.testing.assert_allclose(result.x, baseline.x, equal_nan=True)
    np.testing.assert_allclose(result.y, baseline.y, equal_nan=True)
    np.testing.assert_array_equal(result.vis, baseline.vis)
    np.testing.assert_array_equal(result.interp, baseline.interp)
    np.testing.assert_array_equal(result.conf, baseline.conf)


def test_boundary_mask_must_match_track_length_and_have_boolean_dtype() -> None:
    raw = _track([1.0, 2.0, 3.0])
    for invalid in (np.zeros(2, bool), np.zeros((3, 1), bool), np.array([0, 0, 1])):
        with pytest.raises(ValueError, match="break_before"):
            process(raw, break_before=invalid)
