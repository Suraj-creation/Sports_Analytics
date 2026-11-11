"""Fresh Test2 baseline; preserves Test1 and historical benchmark evidence.

Run with ../gpu-env.sh and the existing venv. Never changes production code.
"""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
WORK = ROOT / 'evaluation/ground_truth_validation'
TEST = WORK / 'test_02'
ART = ROOT.parent / 'ground-truth-validation-artifacts-20261110/test_02/baseline_v1'
VIDEO = TEST / 'inputs/Test2_Full_Rev.mp4'
PYTHON = ROOT / '.venv/bin/python'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def state(stage, **details):
    path = TEST / 'orchestration/status.json'
    tmp = path.with_suffix('.tmp')
    tmp.write_text(json.dumps(dict(test=2, stage=stage, epoch=time.time(), details=details), indent=2)+'\n')
    tmp.replace(path)
    print(stage, flush=True)


def call(args, name):
    command = [str(PYTHON), *map(str, args)]
    dump(ART / (name + '.command.json'), dict(argv=command, started_epoch=time.time()))
    with (ART / (name + '.log')).open('x') as stream:
        result = subprocess.run(command, cwd=ROOT, stdout=stream, stderr=subprocess.STDOUT)
    if result.returncode:
        raise RuntimeError(f'{name} exited {result.returncode}; original failure and outputs retained')


def main():
    os.chdir(ROOT)
    assert sha(VIDEO) == '4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a'
    assert (TEST / 'annotations/annotation_mapping.md').exists(), 'Test2 annotation review required'
    old = ROOT.parent / 'ground-truth-validation-artifacts-20261110/test_01/improved_v1'
    assert read(old / 'regression_completion.json')['status'] == 'fresh_postfix_Test1_all_reference_evaluation_complete'
    fixes = read(WORK / 'orchestration/test01_integrated_fixes.json')
    for path, value in fixes['production_files'].items():
        assert sha(path) == value['after_sha256'], f'Test1 repair source changed: {path}'
    ART.mkdir(parents=True, exist_ok=False)
    (TEST / 'baseline_v1').symlink_to(ART, target_is_directory=True)
    annotations = {str(p): sha(p) for p in sorted((ROOT / 'Part2/dataset/Test2_Full').iterdir()) if p.is_file()}
    dump(ART / 'annotation_hashes_before.json', annotations)
    dump(ART / 'input_pairing.json', read(TEST / 'inputs/download_verification.json'))
    dump(ART / 'test1_carry_forward.json', dict(
        integrated_fixes=fixes, test1_completion_sha256=sha(old / 'regression_completion.json'),
        review_report=str(TEST / 'diagnostics/prior_findings_and_plan.md'),
        open_issues='Identity/outcome conventions and independent component labels remain unresolved; no fabricated fixes.',
        historical_benchmarks_immutable=True))
    from research.validate_real_video_runtime import package_versions
    dump(ART / 'environment.json', dict(packages=package_versions(),
         git_commit=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),
         git_status=subprocess.check_output(['git','status','--short'],text=True),
         gpu=subprocess.check_output(['nvidia-smi','--query-gpu=index,name,uuid,driver_version','--format=csv'],text=True)))
    state('preparing verified fresh Test2 upload')
    call([ROOT/'research/production_external_stress.py','prepare-upload','--case','test2','--video',VIDEO,
          '--profile-source',ROOT/'config/profiles/experimental-pipeline-repair-v1.yaml','--output',ART/'protocol'], 'prepare')
    plan = read(ART/'protocol/plan.json')
    assert plan['cases']['test2']['frames'] == 29296
    profile1 = read(old/'protocol/plan.json')
    assert plan['profile_source_sha256'] == profile1['profile_source_sha256']
    state('fresh Test2 full inference on physical GPU 1', frames=29296, plan=str(ART/'protocol/plan.json'))
    call([ROOT/'research/production_external_stress.py','run','--case','test2','--plan',ART/'protocol/plan.json',
          '--output',ART/'run','--gpu-index','1'], 'inference')
    state('verifying full Test2 timestamps and component coverage')
    call([ROOT/'research/normal_timestamp_audit.py','--run',ART/'run','--output',ART/'timestamps'], 'timestamps')
    call([ROOT/'research/pipeline_repair_run_analysis.py','--run',ART/'run','--output',ART/'analysis'], 'analysis')
    state('evaluating current Test2 against each applicable annotation family')
    call([WORK/'orchestration/evaluate_test02_components.py','--run',ART/'run','--output',ART/'all_reference_components'], 'components')
    call([ROOT/'research/pipeline_repair_evaluation.py','--run',ART/'run','--session','UPLOADTEST2',
          '--reference',ROOT/'Part2/dataset/Test2_Full/Test2_Full_rally.csv','--output',ART/'rally_reference_evaluation'], 'rally_evaluation')
    call([WORK/'orchestration/export_completed_analytics.py','--run',ART/'run','--output',ART/'downstream_exports'], 'downstream_exports')
    state('creating source-bound Test2 semantic traces and visual failures')
    call([ROOT/'research/production_external_semantic_replay.py','--run',ART/'run','--session','UPLOADTEST2',
          '--output',ART/'diagnostic_replay','--trace-ranges','[[0,29296]]','--focus',''], 'diagnostic_replay')
    call([ROOT/'research/test2_failure_package.py','--run',ART/'run','--session','UPLOADTEST2',
          '--replay',ART/'diagnostic_replay','--source',VIDEO,'--source-pts',ART/'timestamps/source_frame_pts.csv',
          '--evaluation',ART/'rally_reference_evaluation','--output',ART/'visual_failure_package'], 'visual_failure_package')
    assert all(sha(p)==expected for p,expected in annotations.items()), 'Original annotation changed'
    dump(ART/'baseline_completion.json',dict(status='completed_fresh_Test2_baseline_and_diagnostics',
         frames=29296, annotations_unchanged=True, production_changes_during_baseline=False,
         next='Review synchronized evidence; verify any proposed defect with regression before production changes. Test3 not started.'))
    state('Test2 baseline complete; root-cause review and justified fixes pending', artifacts=str(ART))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        traceback.print_exc()
        state('Test2 baseline failed; preserve source and logs; no automatic retry or Test3', error=str(error))
        sys.exit(1)
