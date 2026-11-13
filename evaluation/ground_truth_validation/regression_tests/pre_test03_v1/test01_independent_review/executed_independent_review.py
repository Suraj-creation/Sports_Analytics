"""Read-only fresh Test1 review; production/native guards were run in candidate checkout."""
from pathlib import Path
import collections,hashlib,importlib.util,json,math
import numpy as np
import msgpack

ROOT=Path('/home/administrator/Desktop/sport-analytics/Sports_Analytics')
ART=ROOT.parent/'ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01'
OLD=ROOT.parent/'ground-truth-validation-artifacts-20261110/test_01/improved_v1'
CONTROL=ROOT.parent/'ground-truth-validation-artifacts-20261110/test_02/test1_semantic_regression_v1'
OUT=ROOT/'evaluation/ground_truth_validation/regression_tests/pre_test03_v1/test01_independent_review'
SOURCE=ROOT/'evaluation/ground_truth_validation/test_02/fixes/review_semantic_effects.py'
spec=importlib.util.spec_from_file_location('preserved_event_comparison',SOURCE);helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
sha=lambda p:hashlib.file_digest(Path(p).open('rb'),'sha256').hexdigest()
read=lambda p:json.loads(Path(p).read_text())
inputs={}
def consume(p):inputs[str(p)]=sha(p);return read(p)
def dump(name,value):
 p=OUT/name
 with p.open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def dist(values):
 a=np.asarray(values,float)
 return {'count':len(a),'mean':float(a.mean()) if len(a) else None,'median':float(np.median(a)) if len(a) else None,'maximum':float(a.max()) if len(a) else None,'p95':float(np.percentile(a,95)) if len(a) else None}
def point_file(path):
 inputs[str(path)]=sha(path)
 return {row['frame']:row for row in (json.loads(line) for line in path.open())}
def frames(run,catalog):
 result=[]
 for item in catalog['files']:
  path=run/item['path'];assert sha(path)==item['sha256'];inputs[str(path)]=item['sha256'];result.extend(msgpack.unpackb(path.read_bytes(),raw=False)['frames'])
 assert [r['f'] for r in result]==list(range(17268));return result
def iou(a,b):
 inter=np.maximum(0,np.minimum(a[2:],b[2:])-np.maximum(a[:2],b[:2])).prod();union=(a[2:]-a[:2]).prod()+(b[2:]-b[:2]).prod()-inter
 return float(inter/union) if union>0 else 0.

completion=consume(ART/'completion.json');assert completion['status']=='completed_fresh_candidate_regression_root_visual_review_pending'
verified=0
for name,digest in completion['artifact_sha256'].items():assert sha(ART/name)==digest;verified+=1
before=consume(ART/'before_components.json');after=consume(ART/'bound_reference_diagnostics/component_reference_metrics.json');oldanalysis=consume(ART/'before_analysis.json');newanalysis=consume(ART/'analysis/technical_analysis.json');oldworker=consume(ART/'before_worker.json');worker=consume(ART/'run/inference.json');parent=consume(ART/'run.executor.json');plan=consume(ART/'protocol/plan.json');semantic=consume(ART/'before_semantic_control.json');semanticreceipt=consume(ART/'before_semantic_control_completion.json')
assert sha(CONTROL/'replay/current-events.jsonl')==semanticreceipt['artifact_sha256']['replay/current-events.jsonl']
assert worker['status']==parent['status']=='completed' and worker['cached_perception_used'] is False
assert worker['profile']==oldworker['profile']
model_identity=lambda a:{group:{name:{k:v for k,v in row.items() if k in {'sha256','status'}} for name,row in models.items()} for group,models in a['models_verified_during_analysis'].items()}
assert model_identity(oldanalysis)==model_identity(newanalysis)
oldanns={x['file']:x['sha256'] for x in before['annotation_applicability']};newanns={x['file']:x['sha256'] for x in after['annotation_applicability']};assert oldanns==newanns and len(newanns)==9
assert all(v['value'] is None for v in after['unsupported_metrics'].values())
for k,v in after['input_sha256'].items():assert sha(k)==v
oldpoints=point_file(OLD/'bound_reference_diagnostics/frame_point_candidates.jsonl');newpoints=point_file(ART/'bound_reference_diagnostics/frame_point_candidates.jsonl');subsets={};curated={}
for kind in ['all_current_rows_assignments','fresh_detector_rows_assignments']:
 def mapping(rows):return {(f,p['reference_slot']):{'distance':p['distance_px'],'current':r['current_players'][p['current_index']],'row':r} for f,r in rows.items() for p in r.get(kind,[])}
 a,b=mapping(oldpoints),mapping(newpoints);common=a.keys()&b.keys();added=b.keys()-a.keys();removed=a.keys()-b.keys();deltas=[b[k]['distance']-a[k]['distance'] for k in common]
 subsets[kind]={'population':'same source-frame and legacy reference-slot assignment; not physical athlete IDs','before_all':dist([v['distance'] for v in a.values()]),'after_all':dist([v['distance'] for v in b.values()]),'common_count':len(common),'common_before':dist([a[k]['distance'] for k in common]),'common_after':dist([b[k]['distance'] for k in common]),'common_error_delta':dist(deltas),'new_only':dist([b[k]['distance'] for k in added]),'old_only':dist([a[k]['distance'] for k in removed]),'new_only_keys':sorted(added),'old_only_keys':sorted(removed),'largest_new_assignments':[{'frame':k[0],'reference_slot':k[1],'before_distance':a[k]['distance'] if k in a else None,'after_distance':b[k]['distance'],'current':b[k]['current'],'reference':b[k]['row']['reference_players']} for k in sorted(b,key=lambda k:b[k]['distance'],reverse=True)[:20]]}
 for item in subsets[kind]['largest_new_assignments'][:3]:curated.setdefault(item['frame'],set()).add(kind+' extreme generated disagreement')
shuttlecommon=[f for f in oldpoints if 'shuttle_disagreement_px' in oldpoints[f] and 'shuttle_disagreement_px' in newpoints[f]]
subsets['shuttle_same_frame_both_present']={'count':len(shuttlecommon),'before':dist([oldpoints[f]['shuttle_disagreement_px'] for f in shuttlecommon]),'after':dist([newpoints[f]['shuttle_disagreement_px'] for f in shuttlecommon])}
dump('point_subset_diagnostics.json',subsets)
oldcat=consume(ART/'before_catalogue.json');newcat=consume(ART/'run/perception_completion_catalog.json');oldframes=frames(OLD/'run',oldcat);newframes=frames(ART/'run',newcat)
oldlive=helper.live(CONTROL/'replay/current-events.jsonl');newlive=helper.live(ART/'run/events.jsonl');inputs[str(CONTROL/'replay/current-events.jsonl')]=sha(CONTROL/'replay/current-events.jsonl');inputs[str(ART/'run/events.jsonl')]=sha(ART/'run/events.jsonl')
contact=helper.compare_kind(oldlive,newlive,'contact');stroke=helper.compare_kind(oldlive,newlive,'stroke')
actor_details=[];actor_counts=collections.Counter()
for change in contact['same_anchor_changes']:
 f=change['frame'];a,b=change['before'],change['after']
 if a['hypothesis_track_id']==b['hypothesis_track_id'] and a['hypothesis_status']==b['hypothesis_status']:continue
 oldp=[p for p in oldframes[f]['p'] if p['t']==a['hypothesis_track_id']];newp=[p for p in newframes[f]['p'] if p['t']==b['hypothesis_track_id']]
 overlap=iou(np.array(oldp[0]['b']),np.array(newp[0]['b'])) if len(oldp)==len(newp)==1 else None
 category='same source image region despite episode-record change' if overlap is not None and overlap>=.5 else 'different selected image region; requires source adjudication' if overlap is not None else 'selected current raw person unavailable/unresolved'
 actor_counts[category]+=1;actor_details.append({'frame':f,'old_episode_record':a['hypothesis_track_id'],'new_episode_record':b['hypothesis_track_id'],'old_status':a['hypothesis_status'],'new_status':b['hypothesis_status'],'bbox_iou':overlap,'category':category})
for typ in [contact,stroke]:
 for x in typ['unpaired_removed']+typ['unpaired_added']:curated.setdefault(x['frame'],set()).add('unpaired contact/stroke anchor')
for x in stroke['same_anchor_changes']:
 if x['changes'].get('stroke'):curated.setdefault(x['frame'],set()).add('same-anchor predicted stroke-class change')
dump('event_differences.json',{'scope':'Latest dacc05e fixed-perception semantic events versus actual fresh candidate NN; not physical event/identity truth','contact':contact,'stroke':stroke,'anonymous_episode_changes':{'counts':dict(actor_counts),'rows':actor_details},'before_counts':dict(collections.Counter(e['type'] for e in oldlive)),'after_counts':dict(collections.Counter(e['type'] for e in newlive)),'before_stroke_labels':dict(collections.Counter(e['payload'].get('stroke','unknown') for e in oldlive if e['type']=='stroke')),'after_stroke_labels':dict(collections.Counter(e['payload'].get('stroke','unknown') for e in newlive if e['type']=='stroke'))})
rawcounts=collections.Counter();xy_displacements=[];rawranges={}
for a,b in zip(oldframes,newframes,strict=True):
 f=a['f'];rawcounts[f'raw_visible_before={a.get("s") is not None},after={b.get("s") is not None}']+=1
 if a.get('s') is not None and b.get('s') is not None:xy_displacements.append(float(np.linalg.norm(np.array(a['s'])-b['s'])))
 for key in ['do','ps','v','cs','sh','s','g']:
  if a.get(key)!=b.get(key):rawcounts[key+'_different_frames']+=1;rawranges.setdefault(key,[]).append(f)
 for label,threshold in [('person_population',None)]:
  if len(a['p'])!=len(b['p']):rawcounts[label+'_different_frames']+=1;rawranges.setdefault(label,[]).append(f)
oldbarriers={r['frame'] for r in oldanalysis['component_coverage']['scene_records'] if r['actual_barrier']};newbarriers={r['frame'] for r in newanalysis['component_coverage']['scene_records'] if r['actual_barrier']}
raw={'scope':'Raw source observations/cache fields, not physical accuracy; numeric episode/epoch IDs deliberately not scored as identity truth','counts':dict(rawcounts),'common_raw_xy_displacement_px':dist(xy_displacements),'changed_frame_lists':rawranges,'removed_scene_barriers':sorted(oldbarriers-newbarriers),'added_scene_barriers':sorted(newbarriers-oldbarriers),'coverage_before':oldanalysis['component_coverage']['counts'],'coverage_after':newanalysis['component_coverage']['counts']}
dump('raw_perception_changes.json',raw)
references={}
for name,old in before['interval_reference_comparisons'].items():
 new=after['interval_reference_comparisons'][name];assert old['role']==new['role'] and old['metrics']['detection']==new['metrics']['detection'];assert old['metrics']['matching_policy']==new['metrics']['matching_policy'];references[name]={'detection':old['metrics']['detection'],'before_mean_iou':old['metrics']['overlap']['mean_iou'],'after_mean_iou':new['metrics']['overlap']['mean_iou'],'before_errors':old['metrics']['boundary_and_duration_errors'],'after_errors':new['metrics']['boundary_and_duration_errors']}
summary={'status':'completed_independent_Test1_candidate_review','native_guard':{'root':str(ROOT.parent/'test03-pipeline-improvements-20261111'),'mode':'actual unchanged candidate load_analysis_input(run,None) separately executed; not MAIN guard rebasing','passed':True},'completion_status':completion['status'],'completion_artifacts_verified':verified,'candidate_commit':completion['candidate_commit'],'worker_source_sha256':worker['source_sha256'],'profile_exactly_unchanged':True,'actual_model_identities_equal':True,'all_nine_annotations_hash_equal':True,'all_unsupported_physical_metrics_null':True,'references':references,'event_counts':{'latest_semantic_contacts':contact['before_count'],'fresh_contacts':contact['after_count'],'candidate_shifts':len(contact['candidate_temporal_shifts']),'unpaired_removed':[r['frame'] for r in contact['unpaired_removed']],'unpaired_added':[r['frame'] for r in contact['unpaired_added']],'same_anchor_predicted_class_changes':[{'frame':r['frame'],'before':r['before']['stroke'],'after':r['after']['stroke']} for r in stroke['same_anchor_changes'] if 'stroke' in r['changes']],'anonymous_episode_change_categories':dict(actor_counts)},'point_diagnostic_subsets':{k:{x:y for x,y in v.items() if x not in ['new_only_keys','old_only_keys','largest_new_assignments']} for k,v in subsets.items()},'source_regression':{'frames':[7857,7858,7859],'scope':'Visually confirmed stale near-box carried across actual same-camera edit after losing multi-actor scene acquisition; old arm abstained. Not a labelled AP/ID/HOTA result.'},'original_rally_winners_known':sum(e['payload'].get('winner') is not None for e in oldlive if e['type']=='rally_end'),'fresh_rally_winners_known':sum(e['payload'].get('winner') is not None for e in newlive if e['type']=='rally_end'),'original_named_contact_actors':sum(e.get('actors',{}).get('player_id') is not None for e in oldlive if e['type']=='contact'),'fresh_named_contact_actors':sum(e.get('actors',{}).get('player_id') is not None for e in newlive if e['type']=='contact'),'resource_before':oldanalysis['resources'],'resource_after':newanalysis['resources'],'physical_accuracy_improvement_claimed':False,'inputs_sha256':inputs}
for f in [7854,7856,7857,7859,7860,8105,8106,8107,8108,8111,13467]:curated.setdefault(f,set()).add('Edited-transition/newmaximum/rally-start or unchangedmaximum control')
dump('visual_frame_plan_v2.json',{'source_sha256':worker['source_sha256'],'proxy_sha256':worker['proxy_sha256'],'frames':[{'frame':f,'reasons':sorted(reasons)} for f,reasons in sorted(curated.items())],'scope':'Diagnostic source-frame review only; no GT labels'})
assert all(sha(Path(k))==v for k,v in inputs.items())
dump('summary.json',summary)
(OUT/'executed_independent_review.py').write_bytes(Path(__file__).read_bytes())
print(json.dumps({'status':summary['status'],'contact_counts':summary['event_counts'],'point_subsets':summary['point_diagnostic_subsets'],'verified_artifacts':verified},indent=2))
