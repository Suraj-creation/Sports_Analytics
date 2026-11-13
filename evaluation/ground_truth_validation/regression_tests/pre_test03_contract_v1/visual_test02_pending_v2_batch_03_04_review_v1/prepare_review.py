"""Verify closed renderer packages and assemble aspect-preserving review pages."""
from pathlib import Path
import hashlib,json
from collections import Counter
import cv2
import numpy as np

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
CACHE={}
def sha(p):
    p=Path(p)
    if p not in CACHE:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
        CACHE[p]=h.hexdigest()
    return CACHE[p]
def save(name,x):
    with (OUT/name).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def read(p):return json.loads(p.read_text())
def tile(image,title):
    h,w=image.shape[:2];s=min(640/w,445/h)
    im=cv2.resize(image,(round(w*s),round(h*s)),interpolation=cv2.INTER_AREA)
    out=np.zeros((473,640,3),np.uint8);y=28+(445-im.shape[0])//2;x=(640-im.shape[1])//2
    out[y:y+im.shape[0],x:x+im.shape[1]]=im
    cv2.putText(out,title,(5,20),cv2.FONT_HERSHEY_SIMPLEX,.55,(255,255,255),1)
    return out
cv2.setNumThreads(1)
rows=[];bindings={};pixel_receipts=[];reasons=Counter();package_summary=[]
for batch in [3,4]:
    p=ROOT/f'visual_test02_pending_v2_batch_{batch:02}';c=read(p/'completion.json')
    assert c['status']=='completed' and c['source_sha256']=='4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a'
    assert not c['neural_inference_performed'] and not c['physical_gt_created']
    for n,h in c['artifact_sha256'].items():assert sha(p/n)==h,n
    for z in c['input_bindings']:assert sha(z['path'])==z['sha256'],z['path'];bindings[z['path']]=z['sha256']
    package_summary.append({'batch':batch,'frames':len(c['frames']),'artifact_count':len(c['artifact_sha256']),'input_binding_count':len(c['input_bindings']),'completion_sha256':sha(p/'completion.json')})
    for f in c['frames']:
        d=p/f'frame_{f:07}';e=read(d/'evidence.json');arms={}
        for arm in ['source','baseline','current']:
            key='source_original.png' if arm=='source' else f'{arm}_proxy.png';im=cv2.imread(str(d/key))
            receipt=e['source_decode'] if arm=='source' else e['arms'][arm]['proxy_decode']
            assert list(im.shape)==receipt['shape']
            assert hashlib.sha256(im.tobytes()).hexdigest()==receipt['pixels_sha256']
            pixel_receipts.append({'frame':f,'arm':arm,**receipt})
            if arm!='source':
                raw=read(d/f'{arm}_raw_frame.json');cc=raw['cc'];cd=raw['cd']
                arms[arm]={'person_count':len(raw['p']),'fresh_matched_people':sum(x['dm'] is True for x in raw['p']),'foreground_count':len(raw.get('fg',[])),'epoch':raw['ce'],'shot':raw['sh'],'detector_observed':raw['do'],'shuttle_xy':raw['s'],'shuttle_support':raw['c'],'association_status':raw['sa']['association_status'] if raw.get('sa') else None,'scene_status':cc['status'] if cc else None,'raw_hypothesis':cc['hypothesis'] if cc else None,'decision':cd['decision'] if cd else None,'decision_reason':cd['reason'] if cd else None,'people':[{'raw_track_id':x['t'],'bbox':x['b'],'detector_matched':x['dm'],'pose_frame':x['pf']} for x in raw['p']]}
        reasons.update(e['request']['reasons'])
        rows.append({'frame':f,'batch':batch,'reasons':e['request']['reasons'],'evidence_json':str((d/'evidence.json').resolve()),'physical_ground_truth':None,'arms':arms})
assert len(rows)==194 and len({x['frame'] for x in rows})==194
pages=[]
for start in range(0,len(rows),5):
    block=rows[start:start+5];panels=[]
    for row in block:
        d=ROOT/f'visual_test02_pending_v2_batch_{row["batch"]:02}'/f'frame_{row["frame"]:07}';f=row['frame']
        panels.append(np.hstack([tile(cv2.imread(str(d/name)),f'T2 frame{f} | {arm}') for arm,name in [('SOURCE','source_original.png'),('BASELINE','baseline_source_overlay.png'),('CURRENT','current_source_overlay.png')]]))
    n=f'page_{start//5+1:02}.png';cv2.imwrite(str(OUT/n),np.vstack(panels));pages.append({'page':n,'frames':[x['frame'] for x in block],'sha256':sha(OUT/n)})
save('machine_readouts.json',rows)
save('verification.json',{'status':'verified_closed_packages_and_selected_pixels','packages':package_summary,'input_sha256':bindings,'unique_recorded_inputs':len(bindings),'all_package_artifacts_verified':True,'all_recorded_input_bindings_verified':True,'pixel_receipts':pixel_receipts,'pixel_receipt_count':len(pixel_receipts),'pages':pages,'request_reason_counts':dict(reasons),'new_source_decode':False,'new_NN':False,'physical_ground_truth':None,'tile_policy':'scale-to-fit640x445 with letterboxing plus28px title, preserving native source16:9 and overlaytextpanel aspect','visually_reviewed_yet':False})
print(json.dumps({'packages':package_summary,'frames':len(rows),'pages':len(pages),'pixel_receipts':len(pixel_receipts),'reasons':dict(reasons)},indent=2))
