"""Anonymous movement never creates named identity or bridges invalid evidence."""

from pathlib import Path

import pytest

from bai_badminton.analytics.episode_movement import build_episode_movement
from bai_engine.schema import Event, EventStatus, Provenance, TrackObject, TrackSample
from bai_engine.schema.tracks import samples_to_table
from bai_engine.store import EventStore, TrackStore


def setup(
    tmp_path: Path, *, missing_camera=(), missing_xy=(), duplicate=(), jump=(), invalid_bbox=(),
    reverse=False, source_flags=None,
):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    tracks = TrackStore(tmp_path / "tracks")
    obs = store.append(
        Event(
            session_id="S1",
            type="participant_observation",
            frame_start=0,
            frame_end=0,
            pts_us=0,
            status=EventStatus.PROVISIONAL,
            provenance=Provenance(model="participant_tracker_v1"),
            payload={"kind": "PARTICIPANT_FIRST_OBSERVED", "participant_id": "participant-abc-000001", "track_id": 7},
        )
    )
    players = []
    cameras = []
    for frame in range(30):
        x = (30 - frame if reverse else frame) * 0.015
        if frame in jump:
            x += 2
        fields = dict(
            frame_idx=frame,
            obj=TrackObject.PLAYER,
            track_id=7,
            participant_observation_id=obs.event_id,
            bbox=(-100, 0, 5, 20) if frame in invalid_bbox else (10, 10, 30, 50),
            court_x=None if frame in missing_xy else x,
            court_y=None if frame in missing_xy else 0.5,
            visible=True,
            conf=0.9,
            detector_observed=(source_flags or {}).get(frame),
        )
        players.append(TrackSample(**fields))
        if frame in duplicate:
            players.append(TrackSample(**fields))
        if frame not in missing_camera:
            cameras.append(
                TrackSample(
                    frame_idx=frame,
                    obj=TrackObject.CAMERA,
                    track_id=0,
                    visible=True,
                    conf=0.9,
                    cam=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
                )
            )
    tracks.write_chunk(TrackObject.PLAYER, 0, 29, samples_to_table(players))
    tracks.write_chunk(TrackObject.CAMERA, 0, 29, samples_to_table(cameras))
    return store, tracks, obs


def fold(store, tracks, start=0, end=29):
    return build_episode_movement(
        store, tracks, start_frame=start, end_frame=end, max_frame=100, fps=30, frame_width=1280, frame_height=720
    )


def test_valid_episode_only_returns_bounded_anonymous_provisional_metrics(tmp_path):
    store, tracks, obs = setup(tmp_path)
    result = fold(store, tracks)
    assert result["scope"] == "anonymous_track_episodes_not_people"
    episode = result["episodes"][0]
    assert episode["observation_id"] == obs.event_id and episode["track_id"] == 7
    assert episode["distance_m"] > 0 and episode["observed_seconds"] > 0
    assert episode["valid_frames"] == 30 and episode["coverage_fraction"] == 1
    assert episode["positions_m"] and "player_id" not in episode


def test_camera_loss_and_missing_coordinates_never_bridge_or_fabricate_coverage(tmp_path):
    store, tracks, obs = setup(tmp_path, missing_camera={10}, missing_xy={20})
    episode = fold(store, tracks)["episodes"][0]
    assert episode["valid_frames"] == 28
    assert episode["observed_seconds"] < 29 / 30
    assert episode["coverage_fraction"] == pytest.approx(28 / 30)


def test_no_calibration_returns_no_distance_not_zero(tmp_path):
    store, tracks, obs = setup(tmp_path, missing_camera=set(range(30)))
    episode = fold(store, tracks)["episodes"][0]
    assert episode["distance_m"] is None and episode["positions_m"] == []
    assert episode["valid_frames"] == 0 and episode["observed_seconds"] == 0


def test_bad_samples_and_duplicate_track_frames_are_excluded(tmp_path):
    store, tracks, obs = setup(tmp_path, duplicate={10}, invalid_bbox={20})
    episode = fold(store, tracks)["episodes"][0]
    assert episode["valid_frames"] == 28 and episode["coverage_fraction"] == pytest.approx(28 / 30)


def test_implausible_court_jump_is_not_counted_as_distance(tmp_path):
    store, tracks, obs = setup(tmp_path, jump={15})
    episode = fold(store, tracks)["episodes"][0]
    assert episode["distance_m"] < 1.0
    assert episode["observed_seconds"] < 29 / 30


def test_reset_terminates_episode_even_if_rows_keep_old_observation_id(tmp_path):
    store, tracks, obs = setup(tmp_path)
    store.append(
        Event(
            session_id="S1",
            type="identity_ambiguity",
            frame_start=15,
            frame_end=15,
            pts_us=500000,
            status=EventStatus.PROVISIONAL,
            provenance=Provenance(model="participant_tracker_v1"),
            payload={"reason": "visual_tracker_reset", "tracker_instance": "xyz"},
        )
    )
    episode = fold(store, tracks)["episodes"][0]
    assert episode["valid_frames"] == 15
    assert all(row[1] < 1.0 for row in episode["positions_m"])


def test_window_validation_is_bounded(tmp_path):
    store, tracks, obs = setup(tmp_path)
    with pytest.raises(ValueError):
        fold(store, tracks, start=20, end=10)
    with pytest.raises(ValueError):
        build_episode_movement(
            store, tracks, start_frame=0, end_frame=3600, max_frame=5000, fps=30, frame_width=1280, frame_height=720
        )


def test_singular_camera_matrix_is_not_valid_calibration(tmp_path):
    store, tracks, obs = setup(tmp_path)
    cameras = [
        TrackSample(
            frame_idx=f, obj=TrackObject.CAMERA, track_id=0, conf=0.9, cam=(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        )
        for f in range(30)
    ]
    tracks.write_chunk(TrackObject.CAMERA, 0, 29, samples_to_table(cameras))
    episode = fold(store, tracks)["episodes"][0]
    assert episode["distance_m"] is None and episode["valid_frames"] == 0


def test_reused_track_id_never_joins_two_observation_episodes(tmp_path):
    store, tracks, first = setup(tmp_path)
    store.append(
        Event(
            session_id="S1",
            type="participant_observation",
            frame_start=15,
            frame_end=15,
            pts_us=500000,
            status=EventStatus.PROVISIONAL,
            provenance=Provenance(model="participant_tracker_v1"),
            payload={"kind": "PLAYER_EXITED", "participant_id": "participant-abc-000001", "track_id": 7},
        )
    )
    second = store.append(
        Event(
            session_id="S1",
            type="participant_observation",
            frame_start=16,
            frame_end=16,
            pts_us=533333,
            status=EventStatus.PROVISIONAL,
            provenance=Provenance(model="participant_tracker_v1"),
            payload={"kind": "PLAYER_ENTERED", "participant_id": "participant-abc-000002", "track_id": 7},
        )
    )
    players = [
        TrackSample(
            frame_idx=f,
            obj=TrackObject.PLAYER,
            track_id=7,
            participant_observation_id=first.event_id if f < 16 else second.event_id,
            bbox=(10, 10, 30, 50),
            court_x=f * 0.01,
            court_y=0.5,
            conf=0.9,
        )
        for f in range(30)
    ]
    tracks.write_chunk(TrackObject.PLAYER, 0, 29, samples_to_table(players))
    episodes = {episode["observation_id"]: episode for episode in fold(store, tracks)["episodes"]}
    assert episodes[first.event_id]["valid_frames"] == 15
    assert episodes[second.event_id]["valid_frames"] == 14
    assert episodes[first.event_id]["participant_id"] != episodes[second.event_id]["participant_id"]


def test_position_samples_cannot_be_mistaken_for_a_continuous_polyline_across_a_gap(tmp_path):
    store, tracks, _ = setup(tmp_path, missing_camera={10}, reverse=True)
    episode = fold(store, tracks)["episodes"][0]
    assert episode["segments"] >= 2
    assert episode["positions_semantics"] == "unordered_samples_do_not_connect"
    assert episode["positions_m"] == sorted(episode["positions_m"])


def test_movement_counts_source_flags_only_for_valid_frames(tmp_path):
    store, tracks, _ = setup(tmp_path, missing_camera={3}, invalid_bbox={4},
        source_flags={0: True, 1: False, 3: True, 4: False, 5: True, 6: False})
    episode = fold(store, tracks)["episodes"][0]
    assert episode["valid_frames"] == 28
    assert episode["detector_observed_frames"] == 2
    assert episode["carried_frames"] == 2
    assert episode["unknown_source_frames"] == 24
    source_total = sum(episode[k] for k in ("detector_observed_frames", "carried_frames", "unknown_source_frames"))
    assert source_total == episode["valid_frames"]


def test_legacy_movement_marks_all_accepted_sources_unknown(tmp_path):
    store, tracks, _ = setup(tmp_path)
    episode = fold(store, tracks)["episodes"][0]
    assert episode["valid_frames"] == 30
    assert episode["detector_observed_frames"] == 0
    assert episode["carried_frames"] == 0
    assert episode["unknown_source_frames"] == 30
