"""Public export schema and HTTP/WebSocket failure projection contracts."""

import csv
import io

import msgpack
import pytest
from fastapi.testclient import TestClient

from bai_api.app import create_app
from bai_engine.bus import LocalBus, topic
from bai_engine.config import Settings
from bai_engine.schema import Event, EventStatus, MediaInfo, Provenance, Session, Source, SourceKind

COLUMNS = [
    "match_id",
    "game_id",
    "rally_id",
    "frame_start",
    "frame_end",
    "start_time",
    "end_time",
    "duration_s",
    "winner",
    "loser",
    "outcome",
    "shots",
    "n_shots",
    "score_P1",
    "score_P2",
    "score_available",
    "rally_event_id",
]
PRIVATE = "Analysis failed: /private/own-data/media/abc/source.mp4: moov atom not found"


@pytest.fixture
def client(tmp_path):
    settings = Settings(
        _env_file=None,
        data_dir=tmp_path / "data",
        models_dir=tmp_path / "models",
        profiles_dir=tmp_path / "profiles",
        bind_host="127.0.0.1",
        passphrase=None,
    )
    with TestClient(create_app(settings, bus=LocalBus(), start_engine=False)) as instance:
        yield instance


def seed(client, state="failed", *, media=False):
    return client.app.state.repo.save(
        Session(
            title="Controlled public contract",
            source=Source(kind=SourceKind.UPLOAD, uri="/private/own-data/source.mp4"),
            status=state,
            status_detail=PRIVATE if state == "failed" else "Analysing",
            media=MediaInfo(fps_num=30, fps_den=1, n_frames=90, width=320, height=180, duration_us=3_000_000)
            if media
            else None,
        )
    )


@pytest.mark.parametrize("state", ["created", "analysing", "failed", "analysed"])
def test_empty_application_csv_has_stable_public_columns(client, state):
    session = seed(client, state)
    response = client.get(f"/api/sessions/{session.session_id}/exports/rallies.csv")
    assert response.status_code == 200
    assert list(csv.reader(io.StringIO(response.text))) == [COLUMNS]


def test_nonempty_csv_preserves_times_unknown_score_and_private_field_exclusion(client):
    session = seed(client, "analysed", media=True)
    client.app.state.repo.events(session.session_id).append(
        Event(
            session_id=session.session_id,
            type="rally_end",
            frame_start=30,
            frame_end=60,
            pts_us=1_000_000,
            payload={"official": True, "rally_no": 1, "duration_s": 1.0, "winner": None, "shots": []},
            status=EventStatus.CONFIRMED,
            provenance=Provenance(model="controlled-contract"),
        )
    )
    response = client.get(f"/api/sessions/{session.session_id}/exports/rallies.csv")
    reader = csv.DictReader(io.StringIO(response.text))
    assert reader.fieldnames == COLUMNS
    row = next(reader)
    assert row["frame_start"] == "30" and row["frame_end"] == "60"
    assert row["start_time"] == "0:01.000" and row["end_time"] == "0:02.000"
    assert row["duration_s"] == "1.0"
    assert row["winner"] == row["score_P1"] == row["score_P2"] == ""
    assert row["score_available"] == "False"
    assert not any(key.startswith("_") for key in row)


def test_failure_is_sanitized_in_http_list_detail_and_summary_without_mutating_store(client):
    session = seed(client)
    sid = session.session_id
    for path in [f"/api/sessions/{sid}", "/api/sessions", f"/api/sessions/{sid}/exports/summary.json"]:
        response = client.get(path)
        assert response.status_code == 200
        assert "/private/" not in response.text
        assert "Detailed diagnostics are retained on the server" in response.text
    stored = client.app.state.repo.get(sid)
    assert stored.status_detail == PRIVATE
    assert stored.source.uri == "/private/own-data/source.mp4"


def test_healthy_public_status_preserves_useful_detail_and_redacts_only_source_uri(client):
    session = seed(client, "analysing", media=True)
    body = client.get(f"/api/sessions/{session.session_id}").json()
    assert body["status_detail"] == "Analysing"
    assert body["source"]["uri"] == ""
    assert body["media"]["n_frames"] == 90


def test_binary_websocket_failed_hello_is_sanitized(client):
    session = seed(client)
    sid = session.session_id
    with client.websocket_connect(f"/ws/sessions/{sid}") as ws:
        hello = msgpack.unpackb(ws.receive_bytes(), raw=False)
        assert hello["type"] == "hello"
        assert "/private/" not in hello["session"]["status_detail"]


def test_binary_websocket_live_failure_is_sanitized_even_after_a_healthy_hello(client):
    session = seed(client, "analysing", media=True)
    sid = session.session_id
    with client.websocket_connect(f"/ws/sessions/{sid}") as ws:
        assert msgpack.unpackb(ws.receive_bytes(), raw=False)["type"] == "hello"
        message = {"type": "status", "status": "failed", "detail": PRIVATE, "frontier_frame": 0, "analysed_frames": 0}
        client.app.state.bus.publish(topic(sid, "status"), message)
        status = msgpack.unpackb(ws.receive_bytes(), raw=False)
        assert status["type"] == "status"
        assert "/private/" not in status["detail"]
        assert "Detailed diagnostics are retained on the server" in status["detail"]
        assert message["detail"] == PRIVATE


def test_binary_websocket_running_status_and_frame_identity_are_unchanged(client):
    session = seed(client, "analysing", media=True)
    with client.websocket_connect(f"/ws/sessions/{session.session_id}") as ws:
        assert msgpack.unpackb(ws.receive_bytes(), raw=False)["type"] == "hello"
        message = {
            "type": "status",
            "status": "analysing",
            "detail": "Analysing",
            "frontier_frame": 29,
            "analysed_frames": 30,
        }
        client.app.state.bus.publish(topic(session.session_id, "status"), message)
        status = msgpack.unpackb(ws.receive_bytes(), raw=False)
        assert all(status[key] == value for key, value in message.items())
