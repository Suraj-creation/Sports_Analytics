"""Independent completed Test1 candidate review; no inference or original edits.

An actual candidate-native completion guard receipt is mandatory before this
script opens new metrics, events or labels. All output files are exclusive NEW.
"""

from pathlib import Path
from hashlib import file_digest, sha256
from collections import Counter
import importlib.util
import json
import math

import msgpack
import numpy as np


ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
ART = ROOT / 'ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2'
BEFORE = ROOT / 'ground-truth-validation-artifacts-20261110/test_01/improved_v1'
C7 = ROOT / 'ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01'
CONTROL = ROOT / 'ground-truth-validation-artifacts-20261110/test_02/test1_semantic_regression_v1'
CANDIDATE = ROOT / 'test03-scene-continuity-20261112'
OUT = Path(__file__).resolve().parent
SOURCE_SHA = '877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6'


def sha(path):
    with Path(path).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def dist(values):
    array = np.asarray(values, float)
    return {'count': len(array), 'mean': float(array.mean()) if len(array) else None, 'median': float(np.median(array)) if len(array) else None, 'maximum': float(array.max()) if len(array) else None, 'p95': float(np.percentile(array, 95)) if len(array) else None}


def iou(a, b):
    a, b = np.asarray(a), np.asarray(b)
    intersection = np.maximum(0, np.minimum(a[2:], b[2:]) - np.maximum(a[:2], b[:2])).prod()
    union = (a[2:] - a[:2]).prod() + (b[2:] - b[:2]).prod() - intersection
    return float(intersection / union) if union > 0 else 0.


def main():
    # Completion existence and independently executed native guards precede all
    # new reference/prediction consumption. Never import MAIN as native candidate.
    completion_path = ART / 'completion.json'
    native_path = OUT / 'native_guard_receipt.json'
    assert completion_path.is_file() and native_path.is_file()
    completion, native = read(completion_path), read(native_path)
    assert completion['status'] == 'completed_fresh_candidate_regression_root_visual_review_pending'
    assert completion['candidate_commit'] == 'c585e3507a2fef9ff393a8cfbba575a979345f53'
    assert completion['source_sha256'] == native['source_sha256'] == SOURCE_SHA
    assert native['status'] == 'passed_actual_candidate_native_strict_completion_guard' and native['native_root'] == str(CANDIDATE)
    assert completion['own_run_semantic_parity'] is True
    inputs = {str(path): sha(path) for path in [completion_path, native_path, Path(__file__)]}

    def consume(path):
        inputs[str(path)] = sha(path)
        return read(path)

    verified = 0
    for name, digest in completion['artifact_sha256'].items():
        assert sha(ART / name) == digest
        verified += 1
    for path, digest in native['input_paths_sha256'].items():
        assert sha(path) == digest
    plan = consume(ART / 'protocol/plan.json')
    assert all(sha(path) == digest for path, digest in plan['source_files_sha256'].items())
    before = consume(ART / 'before_components.json')
    after = consume(ART / 'bound_reference_diagnostics/component_reference_metrics.json')
    old_analysis = consume(ART / 'before_analysis.json')
    analysis = consume(ART / 'analysis/technical_analysis.json')
    c7analysis = consume(C7 / 'analysis/technical_analysis.json')
    worker = consume(ART / 'run/inference.json')
    old_worker = consume(ART / 'before_worker.json')
    semantic_receipt = consume(ART / 'before_semantic_control_completion.json')
    control_path = CONTROL / 'replay/current-events.jsonl'
    assert sha(control_path) == semantic_receipt['artifact_sha256']['replay/current-events.jsonl']
    assert worker['profile'] == old_worker['profile']
    model_identity = lambda item: {group: {name: {key: value for key, value in entry.items() if key in {'sha256', 'status'}} for name, entry in models.items()} for group, models in item['models_verified_during_analysis'].items()}
    assert model_identity(old_analysis) == model_identity(analysis)
    assert {row['file']: row['sha256'] for row in before['annotation_applicability']} == {row['file']: row['sha256'] for row in after['annotation_applicability']}
    assert len(after['annotation_applicability']) == 9 and len(after['unsupported_metrics']) == 10
    assert all(item['value'] is None for item in after['unsupported_metrics'].values())
    assert all(sha(path) == digest for path, digest in after['input_sha256'].items())
    method_receipt = consume(MAIN / 'evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_foreground_v1/schema_compat_independent_review_v1/receipt_final.json')
    for method in method_receipt['unchanged_evaluator_byte_and_AST_bindings']:
        assert sha(MAIN / method['file']) == sha(CANDIDATE / method['file']) == method['sha256']['main']
    helper_path = MAIN / 'evaluation/ground_truth_validation/test_02/fixes/review_semantic_effects.py'
    spec = importlib.util.spec_from_file_location('preserved_pure_event_review', helper_path)
    helper = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helper)
    inputs[str(helper_path)] = sha(helper_path)
    curated = {}

    def focus(frame, reason):
        if 0 <= frame < 17268:
            curated.setdefault(frame, set()).add(reason)

    def points(path):
        inputs[str(path)] = sha(path)
        result = {row['frame']: row for row in (json.loads(line) for line in path.open())}
        assert sorted(result) == list(range(17268))
        return result

    point_rows = {name: points(base / 'bound_reference_diagnostics/frame_point_candidates.jsonl') for name, base in [('original', BEFORE), ('c7', C7), ('fresh', ART)]}
    subsets = {}
    for arm in ['original', 'c7']:
        comparisons = {}
        for kind in ['all_current_rows_assignments', 'fresh_detector_rows_assignments']:
            def mapping(rows):
                return {(frame, pair['reference_slot']): {'distance': pair['distance_px'], 'current': row['current_players'][pair['current_index']], 'reference': row['reference_players']} for frame, row in rows.items() for pair in row.get(kind, [])}
            a, b = mapping(point_rows[arm]), mapping(point_rows['fresh'])
            common, added, removed = a.keys() & b.keys(), b.keys() - a.keys(), a.keys() - b.keys()
            top = [{'frame': key[0], 'reference_slot': key[1], 'before_distance': a[key]['distance'] if key in a else None, 'fresh_distance': b[key]['distance'], 'current': b[key]['current'], 'reference': b[key]['reference']} for key in sorted(b, key=lambda item: b[item]['distance'], reverse=True)[:20]]
            comparisons[kind] = {'population': 'same source-frame and legacy reference-slot assignment; not physical athlete identity', 'before_all': dist([row['distance'] for row in a.values()]), 'fresh_all': dist([row['distance'] for row in b.values()]), 'common_before': dist([a[key]['distance'] for key in common]), 'common_fresh': dist([b[key]['distance'] for key in common]), 'common_error_delta': dist([b[key]['distance'] - a[key]['distance'] for key in common]), 'new_only': dist([b[key]['distance'] for key in added]), 'old_only': dist([a[key]['distance'] for key in removed]), 'new_only_keys': sorted(added), 'old_only_keys': sorted(removed), 'top_fresh_disagreements': top}
            for row in top[:3]:
                focus(row['frame'], kind + ' top generated-reference disagreement')
            for key in sorted(added, key=lambda item: b[item]['distance'], reverse=True)[:3]:
                focus(key[0], kind + ' newly scored extreme')
            for key in sorted(common, key=lambda item: b[item]['distance'] - a[item]['distance'], reverse=True)[:3]:
                focus(key[0], kind + ' maximum common-pair increase versus ' + arm)
        common = [frame for frame in point_rows[arm] if 'shuttle_disagreement_px' in point_rows[arm][frame] and 'shuttle_disagreement_px' in point_rows['fresh'][frame]]
        comparisons['shuttle_common_both_present'] = {'before': dist([point_rows[arm][frame]['shuttle_disagreement_px'] for frame in common]), 'fresh': dist([point_rows['fresh'][frame]['shuttle_disagreement_px'] for frame in common])}
        subsets[arm + '_versus_fresh'] = comparisons
    for frame, row in sorted(point_rows['fresh'].items(), key=lambda item: item[1].get('shuttle_disagreement_px', -1), reverse=True)[:3]:
        focus(frame, 'largest raw-shuttle versus generated-filled disagreement')
    write('point_population_decomposition.json', subsets)
    references = {}
    for name, a in before['interval_reference_comparisons'].items():
        b = after['interval_reference_comparisons'][name]
        assert a['metrics']['matching_policy'] == b['metrics']['matching_policy']
        if name == 'Test1_Full2.csv':
            assert all(b['metrics']['detection'][key] is None for key in ['false_positives', 'precision', 'f1'])
        rows = []
        comparison_key = lambda row: ('reference', row['reference_data_row']) if 'reference_data_row' in row else ('unmatched_prediction', row.get('pred_rally'))
        old = {comparison_key(row): row for row in a['comparison']}
        current = {comparison_key(row): row for row in b['comparison']}
        for source_row in old.keys() | current.keys():
            if old.get(source_row) != current.get(source_row):
                rows.append({'comparison_key': source_row, 'reference_data_row': source_row[1] if source_row[0] == 'reference' else None, 'before': old.get(source_row), 'fresh': current.get(source_row)})
        references[name] = {'role': b['role'], 'matching_policy_unchanged': True, 'before_metrics': a['metrics'], 'fresh_metrics': b['metrics'], 'changed_reference_comparison_rows': rows}
    write('interval_reference_differences.json', references)

    def cache_frames(run, catalogue):
        records = []
        for entry in catalogue['files']:
            path = run / entry['path']
            assert sha(path) == entry['sha256']
            inputs[str(path)] = entry['sha256']
            records.extend(msgpack.unpackb(path.read_bytes(), raw=False)['frames'])
        assert [row['f'] for row in records] == list(range(17268))
        return records

    old_frames = cache_frames(BEFORE / 'run', consume(ART / 'before_catalogue.json'))
    new_frames = cache_frames(ART / 'run', consume(ART / 'run/perception_completion_catalog.json'))
    old_live = helper.live(control_path)
    new_event_path = ART / 'run/events.jsonl'
    new_live = helper.live(new_event_path)
    inputs[str(control_path)], inputs[str(new_event_path)] = sha(control_path), sha(new_event_path)
    events = {'scope': 'Latest dacc05e445-contact cached-perception semantic control versus fresh c585 pipeline; not physical event/identity truth', 'before_counts': dict(Counter(row['type'] for row in old_live)), 'fresh_counts': dict(Counter(row['type'] for row in new_live)), 'before_stroke_labels': dict(Counter(row['payload'].get('stroke', 'unknown') for row in old_live if row['type'] == 'stroke')), 'fresh_stroke_labels': dict(Counter(row['payload'].get('stroke', 'unknown') for row in new_live if row['type'] == 'stroke'))}
    for kind in ['contact', 'stroke']:
        try:
            events[kind] = helper.compare_kind(old_live, new_live, kind)
        except ValueError as error:
            before_events = {row['frame_start']: helper.compact_event(row) for row in old_live if row['type'] == kind}
            fresh_events = {row['frame_start']: helper.compact_event(row) for row in new_live if row['type'] == kind}
            changes = []
            for frame in sorted(before_events.keys() & fresh_events.keys()):
                a, b = before_events[frame], fresh_events[frame]
                delta = {key: {'before': a[key], 'after': b[key]} for key in a if a[key] != b[key]}
                if delta:
                    changes.append({'frame': frame, 'before': a, 'after': b, 'changes': delta})
            events[kind] = {'nearby_anchor_association_status': 'unavailable_rally_context_changed', 'reason': str(error), 'scope': 'Exact-anchor set differences only; no shifted-event identity inference', 'before_count': len(before_events), 'after_count': len(fresh_events), 'candidate_temporal_shifts': [], 'unpaired_removed': [before_events[frame] for frame in sorted(before_events.keys() - fresh_events.keys())], 'unpaired_added': [fresh_events[frame] for frame in sorted(fresh_events.keys() - before_events.keys())], 'same_anchor_changes': changes}
    actor_changes = []
    for row in events['contact'].get('same_anchor_changes', []):
        a, b = row['before'], row['after']
        if a['hypothesis_track_id'] == b['hypothesis_track_id'] and a['hypothesis_status'] == b['hypothesis_status']:
            continue
        frame = row['frame']
        old_person = [person for person in old_frames[frame]['p'] if person['t'] == a['hypothesis_track_id']]
        new_person = [person for person in new_frames[frame]['p'] if person['t'] == b['hypothesis_track_id']]
        overlap = iou(old_person[0]['b'], new_person[0]['b']) if len(old_person) == len(new_person) == 1 else None
        actor_changes.append({'frame': frame, 'before_episode': a['hypothesis_track_id'], 'fresh_episode': b['hypothesis_track_id'], 'before_status': a['hypothesis_status'], 'fresh_status': b['hypothesis_status'], 'current_box_iou': overlap, 'category': 'same source image region despite episode-record change' if overlap is not None and overlap >= .5 else 'different selected source image regions' if overlap is not None else 'unresolved or selected current raw person unavailable'})
    events['anonymous_actor_region_changes'] = actor_changes
    for kind in ['contact', 'stroke']:
        for row in events[kind].get('unpaired_removed', []) + events[kind].get('unpaired_added', []):
            focus(row['frame'], 'unpaired ' + kind + ' anchor')
        for row in events[kind].get('candidate_temporal_shifts', []):
            focus(row['before_frame'], 'candidate shifted ' + kind + ' before')
            focus(row['after_frame'], 'candidate shifted ' + kind + ' fresh')
    for row in events['stroke'].get('same_anchor_changes', []):
        if 'stroke' in row['changes']:
            focus(row['frame'], 'same-anchor predicted stroke-class change')
    write('event_differences.json', events)
    barrier_sets = {name: {row['frame'] for row in item['component_coverage']['scene_records'] if row['actual_barrier']} for name, item in [('original', old_analysis), ('c7', c7analysis), ('fresh', analysis)]}
    scene = {'barrier_frames': {key: sorted(value) for key, value in barrier_sets.items()}, 'new_vs_original': sorted(barrier_sets['fresh'] - barrier_sets['original']), 'lost_vs_original': sorted(barrier_sets['original'] - barrier_sets['fresh']), 'new_vs_c7': sorted(barrier_sets['fresh'] - barrier_sets['c7']), 'lost_vs_c7': sorted(barrier_sets['c7'] - barrier_sets['fresh']), 'scope': 'Recorded content epoch barriers only; source review required to classify every new/lost boundary as real edit/false reset'}
    for frame in set(scene['new_vs_original'] + scene['lost_vs_original'] + scene['new_vs_c7'] + scene['lost_vs_c7']):
        for nearby in [frame - 1, frame, frame + 1]:
            focus(nearby, 'NEW or LOST content barrier; source review mandatory')
    scene['fresh_changed_boundary_records'] = [row for row in analysis['component_coverage']['scene_records'] if row['frame'] in set(scene['new_vs_original'] + scene['lost_vs_original'] + [7857, 8106])]
    scene['repair_frame_cache_evidence'] = [{key: frame[key] for key in ['f', 'p', 'fg', 'do', 'ce', 'cc', 'cd']} for frame in new_frames if frame['f'] in [7854, 7856, 7857, 7858, 7859, 7860, 8105, 8106, 8107, 8108]]
    scene['stale_near_box_check'] = {'stale_reference_frame': 7856, 'stale_reference_box': max(old_frames[7856]['p'], key=lambda person: person['b'][3])['b'], 'scope': 'Exact known pre-edit spatial region diagnostic, not physical box AP or athlete identity'}
    stale = scene['stale_near_box_check']['stale_reference_box']
    scene['stale_near_box_check']['fresh_frames'] = [{'frame': frame, 'current_box_ious_to_old_stale_region': [iou(stale, person['b']) for person in new_frames[frame]['p']], 'detector_observed': new_frames[frame]['do'], 'person_count': len(new_frames[frame]['p'])} for frame in [7857, 7858, 7859]]
    write('scene_boundary_review_inputs.json', scene)
    for frame in [7854, 7856, 7857, 7858, 7859, 7860, 8105, 8106, 8107, 8108, 8111]:
        focus(frame, 'prior confirmed edit/stale-box/rally-start repair control')
    write('source_frame_plan.json', {'source_sha256': SOURCE_SHA, 'proxy_sha256': worker['proxy_sha256'], 'frames': [{'frame': frame, 'reasons': sorted(reasons)} for frame, reasons in sorted(curated.items())], 'scope': 'Every new/lost content barrier, predicted class change, changed contact anchors and point extremes; no physical annotation labels'})
    summary = {'status': 'completed_independent_fresh_Test1_review_pending_source_classification', 'candidate_commit': completion['candidate_commit'], 'source_sha256': SOURCE_SHA, 'completed_artifacts_verified': verified, 'source_plan_files_verified': len(plan['source_files_sha256']), 'profile_exactly_unchanged': True, 'actual_model_identity_equal': True, 'nine_annotation_hashes_equal': True, 'unsupported_physical_metric_families_null': 10, 'references': {name: {'before_detection': row['before_metrics']['detection'], 'fresh_detection': row['fresh_metrics']['detection'], 'before_mean_iou': row['before_metrics']['overlap']['mean_iou'], 'fresh_mean_iou': row['fresh_metrics']['overlap']['mean_iou'], 'changed_rows': len(row['changed_reference_comparison_rows'])} for name, row in references.items()}, 'scene_differences': {key: value for key, value in scene.items() if key not in ['fresh_changed_boundary_records', 'repair_frame_cache_evidence', 'stale_near_box_check']}, 'event_counts': {'before': events['before_counts'], 'fresh': events['fresh_counts'], 'before_labels': events['before_stroke_labels'], 'fresh_labels': events['fresh_stroke_labels']}, 'named_contact_actors_before_fresh': [sum(row.get('actors', {}).get('player_id') is not None for row in data if row['type'] == 'contact') for data in [old_live, new_live]], 'known_rally_winners_before_fresh': [sum(row['payload'].get('winner') is not None for row in data if row['type'] == 'rally_end') for data in [old_live, new_live]], 'resource_before': old_analysis['resources'], 'resource_fresh': analysis['resources'], 'all_current_raw_coverage_before': old_analysis['component_coverage']['counts'], 'all_current_raw_coverage_fresh': analysis['component_coverage']['counts'], 'physical_accuracy_gain_claimed': False, 'no_original_files_modified': True, 'no_new_inference': True, 'input_sha256': inputs}
    assert all(sha(path) == digest for path, digest in inputs.items())
    write('summary.json', summary)
    print(json.dumps({'status': summary['status'], 'references': summary['references'], 'scenes': summary['scene_differences'], 'event_counts': summary['event_counts'], 'plan_frames': len(curated)}, indent=2))


if __name__ == '__main__':
    main()
