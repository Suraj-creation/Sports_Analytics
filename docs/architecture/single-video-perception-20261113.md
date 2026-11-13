# Single-video validation: perception contract workstream — 13 November 2026

Branch: `engineering/deep-pipeline-overhaul-20261113`; starting commit `e558fd9`.
The integration owner coordinates all actual video processing, model loading and
GPU execution. The initial contract-test phase did not decode a video, load model
weights or run model inference. Later selected-frame diagnosis and the disclosed
test-scope deviation are described below. Initial tests use synthetic arrays, stub model forwards and
session factories, or real preprocessing/association code without neural assets.
The selected single-video empirical run is reported by the integration owner.

## Investigation and ownership

Read `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, the deep-overhaul report and its three
linked workstream reports. Reviewed actual `decode`, media probe, provider
metadata, RF-DETR/RTMPose adapters, player cadence/provenance, TrackNet temporal
stack/export, shuttle reconstruction and existing relevant test sources. Existing
model/evaluation reports distinguish generated trajectories from physical labels,
current pose on propagated boxes from current person detections, and initialized
ORT providers from per-node execution. Those distinctions remain unchanged.

Owned production scope: engine decode/media/runtime-device and badminton
perception tracknet/shuttle-post/keypoints/players. Actual source edits in this
iteration are confined to `perception/players.py` and `perception/tracknet.py`.
The generic tracing module and pipeline/runner integration belong to the root
task. No concurrent edits were made to those shared files by this workstream.

## Residual issues and implemented changes

| ID | Component / evidence | Root cause and severity | Required improvement / implementation | Validation and status |
|---|---|---|---|---|
| PERC01 | Pose port declares array boxes; active default caller currently supplies lists | `PoseEstimator.__call__` tested `if not boxes`, which raises ambiguous-truth-value for a multi-person ndarray. Confirmed source/interface defect; medium | Use `len(boxes)==0`, accept list or ndarray; preserve rejected-crop output slots and four-person ordering | Synthetic four-person ndarray crop/order regression passes; fixed and contract-validated. Not claimed to have failed the selected default workflow |
| PERC02 | Previous overhaul batched TrackNet inputs but had no executed regression | Possible regression in batch allocation/window ordering; hypothesis until tested, high consequence | Dedicated execution test checks no more than the current batch's RGB stacks exist before each stub forward; retain existing short-shot/cut/padding tests | Bounded construction, existing temporal coverage and shot-isolation regressions pass. Real numerical model parity still belongs to the selected run |
| PERC03 | Previous nonmutating ONNX export and pose-output safeguards | Previously unexecuted source fixes; medium | Tests require active live object device/dtype remain unchanged while export receives a detached CPU/float32 copy; malformed tensor/person count fails explicitly; invalid crops/joints remain missing | Stub export/per-crop contract tests pass; no actual graph export or GPU construction occurred |
| PERC04 | Shuttle interpolation evidence must not become observations | Natural spline can overshoot even when endpoint average meets120px/frame gate; confirmed numerical mechanism, high consequence | Preserve previous per-edge rejection and anchor-bounded support; add real SciPy spline regression with100px/frame endpoint average and161.75px/frame interior edge | Rejected gap stays missing; accepted ordinary gap remains interpolated with support capped by weakest anchor. Tests pass; physical accuracy unmeasured |
| PERC05 | Latency attribution previously combined player detection, tracking and pose | Existing aggregate `players` timing cannot identify the costly substage. Confirmed observability limitation, medium | Added optional bounded `player_detector`, `tracking`, `pose`, `shuttle_preprocess` and `shuttle_forward` spans using generic trace API | Trace tests check exact frame bounds, counts/shapes, missing outputs and bounded JSON. Actual latency is measured by root's selected-video runs |
| PERC06 | Runtime provider list does not establish all-node CUDA execution | Provider initialization is weaker evidence than execution placement. High risk of misleading interpretation, low implementation severity | Preserve previous explicit `node_placement_verified=False` and provider-priority evidence semantics | Metadata regression passes; no per-node placement claim |
| PERC07 | RTMPose startup/per-crop implementation costs | rtmlib creates its default session before adapter replacement; configured batch does not change upstream per-crop loop. Confirmed source bottleneck candidates, medium | Do not rewrite constructors or enable speculative batching before actual measured initialization/pose costs | Open for measured prioritization. Existing provider and cropping semantics retained |

No detector confidence, NMS, stride, shot window, model checkpoint, reconstruction
speed limit or scoring threshold was tuned. No model/dependency was introduced.

## Active instrumentation contract

`PlayerDetector.__call__` emits detector implementation, input/output shapes and
dtypes, output count and finite-output summary. This surrounds the common adapter,
so both layout probes and regular scheduled detections are included.
`PlayerPerception` establishes exact canonical frame scopes for each probe,
scheduled detector, tracker update and pose execution. Tracker spans include
input/output counts and track IDs; pose spans include person count, current
detector-match count, missing outputs and per-person output shapes. Pose inference
on a propagated crop remains current image inference on uncertain person geometry.

TrackNet preprocessing spans summarize input BGR shape and RGB/model resize
contract. Each actual forward span includes backend, runtime metadata, batch tensor
shape/dtype and output shape/dtype. No full image, tensor, heatmap or embedding is
written to traces. Host wall-clock spans include host waits; no CUDA
synchronization was added and no device-kernel duration is claimed. Nested span
durations are not additive component totals.

The integration owner's generic trace adds run/session/source identity, frame
range, parent span, start/end timestamps, duration, exception and bounded JSON
serialization. The root task owns session/chunk trace scopes and persistence.

## Executed tests

Logs are outside Git:
`/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/perception-tests/`.

| Log | Scope | Result |
|---|---|---|
| `baseline-focused.log` | Existing RGB/affine, timestamp-aware tracking, pose source stamps, camera-shot/background retention, stub ONNX integrity, shuttle boundaries and stub stream-selection contracts | 49 passed in4.98s |
| `new-contracts-first.log` | New array/crop/shape, batch allocation, nonmutating export, spline/support, ingestion and provider tests | 26 passed in3.16s |
| `instrumented-focused.log` | Combined existing/new tests plus trace frame/payload regressions | 78 passed in5.07s |

Reproduction from the primary checkout:

```bash
source ../gpu-env.sh
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
.venv/bin/python -m pytest -q \
  sports/badminton/tests/test_perception_input_contracts.py \
  sports/badminton/tests/test_pose_observation_provenance.py \
  sports/badminton/tests/test_tracknet_background_retention.py \
  sports/badminton/tests/test_tracknet_onnx_cache_integrity.py \
  sports/badminton/tests/test_shuttle_post_segmentation.py \
  sports/badminton/tests/test_overhaul_perception_contracts.py \
  engine/tests/test_overhaul_ingestion_contracts.py \
  engine/tests/test_media_stream_selection.py
```

The inspected stream-selection tests mock metadata and PyAV containers; no real
source video is read. Export tests replace Torch export/session factories and do
not create a neural model. Existing background/cut tests use synthetic constant
images and stub forward arrays. Real RGB/affine preprocessing and ByteTrack
association execute without neural weights or video sources.

Ruff and scoped Git whitespace checks pass for the owned changes. These checks
verify the listed contracts, not player AP, pose PCK/OKS, shuttle recall,
contact/stroke quality or physical court accuracy. The selected video may not
exercise ONNX export, malformed outputs or every missing-data branch; those are
separately covered by the focused tests rather than declared video-validated.

## Changed files

- `sports/badminton/src/bai_badminton/perception/players.py`: NumPy/list crop input
  contract plus frame-scoped detector/tracker/pose execution summaries.
- `sports/badminton/src/bai_badminton/perception/tracknet.py`: preprocessing and
  per-batch forward traces; temporal scheduling/model outputs unchanged.
- `sports/badminton/tests/test_overhaul_perception_contracts.py`: synthetic active
  adapter, batch/window, export, reconstruction, pose and trace regressions.
- `engine/tests/test_overhaul_ingestion_contracts.py`: positive buffer/thread
  limits, finite media duration/limits and honest provider metadata regressions.

## Remaining empirical requirements

Actual model/checkpoint initialization, provider fallback, finite production
outputs, calibrated geometry, per-person pose association, shuttle visibility,
small/blurred objects, background aliases and observed-versus-estimated overlay
semantics require root's one locked selected-video run and visual evidence. No
accuracy or throughput gain follows from this test count. The initial contract
phase did not process historical benchmark media; a later test-glob scope
deviation is disclosed below.

## Completed selected-video diagnosis and measured optimization follow-up

The integration owner later authorized raw-cache/trace inspection and decoding
selected frames from the one locked `06a5cb...c010` proxy. No additional video or
neural model was opened for that diagnosis. All75 caches contain4462 ordered,
contiguous frames, finite positive boxes and finite positive-support joints.
All10708 pose rows and3205 racket rows identify their exact current frame;
3937 pose rows are actual image inference on carried person boxes. This distinction
is preserved rather than promoted to observed person geometry.

The source/overlay review and exact receipts live outside Git in
`single-video-validation-20261113/run01/visual_review/`. Frame369 is a confirmed
agent-reviewed false temporal boundary: source action remains continuous while
an ambiguous partial/full detector proposal causes the raw fallback to reset
tracking. Two supporting previous witnesses each have current overlap at the
unchanged0.3 gate; one matches a unique proposal atIoU0.8535, the other matches
two proposals at0.5107/0.5763. The root owner implemented a narrow unknown/no-reset
policy with source-bound validation, rather than certify unique continuity or
disable all unknown fallback behavior. New positive/negative synthetic tests and
the opt-in exact selected-source metadata fixture exercise this policy.

Visual examples also show small spectator boxes and later actor handovers,
adjacent-court shuttle marks and anatomical racket aliases. These are diagnostic
examples, not independently adjudicated physical precision/recall. The long raw
shuttle gap600–689 includes pickup/preparation and is not automatically a missed
rally. Remaining physical identity, shuttle and equipment limitations stay open.

Run01 host-wall traces identified a large perception attribution gap; the root
added finer spans for run02. Run02 measured `content_observe` around50ms/frame and
`content_validation` around15ms/frame in its early540-frame sample. This motivated
two source changes after run02 completed and its source lock was released:

- `scene_change.py._flow_groups` keeps independent `goodFeaturesToTrack`
  selection for every exact original background/ROI mask, concatenates only the
  selected point arrays, runs one forward and one backward LK call, and splits
  the unchanged finite/status/median statistics by original group. `_flow` stays
  unchanged as a reference and unusual missing-output fallback. No scene threshold,
  feature cap, mask, image or model schedule changes. Fifteen synthetic
  texture/translation/illumination/noise/blank cases match all reference statistics
  within1e-7, with count/None states equal; additional tests verify exact selected
  point order, two-call execution, fallback and source/mask immutability.
- Validation caches only immutable expected `FeatureOriginMask` record tuples,
  with128 geometry keys maximum. Keys contain every ordered region key/box and
  both source/analysis dimension pairs. Dimension/finite-geometry checks occur
  before lookup. Every submitted proof is still compared and feature/empty-origin
  rules remain enforced. Actual measurement masks are recomputed and never cached.
  Tests cover original raster-byte equivalence, subpixels/clipping/overlap,
  dependency-sensitive misses, forged records on hits, invalid input, eviction,
  immutable records and independent mutable measurement masks.

The root separately removed a duplicate serialization/validation roundtrip while
retaining complete validation and owns the content policy/component versions.
Existing synthetic scene tests that injected single-mask statistics now inject
grouped wrappers invoking the same original stub once per original mask. No
test-function identity branch was introduced into production.

Dedicated optimization/policy suite:51passed in2.11s. Curated synthetic scene suite:
230passed,3historical-image cases explicitly deselected in6.45s. Logs and JUnit
properties are under `perception-tests/scene-optimized-contracts.*` and
`scene-synthetic-final.*`. The controlled120×160 one-thread synthetic timing
sample gave reference/grouped medians approximately15.51/14.27ms over five calls;
this is not a selected-video speed claim. Full run03 under equivalent settings
must establish actual latency and unaffected-prefix observation equivalence.

### Disclosed test-scope deviation

One overly broad `test_scene*.py` invocation unintentionally included three
existing source-bound grayscale-window cases: Test1 frames10766–10770 and
15575–15579, and Test2 frames7699–7703. Those15 retained grayscale images were
processed by three classical scene observers. It also ran51 retained scene-layout
JSON cases. No historical video was decoded and no neural model ran, but this was
outside the user's single-video empirical scope and the integration owner's
synthetic-only instruction. The mistake was reported immediately to the root,
who disclosed it to the user. The unchanged log is
`perception-tests/scene-suite-optimized.log`; those results are excluded from
selected-video empirical claims and were not rerun. Subsequent commands use an
explicit file list and deselect the source-bound image test by name.

That accidental broad invocation returned348passes and two stale codec25assertion
failures; the root owns the codec fixture correction. Those failures were not
hidden or relabelled. The curated230-test result above excludes the historical
image cases and does not depend on reprocessing them.
