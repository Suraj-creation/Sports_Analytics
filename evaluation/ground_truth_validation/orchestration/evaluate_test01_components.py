"""Read-only Test1 component/reference diagnostics after strict fresh-run completion.

No inference, replay, annotation repairs or prediction edits. Model-generated
references are agreement diagnostics, never independent physical ground truth.
"""
from __future__ import annotations
import argparse,csv,json,hashlib,math,sys,collections
from pathlib import Path
from fractions import Fraction
import numpy as np
from scipy.optimize import linear_sum_assignment
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from research.pipeline_repair_run_analysis import load_analysis_input,load_chunks,audit_frames
from scripts.benchmarking.evaluate_rallies import Rally,read_csv,evaluate
from research.test2_evaluation import distribution
from research.pipeline_repair_run_analysis import select_live_events
TEST1_SHA='877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6'

def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def finite(v):
 try:
  n=float(v);return n if math.isfinite(n) else None
 except (TypeError,ValueError):return None
def rows(p):
 with p.open(encoding='utf-8-sig',newline='') as f:
  r=csv.DictReader(f);return r.fieldnames,list(r)
def seconds(v):
 values=v.strip().split(':')
 if len(values)>3:raise ValueError('unsupported timestamp')
 return float(sum(Fraction(t)*60**i for i,t in enumerate(values[::-1])))
def intervals(p,fps):
 fields,raw=rows(p);valid=[];source_rows=[];invalid=[];blank=[]
 for i,r in enumerate(raw,1):
  if not any(v not in ('',None) for v in r.values()):blank.append(i);continue
  try:
   if 'Start_Frame' in fields:
    sf,ef=int(r['Start_Frame']),int(r['End_Frame']);s,e=float(r['Start_Time_sec']),float(r['End_Time_sec'])
    if max(abs(s-sf/fps),abs(e-ef/fps),abs(float(r['Duration_sec'])-(e-s)))>1e-6:raise ValueError('inconsistent frame/time/duration at canonical FPS')
   elif 'start_frame' in fields:
    sf,ef=int(r['start_frame']),int(r['end_frame']);s,e=sf/fps,ef/fps
   else:
    s,e=seconds(r['start_time']),seconds(r['end_time']);sf,ef=round(s*fps),round(e*fps)
    if max(abs(sf/fps-s),abs(ef/fps-e))>1e-6:raise ValueError('timestamp is not a canonical frame boundary')
   if not 0<=sf<ef or not math.isfinite(s+e):raise ValueError('invalid positive interval')
   valid.append(Rally(sf,ef,s,e));source_rows.append(i)
  except (ValueError,TypeError,KeyError) as err:invalid.append({'source_data_row':i,'reason':str(err),'raw':r})
 return valid,source_rows,invalid,blank,raw

def reference_comparison(p,pred,fps,partial=False):
 ref,ids,bad,blank,raw=intervals(p,fps);m,cmp=evaluate(ref,pred,fps)
 for row,i in zip(cmp,ids):row['reference_data_row']=i
 result={'role':'legacy_generated_reference_agreement' if 'win_predictions' in p.name or any(s in p.name for s in ('_rally','_T.','_T4.')) else 'coarse_legacy_label_agreement' if 'Full2' not in p.name else 'partial_mixed_label_candidate', 'independent_physical_accuracy':False,'matching_policy':m['matching_policy'],'reference_source_rows':ids,'invalid_rows':bad,'blank_rows':blank,'comparison':cmp,'metrics':m,'raw_rows':raw}
 if partial:
  # Do not assign false-positive meaning to a partial/incomplete reference.
  result['partial_reference_policy']='Only supplied valid positive rows scored; unmatched current proposals remain unscored because annotation completeness is unknown. No inferred negative/coverage interval.'
  result['unscored_current_prediction_ids']=[v['pred_rally'] for v in m['unmatched_predictions']]
  result['unscored_current_predictions']=m['unmatched_predictions']
  for key in ('false_positives','precision','f1'):m['detection'][key]=None
  m['unmatched_predictions']=[]
  m['conditional_metrics_note']+=' Partial reference: precision/F1/FP unavailable; recall describes agreement only with supplied positive rows.'
 return result

def pair_points(reference,current):
 """Anonymous minimum-distance assignment; no fabricated identity or IoU."""
 if not reference or not current:return []
 a=np.asarray(reference,float);b=np.asarray(current,float);cost=np.linalg.norm(a[:,None,:]-b[None,:,:],axis=2);ii,jj=linear_sum_assignment(cost)
 return [{'reference_slot':int(i)+1,'current_index':int(j),'distance_px':float(cost[i,j])} for i,j in zip(ii,jj)]

def binding_status(binding,bound,refs):
 if binding is None:return {'status':'unverified','reason':'No source/frame/point-semantics review certificate supplied; diagnostic coordinates exported but distance metrics unavailable'}
 expected={'status':'source_and_coordinate_semantics_verified','source_sha256':bound['source_sha256'],'frame_size':[1280,720],'fps_num':30,'fps_den':1}
 for k,v in expected.items():
  if binding.get(k)!=v:raise ValueError(f'Coordinate review certificate mismatch: {k}')
 reviewed=binding.get('reviewed_frames',[])
 if not reviewed or any(type(x) is not int or not 0<=x<bound['media']['n_frames'] for x in reviewed):raise ValueError('Coordinate certificate requires actual valid reviewed frame IDs')
 if not binding.get('evidence') or not binding.get('reviewer_type'):raise ValueError('Coordinate certificate requires evidence and reviewer type')
 components={'legacy_player_point':('bbox_bottom_center','player_detections.csv'),'legacy_shuttle_point':('analysis_image_xy','Test1_Full_ball_filled.csv')}
 for key,(semantics,name) in components.items():
  if binding.get(key) is not None and binding[key]!=semantics:raise ValueError('Unsupported component point semantics: '+key)
  if binding.get(key)==semantics and binding.get('reference_sha256',{}).get(name)!=refs[name]:raise ValueError('Coordinate certificate reference hash mismatch: '+name)
 if binding.get('court_corner_semantics') is not None:
  if binding['court_corner_semantics'] not in ('outer_singles_floor_corners','outer_doubles_floor_corners'):raise ValueError('Unknown court corner semantics')
  if binding.get('reference_sha256',{}).get('Test1_Full_court.json')!=refs['Test1_Full_court.json']:raise ValueError('Court reference hash mismatch')
 return {'status':'diagnostic_coordinate_binding_declared','certificate':binding,'independent_physical_accuracy':False,'limitation':'A qualitative source-bound diagnostic review does not convert generated historical outputs into independently labelled truth'}

def evaluate_components(run,output,completion_recovery=None,coordinate_binding=None):
 run=run.resolve(strict=True);output=output.resolve()
 if output.exists() or output==run or run in output.parents:raise ValueError('Require a new output outside the immutable original run')
 # Reject unrelated videos before expensive full completion validation.
 session=read(run/'session.json')
 if session['source'].get('sha256')!=TEST1_SHA:raise ValueError('This helper requires exact original Test1 source hash; refuses Test3/other videos')
 bound=load_analysis_input(run,completion_recovery)
 media=bound['media'];fps=media['fps_num']/media['fps_den'];n=media['n_frames']
 if bound['source_sha256']!=TEST1_SHA or (media['width'],media['height'],media['fps_num'],media['fps_den'],n)!=(1280,720,30,1,17268):raise ValueError('Test1 canonical source contract differs; explicit mapping required')
 annotations=ROOT/'Part2/dataset/Test1_Full';paths=sorted(p for p in annotations.iterdir() if p.is_file());hashes={p.name:sha(p) for p in paths}
 consumed={str(p):sha(p) for p in bound['input_paths']};consumed[str(run/'predicted_rallies.csv')]=sha(run/'predicted_rallies.csv');consumed.update({str(p):hashes[p.name] for p in paths})
 if coordinate_binding is not None:consumed[str(coordinate_binding)]=sha(coordinate_binding)
 chunks,frames=load_chunks(bound['cache_dir'],bound['cache_sha256'],consumed);coverage,_=audit_frames(frames,n);pred=read_csv(run/'predicted_rallies.csv',fps)
 evpath=bound['events_path'];consumed[str(evpath)]=sha(evpath);live=select_live_events([json.loads(x) for x in evpath.read_text().splitlines() if x.strip()],session['session_id'])
 ends=sorted((x['frame_start'],x['frame_end']) for x in live if x['type']=='rally_end')
 if ends!=[(x.start_frame,x.end_frame) for x in pred]:raise ValueError('Prediction export differs from original live rally ledger')
 ref_results={};applicability=[]
 for p in paths:
  item={'file':p.name,'sha256':hashes[p.name]}
  if p.suffix=='.csv':
   fields,rr=rows(p)
   if 'Start_Frame' in fields or 'start_time' in fields:
    result=reference_comparison(p,pred,fps,partial='Full2' in p.name);ref_results[p.name]=result;item.update(status='evaluated_with_disclosed_reference_role',role=result['role'],valid_positive_rows=len(result['comparison']),invalid_rows=result['invalid_rows'])
   elif fields[0]=='Frame':item.update(status='generated_trajectory_diagnostic',role='filtered/filled model estimate; no observed-vs-filled marker')
   elif 'player_1_x' in fields:item.update(status='generated_two_point_slot_diagnostic',role='points only; no boxes or stable identities')
   else:item.update(status='unsupported_schema_explicitly_recorded',columns=fields,prerequisite='Review file contents and bind an evaluation contract')
  elif p.suffix=='.json':item.update(status='court_single_frame_candidate',role='manual asserted at frame8634; source and corner interpretation require review')
  else:item.update(status='unsupported_file_type_explicitly_recorded',prerequisite='Inspect content and declare an applicable component')
  applicability.append(item)
 # Coordinate candidates are emitted for review even when no binding certificate exists.
 contract=binding_status(read(coordinate_binding) if coordinate_binding else None,bound,hashes);bound_coords=contract['status']=='diagnostic_coordinate_binding_declared';player_bound=bound_coords and contract['certificate'].get('legacy_player_point')=='bbox_bottom_center';shuttle_bound=bound_coords and contract['certificate'].get('legacy_shuttle_point')=='analysis_image_xy'
 _,shuttle=rows(annotations/'Test1_Full_ball_filled.csv');_,players=rows(annotations/'player_detections.csv')
 for rr,key in ((shuttle,'Frame'),(players,'frame_no')):
  if [int(x[key]) for x in rr]!=list(range(n)):raise ValueError('Legacy dense timeline not exactly source-frame compatible; no implicit filling/reindexing allowed')
 out_rows=[];player_dist=[];fresh_dist=[];shuttle_dist=[];presence=collections.Counter();unmatched=collections.Counter();outlier=[]
 for f,s,p in zip(frames,shuttle,players):
  fi=f['f'];legacy=[]
  for slot in (1,2):
   x,y=finite(p[f'player_{slot}_x']),finite(p[f'player_{slot}_y'])
   if x is not None and y is not None:legacy.append({'slot':slot,'xy':[x,y],'support':finite(p[f'player_{slot}_conf'])})
  current=[{'index':j,'xy':[(q['b'][0]+q['b'][2])/2,q['b'][3]],'bbox':q['b'],'track_id':q['t'],'detector_matched':q.get('dm')} for j,q in enumerate(f.get('p',[]))]
  ls=[float(s['X']),float(s['Y'])] if s['Visibility']=='1' else None;cs=f.get('s');presence[f"legacy_shuttle_visible={ls is not None},current_raw_present={cs is not None}"]+=1
  row={'frame':fi,'time_s':fi/fps,'reference_players':legacy,'current_players':current,'reference_shuttle':ls,'reference_visibility':s['Visibility'],'reference_confidence':finite(s.get('Confidence')),'current_raw_shuttle':cs,'current_association_status':(f.get('sa') or {}).get('status'),'current_view':f.get('v'),'current_calibration_state':f.get('cs'),'coordinate_binding_status':contract['status']}
  if player_bound:
   for label,candidates,dest in [('all_current_rows',current,player_dist),('fresh_detector_rows',[q for q in current if q['detector_matched'] is True],fresh_dist)]:
    assignments=pair_points([q['xy'] for q in legacy],[q['xy'] for q in candidates])
    for assignment in assignments:
     assignment['reference_slot']=legacy[assignment['reference_slot']-1]['slot'];assignment['current_index']=candidates[assignment['current_index']]['index']
    row[label+'_assignments']=assignments;dest.extend(v['distance_px'] for v in assignments);unmatched[label+'_reference_points']+=len(legacy)-len(assignments);unmatched[label+'_current_points']+=len(candidates)-len(assignments)
  if shuttle_bound:
   if ls is not None and cs is not None:
    dist=float(np.linalg.norm(np.asarray(ls)-np.asarray(cs)));shuttle_dist.append(dist);row['shuttle_disagreement_px']=dist;outlier.append({'frame':fi,'time_s':fi/fps,'distance_px':dist,'reference_xy':ls,'current_raw_xy':cs})
  out_rows.append(row)
 pointmetrics={'classification':'legacy_generated_output_disagreement; NOT physical ground-truth accuracy','coordinate_binding':contract,'frame_population':n,'legacy_player_slots_present':sum(len(v['reference_players']) for v in out_rows),'current_player_rows':sum(len(v['current_players']) for v in out_rows),'shuttle_presence_cross_counts':dict(presence),'player_bottom_center_distance_px':distribution(player_dist) if player_bound else None,'fresh_detector_bottom_center_distance_px':distribution(fresh_dist) if player_bound else None,'shuttle_raw_distance_px_both_present':distribution(shuttle_dist) if shuttle_bound else None,'unmatched_point_counts':dict(unmatched) if player_bound else None,'largest_shuttle_disagreements':sorted(outlier,key=lambda x:x['distance_px'],reverse=True)[:30],'distance_metric_prerequisite':'Optional coordinate-binding review certificate described in helper-validation.md; no confidence threshold or distance cutoff tuned to these annotations'}
 # Recover automatic court candidate without opening the original SQLite databases.
 court=read(annotations/'Test1_Full_court.json');target=court['frame_no'];fr=frames[target];chunk=next(c for c in chunks if c['start']<=target<=c['end']);court_id=chunk.get('cr');cal=[e for e in live if e['type']=='calibration' and e['frame_start']<=target and e['payload'].get('cam_ref')==court_id]
 court_result={'reference_frame':target,'reference':court,'current_content_epoch':fr.get('ce'),'current_calibration_state':fr.get('cs'),'coordinate_binding_status':contract['status'],'reference_sha256':hashes['Test1_Full_court.json'],'metric':None,'prerequisite':'Source/frame binding plus explicit outer_singles_floor_corners or outer_doubles_floor_corners interpretation of manual TL/TR/BR/BL; current VALID main-view geometry and matching calibration reference'}
 if cal and fr.get('g') and fr.get('cs')=='VALID' and fr.get('v')=='main':
  selected=max(cal,key=lambda e:e.get('seq',0));H=np.asarray(fr['g'],float).reshape(3,3)@np.asarray(selected['payload']['H'],float);world=np.array([[-3.05,6.7,1],[3.05,6.7,1],[3.05,-6.7,1],[-3.05,-6.7,1]],float);image=(H@world.T).T;image=image[:,:2]/image[:,2:3]
  if np.isfinite(image).all():
   court_result.update(current_candidate_outer_doubles_corners=dict(zip(('TL','TR','BR','BL'),image.tolist())),calibration_event_id=selected['event_id'],calibration_source=selected['payload'].get('source'),calibration_method=selected['payload'].get('method'),cache_calibration_ref=court_id,current_effective_H=H.tolist())
   sworld=world.copy();sworld[:,0]*=5.18/6.1;sim=(H@sworld.T).T;sim=sim[:,:2]/sim[:,2:3];court_result['current_candidate_outer_singles_corners']=dict(zip(('TL','TR','BR','BL'),sim.tolist()))
   semantics=contract.get('certificate',{}).get('court_corner_semantics')
   if bound_coords and semantics in ('outer_doubles_floor_corners','outer_singles_floor_corners'):
    if semantics=='outer_singles_floor_corners':image=sim
    distances={name:float(np.linalg.norm(image[i]-np.asarray(court['corners'][name]))) for i,name in enumerate(('TL','TR','BR','BL'))};court_result['metric']={'classification':'single-frame manual-reference disagreement after diagnostic agent/human review; not adjudicated all-frame calibration accuracy','declared_corner_semantics':semantics,'corner_error_px':distances,'mean_corner_error_px':float(np.mean(list(distances.values()))),'maximum_corner_error_px':max(distances.values())}
 unsupported={k:{'value':None,'status':'unavailable','prerequisite':v} for k,v in {'player_AP_mAP_IoU':'Reviewed bounding boxes and exhaustive positive/negative coverage; existing CSV has only two generated point slots','tracking_IDF1_HOTA_ID_switches_fragmentation':'Reviewed persistent athlete identities and complete box/visibility labels; generated slots are not persistent IDs','pose_PCK_OKS':'Reviewed keypoint positions/joint visibility plus scale/skeleton convention','shuttle_physical_localization_PR':'Independent reviewed coordinates/visibility and explicit observed-vs-filled flags; generated filled trajectory is diagnostic only','racket_contact_PR_F1_temporal_error':'Reviewed racket/contact times and negative windows, not rally-level labels','stroke_per_class_PR_F1_confusion':'Exhaustive per-contact stroke labels and declared taxonomy; one ball_types label per rally is insufficient','winner_outcome_accuracy_PR_F1_confusion':'Verified Player A/B mapping and source-bound adjudicated rally outcomes; win_predictions is generated and Full2 is partial/conflicting','score_sequence_accuracy':'Verified identity, point-to-rally mapping, edited-video completeness and reviewed score sequence','highlight_quality':'Reviewed highlight boundaries/relevance; rally overlap alone is only a proxy','player_analytics_accuracy':'Reviewed named-player identity and metric-specific movement/event labels'}.items()}
 outcome={'predicted_rallies':len(pred),'known_winner_outputs':sum(e['payload'].get('winner') is not None for e in live if e['type']=='rally_end'),'winner_comparison_status':'unavailable_without_source_bound_identity_and_outcome_adjudication','stroke_label_counts':dict(collections.Counter(str(e['payload'].get('stroke','unknown')) for e in live if e['type']=='stroke'))}
 result={'status':'completed_readonly_component_reference_diagnostics','test':1,'run':str(run),'session_id':session['session_id'],'completion_mode':bound['completion_mode'],'original_parent_status':bound['original_parent_status'],'source_sha256':bound['source_sha256'],'media':media,'all_annotation_files_accounted_for':len(applicability)==len(paths),'annotation_applicability':applicability,'interval_reference_comparisons':ref_results,'point_diagnostics':pointmetrics,'court_diagnostic':court_result,'unsupported_metrics':unsupported,'outcome_and_stroke_coverage':outcome,'actual_cache_component_coverage':coverage,'input_sha256':consumed,'new_inference_performed':False,'annotations_modified':False,'predictions_modified':False,'physical_accuracy_claimed':False,'helper_sha256':sha(Path(__file__))}
 if any(sha(p)!=v for p,v in consumed.items()):raise ValueError('A consumed input changed during diagnostic evaluation')
 output.mkdir(parents=True)
 (output/'component_reference_metrics.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
 with (output/'frame_point_candidates.jsonl').open('x') as f:
  for row in out_rows:f.write(json.dumps(row,allow_nan=False)+'\n')
 report=['# Test1 component/reference diagnosis','','Strict completed-run/source/cache guards passed before annotations were loaded. No new inference or prediction/annotation edits. Generated references are diagnostic agreement, not independently adjudicated physical truth.','','## Annotation applicability','','| File | Role | Evaluation status |','|---|---|---|']
 for v in applicability:report.append(f"| {v['file']} | {v['role']} | {v['status']} |")
 report+=['','## Interval reference agreement','','| Reference | Valid positives | Matched | Unmatched positive rows | Unmatched current proposals | Precision | Recall | F1 |','|---|---|---|---|---|---|---|']
 for name,v in ref_results.items():
  d=v['metrics']['detection'];report.append('| '+' | '.join(str(x) for x in (name,len(v['comparison']),d['true_positives'],d['false_negatives'],d['false_positives'],d['precision'],d['recall'],d['f1']))+' |')
 report+=['','Full2 malformed row21 and all raw rows remain in the JSON. Full2 precision/F1/unmatched-proposal false-positive meaning are unavailable because its valid20 records do not establish exhaustive coverage; no arbitrary negative interval is inferred.','','## Coordinates and court','','Coordinate contract: '+contract['status']+'. Unverified coordinate semantics produce candidates only, with metric=null. The optional review certificate cannot turn legacy generated points into independent labels. `frame_point_candidates.jsonl` preserves every frame’s legacy/current values, visibility, confidence and source diagnostics for synchronized overlays. Current shuttle distance uses raw analysis-image output, never registered-reference selected coordinates without a transformation contract.','','Court reference frame8634: candidate singles/doubles outer corners and exact calibration event/H are retained when recoverable; a corner error is reported only with the explicit reviewed singles/doubles corner semantics. No original SQLite database was opened.','','## Unavailable requested metrics','']
 for name,v in unsupported.items():report.append(f"- {name}: unavailable; requires {v['prerequisite']}.")
 report+=['','See `component_reference_metrics.json` for full row-by-row matches, malformed rows, boundary/duration/IoU metrics, coverage denominators, diagnostic point distributions (when bound), court candidates and every consumed input hash.','']
 (output/'REPORT.md').write_text('\n'.join(report));return result

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--completion-recovery',type=Path);p.add_argument('--coordinate-binding',type=Path);a=p.parse_args();r=evaluate_components(a.run,a.output,a.completion_recovery,a.coordinate_binding);print(json.dumps({'status':r['status'],'annotation_files':len(r['annotation_applicability']),'coordinate_binding':r['point_diagnostics']['coordinate_binding']['status']}))
if __name__=='__main__':main()
