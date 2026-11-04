# Independent benchmark and evaluation audit

## Scope and immutable evidence

Audit at `b773e20c62d1c398cddc3d23510bd4adf823325b`; production baseline `301baf08be5e989dd0ed93cb885733c3cf6f356a`. No production evaluator/source, original media, GT or frozen baseline artifact was modified. This audit reran evaluation only; it did not rerun video inference.

Read the full benchmark report, README, pipeline trace, seven-column CSVs, metrics, metadata, diagnostics, inference records, raw events, execution log and relevant export/evaluator source. Evidence hashes and all36 per-rally records are in `research/benchmark_audit.json`.

## Independent reproduction

```bash
source ../gpu-env.sh
python research/audit_a_benchmark.py --output artifacts/benchmarking/investigation/audit_a_final
```

The production evaluator was reproduced into a new output directory. Its complete metrics JSON is value-identical and comparison CSV byte-identical to the frozen baseline. Independently, an exact-fraction ordered dynamic program recovered the same30 pair assignments. Ordered DP is valid for these two disjoint, sorted interval lists because positive-overlap matches cannot cross; it is not a replacement for the general bipartite matcher. Independent Python statistics and linear percentiles reproduce all stored errors/tolerances within1e-10. Raw-event folding independently recovers exactly the49 exported intervals. Video/CSV and recorded evidence hashes match; all86 production source hashes match the recorded production Git objects.

| Metric | Independently verified baseline |
| --- | --- |
| GT / predictions / matched | 36 / 49 / 30 |
| TP / FP / FN | 30 / 19 / 6 |
| Precision / recall / F1 | 0.612244898 / 0.833333333 / 0.705882353 |
| Start MAE / RMSE / median absolute, frames | 49.433333 / 75.253128 / 23 |
| End MAE / RMSE / median absolute, frames | 40.4 / 96.463119 / 7 |
| Start / end signed bias, frames | +48.033333 / -33.4 |
| Duration MAE / RMSE / bias, seconds | 2.845556 / 4.346378 / -2.714444 |
| Matched mean / median IoU | 0.763314890 / 0.767948002 |

## Seven-column semantics

`Start_Frame`/`End_Frame` are zero-based boundary indices under the adopted arithmetic convention; `Start_Time_sec`/`End_Time_sec` equal their index divided by independently recorded30FPS. `Duration_sec` is the difference of those timestamps. `Start_Time`/`End_Time` truncate to whole seconds and format MM:SS. Both CSVs have exactly the seven columns in the required order. No numeric drift or missing/invalid row was found. Source/proxy timestamp audits agree, but the numerical checks do not recover the unavailable human annotation-tool history. The raw labels remain authoritative as supplied; no offset is fitted.

Production event endpoints identify inclusive observations; this benchmark measures spans between their timestamps, [start,end), exactly matching annotated durations. It correctly does not copy the rounded inclusive production payload duration. No one-frame adjustment is warranted.

## Matching and interpretation

Eligibility is IoU>=0.5; a pair can be used once. The cardinality bonus2*(min(Ngt,Npred)+1) dominates every possible total secondary score, so maximum eligible count is prioritized. The secondary objective matches the documented IoU plus1e-9/(1+boundary-distance-seconds). Strict 'exceeds' coverage percentages use >, while eligibility uses >=. Frame tolerance checks include equality and correctly report both matched-only and all-GT denominators. Nothing in the audit justifies changing the frozen protocol.

The central diagnostic distinction is **selected-fragment boundary error versus first/last available evidence**. GT2 and19 have initial fragments beginning only4frames late, but matching selects later fragments with179/202frame start errors. GT20/27 have later fragments reaching 20/12frames before the labeled end, while selected fragments end442/218frames early. Those are real whole-interval benchmark failures, yet they do not independently prove an equally large first-onset/final-offset delay. No improved prediction or score is claimed from this GT-dependent diagnostic union.

All19 policy-FP predictions overlap GT, and all6 FN labels have partial coverage. Eleven labels overlap multiple predictions. Therefore inter-rally hallucination suppression is not the primary explanation for this particular FP count. Positive overlap still does not prove a semantically correct interval. GT23 includes a4frame spillover from the previous matched rally; automatic earliest-overlap backdating would join distinct rallies.

GT29's best single IoU is exactly157/315=0.4984126984. Inclusive counting would give158/316=0.5 and manufacture a policy TP. Its existing FN is not floating precision error. The correct investigation target is the observed split, not the evaluator threshold/end convention.

## Per-rally independent error and coverage analysis

The last two columns are supplementary earliest/latest *positive-overlap* diagnostics, not replacement predictions or evaluation results. In particular, GT23's negative earliest start comes from preceding-rally spillover. Errors are predicted minus annotated frames.

| GT | Matched pred | Overlap segments | Best single IoU | Union coverage | Matched start err | Matched end err | Earliest start err | Latest end err |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 1 | 1 | 0.793249 | 0.796610 | 96 | 2 | 96 | 2 |
| 2 | 3 | 2 | 0.504000 | 0.856000 | 179 | -7 | 4 | -7 |
| 3 | 4 | 2 | 0.597744 | 0.857143 | 4 | -103 | 4 | -10 |
| 4 | 6 | 1 | 0.928328 | 0.947735 | 15 | 6 | 15 | 6 |
| 5 | unmatched | 1 | 0.393103 | 0.393103 | unmatched | unmatched | 99 | -77 |
| 6 | 8 | 1 | 0.556452 | 0.556452 | 103 | -7 | 103 | -7 |
| 7 | 9 | 1 | 0.982544 | 0.982544 | 7 | 0 | 7 | 0 |
| 8 | 10 | 1 | 0.696356 | 0.704918 | 72 | 3 | 72 | 3 |
| 9 | 11 | 1 | 0.608696 | 0.608696 | 112 | -14 | 112 | -14 |
| 10 | 12 | 1 | 0.648649 | 0.648649 | 97 | -111 | 97 | -111 |
| 11 | 13 | 1 | 0.728324 | 0.728324 | 29 | -18 | 29 | -18 |
| 12 | 14 | 1 | 0.910284 | 0.943311 | 25 | 16 | 25 | 16 |
| 13 | 15 | 1 | 0.935028 | 0.935028 | 21 | -2 | 21 | -2 |
| 14 | 16 | 1 | 0.686131 | 0.686131 | 69 | -17 | 69 | -17 |
| 15 | 17 | 1 | 0.532995 | 0.532995 | 87 | -5 | 87 | -5 |
| 16 | 18 | 1 | 0.867562 | 0.937759 | 30 | 39 | 30 | 39 |
| 17 | 19 | 1 | 0.937799 | 0.937799 | 3 | -10 | 3 | -10 |
| 18 | 20 | 1 | 0.933962 | 0.933962 | 6 | -1 | 6 | -1 |
| 19 | 22 | 2 | 0.611111 | 0.909962 | 202 | -1 | 4 | -1 |
| 20 | 23 | 3 | 0.630841 | 0.911215 | 32 | -442 | 32 | -20 |
| 21 | 26 | 1 | 0.908805 | 0.908805 | 5 | -24 | 5 | -24 |
| 22 | 27 | 1 | 0.742647 | 1.000000 | -6 | 29 | -6 | 29 |
| 23 | unmatched | 3 | 0.402899 | 0.788406 | unmatched | unmatched | -132 | 7 |
| 24 | 30 | 1 | 0.936508 | 0.975207 | 3 | 5 | 3 | 5 |
| 25 | unmatched | 2 | 0.373737 | 0.589226 | unmatched | unmatched | 66 | 2 |
| 26 | 33 | 1 | 0.678733 | 0.678733 | 70 | -1 | 70 | -1 |
| 27 | 34 | 2 | 0.568932 | 0.924272 | 4 | -218 | 4 | -12 |
| 28 | unmatched | 2 | 0.427835 | 0.623711 | unmatched | unmatched | 122 | -3 |
| 29 | unmatched | 2 | 0.498413 | 0.812698 | unmatched | unmatched | 7 | -12 |
| 30 | 40 | 1 | 0.939655 | 0.939655 | 3 | -4 | 3 | -4 |
| 31 | unmatched | 3 | 0.358768 | 0.776439 | unmatched | unmatched | 87 | 20 |
| 32 | 44 | 1 | 0.945946 | 0.945946 | 4 | -6 | 4 | -6 |
| 33 | 46 | 2 | 0.512676 | 0.711429 | 168 | 5 | 72 | 5 |
| 34 | 47 | 1 | 0.957921 | 0.994859 | -15 | -2 | -15 | -2 |
| 35 | 48 | 1 | 0.805068 | 0.805068 | 8 | -92 | 8 | -92 |
| 36 | 49 | 1 | 0.812500 | 0.812500 | 8 | -22 | 8 | -22 |

## Evidence-backed findings and causal experiments

### A01: verified calculation correctness

**Observed symptom:** Poor baseline scores might be caused by evaluator arithmetic or matching defects.

**Supporting evidence:** Exact-rational ordered dynamic programming returns the same 30 pairs; independent arithmetic matches every recorded boundary/duration statistic and tolerance; fresh production evaluator JSON and comparison bytes match frozen artifacts.

**Source functions:** scripts/benchmarking/evaluate_rallies.py:54 read_csv; scripts/benchmarking/evaluate_rallies.py:98 interval_iou; scripts/benchmarking/evaluate_rallies.py:103 match_rallies; scripts/benchmarking/evaluate_rallies.py:123 error_stats; scripts/benchmarking/evaluate_rallies.py:149 evaluate

**Hypothesized cause:** No arithmetic, assignment, sign or frame-unit defect explains this baseline.

**Alternative explanations:** Annotation ambiguity or physical observation failures can exist despite correct arithmetic.

**Confidence:** high

**Causal experiment:** Replay exactly frozen predictions through the unchanged evaluator and independently recompute pairs and errors; completed successfully.

**Proposed action:** Freeze the existing matching protocol; use supplementary diagnostics rather than changing scores.

**Expected metric effect:** None from evaluator repairs: no baseline score defect was found.

**Regression risk:** Changing matching, endpoints or tolerance denominators would break baseline comparability.

### A02: proven diagnostic interpretation issue

**Observed symptom:** GT2/19 matched starts are +179/+202 frames late; GT20/27 matched ends are -442/-218 frames early.

**Supporting evidence:** GT2/19 first fragments start only +4 frames late. GT20/27 later fragments reach -20/-12 frames before the labeled end. The selected eligible interval excludes those other fragments.

**Source functions:** scripts/benchmarking/evaluate_rallies.py:103 match_rallies; scripts/benchmarking/evaluate_rallies.py:156 per-GT comparison loop; outputs/benchmarking/test1/predicted_rallies.csv; outputs/benchmarking/test1/rally_comparison.csv

**Hypothesized cause:** One-to-one assignment correctly measures whole-interval agreement, while fragmentation makes selected-fragment errors look like first-onset/final-offset detector errors.

**Alternative explanations:** Other single-fragment rallies have real multi-second onset delay; fragmentation does not explain all start errors.; Ground-truth endpoint conventions remain physically unverified.

**Confidence:** high

**Causal experiment:** Compare selected-match errors with earliest/latest positive-overlap boundaries without changing primary predictions; completed as supplementary diagnostics. Replay exact FSM decisions to establish why each split occurred.

**Proposed action:** Prioritize continuity mechanisms for GT2/19/20/27; diagnose standalone onset delays separately.

**Expected metric effect:** Recovering a continuous supported interval can improve FP/FN, selected-boundary errors, duration and IoU together; numeric gain requires inference/replay evidence.

**Regression risk:** Naively unioning all GT-overlapping predictions leaks labels and can join distinct rallies.

### A03: proven error taxonomy

**Observed symptom:** Nineteen false-positive intervals may be mistaken for movement/noise between rallies.

**Supporting evidence:** All 19 unmatched predictions have positive temporal overlap with at least one GT interval; zero predicted intervals have no GT overlap. All six unmatched labels have partial predicted coverage.

**Source functions:** scripts/benchmarking/evaluate_rallies.py:208 TP/FP/FN counts; outputs/benchmarking/test1/predicted_rallies.csv; research/audit_a_benchmark.py:intersection

**Hypothesized cause:** Policy false positives are predominantly unmatched fragments/truncated intervals here; there is no evidence that suppressing inter-rally movement is the principal remedy.

**Alternative explanations:** A false interval may overlap genuine play yet have wrong boundaries; positive overlap does not establish semantic correctness.

**Confidence:** high

**Causal experiment:** Trace gap/stationary closures and continuation evidence at fragment pairs; compare controlled recovery against closely spaced separate-rally controls.

**Proposed action:** Retain FP=19 under the frozen protocol; add the no-overlap FP count and per-GT segment/coverage diagnostics.

**Expected metric effect:** Taxonomy improves causal targeting; it does not reduce the official FP count.

**Regression risk:** Dropping unmatched fragments without restoring intervals can hide failures and worsen recall.

### A04: proven near-threshold sensitivity

**Observed symptom:** GT29 is unmatched despite an almost half-length prediction.

**Supporting evidence:** Best fragment is frames13686..13843 within GT13679..13994: exact boundary-span IoU157/315=0.4984126984, correctly below0.5. Adding one frame to both spans gives158/316=0.5 and would change the result.

**Source functions:** scripts/benchmarking/evaluate_rallies.py:98 interval_iou; scripts/benchmarking/evaluate_rallies.py:115 eligibility; Part2/dataset/Test1_Full/Test1_Full_rally.csv:30

**Hypothesized cause:** Real fragment truncation lies immediately below the fixed eligibility threshold, not floating-point misclassification.

**Alternative explanations:** A physically justified annotation correction could alter this case, but independent review is unavailable and no correction is authorized as benchmark tuning.

**Confidence:** high

**Causal experiment:** Exact-fraction threshold comparison completed. Inspect shuttle/segmentation evidence around13843..13883 to explain the split, not tune IoU eligibility.

**Proposed action:** Preserve GT and [start,end) timestamp spans; report exact best-fragment IoU for unmatched labels.

**Expected metric effect:** No score change without a real predictive boundary improvement.

**Regression risk:** An inclusive-end convention switch manufactures a TP and violates baseline semantics.

### A05: proven cross-rally overlap caveat

**Observed symptom:** An earliest-overlapping-start diagnostic can suggest an unrealistically early start for GT23.

**Supporting evidence:** Prediction27 spans10601..10737 and matches GT22; it overlaps only4 frames at the start of GT23(10733..11078). Thus GT23's earliest-overlapping start is-132 frames, not evidence that this rally began at10601.

**Source functions:** research/audit_a_benchmark.py:per_rally overlap diagnostics; outputs/benchmarking/test1/predicted_rallies.csv; outputs/benchmarking/test1/rally_comparison.csv

**Hypothesized cause:** Any-positive-overlap fragmentation counts include minor cross-boundary spillovers.

**Alternative explanations:** A true merged interval could cross rallies, but this overlap alone cannot establish one.

**Confidence:** high

**Causal experiment:** Review original frames and temporal evidence at10708..10769; separately tag minimal spillovers and substantive fragments in supplementary diagnostics.

**Proposed action:** Use positive-overlap counts as diagnostics, never as an automatic GT-conditioned merging/backdating algorithm.

**Expected metric effect:** Prevents misleading causal conclusions; no change to primary metrics.

**Regression risk:** Naive overlap-based reconstruction can merge distinct legitimate rallies.

### A06: verified export and provenance with explicit limits

**Observed symptom:** Index/FPS/serialization or inclusive production duration payload might explain errors.

**Supporting evidence:** Both seven-column CSVs validate; every GT timestamp equals frame/30 and duration=end-start. All49 current rally_end events from independently folded raw log match prediction frames exactly. All recorded artifact/source hashes and86 production source fingerprints match. Existing source/proxy audits report17268 CFR frames at30FPS.

**Source functions:** scripts/benchmarking/production_inference.py:77 event selection; scripts/benchmarking/production_inference.py:115 export; scripts/benchmarking/evaluate_rallies.py:85 write_predictions; legacy/pipeline/analysis/detect_rallies.py:140 format_time; legacy/pipeline/analysis/detect_rallies.py:598 CSV export

**Hypothesized cause:** No serialized offset, duration-rounding or dropped-row defect explains baseline boundary errors.

**Alternative explanations:** Numerical consistency does not prove the unavailable manual tool's physical frame numbering or label rationale.; Content/frame correspondence needs the independent video audit, not metadata alone.

**Confidence:** high for arithmetic/export; unresolved for human frame semantics

**Causal experiment:** Independent raw-event fold, hash/source verification and evaluator reproduction completed; physical boundary/frame review remains the temporal auditor's task.

**Proposed action:** Preserve exact CSV bytes and annotations. Keep explicit frame conventions and separate observation-end index from interval-span duration.

**Expected metric effect:** No systematic offset correction is justified by this audit.

**Regression risk:** Blind one-frame or FPS corrections can alter near-threshold matches and hide perception defects.

### A07: verified general edge-case hardening opportunity, not baseline cause

**Observed symptom:** An empty GT input produces an empty comparison file with no CSV header.

**Supporting evidence:** save_evaluation opens rally_comparison.csv, but writer/header creation is inside if rows. read_csv also rejects one-frame/zero-span intervals by design; no such interval exists here.

**Source functions:** scripts/benchmarking/evaluate_rallies.py:265 save_evaluation

**Hypothesized cause:** Comparison schema is inferred from the first row rather than defined independently.

**Alternative explanations:** A no-GT benchmark may intentionally be unsupported, but that constraint is not enforced.

**Confidence:** high

**Causal experiment:** Call save_evaluation in a temporary directory with empty GT and prediction inputs, then assert a header; not needed to explain the36-label baseline.

**Proposed action:** Optional future evaluator hardening: fixed comparison schema/header for empty inputs, without changing matching.

**Expected metric effect:** None on Test1; improves artifact robustness only.

**Regression risk:** Low if limited to empty export behavior; do not bundle with matching-policy changes.

## Runtime/provenance limitations and acceptance

Recorded total inference time1469.237seconds implies11.753processedframes/second over17268frames. This elapsed interval covers production ingest/analysis, not source download, all audits or post-reporting. The frozen inference record does not provide per-stage time, peak GPU memory or a CPU utilization series. Hardware capacity is not measured peak usage; absent metrics must remain unavailable. Future experiments should instrument those signals without inventing baseline values.

Baseline publication separated initial evaluator code from additive final reporting fields. The archived execution scripts, final-script hashes and production hashes make this explicit. The legacy helper's null shuttle inspection is independently contradicted by the actual loaded component runtime and execution log (CUDA FP16); it is a reporting wrapper limitation, not evidence that shuttle inference did not run.

Accept an experimental change only with unchanged seven-column semantics and matching, complete prediction/event provenance, full-video metrics, severe-outlier review, FP/FN accounting and separate raw-observation/segmentation experiments. Retain these current baseline numbers. Test1 remains exploratory development evidence; no held-out generalization is established.
