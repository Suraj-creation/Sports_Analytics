"""Explicit human review of tracker episodes and stroke participants.

These events do not verify the stroke's type or change a tracker prediction.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from bai_api.deps import Repo, SessionDep
from bai_badminton.analytics.individual import machine_hypothesis_unchanged
from bai_badminton.analytics.rebuild import lineage_ids
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import Actors, Event, EventStatus, Evidence, EvidenceKind, Provenance

router = APIRouter(prefix="/api/sessions", tags=["identity reviews"])


class IdentityReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    observation_id: str = Field(min_length=1, max_length=128)
    player_id: str = Field(min_length=1, max_length=64)
    frame_start: StrictInt = Field(ge=0)
    frame_end: StrictInt = Field(ge=0)


class StrokeParticipantReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    identity_review_id: str = Field(min_length=1, max_length=128)
    player_id: str = Field(min_length=1, max_length=64)
    participant_id: str = Field(min_length=1, max_length=128)
    track_id: StrictInt = Field(ge=0)


def _ledger(session, store):
    if session.roster is None:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "An explicit participant roster is required")
    media = session.media
    if media is None or media.n_frames <= 0 or media.fps_num <= 0 or media.fps_den <= 0:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "A valid media timeline is required")
    return IdentityReviewLedger(
        store, {p.participant_id for p in session.roster.participants}, max_frame=media.n_frames - 1, fps=media.fps
    )


@router.get("/{session_id}/identity-reviews")
def list_identity_reviews(session: SessionDep, r: Repo) -> list[Event]:
    store = r.events(session.session_id)
    return _ledger(session, store).current()


@router.post("/{session_id}/identity-reviews", status_code=201)
def create_identity_review(session: SessionDep, body: IdentityReviewInput, r: Repo) -> Event:
    store = r.events(session.session_id)
    with store._lock:
        try:
            return _ledger(session, store).confirm(
                body.observation_id, body.player_id, body.frame_start, body.frame_end
            )
        except ValueError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


@router.delete("/{session_id}/identity-reviews/{review_id}")
def revoke_identity_review(session: SessionDep, review_id: str, r: Repo) -> Event:
    store = r.events(session.session_id)
    with store._lock:
        try:
            return _ledger(session, store).revoke(review_id)
        except ValueError as exc:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc


def _scoped_reviews(store):
    return [
        e
        for e in store.query(types=["stroke_participant_review"])
        if e.status == EventStatus.HUMAN_VERIFIED and e.provenance.model == "human"
    ]


@router.get("/{session_id}/stroke-participant-reviews")
def list_stroke_participant_reviews(session: SessionDep, r: Repo) -> list[Event]:
    return _scoped_reviews(r.events(session.session_id))


@router.post("/{session_id}/strokes/{stroke_id}/participant-review", status_code=201)
def review_stroke_participant(
    session: SessionDep, stroke_id: str, body: StrokeParticipantReviewInput, r: Repo
) -> Event:
    store = r.events(session.session_id)
    with store._lock:
        ledger = _ledger(session, store)
        stroke = next((e for e in store.query(types=["stroke"]) if e.event_id == stroke_id), None)
        review = next((e for e in ledger.current() if e.event_id == body.identity_review_id), None)
        if stroke is None or review is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Current stroke and identity review are required")
        hypothesis = stroke.payload.get("participant_hypothesis")
        observation = store.get(review.payload.get("observation_id", ""))
        if not (
            review.actors.player_id == body.player_id
            and review.actors.track_id == body.track_id
            and review.payload.get("participant_id") == body.participant_id
            and review.frame_start <= stroke.frame_start <= review.frame_end
            and observation is not None
            and observation.type == "participant_observation"
            and observation.status == EventStatus.PROVISIONAL
            and observation.provenance.model == "participant_tracker_v1"
            and observation.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
            and observation.payload.get("participant_id") == body.participant_id
            and observation.payload.get("track_id") == body.track_id
            and isinstance(hypothesis, dict)
            and hypothesis.get("status") in ("provisional", "human_verified")
            and hypothesis.get("participant_id") == body.participant_id
            and hypothesis.get("track_id") == body.track_id
            and hypothesis.get("observation_id") == observation.event_id
            and machine_hypothesis_unchanged(store, stroke)
        ):
            raise HTTPException(
                status.HTTP_422_UNPROCESSABLE_ENTITY,
                "Review, observation, interval and explicit participant must match the stroke hypothesis",
            )
        if any(e.payload.get("stroke_event_id") in lineage_ids(store, stroke) for e in _scoped_reviews(store)):
            raise HTTPException(
                status.HTTP_409_CONFLICT, "Revoke the existing stroke participant review before replacing it"
            )
        return store.append(
            Event(
                session_id=session.session_id,
                type="stroke_participant_review",
                frame_start=stroke.frame_start,
                frame_end=stroke.frame_start,
                pts_us=stroke.pts_us,
                actors=Actors(player_id=body.player_id, track_id=body.track_id),
                payload={
                    "stroke_event_id": stroke.event_id,
                    "identity_review_id": review.event_id,
                    "observation_id": observation.event_id,
                    "participant_id": body.participant_id,
                    "track_id": body.track_id,
                    "player_id": body.player_id,
                    "scope": "participant_only",
                },
                status=EventStatus.HUMAN_VERIFIED,
                provenance=Provenance(model="human", worker="review-ui"),
                evidence=tuple(
                    Evidence(kind=EvidenceKind.EVENT, event_id=eid)
                    for eid in (stroke.event_id, review.event_id, observation.event_id)
                ),
            )
        )


@router.delete("/{session_id}/stroke-participant-reviews/{review_id}")
def revoke_stroke_participant_review(session: SessionDep, review_id: str, r: Repo) -> Event:
    store = r.events(session.session_id)
    with store._lock:
        review = next((e for e in _scoped_reviews(store) if e.event_id == review_id), None)
        if review is None:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown current stroke participant review")
        return store.append(
            review.retract(Provenance(model="human", worker="review-ui"), "stroke participant review revoked")
        )
