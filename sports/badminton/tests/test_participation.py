import numpy as np
import pytest

from bai_badminton.participation import ParticipantTracker
from bai_badminton.perception_types import PersonObs


def obs(track, side, confidence=0.9):
    y = 600.0 if side == "near" else 300.0
    return PersonObs(track_id=track, bbox=np.array([10.0, y - 100, 50.0, y]), conf=confidence)


def test_four_participants_have_distinct_ids_and_survive_crossing_and_occlusion():
    t = ParticipantTracker(frame_height=720, entry_frames=2, exit_frames=3)
    initial = [obs(1, "near"), obs(2, "near"), obs(3, "far"), obs(4, "far")]
    assert not t.update(0, initial, coverage_valid=True).participants
    established = t.update(1, initial, coverage_valid=True)
    ids = {p.track_id: p.participant_id for p in established.participants}
    assert len(ids) == len(set(ids.values())) == 4
    t.update(2, [obs(1, "far"), obs(3, "far"), obs(4, "far")], coverage_valid=True)
    returned = t.update(3, [obs(1, "far"), obs(2, "near"), obs(3, "far"), obs(4, "far")], coverage_valid=True)
    assert {p.track_id: p.participant_id for p in returned.participants} == ids
    assert not returned.events


def test_substitution_is_hypothesis_not_identity_transfer():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=2, substitution_window_frames=10)
    before = t.update(0, [obs(1, "near"), obs(2, "far")], coverage_valid=True)
    old = next(p.participant_id for p in before.participants if p.track_id == 1)
    t.update(1, [obs(2, "far")], coverage_valid=True)
    lost = t.update(2, [obs(2, "far")], coverage_valid=True)
    assert [(e.kind, e.participant_id) for e in lost.events] == [("PLAYER_EXITED", old)]
    after = t.update(3, [obs(7, "near"), obs(2, "far")], coverage_valid=True)
    newcomer = next(p.participant_id for p in after.participants if p.track_id == 7)
    assert newcomer != old
    candidate = [e for e in after.events if e.kind == "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN"]
    assert (
        len(candidate) == 1 and candidate[0].participant_id == newcomer and candidate[0].related_participant_id == old
    )


def test_unknown_or_low_confidence_cannot_prove_exit():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=2)
    initial = t.update(0, [obs(1, "near")], coverage_valid=True)
    pid = initial.participants[0].participant_id
    for frame in range(1, 8):
        result = t.update(frame, [obs(1, "near", 0.1)], coverage_valid=False)
        assert not result.events
    assert t.update(8, [obs(1, "near")], coverage_valid=True).participants[0].participant_id == pid


def test_duplicate_visual_track_ids_are_unresolved():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=2)
    result = t.update(0, [obs(1, "near"), obs(1, "far")], coverage_valid=True)
    assert result.participants == () and result.events == ()
    assert result.ambiguous_track_ids == (1,)


def test_reused_track_after_confirmed_exit_gets_new_participant():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    old = t.update(0, [obs(1, "near")], coverage_valid=True).participants[0].participant_id
    t.update(1, [], coverage_valid=True)
    new = t.update(2, [obs(1, "near")], coverage_valid=True).participants[0].participant_id
    assert new != old


def test_timestamps_must_advance_and_name_must_be_user_supplied():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    first = t.update(0, [obs(1, "near")], coverage_valid=True)
    pid = first.participants[0].participant_id
    assert first.participants[0].user_identity is None
    t.assign_user_identity(pid, "Alex")
    assert t.update(1, [obs(1, "near")], coverage_valid=True).participants[0].user_identity == "Alex"
    with pytest.raises(ValueError):
        t.update(1, [], coverage_valid=True)


def test_instances_prevent_cross_restart_id_collision_and_replay_namespace_is_repeatable():
    a = ParticipantTracker(frame_height=720, entry_frames=1)
    b = ParticipantTracker(frame_height=720, entry_frames=1)
    assert a.update(0, [obs(1, "near")], coverage_valid=True).participants[0].participant_id != (
        b.update(0, [obs(1, "near")], coverage_valid=True).participants[0].participant_id
    )
    a = ParticipantTracker(frame_height=720, entry_frames=1, instance_id="fixed123")
    b = ParticipantTracker(frame_height=720, entry_frames=1, instance_id="fixed123")
    assert a.update(0, [obs(1, "near")], coverage_valid=True) == b.update(0, [obs(1, "near")], coverage_valid=True)


def test_over_capacity_cannot_fabricate_exits_or_expand_state():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, max_tracks=4)
    first = t.update(0, [obs(i, "near") for i in range(4)], coverage_valid=True)
    ids = {p.track_id: p.participant_id for p in first.participants}
    for frame in range(1, 20):
        result = t.update(frame, [obs(i, "near") for i in range(5, 10)], coverage_valid=True)
        assert result.capacity_limited and not result.events
    restored = t.update(20, [obs(i, "near") for i in range(4)], coverage_valid=True)
    assert {p.track_id: p.participant_id for p in restored.participants} == ids
    assert len(t._tracks) <= 4 and len(t._pending) <= 4 and len(t._recent_exits) <= 4


def test_low_confidence_existing_track_is_not_negative_evidence():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    pid = t.update(0, [obs(1, "near")], coverage_valid=True).participants[0].participant_id
    result = t.update(1, [obs(1, "near", 0.1)], coverage_valid=True)
    assert not result.events and not result.participants
    assert t.update(2, [obs(1, "near")], coverage_valid=True).participants[0].participant_id == pid


def test_two_plausible_exits_do_not_create_a_specific_substitution_candidate():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    t.update(0, [obs(1, "near"), obs(2, "near")], coverage_valid=True)
    t.update(1, [], coverage_valid=True)
    after = t.update(2, [obs(3, "near")], coverage_valid=True)
    assert [e.kind for e in after.events] == ["PLAYER_ENTERED"]


def test_initial_tracks_are_not_claimed_to_have_entered_the_court():
    t = ParticipantTracker(frame_height=720, entry_frames=2, exit_frames=3)
    initial = [obs(1, "near"), obs(2, "near"), obs(3, "far"), obs(4, "far")]
    t.update(0, initial, coverage_valid=True)
    frame = t.update(1, initial, coverage_valid=True)
    assert len(frame.events) == 4
    assert all(e.kind == "PARTICIPANT_FIRST_OBSERVED" for e in frame.events)
    assert all(e.reason == "recording_initialization" and e.certainty == "hypothesis" for e in frame.events)
    t.update(2, [*initial, obs(5, "far")], coverage_valid=True)
    late = t.update(3, [*initial, obs(5, "far")], coverage_valid=True)
    assert len(late.events) == 1 and late.events[0].kind == "PLAYER_ENTERED"
    assert late.events[0].reason == "late_appearance" and late.events[0].certainty == "hypothesis"


def test_invalid_boxes_and_confidences_cannot_create_participants():
    t = ParticipantTracker(frame_height=720, entry_frames=1)
    invalid = [
        PersonObs(track_id=1, bbox=np.array([100.0, 100.0, 50.0, 200.0]), conf=0.9),
        PersonObs(track_id=2, bbox=np.array([10.0, 100.0, 20.0, 100.0]), conf=0.9),
        PersonObs(track_id=3, bbox=np.array([10.0, 100.0, 20.0, 200.0]), conf=1.5),
    ]
    assert not t.update(0, invalid, coverage_valid=True).participants


def test_missing_tracker_id_does_not_create_a_participant():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    for frame in range(3):
        result = t.update(frame, [obs(-1, "near")], coverage_valid=True)
        assert result.participants == () and result.events == ()


def test_missing_tracker_id_does_not_prove_an_existing_participant_exited():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    first = t.update(0, [obs(1, "near")], coverage_valid=True)
    participant = first.participants[0].participant_id
    for frame in range(1, 4):
        result = t.update(frame, [obs(-1, "near")], coverage_valid=True)
        assert result.participants == () and result.events == ()
    assert t.update(4, [obs(1, "near")], coverage_valid=True).participants[0].participant_id == participant


def test_duplicate_id_observation_does_not_count_as_exit():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    initial = t.update(0, [obs(1, "near")], coverage_valid=True)
    participant = initial.participants[0].participant_id
    frame = t.update(1, [obs(1, "near"), obs(1, "far")], coverage_valid=True)
    assert frame.ambiguous_track_ids == (1,) and frame.events == () and frame.participants == ()
    assert t.update(2, [obs(1, "near")], coverage_valid=True).participants[0].participant_id == participant


def test_duplicate_ids_in_other_observations_do_not_prove_exit():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    initial = t.update(0, [obs(1, "near"), obs(2, "far")], coverage_valid=True)
    ids = {p.track_id: p.participant_id for p in initial.participants}
    frame = t.update(1, [obs(2, "near"), obs(2, "far")], coverage_valid=True)
    assert frame.ambiguous_track_ids == (2,) and frame.events == ()
    restored = t.update(2, [obs(1, "near"), obs(2, "far")], coverage_valid=True)
    assert {p.track_id: p.participant_id for p in restored.participants} == ids


def test_substitution_candidate_when_entrant_appears_before_exit_confirmation():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=2, substitution_window_frames=10)
    start = t.update(0, [obs(1, "near"), obs(2, "far")], coverage_valid=True)
    old = next(p.participant_id for p in start.participants if p.track_id == 1)
    entered = t.update(1, [obs(1, "near"), obs(2, "far"), obs(3, "near")], coverage_valid=True)
    new = next(p.participant_id for p in entered.participants if p.track_id == 3)
    assert all(e.kind != "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN" for e in entered.events)
    t.update(2, [obs(2, "far"), obs(3, "near")], coverage_valid=True)
    exited = t.update(3, [obs(2, "far"), obs(3, "near")], coverage_valid=True)
    candidates = [e for e in exited.events if e.kind == "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN"]
    assert len(candidates) == 1
    assert candidates[0].participant_id == new and candidates[0].related_participant_id == old
    later = t.update(4, [obs(2, "far"), obs(3, "near")], coverage_valid=True)
    assert all(e.kind != "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN" for e in later.events)


def test_multiple_recent_entrants_do_not_identify_a_specific_substitution():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, substitution_window_frames=10)
    t.update(0, [obs(1, "near"), obs(2, "far")], coverage_valid=True)
    t.update(1, [obs(1, "near"), obs(2, "far"), obs(3, "near"), obs(4, "near")], coverage_valid=True)
    frame = t.update(2, [obs(2, "far"), obs(3, "near"), obs(4, "near")], coverage_valid=True)
    assert not [e for e in frame.events if e.kind == "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN"]


def test_candidate_pair_emitted_at_most_once_across_later_transitions():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, substitution_window_frames=10)
    t.update(0, [obs(1, "near")], coverage_valid=True)
    t.update(1, [], coverage_valid=True)
    matched = t.update(2, [obs(3, "near")], coverage_valid=True)
    assert sum(e.kind == "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN" for e in matched.events) == 1
    for frame in range(3, 8):
        current = t.update(frame, [obs(3, "near")], coverage_valid=True)
        assert not any(e.kind == "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN" for e in current.events)


def test_recent_entry_and_exit_buffers_remain_bounded_over_long_sessions():
    t = ParticipantTracker(
        frame_height=720, entry_frames=1, exit_frames=1, substitution_window_frames=1000, max_tracks=4
    )
    for frame in range(600):
        persons = [obs(frame + 1, "near")] if frame % 2 == 0 else []
        t.update(frame, persons, coverage_valid=True)
        assert len(t._recent_entries) <= 4
        assert len(t._recent_exits) <= 4
        assert len(t._tracks) <= 4


def test_strided_detection_only_counts_observed_absences():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=2)
    first = t.update(0, [obs(1, "near")], coverage_valid=True)
    participant = first.participants[0].participant_id
    t.update(1, [], coverage_valid=True, absence_valid=True)
    for frame in range(2, 12):
        result = t.update(frame, [], coverage_valid=True, absence_valid=False)
        assert not result.events
    returned = t.update(12, [obs(1, "far")], coverage_valid=True, absence_valid=False)
    assert returned.participants[0].participant_id == participant
    assert returned.participants[0].side == "far"
    t.update(13, [], coverage_valid=True, absence_valid=True)
    exited = t.update(14, [], coverage_valid=True, absence_valid=True)
    assert [e.kind for e in exited.events] == ["PLAYER_EXITED"]


def test_absence_valid_cannot_override_invalid_coverage():
    t = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1)
    first = t.update(0, [obs(1, "near")], coverage_valid=True)
    participant = first.participants[0].participant_id
    assert not t.update(1, [], coverage_valid=False, absence_valid=True).events
    assert t.update(2, [obs(1, "near")], coverage_valid=True).participants[0].participant_id == participant
