"""Fresh post-fix Test1 inference and all-reference before/after comparison."""
from pathlib import Path
import sys,json,hashlib,subprocess,time,traceback,os
R=Path(__file__).resolve().parents[3];W=R/'evaluation/ground_truth_validation';A=R.parent/'ground-truth-validation-artifacts-20261110/test_01/improved_v1';BASE=A.parent/'baseline_v1';PY=R/'.venv/bin/python';V=R/'data/benchmarking/test1/Test1_Full_rev.mp4';os.chdir(R)
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def read(p):return json.loads(Path(p).read_text())
def dump(p,v):
 p.parent.mkdir(exist_ok=True,parents=True)
 with p.open('x') as f:json.dump(v,f,indent=2);f.write('\n')
def state(stage,more=None):
 p=W/'orchestration/status.json';q=p.with_suffix('.tmp');q.write_text(json.dumps({'active_test':1,'stage':stage,'updated_epoch':time.time(),'details':more,'next_test_gate':'Test1 before/after regression and remaining limitation review; no automatic Test2'},indent=2)+'\n');q.replace(p)
def run(args,label):
 print('RUN',*[str(x) for x in args],flush=True)
 with (A/(label+'.log')).open('x') as f:r=subprocess.run([str(PY),*[str(x) for x in args]],stdout=f,stderr=subprocess.STDOUT)
 if r.returncode:raise RuntimeError(f'{label} failed exit{r.returncode}; evidence retained')
def main():
 integration=W/'orchestration/test01_integrated_fixes.json';i=read(integration);assert i['broad_regressions_passed']
 assert sha(V)=='877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6'
 for path,v in i['production_files'].items():assert sha(path)==v['after_sha256']
 A.mkdir(parents=True,exist_ok=False);(W/'test_01/improved_v1').symlink_to(A,target_is_directory=True)
 dump(A/'code_change_receipt.json',i)
 original={v['path']:v['sha256'] for v in read(W/'dataset_inventory/dataset_manifest.json')['files']}
 state('preparing fresh Test1 post-fix regression')
 run([R/'research/production_external_stress.py','prepare-upload','--case','test1','--video',V,'--profile-source',R/'config/profiles/experimental-pipeline-repair-v1.yaml','--output',A/'protocol'],'prepare')
 oldplan=read(BASE/'protocol/plan.json');plan=read(A/'protocol/plan.json');assert oldplan['profile_source_sha256']==plan['profile_source_sha256'];n=plan['cases']['test1']['frames'];assert n==17268
 state('fresh Test1 post-fix inference on GPU1',{'frames':n,'fixes':['recovery cut-frontier','independent score transition votes','stabilized ground-foot projection'],'source_plan':str(A/'protocol/plan.json')})
 run([R/'research/production_external_stress.py','run','--case','test1','--plan',A/'protocol/plan.json','--output',A/'run','--gpu-index','1'],'inference')
 state('verifying complete post-fix Test1 timestamps and components')
 run([R.parent/'pipeline-repair-runs-20261105/normal_timestamp_audit.py','--run',A/'run','--output',A/'timestamps'],'timestamps')
 run([R/'research/pipeline_repair_run_analysis.py','--run',A/'run','--output',A/'analysis'],'analysis')
 run([R/'research/pipeline_repair_evaluation.py','--run',A/'run','--session','UPLOADTEST1','--reference',R/'Part2/dataset/Test1_Full/Test1_Full_rally.csv','--output',A/'rally_reference_evaluation'],'rally_evaluation')
 run([W/'orchestration/evaluate_test01_components.py','--run',A/'run','--output',A/'all_reference_components'],'all_reference_components')
 binding=W/'test_01/diagnostics/geometry_root_cause/diagnostic_coordinate_binding.json'
 if binding.exists():run([W/'orchestration/evaluate_test01_components.py','--run',A/'run','--output',A/'bound_reference_diagnostics','--coordinate-binding',binding],'bound_reference_diagnostics')
 run([W/'orchestration/export_completed_analytics.py','--run',A/'run','--output',A/'downstream_exports'],'downstream_exports')
 run([R/'research/production_external_semantic_replay.py','--run',A/'run','--session','UPLOADTEST1','--output',A/'diagnostic_replay','--trace-ranges',json.dumps([[0,n]]),'--focus',''],'diagnostic_replay')
 run([R/'research/test2_failure_package.py','--run',A/'run','--session','UPLOADTEST1','--replay',A/'diagnostic_replay','--source',V,'--source-pts',A/'timestamps/source_frame_pts.csv','--evaluation',A/'rally_reference_evaluation','--output',A/'visual_failure_package'],'visual_evidence')
 for p,h in original.items():assert sha(p)==h
 old=read(BASE/'all_reference_components/component_reference_metrics.json');new=read(A/'all_reference_components/component_reference_metrics.json');comparisons={}
 for name,v in old['interval_reference_comparisons'].items():
  nv=new['interval_reference_comparisons'][name];o=v.get('metrics',{});a=nv.get('metrics',{})
  comparisons[name]={'baseline_metrics':o,'postfix_metrics':a,'metrics_equal':o==a,'reference_role':v['role']}
 primary_old=read(BASE/'rally_reference_evaluation/evaluation_results.json');primary_new=read(A/'rally_reference_evaluation/evaluation_results.json')
 comparison={'all_reference_comparisons':comparisons,'primary_baseline':primary_old,'primary_postfix':primary_new,'primary_metrics_equal':primary_old==primary_new,'prediction_csv_bytes_equal':(BASE/'run/predicted_rallies.csv').read_bytes()==(A/'run/predicted_rallies.csv').read_bytes(),'code_improvement_scope':'Three reproducible correctness/safety contracts fixed with RED/GREEN tests. No inferred sporting accuracy gain from unit tests; actual video deltas are recorded here.','original_annotations_unchanged':True,'test2_started':False}
 dump(A/'before_after_comparison.json',comparison)
 run([W/'orchestration/build_test01_matrix.py'],'evaluation_matrix')
 report=['# Test1 code fixes and fresh before/after regression','','Three code defects were fixed in the actual current pipeline after preservation and isolated regression tests: reopened-rally cut frontier, duplicated source-score-transition mapping votes, and transformed detector-foot projection. No threshold/model/profile or original annotation changes.','','## Actual video evidence','',f"Primary baseline detection: `{json.dumps(primary_old['detection'])}`",'',f"Post-fix detection: `{json.dumps(primary_new['detection'])}`",'',f"Prediction CSV byte-identical: **{comparison['prediction_csv_bytes_equal']}**. Primary metrics equal: **{comparison['primary_metrics_equal']}**.",'','These baseline Test1 observations did not trigger the three reproduced edge contracts. Identical video metrics demonstrate a regression-preservation result, not a new physical accuracy gain. Do not report all semantic/annotation limitations fixed: independent box/keypoint/contact/identity labels, conflicting/partial scores and model-generated reference provenance remain explicit.','',f"Full comparison: [before_after_comparison.json]({A/'before_after_comparison.json'}).",'',f"Matrix: [all-data evaluation matrix]({W/'reports/test_01_evaluation_matrix.md'}).",'','Test2 has not started. Remaining observed failure hypotheses require adjudicated source evidence rather than fitting the generated timing labels.','']
 (W/'reports/test_01_fixes_and_regression.md').write_text('\n'.join(report))
 inventory={str(p.relative_to(A)):sha(p) for p in A.rglob('*') if p.is_file()}
 dump(A/'regression_completion.json',{'status':'fresh_postfix_Test1_all_reference_evaluation_complete','files_sha256':inventory,'annotations_unchanged':True,'actual_primary_metric_change':not comparison['primary_metrics_equal'],'source_code_fixed':True,'test2_started':False})
 state('Test1 code fixes and fresh all-reference regression complete; diagnosis review remains before Test2',{'report':str(W/'reports/test_01_fixes_and_regression.md'),'primary_metrics_equal':comparison['primary_metrics_equal'],'source_code_fixed':True})
 print('TEST1 POSTFIX REGRESSION COMPLETE',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:traceback.print_exc();state('Test1 post-fix regression failed; no Test2 advance',{'error':str(e)});sys.exit(1)
