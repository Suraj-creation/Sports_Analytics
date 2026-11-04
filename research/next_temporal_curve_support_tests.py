"""Prespecified synthetic controls; these are not reviewed sporting labels."""

from dataclasses import replace

import numpy as np

from bai_badminton.observations import WindowObs
from bai_badminton.perception.shuttle_post import Track
from research.next_temporal_curve_support import curve_exit_return_support


def flight(apex=-100.0):
    frames = np.arange(45)
    x = 500 + frames.astype(float)
    y = (frames - 20.0) ** 2 + apex
    visible = (frames < 5) | ((frames >= 35) & (frames < 40))
    return WindowObs(0, 30, Track.from_arrays(x, y, visible), {})


def support(window, index=10):
    return curve_exit_return_support(window, index, frame_height=720)


def test_supported_curve_can_have_both_model_endpoints_below_old_top_band():
    w = flight()
    assert w.shuttle.y[4] > 72 and w.shuttle.y[35] > 72
    proof = support(w)
    assert proof.supported
    assert all(value < 0 for value in proof.leave_one_out_apex_y)
    np.testing.assert_allclose(proof.curve["apex_y"], -100, atol=1e-6)


def test_visible_apex_does_not_become_an_exit():
    assert not support(flight(apex=50)).supported


def test_anchor_omission_uncertainty_must_stay_outside_image():
    w = flight(apex=-1)
    w.shuttle.y[2] += 5
    proof = support(w)
    assert proof.curve["apex_y"] < 0
    assert max(proof.leave_one_out_apex_y) > 0
    assert not proof.supported


def test_slow_apex_or_floor_noise_cannot_support_curve():
    w = flight()
    w.shuttle.y[w.shuttle.vis] = 200
    assert not support(w).supported


def test_no_unavailable_future_anchor_is_used():
    w = flight()
    t = w.shuttle
    prefix = replace(
        w,
        shuttle=Track(t.x[:30], t.y[:30], t.vis[:30], t.conf[:30], t.interp[:30]),
        replay=np.zeros(30, bool),
        pose_stride=None,
        break_before=np.zeros(30, bool),
    )
    assert not support(prefix).supported


def test_known_cut_and_invalid_view_abstain():
    w = flight()
    w.break_before[20] = True
    assert not support(w).supported
    w = flight()
    w.replay[10] = True
    assert not support(w).supported


def test_one_stale_or_reconstructed_bracket_is_not_observed_flight():
    w = flight()
    w.shuttle.interp[35:40] = True
    assert not support(w).supported


def test_speed_budget_and_two_second_budget_are_preserved():
    w = flight()
    w.shuttle.x[1] += 500
    assert not support(w).supported
    assert not curve_exit_return_support(flight(), 10, frame_height=720, max_gap_s=0.5).supported
