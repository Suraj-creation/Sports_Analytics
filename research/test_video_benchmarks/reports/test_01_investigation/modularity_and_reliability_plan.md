# Modularity and reliability plan

Audit G, 2026-11-05. This is an implementation recommendation for the orchestrator, not an independent production change or merge decision. Production, original video/GT and frozen baseline artifacts remain unchanged.

## Smallest compatible evidence extension

Keep generic acquisition, timebase, model execution, storage and scheduling in `engine/`. Add any rally-specific evidence representation in `sports/badminton/`, alongside the existing domain ports. A second monolithic pipeline or badminton-specific branch in `SessionRunner` is unnecessary.

Recommended design:

1. A frozen sport-owned `RallyObservation` value with canonical absolute frame index, explicit observation kind (`observed`, `reconstructed`, `missing`, `invalid`), independently observed speed when available, reconstruction-support basis, context validity/discontinuity and optional frame-aligned observed player/pose motion. Confidence values remain uncalibrated model support unless an independent calibration experiment establishes probabilities. No raw human GT enters this value.
2. A runtime-checkable, versioned evidence-aware rally port exposing a typed observation step, plus the existing lifecycle/checkpoint methods. Retain `RallySegmentation` and its legacy `step(frame, visible, speed, replay)` adapter so an independent old provider continues working. Do not add unconditionally passed keywords that break existing implementations. A v2 provider can implement both adapters while the engine selects the richer method only through an explicit supported protocol/capability.
3. Registry declaration for a separate opt-in provider, with input schema/version and explicit observed-versus-estimated contract. Use `Profile.components.rally` to select it. Preserve source-bound v1 replay and test behavior. Universal bug fixes to a provider should also change its recorded contract/behavior version so cache identity cannot silently conflate versions.
4. Compute optional motion support from the existing frame-aligned `WindowObs` and target-court participant episodes. Preserve current detector/pose schedule metadata and episode/track identity. Require valid observed endpoints, same coordinate context and confidence/coverage checks. Do not read `self.activity`'s current state while processing a frame forty frames behind it; that would mix timebases. Do not treat carried boxes or inferred identities as independently observed motion.
5. Keep contacts and starts honest: an estimated trajectory can support bounded continuation but never becomes an independently observed contact, a new start by itself, a confirmed landing or a point winner. Missing/invalid/context-lost evidence are distinct. Motion alone cannot force continuation through an arbitrary break; the D audit measured activity during annotation gaps.

No particular fusion weighting is justified by the 36 rally annotations. Independent signals and reasons must remain inspectable rather than being collapsed into an opaque hand-set probability.

## Controlled implementation sequence

| Order | Change | Control and acceptance |
| --- | --- | --- |
| 1 | Focused FSM correctness fixes established by E/F: stale precontact history, configurable history allocation, onset-versus-confirmation clock | Public provider tests reproduce each counterexample, default behavior changes explained, checkpoint/reset preserves behavior, close separate rallies and cut barriers remain distinct. |
| 2 | Opt-in evidence representation/provider, no default promotion | Protocol replacement tests include an unrelated non-badminton host and independent legacy rally provider. Serialization/fingerprint changes are explicit. |
| 3 | Supported-reconstruction continuation only | Same recorded observations, same matcher; no starts/contacts from interpolation, scene loss remains a barrier. Show misses/extras and start/end outliers, not just IoU. |
| 4 | Independent motion conflict guard only | Frame-aligned actual pose/detection observations; player motion during breaks is a negative control; neither inactivity nor movement becomes a point decision. |
| 5 | Combined candidate with ablations | Isolate interaction between continuation and stationary conflict, compare controls and all difficult intervals. No GT-dependent union/merge. |
| 6 | Fresh production full-video candidate | Same original source, checkpoints and canonical timeline; record changed detector/pose scheduling, all backend status, runtime/resources and exact seven-column export. Cached replay cannot substitute for this. |
| 7 | Path/config/telemetry hardening | Injected model root honored; persist effective rather than nominal chunk settings; no weight migration or environment replacement; distinguish measured peaks from unavailable baseline data. |

The orchestrator decides which changes pass. A Test1 improvement remains exploratory. Keep default promotion separate from proving a mechanism on one known video.

## Production experiment record

Every experiment should contain:

- Production Git SHA plus source-file fingerprints and dirty diff, if any; new component and pipeline versions.
- Source/proxy/GT/config/checkpoint hashes, actual profile, effective HLS chunk length, model step/window/background settings, device/precision and package/driver/FFmpeg versions.
- Prediction CSV in the exact seven-column schema, unchanged evaluator and full metrics, comparison rows, missed/extra/fragmentation coverage, IoU/duration distributions and boundary tolerance denominators.
- Raw observations/events, state transition/rejection reasons, source-bound failure cases and execution log. Weak rejected candidates should remain separately identifiable when diagnostic collection is enabled.
- Resource sample trace and declared scope: process CPU/RSS, stage wall times, device-wide versus per-process GPU use, sampling cadence, missing samples, initialization/media prep versus inference versus export totals.
- Explicit baseline comparison and per-failure resolution/regression. Same labels must never choose interval endpoints, adjust thresholds at runtime, force counts or remove difficult cases.

Prefer an external experiment observer using existing statistics and wrappers before changing generic host interfaces. `perception.stats.seconds` exposes shuttle/player/OCR aggregates; whole perception time less measured children is only unattributed residual, not a measured court stage. Profile exact court/calibration, decoding or semantic functions only when needed. Torch allocator peaks and NVML device memory measure different scopes; report them separately. Capture supported backend/fallback records after actual model construction, not requested names alone.

## Learned temporal alternatives: primary-source screening

No candidate below was downloaded, trained, installed or evaluated on Test1. No independently verified pretrained badminton rally-boundary model was identified in this bounded screen. These are alternatives to investigate after collecting match-disjoint labels, not promised replacements.

| Option | Suitability / label requirements | Licensing and reproducibility | Decision for this mission |
| --- | --- | --- | --- |
| Small feature-based TCN or duration-aware state model | Could consume observed/missing/reconstructed trajectory, contact and body-motion features with explicit missingness. Needs many independent annotated matches and negative breaks; 36 intervals from one source do not establish generalization or calibrated uncertainty. | A new original lightweight model can have an explicit feature/schema/training artifact contract; borrowed implementations/weights still need separate licenses. No fitted model exists in this audit. | Keep as research design. First prove typed evidence and rules using controlled ablations. Do not fit the entire Test1 source and call it held out. |
| ActionFormer | Official temporal action localization model uses pre-extracted video features and supervised interval annotations. THUMOS I3D recipe uses 16-frame clips at stride4 (~0.133s feature spacing), which does not by itself resolve one-frame boundaries. Official available weights target other action datasets. Inference can exceed10GB according to official README, before our existing perception models. | [Official implementation](https://github.com/happyharrycn/actionformer_release), [MIT source license](https://github.com/happyharrycn/actionformer_release/blob/main/LICENSE). The code license alone does not establish every external feature/checkpoint/footage grant. Pinned README/LICENSE URLs and SHA256 are in `audit_g/external_sources/manifest.json`. | Do not add to the Pascal production runtime now. A suitable feature adapter, domain labels, weight/data grants, frame-accurate boundary refinement and isolated cost experiment are required. Published action mAP is not badminton rally accuracy. |
| MS-TCN | Official action-segmentation code trains on frame-wise features/labels for Breakfast,50Salads,GTEA. Its smoothing objective addresses over-segmentation, but its published classes/features are not badminton active/break events. Runtime and VRAM on this stack are unmeasured. | [Official implementation](https://github.com/yabufarha/ms-tcn), [actual license](https://github.com/yabufarha/ms-tcn/blob/master/LICENSE) is MIT **plus Commons Clause**, including a limitation on selling software-derived services. It must not be described simply as unrestricted MIT. External features/data have independent terms. Old official environment names Python2.7/PyTorch0.4.1. | Do not import into production or replace the server environment. Study the architecture/paper separately; require license review and a clean compatible implementation/artifact contract before use. |

Primary papers: [ActionFormer ECCV2022](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136640485.pdf), [MS-TCN CVPR2019](https://openaccess.thecvf.com/content_CVPR_2019/papers/Abu_Farha_MS-TCN_Multi-Stage_Temporal_Convolutional_Network_for_Action_Segmentation_CVPR_2019_paper.pdf). Descriptions above summarize only the author repositories/papers and distinguish inferred suitability from measured performance. No copied implementation or checkpoint was adopted.

## Required regressions and limitations

Retain existing tests for component registry validation, non-badminton host operation, provider replacement, stateful cache refusal, cleanup after failure/stop, transaction rollback and actual backend metadata. Audit G ran 73 of these controlled tests successfully in the existing environment. Add focused real-code tests for evidence v2, legacy adaptation, frame-aligned motion and estimated-versus-observed separation; include singles and four-person synthetic contracts without claiming real doubles accuracy.

Review every severe outlier and any newly merged neighboring labels. Baseline per-stage CPU/GPU peaks are unavailable; only new measurements can establish performance cost. Learned-model suitability, detector pixel accuracy and contact confidence calibration remain unmeasured without independently reviewed data. Preserve unresolved/unknown outputs rather than inventing observations or a sporting result.
