"""Read-only frozen-commit/test handoff; no candidate imports or worker writes."""
from pathlib import Path
import ast,hashlib,json,subprocess

OUT=Path(__file__).resolve().parent
MAIN=OUT.parents[4]
NATIVE=MAIN.parent/'test03-scene-overlap-20261112'
ROOT=OUT.parent
COMP=MAIN/'evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_origins_implementation_review_v1'
COMMIT='5ae614826e6f909defb02445386962ac13b4641a'
INPUTS={}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):INPUTS[str(p.resolve())]=sha(p);return json.loads(p.read_text())
def save(n,x):
    with (OUT/n).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=NATIVE,text=True).strip()==COMMIT
assert subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=NATIVE,text=True)==''
tracked=set(subprocess.check_output(['git','ls-files'],cwd=NATIVE,text=True).splitlines())
research=read(ROOT/'unit_research_preliminary_v1/full_retry_v1/completion.json')
assert research['exit_code']==0 and research['counts']=={'tests':746,'failures':0,'errors':0,'skipped':10}
assert research['source_changed_during_run']==[]
assert all(rel in tracked and sha(NATIVE/rel)==h for rel,h in research['source_sha256_after'].items())
research_bound=len(research['source_sha256_after']);assert research_bound==712
owned=read(ROOT/'unit_research_preliminary_v1/owned_test_freeze.json')
assert all(sha(NATIVE/rel)==h for rel,h in owned['paths_sha256'].items())
app=read(ROOT/'final_app_scope_check_v1.json');manifest=read(ROOT/'unit_main_preliminary_v1/manifest.json');before=manifest['files_sha256']
filtered={p:h for p,h in before.items() if any(p.startswith(prefix) for prefix in app['app_and_test_scope_prefixes'])}
assert len(filtered)==379
app_changes=[p for p,h in filtered.items() if sha(NATIVE/p)!=h]
assert app_changes==[app['only_changed_app_test_file']] and sha(NATIVE/app_changes[0])==app['fixture_sha256']
fixture=read(ROOT/'fixture_metadata_update_v1/verification.json')
assert fixture['targeted_counts']=={'tests':46,'failures':0,'errors':0,'skipped':0}
impl=read(COMP/'completion.json');assert impl['focused_tests_passed']==174 and impl['source_controls']==6
assert all(sha(p)==h for p,h in impl['final_sources_and_tests_sha256'].items())
controls=read(COMP/'bounded_controls_verification.json');assert controls['source_and_tests_unchanged'] and controls['verified_control_inputs']==18
orch=read(ROOT/'orchestration_review_v1/guard_probe_receipt_v2.json');assert len(orch['helper_compatibility'])==15 and all(x['rejected'] for x in orch['fixture_mutation_controls']) and len(orch['fixture_mutation_controls'])==7
assert all(sha(NATIVE/rel)==v['native_sha256'] for rel,v in orch['helper_compatibility'].items())
# The only source-map byte drift is the driver's module description.
driver='evaluation/ground_truth_validation/orchestration/run_pre_test03_regression.py';old=ROOT/'orchestration_review_v1/reviewed_sources'/driver
new=NATIVE/driver
changes=[p for p,h in orch['source_sha256'].items() if sha(p)!=h]
assert changes==[str(new)]
a,b=ast.parse(old.read_text()),ast.parse(new.read_text())
assert isinstance(a.body[0],ast.Expr) and isinstance(a.body[0].value,ast.Constant) and isinstance(a.body[0].value.value,str)
assert isinstance(b.body[0],ast.Expr) and isinstance(b.body[0].value,ast.Constant) and isinstance(b.body[0].value.value,str)
a.body=a.body[1:];b.body=b.body[1:];assert ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
INPUTS[str(old.resolve())]=sha(old);INPUTS[str(new.resolve())]=sha(new)
codec=MAIN.parent/'ground-truth-validation-artifacts-20261112/pre_test03_v4/scene_origin_codec24_source_binding_v3.log';assert '19 passed' in codec.read_text();INPUTS[str(codec)]=sha(codec)
worktrees=subprocess.check_output(['git','worktree','list','--porcelain'],cwd=NATIVE,text=True)
ancestors={c:subprocess.run(['git','merge-base','--is-ancestor',c,COMMIT],cwd=NATIVE,check=False).returncode==0 for c in ['c7cf871','c585','a146953','2418ab8']}
# c585 is a unique prefix in this repository; require proven ancestry, not text similarity.
assert all(ancestors.values())
save('source_and_test_binding.json',{'status':'passed_frozen_candidate_handoff','commit':COMMIT,'candidate_tracked_diff_empty':True,'all712_research_snapshot_sources_committed_and_hash_exact':True,'all4_owned_research_tests_match_sealed_hashes':True,'app_scope379_files_verified':True,'only_app_fixture_change':app_changes,'all10_independent_focused_source_test_hashes_match':True,'all15_orchestration_helpers_hash_exact':True,'only_postreview_driver_change':'module docstring clarifies numerical evaluator invariance and codec24native structural audit; all non-docstring AST exact','old_aux_head_ancestry':ancestors,'worktree_porcelain_readonly':worktrees,'input_sha256':INPUTS,'no_candidate_write_or_import':True,'no_worker_output_read_as_completed':True,'fresh_neural_acceptance':False})
print('gate712sources/379scope/15helpers exact; descriptive driver only; no NN acceptance claim')
