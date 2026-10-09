"""High-rate per-frame perception data.

Tracks are stored columnar (Arrow/Parquet) per session and chunk — one row per (frame, object).
They are streamed to the browser as msgpack windows and referenced from events by frame range.
"""

from __future__ import annotations

from enum import StrEnum

import numpy as np
import pyarrow as pa
from pydantic import BaseModel, ConfigDict, Field


class TrackObject(StrEnum):
    SHUTTLE = "shuttle"
    PLAYER = "player"
    RACKET = "racket"


N_KEYPOINTS = 17  # COCO-17 layout (see bai_badminton.perception.keypoints)


class TrackSample(BaseModel):
    """One observation of one object in one frame (used at API/agent boundaries)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    frame_idx: int = Field(ge=0)
    obj: TrackObject
    track_id: int = -1  # -1 for the shuttle (single object)
    player_id: str | None = None
    x: float | None = None  # image coordinates of the reference point (px, analysis proxy)
    y: float | None = None
    court_x: float | None = None  # metres in court coordinates (origin: court centre)
    court_y: float | None = None
    bbox: tuple[float, float, float, float] | None = None  # x1, y1, x2, y2
    keypoints: tuple[tuple[float, float, float], ...] | None = None  # (x, y, score) × 17
    visible: bool = True
    conf: float = 0.0
    model: str = ""


TRACK_ARROW_SCHEMA = pa.schema(
    [
        pa.field("frame_idx", pa.int32(), nullable=False),
        pa.field("obj", pa.dictionary(pa.int8(), pa.string()), nullable=False),
        pa.field("track_id", pa.int32(), nullable=False),
        pa.field("player_id", pa.dictionary(pa.int8(), pa.string())),
        pa.field("x", pa.float32()),
        pa.field("y", pa.float32()),
        pa.field("court_x", pa.float32()),
        pa.field("court_y", pa.float32()),
        pa.field("bbox", pa.list_(pa.float32())),  # [x1, y1, x2, y2]
        pa.field("keypoints", pa.list_(pa.float32())),  # flattened (x, y, score) x N_KEYPOINTS
        pa.field("visible", pa.bool_(), nullable=False),
        pa.field("conf", pa.float32(), nullable=False),
        pa.field("model", pa.dictionary(pa.int8(), pa.string())),
    ]
)


def samples_to_table(samples: list[TrackSample]) -> pa.Table:
    """Convert samples to the canonical Arrow table (stable column order and types)."""
    cols: dict[str, list[object]] = {f.name: [] for f in TRACK_ARROW_SCHEMA}
    for s in samples:
        cols["frame_idx"].append(s.frame_idx)
        cols["obj"].append(s.obj.value)
        cols["track_id"].append(s.track_id)
        cols["player_id"].append(s.player_id)
        cols["x"].append(s.x)
        cols["y"].append(s.y)
        cols["court_x"].append(s.court_x)
        cols["court_y"].append(s.court_y)
        cols["bbox"].append(list(s.bbox) if s.bbox is not None else None)
        cols["keypoints"].append(
            np.asarray(s.keypoints, dtype=np.float32).reshape(-1).tolist() if s.keypoints is not None else None
        )
        cols["visible"].append(s.visible)
        cols["conf"].append(s.conf)
        cols["model"].append(s.model or None)
    arrays = [pa.array(cols[f.name], type=f.type) for f in TRACK_ARROW_SCHEMA]
    return pa.Table.from_arrays(arrays, schema=TRACK_ARROW_SCHEMA)


def table_to_samples(table: pa.Table) -> list[TrackSample]:
    out: list[TrackSample] = []
    for row in table.to_pylist():
        kps = row["keypoints"]
        out.append(
            TrackSample(
                frame_idx=row["frame_idx"],
                obj=TrackObject(row["obj"]),
                track_id=row["track_id"],
                player_id=row["player_id"],
                x=row["x"],
                y=row["y"],
                court_x=row["court_x"],
                court_y=row["court_y"],
                bbox=tuple(row["bbox"]) if row["bbox"] is not None else None,
                keypoints=tuple(tuple(kps[i : i + 3]) for i in range(0, len(kps), 3)) if kps is not None else None,
                visible=row["visible"],
                conf=row["conf"],
                model=row["model"] or "",
            )
        )
    return out
