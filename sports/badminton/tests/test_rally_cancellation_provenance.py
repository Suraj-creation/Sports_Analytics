"""Rejected exchanges retain exact intervals without becoming accepted rallies."""

import math

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
from bai_badminton.events.rally_fsm import RallyFSM, RallyParams, RallySegment, RallyState, RallyUpdate


def short_exchange():
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(10)
    for frame in range(10, 21):
        fsm.step(frame, True, 12.0)
    return fsm


@pytest.mark.parametrize("reason", ["cut", "flush", "gap"])
def test_rejected_exchange_preserves_exact_source_interval_and_terminal_reason(reason):
    fsm = short_exchange()
    if reason == "cut":
        update = fsm.on_discontinuity(21)
    elif reason == "flush":
        update = fsm.flush(20)
    else:
        updates = [fsm.step(frame, False, math.nan) for frame in range(21, 55)]
        update = next(item for item in updates if item.cancelled_start is not None)
    assert update.cancelled_start == 10
    assert update.cancelled_segment == RallySegment(10, 20, 10, reason)
    assert update.finalized is None
    assert fsm.state is RallyState.IDLE


def test_same_frame_boundary_cancellation_has_no_fabricated_preboundary_interval():
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(10)
    update = fsm.on_discontinuity(10)
    assert update.cancelled_start == 10
    assert update.cancelled_segment is None
    assert update.finalized is None


def test_previous_rejection_and_new_start_keep_distinct_interval_ownership():
    fsm = short_exchange()
    for frame in range(21, 42):
        fsm.step(frame, False, math.nan)
    assert fsm.state is RallyState.CLOSED
    update = fsm.on_contact(43)
    assert update.cancelled_start == 10
    assert update.cancelled_segment == RallySegment(10, 20, 10, "gap")
    assert update.started == 43
    assert fsm.start == 43


def test_ordinary_finalized_exchange_has_no_cancellation_payload():
    fsm = RallyFSM(RallyParams(fps=30))
    fsm.on_contact(10)
    for frame in range(10, 110):
        fsm.step(frame, True, 12.0)
    update = fsm.flush(109)
    assert update.finalized == RallySegment(10, 109, 10, "flush")
    assert update.cancelled_start is None and update.cancelled_segment is None


def supported_opponent_hypothesis(frame, actor):
    inputs = ContactEvidenceInputs(
        frame=frame, available_through=frame + 2, context_start=frame - 2, context_stop=frame + 3,
        provider="controlled_short_exchange_witness",
        motion=ContactMotionEvidence(
            before_frames=(frame - 2, frame - 1, frame),
            after_frames=(frame, frame + 1, frame + 2), speed_before=8, speed_after=12,
            spatial_sigma_px=0.7, incoming_direction_support=0.9, outgoing_direction_support=0.9,
        ),
        observation_status="fresh_observed", context_valid=True, attribution_target=actor,
        participant_context=ContactParticipantContext(0, 1, 2, (
            ContactParticipantObservation(frame, "A", "birth-A", 0, -2.0),
            ContactParticipantObservation(frame, "B", "birth-B", 1, 2.0),
        )),
    )
    return ContactEvidence(
        inputs,
        ReliabilityAssessment(Reliability.PROBABLE, ("controlled_motion_witness",)),
        ReliabilityAssessment(Reliability.INSUFFICIENT, ("physical_impact_not_confirmed",)),
        ReliabilityAssessment(Reliability.AMBIGUOUS, ("anonymous_episode_hypothesis",)),
    )


def test_supported_short_exchange_acceptance_clears_both_cancellation_fields():
    fsm = EvidenceRallyFSM(RallyParams(fps=30), use_reconstruction=False, use_short_exchange_evidence=True)
    final = None
    for frame in range(75):
        if frame in (5, 20):
            fsm.on_contact_evidence(frame, supported_opponent_hypothesis(frame, "A" if frame == 5 else "B"))
        observed = frame < 35
        update = fsm.step_evidence(RallyObservation(
            frame, ObservationKind.OBSERVED if observed else ObservationKind.MISSING,
            12.0 if observed else None,
        ))
        if update.finalized is not None:
            final = update
    assert final is not None and final.finalized.length < fsm.params.min_frames
    assert final.cancelled_start is None and final.cancelled_segment is None


def test_existing_positional_update_construction_is_backward_compatible():
    update = RallyUpdate(None, 10, None)
    assert update.cancelled_start == 10 and update.cancelled_segment is None
