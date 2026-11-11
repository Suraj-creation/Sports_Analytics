"""Complete independent Test1 exports after fresh baseline; never advance to another video."""
from pathlib import Path
import sys,json,time,subprocess,hashlib
R=Path(__file__).resolve().parents[3];W=R/'evaluation/ground_truth_validation';A=R.parent/'ground-truth-validation-artifacts-20261110/test_01/baseline_v1';PY=R/'.venv/bin/python'
print('Waiting for original Test1 baseline completion without changing or signalling it',flush=True)
while not (A/'baseline_completion.json').exists():
 p=W/'orchestration/status.json'
 if p.exists() and 'failed' in json.loads(p.read_text()).get('stage',''):print('Baseline failed; original evidence retained; diagnostics not started',flush=True);sys.exit(1)
 time.sleep(10)
for script,name in [('evaluate_test01_components.py','all_reference_components'),('export_completed_analytics.py','downstream_exports')]:
 p=W/'orchestration'/script
 if not p.exists():raise RuntimeError('Reviewed component helper missing: '+str(p))
 source=A/(script+'.executed');source.write_bytes(p.read_bytes())
 with (A/(name+'.log')).open('x') as stream:r=subprocess.run([str(PY),str(p),'--run',str(A/'run'),'--output',str(A/name)],cwd=R,stdout=stream,stderr=subprocess.STDOUT)
 if r.returncode:
  (W/'test_01/diagnostics/component_job_failure.json').write_text(json.dumps({'script':str(p),'exit':r.returncode,'log':str(A/(name+'.log')),'baseline_unmodified':True},indent=2)+'\n');sys.exit(r.returncode)
(W/'test_01/diagnostics/all_reference_evidence_ready.json').write_text(json.dumps({'fresh_baseline':str(A/'baseline_completion.json'),'component_evaluation':str(A/'all_reference_components'),'actual_downstream_outputs':str(A/'downstream_exports'),'next_required':'Read metrics and overlays; establish causal diagnosis; isolated justified fixes and before/after fresh regression. Test2 remains gated.','new_inference_in_diagnostic_helpers':False},indent=2)+'\n')
print('Test1 all-reference and downstream evidence ready; no automatic pipeline changes or Test2 advance',flush=True)
