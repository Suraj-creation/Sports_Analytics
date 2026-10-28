"""Long-absence matches are review candidates, never identity merges."""

import numpy as np

from bai_badminton.participation import ParticipantTracker
from bai_badminton.perception_types import PersonObs


def obs(tid, vector, x=100.0):
    return PersonObs(
        track_id=tid,
        bbox=np.array([x, 400.0, x + 50.0, 600.0]),
        conf=0.9,
        appearance=None if vector is None else np.asarray(vector, dtype=np.float32),
    )


def test_long_absence_creates_evidenced_hypothesis_without_merging():
    tracker = ParticipantTracker(
        frame_height=720, entry_frames=1, exit_frames=1, substitution_window_frames=2, fps=1, instance_id="fixed"
    )
    previous = tracker.update(0, [obs(1, [1.0, 0.0, 0.0])], coverage_valid=True).participants[0].participant_id
    tracker.update(1, [], coverage_valid=True)
    new = tracker.update(12, [obs(9, [0.99, 0.01, 0.0], x=110)], coverage_valid=True)
    assert new.participants[0].participant_id != previous
    matches = [e for e in new.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]
    assert len(matches) == 1 and matches[0].related_participant_id == previous
    assert matches[0].certainty == "hypothesis" and matches[0].appearance_similarity > 0.9
    assert matches[0].position_distance is not None


def test_matching_appearance_without_position_is_never_enough():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, fps=1)
    tracker.update(0, [obs(1, [1.0, 0.0])], coverage_valid=True)
    tracker.update(1, [], coverage_valid=True)
    result = tracker.update(12, [obs(2, [1.0, 0.0], x=5000)], coverage_valid=True)
    assert not [e for e in result.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]


def test_two_similar_people_remain_ambiguous_and_not_merged():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, fps=1)
    tracker.update(0, [obs(1, [1.0, 0.0]), obs(2, [1.0, 0.0], x=105)], coverage_valid=True)
    tracker.update(1, [], coverage_valid=True)
    result = tracker.update(12, [obs(3, [1.0, 0.0])], coverage_valid=True)
    assert not [e for e in result.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]


def test_missing_appearance_does_not_generate_reidentification():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, fps=1)
    tracker.update(0, [obs(1, None)], coverage_valid=True)
    tracker.update(1, [], coverage_valid=True)
    result = tracker.update(12, [obs(3, None)], coverage_valid=True)
    assert not [e for e in result.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]


def test_simultaneous_lookalikes_cannot_both_claim_prior_participant():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, fps=1)
    tracker.update(0, [obs(1, [1.0, 0.0])], coverage_valid=True)
    tracker.update(1, [], coverage_valid=True)
    result = tracker.update(12, [obs(2, [1.0, 0.0]), obs(3, [1.0, 0.0], x=105)], coverage_valid=True)
    assert not [e for e in result.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]


def test_reid_memory_expires_and_is_bounded():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, fps=1, max_tracks=4)
    tracker.update(0, [obs(1, [1.0, 0.0])], coverage_valid=True)
    tracker.update(1, [], coverage_valid=True)
    result = tracker.update(602, [obs(2, [1.0, 0.0])], coverage_valid=True)
    assert not [e for e in result.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]
    for frame in range(603, 640):
        persons = [obs(frame + 10, [1.0, 0.0])] if frame % 2 == 0 else []
        tracker.update(frame, persons, coverage_valid=True)
        assert len(tracker._reid_memory) <= 4


def test_invalid_appearance_does_not_create_a_candidate():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, fps=1)
    tracker.update(0, [obs(1, [float("nan"), 0.0])], coverage_valid=True)
    tracker.update(1, [], coverage_valid=True)
    result = tracker.update(12, [obs(2, [1.0, 0.0])], coverage_valid=True)
    assert not [e for e in result.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]


def test_badly_typed_appearance_cannot_crash_tracking():
    tracker = ParticipantTracker(frame_height=720, entry_frames=1, exit_frames=1, fps=1)
    invalid = obs(1, None)
    invalid.appearance = ["bad", "data"]
    first = tracker.update(0, [invalid], coverage_valid=True)
    assert len(first.participants) == 1
    tracker.update(1, [], coverage_valid=True)
    result = tracker.update(12, [obs(2, [1.0, 0.0])], coverage_valid=True)
    assert not [e for e in result.events if e.kind == "PLAYER_REIDENTIFICATION_UNCERTAIN"]
