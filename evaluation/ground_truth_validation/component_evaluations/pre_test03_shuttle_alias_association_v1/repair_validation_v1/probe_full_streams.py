"""Prospective association-only raw-NN-cache replay, never fresh NN/pipeline metrics."""
from __future__ import annotations
import argparse,importlib.util,sys,json,hashlib
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from types import SimpleNamespace
import numpy as np,msgpack
import bai_badminton.perception.association as original
from bai_badminton.plugin import BadmintonSession

WORK=Path('/home/administrator/Desktop/sport-analytics')
NATIVE=WORK/'test03-scene-overlap-20261112'
assert Path(original.__file__).resolve()==NATIVE/'sports/badminton/src/bai_badminton/perception/association.py'
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def normalize(v):return json.loads(json.dumps(v,default=lambda x:x.tolist() if isinstance(x,np.ndarray) else str(x)))
def main():
 cli=argparse.ArgumentParser();cli.add_argument('--candidate-root',type=Path,required=True);cli.add_argument('--output',type=Path,required=True);cli.add_argument('--test',type=int,choices=[1,2],required=True);args=cli.parse_args()
 if args.output.exists():raise ValueError('Exclusive NEW validation output required')
 root=args.candidate_root.resolve();candidate_path=root/'sports/badminton/src/bai_badminton/perception/association.py';digest=sha(candidate_path)
 dependency={}
 for n in ['perception/diagnostics.py','perception/shuttle_post.py']:
  rel='sports/badminton/src/bai_badminton/'+n
  if sha(root/rel)!=sha(NATIVE/rel):raise ValueError('Shared pure dependency differs; separate native process required: '+n)
  dependency[str(NATIVE/rel)]=sha(NATIVE/rel)
 spec=importlib.util.spec_from_file_location('_explicit_prospective_association',candidate_path);new=importlib.util.module_from_spec(spec);sys.modules[spec.name]=new;spec.loader.exec_module(new)
 art=WORK/f'ground-truth-validation-artifacts-20261112/pre_test03_v5/test0{args.test}_candidate_v5';run=art/'run'
 completion=json.loads((art/'completion.json').read_text());assert completion['candidate_commit']=='5ae614826e6f909defb02445386962ac13b4641a' and completion['own_run_semantic_parity'] is True
 worker=json.loads((run/'inference.json').read_text());parent=json.loads((art/'run.executor.json').read_text());assert worker['cached_perception_used'] is False and parent['worker_report_sha256']==sha(run/'inference.json')
 cfg=worker['profile']['components']['shuttle_association'];fps=worker['media']['fps_num']/worker['media']['fps_den']
 old=original.CausalShuttleAssociation(fps=fps,**cfg['params']);candidate=new.CausalShuttleAssociation(fps=fps,**cfg['params'])
 cat=json.loads((run/'perception_completion_catalog.json').read_text());inputs={str(p):sha(p) for p in [art/'completion.json',run/'inference.json',art/'run.executor.json',run/'perception_completion_catalog.json',Path(__file__),Path(original.__file__)]};inputs.update(dependency)
 changes=[];counts=Counter();parity=0;dropped_diagnostic_targets=[]
 for entry in cat['files']:
  path=run/entry['path'];assert sha(path)==entry['sha256'];inputs[str(path)]=entry['sha256'];wire=msgpack.unpackb(path.read_bytes(),raw=False)
  receiver=SimpleNamespace(perception=SimpleNamespace(ref_id=wire['cr']),_isolation_id=lambda:wire['ci']);chunk=BadmintonSession.decode_perception(receiver,path.read_bytes(),diagnostic=True)
  for fp in chunk.frames:
   expected=fp.shuttle_observation
   if expected is None:raise ValueError('Current association evidence unavailable')
   peaks=[c.peak_xy for c in expected.candidates if c.selected_peak]
   if len(peaks)>1:raise ValueError('Multiple recorded rawselectedpeaks')
   target=peaks[0] if peaks else None
   if fp.shuttle_xy is not None and target is None:
    if fp.diagnostic is not None and fp.diagnostic.shuttle is not None:target=fp.diagnostic.shuttle.selected_masked_peak_xy
    if target is None:raise ValueError('Exact consumed rawmaskedpeak unavailable at '+str(fp.frame_idx))
   diag=None if 'candidate_evidence_unavailable' in expected.reasons else SimpleNamespace(candidates=expected.candidates,selected_masked_peak_xy=target,threshold=worker['profile']['shuttle']['params']['threshold'])
   transform=np.linalg.inv(fp.cam) if fp.cam is not None and fp.calibration_state.value=='VALID' else None
   kwargs=dict(epoch=(fp.shot_id<<32)|fp.content_epoch,raw_xy=fp.shuttle_xy,raw_support=fp.shuttle_conf,diagnostic=diag,image_valid=not fp.replay,image_to_reference=transform)
   a=old.update(fp.frame_idx,**kwargs)
   if normalize(a.to_dict())!=normalize(expected.to_dict()):raise ValueError('Original frozen output parity failed at '+str(fp.frame_idx))
   parity+=1;b=candidate.update(fp.frame_idx,**kwargs);v=b.to_dict()
   if normalize(v['raw_xy'])!=normalize(expected.raw_xy) or v['raw_model_support']!=expected.raw_model_support:raise ValueError('Prospective rawmodel provenance changed')
   counts['baseline_'+a.status]+=1;counts['candidate_'+b.status]+=1
   changed=(a.status!=b.status or a.association_status!=b.association_status or normalize(a.selected_xy)!=normalize(b.selected_xy))
   if changed:
    alt=b.selected_xy is not None and normalize(b.selected_xy)!=normalize(expected.raw_xy)
    if alt:
     matches=[c.rank for c in expected.candidates if normalize(c.peak_xy)==normalize(b.selected_xy)]
     if len(matches)!=1:raise ValueError('Alternative is not an exact currentobservedmodelcandidatepeak')
     counts['actual_current_alternative_selected']+=1
    elif a.selected_xy is not None and b.selected_xy is None:counts['new_abstention']+=1
    changes.append({'frame':fp.frame_idx,'shot':fp.shot_id,'content_epoch':fp.content_epoch,'before':a.to_dict(),'prospective':v,'selected_alternative':alt,'all_current_candidates':normalize([asdict(c) for c in expected.candidates])})
 args.output.mkdir(parents=True,exist_ok=False)
 with (args.output/'changes.json').open('x') as f:json.dump(normalize(changes),f,indent=2,allow_nan=False);f.write('\n')
 if sha(candidate_path)!=digest:raise ValueError('Candidate association source changed during probe; do not interpret')
 assert all(sha(Path(p))==h for p,h in inputs.items())
 receipt={'status':'completed_prospective_association_only_diagnostic_NOT_fresh_pipeline','test':args.test,'source_root':str(NATIVE),'candidate_association_source':str(candidate_path),'candidate_association_sha256':digest,'unchanged_shared_dependency_sha256':dependency,'original_exact_evidence_parity_frames':parity,'original_NN_completed':True,'new_NN':False,'complete_pipeline_replayed':False,'ground_truth_consumed':False,'thresholds_tuned':False,'source_code_modified_by_probe':False,'counts':dict(counts),'changed_frames':len(changes),'input_sha256':inputs,'evidence_effects_scope':'Only association update over actual frozen neural candidates/camera/epoch. No downstream FSM/profile-feedback or physicalaccuracy claim.'}
 with (args.output/'receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
 print(json.dumps({k:receipt[k] for k in ['status','test','original_exact_evidence_parity_frames','counts','changed_frames']}))
if __name__=='__main__':main()
