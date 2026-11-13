# Perception, model-runtime and ingestion implementation — 13 November 2026

All findings below come from existing reports and source inspection. No test,
model forward, model construction, media probe/decode, semantic replay, benchmark
or new metric calculation was run. Python AST parsing and Git whitespace review
are static checks only. No weights, dependencies or external source were added.

## Evidence and active path

Read the current validation index, Test1/2 root-cause specification and alternative
model investigation, the sequential diagnosis specification, and component,
resource, provenance and missing-label sections of Test03/04/06/07/09/10. The
requested `research/evaluation/benchmark/` and `evaluation/evaluation/` directories
do not exist in this checkout; relevant current evidence is in
`evaluation/ground_truth_validation/` and external artifact links recorded there.
The historical architecture and model-comparison documents were reviewed against
current code rather than treated as a current implementation inventory.

In particular, the existing Test6 report records 17,153 current poses computed
on propagated boxes; Test4 records 14,595. Current pose inference is not proof of
fresh person detection or correct anatomical ownership. Test9 and Test10 preserve
unknown winners and zero canonical accepted points despite source-board readings.
The generated shuttle references contain filled positions without per-row repair
provenance. They do not justify promoting reconstruction to observation.

The active flow is content-addressed source → probe/validation → canonical CFR
proxy and HLS media → `SegmentDecoder` → configured sport perception components.
`BadmintonPerception` loads registered shuttle/detector/pose/OCR/tracking providers,
computes current court/camera geometry, invokes scheduled person/pose and shuttle
perception, passes raw shuttle observations through association, and emits ordered
frame evidence. The temporal engine builds `Track` arrays and calls `process`
with scene/replay/coordinate/ambiguity barriers. Contact/rally consumers retain
separate observed and reconstructed masks. Component registration, model loading,
inference and output consumption are different facts.

Contracts retained: HWC uint8 BGR decoder frames; RGB 512×288 TrackNet frames;
checkpoint-derived L frames plus RGB background, NCHW tensor `(B,3*(L+1),288,512)`
in [0,1]; output `(B,L,288,512)` sigmoid heatmaps; decoded analysis-image pixels;
raw heatmap peak support is a score, not calibrated probability. COCO17 keypoints
use x/y/image-pixel coordinates and model support. Court homographies describe the
floor plane; they do not measure airborne shuttle position in 3-D.

## Diagnosis to implementation

| Evidence / observed limitation | Source-confirmed mechanism | Implemented change | Expected effect and validation |
|---|---|---|---|
| Existing long-video/resource reports motivate bounded processing; no recorded OOM is attributed to this code. | `TrackNetV3._detect` materialized every temporal RGB stack before iterating configured inference batches. | Store small index spans, construct RGB stacks only for the current batch. Preserve window order, background selection, padding and averaging. | Input-stack host memory follows configured batch rather than all windows; no measured memory or throughput gain claimed. |
| Source-confirmed model lifecycle defect; not attributed to a measured FP/FN. | `export_onnx` called in-place `.float().cpu()` on the live Torch model. | Export a detached deep copy, preserving the active model device/dtype and runtime metadata. | Later inference cannot silently move to CPU because export mutated the instance. Temporary export copy costs extra memory; unmeasured. |
| Existing diagnostics distinguish reconstructed context from observations; endpoint gates alone cannot certify a path. | Gap filling gated endpoint average speed, but cubic spline intermediates could overshoot the same configured speed limit. | Check every proposed edge including observed endpoints for finite coordinates and the existing `max_speed`; abstain for the whole gap on failure. | Reject physically implausible reconstructed context without inventing replacement observations; empirical effect unverified. |
| Evidence-support semantics require reconstruction not to manufacture confidence. | `filled_conf` could exceed the support of actual anchors. | Bound filled support by configured filled support and weakest contributing anchor. Preserve `interp=True`. | More conservative uncertainty; observed coordinates/support unchanged. |
| Source-confirmed frame-array contract hole. | NumPy broadcasting could silently accept unaligned shuttle x/y/visibility/confidence arrays. | Require aligned one-dimensional arrays and finite [0,1] support on visible samples. Missing coordinates still remain NaN. | Fail at the producer boundary instead of silently mixing frames. Static inspection only. |
| Source-contract issues, not observed failures in the saved videos. | Invalid chunk size zero allowed an unbounded file buffer; NaN duration passed both duration comparisons. | Validate positive integer decoder chunk/thread settings and finite positive media duration/limit. | Reject invalid ingestion configuration and metadata before downstream use. |
| ONNX provider inventory is not per-node execution evidence. | `ort_runtime` reports initialized provider priority as actual backend without describing placement certainty. | Add `node_placement_verified=False` and `execution_evidence=initialized_provider_priority`. | Honest runtime provenance; no performance measurement or CUDA-node claim. |
| Source-confirmed helper issues; helpers currently have no active production callers. | `keypoints.point` admitted NaN joint scores/coordinates; left/right comparison used different joint populations. | Treat nonfinite joints as unavailable; compare both labelings on the same ≥4 supported anatomical joints. | Safer reusable helper contract only. Do not claim active pose recovery from this change. |

## Model and component audit

| Model/component | Constructed / invoked / consumed by active code? | Integration and known limitations | Change in this workstream |
|---|---|---|---|
| TrackNetV3 | Yes when selected and successful `_load_shuttle`; `.detect`/diagnostic forward results enter frame shuttle/association evidence. Existing reports record Torch CUDA FP16. | Trusted checkpoint loaded through registry snapshot; eight-frame RGB+background default, sigmoid heatmaps. CPU fallback already recorded. ONNX graph cache keys include checkpoint/source/export code. Small-object ambiguity and camera-shared objects remain. | Bound temporal stack memory, tensor/frame guards, isolated export. No new checkpoint. |
| InpaintNet | Manifest entry; no active supported refinement integration. | Cannot present repaired output as independent image observations. | None; not falsely activated. |
| RF-DETR nano/small/medium | Configured `_load_detector` → PlayerDetector → tracking proposals; reports record small/CUDA. | Model normalization/decoding handled by adapter. Test1/2 exact-image evidence already showed athletes present in raw proposals at important misses, so replacing detector is unsupported. | Audited; tracking owner changes active player adapter. |
| YOLOX HumanArt | Explicit alternative in PlayerDetector; not the selected baseline in these reports. | Separate decoder and preprocessing contract; scores preserved rather than fabricated. | Audited; no unsubstantiated replacement. |
| RTMPose-M/body7 and X alias | Selected pose loader constructs tool; scheduled inference goes to PersonObs and contact/geometry. | The `rtmpose_x_halpe26` registry alias actually references body7, as its manifest note says. Missing joints/current pose on carried boxes are not fresh detections. rtmlib processes one crop at a time despite profile batch metadata. | Active adapter owned by tracking workstream; finite helpers improved but not active callers. |
| OSNet-AIN x0.25 | Optional explicit local checkpoint; descriptors consumed by persistent associator if construction succeeds. | Saved runs report missing checkpoint. Pinned adapter validates RGB128×256 crop, 512-vector output, normalization; appearance remains a cue, never named identity. | Audited, not downloaded or enabled. |
| Court lines + camera tracker | Active classical geometry/feature components, not pretrained weights. Geometry and lifecycle consumed downstream. | Current structured quality, floor verification, held/lost/reacquiring state already exist; single-frame generated/manual candidates are not all-frame accuracy. Multi-court airborne ownership remains ambiguous. | Investigated; no threshold relaxation or unsupported model swap. |
| Geometric racket | Builtin active when configured; contours/shafts associated with current person/pose. | Existing raw face/body/banner aliases remain; classical evidence is not a trained detector or proof of impact. | Events owner handles admission/contact improvements. |
| RapidOCR package | Configured package reader invoked on scheduled score crops; board observations consumed separately from accepted point decisions. | Alias `rapidocr_v4` does not pin actual package-selected weight version. Runtime already records package/asset/provider details. | Audited; no unverified numerical score or winner mapping. |
| RacketVision BallTrack | Candidate manifest/config entry; no supported active provider in production. | Distinct temporal contract; manifest presence is not a forward pass. | Not activated without comparable evidence. |
| RacketVision racket pose | Candidate checkpoint entry only; full two-stage racket detector+pose integration absent. | Current official source specifies RTMDet-M then five-keypoint RTMPose-M. A pose checkpoint alone cannot implement raw-frame racket detection. | No superficial integration. |
| WASB | Some profiles name it; missing model manifest/provider means not executed. | Existing alternative study preserves separate code/weight/data licensing review and unmeasured Pascal resource needs. | Not activated. |
| BST-CG-AP | Explicit optional singles shadow adapter; default rules remain active. | Two-player 100×2×72 feature contract and unresolved separate checkpoint grant; no established doubles support. | Investigated, no promotion. |
| Rule stroke/contact/rally components | Active estimates, not pretrained ML checkpoints. | Need outgoing temporal/court/person evidence; missing source labels preclude physical-accuracy claims. | Events workstream owns changes. |

The registry already performs integrity verification, cross-process atomic pin
publication, snapshot checkpoint loading and archive manifests. No duplicate
registry was introduced. First-fetch hashing establishes later integrity, not
publisher authentication. ORT's initialized provider list does not establish
all-node GPU execution. TensorRT native cache writes remain conservatively
disabled without complete compatibility identity and external transaction
ownership.

## Alternatives and source review

Existing evidence does not support replacing a pretrained model in this phase.
Primary sources checked on 13 November 2026 confirm the specialized architecture:
[TrackNetV3](https://github.com/qaz812345/TrackNetV3) combines frame/background
prediction with a separate rectification module; [RacketVision](https://github.com/OrcustD/RacketVision)
uses separate ball, racket and trajectory modules and a two-stage racket
pipeline; [WASB code license](https://github.com/nttcom/WASB-SBDT/blob/main/LICENSE.md)
is MIT, which does not independently resolve weights/data terms.
[ONNX Runtime's execution-provider contract](https://onnxruntime.ai/docs/execution-providers/)
assigns supported nodes/subgraphs to providers, supporting the explicit runtime
metadata caveat added here. No remote implementation was copied and no artifact
was downloaded.

## Files and remaining limits

Edited `engine/src/bai_engine/{decode.py,media/probe.py,runtime/device.py}` and
`sports/badminton/src/bai_badminton/perception/{tracknet.py,shuttle_post.py,keypoints.py}`.
The root integrator owns cache/pipeline version changes. TrackNet's source/export
fingerprint already changes derived ONNX graph identity automatically.

Unresolved: shuttle weak/missing image evidence and logo aliases cannot be
recovered by interpolation; true contact/racket/pose/tracking labels are missing;
floor calibration cannot provide airborne depth; original VFR-to-proxy source
frame correspondence remains distinct from exact proxy CFR timestamps. rtmlib
0.0.16 constructs a default CPU ORT session before the adapter installs the
configured provider session. Its constructor has no session-injection seam;
avoiding this transient duplication safely requires an upstream adapter change,
not a global monkeypatch or bypass of private initialization. ONNX TrackNet
retains a Torch model for its public re-export capability, so dual resident CPU
weights remain a documented memory cost.

Static AST parsing succeeded for six edited Python modules and Git whitespace
review passed at review time. No empirical validation was performed. Numerical
parity of batched construction, reconstruction coverage changes, all regression
behavior, actual memory/latency and export peak memory remain unverified.
