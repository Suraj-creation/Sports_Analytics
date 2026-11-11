"""Independent read-only audit of finished fresh Test2 component outputs.

The enclosing full artifact orchestration can still be active; this report only
asserts the completed fresh worker and available guarded component analyses.
"""
from pathlib import Path
import collections
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
from research.pipeline_repair_run_analysis import load_analysis_input
from review_semantic_effects import EXTERNAL, compact_event, live, read, sha
import msgpack


def main():
    art = EXTERNAL / 'test_02/improved_v1'
    run = art / 'run'
    controlled = EXTERNAL / 'test_02/test2_semantic_regression_v1'
    baseline = EXTERNAL / 'test_02/baseline_v1'
    bound = load_analysis_input(run, None)
    assert bound['completion_mode'] == 'normal_completed_worker'
    assert bound['source_sha256'] == '4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a'
    assert bound['media']['n_frames'] == 29296
    output = HERE / 'fresh_component_review_v1'
    assert not output.exists()
    consumed = {str(path): sha(path) for path in bound['input_paths']}
    paths = [art/'bound_reference_diagnostics/component_reference_metrics.json', art/'analysis/technical_analysis.json', controlled/'completion.json', controlled/'semantic_regression_metrics.json', controlled/'replay/replay_manifest.json', controlled/'replay/current-events.jsonl', Path(__file__)]
    consumed.update({str(path):sha(path) for path in paths})
    metrics, analysis, completion, semantic, manifest = [read(path) for path in paths[:5]]
    assert metrics['status'] == 'completed_readonly_component_reference_diagnostics'
    assert metrics['source_sha256'] == bound['source_sha256']
    assert not metrics['physical_accuracy_claimed'] and metrics['annotations_modified'] is False and metrics['predictions_modified'] is False
    assert completion['status'] == 'completed_controlled_semantic_regression' and completion['test'] == 2
    for path in paths[4:6]:
        assert sha(path) == completion['artifact_sha256'][str(path.relative_to(controlled))]
    fresh, frozen = live(run/'events.jsonl'), live(controlled/'replay/current-events.jsonl')
    warnings = [e for e in fresh if e['type']=='racket_observation_ambiguity']
    warning_keys = {(e['frame_start'], e['payload']['owner_track_id']): e for e in warnings}
    assert len(warning_keys)==len(warnings)
    raw_rows, raw_frames, remainder_frames, all_frames = 0, set(), set(), 0
    withheld_matched, raw_field_differences, differing_frames = set(), collections.Counter(), []
    for path in sorted(Path(bound['cache_dir']).glob('*.msgpack')):
        assert sha(path)==bound['cache_sha256'][path.name]
        oldpath = baseline/'run/data/sessions'/bound['session_id']/'perception'/path.name
        assert sha(oldpath)==manifest['cache_sha256'][path.name]
        consumed[str(path)], consumed[str(oldpath)] = sha(path), sha(oldpath)
        newchunk, oldchunk = [msgpack.unpackb(p.read_bytes(), raw=False) for p in (path,oldpath)]
        assert [f['f'] for f in newchunk['frames']]==[f['f'] for f in oldchunk['frames']]
        for frame, oldframe in zip(newchunk['frames'],oldchunk['frames'],strict=True):
            all_frames+=1
            if frame!=oldframe:
                differing_frames.append(frame['f'])
                raw_field_differences.update(k for k in frame.keys()|oldframe.keys() if frame.get(k)!=oldframe.get(k))
            for person in frame['p']:
                if person.get('rk') is None:
                    continue
                raw_rows+=1
                raw_frames.add(frame['f'])
                key=(frame['f'],person['t'])
                if key in warning_keys:
                    payload=warning_keys[key]['payload']
                    assert payload['raw_candidate']==person['rk']
                    assert payload['raw_candidate_preserved'] is True and payload['semantic_admitted'] is False
                    assert payload['racket_source_frame']==person['rf']==frame['f']
                    withheld_matched.add(key)
                else:
                    remainder_frames.add(frame['f'])
    assert all_frames==29296 and len(withheld_matched)==len(warnings)==4239
    assert raw_rows==metrics['actual_cache_component_coverage']['counts']['racket_present_rows']==20568
    event_comparisons={}
    for kind in ['contact','stroke']:
        a=[compact_event(e) for e in fresh if e['type']==kind]
        b=[compact_event(e) for e in frozen if e['type']==kind]
        event_comparisons[kind]={'fresh_count':len(a),'controlled_count':len(b),'all_compact_semantic_records_equal':a==b}
    def payloads(events, kind):
        return [(e['frame_start'],e['frame_end'],e['payload']) for e in events if e['type']==kind]
    for kind in ['racket_observation_ambiguity','rally_end','highlight']:
        if kind=='rally_end':
            # IDs in rally payloads are provenance identifiers; exact source boundaries are the comparison target here.
            value=[(e['frame_start'],e['frame_end']) for e in fresh if e['type']==kind]==[(e['frame_start'],e['frame_end']) for e in frozen if e['type']==kind]
        elif kind=='highlight':
            value=[(e['frame_start'],e['frame_end'],e['payload'].get('score')) for e in fresh if e['type']==kind]==[(e['frame_start'],e['frame_end'],e['payload'].get('score')) for e in frozen if e['type']==kind]
        else:
            value=payloads(fresh,kind)==payloads(frozen,kind)
        event_comparisons[kind]={'selected_domain_values_equal':value}
    reference_comparisons={}
    for name,value in metrics['interval_reference_comparisons'].items():
        actual=value.get('metrics',value)
        expected=semantic['all_reference_comparisons'][name]['semantic_replay_metrics']
        reference_comparisons[name]={'all_saved_metrics_equal':actual==expected}
    result={
        'status':'completed_independent_fresh_component_review',
        'scope':'Completed actual fresh Test2 NN worker and existing guarded component diagnostics; enclosing artifact pipeline may still be active',
        'source_sha256':bound['source_sha256'],'fresh_cached_perception_used':bound['worker_info']['cached_perception_used'],
        'fresh_vs_original_recorded_perception':{'frames':all_frames,'different_frame_count':len(differing_frames),'differing_field_counts':dict(raw_field_differences),'different_frames':differing_frames},
        'fresh_vs_controlled_semantic':event_comparisons,'fresh_vs_controlled_reference_metrics':reference_comparisons,
        'racket_coverage':{'raw_person_candidate_rows':raw_rows,'raw_frames_with_candidate':len(raw_frames),'verified_unique_withheld_rows':len(withheld_matched),'remaining_semantic_candidate_rows':raw_rows-len(withheld_matched),'remaining_frames_with_candidate':len(remainder_frames),'withheld_fraction_of_raw_rows':len(withheld_matched)/raw_rows,'raw_coverage_all_person_rows':raw_rows/58452,'remaining_coverage_all_person_rows':(raw_rows-len(withheld_matched))/58452,'meaning':'Policy admission coverage only; remaining candidates are not certified equipment or contacts'},
        'runtime_resources':metrics['runtime_resources'],
        'point_diagnostics':{k:v for k,v in metrics['point_diagnostics'].items() if k not in ['coordinate_binding','largest_shuttle_disagreements','reference_shuttle_out_of_image_frames']},
        'court_error_px':metrics['court_diagnostic']['metric'],
        'outcome_and_stroke_coverage':metrics['outcome_and_stroke_coverage'],
        'unsupported_metrics':metrics['unsupported_metrics'],
        'executed_models_reporting_limitation':{'component_executed_models_value':metrics['executed_models'],'actual_provenance_present':True,'correct_sources':['run/inference.json:models','run/inference.json:execution_backends','analysis/technical_analysis.json:model_sets_from_actual_caches','analysis/technical_analysis.json:models_verified_during_analysis'],'meaning':'Redundant summary field looks up loaded_models while worker uses models; null does not mean absent model execution'},
        'actual_backends':bound['worker_info']['execution_backends'],
        'actual_model_identity_from_verified_analysis':analysis['models_verified_during_analysis'],
        'unknown_accuracy_remains_unavailable':True,'physical_accuracy_gain_claimed':False,
        'inputs_unchanged':True,'input_sha256':consumed,
    }
    assert all(sha(Path(path))==value for path,value in consumed.items())
    output.mkdir()
    (output/'executed_review.py').write_bytes(Path(__file__).read_bytes())
    (output/'review.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps({k:result[k] for k in ['fresh_vs_original_recorded_perception','fresh_vs_controlled_semantic','fresh_vs_controlled_reference_metrics','racket_coverage']},indent=2))

if __name__=='__main__':
    main()
