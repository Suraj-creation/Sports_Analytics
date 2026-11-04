"""Source-transition ownership survives score refolds, retries and restart."""

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ScoreReading
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


def setup_engine(tmp_path, monkeypatch):
    store = EventStore(tmp_path / "score.sqlite", "S1")
    engine = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720),
                                  store, player_names={"P1": "Alice", "P2": "Bob"})
    monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
    monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(
        calibrated=False, scoreboard=engine.ocr.board_change(seg.start, seg.end, until, 900)))
    for frame, score in ((0, (3, 2)), (205, (3, 2)), (300, (4, 2))):
        for delta in (0, 5):
            engine.on_ocr(ScoreReading(frame + delta, (("ALICE", score[0]), ("BOB", score[1])), conf=.95))
    engine._pending = [_PendingRally(RallySegment(a, b, None, "stationary"), [], None)
                       for a, b in ((100, 200), (240, 280))]
    return engine, store


def test_source_association_is_durable_and_stays_unique_during_refold(tmp_path, monkeypatch):
    engine, store = setup_engine(tmp_path, monkeypatch)
    with store:
        engine._finalize_pending(400)
        rallies = store.query(types=["rally_end"])
        refs = [r.payload.get("score_transition") for r in rallies]
        assert all(ref is not None for ref in refs)
        assert len({ref["transition_id"] for ref in refs}) == 1
        assert len(store.query(types=["point"])) == 1
        engine.set_reviewed_match_intervals([(100, 280)], Provenance(model="review"))
        assert len(store.query(types=["point"])) == 1
        assert engine.state.score == {"P1": 1, "P2": 0}


def test_unofficial_revision_releases_transition_for_the_remaining_official_rally(tmp_path, monkeypatch):
    engine, store = setup_engine(tmp_path, monkeypatch)
    with store:
        engine._finalize_pending(400)
        engine.set_reviewed_match_intervals([(240, 280)], Provenance(model="review"))
        points = store.query(types=["point"])
        assert len(points) == 1
        assert points[0].frame_start == 280


def test_restart_rebuilds_transition_ownership_without_ocr_history(tmp_path, monkeypatch):
    engine, store = setup_engine(tmp_path, monkeypatch)
    with store:
        engine._finalize_pending(400)
        restored = BadmintonMatchEngine("S1", engine.cfg, store)
        restored.restore_from_log(400)
        assert restored.ocr.readings == []
        restored.set_reviewed_match_intervals([(100, 280)], Provenance(model="review"))
        assert len(store.query(types=["point"])) == 1
        assert restored.state.score == engine.state.score


def test_failed_point_publication_rolls_back_transition_claim_and_can_retry(tmp_path, monkeypatch):
    engine, store = setup_engine(tmp_path, monkeypatch)
    original = store.append
    failed = False

    def append(event):
        nonlocal failed
        if event.type == "point" and not failed:
            failed = True
            raise RuntimeError("controlled point failure")
        return original(event)

    with store:
        monkeypatch.setattr(store, "append", append)
        with pytest.raises(RuntimeError, match="controlled point failure"):
            engine._finalize_pending(400)
        assert store.query(types=["rally_end", "point"]) == []
        assert len(engine._pending) == 2
        ref = engine.ocr.source_transition(100, 200, 320, 900)
        assert ref is not None
        assert engine.ocr.claim_transition(ref, "probe-rollback")
        engine.ocr.clear_transition_claims()
        engine._finalize_pending(400)
        assert len(store.query(types=["point"])) == 1
