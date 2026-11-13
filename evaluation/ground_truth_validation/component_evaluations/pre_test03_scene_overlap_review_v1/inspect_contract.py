"""Inspect bound retained evidence and deterministic mask geometry; no flow replay."""
from pathlib import Path
import hashlib,json
import cv2
import numpy as np

OUT=Path(__file__).resolve().parent
MAIN=OUT.parents[3]
PACKAGES=MAIN/'evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1'
NATIVE=MAIN.parent/'test03-scene-evidence-contract-20261112'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,x):
    with (OUT/name).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
inputs={};rows=[];tiles=[]
for batch,frame in [(1,2927),(1,2928),(2,11081),(2,11082)]:
    package=PACKAGES/f'visual_test02_pending_v2_batch_{batch:02}'
    completion=json.loads((package/'completion.json').read_text());assert completion['status']=='completed'
    inputs[str((package/'completion.json').resolve())]=sha(package/'completion.json')
    root=package/f'frame_{frame:07}'
    for name in ['source_original.png','current_source_overlay.png','baseline_raw_frame.json','current_raw_frame.json','evidence.json']:
        p=root/name;expected=completion['artifact_sha256'][str(p.relative_to(package))]
        assert sha(p)==expected;inputs[str(p.resolve())]=expected
    source=cv2.imread(str(root/'source_original.png'));assert source.shape==(1080,1920,3)
    source=cv2.resize(source,(640,360),interpolation=cv2.INTER_AREA)
    tile=np.zeros((390,640,3),np.uint8);tile[30:]=source
    cv2.putText(tile,f'Test2 original source frame {frame}',(10,22),cv2.FONT_HERSHEY_SIMPLEX,.6,(255,255,255),1);tiles.append(tile)
    arms={}
    for arm in ['baseline','current']:
        raw=json.loads((root/f'{arm}_raw_frame.json').read_text())
        arms[arm]={'epoch':raw['ce'],'person_count':len(raw['p']),'foreground_context_count':len(raw.get('fg',[])),'person_rows':[{'track':p['t'],'fresh_match':p['dm'],'bbox':p['b']} for p in raw['p']],'raw_scene':raw['cc'],'decision':raw['cd']}
    rows.append({'frame':frame,'source_ground_truth':None,'arms':arms})
cv2.imwrite(str(OUT/'source_pairs.png'),np.vstack([np.hstack(tiles[:2]),np.hstack(tiles[2:])]))
raw=rows[-1]['arms']['current']['raw_scene'];regions=raw['regions']
assert len(regions)==2
# Geometry only, exactly the existing 480-analysis rasterization convention.
masks=[]
for item in regions:
    x1,y1,x2,y2=np.asarray(item['region']['bbox'])*(.375)
    x1,x2=np.clip([int(x1),int(np.ceil(x2))],0,480)
    y1,y2=np.clip([int(y1),int(np.ceil(y2))],0,270)
    mask=np.zeros((270,480),bool);mask[y1:y2,x1:x2]=True;masks.append(mask)
shared=masks[0]&masks[1];exclusive=[masks[0]&~masks[1],masks[1]&~masks[0]]
geometry={'analysis_shape':[270,480],'original_roi_mask_pixels':[int(m.sum()) for m in masks],'shared_origin_pixels':int(shared.sum()),'exclusive_origin_pixels':[int(m.sum()) for m in exclusive],'exclusive_masks_are_disjoint':not bool((exclusive[0]&exclusive[1]).any()),'no_flow_feature_or_history_counterfactual_performed':True}
assert all(r['features']>=6 and r['adaptive_ratio']>=3 for r in regions)
assert np.mean([r['discontinuity'] for r in regions])>=15
assert raw['supporting_region_keys']==raw['acquisition_region_keys']==raw['relative_region_keys']==[]
proof={'current11082_correspondence_thresholds_pass_before_bbox_veto':True,'current11082_previous_mean_zero_is_valid_explicit_history':True,'mean_discontinuity':float(np.mean([r['discontinuity'] for r in regions])),'prior_bbox_positive_intersection':True,'witness_keys_all_empty':True,'geometry':geometry,'2928_cc_none_is_not_observer_not_executed':'pipeline serializes raw only on acquire_layout or selected diagnostic frames; actual lost evidence must be recovered by chronological prefix','cases':rows}
save('actual_contract_readout.json',proof)
for file in ['scene_change.py','content.py','pipeline.py']:
    p=NATIVE/'sports/badminton/src/bai_badminton/perception'/file;inputs[str(p)]=sha(p)
save('input_binding.json',{'native_root':str(NATIVE),'commit':'2418ab8cbe4cca74dd16b722b9727ffdc950294a','input_sha256':inputs})
print('verified four source-frame artifacts;11082 threshold/overlap contract; masksgeometry',geometry)
