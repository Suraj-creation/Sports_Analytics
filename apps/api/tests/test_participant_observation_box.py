"""Exact, auditable track boxes for reviewing an anonymous episode."""

import math

import pytest
from fastapi.testclient import TestClient

from bai_engine.schema import Event, EventStatus, Provenance, Session, Source, SourceKind, TrackObject, TrackSample
from bai_engine.schema.session import MediaInfo
from bai_engine.schema.tracks import samples_to_table


def setup_box(client):
    repo = client.app.state.repo
    session = repo.save(Session(title="Review", source=Source(kind=SourceKind.UPLOAD, uri="none")))
    repo.update(
        session.session_id,
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=100, width=1920, height=1080, duration_us=3333333),
    )
    store = repo.events(session.session_id)
    obs = store.append(
        Event(
            session_id=session.session_id,
            type="participant_observation",
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={
                "kind": "PARTICIPANT_FIRST_OBSERVED",
                "participant_id": "participant-abc123-000001",
                "track_id": 7,
            },
            status=EventStatus.PROVISIONAL,
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    url = f"/api/sessions/{session.session_id}/participant-observations/{obs.event_id}/box"
    return repo, session, store, obs, url


def sample(frame=20, track=7, bbox=(100.0, 200.0, 300.0, 500.0), visible=True, detector_observed=True):
    return TrackSample(
        frame_idx=frame, obj=TrackObject.PLAYER, track_id=track, bbox=bbox,
        visible=visible, conf=0.9, detector_observed=detector_observed,
    )


def write(repo, session, rows, *, mark=True):
    obs = repo.events(session.session_id).query(types=["participant_observation"])[0]
    if mark:
        rows = [row.model_copy(update={"participant_observation_id": obs.event_id}) for row in rows]
    repo.tracks(session.session_id).write_chunk(TrackObject.PLAYER, 0, 99, samples_to_table(rows))


def test_exact_frame_box_and_authentication(client: TestClient):
    repo, session, _, _, url = setup_box(client)
    write(repo, session, [sample(), sample(frame=19, track=8)])
    auth = client.app.state.auth
    auth.enabled = True
    assert client.get(url, params={"frame": 20}).status_code == 401
    token, _ = auth.issue()
    client.cookies.set("bai_session", token)
    result = client.get(url, params={"frame": 20})
    assert result.status_code == 200
    assert result.json() == {
        "available": True,
        "frame": 20,
        "bbox": [100.0, 200.0, 300.0, 500.0],
        "video_width": 1920,
        "video_height": 1080,
    }
    assert client.get(url, params={"frame": 19}).json()["available"] is False
    assert client.get(url, params={"frame": 100}).status_code == 422
    assert client.get(url, params={"frame": -1}).status_code == 422


@pytest.mark.parametrize(
    "rows",
    [
        [],
        [sample(), sample()],
        [sample(visible=False)],
        [sample(bbox=(math.nan, 0.0, 10.0, 10.0))],
        [sample(bbox=(10.0, 10.0, 10.0, 20.0))],
        [sample(bbox=(-1.0, 10.0, 20.0, 20.0))],
    ],
)
def test_missing_duplicate_or_invalid_sample_unavailable(client: TestClient, rows):
    repo, session, _, _, url = setup_box(client)
    write(repo, session, rows)
    result = client.get(url, params={"frame": 20})
    assert result.status_code == 200
    assert result.json()["available"] is False and result.json()["bbox"] is None


@pytest.mark.parametrize(
    "kind,payload",
    [
        ("identity_ambiguity", {"reason": "visual_tracker_reset"}),
        (
            "participant_observation",
            {"kind": "PLAYER_EXITED", "participant_id": "participant-abc123-000001", "track_id": 7},
        ),
        (
            "participant_observation",
            {"kind": "PARTICIPANT_FIRST_OBSERVED", "participant_id": "participant-new456-000002", "track_id": 7},
        ),
    ],
)
def test_episode_boundaries_prevent_reused_track_box(client: TestClient, kind, payload):
    repo, session, store, _, url = setup_box(client)
    write(repo, session, [sample()])
    store.append(
        Event(
            session_id=session.session_id,
            type=kind,
            frame_start=15,
            frame_end=15,
            pts_us=0,
            payload=payload,
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    assert client.get(url, params={"frame": 20}).json()["available"] is False


def test_retracted_observation_and_same_frame_reuse_unavailable(client: TestClient):
    repo, session, store, obs, url = setup_box(client)
    write(repo, session, [sample()])
    store.append(
        Event(
            session_id=session.session_id,
            type="participant_observation",
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={"kind": "PLAYER_ENTERED", "participant_id": "participant-def456-000002", "track_id": 7},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    assert client.get(url, params={"frame": 20}).json()["available"] is False
    store.append(obs.retract(Provenance(model="human")))
    assert client.get(url, params={"frame": 20}).json()["available"] is False


def test_invalid_or_missing_observation_unavailable(client: TestClient):
    repo, session, store, obs, url = setup_box(client)
    write(repo, session, [sample()])
    assert client.get(url, params={"frame": 9}).json()["available"] is False
    corrected = store.append(obs.correct(provenance=Provenance(model="human")))
    corrected_url = url.replace(obs.event_id, corrected.event_id)
    assert client.get(corrected_url, params={"frame": 20}).json()["available"] is False
    assert client.get(url, params={"frame": 20}).json()["available"] is False


def test_track_row_without_matching_episode_marker_is_unavailable(client: TestClient):
    repo, session, store, obs, url = setup_box(client)
    write(repo, session, [sample()], mark=False)
    assert client.get(url, params={"frame": 20}).json()["available"] is False


def test_reset_or_exit_after_birth_at_same_frame_prevents_box(client: TestClient):
    repo, session, store, _, url = setup_box(client)
    write(repo, session, [sample()])
    store.append(
        Event(
            session_id=session.session_id,
            type="identity_ambiguity",
            frame_start=10,
            frame_end=10,
            pts_us=0,
            payload={"reason": "visual_tracker_reset"},
            provenance=Provenance(model="participant_tracker_v1"),
        )
    )
    assert client.get(url, params={"frame": 20}).json()["available"] is False


@pytest.mark.parametrize("flag,available", [(True, True), (False, False), (None, False)])
def test_review_seed_requires_explicit_detector_run(client: TestClient, flag, available):
    repo, session, _, _, url = setup_box(client)
    write(repo, session, [sample(detector_observed=flag)])
    response = client.get(url, params={"frame": 20})
    assert response.status_code == 200
    assert response.json()["available"] is available
    if not available:
        assert response.json()["bbox"] is None


def test_legacy_parquet_without_detector_source_fails_closed(client: TestClient):
    import pyarrow.parquet as pq

    repo, session, _, obs, url = setup_box(client)
    row = sample().model_copy(update={"participant_observation_id": obs.event_id})
    track_dir = repo.tracks(session.session_id).root / "player"
    track_dir.mkdir(parents=True, exist_ok=True)
    legacy = samples_to_table([row]).drop(["detector_observed"])
    pq.write_table(legacy, track_dir / "f000000000-000000099.v1.parquet")
    assert client.get(url, params={"frame": 20}).json()["available"] is False
