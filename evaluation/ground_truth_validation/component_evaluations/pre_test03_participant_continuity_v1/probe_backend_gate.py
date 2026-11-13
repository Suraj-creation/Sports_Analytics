"""Read-only conditional motion diagnostics; no production policy/inference changes.

The conditional arm advances the installed model on recorded original selected
measurements, including measurements that a gate would reject. It is NOT a gated
trajectory replay. The independent raw-proposal arm uses a strict fixed gate and
an independently retained origin hypothesis; it is not an engine or named identity.
"""
from pathlib import Path
from hashlib import file_digest
from dataclasses import dataclass
from collections import Counter
import json
import sys
import copy
import importlib.metadata
import msgpack
import numpy as np
from trackers.core.bytetrack.tracklet import ByteTrackTracklet
from trackers.utils.predict_timing import PredictTiming
from bai_badminton.court import Homography
from bai_badminton.perception.players import CourtROI
import bai_badminton.perception.players as players

ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
NATIVE = ROOT / 'test03-scene-continuity-20261112'
HERE = Path(__file__).resolve().parent
PREFIX = MAIN / 'evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_foreground_v1/prefix_v2'
REVIEW = MAIN / 'evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/test01_independent_v2'
OLD = ROOT / 'ground-truth-validation-artifacts-20261110'
LIMIT = 9.4877  # fixed DeepSORT standard 4-dimensional95% quantile; not installed backend calibration
INPUTS = {}


def sha(p):
    with Path(p).open('rb') as f:
        return file_digest(f,'sha256').hexdigest()


def read(p):
    p=Path(p); INPUTS[str(p)] = sha(p)
    return json.loads(p.read_text())


def save(name,obj):
    with (HERE/name).open('x') as f:
        json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')


def dist(x):
    x=np.asarray(x,float)
    return dict(count=len(x),passed=int((x<=LIMIT).sum()),rejected=int((x>LIMIT).sum()),median=float(np.median(x)) if len(x) else None,p95=float(np.percentile(x,95)) if len(x) else None,maximum=float(x.max()) if len(x) else None)


def overlap(a,b):
    a,b=np.asarray(a),np.asarray(b)
    i=np.maximum(0,np.minimum(a[2:],b[2:])-np.maximum(a[:2],b[:2])).prod()
    u=(a[2:]-a[:2]).prod()+(b[2:]-b[:2]).prod()-i
    return float(i/u) if u>0 else 0.


def gate(track,box):
    k=track.state_estimator.kf
    mean=(k.observation_mtx@k.state).ravel()
    S=k.observation_mtx@k.state_covariance@k.observation_mtx.T+k.measurement_noise
    residual=track.state_estimator.bbox_to_measurement(np.asarray(box))-mean
    return float(residual@np.linalg.solve(S,residual)),mean.tolist(),np.diag(S).tolist()


def frames(run):
    catalog=read(run/'perception_completion_catalog.json');out=[]
    for item in catalog['files']:
        p=run/item['path'];assert sha(p)==item['sha256'];INPUTS[str(p)]=item['sha256']
        out.extend(msgpack.unpackb(p.read_bytes(),raw=False)['frames'])
    assert [r['f'] for r in out] == list(range(catalog['frame_count']))
    return out


def conditional(rows,coverage):
    states={};result=[];byframe={};recorded=[]
    for row in rows:
        f=row['f']; epoch=(row['sh'],row['ce'])
        if not row['do']:
            byframe[f]=[];continue
        states={key:value for key,value in states.items() if key[:2]==epoch and f-value['last']<=30}
        for s in states.values():
            dt=f-s['pred'];s['track'].predict(PredictTiming(dt,dt/30,frame_rate=30));s['pred']=f
        current=[]
        for p in row['p']:
            if not p['dm']:continue
            key=(*epoch,p['rt']);box=np.asarray(p['b'],float)
            if key in states:
                s=states[key];d,mean,Sdiag=gate(s['track'],box)
                entry={'frame':f,'raw_track':p['rt'],'epoch':list(epoch),'bbox':box.tolist(),'previous_measurement_frame':s['last'],'d2':d,'passes':d<=LIMIT,'predicted_xyxy':mean,'innovation_cov_diagonal':Sdiag,'selected_observation_history_not_gate_filtered':True}
                result.append(entry);current.append(entry)
                s['track'].update(box);s['last']=f
            else:
                states[key]={'track':ByteTrackTracklet(box),'last':f,'pred':f}
        byframe[f]=current
    for loss in coverage['all_rows']:
        f=loss['frame'];p=loss['old_withheld_region'];match=[x for x in byframe[f] if x['raw_track']==p['rt'] and overlap(x['bbox'],p['b'])>.99]
        recorded.append({'frame':f,'historical_dm':p['dm'],'conditional_observation':match[0] if match else None,'no_current_observation_reason':'scheduled_carry_or_first_observation' if not match else None})
    return {'all_observed_pairs':dist([x['d2'] for x in result]),'loss_groups':[{'frames':g['frames'],'rows':g['count'],'fresh_pairs':dist([x['conditional_observation']['d2'] for x in recorded if g['frames'][0]<=x['frame']<=g['frames'][1] and x['conditional_observation']])} for g in coverage['groups']]},result,recorded


def raw_shadow(case,baseframes,H):
    rows=case['variants']['foreground'];sched={r['frame']:r for r in rows};states=[];serial=0;results=[];detail=[];prior=[]
    inputs={}
    for item in case['detector_inputs']:
        inputs.setdefault(item['frame'],[]).append(item)
    for row in rows:
        f=row['frame']
        if row['barrier'] or row['hard_camera_cut']:
            states=[]
        if not row['detector_observed']:
            states=[s for s in states if f-s['last']<=30]
            results.append({'frame':f,'fresh':False,'hypotheses':[s['id'] for s in states]})
            continue
        original=baseframes[f];g=np.asarray(original['g']).reshape(3,3) if original['g'] is not None else np.eye(3)
        roi=CourtROI(np.zeros((4,2),np.float32),homography=Homography(g@H,0,4))
        origin=row['tracking_diagnostic']['crop_origin'];xx=np.array([*origin,*origin])
        choices=inputs.get(f,[])
        # Same original schedule/geometry; no inference on a missing proposal.
        unique={json.dumps([x['boxes_crop'],x['scores']]):x for x in choices}
        if len(unique)!=1:
            raise ValueError(f'Rawproposal missing/ambiguous: {case["test"]}:{f}')
        item=next(iter(unique.values()));boxes=np.asarray(item['boxes_crop'],float).reshape(-1,4)+xx
        states=[s for s in states if f-s['last']<=30]
        for s in states:
            dt=f-s['pred'];s['track'].predict(PredictTiming(dt,dt/30,frame_rate=30));s['pred']=f
        pair=[]
        for s in states:
            for i,b in enumerate(boxes):
                d,mean,S=gate(s['track'],b);iou=overlap(s['box'],b)
                if iou>=.3:
                    pair.append({'frame':f,'hypothesis':s['id'],'candidate':i,'d2':d,'passes':d<=LIMIT,'iou_last_observed':iou,'box':b.tolist(),'inside':roi.contains_feet(b),'predicted':mean,'innovation_cov_diagonal':S,'anchor':s['anchor']})
        detail.extend(pair)
        accepted=[];used=set()
        # A hypothesis stays only through mutually unique positive observations;
        # an inside observation can start new origin evidence independently.
        for s in states:
            admissible=[p for p in pair if p['hypothesis']==s['id'] and p['passes']]
            if len(admissible)!=1:continue
            p=admissible[0]
            if sum(x['candidate']==p['candidate'] and x['passes'] for x in pair)!=1:continue
            i=p['candidate'];b=boxes[i];s['track'].update(b);s['last']=f;s['box']=b.copy();used.add(i)
            if p['inside']:s['anchor']=f
            accepted.append({'hypothesis':s['id'],'candidate':i,'inside':p['inside'],'last_actual_court_anchor':s['anchor'],'d2':p['d2']})
        for i,b in enumerate(boxes):
            if i not in used and roi.contains_feet(b):
                serial+=1;states.append({'id':serial,'track':ByteTrackTracklet(b),'last':f,'pred':f,'box':b.copy(),'anchor':f});accepted.append({'hypothesis':serial,'candidate':i,'inside':True,'last_actual_court_anchor':f,'d2':None})
        results.append({'frame':f,'fresh':True,'accepted':accepted,'hypotheses':[s['id'] for s in states],'raw_boxes':boxes.tolist(),'supports':item['scores']})
    return {'test':case['test'],'range':case['range'],'fresh_frames':sum(r['fresh'] for r in results),'pair_d2':dist([p['d2'] for p in detail]),'accepted_outside_observations':sum(not a['inside'] for r in results if r['fresh'] for a in r['accepted']),'diagnostic_only_not_complete_pipeline':True},results,detail


def main():
    assert Path(players.__file__).resolve().is_relative_to(NATIVE)
    assert read(REVIEW/'verification_receipt.json')['status']=='completed_independent_Test1_review_with_disclosed_coverage_tradeoffs'
    cov=read(REVIEW/'gross_coverage_all_182_rows.json')
    sources={};baseline={};Hs={}
    for t in [1,2]:
        run=OLD/f'test_0{t}/improved_v1/run'; info=read(run/'inference.json');assert info['status']=='completed' and info['cached_perception_used'] is False
        baseline[t]=frames(run)
        ep=run/'events.jsonl';INPUTS[str(ep)]=sha(ep)
        events=[json.loads(x) for x in ep.open()];Hs[t]=np.asarray(next(x['payload']['H'] for x in events if x['type']=='calibration'))
        sources[t]={'source_sha256':info['source_sha256'],'proxy_sha256':info['proxy_sha256']}
    condition,pairs,loss=conditional(baseline[1],cov)
    save('conditional_backend_pairs.json',pairs);save('all_182_conditional_rows.json',loss)
    windows=[];official=[]
    receipt=read(PREFIX/'artifact_receipt.json')
    for path in sorted(PREFIX.glob('test[12]_*.json')):
        assert sha(path)==receipt['artifact_sha256'][path.name]
        case=read(path);assert case['source_sha256']==sources[case['test']]['source_sha256']
        summary,rows,pair=raw_shadow(case,baseline[case['test']],Hs[case['test']]);windows.append(summary)
        save(path.stem+'_shadow.json',{'summary':summary,'frames':rows,'pairs':pair})
        if case['test']==2 and case['range']==[5505,6510]:
            for f in [5954,5956,5958,5960,6492]:
                selected=[x for x in pair if x['frame']==f];official.append({'frame':f,'pairs':selected,'result':next(x for x in rows if x['frame']==f)})
    save('critical_official_handover.json',official)
    # Freeze pinned installed implementation, not mutable online documentation.
    import trackers
    pkg=Path(trackers.__file__).parent
    for rel in ['core/bytetrack/tracker.py','core/bytetrack/tracklet.py','utils/kalman_filter.py','utils/state_representations.py','utils/motion_models.py','utils/predict_timing.py']:
        p=pkg/rel;INPUTS[str(p)]=sha(p)
    INPUTS[str(Path(__file__))]=sha(__file__)
    summary={'scope':'Fixed standard4D95%9.4877 with installed uncalibrated XYXY covariance. Conditional historical selected observations and separate raw-proposal shadow are distinct; no physical metrics/no new inference/no production change.','native_import_root':str(NATIVE),'trackers_version':importlib.metadata.version('trackers'),'gate':LIMIT,'sources':sources,'conditional':condition,'raw_windows':windows,'all_182_accounted':len(loss),'all_inputs_unchanged':all(sha(p)==s for p,s in INPUTS.items()),'input_sha256':INPUTS}
    assert summary['all_inputs_unchanged'];save('summary.json',summary)
    print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':main()
