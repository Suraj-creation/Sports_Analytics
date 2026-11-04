# Next-session result — 2026-11-05

The selected experimental profile completed actual full-video production inference
with **36 TP, 0 FP, 0 FN**, start MAE **29.14 frames** and end MAE **10.33 frames**.
It repairs demonstrated upstream admission losses and makes previously discarded
perception evidence reviewable. It is **not recommended for production promotion**:
GT27's recovered continuity still depends on a suspect contact, same-camera edits
remain missed, fine onset accuracy is limited, and independent reviewed validation
is unavailable. These limitations are not closed by the perfect detection F1.

## Source, scope and preservation

Actual inference source is `33d3a5b1bcfd945555b76360cc361881e5a3eb8a` on
`Benchmarking`. Initial clean HEAD was `64d098b`; no historical reset, clean,
deployment change, dependency installation or unrelated job termination occurred.
Local `main` remains `301baf08be5e989dd0ed93cb885733c3cf6f356a`. The initial audit
read the complete handoff, inventory, mandatory reports and referenced evidence
before production changes. Original video, labels, model weights, baseline,
fresh-v1 and historical experiments remain immutable. New artifacts use distinct
`next_20261105_*` directories. The inventory retains handoff measurements and old
status strings alongside the new source-specific review.

The unchanged matcher, IoU threshold, zero-origin indexing, actual FPS conversion
and half-open seven-column export apply. No annotation value enters inference;
the parent evaluates only after the worker writes predictions. The measured
prediction count was not constrained to 36. This is Test1 development footage,
not held-out validation, live-mode evidence or reviewed component accuracy.

## Implemented and retained changes

1. An opt-in image-ceiling flight policy sweeps horizontally clipped visible
   court columns to the image top. It keeps floor/side admission and invalid-view
   gates. It fixes a demonstrated floor-derived mask rejecting source-visible
   high shuttle flight; it is not 3D airborne court ownership.
2. `rally-evidence-tracklets-v1` preserves the existing exit proof and adds one
   bounded singleton association alternative for events qualified **before**
   observation loss. It preserves the singleton's original coordinate and all
   contact inputs. No new point, idle start, merge timeout or global offset is
   introduced. The curve alternate remains available but disabled: it adds no
   result after the upstream mask correction.
3. Bounded optional codec18 telemetry captures raw/masked shuttle peaks, ranked
   connected components, rejection reasons, entropy, window/background provenance,
   detector queries/ROI rejections and fresh/carried tracking summaries. Legacy17
   remains diagnostic-readable; live sequential cache reuse remains prohibited.
   Component scores remain uncalibrated. The schema does not retain every local
   maximum or full heatmap, and unrecorded evidence remains unknown.
4. An independently injectable contact-reliability provider handles unresolved
   direction and absolute speed gain with explicit spatial/fit sensitivity,
   including zero-incoming weak-launch controls. Its earlier old-perception trial
   regressed GT27 and it is not selected. Contact attribution and contact-model
   provenance stay separate. The selected legacy scorer still has a proven
   numerical/association defect.
5. Empty comparison exports retain their header; matching and nonempty metrics
   are unchanged. Ablations bind executing source separately from trace source,
   derive recorded format epochs and refuse output reuse. New failure packages
   require exact cache/trace hashes and interval/end-reason multiplicities, use
   half-open overlap and preserve the executed packager bytes.

Generic host code and ordinary profiles are unchanged. The new provider and
experimental YAML are explicit opt-ins. Score, winner, stroke, team, identity,
four-player retention and independent plugin contracts remain in the software
validation scope. Their sporting accuracy is not inferred from rally results.

## Detection, boundaries and duration

| Metric | Frozen original | Fresh v1 | Selected fresh |
| --- | ---: | ---: | ---: |
| TP / FP / FN | 30 /19 /6 | 35 /4 /1 | 36 /0 /0 |
| Precision | 61.22% | 89.74% | 100% |
| Recall | 83.33% | 97.22% | 100% |
| F1 | 70.59% | 93.33% | 100% |
| Mean IoU | 0.763315 | 0.817808 | 0.867622 |
| Start MAE, frames | 49.43 | 45.77 | 29.14 |
| End MAE, frames | 40.40 | 16.31 | 10.33 |
| Duration MAE, seconds | 2.8456 | 1.8943 | 1.1324 |

| Selected error | MAE | RMSE | Median absolute | Signed bias | P90 absolute | Maximum absolute |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Start, frames | 29.1389 | 41.3673 | 21 | +22.75 | 69.5 | 106 |
| End, frames | 10.3333 | 14.3003 | 6 | −2.2778 | 22 | 41 |
| Duration, seconds | 1.1324 | 1.5477 | 0.6333 | −0.8343 | 2.7 | 4.0 |

Selected median/minimum IoU are 0.921529/0.538071. Percentages strictly exceeding
0.5/0.75/0.9/0.95 are 100/80.56/55.56/27.78%. GT15 remains close to the matching
threshold. Duration truncation is largest at GT9 (−4.0s), GT5 (−3.4s) and GT15
(−3.0333s); the early GT4 interval is 2.5667s too long.

| Tolerance, frames | Start within /36 | Start accuracy | End within /36 | End accuracy |
| --- | ---: | ---: | ---: | ---: |
| ±1 | 1 | 2.78% | 4 | 11.11% |
| ±3 | 5 | 13.89% | 9 | 25.00% |
| ±5 | 10 | 27.78% | 17 | 47.22% |
| ±10 | 15 | 41.67% | 23 | 63.89% |
| ±15 | 16 | 44.44% | 26 | 72.22% |
| ±30 | 25 | 69.44% | 34 | 94.44% |

Selected matched/all-GT denominators both equal 36. All reference metrics retain
their separate matched/all-GT denominators. On the **same 35 v1-matched rows**,
start/end MAE improve 45.7714→28.9429 and 16.3143→10.4286; no start, end or duration
error worsens. GT23 is newly matched, with no lost v1 recovery, including
GT2/19/20. On the same 30 original-matched rows, start/end MAE improve 49.4333→25.8667
and 40.4→10.8. Original-reference regressions remain GT4/22 starts, GT8/13/16 ends
and GT4/16/22 durations. Both references and every unmatched prediction remain
in the complete comparison; none is removed for difficulty.

The selected run has no unmatched prediction. GT22 ends 10737 and GT23 begins 10769;
they remain separate. GT22's four-frame tail overlaps the GT23 annotation, so the
geometric positive-overlap topology still flags two predictions touching GT23's
span. This is retained diagnostic topology, not proof that the later rally is
still split. Partial onset coverage and boundary ambiguity remain visible.

## Causal conclusions and rejected experiments

GT23's later loss contains an isolated competing observation, not only absent
coordinates. Qualified association recovers its later continuation and preserves
GT22. The missed 10769→10770 edit is physically distinct from that later gap;
its detection and the human pre-edit onset convention remain open.

GT31 contains16 above-threshold raw observations discarded by the finite old
mask, around 14647–14650 and 14683–14694. With admission repaired, the remaining
32-frame gap uses the ordinary existing top-exit proof. The retained start 14430
improves the assigned 14701 boundary without backdating into pickup close-up
footage. Missing/subthreshold frames are not filled with invented coordinates.

GT27 still locks onto the service T. The mask admits real earlier upper re-entry,
but the selected trace proposes end 12748 at 12757, closes 12763 and reopens through
suspect contact 12766. Removing only that selected contact, after unchanged
scoring/NMS, restores end 12748 and adds fragment 12772–12954; all other 35 GT rows
and every processed shuttle step are identical. Thus the apparent repair is
causally contact-dependent. Its T coordinate, zero swing/overlap, incoming speed
0.1247 and outgoing 122.1241 px/frame do not establish a physical impact. The
reliable-motion scorer reduces local support 0.7872→0.0359. H02/H10 remain open.

Unrestricted singleton association is rejected: GT7 becomes 81frames early,
although GT15 improves. Qualification before loss preserves the negative control
and deliberately leaves GT15 unresolved. Fixed-startup background removes all 24
T outputs in the reviewed block but fails to recover the real airborne track;
zero-background is not a separately trained background-free model. Neither is
selected merely for producing fewer points. The curve alternate's old-stream
gain is preserved as measured, but its new-mask result adds no benefit.

Foreground continuity exposes two histogram-missed same-camera edits,
10603→10604 and 10769→10770, against 1,246 inspected source pairs and fast-play
controls. No cut threshold is promoted without independently reviewed edits,
occlusion and fast-action negatives. GT4's high serve/feed before the label and
GT22's weak contact crossing an edit remain bounded early-start regressions.
No annotation was changed and the onset convention remains unknown.

## Freshness, runtime and evidence identity

The selected run is actual full production inference, not a cached replay. It
matches the hybrid prediction CSV byte-for-byte and every metric value, while
changed cadence alters player records on 2,045 frames, pose stride on 300 and
detector scheduling on 100. Fresh live contacts/strokes are 457 versus 454 in the
hybrid and 447 in v1. Shuttle coordinates/support match all 17,268 hybrid frames.
Contact timing accuracy remains unlabelled. The own-cache semantic replay also
matches all 36 interval/end-reason triples, prediction bytes, all 457 live contact
and stroke timestamps, all 288 cache hashes and its trace SHA.

Runtime is 1516.497 s, throughput 11.3868 frames/s. The independent v1 control took
1498.199 s; the 18.298 s difference is observed walltime, not isolated diagnostic or
algorithm cost. Short diagnostic CPU work overlapped startup (32.11 CPU-s before
being paused); all later tests/replays/probes began after this run completed.
Worker peak RSS is 2,871,062,528bytes; mean CPU463.29%; sampled peak PID GPU memory
2880 MiB; Torch peak allocation1,133,421,056bytes. CPU/RSS exclude child-process
usage, GPU samples are not instantaneous maxima, and Torch excludes ORT.

| Wall aggregate | Seconds |
| --- | ---: |
| Media ready | 1.440 |
| Decode/perception/cache parent | 1311.462 |
| Court/scene wrapper | 107.695 |
| Perception court | 101.818 |
| Perception shuttle | 217.930 |
| Perception players/pose | 544.700 |
| Perception OCR | 333.675 |
| Semantic ingest | 83.243 |

These parent/child aggregates overlap and must not be summed. Actual hardware
is GTX1080Ti, not the RTX4000 profile name. TrackNet records CUDA0/torch.float16
with no fallback; RF-DETR/pose/OCR sessions record CUDA and CPU providers without
fallback. Per-node ORT placement and precision are not measured by that list.
OSNet/ReID remains unavailable and named actors remain unknown. Model hashes,
source hashes, exact configuration, resources and backend records remain in
the selected run's `benchmark_metadata.json`, `inference.json` and resources log.

## Validation, artifacts and disposition

Release checks passed 1,966 application/engine/sport tests and 77 benchmark tests
(2,043 combined), with 19 existing deprecation warnings. The default pytest paths
exclude the benchmark directory, so its 77 tests were explicitly run separately.
The provenance packager has 12 failing pre-fix controls and 14 passing post-fix
controls. Fifteen additional research diagnostic/identity controls pass.
`next_session_validation_matrix.md` maps each required stress
class to executed tests and states the real-evidence limits. Each H01–H28 entry
receives a source-specific conclusion, evidence, limitation and next experiment;
none is marked fixed solely by an aggregate score.

Primary run: `artifacts/benchmarking/experiments/next_20261105_fresh_air_tracklet_v1/`.
Own semantic trace: `next_20261105_fresh_air_tracklet_semantic/`.
All 36 causal firsts/end chains and synchronized source-frame replay use that run's
own observations. The full results JSON includes both references, all 36 row
coordinates/errors/durations, every unmatched prediction, fixed-common metrics,
IoU distributions, topology, models, resources, test logs and experiment catalog.

Keep the profile experimental. The next substantive work is trustworthy
static-versus-flight association, contact/terminal validation and scene authority,
followed by reviewed onset conventions and match-disjoint validation. A geometric
static-cluster counterfactual must remain ambiguous when a floor-stop/fresh-launch
alternative is indistinguishable; it must not silently relabel observed points as
missing or join separate rallies. Live causality, generic VFR mapping, HLS seeking,
rollback scaling and real doubles accuracy remain unvalidated in this session.


## Supplemental source-bound controls

Both additional rolling-only onset probes reproduce accepted coordinates and raw
support literally, with maximum absolute difference 0 over 1,197 and 1,779 frames.
Combining their separately labelled component evidence with own-cache telemetry
gives 5,081 distinct diagnostic frames and 100% diagnostic coverage of all 36 onset
review windows. The latest model/temporal firsts table is in
`next_20261105_fresh_air_tracklet_all36_model_firsts_v2/`.

Original-frame review of the six earlier strong rejected peaks at GT6/9/13/14/16/31
finds excluded player close-ups and lost geometry. They do not justify earlier
sporting onsets or broader admission. GT28 differs: frame 13054 is a wide court with a
source-visible upper streak and accepted provider point, but REACQUIRING geometry
invalidates the first two processed samples. Later visibility is lost until 13112.
This needs separate image-versus-floor-geometry validity controls.

The direct unique-contact control uses the actual selected fresh run's own caches:
496 selected callbacks become 495; 457 live contacts become 456, only 12766 is removed,
and all other scores/coordinates/models, all 17,268 steps and all other 35 GT rows
are identical. GT27 returns to end 12748 and adds fragment 12772–12954. The new-mask
reliable-contact interaction also fragments GT27: 36 TP / 1 FP / 0 FN, 154 estimated contacts,
end MAE 16.667 frames. It is rejected despite improving GT4/22 starts.

The static-cluster observer examines 916 actual available-window/control frames
without changing observations or predictions. At the prespecified one-cell radius
it finds zero qualifying alternatives: T-centroid outliers break the assumed
single compact cluster. No radius widening, outlier deletion or automatic
continuity adoption follows. The simple hypothesis is rejected.

Final integrity passes 2,174 checks, including all 1,766 frozen files, 86 historical
source blobs and all 28 historical metric objects. Every original inventory field,
evidence item, control and old status remains preserved.

New evidence under `artifacts/benchmarking/experiments/`:

- `next_20261105_fresh_air_tracklet_all36_model_firsts_v2/all36_model_temporal_firsts.md`
- `next_20261105_temporal_source_onset_review/review.json`
- `next_20261105_fresh_air_tracklet_replay/index.html` (1,796 exact-PTS frames)
- `next_20261105_fresh_remaining_onsets_probe_replay/index.html` (1,197 frames)
- `next_20261105_fresh_other_onsets_probe_replay/index.html` (1,779 frames)
- `next_20261105_fresh_air_tracklet_v1/failure_cases/index.json` (36 cases)
- `next_20261105_fresh_contact12766_suppressed/causal_parity_validation.json`
- `next_20261105_fresh_mask_reliable_contact_replay/`
- `next_20261105_final_comparison/results.json` and exact reporting-source snapshots
- `next_20261105_final_integrity/validation.json`

## Complete row and reference comparison

All intervals below are half-open canonical frames. Conditional error statistics
use IoU-qualified matches. Unmatched rows have no invented boundary error; their
detection misses and all-GT tolerance denominators remain separate.

| GT | GT interval | Selected interval | Start/end error | IoU | Duration error s |
| --- | --- | --- | --- | --- | --- |
| 1 | 243–715 | 264–717 | +21/+2 | 0.951477 | -0.6333 |
| 2 | 887–1262 | 890–1255 | +3/-7 | 0.973333 | -0.3333 |
| 3 | 1398–1664 | 1402–1659 | +4/-5 | 0.966165 | -0.3000 |
| 4 | 1874–2161 | 1803–2167 | -71/+6 | 0.788462 | +2.5667 |
| 5 | 2210–2500 | 2308–2496 | +98/-4 | 0.648276 | -3.4000 |
| 6 | 2558–2806 | 2578–2799 | +20/-7 | 0.891129 | -0.9000 |
| 7 | 2976–3377 | 2977–3377 | +1/+0 | 0.997506 | -0.0333 |
| 8 | 3451–3695 | 3519–3699 | +68/+4 | 0.709677 | -2.1333 |
| 9 | 3751–4073 | 3857–4059 | +106/-14 | 0.627329 | -4.0000 |
| 10 | 4247–4839 | 4272–4804 | +25/-35 | 0.898649 | -2.0000 |
| 11 | 4872–5045 | 4901–5027 | +29/-18 | 0.728324 | -1.5667 |
| 12 | 5430–5871 | 5455–5887 | +25/+16 | 0.910284 | -0.3000 |
| 13 | 5958–6312 | 5979–6315 | +21/+3 | 0.932773 | -0.6000 |
| 14 | 6382–6656 | 6450–6639 | +68/-17 | 0.689781 | -2.8333 |
| 15 | 6716–6913 | 6802–6908 | +86/-5 | 0.538071 | -3.0333 |
| 16 | 6976–7458 | 7006–7499 | +30/+41 | 0.864245 | +0.3667 |
| 17 | 7532–7741 | 7535–7731 | +3/-10 | 0.937799 | -0.4333 |
| 18 | 7947–8053 | 7953–8052 | +6/-1 | 0.933962 | -0.2333 |
| 19 | 8106–8628 | 8110–8627 | +4/-1 | 0.990421 | -0.1667 |
| 20 | 8683–9967 | 8715–9947 | +32/-20 | 0.959502 | -1.7333 |
| 21 | 10245–10563 | 10250–10539 | +5/-24 | 0.908805 | -0.9667 |
| 22 | 10607–10708 | 10578–10737 | -29/+29 | 0.635220 | +1.9333 |
| 23 | 10733–11078 | 10769–11085 | +36/+7 | 0.877841 | -0.9667 |
| 24 | 11271–11392 | 11274–11397 | +3/+5 | 0.936508 | +0.0667 |
| 25 | 11568–11865 | 11613–11867 | +45/+2 | 0.842809 | -1.4333 |
| 26 | 11976–12197 | 11982–12196 | +6/-1 | 0.968326 | -0.2333 |
| 27 | 12451–12966 | 12455–12954 | +4/-12 | 0.968932 | -0.5333 |
| 28 | 13054–13442 | 13115–13439 | +61/-3 | 0.835052 | -2.1333 |
| 29 | 13679–13994 | 13686–13982 | +7/-12 | 0.939683 | -0.6333 |
| 30 | 14219–14335 | 14222–14331 | +3/-4 | 0.939655 | -0.2333 |
| 31 | 14404–15151 | 14430–15171 | +26/+20 | 0.940026 | -0.2000 |
| 32 | 15350–15535 | 15354–15529 | +4/-6 | 0.945946 | -0.3333 |
| 33 | 15596–15946 | 15664–15951 | +68/+5 | 0.794366 | -2.1000 |
| 34 | 15998–16387 | 15983–16385 | -15/-2 | 0.957921 | +0.4333 |
| 35 | 16513–17026 | 16521–17031 | +8/+5 | 0.974903 | -0.1000 |
| 36 | 17066–17226 | 17074–17207 | +8/-19 | 0.831250 | -0.9000 |

Signed start/end errors for both immutable references:

| GT | Original | Fresh v1 | Selected fresh |
| --- | --- | --- | --- |
| 1 | 96/2 | 96/2 | 21/2 |
| 2 | 179/-7 | 4/-7 | 3/-7 |
| 3 | 4/-103 | 4/-5 | 4/-5 |
| 4 | 15/6 | -71/6 | -71/6 |
| 5 | None/None | 99/-4 | 98/-4 |
| 6 | 103/-7 | 103/-7 | 20/-7 |
| 7 | 7/0 | 7/0 | 1/0 |
| 8 | 72/3 | 72/4 | 68/4 |
| 9 | 112/-14 | 112/-14 | 106/-14 |
| 10 | 97/-111 | 97/-35 | 25/-35 |
| 11 | 29/-18 | 29/-18 | 29/-18 |
| 12 | 25/16 | 25/16 | 25/16 |
| 13 | 21/-2 | 21/3 | 21/3 |
| 14 | 69/-17 | 69/-17 | 68/-17 |
| 15 | 87/-5 | 87/-5 | 86/-5 |
| 16 | 30/39 | 30/41 | 30/41 |
| 17 | 3/-10 | 3/-10 | 3/-10 |
| 18 | 6/-1 | 6/-1 | 6/-1 |
| 19 | 202/-1 | 4/-1 | 4/-1 |
| 20 | 32/-442 | 32/-20 | 32/-20 |
| 21 | 5/-24 | 5/-24 | 5/-24 |
| 22 | -6/29 | -29/29 | -29/29 |
| 23 | None/None | None/None | 36/7 |
| 24 | 3/5 | 3/5 | 3/5 |
| 25 | None/None | 45/2 | 45/2 |
| 26 | 70/-1 | 70/-1 | 6/-1 |
| 27 | 4/-218 | 4/-218 | 4/-12 |
| 28 | None/None | 61/-3 | 61/-3 |
| 29 | None/None | 7/-12 | 7/-12 |
| 30 | 3/-4 | 3/-4 | 3/-4 |
| 31 | None/None | 297/20 | 26/20 |
| 32 | 4/-6 | 4/-6 | 4/-6 |
| 33 | 168/5 | 72/5 | 68/5 |
| 34 | -15/-2 | -15/-2 | -15/-2 |
| 35 | 8/-92 | 8/5 | 8/5 |
| 36 | 8/-22 | 8/-19 | 8/-19 |

Start tolerances: each cell is count / matched denominator; matched accuracy / all 36 accuracy.

| Frames | Original | Fresh v1 | Selected fresh |
| --- | --- | --- | --- |
| ±1 | 0/30; 0.00% / 0.00% | 0/35; 0.00% / 0.00% | 1/36; 2.78% / 2.78% |
| ±3 | 3/30; 10.00% / 8.33% | 3/35; 8.57% / 8.33% | 5/36; 13.89% / 13.89% |
| ±5 | 7/30; 23.33% / 19.44% | 9/35; 25.71% / 25.00% | 10/36; 27.78% / 27.78% |
| ±10 | 12/30; 40.00% / 33.33% | 14/35; 40.00% / 38.89% | 15/36; 41.67% / 41.67% |
| ±15 | 14/30; 46.67% / 38.89% | 15/35; 42.86% / 41.67% | 16/36; 44.44% / 44.44% |
| ±30 | 18/30; 60.00% / 50.00% | 20/35; 57.14% / 55.56% | 25/36; 69.44% / 69.44% |

End tolerances: each cell is count / matched denominator; matched accuracy / all 36 accuracy.

| Frames | Original | Fresh v1 | Selected fresh |
| --- | --- | --- | --- |
| ±1 | 4/30; 13.33% / 11.11% | 4/35; 11.43% / 11.11% | 4/36; 11.11% / 11.11% |
| ±3 | 8/30; 26.67% / 22.22% | 9/35; 25.71% / 25.00% | 9/36; 25.00% / 25.00% |
| ±5 | 12/30; 40.00% / 33.33% | 17/35; 48.57% / 47.22% | 17/36; 47.22% / 47.22% |
| ±10 | 17/30; 56.67% / 47.22% | 22/35; 62.86% / 61.11% | 23/36; 63.89% / 63.89% |
| ±15 | 18/30; 60.00% / 50.00% | 24/35; 68.57% / 66.67% | 26/36; 72.22% / 72.22% |
| ±30 | 24/30; 80.00% / 66.67% | 32/35; 91.43% / 88.89% | 34/36; 94.44% / 94.44% |

All unmatched predictions under the unchanged matcher:

| Run | Prediction | Start | End |
| --- | --- | --- | --- |
| original | 2 | 891 | 1023 |
| original | 5 | 1585 | 1654 |
| original | 7 | 2309 | 2423 |
| original | 21 | 8110 | 8266 |
| original | 24 | 9548 | 9646 |
| original | 25 | 9685 | 9947 |
| original | 28 | 10769 | 10908 |
| original | 29 | 10949 | 11085 |
| original | 31 | 11634 | 11745 |
| original | 32 | 11801 | 11867 |
| original | 35 | 12771 | 12954 |
| original | 36 | 13176 | 13252 |
| original | 37 | 13273 | 13439 |
| original | 38 | 13686 | 13843 |
| original | 39 | 13883 | 13982 |
| original | 41 | 14491 | 14646 |
| original | 42 | 14701 | 14969 |
| original | 43 | 14994 | 15171 |
| original | 45 | 15668 | 15735 |
| fresh_v1 | 23 | 10769 | 10908 |
| fresh_v1 | 24 | 10949 | 11085 |
| fresh_v1 | 29 | 12771 | 12954 |
| fresh_v1 | 33 | 14430 | 14646 |
| selected_fresh | none | — | — |

Complete reference boundary/duration distributions, IoU distributions and geometric topology
are retained in `next_session_experiment_results.json`; the unchanged primary evaluator metrics
remain in each immutable run. GT-dependent union coverage is offline diagnosis only.

## Reproduction and completion limits

```bash
source ../gpu-env.sh
CUDA_VISIBLE_DEVICES=0 python research/run_pipeline_experiment.py \
  --output artifacts/benchmarking/experiments/NEW_fresh_air_tracklet \
  --rally-implementation rally-evidence-tracklets-v1 \
  --rally-params '{"use_reconstruction":false,"motion_guard":false,"use_exit_recovery":true,"use_curve_exit":false}' \
  --shuttle-params '{"flight_region":"vertical_columns_to_image_top_v1","diagnostics":{"ranges":[[1770,2175],[3000,3119],[10560,11099],[12420,12979],[14380,14719],[15090,15190],[15360,15479]],"top_k":5,"candidate_floor":0.1}}'
```

The selected run stores its
exact YAML, seven diagnostic ranges, model/source hashes and launch log.
`research/next_session_results.py --run COMPLETED_RUN --output NEW_DIRECTORY`
recreates the complete comparison with exact reporting-source snapshots.
All wrappers refuse existing output paths. Historical fixed-path finalizers were not run.

All 28 issues have truthful dispositions; accepted code defects have tests; all 36
causal/boundary comparisons and fresh own-evidence packages are delivered. Contact
reliability, terminal validity and scene authority remain open requirements. No claim
is made that every mission reliability criterion is satisfied. Continued experimentation
is appropriate; production/default promotion is not.
