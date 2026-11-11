"""Observed recovery survives a following cut without extending unobserved time."""
from math import nan

import pytest

from bai_badminton.events.rally_evidence import EvidenceRallyFSM
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallyState


@pytest.fixture(params=[RallyFSM, EvidenceRallyFSM], ids=['base', 'evidence'])
def active(request):
    fsm = request.param(RallyParams(fps=30))
    fsm.on_contact(0)
    for frame in range(101):
        fsm.step(frame, True, 10)
    return fsm


def test_closed_motion_recovery_cut_retains_all_observed_frames(active):
    for frame in range(101, 116):
        active.step(frame, False, nan)
    assert active.state is RallyState.CLOSED
    assert active.closed.end == 100
    for frame in range(116, 119):
        active.step(frame, True, 10)
    assert active.state is RallyState.IN_PLAY
    result = active.on_discontinuity(119)
    assert result.finalized is not None
    assert (result.finalized.start, result.finalized.end) == (0, 118)
    assert active.state is RallyState.IDLE


def test_ending_observed_resume_cut_retains_resume_frame(active):
    for frame in range(101, 111):
        active.step(frame, False, nan)
    assert active.state is RallyState.ENDING
    active.step(111, True, 10)
    assert active.state is RallyState.IN_PLAY
    result = active.on_discontinuity(112)
    assert result.finalized.end == 111


def test_delayed_cut_does_not_invent_unprocessed_frames(active):
    result = active.on_discontinuity(200)
    assert result.finalized.end == 100


def test_cut_preserves_earlier_tentative_gap_end(active):
    for frame in range(101, 111):
        active.step(frame, False, nan)
    assert active.state is RallyState.ENDING
    result = active.on_discontinuity(111)
    assert result.finalized.end == 100


def test_missing_evidence_does_not_reopen_closed_candidate(active):
    for frame in range(101, 116):
        active.step(frame, False, nan)
    for frame in range(116, 119):
        active.step(frame, False, nan)
    assert active.state is RallyState.CLOSED
    result = active.on_discontinuity(119)
    assert result.finalized.end == 100


def test_replay_frame_is_excluded_after_motion_recovery(active):
    for frame in range(101, 116):
        active.step(frame, False, nan)
    for frame in range(116, 119):
        active.step(frame, True, 10)
    result = active.step(119, True, 10, replay=True)
    assert result.finalized.end == 118
    assert active.state is RallyState.IDLE


def test_flush_does_not_replace_an_earlier_tentative_end(active):
    for frame in range(101, 111):
        active.step(frame, False, nan)
    assert active.state is RallyState.ENDING
    result = active.flush(111)
    assert result.finalized.end == 100
