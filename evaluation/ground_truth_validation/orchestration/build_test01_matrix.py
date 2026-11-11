from pathlib import Path
import json
R=Path(__file__).resolve().parents[3];W=R/'evaluation/ground_truth_validation';A=R.parent/'ground-truth-validation-artifacts-20261110/test_01';B=A/'baseline_v1';P=A/'improved_v1'
def read(p):return json.loads(p.read_text())
base=read(B/'all_reference_components/component_reference_metrics.json');r=read(B/'rally_reference_evaluation/evaluation_results.json');a=read(B/'analysis/technical_analysis.json');post=read(P/'all_reference_components/component_reference_metrics.json') if (P/'all_reference_components/component_reference_metrics.json').exists() else None
rows=[]
for file,v in base['interval_reference_comparisons'].items():
 d=v.get('metrics',{}).get('detection',v.get('detection',{}));rows.append({'component':'rally interval / '+file,'reference_role':v['role'],'baseline':d,'after':None if post is None else post['interval_reference_comparisons'][file].get('metrics',{}).get('detection',post['interval_reference_comparisons'][file].get('detection',{})),'note':'Separate reference population. Full2 is partial: no false-positive/precision/F1 claim outside established completeness.' if 'Full2' in file else 'Legacy or coarse reference agreement; no physical accuracy certification inferred'})
for k,v in base['unsupported_metrics'].items():rows.append({'component':k,'reference_role':'Insufficient independent labels or mapping','baseline':None,'after':None,'note':v['prerequisite']})
bound_path=W/'test_01/diagnostics/geometry_root_cause/bound_reference_diagnostic_v1/component_reference_metrics.json'
bound_base=read(bound_path) if bound_path.exists() else None
bound_after=read(P/'bound_reference_diagnostics/component_reference_metrics.json') if (P/'bound_reference_diagnostics/component_reference_metrics.json').exists() else None
if bound_base:
 for key in ('player_bottom_center_distance_px','fresh_detector_bottom_center_distance_px','shuttle_raw_distance_px_both_present'):
  rows.append({'component':key,'reference_role':'source-bound generated-output disagreement, NOT physical accuracy','baseline':bound_base['point_diagnostics'][key],'after':None if bound_after is None else bound_after['point_diagnostics'][key],'note':'Same reviewed coordinate binding; no distance/confidence threshold fitted'})
 rows.append({'component':'court singles corners at frame8634','reference_role':'frame-specific declared manual geometry, diagnostic coordinate review','baseline':bound_base['court_diagnostic']['metric'],'after':None if bound_after is None else bound_after['court_diagnostic']['metric'],'note':'Use singles corner correspondence; doubles comparison would fabricate error'})
out={'baseline_source':str(B),'after_source':str(P) if post else None,'rows':rows,'baseline_rally_metrics':r,'baseline_component_coverage':a['component_coverage'],'outcome_and_stroke_coverage':base['outcome_and_stroke_coverage'],'point_diagnostics':base['point_diagnostics'],'court_diagnostic':base['court_diagnostic'],'pipeline_improvement_claim':'Pending fresh post-fix full-video regression' if post is None else 'See explicit before/after metrics and source change receipt; code correctness gains are distinct from video accuracy gains','test2_gate':'Do not advance automatically'}
(W/'reports/test_01_evaluation_matrix.json').write_text(json.dumps(out,indent=2)+'\n')
lines=['# Test 1 evaluation matrix and fix gates','','Fresh baseline17,268frames; actual current improved code, no annotation input. Separate all reference families. Original Part2 data and baseline remain untouched.','','| Component / reference | Reference role | Baseline values | After fixes | Limits / next action |','|---|---|---|---|---|']
for v in rows:lines.append('| '+' | '.join(str(x).replace('|','\\|').replace('\n',' ') for x in (v['component'],v['reference_role'],json.dumps(v['baseline']),json.dumps(v['after']),v['note']))+' |')
lines+=['','## Baseline primary rally scores','','| Metric | Baseline |','|---|---|']
for k,v in r['detection'].items():lines.append(f'| {k} | {v} |')
for k,v in r['overlap'].items():lines.append(f'| {k} | {v} |')
for k,v in r['boundary_and_duration_errors'].items():
 for s,z in v.items():lines.append(f'| {k}: {s} | {z} |')
lines+=['','## Interpretation','','All36rallies are matched; boundary/semantic accuracy is not perfect merely because detectionF1=1. The raw-source OCR20:20 is consistent with pixels, while provided10:9/9:10scores have incompatible conventions. Preserve unknown named identities and distinguish generated output disagreement from independently labelled accuracy.','','## Code changes and relevance','','Verified independent regression defects are being repaired in an isolated copy of the actual inherited improved code. Reopened-rally cut-frontier and repeated-score-transition vote defects are genuine contract bugs; current evidence has not shown they caused baseline Test1 errors. Nonidentity camera-foot projection is a verified mathematical invariant defect but Test1 camera matrices are identity. No video metric gain may be claimed from those unit tests alone. Fresh full-video before/after evidence is required.','','## Next-test gate','','Test2 remains gated on Test1 diagnosis, justified fixes and recorded regression comparison. Unsupported labels and ambiguous annotation conventions remain documented limitations; do not invent fixes/ground truth to report all issues solved.','']
def flatten_metrics(obj,prefix=''):
 result={}
 if isinstance(obj,dict):
  for key,value in obj.items():result.update(flatten_metrics(value,prefix+'.'+key if prefix else key))
 elif isinstance(obj,list) and obj and isinstance(obj[0],dict):
  for index,value in enumerate(obj):result.update(flatten_metrics(value,prefix+f'[{index}]'))
 else:result[prefix]=obj
 return result
lines+=['## Every saved aggregate metric, separately for each annotation family','']
for name,entry in base['interval_reference_comparisons'].items():
 before=flatten_metrics(entry.get('metrics',{}));after=flatten_metrics(post['interval_reference_comparisons'][name].get('metrics',{})) if post else {}
 lines += ['### '+name,'','| Field | Baseline | Post-fix fresh run | Numeric delta |','|---|---|---|---|']
 for key,value in before.items():
  if key.startswith('unmatched_predictions'):continue
  new=after.get(key);delta=new-value if isinstance(new,(int,float)) and not isinstance(new,bool) and isinstance(value,(int,float)) and not isinstance(value,bool) else None
  vals=(key,json.dumps(value),json.dumps(new) if post else 'pending fresh evaluation',json.dumps(delta))
  lines.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in vals)+' |')
 lines.append('')
lines+=['## Semantic output and per-frame component coverage before/after','','| Field | Baseline | Post-fix fresh run |','|---|---|---|']
for section in ('outcome_and_stroke_coverage','actual_cache_component_coverage'):
 before=flatten_metrics(base[section]);after=flatten_metrics(post[section]) if post else {}
 for key,value in before.items():
  vals=(section+'.'+key,json.dumps(value),json.dumps(after.get(key)) if post else 'pending fresh evaluation')
  lines.append('| '+' | '.join(str(v).replace('|','\\|').replace('\n',' ') for v in vals)+' |')
lines.append('')
(W/'reports/test_01_evaluation_matrix.md').write_text('\n'.join(lines))
print('Updated Test1 evaluation matrix')
