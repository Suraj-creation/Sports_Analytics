"""Exploratory width-ablation shadow AFTER width failure diagnosis; not held-out validation.

Every parameter is inherited from installed BoTSORT/noise, existing ROI IoU .3
and source one-second missing-observation budget, or fixed chi-square4D95%.
No roster identity, team/score authority, new neural inference or source edits.
"""
from pathlib import Path
from dataclasses import dataclass
from collections import Counter
import json
import numpy as np
import probe_backend_gate as base
from trackers.core.botsort.tracklet import BoTSORTTracklet
from trackers.utils.predict_timing import PredictTiming
from bai_badminton.court import Homography
from bai_badminton.perception.players import CourtROI

OUT=Path(__file__).resolve().parent/'hypothesis_partition_v3'
LIMIT=base.LIMIT


def gate(track,box):
    track._refresh_measurement_noise_from_state()
    return base.gate(track,box)


class Hypothesis:
    """Origin-linked anonymous geometric hypothesis, with independent authority."""
    def __init__(self,fps=30):
        self.fps=fps;self.states=[];self.serial=0;self.last=-1
    def reset(self):
        self.states=[]
    def step(self,f,boxes,inside,observed):
        assert f>self.last;self.last=f
        self.states=[s for s in self.states if f-s['last']<=self.fps]
        if not observed:
            return {'frame':f,'observed':False,'accepted':[],'regions':[{'id':s['id'],'box':s['box'].tolist(),'anchor':s['anchor'],'last':s['last']} for s in self.states],'decisions':[]}
        boxes=np.asarray(boxes,float).reshape(-1,4);inside=np.asarray(inside,bool)
        decisions=[];accepted=[];used=set();remove=set()
        for s in self.states:
            dt=f-s['pred'];s['track'].predict(PredictTiming(dt,dt/self.fps,frame_rate=self.fps));s['pred']=f
        overlaps=np.asarray([[base.overlap(s['box'],b)>=.3 for b in boxes] for s in self.states],bool).reshape(len(self.states),len(boxes))
        for j,s in enumerate(self.states):
            cand=np.flatnonzero(overlaps[j])
            if len(cand)!=1 or overlaps[:,cand[0]].sum()!=1:
                decisions.append({'id':s['id'],'status':'missing_or_ambiguous_no_renewal','candidate_indices':cand.tolist()});continue
            i=int(cand[0]);d,mean,S=gate(s['track'],boxes[i]);measurement=s['track'].state_estimator.bbox_to_measurement(boxes[i]);residual2=(measurement-np.asarray(mean))**2/np.asarray(S);center_d2=float(residual2[:2].sum());height_d2=float(residual2[3]);passed=center_d2<=5.9915 and height_d2<=3.8415
            entry={'id':s['id'],'candidate':i,'inside':bool(inside[i]),'d2':d,'center_2d_d2':center_d2,'height_1d_d2':height_d2,'width_1d_d2_diagnostic_only':float(residual2[2]),'predicted_xcycwh':mean,'innovation_cov_diagonal':S,'anchor':s['anchor'],'previous_observed':s['last'],'status':'accepted_unique_current' if passed else 'contradictory_unique_current_origin_revoked'}
            decisions.append(entry)
            if not passed:
                remove.add(s['id']);continue
            s['track'].update(boxes[i]);s['box']=boxes[i].copy();s['last']=f
            if inside[i]:s['anchor']=f
            accepted.append({'id':s['id'],'candidate':i,'inside':bool(inside[i]),'d2':d,'anchor':s['anchor']});used.add(i)
        self.states=[s for s in self.states if s['id'] not in remove]
        for i,b in enumerate(boxes):
            if i not in used and inside[i]:
                # Current actual court evidence may seed anew, but must not
                # multiply an ambiguous bundle of overlapping origin states.
                self.states=[s for s in self.states if base.overlap(s['box'],b)<.3]
                self.serial+=1
                self.states.append({'id':self.serial,'track':BoTSORTTracklet(b),'box':b.copy(),'last':f,'pred':f,'anchor':f})
                accepted.append({'id':self.serial,'candidate':i,'inside':True,'d2':None,'anchor':f})
        return {'frame':f,'observed':True,'accepted':accepted,'regions':[{'id':s['id'],'box':s['box'].tolist(),'anchor':s['anchor'],'last':s['last']} for s in self.states],'decisions':decisions}


def save(name,obj):
    with (OUT/name).open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')


def roi_for(row,H):
    g=np.asarray(row['g']).reshape(3,3) if row['g'] is not None else np.eye(3)
    return CourtROI(np.zeros((4,2),np.float32),homography=Homography(g@H,0,4))


def shadow_full_selected(rows,H,coverage):
    state=Hypothesis();result=[];last_epoch=None
    for row in rows:
        f=row['f'];epoch=(row['sh'],row['ce'])
        if epoch!=last_epoch:state.reset();last_epoch=epoch
        current=[p for p in row['p'] if p['dm']] if row['do'] else []
        boxes=[p['b'] for p in current];roi=roi_for(row,H)
        r=state.step(f,boxes,[roi.contains_feet(np.asarray(b)) for b in boxes],row['do'])
        r['selected_original_observations_only']=True;result.append(r)
    losses=[]
    for old in coverage['all_rows']:
        f=old['frame'];box=old['old_withheld_region']['b'];r=result[f]
        close=[s for s in r['regions'] if base.overlap(s['box'],box)>.99]
        losses.append({'frame':f,'historical_dm':old['old_withheld_region']['dm'],'hypothesis_retained':bool(close),'region_matches':close,'nearest_region_iou':max([base.overlap(s['box'],box) for s in r['regions']],default=0.),'decisions':r['decisions']})
    grouped=[{'frames':g['frames'],'total':g['count'],'retained_exact_region':sum(x['hypothesis_retained'] for x in losses if g['frames'][0]<=x['frame']<=g['frames'][1])} for g in coverage['groups']]
    return grouped,losses,result


def shadow_raw(case,baseline,H):
    rows=case['variants']['foreground'];inputs={};state=Hypothesis();out=[]
    for item in case['detector_inputs']:inputs.setdefault(item['frame'],[]).append(item)
    for r in rows:
        f=r['frame']
        if r['barrier'] or r['hard_camera_cut']:state.reset()
        boxes=[];inside=[]
        if r['detector_observed']:
            choices={json.dumps([x['boxes_crop'],x['scores']]):x for x in inputs[f]};assert len(choices)==1
            p=next(iter(choices.values()));origin=r['tracking_diagnostic']['crop_origin']
            boxes=np.asarray(p['boxes_crop'],float).reshape(-1,4)+np.array([*origin,*origin]);roi=roi_for(baseline[f],H)
            inside=[roi.contains_feet(b) for b in boxes]
        row=state.step(f,boxes,inside,r['detector_observed']);row['raw_boxes']=np.asarray(boxes).tolist();out.append(row)
    summary={'test':case['test'],'range':case['range'],'accepted_outside':sum(not a['inside'] for r in out for a in r['accepted']),'contradiction_revocations':sum(d['status']=='contradictory_unique_current_origin_revoked' for r in out for d in r['decisions'])}
    return summary,out


def main():
    OUT.mkdir(exist_ok=False)
    assert base.sha(base.REVIEW/'verification_receipt.json')==base.read(base.HERE/'summary.json')['input_sha256'][str(base.REVIEW/'verification_receipt.json')]
    cov=base.read(base.REVIEW/'gross_coverage_all_182_rows.json');sources={};baseline={};Hs={}
    for t in [1,2]:
        run=base.OLD/f'test_0{t}/improved_v1/run';baseline[t]=base.frames(run)
        events=run/'events.jsonl';base.INPUTS[str(events)]=base.sha(events)
        Hs[t]=np.asarray(next(json.loads(x)['payload']['H'] for x in events.open() if json.loads(x)['type']=='calibration'))
    groups,losses,allrows=shadow_full_selected(baseline[1],Hs[1],cov)
    save('all_182_selected_observation_differential.json',{'scope':'Historical selected current observations only, no competing unreturned raw detections; conditional potential coverage, NOT complete perception or physical recall','groups':groups,'rows':losses})
    save('selected_observation_full_timeline.json',allrows)
    windows=[]
    for path in sorted(base.PREFIX.glob('test[12]_*.json')):
        case=base.read(path);summary,rows=shadow_raw(case,baseline[case['test']],Hs[case['test']]);windows.append(summary);save(path.stem+'.json',{'summary':summary,'frames':rows})
    base.INPUTS[str(Path(__file__).resolve())]=base.sha(__file__)
    base.INPUTS[str(Path(base.__file__).resolve())]=base.sha(base.__file__)
    import inspect
    for cls in [BoTSORTTracklet,Hypothesis]:
        p=Path(inspect.getfile(cls)).resolve();base.INPUTS[str(p)]=base.sha(p)
    assert all(base.sha(p)==v for p,v in base.INPUTS.items())
    summary={'scope':'Diagnostic only; fixed hypothesis policy not production implementation; no physical accuracy/roster/scoring identity; all182 preserved, ten closed full-raw windows, no inference/source edits','groups':groups,'total_182_retained':sum(r['hypothesis_retained'] for r in losses),'windows':windows,'full_4D95_diagnostic_only':LIMIT,'center_2D95_gate':5.9915,'height_1D95_gate':3.8415,'exploratory_after_width_failure_inspection':True,'roi_iou_existing':.3,'source_missing_budget_seconds':1,'statistical_confidence_calibrated':False,'input_sha256':base.INPUTS}
    save('summary.json',summary);print(json.dumps({k:v for k,v in summary.items() if k!='input_sha256'},indent=2))

if __name__=='__main__':main()
