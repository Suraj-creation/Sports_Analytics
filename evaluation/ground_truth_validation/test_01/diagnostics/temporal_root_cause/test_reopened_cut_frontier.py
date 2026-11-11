"""Candidate regression; read-only production imports, no threshold tuning."""
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState


def test_cut_keeps_observed_recovery_frames_after_closed_rally_reopens():
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(0)
    for frame in range(101):
        fsm.step(frame, True, 10)
    for frame in range(101,116):
        fsm.step(frame, False, float('nan'))
    assert fsm.state is RallyState.CLOSED
    assert fsm.closed.end == 100
    for frame in range(116,119):
        fsm.step(frame, True, 10)
    assert fsm.state is RallyState.IN_PLAY
    result = fsm.on_discontinuity(119)
    assert result.finalized is not None
    # Three independently observed recovery frames116,117,118 were accepted as
    # continuation. A cut at119 must retain them, not use a stale pre-reopen frontier.
    assert result.finalized.end == 118
