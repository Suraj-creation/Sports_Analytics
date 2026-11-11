"""Stationary termination does not weaken its resume gate after closing."""

from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState


def closed_stationary():
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(0)
    for frame in range(80):
        fsm.step(frame, True, 12)
    for frame in range(80, 93):
        fsm.step(frame, True, 0.5)
    assert fsm.state is RallyState.CLOSED
    assert fsm.closed.reason == "stationary"
    return fsm


def test_closed_stationary_recovery_retains_existing_resume_threshold():
    fsm = closed_stationary()
    for frame in range(93, 96):
        fsm.step(frame, True, 4)
        assert fsm.state is RallyState.CLOSED


def test_fast_observed_motion_still_recovers_before_merge_budget():
    fsm = closed_stationary()
    for frame in range(93, 96):
        fsm.step(frame, True, 12)
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.start == 0


def test_after_stationary_merge_window_expires_idle_launch_uses_start_threshold():
    from bai_badminton.events.rally_fsm import RallySegment

    fsm = RallyFSM(RallyParams(fps=30))
    fsm.state, fsm.start = RallyState.CLOSED, 0
    fsm.closed = RallySegment(0, 80, None, "stationary")
    fsm.step(103, True, 4.0)
    fsm.step(104, True, 4.0)
    result = fsm.step(105, True, 4.0)
    assert result.started == 103
