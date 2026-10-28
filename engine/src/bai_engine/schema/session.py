"""Session = one analysed video source (uploaded file, YouTube video, or a live stream)."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from fractions import Fraction
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator
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


class TeamInfo(BaseModel):
    """An explicitly recorded team, separate from the score-side slot."""

    model_config = ConfigDict(extra="forbid")
    team_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
    score_slot: Literal["P1", "P2"] | None = None


class ParticipantInfo(BaseModel):
    """A session participant; identity is not inferred from court position."""

    model_config = ConfigDict(extra="forbid")
    participant_id: str = Field(min_length=1, max_length=64, pattern=r"^[A-Za-z0-9][A-Za-z0-9_-]*$")
    name: str | None = Field(default=None, max_length=80)
    team_id: str | None = None


class ParticipantRoster(BaseModel):
    """User-provided session roster; it is not a tracker-to-person mapping."""

    model_config = ConfigDict(extra="forbid")
    match_format: Literal["singles", "doubles"]
    teams: list[TeamInfo] = Field(default_factory=list, max_length=2)
    participants: list[ParticipantInfo] = Field(default_factory=list, max_length=32)

    @model_validator(mode="after")
    def validate_identifiers(self) -> ParticipantRoster:
        team_ids = [team.team_id for team in self.teams]
        participant_ids = [participant.participant_id for participant in self.participants]
        slots = [team.score_slot for team in self.teams if team.score_slot is not None]
        normalized_teams = {value.casefold() for value in team_ids}
        normalized_people = {value.casefold() for value in participant_ids}
        if len(normalized_teams) != len(team_ids) or len(normalized_people) != len(participant_ids):
            raise ValueError("team and participant identifiers must be unique")
        if len(set(slots)) != len(slots):
            raise ValueError("a score slot cannot belong to two teams")
        if normalized_teams & {"p1", "p2"}:
            raise ValueError("team identifiers must be distinct from score slots")
        if normalized_people & ({"p1", "p2"} | normalized_teams) or any(
            value.startswith("participant-") for value in normalized_people
        ):
            raise ValueError("participant identifiers must be distinct from score slots, teams and tracker episodes")
        if any(
            participant.team_id is not None and participant.team_id not in team_ids
            for participant in self.participants
        ):
            raise ValueError("participant team must exist in the roster")
        return self


class Session(BaseModel):
    model_config = ConfigDict(extra="forbid")

    session_id: str = Field(default_factory=lambda: str(ULID()))
    title: str
    sport: str = "badminton"
    source: Source
    media: MediaInfo | None = None
    players: list[PlayerInfo] = Field(default_factory=lambda: [PlayerInfo(player_id="P1"), PlayerInfo(player_id="P2")])
    roster: ParticipantRoster | None = None
    profile: str = "gpu-rtx4000"
    status: SessionStatus = SessionStatus.CREATED
    status_detail: str | None = None
    frontier_frame: int = 0  # highest frame with fully analysed perception (contiguous from 0)
    analysed_frames: int = 0  # total analysed frames (may be non-contiguous after seeks)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    meta: dict[str, Any] = Field(default_factory=dict)
