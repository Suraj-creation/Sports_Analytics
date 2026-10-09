"""Canonical, versioned data contracts (pydantic v2 → JSON Schema → generated TypeScript types)."""

from bai_engine.schema.events import (
    SCHEMA_VERSION,
    Actors,
    ConfidenceBand,
    Event,
    EventStatus,
    Evidence,
    EvidenceKind,
    Provenance,
    current_view,
    new_event_id,
)
from bai_engine.schema.session import MediaInfo, PlayerInfo, Session, SessionStatus, Source, SourceKind
from bai_engine.schema.state import StateSnapshot
from bai_engine.schema.tracks import TRACK_ARROW_SCHEMA, TrackObject, TrackSample, samples_to_table, table_to_samples

__all__ = [
    "SCHEMA_VERSION",
    "TRACK_ARROW_SCHEMA",
    "Actors",
    "ConfidenceBand",
    "Event",
    "EventStatus",
    "Evidence",
    "EvidenceKind",
    "MediaInfo",
    "PlayerInfo",
    "Provenance",
    "Session",
    "SessionStatus",
    "Source",
    "SourceKind",
    "StateSnapshot",
    "TrackObject",
    "TrackSample",
    "current_view",
    "new_event_id",
    "samples_to_table",
    "table_to_samples",
]
