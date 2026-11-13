"""Actual frozen component replay from a verified cut; no NN or source edits."""
import json,hashlib
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
import msgpack,numpy as np
from bai_badminton.perception.association import CausalShuttleAssociation
from bai_badminton.plugin import BadmintonSession
import bai_badminton.perception.association as module
ROOT=Path('/home/administrator/Desktop/sport-analytics/test03-scene-overlap-20261112');HERE=Path(__file__).resolve().parent
ART=ROOT.parent/'ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5';RUN=ART/'run'
assert Path(module.__file__).resolve()==ROOT/'sports/badminton/src/bai_badminton/perception/association.py'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
INPUTS={}
def read(p):INPUTS[str(p)]=sha(p);return json.loads(Path(p).read_text())
def normal(v):return json.loads(json.dumps(v,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else str(x)))
def save(n,v):
 with (HERE/n).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def state(a):
 return {'tracks':[{'id':t.identity,'n':len(t.samples),'first':t.samples[0][0],'last':t.last_frame,'centre':t.descriptor()[0].tolist(),'spread':t.descriptor()[1],'compact':t.compact(a.stationary_samples),'witnesses':list(t.witnesses),'samples':[list(x) for x in t.samples]} for t in a._tracks], 'primary':[[f,p.tolist()] for f,p in a._primary], 'unavailable':a._unavailable,'context':a._context}

def main():
 completion=read(ART/'completion.json');assert completion['candidate_commit']=='5ae614826e6f909defb02445386962ac13b4641a' and completion['own_run_semantic_parity'] is True
 worker=read(RUN/'inference.json');choice=worker['profile']['components']['shuttle_association'];assert choice['implementation']=='coobserved-static-hypotheses-v1'
 assoc=CausalShuttleAssociation(fps=30,**choice['params']);catalog=read(RUN/'perception_completion_catalog.json')
 frames=[];previous=None
 for e in catalog['files']:
  if e['end']<23278 or e['start']>23543:continue
  p=RUN/e['path'];assert sha(p)==e['sha256'];INPUTS[str(p)]=e['sha256'];raw=msgpack.unpackb(p.read_bytes(),raw=False)
  receiver=SimpleNamespace(perception=SimpleNamespace(ref_id=raw['cr']),_isolation_id=lambda:raw['ci'])
  chunk=BadmintonSession.decode_perception(receiver,p.read_bytes(),diagnostic=True)
  for f in chunk.frames:
   if f.frame_idx==23278:previous=f
   if 23279<=f.frame_idx<=23543:frames.append(f)
 assert [f.frame_idx for f in frames]==list(range(23279,23544))
 assert previous is not None and previous.shuttle_observation.epoch!=frames[0].shuttle_observation.epoch
 rows=[];parity=0
 for fp in frames:
  expected=fp.shuttle_observation;assert expected is not None
  candidates=expected.candidates # full retained acquisition budget, never truncated public dg
  peaks=[c.peak_xy for c in candidates if c.selected_peak]
  assert len(peaks)<=1
  assert fp.shuttle_xy is None or len(peaks)==1,'Rawaccepted selectedpeaknotrecoverable'
  diagnostic=SimpleNamespace(candidates=candidates,selected_masked_peak_xy=peaks[0] if peaks else None)
  transform=np.linalg.inv(fp.cam) if fp.cam is not None and fp.calibration_state.value=='VALID' else None
  before=state(assoc)
  actual=assoc.update(fp.frame_idx,epoch=(fp.shot_id<<32)|fp.content_epoch,raw_xy=fp.shuttle_xy,raw_support=fp.shuttle_conf,diagnostic=diagnostic,image_valid=not fp.replay,image_to_reference=transform)
  assert normal(actual.to_dict())==normal(expected.to_dict()),fp.frame_idx
  parity+=1;after=state(assoc)
  target=None
  if peaks:
   pp=np.r_[peaks[0],1.];q=pp if transform is None else transform@pp;q=q[:2]/q[2]
   target=next((t for t in after['tracks'] if t['last']==fp.frame_idx and np.linalg.norm(np.array(t['samples'][-1][1:3])-q)<1e-7),None)
  primary=after['primary'];speeds=[];dots=[];displacement=None
  if len(primary)==4:
   points=np.array([v[1] for v in primary]);steps=np.diff(points,axis=0);speeds=np.linalg.norm(steps,axis=1).tolist();dots=[float(np.dot(a,b)) for a,b in zip(steps[:-1],steps[1:])];displacement=float(np.linalg.norm(points[-1]-points[0])/3)
  rows.append({'frame':fp.frame_idx,'raw_xy':fp.shuttle_xy,'evidence':actual.to_dict(),'selected_hypothesis':target,'primary_steps':speeds,'primary_dots':dots,'primary_displacement_per_frame':displacement,'state_before':before,'state_after':after})
 save('actual_state_rows.json',normal(rows))
 selected=[]
 for r in rows:
  if 23525<=r['frame']<=23543:
   t=r['selected_hypothesis'];floor=[x for x in r['state_after']['tracks'] if np.linalg.norm(np.array(x['centre'])-np.array([572.5,437.5]))<15]
   selected.append({'frame':r['frame'],'raw_xy':r['raw_xy'],'selected_id':t['id'] if t else None,'selected_compact':t['compact'] if t else None,'selected_sample_count':t['n'] if t else None,'selected_witnesses':t['witnesses'] if t else None,'primary_steps':r['primary_steps'],'primary_dots':r['primary_dots'],'floor_tracks':[{'id':t['id'],'n':t['n'],'compact':t['compact'],'witnesses':t['witnesses'],'centre':t['centre'],'spread':t['spread']} for t in floor]})
 save('compact_causal_rows.json',selected)
 INPUTS[str(Path(module.__file__))]=sha(module.__file__);INPUTS[str(Path(__file__))]=sha(__file__)
 assert all(sha(p)==h for p,h in INPUTS.items())
 save('parity_receipt.json',{'status':'EXACT_actual_frozen_association_evidence_reproduced','frames':parity,'range':[23279,23543],'verified_fresh_cut_epoch_at_start':True,'config':choice,'all_actual_candidates_preserved':True,'diagnostic_rehydration':'Only actually consumed candidate tuple and selected_peak target; no invented entropy/threshold/unused diagnostic data. Every rawaccepted frame has exactlyone retained selected_peak.','native_module':str(module.__file__),'input_sha256':INPUTS,'NN':False,'source_modified':False})
 print(json.dumps({'parity_frames':parity,'keyrows':[r for r in selected if r['frame'] in [23534,23535,23536,23540,23541,23542,23543]]}))
if __name__=='__main__':main()
