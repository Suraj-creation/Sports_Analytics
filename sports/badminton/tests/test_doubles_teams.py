"""Doubles partnerships are provisional and require sustained visual evidence."""

from bai_badminton.participation import ParticipantFrame, ParticipantObservation
from bai_badminton.teams import DoublesTeamTracker


def frame(i, sides):
    return ParticipantFrame(
        i, "epoch", tuple(ParticipantObservation(f"p{track}", track, side, 0.9) for track, side in sides)
    )


def test_sustained_two_per_side_forms_provisional_teams_without_score_assignment():
    tracker = DoublesTeamTracker(fps=10, sustain_frames=3)
    participants = [(1, "near"), (2, "near"), (3, "far"), (4, "far")]
    for i in range(2):
        assert tracker.update(frame(i, participants), court_valid=True, active_play_evidence=True).teams == ()
    state = tracker.update(frame(2, participants), court_valid=True, active_play_evidence=True)
    assert state.status == "provisional"
    assert {tuple(team.members) for team in state.teams} == {("p1", "p2"), ("p3", "p4")}
    assert state.match_intent == "unknown" and all(team.certainty == "hypothesis" for team in state.teams)


def test_ends_switch_preserves_partnership_ids_after_sustained_evidence():
    tracker = DoublesTeamTracker(fps=10, sustain_frames=2)
    before = [(1, "near"), (2, "near"), (3, "far"), (4, "far")]
    switched = [(4, "near"), (3, "near"), (2, "far"), (1, "far")]
    tracker.update(frame(0, before), court_valid=True, active_play_evidence=True)
    a = tracker.update(frame(1, before), court_valid=True, active_play_evidence=True)
    tracker.update(frame(2, switched), court_valid=True, active_play_evidence=True)
    b = tracker.update(frame(3, switched), court_valid=True, active_play_evidence=True)
    assert {tuple(x.members): x.team_id for x in a.teams} == {tuple(x.members): x.team_id for x in b.teams}
    assert {x.side for x in b.teams} == {"near", "far"}


def test_missing_invalid_or_inactive_evidence_withholds_teams_and_resets_hysteresis():
    tracker = DoublesTeamTracker(fps=10, sustain_frames=2)
    p = [(1, "near"), (2, "near"), (3, "far"), (4, "far")]
    tracker.update(frame(0, p), court_valid=True, active_play_evidence=True)
    assert tracker.update(frame(1, p), court_valid=True, active_play_evidence=True).teams
    assert not tracker.update(frame(2, p), court_valid=False, active_play_evidence=True).teams
    assert not tracker.update(frame(3, p), court_valid=True, active_play_evidence=False).teams
    assert not tracker.update(frame(4, p), court_valid=True, active_play_evidence=True).teams
    assert tracker.update(frame(5, p), court_valid=True, active_play_evidence=True).teams


def test_unstable_crossing_or_replacement_does_not_inherit_old_membership():
    tracker = DoublesTeamTracker(fps=10, sustain_frames=2)
    a = [(1, "near"), (2, "near"), (3, "far"), (4, "far")]
    crossing = [(1, "near"), (2, "far"), (3, "far"), (4, "far")]
    replacement = [(1, "near"), (5, "near"), (3, "far"), (4, "far")]
    tracker.update(frame(0, a), court_valid=True, active_play_evidence=True)
    old = tracker.update(frame(1, a), court_valid=True, active_play_evidence=True)
    assert not tracker.update(frame(2, crossing), court_valid=True, active_play_evidence=True).teams
    assert not tracker.update(frame(3, replacement), court_valid=True, active_play_evidence=True).teams
    new = tracker.update(frame(4, replacement), court_valid=True, active_play_evidence=True)
    assert ("p1", "p5") in {x.members for x in new.teams}
    assert {x.team_id for x in old.teams} != {x.team_id for x in new.teams}


def test_duplicate_participant_and_frame_gap_never_form_a_team():
    tracker = DoublesTeamTracker(fps=10, sustain_frames=2)
    p = [(1, "near"), (2, "near"), (3, "far"), (4, "far")]
    tracker.update(frame(0, p), court_valid=True, active_play_evidence=True)
    assert not tracker.update(frame(2, p), court_valid=True, active_play_evidence=True).teams
    duplicate = [(1, "near"), (1, "near"), (3, "far"), (4, "far")]
    assert not tracker.update(frame(3, duplicate), court_valid=True, active_play_evidence=True).teams


def test_tracker_state_remains_bounded_over_a_long_recording():
    tracker = DoublesTeamTracker(fps=30, sustain_frames=3)
    participants = [(1, "near"), (2, "near"), (3, "far"), (4, "far")]
    for i in range(10000):
        result = tracker.update(frame(i, participants), court_valid=True, active_play_evidence=True)
    assert result.supporting_frames <= tracker.sustain_frames


def test_no_team_when_track_confidence_low_or_frame_is_ambiguous():
    tracker = DoublesTeamTracker(fps=30, sustain_frames=1)
    participants = frame(0, [(1, "near"), (2, "near"), (3, "far"), (4, "far")])
    from dataclasses import replace

    bad = replace(
        participants,
        participants=(replace(participants.participants[0], confidence=float("nan")), *participants.participants[1:]),
    )
    assert tracker.update(bad, court_valid=True, active_play_evidence=True).teams == ()
    bad2 = replace(frame(1, [(1, "near"), (2, "near"), (3, "far"), (4, "far")]), ambiguous_track_ids=(9,))
    assert tracker.update(bad2, court_valid=True, active_play_evidence=True).teams == ()
