"""Current source-bound detector-layout decisions; no neural inference."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT / 'sports/badminton/src'), str(ROOT / 'engine/src')]
from bai_badminton.perception.content import ContentContinuityProviderV2, scene_change_from_dict, scene_decision_to_dict
from bai_badminton.perception.players import PlayerDetectionProbe


def main():
    fixture = ROOT / 'sports/badminton/tests/fixtures/scene_detector_layout_cases.json'
    raw = json.loads(fixture.read_text())
    provider = ContentContinuityProviderV2(mode='barrier_detector_layout_v2')
    rows = []
    for case in raw['cases']:
        p = case['probe']
        probe = PlayerDetectionProbe(p['frame_idx'], tuple(p['image_shape']), p['image_sha256'],
                  tuple(tuple(b) for b in p['boxes']), tuple(p['scores']), tuple(p['crop_box']),
                  tuple(p['admitted_indices']))
        evidence = scene_change_from_dict(case['raw_scene_evidence'], frame_idx=case['source_frame'])
        decision = provider.layout_decision(evidence, probe, detector_model='rfdetr_small@1', geometry_valid=True)
        assert decision.decision == case['expected_decision']
        rows.append({'video': case['video'], 'frame': case['source_frame'],
                     'raw_hypothesis': evidence.hypothesis, 'decision': scene_decision_to_dict(decision),
                     'tracking_barrier': provider.tracking_barrier_for_decision(decision)})
    sources = {}
    for name in ('content.py', 'scene_change.py', 'pipeline.py'):
        path = Path('sports/badminton/src/bai_badminton/perception') / name
        old = subprocess.check_output(['git', 'show', f'caa9176:{path}'], cwd=ROOT)
        sources[str(path)] = {'historical_caa9176_sha256': hashlib.sha256(old).hexdigest(),
                             'current_sha256': hashlib.sha256((ROOT / path).read_bytes()).hexdigest()}
    output = {'schema': 'test02-current-scene-recorded-probe-recomputation:v1',
              'no_neural_inference': True, 'no_annotations_used': True,
              'fixture_sha256': hashlib.sha256(fixture.read_bytes()).hexdigest(),
              'fixture_scope': raw['scope'], 'sources': sources,
              'recorded_probe_cases': len(rows),
              'barriers': sum(r['tracking_barrier'] for r in rows),
              'positive_correspondence_vetoes': [
                  {'video': r['video'], 'frame': r['frame']} for r in rows if not r['tracking_barrier']],
              'all_cases': rows,
              'missing_edit_11346_in_candidate_fixture': not any(r['video'] == 'Test2' and r['frame'] == 11346 for r in rows),
              'independent_scene_accuracy_established': False,
              'new_fullvideo_results_established': False}
    with Path(__file__).with_name('current_scene_recorded_probe_evidence.json').open('x') as stream:
        json.dump(output, stream, indent=2)
        stream.write('\n')
    print(json.dumps({k: output[k] for k in ('recorded_probe_cases', 'barriers', 'positive_correspondence_vetoes',
                                             'missing_edit_11346_in_candidate_fixture')}, indent=2))


if __name__ == '__main__':
    main()
