"""Current-source Test1 baseline and retained diagnostic evidence; no fixes or Test2 execution."""
import sys,json,hashlib,subprocess,time,os,traceback
from pathlib import Path
R=Path(__file__).resolve().parents[3];W=R/'evaluation/ground_truth_validation';A=R.parent/'ground-truth-validation-artifacts-20261110/test_01/baseline_v1';PY=R/'.venv/bin/python';V=R/'data/benchmarking/test1/Test1_Full_rev.mp4'
os.chdir(R);sys.path.insert(0,str(R))
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p,v):
 p.parent.mkdir(parents=True,exist_ok=True)
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def state(s,extra=None):
 p=W/'orchestration/status.json';q=p.with_suffix('.tmp');q.write_text(json.dumps({'active_test':1,'stage':s,'updated_epoch':time.time(),'next_test_gate':'Test1 diagnosis, measured fixes if warranted, and before/after regression review required; no automatic Test2 advance','details':extra},indent=2)+'\n');q.replace(p)
def call(args,name):
 print('RUN',*[str(x) for x in args],flush=True)
 with (A/(name+'.log')).open('x') as f:r=subprocess.run([str(PY),*[str(x) for x in args]],stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(f'{name} failed with exit{r.returncode}; original log retained')
def main():
 ready=W/'dataset_inventory/phase1_review.json'
 if not ready.exists():raise RuntimeError('Annotation-understanding gate has not been completed')
 phase=json.loads(ready.read_text());assert phase['test1_baseline_authorized_by_completed_inventory_review'] is True
 assert sha(V)=='877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6'
 A.mkdir(parents=True,exist_ok=False);link=W/'test_01/baseline_v1';link.symlink_to(A,target_is_directory=True)
 original={p['path']:p['sha256'] for p in json.loads((W/'dataset_inventory/dataset_manifest.json').read_text())['files']}
 dump(A/'annotation_hashes_before.json',original)
 dump(A/'input_pairing.json',{'source':str(V),'source_sha256':sha(V),'drive_file_id':'1vR71QTkUYEGWy4PjXa5vfMdJEXt_OwLn','source_folder':'https://drive.google.com/drive/folders/1_2QWSYd_X_BojdRwbu-AMKdx74cIQvGp?usp=sharing','original_retained_local':True,'annotation_directory':str(R/'Part2/dataset/Test1_Full'),'annotation_gate_sha256':sha(ready),'raw_inputs_untouched':True})
 from research.validate_real_video_runtime import package_versions
 dump(A/'runtime_environment.json',package_versions())
 state('preparing current-source Test1 baseline')
 call([R/'research/production_external_stress.py','prepare-upload','--case','test1','--video',V,'--profile-source',R/'config/profiles/experimental-pipeline-repair-v1.yaml','--output',A/'protocol'],'prepare')
 plan=json.loads((A/'protocol/plan.json').read_text());n=plan['cases']['test1']['frames']
 state('fresh current-source Test1 inference on GPU1',{'frames':n,'plan':str(A/'protocol/plan.json')})
 call([R/'research/production_external_stress.py','run','--case','test1','--plan',A/'protocol/plan.json','--output',A/'run','--gpu-index','1'],'fresh_inference')
 state('Test1 full-timestamp and component analysis')
 call([R/'research/normal_timestamp_audit.py','--run',A/'run','--output',A/'timestamps'],'timestamps')
 call([R/'research/pipeline_repair_run_analysis.py','--run',A/'run','--output',A/'analysis'],'component_analysis')
 state('Test1 legacy rally reference evaluation; additional reference metrics pending explicit mapping')
 call([R/'research/pipeline_repair_evaluation.py','--run',A/'run','--session','UPLOADTEST1','--reference',R/'Part2/dataset/Test1_Full/Test1_Full_rally.csv','--output',A/'rally_reference_evaluation'],'rally_evaluation')
 state('Test1 diagnostic semantic trace from fresh run observations; not new neural inference')
 call([R/'research/production_external_semantic_replay.py','--run',A/'run','--session','UPLOADTEST1','--output',A/'diagnostic_replay','--trace-ranges',json.dumps([[0,n]]),'--focus',''],'diagnostic_replay')
 state('building source-bound Test1 visual failure evidence')
 call([R/'research/test2_failure_package.py','--run',A/'run','--session','UPLOADTEST1','--replay',A/'diagnostic_replay','--source',V,'--source-pts',A/'timestamps/source_frame_pts.csv','--evaluation',A/'rally_reference_evaluation','--output',A/'visual_failure_package'],'failure_evidence')
 for p,h in original.items():assert sha(p)==h,('Original data changed',p)
 metrics=json.loads((A/'rally_reference_evaluation/evaluation_results.json').read_text())
 dump(A/'baseline_completion.json',{'status':'fresh_baseline_and_diagnostic_artifacts_complete','annotation_inputs_unchanged':True,'model_changes':False,'pipeline_changes':False,'rally_reference_detection':metrics['detection'],'next_required':'All-reference component comparisons, visual/source review, ranked diagnosis; only then isolated fixes and fresh regressions; do not start Test2 yet'})
 state('Test1 fresh baseline and source-bound visual package ready for deep diagnosis',{'artifact_root':str(A),'rally_reference_detection':metrics['detection']})
 print('TEST1 BASELINE EVIDENCE READY; diagnosis/fix/regression gate remains closed for Test2',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:traceback.print_exc();state('Test1 baseline/evidence job failed; preserve inputs and logs',{'error':str(e)});sys.exit(1)
