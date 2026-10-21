"""Canonical event model — the contract between perception, temporal reasoning, analytics,
agents and the UI.

Events are low-rate, append-only facts about the match.  High-rate per-frame data lives in
:mod:`bai_engine.schema.tracks` and is *referenced* from events through ``evidence``.

Lifecycle: an event is first emitted ``provisional`` (e.g. a contact detected from a partial
window), then ``confirmed`` once its look-ahead window has been analysed.  A later refinement
never mutates an event in place: it appends a new event with ``supersedes`` pointing at the old
``event_id`` and ``status=corrected`` (or ``retracted`` to withdraw it).  Human review appends
``human_verified`` events the same way.  The "current view" of the match is therefore always a
deterministic fold over the log, which makes live updates, corrections, replay and audit work
with one mechanism.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator
from ulid import ULID

SCHEMA_VERSION = 1


class EventStatus(StrEnum):
    PROVISIONAL = "provisional"
    CONFIRMED = "confirmed"
    CORRECTED = "corrected"
    RETRACTED = "retracted"
    HUMAN_VERIFIED = "human_verified"


class ConfidenceBand(StrEnum):
    """Coarse, user-facing certainty. Thresholds are owned by the sport plugin's ontology."""

    CONFIRMED = "confirmed"
    PROBABLE = "probable"
    UNCERTAIN = "uncertain"
    UNKNOWN = "unknown"

    @classmethod
    def from_confidence(cls, p: float | None, *, confirmed: float = 0.85, probable: float = 0.6) -> ConfidenceBand:
        if p is None:
            return cls.UNKNOWN
        if p >= confirmed:
            return cls.CONFIRMED
        if p >= probable:
            return cls.PROBABLE
        return cls.UNCERTAIN


class EvidenceKind(StrEnum):
    TRACK_WINDOW = "track_window"  # a frame range of TrackSamples (shuttle / player / racket)
    POSE = "pose"
    COURT = "court"
    SCORE_OCR = "score_ocr"
    COMPONENT_SCORES = "component_scores"  # per-cue scores of a fused decision
    EVENT = "event"  # reference to another event
    DATASET = "dataset"  # ground-truth provenance
    HUMAN = "human"


class Evidence(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: EvidenceKind
    frames: tuple[int, int] | None = None
    track_id: int | None = None
    obj: str | None = None
    event_id: str | None = None
    scores: dict[str, float] | None = None
    note: str | None = None


class Provenance(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    model: str  # "<name>@<version>" or "rule:<name>" or "human" or "dataset:<name>"
    params_hash: str | None = None
    worker: str | None = None
    profile: str | None = None


class Actors(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    player_id: str | None = None  # stable match identity, e.g. "P1"
    track_id: int | None = None  # tracker id at the time of the event
    opponent_id: str | None = None


def new_event_id() -> str:
    return str(ULID())


class Event(BaseModel):
    """One immutable fact in the session's event log."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    event_id: str = Field(default_factory=new_event_id)
    session_id: str
    schema_version: int = SCHEMA_VERSION
    type: str  # namespaced by the sport ontology, e.g. "contact", "stroke", "rally_end"
    frame_start: int = Field(ge=0)
    frame_end: int = Field(ge=0)
    pts_us: int = Field(ge=0)  # presentation time of frame_start
    actors: Actors = Field(default_factory=Actors)
    payload: dict[str, Any] = Field(default_factory=dict)
    confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    band: ConfidenceBand = ConfidenceBand.UNKNOWN
    status: EventStatus = EventStatus.PROVISIONAL
    evidence: tuple[Evidence, ...] = ()
    provenance: Provenance
    supersedes: str | None = None
    parent_id: str | None = None
    seq: int | None = None  # assigned by the store on append (monotonic per session)

    @field_validator("type")
    @classmethod
    def _type_is_identifier(cls, v: str) -> str:
        if not v or not all(c.isalnum() or c in "_." for c in v):
            raise ValueError(f"invalid event type {v!r}")
        return v

    @model_validator(mode="after")
    def _check(self) -> Event:
        if self.frame_end < self.frame_start:
            raise ValueError("frame_end < frame_start")
        if self.status in (EventStatus.CORRECTED, EventStatus.RETRACTED) and not self.supersedes:
            raise ValueError(f"status={self.status} requires 'supersedes'")
        return self

    def with_seq(self, seq: int) -> Event:
        return self.model_copy(update={"seq": seq})

    def correct(self, **changes: Any) -> Event:
        """Return a correcting event that supersedes this one."""
        base = self.model_dump(exclude={"event_id", "seq", "supersedes", "status"})
        base.update(changes)
        base["status"] = changes.get("status", EventStatus.CORRECTED)
        base["supersedes"] = self.event_id
        return Event.model_validate(base)

    def retract(self, provenance: Provenance, note: str | None = None) -> Event:
        ev = (Evidence(kind=EvidenceKind.EVENT, event_id=self.event_id, note=note),)
        return Event(
            session_id=self.session_id,
            type=self.type,
            frame_start=self.frame_start,
            frame_end=self.frame_end,
            pts_us=self.pts_us,
            status=EventStatus.RETRACTED,
            supersedes=self.event_id,
            provenance=provenance,
            evidence=ev,
        )


def current_view(events: list[Event]) -> list[Event]:
    """Fold an ordered log into the live set of events.

    Each event that is superseded is replaced by its successor (transitively); retracted events
    disappear.  The returned list keeps log order of the surviving *latest* versions.
    """
    superseded: set[str] = set()
    for e in events:
        if e.supersedes:
            superseded.add(e.supersedes)
    return [e for e in events if e.event_id not in superseded and e.status != EventStatus.RETRACTED]
