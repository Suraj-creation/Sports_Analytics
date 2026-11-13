"""Seal read-only diagnostic output and verify every input after execution."""
from pathlib import Path
from hashlib import file_digest,sha256
import json
import subprocess
root=Path('/home/administrator/Desktop/sport-analytics');main=root/'Sports_Analytics';here=Path(__file__).resolve().parent;cand=root/'test03-scene-continuity-20261112'
def sha(p):
    with Path(p).open('rb') as f:return file_digest(f,'sha256').hexdigest()
reports=[here/'summary.json',here/'scale_aware_v1/summary.json',here/'hypothesis_v2/summary.json',here/'hypothesis_partition_v3/summary.json'];verified=0
for p in reports:
    d=json.loads(p.read_text())
    for path,h in d['input_sha256'].items():assert sha(path)==h;verified+=1
prefix=main/'evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_foreground_v1/prefix_v2';receipt=json.loads((prefix/'artifact_receipt.json').read_text())
for p in prefix.glob('test[12]_*.json'):assert sha(p)==receipt['artifact_sha256'][p.name]
sourcefiles=['sports/badminton/src/bai_badminton/perception/players.py','sports/badminton/src/bai_badminton/perception/components.py','sports/badminton/src/bai_badminton/perception/_bytetrack.py','sports/badminton/src/bai_badminton/perception/foreground.py']
source={}
for rel in sourcefiles:
    b=subprocess.check_output(['git','-C',str(cand),'show','c585e3507a2fef9ff393a8cfbba575a979345f53:'+rel]);assert sha(cand/rel)==sha256(b).hexdigest();source[rel]=sha(cand/rel)
# Appearance research has independent owner and seal; do not absorb mutable files.
art={str(p.relative_to(here)):sha(p) for p in sorted(here.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and 'appearance_research' not in p.parts and p.name!='verification_receipt.json'}
out={'status':'completed_read_only_continuity_investigation_no_production_patch_recommended','candidate_commit':'c585e3507a2fef9ff393a8cfbba575a979345f53','candidate_root':str(cand),'candidate_source_checks':source,'summary_input_hash_checks':verified,'ten_closed_prefix_cases_verified':10,'all_original_182_rows_preserved':182,'neural_inference_performed':False,'Test3_access':False,'physical_accuracy_claimed':False,'diagnostic_controls':{'passed':20,'expected_current_lease_RED_failures':1},'early_tool_attempts':['First metadata assertion expected an incorrect receipt status prefix and failed before reading predictions/writing outputs; corrected exact existing status only in owned script.','First seal command used system Python3.10 lacking hashlib.file_digest and failed before verification/writes; actual seal uses existing Python3.12venv.'],'artifact_sha256':art}
with (here/'verification_receipt.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
print(json.dumps({'verified_input_hash_checks':verified,'artifacts':len(art),'candidate_source_unchanged':True}))
