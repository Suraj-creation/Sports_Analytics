"""Synthetic software controls, not badminton localization ground truth."""

from dataclasses import replace

import numpy as np

from bai_badminton.events.rally_motion import image_exit_return_supported
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.shuttle_post import Track
from research.next_temporal_association import associated_exit_return_supported


def window(*, singleton=True):
    n = 35
    x, y = np.full(n, np.nan), np.full(n, np.nan)
    vis = np.zeros(n, bool)
    for f in range(5):
        x[f], y[f], vis[f] = 500 + f, 60 - f * 8, True
    for f in range(25, 30):
        x[f], y[f], vis[f] = 530 + (f - 25), 28 + (f - 25) * 8, True
    if singleton:
        x[15], y[15], vis[15] = 740, 450, True
    return WindowObs(0, 30, Track.from_arrays(x, y, vis), {})


def support(w, index=10):
    return associated_exit_return_supported(w, index, frame_height=720)


def test_singleton_blocks_original_but_not_coherent_tracklet_proof():
    w = window()
    assert not image_exit_return_supported(w, 10, frame_height=720)
    before = w.shuttle.vis.copy(), w.shuttle.x.copy(), w.shuttle.y.copy()
    assert support(w, 10)
    assert support(w, 20)
    assert not support(w, 15), "Actual singleton is still an observed point, not rewritten as missing"
    for actual, expected in zip((w.shuttle.vis, w.shuttle.x, w.shuttle.y), before, strict=True):
        np.testing.assert_equal(actual, expected)


def test_clean_exit_preserves_existing_positive():
    w = window(singleton=False)
    assert image_exit_return_supported(w, 10, frame_height=720)
    assert support(w)


def test_coherent_floor_tracklet_is_not_ignored():
    w = window()
    w.shuttle.x[16], w.shuttle.y[16], w.shuttle.vis[16] = 740.1, 450.1, True
    assert not support(w)


def test_singleton_landing_without_positive_return_abstains():
    w = window()
    w.shuttle.vis[25:] = False
    assert not support(w)


def test_false_return_direction_and_non_top_return_abstain():
    w = window()
    w.shuttle.y[25:30] = [50, 44, 38, 32, 26]
    assert not support(w)
    w.shuttle.y[25:30] = [200, 208, 216, 224, 232]
    assert not support(w)


def test_available_future_prefix_cannot_use_hidden_return():
    w = window()
    t = w.shuttle
    prefix = replace(
        w,
        shuttle=Track(t.x[:20], t.y[:20], t.vis[:20], t.conf[:20], t.interp[:20]),
        replay=np.zeros(20, bool),
        pose_stride=None,
        break_before=np.zeros(20, bool),
    )
    assert not support(prefix)


def test_cut_and_invalid_replay_cannot_be_crossed():
    w = window()
    w.break_before[18] = True
    assert not support(w)
    w = window()
    w.replay[10] = True
    assert not support(w)


def test_multiple_isolated_alternatives_are_out_of_scope():
    w = window()
    w.shuttle.x[20], w.shuttle.y[20], w.shuttle.vis[20] = 300, 300, True
    assert not support(w, 17)


def test_four_player_series_do_not_change_proof_or_get_mutated():
    w = window()
    w.players = {f"player{n}": PlayerSeries.empty(w.n) for n in range(4)}
    assert support(w)
    assert len(w.players) == 4
