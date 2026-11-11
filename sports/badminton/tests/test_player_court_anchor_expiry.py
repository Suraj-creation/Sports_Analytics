"""Continuity can borrow an observed court anchor, never renew its own lease."""

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
def test_outside_observation_cannot_renew_court_anchor_forever(count):
    perception, state, image = setup(count)
    assert len(perception.process(0, image)) == count
    state["bottom"] = 103.0
    for frame in range(1, 31):
        assert len(perception.process(frame, image)) == count
    assert perception.process(31, image) == []
    assert perception._court_tracks == {}


@pytest.mark.parametrize("count", [2, 4])
def test_inside_reentry_refreshes_lease_and_short_jump_is_preserved(count):
    perception, state, image = setup(count)
    assert len(perception.process(0, image)) == count
    state["bottom"] = 103.0
    for frame in range(1, 20):
        assert len(perception.process(frame, image)) == count
    state["bottom"] = 95.0
    assert len(perception.process(20, image)) == count
    assert all(last == 20 for last, _ in perception._court_tracks.values())
    state["bottom"] = 103.0
    for frame in range(21, 51):
        assert len(perception.process(frame, image)) == count
    assert perception.process(51, image) == []


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
    assert all(last == 0 for last, _ in perception._court_tracks.values())
    perception.on_cut()
    assert perception._court_tracks == {}
    assert perception.process(3, image) == []


@pytest.mark.parametrize("count", [2, 4])
def test_moving_outside_continuity_keeps_latest_box_but_original_anchor_time(count):
    perception, state, image = setup(count)
    assert len(perception.process(0, image)) == count
    state["bottom"] = 103.0
    for frame in range(1, 31):
        state["left"] = 3.0 * frame
        assert len(perception.process(frame, image)) == count
        assert all(anchor == 0 for anchor, _ in perception._court_tracks.values())
    # By now no current box overlaps its original court observation. The
    # preserved latest box allowed motion without renewing court authority.
    assert all(box[0] >= 100 for _, box in perception._court_tracks.values())
    state["left"] = 93.0
    assert perception.process(31, image) == []


def test_scheduled_carry_cannot_outlive_court_anchor_until_next_detector_tick():
    perception, state, image = setup()
    assert len(perception.process(0, image)) == 2
    state["bottom"] = 103.0
    assert len(perception.process(1, image)) == 2
    assert len(perception.process(30, image)) == 2
    assert perception.process(31, image, (6, 0)) == []
    assert perception._court_tracks == {}
