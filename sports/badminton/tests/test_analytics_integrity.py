"""Regression tests for canonical evidence and conservative spatial metrics."""

from pathlib import Path

import numpy as np
import pytest

from bai_badminton.analytics.heatmaps import HeatmapSet
from bai_badminton.analytics.rebuild import build, rally_records
from bai_engine.schema import Actors, Event, EventStatus, Provenance, TrackObject, TrackSample
from bai_engine.schema.tracks import samples_to_table
from bai_engine.store import EventStore, TrackStore


def event(kind: str, start: int = 0, end: int = 30, **kwargs: object) -> Event:
    return Event(
        session_id="analytics",
        type=kind,
        frame_start=start,
        frame_end=end,
        pts_us=start * 1_000_000 // 30,
        provenance=Provenance(model="test"),
        status=EventStatus.CONFIRMED,
        **kwargs,
    )


def rally(store: EventStore, shots: list[Event], official: bool = True) -> Event:
    return store.append(
        event(
            "rally_end",
            payload={
                "rally_no": 1,
                "official": official,
                "winner": "P1",
                "loser": "P2",
                "outcome": "winner",
                "duration_s": 31 / 30,
                "shots": [
                    {"event_id": s.event_id, "frame": s.frame_start, "player_id": s.actors.player_id, **s.payload}
                    for s in shots
                ],
            },
        )
    )


def test_canonical_stroke_corrections_reach_rally_tactics(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        stroke = store.append(
            event(
                "stroke",
                10,
                10,
                actors=Actors(player_id="P1"),
                payload={"stroke": "smash", "subtype": "jump_smash", "is_serve": True},
            )
        )
        rally(store, [stroke])
        corrected = store.append(
            stroke.correct(actors=Actors(player_id="P2"), payload={"stroke": "clear", "is_serve": False})
        )
        record = rally_records(store)[0]
        assert record.shots == [
            {"event_id": corrected.event_id, "frame": 10, "player_id": "P2", "stroke": "clear", "is_serve": False}
        ]
        analytics = build(store, None, 30)
        assert analytics.players["P1"].smash_points == 0
        assert analytics.players["P1"].serve_points_won == 0
        assert analytics.players["P2"].strokes == {"clear": 1}


def test_corrected_unofficial_stroke_never_enters_official_totals(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        stroke = store.append(event("stroke", 10, 10, actors=Actors(player_id="P1"), payload={"stroke": "smash"}))
        rally(store, [stroke], official=False)
        store.append(stroke.correct(payload={"stroke": "clear"}))
        analytics = build(store, None, 30)
        assert sum(sum(p.strokes.values()) for p in analytics.players.values()) == 0


def test_retracted_stroke_is_removed_from_embedded_sequence(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        stroke = store.append(event("stroke", 10, 10, actors=Actors(player_id="P1"), payload={"stroke": "smash"}))
        rally(store, [stroke])
        store.append(stroke.retract(Provenance(model="human")))
        assert rally_records(store)[0].shots == []
        assert build(store, None, 30).to_public()["avg_rally_shots"] == 0


def test_unsegmented_contact_hypotheses_do_not_become_match_strokes(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        store.append(event("stroke", 10, 10, actors=Actors(player_id="P1"), payload={"stroke": "smash"}))
        assert build(store, None, 30).to_public()["players"] == {}


def test_heatmap_does_not_bridge_nonfinite_gap_or_admit_below_margin() -> None:
    maps = HeatmapSet()
    assert maps.add_path("P1", np.array([[0, 0], [np.nan, np.nan], [1, 0]])) == 0
    maps.add("P1", "presence", -4.1, 0)  # below -4.05 m lower grid bound
    assert ("P1", "presence") not in maps.grids


def samples(
    xs: list[float | None], frames: list[int], *, quality: float = 0.9, tracks: list[int] | None = None
) -> list[TrackSample]:
    out = []
    for i, (frame, x) in enumerate(zip(frames, xs, strict=True)):
        out.append(
            TrackSample(
                frame_idx=frame,
                obj=TrackObject.PLAYER,
                track_id=tracks[i] if tracks else 1,
                player_id="P1",
                court_x=x,
                court_y=0 if x is not None else None,
                conf=0.9,
            )
        )
        out.append(
            TrackSample(
                frame_idx=frame, obj=TrackObject.CAMERA, track_id=0, conf=quality, cam=(1, 0, 0, 0, 1, 0, 0, 0, 1)
            )
        )
    return out


def spatial_fold(tmp_path: Path, rows: list[TrackSample]) -> dict:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        rally(store, [])
        tracks = TrackStore(tmp_path / "tracks")
        for obj in (TrackObject.PLAYER, TrackObject.CAMERA):
            tracks.write_chunk(obj, 0, 30, samples_to_table([s for s in rows if s.obj == obj]))
        return build(store, tracks, 30).to_public()["players"]["P1"]


def test_spatial_distance_withholds_without_calibration_quality(tmp_path: Path) -> None:
    result = spatial_fold(tmp_path, samples([0, 0.5, 1], [0, 6, 12], quality=0.2))
    assert result["distance_m"] is None
    assert result["distance_quality"]["coverage"] == 0
    assert result["distance_quality"]["status"] == "unavailable"


@pytest.mark.parametrize(
    "xs,frames,ids",
    [
        ([0, None, 1], [0, 6, 12], [1, 1, 1]),
        ([0, 1], [0, 30], [1, 1]),
        ([0, 1], [0, 6], [1, 2]),
    ],
)
def test_spatial_distance_never_spans_missing_time_or_identity(
    tmp_path: Path,
    xs: list,
    frames: list[int],
    ids: list[int],
) -> None:
    result = spatial_fold(tmp_path, samples(xs, frames, tracks=ids))
    assert result["distance_m"] is None
    assert result["distance_quality"]["segments"] == 0


def test_spatial_estimate_keeps_measured_stillness_and_suppresses_jitter(tmp_path: Path) -> None:
    xs = [0.02 if i % 2 else -0.02 for i in range(31)]
    result = spatial_fold(tmp_path, samples(xs, list(range(31))))
    assert result["distance_m"] == 0
    assert result["distance_quality"]["status"] == "estimate"
    assert result["distance_quality"]["coverage"] == 1
    assert result["distance_quality"]["observed_s"] > 0.8


def test_spatial_distance_accepts_continuous_measured_motion(tmp_path: Path) -> None:
    result = spatial_fold(tmp_path, samples([i / 30 for i in range(31)], list(range(31))))
    assert 0.8 <= result["distance_m"] <= 1
    assert result["distance_quality"]["method"] == "court_path_v2"


def test_receiver_feet_are_not_reported_as_a_shuttle_landing(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        stroke = store.append(
            event(
                "stroke",
                10,
                10,
                actors=Actors(player_id="P1"),
                payload={
                    "stroke": "clear",
                    "receiver_id": "P2",
                    "landing_court_xy": [0, 4],
                },
            )
        )
        rally(store, [stroke])
        analytics = build(store, None, 30)
        assert ("P1", "landing") not in analytics.heatmaps.grids


def test_dropped_player_row_breaks_an_otherwise_plausible_path(tmp_path: Path) -> None:
    frames = list(range(6)) + list(range(7, 14))
    # Both observed runs are stationary. The 0.5 m change happened in the missing frame,
    # so it cannot be measured as a continuous observed path.
    result = spatial_fold(tmp_path, samples([0] * 6 + [0.5] * 7, frames))
    assert result["distance_m"] == 0
    assert result["distance_quality"]["observed_s"] < 0.4


def test_official_rally_without_a_point_has_no_supported_score(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        rally(store, [])
        record = rally_records(store)[0]
        assert record.score_available is False
        assert build(store, None, 30).score_timeline == []


def test_canonical_point_marks_rally_score_as_available(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        parent = rally(store, [])
        store.append(
            event(
                "point",
                parent_id=parent.event_id,
                payload={
                    "state_before": {"game_no": 1},
                    "state_after": {"score": {"P1": 1, "P2": 0}},
                },
            )
        )
        record = rally_records(store)[0]
        assert record.score_available is True
        assert record.score_after == {"P1": 1, "P2": 0}
        assert build(store, None, 30).score_timeline[0]["score"] == {"P1": 1, "P2": 0}


def test_official_shot_totals_reconcile_attributed_and_unattributed_events(tmp_path: Path) -> None:
    with EventStore(tmp_path / "events.db", "analytics") as store:
        assigned = [store.append(event("stroke", i, i, actors=Actors(player_id=f"P{i}"),
                                       payload={"stroke": "drive"})) for i in range(1, 5)]
        unresolved = store.append(event("stroke", 5, 5, actors=Actors(), payload={"stroke": "unknown"}))
        rally(store, [*assigned, unresolved, unresolved])
        practice = store.append(event("stroke", 8, 8, actors=Actors(), payload={"stroke": "smash"}))
        rally(store, [practice], official=False)
        public = build(store, None, 30).to_public()
        assert public["shot_accounting"] == {"total": 5, "attributed": 4, "unattributed": 1}
        assert sum(sum(player["strokes"].values()) for player in public["players"].values()) == 4
        store.append(unresolved.correct(actors=Actors(player_id="P3")))
        corrected = build(store, None, 30).to_public()
        assert corrected["shot_accounting"] == {"total": 5, "attributed": 5, "unattributed": 0}
