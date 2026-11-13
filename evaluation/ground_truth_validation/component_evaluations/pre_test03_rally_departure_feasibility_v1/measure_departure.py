"""CPU-only descriptive feasibility; no acquisition/admission classifier or NN."""
from __future__ import annotations
import csv,hashlib,json,math
from pathlib import Path
import numpy as np
import msgpack

HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'pre_test03_test02_regression_diagnosis_v1'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(name,value):
 with (HERE/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def main():
 receipt=json.loads((OLD/'departure_rows_receipt.json').read_text())
 for p,h in receipt['input_sha256'].items():assert sha(p)==h,p
 files=['departure_rows_receipt.json','departure_image_rows.csv','departure_body_details.json','actual_event_cases.json','actual_trace_cases.jsonl']
 inputs={str(OLD/p):sha(OLD/p) for p in files}
 rows=list(csv.DictReader((OLD/'departure_image_rows.csv').open()));assert len(rows)==876
 for r in rows:
  for k in ['frame','shot','content_epoch','raw_track']:r[k]=int(r[k])
  for k in ['shuttle_x','shuttle_y','body_center_x','body_center_y','body_height_px','distance_from_box_px','distance_from_box_body_heights','nearest_fresh_wrist_distance_px','nearest_fresh_wrist_distance_body_heights']:
   r[k]=float(r[k]) if r[k] else None
  for k in ['detector_matched','detector_observed']:r[k]=r[k]=='True'
  r['pose_source_frame']=int(r['pose_source_frame']) if r['pose_source_frame'] else None
 details=json.loads((OLD/'departure_body_details.json').read_text())['rows']
 detail={(r['arm'],r['case'],r['frame'],r['raw_track']):r for r in details}
 def point(r):return np.array([r['shuttle_x'],r['shuttle_y']],float)
 def center(r):return np.array([r['body_center_x'],r['body_center_y']],float)
 summary=[]
 windows=[('held_old','before','held_control',4,810,822),('held_current_observed_later','after','held_control',0,822,834),('short_origin_to_flight','after','short_exchange',0,11714,11724),('short_FSM_three_fresh','after','short_exchange',0,11716,11720),('source_serve_positive','after','serve_control',0,904,910)]
 for label,arm,case,track,lo,hi in windows:
  allrows=[r for r in rows if r['arm']==arm and r['case']==case and lo<=r['frame']<=hi and r['raw_track']==track]
  selected=[r for r in allrows if r['detector_matched'] and r['detector_observed'] and r['shuttle_status']=='observed' and r['pose_source_frame']==r['frame']]
  a,b=selected[0],selected[-1];delta=point(b)-point(a);body=center(b)-center(a)
  seq=[r for r in allrows if r['shuttle_status']=='observed']
  origins=[r for r in rows if r['arm']==arm and r['case']==case and r['frame']==a['frame']]
  ranking=[{'raw_track':r['raw_track'],'box_distance_px':r['distance_from_box_px'],'wrist_distance_px':r['nearest_fresh_wrist_distance_px']} for r in origins]
  freshframes=[r['frame'] for r in selected]
  summary.append({'case':label,'arm':arm,'window':[lo,hi],'actor_raw_track_only':track,'fresh_observed_frames':freshframes,'origin_rankings':ranking,'raw_associations':{str(r['frame']):r['association'] for r in allrows},'missing_shuttle_frames':[r['frame'] for r in allrows if r['shuttle_status']!='observed'],'shuttle_net_displacement_px':float(np.linalg.norm(delta)),'actor_box_center_net_displacement_px':float(np.linalg.norm(body)),'body_relative_net_displacement_px':float(np.linalg.norm(delta-body)),'origin_box_distance_px':a['distance_from_box_px'],'last_box_distance_px':b['distance_from_box_px'],'origin_box_distance_heights':a['distance_from_box_body_heights'],'last_box_distance_heights':b['distance_from_box_body_heights'],'fresh_box_distance_series':[r['distance_from_box_px'] for r in selected],'fresh_wrist_distance_series_px':[r['nearest_fresh_wrist_distance_px'] for r in selected],'source_box_uncertainty_px':None,'source_wrist_uncertainty_px':None,'motion_unit':'registered reference image pixels; not airborne court metres','physical_departure_label':None,'admission_decision':None})
 # Preserve actual raw observation states/coordinate contexts independently of derived CSV.
 cacheframes={}
 for name,h in receipt['input_sha256'].items():
  p=Path(name)
  if 'test02_candidate_v4' not in name or p.suffix!='.msgpack':continue
  d=msgpack.unpackb(p.read_bytes(),raw=False)
  for r in d['frames']:
   if 11711<=r['f']<=11744:
    cacheframes[r['f']]={'frame':r['f'],'shot':r['sh'],'content_epoch':r['ce'],'calibration_state':r['cs'],'view':r['v'],'replay':r['r'],'shuttle_observation':r['sa'],'persons_raw_track_freshness':[{'track_id':p['t'],'detector_matched':p['dm'],'pose_frame':p['pf']} for p in r['p']]}
 events=json.loads((OLD/'actual_event_cases.json').read_text())['after']
 far=[e for e in events['append_only'] if e['type']=='contact' and e['frame_start']==11740]
 assert far
 contact=next(e for e in far if e['status']=='provisional')
 assert not any(e['type']=='contact' and e['frame_start']==11740 for e in events['live'])
 physics=contact['payload']['physical_evidence']
 context=physics['inputs']['participant_context']
 assert context['shot_id']==3 and context['content_epoch']==21
 trace=[]
 for s in (OLD/'actual_trace_cases.jsonl').open():
  d=json.loads(s)
  if 11714<=d['frame']<=11774 and d['call'] in ['step','contact']:
   trace.append({k:d[k] for k in ['call','frame','observation','before','after','update'] if k in d})
 save('window_measurements.json',{'scope':'Descriptive preserved-cache measurements, no learned/selected cutoff, no physical labels or admission decision','rows':summary})
 save('actual_short_context.json',{'frames':[cacheframes[k] for k in sorted(cacheframes)],'later_contact_append_only':contact,'later_contact_live_after_rally_cancellation':False,'trace':trace,'origin_participant_birth_context_in_retained_image_rows':None,'origin_context_limitation':'Raw track IDs and source epochs alone are not a bound ContactParticipantContext; a future engine path must supply actual participant snapshots, not manufacture them from raw IDs.'})
 assert all(sha(p)==h for p,h in receipt['input_sha256'].items())
 assert all(sha(p)==h for p,h in inputs.items())
 save('measurement_receipt.json',{'status':'completed_CPU_only_descriptive_departure_feasibility','source_image_rows':876,'input_sha256':{**receipt['input_sha256'],**inputs,str(Path(__file__).resolve()):sha(Path(__file__))},'new_NN':False,'candidate_source_modified':False,'contact_score_modified':False,'rally_admission_modified':False,'physical_accuracy_claimed':False,'frame_or_threshold_selection_basis':'Existing source-reviewed held/serve/short-exchange cases; endpoints descriptive only, no cutoff tuned or classifier applied'})
 print(json.dumps({'status':'complete','input_rows':len(rows),'descriptive_windows':len(summary),'actual_short_frames':len(cacheframes),'no_NN':True}))
if __name__=='__main__':main()
