"""Temporal activity evidence should preserve unknowns and observation boundaries."""

import pytest

from bai_badminton.events.activity import ActivityObservation, ActivityState, ActivityTracker


def frame(i, **changes):
    kw = dict(frame_idx=i, view_valid=True, person_count=2, moving=True, shuttle_visible=True)
    kw.update(changes)
    return ActivityObservation(**kw)


def test_visible_movement_and_shuttle_support_active_play_without_claiming_match():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    estimates = [tracker.update(frame(i))[0] for i in range(8)]
    assert estimates[-1].state is ActivityState.ACTIVE_PLAY
    assert estimates[-1].match_intent == "unknown"
    assert estimates[-1].basis == "movement_and_shuttle"


def test_missing_visual_observations_remain_unknown_not_inactive():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    samples = [tracker.update(frame(i, person_count=None, moving=None, shuttle_visible=None))[0] for i in range(8)]
    assert all(s.state is ActivityState.UNKNOWN for s in samples)


def test_lost_view_enters_reacquisition_and_old_evidence_is_not_reused():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    for i in range(8):
        tracker.update(frame(i))
    lost, _ = tracker.update(frame(8, view_valid=False))
    assert lost.state is ActivityState.REACQUIRING
    restored, _ = tracker.update(frame(9, person_count=None, moving=None, shuttle_visible=None))
    assert restored.state in (ActivityState.REACQUIRING, ActivityState.UNKNOWN)
    for i in range(10, 18):
        last, _ = tracker.update(frame(i, moving=None, shuttle_visible=None))
    assert last.state is ActivityState.UNKNOWN


def test_explicit_rally_evidence_is_distinct_from_active_play():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    for i in range(8):
        estimate, _ = tracker.update(frame(i, rally_observed=True))
    assert estimate.state is ActivityState.RALLY
    assert estimate.basis == "rally_observation"


def test_sustained_low_motion_never_labels_talk_or_rest():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    for i in range(8):
        estimate, _ = tracker.update(frame(i, moving=False, shuttle_visible=False, absence_verified=True))
    assert estimate.state is ActivityState.INACTIVE
    assert estimate.basis == "observed_low_motion"
    assert estimate.match_intent == "unknown"


@pytest.mark.parametrize("shuttle", [None, False])
def test_unobserved_shuttle_cannot_establish_inactivity(shuttle):
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    for i in range(8):
        estimate, _ = tracker.update(frame(i, moving=False, shuttle_visible=shuttle))
    assert estimate.state is ActivityState.UNKNOWN


def test_out_of_order_frames_are_rejected_and_gaps_clear_stale_evidence():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    for i in range(8):
        tracker.update(frame(i))
    with pytest.raises(ValueError):
        tracker.update(frame(7))
    estimate, closed = tracker.update(frame(20, moving=None, shuttle_visible=None))
    assert estimate.state is ActivityState.UNKNOWN
    assert closed is not None and closed.end_frame == 7


def test_intervals_are_bounded_non_overlapping_and_flush_exactly_once():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    closed = []
    for i in range(8):
        _, interval = tracker.update(frame(i))
        if interval is not None:
            closed.append(interval)
    _, interval = tracker.update(frame(8, view_valid=False))
    if interval is not None:
        closed.append(interval)
    final = tracker.flush()
    assert final is not None and final.end_frame == 8
    assert tracker.flush() is None
    intervals = closed + [final]
    assert all(a.end_frame + 1 == b.start_frame for a, b in zip(intervals, intervals[1:], strict=False))
    assert all(interval.start_frame <= interval.end_frame for interval in intervals)


def test_long_stream_has_bounded_history_and_no_retained_interval_queue():
    tracker = ActivityTracker(fps=10, window_s=2, hold_s=1)
    for i in range(10000):
        tracker.update(frame(i, moving=bool((i // 30) % 2), shuttle_visible=True))
    assert len(tracker._window) == 20
    assert not hasattr(tracker, "intervals")


def test_loss_of_required_evidence_clears_active_status():
    tracker = ActivityTracker(fps=2, window_s=2, hold_s=1)
    for i in range(8):
        estimate, _ = tracker.update(frame(i))
    assert estimate.state is ActivityState.ACTIVE_PLAY
    for i in range(8, 12):
        estimate, _ = tracker.update(frame(i, moving=None, shuttle_visible=None))
    assert estimate.state is ActivityState.UNKNOWN
