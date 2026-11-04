# Component, integration and execution evidence

This report separates software behavior checks, real-media checks, fixed-input
semantic replay, actual component inference and fresh full-pipeline inference.
They answer different questions. Passing controlled or synthetic tests does not
establish shuttle localization, physical contact accuracy or sporting outcomes.
Test 1 remains development footage; no generalization claim is made.

All recorded commands used the existing GPU-host environment:

```bash
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
```

No package installation, replacement CUDA environment, new checkpoint download or
change to the original video/ground truth/frozen baseline was needed. Large logs,
resources, observations and diagnostic packages are retained under the ignored
`artifacts/benchmarking/` directory.

## Full regression checkpoints

The common full-suite invocation was:

```bash
pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests tests/benchmarking
```

| Code checkpoint / purpose | Actual result | Retained log |
| --- | --- | --- |
| Frozen production behavior, before implementation | **1725 passed**, 19 warnings, 280.32 s | `investigation/phase1/baseline_component_tests.log` |
| Typed evidence and component integration at `af70da7` | **1846 passed**, 19 warnings, 280.77 s | `experiments/full_regression_after.log` |
| Frozen final candidate source `3653b0d` | **1895 passed**, 19 warnings, 283.02 s | `experiments/full_regression_final.log` |

All three completed full-suite logs contain no skipped tests. Their 19 warnings are
Starlette/FastAPI deprecation warnings for the HTTP422 constant, not hidden test
failures. The counts describe collected cases in each source state, including
parameterized tests. Counts from different rows or focused subsets must not be
added as though they were unique tests.

The final full suite was launched concurrently with the fresh candidate worker.
That CPU co-run interval matters when interpreting wall-clock runtime. The
worker's measured time remains a real elapsed time, but a difference from the
historical baseline is **not** an isolated measurement of algorithm cost, and no
latency improvement is claimed from that comparison.

## Focused changes and counterexamples

| Scope | Actual evidence / result | Meaning and limits |
| --- | --- | --- |
| Temporal correctness regressions before the fix | **11 failed, 11 passed**, 1.07 s; `experiments/correctness_tests_red.log` | Intended failures reproduced fixed-length stationarity history, stale precontact history and delayed-confirmation recovery clocks. These are actual production-class counterexamples with synthetic inputs. |
| Corrected temporal behavior and existing rally contracts | **31 passed**, 1.12 s; `experiments/correctness_tests_green.log` | Parameter-shaped state, reset/checkpoint, contact history rebasing, motion-run onset versus confirmation, cuts, short intervals and separate exchanges. No detector accuracy is measured. |
| Injected model-root regression | **3 intended failures** before the fix; **21 passed**, 1.89 s after the fix | Unknown/singles/doubles constructor cases use a real empty temporary registry and controlled perception constructor. Global and injected roots differ. No model was loaded; lifecycle is checked. Logs: `investigation/audit_g/model_root_red.log`, `model_root_green.log`. |
| Typed observation/provider support | **53 passed**, 0.99 s; `experiments/evidence_v2_supported_tests.log` | Observed/reconstructed/missing/invalid states, strict value validation, estimated-versus-observed separation, no starts or contacts from motion/estimates, valid cut/replay barriers and provider reset/checkpoint behavior. |
| Typed evidence integration | **54 passed**, 2.00 s; `experiments/evidence_integration_tests.log` | Domain factory/engine integration and legacy compatibility; controlled real-code paths, not new model inference. Earlier development-stage43-case log is retained separately. |
| Combined motion/provider iterations | **109 passed**, 1.11 s and **131 passed**, 2.14 s in recorded integration groups | `rally_provider_tests_combined.log`, `integrated_evidence_tests.log`; these overlap other groups and are not unique additional counts. |
| Image-exit provider integration | **109 passed**, 1.12 s; `experiments/image_exit_provider_tests.log` | Contains bounded supported-loss behavior and legacy/provider controls. Supported exit/return cannot create observed coordinates, contacts or idle starts; unsupported loss, stationary closed exchanges, late recovery and context barriers remain separate. |
| Latest combined exit/motion/integration group | **159 passed**, 1.34 s; `experiments/exit_integrated_tests.log` | Most recent recorded focused group before the final full suite. Includes motion, provider, temporal and integration controls; not end-to-end model accuracy. |

The reported development-stage subsets of 34 image-exit provider cases, 49
motion/helper cases and a 90-case combined group are covered by the persisted
passing integration groups above. They have no separate retained standalone
log in this record and are not added as unique tests. The final full-suite
summary is the authoritative total for its collected source state.

The motion helper checks same-episode/track provenance, fresh matched detections
or actual scheduled confident poses, sparse pose timing, missing coverage,
stationary/one-joint jitter controls, camera boundaries, reconstructed-anchor
requirements and bounded image-exit direction/return evidence. It does not read
the future/current activity state as though it were aligned to an earlier
finalized frame.

Representative focused commands, with the exact currently recorded source:

```bash
pytest -q sports/badminton/tests/test_rally_temporal_correctness.py
pytest -q sports/badminton/tests/test_rally_evidence_v2.py
pytest -q sports/badminton/tests/test_rally_motion_evidence.py
pytest -q sports/badminton/tests/test_rally_image_exit_evidence.py
pytest -q sports/badminton/tests/test_injected_model_root.py \
  sports/badminton/tests/test_pipeline_declarations.py \
  sports/badminton/tests/test_domain_component_selection.py \
  sports/badminton/tests/test_component_construction_cleanup.py \
  sports/badminton/tests/test_plugin_component_lifecycle.py
pytest -q tests/benchmarking
```

These reproduction commands identify the owning test files. Their current
standalone counts need not equal an earlier grouped log: tests were added during
implementation. A selected file's collected subset must not be reported as a
separate measured run unless its execution result was actually retained.

## Specialist audit validation

| Audit | Actual result and evidence class |
| --- | --- |
| A: benchmark/evaluation | Exact-rational independent assignment and independent arithmetic reproduced all30 pairs, detection/error/IoU/tolerance values and event-to-CSV export. Production metrics JSON matched completely, comparison CSV matched byte-for-byte, and immutable hashes matched. This is measurement validation, not model inference. |
| B: temporal/media | **36 passed in5.06 s**; `investigation/audit_b/tests.log`. Includes real FFmpeg barcode source→proxy/HLS→decode identity tests using explicit CPU `libx264`, plus controlled subprocess/shared-writer tests. Actual Test1 NVENC outputs were checked separately by packet scans and decoded comparisons; the synthetic fixture is not mislabeled as NVENC. |
| C: shuttle contracts | **10 passed in3.23 s**; `investigation/audit_c/component_tests.log`. Synthetic heatmaps/window checks verify every real frame has an output position for lengths1,7,8,9,48,60,64. They do not measure TrackNet detection quality. |
| D: player/court/pose/activity | **141 passed in4.04 s**; `investigation/audit_d/component_tests.log`. Controlled/synthetic ROI, identity, cadence, pose, activity, geometry, format and four-player contracts. No independent real player/pose/ReID accuracy claim follows. |
| E: contact/event evidence | **97 passed in7.65 s**; `investigation/audit_e_final/tests.log`. Controlled contact/racket/streaming/singles/doubles tests and two additional diagnostic production-code probes. No manually reviewed physical-contact dataset exists, so no contact precision/recall is claimed. |
| F: FSM mechanism probes | Ten production-FSM diagnostic probes executed and recorded in `investigation/audit_f/fsm_probe_results.json`. They establish configuration/clock/history behavior under controlled inputs; real failure attribution also uses the exact semantic replay. |
| G: architecture/runtime | **73 passed in4.31 s**; `investigation/audit_g/component_tests.log`. Registry validation, unrelated non-badminton host, independent rally port, lifecycle, explicit backend metadata and stateful-cache tests. Controlled backends/decoding are identified as such. |

Precise audit commands and fixture configurations are preserved in the individual
audit reports: `temporal_alignment_tests.md`, `shuttle_perception_audit.md`,
`player_tracking_experiments.md`, `contact_event_audit.md`,
`rally_segmentation_audit.md` and `production_architecture_audit.md`. These groups
overlap the full suite and each other. They are not a second independent match
dataset and must not be summed into a larger unique-test claim.

## Real recorded evidence, replay and inference

### Immutable baseline and diagnostic replay

The original baseline is actual full-video production inference at production
`301baf08`, with benchmark artifacts frozen by `b773e20`. The investigation's
baseline semantic replay uses its recorded real perception through the actual
production structural decoder, match engine and domain ports. It reproduced:

- all 49 interval endpoints and all 49 end reasons;
- all 49 live start anchors;
- all 432 live contact and stroke timestamps.

This exact control supports causal temporal tracing. It does not rerun the
neural models or restore private live perception/tracker state. The baseline
replay record and state trace are in
`investigation/baseline_semantic_replay/`; the helper is
`research/replay_rally_evidence.py`.

Subsequent fixed-input FSM/semantic ablations are explicitly conditional on the
baseline observations. Changing segmentation can change in-play perception
cadence in a fresh run, so improved replay metrics are not a fresh pipeline
benchmark. References to `parity:false` in candidate replay logs mean the
candidate intentionally produced different intervals; they are not claims of
baseline reproduction. Baseline parity is established only by the unchanged
control.

There are 55 source-bound review packages: all 36 annotated rallies plus all 19
unmatched predictions, with all six misses, eleven multi-segment labels, severe
outliers and four controls retained. They include raw shuttle/player/pose
observations, inferred contacts, exact transitions, provenance and original-frame
overlays. These packages select evidence for review; they never enter prediction
generation and are not new human shuttle/contact labels.

### Actual paired TrackNet component experiment

`experiments/tracknet_window_pair/manifest.json` records real TrackNetV3 CUDA FP16
inference on physical GPU 1 for **2160 frames per strategy**, 12 fixed 180-frame
regions. Both strategies used the same pinned checkpoint, frames, fixed
background/masks and configuration apart from window step8 versus4. The manifest
records source/config/runtime/model hashes and controls. The actual component
command and code are in `research/audit_c_paired_inference.py` and its execution
log; no alternative checkpoint was downloaded.

Measured component-only wall totals were 20.3554 s for step8 and 29.7218 s for
step4, a 1.4601× ratio. This is not whole-pipeline latency. Neither strategy
detected the known upper-image disappearance in the tested region. There are no
independently labeled shuttle pixels, so raw observation counts are coverage,
not localization accuracy. This paired seed/background setup is not a replica of
the baseline's evolving full-video background. No full-video step4 result is
claimed.

### Fresh full-video candidate

The candidate is a separate real production run under
`experiments/fresh_image_exit_v1/`, source frozen at `3653b0d`. It uses the original
video through `SessionRunner`, normal production proxy, actual configured
TrackNet/detector/pose components, explicit opt-in `rally-evidence-v2`, and the
same seven-column exporter and frozen evaluator. Its selected flags are
`use_exit_recovery=true`, `use_reconstruction=false`, `motion_guard=false`;
TrackNet step remains8. It is not the richer all-signals replay configuration.

This fresh run **completed actual video inference and evaluation**.
`inference.json` records `status=analysed`, all 17268 frames and final frame 17267;
`benchmark_metadata.json` records `status=completed` at source commit
`3653b0deee367297037de449d882e9945e6d9c28`. Its 39 prediction rows have the exact
seven-column schema, sorted unique integer intervals and positive spans. The
prediction SHA256 matches the manifest. Independent Audit A verified the
source/config/checkpoint fingerprints and runtime evidence.

| Fresh execution check | Actual result |
| --- | --- |
| Source/proxy timeline | `proxy_alignment.json` confirms 17268 decoded frames/packets on the original zero-origin 30 FPS grid; proxy bytes have the same SHA256 as the frozen baseline |
| Ground truth / predictions / matched | 36 / 39 / 35 |
| TP / FP / FN | 35 / 4 / 1 |
| Precision / recall / F1 | 0.897436 / 0.972222 / 0.933333 |
| Measured complete worker elapsed / rate | 1509.99594 s / 11.43579 frames/s |
| Maximum sampled process RSS | 2945028096 bytes |
| Maximum sampled process GPU use | 2890 MiB, current-PID scope |
| Torch allocator peak | 1133421056 bytes; excludes ORT/FFmpeg allocations |

The distinct `experiments/fresh_image_exit_semantic_check/` verification then
replayed these newly recorded observations through the production semantic
engine. It reproduced **all 39 intervals and end reasons and all 447 live
contact timestamps exactly**. Its `replay_metadata.json` records interval parity.
This is a recorded-perception reproducibility check, **not a second fresh CUDA
inference run** and not proof of bitwise reproducibility of an independent GPU
run. The fresh contact count is 447 versus the baseline's 432, so its own
observations/contact stream must be retained rather than substituted with the
frozen baseline inputs. State-dependent upstream scheduling is a documented
dependency; this check does not separately attribute every changed contact to
scheduling or establish contact accuracy.

Full boundary, duration, tolerance and outlier results, remaining failures and
regressions belong in `final_benchmark_report.md`; these detection counts or a
pytest pass total do not replace them. All Test 1 results remain exploratory.
The CPU co-run and resource-sampling caveats below apply to the measured elapsed
time; no isolated algorithm-speed improvement is claimed.

## Final artifact and source verification

`python research/finalize_pipeline_investigation.py` completed after the fresh
run and exact semantic check. It rehashed all 1,766 frozen files, the original
video/annotation and active checkpoints; verified all 88 measured production
source files and the measured inference wrapper remain unchanged; recomputed
the fresh metrics using the frozen evaluator; and checked main's commit.

The new failure index contains 40 complete source-bound packages: all 36
annotations plus four unmatched predictions. Every case manifest hash and
required observation/event/trace/log/overlay file passed validation. All 17,268
perception frame identities are contiguous across 288 cache files. Camera-lost
state occurs on 285 frames and is reported separately from dropped video frames.
No source/proxy PTS or perception-index omissions were found.

Ruff lint passed all 27 changed Python files. Format checks passed 26; the sole
remaining `plugin.py` review-action string formatting issue was independently
reproduced from the unchanged main version. That pre-existing line was preserved
to avoid an unrelated production edit. `git diff --check` passed.

## Runtime and evidence limits

The frozen baseline did not persist process CPU/RSS peaks, per-process GPU peaks
or per-stage timing totals. Those values remain unavailable. Later hardware or
idle GPU snapshots cannot reconstruct them. The fresh worker uses standard
`resource`, `/proc/self/statm` and `nvidia-smi` sampling for its own PID; no
`psutil` installation was performed. Process CPU percentage may exceed 100 across
cores. Sampled process GPU memory is not an instantaneous peak; Torch allocator
memory excludes ORT and FFmpeg allocations. Stage wall aggregates overlap and
must not be added into a fictitious total; no extra CUDA synchronizations were
inserted to manufacture precise isolated kernel timings.

The broad regression suite and fresh worker overlapped on the CPU as stated
above. Fresh runtime is evidence of this observed configuration/load, not an
unconfounded baseline-versus-candidate speed comparison. The environment,
checkpoint assets and unrelated workloads were preserved.

The supplied source is real broadcast singles footage. Four-player/doubles,
uncertain identity, dropout and view transitions have software-contract coverage,
including synthetic inputs, but this mission has no independently labeled real
doubles rally-boundary video. No unannotated frames were assigned manufactured
sporting expectations. No detector/pose/contact probability calibration,
independent held-out generalization, real browser seek behavior or alternative
pretrained temporal-model quality was established by these tests.
