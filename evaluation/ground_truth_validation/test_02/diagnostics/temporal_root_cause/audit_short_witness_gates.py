"""Recompute typed episode gate on original consumed contact evidence only."""
from pathlib import Path
import sys,json,hashlib

ROOT=Path(__file__).resolve().parents[5]
sys.path.insert(0,str(ROOT/'sports/badminton/src'))
from bai_badminton.events.exchange_evidence import ContactParticipantContext,ContactParticipantObservation,simultaneous_opponents

OUT=Path(__file__).resolve().parent
SOURCE=ROOT.parent/'ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run/events.jsonl'
PAIRS={'G31':[11715,11740],'G32':[11899,11922],'G56':[20947,20994],
       'G58_walking_control':[21759,21771],'G63':[23968,24009]}
wanted={f for pair in PAIRS.values()for f in pair};contacts={}
for line in SOURCE.open():
    e=json.loads(line)
    if e['type']=='contact' and e['frame_start'] in wanted and e['frame_start']not in contacts:
        pe=e['payload'].get('physical_evidence')
        if pe:
            contacts[e['frame_start']]=pe
assert set(contacts)==wanted

def context(raw):
    if raw is None:return None
    return ContactParticipantContext(raw['shot_id'],raw['content_epoch'],raw['coordinate_epoch'],
             tuple(ContactParticipantObservation(**row)for row in raw['observations']))

rows=[]
for name,frames in PAIRS.items():
    a,b=(contacts[f]for f in frames);i,j=a['inputs'],b['inputs']
    proof=simultaneous_opponents(context(i.get('participant_context')),i.get('attribution_target'),
             context(j.get('participant_context')),j.get('attribution_target'))
    ma,mb=i.get('motion')or{},j.get('motion')or{}
    fa=ma.get('before_frames',[])+ma.get('after_frames',[]);fb=mb.get('before_frames',[])+mb.get('after_frames',[])
    motion_gates=[bool(m.get('spatial_sigma_px')is not None and len(m.get('before_frames',[]))>=2
                   and len(m.get('after_frames',[]))>=2 and
                   ((m.get('incoming_direction_support')or 0)>0 or(m.get('outgoing_direction_support')or 0)>0))for m in (ma,mb)]
    probable=any(v[k]['reliability']in('probable','confirmed')for v in(a,b)for k in('impact','trajectory'))
    rows.append({'case':name,'witness_frames':frames,'typed_stable_opponent_proof':proof,
      'targets':[i.get('attribution_target'),j.get('attribution_target')],
      'motion_gates':motion_gates,'motion_windows_disjoint':not set(fa).intersection(fb),
      'any_probable_trajectory_or_impact':probable,
      'assessment_reliabilities':[{k:v[k]['reliability']for k in('trajectory','impact')}for v in(a,b)],
      'participant_context_episode_sets':[sorted({o['participant_id']for o in q.get('participant_context',{}).get('observations',[])})for q in(i,j)],
      'sampled_pair_passes_required_gates':proof is not None and all(motion_gates)and not set(fa).intersection(fb)and probable,
      'independent_physical_impact_validated':False})
with SOURCE.open('rb')as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
with (OUT/'short_witness_gate_audit.json').open('x')as f:
    json.dump({'schema':'test02-original-contact-short-witness-gate-audit:v1','events_path':str(SOURCE),
       'events_sha256':digest,'scope':'Original evidence consumed by actual FSM, not later public sanitized contact payloads',
       'no_new_inference':True,'pairs':rows},f,indent=2);f.write('\n')
for r in rows:print(r['case'],'opponents',r['typed_stable_opponent_proof']is not None,'probable',r['any_probable_trajectory_or_impact'],'passes',r['sampled_pair_passes_required_gates'])
