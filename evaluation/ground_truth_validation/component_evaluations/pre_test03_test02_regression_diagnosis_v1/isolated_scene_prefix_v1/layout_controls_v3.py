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
 retained=read(OUT/'layout_results_v2.json');prior_receipt=read(OUT/'layout_receipt_v2.json');hardware=read(OUT/'actual_hardware_v2.json');assert hardware['node_provider_counts'].get('CUDAExecutionProvider',0)>0
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
  saved=next(r for r in retained if r['frame']==f)
  assert saved['source_BGR_sha256']==sha256(image.tobytes()).hexdigest()
  assert tuple(saved['crop_box'])==crop and saved['crop_BGR_sha256']==crop_digest
  boxes=np.asarray(saved['decision']['detector_boxes'],float)-np.array([x0,y0,x0,y0],float)
  scores=np.asarray(saved['decision']['detector_scores'],float)
  scope='reused exact-source/crop/model-bound actual RFDETR proposal; no new neural inference'
  elapsed=None
  boxes=np.asarray(boxes,float).reshape(-1,4)+np.array([x0,y0,x0,y0],float);scores=np.asarray(scores,float)
  polygon=tuple(tuple(float(v) for v in p) for p in poly)
  admitted=tuple(i for i,b in enumerate(boxes) if roi.contains_feet(b))
  probe=PlayerDetectionProbe(f,tuple(image.shape),sha256(image.tobytes()).hexdigest(),tuple(tuple(float(v) for v in b) for b in boxes),tuple(float(v) for v in scores),crop,admitted,polygon,strict_court_indices(boxes,polygon))
  context=wire['ci']['layout_format_context'];expected={'singles':2,'doubles':4}.get(context['match_format']) if context['confirmed'] else None
  decision=provider.layout_decision(raw,probe,detector_model=wire['models']['player_detector'],geometry_valid=True,expected_participants=expected,previous_camera=tuple(float(v) for v in priorg.ravel()),previous_to_current=tuple(float(v) for v in (g@np.linalg.inv(priorg)).ravel()))
  validate_scene_decision_binding(decision,raw)
  results.append({'frame':f,'raw_hypothesis':raw.hypothesis,'decision':scene_decision_to_dict(decision),'tracking_barrier':provider.tracking_barrier_for_decision(decision),'detector_scope':scope,'admitted_scope':'fresh ROI gate only; no tracker lease simulated (not used by all-raw strong-layout policy)','component_forward_s':elapsed,'source_BGR_sha256':probe.image_sha256,'crop_box':crop,'crop_BGR_sha256':crop_digest,'source_full_ROIs':[r.region.bbox for r in raw.regions]})
  print(json.dumps({'frame':f,'decision':decision.decision,'reason':decision.reason,'matched':decision.matched_pairs,'barrier':results[-1]['tracking_barrier']}),flush=True)
 assert {r['frame'] for r in results if r['tracking_barrier']}=={2928,11082,22416,23279}
 assert all(r['decision']['decision']=='no_barrier' for r in results if r['frame'] in [7703,23639])
 snapshot=OUT/'executed_final_policy_v3';snapshot.mkdir(exist_ok=False)
 for source in [Path(content.__file__),NATIVE/'sports/badminton/src/bai_badminton/perception/scene_change.py',NATIVE/'sports/badminton/src/bai_badminton/perception/players.py']:
  (snapshot/source.name).write_bytes(source.read_bytes())
 save('layout_results_v3.json',results)
 assert all(sha(p)==h for p,h in INPUTS.items())
 save('layout_receipt_v3.json',{'status':'completed_source_bound_observer_detector_layout_component_controls','source_root':str(NATIVE),'fresh_RFD_forwards':0,'reused_actual_source_crop_model_bound_queries':6,'full_NN_pipeline_rerun':False,'models_modified':False,'thresholds_or_matching_changed':False,'input_sha256':INPUTS,'source_NN_providers':prior_receipt['actual_providers'],'source_NN_hardware_profile_sha256':hardware['profile_sha256'],'physical_accuracy_claimed':False})
if __name__=='__main__':main()
