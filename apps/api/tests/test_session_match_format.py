"""Optional match format is saved before a new analysis is queued."""

import pytest
from fastapi.testclient import TestClient


def _capture_before_dispatch(client: TestClient, monkeypatch):
    captured = []

    def capture(command):
        assert command["cmd"] == "start"
        saved = client.app.state.repo.get(command["session_id"])
        assert saved is not None
        captured.append(saved)

    monkeypatch.setattr(client.app.state.bus, "send_command", capture)
    return captured


def _assert_roster(data, expected_count, match_format):
    roster = data["roster"]
    assert roster["match_format"] == match_format
    assert len(roster["participants"]) == expected_count
    ids = [person["participant_id"] for person in roster["participants"]]
    assert len(set(ids)) == expected_count
    assert all(person["name"] is None and person["team_id"] is None for person in roster["participants"])
    assert len(roster["teams"]) == 2 and all(team["score_slot"] is None for team in roster["teams"])
    assert all(value not in {"P1", "P2", "T1", "T2"} for value in ids)
    return set(ids)


@pytest.mark.parametrize("match_format,count", [("singles", 2), ("doubles", 4)])
def test_upload_records_format_and_unassigned_participants_before_start(
    client: TestClient, monkeypatch, match_format, count
):
    captured = _capture_before_dispatch(client, monkeypatch)
    result = client.post(
        "/api/sessions", files={"file": ("match.mp4", b"video", "video/mp4")}, data={"match_format": match_format}
    )
    assert result.status_code == 201, result.text
    first_ids = _assert_roster(result.json(), count, match_format)
    assert captured[0].roster.model_dump(mode="json") == result.json()["roster"]
    second = client.post(
        "/api/sessions", files={"file": ("match.mp4", b"video2", "video/mp4")}, data={"match_format": match_format}
    )
    assert second.status_code == 201
    assert first_ids.isdisjoint(_assert_roster(second.json(), count, match_format))


def test_upload_absent_format_preserves_legacy_and_bad_format_rejected(client: TestClient, monkeypatch):
    captured = _capture_before_dispatch(client, monkeypatch)
    result = client.post("/api/sessions", files={"file": ("match.mp4", b"video", "video/mp4")})
    assert result.status_code == 201 and result.json()["roster"] is None
    assert captured[0].roster is None
    result = client.post(
        "/api/sessions", files={"file": ("match.mp4", b"video", "video/mp4")}, data={"match_format": "mixed"}
    )
    assert result.status_code == 422 and len(captured) == 1


def test_youtube_format_is_saved_before_start_and_invalid_is_rejected(client: TestClient, settings, monkeypatch):
    settings.youtube_ingest = True
    captured = _capture_before_dispatch(client, monkeypatch)
    body = {"url": "https://youtu.be/dQw4w9WgXcQ", "acknowledge_rights": True, "match_format": "doubles"}
    result = client.post("/api/sessions/youtube", json=body)
    assert result.status_code == 201, result.text
    _assert_roster(result.json(), 4, "doubles")
    assert captured[0].roster.model_dump(mode="json") == result.json()["roster"]
    body["match_format"] = "mixed"
    assert client.post("/api/sessions/youtube", json=body).status_code == 422
    assert len(captured) == 1
