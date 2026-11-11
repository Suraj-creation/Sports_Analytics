"""A contact candidate does not by itself contradict observed terminal rest.

Actor-neutral controls apply to singles/doubles; no reference interval is used.
"""

from dataclasses import asdict

import pytest

from bai_badminton.components import _EvidenceRally
from bai_badminton.events.contact_evidence import (
    ContactEvidence,
    ContactEvidenceInputs,
    Reliability,
    ReliabilityAssessment,
)
from bai_badminton.events.rally_evidence import EvidenceRallyFSM, ObservationKind, RallyObservation
from bai_badminton.events.rally_fsm import RallyParams, RallyState


def evidence(frame, *, impact=Reliability.INSUFFICIENT, trajectory=Reliability.INSUFFICIENT, context=True):
    inputs = ContactEvidenceInputs(
        frame,
        frame + 3,
        max(0, frame - 3),
        frame + 4,
        "controlled",
        observation_status="fresh_observed",
        context_valid=context,
    )
    return ContactEvidence(
        inputs,
        ReliabilityAssessment(trajectory, ("controlled",)),
        ReliabilityAssessment(impact, ("controlled",)),
        ReliabilityAssessment(Reliability.INSUFFICIENT, ("anonymous",)),
    )


def playing(provider=EvidenceRallyFSM):
    fsm = provider(RallyParams(fps=30), use_reconstruction=False, use_terminal_contact_evidence=True)
    fsm.on_contact(0)
    for frame in range(80):
        fsm.step_evidence(RallyObservation(frame, ObservationKind.OBSERVED, 12))
    return fsm


@pytest.mark.parametrize("provider", [EvidenceRallyFSM, _EvidenceRally])
@pytest.mark.parametrize(
    "impact,trajectory",
    [
        (Reliability.INSUFFICIENT, Reliability.AMBIGUOUS),
        (Reliability.AMBIGUOUS, Reliability.INSUFFICIENT),
        (Reliability.REJECTED, Reliability.PROBABLE),
    ],
)
def test_insufficient_or_rejected_contact_cannot_undo_terminal_rest(provider, impact, trajectory):
    fsm = playing(provider)
    for frame in range(80, 87):
        fsm.step_evidence(RallyObservation(frame, ObservationKind.OBSERVED, 0.5, player_motion=True))
    assert fsm.state is RallyState.ENDING
    previous = fsm.state, fsm.tentative_end, fsm._last_contact_frame, list(fsm._recent)
    result = fsm.on_contact_evidence(87, evidence(87, impact=impact, trajectory=trajectory))
    assert asdict(result) == {"started": None, "cancelled_start": None, "finalized": None}
    assert (fsm.state, fsm.tentative_end, fsm._last_contact_frame, list(fsm._recent)) == previous
    assert not fsm.last_contact_admission.accepted


def test_weak_in_play_candidates_keep_legacy_serve_contact_behavior():
    fsm = playing()
    assert fsm.on_contact_evidence(80, evidence(80)).started is None
    assert fsm.last_contact_admission.accepted
    assert fsm._last_contact_frame == 80


def test_supported_contact_still_resumes_and_rebuilds_postcontact_history():
    fsm = playing()
    for frame in range(80, 87):
        fsm.step_evidence(RallyObservation(frame, ObservationKind.OBSERVED, 0.5))
    fsm.on_contact_evidence(87, evidence(87, impact=Reliability.PROBABLE, trajectory=Reliability.PROBABLE))
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.tentative_end is None
    assert fsm._last_contact_frame == 87
    assert not fsm._recent
    assert fsm.last_contact_admission.accepted


def test_unknown_contact_can_propose_idle_exchange_without_becoming_physical_confirmation():
    fsm = EvidenceRallyFSM(RallyParams(fps=30), use_terminal_contact_evidence=True)
    assert fsm.on_contact_evidence(0, evidence(0)).started == 0
    assert fsm.last_contact_admission.reason == "provisional_contact_start"
    assert fsm.last_contact_admission.impact == "insufficient"


def test_invalid_context_or_explicit_rejection_cannot_start():
    for candidate in (evidence(0, context=False), evidence(0, impact=Reliability.REJECTED)):
        fsm = EvidenceRallyFSM(RallyParams(fps=30), use_terminal_contact_evidence=True)
        assert fsm.on_contact_evidence(0, candidate).started is None
        assert fsm.state is RallyState.IDLE


def test_probable_trajectory_can_continue_despite_missing_physical_impact_cues():
    fsm = playing()
    for frame in range(80, 87):
        fsm.step_evidence(RallyObservation(frame, ObservationKind.OBSERVED, 0.5))
    fsm.on_contact_evidence(87, evidence(87, trajectory=Reliability.PROBABLE))
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.last_contact_admission.impact == "insufficient"
    assert fsm.last_contact_admission.accepted


def test_contact_frame_binding_is_required():
    fsm = playing()
    with pytest.raises(ValueError, match="frame"):
        fsm.on_contact_evidence(80, evidence(81))


def test_admission_reason_survives_checkpoint_and_clears_on_reset():
    fsm = playing(_EvidenceRally)
    fsm.on_contact_evidence(80, evidence(80))
    checkpoint = fsm.checkpoint()
    decision = fsm.last_contact_admission
    fsm.reset()
    assert fsm.last_contact_admission is None
    fsm.restore(checkpoint)
    assert fsm.last_contact_admission == decision


def test_missing_shuttle_is_not_positive_rest_evidence_against_weak_contact():
    fsm = playing()
    for frame in range(80, 90):
        fsm.step_evidence(RallyObservation(frame, ObservationKind.MISSING))
    assert fsm.state is RallyState.ENDING and fsm.end_reason == "gap"
    fsm.on_contact_evidence(90, evidence(90, trajectory=Reliability.AMBIGUOUS))
    assert fsm.state is RallyState.IN_PLAY
    assert fsm.last_contact_admission.accepted
