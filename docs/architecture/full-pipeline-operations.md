# Pipeline operation and evaluation notes

The existing engine/sport-plugin architecture remains in place. Current Phase 2
contracts and measured evidence are in [the report](full-pipeline-phase-2-report.md)
and [the ledger](full-pipeline-phase-2-ledger.md). The phase-1 architecture/research
files retain their historical evidence statements; the later report supersedes
unexecuted-test and unresolved-temporal-implementation descriptions.

## Authorized runtime and transfer

Author changes in the local Windows checkout. Commit scoped files, push
`origin/full_pipeline`, and pull with `git pull --ff-only origin full_pipeline` in
the isolated server worktree. Preserve unrelated local changes, primary server
checkout state, existing model artifacts and session results. Use the existing
GPU environment; do not install or replace dependencies to make a check pass.
The latest user instruction authorizes SSH and server tests/inference. Keep
Cloudflare disabled; use loopback or a local SSH forward for browser access.

From `/home/administrator/Desktop/sport-analytics/full-pipeline-phase2-20261102`:

```bash
source ../gpu-env.sh
export GPU_PY=/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
"$GPU_PY" -m pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests
```

Logs and fresh diagnostic outputs live in `../full-pipeline-validation-20261102/`.
Do not rerun analysis over user sessions without backing them up. The configured
application uses `../start-server.sh` on 8010; the isolated model-free smoke used
8011 to preserve that running service. It is validation, not deployment.

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

The real server export attempt failed because `onnxscript` is missing; `onnx` was
also absent at preflight. Torch FP32 CUDA tensor parity passed exactly, but this
does not establish ONNX numerical parity. Do not install packages or reuse an
unproven legacy graph to conceal the failed export. An ONNX-requesting profile can
report a degraded shuttle stage until exporter readiness is separately resolved.
Existing Torch profiles retain the baseline model contract.

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
