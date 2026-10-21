"""Append-only event log and state snapshots for one session (SQLite, WAL mode).

Design notes
------------
* ``seq`` is a per-session monotonic integer assigned on append.  Clients resume WebSocket
  streams with ``last_seq`` and the UI folds deltas in order.
* Events are never updated or deleted; corrections are appended (see
  :func:`bai_engine.schema.events.current_view`).
* The store is safe for one writer (the temporal engine) and many readers (API, agents) across
  threads; SQLite WAL gives readers a consistent snapshot without blocking the writer.
"""

from __future__ import annotations

import json
import sqlite3
import threading
from collections.abc import Iterable, Iterator
from contextlib import contextmanager
from pathlib import Path

from bai_engine.schema.events import Event, EventStatus, current_view
from bai_engine.schema.state import StateSnapshot

_SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    seq          INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id     TEXT NOT NULL UNIQUE,
    type         TEXT NOT NULL,
    frame_start  INTEGER NOT NULL,
    frame_end    INTEGER NOT NULL,
    status       TEXT NOT NULL,
    supersedes   TEXT,
    player_id    TEXT,
    body         TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_events_type_frame ON events(type, frame_start);
CREATE INDEX IF NOT EXISTS ix_events_frame ON events(frame_start);
CREATE INDEX IF NOT EXISTS ix_events_supersedes ON events(supersedes);

CREATE TABLE IF NOT EXISTS states (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    frame_idx  INTEGER NOT NULL,
    kind       TEXT NOT NULL,
    event_seq  INTEGER,
    body       TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_states_kind_frame ON states(kind, frame_idx);

CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


class EventStore:
    def __init__(self, path: Path | str, session_id: str) -> None:
        self.path = Path(path)
        self.session_id = session_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(self.path, check_same_thread=False, isolation_level=None, timeout=30)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")
            self._conn.execute("PRAGMA foreign_keys=ON")
            self._conn.executescript(_SCHEMA)

    # ------------------------------------------------------------------ lifecycle
    def close(self) -> None:
        with self._lock:
            self._conn.close()

    def __enter__(self) -> EventStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with self._lock:
            self._conn.execute("BEGIN IMMEDIATE")
            try:
                yield self._conn
            except BaseException:
                self._conn.execute("ROLLBACK")
                raise
            else:
                self._conn.execute("COMMIT")

    # ------------------------------------------------------------------ writes
    def append(self, event: Event) -> Event:
        return self.append_many([event])[0]

    def append_many(self, events: Iterable[Event]) -> list[Event]:
        out: list[Event] = []
        with self._tx() as conn:
            for ev in events:
                if ev.session_id != self.session_id:
                    raise ValueError(f"event for session {ev.session_id} appended to {self.session_id}")
                if ev.supersedes is not None:
                    row = conn.execute("SELECT 1 FROM events WHERE event_id=?", (ev.supersedes,)).fetchone()
                    if row is None:
                        raise KeyError(f"supersedes unknown event {ev.supersedes}")
                body = ev.model_dump_json(exclude={"seq"})
                cur = conn.execute(
                    "INSERT INTO events(event_id,type,frame_start,frame_end,status,supersedes,player_id,body)"
                    " VALUES (?,?,?,?,?,?,?,?)",
                    (
                        ev.event_id,
                        ev.type,
                        ev.frame_start,
                        ev.frame_end,
                        ev.status.value,
                        ev.supersedes,
                        ev.actors.player_id,
                        body,
                    ),
                )
                seq = cur.lastrowid
                assert seq is not None
                out.append(ev.with_seq(seq))
        return out

    def put_state(self, snap: StateSnapshot) -> None:
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO states(frame_idx,kind,event_seq,body) VALUES (?,?,?,?)",
                (snap.frame_idx, snap.kind, snap.event_seq, json.dumps(snap.state)),
            )

    def set_meta(self, key: str, value: str) -> None:
        with self._tx() as conn:
            conn.execute(
                "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    def get_meta(self, key: str) -> str | None:
        with self._lock:
            row = self._conn.execute("SELECT value FROM meta WHERE key=?", (key,)).fetchone()
        return None if row is None else str(row["value"])

    # ------------------------------------------------------------------ reads
    @staticmethod
    def _row_to_event(row: sqlite3.Row) -> Event:
        ev = Event.model_validate_json(row["body"])
        return ev.with_seq(int(row["seq"]))

    def since(self, last_seq: int = 0, limit: int = 10_000) -> list[Event]:
        """Raw log entries with ``seq > last_seq`` in order (for streaming deltas)."""
        with self._lock:
            rows = self._conn.execute(
                "SELECT seq, body FROM events WHERE seq > ? ORDER BY seq LIMIT ?", (last_seq, limit)
            ).fetchall()
        return [self._row_to_event(r) for r in rows]

    def last_seq(self) -> int:
        with self._lock:
            row = self._conn.execute("SELECT COALESCE(MAX(seq), 0) AS s FROM events").fetchone()
        return int(row["s"])

    def get(self, event_id: str) -> Event | None:
        with self._lock:
            row = self._conn.execute("SELECT seq, body FROM events WHERE event_id=?", (event_id,)).fetchone()
        return None if row is None else self._row_to_event(row)

    def query(
        self,
        *,
        types: Iterable[str] | None = None,
        frame_from: int | None = None,
        frame_to: int | None = None,
        player_id: str | None = None,
        live_only: bool = True,
    ) -> list[Event]:
        """Events overlapping ``[frame_from, frame_to]``; ``live_only`` folds corrections."""
        clauses: list[str] = []
        params: list[object] = []
        if types is not None:
            t = list(types)
            if not t:
                return []
            clauses.append(f"type IN ({','.join('?' * len(t))})")
            params.extend(t)
        if frame_from is not None:
            clauses.append("frame_end >= ?")
            params.append(frame_from)
        if frame_to is not None:
            clauses.append("frame_start <= ?")
            params.append(frame_to)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._lock:
            rows = self._conn.execute(f"SELECT seq, body FROM events {where} ORDER BY seq", params).fetchall()  # noqa: S608
        events = [self._row_to_event(r) for r in rows]
        if live_only:
            events = self._fold(events)
        if player_id is not None:
            events = [e for e in events if e.actors.player_id == player_id]
        return sorted(events, key=lambda e: (e.frame_start, e.seq or 0))

    def _fold(self, events: list[Event]) -> list[Event]:
        # A superseding event may fall outside the filtered window; look up successors globally.
        if not events:
            return events
        ids = [e.event_id for e in events]
        with self._lock:
            succ_rows = self._conn.execute(
                f"SELECT supersedes FROM events WHERE supersedes IN ({','.join('?' * len(ids))})",  # noqa: S608 - placeholders only
                ids,
            ).fetchall()
        superseded = {r["supersedes"] for r in succ_rows}
        return [e for e in current_view(events) if e.event_id not in superseded and e.status != EventStatus.RETRACTED]

    def all_live(self) -> list[Event]:
        return self.query()

    def state_at(self, frame_idx: int, kind: str = "match") -> StateSnapshot | None:
        """Latest snapshot at or before ``frame_idx`` (used for seek recovery)."""
        with self._lock:
            row = self._conn.execute(
                "SELECT frame_idx, kind, event_seq, body FROM states WHERE kind=? AND frame_idx<=? "
                "ORDER BY frame_idx DESC, id DESC LIMIT 1",
                (kind, frame_idx),
            ).fetchone()
        if row is None:
            return None
        return StateSnapshot(
            session_id=self.session_id,
            frame_idx=int(row["frame_idx"]),
            kind=str(row["kind"]),
            event_seq=row["event_seq"],
            state=json.loads(row["body"]),
        )

    def states(self, kind: str = "match") -> list[StateSnapshot]:
        with self._lock:
            rows = self._conn.execute(
                "SELECT frame_idx, kind, event_seq, body FROM states WHERE kind=? ORDER BY frame_idx, id", (kind,)
            ).fetchall()
        return [
            StateSnapshot(
                session_id=self.session_id,
                frame_idx=int(r["frame_idx"]),
                kind=str(r["kind"]),
                event_seq=r["event_seq"],
                state=json.loads(r["body"]),
            )
            for r in rows
        ]

    def count(self, type_: str | None = None) -> int:
        with self._lock:
            if type_ is None:
                row = self._conn.execute("SELECT COUNT(*) AS n FROM events").fetchone()
            else:
                row = self._conn.execute("SELECT COUNT(*) AS n FROM events WHERE type=?", (type_,)).fetchone()
        return int(row["n"])
