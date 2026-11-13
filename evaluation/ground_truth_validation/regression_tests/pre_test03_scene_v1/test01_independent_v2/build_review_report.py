"""Publish an exclusive independent report from already guarded closed evidence."""

from pathlib import Path
from hashlib import file_digest
import datetime
import json
import re

ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
ART = ROOT / 'ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2'
OUT = Path(__file__).resolve().parent


def read(path):
    return json.loads(Path(path).read_text())


def sha(path):
    with Path(path).open('rb') as source:
        return file_digest(source, 'sha256').hexdigest()


def number(value, digits=6):
    return 'unavailable' if value is None else f'{value:.{digits}f}'


def main():
    s = read(OUT / 'summary.json')
    refs = read(OUT / 'interval_reference_differences.json')
    points = read(OUT / 'point_population_decomposition.json')
    events = read(OUT / 'event_differences.json')
    gross = read(OUT / 'gross_coverage_all_182_rows.json')
    coverage = read(OUT / 'coverage_tradeoffs.json')
    scene = read(OUT / 'scene_boundary_review_inputs.json')
    native = read(OUT / 'native_guard_receipt.json')
    completion = read(ART / 'completion.json')
    for data in [s, gross, coverage]:
        assert all(sha(path) == digest for path, digest in data['input_sha256'].items())
    for path, digest in completion['artifact_sha256'].items():
        assert sha(ART / path) == digest
    assert all(sha(path) == digest for path, digest in native['input_paths_sha256'].items())
    assert not s['scene_differences']['new_vs_original'] and not s['scene_differences']['lost_vs_original']
    assert gross['original_vs_fresh_common_raw_shuttle_equal'] is True
    original = points['original_versus_fresh']
    lines = [
        '# Independent fresh Test1 review — c585e35 candidate v2', '',
        '**The candidate repairs both failed c7 edit controls and removes the7857–7859 stale box, while preserving all six interval detection matrices. There is a material participant-coverage tradeoff:182 original participant rows are withheld across seven offcourt intervals, even though their image regions remain available for scene continuity.** Conditional point agreement and net coverage gains must not hide those losses or be called physical recall nonregression.', '',
        'This is an independent read-only review of a completed genuine fresh-NN run. It does not approve the whole phase, claim every Test1 issue is fixed, certify physical component accuracy, or complete Test3. Root owns acceptance and the next sequential video.', '',
        '## Evidence gates and comparison arms', '',
        f'- Actual candidate:`{s["candidate_commit"]}`;17,268canonical1280×720frames at30/1fps. Worker and original parent completed with fresh perception; own-cache semantic parity is recorded true.',
        f'- The unchanged strict guard was executed from the actual recorded candidate ROOT, without rebasing imports. All{s["completed_artifacts_verified"]:,} completed artifact hashes and{s["source_plan_files_verified"]} source-plan hashes were independently checked. Numerical profile, actual model identities, nine Test1 annotation hashes and unchanged evaluation-method bindings pass.',
        '- Before perception/resources/intervals: original preserved Test1improved_v1 full-NN output. Additional failed-control comparison:c7freshTest1. Baselines were read as saved, not re-evaluated using current code.',
        '- Before contacts/classes: latest dacc05e semantic replay over preserved perception (445contacts,301unknown). This is cached-semantic versus fresh-NN, not a single-variable fresh-NN experiment.',
        f'- SourceSHA256:`{s["source_sha256"]}`. Complete native/source/model/method bindings:[native guard](native_guard_receipt.json), [computational summary](summary.json), [original completion]({ART / "completion.json"}).', '',
        '## Six reference matrices', '',
        'Detection dictionaries and matching policies are unchanged. Existing IoU≥0.5assignment, half-open timestamps, tolerance denominators, exclusions and zero/unavailable conventions remain intact. Coarse labels, generated timing references and partial Full2 retain their original disclosed roles; generated agreement is not independent physical ground truth.', '',
        '| Reference | TP/FP/FN before = fresh | Precision / Recall / F1 before = fresh | Mean IoU before → fresh | Fresh start/end/duration MAE(s) |',
        '|---|---|---|---|---|',
    ]
    for name, row in refs.items():
        a, b = row['before_metrics'], row['fresh_metrics']
        assert a['detection'] == b['detection']
        d = b['detection']
        counts = '/'.join('unavailable' if d[key] is None else str(d[key]) for key in ['true_positives', 'false_positives', 'false_negatives'])
        rates = ' / '.join(number(d[key]) for key in ['precision', 'recall', 'f1'])
        errors = ' / '.join(number(b['boundary_and_duration_errors'][key]['mae']) for key in ['start_time_sec', 'end_time_sec', 'duration_sec'])
        lines.append(f'| `{name}` | {counts} | {rates} | {number(a["overlap"]["mean_iou"])} → {number(b["overlap"]["mean_iou"])} | {errors} |')
    lines += [
        '', 'Only predicted rally19start changes8111→8108; all other starts and every end are unchanged. Primary generated reference19starts8106and ends8628: start error5→2frames, prediction end8627unchanged, duration error−0.2→−0.1s and rowIoU0.988505747→0.994252874. The tiny six-reference IoU improvement comes from this single boundary. Full2FP/precision/F1 remainnull; unlabelled predictions are not silently counted as false detections.', '',
        'All changed per-reference rows, complete metrics/tolerances/signed-error distributions and raw source rows remain accessible:[independent interval differences](interval_reference_differences.json), [fresh component matrix](' + str(ART / 'bound_reference_diagnostics/component_reference_metrics.json') + '), [saved baseline](' + str(ART / 'before_components.json') + ').', '',
        '## Scene continuity: confirmed repairs', '',
        'Fresh content barriers exactly match the original13:2195,4837,7503,7857,8106,10023,10604,10770,11903,15579,15985,16446,17069. Relative to c7,7857and8106are recovered and none are lost. Relative to the original there are no new or lost content barriers. Matching a count alone is not scene precision/recall or proof that every inherited barrier is a true edit.', '',
        'At7857two current athlete boxes are detector-observed immediately;7858–7859carry those current boxes. Every box has0IoUto the known old7854/7856 near-player stale region, which is visibly empty after the edit. The failed c7maximum170.104874px disappears; the all-returned generated-player maximum returns to the inherited70.435594px at13467. At8106the barrier and immediate current athlete acquisition also hold.', '',
        'Independent source views:[7857](source_evidence/frame_07857.png), [7859](source_evidence/frame_07859.png), [8106](source_evidence/frame_08106.png). Exact cache/scene evidence:[scene boundary review inputs](scene_boundary_review_inputs.json). These are source-bound agent diagnostics, not newly created physical labels.', '',
        '## Point agreement and population changes', '',
        '| Original full-NN → fresh | Pairs | Mean disagreement(px) | Maximum(px) |',
        '|---|---|---|---|',
    ]
    for kind, title in [('all_current_rows_assignments', 'All returned players'), ('fresh_detector_rows_assignments', 'Fresh detector-matched players')]:
        p = original[kind]
        lines.append(f'| {title}: full population | {p["before_all"]["count"]} → {p["fresh_all"]["count"]} | {number(p["before_all"]["mean"])} → {number(p["fresh_all"]["mean"])} | {number(p["before_all"]["maximum"])} → {number(p["fresh_all"]["maximum"])} |')
        lines.append(f'| {title}: identical frame/legacy-slot subset | {p["common_before"]["count"]} → {p["common_fresh"]["count"]} | {number(p["common_before"]["mean"])} → {number(p["common_fresh"]["mean"])} | {number(p["common_before"]["maximum"])} → {number(p["common_fresh"]["maximum"])} |')
        lines.append(f'| {title}: new-only | {p["new_only"]["count"]} | {number(p["new_only"]["mean"])} | {number(p["new_only"]["maximum"])} |')
        lines.append(f'| {title}: old-only | {p["old_only"]["count"]} | {number(p["old_only"]["mean"])} | {number(p["old_only"]["maximum"])} |')
    lines += [
        '', 'Every33,409common all-player error and every13,955common detector-matched error is numerically identical to the original. The all-row mean increase is therefore a population effect, not a common-subset degradation. This conditional equality does **not** demonstrate all-frame physical recall preservation. Comparing c7→fresh, the common all-row mean decreases3.101034→3.082969px and the170px stale-box outlier is removed; all14,000common detector-matched errors are unchanged.', '',
        'Raw shuttle XYand confidence are exactly identical to the original on all17,268frames. Presence12,036and generated-reference both-present11,853 remain unchanged; mean7.459980px, median1.478514px and maximum561.768698px are unchanged. Source13153still exposes an inherited shoe-alias diagnostic. Filled-reference disagreement cannot be converted into physical shuttleAP/PR or a reviewed localization error.', '',
        'Complete common/new-only/old-only keys and original/c7 decompositions:[point population decomposition](point_population_decomposition.json). Original source rows are preserved in the producer’s [frame-point JSONL](' + str(ART / 'bound_reference_diagnostics/frame_point_candidates.jsonl') + ').', '',
        '## Explicit coverage costs: all57scored losses and all182withheld rows', '',
        'The57old-only generated-point pairs are alllegacy slot2:6375–6381(7),7801–7805(5),7812–7856(45). Their former matched distances average2.812589px, maximum7.040684px; they are not dropped from this report. All57corresponding image regions remain in foreground context withIoU>0.99to the original box;46are unobserved carries and11are fresh matched image observations. Current detector support is retained in8of these rows’ detailed diagnostics. Foreground has no confidence field; missing current support is explicitly unavailable and is never copied from historical person confidence.', '',
        'The broader raw participant tradeoff is182withheld rows over182frames, compared with240additional rows over173frames: net+58rows. The net gain must not conceal the gross losses. The182missing participant regions are all retained as scene-only context (minimum same-regionIoU>0.999998).', '',
        '| Fewer-participant interval | Rows withheld | Reconstructed last padded-court anchor | Representative source assessment |',
        '|---|---:|---:|---|',
    ]
    descriptions = ['Near dark-top athlete beyond near baseline, lower-left', 'Near dark-top athlete beyond near baseline, lower-right', 'White-top athlete outside right sideline near umpire', 'White-top athlete beyond far baseline', 'Far white-top athlete remains visible near boards', 'Near dark-top athlete beyond near baseline, lower-right', 'Far dark-top athlete outside right sideline near umpire']
    for row, description in zip(gross['groups'], descriptions, strict=True):
        start, end = row['frames']
        lines.append(f'| {start}–{end} | {row["count"]} | {row["last_padded_court_anchor_reconstructions"][0]} | [{description}](source_evidence/frame_{start:05d}.png) |')
    lines += [
        '', 'These reconstructed leases expire31frames after the last observed padded-court anchor; later raw image matches renew scene context, not participant authority. Source checks in every interval show visible courtside athletes at representative frames, not obvious officials. This is a real semantic-coverage tradeoff. It does not become182independently labelled false negatives, because complete role/visibility identities are unavailable and not every frame was manually adjudicated. Scene context also supplies no pose/contact/named-player authority for those withheld people.', '',
        'Only57of those182losses appear as old-only matched legacy pairs. Other frames, including8087–8105, lack the same legacy assignment population; a generated reference’s missing pair is not proof the visible athlete is irrelevant. All182rows, flags, exact boxes, reconstructed ages and available current support are retained:[gross coverage ledger](gross_coverage_all_182_rows.json), [57pair ledger](coverage_tradeoffs.json). Timestamps are reconstructed from recorded observations/native court predicates, not invented private-state traces.', '',
        '## Contacts, classes and identity scope', '',
        'Latest dacc semantic445→fresh452contacts/strokes. All445exact anchors are retained with no candidate shifts or removals. Seven new anchors are1438,1488,3015,3558,6471,8108,10676: fiveunknown and twolift(1488/3558). Their recorded physical statuses are ambiguous or insufficient; added counts are not validated contact recall.', '',
        'Only same-anchor class changes are3540lift→push and6456clear→drop. Their recorded flight-time features change1.733333→0.6s and2.0→0.5s respectively. These are temporal/context feature changes with unchanged raw neural shuttle observations; class accuracy is unavailable without per-contact GT. The failed c7candidate’s three shifted anchors and8380lift→drive change are absent here.', '',
        '| Predicted class | Latest cached-semantic before | Fresh c585 |', '|---|---:|---:|',
    ]
    for label in sorted(events['before_stroke_labels'].keys() | events['fresh_stroke_labels'].keys()):
        lines.append(f'| {label} | {events["before_stroke_labels"].get(label, 0)} | {events["fresh_stroke_labels"].get(label, 0)} |')
    lines += [
        '', 'Unknown301/445=67.640449%→306/452=67.699115%. No same-anchor anonymous actor episode/status change is detected; no physicalIDF1/HOTA inference follows. Named contact actors remain0and known rally winners remain0. Broadcast-score observations473and highlights4are unchanged; no accepted point event is recorded. Observed scoreboard values are not an accepted verified match score.', '',
        'Detailed compact event differences, physical-evidence statuses and class counts:[event differences](event_differences.json). The [45-frame source plan](source_frame_plan.json), [all-coverage plan](all_coverage_frame_plan.json) and source-bound [agent observations](agent_source_observations.json) preserve controls for separate rendering/review.', '',
        '## Remaining perception limitations', '',
        '- At11333a newly available box is carried from11328while the near athlete lunges. It visibly lags; its generated-reference distance57.284493px is a newly exposed estimate/cadence limitation, not physical GT localization error. The old arm had no matched pair there. [Source11333](source_evidence/frame_11333.png).',
        '- At13153the inherited raw shuttle point is near the athlete’s shoe. The filled reference is also not independently trustworthy; this remains an unresolved model/candidate diagnostic. [Source13153](source_evidence/frame_13153.png).',
        '- At13467athletes overlap near the left/net region; the inherited70.435594px player disagreement remains. No box-ground-truth adjudication establishes a physical IoU/AP score. [Source13467](source_evidence/frame_13467.png).',
        '- Other independent rendered review retains inherited false raw racket ellipses, including near-body15808. Semantic ambiguity admission is not a repair of every raw racket detection. [Separate rendered review](' + str(MAIN / 'evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/visual_test01_v1_review.md') + ').', '',
        '## Component coverage, resources and unavailable metrics', '',
        '| Count / resource | Original full-NN | Fresh c585 full-NN |', '|---|---:|---:|',
    ]
    for key in ['detector_executed_frames', 'person_rows', 'person_current_detector_matches', 'person_propagated_or_unmatched', 'pose_present_rows', 'racket_present_rows']:
        lines.append(f'| `{key}` | {s["all_current_raw_coverage_before"][key]} | {s["all_current_raw_coverage_fresh"][key]} |')
    for key in ['worker_elapsed_s', 'worker_source_fps', 'parent_completed_elapsed_s', 'worker_final_cpu_s', 'worker_maxrss_bytes', 'sampled_worker_tree_peak_rss_bytes', 'sampled_worker_gpu_peak_mib']:
        lines.append(f'| `{key}` | {number(s["resource_before"][key], 3)} | {number(s["resource_fresh"][key], 3)} |')
    lines += [
        '', 'Both runs use physicalGPU1with the same recorded device UUID. These are resource observations on a shared host; overlapping stage timers and sampled peaks do not support a causal throughput claim. Peak processRSS increases2.841→3.213GB while sampled GPU peak remains2124MiB. Full actual backend/checkpoint provenance, including OCR package assets and extracted pose graph, is preserved in the [runtime asset audit](' + str(MAIN / 'evaluation/ground_truth_validation/regression_tests/pre_test03_scene_v1/runtime_assets_v1/REPORT.md') + ').', '',
        'Single-frame court reference8634 remains mean1.797572px/max3.529582px outer-singles-corner disagreement under its source/coordinate certificate; it does not certify all-frame geometry. All10unsupported physical metric families remainnull: playerAP/mAP/boxIoU; trackingIDF1/HOTA/switches/fragmentation; posePCK/OKS; physical shuttlePR/localization; racket/contactPR/F1/timing; per-stroke classPR/F1/confusion; physical outcome accuracy/confusion; score accuracy; highlight quality; named-player analytics accuracy. Null means unavailable evidence, not zero performance.', '',
        '**Disposition:** the confirmed c7same-camera edit regression is repaired in this genuine fresh run and reference detection agreement is preserved. Acceptance must retain the explicit182-row participant-coverage cost,57old-onlypairs, newly exposed carried-box lag and inherited raw perception errors. This review provides no new code fix, no full-phase/Test3 completion claim and no physical generalisation guarantee. Complete fresh Test2 and the planned component-specific diagnostics remain separate work.', '',
    ]
    report = OUT / 'REPORT.md'
    with report.open('x') as output:
        output.write('\n'.join(lines))
    for link in re.findall(r'\]\(([^)]+)\)', report.read_text()):
        assert (Path(link) if link.startswith('/') else OUT / link).exists(), link
    final = {'status': 'completed_independent_Test1_review_with_disclosed_coverage_tradeoffs', 'candidate_commit': s['candidate_commit'], 'completed_artifacts_verified': s['completed_artifacts_verified'], 'source_plan_files_verified': s['source_plan_files_verified'], 'six_detection_matrices_unchanged': True, 'common_point_errors_exactly_unchanged': True, 'all_original13_content_barriers_preserved': True, 'c7_failed_edit_controls_repaired': [7857, 8106], 'new_or_lost_barriers_vs_original': [], 'gross_withheld_participant_rows': 182, 'original_only_generated_point_pairs': 57, 'gross_new_participant_rows': 240, 'all_withheld_regions_retained_as_scene_context': True, 'physical_recall_nonregression_claimed': False, 'all_Test1_issues_fixed_claimed': False, 'physical_metric_families_unavailable': 10, 'source_examples_reviewed': read(OUT / 'agent_source_observations.json')['visually_reviewed_frames'], 'full_phase_or_Test3_completed_claimed': False}
    with (OUT / 'final_summary.json').open('x') as output:
        json.dump(final, output, indent=2)
        output.write('\n')
    artifacts = {str(path.relative_to(OUT)): sha(path) for path in sorted(OUT.rglob('*')) if path.is_file()}
    with (OUT / 'verification_receipt.json').open('x') as output:
        json.dump({'status': final['status'], 'verified_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'completed_worker_parent_catalogue_native_guards_passed': True, 'all_consumed_inputs_unchanged': True, 'completed_artifacts_rehashed': len(completion['artifact_sha256']), 'no_inference_or_production_evaluator_annotation_edits': True, 'no_Test3_access': True, 'artifact_sha256': artifacts}, output, indent=2)
        output.write('\n')
    print(json.dumps(final, indent=2))


if __name__ == '__main__':
    main()
