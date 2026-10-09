"""WebSocket gateway ``/ws/sessions/{id}`` — live analysis for one session.

Frames are msgpack maps (binary WebSocket messages), each with a ``type``:

server → client
  ``hello``     session, media, current state, calibration, last event seq
  ``events``    appended events (backlog since the client's ``last_seq`` first, then live)
  ``tracks``    columnar track window ``{from, to, bin}`` (see :mod:`bai_engine.wire`)
  ``status``    analysis status / frontier / speed / degradations
  ``state``     match state + analytics summary
  ``reply``     command results (e.g. calibration)

client → server
  ``playhead``  ``{frame, playing}`` — throttled and forwarded to the engine (seek priority)
  ``seek``      ``{frame}`` — server answers with the stored track window and state at that frame
  ``tracks``    ``{from, to}`` — explicit window request (e.g. scrubbing)
"""

from __future__ import annotations

import asyncio
import contextlib
import time
from typing import Any

import msgpack
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from bai_api.auth import ws_user
from bai_engine.bus import Bus, topic
from bai_engine.obs import WS_CLIENTS, get_logger
from bai_engine.schema import TrackObject, table_to_samples
from bai_engine.store import SessionRepository
from bai_engine.wire import encode_tracks

log = get_logger(__name__)
router = APIRouter()
TOPICS = ("events", "tracks", "status", "state", "replies")
MAX_BACKLOG = 20_000
WINDOW_BEFORE_S = 2.0
WINDOW_AFTER_S = 12.0


def _pack(msg: dict[str, Any]) -> bytes:
    out = msgpack.packb(msg, use_bin_type=True, default=str)
    assert isinstance(out, bytes)
    return out


@router.websocket("/ws/sessions/{session_id}")
async def session_ws(ws: WebSocket, session_id: str) -> None:
    if ws_user(ws) is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    repo: SessionRepository = ws.app.state.repo
    bus: Bus = ws.app.state.bus
    session = repo.get(session_id) if session_id.isalnum() else None
    if session is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await ws.accept()
    WS_CLIENTS.inc()
    store = repo.events(session_id)
    fps = float(session.media.fps) if session.media else 30.0
    send_lock = asyncio.Lock()

    async def send(msg: dict[str, Any]) -> None:
        async with send_lock:
            await ws.send_bytes(_pack(msg))

    try:
        last_seq = int(ws.query_params.get("last_seq", "0") or 0)
    except ValueError:
        last_seq = 0
    snap = store.state_at(10**12)
    cal = store.query(types=["calibration"])
    await send(
        {
            "type": "hello",
            "session": session.model_dump(mode="json"),
            "state": snap.state if snap else None,
            "calibration": cal[-1].payload if cal else None,
            "last_seq": store.last_seq(),
        }
    )
    backlog = store.since(last_seq, limit=MAX_BACKLOG)
    for i in range(0, len(backlog), 500):
        await send(
            {"type": "events", "events": [e.model_dump(mode="json") for e in backlog[i : i + 500]], "backlog": True}
        )

    async def forward(name: str) -> None:
        async for m in bus.subscribe(topic(session_id, name)):
            await send(m)

    async def track_window(center: int) -> None:
        a = max(0, center - int(WINDOW_BEFORE_S * fps))
        b = center + int(WINDOW_AFTER_S * fps)
        table = repo.tracks(session_id).read([TrackObject.SHUTTLE, TrackObject.PLAYER], a, b)
        if table.num_rows:
            await send({"type": "tracks", "from": a, "to": b, "bin": encode_tracks(table_to_samples(table), a, b)})
        snap = store.state_at(center)
        await send({"type": "state_at", "frame": center, "state": snap.state if snap else None})

    tasks = [asyncio.create_task(forward(t)) for t in TOPICS]
    last_playhead_sent = 0.0
    try:
        while True:
            raw = await ws.receive()
            if raw["type"] == "websocket.disconnect":
                break
            data = raw.get("bytes") or raw.get("text")
            if data is None:
                continue
            try:
                msg = msgpack.unpackb(data, raw=False) if isinstance(data, bytes) else __import__("json").loads(data)
            except (ValueError, TypeError, msgpack.ExtraData, msgpack.FormatError, msgpack.StackError):
                log.debug("ws.bad_frame", session=session_id)
                continue
            if not isinstance(msg, dict):
                continue
            kind = msg.get("type")
            frame = int(msg.get("frame", 0) or 0)
            if kind == "playhead":
                now = time.monotonic()
                if now - last_playhead_sent > 0.25:
                    bus.send_command(
                        {
                            "cmd": "playhead",
                            "session_id": session_id,
                            "frame": frame,
                            "playing": bool(msg.get("playing")),
                        }
                    )
                    last_playhead_sent = now
            elif kind == "seek":
                bus.send_command({"cmd": "playhead", "session_id": session_id, "frame": frame, "playing": False})
                await track_window(frame)
            elif kind == "tracks":
                a, b = int(msg.get("from", 0)), int(msg.get("to", 0))
                if 0 <= a <= b and b - a <= 60 * fps:
                    table = repo.tracks(session_id).read([TrackObject.SHUTTLE, TrackObject.PLAYER], a, b)
                    await send(
                        {"type": "tracks", "from": a, "to": b, "bin": encode_tracks(table_to_samples(table), a, b)}
                    )
    except WebSocketDisconnect:
        pass
    finally:
        WS_CLIENTS.dec()
        for t in tasks:
            t.cancel()
        for t in tasks:
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await t
