"""Short exchange admission needs independent source witnesses, not duration tuning."""

import pytest

from bai_badminton.events.contact_evidence import (
    ContactEvidence,
    ContactEvidenceInputs,
    ContactMotionEvidence,
    Reliability,
    ReliabilityAssessment,
)
from bai_badminton.events.exchange_evidence import ContactParticipantContext, ContactParticipantObservation
from bai_badminton.events.rally_evidence import EvidenceRallyFSM, ObservationKind, RallyObservation
from bai_badminton.events.rally_fsm import RallyParams


def contact(frame, actor, *, reliable=True, motion=True, targets=("A", "B"), coobserved=True):
    support = (
        ContactMotionEvidence(
            (frame - 2, frame - 1, frame),
            (frame, frame + 1, frame + 2),
            8,
            12,
            spatial_sigma_px=0.7,
            incoming_direction_support=0.9,
            outgoing_direction_support=0.9,
        )
        if motion
        else None
    )
    inputs = ContactEvidenceInputs(
        frame,
        frame + 2,
        frame - 2,
        frame + 3,
        "controlled",
        motion=support,
        observation_status="fresh_observed",
        context_valid=True,
        attribution_target=actor,
        participant_context=ContactParticipantContext(
            0,
            1,
            2,
            tuple(
                ContactParticipantObservation(frame, target, "birth-" + target, index, -2.0 if index == 0 else 2.0)
                for index, target in enumerate(targets)
                if coobserved or target == actor
            ),
        ),
    )
    return ContactEvidence(
        inputs,
        ReliabilityAssessment(Reliability.PROBABLE if reliable else Reliability.AMBIGUOUS, ("controlled",)),
        ReliabilityAssessment(Reliability.INSUFFICIENT, ("no_impact_confirmation",)),
        ReliabilityAssessment(Reliability.AMBIGUOUS, ("anonymous_target",)),
    )


def exchange(actors, *, moving=True, reliable=True, witness_motion=True, coobserved=True, enabled=True):
    fsm = EvidenceRallyFSM(RallyParams(fps=30), use_reconstruction=False, use_short_exchange_evidence=enabled)
    segments, cancellations = [], []
    for frame in range(75):
        if frame in (5, 20):
            fsm.on_contact_evidence(
                frame,
                contact(
                    frame,
                    actors[frame == 20],
                    reliable=reliable,
                    motion=witness_motion,
                    targets=tuple(dict.fromkeys(actors)),
                    coobserved=coobserved,
                ),
            )
        visible = frame < 35
        update = fsm.step_evidence(
            RallyObservation(
                frame,
                ObservationKind.OBSERVED if visible else ObservationKind.MISSING,
                (12 if moving else 0.5) if visible else None,
            )
        )
        if update.finalized is not None:
            segments.append(update.finalized)
        if update.cancelled_start is not None:
            cancellations.append(update.cancelled_start)
    return fsm, segments, cancellations


def test_independent_contact_hypotheses_and_observed_flight_preserve_short_exchange():
    fsm, segments, cancelled = exchange(("anonymous-episode-A", "anonymous-episode-B"))
    assert len(segments) == 1
    assert segments[0].length < fsm.params.min_frames
    assert not cancelled
    assert fsm.last_exchange_admission["reason"] == "independent_contact_and_observed_motion_witnesses"
    assert fsm.last_exchange_admission["witness_frames"] == [5, 20]
    assert fsm.last_exchange_admission["short_exchange_evidence"] == {
        "enabled": True,
        "status": "qualified_pair",
        "observed_motion_span": [0, 2],
        "observed_motion_span_in_interval": True,
        "retained_witness_frames": [5, 20],
        "witness_scope": "retained_eligible_contact_evidence",
    }
    assert fsm.params.min_duration_s == 2


@pytest.mark.parametrize(
    "options,status,span",
    [
        ({"enabled": False}, "disabled", [0, 2]),
        ({"moving": False}, "motion_span_unavailable", None),
        ({"reliable": False}, "independent_pair_unavailable", [0, 2]),
        ({"witness_motion": False}, "independent_pair_unavailable", [0, 2]),
        ({"coobserved": False}, "independent_pair_unavailable", [0, 2]),
    ],
)
def test_unqualified_exchange_preserves_policy_inputs_without_claiming_exhaustive_reasons(options, status, span):
    fsm, segments, cancellations = exchange(("A", "B"), **options)
    assert not segments and cancellations
    details = fsm.last_exchange_admission["short_exchange_evidence"]
    assert details["enabled"] is options.get("enabled", True)
    assert details["status"] == status
    assert details["observed_motion_span"] == span
    assert details["observed_motion_span_in_interval"] is (span is not None)
    assert details["retained_witness_frames"] == [5, 20]
    assert fsm.last_exchange_admission["witness_frames"] == []


def test_short_exchange_diagnostics_exclude_out_of_interval_retained_witnesses():
    fsm = EvidenceRallyFSM(RallyParams(fps=30), use_short_exchange_evidence=True)
    fsm.on_contact(10)
    fsm._contact_witnesses = [contact(5, "A"), contact(15, "B"), contact(25, "A")]
    fsm._first_observed_motion_span = (1, 3)
    for frame in range(10, 21):
        fsm.step_evidence(RallyObservation(frame, ObservationKind.OBSERVED, 12))
    result = fsm.flush(20)
    assert result.cancelled_segment is not None
    details = fsm.last_exchange_admission["short_exchange_evidence"]
    assert details["observed_motion_span"] == [1, 3]
    assert details["observed_motion_span_in_interval"] is False
    assert details["status"] == "motion_span_unavailable"
    assert details["retained_witness_frames"] == [15]


def test_same_target_walking_or_handling_negative_is_still_cancelled():
    _, segments, _ = exchange(("same-episode", "same-episode"))
    assert not segments


def test_stationary_observations_cannot_mature_short_candidate_from_contacts_alone():
    _, segments, _ = exchange(("A", "B"), moving=False)
    assert not segments


def test_two_ambiguous_cues_without_any_reliable_trajectory_are_insufficient():
    _, segments, _ = exchange(("A", "B"), reliable=False)
    assert not segments


def test_missing_observed_motion_windows_do_not_establish_independent_contacts():
    _, segments, _ = exchange(("A", "B"), witness_motion=False)
    assert not segments


def test_fragmented_keys_without_simultaneous_observation_do_not_mature():
    _, segments, _ = exchange(("fragment-A", "fragment-B"), coobserved=False)
    assert not segments


def test_evidence_waiver_is_explicit_opt_in():
    _, segments, _ = exchange(("A", "B"), enabled=False)
    assert not segments


def test_precontact_motion_cannot_poison_or_satisfy_candidate_observed_start_witness():
    fsm = EvidenceRallyFSM(RallyParams(fps=30), use_short_exchange_evidence=True)
    fsm._run_start, fsm._run_visible = 3, 2
    fsm.on_contact_evidence(5, contact(5, "A"))
    fsm.step_evidence(RallyObservation(5, ObservationKind.OBSERVED, 12))
    assert fsm._first_observed_motion_span is None
    fsm.step_evidence(RallyObservation(6, ObservationKind.OBSERVED, 12))
    assert fsm._first_observed_motion_span is None
    fsm.step_evidence(RallyObservation(7, ObservationKind.OBSERVED, 12))
    assert fsm._first_observed_motion_span == (5, 7)
