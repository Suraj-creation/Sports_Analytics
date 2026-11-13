"""Bind native synthetic codec tests to exact unchanged executed source bytes."""
from pathlib import Path
from hashlib import file_digest
import json
import os
import subprocess

ROOT=Path('/home/administrator/Desktop/sport-analytics')
CANDIDATE=ROOT/'test03-scene-acquisition-20261112'
OUT=Path(__file__).resolve().parent
RELATIVE=['sports/badminton/tests/test_scene_acquisition_codec_v23.py','sports/badminton/tests/test_scene_acquisition_v4.py','sports/badminton/src/bai_badminton/plugin.py','sports/badminton/src/bai_badminton/perception/players.py','sports/badminton/src/bai_badminton/perception/pipeline.py','sports/badminton/src/bai_badminton/perception/content.py','sports/badminton/src/bai_badminton/perception/scene_change.py']

def sha(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()

before={r:sha(CANDIDATE/r) for r in RELATIVE}
with (OUT/'executed_sources_before.json').open('x') as f:json.dump(before,f,indent=2);f.write('\n')
env=dict(os.environ);env['PYTHONPATH']=str(CANDIDATE/'sports/badminton/src')+':'+str(CANDIDATE/'engine/src')
command=[str(CANDIDATE/'.venv/bin/python'),'-m','pytest','-q',*RELATIVE[:2], 'sports/badminton/tests/test_scene_foreground_codec_v22.py','sports/badminton/tests/test_scene_decision_cache.py']
with (OUT/'guarded_tests.log').open('x') as log:
    result=subprocess.run(command,cwd=CANDIDATE,env=env,stdout=log,stderr=subprocess.STDOUT,check=False)
after={r:sha(CANDIDATE/r) for r in RELATIVE}
receipt={'status':'passed_exact_native_source_guarded_synthetic_codec_tests' if result.returncode==0 and before==after else 'failed_tests_or_source_changed','native_root':str(CANDIDATE),'command':command,'environment_PYTHONPATH':env['PYTHONPATH'],'executed_sources_sha256':before,'sources_unchanged_during_tests':before==after,'exit_code':result.returncode,'test_log_sha256':sha(OUT/'guarded_tests.log'),'helper_review_sha256':sha(OUT/'helper_review.json'),'neural_inference':False,'media_decoding':False,'synthetic_Session_media_fps':25,'script_sha256':sha(Path(__file__))}
with (OUT/'execution_receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
assert receipt['status'].startswith('passed'),receipt
print(receipt['status'])
