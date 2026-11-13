"""Read-only source-frame coverage decomposition, without physical GT claims."""

from pathlib import Path
from hashlib import file_digest
from collections import Counter
import json

import msgpack
import numpy as np

from bai_badminton.court import Homography
from bai_badminton.perception.players import CourtROI


ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
CANDIDATE = ROOT / 'test03-scene-continuity-20261112'
ART = ROOT / 'ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2'
OLD = ROOT / 'ground-truth-validation-artifacts-20261110/test_01/improved_v1'
OUT = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open('rb') as source:
        return file_digest(source, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    with (OUT / name).open('x') as output:
        json.dump(value, output, indent=2, allow_nan=False)
        output.write('\n')


def iou(a, b):
    a, b = np.asarray(a), np.asarray(b)
    intersection = np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2])).prod()
    return float(intersection / ((a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - intersection))


def groups(values):
    result = []
    for frame in sorted(set(values)):
        if result and result[-1][1] == frame - 1:
            result[-1][1] = frame
        else:
            result.append([frame, frame])
    return result


def main():
    import bai_badminton.perception.players as native

    assert Path(native.__file__).resolve().is_relative_to(CANDIDATE)
    summary = read(OUT / 'summary.json')
    assert summary['status'] == 'completed_independent_fresh_Test1_review_pending_source_classification'
    inputs = {str(OUT / 'summary.json'): sha(OUT / 'summary.json'), str(Path(__file__)): sha(__file__), str(Path(native.__file__)): sha(native.__file__)}
    all_frames, point_rows = {}, {}
    for arm, base in [('original', OLD), ('fresh', ART)]:
        catalog_path = base / 'run/perception_completion_catalog.json'
        inputs[str(catalog_path)] = sha(catalog_path)
        frames = []
        for row in read(catalog_path)['files']:
            path = base / 'run' / row['path']
            assert sha(path) == row['sha256']
            inputs[str(path)] = row['sha256']
            frames.extend(msgpack.unpackb(path.read_bytes(), raw=False)['frames'])
        assert [row['f'] for row in frames] == list(range(17268))
        all_frames[arm] = frames
        path = base / 'bound_reference_diagnostics/frame_point_candidates.jsonl'
        inputs[str(path)] = sha(path)
        point_rows[arm] = {row['frame']: row for row in (json.loads(line) for line in path.open())}
    differences = read(OUT / 'point_population_decomposition.json')['original_versus_fresh']['all_current_rows_assignments']
    removed_keys = differences['old_only_keys']
    assert len(removed_keys) == 57
    events_path = ART / 'run/events.jsonl'
    inputs[str(events_path)] = sha(events_path)
    calibration = next(json.loads(line) for line in events_path.open() if json.loads(line)['type'] == 'calibration')
    reference_H = np.asarray(calibration['payload']['H'])
    anchors, frame_anchors, fg_last, frame_fg_last = {}, {}, {}, {}
    for frame in all_frames['fresh']:
        number = frame['f']
        if frame['g'] is not None:
            h = Homography(np.asarray(frame['g']).reshape(3, 3) @ reference_H, 0., 4)
            roi = CourtROI(np.zeros((4, 2), np.float32), homography=h)
            for person in frame['p']:
                key = (frame['sh'], frame['ce'], person['rt'])
                if person['dm'] is True and roi.contains_feet(np.asarray(person['b'])):
                    anchors[key] = number
        frame_anchors[number] = {str(key[2]): value for key, value in anchors.items() if key[:2] == (frame['sh'], frame['ce'])}
        for region in frame.get('fg', []):
            if region['detector_matched'] is True and region['detector_observed'] is True:
                fg_last[region['key']] = number
        frame_fg_last[number] = dict(fg_last)
    removed = []
    focus = set()
    for number, slot in removed_keys:
        original = point_rows['original'][number]
        pair = next(row for row in original['all_current_rows_assignments'] if row['reference_slot'] == slot)
        old_player = original['current_players'][pair['current_index']]
        old_person = next(row for row in all_frames['original'][number]['p'] if row['t'] == old_player['track_id'])
        fresh = all_frames['fresh'][number]
        candidates = [(iou(old_player['bbox'], region['bbox']), region) for region in fresh['fg']]
        overlap, region = max(candidates, key=lambda item: item[0])
        assert overlap > .99
        diagnostic = (fresh.get('dg') or {}).get('players') or {}
        confidences = [{'bbox': row['bbox'], 'uncalibrated_detector_support': row['support']} for row in diagnostic.get('roi_rejected', []) if iou(row['bbox'], region['bbox']) > .99]
        anchor = frame_anchors[number].get(str(old_person['rt']))
        removed.append({'frame': number, 'seconds': number / 30, 'legacy_reference_slot': slot, 'original_matched_distance_px': pair['distance_px'], 'original_person': {key: old_person[key] for key in ['t', 'rt', 'b', 'c', 'dm']}, 'fresh_participant_count': len(fresh['p']), 'fresh_scene_foreground': region, 'original_person_to_fresh_scene_region_iou': overlap, 'reconstructed_last_in_court_anchor': anchor, 'court_anchor_age_frames': number - anchor if anchor is not None else None, 'foreground_last_fresh_matched_frame': frame_fg_last[number].get(region['key']), 'foreground_age_frames': number - frame_fg_last[number][region['key']], 'current_foreground_confidence_field': None, 'current_foreground_confidence_status': 'UNAVAILABLE_field_not_in_scene_only_contract; not copied from historical person confidence', 'current_diagnostic_detector_support': confidences if confidences else None, 'coverage_classification': 'Participant evidence withheld; same image region retained separately for scene continuity. Physical role/recall requires source review; generated legacy slot is not identity GT.'})
    gross_removed = [number for number in range(17268) if len(all_frames['fresh'][number]['p']) < len(all_frames['original'][number]['p'])]
    gross_added = [number for number in range(17268) if len(all_frames['fresh'][number]['p']) > len(all_frames['original'][number]['p'])]
    populations = {'frames_with_fewer_participants': len(gross_removed), 'fewer_participant_groups': groups(gross_removed), 'gross_withheld_person_rows': sum(len(all_frames['original'][n]['p']) - len(all_frames['fresh'][n]['p']) for n in gross_removed), 'frames_with_more_participants': len(gross_added), 'more_participant_groups': groups(gross_added), 'gross_additional_person_rows': sum(len(all_frames['fresh'][n]['p']) - len(all_frames['original'][n]['p']) for n in gross_added)}
    visible = []
    for number in [6372, 6373, 6374, 6375, 6376, 6381, 7800, 7801, 7805, 7806, 7812, 7854, 7856, 8086, 8087, 8105]:
        focus.add(number)
        visible.append({'frame': number, 'original_persons': [{key: row[key] for key in ['t', 'rt', 'b', 'c', 'dm']} for row in all_frames['original'][number]['p']], 'fresh_persons': [{key: row[key] for key in ['t', 'rt', 'b', 'c', 'dm']} for row in all_frames['fresh'][number]['p']], 'foreground_regions': all_frames['fresh'][number]['fg'], 'original_legacy_reference_points': point_rows['original'][number]['reference_players'], 'original_assignments': point_rows['original'][number]['all_current_rows_assignments'], 'fresh_assignments': point_rows['fresh'][number]['all_current_rows_assignments']})
    write('coverage_tradeoffs.json', {'scope': 'Explicit gross coverage loss plus original-only generated-reference pair decomposition, never physical recall/ID accuracy', 'original_only_pair_count': len(removed), 'original_only_pair_groups': groups([row[0] for row in removed_keys]), 'all_57_rows': removed, 'gross_participant_population_changes': populations, 'source_control_rows': visible, 'known_limits': ['Foreground regions contain no confidence value; detailed current detector support is retained only on diagnostic frames', 'Current image context is not participant identity/authority', 'Legacy-generated slot visibility does not label every actual offcourt athlete'], 'all_consumed_inputs_unchanged': True, 'input_sha256': inputs})
    write('coverage_tradeoff_frame_plan.json', {'source_sha256': summary['source_sha256'], 'proxy_sha256': read(ART / 'run/inference.json')['proxy_sha256'], 'frames': [{'frame': number, 'reasons': ['Explicit participant authority/coverage loss and retained scene-only context control']} for number in sorted(focus)], 'scope': 'Additional coverage cases; supplements immutable45-frame actual-change plan'})
    assert all(sha(path) == expected for path, expected in inputs.items())
    print(json.dumps({'original_only_pair_groups': groups([row[0] for row in removed_keys]), 'gross_population': populations, 'fg_matched_flags': dict(Counter(row['fresh_scene_foreground']['detector_matched'] for row in removed)), 'current_confidence_diagnostic_rows': sum(row['current_diagnostic_detector_support'] is not None for row in removed)}))


if __name__ == '__main__':
    main()
