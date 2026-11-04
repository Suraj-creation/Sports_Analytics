"""Temporal correctness for the real segmenter and checkpointable rally port.

The port accepts shuttle/contact/context evidence independently of named actors;
these cases apply to singles and doubles contracts without inventing video labels.
"""

import math

import pytest

from bai_badminton.components import _Rally
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState


def _playing(params=None, provider=RallyFSM):
    fsm = provider(params or RallyParams(fps=30))
    assert fsm.on_contact(0).started == 0
    for frame in range(80):
        fsm.step(frame, True, 12.0)
    assert fsm.state is RallyState.IN_PLAY
    return fsm


@pytest.mark.parametrize("window,count", [(5, 3), (10, 7), (15, 10)])
@pytest.mark.parametrize("provider", [RallyFSM, _Rally])
def test_configured_stationary_window_controls_fresh_observed_evidence(window, count, provider):
    fsm = _playing(RallyParams(fps=30, stationary_window=window, stationary_count=count), provider)
    for frame in range(80, 80 + count - 1):
        fsm.step(frame, True, 0.5)
        assert fsm.state is RallyState.IN_PLAY
    fsm.step(80 + count - 1, True, 0.5)
    assert fsm.state is RallyState.ENDING
    assert fsm.end_reason == "stationary"


@pytest.mark.parametrize("window,count", [(5, 3), (10, 7), (15, 10)])
def test_window_configuration_survives_real_provider_checkpoint_and_reset(window, count):
    fsm = _playing(RallyParams(fps=30, stationary_window=window, stationary_count=count), _Rally)
    checkpoint = fsm.checkpoint()
    for frame in range(80, 80 + count):
        fsm.step(frame, True, 0.5)
    assert fsm.state is RallyState.ENDING
    first_end = fsm.tentative_end
    fsm.restore(checkpoint)
    assert fsm.state is RallyState.IN_PLAY
    for frame in range(80, 80 + count):
        fsm.step(frame, True, 0.5)
    assert fsm.state is RallyState.ENDING
    assert fsm.tentative_end == first_end
    fsm.reset()
    assert fsm.state is RallyState.IDLE
    assert fsm.on_contact(0).started == 0
    for frame in range(80):
        fsm.step(frame, True, 12.0)
    for frame in range(80, 80 + count):
        fsm.step(frame, True, 0.5)
    assert fsm.state is RallyState.ENDING
    assert fsm.tentative_end == first_end


def test_default_ten_frame_stationarity_without_new_contact_is_unchanged():
    fsm = _playing()
    for frame in range(80, 87):
        fsm.step(frame, True, 0.5)
    assert fsm.state is RallyState.ENDING
    assert fsm.tentative_end == 77


@pytest.mark.parametrize("provider", [RallyFSM, _Rally])
def test_contact_and_current_fast_observation_cannot_reuse_precontact_rest(provider):
    fsm = _playing(provider=provider)
    for frame in range(80, 87):
        fsm.step(frame, True, 0.5)
    assert fsm.state is RallyState.ENDING
    fsm.on_contact(87)
    assert fsm.state is RallyState.IN_PLAY
    fsm.step(87, True, 12.0)
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.tentative_end is None


def test_contact_does_not_disable_a_new_fully_observed_stationary_window():
    fsm = _playing()
    for frame in range(80, 87):
        fsm.step(frame, True, 0.5)
    fsm.on_contact(87)
    fsm.step(87, True, 12.0)
    for frame in range(88, 96):
        fsm.step(frame, True, 0.5)
        assert fsm.state is RallyState.IN_PLAY
    fsm.step(96, True, 0.5)
    assert fsm.state is RallyState.ENDING
    assert fsm.end_reason == "stationary"
    assert fsm.tentative_end >= 87


def _closed():
    fsm = _playing()
    for frame in range(80, 100):
        fsm.step(frame, True, 12.0)
    for frame in range(100, 115):
        fsm.step(frame, False, math.nan)
    assert fsm.state is RallyState.CLOSED
    assert fsm.closed.end == 99
    assert fsm.params.merge_frames == 22
    return fsm


@pytest.mark.parametrize("run_start", [120, 121])
def test_motion_onset_within_or_at_merge_budget_waits_for_three_sample_confirmation(run_start):
    fsm = _closed()
    for frame in range(115, run_start - 1):
        fsm.step(frame, False, math.nan)
    fsm.step(run_start - 1, True, math.nan)  # First returning position has no adjacent observed velocity.
    for frame in range(run_start, run_start + 2):
        update = fsm.step(frame, True, 4.0)
        assert update.finalized is None
        assert fsm.state is RallyState.CLOSED
    update = fsm.step(run_start + 2, True, 4.0)
    assert update.finalized is None
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.start == 0
    assert fsm.flush(run_start + 3).finalized.start == 0


def test_motion_onset_outside_merge_budget_keeps_separate_intervals():
    fsm = _closed()
    for frame in range(115, 121):
        fsm.step(frame, False, math.nan)
    fsm.step(121, True, math.nan)
    old = fsm.step(122, True, 4.0)
    assert old.finalized is not None
    assert (old.finalized.start, old.finalized.end) == (0, 99)
    assert fsm.state is RallyState.IDLE
    assert fsm.step(123, True, 4.0).started is None
    assert fsm.step(124, True, 4.0).started == 122
    assert fsm.start == 122


def test_unconfirmed_motion_at_window_edge_expires_if_motion_disappears():
    fsm = _closed()
    for frame in range(115, 120):
        fsm.step(frame, False, math.nan)
    fsm.step(120, True, math.nan)
    assert fsm.step(121, True, 4.0).finalized is None
    update = fsm.step(122, False, math.nan)
    assert update.finalized is not None
    assert (update.finalized.start, update.finalized.end) == (0, 99)
    assert fsm.state is RallyState.IDLE


def test_cut_during_boundary_candidate_prevents_cross_context_merge():
    fsm = _closed()
    for frame in range(115, 120):
        fsm.step(frame, False, math.nan)
    fsm.step(120, True, math.nan)
    fsm.step(121, True, 4.0)
    update = fsm.on_discontinuity(122)
    assert update.finalized is not None
    assert (update.finalized.start, update.finalized.end) == (0, 99)
    assert fsm.state is RallyState.IDLE
    fsm.step(122, True, math.nan)
    for frame in range(123, 126):
        update = fsm.step(frame, True, 12.0)
    assert update.started == 123
    assert fsm.start == 123


def test_recovery_contact_outside_budget_remains_a_distinct_exchange():
    fsm = _closed()
    for frame in range(115, 122):
        fsm.step(frame, False, math.nan)
    update = fsm.on_contact(122)
    assert update.finalized is not None
    assert (update.finalized.start, update.finalized.end) == (0, 99)
    assert update.started == 122
    assert fsm.start == 122


def test_short_positive_exchange_survives_while_short_false_motion_is_cancelled():
    for observed_count, should_survive in [(64, True), (20, False)]:
        fsm = RallyFSM(RallyParams(fps=30))
        fsm.on_contact(0)
        finalized, cancelled = [], []
        for frame in range(observed_count + 40):
            visible = frame < observed_count
            update = fsm.step(frame, visible, 12.0 if visible else math.nan)
            if update.finalized:
                finalized.append(update.finalized)
            if update.cancelled_start is not None:
                cancelled.append(update.cancelled_start)
        if should_survive:
            assert [(s.start, s.end) for s in finalized] == [(0, observed_count - 1)]
            assert cancelled == []
        else:
            assert finalized == []
            assert cancelled == [0]


def test_observed_fast_shuttle_survives_intermittent_short_losses_without_player_input():
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(0)
    for frame in range(300):
        visible = not any(start <= frame < start + 5 for start in [80, 160, 240])
        update = fsm.step(frame, visible, 12.0 if visible else math.nan)
        assert update.finalized is None
    final = fsm.flush(299).finalized
    assert (final.start, final.end) == (0, 299)


def test_unobserved_shuttle_during_a_break_cannot_start_from_player_motion():
    fsm = RallyFSM(RallyParams(fps=30))
    for frame in range(120):
        update = fsm.step(frame, False, math.nan)
        assert update.started is None
        assert update.finalized is None
    assert fsm.state is RallyState.IDLE
