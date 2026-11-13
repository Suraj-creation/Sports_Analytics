"""Reassess actual preserved contact evidence and synthetic contract controls only.

No inference, frame-cache loader, engine replay or policy replacement is performed.
"""
from dataclasses import replace
import hashlib
import importlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
MAIN=OUT.parents[3]
NATIVE=MAIN.parent/'test03-scene-evidence-contract-20261112'
EVIDENCE=OUT.parent/'pre_test03_test02_regression_diagnosis_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(n,x):
    with (OUT/n).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
ce=importlib.import_module('bai_badminton.events.contact_evidence')
ex=importlib.import_module('bai_badminton.events.exchange_evidence')
assert Path(ce.__file__).resolve().is_relative_to(NATIVE)
assert Path(ex.__file__).resolve().is_relative_to(NATIVE)
events=json.loads((EVIDENCE/'actual_event_cases.json').read_text())
contact=next(e for e in events['before']['live'] if e['type']=='contact' and e['frame_start']==11715)
original=contact['payload']['physical_evidence']
inputs=dict(original['inputs']);motion=dict(inputs.pop('motion'))
for key in ('before_frames','after_frames'):motion[key]=tuple(motion[key])
ctx=dict(inputs.pop('participant_context'));ctx['observations']=tuple(ex.ContactParticipantObservation(**row) for row in ctx['observations'])
for key in ('player_observation_frames','pose_observation_frames','racket_observation_frames'):inputs[key]=tuple(inputs[key])
base=ce.ContactEvidenceInputs(**inputs,motion=ce.ContactMotionEvidence(**motion),participant_context=ex.ContactParticipantContext(**ctx))
actual=ce.assess_contact_evidence(base)
assert json.loads(json.dumps(actual.to_payload()))==original
results={'actual_preserved11715_reassessment':actual.to_payload(),'synthetic_controls_not_video_observations':{}}
def check(name,inp,expected):
    evidence=ce.assess_contact_evidence(inp)
    assert evidence.impact.reliability.value==expected,(name,evidence)
    results['synthetic_controls_not_video_observations'][name]={'expected_impact':expected,'actual':evidence.to_payload()}
check('original_reacquisition_even_if_player_fresh',replace(base,player_observed=True),'ambiguous')
check('tracked_but_player_not_fresh',replace(base,association_status='tracked'),'insufficient')
check('tracked_fresh_player_without_swing_or_racket',replace(base,association_status='tracked',player_observed=True),'ambiguous')
positive=replace(base,association_status='static_candidate',player_observed=True,pose_observed=True,swing_support=.01)
check('synthetic_static_launch_with_fresh_swing',positive,'probable')
check('synthetic_tracked_launch_with_fresh_swing',replace(positive,association_status='tracked'),'probable')
check('synthetic_reacquisition_despite_fresh_swing',replace(positive,association_status='reacquisition'),'ambiguous')
check('synthetic_stale_player_despite_launch',replace(positive,player_observed=False),'insufficient')
check('synthetic_pose_available_but_zero_swing',replace(positive,swing_support=0),'ambiguous')
check('synthetic_carried_pose_cannot_supply_swing',replace(positive,pose_observed=False),'ambiguous')
check('synthetic_outgoing_direction_unresolved',replace(positive,motion=replace(positive.motion,outgoing_direction_support=0)),'ambiguous')
check('synthetic_no_resolved_speed_gain',replace(positive,motion=replace(positive.motion,speed_gain_support=0)),'ambiguous')
check('synthetic_interpolated_anchor',replace(positive,observation_status='reconstructed'),'insufficient')
check('synthetic_cut_context',replace(positive,context_valid=False),'rejected')
check('synthetic_fresh_geometric_overlap_without_pose',replace(positive,pose_observed=False,swing_support=0,racket_observed=True,racket_overlap_support=.5),'probable')
check('synthetic_stale_overlap_cannot_supply_cue',replace(positive,pose_observed=False,swing_support=0,racket_observed=False,racket_overlap_support=.5),'ambiguous')
# Preserve literal p/features and kept membership, without rebuilding the engine.
probes=json.loads((EVIDENCE/'component_score_probes.json').read_text())
compact=[]
for group in probes['cases']:
    for arm,data in group['arms'].items():
        for policy,p in data.items():
            for score in p['all_scores']:
                if score['frame'] in (809,904,11715):
                    compact.append({'range':group['range'],'arm':arm,'interpolation_policy':policy,'frame':score['frame'],'p':score['p'],'features':score['scores'],'kept':score['frame'] in [r['frame'] for r in p['kept']]})
results['unchanged_probe_numeric_extract']=compact
results['scope']='Actual old11715typed-evidence parity plus15synthetic evidence-policy controls, not new observed cues/current full-engine re-evaluation.'
write('contract_readout.json',results)
source_names=['sports/badminton/src/bai_badminton/events/contact.py','sports/badminton/src/bai_badminton/events/contact_evidence.py','sports/badminton/src/bai_badminton/events/exchange_evidence.py','sports/badminton/src/bai_badminton/engine.py','sports/badminton/src/bai_badminton/components.py','sports/badminton/tests/test_contact_motion_reliability.py','sports/badminton/tests/test_contact_physical_evidence.py']
inputs_hash={str((NATIVE/p).resolve()):sha(NATIVE/p) for p in source_names}
inputs_hash.update({str((EVIDENCE/n).resolve()):sha(EVIDENCE/n) for n in ['component_score_probes.json','actual_event_cases.json','probe_input_receipt.json']})
write('source_binding.json',{'native_root':str(NATIVE),'producer_commit':'2418ab8cbe4cca74dd16b722b9727ffdc950294a','loaded_evidence_module':ce.__file__,'loaded_exchange_module':ex.__file__,'input_sha256':inputs_hash,'new_models':False,'new_engine_replay':False})
print('actual11715evidence parity exact;15synthetic controls passed; native imports verified')
