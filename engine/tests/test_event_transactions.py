"""Durable event batches, retry identity and committed-only delivery."""

import sqlite3
import threading
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

from bai_engine.schema import Event, EventStatus, Provenance, StateSnapshot
from bai_engine.store import EventStore


def point(frame: int = 30) -> Event:
    return Event(
        session_id="S1", type="point", frame_start=frame, frame_end=frame,
        pts_us=frame * 33333, status=EventStatus.CONFIRMED,
        provenance=Provenance(model="rule:test"), payload={"winner": "P1"},
    )


def test_identical_event_retry_preserves_sequence_and_one_row(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        original = point()
        saved = store.append(original)
        assert store.append(original) == saved
        assert store.append(saved) == saved
        assert store.count("point") == 1
        conflict = original.model_copy(update={"payload": {"winner": "P2"}})
        with pytest.raises(ValueError, match=r"event.*conflict"):
            store.append(conflict)
        assert store.since() == [saved]


def test_concurrent_identical_delivery_across_store_connections(tmp_path: Path) -> None:
    path = tmp_path / "events.sqlite"
    with EventStore(path, "S1") as first, EventStore(path, "S1") as second:
        event = point()
        barrier = threading.Barrier(2)

        def deliver(store: EventStore) -> Event:
            barrier.wait(timeout=5)
            return store.append(event)

        with ThreadPoolExecutor(max_workers=2) as workers:
            futures = [workers.submit(deliver, store) for store in (first, second)]
            saved = [future.result(timeout=10) for future in futures]
        assert saved[0] == saved[1]
        assert first.count("point") == 1


def test_point_and_snapshot_failure_roll_back_together_then_retry(tmp_path: Path) -> None:
    path = tmp_path / "events.sqlite"
    with EventStore(path, "S1") as store:
        with sqlite3.connect(path) as connection:
            connection.execute("CREATE TRIGGER fail_state BEFORE INSERT ON states "
                               "BEGIN SELECT RAISE(ABORT, 'snapshot unavailable'); END")
        event = point()
        delivered: list[Event] = []

        def decide() -> None:
            with store.transaction():
                saved = store.append(event)
                store.after_commit(lambda: delivered.append(saved))
                store.put_state(StateSnapshot(session_id="S1", frame_idx=30,
                                              event_seq=saved.seq, state={"score": {"P1": 1, "P2": 0}}))

        with pytest.raises(sqlite3.IntegrityError, match="snapshot unavailable"):
            decide()
        assert store.count() == 0
        assert store.state_at(30) is None
        assert delivered == []
        with sqlite3.connect(path) as connection:
            connection.execute("DROP TRIGGER fail_state")
        decide()
        assert len(delivered) == store.count() == 1
        snapshot = store.state_at(30)
        assert snapshot is not None and snapshot.event_seq == delivered[0].seq
    with EventStore(path, "S1") as reopened:
        assert reopened.count("point") == 1
        assert reopened.state_at(30).state["score"] == {"P1": 1, "P2": 0}


def test_reader_sees_whole_committed_batch_and_delivery_occurs_after_commit(tmp_path: Path) -> None:
    path = tmp_path / "events.sqlite"
    with EventStore(path, "S1") as writer, EventStore(path, "S1") as reader:
        delivered: list[int] = []
        with writer.transaction():
            writer.append(point())
            writer.after_commit(lambda: delivered.append(reader.count()))
            assert reader.count() == 0
            assert delivered == []
            writer.append(point(60))
        assert delivered == [2]
        assert reader.count("point") == 2


def test_nested_rollback_discards_events_and_notifications_only_from_savepoint(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        delivered: list[str] = []
        with store.transaction():
            store.append(point(30))
            store.after_commit(lambda: delivered.append("outer"))
            with pytest.raises(ValueError, match="reject inner"), store.transaction():
                store.append(point(60))
                store.after_commit(lambda: delivered.append("inner"))
                raise ValueError("reject inner")
            store.append(point(90))
        assert [event.frame_start for event in store.since()] == [30, 90]
        assert delivered == ["outer"]


def test_delivery_failure_does_not_report_committed_transaction_as_failed(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        def unavailable_bus() -> None:
            raise ConnectionError("bus unavailable")

        with store.transaction():
            store.append(point())
            store.after_commit(unavailable_bus)
        assert store.count("point") == 1


def test_snapshot_history_projection_uses_latest_revision_for_each_frame(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        for frame, score in ((30, [1, 0]), (60, [2, 0]), (30, [0, 1]), (60, [1, 1])):
            store.put_state(StateSnapshot(session_id="S1", frame_idx=frame, state={"score": score}))
        assert [snapshot.state["score"] for snapshot in store.states()] == [[0, 1], [1, 1]]
        assert store.state_at(45).state["score"] == [0, 1]


def test_read_snapshot_rejects_writes_and_releases_after_failure(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        original = store.append(point())
        with pytest.raises(RuntimeError, match="Cannot write"), store.read_snapshot():
            with store.read_snapshot():
                assert store.query() == [original]
            store.append(point(60))
        assert store.append(point(90)).seq == 2
        with store.transaction():
            store.append(point(120))
            with store.read_snapshot():
                assert store.count() == 3
        assert store.count() == 3


def test_live_query_cannot_mix_old_rows_with_new_superseders(tmp_path: Path, monkeypatch) -> None:
    with EventStore(tmp_path / "events.sqlite", "S1") as store:
        original = store.append(point())
        selected, release = threading.Event(), threading.Event()
        decode = store._row_to_event

        def paused_decode(row):
            result = decode(row)
            selected.set()
            assert release.wait(timeout=5)
            return result

        monkeypatch.setattr(store, "_row_to_event", paused_decode)
        with ThreadPoolExecutor(max_workers=1) as workers:
            query = workers.submit(store.query, types=["point"])
            try:
                assert selected.wait(timeout=5)
                with store.transaction():
                    replacement = store.append(original.correct(payload={"winner": "P2"}))
            finally:
                release.set()
            result = query.result(timeout=10)
        assert result in ([original], [replacement])
