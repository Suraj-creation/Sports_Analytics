"""Session catalogue (SQLite) and per-session storage layout on disk.

Layout under ``data_dir``::

    sessions.sqlite
    media/<sha256>/source.<ext>       content-addressed original
    media/<sha256>/proxy.mp4          CFR analysis + playback proxy
    media/<sha256>/hls/               fMP4 HLS (index.m3u8, init.mp4, seg_*.m4s)
    media/<sha256>/sprite.jpg         scrubber thumbnails (+ sprite.json)
    sessions/<id>/events.sqlite       event log + state snapshots
    sessions/<id>/tracks/             parquet track chunks
    sessions/<id>/exports/            generated reports, clips, csv
"""

from __future__ import annotations

import sqlite3
import threading
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from bai_engine.schema.session import Session, SessionStatus
from bai_engine.store.events import EventStore
from bai_engine.store.tracks import TrackStore


@dataclass(frozen=True)
class SessionPaths:
    root: Path

    @property
    def events_db(self) -> Path:
        return self.root / "events.sqlite"

    @property
    def tracks(self) -> Path:
        return self.root / "tracks"

    @property
    def exports(self) -> Path:
        return self.root / "exports"


@dataclass(frozen=True)
class MediaPaths:
    root: Path

    def source(self, ext: str) -> Path:
        return self.root / f"source{ext}"

    @property
    def proxy(self) -> Path:
        return self.root / "proxy.mp4"

    @property
    def hls(self) -> Path:
        return self.root / "hls"

    @property
    def playlist(self) -> Path:
        return self.hls / "index.m3u8"

    @property
    def sprite(self) -> Path:
        return self.root / "sprite.jpg"

    @property
    def sprite_meta(self) -> Path:
        return self.root / "sprite.json"

    @property
    def cuts(self) -> Path:
        return self.root / "cuts.json"

    @property
    def background_dir(self) -> Path:
        return self.root / "background"


class SessionRepository:
    def __init__(self, data_dir: Path | str) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "sessions").mkdir(exist_ok=True)
        (self.data_dir / "media").mkdir(exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.data_dir / "sessions.sqlite", check_same_thread=False, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute(
                "CREATE TABLE IF NOT EXISTS sessions (session_id TEXT PRIMARY KEY, created_at TEXT NOT NULL,"
                " status TEXT NOT NULL, body TEXT NOT NULL)"
            )
        self._event_stores: dict[str, EventStore] = {}
        self._track_stores: dict[str, TrackStore] = {}

    # ------------------------------------------------------------------ paths
    def paths(self, session_id: str) -> SessionPaths:
        if not session_id.isalnum():
            raise ValueError("invalid session id")
        return SessionPaths(self.data_dir / "sessions" / session_id)

    def media_paths(self, sha256: str) -> MediaPaths:
        if len(sha256) != 64 or not all(c in "0123456789abcdef" for c in sha256):
            raise ValueError("invalid media hash")
        return MediaPaths(self.data_dir / "media" / sha256)

    # ------------------------------------------------------------------ CRUD
    def save(self, session: Session) -> Session:
        session = session.model_copy(update={"updated_at": datetime.now(UTC)})
        with self._lock:
            self._conn.execute(
                "INSERT INTO sessions(session_id,created_at,status,body) VALUES(?,?,?,?) "
                "ON CONFLICT(session_id) DO UPDATE SET status=excluded.status, body=excluded.body",
                (session.session_id, session.created_at.isoformat(), session.status.value, session.model_dump_json()),
            )
        self.paths(session.session_id).root.mkdir(parents=True, exist_ok=True)
        return session

    def get(self, session_id: str) -> Session | None:
        with self._lock:
            row = self._conn.execute("SELECT body FROM sessions WHERE session_id=?", (session_id,)).fetchone()
        return None if row is None else Session.model_validate_json(row["body"])

    def list(self, limit: int = 200) -> list[Session]:
        with self._lock:
            rows = self._conn.execute("SELECT body FROM sessions ORDER BY created_at DESC LIMIT ?", (limit,)).fetchall()
        return [Session.model_validate_json(r["body"]) for r in rows]

    def update(self, session_id: str, **changes: object) -> Session:
        with self._lock:
            current = self.get(session_id)
            if current is None:
                raise KeyError(session_id)
            return self.save(current.model_copy(update=changes))

    def set_status(self, session_id: str, status: SessionStatus, detail: str | None = None) -> Session:
        return self.update(session_id, status=status, status_detail=detail)

    def delete(self, session_id: str) -> None:
        import shutil

        with self._lock:
            es = self._event_stores.pop(session_id, None)
            if es:
                es.close()
            self._track_stores.pop(session_id, None)
            self._conn.execute("DELETE FROM sessions WHERE session_id=?", (session_id,))
        shutil.rmtree(self.paths(session_id).root, ignore_errors=True)

    def reset_analysis(self, session_id: str) -> None:
        """Delete the event log and tracks of a session, keeping media and the perception cache."""
        import shutil

        with self._lock:
            es = self._event_stores.pop(session_id, None)
            if es:
                es.close()
            self._track_stores.pop(session_id, None)
        p = self.paths(session_id)
        for f in (p.events_db, Path(f"{p.events_db}-wal"), Path(f"{p.events_db}-shm")):
            f.unlink(missing_ok=True)
        shutil.rmtree(p.tracks, ignore_errors=True)
        self.update(session_id, frontier_frame=0, analysed_frames=0)

    # ------------------------------------------------------------------ stores
    def events(self, session_id: str) -> EventStore:
        with self._lock:
            if session_id not in self._event_stores:
                self._event_stores[session_id] = EventStore(self.paths(session_id).events_db, session_id)
            return self._event_stores[session_id]

    def tracks(self, session_id: str) -> TrackStore:
        with self._lock:
            if session_id not in self._track_stores:
                self._track_stores[session_id] = TrackStore(self.paths(session_id).tracks)
            return self._track_stores[session_id]

    def close(self) -> None:
        with self._lock:
            for es in self._event_stores.values():
                es.close()
            self._event_stores.clear()
            self._conn.close()
