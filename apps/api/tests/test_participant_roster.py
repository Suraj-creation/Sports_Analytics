import pytest
from fastapi.testclient import TestClient

from bai_engine.schema import PlayerInfo, Session, Source, SourceKind


def make_session(client: TestClient) -> Session:
    return client.app.state.repo.save(Session(
        title="Doubles recording",
        source=Source(kind=SourceKind.UPLOAD, uri="none"),
        players=[PlayerInfo(player_id="P1", name="Team A"), PlayerInfo(player_id="P2", name="Team B")],
    ))


def roster() -> dict:
    return {
        "match_format": "doubles",
        "teams": [{"team_id": "T1", "score_slot": "P1"}, {"team_id": "T2", "score_slot": "P2"}],
        "participants": [
            {"participant_id": "U1", "name": "Alice", "team_id": "T1"},
            {"participant_id": "U2", "name": "Bob", "team_id": "T1"},
            {"participant_id": "U3", "name": "Cara", "team_id": "T2"},
            {"participant_id": "U4", "name": "Dev", "team_id": "T2"},
        ],
    }


def test_roster_is_explicit_and_does_not_replace_score_slots(client: TestClient) -> None:
    session = make_session(client)
    result = client.put(f"/api/sessions/{session.session_id}/roster", json=roster())
    assert result.status_code == 200, result.text
    payload = result.json()
    assert payload["roster"] == roster()
    assert [(p["player_id"], p["name"]) for p in payload["players"]] == [("P1", "Team A"), ("P2", "Team B")]
    assert client.get(f"/api/sessions/{session.session_id}").json()["roster"] == roster()


@pytest.mark.parametrize("bad", ["duplicate_participant", "unknown_team", "duplicate_slot", "score_slot_as_person"])
def test_invalid_roster_cannot_be_persisted(client: TestClient, bad: str) -> None:
    session = make_session(client)
    payload = roster()
    if bad == "duplicate_participant":
        payload["participants"][1]["participant_id"] = "U1"
    elif bad == "unknown_team":
        payload["participants"][1]["team_id"] = "T3"
    elif bad == "duplicate_slot":
        payload["teams"][1]["score_slot"] = "P1"
    else:
        payload["participants"][0]["participant_id"] = "P1"
    result = client.put(f"/api/sessions/{session.session_id}/roster", json=payload)
    assert result.status_code == 422
    assert client.get(f"/api/sessions/{session.session_id}").json()["roster"] is None


@pytest.mark.parametrize("bad", ["team_uses_score_slot", "episode_as_participant", "case_duplicate"])
def test_roster_identity_namespaces_do_not_alias_scores_or_tracking(client: TestClient, bad: str) -> None:
    session = make_session(client)
    payload = roster()
    if bad == "team_uses_score_slot":
        payload["teams"][0]["team_id"] = "P1"
        payload["participants"][0]["team_id"] = "P1"
        payload["participants"][1]["team_id"] = "P1"
    elif bad == "episode_as_participant":
        payload["participants"][0]["participant_id"] = "participant-abc123-000001"
    else:
        payload["participants"][1]["participant_id"] = "u1"
    response = client.put(f"/api/sessions/{session.session_id}/roster", json=payload)
    assert response.status_code == 422


def test_roster_cannot_remove_or_reassign_a_reviewed_participant(client: TestClient) -> None:
    from bai_engine.schema import Actors, Event, EventStatus, Provenance

    session = make_session(client)
    assert client.put(f"/api/sessions/{session.session_id}/roster", json=roster()).status_code == 200
    store = client.app.state.repo.events(session.session_id)
    store.append(Event(session_id=session.session_id, type="identity_review", frame_start=1, frame_end=10,
                       pts_us=0, actors=Actors(player_id="U1"), status=EventStatus.HUMAN_VERIFIED,
                       provenance=Provenance(model="human"), payload={}))
    updated = roster()
    updated["participants"][0]["team_id"] = "T2"
    assert client.put(f"/api/sessions/{session.session_id}/roster", json=updated).status_code == 409
    updated = roster()
    updated["participants"] = updated["participants"][1:]
    assert client.put(f"/api/sessions/{session.session_id}/roster", json=updated).status_code == 409
    assert client.get(f"/api/sessions/{session.session_id}").json()["roster"] == roster()


def test_roster_name_correction_and_substitution_preserve_reviewed_team(client: TestClient) -> None:
    from bai_engine.schema import Actors, Event, EventStatus, Provenance

    session = make_session(client)
    assert client.put(f"/api/sessions/{session.session_id}/roster", json=roster()).status_code == 200
    client.app.state.repo.events(session.session_id).append(
        Event(session_id=session.session_id, type="identity_review", frame_start=1, frame_end=10, pts_us=0,
              actors=Actors(player_id="U1"), status=EventStatus.HUMAN_VERIFIED,
              provenance=Provenance(model="human"), payload={})
    )
    updated = roster()
    updated["participants"][0]["name"] = "Alice Updated"
    updated["participants"].append({"participant_id": "U5", "name": "Substitute", "team_id": "T1"})
    assert client.put(f"/api/sessions/{session.session_id}/roster", json=updated).status_code == 200
    updated["teams"][0]["score_slot"] = None
    assert client.put(f"/api/sessions/{session.session_id}/roster", json=updated).status_code == 409


def test_individual_analytics_reports_empty_roster_separately(client: TestClient) -> None:
    from bai_engine.schema.session import MediaInfo
    session = make_session(client)
    client.app.state.repo.update(session.session_id, media=MediaInfo(
        fps_num=30, fps_den=1, n_frames=300, width=1920, height=1080, duration_us=10_000_000
    ))
    url = f"/api/sessions/{session.session_id}/individual-analytics"
    assert client.get(url).json()["available"] is False
    assert client.put(f"/api/sessions/{session.session_id}/roster", json=roster()).status_code == 200
    result = client.get(url)
    assert result.status_code == 200
    assert set(result.json()["participants"]) == {"U1", "U2", "U3", "U4"}
    assert result.json()["accounting"] == {"total_shots": 0, "attributed_shots": 0, "unattributed_shots": 0}
