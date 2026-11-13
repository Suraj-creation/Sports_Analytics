"""Read-only review of closed prefix evidence; no pipeline imports or inference."""

from hashlib import file_digest, sha256
from pathlib import Path
import json
import subprocess

import msgpack
import numpy as np


ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
CANDIDATE = ROOT / 'test03-scene-continuity-20261112'
OUT = Path(__file__).resolve().parent
PREFIX = OUT.parent / 'prefix_v1'


def sha(path):
    with Path(path).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def iou(a, b):
    a, b = np.asarray(a), np.asarray(b)
    overlap = np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2])).prod()
    return float(overlap / ((a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - overlap))


def main():
    extraction = read(OUT / 'source_extraction_receipt.json')
    summary = read(PREFIX / 'summary.json')
    data = read(PREFIX / 'test2_05505_06510.json')
    test1 = read(PREFIX / 'test1_07650_08150.json')
    inputs = dict(extraction['input_sha256'])
    inputs.update({str(path): sha(path) for path in [PREFIX / 'test1_07650_08150.json', OUT / 'source_extraction_receipt.json', Path(__file__)]})
    assert summary['status'] == 'completed_bounded_scene_foreground_probe'
    assert summary['candidate_commit'] == '7ed2f731e2d58273e381710226500f30d47e00bb'
    # The live candidate is free to evolve after the closed prefix. Verify the
    # exact immutable Git objects, never rebase/import a historical runtime.
    historical_source_count = 0
    for path, digest in summary['input_sha256'].items():
        path = Path(path)
        if path.is_relative_to(CANDIDATE):
            relative = path.relative_to(CANDIDATE)
            blob = subprocess.check_output(['/usr/bin/git', '-C', str(CANDIDATE), 'show', f'{summary["candidate_commit"]}:{relative}'])
            assert sha256(blob).hexdigest() == digest, relative
            historical_source_count += 1
    for frame in extraction['frames']:
        path = OUT / frame['file']
        assert sha(path) == frame['sha256']
        inputs[str(path)] = frame['sha256']
    variants = {name: {row['frame']: row for row in rows} for name, rows in data['variants'].items()}
    new = variants['foreground'][6151]
    support = [region for region in new['raw_content']['regions'] if region['region']['key'] in new['raw_content']['supporting_region_keys']]
    matrix = [[iou(region['region']['bbox'], box) for box in new['decision']['detector_boxes']] for region in support]
    assert len(support) == 2 and np.asarray(matrix).shape == (2, 5) and np.count_nonzero(matrix) == 0
    assert new['decision']['decision'] == 'barrier' and new['barrier']
    assert not any(variants[name][6151]['barrier'] for name in ['original', 'c7'])
    for name in variants:
        assert variants[name][6151]['source_pts'] == 3149312
        assert variants[name][6151]['source_time_base'] == '1/15360'
        assert variants[name][6151]['source_pixels_sha256'] == new['source_pixels_sha256']
    run = ROOT / 'ground-truth-validation-artifacts-20261110/test_02/improved_v1/run'
    catalogue = read(run / 'perception_completion_catalog.json')
    entry = next(row for row in catalogue['files'] if row['path'].endswith('seg_00102.msgpack'))
    packet = run / entry['path']
    assert sha(packet) == entry['sha256']
    inputs[str(packet)] = entry['sha256']
    original_actual = [row for row in msgpack.unpackb(packet.read_bytes(), raw=False)['frames'] if 6148 <= row['f'] <= 6154]
    assert len(original_actual) == 7
    actual = next(row for row in original_actual if row['f'] == 6151)
    assert actual['ce'] == 8 and actual['do'] is False
    assert actual['cc']['hypothesis'] is False and actual['cd'] is None
    # Recompute the exact existing0.3 image-box ambiguity gate for the separate
    # unresolved Test1 source case without importing changing candidate code.
    rows1 = {row['frame']: row for row in test1['variants']['foreground']}
    prior = next(region for region in rows1[7800]['foreground_regions'] if region['key'] == 'court-origin:0')
    ambiguity = []
    for frame in [7806, 7812]:
        detector = next(row for row in test1['detector_inputs'] if row['frame'] == frame)
        origin = rows1[frame]['tracking_diagnostic']['crop_origin']
        boxes = np.asarray(detector['boxes_crop']) + [*origin, *origin]
        overlaps = [iou(prior['bbox'], box) for box in boxes]
        ambiguity.append({'frame': frame, 'last_unambiguous_frame': 7800, 'age_frames': frame - 7800, 'existing_iou_gate': 0.3, 'raw_boxes': boxes.tolist(), 'iou_to_last_unambiguous_box': overlaps, 'qualifying_raw_indices': [i for i, value in enumerate(overlaps) if value >= .3], 'actual_foreground_after': rows1[frame]['foreground_regions']})
    write('decision_evidence.json', {
        'scope': 'Agent source review and exact completed prefix/cache diagnostics; no physical annotation or aggregate accuracy metric',
        'source_sha256': extraction['source_sha256'], 'proxy_sha256': extraction['proxy_sha256'],
        'candidate_prefix_commit': summary['candidate_commit'],
        'historical_candidate_Git_blobs_verified': historical_source_count,
        'live_candidate_imported_or_assumed_unchanged': False,
        'source_diagnosis': {'previous_frame': 6150, 'previous_seconds': 205., 'current_frame': 6151, 'current_seconds': 6151 / 30, 'display_before': {'AXELSEN': 10, 'ANTONSEN': 13}, 'display_after': {'AXELSEN': 10, 'ANTONSEN': 14}, 'visual_status': 'confirmed_same_camera_edited_jump_with_discontinuous_athlete_layout', 'score_scope': 'Observed broadcast text only; no point decision, athlete-track name binding or outcome GT manufactured'},
        'support_to_all_raw_current_iou': matrix,
        'support_regions': support,
        'new_decision': new['decision'],
        'source_bound_prefix_rows': {name: [rows[frame] for frame in range(6148, 6155)] for name, rows in variants.items()},
        'actual_original_full_NN_cache_rows': original_actual,
        'Test1_ambiguous_memory_case': ambiguity,
        'new_inference_performed_by_review': False,
        'original_prefix_or_annotations_modified': False,
        'input_sha256': inputs,
    })
    assert all(sha(path) == digest for path, digest in inputs.items())
    print(json.dumps({'status': 'completed_read_only_source_review', '6151': 'genuine_same_camera_edit', 'historical_candidate_files_verified': historical_source_count, 'ambiguity': [(row['frame'], row['qualifying_raw_indices']) for row in ambiguity]}))


if __name__ == '__main__':
    main()
