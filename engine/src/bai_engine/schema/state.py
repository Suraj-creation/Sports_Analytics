"""Sport-agnostic state snapshots.

The sport plugin owns the concrete state model (e.g. ``bai_badminton.rules.MatchState``); the
engine stores and serves it as an opaque JSON payload keyed by frame.  Snapshots are written at
every state change (point, game end) and periodically as seek checkpoints.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class StateSnapshot(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    session_id: str
    frame_idx: int = Field(ge=0)
    kind: str = "match"  # "match" | "checkpoint" | sport-defined
    state: dict[str, Any]
    event_seq: int | None = None  # last event seq folded into this state
