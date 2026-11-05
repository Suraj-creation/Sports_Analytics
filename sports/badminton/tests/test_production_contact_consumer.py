"""Independent event-consumer controls: lifecycle finality is not physical proof."""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import ContactCandidate
from bai_badminton.events.contact_evidence import (
    ContactEvidenceInputs,
    ContactReview,
    Reliability,
    assess_contact_evidence,
)
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.participant_contact import ParticipantSnapshot
from bai_badminton.perception.association import ShuttleObservationEvidence
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.perception_types import FramePerception
from bai_badminton.testing.synth import make_rally
from bai_engine.schema import EvidenceKind
from bai_engine.store import EventStore


@pytest.fixture
def engine(tmp_path):
    store = EventStore(tmp_path / "events.sqlite", "consumer-test")
    instance = BadmintonMatchEngine("consumer-test", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    yield instance
    store.close()


def cue_window(schedule):
    n = 9
    frames = []
    player = PlayerSeries.empty(n)
    player.bbox[:] = [0, 0, 100, 200]
    for i in range(n):
        kps = np.full((17, 3), np.nan)
        kps[9] = [i * 10, 30, 0.9]
        frames.append(
            {
                "episode": ParticipantSnapshot(
                    track_id=1,
                    bbox=player.bbox[i],
                    kps=kps,
                    court_xy=(0, 0),
                    observation_id="birth",
                    detector_observed=True,
                    detector_matched=True,
                    pose_frame_idx=i,
                )
            }
        )
    window = WindowObs(
        frame0=0,
        fps=30,
        shuttle=Track.from_arrays(np.arange(n, dtype=float) * 10, np.zeros(n), np.ones(n, bool)),
        players={"episode": player},
        pose_stride=np.full(n, schedule, dtype=int),
    )
    candidate = ContactCandidate(frame=4, player_id="episode", p=0.9, scores={"proximity": 0.9, "swing": 0.8})
    return window, frames, candidate


@pytest.mark.parametrize("schedule", [0, -1])
def test_disabled_or_unknown_pose_schedule_cannot_claim_fresh_pose_frames(engine, schedule):
    window, frames, candidate = cue_window(schedule)
    result = engine._contact_with_observation_evidence(candidate, window, frames)
    assert result.evidence.inputs.pose_observation_frames == ()
    assert result.evidence.inputs.pose_observed is not True


def test_only_declared_pose_ticks_can_be_cue_frames(engine):
    window, frames, candidate = cue_window(3)
    result = engine._contact_with_observation_evidence(candidate, window, frames)
    assert result.evidence.inputs.pose_observation_frames == (0, 3, 6)


def test_stroke_keeps_parent_physical_reliability_after_ledger_confirmation(engine):
    evidence = assess_contact_evidence(
        ContactEvidenceInputs(
            frame=10,
            available_through=13,
            context_start=7,
            context_stop=14,
            provider="controlled-provider",
            observation_status="invalid",
            context_valid=False,
        )
    )
    candidate = ContactCandidate(frame=10, player_id=None, p=0.99, evidence=evidence)
    engine._on_contact(candidate, make_rally(n_shots=3).obs)
    engine._classify(engine._open_contacts[-1], next_frame=20, is_serve=False, receiver=None)
    contact = engine.store.query(types=["contact"])[0]
    stroke = engine.store.query(types=["stroke"])[0]
    assert contact.payload["physical_event_status"] == "rejected"
    assert stroke.payload["physical_event_status"] == "rejected"
    assert stroke.status.value == contact.status.value == "confirmed"


def test_unobserved_pose_is_not_declared_as_evidence_for_an_unknown_stroke(engine):
    candidate = ContactCandidate(frame=10, player_id=None, p=0.8)
    engine._on_contact(candidate, make_rally(n_shots=3).obs)
    engine._classify(engine._open_contacts[-1], next_frame=20, is_serve=False, receiver=None)
    stroke = engine.store.query(types=["stroke"])[0]
    assert all(item.kind is not EvidenceKind.POSE for item in stroke.evidence)


def test_declared_pose_range_comes_from_exact_bounded_cue_frames(engine):
    evidence = assess_contact_evidence(
        ContactEvidenceInputs(
            frame=10,
            available_through=13,
            context_start=7,
            context_stop=14,
            provider="controlled-provider",
            pose_observation_frames=(8, 10, 12),
            pose_observed=True,
        )
    )
    engine._on_contact(ContactCandidate(frame=10, player_id=None, p=0.8, evidence=evidence), make_rally(n_shots=3).obs)
    engine._classify(engine._open_contacts[-1], next_frame=20, is_serve=False, receiver=None)
    stroke = engine.store.query(types=["stroke"])[0]
    assert [item.frames for item in stroke.evidence if item.kind is EvidenceKind.POSE] == [(8, 12)]


def test_legacy_provider_missing_physical_evidence_stays_insufficient(engine):
    window, frames, candidate = cue_window(1)
    candidate = replace(candidate, evidence=None)
    result = engine._contact_with_observation_evidence(candidate, window, frames)
    assert result.evidence.impact.reliability is Reliability.INSUFFICIENT
    assert result.p == candidate.p and result.scores == candidate.scores


def test_provider_cannot_borrow_external_review_from_another_candidate_frame(engine):
    window, frames, candidate = cue_window(1)
    evidence = assess_contact_evidence(
        ContactEvidenceInputs(
            frame=5,
            available_through=8,
            context_start=1,
            context_stop=9,
            provider="independent-test-provider",
            review=ContactReview(
                frame=5,
                source_sha256="a" * 64,
                reviewer="controlled-fixture",
                review_id="other-frame",
                physical_impact=True,
            ),
        )
    )
    with pytest.raises(ValueError, match=r"frame|identity|evidence"):
        forged = replace(candidate, evidence=evidence)
        engine._contact_with_observation_evidence(forged, window, frames)


def test_provider_cannot_claim_motion_context_beyond_supplied_window(engine):
    window, frames, candidate = cue_window(1)
    evidence = assess_contact_evidence(
        ContactEvidenceInputs(
            frame=4,
            available_through=99,
            context_start=0,
            context_stop=100,
            provider="independent-test-provider",
        )
    )
    with pytest.raises(ValueError, match=r"window|context|available"):
        engine._contact_with_observation_evidence(replace(candidate, evidence=evidence), window, frames)


def test_frame_wire_rejects_association_from_another_content_epoch():
    evidence = ShuttleObservationEvidence(
        frame_idx=7,
        epoch=0,
        status="observed",
        association_status="tracked",
        raw_xy=(10, 20),
        selected_xy=(10, 20),
        raw_model_support=0.8,
    )
    with pytest.raises(ValueError, match=r"epoch|context"):
        FramePerception(
            frame_idx=7, shot_id=1, content_epoch=2, shuttle_xy=(10, 20), shuttle_conf=0.8, shuttle_observation=evidence
        )


@pytest.mark.parametrize("kind", ["player_observation_frames", "pose_observation_frames", "racket_observation_frames"])
@pytest.mark.parametrize("frames", [(101,), (6,), (8, 8), (10, 9)])
def test_cue_frames_cannot_escape_context_or_available_frontier(kind, frames):
    with pytest.raises(ValueError, match="cue"):
        ContactEvidenceInputs(
            frame=10, available_through=13, context_start=7, context_stop=14, provider="fixture", **{kind: frames}
        )
