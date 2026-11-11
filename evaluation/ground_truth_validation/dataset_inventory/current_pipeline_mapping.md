# Current pipeline, baseline execution and diagnostic mapping

Read-only inspection of the actual working checkout on 10 November 2026. No inference, model fetch, production change, annotation conversion or label adjudication was performed in this review. Machine-readable hashes/configuration are in `current_pipeline_mapping.json`.

## Current source is the source to execute

The checkout is on `repair/pipeline-generalization-20261105`, HEAD `caa91761948d09f2cfe4937b0db743fff8643a12`, with substantial inherited modified and untracked implementation files. The commit alone does not reproduce the pipeline. All **289** source/helper/profile/model-manifest/model-lock paths in the former sequential benchmark's `frozen_pipeline.json` still exist and match their prior hashes. Therefore the latest current implementation presently equals the prior improved implementation for that recorded set. This does not authorize substituting historical inference for the user’s requested fresh baseline.

Use the **current working files**, capture their exact hashes and executed-source copies in a new plan, and preserve the user's dirty state. The old frozen inventory is a comparison reference only. Preserve a full dirty diff/untracked manifest before any proposed fix. The selected existing profile is `config/profiles/experimental-pipeline-repair-v1.yaml` (SHA256 `280cbf717568fa2a7a1c3b476921bac1b48e9958bf65be0469fae7b5b2dae756`), which carries the actual improved rally/scene/OCR selections. Its old diagnostic ranges are input-independent telemetry settings; the existing preparation method regenerates passive ranges from actual new source length.

## Actual stage implementation and evidence

| Stage | Current implementation / configuration | Output and diagnostic evidence | Evaluation gate |
|---|---|---|---|
| Ingestion/media | Real upload `SessionRunner`, source probe, CFR source→720p proxy/HLS | Source/proxy SHA256, decoded population, rational PTS, session frontier | Entire decoded count, identity source/proxy PTS and last-frame coverage before metrics |
| Court/calibration | Actual keyframe seeding and court-line calibration; ongoing camera/calibration states | Calibration events, camera and player projection tracks, cache calibration state | Court JSON point order/source dimensions/time applicability must be established before geometric comparison; floor homography is not airborne 3D truth |
| Scene/content continuity | `foreground-content-continuity-v2`, `barrier_detector_layout_v2` | Per-frame epochs, raw hypotheses, detached detector probes, veto/barrier reasons, exact BGR source hashes | Scene counts are telemetry, not labelled cut precision/recall |
| Player detection | RF-DETR small ONNX, CUDA provider, actual FP32 graph, threshold0.35, court ROI | Current matched detections versus propagated boxes, anonymous tracks and per-frame person observations | Independent exhaustive boxes and image coordinate mapping required for AP/mAP; generated detection CSV supports diagnostic agreement only until provenance established |
| Tracking/identity | `court-player-episodes-v1` / recorded ByteTrack episodes; explicit format handling | Episode IDs, track exports, identity ambiguity/degradation | OSNet/ReID unavailability must remain recorded, not suppressed; reviewed cross-frame identities needed for IDF1/HOTA/switch claims |
| Pose | RTMPose-M body7 ONNX, CUDA provider, actual FP32 | Current-source pose rows and pose-on-propagated-box distinction | Need actual reviewed joints/visibility and joint convention for PCK/OKS; bbox presence is not pose accuracy |
| Shuttle | TrackNetV3 CUDA FP16, sequence8, background concat, threshold0.5, step8, vertical flight region | Raw observations, candidates, association reasons and output trajectory; full raw observations plus bounded peak diagnostics | Distinguish observed, missing, interpolated/filled and associated samples; verify coordinate/time source and generated-versus-human trajectory provenance |
| Shuttle association | `coobserved-static-hypotheses-v1` | Competing candidates, selected observation and association abstention | A model-produced filled CSV cannot automatically certify physical localization precision/recall |
| Racket | Existing `racket_geometry_v1` OpenCV geometry | Current-source racket rows, source frame and support | Learned racketvision model is absent; geometry still runs. Reviewed racket/contact labels required for accuracy |
| Contact | `contact-evidence-v1` / fusion evidence; sigma0.7216878364870323 | All candidates, impact/trajectory status, fresh-player/pose/racket gates, attribution reasons | Timing tolerance and exhaustive independent physical contact labels required; emitted contact candidates are predictions |
| Stroke | `stroke-rules-v0`; classifier families and explicit unknown | Stroke labels, unknown/missing evidence, linked contacts | One `ball_types` value per rally is not exhaustive per-shot labels. BST is explicit singles shadow only, not silently active |
| Rally | `rally-evidence-tracklets-v1`; exit recovery and short-exchange evidence on; reconstruction/motion guard/curve exit/terminal-contact evidence off | Exact `rally_end` export, bounded FSM trace, short-admission witnesses | Existing unchanged one-to-one IoU≥0.5 comparator; separate supplied exact and coarse reference families |
| Outcome/score | Actual engine rules, format, observed OCR, eligibility and unknown outcomes | Winner/official flag, observed score, candidate transitions, unknowns and rejected evidence | Resolve symbolic A/B↔actual athlete/team mapping and source-bound point correspondence before outcome or score accuracy |
| OCR | RapidOCR3.10.0, explicit ONNX CPU; `nearest-name-current-column-v2`; one-second cadence | Boxes/text/confidence and parsed row/score output; recorded model hashes | Text/row acquisition and accepted scoring are distinct; provider labels do not certify correctness |
| Analytics | Actual canonical event+track rebuild in `BadmintonSession.analytics()` | Rally/shot/score fold, anonymous presence/movement and identity coverage | Compare only supported labelled quantities; unknown identities cannot become named player statistics |
| Highlights | Actual analytics fold `highlights(k=12)` and emitted highlight evidence | Highlight bounds and same-session supporting event IDs | Reference membership/bounds can be checked; highlight relevance/importance accuracy needs labels |

The plugin explicitly declares pipeline version4 and the stage graph `perception→format/identity→activity/contact→rally→stroke/outcome/scoring→analytics`. The real runner's `_analyse()` seeds calibration, processes every sequential chunk, publishes tracks, ingests the engine, flushes, and invokes `self.sport.analytics()` on completion. Thus the full upload harness does not merely run a detached rally classifier. However, its final `inference.json` does not itself serialize the full API analytics JSON or rendered highlight video: explicitly export those after completion to keep them reviewable.

### Model availability

Current core files exist: TrackNetV3 `df867641…`, RF-DETR small `fcd3c3c4…`, RTMPose-M archive `f7fbb6c5…`; full pins are in the companion JSON. Requested optional model directories `osnet_ain_x0_25`, `racketvision_balltrack`, `wasb_badminton` are absent. Preserve the actual resulting unavailable/unknown/fallback reports. Do not silently disable components or claim these weights ran. Any later model adoption needs separate source, weight and data licence verification plus a before/after controlled test, and must not be smuggled into the baseline.

## Fresh Test1 baseline commands

Run from the existing GPU checkout after `source ../gpu-env.sh`; use `.venv/bin/python` without dependency resynchronisation. Test1 original already exists at `data/benchmarking/test1/Test1_Full_rev.mp4`; historical recorded SHA256 is `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`, decoded count17268, CFR30. Verify current bytes/probe rather than re-download a duplicate. New output paths must not exist and must be outside the repo: the existing harness’s `validate_output(...,[ROOT])` deliberately rejects an in-repository run directory. The requested workspace can contain metadata and links to external raw run artifacts.

```bash
source ../gpu-env.sh
.venv/bin/python research/production_external_stress.py prepare-upload \
  --case test1 --video data/benchmarking/test1/Test1_Full_rev.mp4 \
  --profile-source config/profiles/experimental-pipeline-repair-v1.yaml \
  --output ../ground-truth-validation-runs-20261110/test01_baseline_protocol_v1
.venv/bin/python research/production_external_stress.py run \
  --case test1 --plan ../ground-truth-validation-runs-20261110/test01_baseline_protocol_v1/plan.json \
  --output ../ground-truth-validation-runs-20261110/test01_baseline_run_v1 --gpu-index 1
```

GPU index is an allocation choice; inspect free resources and respect the existing lease mechanism/unrelated jobs. A frame-count deadline exception must be recorded separately from inference configuration; Test10 historically required340s versus a300s cap, while Test1 is shorter. Do not change the preparation deadline, settings, models or profile before the baseline without recording the operational reason.

After genuine worker/parent completion, use existing helpers with new output paths:

```bash
.venv/bin/python ../pipeline-repair-runs-20261105/normal_timestamp_audit.py --run "$RUN" --output "$PTS_AUDIT"
.venv/bin/python research/pipeline_repair_run_analysis.py --run "$RUN" --output "$COMPONENT_ANALYSIS"
.venv/bin/python research/pipeline_repair_evaluation.py --run "$RUN" --session UPLOADTEST1 \
  --reference Part2/dataset/Test1_Full/Test1_Full_rally.csv --output "$PRIMARY_EVALUATION"
```

The timestamp tool independently checks all source/proxy rational PTS, including tail, and all recorded source-pixel detector probes. The technical analysis folds every cache and original live event ledger, verifies exact predictions against all rally-end events, and separates models/providers, unknowns, detector freshness, pose/racket origin, tracking geometry, OCR and runtime samples. Evaluation opens the reference only after the strict completed inference guard. `cached_perception_used=false` is required: pure own-cache replay is not a fresh baseline.

## Frame/event root-cause workflow

1. Audit reference families first. Record clocks, frame basis, source dimensions, identities, missing/filled flags and review provenance. Keep each supplied file unchanged. Store strict primary results and alternative-reference diagnostic agreement separately.
2. Review *every* primary miss, extra and significant boundary/IoU case, plus component-specific discrepancies from other valid annotations. Source-bound per-case expected/actual lists must retain the exact CSV row and full frame/time coordinates. Do not classify overlap geometry as a sporting semantic split or merge without visual review.
3. `production_external_semantic_replay.py` can replay the completed run's own perceptions through the current engine, checking baseline parity. It has no new NN inference. **Its default trace ranges are empty**; `test2_failure_package.py` requires ordered detailed step traces for every frame. For Test1 request `--trace-ranges '[[0,17268]]' --focus ''`, without `--geometry-bracket` or `--contact-motion-reliability`, to retain all baseline steps and avoid irrelevant inherited hard-coded focus landmarks.
4. `test2_failure_package.py` supports the generic completed-upload binding despite its historical filename. Supply `--run`, `--replay`, `--source`, `--source-pts`, `--evaluation`, `--output`, `--session UPLOADTEST1`. It verifies the full source mapping, replay parity, source cache hashes, half-open windows around *all* relevant GT/prediction boundaries and overlapping fragments. The package contains exact-source imagery, evidence, timelines and interactive replay. `test2_source_frame_cache.py` is optional source-only JPEG preparation; retaining every source JPEG costs space and is unnecessary unless repeated rendering justifies it.
5. `test2_causal_analysis.py`, component diagnostics and cached trace fields expose observed-versus-interpolated shuttle, candidate/association decisions, detector/pose/racket freshness, identity/epoch changes and admission witnesses. Trace the first failing dependency, not merely the final empty outcome. Physical cause statements need the supporting source frames and must remain hypotheses where unreviewed.
6. Export actual completed analytics/highlights through a read-only detached store/fold or isolated product fixture. `pipeline_repair_product.py` accepts arbitrary completed uploads but its receipt filenames/UI labels still say Test2; document that legacy naming. It checks API analytics/individual estimates/highlights/summary/evidence IDs and provider-call absence, using `--completed-run`, `--output`, `--build apps/web/dist`. It copies completed artifacts to an isolated product fixture and performs no fresh inference. Output correctness remains separate from transport success.
7. For supported annotations, reuse source-bound shot/tracking/participant evaluators only when their schema and exhaustive review requirements hold. `tracking_benchmark.py` is sampled localization/global identity agreement; it is not evidence that HOTA/mAP are already implemented or eligible from arbitrary generated player CSVs. Do not manufacture contact/pose labels from the model being evaluated. Record unsupported metrics as unavailable and build a review queue rather than reporting invented zeros.
8. Only after the frozen new baseline and documented Test1 diagnosis should the orchestrator select a scoped change, record a separate implementation/profile revision and focused regression test, rerun comparable fresh before/after evidence, retain adverse controls, and decide whether to keep it. Current remaining recordings are exposed diagnostic/development material, not a certified prospective blind test. Later prioritization across multiple recordings must preserve exact versions; do not claim the same source was evaluated after a change without rerunning it.

## Important limits of this review

This document does not certify model accuracy or visually adjudicate labels. It identifies the actual implementation, evidence plumbing, current missing model capabilities, reproducible fresh execution and available frame-level diagnostic tools. The inventory/provenance agents separately establish which Part2 annotation columns can support each requested metric. Missing Test5/Test8 inputs should remain explicit manifest entries; the sequence must not silently skip them or fabricate labels.
