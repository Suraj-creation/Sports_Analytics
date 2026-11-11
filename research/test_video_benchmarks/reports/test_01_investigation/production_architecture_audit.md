# Production architecture and reliability audit

Audit G, 2026-11-05. Inspected the working `Benchmarking` checkout at frozen benchmark revision `b773e20`, with production source baseline `301baf08be5e989dd0ed93cb885733c3cf6f356a`. No production files, original media, annotation CSV or frozen benchmark artifacts were modified. Audit-specific evidence is under `artifacts/benchmarking/investigation/audit_g/`.

## Conclusion

The platform already has useful component factories, typed runtime protocols, provenance, append-only event storage and lifecycle tests. The strongest next step is a small sport-owned evidence-aware segmentation interface and explicit experiment telemetry, not a second pipeline or broad host refactor. The current rally interface collapses several different observation states into a boolean plus speed; that limits how a replacement segmenter can reason about supported occlusion or conflicting stationary evidence.

Architecture does not itself prove a Test 1 cause. The A/B/C/E/F audits and the orchestrator's exact semantic replay establish the relevant boundary mechanisms. This audit identifies the interfaces and reliability controls needed to test those mechanisms without changing unrelated analytics.

## Verified processing and ownership map

| Boundary | Actual owner / source | Verified behavior |
| --- | --- | --- |
| Acquisition, canonical media/time | `engine/media/{probe,proxy}.py`, `engine/decode.py` | Source probing, CFR proxy/HLS preparation and absolute decoded frame indices are generic infrastructure. No badminton-specific evidence is needed here. |
| Generic session orchestration | `engine/runtime/runner.py:353`, `_perceive`; `:461`, `_analyse` | Plugin selection, decoding, ordered ingestion, persistence and transport stay in the host. The main VOD chunk length is `plan.frames_per_segment`, not `Profile.chunk_frames`. |
| Whole pipeline selection | `engine/sport.py`, `get_plugin`; `badminton/plugin.py`, `BadmintonPlugin.describe_pipeline/create_session` | Installed plugin entry points and explicit stages select the sport runtime. The independent machine-intensity plugin tests execute the host without badminton imports. |
| Component construction | `engine/components.py`, `ComponentContract/ComponentRegistry.create` | Versioned input/output schema IDs, runtime-checkable Protocols, typed contexts, declared formats, finite configuration snapshots and per-session construction fingerprints are enforced. Stateful instances need reset/close; sport temporal ports additionally expose checkpoint/restore. |
| Perception selection and fallback | `badminton/perception/pipeline.py:215`, `_create_component`; `:416`, `_degrade` | An explicit failed provider is recorded unavailable; it does not silently select a different provider. Requested and actual runtimes are attached to the component/cache identity. |
| Badminton semantics | `badminton/components.py`, `BadmintonMatchEngine` | Identity, contact, classification, activity, rally, outcome, rules and analytics are replaceable domain ports. The engine, not generic media code, combines their evidence. |
| Cache and chronology | `badminton/plugin.py:1015`, `requires_sequential_perception`; `:1025`, `_isolation_id`; `:1122`, `decode_perception` | Badminton always processes fresh perception sequentially. Caches preserve diagnostics but cannot restore private tracker/cut/background state. Diagnostic decode is explicitly gated and bound to codec, calibration, format, profile, runtime and component metadata. |
| Durable evidence | `engine/store/events.py`; event schema | Events are append-only with correction/retraction folding. Track observations remain separately referenced. Provisional, confirmed, corrected, retracted and reviewed evidence must not be treated as interchangeable. |

The independent rally-port test is significant: it supplies a provider implementing only the public port, without inheriting baseline FSM internals. Any new engine code that reads `_recent`, `_invisible` or a baseline-only property from arbitrary providers would regress this architecture.

## Finding G1 — the rally observation boundary is too narrow

**Symptom:** a valid reconstructed trajectory and an entirely unsupported missing observation both reach `RallySegmentation.step(frame, visible, speed, replay)` as `visible=False` and unavailable speed. There is no typed field for reconstruction support, conflicting body/pose motion, observation quality or abstention basis.

**Source:** `sports/badminton/src/bai_badminton/components.py:109`, `RallySegmentation`; `engine.py`, `_window/_advance`; `events/rally_fsm.py`, `step`.

**Evidence:** source trace plus exact recorded semantic replay reproducing all 49 baseline intervals, their end reasons and 432 live contact timestamps. Audit C/F documents GT20's successful estimated trajectory while the FSM closes its interval. This audit did not rerun the model.

**Cause/confidence:** high confidence that the port cannot express the distinction; it does not follow that every interpolated point should continue a rally. Reconstruction remains estimated evidence, and player motion occurs between rallies too.

**Alternatives:** a stronger detector or contact provider might reduce ambiguous inputs without changing the interface; they cannot observe a physically out-of-image shuttle. Longer merge thresholds can improve some cases while joining legitimate breaks.

**Causal experiment/action:** add an opt-in, versioned sport-owned evidence protocol/provider with a backward-compatible legacy adapter. Ablate supported reconstruction and frame-aligned independent motion separately on fixed observations, then run full fresh perception. Keep observed, reconstructed, missing and invalid states distinct. Do not make a reconstructed sample eligible as an observed contact or a new rally start.

**Expected metrics/risk:** fewer fragments and better end/start outliers are plausible, not guaranteed. The main risk is bridging distinct rallies or prolonging floor pickups. Preserve camera/coordinate discontinuities and test short separate exchanges.

## Finding G2 — segmentation feeds back into upstream scheduling

**Symptom:** cached-perception replay can improve intervals without proving equivalent end-to-end behavior.

**Source:** `plugin.py:493`, `perceive`; `:649`, `in_play`; `perception/pipeline.py:497`, `process`, selecting player and pose cadence from the supplied in-play state.

**Evidence/cause:** the active rally state controls detector/pose stride for the following perception chunks. A new segmenter's state transitions can therefore change observed players, poses and downstream contact candidates in a fresh run. This is a proven dependency, not a claim that the current cadence is incorrect.

**Action:** label fixed-cache experiments conditional on baseline perception. The selected candidate must run the entire original video through the actual production pipeline with unchanged checkpoint hashes and explicit effective profile. Compare new contact/coverage counts and every newly missed or merged interval.

**Risk:** declaring a cache-only improvement production ready; treating contact input as fixed when its scheduling changed. Full-video output parity is the acceptance experiment.

## Finding G3 — effective chunk configuration is easy to misread

**Symptom:** the baseline profile names 64-frame chunks, while all recorded perception chunks contain 60 frames except the 48-frame tail.

**Source:** `Profile.chunk_frames` in `engine/config.py`; `SessionRunner._analyse` uses the media proxy plan's frames-per-segment; proxy planning targets two-second HLS segments.

**Evidence/cause:** baseline source/proxy are 30 FPS, so the effective segment length is 60. TrackNet step8 still emits every real frame, but 60 is not divisible by8 and tails overlap irregularly. The nominal profile field does not govern this VOD path.

**Action/experiment:** record both configured and effective chunk/window strategy. Compare fixed-input step8/4 or chunk strategies without conflating window overlap with dropped frames. Do not alter canonical HLS frame numbering just to make a model's batch shape convenient.

**Expected effect/risk:** clearer experiment identity and potentially different model context; no accuracy gain established. Changing chunk strategy can alter background refresh, tracking cadence and preprocessing context, so it is not a cost-free scheduling refactor.

## Finding G4 — baseline telemetry cannot establish per-stage resource peaks

**Available evidence:** whole-pipeline inference elapsed 1469.2373 seconds for 17,268 frames, approximately 11.752 frames/s. The runtime records TrackNet CUDA FP16/checkpoint hash, detector/pose active CUDA provider order, model/package versions, explicit missing OSNet/ReID degradation, hardware names and driver version.

**Unavailable evidence:** persisted baseline CPU utilization/RSS peaks, process-attributed GPU peak memory, per-stage timings and an execution-time resource trace. Hardware-memory totals and a later `nvidia-smi` snapshot are not inference peaks. This absence must remain `unavailable`, not be estimated and presented as measurement.

**Source:** `engine/obs.py:61`, `timed` records per-stage Prometheus histograms; `perception/pipeline.py:717`, `_rate` accumulates `perception.stats.seconds` for shuttle, players and OCR. Court/scene work is not separately persisted by the baseline worker. `engine/runtime/device.py`, `gpu_snapshot`, returns device-wide values and updates global metrics; it is not session/process attribution.

**Action:** fresh experiment observer should persist before/after stage aggregates and per-chunk wall times, decode/semantic/export costs, effective frame counts, process CPU/RSS samples and GPU process/device samples. Record sampling interval and gaps. Torch allocator peaks exclude ORT/FFmpeg allocations; device totals can include unrelated jobs. Distinguish these measures. Avoid synchronizing GPU after every tiny operation unless running an explicitly separate profiling experiment, because that changes timing.

**Expected effect/risk:** reproducible latency/resource comparisons, no promised boundary gain. Label Prometheus metrics correctly when multiple sessions share the process. A provider list with CUDA first establishes configured active session providers, not that every individual graph node executes on CUDA; per-node profiling would be needed for that stronger claim.

## Finding G5 — model/cache root is partly selected through global settings

**Source/evidence:** `badminton/plugin.py:245` passes `get_settings().models_dir` to perception although the session factory already receives an injected `ModelRegistry` with `registry.models_dir`. That global path controls derived runtime/engine cache placement, while artifact resolution uses the registry.

**Diagnosis:** a real dependency-injection inconsistency for isolated runtimes; not a demonstrated Test1 cause because the baseline's paths coincide. Configuration snapshots may be reproducible while derived caches are written under a different global root.

**Action/experiment:** a small owning-module fix can consistently use the injected registry's model root. A focused test should select a temporary model root while global settings point elsewhere and verify the passed derived-cache root. No model load/download is needed for this contract test.

**Risk:** accidentally moving/replacing existing accepted weights or native caches. Leave existing files intact; test path selection rather than migrating data.

## Finding G6 — growing rollback history may become a CPU/memory cost

**Source:** `BadmintonMatchEngine._score_transaction` snapshots semantic state and all registered transactional providers. `TransactionalAnalytics.checkpoint` deepcopies an accumulated `_operations` list, and rollback replays typed operations. Dense perception buffers are trimmed by `_trim`, but analytics operation history intentionally preserves match evidence.

**Diagnosis:** source-supported performance hypothesis, not a measured bottleneck or evidence of leaked GPU memory. It may create increasing copy cost as a match grows. It is unsafe to remove rollback/accepted evidence to improve benchmark speed.

**Experiment/action:** capture CPU profile and transaction duration versus processed frame/operation count in a separate observer run. Only if measured, consider immutable operation-log checkpoints or append-position rollback while retaining provider-owned opaque checkpoints and transaction semantics. Do not broadly rewrite analytics for this boundary task.

**Risk:** corrupting accepted events/score corrections, reducing historical evidence or breaking custom provider lifecycle. Existing rollback and component lifecycle tests are mandatory controls.

## Runtime/version evidence and model policy

Checkpoint pinning and private verified streams in `ModelRegistry.open_verified` protect the bytes loaded from later path replacement. Construction metadata alone is not a checkpoint identity; perception adds actual runtime/model identity after loading. Cache fingerprints include domain provider and format metadata, so algorithm/contract changes need an explicit version change and new experiment outputs. The frozen baseline must never be regenerated in place.

Missing OSNet is explicit startup degradation, not permission to fabricate embeddings or named actors. The documented singles-format path generally omits optional ReID once singles is inferred; it does not explain all rally errors. A/B/D/E source evidence must determine its actual effect. A fallback/no-model path can be software-correct while having lower coverage; report both availability and accuracy limits.

## Executed contract tests

Command in the configured GPU-host environment:

```bash
source ../gpu-env.sh
pytest -q engine/tests/test_component_registry.py engine/tests/test_component_declarations.py \
  engine/tests/test_independent_pipeline_plugin.py engine/tests/test_pipeline_component_lifecycle.py \
  sports/badminton/tests/test_rally_port_independence.py \
  sports/badminton/tests/test_domain_component_selection.py \
  sports/badminton/tests/test_device_contracts.py \
  sports/badminton/tests/test_stateful_perception_cache.py
```

Result: **73 passed in 4.31 seconds**, recorded in `audit_g/component_tests.log`. These are existing controlled protocol/runtime/cache/lifecycle tests, including mocked/controlled decoder and backend cases. They are not contact/localization/model accuracy measurements or fresh video inference. No test was reported as an end-to-end performance result.

## Limits

No model download, new learned temporal model, broad refactor, GPU inference or resource profiling was performed by this auditor. Proposed evidence fusion requires measurement and tests for singles, doubles, unknown identity and view loss. This Test1 source provides real singles evidence; synthetic doubles contract tests cannot establish real doubles rally-boundary quality. The separate modularity plan screens learned temporal alternatives and defines bounded implementation gates.
