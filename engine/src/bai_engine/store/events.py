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
import logging
import sqlite3
import threading
from collections.abc import Callable, Iterable, Iterator
from contextlib import closing, contextmanager
from pathlib import Path

from bai_engine.schema.events import Event, EventStatus
from bai_engine.schema.state import StateSnapshot

log = logging.getLogger(__name__)

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
        self._commit_callbacks: list[list[Callable[[], None]]] = []
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

    def backup_to(self, path: Path) -> None:
        """Write a consistent SQLite snapshot, including uncheckpointed WAL data."""
        if path.exists():
            raise FileExistsError(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with self._lock, closing(sqlite3.connect(path)) as destination:
            self._conn.backup(destination)

    def __enter__(self) -> EventStore:
        return self

    def __exit__(self, *exc: object) -> None:
        self.close()

    @contextmanager
    def read_snapshot(self) -> Iterator[None]:
        """Read related projections from one committed SQLite revision.

        The connection lock excludes same-connection writers; the deferred WAL
        transaction also keeps separate connections' commits out of this read.
        Nested readers and readers inside a write transaction share its snapshot.
        """
        with self._lock:
            outer = not self._conn.in_transaction
            if outer:
                self._conn.execute("BEGIN")
            try:
                yield
            finally:
                if outer:
                    self._conn.execute("ROLLBACK")

    @contextmanager
    def transaction(self) -> Iterator[None]:
        """Commit one logical mutation, including nested event/snapshot writes.

        The writer lock covers the whole mutation. Nested callers use savepoints,
        so a rejected inner write cannot leak records or delivery callbacks into
        a successful outer transaction. Other SQLite connections see only the
        complete committed decision.
        """
        callbacks: list[Callable[[], None]] = []
        with self._lock:
            depth = len(self._commit_callbacks)
            if depth == 0 and self._conn.in_transaction:
                raise RuntimeError("Cannot write inside an event read snapshot")
            savepoint = f"event_store_{depth}"
            self._conn.execute("BEGIN IMMEDIATE" if depth == 0 else f"SAVEPOINT {savepoint}")
            self._commit_callbacks.append(callbacks)
            try:
                yield
                self._conn.execute("COMMIT" if depth == 0 else f"RELEASE SAVEPOINT {savepoint}")
            except BaseException:
                if self._conn.in_transaction:
                    if depth == 0:
                        self._conn.execute("ROLLBACK")
                    else:
                        self._conn.execute(f"ROLLBACK TO SAVEPOINT {savepoint}")
                        self._conn.execute(f"RELEASE SAVEPOINT {savepoint}")
                raise
            else:
                if depth:
                    self._commit_callbacks[-2].extend(callbacks)
            finally:
                self._commit_callbacks.pop()
        if depth == 0:
            for callback in callbacks:
                self._deliver(callback)

    @contextmanager
    def _tx(self) -> Iterator[sqlite3.Connection]:
        with self.transaction():
            yield self._conn

    def after_commit(self, callback: Callable[[], None]) -> None:
        """Notify only after durable publication; transport failure is retryable by replay."""
        with self._lock:
            if self._commit_callbacks:
                self._commit_callbacks[-1].append(callback)
                return
        self._deliver(callback)

    @staticmethod
    def _deliver(callback: Callable[[], None]) -> None:
        try:
            callback()
        except Exception:
            # The decision is already durable. Reporting persistence failure here
            # would invite a caller to award it again; the gateway replays the log.
            log.exception("event notification failed after commit; recover from the durable log")

    # ------------------------------------------------------------------ writes
    def append(self, event: Event) -> Event:
        return self.append_many([event])[0]

    def append_many(self, events: Iterable[Event]) -> list[Event]:
        out: list[Event] = []
        with self._tx() as conn:
            for ev in events:
                if ev.session_id != self.session_id:
                    raise ValueError(f"event for session {ev.session_id} appended to {self.session_id}")
                body = ev.model_dump_json(exclude={"seq"})
                existing = conn.execute("SELECT seq, body FROM events WHERE event_id=?", (ev.event_id,)).fetchone()
                if existing is not None:
                    if json.loads(existing["body"]) != json.loads(body):
                        raise ValueError(f"event identity conflict: {ev.event_id}")
                    out.append(ev.with_seq(int(existing["seq"])))
                    continue
                if ev.supersedes is not None:
                    row = conn.execute("SELECT 1 FROM events WHERE event_id=?", (ev.supersedes,)).fetchone()
                    if row is None:
                        raise KeyError(f"supersedes unknown event {ev.supersedes}")
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
        if snap.session_id != self.session_id:
            raise ValueError(f"state for session {snap.session_id} appended to {self.session_id}")
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
        if live_only:
            # Fold against the same SQLite snapshot that selects these rows.
            # A second superseder query can otherwise observe a newer correction
            # and discard the old row without having selected its replacement.
            clauses.extend(
                [
                    "status != ?",
                    "NOT EXISTS (SELECT 1 FROM events AS successor WHERE successor.supersedes=events.event_id)",
                ]
            )
            params.append(EventStatus.RETRACTED.value)
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        with self._lock:
            rows = self._conn.execute(f"SELECT seq, body FROM events {where} ORDER BY seq", params).fetchall()  # noqa: S608
        events = [self._row_to_event(r) for r in rows]
        if player_id is not None:
            events = [e for e in events if e.actors.player_id == player_id]
        return sorted(events, key=lambda e: (e.frame_start, e.seq or 0))

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
                "SELECT frame_idx, kind, event_seq, body FROM states "
                "WHERE id IN (SELECT MAX(id) FROM states WHERE kind=? GROUP BY frame_idx) ORDER BY frame_idx", (kind,)
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
