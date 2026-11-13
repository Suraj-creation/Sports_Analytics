"""Bounded actual-image detector/ROI/tracker/content comparisons, no GT input.

Before uses the unchanged installed ByteTrack backend; after changes only birth
activation. Detector and source pixels are shared; content policy is unchanged.
Detector/pose scheduling follows the recorded before-run rate schedule rather
than new downstream FSM feedback. No pose/shuttle/engine inference is claimed.
"""
from pathlib import Path
import collections,copy,hashlib,json,sys
import av,cv2,msgpack,numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CAND=ROOT.parent/'test03-pipeline-improvements-20261111'
from bai_badminton.perception import players
from bai_badminton.court import Homography
from bai_badminton.perception.content import ContentContinuityProviderV2,scene_change_to_dict,scene_decision_to_dict
from bai_badminton.perception.scene_change import ForegroundRegion
from trackers import ByteTrackTracker

assert Path(players.__file__).is_relative_to(CAND)
sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
BASE=ROOT.parent/'ground-truth-validation-artifacts-20261110'
OUT=HERE/'tracking_prefix_probe_v3'
CASES={1:('test_01/improved_v1',[(0,80),(235,310),(9000,9060)]),2:('test_02/improved_v1',[(300,365),(5505,6510),(11300,11360),(25206,25540)])}
FOCUS={1:{0,1,2,243,300,9000},2:{300,354,355,356,5956,5957,5958,5960,6486,6492,6493,11345,11346,11347,11348,25518,25519,25520,25521,25524}}

class OriginalTracker(players.PlayerTracker):
 def __init__(self,fps):
  self._tracker=ByteTrackTracker(frame_rate=fps,lost_track_buffer=30,track_activation_threshold=.4,minimum_consecutive_frames=1,high_conf_det_threshold=.5)
  self.fps=fps

class SharedDetector:
 def __init__(self,detector):self.detector=detector;self.cache={};self.frame=None;self.last_diagnostic=None;self.fresh_calls=0
 def __call__(self,image):
  key=(self.frame,hashlib.sha256(image.tobytes()).hexdigest())
  if key not in self.cache:
   self.fresh_calls+=1
   b,s=self.detector(image);self.cache[key]=(b.copy(),s.copy(),copy.deepcopy(self.detector.last_diagnostic))
  b,s,self.last_diagnostic=self.cache[key]
  return b.copy(),s.copy()

def make_perception(detector,fps,before):
 saved=players.PlayerTracker
 try:
  if before:players.PlayerTracker=OriginalTracker
  p=players.PlayerPerception(detector,None,fps,det_stride=2,pose_stride=0,max_players=2)
 finally:players.PlayerTracker=saved
 p.set_diagnostics(True,8)
 return p

def body(person):
 return {'track':person.track_id,'raw_track':person.raw_track_id,'bbox':person.bbox.tolist(),'confidence':person.conf,'detector_matched':person.detector_matched}

def main():
 assert not OUT.exists();cv2.setNumThreads(1)
 model=ROOT/'models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx';assert sha(model)=='fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e'
 detector=players.PlayerDetector(model,(512,512),[('CUDAExecutionProvider',{'device_id':0}),'CPUExecutionProvider'],score_thr=.35);detector.set_diagnostics(True,8)
 inputs={str(model):sha(model),str(Path(__file__)):sha(Path(__file__))}
 for f in ['players.py','_bytetrack.py','content.py','scene_change.py','components.py']:
  path=CAND/'sports/badminton/src/bai_badminton/perception'/f;inputs[str(path)]=sha(path)
 OUT.mkdir();summary=[]
 for test,(relative,windows) in CASES.items():
  art=BASE/relative;run=art/'run';info=json.loads((run/'inference.json').read_text());session=json.loads((run/'session.json').read_text());sid=session['session_id'];proxy=run/'data/media'/info['source_sha256']/'proxy.mp4';assert sha(proxy)==info['proxy_sha256'];inputs[str(proxy)]=sha(proxy)
  events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()];calibration=next(e for e in events if e['type']=='calibration');H=np.array(calibration['payload']['H']);raw={};profiles=[]
  catalogue=json.loads((run/'perception_completion_catalog.json').read_text()) if (run/'perception_completion_catalog.json').exists() else None
  for path in sorted((run/'data/sessions'/sid/'perception').glob('*.msgpack')):
   chunk=msgpack.unpackb(path.read_bytes(),raw=False)
   if any(chunk['start']<=end and chunk['end']>=start for start,end in windows):
    inputs[str(path)]=sha(path);raw.update({f['f']:f for f in chunk['frames'] if any(a<=f['f']<=b for a,b in windows)});profiles.append(chunk['ci']['profile'])
  p0=profiles[0];assert all(p==p0 for p in profiles)
  rates={p0['pose_rates'][state]:p0['detector_rates'][state] for state in ['in_play','idle']}
  parameters=p0['components']['content_continuity']['params'];assert parameters['mode']=='barrier_detector_layout_v2'
  fps=info['media']['fps_num']/info['media']['fps_den']
  for start,end in windows:
   key=f'test{test}_{start:05d}_{end:05d}';shared=SharedDetector(detector)
   prior_path=HERE/'tracking_prefix_probe_v2'/f'{key}.json'
   prior=json.loads(prior_path.read_text());inputs[str(prior_path)]=sha(prior_path)
   for item in prior['detector_inputs']:
    shared.cache[(item['frame'],item['crop_pixels_sha256'])]=(np.asarray(item['boxes_crop'],float).reshape(-1,4),np.asarray(item['scores'],float),item['diagnostics'])
   variants={name:{'players':make_perception(shared,fps,name=='before'),'content':ContentContinuityProviderV2(**parameters),'previous':None,'rows':[]} for name in ['before','after']}
   with av.open(str(proxy)) as container:
    stream=container.streams.video[0];stream.thread_count=1;container.seek(int(start/fps/stream.time_base),stream=stream,backward=True)
    for decoded in container.decode(video=0):
     frame=round(float(decoded.pts*decoded.time_base)*fps)
     if frame<start:continue
     if frame>end:break
     assert abs(float(decoded.pts*decoded.time_base)-frame/fps)<1e-8
     image=decoded.to_ndarray(format='bgr24');current=raw[frame];G=np.array(current['g']).reshape(3,3) if current.get('g') is not None else None;h=Homography(G@H if G is not None else H,0,4);world=np.array([[-3.05,6.7],[3.05,6.7],[3.05,-6.7],[-3.05,-6.7]]);roi=players.CourtROI(h.court_to_image(world).astype(np.float32),homography=h);shared.frame=frame
     hardcut=frame>start and current['sh']!=raw[frame-1]['sh'];det_stride=rates[current['ps']]
     for name,v in variants.items():
      p,content,previous=v['players'],v['content'],v['previous'];p.set_roi(roi)
      regions=[] if previous is None else [ForegroundRegion(frame-1,f'track:{x.track_id}',tuple(x.bbox),x.detector_matched,previous['detector_observed']) for x in previous['persons']]
      evidence=content.observe(frame,image,previous_regions=regions,previous_view_valid=previous is not None and previous['view_valid'],current_view_valid=current['v']=='main',hard_cut=hardcut)
      probe,decision,barrier=None,None,False
      if evidence.hypothesis:
       probe=p.probe_detection(frame,image)
       decision=content.layout_decision(evidence,probe,detector_model='rfdetr_small@1.4.2',geometry_valid=current['v']=='main' and current['cs']=='VALID')
       barrier=content.tracking_barrier_for_decision(decision)
      if hardcut or barrier:p.on_cut()
      if current['v']=='main':persons=p.process(frame,image,(det_stride,0),detection_probe=probe)
      else:persons=[]
      if name=='before':
       # Restore the old independent membership behavior after processing:
       # every uniquely matched observation renewed both time and box.
       for person in persons:
        if person.detector_matched is True:
         p._court_tracks[person.raw_track_id]=(frame,person.bbox.copy())
      v['rows'].append({'frame':frame,'detector_stride':det_stride,'detector_observed':p.last_detector_observed,'persons':[body(x) for x in persons],'raw_content':scene_change_to_dict(evidence),'decision':scene_decision_to_dict(decision) if decision is not None else None,'barrier':barrier,'tracking_diagnostic':copy.deepcopy(p.last_diagnostic),'original_persons':[{k:x[k] for k in ['t','b','dm']} for x in current['p']],'source_pixels_sha256':hashlib.sha256(image.tobytes()).hexdigest()})
      v['previous']={'persons':persons,'detector_observed':p.last_detector_observed,'view_valid':current['v']=='main'}
     if frame in FOCUS[test]:
      panels=[]
      for name,v in variants.items():
       panel=image.copy()
       for person in v['rows'][-1]['persons']:
        b=np.array(person['bbox']).astype(int);color=(0,230,0) if person['detector_matched'] else (0,150,250);cv2.rectangle(panel,tuple(b[:2]),tuple(b[2:]),color,2);cv2.putText(panel,f"{person['track']}",tuple(b[:2]),cv2.FONT_HERSHEY_SIMPLEX,.7,color,2)
       cv2.putText(panel,f'{name} frame{frame} birth contract only',(10,25),cv2.FONT_HERSHEY_SIMPLEX,.65,(255,255,255),2);panels.append(panel)
      cv2.imwrite(str(OUT/f'{key}_frame_{frame:05d}.png'),np.concatenate(panels,axis=1))
   for name,v in variants.items():assert len(v['rows'])==end-start+1
   detail={'scope':'Bounded real detector/ROI/tracker/content: original birth+membership versus corrected birth+independent court-anchor lease; retained exact source detector proposals reused; frozen original rate schedule; no full pipeline/GT','test':test,'range':[start,end],'variants':{name:v['rows'] for name,v in variants.items()},'detector_inputs':[{'frame':f,'crop_pixels_sha256':digest,'boxes_crop':b.tolist(),'scores':s.tolist(),'diagnostics':dg} for (f,digest),(b,s,dg) in shared.cache.items()]}
   (OUT/f'{key}.json').write_text(json.dumps(detail,indent=2,allow_nan=False)+'\n')
   values={'test':test,'range':[start,end],'detector_evaluations':len(shared.cache),'fresh_detector_calls':shared.fresh_calls,'before_barriers':[r['frame'] for r in variants['before']['rows'] if r['barrier']],'after_barriers':[r['frame'] for r in variants['after']['rows'] if r['barrier']],'focus':{}}
   for f in sorted(FOCUS[test]&set(range(start,end+1))):
    values['focus'][str(f)]={name:[{'bbox':r['bbox'],'matched':r['detector_matched']} for r in v['rows'][f-start]['persons']] for name,v in variants.items()}
   for name,v in variants.items():
    values[name+'_fresh_person_rows']=sum(p['detector_matched'] is True for row in v['rows'] for p in row['persons'])
   summary.append(values);print(json.dumps({'completed':key,'detector_calls':len(shared.cache),'fresh_detector_calls':shared.fresh_calls,'before_barriers':values['before_barriers'],'after_barriers':values['after_barriers']}),flush=True)
 assert all(sha(Path(k))==value for k,value in inputs.items())
 (OUT/'summary.json').write_text(json.dumps({'status':'completed','cases':summary,'input_sha256':inputs,'providers':detector.tool.session.get_providers(),'candidate_players_import':str(Path(players.__file__).resolve()),'full_pipeline':False,'independent_physical_accuracy':False},indent=2)+'\n')
 (OUT/'executed_probe.py').write_bytes(Path(__file__).read_bytes())

if __name__=='__main__':main()
