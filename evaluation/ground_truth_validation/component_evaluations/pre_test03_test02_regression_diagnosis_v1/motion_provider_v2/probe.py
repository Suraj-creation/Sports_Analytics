"""Existing motion-reliability provider component counterfactual; no live profile change."""
import json
from dataclasses import asdict
from hashlib import file_digest
from pathlib import Path
from types import SimpleNamespace

import msgpack
import numpy as np

NATIVE=Path('/home/administrator/Desktop/sport-analytics/test03-scene-evidence-contract-20261112')
MAIN=NATIVE.parent/'Sports_Analytics'
ART=NATIVE.parent/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4'
BASE=NATIVE.parent/'ground-truth-validation-artifacts-20261110/test_02/improved_v1'
REPLAY=ART.parent/'test02_postprocessing_v1/diagnostic_replay'
OUT=Path(__file__).resolve().parent
INPUTS={}


def sha(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()


def read(path):
    INPUTS[str(path)]=sha(path)
    return json.loads(Path(path).read_text())


def save(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def compact(c):
    return None if c is None else {'frame':c.frame,'p':c.p,'player_episode_track':c.player_id,'scores':c.scores,
                                  'shuttle_xy':c.shuttle_xy,'attribution_reason':c.attribution_reason}


def main():
    from research import pipeline_repair_run_analysis as native
    from research.production_external_semantic_replay import verify_replay_output_artifacts
    from bai_badminton.plugin import BadmintonSession
    from bai_badminton.engine import _stabilise
    from bai_badminton.perception.camera import project
    from bai_badminton.perception.shuttle_post import Track,process
    from bai_badminton.observations import PlayerSeries,WindowObs
    from bai_badminton.racket_admission import admit_racket_candidates
    from bai_badminton.events.contact import score_frame,detect_contacts,ATTRIBUTION_MIN_PROXIMITY,ContactMotionReliability
    assert native.ROOT==NATIVE
    bound=native.load_analysis_input(ART/'run',None)
    assert bound['completion_mode']=='normal_completed_worker' and bound['media']['n_frames']==29296
    manifest=read(REPLAY/'replay_manifest.json');verify_replay_output_artifacts(REPLAY,manifest)
    assert manifest['trace_step_count']==29296 and manifest['baseline_parity'] is True
    parity=read(REPLAY/'parity_vs_fresh.json');assert parity['differences']==[]
    for name,sub in [('before_worker.json','run/inference.json'),('before_catalogue.json','run/perception_completion_catalog.json')]:
        assert sha(ART/name)==sha(BASE/sub)
    plan=read(ART/'protocol/plan.json')
    for path,digest in plan['source_files_sha256'].items():assert sha(path)==digest
    motion_policy=ContactMotionReliability(bound['profile']['components']['contact']['params']['spatial_sigma_px'])
    windows=[(780,959),(4590,4799),(11640,11819)]
    selected={f for lo,hi in windows for f in range(lo,hi+1)}
    frames={};packets={}
    for label,root in [('before',BASE/'run'),('after',ART/'run')]:
        catalogue=read(root/'perception_completion_catalog.json');frames[label]={};packets[label]=[]
        for entry in catalogue['files']:
            if not any(entry['start']<=f<=entry['end'] for f in selected):continue
            path=root/entry['path'];assert sha(path)==entry['sha256'];INPUTS[str(path)]=entry['sha256']
            wire=msgpack.unpackb(path.read_bytes(),raw=False)
            receiver=SimpleNamespace(perception=SimpleNamespace(ref_id=wire['cr']),_isolation_id=lambda wire=wire:wire['ci'])
            decoded=BadmintonSession.decode_perception(receiver,path.read_bytes(),diagnostic=True)
            packets[label].append(wire)
            for raw,typed in zip(wire['frames'],decoded.frames,strict=True):
                if raw['f'] in selected:frames[label][raw['f']]=(raw,typed)
    trace_path=REPLAY/'bounded_fsm_trace.jsonl';INPUTS[str(trace_path)]=sha(trace_path)
    trace=[]
    for line in trace_path.open():
        row=json.loads(line)
        if row['frame'] in selected:trace.append(row)
    with (OUT/'actual_trace_cases.jsonl').open('x') as f:
        for row in trace:f.write(json.dumps(row,allow_nan=False)+'\n')
    step={r['frame']:r for r in trace if r['call']=='step'}
    case=[]
    for lo,hi in windows:
        arms={}
        for label in ['before','after']:
            n=hi-lo+1;raw=[frames[label][f][0] for f in range(lo,hi+1)];typed=[frames[label][f][1] for f in range(lo,hi+1)]
            x=np.full(n,np.nan);y=x.copy();v=np.zeros(n,bool);conf=np.zeros(n);players={};breaks=np.zeros(n,bool)
            excluded=np.zeros(n,bool);replay=np.asarray([f.replay for f in typed]);evidence=tuple(f.shuttle_observation for f in typed)
            for i,fp in enumerate(typed):
                inverse=np.linalg.inv(fp.cam) if fp.cam is not None else None
                xy=fp.shuttle_observation.selected_xy if fp.shuttle_observation is not None else fp.shuttle_xy
                if xy is not None:
                    q=project(inverse,[xy])[0] if inverse is not None else np.asarray(xy);x[i],y[i]=q;v[i]=True
                conf[i]=fp.shuttle_conf
                excluded[i]=(fp.view!='main' or fp.cam is None or fp.replay
                             or (fp.shuttle_observation is not None and (fp.shuttle_observation.status in {'ambiguous','invalid'}
                                 or fp.shuttle_observation.association_status=='rejected')))
                if i:breaks[i]=any(raw[i][k]!=raw[i-1][k] for k in ['sh','ce','r','v'])
                semantic,_=admit_racket_candidates(fp.persons,frame_idx=fp.frame_idx)
                for p in semantic:
                    p=_stabilise(p,inverse) if inverse is not None else p
                    # Conditional current visual series only, not identity or
                    # participant admission. Actual event score controls below
                    # establish whether this simplified local view agrees.
                    key=str(p.track_id);series=players.setdefault(key,PlayerSeries.empty(n));series.bbox[i]=p.bbox
                    if p.kps is not None:series.kps[i]=p.kps
                    if p.detector_matched is True:series.racket[i]=p.racket
            policies={}
            for policy in ['legacy','current']:
                processing_breaks=breaks.copy()
                if policy=='current':
                    processing_breaks|=excluded;processing_breaks[1:]|=excluded[:-1]
                track=process(Track.from_arrays(x,y,v&~excluded,conf),break_before=processing_breaks)
                if policy=='legacy':
                    for i,e in enumerate(evidence):
                        if e is not None and e.status!='observed':track.vis[i]=False;track.interp[i]=False
                else:track.vis[excluded]=False;track.interp[excluded]=False
                w=WindowObs(lo,30.,track,players,replay,np.asarray([f.pose_stride or 0 for f in typed]),breaks,evidence)
                candidates=[score_frame(w,i,motion_reliability=motion_policy) for i in range(n)]
                kept=detect_contacts(w,enforce_alternation=False,proximity_split=ATTRIBUTION_MIN_PROXIMITY,motion_reliability=motion_policy)
                policies[policy]={'all_scores':[compact(c) for c in candidates if c is not None],
                                  'kept':[compact(c) for c in kept]}
                if label=='after' and policy=='current':
                    observed_errors=[]
                    for f in range(lo,hi+1):
                        a=step.get(f)
                        if a and a['observation']['kind']=='observed':
                            assert not a['interpolated'] and track.vis[f-lo] and not track.interp[f-lo]
                            observed_errors.append(float(np.linalg.norm(np.asarray(a['processed_xy'])-[track.x[f-lo],track.y[f-lo]])))
                    policies[policy]['actual_full_engine_observed_point_max_error']=max(observed_errors,default=None)
            arms[label]=policies
        case.append({'range':[lo,hi],'arms':arms})
    save('component_score_probes.json',{'scope':'Bounded source-cache conditional raw-track visual series, not full participant/engine replay. Validate actual anchor score agreement before causal use.','cases':case})
    events={}
    for label,root in [('before',BASE/'run'),('after',ART/'run')]:
        path=root/'events.jsonl';INPUTS[str(path)]=sha(path);all_events=[json.loads(s) for s in path.open()]
        live=native.select_live_events(all_events,all_events[0]['session_id'])
        events[label]={'live':[e for e in live if e['frame_start'] in selected and e['type'] in {'contact','stroke','rally_start','rally_end'}],
                       'append_only':[e for e in all_events if e['frame_start'] in selected and e['type'] in {'contact','stroke','rally_start','rally_end'}]}
    save('actual_event_cases.json',events)
    save('cache_cases.json',{label:{str(f):raw for f,(raw,_) in rows.items()} for label,rows in frames.items()})
    summary=[]
    for c in case:
        for label,policies in c['arms'].items():
            p=policies['current' if label=='after' else 'legacy'];scores={a['frame']:a for a in p['all_scores']}
            anchors=[f for f in [809,904,4633,4681,11714,11715,11716,11717,11718,11720,11731,11740] if c['range'][0]<=f<=c['range'][1]]
            summary.append({'range':c['range'],'arm':label,'anchors':[{'frame':f,'score':scores.get(f)} for f in anchors],
                            'kept':[a['frame'] for a in p['kept']]})
    save('component_probe_summary.json',summary)
    assert all(sha(p)==h for p,h in INPUTS.items())
    save('probe_input_receipt.json',{'status':'completed_bounded_readonly_component_probe','native_root':str(NATIVE),'frames':29296,
         'full_fresh_own_replay_parity':True,'new_NN_or_full_engine_replay':False,'original_changes':False,'policy':{'provider':'existing_contact_motion_reliability_v1','spatial_sigma_px':motion_policy.spatial_sigma_px,'p_min_unchanged':0.35},'input_sha256':INPUTS})
    print(json.dumps([{'range':c['range'],'arm':c['arm'],'kept':c['kept'],
                      'scores':[(s['frame'],None if s['score'] is None else round(s['score']['p'],6)) for s in c['anchors']]} for c in summary],indent=2))

if __name__=='__main__':main()
