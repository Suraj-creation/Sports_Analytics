"""Raw tracking/appearance episodes use a selected session-owned component."""
from importlib import import_module

import numpy as np
import pytest

from bai_badminton.perception.pipeline import BadmintonPerception, _Scene
from bai_badminton.perception_types import PersonObs
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.config import ModelChoice, Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry


class ControlledTracking:
    detector = pose = reid = None
    last_detector_observed = True
    last_capacity_limited = False
    last_identity_error = None
    identity_policy = {'state': 'controlled', 'policy': 'controlled-episodes-v1'}

    def __init__(self, context, config):
        self.max_players = context.max_players
        self.track_id = config['params']['track_id']
        self.resets = self.closes = 0

    def process(self, frame, image, strides):
        return [PersonObs(self.track_id, np.array([10., 20., 30., 80.]), 0.9, detector_matched=True)]

    def set_roi(self, roi):
        pass

    def on_cut(self):
        self.resets += 1

    def reset(self):
        self.resets += 1

    def close(self):
        self.closes += 1


@pytest.mark.parametrize('match_format,capacity', [('singles', 2), ('doubles', 4), ('unknown', 4)])
def test_selected_tracking_factory_feeds_real_perception_and_has_a_lifecycle(tmp_path, monkeypatch, match_format, capacity):
    api = import_module('bai_badminton.perception.components')
    registry = ComponentRegistry()
    api.register_perception_components(registry)
    registry.register(ComponentContract(
        kind='tracking', implementation='controlled', version='1', input_schema='person-frame:v1',
        output_schema='person-episodes:v1', interface=api.PERCEPTION_PORTS['tracking'], context_type=api.TrackingContext,
        supported_formats=frozenset({'singles', 'doubles', 'unknown'}), failure_policy='unavailable', stateful=True,
    ), lambda context, config: ControlledTracking(context, config))
    model_dir = tmp_path / 'models'
    model_dir.mkdir()
    (model_dir / 'manifest.yaml').write_text('models: {}\n', encoding='utf-8')
    perception = BadmintonPerception(Profile(name='tracking-choice', components={'tracking': ModelChoice(
        model='none', backend='none', implementation='controlled', params={'track_id': 42},
    )}), ModelRegistry(model_dir), 30.0, model_dir, (100, 100), match_format=match_format,
        component_registry=registry)
    monkeypatch.setattr(perception, '_scene', lambda chunk, cuts: _Scene(['main'], [0], [1.0], None, [None]))
    result = perception.process(DecodedChunk(0, [np.zeros((100, 100, 3), np.uint8)]), True)
    assert result.frames[0].persons[0].track_id == 42
    assert result.frames[0].detector_observed
    assert perception.players.max_players == capacity
    assert perception.component_metadata['tracking']['contract']['implementation'] == 'controlled'
    instance = perception.players
    perception.reset_components()
    perception.close()
    perception.close()
    assert (instance.resets, instance.closes) == (1, 1)


def test_baseline_tracking_configuration_is_part_of_cache_identity(tmp_path):
    model_dir = tmp_path / 'models'
    model_dir.mkdir()
    (model_dir / 'manifest.yaml').write_text('models: {}\n', encoding='utf-8')
    profile = Profile(name='baseline-tracking')
    perception = BadmintonPerception(profile, ModelRegistry(model_dir), 30., model_dir, match_format='unknown')
    metadata = perception.component_metadata['tracking']
    assert metadata['contract']['stateful']
    assert metadata['contract']['declaration']['state_restore'] == 'recompute_in_frame_order'
    assert metadata['contract']['implementation'] == 'court-player-episodes-v1'
    perception.close()
