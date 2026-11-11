"""Compact read-only case register from completed Test2 metrics and exact replay."""
from __future__ import annotations
from collections import Counter
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
BASE = ROOT.parent / 'ground-truth-validation-artifacts-20261110/test_02/baseline_v1'
TRACE = BASE / 'diagnostic_replay/bounded_fsm_trace.jsonl'
METRICS = BASE / 'rally_reference_evaluation/supplemental_metrics.json'
OLD = ROOT / 'artifacts/benchmarking/experiments/pipeline_repair_20261105_v1/case_issue_register.json'
SOURCE = '4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a'


def sha(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def admission(value):
    if not value:
        return None
    return {k: value.get(k) for k in ('start', 'end', 'accepted', 'reason', 'witness_frames')}


def short_state(value):
    return {k: value.get(k) for k in ('state', 'start', 'tentative_end', 'end_reason', 'closed',
                                     'moving_run', 'moving_run_start', 'invisible_run', 'last_contact')}


def interval(value):
    if value is None:
        return None
    return {'frames_half_open': list(value), 'seconds_half_open': [v / 30 for v in value]}


def main():
    proof_path = BASE / 'diagnostic_replay/replay_manifest.json'
    proof = read(proof_path)
    assert proof['baseline_parity'] is True and proof['frames'] == proof['trace_step_count'] == 29296
    assert sha(TRACE) == proof['output_artifact_sha256']['bounded_fsm_trace.jsonl']
    binding_path = OUT.parent / 'current_scene_and_ocr_review/completed_snapshot_binding.json'
    binding = read(binding_path)
    assert binding['strict_completed_guard'] and binding['source_sha256'] == SOURCE
    supplemental = read(METRICS)
    old = read(OLD)
    history, evidence = {}, {}
    for case in old['cases']:
        p, expected = case.get('source_review'), case.get('source_review_sha256')
        if p and expected:
            path = ROOT / p
            assert sha(path) == expected
            assert read(path)['source_sha256'] == SOURCE
            evidence[p] = {'sha256': expected, 'source_sha256': SOURCE,
                           'role': 'Historical agent diagnostic review, not independent physical ground truth'}
        for name in case.get('fresh_case_ids', []):
            history.setdefault(name, []).append(case)
        history.setdefault(case['case_id'], []).append(case)
    steps, transitions = {}, []
    for line in TRACE.open():
        row = json.loads(line)
        before, after, update = row['before'], row['after'], row['update']
        if row['call'] == 'step':
            obs, raw = row['observation'], row['raw_perception']
            assoc = raw.get('sa') or {}
            steps[row['frame']] = {'frame': row['frame'], 'kind': obs['kind'], 'speed': obs.get('speed'),
                'context_valid': obs.get('context_valid'), 'continuation_supported': obs.get('continuation_supported'),
                'exit_return_supported': obs.get('exit_return_supported'),
                'raw_present': raw.get('s') is not None, 'raw_xy': raw.get('s'),
                'association_status': assoc.get('status'), 'association_decision': assoc.get('association_status'),
                'association_reasons': assoc.get('reasons', []), 'view': raw.get('v'), 'calibration': raw.get('cs'),
                'content_epoch': raw.get('ce'), 'people_count': len(raw.get('people', [])),
                'before_state': before['state'], 'after_state': after['state'],
                'moving_run': after.get('moving_run'), 'invisible_run': after.get('invisible_run')}
        changed = before['state'] != after['state'] or before.get('tentative_end') != after.get('tentative_end')
        update_present = any(update.get(k) is not None for k in ('started', 'cancelled_start', 'finalized'))
        if changed or update_present or row['call'] in ('on_contact_evidence', 'on_discontinuity'):
            transitions.append({'frame': row['frame'], 'seconds': row['frame']/30, 'call': row['call'],
                'available_through': row['available_through'], 'before': short_state(before),
                'after': short_state(after), 'update': update, 'observation': row.get('observation'),
                'contact_admission': after.get('contact_admission'),
                'exchange_admission': admission(after.get('exchange_admission'))})
    assert list(steps) == list(range(29296))
    # Wrapper callbacks can expose one logical update twice. Preserve one compact
    # row and its callback names; do not count these as independent events.
    logical = {}
    for row in transitions:
        key = (row['frame'], json.dumps(row['update'], sort_keys=True),
               json.dumps(row['after'], sort_keys=True))
        if key not in logical:
            logical[key] = {**row, 'wrapper_calls': [row['call']]}
        else:
            logical[key]['wrapper_calls'].append(row['call'])
            if row['call'] == 'on_contact_evidence':
                logical[key]['contact_admission'] = row['contact_admission']
    transitions = list(logical.values())
    records = []
    for case in supplemental['failure_cases']:
        reference = None if case.get('gt_start_frame') is None else (case['gt_start_frame'], case['gt_end_frame'])
        pred = (case['start_frame'], case['end_frame']) if case['matching_status'] == 'unmatched_prediction' else (
            None if case.get('pred_start_frame') is None else (case['pred_start_frame'], case['pred_end_frame']))
        base = reference or pred
        lo = max(0, min((reference or base)[0], (pred or base)[0]) - 60)
        hi = min(29296, max((reference or base)[1], (pred or base)[1]) + 60)
        selected = [s for f, s in steps.items() if base[0] <= f < base[1]]
        ctx = [t for t in transitions if lo <= t['frame'] < hi]
        finals = [t for t in transitions if pred is not None and t['update'].get('finalized') and
                  (t['update']['finalized']['start'], t['update']['finalized']['end']) == pred]
        if pred is not None:
            assert len(finals) == 1
        prior = []
        for item in history.get(case['case_id'], []):
            if item['case_id'] in {v['original_case_id'] for v in prior}:
                continue
            prior.append({'original_case_id': item['case_id'], 'issue_groups': item.get('issue_groups'),
                          'source_observation': item.get('source_observation'),
                          'source_review': item.get('source_review'),
                          'source_review_sha256': item.get('source_review_sha256'),
                          'independent_physical_labels': False})
        record = {'case_id': case['case_id'], 'matching_status': case['matching_status'],
                  'reference_role': 'Unchanged legacy-generated rally interval, not adjudicated physical boundaries',
                  'expected_reference': interval(reference), 'actual_prediction': interval(pred),
                  'metrics': {k: case.get(k) for k in ('gt_rally', 'pred_rally', 'interval_iou',
                         'start_frame_error', 'end_frame_error', 'duration_error_sec')},
                  'reference_or_prediction_observation_counts': dict(Counter(s['kind'] for s in selected)),
                  'raw_provider_absent_frames': sum(not s['raw_present'] for s in selected),
                  'association_withheld_frames': sum(s['association_status'] in ('invalid','ambiguous') for s in selected),
                  'invalid_temporal_context_frames': sum(s['context_valid'] is False for s in selected),
                  'content_epochs': sorted(set(s['content_epoch'] for s in selected)),
                  'prediction_finalization': None if not finals else finals[0],
                  'context_half_open': [lo, hi],
                  'context_candidate_cancellations': [t for t in ctx if t['update'].get('cancelled_start') is not None],
                  'context_terminal_proposals': [t for t in ctx if t['after'].get('tentative_end') is not None and
                         t['before'].get('tentative_end') != t['after'].get('tentative_end')],
                  'historical_source_diagnostic_reused': prior,
                  'physical_failure_classification': 'Unadjudicated; preserve numeric result and source uncertainty',
                  'new_temporal_software_defect_established_by_this_register': False}
        records.append(record)
    assert len(records) == 39
    focus_ranges = {'missed_edit_11346': (11335, 11410), 'G31_G32': (11690,11980),
                    'G56': (20930,21070), 'G58_walking_control': (21720,21840),
                    'G63': (23860,24060), 'G69': (27315,27360)}
    focus = {name: {'window_inclusive': [lo,hi], 'transitions': [t for t in transitions if lo<=t['frame']<=hi],
                   'selected_steps': [steps[f] for f in range(lo,hi+1)]}
             for name,(lo,hi) in focus_ranges.items()}
    consumed = {str(p.resolve()): sha(p) for p in (TRACE, METRICS, OLD, proof_path, binding_path,
                          BASE/'rally_reference_evaluation/per_rally_comparison.csv', BASE/'run/predicted_rallies.csv')}
    payload = {'schema': 'test02-current-significant-temporal-register:v1',
         'complete_source_and_replay_verified': True, 'source_sha256': SOURCE,
         'significant_case_count': len(records), 'case_ids': [r['case_id'] for r in records],
         'matching_policy_unchanged': True, 'all_original_significant_current_cases_preserved': True,
         'historical_evidence': evidence, 'input_sha256': consumed,
         'cases': records, 'production_modified': False, 'annotations_modified': False}
    for name,value in [('case_register.json', payload), ('focused_transition_evidence.json', focus)]:
        with (OUT/name).open('x') as stream:
            json.dump(value, stream, indent=2, allow_nan=False)
            stream.write('\n')
    lines = ['# Test 2 current significant-case register','',
      'All39 current significant cases are preserved. Reference intervals are unchanged legacy-generated proposals; '
      'expected means the supplied benchmark interval, not a newly verified physical serve/landing. '
      'Signed errors are prediction minus reference. Historical source comments are agent diagnostics on the exact same hashed video.','',
      '| Case | Reference frames / seconds | Actual frames / seconds | IoU | Δstart / Δend frames | Actual publication / reason |',
      '|---|---|---|---:|---|---|']
    def shown(value):
        if value is None:
            return 'Unavailable'
        a,b=value['frames_half_open'];c,d=value['seconds_half_open']
        return f'[{a},{b}) /{c:.3f}–{d:.3f}s'
    for r in records:
        m=r['metrics'];fin=r['prediction_finalization'];result=fin['update']['finalized'] if fin else None
        lines.append(f"|{r['case_id']}|{shown(r['expected_reference'])}|{shown(r['actual_prediction'])}|"
           f"{m['interval_iou'] if m['interval_iou'] is not None else 'Unavailable'}|"
           f"{m['start_frame_error']} /{m['end_frame_error']}|"
           f"{str(fin['frame'])+'/'+result['reason'] if fin else 'No matched prediction'}|")
    lines += ['', '## Per-case machine evidence and source limitations', '']
    for r in records:
        lines += [f"### {r['case_id']}", '',
            f"Reference: {shown(r['expected_reference'])}. Actual: {shown(r['actual_prediction'])}. Matching: {r['matching_status']}.", '',
            f"Observed/missing/invalid processing counts: `{r['reference_or_prediction_observation_counts']}`; "
            f"raw-provider absence {r['raw_provider_absent_frames']} frames; association withheld {r['association_withheld_frames']}; "
            f"invalid context {r['invalid_temporal_context_frames']}; epochs {r['content_epochs']}.", '']
        if r['prediction_finalization']:
            f=r['prediction_finalization'];a=f['exchange_admission'] or {}
            lines += [f"Finalized at frame{f['frame']} /{f['frame']/30:.6f}s, reason "
                      f"`{f['update']['finalized']['reason']}`; exchange admission `{a.get('reason')}`.", '']
        if r['context_candidate_cancellations']:
            cs=[f"{t['update']['cancelled_start']} at{t['frame']} ({(t['exchange_admission']or{}).get('reason')})" for t in r['context_candidate_cancellations']]
            lines += ['Nearby canceled candidates: '+ '; '.join(cs)+'.', '']
        for p in r['historical_source_diagnostic_reused']:
            lines += [f"Source diagnostic ({p['original_case_id']}): {p['source_observation']}", '']
        lines += ['Disposition: keep numeric result; source and component observations do not independently establish exact physical boundaries. '
                  'No new temporal threshold change is justified by this register alone.', '']
    with (OUT/'case_register.md').open('x') as stream:
        stream.write('\n'.join(lines))
    print('Preserved all39 significant cases; focused actual transition windows:', ', '.join(focus_ranges))


if __name__ == '__main__':
    main()
