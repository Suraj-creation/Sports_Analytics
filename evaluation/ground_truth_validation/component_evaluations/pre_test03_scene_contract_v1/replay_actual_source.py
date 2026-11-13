"""Read-only source-pixel scene-component probe on FAILED partial run, no inference.

Replays native old observer with each recorded preceding foreground region.
Never calls completed-run evaluators or treats partial outputs as a benchmark.
"""
from pathlib import Path
from hashlib import file_digest,sha256
from dataclasses import asdict
import json
import av
import cv2
import msgpack
from bai_badminton.perception.scene_change import ForegroundRegion,SceneContinuityDetectorV4
from bai_badminton.perception.content import scene_change_to_dict
import bai_badminton.perception.scene_change as native

ROOT=Path('/home/administrator/Desktop/sport-analytics')
OLD=ROOT/'test03-scene-acquisition-20261112'
ART=ROOT/'ground-truth-validation-artifacts-20261112/pre_test03_v3/test01_candidate_v3'
OUT=Path(__file__).resolve().parent
SOURCE_SHA='877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6'
PROXY_SHA='d352d684fb5399d804b8f50c785a3605346e7f03987ecb1d9a73ef3482535a97'
INPUTS={}

def sha(p):
    with Path(p).open('rb') as f:return file_digest(f,'sha256').hexdigest()

def read(p):INPUTS[str(p)]=sha(p);return json.loads(p.read_text())

def save(name,obj):
    with (OUT/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')

def main():
    assert Path(native.__file__).resolve().is_relative_to(OLD)
    assert not (ART/'completion.json').exists()
    preflight=read(ART/'preflight.json');assert preflight['pipeline_root']==str(OLD) and preflight['commit']=='a14695372f0d66d0c80a0bbad8d2c63864001d95'
    source=Path(preflight['video']);assert sha(source)==SOURCE_SHA;INPUTS[str(source)]=SOURCE_SHA
    paths=sorted((ART/'run/data/sessions/UPLOADTEST1/perception').glob('*.msgpack'));records={}
    for p in paths:
        INPUTS[str(p)]=sha(p);packet=msgpack.unpackb(p.read_bytes(),raw=False)
        assert packet['v']==23
        records.update({r['f']:r for r in packet['frames']})
    assert sorted(records)==list(range(1500))
    proxy=ART/'run/data/media'/SOURCE_SHA/'proxy.mp4';assert sha(proxy)==PROXY_SHA;INPUTS[str(proxy)]=PROXY_SHA
    parameters=packet['ci']['profile']['components']['content_continuity']['params'];assert parameters=={'mode':'barrier_detector_layout_v2'}
    for rel in ['scene_change.py','content.py','pipeline.py','players.py']:
        p=OLD/'sports/badminton/src/bai_badminton/perception'/rel;INPUTS[str(p)]=sha(p)
    failure_log=ART/'run.execution.log';INPUTS[str(failure_log)]=sha(failure_log)
    observer=SceneContinuityDetectorV4();parity=[];errors=[];source_rows=[];raw_count=0
    cv2.setNumThreads(1)
    selected=OUT/'source_evidence';selected.mkdir(exist_ok=False)
    with (OUT/'source_reconstructed_raw.jsonl').open('x') as raw_output:
        with av.open(str(proxy)) as container:
            stream=container.streams.video[0];stream.thread_count=1
            for decoded in container.decode(video=0):
                f=round(float(decoded.pts*decoded.time_base)*30)
                if f>1500:break
                assert abs(float(decoded.pts*decoded.time_base)-f/30)<1e-8
                image=decoded.to_ndarray(format='bgr24')
                previous=records.get(f-1);current=records.get(f)
                current_replay=current['r'] if current is not None else False
                hard=bool(current and previous and current['sh']!=previous['sh'])
                regions=tuple(ForegroundRegion(**r) for r in previous['fg']) if previous else ()
                raw=observer.observe(f,image,previous_regions=regions,previous_view_valid=bool(previous and not previous['r']),current_view_valid=not current_replay,hard_cut=hard)
                value=asdict(raw);raw_output.write(json.dumps({'frame':f,'raw_unvalidated_observer_output':value},allow_nan=False)+'\n');raw_count+=1
                if current is not None and current.get('cc') is not None:
                    exact=json.dumps(value,sort_keys=True)==json.dumps(current['cc'],sort_keys=True)
                    parity.append({'frame':f,'exact_recorded_retained_observer_equal':exact})
                if f>=1495:
                    dest=selected/f'frame_{f:05d}.png';assert cv2.imwrite(str(dest),image)
                    source_rows.append({'frame':f,'pts':decoded.pts,'time_base':str(decoded.time_base),'bgr_sha256':sha256(image.tobytes()).hexdigest(),'png':str(dest.relative_to(OUT)),'png_sha256':sha(dest),'preceding_regions_exactly_recorded':f-1 in records,'current_view_flag_source':'actual_partial_cache' if current is not None else 'explicit_nonreplay_probe_assumption_at_first_uncached_frame'})
                try:scene_change_to_dict(raw)
                except ValueError as error:
                    affected=[asdict(r) for r in raw.regions if r.features<6]
                    errors.append({'frame':f,'error':str(error),'low_feature_regions':affected,'raw_unvalidated':value})
                    if f>=1500:break
    save('observer_replay_failures.json',errors)
    save('retained_observer_parity.json',parity)
    save('source_frames.json',source_rows)
    INPUTS[str(Path(__file__))]=sha(__file__)
    assert all(sha(p)==h for p,h in INPUTS.items())
    summary={'status':'source_component_probe_of_failed_partial_run_not_evaluation','native_root':str(OLD),'native_commit':preflight['commit'],'cached_extent':[0,1499],'raw_observer_frames_replayed':raw_count,'source_sha256':SOURCE_SHA,'proxy_sha256':PROXY_SHA,'recorded_retained_cc_comparisons':len(parity),'exact_recorded_cc_matches':sum(p['exact_recorded_retained_observer_equal'] for p in parity),'failure_frames':[r['frame'] for r in errors],'first_uncached_frame_probe_view_assumption':'nonreplay; no post1499 player/foreground predictions were fabricated','neural_inference':False,'completed_run_or_accuracy_claimed':False,'input_sha256':INPUTS}
    save('source_replay_receipt.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':main()
