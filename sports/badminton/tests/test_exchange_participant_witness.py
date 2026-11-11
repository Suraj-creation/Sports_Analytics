"""Anonymous key changes cannot silently establish two opposing participants."""

from dataclasses import replace

import pytest

from bai_badminton.events.contact_evidence import ContactEvidenceInputs
from bai_badminton.events.exchange_evidence import (
    ContactParticipantContext,
    ContactParticipantObservation,
    simultaneous_opponents,
)


def context(frame, *, shot=0, content=1, coordinate=2, second_y=2, second_birth="birth-B", second_track=2):
    return ContactParticipantContext(
        shot,
        content,
        coordinate,
        (
            ContactParticipantObservation(frame, "A", "birth-A", 1, -2),
            ContactParticipantObservation(frame, "B", second_birth, second_track, second_y),
        ),
    )


def test_source_bound_simultaneous_opponents_supply_anonymous_activity_proof():
    proof = simultaneous_opponents(context(5), "A", context(20), "B")
    assert proof["coobserved_frames"] == [5, 20]
    assert proof["epoch"] == [0, 1, 2]
    assert proof["birth_observation_ids"] == ["birth-A", "birth-B"]


@pytest.mark.parametrize(
    "changes",
    [
        {"shot": 1},
        {"content": 2},
        {"coordinate": 3},
        {"second_birth": "replacement"},
        {"second_track": 3},
        {"second_y": -1},
        {"second_y": 0},
    ],
)
def test_epoch_fragmentation_or_same_side_does_not_prove_opponents(changes):
    assert simultaneous_opponents(context(5), "A", context(20, **changes), "B") is None


def test_different_keys_without_simultaneous_coverage_do_not_prove_different_people():
    first = replace(context(5), observations=context(5).observations[:1])
    second = replace(context(20), observations=context(20).observations[1:])
    assert simultaneous_opponents(first, "A", second, "B") is None


def test_all_witness_frames_must_be_inside_available_contact_source_context():
    with pytest.raises(ValueError, match="availability"):
        ContactEvidenceInputs(5, 6, 3, 8, "controlled", participant_context=context(7))
    with pytest.raises(ValueError, match="context"):
        ContactEvidenceInputs(5, 9, 3, 8, "controlled", participant_context=context(2))


def test_duplicate_episode_rows_cannot_claim_independent_observations():
    with pytest.raises(ValueError, match="duplicate"):
        replace(context(5), observations=context(5).observations * 2)


def test_two_keys_cannot_reuse_the_same_track_or_birth_to_claim_two_people():
    assert simultaneous_opponents(context(5, second_track=1), "A", context(20, second_track=1), "B") is None
    assert (
        simultaneous_opponents(context(5, second_birth="birth-A"), "A", context(20, second_birth="birth-A"), "B")
        is None
    )
