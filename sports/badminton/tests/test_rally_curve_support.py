"""Continuation contracts and source-bound numerical reproduction fixtures.

Cached fixture coordinates are model output, never reviewed shuttle ground truth.
"""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.events.rally_motion import (
    image_exit_return_curve_support,
    image_exit_return_supported,
)
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.shuttle_post import Track


def observed_window(frame0, n, points):
    x, y, vis = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, bool)
    for frame, px, py in points:
        x[frame - frame0], y[frame - frame0], vis[frame - frame0] = px, py, True
    return WindowObs(frame0, 30, Track.from_arrays(x, y, vis), {})


def curve_window(apex=-100.0):
    points = [(f, 500 + f, (f - 20) ** 2 + apex) for f in [*range(5), *range(35, 40)]]
    return observed_window(0, 45, points)


def prefix(window, length):
    t = window.shuttle
    return replace(
        window,
        shuttle=Track(t.x[:length], t.y[:length], t.vis[:length], t.conf[:length], t.interp[:length]),
        replay=np.zeros(length, bool),
        break_before=np.zeros(length, bool),
        pose_stride=None,
    )


def test_curve_source_bound_mixed_loss_support_has_explicit_sensitivity():
    points = [
        (14642, 855.5906825766926, 241.32583550496042),
        (14643, 865.14326736355, 179.74414328802214),
        (14644, 865.3055469476294, 180.05004648280135),
        (14645, 871.6720884840599, 130.68409780958578),
        (14646, 879.2233638055175, 87.84078958013106),
        (14695, 936.0669261414268, 240.6095691146407),
        (14696, 937.434624422042, 267.52757143939965),
        (14697, 936.9569051983536, 292.6421505897001),
        (14698, 936.9625183945523, 293.1135845572323),
        (14699, 936.2457875748325, 319.4673512270547),
    ]
    window = observed_window(14642, 58, points)
    assert not image_exit_return_supported(window, 5, frame_height=720)
    proof = image_exit_return_curve_support(window, 5, frame_height=720, minimum_exit_frame=14646)
    assert proof.supported
    assert (proof.gap_start, proof.gap_end) == (14647, 14695)
    assert proof.curve.apex_y == pytest.approx(-136.7733546)
    assert proof.curve.residual_rmse_px == pytest.approx(18.7811354)
    assert max(proof.leave_one_out_apex_y) < 0
    assert proof.sensitivity_semantics == "leave_one_anchor_out_sensitivity_not_calibrated_uncertainty"


@pytest.mark.parametrize("current", [10, 20, 30])
def test_curve_event_maturity_uses_last_pre_loss_anchor(current):
    window = curve_window()
    window.frame0 = 100
    assert image_exit_return_curve_support(window, current, frame_height=720, minimum_exit_frame=104).supported
    assert not image_exit_return_curve_support(window, current, frame_height=720, minimum_exit_frame=105).supported


def test_visible_or_uncertain_apex_does_not_prove_out_of_image_flight():
    assert not image_exit_return_curve_support(curve_window(apex=50), 10, frame_height=720).supported
    window = curve_window(apex=-1)
    window.shuttle.y[2] += 5
    proof = image_exit_return_curve_support(window, 10, frame_height=720)
    assert proof.curve.apex_y < 0 < max(proof.leave_one_out_apex_y)
    assert not proof.supported


@pytest.mark.parametrize(
    "cue,factory",
    [(image_exit_return_curve_support, curve_window)],
)
def test_no_cut_replay_missing_future_or_reconstructed_return(cue, factory):
    window = factory()
    window.break_before[18] = True
    assert not cue(window, 10, frame_height=720).supported
    window = factory()
    window.replay[10] = True
    assert not cue(window, 10, frame_height=720).supported
    assert not cue(prefix(factory(), 20), 10, frame_height=720).supported
    window = factory()
    window.shuttle.interp[25:] = True
    assert not cue(window, 10, frame_height=720).supported


@pytest.mark.parametrize(
    "cue,factory",
    [(image_exit_return_curve_support, curve_window)],
)
def test_four_player_retention_and_finite_input_contracts(cue, factory):
    window = factory()
    window.players = {str(n): PlayerSeries.empty(window.n) for n in range(4)}
    assert cue(window, 10, frame_height=720).supported
    assert len(window.players) == 4
    with pytest.raises(ValueError):
        cue(window, 10, frame_height=720, minimum_exit_frame=True)
    with pytest.raises(ValueError):
        cue(window, 10, frame_height=float("nan"))
