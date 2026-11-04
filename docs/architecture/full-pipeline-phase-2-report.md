# Full pipeline phase 2: implementation and validation

Date: 2 November 2026. Branch: `full_pipeline`. Runtime changes were authored in
the local Windows checkout, committed and pushed, then pulled into an isolated
GPU-server worktree. The primary server checkout and existing analysis sessions
were preserved. This report supersedes the phase-1 report's unexecuted-test status;
it does not claim production readiness or improved labelled accuracy.

## Implemented behavior

The engine keeps raw analysis-proxy pixels for persisted overlays. Its private
temporal arrays use a compatible stabilized image reference where tracking is
configured. Missing, invalid or mismatched camera transforms withhold temporal
observations. Shot, replay, view, transform availability and calibration/reference
epochs separate context; ordinary missing shuttle detections do not create a cut.
Legacy fixed-camera image analysis can continue without calibrated court geometry.
Court metres remain floor-plane measurements, never airborne 3D positions.

`Track.vis` retains its established processed-track meaning. The rally FSM receives
`vis & ~interp`, and its speeds require adjacent independently observed positions.
Short gaps retain the existing bounded end/lookahead/merge policy. A genuine
discontinuity finishes old evidence before current-frame contacts, clears history
and prevents cross-cut merging. A cut/EOF is not a geometric sporting outcome.

`WindowObs.segment_bounds` provides relative half-open context shared by contact
and stroke motion calculations. Post-contact speed cannot consume another scene;
flight duration, receiver and receiver-position landing proxy stay unknown across
segments. Even an uncertain next-hit link excludes that hit's sample from outgoing
speed. Service, jump and outcome windows respect coordinate boundaries. A long
exchange whose beginning left the bounded buffer has unknown start context.
Delayed outcomes use the calibration captured with their terminal observations,
not whichever calibration was installed later.

`ModelRegistry.open_verified` copies and hashes a private seekable checkpoint
snapshot, checks its existing integrity pin and hands that same stream to TrackNet.
Replacing or mutating the original path cannot change the loaded snapshot. Pin
read/compare/publication is serialized across processes; failed atomic publication
preserves existing pins. First-use pins do not authenticate a publisher or make
pickle deserialization safe; only previously trusted checkpoints were used here.

TrackNet's v3 export cache validates graph bytes through CPU ORT and checks the
established float32, dynamic-batch, 27-channel to 8-heatmap contract. Reuse requires
the recorded graph SHA and matching tensor contract. Writers publish a complete
content-addressed graph before an atomic manifest. Corrupt graphs rebuild, failed
exports clean their staging directory, and concurrent writers cannot pair one
manifest with another graph. Final provider configuration receives the graph SHA.
The final ORT path open assumes application-owned cache storage.

Persistent native TensorRT engine/timing caches are explicitly disabled by default.
An internal namespace helper includes graph SHA, precision/builder options,
ORT/TRT/CUDA/driver versions and selected GPU identity. It can only be used by a
future session owner that also serializes and validates native cache builds and
inference-time writes. Namespace tests do not establish native publication safety.

Rally evaluation v1 now rejects unsupported coverage/existence/review fields,
malformed/nonfinite/boolean timestamps, and winners other than `P1`, `P2` or null.
Null excludes unknown winner truth from winner metrics while retaining known rally
existence. Actual source/proxy bytes are streamed and verified before CLI metrics;
the annotation digest describes the same bytes that were parsed. Optional session,
FPS numerator/denominator, frame count and proxy digest declarations are checked.

## Verification

The configured environment was sourced with `source ../gpu-env.sh`; all Python
execution used the existing `Sports_Analytics/.venv/bin/python`. No dependency,
model, CUDA, FFmpeg or PyTorch environment was installed or replaced. The server
reported Python 3.12.12, Torch 2.14.1+cu126, ORT 1.29.0 and two GTX 1080 Ti GPUs
(compute 6.1, 11 GiB each). No unrelated compute job was stopped. Cloudflare was
disabled before testing.

| Gate | Result |
|---|---|
| Phase-1 focused regressions | 44 passed |
| Baseline including research tests | 1,148 passed; 12 existing Starlette warnings |
| Temporal RED | 33 failed, 4 passed, before implementation |
| Cache/provider/snapshot RED | 27 failed before implementation |
| Cache and integration GREEN | 62 passed |
| Atomic/cross-process pins and snapshots | 6 passed |
| Evaluation RED then GREEN | 73 failed / 45 passed, then 118 passed |
| Calibration capture and camera/outcome gate | 24 passed |
| Existing fixture contract gate | 45 passed |
| Final integrated engine/sport/agents/API/research suite | **1,307 passed**, 12 existing warnings, 203.20 s, exit 0, revision `5f9d0a4` |
| Independent final source review | Calibration finding fixed; no further material findings |
| Frontend TypeScript and Vite build | Passed using existing server dependencies |
| Isolated API/application/browser smoke | 240/240 frames analysed; completed playback and event export |
| Scoped production-source Ruff check | All checks passed; evaluation gate repeated after spacing correction: 118 passed |

The four failures in the first broader default-path run came from fixtures that
supplied no retained next-contact timeline, no camera reference/pose after tracked
recalibration, or a replay implicitly declaring no view. Fixtures now supply the
required evidence; production abstention guards were retained. Negative attribution
fixtures also have compatible flight context, keeping their intended checks meaningful.

The final integrated command is:

```bash
source ../gpu-env.sh
export GPU_PY=/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
"$GPU_PY" -m pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests
```

Validation logs and generated results are outside user sessions at
`/home/administrator/Desktop/sport-analytics/full-pipeline-validation-20261102/`.
The candidate worktree is `../full-pipeline-phase2-20261102`; detached baseline is
`../full-pipeline-baseline-20261102` at `27e2a20`. See the ledger for ownership and
the tested code revisions in Git. Existing untracked folders and web dependency
edits were not included in task commits.

## Real model and recorded-observation checks

The runtime harness compared baseline `27e2a20` with the candidate TrackNet code at
`e1225c9`, using the same verified existing checkpoint:
`df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`.
One deterministic FP32 CUDA tensor produced finite `[1,8,288,512]` outputs with
exact equality: maximum and mean absolute difference were **0**. After one warmup,
one measured GPU forward was 21.189 ms / 20.892 ms; peak Torch allocated memory was
374,857,728 bytes for each. These bounded observations are not a throughput or
accuracy benchmark. One detection call on eight existing proxy frames completed
with finite detections; detections/misses are unlabelled diagnostics.

The real fresh export attempt failed with `ModuleNotFoundError: onnxscript`.
Preflight also found `onnx` absent. No new graph or legacy cache adoption was
published, and no package was installed to bypass the constraint. Real TrackNet
Torch-to-ONNX numerical parity and native TensorRT execution remain unverified.
ORT advertising a provider is not evidence of successful model execution on it.

```bash
"$GPU_PY" research/validate_phase2_tracknet_runtime.py \
  --models-dir ../Sports_Analytics/models \
  --output-dir ../full-pipeline-validation-20261102/tracknet-runtime-NEW \
  --baseline-commit 27e2a20 --proxy /absolute/existing/proxy.mp4
```

The checked-in harness requires existing pins, refuses reused output directories,
never fetches weights, and records hashes, timing, tensor parity and export failure
in `report.json`. This run's report is `tracknet-runtime/report.json`.

Historical observations were replayed through both implementations into fresh
event stores, using identical initial calibration and no reviewer corrections:

| Recording / replay discipline | Frames | Rallies baseline → candidate | Strokes baseline → candidate |
|---|---:|---:|---:|
| SampleRally / singles | 480 | 1 → 0 | 2 → 0 |
| Real Video / singles | 4,462 | 0 → 0 | 0 → 0 |
| A02 multi-court / doubles | 22,802 | 69 → 44 | 480 → 282 |

All 27,744 input frames were covered in each revision with matching cached-input
hashes. All compared rally outcomes remained unresolved and no official points
were added. A02 replay elapsed time was 36.949 s / 36.163 s, a single diagnostic
run rather than a controlled performance study. Reduced counts are a behavior
change; without independent labels they do not demonstrate improved precision,
recall, shot classification, identity or point accuracy. These historical codec-7
caches lack pose-schedule metadata and are semantic replay inputs, not current
perception-cache compatibility proof.

## Application smoke and remaining gates

The fresh build was served by the existing model-free E2E harness on server
localhost port 8011, keeping the active application on 8010 untouched. A temporary
SSH local forward supported the local browser. Upload, FFmpeg proxy/HLS, scheduling,
API state and event-log export completed. The browser displayed `Analysed`, played
to source frame 239 of 240, reported video readyState 4 with no media error, and
had no captured console errors. The model-free clip makes no perception-accuracy
claim. A screenshot was saved as a local review artifact outside Git.
Server-side Playwright browser binaries were absent; browser verification used the
existing desktop in-app browser. The Playwright specification itself was not run.

Evaluation schema v1 still requires one fully reviewed exhaustive window. For
partial review, produce separate exhaustive-window manifests, excluding uncertain
existence spans. Do not set review flags mechanically. Future v2 can add explicit
reviewed coverage and exclusions, with both truth and predictions clipped under a
defined boundary policy; v1 continues to reject such semantic fields. Unknown
winner is represented by null. Descriptive notes/provenance do not change coverage.
Legacy manifests without a proxy SHA remain usable but report
`proxy_label_bound=false`; hash verification cannot recover missing annotation
provenance or verify actual proxy FPS/frame count through decoding.

Independent source-bound, exhaustively reviewed, match-disjoint target labels are
still missing. `held_out` and human attestation are declarations, not independently
verified split isolation or annotation quality. Rally manifests do not evaluate
target-court identity, player identities, shuttle visibility/localization, contacts,
shot family, verified floor contact or line calls; use/extend the existing tracking
and shot protocols for those components before claiming improvement.

Legacy registry `onnx-zip` extraction remains a separate known issue: extracted
graph reuse is not bound to archive content and its lexical containment check
needs a dedicated traversal fix. The new verified-checkpoint API rejects archives.
Production ONNX/TensorRT adoption additionally needs authorized exporter/runtime
readiness, real numerical parity and native cache lifecycle verification. This
phase neither deploys the branch nor replaces the baseline models.
