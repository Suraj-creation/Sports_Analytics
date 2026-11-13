"""Independent read-only candidate guard review; mutations exist only in fixtures."""
from __future__ import annotations
import ast
import hashlib
import importlib.util
import json
import os
import pathlib
import shutil
import tempfile

BASE=pathlib.Path('/home/administrator/Desktop/sport-analytics')
PRIMARY=BASE/'Sports_Analytics'
CANDIDATE=BASE/'pipeline-tracking-repair-20261112'
HERE=pathlib.Path(__file__).resolve().parent
os.environ['SPORTS_ANALYTICS_PRIMARY_WORKSPACE']=str(PRIMARY)
path=CANDIDATE/'evaluation/ground_truth_validation/orchestration/run_pre_test03_regression.py'
spec=importlib.util.spec_from_file_location('readonly_candidate_runner',path)
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
source_paths=[path,*[CANDIDATE/p for p in (*runner.COMMON,'research/pipeline_repair_completion.py')]]
before={str(p):digest(p) for p in source_paths}
receipt=runner.require_helper_compatibility(CANDIDATE)
assert runner.MAIN==PRIMARY
assert str(CANDIDATE/'sports/badminton/src') in runner.environment(CANDIDATE)['PYTHONPATH']
assert str(PRIMARY/'sports/badminton/src') not in runner.environment(CANDIDATE)['PYTHONPATH']
controls=[]
with tempfile.TemporaryDirectory(prefix='helper_fixture_',dir=HERE) as tmp:
 fixture=pathlib.Path(tmp)
 for name in (*runner.COMMON,'research/pipeline_repair_completion.py'):
  dest=fixture/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(CANDIDATE/name,dest)
 runner.require_helper_compatibility(fixture)
 cases=[
 ('matching_iou_default','scripts/benchmarking/evaluate_rallies.py','def match_rallies(gt, pred, minimum_iou=0.5):','def match_rallies(gt, pred, minimum_iou=0.4):'),
 ('coordinate_tolerance','evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py',">1e-6:raise ValueError('inconsistent frame/time/duration at canonical FPS')",">1e-5:raise ValueError('inconsistent frame/time/duration at canonical FPS')"),
 ('partial_reference_fp_policy','evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py',"for key in ('false_positives','precision','f1'):m['detection'][key]=None","for key in ('false_positives','precision','f1'):m['detection'][key]=0"),
 ('early_dispatch_codec23','evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py','if any(chunk["v"] >= 24 for chunk in chunks)','if any(chunk["v"] >= 23 for chunk in chunks)'),
 ('future_codec26_catalogue','research/production_external_stress.py','"accepted_codec_versions": [20, 21, 22, 23, 24, 25]','"accepted_codec_versions": [20, 21, 22, 23, 24, 25, 26]'),
 ('future_codec26_completion','research/pipeline_repair_completion.py','accepted_versions=(21, 22, 23, 24, 25)','accepted_versions=(21, 22, 23, 24, 25, 26)'),
 ('weaken_catalogue_fps','research/production_external_stress.py','abs_tol=1e-9','abs_tol=1e-3'),
 ('historical_recovery_must_stay21','research/pipeline_repair_completion.py','accepted_versions=(21,)','accepted_versions=(21,25)'),
 ('historical_population_cannot_be_ignored','research/production_external_stress.py','and all(row["codec_version"] in historical_versions for row in observed["files"])','and True'),
 ]
 for label,name,old,new in cases:
  target=fixture/name;source=target.read_text();assert old in source,(label,old)
  target.write_text(source.replace(old,new,1))
  try:runner.require_helper_compatibility(fixture)
  except ValueError as e:controls.append({'case':label,'rejected':True,'reason':str(e)})
  else:raise AssertionError('Guard accepted '+label)
  finally:target.write_text(source)
 assert len(controls)==9
 assert runner.require_helper_compatibility(fixture)
assert before=={str(p):digest(p) for p in source_paths},'Candidate changed during this probe'
result={'status':'readonly_helper_compatibility_review_passed','candidate_root':str(CANDIDATE),'primary_workspace':str(runner.MAIN),'native_ROOT_reassigned':False,'inference_started':False,'source_sha256':before,'helper_compatibility':receipt,'fixture_mutation_controls':controls,'actual_candidate_helpers_accepted':True,'matching_and_numeric_AST_unchanged_except_declared_structural_dispatch':True}
with (HERE/'guard_probe_receipt.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({'status':result['status'],'actual_helpers':len(receipt),'rejected_mutations':len(controls),'no_inference':True}))
