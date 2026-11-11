"""Replay actual source observations, not physical ground-truth annotations.

These cases encode evidence admission and abstention contracts. Source pixels
were diagnostically reviewed; no hit, shot or participant identity is certified.
"""

import json
from pathlib import Path

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

FIXTURE = Path(__file__).parent / "fixtures/test2_short_exchange_observations.json"


def evidence(payload):
    inputs = dict(payload["inputs"])
    if inputs["motion"] is not None:
        motion = dict(inputs["motion"])
        for key in ("before_frames", "after_frames"):
            motion[key] = tuple(motion[key])
        inputs["motion"] = ContactMotionEvidence(**motion)
    for key in ("player_observation_frames", "pose_observation_frames", "racket_observation_frames"):
        inputs[key] = tuple(inputs[key])
    if inputs.get("participant_context") is not None:
        context = dict(inputs["participant_context"])
        context["observations"] = tuple(ContactParticipantObservation(**row) for row in context["observations"])
        inputs["participant_context"] = ContactParticipantContext(**context)
    return ContactEvidence(
        ContactEvidenceInputs(**inputs),
        **{
            key: ReliabilityAssessment(Reliability(payload[key]["reliability"]), tuple(payload[key]["reasons"]))
            for key in ("trajectory", "impact", "attribution")
        },
    )


def replay_case(case, *, short):
    fsm = EvidenceRallyFSM(
        RallyParams(fps=30),
        use_reconstruction=False,
        motion_guard=False,
        use_exit_recovery=True,
        use_short_exchange_evidence=short,
        use_terminal_contact_evidence=False,
    )
    assert case["initial_state"]["state"] == "idle"
    intervals, proofs = [], []
    for row in case["rows"]:
        f = row["frame"]
        if row.get("call") == "on_discontinuity":
            update = fsm.on_discontinuity(f)
        else:
            payload = case["contact_inputs"].get(str(f))
            if payload is not None:
                contact = evidence(payload)
                assert contact.inputs.available_through <= row["available_through"]
                update = fsm.on_contact_evidence(f, contact)
                if update.finalized is not None:
                    intervals.append((update.finalized.start, update.finalized.end))
                    proofs.append(fsm.last_exchange_admission)
            observation = {**row["observation"], "kind": ObservationKind(row["observation"]["kind"])}
            update = fsm.step_evidence(RallyObservation(**observation))
        if update.finalized is not None:
            intervals.append((update.finalized.start, update.finalized.end))
            proofs.append(fsm.last_exchange_admission)
    return intervals, proofs


@pytest.mark.parametrize("name,interval", [("short_31", (11715, 11751)), ("short_32", (11873, 11926))])
def test_actual_short_observations_require_independent_opposite_episode_proof(name, interval):
    case = json.loads(FIXTURE.read_text())["cases"][name]
    baseline, _ = replay_case(case, short=False)
    assert interval not in baseline
    actual, proofs = replay_case(case, short=True)
    assert actual == [interval]
    assert proofs[0]["participant_proof"]["track_ids"][0] != proofs[0]["participant_proof"]["track_ids"][1]
    assert proofs[0]["reason"] == "independent_contact_and_observed_motion_witnesses"


@pytest.mark.parametrize("name", ["unsupported_56", "handling_58", "fragmented_63"])
def test_source_uncertainty_handling_or_track_rebirth_cannot_fabricate_short_admission(name):
    case = json.loads(FIXTURE.read_text())["cases"][name]
    actual, _ = replay_case(case, short=True)
    assert actual == []
