"""Read-only fresh RFDETR proposals on exact retained source-proxy frames.

Isolated detector probe, not a full production rerun or physical precision/recall.
"""
from pathlib import Path
import hashlib,json,sys
import av,cv2,msgpack,numpy as np

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
from bai_badminton.court import Homography
from bai_badminton.perception.players import PlayerDetector,CourtROI

sha=lambda p:hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
BASE=ROOT.parent/'ground-truth-validation-artifacts-20261110'
OUT=Path(__file__).parent/'detector_frame_probe_v1'
CASES={1:('test_01/improved_v1',[243,300,6152,9000]),2:('test_02/improved_v1',[300,354,355,356,5952,5958,6492,11345,11346,11348,25518,25521])}

def main():
 assert not OUT.exists()
 cv2.setNumThreads(1)
 model=ROOT/'models/cache/rfdetr_small/rfdetr_s_v142_512x512.onnx'
 assert sha(model)=='fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e'
 detector=PlayerDetector(model,(512,512),[('CUDAExecutionProvider',{'device_id':0}),'CPUExecutionProvider'],score_thr=.35)
 detector.set_diagnostics(True,8)
 results=[];inputs={str(model):sha(model),str(Path(__file__)):sha(Path(__file__))}
 OUT.mkdir()
 for test,(relative,indices) in CASES.items():
  art=BASE/relative;run=art/'run';session=json.loads((run/'session.json').read_text());info=json.loads((run/'inference.json').read_text());events=[json.loads(x) for x in (run/'events.jsonl').read_text().splitlines()]
  source_sha=info['source_sha256'];proxy=run/'data/media'/source_sha/'proxy.mp4'
  assert sha(proxy)==info['proxy_sha256']
  inputs[str(proxy)]=sha(proxy)
  calibration=next(e for e in events if e['type']=='calibration');H=np.array(calibration['payload']['H'])
  world=np.array([[-3.05,6.7],[3.05,6.7],[3.05,-6.7],[-3.05,-6.7]])
  raw={}
  for path in sorted((run/'data/sessions'/session['session_id']/'perception').glob('*.msgpack')):
   chunk=msgpack.unpackb(path.read_bytes(),raw=False)
   if any(chunk['start']<=i<=chunk['end'] for i in indices):
    inputs[str(path)]=sha(path)
    raw.update({f['f']:f for f in chunk['frames'] if f['f'] in indices})
  with av.open(str(proxy)) as container:
   video=container.streams.video[0];video.thread_count=1
   for index in indices:
    container.seek(int(index/30/video.time_base),stream=video,backward=True)
    frame=next(f for f in container.decode(video=0) if float(f.pts*f.time_base)>=index/30-1e-8)
    assert abs(float(frame.pts*frame.time_base)-index/30)<1e-8
    image=frame.to_ndarray(format='bgr24');g=np.array(raw[index]['g']).reshape(3,3);h=Homography(g@H,0,4);poly=h.court_to_image(world);roi=CourtROI(poly.astype(np.float32),homography=h)
    x0,y0,x1,y1=roi.crop_box(1280,720);boxes,scores=detector(image[y0:y1,x0:x1]);boxes=boxes+np.array([x0,y0,x0,y0]);pixels_sha=hashlib.sha256(image.tobytes()).hexdigest()
    record={'test':test,'frame':index,'proxy_pts':frame.pts,'source_pixels_sha256':pixels_sha,'crop':[x0,y0,x1,y1],'raw_persons':[{k:v for k,v in p.items() if k in ['t','b','c','dm']} for p in raw[index]['p']],'proposals':[{'bbox':b.tolist(),'confidence':float(s),'court_xy':h.image_to_court(np.array([[(b[0]+b[2])/2,b[3]]]))[0].tolist(),'strict_court':roi.contains_feet(b,allow_runoff=False),'padded_court':roi.contains_feet(b)} for b,s in zip(boxes,scores,strict=True)],'detector_diagnostics':detector.last_diagnostic}
    for b,s in zip(boxes,scores,strict=True):
     color=(0,220,0) if roi.contains_feet(b,allow_runoff=False) else (0,0,255);cv2.rectangle(image,tuple(b[:2].astype(int)),tuple(b[2:].astype(int)),color,2);cv2.putText(image,f'{s:.3f}',tuple(b[:2].astype(int)),cv2.FONT_HERSHEY_SIMPLEX,.45,color,1)
    cv2.polylines(image,[poly.astype(int)],True,(255,200,0),2);name=f'test{test}_frame_{index:05d}.png';cv2.imwrite(str(OUT/name),image);record['overlay']=name;record['overlay_sha256']=sha(OUT/name);results.append(record)
 assert all(sha(Path(k))==v for k,v in inputs.items())
 (OUT/'probe.json').write_text(json.dumps({'scope':'Fresh isolated actualRFDETR detector probe; not full pipeline or physicalGT','model_sha256':sha(model),'providers':detector.tool.session.get_providers(),'results':results,'input_sha256':inputs},indent=2)+'\n')
 (OUT/'executed_probe.py').write_bytes(Path(__file__).read_bytes())
 print(json.dumps({'status':'completed','cases':len(results),'output':str(OUT)}))

if __name__=='__main__': main()
