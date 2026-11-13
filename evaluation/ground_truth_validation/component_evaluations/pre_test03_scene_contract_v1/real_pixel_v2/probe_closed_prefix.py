"""Actual current closed-prefix pixels/foreground; historical validator counterfactual.

This does not reconstruct the old process's unavailable fatal frame, load models,
run a neural pipeline, or evaluate an incomplete video against annotations.
"""
from pathlib import Path
from hashlib import file_digest,sha256
from dataclasses import asdict
from collections import deque
import importlib.util
import json
import sys
import copy
import av
import cv2
import msgpack
from bai_badminton.perception import scene_change
from bai_badminton.perception.scene_change import SceneContinuityDetectorV4,ForegroundRegion
from bai_badminton.perception.content import scene_change_to_dict

ROOT=Path('/home/administrator/Desktop/sport-analytics')
NATIVE=ROOT/'test03-scene-evidence-contract-20261112'
OLD=ROOT/'test03-scene-acquisition-20261112'
ART=ROOT/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test01_candidate_v4'
FAILED=ROOT/'ground-truth-validation-artifacts-20261112/pre_test03_v3/test01_candidate_v3'
OUT=Path(__file__).resolve().parent
SOURCE_SHA='877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6'
PROXY_SHA='d352d684fb5399d804b8f50c785a3605346e7f03987ecb1d9a73ef3482535a97'
INPUTS={}

def sha(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()

def read(path):INPUTS[str(path)]=sha(path);return json.loads(path.read_text())

def write(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')

def cache_prefix(run,chunks):
    rows={}
    for i in range(chunks):
        p=run/f'run/data/sessions/UPLOADTEST1/perception/seg_{i:05d}.msgpack'
        before=sha(p);packet=msgpack.unpackb(p.read_bytes(),raw=False)
        assert packet['v']==23 and packet['start']==i*60 and packet['end']==(i+1)*60-1
        assert [r['f'] for r in packet['frames']]==list(range(i*60,(i+1)*60))
        assert before==sha(p);INPUTS[str(p)]=before;rows.update({r['f']:r for r in packet['frames']})
    return rows


def main():
    assert Path(scene_change.__file__).resolve().is_relative_to(NATIVE)
    assert sha(NATIVE/'sports/badminton/src/bai_badminton/perception/scene_change.py')==sha(OLD/'sports/badminton/src/bai_badminton/perception/scene_change.py')
    preflight=read(ART/'preflight.json');assert preflight['pipeline_root']==str(NATIVE) and preflight['commit']=='2418ab8cbe4cca74dd16b722b9727ffdc950294a'
    current=cache_prefix(ART,26);old=cache_prefix(FAILED,25)
    overlap=[{'frame':f,'foreground_exact':old[f]['fg']==current[f]['fg'],'retained_cc_exact':old[f]['cc']==current[f]['cc'],'view_flags_exact':(old[f]['r'],old[f]['sh'])==(current[f]['r'],current[f]['sh'])} for f in range(1500)]
    write('old_current_overlap_comparison.json',overlap)
    proxy=ART/'run/data/media'/SOURCE_SHA/'proxy.mp4';assert sha(proxy)==PROXY_SHA;INPUTS[str(proxy)]=PROXY_SHA
    old_content=OLD/'sports/badminton/src/bai_badminton/perception/content.py'
    # Historical validator code is loaded unchanged; its imported raw-evidence
    # class/observer module is byte-identical between old and current source.
    spec=importlib.util.spec_from_file_location('preserved_old_scene_content_counterfactual',old_content)
    historical=importlib.util.module_from_spec(spec);sys.modules[spec.name]=historical;spec.loader.exec_module(historical)
    for p in [old_content,NATIVE/'sports/badminton/src/bai_badminton/perception/content.py',Path(scene_change.__file__)]:INPUTS[str(p)]=sha(p)
    observer=SceneContinuityDetectorV4();counterfactual=[];parity=[];fixed=[];low=[];pictures=[];ring=deque(maxlen=2);selected_frame=None;forgery=None
    cv2.setNumThreads(1);images=OUT/'source_evidence';images.mkdir(exist_ok=False)
    def save_image(frame,image,pts,timebase):
        dest=images/f'frame_{frame:05d}.png'
        if dest.exists():return
        assert cv2.imwrite(str(dest),image)
        pictures.append({'frame':frame,'source_pts':pts,'source_time_base':str(timebase),'source_bgr_sha256':sha256(image.tobytes()).hexdigest(),'png':str(dest.relative_to(OUT)),'png_sha256':sha(dest)})
    with (OUT/'observer_raw_rows.jsonl').open('x') as raw_file:
        with av.open(str(proxy)) as container:
            stream=container.streams.video[0];stream.thread_count=1
            for decoded in container.decode(video=0):
                f=round(float(decoded.pts*decoded.time_base)*30)
                if f>=1560:break
                assert abs(float(decoded.pts*decoded.time_base)-f/30)<1e-8
                image=decoded.to_ndarray(format='bgr24');previous=current.get(f-1);record=current[f]
                regions=tuple(ForegroundRegion(**r) for r in previous['fg']) if previous else ()
                raw=observer.observe(f,image,previous_regions=regions,previous_view_valid=bool(previous and not previous['r']),current_view_valid=not record['r'],hard_cut=bool(previous and record['sh']!=previous['sh']))
                value=asdict(raw);raw_file.write(json.dumps({'frame':f,'actual_current_closed_prefix_observer':value},allow_nan=False)+'\n')
                fixed.append({'frame':f,'fixed_validator_accepted':scene_change_to_dict(raw)==value})
                if record['cc'] is not None:
                    parity.append({'frame':f,'exact_current_retained_cc_equal':json.dumps(value,sort_keys=True)==json.dumps(record['cc'],sort_keys=True)})
                for i,r in enumerate(raw.regions):
                    if r.features<6 and r.median_patch_error is not None:
                        low.append({'frame':f,'region_index':i,**asdict(r)})
                try:historical.scene_change_to_dict(raw)
                except ValueError as error:
                    counterfactual.append({'frame':f,'error':str(error),'regions':[{**asdict(r),'region_index':i} for i,r in enumerate(raw.regions) if r.features<6],'scope':'Old validator on ACTUAL CURRENT-run input, not recovered original fatal frame'})
                    if selected_frame is None:
                        selected_frame=f
                        for sample in ring:save_image(*sample)
                        save_image(f,image,decoded.pts,decoded.time_base)
                        # A numerically consistent low-feature ratio remains
                        # unsupported evidence and must be rejected by the fix.
                        for i,r in enumerate(raw.regions):
                            if r.features<6 and r.median_patch_error is not None and r.appearance_previous_mean is not None:
                                forged=copy.deepcopy(value);forged['regions'][i]['appearance_adaptive_ratio']=r.median_patch_error/max(1.,r.appearance_previous_mean)
                                old_accept=True;new_accept=True
                                try:historical.scene_change_from_dict(forged)
                                except ValueError:old_accept=False
                                try:
                                    from bai_badminton.perception.content import scene_change_from_dict
                                    scene_change_from_dict(forged)
                                except ValueError:new_accept=False
                                forgery={'frame':f,'region_index':i,'features':r.features,'forged_ratio':forged['regions'][i]['appearance_adaptive_ratio'],'old_validator_accepts':old_accept,'fixed_validator_accepts':new_accept,'scope':'Controlled unsupported-value mutation of actual current-run measurement'}
                                break
                if selected_frame is not None and f==selected_frame+1:save_image(f,image,decoded.pts,decoded.time_base)
                ring.append((f,image.copy(),decoded.pts,decoded.time_base))
    assert len(fixed)==1560 and all(x['fixed_validator_accepted'] for x in fixed)
    assert all(x['exact_current_retained_cc_equal'] for x in parity)
    write('old_validator_current_input_rejections.json',counterfactual);write('low_feature_current_measurements.json',low);write('current_retained_cc_parity.json',parity);write('real_measurement_forgery_control.json',forgery);write('source_frames.json',pictures)
    INPUTS[str(Path(__file__))]=sha(__file__);assert all(sha(p)==h for p,h in INPUTS.items())
    result={'status':'completed_bounded_current_input_scene_contract_probe_not_full_evaluation','native_root':str(NATIVE),'native_commit':preflight['commit'],'source_sha256':SOURCE_SHA,'proxy_sha256':PROXY_SHA,'actual_closed_extent':[0,1559],'old_overlap_extent':[0,1499],'old_current_foreground_equal_frames':sum(x['foreground_exact'] for x in overlap),'old_current_retained_cc_equal_frames':sum(x['retained_cc_exact'] for x in overlap),'old_current_view_flags_equal_frames':sum(x['view_flags_exact'] for x in overlap),'current_retained_cc_exact_parity':[sum(x['exact_current_retained_cc_equal'] for x in parity),len(parity)],'fixed_validator_accepted_frames':len(fixed),'old_validator_rejection_frames_on_current_inputs':[r['frame'] for r in counterfactual],'old_precise_fatal_frame_recovered':False,'forged_ratio_control':forgery,'new_neural_inference':False,'completed_benchmark_or_physical_accuracy_claimed':False,'all_input_hashes_unchanged':True,'input_sha256':INPUTS}
    write('receipt.json',result);print(json.dumps({k:v for k,v in result.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':main()
