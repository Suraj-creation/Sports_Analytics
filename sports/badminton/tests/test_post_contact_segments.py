"""Post-contact motion and event context require one contiguous temporal segment."""

import numpy as np
import pytest

from bai_badminton.events.stroke import post_contact_motion
from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track


def _window(boundaries=None, replay=None):
    n = 10
    return WindowObs(
        frame0=100,
        fps=30.0,
        shuttle=Track.from_arrays(np.arange(n, dtype=float) * 10, np.arange(n, dtype=float), np.ones(n, bool)),
        players={},
        break_before=boundaries,
        replay=np.zeros(n, bool) if replay is None else replay,
    )


def _motion(*, contact=0, visible=None, boundaries=None, next_contact=None):
    n = 10
    return post_contact_motion(
        np.arange(n, dtype=float) * 10,
        np.arange(n, dtype=float),
        np.ones(n, bool) if visible is None else visible,
        np.zeros(n, bool),
        contact,
        30.0,
        720.0,
        next_contact_idx=next_contact,
        break_before=boundaries,
    )


@pytest.mark.parametrize(
    "index,expected", [(0, (0, 3)), (2, (0, 3)), (3, (3, 6)), (5, (3, 6)), (6, (6, 10)), (9, (6, 10))]
)
def test_window_exposes_contiguous_half_open_segment(index, expected):
    boundaries = np.zeros(10, bool)
    boundaries[[3, 6]] = True
    assert _window(boundaries).segment_bounds(index) == expected


def test_no_boundary_preserves_whole_window_context():
    window = _window()
    assert window.segment_bounds(0) == (0, 10)
    assert window.segment_bounds(9) == (0, 10)


def test_segment_accessor_respects_replay_entry_and_exit():
    replay = np.zeros(10, bool)
    replay[3:6] = True
    window = _window(replay=replay)
    assert window.segment_bounds(2) == (0, 3)
    assert window.segment_bounds(4) == (3, 6)
    assert window.segment_bounds(6) == (6, 10)


@pytest.mark.parametrize("index", [-1, 10])
def test_segment_accessor_rejects_index_outside_its_window(index):
    with pytest.raises(IndexError, match="index"):
        _window().segment_bounds(index)


def test_post_contact_motion_cannot_use_consistent_points_after_a_cut():
    boundaries = np.zeros(10, bool)
    boundaries[3] = True
    visible = np.ones(10, bool)
    visible[1:3] = False
    # The three apparent flight samples are all from another scene. Their
    # consistency cannot turn them into evidence for the original contact.
    assert _motion(visible=visible, boundaries=boundaries) == (None, None)


def test_post_contact_motion_withholds_when_cut_leaves_too_few_observations():
    boundaries = np.zeros(10, bool)
    boundaries[3] = True
    assert _motion(boundaries=boundaries) == (None, None)


def test_valid_motion_before_later_cut_remains_available():
    boundaries = np.zeros(10, bool)
    boundaries[5] = True
    speed, vertical = _motion(boundaries=boundaries)
    assert speed == pytest.approx(np.hypot(300.0, 30.0))
    assert vertical == pytest.approx(30.0)


def test_contact_after_boundary_uses_its_new_segment():
    boundaries = np.zeros(10, bool)
    boundaries[3] = True
    speed, vertical = _motion(contact=3, boundaries=boundaries)
    assert speed == pytest.approx(np.hypot(300.0, 30.0))
    assert vertical == pytest.approx(30.0)


def test_no_boundary_and_next_contact_preserve_existing_motion_result():
    x, y = np.arange(10, dtype=float) * 10, np.arange(10, dtype=float)
    visible, inferred = np.ones(10, bool), np.zeros(10, bool)
    expected = post_contact_motion(x, y, visible, inferred, 0, 30.0, 720.0, next_contact_idx=5)
    assert _motion(boundaries=np.zeros(10, bool), next_contact=5) == expected


@pytest.mark.parametrize("invalid", [np.zeros(9, bool), np.zeros((10, 1), bool), np.zeros(10, int)])
def test_post_contact_motion_rejects_misaligned_or_nonboolean_boundaries(invalid):
    with pytest.raises(ValueError, match="break_before"):
        _motion(boundaries=invalid)
