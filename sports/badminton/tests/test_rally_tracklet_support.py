"""Continuation contracts and source-bound numerical reproduction fixtures.

Cached fixture coordinates are model output, never reviewed shuttle ground truth.
"""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.events.rally_motion import (
    image_exit_return_supported,
    image_exit_return_tracklet_support,
)
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.shuttle_post import Track


def observed_window(frame0, n, points):
    x, y, vis = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, bool)
    for frame, px, py in points:
        x[frame - frame0], y[frame - frame0], vis[frame - frame0] = px, py, True
    return WindowObs(frame0, 30, Track.from_arrays(x, y, vis), {})


def singleton_window():
    points = [(f, 500 + f, 60 - f * 8) for f in range(5)]
    points += [(f, 530 + f - 25, 28 + (f - 25) * 8) for f in range(25, 30)]
    return observed_window(0, 35, [*points, (15, 740, 450)])


def prefix(window, length):
    t = window.shuttle
    return replace(
        window,
        shuttle=Track(t.x[:length], t.y[:length], t.vis[:length], t.conf[:length], t.interp[:length]),
        replay=np.zeros(length, bool),
        break_before=np.zeros(length, bool),
        pose_stride=None,
    )


def test_source_bound_singleton_blocks_valid_return_without_removing_observation():
    # Fresh v1 source877c6d39..., tracef2417843...; coordinates remain model evidence.
    points = [
        (10904, 804.28074324, 250.00067568),
        (10905, 809.07153789, 181.85745197),
        (10906, 815.38557710, 125.09421997),
        (10907, 820.11359751, 77.60647392),
        (10908, 824.95041196, 38.35800020),
        (10936, 740.0, 450.0),
        (10948, 853.79930508, 38.64319272),
        (10949, 852.57883412, 59.97712726),
        (10950, 851.87956666, 84.28398322),
        (10951, 850.23549563, 110.03181005),
        (10952, 850.67814787, 110.59235428),
    ]
    window = observed_window(10904, 49, points)
    before = window.shuttle.vis.copy(), window.shuttle.x.copy(), window.shuttle.y.copy()
    assert not image_exit_return_supported(window, 5, frame_height=720)
    proof = image_exit_return_tracklet_support(window, 5, frame_height=720, minimum_exit_frame=10908)
    assert proof.supported
    assert (proof.gap_start, proof.gap_end, proof.ignored_frame) == (10909, 10948, 10936)
    assert proof.before_frames == tuple(range(10904, 10909))
    assert proof.after_frames == tuple(range(10948, 10953))
    assert not image_exit_return_tracklet_support(window, 32, frame_height=720).supported
    for actual, original in zip((window.shuttle.vis, window.shuttle.x, window.shuttle.y), before, strict=True):
        np.testing.assert_equal(actual, original)


@pytest.mark.parametrize("current", [10, 20, 24])
def test_singleton_event_maturity_cannot_be_earned_during_loss(current):
    window = singleton_window()
    window.frame0 = 100
    assert image_exit_return_tracklet_support(window, current, frame_height=720, minimum_exit_frame=104).supported
    proof = image_exit_return_tracklet_support(window, current, frame_height=720, minimum_exit_frame=105)
    assert not proof.supported and proof.reason == "event_not_qualified_before_loss"


def test_singleton_cue_preserves_two_point_floor_tracklet_and_real_landing():
    window = singleton_window()
    window.shuttle.x[16], window.shuttle.y[16], window.shuttle.vis[16] = 740.1, 450.1, True
    assert not image_exit_return_tracklet_support(window, 10, frame_height=720).supported
    window = singleton_window()
    window.shuttle.vis[25:] = False
    assert not image_exit_return_tracklet_support(window, 10, frame_height=720).supported


def test_singleton_false_return_direction_and_competing_singletons_abstain():
    window = singleton_window()
    window.shuttle.y[25:30] = [50, 44, 38, 32, 26]
    assert not image_exit_return_tracklet_support(window, 10, frame_height=720).supported
    window = singleton_window()
    window.shuttle.x[20], window.shuttle.y[20], window.shuttle.vis[20] = 300, 300, True
    assert not image_exit_return_tracklet_support(window, 17, frame_height=720).supported


@pytest.mark.parametrize(
    "cue,factory",
    [
        (image_exit_return_tracklet_support, singleton_window),
    ],
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
    [
        (image_exit_return_tracklet_support, singleton_window),
    ],
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


def test_original_top_return_proof_is_preserved_without_alternatives():
    window = singleton_window()
    window.shuttle.vis[15] = False
    assert image_exit_return_supported(window, 10, frame_height=720)
    proof = image_exit_return_tracklet_support(window, 10, frame_height=720)
    assert proof.supported and proof.ignored_frame is None
