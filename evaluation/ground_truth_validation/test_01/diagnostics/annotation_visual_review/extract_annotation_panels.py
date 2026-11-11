from pathlib import Path
import csv,json,hashlib
import av,cv2,numpy as np
R=Path('/home/administrator/Desktop/sport-analytics/Sports_Analytics');D=R/'evaluation/ground_truth_validation/test_01/diagnostics/annotation_visual_review';D.mkdir(parents=True,exist_ok=True)
video=R/'data/benchmarking/test1/Test1_Full_rev.mp4';folder=R/'Part2/dataset/Test1_Full'
with (folder/'player_detections.csv').open() as f:players={int(r['frame_no']):r for r in csv.DictReader(f)}
with (folder/'Test1_Full_ball_filled.csv').open() as f:ball={int(r['Frame']):r for r in csv.DictReader(f)}
court=json.loads((folder/'Test1_Full_court.json').read_text())
target={0,150,243,300,715,8106,8460,8628,8634,8640,8683,9000,9967};records=[]
with av.open(str(video)) as c:
 s=c.streams.video[0];s.thread_type='AUTO';s.codec_context.thread_count=2
 for i,fr in enumerate(c.decode(s)):
  if i not in target:continue
  src=fr.to_ndarray(format='bgr24');img=cv2.resize(src,(1280,720),interpolation=cv2.INTER_AREA)
  raw=D/f'frame_{i:05d}_source_resized.png';cv2.imwrite(str(raw),img)
  declared=i==court['frame_no']
  pts=np.array([court['corners'][k] for k in ('TL','TR','BR','BL')],np.int32)
  cv2.polylines(img,[pts],True,(0,255,0),2)
  for k,v in court['corners'].items():cv2.circle(img,tuple(map(round,v)),5,(0,255,0),-1);cv2.putText(img,k,tuple(map(round,v)),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,255,0),1)
  for k in ('left_bottom','right_bottom','cable_left','cable_right'):cv2.circle(img,tuple(map(round,court['net'][k])),6,(255,0,255),2);cv2.putText(img,k,tuple(map(round,court['net'][k])),cv2.FONT_HERSHEY_SIMPLEX,.4,(255,0,255),1)
  cv2.line(img,tuple(map(round,court['net']['cable_left'])),tuple(map(round,court['net']['cable_right'])),(255,0,255),2)
  pr=players.get(i);br=ball.get(i)
  if pr:
   for j,col in [(1,(0,255,255)),(2,(255,255,0))]:
    if not pr.get(f'player_{j}_x') or not pr.get(f'player_{j}_y'):continue
    x,y=float(pr[f'player_{j}_x']),float(pr[f'player_{j}_y']);cv2.circle(img,(round(x),round(y)),9,col,2);cv2.putText(img,f'legacy slot{j}',(round(x)+10,round(y)),cv2.FONT_HERSHEY_SIMPLEX,.5,col,1)
  if br and br['Visibility']=='1':
   x,y=int(float(br['X'])),int(float(br['Y']));cv2.circle(img,(x,y),8,(0,0,255),2);cv2.putText(img,'legacy shuttle',(x+8,y),cv2.FONT_HERSHEY_SIMPLEX,.5,(0,0,255),1)
  label=f'Source frame {i} / {float(fr.pts*fr.time_base):.6f}s; court '+('DECLARED FRAME' if declared else 'reference from frame8634 - not certified persistent')
  cv2.rectangle(img,(0,680),(1280,720),(0,0,0),-1);cv2.putText(img,label,(10,706),cv2.FONT_HERSHEY_SIMPLEX,.56,(255,255,255),1)
  out=D/f'frame_{i:05d}_legacy_overlay.png';cv2.imwrite(str(out),img)
  records.append({'source_frame':i,'source_pts':fr.pts,'time_base_num':fr.time_base.numerator,'time_base_den':fr.time_base.denominator,'seconds':float(fr.pts*fr.time_base),'source_shape':list(src.shape),'resized_shape':[720,1280,3],'coordinate_scaling':'source1920x1080 ->1280x720; original legacy coordinates drawn unchanged','source_pixels_sha256':hashlib.sha256(src.tobytes()).hexdigest(),'court_declared_frame':declared,'legacy_player_row':pr,'legacy_shuttle_row':br,'raw_image':raw.name,'overlay_image':out.name,'overlay_sha256':hashlib.sha256(out.read_bytes()).hexdigest()})
  print(i,flush=True)
  if i==max(target):break
(D/'frame_metadata.json').write_text(json.dumps({'video':str(video),'scope':'Read-only source decoding and legacy annotation overlays; no inference or certified new labels','sample_frames':sorted(target),'frames':records},indent=2)+'\n')
