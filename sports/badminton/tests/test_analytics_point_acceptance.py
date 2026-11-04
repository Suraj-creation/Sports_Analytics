"""Analytics and engine restoration share the accepted point-decision boundary."""

from pathlib import Path

import pytest
from synthetic_support import bind_labelled_synthetic_singles

from bai_badminton.analytics.rebuild import build, rally_records
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_engine.schema import EventStatus
from bai_engine.store import EventStore


@pytest.fixture
def scored_rally(tmp_path: Path, monkeypatch):
    with EventStore(tmp_path / "score.sqlite", "S1") as store:
        cfg = EngineConfig(fps=30, frame_width=1280, frame_height=720)
        engine = BadmintonMatchEngine("S1", cfg, store)
        bind_labelled_synthetic_singles(engine)
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("winner", "far", "controlled_fixture", 0.85))
        monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(scoreboard="changed"))
        engine._pending = [_PendingRally(RallySegment(10, 20, None, "stationary"), [], None)]
        engine._finalize_pending(100)
        yield cfg, store, store.query(types=["point"])[0]


@pytest.mark.parametrize("invalid", ["provisional", "malformed_provisional", "unknown_winner"])
def test_unaccepted_point_is_unavailable_in_canonical_analytics(scored_rally, invalid):
    _, store, point = scored_rally
    payload = dict(point.payload)
    status = EventStatus.PROVISIONAL
    if invalid == "malformed_provisional":
        payload = {"winner": "P1"}  # candidates need not carry a finalized score projection
    elif invalid == "unknown_winner":
        status = EventStatus.CONFIRMED
        payload["winner"] = None
    store.append(point.correct(payload=payload, status=status))

    record = rally_records(store)[0]
    assert record.score_available is False
    analytics = build(store, None, 30)
    assert analytics.score_timeline == []
    assert sum(player.points_won for player in analytics.players.values()) == 0


@pytest.mark.parametrize("malformed", [False, True])
def test_restoration_does_not_reintroduce_rejected_point_availability(scored_rally, malformed):
    cfg, store, point = scored_rally
    payload = {"winner": "P1"} if malformed else point.payload
    store.append(point.correct(payload=payload, status=EventStatus.PROVISIONAL))

    restored = BadmintonMatchEngine("S1", cfg, store)
    assert restored.restore_from_log(100) == 1
    assert restored.public_state()["score"] == {"P1": 0, "P2": 0}
    assert restored._rallies[0].record.score_available is False
    assert restored.analytics.score_timeline == []
    assert sum(player.points_won for player in restored.analytics.players.values()) == 0


@pytest.mark.parametrize("status", [EventStatus.CONFIRMED, EventStatus.CORRECTED, EventStatus.HUMAN_VERIFIED])
def test_accepted_point_revisions_remain_available_to_analytics_and_restore(scored_rally, status):
    cfg, store, point = scored_rally
    store.append(point.correct(payload=point.payload, status=status))

    record = rally_records(store)[0]
    assert record.score_available is True
    assert record.score_after == {"P1": 1, "P2": 0}
    analytics = build(store, None, 30)
    assert analytics.score_timeline[0]["score"] == {"P1": 1, "P2": 0}
    assert analytics.players["P1"].points_won == 1
    restored = BadmintonMatchEngine("S1", cfg, store)
    restored.restore_from_log(100)
    assert restored.public_state()["score"] == {"P1": 1, "P2": 0}
    assert restored._rallies[0].record.score_available is True
