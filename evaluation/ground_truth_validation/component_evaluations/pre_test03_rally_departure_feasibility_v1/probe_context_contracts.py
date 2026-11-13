"""Synthetic source-episode contract feasibility; no activity classifier or NN."""
import hashlib,json
from pathlib import Path
from bai_badminton.events import exchange_evidence as x
ROOT=Path('/home/administrator/Desktop/sport-analytics/test03-scene-evidence-contract-20261112')
assert Path(x.__file__).resolve()==ROOT/'sports/badminton/src/bai_badminton/events/exchange_evidence.py'
HERE=Path(__file__).resolve().parent

def ctx(frame,epoch=21,tracks=(0,1),births=('n-birth','f-birth'),ys=(-3,2),extra=()):
 return x.ContactParticipantContext(3,epoch,1,tuple(x.ContactParticipantObservation(frame,p,b,t,y) for p,b,t,y in zip(('near','far'),births,tracks,ys))+tuple(extra))
a,b=ctx(11714),ctx(11740)
controls=[]
def test(name,left,right,first,second,expected):
 result=x.simultaneous_opponents(left,first,right,second)
 assert (result is not None)==expected,name
 controls.append({'name':name,'pair_proof_available':result is not None,'proof':result,'synthetic':True,'physical_contact_or_departure_proven':False})
test('singles_observed_opposite_episodes',a,b,'near','far',True)
test('unknown_origin_context',None,b,'near','far',False)
test('unknown_origin_target',a,b,None,'far',False)
test('cross_content_epoch',a,ctx(11740,epoch=22),'near','far',False)
test('same_raw_track_collision',ctx(11714,tracks=(0,0)),ctx(11740,tracks=(0,0)),'near','far',False)
test('same_birth_alias',ctx(11714,births=('shared','shared')),ctx(11740,births=('shared','shared')),'near','far',False)
test('same_court_half',ctx(11714,ys=(-3,-2)),ctx(11740,ys=(-3,-2)),'near','far',False)
extra=lambda f:(x.ContactParticipantObservation(f,'near2','n2-birth',2,-2),x.ContactParticipantObservation(f,'far2','f2-birth',3,3))
test('doubles_two_known_targets_with_all_four_observed',ctx(11714,extra=extra(11714)),ctx(11740,extra=extra(11740)),'near','far',True)
test('doubles_partial_population_is_not_checked_by_pair_helper',a,b,'near','far',True)
try:x.ContactParticipantContext(3,21,1,a.observations+a.observations)
except ValueError:controls.append({'name':'duplicate_same_frame_participant_rejected','rejected':True,'synthetic':True})
else:raise AssertionError('Duplicate synthetic observations accepted')
p=Path(x.__file__)
with (HERE/'context_controls.json').open('x') as f:json.dump({'status':'original_pure_pair_contracts_verified','module':str(p),'module_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'controls':controls,'scope':'Pair helper checks simultaneous opposite episode observations only; departure confidence, all-format ownership, source timestamp dedup and physical impact remain separate unknowns.'},f,indent=2);f.write('\n')
print(json.dumps({'synthetic_controls':len(controls),'all_expected_contract_results':True,'NN':False}))
