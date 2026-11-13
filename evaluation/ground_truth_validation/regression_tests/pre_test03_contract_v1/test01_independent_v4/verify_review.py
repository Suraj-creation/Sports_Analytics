"""Seal independently derived completed review without changing its inputs."""
from pathlib import Path
from hashlib import file_digest
import json
import re

OUT=Path(__file__).resolve().parent
CONFIG=json.loads((OUT/'review_config.json').read_text())
ART=Path(CONFIG['artifact_root']);VISUAL=OUT.parent/'visual_test01_v4_review'


def sha(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()


def main():
    summary=json.loads((OUT/'summary.json').read_text());final=json.loads((OUT/'final_summary.json').read_text())
    inputs=dict(summary['input_sha256'])
    for name,key in [('native_guard_receipt.json','input_paths_sha256'),('additional_reproducibility_review.json','input_sha256')]:
        record=json.loads((OUT/name).read_text());inputs.update(record[key])
    protected=json.loads((OUT/'protected_inputs_review.json').read_text());inputs.update(protected['protected_paths_sha256'])
    for path,h in inputs.items():assert sha(path)==h,path
    visual=json.loads((VISUAL/'completion.json').read_text());assert visual['status']=='completed' and visual['candidate_commit']==CONFIG['expected_commit']
    assert visual['no_additional_gross_visual_blocker_found'] is True and visual['pipeline_acceptance_claimed'] is False
    for rel,h in visual['artifact_sha256'].items():assert sha(VISUAL/rel)==h
    plans=json.loads((OUT/'source_frame_plan.json').read_text());batches=[]
    for p in sorted((OUT/'source_frame_plans').glob('batch_*.json')):
        row=json.loads(p.read_text());assert len(row['frames'])<=128;batches.extend(row['frames'])
    assert batches==plans['frames'] and len(batches)==88
    assert final['all_182_coverage_audit']['bbox_exact']==182 and final['current_gross_count_loss_frames']==0
    assert final['all_raw_shuttle_xy_support_identical'] is True and final['unsupported_physical_metric_families_null']==10
    assert final['unexplained_format_context_transitions']==0 and final['unit_tests_passed']==3478
    text=(OUT/'REPORT.md').read_text();links=[]
    for label,target in re.findall(r'\[([^\]]+)\]\(([^)]+)\)',text):
        path=Path(target.split('#')[0]);path=path if path.is_absolute() else OUT/path
        assert path.exists(),(label,str(path));links.append(str(path))
    artifacts={str(p.relative_to(OUT)):sha(p) for p in OUT.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='verification_receipt.json'}
    result={'status':'sealed_independent_Test1_v4_metric_source_visual_review_root_acceptance_pending','candidate_commit':CONFIG['expected_commit'],'native_root':CONFIG['native_root'],'completed_run_artifacts_verified':summary['completed_artifacts_verified'],'worker_plan_source_files_verified':summary['source_plan_files_verified'],'all_consumed_input_hashes_unchanged':True,'unique_bound_input_paths_verified':len(inputs),'protected_original_Part2_files':62,'unit_tests_passed':3478,'visual_frames_independently_reviewed':88,'visual_completion_sha256':sha(VISUAL/'completion.json'),'visual_report_sha256':sha(VISUAL/'REPORT.md'),'visual_retained_artifacts_verified':len(visual['artifact_sha256']),'markdown_links_verified':len(links),'physical_accuracy_claimed':False,'pipeline_acceptance_claimed':False,'new_neural_inference_performed':False,'historical_reports_or_evaluator_changes':False,'artifact_sha256':artifacts}
    with (OUT/'verification_receipt.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='artifact_sha256'},indent=2))

if __name__=='__main__':main()
