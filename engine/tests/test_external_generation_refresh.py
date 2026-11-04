"""Independent repository handles must follow a completed analysis generation reset."""

from contextlib import contextmanager

import pytest

from bai_engine.schema import Event, Provenance, Session, Source, SourceKind
from bai_engine.store import SessionRepository


def test_reader_reopens_event_store_after_other_repository_resets_analysis(tmp_path):
    writer, reader = SessionRepository(tmp_path), SessionRepository(tmp_path)
    try:
        session = writer.save(Session(title="Separate handles", source=Source(kind=SourceKind.UPLOAD, uri="fixture")))
        sid = session.session_id

        def event(value):
            return Event(session_id=sid, type="diagnostic", frame_start=0, frame_end=0, pts_us=0,
                         payload={"value": value}, provenance=Provenance(model="controlled_fixture"))

        writer.events(sid).append(event("before"))
        with reader.analysis_snapshot(sid) as (_, store, _):
            assert store.since()[0].payload == {"value": "before"}
        writer.reset_analysis(sid)
        writer.events(sid).append(event("after"))
        with reader.analysis_snapshot(sid) as (current, store, _):
            assert current.meta["analysis_generation"] == writer.get(sid).meta["analysis_generation"]
            assert [row.payload for row in store.since()] == [{"value": "after"}]
    finally:
        reader.close()
        writer.close()


@pytest.fixture
def generation_pair(tmp_path):
    writer, reader = SessionRepository(tmp_path), SessionRepository(tmp_path)
    session = writer.save(Session(title="Snapshot race", source=Source(kind=SourceKind.UPLOAD, uri="fixture")))
    sid = session.session_id

    def append(value):
        writer.events(sid).append(Event(
            session_id=sid,
            type="diagnostic",
            frame_start=0,
            frame_end=0,
            pts_us=0,
            payload={"value": value},
            provenance=Provenance(model="controlled_fixture"),
        ))

    append("before")
    # Establish an old-generation handle in the independent reader.
    assert reader.events(sid).since()[0].payload == {"value": "before"}

    def reset():
        writer.reset_analysis(sid)
        append("after")

    try:
        yield writer, reader, sid, reset
    finally:
        reader.close()
        writer.close()


def snapshot_rows_or_explicit_generation_refusal(reader, sid):
    """A crossing may retry or refuse before exposing a mixed/closed snapshot."""
    observed = []
    try:
        with reader.analysis_snapshot(sid) as (session, store, _):
            observed.append((
                str(session.meta.get("analysis_generation") or ""),
                [row.payload["value"] for row in store.since()],
            ))
    except RuntimeError as exc:
        assert not observed, "Generation crossing was detected only after exposing a snapshot"
        assert "generation" in str(exc).lower(), "Refusal must identify the generation conflict"
    return observed


def test_reset_after_metadata_read_cannot_mix_session_and_event_generations(generation_pair, monkeypatch):
    writer, reader, sid, reset = generation_pair
    original_get = reader.get
    crossed = False

    def get_then_reset(session_id):
        nonlocal crossed
        session = original_get(session_id)
        if not crossed:
            crossed = True
            reset()
        return session

    monkeypatch.setattr(reader, "get", get_then_reset)
    observed = snapshot_rows_or_explicit_generation_refusal(reader, sid)
    assert crossed
    # The reset completes before any event snapshot is acquired, so a successful
    # retry must expose the new session metadata and the new event rows together.
    assert not observed or observed == [(writer.get(sid).meta["analysis_generation"], ["after"])]


def test_reset_before_track_acquisition_cannot_close_the_active_event_snapshot(generation_pair, monkeypatch):
    writer, reader, sid, reset = generation_pair
    old_generation = str(reader.get(sid).meta.get("analysis_generation") or "")
    store = reader.events(sid)
    original_snapshot = store.read_snapshot
    crossed = False

    @contextmanager
    def read_then_reset():
        nonlocal crossed
        with original_snapshot():
            # Pin the old WAL read revision before another repository replaces
            # the files. The baseline next calls tracks(), refreshes generation
            # again and closes this same active EventStore.
            assert [row.payload["value"] for row in store.since()] == ["before"]
            if not crossed:
                crossed = True
                reset()
            yield

    monkeypatch.setattr(store, "read_snapshot", read_then_reset)
    observed = snapshot_rows_or_explicit_generation_refusal(reader, sid)
    assert crossed
    new_generation = writer.get(sid).meta["analysis_generation"]
    assert not observed or observed in (
        [(old_generation, ["before"])],
        [(new_generation, ["after"])],
    )
