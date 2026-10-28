"""Human-confirmed finite intervals must not authorize intervening casual play."""

import pytest

from bai_badminton.events.match_phase import MatchPhaseTracker, Phase, RallyEvidence


def test_two_bounded_intervals_leave_break_and_outside_unknown():
    tracker = MatchPhaseTracker()
    tracker.set_reviewed_intervals([(10, 20), (40, 50)])
    assert tracker.decide(10, RallyEvidence(formation=False), end=20).official
    outside = tracker.decide(21, RallyEvidence(scoreboard="changed"), end=25)
    assert not outside.official and outside.phase is Phase.UNKNOWN and outside.basis == "insufficient"
    assert tracker.decide(40, RallyEvidence(formation=False), end=50).official
    assert not tracker.decide(51, RallyEvidence(), end=52).official


def test_rally_crossing_boundary_or_missing_end_is_not_authorized():
    tracker = MatchPhaseTracker()
    tracker.set_reviewed_intervals([(10, 20)])
    assert not tracker.decide(15, RallyEvidence(), end=21).official
    assert not tracker.decide(15, RallyEvidence()).official
    assert not tracker.decide(9, RallyEvidence(), end=10).official


def test_per_rally_override_has_priority_and_marker_never_extends_intervals():
    tracker = MatchPhaseTracker(match_start_frame=0)
    tracker.set_reviewed_intervals([(10, 20)])
    assert not tracker.decide(25, RallyEvidence(), end=30).official
    assert tracker.decide(25, RallyEvidence(), end=30, override=True).official
    assert not tracker.decide(10, RallyEvidence(), end=20, override=False).official


def test_empty_intervals_explicitly_withhold_and_none_restores_legacy_marker():
    tracker = MatchPhaseTracker(match_start_frame=0)
    tracker.set_reviewed_intervals([])
    assert not tracker.decide(10, RallyEvidence(), end=20).official
    tracker.set_reviewed_intervals(None)
    assert tracker.decide(10, RallyEvidence(), end=20).official


@pytest.mark.parametrize("intervals", [[(-1, 3)], [(2, 1)], [(0, 5), (5, 7)], [(True, 4)], [(0, 3.5)]])
def test_rejects_invalid_or_overlapping_intervals(intervals):
    tracker = MatchPhaseTracker()
    with pytest.raises(ValueError):
        tracker.set_reviewed_intervals(intervals)
    assert tracker.reviewed_intervals is None


def test_unsorted_disjoint_intervals_are_sorted():
    tracker = MatchPhaseTracker()
    tracker.set_reviewed_intervals([(40, 50), (10, 20)])
    assert tracker.reviewed_intervals == ((10, 20), (40, 50))


def test_invalid_update_preserves_prior_reviewed_intervals():
    tracker = MatchPhaseTracker()
    tracker.set_reviewed_intervals([(10, 20)])
    with pytest.raises(ValueError):
        tracker.set_reviewed_intervals([(1, 4), (4, 5)])
    assert tracker.reviewed_intervals == ((10, 20),)
