"""Root acceptance receipt: integrity and existing results, no re-evaluation."""
import datetime
import hashlib
import json
from pathlib import Path

MAIN = Path('/home/administrator/Desktop/sport-analytics/Sports_Analytics')
WORK = MAIN / 'evaluation/ground_truth_validation'
ART = MAIN.parent / 'ground-truth-validation-artifacts-20261112/pre_test03_v4/test01_candidate_v4'
REVIEW = WORK / 'regression_tests/pre_test03_contract_v1/test01_independent_v4'
VISUAL = WORK / 'regression_tests/pre_test03_contract_v1/visual_test01_v4_review'

def read(path):
    return json.loads(path.read_text())

def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()

completion = read(ART / 'completion.json')
comparison = read(ART / 'comparison.json')
visual = read(VISUAL / 'completion.json')
guard = read(REVIEW / 'native_guard_receipt.json')
protected = read(REVIEW / 'protected_inputs_review.json')
assert completion['candidate_commit'] == '2418ab8cbe4cca74dd16b722b9727ffdc950294a'
assert completion['frames'] == 17268 and completion['new_neural_inference'] and completion['own_run_semantic_parity']
assert all(completion[k] for k in ('source_helpers_models_profile_frozen', 'annotations_and_baselines_unchanged', 'actual_model_identity_equal'))
assert all(row['baseline']['detection'] == row['candidate']['detection'] for row in comparison['interval_references'].values())
coverage = read(REVIEW / 'all_182_coverage_review.json')['summary']
assert coverage['total'] == coverage['bbox_exact'] == 182
assert not read(REVIEW / 'all_current_gross_population_losses.json')['rows']
scene = read(REVIEW / 'summary.json')['scene_differences']
assert not scene['new_vs_original'] and not scene['lost_vs_original']
assert guard['status'] == 'passed_actual_candidate_native_strict_completion_guard' and guard['guard_ROOT_rebased'] is False
assert protected['status'] == 'all_protected_inputs_unchanged' and protected['original_Part2_file_count'] == 62
assert visual['status'] == 'completed' and visual['unique_source_frames_visually_reviewed'] == 88
assert visual['no_additional_gross_visual_blocker_found'] is True
counts = {}
for label, base, values in [('producer', ART, completion['artifact_sha256']), ('visual_review', VISUAL, visual['artifact_sha256'])]:
    for name, digest in values.items():
        path = Path(name) if Path(name).is_absolute() else base / name
        assert path.is_file() and sha(path) == digest, (label, str(path))
    counts[label] = len(values)
receipt = {
    'status': 'accepted_for_sequential_cross_test_validation_with_disclosed_limitations',
    'accepted_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'test': 1, 'candidate_commit': completion['candidate_commit'],
    'candidate_root': '/home/administrator/Desktop/sport-analytics/test03-scene-evidence-contract-20261112',
    'full_fresh_frames': 17268, 'all_six_detection_matrices_unchanged': True,
    'all_13_original_content_barriers_preserved': True,
    'previously_withheld_regions_restored_exactly': 182, 'new_gross_participant_count_loss_rows': 0,
    'verified_artifact_counts': counts, 'original_Part2_hashes_unchanged': 62,
    'physical_accuracy_gain_claimed': False, 'all_test1_issues_fixed_claimed': False,
    'retained_limitations': [
        '61 common legacy point distances worsen; maximum increase about3.99px; references are not physical truth',
        'Carry lag, shoe-adjacent shuttle alias and occlusion uncertainty remain',
        'Six added contacts, three class changes and anonymous actor changes remain unverified hypotheses',
        'Internal confirmed event status is not independently verified physical contact',
        'Unsupported physical AP/identity/pose/contact/class/winner/highlight accuracy remains unavailable',
        'Named winners and accepted points remain unavailable',
    ],
    'next_authorized_step': 'Restore only exact Test2 bytes into a new owned directory and run the same frozen candidate; Test3 remains gated',
    'input_receipt_sha256': {str(p): sha(p) for p in [
        ART / 'completion.json', ART / 'comparison.json', REVIEW / 'native_guard_receipt.json',
        REVIEW / 'summary.json', REVIEW / 'all_182_coverage_review.json',
        REVIEW / 'all_current_gross_population_losses.json', REVIEW / 'protected_inputs_review.json',
        VISUAL / 'completion.json', VISUAL / 'REPORT.md', Path(__file__).resolve(),
    ]},
}
output = WORK / 'regression_tests/pre_test03_contract_v1/test01_acceptance_v4.json'
with output.open('x') as stream:
    json.dump(receipt, stream, indent=2)
    stream.write('\n')
print(json.dumps({'accepted': True, 'verified_artifacts': counts, 'next': 'exact owned Test2 restoration'}))
