# Perception reliability repairs — 29 October 2026

The inspected runtime is the local Linux RTX 4000 Ada environment. Existing user
session stores were read without modification; the light GPU probe ran while the
user's session was also processing. Historical Pascal/Windows benchmark timings
are not measurements of this machine.

## Confirmed mechanisms and repairs

- **Detector and pose input colour:** video decode supplies BGR. The installed
  rtmlib 0.0.16 RF-DETR and RTMPose adapters normalise and transpose channels but
  never convert BGR to RGB. The RF-DETR [official inference contract](https://rfdetr.roboflow.com/latest/reference/rfdetr/)
  requires RGB. The exact downloaded RTMPose archive's `pipeline.json` specifies
  `Normalize.to_rgb=true`, with RGB mean `[123.675, 116.28, 103.53]`. Both project
  wrappers now convert once, before detector normalisation or pose crop and
  normalisation. Person class index 1, original-image box rescaling, and pose
  affine inverse were checked and retained.
- **Tracking time:** detector stride changes between idle and active play.
  ByteTrack previously received no timestamps, so dynamics and lost-track age
  advanced by detector calls. It now receives the absolute video frame divided
  by FPS. Its lost buffer is expressed correctly as 30 reference frames (one
  second), rather than scaling by the source FPS twice. The dependency floor is
  the already-installed/locked `trackers==2.6.1` API.
- **Mutable perception history:** all badminton modes have stateful player,
  cut, camera and background history. Previously only doubles with neural ReID
  disabled cache reads and seeking ahead through that history. Every badminton
  mode now requests chronological fresh perception. Observation caches remain
  available for an explicit `decode_perception(..., diagnostic=True)` replay;
  they do not restore a live tracker's state. Codec 10 fingerprints the complete
  profile, loaded model references, frame size, FPS, match format and existing
  court/identity policy. Older or mismatched diagnostics are rejected.
- **Shuttle context:** TrackNet windows now stop at each camera-shot transition.
  A short shot is padded within itself. An adjacent shot's frames can no longer
  enter the same temporal model input. Tail coverage and overlapping-window
  averaging are retained.
- **Capability reporting:** `BadmintonSession.capabilities()` reports actual
  loaded core stages separately from disabled/unavailable ones. Shot rules and
  contact fusion are explicitly heuristic. Configured racket, live-shuttle,
  second-opinion and InpaintNet stages are disclosed as optional unsupported
  research stages, rather than advertised as executed or counted as failed
  required stages.

## Real-video evidence

The frozen cache-prefix summary covers session `01M62Y12THWAV746H1H8PXWGVX`,
frames 0–10379 at 30 FPS, a 1280×720 singles proxy. It contains 10,108 frames
with two player observations, 166 with one, and 106 with none; 37 temporary
visual track IDs; 18,137 finite COCO-17 poses; 7,627 shuttle detections; and
10,326 frames with valid calibration. These are coverage counts, not recall,
identity-switch counts or accuracy.

Frames 300, 1500, 3000, 6000, 9000 and 10320 were decoded and visually inspected
with their cached observations. Both player boxes align with the visible
athletes and the visible joints have plausible anatomical locations. The court
geometry aligns with the visible playing court. Frame 6000 has no detected
shuttle. Sparse inspection does not determine whether every other detected
shuttle point is correct.

The GPU A/B probe held each original frame and each pose crop fixed, using the
archived baseline adapter with either its original BGR input or manually
converted RGB input. Both variants found two court players and 34 keypoints
above 0.3 in every one of the six frames. Mean joint-location changes per frame
were 0.32–1.15 pixels. Mean model keypoint score changed from 0.7352 to 0.7392;
model score is not keypoint accuracy. This verifies a corrected contract with
valid outputs, **not a measured large accuracy improvement**.

Both ONNX sessions used CUDA. Model load took 2.74 seconds. Subsequent call times
are stored individually; baseline calls include first-inference warm-up and
concurrent user processing, so their difference must not be presented as a
throughput improvement.

Artifacts under `data/audit-20261029/perception/`:

- `baseline-cache-summary.json`, `baseline-cache-overlay.jpg`;
- `color-contract-ab.json`, `color-contract-ab.jpg`, `color-contract-ab.log`;
- `color_contract_probe.py`, which loads the archived baseline adapter explicitly;
- `focused-tests.log`.

The checkpoint export reference for the exact pose colour requirement is
`models/cache/rtmpose_m_body7/extracted/20230831/rtmpose_onnx/rtmpose-m_simcc-body7_pt-body7_420e-256x192-e48f03d0_20230504/pipeline.json`.
The A/B JSON includes the archived adapter SHA-256 and source references.

## Reproduction and limits

Use the existing `.venv` and NVIDIA library paths configured by `start-app.sh`.
Do not replace the GPU environment. The colour probe reads the original session
calibration and source only; it writes diagnostics under its own audit folder.
Run it only after checking available GPU capacity.

Focused regressions are in `test_perception_input_contracts.py` and
`test_stateful_perception_cache.py`. The former exercises the actual installed
rtmlib preprocessing and real ByteTrack expiry at 25/30/60 FPS, plus temporal
window construction across short and long camera shots. Existing court, camera,
pose, identity and detector-provenance tests retain their assertions and use
explicit diagnostic decoding where serialization is the subject of the test.

These perception repairs do not add a trained racket adapter, independently
labelled shuttle/pose ground truth, or persistent names for temporary visual
tracks. Missing shuttle observations do not establish whether the object was
occluded or outside the frame. No new model downloads or architecture changes
were needed for these fixes. Representative contiguous singles/doubles and
full-application evaluation belong to the integrated validation report. The
subsequent optional singles BST shadow adapter is documented separately in
`docs/testing/bst-adapter-20261029.md`; it does not change the default classifier.

## Executed focused regressions

The expanded run passed all 83 badminton tests. Three of six scheduler tests
initially failed because their lightweight session fixture lacked the newly
added analysis-revision metadata; adding an empty metadata dictionary retained
the real scheduler contract. The scheduler and new perception/cache-contract
rerun then passed 27 tests in 3.68 seconds. Source/new-test Ruff checks and
`git diff --check` passed. Logs retain both runs; the first failure is not hidden.

## Intermittent player visibility follow-up

The completed original recording has 23,494 main-view frames: 22,978 contain two
player rows, 416 one, 94 none and six three. Another 790 frames are classified
as no usable court view (mostly close-ups); these intentionally have no court
player analytics. These are availability counts, not labelled recall.

Inspection of the longest main-view gaps found a separate ground-plane error:
RF-DETR detects the athlete during a jump and sideline runoff, but every box is
filtered by projecting its bottom centre onto the floor. An airborne foot at
frame 9666 projects beyond the far baseline, although the athlete remains in
view. Frames 8192 and 17820 similarly lose already-tracked athletes in runoff.

PlayerPerception now admits an outside detection only through unique box overlap
with a recent established court track. It does not enlarge the admission region
for new people. Current detector evidence is still required; no missing body is
synthesized. A one-second history expires and camera cuts clear it. The policy
is included in observation-cache provenance. Court-space analytics keep their
existing spatial validity/bounds guards.

On exactly the same 178 real RF-DETR samples from three preselected problem
intervals, two-player availability changes from 141 to 173 frames; neither
variant emits extra tracks in this sample. All three inspected athletes are
recovered. Five frames still have fewer than two tracks, including three initial
ByteTrack admission frames. This is a targeted regression/availability result,
not general detection precision or identity accuracy. Recorded detections are
in `sports/badminton/tests/fixtures/roi_tracking_real.json`; ignored raw probes,
before/after replay and the visual gap montage are under the audit directory.

The frontend also provides a bounded, display-only pose estimate between sampled
pose frames. It uses a current body box and the same continuous track episode,
never bridges a missing body/camera change, expires after five frames, and draws
the estimated skeleton dashed with a label. Stored observations, contact/BST
inputs and movement calculations continue to use the actual observed poses.
