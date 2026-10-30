"""Broadcast score observations stay useful without inferred player identities."""
from pathlib import Path

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler
from bai_engine.store import EventStore


def reading(frame, a=3, b=2, names=("ANTONSEN", "FARHAN"), conf=0.99):
    return ScoreReading(frame_idx=frame, rows=((names[0], a), (names[1], b)), conf=conf)


def test_stable_board_is_available_without_player_name_mapping():
    rec = ScoreReconciler(player_names={"P1": "Sam", "P2": "TAM"})
    assert rec.add(reading(224)) is None
    assert rec.add(reading(249)) == reading(249)
    assert rec.row_map is None


def test_changed_or_renamed_board_needs_a_second_distinct_observation():
    rec = ScoreReconciler()
    rec.add(reading(224))
    assert rec.add(reading(224)) is None  # duplicate delivery is not corroboration
    assert rec.add(reading(249, a=4)) is None
    assert rec.add(reading(274, a=4)) == reading(274, a=4)
    assert rec.add(reading(299, a=4, names=("OTHER", "FARHAN"))) is None
    assert rec.add(reading(324, a=4, conf=0.3)) is None


def test_engine_persists_observed_board_without_awarding_points(tmp_path: Path):
    store = EventStore(tmp_path / "events.sqlite", "S1")
    engine = BadmintonMatchEngine(
        "S1", EngineConfig(fps=25, frame_width=1280, frame_height=720), store,
        player_names={"P1": "Sam", "P2": "TAM"},
    )
    engine.on_ocr(reading(224))
    assert store.query(types=["broadcast_score"]) == []
    engine.on_ocr(reading(249))
    events = store.query(types=["broadcast_score"])
    assert len(events) == 1
    event = events[0]
    assert event.frame_start == event.frame_end == 249
    assert event.payload["rows"] == [{"name": "ANTONSEN", "points": 3}, {"name": "FARHAN", "points": 2}]
    assert event.payload["player_mapping"] is None
    assert event.actors.player_id is None
    assert store.query(types=["point"]) == []
    assert engine.public_state()["score"] == {"P1": 0, "P2": 0}
