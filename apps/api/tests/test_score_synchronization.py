"""Controlled observations → decision → durable log → REST/WS → app recreation."""

import time
from types import SimpleNamespace

import msgpack
import pytest
from fastapi.testclient import TestClient

from apps.web.e2e.score_fixture import create_score_fixture
from bai_api.app import create_app
from bai_engine.config import Settings
from bai_engine.schema import Event, Provenance, Session, Source, SourceKind


@pytest.mark.parametrize(
    "event_type", ["point", "rally_end", "match_phase", "game_end", "match_end", "side_switch", "interval"]
)
def test_generic_verification_cannot_bypass_score_refold(client: TestClient, monkeypatch, event_type: str) -> None:
    session = client.app.state.repo.save(Session(title="Review", source=Source(kind=SourceKind.UPLOAD, uri="none")))
    store = client.app.state.repo.events(session.session_id)
    event = store.append(Event(session_id=session.session_id, type=event_type, frame_start=10, frame_end=10,
                               pts_us=333333, payload={"winner": "P1"}, provenance=Provenance(model="rule:test")))
    commands = []
    monkeypatch.setattr(client.app.state.bus, "send_command", commands.append)
    result = client.post(f"/api/sessions/{session.session_id}/corrections", json={
        "kind": "verify", "event_id": event.event_id, "payload": {"winner": "P2"},
    })
    assert result.status_code == 422
    assert commands == []
    assert store.count() == 1


def test_internal_generic_verification_cannot_change_a_point(client: TestClient) -> None:
    from bai_badminton.plugin import BadmintonSession

    session = client.app.state.repo.save(Session(title="Review", source=Source(kind=SourceKind.UPLOAD, uri="none")))
    store = client.app.state.repo.events(session.session_id)
    event = store.append(Event(session_id=session.session_id, type="point", frame_start=10, frame_end=10,
                               pts_us=333333, payload={"winner": "P1"}, provenance=Provenance(model="rule:test")))
    plugin = object.__new__(BadmintonSession)
    plugin.store = store
    plugin.engine = SimpleNamespace(on_superseded=lambda event: None)
    plugin._emit = lambda events: None
    result = plugin.handle({"cmd": "verify_event", "event_id": event.event_id, "payload": {"winner": "P2"}})
    assert result["ok"] is False
    assert store.count() == 1


def test_score_decision_correction_realtime_and_process_reload(settings: Settings) -> None:
    with TestClient(create_app(settings)) as client:
        fixture = create_score_fixture(client.app.state.repo, settings.profile, media=True)
        sid = fixture["session_id"]
        base = f"/api/sessions/{sid}"
        assert fixture["score"] == {"P1": 1, "P2": 1}
        assert len(fixture["rally_event_ids"]) == 2
        initial = client.get(f"{base}/state").json()
        assert initial["state"]["score"] == fixture["score"]
        events = client.get(f"{base}/events").json()
        initial_seq = events["last_seq"]
        with client.websocket_connect(f"/ws/sessions/{sid}?last_seq={initial_seq}&analysis_revision=0") as ws:
            hello = msgpack.unpackb(ws.receive_bytes())
            assert hello["type"] == "hello" and hello["state"]["score"] == fixture["score"]
            response = client.post(f"{base}/corrections", json={
                "kind": "winner", "rally_event_id": fixture["rally_event_ids"][1], "winner": "P1",
            })
            assert response.status_code == 202
            deadline = time.monotonic() + 15
            while time.monotonic() < deadline:
                current = client.get(f"{base}/state").json()
                if current["state"]["score"] == {"P1": 2, "P2": 0}:
                    break
                time.sleep(0.05)
            else:
                raise AssertionError("correction was not durably reflected in state")
            # A seek drains the durable backlog even if a pub/sub hint is lost.
            ws.send_bytes(msgpack.packb({"type": "seek", "frame": fixture["frame"]}))
            changed, delivered = False, []
            for _ in range(30):
                message = msgpack.unpackb(ws.receive_bytes())
                if message["type"] == "events":
                    assert message["analysis_revision"] == 0
                    delivered.extend(message["events"])
                if message["type"] == "state_at":
                    assert message["state"]["score"] == {"P1": 2, "P2": 0}
                    changed = True
                    break
            assert changed
            assert any(event["type"] == "point" and event["status"] == "retracted" for event in delivered)
            assert any(event["type"] == "point" and event["payload"].get("state_after", {}).get("score")
                       == {"P1": 2, "P2": 0} for event in delivered)
        live = client.get(f"{base}/events?types=point").json()["events"]
        assert len(live) == 2 and all(event["payload"]["winner"] == "P1" for event in live)
        assert len(client.get(f"{base}/state").json()["states"]) == 2
        final_seq = client.get(f"{base}/events").json()["last_seq"]
    # New app/repository/store instances read durable state without the old engine.
    with TestClient(create_app(settings)) as reopened:
        assert reopened.get(f"{base}/state").json()["state"]["score"] == {"P1": 2, "P2": 0}
        assert reopened.get(f"{base}/events").json()["last_seq"] == final_seq
        assert len(reopened.get(f"{base}/events?types=point").json()["events"]) == 2
