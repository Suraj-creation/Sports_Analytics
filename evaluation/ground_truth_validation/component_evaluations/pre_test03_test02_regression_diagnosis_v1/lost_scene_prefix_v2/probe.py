"""CPU-only chronological scene observer probe on actual saved source pixels."""
import importlib.util,json,sys
from dataclasses import asdict
from hashlib import file_digest
from pathlib import Path
import numpy as np
import msgpack
OUT=Path(__file__).resolve().parent
SPACE=OUT.parents[5]
NATIVE=SPACE/'test03-scene-evidence-contract-20261112'
ART=SPACE/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4'
INPUTS={}
def sha(p):
 with Path(p).open('rb') as f:return file_digest(f,'sha256').hexdigest()
def read(p):INPUTS[str(p)]=sha(p);return json.loads(Path(p).read_text())
def write(name,value):
 with (OUT/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')
def main():
 from bai_badminton.perception.scene_change import SceneContinuityDetectorV4,ForegroundRegion
 from bai_badminton.perception.content import scene_change_to_dict
 from bai_engine.decode import SegmentDecoder
 from bai_engine.store.sessions import MediaPaths
 import bai_badminton.perception.scene_change as native_module
 assert Path(native_module.__file__).is_relative_to(NATIVE)
 spec=importlib.util.spec_from_file_location('explicit_diagnostic_exclusive_scene',OUT/'exclusive_pixel_candidate.py')
 candidate=importlib.util.module_from_spec(spec);sys.modules[spec.name]=candidate;spec.loader.exec_module(candidate)
 INPUTS[str(Path(native_module.__file__))]=sha(native_module.__file__)
 INPUTS[str(OUT/'exclusive_pixel_candidate.py')]=sha(OUT/'exclusive_pixel_candidate.py')
 run=ART/'run';cat=read(run/'perception_completion_catalog.json');worker=read(run/'inference.json')
 assert worker['status']=='completed' and worker['frames_processed']==29296 and worker['cached_perception_used'] is False
 media=run/'data/media'/worker['source_sha256'];decoder=SegmentDecoder(MediaPaths(media),60)
 INPUTS[str(media/'hls/init.mp4')]=sha(media/'hls/init.mp4')
 entries={r['start']//60:r for r in cat['files']}
 targets=[2928,11082,22416,23279,7703,23639]
 results=[];all_rows=[]
 for target in targets:
  first=max(0,(target-120)//60);last=(target+6)//60
  frames={}
  for k in range(max(0,first-1),last+1):
   row=entries[k];p=run/row['path'];assert sha(p)==row['sha256'];INPUTS[str(p)]=row['sha256']
   for f in msgpack.unpackb(p.read_bytes(),raw=False)['frames']:frames[f['f']]=f
  native=SceneContinuityDetectorV4();experimental=candidate.SceneContinuityDetectorV4()
  parity=[];case_rows=[]
  for k in range(first,last+1):
   for p in sorted((media/'hls').glob(f'*{k:05d}*')):
    if p.is_file():INPUTS[str(p)]=sha(p)
   chunk=decoder.decode_segment(k)
   for i,image in enumerate(chunk.frames):
    f=chunk.start+i
    if f>target+6:break
    current=frames[f];prior=frames.get(f-1)
    hard=bool(prior is not None and current['sh']!=prior['sh'])
    regions=[ForegroundRegion(**r) for r in prior.get('fg',[])] if prior else []
    args={'previous_regions':regions,'previous_view_valid':bool(prior and not prior['r']),
          'current_view_valid':not current['r'],'hard_cut':hard}
    a=native.observe(f,image,**args)
    candidate_regions=[candidate.ForegroundRegion(**asdict(r)) for r in regions]
    b=experimental.observe(f,image,**{**args,'previous_regions':candidate_regions})
    actual=scene_change_to_dict(a)
    if current.get('cc') is not None and f>=first*60+10:
     parity.append({'frame':f,'exact':json.dumps(actual,sort_keys=True)==json.dumps(current['cc'],sort_keys=True)})
    if target-3<=f<=target+3:
     item={'frame':f,'source_BGR_sha256':__import__('hashlib').sha256(image.tobytes()).hexdigest(),
       'native_raw':actual,'exclusive_candidate':asdict(b),'actual_cached_raw':current.get('cc'),
       'actual_decision':current.get('cd'),'actual_content_epoch':current['ce'],
       'prior_foreground':prior.get('fg',[]) if prior else [],'actual_people':current['p']}
     case_rows.append(item);all_rows.append(item)
  results.append({'target':target,'prefix':[first*60,target+6],'recorded_raw_parity_count':len(parity),
                  'recorded_raw_parity_failures':[r for r in parity if not r['exact']],
                  'native':next(r['native_raw'] for r in case_rows if r['frame']==target),
                  'exclusive_candidate':next(r['exclusive_candidate'] for r in case_rows if r['frame']==target)})
  print(json.dumps({'target':target,'parity':len(parity),'parity_mismatch':sum(not r['exact'] for r in parity),
                    'native_hypothesis':results[-1]['native']['hypothesis'],'native_acquisition':results[-1]['native']['acquisition_region_keys'],
                    'exclusive_hypothesis':results[-1]['exclusive_candidate']['hypothesis'],
                    'exclusive_acquisition':results[-1]['exclusive_candidate']['acquisition_region_keys'] }),flush=True)
 write('source_bound_rows.json',all_rows);write('summary.json',results)
 assert all(sha(p)==h for p,h in INPUTS.items())
 write('receipt.json',{'status':'completed_observer_only_actual_pixel_prefix_control','source_root':str(NATIVE),
    'producer_implementation_unchanged':True,'candidate_scope':'Detached diagnostic mask semantics ONLY, not valid current codec or pipeline output',
    'new_neural_inference':False,'two_witness_ratio_intensity_gates_changed':False,'new_detector_or_layout_inference':False,
    'physical_GT_or_reset_accuracy_claimed':False,'input_sha256':INPUTS})
if __name__=='__main__':main()
