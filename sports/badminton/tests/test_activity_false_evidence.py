"""False shuttle evidence must not turn walking into badminton play."""

from bai_badminton.events.activity import ActivityObservation, ActivityState, ActivityTracker


def run_case(positions):
    tracker = ActivityTracker(fps=10, window_s=2, hold_s=0.5)
    for i, position in enumerate(positions):
        estimate, _ = tracker.update(
            ActivityObservation(
                frame_idx=i,
                view_valid=True,
                person_count=2,
                moving=True,
                shuttle_visible=True if position is not None else None,
                shuttle_position=position,
            )
        )
    return estimate


def test_stationary_shuttle_with_people_walking_is_unknown():
    estimate = run_case([(0.30, 0.40)] * 40)
    assert estimate.state is ActivityState.UNKNOWN


def test_single_spurious_shuttle_position_cannot_establish_play():
    estimate = run_case([(0.90, 0.4) if i % 20 == 10 else (0.3, 0.4) if i % 5 == 0 else None for i in range(40)])
    assert estimate.state is ActivityState.UNKNOWN


def test_discontinuous_shuttle_jumps_do_not_establish_play():
    positions = [(0.1 if (i // 5) % 2 == 0 else 0.9, 0.4) if i % 5 == 0 else None for i in range(40)]
    assert run_case(positions).state is ActivityState.UNKNOWN


def test_jump_threshold_is_time_based_at_30_fps():
    tracker = ActivityTracker(fps=30, window_s=2, hold_s=0.5)
    for i in range(120):
        pos = (0.1 if (i // 15) % 2 == 0 else 0.9, 0.4) if i % 15 == 0 else None
        estimate, _ = tracker.update(
            ActivityObservation(
                frame_idx=i,
                view_valid=True,
                person_count=2,
                moving=True,
                shuttle_visible=True if pos is not None else None,
                shuttle_position=pos,
            )
        )
    assert estimate.state is ActivityState.UNKNOWN


def test_consistent_trajectory_at_different_frame_rates():
    for fps in (10, 30):
        tracker = ActivityTracker(fps=fps, window_s=2, hold_s=0.5)
        for i in range(4 * fps):
            pos = (0.2 + 0.03 * (i / fps), 0.4) if i % (fps // 2) == 0 else None
            estimate, _ = tracker.update(
                ActivityObservation(
                    frame_idx=i,
                    view_valid=True,
                    person_count=2,
                    moving=True,
                    shuttle_visible=True if pos is not None else None,
                    shuttle_position=pos,
                )
            )
        assert estimate.state is ActivityState.ACTIVE_PLAY
        assert estimate.match_intent == "unknown"
