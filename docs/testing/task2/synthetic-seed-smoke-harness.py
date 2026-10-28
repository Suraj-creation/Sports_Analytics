from __future__ import annotations
import json,os,sqlite3
from pathlib import Path
from bai_badminton.analytics.automatic_individual import _continuous, build_estimated_individual_analytics
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import TrackObject
from bai_engine.schema.session import ParticipantInfo, ParticipantRoster
from bai_engine.store import EventStore,TrackStore
p=Path(os.environ['TASK2_TRACK_REPLAY']); sid='01M56T2EED5Z7W9VTGG19FHNTF'
src=p/(sid+'.sqlite'); dest=p/'synthetic-seeds.sqlite'
if dest.exists(): raise FileExistsError(dest)
with sqlite3.connect('file:'+str(src)+'?mode=ro',uri=True) as r, sqlite3.connect(dest) as w: r.backup(w)
store=EventStore(dest,sid); tracks=TrackStore(p/(sid+'-tracks'))
roster=ParticipantRoster(match_format='doubles',participants=[ParticipantInfo(participant_id=f'U{i}',name=f'Synthetic {i}') for i in range(1,5)])
kwargs=dict(max_frame=12147,fps=25,frame_width=1280,frame_height=720,include_events=True)
base=build_estimated_individual_analytics(store,tracks,None,**kwargs)
ledger=IdentityReviewLedger(store,{f'U{i}' for i in range(1,5)},max_frame=12147,fps=25)
seeds=[]
for episode in base['episode_profiles']['all_linked']['episodes']:
    if len(seeds)>=4: break
    for ev in episode['events']:
        frame=ev['frame']; obs=store.get(episode['observation_id'])
        if obs is None: continue
        rows=tracks.read([TrackObject.PLAYER],max(obs.frame_start,frame-6),frame).to_pylist()
        prior=sorted({r['frame_idx'] for r in rows if r['frame_idx']<frame and r['track_id']==episode['track_id']
            and r['participant_observation_id']==episode['observation_id']},reverse=True)
        selected=next((f for f in prior if _continuous(rows,episode['observation_id'],episode['track_id'],f,frame,1280,720)),None)
        if selected is None: continue
        pid=f'U{len(seeds)+1}'
        try: review=ledger.confirm(episode['observation_id'],pid,selected,selected)
        except ValueError: continue
        result=build_estimated_individual_analytics(store,tracks,roster,**kwargs)
        if result['all_linked']['participants'][pid]['estimated_shots']:
            seeds.append({'synthetic_player':pid,'observation_id':episode['observation_id'],'seed_frame':selected,
                'target_shot':ev['event_id'],'shot_frame':frame,'review_id':review.event_id})
            break
        ledger.revoke(review.event_id)
result=build_estimated_individual_analytics(store,tracks,roster,**kwargs)
counts={pid:v['estimated_shots'] for pid,v in result['all_linked']['participants'].items()}
summary={'kind':'synthetic_seed_integration_smoke','accuracy_claim':False,'identity_mapping_real':False,
    'note':'Synthetic labels and simulated reviews on a copied event database, not human identity annotations.',
    'seeds':seeds,'all_linked_counts':counts,'official_accounting':result['official']['accounting'],
    'all_linked_accounting':result['all_linked']['accounting']}
(p/'synthetic-seed-smoke.json').write_text(json.dumps(summary,indent=2))
print(json.dumps({'simulated_seeds':len(seeds),'counts':counts,'official':result['official']['accounting'],
    'all_linked':result['all_linked']['accounting']}))
if not seeds: raise RuntimeError('No synthetic seeded episode could be verified through the pipeline')
