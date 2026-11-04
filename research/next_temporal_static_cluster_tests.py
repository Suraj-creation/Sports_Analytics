"""Synthetic association controls; no sporting labels or production decisions."""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.shuttle_post import Track
from research.next_temporal_static_cluster import static_cluster_exit_counterfactual


def evidence_window():
    n = 45
    x, y, visible = np.full(n, np.nan), np.full(n, np.nan), np.zeros(n, bool)
    for f in range(5):
        x[f], y[f], visible[f] = 500 + f, 60 - 8 * f, True
    for f in range(10, 30):
        x[f], y[f], visible[f] = 640 + 0.2 * np.sin(f), 393 + 0.2 * np.cos(f), True
    for f in range(35, 40):
        x[f], y[f], visible[f] = 535 + f - 35, 28 + 8 * (f - 35), True
    return WindowObs(1000, 30, Track.from_arrays(x, y, visible), {})


def review(window, index=15, start=900):
    return static_cluster_exit_counterfactual(
        window,
        index,
        frame_height=720,
        interval_start=start,
        minimum_event_frames=60,
        heatmap_cell_px=(2.5, 2.5),
    )


def test_static_cluster_can_expose_an_alternative_but_never_authorize_continuity():
    window = evidence_window()
    original = tuple(
        array.copy()
        for array in (
            window.shuttle.x,
            window.shuttle.y,
            window.shuttle.vis,
            window.shuttle.conf,
            window.shuttle.interp,
        )
    )
    result = review(window)
    assert result.status == "abstain_ambiguous_association"
    assert result.counterfactuals[0].unassociated_frames == tuple(range(1010, 1030))
    assert (result.counterfactuals[0].gap_start, result.counterfactuals[0].gap_end) == (1005, 1035)
    assert result.accepted_continuity is False
    assert result.requires_independent_context_evidence is True
    for actual, previous in zip(
        (window.shuttle.x, window.shuttle.y, window.shuttle.vis, window.shuttle.conf, window.shuttle.interp),
        original,
        strict=True,
    ):
        np.testing.assert_equal(actual, previous)


def test_real_floor_or_spare_shuttle_without_positive_upper_return_abstains():
    window = evidence_window()
    window.shuttle.vis[35:] = False
    assert not review(window).counterfactuals


def test_floor_stop_followed_by_a_separate_launch_is_still_explicitly_ambiguous():
    # Exactly the same observed positions can arise from a real landing and a
    # later serve when scene identity/break evidence is unavailable. Geometry
    # alone must never declare continuity or relabel this a proven distractor.
    result = review(evidence_window())
    assert result.counterfactuals
    assert result.accepted_continuity is False
    assert result.status == "abstain_ambiguous_association"


def test_known_break_between_close_rallies_prevents_cross_context_proof():
    window = evidence_window()
    window.break_before[32] = True
    assert not review(window).counterfactuals


def test_upper_image_slow_apex_is_retained_as_observed_not_a_static_distractor():
    window = evidence_window()
    window.shuttle.y[10:30] = 8
    assert not review(window).counterfactuals


def test_coherent_moving_tracklet_cannot_be_ignored_as_a_compact_cluster():
    window = evidence_window()
    window.shuttle.x[10:30] = 640 + 5 * np.arange(20)
    assert not review(window).counterfactuals


@pytest.mark.parametrize("index", [6, 15, 31])
def test_preparatory_candidate_does_not_gain_maturity_while_waiting(index):
    # Last coherent exit is1004, only40 frames after965; by current frame1031
    # the same candidate would have aged67frames. Waiting through the unknown
    # span must never satisfy the existing60-frame qualification contract.
    result = review(evidence_window(), index=index, start=965)
    assert not result.counterfactuals
    assert result.accepted_continuity is False


def test_no_unavailable_future_bracket_or_interpolated_return_is_promoted():
    window = evidence_window()
    t = window.shuttle
    prefix = replace(
        window,
        shuttle=Track(t.x[:32], t.y[:32], t.vis[:32], t.conf[:32], t.interp[:32]),
        replay=np.zeros(32, bool),
        break_before=np.zeros(32, bool),
        pose_stride=None,
    )
    assert not review(prefix).counterfactuals
    window = evidence_window()
    window.shuttle.interp[35:] = True
    assert not review(window).counterfactuals


def test_observed_return_and_four_player_state_are_not_overwritten():
    window = evidence_window()
    window.players = {str(n): PlayerSeries.empty(window.n) for n in range(4)}
    assert not review(window, index=36).counterfactuals
    assert len(window.players) == 4
    assert window.shuttle.vis[36]


def test_unknown_event_or_bad_canonical_inputs_cannot_support_an_action():
    assert not review(evidence_window(), start=None).counterfactuals
    with pytest.raises(ValueError):
        review(evidence_window(), start=True)
