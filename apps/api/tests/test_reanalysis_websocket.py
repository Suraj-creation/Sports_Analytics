"""A live page must never mix event generations or query a closed event store."""

import msgpack
from fastapi.testclient import TestClient

from bai_api.app import create_app
from bai_engine.schema import Event, Provenance, Session, Source, SourceKind, StateSnapshot


def seed(repo, generation="new", count=3):
    session = repo.save(
        Session(
            title="Saved",
            source=Source(kind=SourceKind.UPLOAD, uri="local.mp4"),
            meta={"analysis_generation": generation},
        )
    )
    for i in range(count):
        repo.events(session.session_id).append(
            Event(
                session_id=session.session_id,
                type="stroke",
                frame_start=i,
                frame_end=i,
                pts_us=i,
                payload={"stroke": "unknown"},
                provenance=Provenance(model="test"),
            )
        )
    return session


def test_reconnect_replays_all_events_when_generation_changes(settings):
    from bai_engine.runtime.runner import EngineService

    with TestClient(create_app(settings, start_engine=False)) as client:
        repo = client.app.state.repo
        s = seed(repo, generation="old")
        service = EngineService(repo, client.app.state.bus, settings)
        service._reset_semantics(s.session_id)
        generation = repo.get(s.session_id).meta["analysis_generation"]
        assert generation and generation != "old"
        for i in range(3):
            repo.events(s.session_id).append(
                Event(
                    session_id=s.session_id,
                    type="stroke",
                    frame_start=i,
                    frame_end=i,
                    pts_us=i,
                    payload={"stroke": "unknown"},
                    provenance=Provenance(model="test"),
                )
            )
        with client.websocket_connect(f"/ws/sessions/{s.session_id}?last_seq=2&generation=old") as ws:
            hello = msgpack.unpackb(ws.receive_bytes())
            assert hello["type"] == "hello"
            assert hello["session"]["meta"]["analysis_generation"] == generation
            ws.send_json({"type": "seek", "frame": 2})
            events = msgpack.unpackb(ws.receive_bytes())
            assert events["type"] == "events"
            assert [e["seq"] for e in events["events"]] == [1, 2, 3]


def test_reconnect_clamps_old_cursor_for_legacy_session(settings):
    with TestClient(create_app(settings, start_engine=False)) as client:
        s = seed(client.app.state.repo, generation="", count=1)
        with client.websocket_connect(f"/ws/sessions/{s.session_id}?last_seq=100") as ws:
            ws.receive_bytes()
            ws.send_json({"type": "seek", "frame": 0})
            events = msgpack.unpackb(ws.receive_bytes())
            assert events["type"] == "events"
            assert len(events["events"]) == 1


def test_open_socket_seek_reads_new_store_after_reanalysis(settings):
    with TestClient(create_app(settings, start_engine=False)) as client:
        repo = client.app.state.repo
        s = seed(repo)
        with client.websocket_connect(f"/ws/sessions/{s.session_id}") as ws:
            ws.receive_bytes()
            ws.receive_bytes()
            repo.reset_analysis(s.session_id)
            repo.events(s.session_id).put_state(
                StateSnapshot(session_id=s.session_id, frame_idx=2, state={"marker": "new analysis"})
            )
            ws.send_json({"type": "seek", "frame": 2})
            response = msgpack.unpackb(ws.receive_bytes())
            assert response["type"] == "state_at"
            assert response["state"] == {"marker": "new analysis"}
