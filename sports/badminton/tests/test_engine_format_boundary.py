"""A format transition is a sequential evidence boundary with preserved history."""
import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.rally_fsm import RallyState
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.rules import MatchConfig
from bai_badminton.testing.synth import make_rally
from bai_engine.schema import Provenance
from bai_engine.store import EventStore


PROVENANCE = Provenance(model='sustained_target_court_format_v1')


def _engine(tmp_path, *, known=False):
    store = EventStore(tmp_path / 'format-boundary.sqlite', 'S1')
    engine = BadmintonMatchEngine('S1', EngineConfig(
        fps=30, frame_width=1280, frame_height=720, match_format_known=known,
        match=MatchConfig(discipline='singles'),
    ), store)
    return engine, store


def _chunk(start, positions):
    return ChunkPerception(start, start + len(positions) - 1, [
        FramePerception(start + index, xy, 0.9 if xy else 0.0)
        for index, xy in enumerate(positions)
    ])


def test_unknown_to_doubles_updates_rules_geometry_and_records_evidence(tmp_path):
    engine, store = _engine(tmp_path)
    with store:
        h = make_rally().homography
        engine.set_calibration(0, h, emit=False)
        epoch = engine._coordinate_epoch
        events = engine.set_match_format('doubles', 0, PROVENANCE, decision={'source': 'inferred'})
        assert engine.cfg.match_format_known
        assert engine.match_cfg.discipline == 'doubles'
        assert engine.cfg.match.discipline == 'doubles'
        assert engine._coordinate_epoch > epoch
        point = h.court_to_image(np.array([[2.8, 1.0]]))[0]
        assert engine.calibration[0].geometry.signed_dist(*point) > 0
        assert events and all(event.frame_start == 0 for event in events)
        assert not store.query(types=['point'])


def test_format_switch_uses_a_temporal_boundary_without_changing_old_calibration(tmp_path):
    engine, store = _engine(tmp_path, known=True)
    with store:
        h = make_rally().homography
        engine.set_calibration(0, h, emit=False)
        old_calibration = engine.calibration[0]
        engine.ingest(_chunk(0, [(600.0, 300.0), (610.0, 310.0)]))
        engine.set_match_format('doubles', 2, PROVENANCE)
        engine.ingest(_chunk(2, [None, (630.0, 330.0)]))
        assert engine._segment_breaks(0, 3).tolist() == [False, False, True, False]
        assert engine._frame_calib[0] is old_calibration
        assert engine.calibration[0] is not old_calibration
        old_point = h.court_to_image(np.array([[2.8, 1.0]]))[0]
        assert old_calibration.geometry.signed_dist(*old_point) < 0
        assert not engine._window(0, 3).shuttle.vis[2]


def test_format_change_closes_old_temporal_state_and_withholds_named_identity(tmp_path):
    engine, store = _engine(tmp_path, known=True)
    with store:
        engine.ingest(_chunk(0, [None] * 10))
        engine._handle_fsm(engine.fsm.on_contact(5), 5)
        assert engine.fsm.state is RallyState.IN_PLAY
        engine._last_contact_candidate = object()
        engine.set_match_format('doubles', 10, PROVENANCE)
        assert engine.fsm.state is RallyState.IDLE
        assert engine._last_contact_candidate is None
        assert not engine._open_contacts
        assert engine._multi_person_identity_ambiguous
        assert not store.query(types=['point'])


def test_revoking_inferred_format_returns_to_unknown_without_a_point(tmp_path):
    engine, store = _engine(tmp_path, known=True)
    with store:
        engine.ingest(_chunk(0, [None]))
        engine.set_match_format(None, 1, PROVENANCE, decision={'reason': 'new_target_epoch'})
        assert not engine.cfg.match_format_known
        assert engine._multi_person_identity_ambiguous
        assert not store.query(types=['point'])


@pytest.mark.parametrize('bad', [-1, 0.5, True, 2])
def test_format_change_requires_the_next_canonical_frame(tmp_path, bad):
    engine, store = _engine(tmp_path)
    with store:
        epoch = engine._coordinate_epoch
        with pytest.raises(ValueError, match='frame'):
            engine.set_match_format('doubles', bad, PROVENANCE)
        assert engine._coordinate_epoch == epoch
        assert not engine.cfg.match_format_known


@pytest.mark.parametrize('bad', ['auto', '', 'triples'])
def test_invalid_format_is_not_coerced(tmp_path, bad):
    engine, store = _engine(tmp_path)
    with store:
        with pytest.raises(ValueError, match='format'):
            engine.set_match_format(bad, 0, PROVENANCE)
        assert not engine.cfg.match_format_known


def test_repeating_an_unchanged_decision_is_idempotent(tmp_path):
    engine, store = _engine(tmp_path)
    with store:
        engine.set_match_format('doubles', 0, PROVENANCE)
        epoch, seq = engine._coordinate_epoch, store.last_seq()
        assert engine.set_match_format('doubles', 0, PROVENANCE) == []
        assert (engine._coordinate_epoch, store.last_seq()) == (epoch, seq)


def test_a_new_format_does_not_authorize_an_older_unknown_pending_rally(tmp_path, monkeypatch):
    from bai_badminton.engine import _PendingRally
    from bai_badminton.events.match_phase import RallyEvidence
    from bai_badminton.events.rally_fsm import RallySegment
    from bai_badminton.perception_types import ScoreReading

    engine, store = _engine(tmp_path)
    with store:
        engine.ocr.player_names = {'P1': 'Alice', 'P2': 'Bob'}
        monkeypatch.setattr(engine, '_outcome', lambda seg: ('unknown', 'unknown', 'terminal_not_observed', 0.2))
        monkeypatch.setattr(engine, '_phase_evidence', lambda seg, until: RallyEvidence(calibrated=False))
        for frame in (0, 5):
            engine.on_ocr(ScoreReading(frame, (('ALICE', 3), ('BOB', 2)), conf=0.95))
        engine.ingest(_chunk(0, [None] * 30))
        engine.set_reviewed_match_intervals([(10, 20)], Provenance(model='human'))
        engine._pending = [_PendingRally(RallySegment(10, 20, None, 'stationary'), [], None)]
        engine.set_match_format('singles', 30, PROVENANCE)
        assert not engine._pending
        ends = store.query(types=['rally_end'])
        assert len(ends) == 1 and ends[0].payload['match_format_known'] is False
        for frame in (40, 45):
            engine.on_ocr(ScoreReading(frame, (('ALICE', 4), ('BOB', 2)), conf=0.95))
        assert not store.query(types=['point'])


@pytest.mark.parametrize('known', [False, True])
def test_geometry_outcome_never_applies_a_rules_placeholder_to_unknown_format(tmp_path, monkeypatch, known):
    from types import SimpleNamespace
    from bai_badminton.components import OutcomePrediction
    from bai_badminton.events.rally_fsm import RallySegment

    engine, store = _engine(tmp_path, known=known)
    with store:
        engine.set_calibration(0, make_rally().homography, emit=False)
        engine._proc = object()
        engine._last_frame = 3
        engine._frame_calib = [engine.calibration[0]] * 4
        engine._geometry_valid = [True] * 4
        window = SimpleNamespace(frames=np.arange(4), shuttle=SimpleNamespace(
            vis=np.ones(4, dtype=bool), interp=np.zeros(4, dtype=bool), conf=np.ones(4),
            x=np.full(4, 100.), y=np.full(4, 100.)))
        monkeypatch.setattr(engine, '_window', lambda lo, hi: window)
        monkeypatch.setattr(engine, '_same_segment', lambda lo, hi: True)
        called = []
        def predict(request):
            called.append(True)
            return OutcomePrediction('out', 'near', 'controlled-terminal', .5)
        engine.outcome_inference = SimpleNamespace(predict=predict)
        result = engine._outcome(RallySegment(0, 3, None, 'stationary'))
        assert called == ([True] if known else [])
        assert result[0] == ('out' if known else 'unknown')
        if not known:
            assert result[2] == 'match_format_unknown'
