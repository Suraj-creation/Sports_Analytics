from fastapi.testclient import TestClient

from bai_engine.schema import Event, EventStatus, Provenance, Session, Source, SourceKind
from bai_engine.schema.session import MediaInfo


def setup_review(client):
    session = client.app.state.repo.save(Session(title="Review", source=Source(kind=SourceKind.UPLOAD, uri="none")))
    client.app.state.repo.update(
        session.session_id,
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=300, width=1920, height=1080, duration_us=10_000_000),
    )
    root = f"/api/sessions/{session.session_id}"
    roster = {
        "match_format": "doubles",
        "teams": [{"team_id": "T1", "score_slot": "P1"}, {"team_id": "T2", "score_slot": "P2"}],
        "participants": [
            {"participant_id": "U1", "name": "A", "team_id": "T1"},
            {"participant_id": "U2", "name": "B", "team_id": "T1"},
            {"participant_id": "U3", "name": "C", "team_id": "T2"},
            {"participant_id": "U4", "name": "D", "team_id": "T2"},
        ],
    }
    assert client.put(root + "/roster", json=roster).status_code == 200
    store = client.app.state.repo.events(session.session_id)
    obs = store.append(
        Event(
            session_id=session.session_id,
            type="participant_observation",
            frame_start=10,
            frame_end=10,
            pts_us=333333,
            payload={
                "kind": "PARTICIPANT_FIRST_OBSERVED",
                "participant_id": "participant-abc123-000001",
                "track_id": 7,
            },
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    stroke = store.append(
        Event(
            session_id=session.session_id,
            type="stroke",
            frame_start=25,
            frame_end=25,
            pts_us=833333,
            payload={
                "stroke": "smash",
                "participant_hypothesis": {
                    "status": "provisional",
                    "participant_id": "participant-abc123-000001",
                    "track_id": 7,
                },
            },
            provenance=Provenance(model="stroke_rules_v0"),
        )
    )
    return root, store, obs, stroke


def test_identity_and_scoped_stroke_review_lifecycle(client: TestClient):
    root, store, obs, stroke = setup_review(client)
    response = client.post(
        root + "/identity-reviews",
        json={"observation_id": obs.event_id, "player_id": "U1", "frame_start": 10, "frame_end": 30},
    )
    assert response.status_code == 201, response.text
    identity = response.json()
    assert identity["actors"]["player_id"] == "U1"
    assert len(client.get(root + "/identity-reviews").json()) == 1
    url = root + f"/strokes/{stroke.event_id}/participant-review"
    body = {
        "identity_review_id": identity["event_id"],
        "player_id": "U1",
        "participant_id": "participant-abc123-000001",
        "track_id": 7,
    }
    result = client.post(url, json=body)
    assert result.status_code == 201, result.text
    reviewed = result.json()
    assert reviewed["type"] == "stroke_participant_review"
    assert reviewed["payload"]["scope"] == "participant_only"
    assert reviewed["status"] == "human_verified"
    assert store.get(stroke.event_id).status == EventStatus.PROVISIONAL
    assert store.get(stroke.event_id).payload["stroke"] == "smash"
    assert client.post(url, json=body).status_code == 409
    deleted = client.delete(root + "/stroke-participant-reviews/" + reviewed["event_id"])
    assert deleted.status_code == 200
    assert client.post(url, json=body).status_code == 201
    assert client.delete(root + "/identity-reviews/" + identity["event_id"]).status_code == 200
    assert client.get(root + "/identity-reviews").json() == []
    assert client.post(url, json=body).status_code == 422


def test_review_requires_explicit_matching_observation_player_and_interval(client: TestClient):
    root, store, obs, stroke = setup_review(client)
    assert (
        client.post(
            root + "/identity-reviews",
            json={"observation_id": obs.event_id, "player_id": "P1", "frame_start": 10, "frame_end": 30},
        ).status_code
        == 422
    )
    assert (
        client.post(
            root + "/identity-reviews",
            json={"observation_id": obs.event_id, "player_id": "U1", "frame_start": 9, "frame_end": 30},
        ).status_code
        == 422
    )
    assert (
        client.post(
            root + "/identity-reviews",
            json={"observation_id": obs.event_id, "player_id": "U1", "frame_start": 10, "frame_end": True},
        ).status_code
        == 422
    )
    identity = client.post(
        root + "/identity-reviews",
        json={"observation_id": obs.event_id, "player_id": "U1", "frame_start": 10, "frame_end": 20},
    ).json()
    body = {
        "identity_review_id": identity["event_id"],
        "player_id": "U1",
        "participant_id": "participant-abc123-000001",
        "track_id": 7,
    }
    assert client.post(root + f"/strokes/{stroke.event_id}/participant-review", json=body).status_code == 422
    assert (
        client.post(
            root + "/identity-reviews",
            json={"observation_id": obs.event_id, "player_id": "U2", "frame_start": 10, "frame_end": 20},
        ).status_code
        == 422
    )
    assert not store.query(types=["stroke_participant_review"])


def test_authentication_and_csrf_are_enforced(client: TestClient):
    root, _, obs, _ = setup_review(client)
    auth = client.app.state.auth
    auth.enabled = True
    assert client.get(root + "/identity-reviews").status_code == 401
    token, csrf = auth.issue()
    client.cookies.set("bai_session", token)
    assert client.get(root + "/identity-reviews").status_code == 200
    body = {"observation_id": obs.event_id, "player_id": "U1", "frame_start": 10, "frame_end": 30}
    assert client.post(root + "/identity-reviews", json=body).status_code == 403
    assert client.post(root + "/identity-reviews", json=body, headers={"X-CSRF-Token": csrf}).status_code == 201


def test_cannot_duplicate_review_after_stroke_correction(client: TestClient):
    root, store, obs, stroke = setup_review(client)
    identity = client.post(
        root + "/identity-reviews",
        json={"observation_id": obs.event_id, "player_id": "U1", "frame_start": 10, "frame_end": 30},
    ).json()
    body = {
        "identity_review_id": identity["event_id"],
        "player_id": "U1",
        "participant_id": "participant-abc123-000001",
        "track_id": 7,
    }
    assert client.post(root + f"/strokes/{stroke.event_id}/participant-review", json=body).status_code == 201
    corrected = store.append(stroke.correct(payload={**stroke.payload, "stroke": "clear"}))
    assert client.post(root + f"/strokes/{corrected.event_id}/participant-review", json=body).status_code == 409


def test_cannot_verify_mismatched_participant_or_player(client: TestClient):
    root, store, obs, stroke = setup_review(client)
    identity = client.post(
        root + "/identity-reviews",
        json={"observation_id": obs.event_id, "player_id": "U1", "frame_start": 10, "frame_end": 30},
    ).json()
    url = root + f"/strokes/{stroke.event_id}/participant-review"
    body = {
        "identity_review_id": identity["event_id"],
        "player_id": "U1",
        "participant_id": "participant-abc123-000001",
        "track_id": 7,
    }
    for key, value in [("player_id", "U2"), ("participant_id", "participant-abc123-000002"), ("track_id", 8)]:
        assert client.post(url, json={**body, key: value}).status_code == 422
    assert not store.query(types=["stroke_participant_review"])


def test_scoped_api_review_drives_individual_analytics_and_revoke(client: TestClient):
    root, store, obs, stroke = setup_review(client)
    store.append(
        Event(
            session_id=store.session_id,
            type="rally_end",
            frame_start=50,
            frame_end=50,
            pts_us=1666666,
            payload={"official": True, "rally_no": 1, "duration_s": 1.0, "shots": [{"event_id": stroke.event_id}]},
            provenance=Provenance(model="test"),
        )
    )
    analytics = root + "/individual-analytics"
    assert client.get(analytics).json()["accounting"]["unattributed_shots"] == 1
    identity = client.post(
        root + "/identity-reviews",
        json={"observation_id": obs.event_id, "player_id": "U1", "frame_start": 10, "frame_end": 30},
    ).json()
    body = {
        "identity_review_id": identity["event_id"],
        "player_id": "U1",
        "participant_id": "participant-abc123-000001",
        "track_id": 7,
    }
    scoped = client.post(root + f"/strokes/{stroke.event_id}/participant-review", json=body)
    assert scoped.status_code == 201
    result = client.get(analytics).json()
    assert result["accounting"]["attributed_shots"] == 1
    assert result["participants"]["U1"]["shot_distribution"] == {"smash": 1}
    assert store.get(stroke.event_id).status == EventStatus.PROVISIONAL
    assert client.delete(root + "/stroke-participant-reviews/" + scoped.json()["event_id"]).status_code == 200
    assert client.get(analytics).json()["accounting"]["unattributed_shots"] == 1
