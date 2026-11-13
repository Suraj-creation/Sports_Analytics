"""Fresh-source detector/layout controls; no tracking or full inference rerun."""
import json,time,subprocess
from dataclasses import asdict
from hashlib import file_digest,sha256
from pathlib import Path
import msgpack
import numpy as np
OUT=Path(__file__).resolve().parent
SPACE=OUT.parents[5]
NATIVE=SPACE/'test03-scene-overlap-20261112'
MAIN=SPACE/'Sports_Analytics'
ART=SPACE/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4'
INPUTS={}
def sha(p):
 with Path(p).open('rb') as f:return file_digest(f,'sha256').hexdigest()
def read(p):INPUTS[str(p)]=sha(p);return json.loads(Path(p).read_text())
def save(n,v):
 with (OUT/n).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def main():
 from bai_badminton.perception.content import ContentContinuityProviderV2,scene_change_from_dict,scene_decision_to_dict,validate_scene_decision_binding
 from bai_badminton.perception.players import CourtROI,PlayerDetector,PlayerDetectionProbe,strict_court_indices
 from bai_badminton.perception.camera import project
 from bai_badminton.court import Homography,REFERENCE_POINTS
 from bai_engine.decode import SegmentDecoder
 from bai_engine.store.sessions import MediaPaths
 import bai_badminton.perception.content as content
 assert Path(content.__file__).is_relative_to(NATIVE)
 # Source files are stable for this component control; no full-run claims.
 for p in [Path(content.__file__),NATIVE/'sports/badminton/src/bai_badminton/perception/scene_change.py',NATIVE/'sports/badminton/src/bai_badminton/perception/players.py']:INPUTS[str(p)]=sha(p)
 observed=read(OUT/'summary.json');run=ART/'run';worker=read(run/'inference.json');cat=read(run/'perception_completion_catalog.json')
 model=worker['models']['artifacts']['rfdetr_small'];weights=Path(model['staged_path']);assert sha(weights)==model['sha256'];INPUTS[str(weights)]=model['sha256']
 choice=worker['profile']['player_detector'];assert choice['params']['score_threshold']==.35 and choice['precision']=='fp32'
 media=run/'data/media'/worker['source_sha256'];decoder=SegmentDecoder(MediaPaths(media),60)
 INPUTS[str(media/'hls/init.mp4')]=sha(media/'hls/init.mp4')
 events_path=run/'events.jsonl';INPUTS[str(events_path)]=sha(events_path)
 calibration=next(json.loads(s) for s in events_path.open() if json.loads(s)['type']=='calibration')
 h=Homography.from_json(calibration['payload']);reference=h.court_to_image(np.array([REFERENCE_POINTS[n] for n in ('far_left','far_right','near_right','near_left')])).astype(np.float32)
 detector=None;provider=ContentContinuityProviderV2(mode='barrier_detector_layout_v2');results=[]
 for item in observed:
  f=item['target'];raw=scene_change_from_dict(item['exclusive_candidate'],frame_idx=f)
  entry=next(e for e in cat['files'] if e['start']<=f<=e['end']);path=run/entry['path'];assert sha(path)==entry['sha256'];INPUTS[str(path)]=entry['sha256'];wire=msgpack.unpackb(path.read_bytes(),raw=False);current=next(r for r in wire['frames'] if r['f']==f);previous=next(r for r in wire['frames'] if r['f']==f-1)
  image=decoder.decode_frame(f);g=np.asarray(current['g']).reshape(3,3);priorg=np.asarray(previous['g']).reshape(3,3)
  poly=project(g,reference).astype(np.float32);roi=CourtROI(poly,homography=Homography(g@h.H,0.,4));crop=roi.crop_box(image.shape[1],image.shape[0]);x0,y0,x1,y1=crop;crop_image=image[y0:y1,x0:x1];crop_digest=sha256(crop_image.tobytes()).hexdigest()
  if f in [7703,23639]:
   bank_path=MAIN/'evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_acquisition_v1/prefix_v2'/('test2_07640_07740.json' if f==7703 else 'test2_23570_23680.json')
   bank=read(bank_path);assert bank['source_sha256']==worker['source_sha256'] and bank['proxy_sha256']==worker['proxy_sha256']
   query=next(r for r in bank['detector_inputs'] if r['frame']==f);assert query['crop_pixels_sha256']==crop_digest
   bank_model_manifest=MAIN/'evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_acquisition_v1/prefix_v2/input_manifest_at_start.json'
   manifest=read(bank_model_manifest);assert model['sha256'] in str(manifest)
   boxes=np.asarray(query['boxes_crop'],float);scores=np.asarray(query['scores'],float);scope='retained actual fresh detector proposal bank: exact source/proxy/crop/model binding';elapsed=None
  else:
   if detector is None:
    detector=PlayerDetector(weights,tuple(choice['input_size']),[('CUDAExecutionProvider',{'device_id':0}),'CPUExecutionProvider'],score_thr=.35,kind='rfdetr')
    import onnxruntime as ort
    options=ort.SessionOptions();options.graph_optimization_level=ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    options.enable_profiling=True;options.profile_file_prefix=str(OUT/'rfdetr_node_profile_v2')
    detector.tool.session=ort.InferenceSession(str(weights),sess_options=options,providers=[('CUDAExecutionProvider',{'device_id':0}),'CPUExecutionProvider'])
    assert detector.tool.session.get_providers()[0]=='CUDAExecutionProvider' 
   started=time.perf_counter();boxes,scores=detector(crop_image);elapsed=time.perf_counter()-started;scope='new bounded detached RFDETR component inference physicalGPU1; not full pipeline inference'
  boxes=np.asarray(boxes,float).reshape(-1,4)+np.array([x0,y0,x0,y0],float);scores=np.asarray(scores,float)
  polygon=tuple(tuple(float(v) for v in p) for p in poly)
  admitted=tuple(i for i,b in enumerate(boxes) if roi.contains_feet(b))
  probe=PlayerDetectionProbe(f,tuple(image.shape),sha256(image.tobytes()).hexdigest(),tuple(tuple(float(v) for v in b) for b in boxes),tuple(float(v) for v in scores),crop,admitted,polygon,strict_court_indices(boxes,polygon))
  context=wire['ci']['layout_format_context'];expected={'singles':2,'doubles':4}.get(context['match_format']) if context['confirmed'] else None
  decision=provider.layout_decision(raw,probe,detector_model=wire['models']['player_detector'],geometry_valid=True,expected_participants=expected,previous_camera=tuple(float(v) for v in priorg.ravel()),previous_to_current=tuple(float(v) for v in (g@np.linalg.inv(priorg)).ravel()))
  validate_scene_decision_binding(decision,raw)
  results.append({'frame':f,'raw_hypothesis':raw.hypothesis,'decision':scene_decision_to_dict(decision),'tracking_barrier':provider.tracking_barrier_for_decision(decision),'detector_scope':scope,'admitted_scope':'fresh ROI gate only; no tracker lease simulated (not used by all-raw strong-layout policy)','component_forward_s':elapsed,'source_BGR_sha256':probe.image_sha256,'crop_box':crop,'crop_BGR_sha256':crop_digest,'source_full_ROIs':[r.region.bbox for r in raw.regions]})
  print(json.dumps({'frame':f,'decision':decision.decision,'reason':decision.reason,'matched':decision.matched_pairs,'barrier':results[-1]['tracking_barrier']}),flush=True)
 profile_path=Path(detector.tool.session.end_profiling())
 profile=json.loads(profile_path.read_text());providers={}
 for event in profile:
  name=event.get('args',{}).get('provider')
  if name:providers[name]=providers.get(name,0)+1
 assert providers.get('CUDAExecutionProvider',0)>0
 save('actual_hardware_v2.json',{'pid':__import__('os').getpid(),'CUDA_VISIBLE_DEVICES':__import__('os').environ.get('CUDA_VISIBLE_DEVICES'),'profile':str(profile_path),'profile_sha256':sha(profile_path),'node_provider_counts':providers,'gpu_process_rows':subprocess.run(['nvidia-smi','--query-compute-apps=pid,gpu_uuid,used_memory','--format=csv,noheader'],capture_output=True,text=True,check=True).stdout})
 save('layout_results_v2.json',results)
 assert all(sha(p)==h for p,h in INPUTS.items())
 save('layout_receipt_v2.json',{'status':'completed_source_bound_observer_detector_layout_component_controls','source_root':str(NATIVE),'fresh_RFD_forwards':4,'retained_source_crop_model_bound_queries':2,'full_NN_pipeline_rerun':False,'models_modified':False,'thresholds_or_matching_changed':False,'input_sha256':INPUTS,'actual_providers':detector.tool.session.get_providers() if detector else None,'physical_accuracy_claimed':False})
if __name__=='__main__':main()
