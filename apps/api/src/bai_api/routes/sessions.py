"""Sessions: create (upload / YouTube), list, inspect, control, events, state, tracks, corrections."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Annotated, Any, Literal

from fastapi import APIRouter, File, Form, HTTPException, Query, Request, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, Field

from bai_api.deps import BusDep, Repo, SessionDep, SettingsDep, User
from bai_engine.bus import topic
from bai_engine.config import load_profile
from bai_engine.schema import PlayerInfo, Session, Source, SourceKind, TrackObject, table_to_samples
from bai_engine.sources import SourceError, parse_youtube_url, store_upload
from bai_engine.wire import encode_tracks

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


def _players(p1: str | None, p2: str | None) -> list[PlayerInfo]:
    return [
        PlayerInfo(player_id="P1", name=(p1 or "").strip()[:80] or None),
        PlayerInfo(player_id="P2", name=(p2 or "").strip()[:80] or None),
    ]


def _check_profile(name: str, settings: Any) -> str:
    try:
        load_profile(name, settings.profiles_dir)
    except FileNotFoundError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    return name


def _iter_upload(f: UploadFile) -> Iterator[bytes]:
    while chunk := f.file.read(1 << 20):
        yield chunk


@router.post("", status_code=201)
def create_upload(
    r: Repo,
    b: BusDep,
    s: SettingsDep,
    _: User,
    file: Annotated[UploadFile, File()],
    title: Annotated[str | None, Form()] = None,
    player1: Annotated[str | None, Form()] = None,
    player2: Annotated[str | None, Form()] = None,
    profile: Annotated[str | None, Form()] = None,
) -> Session:
    prof = _check_profile(profile or s.profile, s)
    try:
        stored = store_upload(_iter_upload(file), s.data_dir / "media", file.filename, s.max_upload_bytes)
    except SourceError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    name = (title or file.filename or "Untitled match").strip()[:120]
    session = r.save(
        Session(
            title=name,
            source=Source(
                kind=SourceKind.UPLOAD, uri=str(stored.path), original_name=file.filename, sha256=stored.sha256
            ),
            players=_players(player1, player2),
            profile=prof,
        )
    )
    b.send_command({"cmd": "start", "session_id": session.session_id})
    return session


class YouTubeRequest(BaseModel):
    url: str = Field(max_length=300)
    title: str | None = Field(default=None, max_length=120)
    player1: str | None = Field(default=None, max_length=80)
    player2: str | None = Field(default=None, max_length=80)
    profile: str | None = None
    acknowledge_rights: bool = False


@router.post("/youtube", status_code=201)
def create_youtube(body: YouTubeRequest, r: Repo, b: BusDep, s: SettingsDep, _: User) -> Session:
    if not s.youtube_ingest:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, "YouTube import is turned off on this server (BAI_YOUTUBE_INGEST)"
        )
    if not body.acknowledge_rights:
        raise HTTPException(
            status.HTTP_422_UNPROCESSABLE_ENTITY, "Confirm that you have the rights to analyse this video"
        )
    try:
        vid = parse_youtube_url(body.url)
    except SourceError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    session = r.save(
        Session(
            title=body.title or "YouTube video",
            source=Source(kind=SourceKind.YOUTUBE, uri=f"https://www.youtube.com/watch?v={vid}"),
            players=_players(body.player1, body.player2),
            profile=_check_profile(body.profile or s.profile, s),
        )
    )
    b.send_command({"cmd": "start", "session_id": session.session_id})
    return session


@router.get("")
def list_sessions(r: Repo, _: User, limit: Annotated[int, Query(ge=1, le=500)] = 100) -> list[Session]:
    return r.list(limit)


@router.get("/{session_id}")
def get_one(session: SessionDep) -> Session:
    return session


class SessionPatch(BaseModel):
    title: str | None = Field(default=None, max_length=120)
    player1: str | None = Field(default=None, max_length=80)
    player2: str | None = Field(default=None, max_length=80)


@router.patch("/{session_id}")
def patch(session: SessionDep, body: SessionPatch, r: Repo) -> Session:
    changes: dict[str, Any] = {}
    if body.title is not None:
        changes["title"] = body.title.strip() or session.title
    if body.player1 is not None or body.player2 is not None:
        cur = {p.player_id: p.name for p in session.players}
        changes["players"] = _players(
            body.player1 if body.player1 is not None else cur.get("P1"),
            body.player2 if body.player2 is not None else cur.get("P2"),
        )
    return r.update(session.session_id, **changes) if changes else session


@router.delete("/{session_id}", status_code=204)
def delete(session: SessionDep, r: Repo, b: BusDep, request: Request) -> Response:
    engine = request.app.state.engine
    if engine is not None:
        engine.stop_session(session.session_id)
    else:
        b.send_command({"cmd": "stop", "session_id": session.session_id})
    r.delete(session.session_id)
    return Response(status_code=204)


def _control(session: Session, b: Any, action: str) -> dict[str, str]:
    b.send_command({"cmd": action, "session_id": session.session_id})
    return {"status": "accepted", "action": action}


@router.post("/{session_id}/start", status_code=202)
def start(session: SessionDep, b: BusDep) -> dict[str, str]:
    """(Re)start analysis — resumes from the perception cache, never redoes GPU work."""
    return _control(session, b, "start")


@router.post("/{session_id}/stop", status_code=202)
def stop(session: SessionDep, b: BusDep) -> dict[str, str]:
    return _control(session, b, "stop")


@router.post("/{session_id}/reanalyse", status_code=202)
def reanalyse(session: SessionDep, b: BusDep) -> dict[str, str]:
    """Rebuild all events from cached perception (after calibration changes or rule upgrades)."""
    return _control(session, b, "reanalyse")


# ---------------------------------------------------------------------- events / state / tracks
@router.get("/{session_id}/events")
def events(
    session: SessionDep,
    r: Repo,
    types: Annotated[str | None, Query(description="comma-separated event types")] = None,
    frame_from: Annotated[int | None, Query(alias="from", ge=0)] = None,
    frame_to: Annotated[int | None, Query(alias="to", ge=0)] = None,
    player: Annotated[str | None, Query(pattern="^P[12]$")] = None,
    live: bool = True,
    since_seq: Annotated[int | None, Query(ge=0)] = None,
) -> dict[str, Any]:
    store = r.events(session.session_id)
    if since_seq is not None:
        evs = store.since(since_seq)
    else:
        evs = store.query(
            types=types.split(",") if types else None,
            frame_from=frame_from,
            frame_to=frame_to,
            player_id=player,
            live_only=live,
        )
    return {"last_seq": store.last_seq(), "events": [e.model_dump(mode="json") for e in evs]}


@router.get("/{session_id}/state")
def state(session: SessionDep, r: Repo, frame: Annotated[int | None, Query(ge=0)] = None) -> dict[str, Any]:
    store = r.events(session.session_id)
    snap = store.state_at(frame if frame is not None else 10**12)
    return {
        "frame": snap.frame_idx if snap else None,
        "state": snap.state if snap else None,
        "states": [
            {"frame": s.frame_idx, "score": s.state.get("score"), "game_no": s.state.get("game_no")}
            for s in store.states()
        ]
        if frame is None
        else None,
    }


@router.get("/{session_id}/tracks")
def tracks(
    session: SessionDep,
    r: Repo,
    frame_from: Annotated[int, Query(alias="from", ge=0)],
    frame_to: Annotated[int, Query(alias="to", ge=0)],
) -> Response:
    if frame_to - frame_from > 30 * 60 * 60:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "window too large (max 1 h of frames)")
    table = r.tracks(session.session_id).read([TrackObject.SHUTTLE, TrackObject.PLAYER], frame_from, frame_to)
    return Response(encode_tracks(table_to_samples(table), frame_from, frame_to), media_type="application/msgpack")


# ---------------------------------------------------------------------- calibration
class Calibration(BaseModel):
    points: dict[str, tuple[float, float]]
    net_top: tuple[tuple[float, float], tuple[float, float]] | None = None


@router.post("/{session_id}/calibration", status_code=202)
def calibrate(session: SessionDep, body: Calibration, b: BusDep) -> dict[str, Any]:
    from bai_badminton.court import CalibrationError, fit_homography

    try:
        h = fit_homography(body.points)
    except CalibrationError as e:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(e)) from e
    b.send_command(
        {
            "cmd": "calibrate",
            "session_id": session.session_id,
            "points": body.points,
            "net_top": body.net_top,
            "reply_to": topic(session.session_id, "replies"),
        }
    )
    return {"status": "accepted", "reprojection_error_px": round(h.reprojection_error_px, 2), "n_points": h.n_points}


@router.get("/{session_id}/calibration/proposal")
def calibration_proposal(session: SessionDep, r: Repo, segment: Annotated[int, Query(ge=0)] = 0) -> dict[str, Any]:
    from bai_badminton.court import REFERENCE_POINTS
    from bai_badminton.perception.scene import propose_corners
    from bai_engine.decode import SegmentDecoder

    if session.media is None or not session.source.sha256:
        raise HTTPException(status.HTTP_409_CONFLICT, "The video is still being prepared")
    mp = r.media_paths(session.source.sha256)
    fps_seg = int(session.meta.get("frames_per_segment", 60))
    try:
        frame = SegmentDecoder(mp, fps_seg).keyframe(segment)
    except FileNotFoundError as e:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That part of the video is not ready yet") from e
    prop = propose_corners(frame)
    current = r.events(session.session_id).query(types=["calibration"])
    return {
        "frame": segment * fps_seg,
        "width": frame.shape[1],
        "height": frame.shape[0],
        "proposal": None if prop is None else {"points": prop[0], "score": round(prop[1], 3)},
        "current": current[-1].payload if current else None,
        "reference_points": {k: list(v) for k, v in REFERENCE_POINTS.items()},
    }


# ---------------------------------------------------------------------- corrections
class Correction(BaseModel):
    kind: Literal["winner", "verify"]
    rally_event_id: str | None = None
    winner: Literal["P1", "P2"] | None = None
    event_id: str | None = None
    payload: dict[str, Any] | None = None


@router.post("/{session_id}/corrections", status_code=202)
def correct(session: SessionDep, body: Correction, b: BusDep) -> dict[str, str]:
    if body.kind == "winner":
        if not body.rally_event_id or not body.winner:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "rally_event_id and winner are required")
        b.send_command(
            {
                "cmd": "correct_winner",
                "session_id": session.session_id,
                "rally_event_id": body.rally_event_id,
                "winner": body.winner,
            }
        )
    else:
        if not body.event_id:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "event_id is required")
        b.send_command(
            {
                "cmd": "verify_event",
                "session_id": session.session_id,
                "event_id": body.event_id,
                "payload": body.payload or {},
            }
        )
    return {"status": "accepted"}


# ---------------------------------------------------------------------- analytics
def _analytics(request: Request, session: Session):  # type: ignore[no-untyped-def]
    return request.app.state.analytics.get(session.session_id)


@router.get("/{session_id}/analytics")
def analytics(session: SessionDep, request: Request) -> dict[str, Any]:
    return _analytics(request, session).to_public()  # type: ignore[no-any-return]


@router.get("/{session_id}/heatmap")
def heatmap(
    session: SessionDep,
    request: Request,
    player: Annotated[str, Query(pattern="^P[12]$")],
    kind: Annotated[str, Query(pattern="^(presence|origin|landing|movement|targeting)$")] = "presence",
) -> dict[str, Any]:
    return _analytics(request, session).heatmaps.to_public(player, kind)  # type: ignore[no-any-return]


@router.get("/{session_id}/highlights")
def highlights(
    session: SessionDep,
    request: Request,
    k: Annotated[int, Query(ge=1, le=50)] = 10,
    player: Annotated[str | None, Query(pattern="^P[12]$")] = None,
    diversity: Annotated[float, Query(ge=0.0, le=0.9)] = 0.35,
) -> dict[str, Any]:
    hl = _analytics(request, session).highlights(k=k, player=player, diversity=diversity)
    return {"highlights": [h.to_public() for h in hl]}
