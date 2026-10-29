"""Live public snapshots use the persisted, correction-aware spatial fold."""

from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from bai_badminton.analytics.rebuild import build
from bai_badminton.plugin import BadmintonSession
from bai_engine.schema import Actors, Event, EventStatus, Provenance, TrackObject, TrackSample
from bai_engine.schema.tracks import samples_to_table
from bai_engine.store import EventStore, TrackStore


def event(kind: str, **kwargs) -> Event:
    return Event(
        session_id="S1",
        type=kind,
        frame_start=0,
        frame_end=30,
        pts_us=0,
        provenance=Provenance(model="test"),
        status=EventStatus.CONFIRMED,
        **kwargs,
    )


def plugin(store: EventStore) -> BadmintonSession:
    session = BadmintonSession.__new__(BadmintonSession)
    session.store = store
    session.session = SimpleNamespace(media=SimpleNamespace(fps=30.0, fps_num=30, fps_den=1))
    return session


def write_tracks(tracks: TrackStore, *, moving: bool) -> None:
    for kind in (TrackObject.PLAYER, TrackObject.CAMERA):
        rows = [
            TrackSample(
                frame_idx=i,
                obj=kind,
                track_id=1 if kind == TrackObject.PLAYER else 0,
                player_id="P1" if kind == TrackObject.PLAYER else None,
                court_x=(i / 30 if moving else 0),
                court_y=-4,
                conf=0.9,
                cam=(1, 0, 0, 0, 1, 0, 0, 0, 1) if kind == TrackObject.CAMERA else None,
            )
            for i in range(31)
        ]
        tracks.write_chunk(kind, 0, 30, samples_to_table(rows))


def test_live_analytics_matches_persisted_spatial_fold_and_caches_unchanged_status(tmp_path: Path) -> None:
    store = EventStore(tmp_path / "events.sqlite", "S1")
    stroke = store.append(
        event(
            "stroke",
            actors=Actors(player_id="P1"),
            payload={
                "stroke": "clear",
                "hitter_court_xy": [0, -4],
            },
        )
    )
    store.append(
        event(
            "rally_end",
            payload={
                "official": True,
                "duration_s": 31 / 30,
                "shots": [{"event_id": stroke.event_id}],
            },
        )
    )
    tracks = TrackStore(tmp_path / "tracks")
    write_tracks(tracks, moving=True)
    live = plugin(store)
    with patch("bai_badminton.analytics.rebuild.build", wraps=build) as fold:
        first = live.analytics()
        assert live.analytics() == first
        assert fold.call_count == 1
        persisted = build(store, tracks, 30).to_public()
        assert {k: v for k, v in first.items() if k != "highlights"} == persisted
        assert first["players"]["P1"]["distance_m"] >= 0.8
        assert live._analytics_fold.heatmaps.to_public("P1", "origin")["total"] == 1
        write_tracks(tracks, moving=False)
        assert live.analytics()["players"]["P1"]["distance_m"] == 0
        assert fold.call_count == 2  # track-only revision, no new event
        store.append(stroke.correct(payload={"stroke": "drop"}))
        assert live.analytics()["players"]["P1"]["strokes"] == {"drop": 1}
        assert fold.call_count == 3
    store.close()


def test_replaced_event_database_does_not_reuse_equal_sequence_cache(tmp_path: Path) -> None:
    path = tmp_path / "events.sqlite"
    store = EventStore(path, "S1")
    store.append(event("rally_end", payload={"official": True, "shots": []}))
    live = plugin(store)
    assert live.analytics()["rallies"] == 1
    store.close()
    # Keep the original inode allocated, as reset_analysis's backup does.
    path.rename(tmp_path / "events.before.sqlite")
    replacement = EventStore(path, "S1")
    replacement.append(event("rally_end", payload={"official": False, "shots": []}))
    live.store = replacement
    assert live.analytics()["rallies"] == 0
    assert live.analytics()["unofficial_rallies"] == 1
    replacement.close()
