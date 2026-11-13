"""Source-bound contact sensitivity and prevalence; no inference or fixes."""
import json,math
from dataclasses import asdict
from hashlib import file_digest
from pathlib import Path
import numpy as np
OUT=Path(__file__).resolve().parent
MAIN=OUT.parents[3]
SPACE=MAIN.parent
NATIVE=SPACE/'test03-scene-evidence-contract-20261112'
INPUTS={}
def sha(p):
 with Path(p).open('rb') as f:return file_digest(f,'sha256').hexdigest()
def read(p):INPUTS[str(p)]=sha(p);return json.loads(Path(p).read_text())
def save(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def main():
 import bai_badminton.events.contact as contact
 from bai_badminton.observations import WindowObs,PlayerSeries
 from bai_badminton.perception.shuttle_post import Track
 from bai_badminton.perception.camera import project
 from research.pipeline_repair_run_analysis import select_live_events
 assert Path(contact.__file__).is_relative_to(NATIVE)
 probes=read(OUT/'component_score_probes.json')
 cases={arm:{r['frame']:r for r in probes['cases'][-1]['arms'][arm]['legacy' if arm=='before' else 'current']['all_scores']} for arm in ['before','after']}
 def probability(s):return contact._sigmoid(contact.W_BIAS+contact.W_REDIRECT*s['redirect']+contact.W_IMPULSE*s['impulse']+contact.W_PROX*s['proximity']+contact.W_SWING*s['swing']+1.4*s['racket_overlap'])
 a,b=cases['before'][11715],cases['after'][11715]
 assert abs(probability(a['scores'])-a['p'])<1e-15 and abs(probability(b['scores'])-b['p'])<1e-15
 sensitivity={'classification':'Declared score-factor counterfactual only; not a model/pipeline rerun or physical label','source_anchor':11715,'before_p':a['p'],'fresh_p':b['p'],'unchanged_p_min':contact.P_MIN,'fresh_other_cues_with_old_heading_p':probability({**b['scores'],'redirect':a['scores']['redirect']}),'old_other_cues_with_fresh_heading_p':probability({**a['scores'],'redirect':b['scores']['redirect']}),'before_scores':a['scores'],'fresh_scores':b['scores']}
 assert sensitivity['fresh_other_cues_with_old_heading_p']>contact.P_MIN and sensitivity['old_other_cues_with_fresh_heading_p']<contact.P_MIN
 cache=read(OUT/'cache_cases.json');current=SPACE/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4/run';worker=read(current/'inference.json');sigma=worker['profile']['components']['contact']['params']['spatial_sigma_px']
 motion={}
 for arm,record in [('before',a),('after',b)]:
  lo,hi=11711,11719;raw=[cache[arm][str(f)] for f in range(lo,hi)];x=[];y=[];visible=[]
  for f in raw:
   xy=(f.get('sa') or {}).get('selected_xy');ok=xy is not None and (f.get('sa') or {}).get('status')=='observed'
   q=project(np.linalg.inv(np.asarray(f['g']).reshape(3,3)),[xy])[0] if ok else [np.nan,np.nan]
   x.append(q[0]);y.append(q[1]);visible.append(ok)
  w=WindowObs(lo,30.,Track.from_arrays(x,y,visible),{},break_before=np.zeros(hi-lo,bool));cand=contact.ContactCandidate(11715,None,record['p'],record['scores'])
  evidence=contact.build_contact_evidence(w,cand,motion_reliability=contact.ContactMotionReliability(sigma));motion[arm]=asdict(evidence.inputs.motion)
 sensitivity['declared_spatial_sensitivity_px']=sigma;sensitivity['existing_motion_evidence']=motion
 assert motion['before']['incoming_direction_support']==motion['after']['incoming_direction_support']==0
 assert all(motion[k]['outgoing_direction_support']>0 and motion[k]['speed_gain_support']>0 for k in motion)
 save('launch_heading_sensitivity.json',sensitivity)
 roots={'Test2_baseline_full_NN':SPACE/'ground-truth-validation-artifacts-20261110/test_02/improved_v1/run','Test2_fresh_2418':current,'Test1_baseline_full_NN':SPACE/'ground-truth-validation-artifacts-20261110/test_01/improved_v1/run','Test1_fresh_2418':SPACE/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test01_candidate_v4/run'}
 prevalence={}
 for label,root in roots.items():
  path=root/'events.jsonl';INPUTS[str(path)]=sha(path);events=[json.loads(s) for s in path.open()];live=select_live_events(events,events[0]['session_id']);contacts=[e for e in live if e['type']=='contact'];starts={e['frame_start'] for e in live if e['type']=='rally_end'};rows=[]
  for e in contacts:
   p=e['payload'];motion=(p.get('physical_evidence') or {}).get('inputs',{}).get('motion') or {};score=next((d['scores'] for d in e.get('evidence',[]) if d.get('kind')=='component_scores'),{})
   if motion.get('incoming_direction_support')==0 and score.get('redirect',0)>0:
    rows.append({'frame':e['frame_start'],'initial_anchor':e['frame_start'] in starts,'raw_redirect':score['redirect'],'incoming_speed':score.get('speed_before'),'outgoing_speed':score.get('speed_after'),'angle_deg':score.get('angle_deg'),'incoming_direction_support':0,'outgoing_direction_support':motion.get('outgoing_direction_support'),'speed_gain_support':motion.get('speed_gain_support'),'physical_impact':(p.get('physical_evidence') or {}).get('impact')})
  prevalence[label]={'live_contact_count':len(contacts),'unreliable_incoming_nonzero_redirect_count':len(rows),'initial_anchor_count':sum(r['initial_anchor'] for r in rows),'exact_zero_incoming_count':sum(r['incoming_speed']==0 for r in rows),'rows':rows,'scope':'Selected model contacts only, not physical precision or defect count'}
 save('cross_test_selected_contact_prevalence.json',prevalence)
 synthetic=[]
 for angle in [0,45,90,180,270]:
  radians=math.radians(angle);direction=np.array([math.cos(radians),math.sin(radians)]);xy=np.zeros((9,2));xy[5:]=np.arange(1,5)[:,None]*10*direction;player=PlayerSeries.empty(9);player.bbox[:]=[-20,-30,20,100]
  w=WindowObs(0,30.,Track.from_arrays(xy[:,0],xy[:,1],np.ones(9,bool)),{'unknown_episode':player});raw=contact.score_frame(w,4);reliable=contact.score_frame(w,4,motion_reliability=contact.ContactMotionReliability(sigma))
  assert raw.scores['speed_before']==0 and raw.scores['angle_deg']==90 and reliable.scores['redirect']==0
  synthetic.append({'outgoing_orientation_deg':angle,'legacy_heading_deg':raw.scores['angle_deg'],'legacy_redirect':raw.scores['redirect'],'legacy_p':raw.p,'motion_reliable_redirect':reliable.scores['redirect'],'motion_reliable_p':reliable.p,'scope':'Controlled image-plane trajectory; no physical impact label'})
 stationary=WindowObs(0,30.,Track.from_arrays(np.zeros(9),np.zeros(9),np.ones(9,bool)),{});assert contact.score_frame(stationary,4) is None
 save('synthetic_zero_heading_controls.json',{'cases':synthetic,'stationary_control_none':True,'provider_or_profile_changed':False,'threshold_changed':False})
 assert all(sha(p)==h for p,h in INPUTS.items())
 save('sensitivity_receipt.json',{'status':'complete_readonly_contact_sensitivity_controls','source_root':str(NATIVE),'contact_source_sha256':sha(contact.__file__),'inputs_sha256':INPUTS,'new_NN':False,'source_modified':False,'physical_metrics_claimed':False})
 print(json.dumps({'factorial_p':{k:v for k,v in sensitivity.items() if k not in ['before_scores','fresh_scores','existing_motion_evidence']},'prevalence':{k:{i:v for i,v in d.items() if i!='rows'} for k,d in prevalence.items()}},indent=2))
if __name__=='__main__':main()
