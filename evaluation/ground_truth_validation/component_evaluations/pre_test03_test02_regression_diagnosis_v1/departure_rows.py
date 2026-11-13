"""Source-cache image-plane departure/co-motion rows, no event decisions."""
import csv,json,math
from hashlib import file_digest
from pathlib import Path
from types import SimpleNamespace
import msgpack
import numpy as np
OUT=Path(__file__).resolve().parent
SPACE=OUT.parents[4]
NATIVE=SPACE/'test03-scene-evidence-contract-20261112'
ROOTS={'before':SPACE/'ground-truth-validation-artifacts-20261110/test_02/improved_v1/run',
       'after':SPACE/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4/run'}
INPUTS={}
def sha(p):
 with Path(p).open('rb') as f:return file_digest(f,'sha256').hexdigest()
def read(p):INPUTS[str(p)]=sha(p);return json.loads(Path(p).read_text())
def save(n,v):
 with (OUT/n).open('x') as f:json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
def main():
 from bai_badminton.plugin import BadmintonSession
 from bai_badminton.engine import _stabilise
 from bai_badminton.racket_admission import admit_racket_candidates
 from bai_badminton.perception.camera import project
 assert Path(__import__('bai_badminton.plugin',fromlist=['x']).__file__).is_relative_to(NATIVE)
 ranges=[('held_control',800,850),('serve_control',890,930),('start13',4625,4710),('short_exchange',11711,11751)]
 rows=[];details=[]
 for arm,run in ROOTS.items():
  catalog=read(run/'perception_completion_catalog.json')
  for entry in catalog['files']:
   if not any(entry['start']<=hi and lo<=entry['end'] for _,lo,hi in ranges):continue
   path=run/entry['path'];assert sha(path)==entry['sha256'];INPUTS[str(path)]=entry['sha256'];wire=msgpack.unpackb(path.read_bytes(),raw=False)
   receiver=SimpleNamespace(perception=SimpleNamespace(ref_id=wire['cr']),_isolation_id=lambda:wire['ci'])
   chunk=BadmintonSession.decode_perception(receiver,path.read_bytes(),diagnostic=True)
   for raw,fp in zip(wire['frames'],chunk.frames,strict=True):
    relevant=[name for name,lo,hi in ranges if lo<=fp.frame_idx<=hi]
    if not relevant:continue
    inverse=np.linalg.inv(fp.cam) if fp.cam is not None else None
    xy=fp.shuttle_observation.selected_xy if fp.shuttle_observation is not None else fp.shuttle_xy
    registered=project(inverse,[xy])[0] if xy is not None and inverse is not None else None
    semantic,_=admit_racket_candidates(fp.persons,frame_idx=fp.frame_idx)
    for person in semantic:
     p=_stabilise(person,inverse) if inverse is not None else person
     b=p.bbox;h=float(b[3]-b[1]);center=[float((b[0]+b[2])/2),float((b[1]+b[3])/2)]
     wrist=[]
     if p.kps is not None and p.pose_frame_idx==fp.frame_idx:
      wrist=[{'joint':j,'xy':p.kps[j,:2].tolist(),'support':float(p.kps[j,2])} for j in [9,10] if np.isfinite(p.kps[j]).all() and p.kps[j,2]>=.3]
     distances=[float(np.linalg.norm(registered-np.asarray(w['xy']))) for w in wrist] if registered is not None else []
     nearest=min(range(len(distances)),key=distances.__getitem__) if distances else None
     boxdist=math.hypot(max(float(b[0]-registered[0]),0.,float(registered[0]-b[2])),max(float(b[1]-registered[1]),0.,float(registered[1]-b[3]))) if registered is not None else None
     rows.append({'arm':arm,'case':relevant[0],'frame':fp.frame_idx,'shot':fp.shot_id,'content_epoch':fp.content_epoch,
       'raw_track':p.track_id,'detector_matched':p.detector_matched,'detector_observed':fp.detector_observed,'pose_source_frame':p.pose_frame_idx,
       'shuttle_status':fp.shuttle_observation.status if fp.shuttle_observation else None,'association':fp.shuttle_observation.association_status if fp.shuttle_observation else None,
       'shuttle_x':float(registered[0]) if registered is not None else None,'shuttle_y':float(registered[1]) if registered is not None else None,
       'body_center_x':center[0],'body_center_y':center[1],'body_height_px':h,'distance_from_box_px':boxdist,
       'distance_from_box_body_heights':boxdist/h if boxdist is not None else None,
       'nearest_fresh_wrist':wrist[nearest]['joint'] if nearest is not None else None,
       'nearest_fresh_wrist_distance_px':distances[nearest] if nearest is not None else None,
       'nearest_fresh_wrist_distance_body_heights':distances[nearest]/h if nearest is not None else None})
     details.append({'arm':arm,'case':relevant[0],'frame':fp.frame_idx,'raw_track':p.track_id,'box_registered':b.tolist(),
                     'fresh_wrists_registered':wrist,'source_pose_uncertainty_px':None,'source_box_uncertainty_px':None})
 # No body/wrist uncertainty inferred from the shuttle's sensitivity assumption.
 rows.sort(key=lambda r:(r['arm'],r['case'],r['frame'],r['raw_track']))
 with (OUT/'departure_image_rows.csv').open('x',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 save('departure_body_details.json',{'rows':details,'scope':'Raw observed source image geometry only, not named identities or physical departure GT. Wrist/box covariance unavailable; no shuttle-sigma reuse.'})
 selected=[r for r in rows if r['frame'] in [809,810,904,905,906,11714,11715,11716,11718,11720,11722,11725,11728,11731,11740]]
 save('departure_selected_rows.json',{'rows':selected,'scope':'Image-plane distances; no eligibility threshold or activity decision proposed by these measurements'})
 assert all(sha(p)==h for p,h in INPUTS.items())
 save('departure_rows_receipt.json',{'status':'completed_readonly_image_geometry_rows','rows':len(rows),'input_sha256':INPUTS,'source_root':str(NATIVE),'new_NN':False,'event_or_metric_changes':False,'physical_GT_claimed':False})
 print(json.dumps({'status':'complete','rows':len(rows)},indent=2))
if __name__=='__main__':main()
