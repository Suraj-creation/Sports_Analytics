"""Session = one analysed video source (uploaded file, YouTube video, or a live stream)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from fractions import Fraction
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from ulid import ULID

from bai_engine.timeline import Timeline


class SourceKind(StrEnum):
    UPLOAD = "upload"
    YOUTUBE = "youtube"
    RTSP = "rtsp"
    SRT = "srt"
    WEBRTC = "webrtc"
    CAMERA = "camera"

    @property
    def is_live(self) -> bool:
        return self in (SourceKind.RTSP, SourceKind.SRT, SourceKind.WEBRTC, SourceKind.CAMERA)


class SessionStatus(StrEnum):
    CREATED = "created"
    INGESTING = "ingesting"  # downloading / probing / building proxy
    READY_TO_PLAY = "ready_to_play"  # first HLS segments available; analysis may still run
    ANALYSING = "analysing"
    ANALYSED = "analysed"
    FAILED = "failed"


class Source(BaseModel):
    model_config = ConfigDict(extra="forbid")

    kind: SourceKind
    uri: str  # stored path (content-addressed) or URL
    original_name: str | None = None
    sha256: str | None = None


class MediaInfo(BaseModel):
    """Properties of the CFR analysis proxy (the canonical timeline)."""

    model_config = ConfigDict(extra="forbid")

    fps_num: int
    fps_den: int
    n_frames: int
    width: int
    height: int
    duration_us: int
    codec: str = "h264"
    has_audio: bool = False
    source_width: int | None = None
    source_height: int | None = None
    source_codec: str | None = None
    source_fps: str | None = None
    variable_frame_rate: bool = False

    @property
    def fps(self) -> Fraction:
        return Fraction(self.fps_num, self.fps_den)

    def timeline(self) -> Timeline:
        return Timeline(self.fps, self.n_frames)


class PlayerInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    player_id: str  # "P1" / "P2" (doubles: "P1a" ...)
    name: str | None = None
    color: str | None = None


class Session(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(default_factory=lambda: str(ULID()))
    title: str
    sport: str = "badminton"
    source: Source
    media: MediaInfo | None = None
    players: list[PlayerInfo] = Field(default_factory=lambda: [PlayerInfo(player_id="P1"), PlayerInfo(player_id="P2")])
    profile: str = "gpu-rtx4000"
    status: SessionStatus = SessionStatus.CREATED
    status_detail: str | None = None
    frontier_frame: int = 0  # highest frame with fully analysed perception (contiguous from 0)
    analysed_frames: int = 0  # total analysed frames (may be non-contiguous after seeks)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    meta: dict[str, Any] = Field(default_factory=dict)
