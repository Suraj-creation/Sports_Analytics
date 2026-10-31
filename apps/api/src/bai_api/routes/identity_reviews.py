"""Finite, explicit person/track and hitter reviews; never generic event verification."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field, StrictInt

from bai_api.deps import BusDep, Repo, SessionDep
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.bus import topic
from bai_engine.schema import Event, EventStatus, Provenance, Session
from bai_engine.store import EventStore

router = APIRouter(prefix="/api/sessions/{session_id}", tags=["identity reviews"])


class ReviewVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    analysis_revision: StrictInt = Field(ge=0)


class IdentityBody(ReviewVersion):
    observation_id: str = Field(min_length=1, max_length=80)
    participant_id: str = Field(min_length=1, max_length=64)
    start: StrictInt = Field(ge=0)
    end: StrictInt = Field(ge=0)


class StrokeBody(ReviewVersion):
    stroke_event_id: str = Field(min_length=1, max_length=80)
    identity_review_id: str = Field(min_length=1, max_length=80)


class ServiceBody(ReviewVersion):
    server_participant_id: str = Field(min_length=1, max_length=64)
    receiver_participant_id: str = Field(min_length=1, max_length=64)
    frame: StrictInt = Field(ge=0)


@contextmanager
def _snapshot(
    session: Session, repo: Repo, revision: int | None = None
) -> Iterator[tuple[Session, EventStore, IdentityReviewLedger]]:
    with repo.analysis_snapshot(session.session_id) as (current, store, _):
        if current.media is None or current.media.n_frames < 1 or current.roster is None:
            raise HTTPException(409, "A video timeline and participant roster are required")
        if revision is not None:
            if current.status != "analysed":
                raise HTTPException(409, "Review saved completed analysis; wait for processing to finish")
            if revision != int(current.meta.get("analysis_revision", 0)):
                raise HTTPException(409, "Analysis changed; reload its observations before reviewing")
        ledger = IdentityReviewLedger(
            store,
            [p.participant_id for p in current.roster.participants],
            max_frame=current.media.n_frames - 1,
            fps=str(current.media.fps),
        )
        yield current, store, ledger


def _publish(bus: BusDep, session: Session, event: Event) -> Event:
    bus.publish(
        topic(session.session_id, "events"),
        {
            "type": "events",
            "analysis_revision": int(session.meta.get("analysis_revision", 0)),
            "generation": str(session.meta.get("analysis_generation") or ""),
            "events": [event.model_dump(mode="json")],
        },
    )
    return event


@router.get("/identity-reviews")
def current_reviews(session: SessionDep, repo: Repo) -> dict:
    from bai_badminton.analytics.rebuild import lineage_ids

    with _snapshot(session, repo) as (current, store, ledger):
        current_strokes = {
            ancestor: stroke.event_id
            for stroke in store.query(types=["stroke"])
            for ancestor in lineage_ids(store, stroke)
        }
        return {
            "analysis_revision": int(current.meta.get("analysis_revision", 0)),
            "events": [event.model_dump(mode="json") for event in ledger.current()],
            "stroke_reviews": [
                {
                    **event.model_dump(mode="json"),
                    "current_stroke_event_id": current_strokes.get(event.payload.get("stroke_event_id")),
                }
                for event in store.query(types=["stroke_participant_review"])
            ],
        }


@router.post("/identity-reviews", status_code=201)
def confirm_identity(session: SessionDep, repo: Repo, bus: BusDep, body: IdentityBody) -> Event:
    with _snapshot(session, repo, body.analysis_revision) as (current, _, ledger):
        event = ledger.confirm(body.observation_id, body.participant_id, body.start, body.end)
    return _publish(bus, current, event)


@router.delete("/identity-reviews/{event_id}")
def revoke_identity(
    session: SessionDep, repo: Repo, bus: BusDep, event_id: str, analysis_revision: Annotated[int, Query(ge=0)]
) -> Event:
    with _snapshot(session, repo, analysis_revision) as (current, _, ledger):
        event = ledger.revoke(event_id)
    return _publish(bus, current, event)


@router.post("/stroke-participant-reviews", status_code=201)
def confirm_stroke(session: SessionDep, repo: Repo, bus: BusDep, body: StrokeBody) -> Event:
    with _snapshot(session, repo, body.analysis_revision) as (current, _, ledger):
        event = ledger.confirm_stroke(body.stroke_event_id, body.identity_review_id)
    return _publish(bus, current, event)


@router.delete("/stroke-participant-reviews/{event_id}")
def revoke_stroke(
    session: SessionDep, repo: Repo, bus: BusDep, event_id: str, analysis_revision: Annotated[int, Query(ge=0)]
) -> Event:
    from bai_engine.schema import Provenance

    with _snapshot(session, repo, analysis_revision) as (current, store, _):
        event = next(
            (
                event
                for event in store.query(types=["stroke_participant_review"])
                if event.event_id == event_id and event.provenance.model == "human"
            ),
            None,
        )
        if event is None:
            raise ValueError("unknown current hitter review")
        event = store.append(event.retract(Provenance(model="human", worker="review-ui"), "hitter review revoked"))
    return _publish(bus, current, event)


@router.get("/doubles-service")
def doubles_service(session: SessionDep, repo: Repo, frame: Annotated[int | None, Query(ge=0)] = None) -> dict:
    from bai_badminton.analytics.doubles_service import service_at

    with _snapshot(session, repo) as (current, store, _):
        maximum = current.media.n_frames - 1
        if frame is not None and frame > maximum:
            raise ValueError("service frame outside the video timeline")
        result = service_at(
            store, current.roster, maximum if frame is None else frame, int(current.meta.get("analysis_revision", 0))
        )
        return {**result, "analysis_revision": int(current.meta.get("analysis_revision", 0))}


@router.post("/doubles-service", status_code=201)
def setup_doubles_service(session: SessionDep, repo: Repo, bus: BusDep, body: ServiceBody) -> Event:
    from bai_badminton.analytics.doubles_service import canonical_score_state, prefix_digest, teams_for
    from bai_badminton.rules.doubles import DoublesServiceOrder

    with _snapshot(session, repo, body.analysis_revision) as (current, store, _):
        if body.frame >= current.media.n_frames:
            raise ValueError("service frame outside the video timeline")
        teams = teams_for(current.roster)
        snapshot = store.state_at(body.frame)
        recorded = canonical_score_state(store, body.frame)
        if recorded is None and snapshot is not None:
            recorded = snapshot.state
        if recorded is None:
            if body.frame != 0 or store.query(types=["point"], frame_to=body.frame):
                raise ValueError("mid-game setup requires a recorded score snapshot")
            score, game = {"P1": 0, "P2": 0}, 1
        else:
            score, game = recorded.get("score"), recorded.get("game_no")
            if recorded.get("winner") is not None:
                raise ValueError("match is already finished")
        state = DoublesServiceOrder.seed(teams, body.server_participant_id, body.receiver_participant_id, score)
        if recorded is not None and recorded.get("server_known", True) and recorded.get("server") != state.serving_team:
            raise ValueError("chosen server conflicts with the recorded serving team")
        event = store.append(
            Event(
                session_id=current.session_id,
                type="doubles_service_setup",
                frame_start=body.frame,
                frame_end=body.frame,
                pts_us=current.media.timeline().frame_to_pts_us(body.frame),
                status=EventStatus.HUMAN_VERIFIED,
                provenance=Provenance(model="human", worker="review-ui"),
                payload={
                    "server": state.server,
                    "receiver": state.receiver,
                    "teams": {slot: list(pair) for slot, pair in teams.items()},
                    "score": score,
                    "game_no": game,
                    "analysis_revision": body.analysis_revision,
                    "score_prefix_sha256": prefix_digest(store, body.frame),
                    "basis": "explicit_opening_selection"
                    if recorded is None
                    else "explicit_selection_at_recorded_score",
                },
            )
        )
    return _publish(bus, current, event)
