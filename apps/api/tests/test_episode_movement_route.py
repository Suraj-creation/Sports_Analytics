"""The anonymous movement endpoint returns calibrated paths or explicit unavailability."""

from fastapi.testclient import TestClient

from bai_engine.schema import Event, EventStatus, Provenance, Session, Source, SourceKind, TrackObject, TrackSample
from bai_engine.schema.session import MediaInfo
from bai_engine.schema.tracks import samples_to_table


def test_movement_route_reports_anonymous_calibrated_data_and_rejects_bad_windows(client: TestClient):
    session = client.app.state.repo.save(
        Session(
            title="match",
            source=Source(kind=SourceKind.UPLOAD, uri="none"),
            media=MediaInfo(fps_num=30, fps_den=1, n_frames=6000, width=1280, height=720, duration_us=200000000),
        )
    )
    store = client.app.state.repo.events(session.session_id)
    tracks = client.app.state.repo.tracks(session.session_id)
    obs = store.append(
        Event(
            session_id=session.session_id,
            type="participant_observation",
            frame_start=0,
            frame_end=0,
            pts_us=0,
            status=EventStatus.PROVISIONAL,
            provenance=Provenance(model="participant_tracker_v1"),
            payload={"kind": "PARTICIPANT_FIRST_OBSERVED", "participant_id": "participant-abc-000001", "track_id": 7},
        )
    )
    players = [
        TrackSample(
            frame_idx=f,
            obj=TrackObject.PLAYER,
            track_id=7,
            participant_observation_id=obs.event_id,
            bbox=(10, 10, 30, 50),
            court_x=f * 0.01,
            court_y=0.5,
            conf=0.9,
        )
        for f in range(30)
    ]
    cameras = [
        TrackSample(
            frame_idx=f, obj=TrackObject.CAMERA, track_id=0, conf=0.9, cam=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0)
        )
        for f in range(30)
    ]
    tracks.write_chunk(TrackObject.PLAYER, 0, 29, samples_to_table(players))
    tracks.write_chunk(TrackObject.CAMERA, 0, 29, samples_to_table(cameras))
    url = f"/api/sessions/{session.session_id}/episode-movement"
    response = client.get(url, params={"from": 0, "to": 29})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["available"] is True and data["scope"] == "anonymous_track_episodes_not_people"
    assert data["episodes"][0]["distance_m"] > 0
    assert "player_id" not in data["episodes"][0]
    assert client.get(url, params={"from": 0, "to": 3600}).status_code == 422
    assert client.get(url, params={"from": 40, "to": 0}).status_code == 422
    empty = client.get(url, params={"from": 30, "to": 60}).json()
    assert empty["available"] is False and empty["reason"] == "no_valid_calibrated_movement_segments"


def test_movement_route_requires_session_and_media(client: TestClient):
    assert client.get("/api/sessions/missing/episode-movement", params={"from": 0, "to": 29}).status_code == 404
    session = client.app.state.repo.save(
        Session(title="missing media", source=Source(kind=SourceKind.UPLOAD, uri="none"))
    )
    assert (
        client.get(f"/api/sessions/{session.session_id}/episode-movement", params={"from": 0, "to": 29}).status_code
        == 409
    )
