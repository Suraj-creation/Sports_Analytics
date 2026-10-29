import json

import msgpack
from fastapi.testclient import TestClient

from bai_api.app import create_app
from bai_engine.config import REPO_ROOT, Settings
from bai_engine.schema import Event, Provenance, Session, Source, SourceKind, TrackObject, TrackSample, samples_to_table


def seed(repo, count=3):
    session = repo.save(Session(title="Wire regression", source=Source(kind=SourceKind.UPLOAD, uri="fixture")))
    append(repo, session.session_id, count)
    return session.session_id


def append(repo, sid, count):
    return repo.events(sid).append_many(
        [
            Event(
                session_id=sid,
                type="contact",
                frame_start=i,
                frame_end=i,
                pts_us=i * 33333,
                provenance=Provenance(model="transport-fixture"),
            )
            for i in range(count)
        ]
    )


def receive(ws):
    return msgpack.unpackb(ws.receive_bytes(), raw=False)


def test_backlog_pages_are_not_a_total_limit(settings: Settings, monkeypatch):
    monkeypatch.setattr("bai_api.ws.MAX_BACKLOG", 2)
    with TestClient(create_app(settings, start_engine=False)) as client:
        sid = seed(client.app.state.repo, 7)
        with client.websocket_connect(f"/ws/sessions/{sid}?analysis_revision=0") as ws:
            assert receive(ws)["type"] == "hello"
            pages = [receive(ws) for _ in range(4)]
            assert [event["seq"] for page in pages for event in page["events"]] == list(range(1, 8))


def test_open_socket_recovers_replaced_store_and_replays_new_generation(settings: Settings):
    with TestClient(create_app(settings, start_engine=False)) as client:
        repo = client.app.state.repo
        sid = seed(repo)
        with client.websocket_connect(f"/ws/sessions/{sid}?analysis_revision=0") as ws:
            assert receive(ws)["analysis_revision"] == 0
            assert len(receive(ws)["events"]) == 3
            repo.reset_analysis(sid)
            repo.update(sid, meta={"analysis_revision": 1})
            fresh = append(repo, sid, 2)
            ws.send_bytes(msgpack.packb({"type": "seek", "frame": 0}))
            hello = receive(ws)
            assert hello["type"] == "hello" and hello["reset"] and hello["analysis_revision"] == 1
            page = receive(ws)
            assert [e["event_id"] for e in page["events"]] == [e.event_id for e in fresh]
            assert receive(ws)["type"] == "state_at"  # No closed SQLite exception.


def test_stale_reconnect_cursor_cannot_skip_new_analysis(settings: Settings):
    with TestClient(create_app(settings, start_engine=False)) as client:
        repo = client.app.state.repo
        sid = seed(repo)
        repo.update(sid, meta={"analysis_revision": 2})
        with client.websocket_connect(f"/ws/sessions/{sid}?analysis_revision=1&last_seq=2") as ws:
            assert receive(ws)["reset"]
            assert [e["seq"] for e in receive(ws)["events"]] == [1, 2, 3]


def test_real_anonymous_tracks_reach_rest_response(settings: Settings):
    fixture = json.loads((REPO_ROOT / "engine/tests/fixtures/anonymous_real_tracks.json").read_text())
    samples = [TrackSample.model_validate(row) for row in fixture["samples"]]
    with TestClient(create_app(settings, start_engine=False)) as client:
        repo = client.app.state.repo
        sid = seed(repo)
        repo.tracks(sid).write_chunk(TrackObject.PLAYER, 10200, 10201, samples_to_table(samples))
        response = client.get(f"/api/sessions/{sid}/tracks?from=10200&to=10201")
        body = msgpack.unpackb(response.content, raw=False)
        assert response.headers["X-Analysis-Revision"] == "0"
        assert sum(len(p["f"]) for p in body["anonymous"].values()) == 4
        assert all(len(p["k"]) == 102 for p in body["anonymous"].values())
        assert client.get(f"/api/sessions/{sid}/tracks?from=2&to=1").status_code == 422
