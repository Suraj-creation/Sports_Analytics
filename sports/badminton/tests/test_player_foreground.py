"""Scene-only court-origin image context must never renew player authority."""

import numpy as np
import pytest

from bai_badminton.perception.players import CourtROI, PlayerPerception


def perception(count=2, *, stride=1, roi=True):
    state = {"bottom": 95.0, "left": 0.0, "count": count}

    def detector(_image):
        return np.array(
            [
                [10.0 + i * 40 + state["left"], 10.0, 30.0 + i * 40 + state["left"], state["bottom"]]
                for i in range(state["count"])
            ],
            float,
        ).reshape(-1, 4), np.full(state["count"], 0.95)

    p = PlayerPerception(detector, None, 30, det_stride=stride, pose_stride=0, max_players=count)
    if roi:
        p.set_roi(CourtROI(np.array([[0, 0], [450, 0], [450, 100], [0, 100]], np.float32), pad_px=0))
    return p, state, np.zeros((150, 460, 3), np.uint8)


def regions(p, frame):
    port = getattr(p, "foreground_regions", None)
    assert callable(port), "Tracking needs optional detached visual context independent of participant admission"
    return port(frame)


@pytest.mark.parametrize("count", [2, 4])
def test_observed_offcourt_visual_context_survives_but_authority_expires(count):
    p, state, image = perception(count)
    assert len(p.process(0, image)) == count
    initial = regions(p, 0)
    assert len(initial) == count
    state["bottom"] = 103.0
    for frame in range(1, 32):
        people = p.process(frame, image)
    assert people == [] and p._court_tracks == {}
    visual = regions(p, 31)
    assert len(visual) == count
    assert {r.key for r in visual} == {r.key for r in initial}
    assert all(r.frame == 31 and r.detector_matched and r.detector_observed for r in visual)
    assert p._last == []


def test_outside_person_without_observed_court_origin_cannot_seed_visual_context():
    p, state, image = perception()
    state["bottom"] = 103.0
    for frame in range(35):
        assert p.process(frame, image) == []
        assert regions(p, frame) == ()


def test_no_calibration_cannot_create_court_origin_visual_context():
    p, _, image = perception(roi=False)
    assert len(p.process(0, image)) == 2
    assert regions(p, 0) == ()


def test_cut_clears_visual_context_without_outside_rebirth():
    p, state, image = perception()
    p.process(0, image)
    assert len(regions(p, 0)) == 2
    state["bottom"] = 103.0
    p.on_cut()
    assert regions(p, 0) == ()
    assert p.process(1, image) == []
    assert regions(p, 1) == ()


def test_empty_fresh_output_is_bounded_unobserved_context_not_freshness_renewal():
    p, state, image = perception()
    p.process(0, image)
    assert len(regions(p, 0)) == 2
    state["count"] = 0
    for frame in range(1, 31):
        p.process(frame, image)
        context = regions(p, frame)
        assert len(context) == 2
        assert all(r.detector_observed and not r.detector_matched for r in context)
    p.process(31, image)
    assert regions(p, 31) == ()


def test_query_does_not_relabel_stale_frame_as_current():
    p, _, image = perception()
    p.process(0, image)
    assert len(regions(p, 0)) == 2
    assert regions(p, 1) == ()


def test_visual_carries_are_typed_unobserved_and_do_not_create_detection():
    p, state, image = perception()
    p.process(0, image)
    state["bottom"] = 103.0
    p.process(1, image)
    previous = regions(p, 1)
    p.process(2, image, (6, 0))
    current = regions(p, 2)
    assert {r.key for r in previous} == {r.key for r in current}
    assert all(r.frame == 2 and not r.detector_matched and not r.detector_observed for r in current)
    assert not p.last_detector_observed


def test_single_current_box_cannot_refresh_two_visual_episodes():
    p, state, image = perception()
    p.process(0, image)
    assert len(regions(p, 0)) == 2
    # Both prior boxes overlap this wide current proposal at the existing .3 gate.
    p.detector = lambda _image: (np.array([[10.0, 10.0, 70.0, 95.0]]), np.array([0.95]))
    p.process(1, image)
    keys = [r.key for r in regions(p, 1)]
    assert len(keys) == len(set(keys))
    assert len(keys) <= 1


def test_visual_context_cannot_revive_after_unscheduled_gap():
    p, _, image = perception()
    p.process(0, image)
    assert len(regions(p, 0)) == 2
    p.process(7, image, (6, 0))
    assert regions(p, 7) == ()


def test_overflow_withholds_visual_context_until_explicit_reset():
    p, state, image = perception()
    p.process(0, image)
    assert len(regions(p, 0)) == 2
    state["count"] = 9
    p.process(1, image)
    assert regions(p, 1) == ()
    state["count"] = 2
    p.process(2, image)
    assert regions(p, 2) == ()
    p.on_cut()
    p.process(3, image)
    assert len(regions(p, 3)) == 2


def test_foreground_snapshot_is_detached_from_later_updates():
    p, state, image = perception()
    p.process(0, image)
    saved = regions(p, 0)
    boxes = [r.bbox for r in saved]
    state["bottom"] = 103.0
    p.process(1, image)
    assert [r.bbox for r in saved] == boxes
    assert all(r.frame == 0 for r in saved)


def test_visual_memory_carry_cannot_rewind_and_revive_expired_context():
    from bai_badminton.perception.foreground import CourtForegroundMemory

    memory = CourtForegroundMemory(30)
    memory.update(0, np.array([[10.0, 10.0, 30.0, 95.0]]), np.array([True]))
    memory.carry(31)
    assert memory.at(31) == ()
    with pytest.raises(ValueError, match="increasing"):
        memory.carry(1)
