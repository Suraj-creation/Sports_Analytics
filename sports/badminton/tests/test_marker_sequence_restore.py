"""Human marker state follows append sequence, not marker position in the video."""

from pathlib import Path

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_engine.schema import Provenance
from bai_engine.store import EventStore

HUMAN = Provenance(model="human", worker="test")


def _engine(store: EventStore) -> BadmintonMatchEngine:
    return BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)


@pytest.mark.parametrize("last", [[(10, 20)], [], None])
def test_restore_latest_reviewed_intervals_by_append_order(tmp_path: Path, last) -> None:
    store = EventStore(tmp_path / "interval.sqlite", "S1")
    original = _engine(store)
    original.set_reviewed_match_intervals([(100, 150)], HUMAN)
    original.set_reviewed_match_intervals(last, HUMAN)
    restored = _engine(store)
    restored.restore_from_log(200)
    expected = None if last is None else tuple(tuple(pair) for pair in last)
    assert restored.phase.reviewed_intervals == expected


@pytest.mark.parametrize("last", [20, None])
def test_restore_latest_match_start_by_append_order(tmp_path: Path, last) -> None:
    store = EventStore(tmp_path / "start.sqlite", "S1")
    original = _engine(store)
    original.set_match_start(100, HUMAN)
    original.set_match_start(last, HUMAN)
    restored = _engine(store)
    restored.restore_from_log(200)
    assert restored.phase.match_start_frame == last


@pytest.mark.parametrize("last", [[(10, 20)], [], None])
def test_carry_over_uses_latest_interval_marker_and_is_idempotent(tmp_path: Path, last) -> None:
    old = EventStore(tmp_path / "old.sqlite", "S1")
    original = _engine(old)
    original.set_reviewed_match_intervals([(100, 150)], HUMAN)
    original.set_reviewed_match_intervals(last, HUMAN)
    target = _engine(EventStore(tmp_path / "new.sqlite", "S1"))
    markers = old.query(types=["match_phase"])
    target.carry_over(markers, HUMAN)
    expected = None if last is None else tuple(tuple(pair) for pair in last)
    assert target.phase.reviewed_intervals == expected
    assert target.carry_over(markers, HUMAN) == 0


@pytest.mark.parametrize("last", [20, None])
def test_carry_over_uses_latest_start_marker_and_is_idempotent(tmp_path: Path, last) -> None:
    old = EventStore(tmp_path / "old.sqlite", "S1")
    original = _engine(old)
    original.set_match_start(100, HUMAN)
    original.set_match_start(last, HUMAN)
    target = _engine(EventStore(tmp_path / "new.sqlite", "S1"))
    markers = old.query(types=["match_phase"])
    target.carry_over(markers, HUMAN)
    assert target.phase.match_start_frame == last
    assert target.carry_over(markers, HUMAN) == 0
