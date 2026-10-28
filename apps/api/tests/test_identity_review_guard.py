import pytest
from fastapi.testclient import TestClient

from bai_engine.schema import Event, Provenance, Session, Source, SourceKind


@pytest.mark.parametrize(
    "event_type",
    [
        "identity_review",
        "identity_ambiguity",
        "participant_observation",
        "doubles_team_hypothesis",
        "stroke_participant_review",
    ],
)
def test_generic_verify_rejects_tracker_evidence_before_queueing(
    client: TestClient, monkeypatch, event_type: str
) -> None:
    session = client.app.state.repo.save(Session(title="Review", source=Source(kind=SourceKind.UPLOAD, uri="none")))
    store = client.app.state.repo.events(session.session_id)
    event = store.append(
        Event(
            session_id=session.session_id,
            type=event_type,
            frame_start=5,
            frame_end=5,
            pts_us=0,
            payload={"reason": "visual_tracker_reset"},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    commands = []
    monkeypatch.setattr(client.app.state.bus, "send_command", commands.append)
    response = client.post(
        f"/api/sessions/{session.session_id}/corrections",
        json={
            "kind": "verify",
            "event_id": event.event_id,
            "payload": {"reason": "none"},
        },
    )
    assert response.status_code == 422
    assert not commands
    assert store.get(event.event_id).payload["reason"] == "visual_tracker_reset"
