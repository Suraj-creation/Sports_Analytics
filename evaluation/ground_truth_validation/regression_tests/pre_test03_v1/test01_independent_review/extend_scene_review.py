"""Read-only source/cache reconstruction of the two failed Test1 cut controls.

Execute with the frozen candidate on PYTHONPATH. No models or inference are used.
This is a diagnostic ledger, not an alternative evaluation/matching policy.
"""

from pathlib import Path
from hashlib import file_digest
import json

import msgpack
import numpy as np

from bai_badminton.court import Homography
from bai_badminton.perception.players import CourtROI


ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
CANDIDATE = ROOT / 'test03-pipeline-improvements-20261111'
ART = ROOT / 'ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01'
OLD = ROOT / 'ground-truth-validation-artifacts-20261110/test_01/improved_v1/run'
OUT = MAIN / 'evaluation/ground_truth_validation/regression_tests/pre_test03_v1/test01_independent_review'


def sha(path):
    with Path(path).open('rb') as source:
        return file_digest(source, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(name, value):
    with (OUT / name).open('x') as target:
        json.dump(value, target, indent=2, allow_nan=False)
        target.write('\n')


def main():
    import bai_badminton.perception.players as players

    assert Path(players.__file__).resolve().is_relative_to(CANDIDATE)
    plan = read(ART / 'protocol/plan.json')
    assert all(sha(path) == value for path, value in plan['source_files_sha256'].items())
    frames = {}
    consumed = {}
    for arm, run, catalogue in (
        ('before', OLD, ART / 'before_catalogue.json'),
        ('after', ART / 'run', ART / 'run/perception_completion_catalog.json'),
    ):
        consumed[str(catalogue)] = sha(catalogue)
        records = []
        for entry in read(catalogue)['files']:
            # Start before the last positive anchors and include reacquisition.
            segment = int(Path(entry['path']).stem.split('_')[-1])
            if not 7500 <= segment * 60 <= 8160:
                continue
            path = run / entry['path']
            assert sha(path) == entry['sha256']
            consumed[str(path)] = entry['sha256']
            records.extend(msgpack.unpackb(path.read_bytes(), raw=False)['frames'])
        frames[arm] = {frame['f']: frame for frame in records}

    events = ART / 'run/events.jsonl'
    consumed[str(events)] = sha(events)
    calibration = next(json.loads(line) for line in events.open() if json.loads(line)['type'] == 'calibration')
    reference_H = np.array(calibration['payload']['H'])
    ledger = []
    leases = []
    for raw_id, start, cut in [(1, 7600, 7857), (4, 7950, 8106)]:
        history = []
        for number, frame in frames['after'].items():
            if not start <= number <= cut:
                continue
            effective_H = np.array(frame['g']).reshape(3, 3) @ reference_H
            homography = Homography(effective_H, 0.0, 4)
            roi = CourtROI(np.zeros((4, 2), np.float32), homography=homography)
            for person in frame['p']:
                if person['rt'] != raw_id:
                    continue
                bbox = np.array(person['b'])
                feet = np.array([[(bbox[0] + bbox[2]) / 2, bbox[3]]])
                history.append({
                    'frame': number,
                    'seconds': number / 30,
                    'raw_track_id': raw_id,
                    'bbox': person['b'],
                    'fresh_matched': bool(frame['do'] and person['dm']),
                    'contains_feet_in_existing_padded_policy': roi.contains_feet(bbox),
                    'floor_projection_m': homography.image_to_court(feet)[0].tolist(),
                    'calibration_state': frame['cs'],
                    'calibration_reference': calibration['event_id'],
                })
        anchor = [row for row in history if row['fresh_matched'] and row['contains_feet_in_existing_padded_policy']][-1]
        last = history[-1]
        expiry = anchor['frame'] + 31
        assert last['frame'] == expiry - 1
        assert all(not any(p['rt'] == raw_id for p in frames['after'][n]['p']) for n in range(expiry, cut + 1))
        leases.append({
            'cut_frame': cut,
            'missing_prior_raw_episode': raw_id,
            'last_returned_fresh_padded_court_anchor': anchor,
            'last_returned_outside_row': last,
            'first_unreturned_frame': expiry,
            'lease_policy_frames': 30,
            'private_timestamp_status': 'not serialized; reconstructed from completed returned fresh matches and exact native candidate CourtROI predicate',
            'source_basis': 'G(frame) @ recorded calibration H; floor projection of box bottom is a gating heuristic, not athlete ground truth',
        })
        for n in sorted(set(range(expiry - 2, expiry + 2)) | set(range(cut - 3, cut + 5))):
            for arm in ['before', 'after']:
                f = frames[arm][n]
                ledger.append({
                    'cut_frame': cut, 'arm': arm, 'frame': n, 'seconds': n / 30,
                    'view': f['v'], 'calibration_state': f['cs'],
                    'content_epoch': f['ce'], 'detector_executed': f['do'],
                    'pose_stride': f['ps'],
                    'people': [{key: person.get(key) for key in ['t', 'rt', 'b', 'dm', 'pf']} for person in f['p']],
                    'raw_scene': f['cc'], 'layout_decision': f['cd'],
                })
    source_hashes = {str(CANDIDATE / rel): sha(CANDIDATE / rel) for rel in [
        'sports/badminton/src/bai_badminton/perception/players.py',
        'sports/badminton/src/bai_badminton/perception/pipeline.py',
        'sports/badminton/src/bai_badminton/perception/scene_change.py',
        'sports/badminton/src/bai_badminton/court.py',
    ]}
    dump('scene_lease_diagnostics.json', {
        'classification': 'failed_acceptance_control_source_and_cache_diagnosis',
        'source_sha256': read(ART / 'run/inference.json')['source_sha256'],
        'candidate_native_module': players.__file__,
        'candidate_commit': read(ART / 'completion.json')['candidate_commit'],
        'native_source_sha256': source_hashes,
        'source_plan_files_verified': len(plan['source_files_sha256']),
        'private_lease_timestamps_serialized': False,
        'leases': leases,
        'prior_region_inventory_rule': 'Frozen pipeline forms scene witnesses only from immediately previous returned _PlayerFrame.persons; leases can remove an actor from that inventory',
        'unknown_reason_source_derivation': 'SceneContinuityDetector.observe exits before pixel comparison and detector-layout acquisition when fewer than two prior regions; these unselected unknown records are not serialized at the two new cut frames',
        'raw_ledger': ledger,
        'input_sha256': consumed,
        'new_inference_performed': False,
        'physical_accuracy_claimed': False,
    })
    cases = []
    for cut, display_before, display_after, missing, anchor, expiry in [
        (7857, [18, 16], [20, 18], 'far-side anonymous athlete episode1', 7770, 7801),
        (8106, [20, 18], [20, 20], 'near-side anonymous athlete episode4', 8056, 8087),
    ]:
        cases.append({
            'case_id': f'Test1_actual_same_camera_edit_{cut}_c7_failed_control',
            'source_frame': cut, 'source_seconds': cut / 30,
            'previous_frame': cut - 1, 'previous_seconds': (cut - 1) / 30,
            'agent_source_review': 'same-camera edited jump; athlete layout and displayed broadcast scores change discontinuously',
            'displayed_score_before': display_before, 'displayed_score_after': display_after,
            'displayed_score_scope': 'observed broadcast text; no point-to-rally/named identity inference',
            'baseline': {'prior_regions': 2, 'raw_hypothesis': True, 'layout_decision': 'barrier', 'content_epoch_before': 3 if cut == 7857 else 4, 'content_epoch_after': 4 if cut == 7857 else 5, 'current_person_count': 0},
            'fresh_candidate': {'prior_regions': 1, 'raw_hypothesis_serialized': False, 'layout_decision_serialized': False, 'content_epoch_before': 3, 'content_epoch_after': 3, 'current_person_count': 1 if cut == 7857 else 2, 'detector_executed': cut != 7857},
            'missing_prior_region': missing,
            'reconstructed_last_court_anchor': anchor,
            'first_lease_exclusion_frame': expiry,
            'mechanism': 'Bounded target-court membership reduces source scene-witness population below unchanged two-region admission; no raw hypothesis can trigger detector-layout barrier',
            'downstream': {'stale_carried_bbox_frames': [7857, 7858, 7859], 'next_scheduled_fresh_athletes_frame': 7860} if cut == 7857 else {
                'fresh_current_athletes_available_at': 8106,
                'baseline_reacquisition_frame': 8108,
                'primary_generated_reference_row': 19,
                'reference_start_frame': 8106,
                'before_predicted_start_frame': 8111,
                'after_predicted_start_frame': 8108,
                'before_interval_iou': 0.9885057471264342,
                'after_interval_iou': 0.9942528735632171,
                'interpretation': 'Generated-reference rally start improves despite missing temporal barrier; interval score cannot certify cut safety',
            },
            'source_images': [f'source_evidence/frame_{n:05d}_new_proxy.png' for n in [cut - 1, cut]],
            'review_status': 'confirmed_source_edit_and_failed_temporal_barrier_control; physical AP/contact/identity accuracy unavailable',
            'production_fix_applied_by_this_review': False,
        })
    dump('structured_failure_cases.json', {
        'source_sha256': read(ART / 'run/inference.json')['source_sha256'],
        'candidate_commit': read(ART / 'completion.json')['candidate_commit'],
        'arm_acceptance': 'failed_acceptance_control',
        'original_frozen_failure_database_modified': False,
        'cases': cases,
    })
    assert all(sha(path) == digest for path, digest in consumed.items())
    print(json.dumps({'leases': [{'cut': r['cut_frame'], 'anchor': r['last_returned_fresh_padded_court_anchor']['frame'], 'first_exclusion': r['first_unreturned_frame']} for r in leases], 'source_files_verified': len(plan['source_files_sha256'])}))


if __name__ == '__main__':
    main()
