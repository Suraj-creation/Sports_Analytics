# Pipeline operation and evaluation notes

The existing engine/sport-plugin architecture remains in place. Current Phase 2
contracts and measured evidence are in [the report](full-pipeline-phase-2-report.md)
and [the ledger](full-pipeline-phase-2-ledger.md). The phase-1 architecture/research
files retain their historical evidence statements; the later report supersedes
unexecuted-test and unresolved-temporal-implementation descriptions.

The subsequent [event and score integrity report](event-score-integrity-20261103.md)
and [defect ledger](event-score-integrity-ledger-20261103.md) record the 3 November
score publication, recovery, read consistency and frontend synchronization work.
They distinguish deterministic software validation from real-video accuracy.

The expanded [component ledger](full-pipeline-phase-2-ledger.md),
[event contracts](full-pipeline-contracts-20261103.md) and
[validation record](full-pipeline-phase-2-validation.md) cover the later full-system
audit. They supersede older descriptions of archive reuse, media cancellation,
export publication and frontend failure handling. External worker coordination
and real-footage accuracy still have explicit unmet guarantees. The later
[real-video/runtime continuation](real-video-runtime-validation-20261103.md)
records successful ONNX CPU/CUDA parity and real private-Redis coordination;
crash acknowledgement, general distributed fencing and reviewed accuracy remain
open.

## Authorized runtime and transfer

Author changes in the local Windows checkout. The current integrity mission
prohibits commits: transfer a scoped Git binary patch against the recorded HEAD
to an isolated server worktree, using a temporary index to include new task files
without changing the user's real index. Commit/push only when explicitly authorized.
Preserve unrelated local changes, primary server
checkout state, existing model artifacts and session results. Use the existing
GPU environment. The user subsequently approved exactly four additive exporter
packages and a private Redis7.2.12 build; their pins, licenses, inventory delta
and validation are in the continuation report. This is not authorization to
replace Torch, CUDA, ORT, FFmpeg or other installed packages. The latest user
instruction authorizes SSH and server tests/inference. Keep
Cloudflare disabled; use loopback or a local SSH forward for browser access.

For the current audit, from
`/home/administrator/Desktop/sport-analytics/event-score-integrity-20261103`:

```bash
source ../gpu-env.sh
export GPU_PY=/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
"$GPU_PY" -m pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests
```

Current logs live in `../full-pipeline-audit-validation-20261103/`.
The later ONNX, Redis and fresh-video logs/results live in
`../real-video-runtime-validation-20261103/`; its private Redis uses loopback
port16379 only while validation runs. The opt-in harness requires a fresh output
and private empty Redis database; it does not start/stop a system service or
flush a shared database. Graceful process restart checks do not establish queue
crash durability.
Historical phase-2 logs remain in `../full-pipeline-validation-20261102/`.
Do not rerun analysis over user sessions without backing them up. The configured
application uses `../start-server.sh` on 8010; the isolated model-free smoke used
8011 to preserve that running service. It is validation, not deployment.
When starting the disposable E2E server in a background SSH shell, detach stdin
with `</dev/null`; its data is temporary and its fixture endpoints must never be
added to the production app. The NVENC capability probe also uses `-nostdin`.
Record and stop only that test server's own PID. Do not stop unrelated GPU jobs.

## Coordinate and temporal evidence

Persisted shuttle/player overlays use original analysis-proxy image pixels.
Tracked temporal analysis uses the calibrated reference image. Missing, singular,
nonfinite or reference-mismatched poses cannot supply temporal shuttle observations
or authoritative court positions. Recovery, view changes, shot/replay transitions
and recalibration form barriers; ordinary missing detections retain bounded gap
handling. Raw overlay evidence is preserved during loss.

`Track.vis` may include reconstructed positions. Independently observed shuttle
support is `vis & ~interp`. The rally FSM receives only this observed support and
adjacent observed motion. Cuts close old evidence before new contacts, clear
history and prevent cross-cut merging. Post-contact motion, next-contact flight,
receiver context, service/jump windows and geometric outcomes obey the same
segment contract. No measurement is invented when context is missing. Delayed
outcomes retain the calibration used by their observations.

Court coordinates describe the floor plane. They cannot reconstruct airborne 3D
position/speed, prove physical racket contact or establish an official line call.
The CFR proxy Timeline also does not provide a per-frame original-source PTS or
establish that duplicated source frames are independent observations.

## TrackNet artifacts and derived caches

The application consumes a registry-verified private checkpoint stream, and checks
its expected digest before deserialization. Atomic process-serialized first-use
pins establish later integrity, not publisher authenticity or pickle safety.
Continue using only previously trusted weights. No manifest/checkpoint/model
choice changed in this phase.

The TrackNet v3 export cache requires a fresh export for a new key; legacy graphs
are preserved and not silently adopted. Cache identity includes checkpoint,
exporter/builder/source and configured tensor/export inputs. ORT validates graph
bytes, float32 dynamic-batch tensor shapes and names before publication/reuse.
A content-hash graph is published before its atomic manifest; digest or contract
failure rebuilds instead of reusing a corrupt graph. Final ORT path loading assumes
application-owned cache paths. Cache growth has no automatic eviction policy;
preserve historical artifacts and manage space separately.

The earlier real export attempt failed because `onnxscript`/`onnx` were missing.
The approved additive pins in `config/runtime/onnx-export-pascal.txt` resolved
that prerequisite. A fresh graph, CPU/CUDA dynamic batches1/2, cache reuse and
eight-frame detection parity passed; maximum heatmap difference was below9e-7,
and profiling confirmed CUDA convolution. See the continuation report for exact
commands/artifacts. No legacy graph was silently adopted. Existing Torch profiles
retain the baseline model contract; these checks do not change a production
profile or establish labelled model accuracy.

Persistent TensorRT engine and timing caching is explicitly disabled by default.
The internal compatibility namespace includes graph/runtime/driver/GPU identity
and precision/builder options, but does not itself make native ORT writes atomic.
Only a future owner of native build/use lifecycle may provide cache context.
TensorRT provider advertisement is not proof of usable execution on Pascal GPUs.
No native engine-build or throughput claim was established here.

The existing `onnx-zip` path API remains outside the new snapshot contract. Its
extraction cache is not digest-bound and its lexical containment check needs
separate hardening; `open_verified` rejects archives. Preserve that limitation
when assessing pose/other legacy archive adapters.

## Rally evaluation manifest and migration

`research/evaluate_session.py` consumes schema v1 with one source-bound exhaustive
rally window in half-open canonical proxy seconds. Choose population and split
explicitly. A draft requires `--allow-draft` and cannot support an accuracy claim.
Reviewed labels require `review.human_verified=true` supplied by an actual human
reviewer. Attestation and `held_out` remain declarations, not independent proof of
annotation correctness or match-level split isolation.

Top-level supported fields are `schema_version`, `media_sha256`, `timebase`,
`status`, `split`, `population`, `exhaustive`, `window_s`, `rallies`, `review`,
`boundary_uncertainty_s`, `notes`, `provenance`, and optional `session_id`,
`fps_num`, `fps_den`, `n_frames`, `proxy_sha256`. Rally rows accept `start_s`,
`end_s`, `winner`, `notes`, `provenance`, `boundary_uncertainty_s`. Unknown semantic
fields are rejected. Windows/rows require finite non-boolean numbers; winner is
`P1`, `P2` or null. Null means unknown outcome of a known rally, and is excluded
from winner metrics rather than treated as a negative or definite label.

Partial review, uncertain rally existence or unreviewed intervals cannot be
expressed silently in v1. Use separate fully reviewed exhaustive-window manifests
and exclude uncertain spans. A future version can add explicit evaluated coverage
with defined truth/prediction clipping; v1 rejects those proposed semantic keys.
Do not mechanically promote review flags or fabricate labels.

The CLI hashes actual source/proxy files and the exact parsed annotation snapshot.
It supports stored source extensions and records `media_verification` in output.
Legacy labels without proxy SHA remain usable with `proxy_label_bound=false`.
Declare the optional proxy hash and rational FPS/frame count for new annotations;
this binds them to catalogue metadata, not an independent FFprobe recount.

The evaluator reports one-to-one interval matches, unmatched predictions/truth and
unknown winners. It does not validate court identity, individual identity, shuttle
localization/visibility, contact timing, shot family, floor contact or line calls.
Use the existing tracking/shot annotation protocols for those labels. No reduced
candidate event count, geometric exclusion statistic or synthetic pass establishes
accuracy without independently reviewed target-footage labels.

## YouTube in the requested public preview — 3 November 2026

The user subsequently requested a Cloudflare preview and YouTube import. This
public run is separate from the earlier offline validation phase. It uses the
validated uncommitted checkout on loopback port 8011 with its own data, an app
passphrase, and GPU1; the primary port 8010 service is preserved. No pre-existing
private validation sessions were copied into the public library.

YouTube is deliberately opt-in: set `BAI_YOUTUBE_INGEST=true` in the API process's
startup environment before launching it. The embedded worker inherits that
environment. `/api/system.youtube_ingest` drives the library form, and the API
still requires its existing rights acknowledgement. The initial preview launch
omitted this flag, so both API and UI correctly reported import unavailable.
The runtime launch helper now includes the flag; the global default remains off.
Existing login/session signing, data and the Cloudflare process are preserved
across the correction. No dependency installation was required: the existing
yt-dlp 2026.8.19 and configured FFmpeg handled the supplied video.

The requested `XupJpJH_9e4` video exposed a second defect during real use: two
sessions with different roster metadata shared its content hash and concurrently
encoded the same proxy/HLS. The MP4 probe reported invalid NAL units and one
session recorded 7,320 frames despite the full 684-second media. Session identity
and roster matching must remain separate from shared media preparation.

`media_writer_lock` in `engine/src/bai_engine/media/proxy.py` now serializes writers by media
directory with a cancellable OS advisory lock. `SessionRunner` rechecks completed
HLS after acquiring ownership, creates an encoder only if still needed, updates
each session from the completed playlist, and retains ownership through sprite
generation. Independent media can still prepare concurrently. The stable lock
file is retained; its existence is not a stale-lock marker. This does not add
distributed locking to the event stores or claim general multi-writer safety.

GPU evidence is retained in
`/home/administrator/Desktop/sport-analytics/cloudflare-empty-preview-20261103T084904Z/`:

- `media-race-red-valid.log`: **2 failed, 1 passed**, reproducing duplicate encoders
  and a cancelled waiter starting another encoder. Earlier fixture failures are
  separate logs and are not counted as defect reproductions.
- `media-race-green.log`: **26 passed** across the three new preparation cases,
  stop/cleanup, source validation and saved-session lifecycle controls. Scoped
  Ruff passed; independent read-only review found no important issues.
- `youtube-full-backend.log/.exit`: **1,421 passed**, 19 existing Starlette
  deprecation warnings, 240.97s, exit0.
- `real-media-concurrency.json`: the two actual sessions prepared the real video
  with **one encoder**, both got **20,524 frames**, and all 20,524 proxy frames
  decoded successfully. The 343-segment completed playlist spans 684.133333s.
  Total check 86.72s. Source SHA256:
  `467bce4a4dba4262cd32d30db52e9015ce6ec94b9e33ff7394ee26e7816b0bb1`.

Before rebuilding, the preview stopped gracefully, its current session data was
copied and its affected media moved into `before-media-repair-094817/`; the
original source was retained. The primary service was untouched. Cloudflare was
suspended during regression tests. Its temporary address expired during that
pause, so the tunnel was refreshed afterward; `launch.json` records the final
URL without putting runtime credentials in this repository.
The agent-created verification session is
removed after backup; the user's own session is retained and explicitly
reanalysed on the repaired media, using the normal backup/review-preservation
path. Generated data, login secrets, runtime helpers and logs remain outside Git.

The new tests cover normal owner completion, waiting-session cancellation and
independent media. Owner interruption/takeover, Windows locking and a second
process were not newly exercised; no broader recovery guarantee is asserted.
Successful import, full decoding and model progress do not establish labelled
event or score accuracy. All source changes remain uncommitted.
