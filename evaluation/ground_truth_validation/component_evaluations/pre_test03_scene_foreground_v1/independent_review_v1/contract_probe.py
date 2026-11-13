"""Independent synthetic scene-contract smoke; no models, videos or GT labels.

Run with the new scene candidate's packages first on PYTHONPATH. Writes only a
new --output JSON receipt, after verifying the inspected source did not change.
"""

from dataclasses import asdict, replace
from hashlib import file_digest, sha256
from pathlib import Path
from unittest.mock import patch
import argparse
import json

import numpy as np

from bai_badminton.perception import scene_change
from bai_badminton.perception.content import (
    ContentContinuityProviderV2,
    SceneDecisionEvidence,
    scene_change_from_dict,
    scene_change_to_dict,
    validate_scene_decision_binding,
)
from bai_badminton.perception.foreground import CourtForegroundMemory
from bai_badminton.perception.players import PlayerDetectionProbe


ROOT = Path('/home/administrator/Desktop/sport-analytics/test03-scene-continuity-20261112')
FILES = [f'sports/badminton/src/bai_badminton/{path}' for path in [
    'perception/foreground.py', 'perception/players.py', 'perception/pipeline.py',
    'perception/scene_change.py', 'perception/content.py', 'perception/components.py',
    'perception_types.py', 'plugin.py',
]]


def digest(path):
    with Path(path).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def innovation(count=2, *, missing_features=False):
    """Actual observer/provider; only low-level flow measurements are controlled."""
    provider = ContentContinuityProviderV2(mode='barrier_detector_layout_v2')
    source = np.random.default_rng(761).integers(20, 220, (240, 600, 3), dtype=np.uint8)
    boxes = tuple((20. + k * 70, 20., 55. + k * 70, 150.) for k in range(count))
    calls = 0

    def flow(*_args):
        nonlocal calls
        pair, region = divmod(calls, count + 1)
        calls += 1
        if not region:
            return 80, 1., 1., 0.
        if missing_features:
            return 0, None, None, None
        return 40, .1 if pair == 2 else .95, 100. if pair == 2 else 3., .1

    with patch.object(scene_change, '_flow', flow):
        for frame in range(4):
            regions = [scene_change.ForegroundRegion(frame - 1, f'image:{k}', box, True, True) for k, box in enumerate(boxes)] if frame else []
            raw = provider.observe(frame, source, previous_regions=regions, previous_view_valid=True, current_view_valid=True)
    return provider, source, boxes, raw


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    assert not args.output.exists()
    assert Path(scene_change.__file__).resolve().is_relative_to(ROOT)
    before = {str(ROOT / path): digest(ROOT / path) for path in FILES}
    checks = []
    for count in [2, 4]:
        provider, source, boxes, raw = innovation(count)
        assert raw.hypothesis and len(raw.supporting_region_keys) == count
        assert scene_change_from_dict(scene_change_to_dict(raw)) == raw
        for admitted in [tuple(range(count)), (0,), ()]:
            probe = PlayerDetectionProbe(3, tuple(source.shape), sha256(source.tobytes()).hexdigest(), boxes, (.95,) * count, (0, 0, 600, 240), admitted)
            decision = provider.layout_decision(raw, probe, detector_model='synthetic-contract@1', geometry_valid=True)
            validate_scene_decision_binding(decision, raw)
            assert decision.decision == 'no_barrier' and not provider.tracking_barrier_for_decision(decision)
            assert decision.admitted_indices == admitted
            assert decision.layout_indices == tuple(range(count))
            checks.append({'case': 'complete_raw_image_correspondence_veto_independent_of_court_authority', 'regions': count, 'participant_admitted': admitted, 'decision': decision.decision})
        # Current raw duplicates make correspondence ambiguous, never positive.
        probe = PlayerDetectionProbe(3, tuple(source.shape), sha256(source.tobytes()).hexdigest(), (*boxes, boxes[0]), (.95,) * (count + 1), (0, 0, 600, 240), tuple(range(count)))
        ambiguous = provider.layout_decision(raw, probe, detector_model='synthetic-contract@1', geometry_valid=True)
        assert ambiguous.decision == 'unknown'
        assert provider.tracking_barrier_for_decision(ambiguous) is True
        checks.append({'case': 'ambiguous_raw_duplicate_keeps_explicit_unknown_experimental_fallback', 'regions': count, 'decision': ambiguous.decision, 'actual_barrier': True})
        # A historical decision cannot bypass a new supporting-witness contract.
        decision = provider.layout_decision(raw, PlayerDetectionProbe(3, tuple(source.shape), sha256(source.tobytes()).hexdigest(), boxes, (.95,) * count, (0, 0, 600, 240), tuple(range(count))), detector_model='synthetic-contract@1', geometry_valid=True)
        old = replace(decision, version='detector-layout-scene-decision:v1', supporting_region_keys=(), layout_indices=())
        try:
            validate_scene_decision_binding(old, raw)
        except ValueError:
            checks.append({'case': 'cross_version_binding_rejected', 'regions': count})
        else:
            raise AssertionError('old decision accepted for V3 raw evidence')
        forged = asdict(raw)
        forged['supporting_region_keys'] = [raw.supporting_region_keys[0]]
        try:
            scene_change_from_dict(forged)
        except ValueError:
            checks.append({'case': 'forged_witness_subset_rejected', 'regions': count})
        else:
            raise AssertionError('incomplete cohort accepted')
    _, _, _, missing = innovation(missing_features=True)
    assert missing.status == 'unknown' and not missing.hypothesis
    assert scene_change_from_dict(scene_change_to_dict(missing)).status == 'unknown'
    checks.append({'case': 'background_only_no_foreground_features_remains_unknown'})
    boxes = np.array([[20., 20., 55., 150.], [90., 20., 125., 150.]])
    memory = CourtForegroundMemory(30)
    memory.update(0, boxes, np.array([True, True]))
    snapshot = memory.at(0)
    memory.update(1, np.empty((0, 4)), np.empty(0, bool))
    assert len(memory.at(1)) == 2
    assert all(r.detector_matched is False and r.detector_observed is True for r in memory.at(1))
    assert all(r.frame == 0 for r in snapshot)
    memory.carry(30)
    assert len(memory.at(30)) == 2
    assert all(r.detector_observed is False and r.detector_matched is False for r in memory.at(30))
    memory.carry(31)
    assert memory.at(31) == ()
    try:
        memory.carry(1)
    except ValueError:
        pass
    else:
        raise AssertionError('expired foreground revived by stale frame')
    checks.append({'case': 'empty_fresh_proposals_retain_only_unmatched_bounded_estimates_then_expire_without_rewind'})
    before_reset = {r.key for r in snapshot}
    memory.reset()
    memory.update(40, boxes, np.array([True, True]))
    assert before_reset.isdisjoint({r.key for r in memory.at(40)})
    checks.append({'case': 'reset_clears_state_and_avoids_reusing_old_history_keys'})
    assert before == {str(ROOT / path): digest(ROOT / path) for path in FILES}
    with args.output.open('x') as stream:
        json.dump({'status': 'passed_independent_synthetic_read_only_contract_probe', 'source_root': str(ROOT), 'source_sha256': before, 'checks': checks, 'check_count': len(checks), 'neural_inference_performed': False, 'video_or_annotations_consumed': False, 'physical_scene_accuracy_claimed': False, 'source_unchanged_during_probe': True}, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'status': 'passed', 'checks': len(checks), 'output': str(args.output)}))


if __name__ == '__main__':
    main()
