"""Unknown format cannot turn a configured rules placeholder into accepted points."""

from dataclasses import replace

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig, _PendingRally
from bai_badminton.events.match_phase import RallyEvidence
from bai_badminton.events.rally_fsm import RallySegment
from bai_badminton.perception_types import ScoreReading
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


@pytest.mark.parametrize('known', [False, True])
@pytest.mark.parametrize('basis', ['ocr', 'geometry'])
def test_unknown_format_withholds_point_acceptance_until_a_supported_format_is_known(tmp_path, monkeypatch, known, basis):
    store = EventStore(tmp_path / 'format-score.sqlite', 'S1')
    with store:
        engine = BadmintonMatchEngine('S1', EngineConfig(
            fps=30, frame_width=1280, frame_height=720, match_format_known=known,
        ), store, player_names={'P1': 'Alice', 'P2': 'Bob'})
        monkeypatch.setattr(engine, '_outcome', lambda seg: (
            ('winner', 'far', 'c0_static_in', 0.8) if basis == 'geometry'
            else ('unknown', 'unknown', 'terminal_not_observed', 0.2)
        ))
        monkeypatch.setattr(engine, '_phase_evidence', lambda seg, until: RallyEvidence(
            calibrated=True, scoreboard='changed' if basis == 'ocr' else None,
        ))
        if basis == 'ocr':
            for frame, score in ((0, (3, 2)), (5, (3, 2)), (300, (4, 2)), (305, (4, 2))):
                engine.on_ocr(ScoreReading(frame, (('ALICE', score[0]), ('BOB', score[1])), conf=0.95))
        engine.set_reviewed_match_intervals([(100, 200)], Provenance(model='human'))
        engine._pending = [_PendingRally(RallySegment(100, 200, None, 'stationary'), [], None)]
        engine._finalize_pending(400)
        # Geometry cannot name a winner without a reviewed physical identity,
        # even when the match format is configured. OCR supplies scoring rows.
        assert len(store.query(types=['point'])) == int(known and basis == 'ocr')
        if not known:
            assert store.query(types=['rally_end'])[-1].payload['winner'] is None
            assert engine.state.rally_no == 0


@pytest.mark.parametrize("original_known", [False, True])
@pytest.mark.parametrize("restart", [False, True])
def test_format_epoch_changes_do_not_reinterpret_historical_rally_format(
    tmp_path, monkeypatch, original_known, restart,
):
    with EventStore(tmp_path / "historical-format.sqlite", "S1") as store:
        cfg = EngineConfig(fps=30, frame_width=1280, frame_height=720, match_format_known=original_known)
        engine = BadmintonMatchEngine("S1", cfg, store, player_names={"P1": "Alice", "P2": "Bob"})
        monkeypatch.setattr(engine, "_outcome", lambda seg: ("unknown", "unknown", "terminal_not_observed", .2))
        monkeypatch.setattr(engine, "_phase_evidence", lambda seg, until: RallyEvidence(scoreboard="changed"))
        for frame, score in ((0, (3, 2)), (5, (3, 2)), (300, (4, 2)), (305, (4, 2))):
            engine.on_ocr(ScoreReading(frame, (("ALICE", score[0]), ("BOB", score[1])), conf=.95))
        engine.set_reviewed_match_intervals([(100, 200)], Provenance(model="human"))
        engine._pending = [_PendingRally(RallySegment(100, 200, None, "stationary"), [], None)]
        engine._finalize_pending(400)
        before = engine.public_state()["score"]
        assert len(store.query(types=["point"])) == int(original_known)

        # A new target/calibration epoch changes the current format decision.
        # It neither revokes earlier valid evidence nor confirms an old unknown.
        later_cfg = replace(cfg, match_format_known=not original_known)
        if restart:
            engine = BadmintonMatchEngine("S1", later_cfg, store)
            engine.restore_from_log(400)
        else:
            engine.cfg = later_cfg
        engine.set_match_start(0, Provenance(model="human"))

        assert len(store.query(types=["point"])) == int(original_known)
        assert engine.public_state()["score"] == before
