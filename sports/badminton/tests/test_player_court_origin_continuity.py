"""Fresh court-origin image continuity and actual court anchors stay distinct.

The rejected strict one-second court-anchor policy lost visible athletes on
real source frames. Its original tests remain in frozen commit c585e35. A
missing-observation lease is different from a visible athlete's runoff.
"""

import numpy as np
import pytest

from bai_badminton.perception.players import CourtROI, PlayerPerception


def setup(count=2, roi=True):
    state = {"bottom": 95.0, "left": 0.0}

    def detector(_):
        return np.array(
            [
                [10.0 + 40 * i + state["left"], 10.0, 30.0 + 40 * i + state["left"], state["bottom"]]
                for i in range(count)
            ]
        ), np.full(count, 0.95)

    perception = PlayerPerception(detector, None, 30, det_stride=1, pose_stride=0, max_players=count)
    if roi:
        perception.set_roi(CourtROI(np.array([[0, 0], [250, 0], [250, 100], [0, 100]], np.float32), pad_px=0))
    return perception, state, np.zeros((150, 260, 3), np.uint8)


@pytest.mark.parametrize("count", [2, 4])
def test_fresh_outside_observations_preserve_athletes_but_not_court_anchor(count):
    perception, state, image = setup(count)
    assert len(perception.process(0, image)) == count
    state["bottom"] = 103.0
    for frame in range(1, 91):
        assert len(perception.process(frame, image)) == count
    assert all(last == 90 for last, _ in perception._court_tracks.values())
    assert set(perception._court_anchor_frames.values()) == {0}


@pytest.mark.parametrize("count", [2, 4])
def test_inside_reentry_refreshes_actual_anchor_and_short_jump_is_preserved(count):
    perception, state, image = setup(count)
    assert len(perception.process(0, image)) == count
    state["bottom"] = 103.0
    for frame in range(1, 20):
        assert len(perception.process(frame, image)) == count
    state["bottom"] = 95.0
    assert len(perception.process(20, image)) == count
    assert all(last == 20 for last, _ in perception._court_tracks.values())
    assert set(perception._court_anchor_frames.values()) == {20}
    state["bottom"] = 103.0
    for frame in range(21, 51):
        assert len(perception.process(frame, image)) == count
    assert len(perception.process(51, image)) == count
    assert set(perception._court_anchor_frames.values()) == {20}


def test_missing_roi_cannot_create_court_membership_anchor():
    perception, _, image = setup(roi=False)
    assert len(perception.process(0, image)) == 2
    assert perception._court_tracks == {}


def test_never_inside_outside_person_cannot_bootstrap_continuity():
    perception, state, image = setup()
    state["bottom"] = 103.0
    for frame in range(35):
        assert perception.process(frame, image) == []
    assert perception._court_tracks == {}


def test_unobserved_carries_do_not_refresh_anchor_and_cut_clears_it():
    perception, state, image = setup()
    assert len(perception.process(0, image)) == 2
    state["bottom"] = 103.0
    assert len(perception.process(1, image)) == 2
    assert len(perception.process(2, image, (6, 0))) == 2
    assert all(last == 1 for last, _ in perception._court_tracks.values())
    assert set(perception._court_anchor_frames.values()) == {0}
    perception.on_cut()
    assert perception._court_tracks == {}
    assert perception._court_anchor_frames == {}
    assert perception.process(3, image) == []


@pytest.mark.parametrize("count", [2, 4])
def test_moving_outside_continuity_keeps_latest_box_and_separate_actual_anchor(count):
    perception, state, image = setup(count)
    assert len(perception.process(0, image)) == count
    state["bottom"] = 103.0
    for frame in range(1, 31):
        state["left"] = 3.0 * frame
        assert len(perception.process(frame, image)) == count
        assert all(last == frame for last, _ in perception._court_tracks.values())
        assert set(perception._court_anchor_frames.values()) == {0}
    # By now no current box overlaps its original court observation. The
    # preserved latest box allowed motion without renewing court authority.
    assert all(box[0] >= 100 for _, box in perception._court_tracks.values())
    state["left"] = 93.0
    assert len(perception.process(31, image)) == count


def test_scheduled_carry_cannot_extend_missing_fresh_observation_lease():
    perception, state, image = setup()
    assert len(perception.process(0, image)) == 2
    state["bottom"] = 103.0
    assert len(perception.process(1, image)) == 2
    # A long synthetic cadence may carry the last observation, but never renew
    # its timestamp. Production cadence separately rejects stale carried rows.
    assert len(perception.process(30, image, (60, 0))) == 2
    assert len(perception.process(31, image, (60, 0))) == 2
    assert perception.process(32, image, (60, 0)) == []
    assert perception._court_tracks == {}
