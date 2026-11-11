"""Complete separate read-only Test2 diagnostics after the fresh baseline.

Does not infer, change pipeline code, clean media or advance to Test3.
"""
from pathlib import Path
import json
import sys
import time
import traceback

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from run_test02_baseline import ART, TEST, WORK, call, dump, read, sha, state


def main():
    resume_causal = sys.argv[1:] == ['--resume-causal-provider-options']
    if sys.argv[1:] and not resume_causal:
        raise ValueError('Unsupported diagnostic continuation option')
    print('Waiting for full Test2 baseline; no live database opened', flush=True)
    while not (ART/'baseline_completion.json').exists():
        status = read(TEST/'orchestration/status.json')
        if 'failed' in status['stage']:
            raise RuntimeError('Original baseline failed; preserving it without diagnostic bypass')
        time.sleep(20)
    assert read(ART/'baseline_completion.json')['status'] == 'completed_fresh_Test2_baseline_and_diagnostics'
    state('Test2 full baseline complete; coordinate-bound diagnostics and causal review in progress')
    binding = TEST/'diagnostics/annotation_visual_review/diagnostic_coordinate_binding.json'
    if resume_causal:
        assert 'unexpected keyword argument' in (ART/'causal_analysis.log').read_text()
        assert 'use_short_exchange_evidence' in (ART/'causal_analysis.log').read_text()
        assert not (ART/'causal_analysis').exists(), 'Never overwrite partial causal artifacts'
        assert read(ART/'bound_reference_diagnostics/component_reference_metrics.json')['status'] == 'completed_readonly_component_reference_diagnostics'
    else:
        call([WORK/'orchestration/evaluate_test02_components.py','--run',ART/'run',
              '--output',ART/'bound_reference_diagnostics','--coordinate-binding',binding], 'bound_reference_diagnostics')
    call([ROOT/'research/test2_causal_analysis.py','--run',ART/'run','--replay',ART/'diagnostic_replay',
          '--evaluation',ART/'rally_reference_evaluation','--output',ART/'causal_analysis'],
         'causal_analysis_retry_provider_options' if resume_causal else 'causal_analysis')
    call([WORK/'orchestration/export_test02_heatmaps.py','--artifact-root',ART,
          '--output',ART/'heatmap_exports'], 'heatmaps')
    call([WORK/'orchestration/build_test02_matrix.py','--artifact-root',ART,
          '--output',WORK/'reports/test_02_baseline_v1'], 'evaluation_matrix')
    original = read(ART/'annotation_hashes_before.json')
    assert all(sha(p)==h for p,h in original.items()), 'Original annotation changed'
    dump(ART/'all_reference_diagnostics_completion.json', dict(
        status='full_Test2_baseline_component_metrics_and_source_diagnostics_complete',
        report=str(WORK/'reports/test_02_baseline_v1/matrix.md'),
        original_annotations_unchanged=True, production_code_changed=False,
        next='Root review synchronized findings and decide evidence-based fixes/regressions; no automatic Test3 or cleanup.'))
    state('Test2 baseline matrix ready; final root-cause review and fix decision pending',
          report=str(WORK/'reports/test_02_baseline_v1/matrix.md'))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        traceback.print_exc()
        state('Test2 additional diagnostics failed; preserve complete baseline and logs', error=str(error))
        sys.exit(1)
