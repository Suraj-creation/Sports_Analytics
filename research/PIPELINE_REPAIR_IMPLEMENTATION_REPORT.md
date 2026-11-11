# Pipeline repair implementation report

**Final scope clarification:** the user requested Video2 only. Completed additional local-video checks are preserved as incidental historical context. The extra amateur run was interrupted and is not a completed benchmark. No further video inference is running. The additional Video2 repeat was not performed: preparation timed out during its300second FFprobe count before a new plan or NN run was created. The original full fresh Video2 run, independent completion proof, unchanged evaluation and failure analysis are complete. Nothing was deleted.

The repair branch is `repair/pipeline-generalization-20261105`, based on HEAD `caa91761948d09f2cfe4937b0db743fff8643a12`. The implementation includes uncommitted source changes; that commit alone does not reproduce it. All 26 inherited modified/untracked files were preserved in the [baseline archive and hash receipt](../../pipeline-repair-runs-20261105/baseline/state.json). Historical videos, annotations, model weights and accepted experiments were retained. The five Test2 reports and the full architecture blueprint informed this investigation; actual source and measured hardware take precedence over historical architecture estimates.

**Fresh Test1 and Test2 analysis is complete and independently verified.** Both original workers failed only while publishing a codec21 catalogue through an older codec20 allowlist, after writing their analysed sessions, complete caches, events, predictions and stage samples. Separate post-hoc proofs verify all actual frames and preserve both original failed receipts; no inference.json or predictions were synthesized. Test1/Test2 remain exposed development/validation material, and their legacy references are not independently reviewed physical-contact or boundary truth. A second fresh neural run of the latest Test2 profile was **NOT PERFORMED**: its preparation attempt timed out during FFprobe frame counting after300seconds, before a new manifest or NN execution. The user then restricted scope to the existing Video2 evaluation and cleanup inventory. Whole latest-profile NN repeatability remains unvalidated.

## Implemented behavior

| Area | Actual change | Evidence and limits |
|---|---|---|
| Startup format | `engine.py` preserves an existing temporal candidate, identity state and coordinate epoch when unknown format becomes the compatible existing format. `plugin.py` avoids resetting player tracking for that compatible confirmation. Real discipline changes still reset context. Rule eligibility is bound to the rally's origin, preventing retrospective official scoring of unknown-origin activity. | Focused format/epoch/outcome regressions. Controlled Test2 starts at82 rather than101; its unknown-origin rally retains `match_format_known=false`. Preparation at legacy reference53 is not established as missed play. |
| Contact admission | An optional typed `on_contact_evidence` rally port separates temporal admission from physical impact reliability. All upstream contact candidates remain in the event/evidence chain, including rejected admission decisions. Explicit invalid/rejected evidence cannot open or renew a candidate. | Ambiguous/insufficient impact is not a negative physical label. The experimental stationary-rest veto remains disabled after adverse controls; ordinary missing-shuttle gaps preserve weak contact behavior. |
| Stationary recovery | CLOSED stationary recovery uses the existing `resume_speed` while the interval remains mergeable, matching ENDING behavior. Once that window expires, a new idle launch retains `start_speed`. | Reproduced slow-pickup reopening and expiry-boundary defect. No global timeout, minimum duration or numerical threshold was changed. Recorded-observation Test2 control retains67/6/6 TP/FP/FN and reduces end MAE21.627→21.104 frames; Test1 intervals remain unchanged. This control is not fresh inference. |
| Short exchanges | `events/exchange_evidence.py` and `rally_evidence.py` add explicit opt-in admission requiring observed moving-start frames, disjoint actual shuttle motion windows, at least one probable/confirmed trajectory or impact assessment, and simultaneous fresh detector-matched opposite-court episodes in both local contact contexts. Episode birth IDs/tracks and `(shot,content,coordinate)` epoch must agree. Candidate motion must be inside its own start boundary. | Distinct anonymous keys alone, shared tracks/births, carried boxes, changed epochs, same-side actors and absent coobservation cannot satisfy the proof. The engine builds bounded source context and retains exact proof in `rally_end.payload.rally_admission`. It asserts no named identity, team, serve, winner or official point. Defaults remain off. |
| Scene decisions | Experimental `foreground-content-continuity-v2/barrier_detector_layout_v2` retains the existing v1 raw image observer. A raw change triggers a source-bound RF-DETR probe on the actual current image before tracker mutation. Complete unique2–4-person layout correspondence suppresses the reset; a disjoint layout corroborates it. Missing/ambiguous evidence records unknown and preserves the prior raw-reset fallback. | Reuses the existing0.3 box-IoU continuity gate. On51 historical candidate frames, fresh detector-only probes retain all13 Test1 resets and36/38 Test2 resets, suppressing source-supported false resets7703/23639. This is candidate-level diagnosis, not full-video scene accuracy. Missed edit11346 remains unresolved. |
| Player acquisition | `players.py` exposes detached detector probes bound to frame, BGR-image SHA256/shape, boxes, supports, crop and admitted indices; normal tracking consumes the probe once. A cut forces current detection on the next enabled step even off normal cadence. | Reproduced the prior odd-frame empty-carry defect. Tests cover source mismatch, reuse, no tracker advance, two/four participants and disabled detection. Fresh pose inference on a propagated box remains distinct from a fresh detector association. |
| Provenance/cache | Codec21 stores scene decision evidence separately from raw appearance hypotheses. Constructors and cache readers bind raw frame/hypothesis/region count, producer detector model, image dimensions, bounds and recomputed0.3-IoU matching pairs. Mandatory decisions for the selected policy cannot silently disappear. | Older diagnostic cache reads retain unknown decision provenance. Missing legacy epoch metadata and opaque synthetic isolation metadata preserve explicit compatibility; no scene decision is invented. Sport pipeline contract is4 and rally component contract2. |
| OCR | Spatial ownership associates numbers with the nearest compatible athlete-label row and aligned current-score columns, preventing a logo from borrowing another row's scores. Missing digits cause abstention. Parser policy `nearest-name-current-column-v2` enters runtime/model identity. Optional explicit thread count is validated against actual ORT sessions. | No athlete blacklist, frame exception, score repair, checkpoint, preprocessing or OCR threshold change. A real Test2 missing top score remains missing. CPU OCR is selected only in the experimental profile. |
| Execution/measurement | The generic complete-upload harness validates actual decoded count, verified CFR and unchanged proxy FPS, freezes source/config/input hashes, and starts clean sessions through the real `SessionRunner`. Own-cache replay binds completed worker reports, source models/configuration, cache catalogues and exact output digests. Timing observes existing stage scopes; worker-tree CPU/RSS and physical GPU UUID/PID samples are separate. | No reference-window or annotation argument enters the upload worker. VFR/rate conversion requires an explicit map and is rejected by this executor. Stage wall times overlap and cannot be summed as kernel latency. Timestamp/tail completion and actual execution providers still require post-run verification. |

Source modules and regressions are included in each protocol's `executed_source/` snapshot and hash catalogue. Detailed component evidence is in the [temporal report](../../pipeline-repair-runs-20261105/temporal_mechanism_review_v1/REPORT.md), [scene report](../../pipeline-repair-runs-20261105/SCENE_REPAIR_REPORT.md) and [OCR report](../../pipeline-repair-runs-20261105/OCR_REPAIR_REPORT_v2.md).

## Selected experimental profile and bindings

[experimental-pipeline-repair-v1.yaml](../config/profiles/experimental-pipeline-repair-v1.yaml) was selected before fresh predictions; its source SHA256 is `280cbf717568fa2a7a1c3b476921bac1b48e9958bf65be0469fae7b5b2dae756`. The [selection receipt](../artifacts/benchmarking/experiments/pipeline_repair_20261105_v1/profile_selection.json) records the rationale and rejects automatic production promotion.

The profile retains TrackNetV3 FP16, threshold0.5, vertical flight columns, existing coobserved-static association and `rally-evidence-tracklets-v1` with reconstruction=false, motion_guard=false, exit_recovery=true, curve_exit=false. It explicitly selects short_exchange_evidence=true, terminal_contact_evidence=false, detector-layout scene policy and CPU RapidOCR with package default threading. RF-DETR and RTMPose are declared FP32 to describe their unchanged actual ONNX graphs. Pose/racket/shot/official-phase evidence requirements remain enforced.

Each plan binds286 source/helper/API/frontend files, the session and source video, exact effective YAML, model manifest and model lock; it stores an executed-source snapshot. Only passive diagnostic ranges are regenerated from input length:120 evenly spaced30-frame windows, at most3600frames. Full raw/association evidence remains per frame. No annotation or failure-window selection determines those ranges.

| Frozen plan | Frames | Source SHA256 | Plan SHA256 |
|---|---:|---|---|
| [protocol_test1_v2](../../pipeline-repair-runs-20261105/protocol_test1_v2/plan.json) |17268|`877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`|`be66b6b14edbdb73018a339f6b349697a84fcf82a97f04258640a023c75c6788`|
| [protocol_test2_v2](../../pipeline-repair-runs-20261105/protocol_test2_v2/plan.json) |29296|`4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`|`04074b1d99c30e6f90b92991c7fd5fe55b0d2270ce0ed182458db19857b6a7b8`|
| [protocol_test7_v2](../../pipeline-repair-runs-20261105/protocol_test7_v2/plan.json) |10725|`1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c`|`3d7665d6a5c7fc3ee835847f902d94ad89e5cb1bde0de209099f6d5c284d1116`|

The bound model manifest SHA256 is `b5590b8ff1437945da036b42b01729f521728259a0dfc4c3299a926216ba8df3`; lock SHA256 is `fb3b69b8ff3224d6f7b647c68acb08ec4ed4ffec6c67e3acf6f08da485ff9966`. Locked checkpoints include TrackNetV3 `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`, RF-DETR small `fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e` and RTMPose `f7fbb6c5c11a1bb70f3d445e4ddec5d144ea89ad5649c081ef976f9b24a0b741`. The completed independent proofs verify staged/source/package artifacts and actual recorded execution metadata; configuration alone is not execution proof. Missing worker-local timings remain unavailable.

## Completed controls and rejected experiments

The [actual-engine semantic intervention](../../pipeline-repair-runs-20261105/semantic_test2_short_v2/replay_manifest.json) processes all29296 original cached perceptions with short admission enabled and terminal veto disabled. It yields75 predictions,68 TP,7 FP,5 FN, F1 `0.918918918918919`, against the unchanged legacy reference/matcher, compared with original73 predictions and67/6/6. This is **not fresh neural inference**, and it does not exercise changed scene perception or CPU OCR end to end.

The [independent source diagnostic review](../../pipeline-repair-runs-20261105/semantic_short_review_v1/REPORT.md) verifies output hashes, sampled exact original raw-cache parity, contact availability and disjoint shuttle samples. Added intervals11715–11751 and11873–11926 are retained with Unknown shot labels, unknown/nonofficial phase and no winner. The first remains an unmatched prediction against the longer legacy reference; endpoints were not padded. G63 is not admitted: far track1 disappears at24000 and returns as track2/new episode24004, so same-episode coobservation cannot be proven across contacts23968/24009. Source also shows floor-shuttle behavior near the second candidate. G58 same-target walking remains a negative control. This establishes technical behavior and diagnostic plausibility, not independently annotated physical accuracy.

All failed variants remain preserved. Broad contact gating worsened Test2 to62/9/11 TP/FP/FN. Stationary-only gating shortened plausible brief activities below the unchanged60-frame duration rule and remains unselected. Correspondence-only scene gating removed real Test1 edits10770/15579; cadence-history gating removed real Test2 edits4257/5174/14107. Neither is selected. G39/G55/G69 still expose missing or conflicting flight/association evidence; no coordinates, extra contacts or global timeout extensions were invented.

OCR component controls on25 fixed inputs preserve decoded text/boxes and all score rows/abstentions across CUDA/CPU. One confidence differs by1e-5; raw allclose1e-4 fails14/25 and all failures are retained. Shared-host p50 latency is8431ms CUDA,1388ms CPU4threads,658ms CPUauto. These measurements justify testing explicit CPU OCR on this host; they establish neither general backend equivalence nor full-pipeline speedup or score accuracy.

## Completed fresh analysis and failure recovery

| Metric | Fresh Test1 | Fresh Test2 |
|---|---:|---:|
| Complete frames |17268|29296|
| Predictions |36|75|
| TP / FP / FN |36 / 0 / 0|68 / 7 / 5|
| Precision / recall |1 / 1|0.906667 / 0.931507|
| F1 |1|0.918918919|
| Mean matched IoU |0.871025665|0.848134654|
| Start / end MAE, frames |28.25 / 10.4722|23.8824 / 21.1618|
| Duration MAE, seconds |1.11111|1.30245|

These use the unchanged one-to-one IoU0.5 evaluator and original legacy references. Against the original Test2 primary, detection changes from67/6/6 to68/7/5; the additional unmatched short interval is retained. Overall meanIoU regresses from0.849962266 to0.848134654. On the same67previously matched references it rises to0.851146492, a denominator diagnostic that does not replace the overall result. Test1 rally intervals/metrics retain the frozen latest baseline result.

[Fresh case review](../../pipeline-repair-runs-20261105/fresh_test2_case_review_v1/REPORT.md) maps all40old+39fresh significant cases into41stable records. Every one of79source-contract checks passes: complete source windows, raw-cache/trace identity, availability causality, observed-versus-interpolated evidence, provider/epoch links, actual coobserved short-proof rows/births, and named-actor/winner abstention. These are transport/evidence regression checks, not79physical boundary labels. Source diagnostics isolate six changed reference matches and one retained additional prediction. GT32is recovered; GT31/39/56/58/63remain unmatched. Current system phases and OCR outputs are not certified sporting truth.

G24illustrates an interaction beyond aggregate scores: suppressing false reset7703changes TrackNet's actual epoch-keyed background reservoir. CPU-only preparation replay reproduces420retained background hashes while source/proxy, calibration/camera, flight-mask recipe, TrackNet code/configuration and checkpoint remain equal. At8749the observed before-speed changes0.524844→0.451279pixels/frame, crossing the unchanged0.5static-contact gate; the old low-speed candidate disappears and end8751→8734. This is an observed input pathway, not evidence of random NN behavior or independently validated physical impact. No GPU forward, numerical threshold change or latest-profile NN repeat was used for this diagnosis.

The [Test1 completion report](../../pipeline-repair-runs-20261105/completion_test1_v1/REPORT.md) and [Test2 completion report](../../pipeline-repair-runs-20261105/completion_test2_v1/REPORT.md) bind original failed worker argv/source guards, committed session/event databases, exact original prediction CSVs, every cache, actual source/proxy rationalPTS including tails, and13/38scene-probe pixel hashes. The explicit strict recovery verifier preserves original `partial_or_failed` status and opens detached SQLite copies. A separate initial Test1 schema inspection created empty SQLite companions; their preservation and unchanged mainDB hashes across subsequent archival are recorded under sqlite_inspection_side_effects_v1. A pre-inspection mainDB hash was not captured. Lost worker initialization/staging time, exact worker inference elapsed, CPU total and peakRSS were not invented; failure-inclusive parent elapsed and sampled resources remain separate.

The catalogue defect was then fixed for future workers: codec20/21acceptance plus strict21Profile/model/scene-decision validation. Core models/profile were unchanged. Test7subsequently published an ordinary successful worker receipt under protocol_test7_v3; this report makes no Test7sporting-accuracy claim. Only the older original Test2profile has two full byte-identical NN executions already established. Latest-profile per-video own-cache parity verifies semantic reproducibility of retained observations, not neural repeatability; the latest-profile Test2NNrepeat was NOT PERFORMED (preparation timed out before a new plan; no NN repeat).

## Validation and reproduction

The [final suite log](../../pipeline-repair-runs-20261105/full_suite_v5.log) records **3151 passed,19 warnings in438.46s**. The earlier v3receipt records3053passed; v4had3143passes and one stale test expectation after the intentional codec allowlist upgrade. That test now snapshots the actual allowlist, verifies no mutation and uses a normalized valid Profile; all30completion tests and the687-test research group pass. Earlier red logs remain preserved. Focused contracts cover format eligibility, bounded recovery, optional short admission, participant fragmentation, detector probes/cadence, scene-decision cache tampering, OCR layouts/runtime and harness isolation. Earlier full-suite failures are retained: v1 had11 failures/3031passes from optional context with unavailable legacy epochs; v2 had1failure/3048passes from an opaque synthetic isolation identifier. Both compatibility defects were corrected without inventing missing provenance. The initial v1 protocol preparation also failed its old scene allowlist before NN execution; the corrected explicit v2 allowlist is covered by the final suite and focused113-test guard check.

Run from `Sports_Analytics`; source the existing GPU environment instead of resynchronizing dependencies:

```bash
source ../gpu-env.sh
.venv/bin/python -m pytest engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests tests/benchmarking -m 'not gpu and not network and not slow' -q
```

Recorded preparation pattern below creates the frozen `protocol_test{1,2,7}_v2` inputs. Existing directories are immutable; reproduction requires new protocol/output names rather than overwriting them.

```bash
repair_artifacts=/home/administrator/Desktop/sport-analytics/pipeline-repair-runs-20261105
.venv/bin/python research/production_external_stress.py prepare-upload --case test1 --video data/benchmarking/test1/Test1_Full_rev.mp4 --profile-source config/profiles/experimental-pipeline-repair-v1.yaml --output "$repair_artifacts/protocol_test1_v2"
.venv/bin/python research/production_external_stress.py prepare-upload --case test2 --video Part2/video_raw/Test2_Full_Rev.mp4 --profile-source config/profiles/experimental-pipeline-repair-v1.yaml --output "$repair_artifacts/protocol_test2_v2"
.venv/bin/python research/production_external_stress.py prepare-upload --case test7 --video data/task2-review/Test7_Full.mp4 --profile-source config/profiles/experimental-pipeline-repair-v1.yaml --output "$repair_artifacts/protocol_test7_v2"
```

Actual first fresh launch commands (analysis completed; original publication failures are retained):

```bash
.venv/bin/python research/production_external_stress.py run --plan "$repair_artifacts/protocol_test1_v2/plan.json" --case test1 --gpu-index 0 --output "$repair_artifacts/fresh_test1_v1"
.venv/bin/python research/production_external_stress.py run --plan "$repair_artifacts/protocol_test2_v2/plan.json" --case test2 --gpu-index 1 --output "$repair_artifacts/fresh_test2_v1"
```

The controller resolves physical GPU UUIDs, leases only its assigned GPU, validates frozen inputs before/after execution and records process resources separately. Test1/Test2 overlap on this host, which limits historical runtime comparisons. Test7first-stage protocol_test7_v2 remains historical; its successful fresh execution used protocol_test7_v3 after the catalogue-only fix. Test1/Test2 completion proofs, full frame/PTS checks, parity-bound traces and fresh scoring are now retained. The latest-profile Test2NNrepeat was NOT PERFORMED (preparation timed out before a new plan; no NN repeat); broader accuracy validation remains unresolved. Unmatched predictions, unresolved component accuracy and legacy-reference ambiguity remain visible.


The explicit recovery command is:

```bash
.venv/bin/python research/pipeline_repair_completion.py --plan "$repair_artifacts/protocol_test2_v2/plan.json" --case test2 --run "$repair_artifacts/fresh_test2_v1" --output "$repair_artifacts/completion_test2_v1"
```

Existing recovery outputs are exclusive-create. Initial recovery required current frozen source guards; later consumers explicitly call `verify_completion_receipt(run,recovery)` against original executed-source snapshots. This does not silently convert a failed original publication into a normal successful worker report.
