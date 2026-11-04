"""All-image HUD acquisition is explicit and never labels an analysis skip a replay."""
from importlib import import_module

import numpy as np
import pytest
from test_plugin_discipline import make_session
from test_scoreboard_acquisition_cadence import _chunk, _perception

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import ScoreReading
from bai_badminton.score_ocr import ScoreReconciler
from bai_engine.decode import DecodedChunk
from bai_engine.store import EventStore


def _context(**kwargs):
    return import_module('bai_badminton.perception_types').ScoreObservationContext(**kwargs)


@pytest.mark.parametrize('view', ['none', 'alt'])
def test_optin_acquires_source_overlay_from_non_main_images_with_unknown_replay_status(tmp_path, monkeypatch, view):
    perception = _perception(tmp_path, monkeypatch, 'singles', views=[view] * 4,
                             scene_policy='all_image_broadcast_overlay')
    result = perception.process(_chunk(0, 4), in_play=True)
    assert [reading.frame_idx for reading in result.ocr] == [0, 3]
    assert all(frame.replay for frame in result.frames), 'analysis exclusion stays a separate legacy mask'
    for reading in result.ocr:
        assert reading.context.view == view
        assert reading.context.analysis_excluded is True
        assert reading.context.actual_replay_status == 'unknown'
        assert reading.context.acquisition_policy == 'all_image_broadcast_overlay'


def test_default_main_policy_keeps_existing_exclusion_and_records_context(tmp_path, monkeypatch):
    perception = _perception(tmp_path, monkeypatch, 'singles', views=['main', 'none', 'none', 'main'])
    result = perception.process(_chunk(0, 4), in_play=True)
    assert [reading.frame_idx for reading in result.ocr] == [0, 3]
    assert result.ocr[0].context.view == 'main'
    assert result.ocr[0].context.analysis_excluded is False
    assert result.ocr[0].context.actual_replay_status == 'unknown'


def test_explicit_replay_facts_remain_reviewable_but_never_enter_score_reconciliation(tmp_path, monkeypatch):
    perception = _perception(tmp_path, monkeypatch, 'singles', views=['none'] * 4,
                             scene_policy='all_image_broadcast_overlay', replay_status=['replay'] * 4)
    result = perception.process(_chunk(0, 4), in_play=False)
    assert len(result.ocr) == 2
    with EventStore(tmp_path / 'replay-score.sqlite', 'S1') as store:
        engine = BadmintonMatchEngine('S1', EngineConfig(fps=30, frame_width=160, frame_height=80), store)
        for reading in result.ocr:
            engine.on_ocr(reading)
        assert not engine.ocr.readings
        assert not store.query(types=['broadcast_score', 'point'])
        facts = store.query(types=['score_ocr_observation'])
        assert len(facts) == 2
        assert all(event.payload['eligible_for_scoring'] is False for event in facts)
        assert all(event.payload['context']['actual_replay_status'] == 'replay' for event in facts)


def test_direct_known_replay_observations_do_not_set_name_mapping_or_stable_score():
    reconciler = ScoreReconciler(player_names={'P1': 'Alpha', 'P2': 'Beta'})
    for frame in (0, 3):
        reading = ScoreReading(frame, (('ALPHA', 9), ('BETA', 8)), conf=.95,
                               context=_context(view='main', analysis_excluded=False,
                                                actual_replay_status='replay', acquisition_policy='main_camera'))
        assert reconciler.add(reading) is None
    assert reconciler.readings == [] and reconciler.row_map is None


def test_context_roundtrips_with_canonical_perception_cache_and_broadcast_event(tmp_path):
    plugin = make_session(tmp_path, 'singles')
    try:
        chunk = plugin.perceive(DecodedChunk(0, [np.zeros((720, 1280, 3), np.uint8)]))
        context = _context(view='none', analysis_excluded=True, actual_replay_status='unknown',
                           acquisition_policy='all_image_broadcast_overlay')
        chunk.ocr = [ScoreReading(0, (('ALPHA', 9), ('BETA', 8)), conf=.95, context=context)]
        decoded = plugin.decode_perception(plugin.encode_perception(chunk), diagnostic=True)
        assert decoded.ocr[0].context == context
        for frame in (0, 3):
            plugin.engine.on_ocr(ScoreReading(frame, (('ALPHA', 9), ('BETA', 8)), conf=.95, context=context))
        fact = plugin.store.query(types=['broadcast_score'])[-1]
        assert fact.payload['context']['analysis_excluded'] is True
        assert fact.payload['context']['actual_replay_status'] == 'unknown'
    finally:
        plugin.close()


def test_invalid_scene_policy_fails_before_loading_a_model(tmp_path, monkeypatch):
    with pytest.raises(ValueError, match='scene_policy'):
        _perception(tmp_path, monkeypatch, 'singles', scene_policy='all_images_typo')


def test_reader_replay_evidence_is_not_downgraded_by_an_unknown_scene_label(tmp_path, monkeypatch):
    perception = _perception(tmp_path, monkeypatch, 'singles', views=['main'],
                             scene_policy='all_image_broadcast_overlay')
    known = _context(view='main', analysis_excluded=False, actual_replay_status='replay',
                     acquisition_policy='all_image_broadcast_overlay')
    monkeypatch.setattr(perception.scoreboard, 'maybe_read', lambda frame, image: ScoreReading(
        frame, (('ALPHA', 9), ('BETA', 8)), conf=.95, context=known))
    result = perception.process(_chunk(0, 1), in_play=False)
    assert result.ocr[0].context.actual_replay_status == 'replay'
