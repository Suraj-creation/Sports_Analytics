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
from bai_api.public import public_session
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
    send_lock = asyncio.Lock()
    sync_lock = asyncio.Lock()
    initialized = asyncio.Event()
    fps = float(session.media.fps) if session.media else 30.0
    revision = int(session.meta.get("analysis_revision", 0))

    def query_int(name: str, default: int) -> int:
        try:
            return int(ws.query_params.get(name, str(default)))
        except (ValueError, TypeError):
            return default

    requested_revision = query_int("analysis_revision", -1)
    sent_seq = max(0, query_int("last_seq", 0)) if requested_revision == revision else 0

    async def send(msg: dict[str, Any]) -> None:
        async with send_lock:
            await ws.send_bytes(_pack(msg))

    async def sync_events(*, hello: bool = False) -> None:
        """Replay durable pages, recovering queue gaps and replaced analysis logs."""
        nonlocal sent_seq, revision, fps
        async with sync_lock:
            while True:
                try:
                    with repo.analysis_snapshot(session_id) as (current, store, _):
                        current_revision = int(current.meta.get("analysis_revision", 0))
                        last_seq = store.last_seq()
                        reset = current_revision != revision or sent_seq > last_seq
                        if reset:
                            sent_seq = 0
                        revision = current_revision
                        fps = float(current.media.fps) if current.media else 30.0
                        greeting = None
                        if hello or reset:
                            snap = store.state_at(10**12)
                            cal = store.query(types=["calibration"])
                            greeting = {
                                "type": "hello",
                                "session": public_session(current).model_dump(mode="json"),
                                "state": snap.state if snap else None,
                                "calibration": cal[-1].payload if cal else None,
                                "last_seq": last_seq,
                                "analysis_revision": revision,
                                "reset": reset or (hello and requested_revision != revision),
                            }
                        page = store.since(sent_seq, limit=min(500, MAX_BACKLOG)) if sent_seq < last_seq else []
                        page = [e for e in page if (e.seq or 0) <= last_seq]
                except KeyError:
                    return
                # Never hold the repository lock across network awaits. A new
                # generation is detected before reading each successive page.
                if greeting is not None:
                    await send(greeting)
                if not page:
                    return
                await send(
                    {
                        "type": "events",
                        "events": [e.model_dump(mode="json") for e in page],
                        "backlog": hello or reset,
                        "analysis_revision": revision,
                    }
                )
                sent_seq = page[-1].seq or sent_seq
                hello = False

    async def forward(name: str) -> None:
        async for message in bus.subscribe(topic(session_id, name)):
            await initialized.wait()
            # Log entries are replayed from storage so a dropped bus packet cannot
            # permanently lose events while the connection stays open.
            await sync_events()
            if name == "events":
                continue
            incoming_revision = message.get("analysis_revision", revision)
            if incoming_revision != revision:
                continue
            await send({**message, "analysis_revision": revision})

    async def track_window(a: int, b: int, *, center: int | None = None) -> None:
        await sync_events()
        try:
            with repo.analysis_snapshot(session_id) as (current, store, tracks):
                captured_revision = int(current.meta.get("analysis_revision", 0))
                b = min(b, current.frontier_frame)
                payload = None
                if current.analysed_frames > 0 and a <= b:
                    table = tracks.read([TrackObject.SHUTTLE, TrackObject.PLAYER, TrackObject.CAMERA], a, b)
                    payload = encode_tracks(table_to_samples(table), a, b)
                snap = store.state_at(center) if center is not None else None
        except KeyError:
            return
        if captured_revision != revision:
            # Announce a reset before responding to any new-generation window.
            await sync_events()
            return
        if payload is not None:
            await send(
                {
                    "type": "tracks",
                    "from": a,
                    "to": b,
                    "bin": payload,
                    "analysis_revision": captured_revision,
                }
            )
        if center is not None:
            await send(
                {
                    "type": "state_at",
                    "frame": center,
                    "state": snap.state if snap else None,
                    "analysis_revision": captured_revision,
                }
            )

    tasks = [asyncio.create_task(forward(t)) for t in TOPICS]
    last_playhead_sent = 0.0
    try:
        # Install subscriptions before the backlog snapshot; their queues hold
        # messages arriving while the initial durable replay is sent.
        await asyncio.sleep(0)
        await sync_events(hello=True)
        initialized.set()
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
            try:
                frame = max(0, int(msg.get("frame", 0) or 0))
                a, b = int(msg.get("from", 0)), int(msg.get("to", 0))
            except (TypeError, ValueError, OverflowError):
                continue
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
                await track_window(
                    max(0, frame - int(WINDOW_BEFORE_S * fps)), frame + int(WINDOW_AFTER_S * fps), center=frame
                )
            elif kind == "tracks" and 0 <= a <= b and b - a <= 60 * fps:
                await track_window(a, b)
    except WebSocketDisconnect:
        pass
    finally:
        WS_CLIENTS.dec()
        for t in tasks:
            t.cancel()
        for t in tasks:
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await t
