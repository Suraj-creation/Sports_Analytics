# Real-video, ONNX and Redis validation — 3 November 2026

The missing ONNX exporter and Redis-service prerequisites were resolved in the
existing GPU-server runtime after the user's explicit approval. Fresh ONNX
CPU/CUDA execution, real Redis coordination with separate API/worker processes,
and fresh video inference completed. These results establish runtime behavior;
they do not establish independently reviewed badminton accuracy or production
readiness. Test7 still has **33 unknown rally outcomes and zero accepted points**.

The candidate remains uncommitted on `full_pipeline`, based on
`cc73688630e40d534d94b7ef32bd0cbfed7e0571`. Code was authored on Windows and
transferred by scoped Git binary patches to
`/home/administrator/Desktop/sport-analytics/event-score-integrity-20261103`.
All dependency resolution, tests, inference and media processing ran on the GPU
server. The primary checkout and its port-8010 service were not deployment targets.

## Runtime and evidence location

Unless stated otherwise, artifact paths below are relative to:

`/home/administrator/Desktop/sport-analytics/real-video-runtime-validation-20261103`

The configured runtime was sourced before execution:

```bash
source ../gpu-env.sh
export GPU_PY=/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
```

Existing Python 3.12.12, Torch 2.14.1+cu126, ONNX Runtime GPU 1.29.0, CUDA,
FFmpeg, models and baselines were retained. Learned inference used physical GPU1
(Pascal GTX1080Ti, logical `cuda:0` under `CUDA_VISIBLE_DEVICES=1`), preserving the
primary application on GPU0. Long runs were detached so an SSH interruption
would not invalidate processing. Outputs use separate directories rather than
overwriting original sessions, tracks, caches, annotations or media.

## Additive exporter installation

The earlier `ModuleNotFoundError: onnxscript` is preserved in the preceding
[validation record](full-pipeline-phase-2-validation.md). Official
[PyTorch exporter documentation](https://docs.pytorch.org/docs/stable/onnx_export.html)
identifies ONNX and ONNX Script as exporter dependencies. A dependency dry run
showed four additions and no changes to installed distributions. The user then
approved these exact additions and the private Redis build:

```bash
uv pip install --python ../Sports_Analytics/.venv/bin/python --no-deps \
  onnx==1.23.2 onnxscript==0.7.2 onnx-ir==1.1.0 ml-dtypes==0.6.0
```

The before/after inventory confirms **exactly those four additions and no existing
package version changes**. Pins and additive installation instructions are in
[`config/runtime/onnx-export-pascal.txt`](../../config/runtime/onnx-export-pascal.txt).
The existing environment has no pip module, so its existing `uv pip` was used.
No dependency or lockfile was rewritten.

Licenses were checked against the official pinned package metadata: ONNX,
ONNX IR and ml-dtypes are Apache-2.0; ONNX Script is MIT. Version metadata,
distribution artifact digests and license declarations are retained in
`export-dependency-metadata.json`. The official version pages are
[ONNX](https://pypi.org/project/onnx/1.23.2/),
[ONNX Script](https://pypi.org/project/onnxscript/0.7.2/),
[ONNX IR](https://pypi.org/project/onnx-ir/1.1.0/) and
[ml-dtypes](https://pypi.org/project/ml-dtypes/0.6.0/).

`uv pip check` reports the **pre-existing distribution-name mismatch** where
rtmlib requires `onnxruntime` while the installed `onnxruntime-gpu` supplies the
runtime module. This was not concealed by installing a second CPU distribution
over the configured GPU package. `environment-before.txt`,
`environment-after.txt`, `environment-delta.json` and `onnx-install.log` preserve
the inventory and installation evidence.

## Fresh ONNX export, parity and cache reuse

The existing `research/validate_phase2_tracknet_runtime.py` was rerun with the
trusted checkpoint and a fresh output/cache under `onnx-initial/`, after the
approved installation. It **passed**: a new graph and atomic manifest were
published, and the real CPU constructor validated the IO contract.

- TrackNet `tracknetv3@3.0` checkpoint SHA256:
  `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`.
- New single-file ONNX graph: **45,361,944 bytes**, SHA256
  `79e5adaca3b91abedd3a7d6f8397cd6a7cec9337aa797c65355bc1ec7e3d536b5`.
- Content/configuration cache key:
  `6e43e65a618d0cbc0cc0ad212d157ee207fc592b16d3aca32efd1a01eac135e7`.

The new bounded `research/validate_tracknet_onnx_runtime.py` then exercised the
actual published artifact. It forbids export, requires the existing integrity
pin, verifies imports come from this checkout, disables ORT execution fallback,
checks CPU construction twice and CUDA construction once, and fingerprints all
cache files before/after. It compares seeded FP32 Torch CPU heatmaps against
real ORT CPU and CUDA outputs for batches **1 and 2**, using `atol=1e-4` and
`rtol=1e-3`.

Executed from the isolated checkout (paths identify the preserved original runs;
choose new output directories for another run):

```bash
validation_root=../real-video-runtime-validation-20261103
real_proxy=../Sports_Analytics/data/media/06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010/proxy.mp4
CUDA_VISIBLE_DEVICES=1 "$GPU_PY" research/validate_phase2_tracknet_runtime.py \
  --models-dir ../Sports_Analytics/models --output-dir "$validation_root/onnx-initial" \
  --baseline-commit cc73688630e40d534d94b7ef32bd0cbfed7e0571 --proxy "$real_proxy"
CUDA_VISIBLE_DEVICES=1 "$GPU_PY" research/validate_tracknet_onnx_runtime.py \
  --models-dir ../Sports_Analytics/models --onnx-cache "$validation_root/onnx-initial/onnx-cache" \
  --proxy "$real_proxy" --output-dir "$validation_root/onnx-parity-initial"
```

Result: **passed**, finite float32 `[batch,8,288,512]` outputs, maximum absolute
heatmap difference across comparisons **8.940696716308594e-7**, unchanged cache
and checkpoint, and **135 profiled CUDA kernel events**, including convolution
compute. The profile recorded no CPU node events. Eight existing real proxy
frames also had presence agreement **8/8** and position/confidence agreement
within the same tolerances for both ORT providers versus Torch. This is agreement
between implementations of one checkpoint, not labelled detection accuracy.

Artifacts: `onnx-initial/report.json`, `onnx-parity-initial/report.json`, its
CUDA profile, `onnx-parity-initial.log/.exit` and `onnx-summary.json`. The proxy
was the existing RealVideo asset with source hash
`06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010`.
Only two parentheses were added afterward to satisfy Ruff grouping rules; no
numeric, provider or cache behavior changed. Native TensorRT was not exercised.

ORT emitted a plugin-device discovery warning before selecting its built-in
CUDA provider factory. The observed CUDA convolution profile, provider metadata
and passing numerical checks establish actual execution; the warning alone was
not treated as evidence of CPU fallback or a reason to replace CUDA/ORT.

## Real private Redis and separate processes

There was no usable existing Redis service/binary. The official release archive
endpoint returned HTTP403; the failed bootstrap remains in `redis-bootstrap.log`.
The approved private build instead used the official
[Redis repository](https://github.com/redis/redis/tree/7.2.12), tag **7.2.12**,
commit **9913c926510755fa0d241658f550338a02258edb**, checked against the remote tag.
The tag's [COPYING](https://github.com/redis/redis/blob/7.2.12/COPYING) is BSD-3-Clause.
The source and binaries are outside both checkouts in `redis-github-source/`.

```bash
make -j2 MALLOC=libc BUILD_TLS=no redis-server redis-cli
```

Build exit0 and a real PONG are recorded. Redis listened only on
`127.0.0.1:16379`, protected mode enabled, with a private data directory and
snapshot/AOF persistence disabled. No system service, privileged installation,
production configuration, Docker permission or public listener was changed.

```bash
BAI_VALIDATION_REDIS_URL=redis://127.0.0.1:16379/0 \
  "$GPU_PY" research/validate_redis_runtime.py \
  --confirm-private-redis \
  --output-dir ../real-video-runtime-validation-20261103/redis-initial \
  --video ../Sports_Analytics/data/media/44ae09ac4369edc971588158a5b4eb2df7586b95c8992770277d4d36f93ea790/source.mp4 \
  --stage-timeout 180 --overall-timeout 900
```

The opt-in harness requires an empty private database and rejects other clients,
shared/default endpoints without explicit override, and reused output paths. It
does not FLUSH Redis. Its actual separate API/worker subprocesses use an isolated
all-models-disabled profile. The real 480-frame clip exercises upload/proxy/HLS
and completion; controlled synthetic score evidence separately exercises rules,
persistence and propagation. Synthetic winners are explicitly not video labels.

**All 13 stages passed**, exit0, in approximately 43.64 seconds:

- Fractional BLPOP requests 0.05, 0.5 and 1.5 seconds returned in approximately
  0.117, 0.600 and 1.504 seconds; real command transfer and binary pub/sub passed
  across processes.
- Separate API/worker startup, real clip upload and 480-frame model-free
  completion passed.
- A synthetic 1–1 score, correction to 2–0, live WebSocket notification and
  reconnect from cursor32 to sequence64 passed.
- Graceful API restart retained 2–0; graceful worker restart restored state and
  applied a correction back to 1–1.
- Reanalysis advanced the storage generation from revision0 to1 and processed
  the 480-frame clip again; API readers refreshed the generation.
- External DELETE returned409 and retained catalogue/evidence, as designed.

`redis-initial/report.json` includes stages, timings, HTTP/WS receipts and all
owned process exits. **No cleanup required SIGKILL**. The private Redis instance
is stopped after validation; source, binaries and logs are retained for reuse.

This closes the missing-service and unexecuted ordinary-coordination gates.
It does **not** establish Redis persistence, command acknowledgement, retries,
crash/power-loss durability, exactly-once delivery, general concurrent reset
fencing, multi-writer safety or dispatch-versus-shutdown ordering. BLPOP still
removes commands before a durable processing acknowledgement. External DELETE
remains deliberately unavailable until a worker-stop acknowledgement exists.

## Fresh continuous video inference

`research/validate_real_video_runtime.py` sequentially decodes canonical proxy
frames with PyAV and runs fresh `BadmintonSession.perceive`, engine ingestion,
track persistence and flush. It uses no cached perception or score/identity
reviews. Verified model copies are staged into the new output directory and
network downloads are blocked. Calls to the actual model adapters are counted;
declared-but-inactive statistics do not stand in for executed inference.

Existing SampleRally/A02 calibration inputs were explicitly preserved and hashed.
Test7 used fresh automatic calibration with the production whole-video source
keyframe sampler. These are offline VOD runs with future-video seed context,
not causal live-stream evaluations. The effective profile was `gpu-rtx4000`
with an explicit **FP32** shuttle override and **60-frame** processing chunks;
the profile's descriptive FP16/chunk64 text does not override those facts.

| Run/output directory | Canonical scope | Actual completed calls: shuttle forward / detector / pose / OCR | Result and effective event outputs |
|---|---|---|---|
| `sample-initial/` | Full SampleRally: **480/480**, 16s at30fps | **16 / 140 / 229 / 10** | Complete/exit0, 77.32s. No contact, stroke, rally-end or point events. |
| `test7-full-initial/` | Full Test7: **10,725/10,725**, 357.5s at30fps | **364 / 3,954 / 7,265 / 118** | Complete/exit0, 693.11s. **246 estimated contacts, 246 strokes, 33 rally ends, 62 broadcast readings**, zero accepted points. |
| `a02-prefix/` | A02 doubles/multi-court prefix: **1,800/22,802**, 60s at30fps | **60 / 660 / 1,199 / 24** | Partial/exit2: bounded prefix and unavailable optional OSNet identity model. **33 estimated contacts/strokes, 6 rally ends, 6 team hypotheses**, zero accepted points. |

All required model stages were available and exercised in all three runs.

The exact fresh-video arguments are retained in each `run.json`. The executed
commands, using the environment above, were:

```bash
CUDA_VISIBLE_DEVICES=1 "$GPU_PY" research/validate_real_video_runtime.py \
  --data-dir ../Sports_Analytics/data --session 01M55MFY9GQF6ZXP2SQPQ8X1KG \
  --models-dir ../Sports_Analytics/models --profiles-dir config/profiles \
  --profile gpu-rtx4000 --shuttle-precision fp32 --samples 5 \
  --output-dir "$validation_root/sample-initial"
CUDA_VISIBLE_DEVICES=1 "$GPU_PY" research/validate_real_video_runtime.py \
  --session-json "$validation_root/test7-input/session.json" \
  --proxy-path "$validation_root/test7-input/media/proxy.mp4" \
  --data-dir ../Sports_Analytics/data --models-dir ../Sports_Analytics/models \
  --profiles-dir config/profiles --profile gpu-rtx4000 --shuttle-precision fp32 \
  --samples 8 --output-dir "$validation_root/test7-full-initial"
CUDA_VISIBLE_DEVICES=1 "$GPU_PY" research/validate_real_video_runtime.py \
  --data-dir ../Sports_Analytics/data --session 01M5EXGZNEVGYAJ3AR6CJS5ZG9 \
  --models-dir ../Sports_Analytics/models --profiles-dir config/profiles \
  --profile gpu-rtx4000 --shuttle-precision fp32 --window-end-frame 1800 \
  --samples 6 --output-dir "$validation_root/a02-prefix"
```

SampleRally and Test7 reported no degraded stages. A02 explicitly records
`player_identity` unavailable rather than fabricating named four-player identity;
no model was fetched to change that outcome. All three fresh stores passed the
implemented event lineage/sequence/timestamp checks and live-versus-restored
score fold checks, with no listed consistency issues. Their accepted-point score
remained **0–0**; this is not the observed match score.

Coverage evidence is internal runtime output, not reviewed calibration or recall:

| Run | Calibration VALID / REACQUIRING / LOST | Frames with model-observed shuttle | Player track rows |
|---|---|---|---|
| SampleRally | 478 / 2 / 0 | 95 | 918 |
| Test7 | 10,194 / 36 / 495 | 6,394 | 20,138 |
| A02 prefix | 1,798 / 2 / 0 | 809 | 7,342 |

Test7's current view contains **33 unknown outcomes**: six rallies pass the
implemented official-phase gate and 27 remain unofficial. All 41 shots in the
official-rally analytics population are unattributed. Broadcast OCR saw names
such as `TAI T.Y.` and `MARIN`; the current conservative name matcher did not
establish the complete mapping to the supplied `Tai Tzu Ying` / `Carolina Marin`
scoring names. No player mapping or point was forced to make score output nonzero.
Resolving abbreviation/identity evidence and terminal outcomes is follow-up work;
these runs do not show correct end-to-end match scoring. SampleRally's empty
semantic output also remains an explicit diagnostic limitation.

The A02 source is 15fps/VFR while its proxy is30fps CFR. Source-to-proxy PTS and
duplicated-observation identity remain unavailable. A floor homography is not a
3D airborne shuttle/contact/landing measurement. The 60-second prefix does not
establish full-video coverage or labelled target-court exclusion accuracy.

Each run retains `run.json`, `results/<session-id>/report.json`, raw/current event
JSONL, frame-coverage JSONL, session JSON, Parquet tracks, capabilities, source,
proxy/model/profile/code digests and unreviewed overlays. A GPU-generated
`real-video-model-evidence.jpg` contact sheet was inspected for representative
singles and multi-court outputs; it is qualitative review evidence only.

## Matching Test7 and the Part2 annotation reference

The supplied Drive folder matched an already downloaded Test7 video recorded in
`docs/testing/task2/drive-video-download-manifest.json`; no redundant download
was needed. Original file:
`../Sports_Analytics/data/task2-review/Test7_Full.mp4`, 664,899,136 bytes, SHA256
`1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c`.
A separate proxy/HLS and session descriptor were created under `test7-input/`.
Proxy SHA256:
`5a0bc6a8e750e67376c436941fb15730de9f5bd10fd107e483b93f4d5691e9e6`.

The untouched local reference `Part2/dataset/Test7_Full/Test7_Full.csv` has **31
rows**, SHA256
`5f1ebabcc0a66dae579bf7ad35ddc48a97e88d1277cc7afa5e7d369a3fcbd9ea`.
The [label-readiness audit](audits/part2-label-readiness-20261103.md) distinguishes
this source from generated model-output CSVs. Review provenance, source/proxy
timeline binding, exhaustive coverage, held-out split and A/B-to-athlete mapping
are unresolved. The first row's winner conflicts with the legacy reference and
its displayed A/B score increment. A single `ball_types` field per rally is not
per-contact, hitter, shot or shuttle ground truth. Dataset licensing/provenance
is not established for redistribution; this was an internal user-authorized
diagnostic, with no dataset committed or relabelled as reviewed truth.

`part2-interval-diagnostic/reference-best-overlaps.csv` pairs each raw interval
with its independently best-overlapping current candidate, allowing many-to-one
matches. Thirty rows have some overlap; row9 has none. This deliberately is
**not** precision, recall, F1, winner accuracy or boundary accuracy. It assumes
raw annotation elapsed seconds can be compared with canonical frame/30; it does
not supply the missing original-source PTS map or resolve inclusive endpoint
conventions. The first raw interval6–15s overlaps candidate6.933–15s, whose
outcome remains unknown. No A/B-to-P1/P2 mapping or winner metric was invented.
The diagnostic JSON binds the reference, current-event, source and proxy hashes.

## Regression and source verification

- Full GPU backend command:
  `"$GPU_PY" -m pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests`.
  **1,418 passed**,19 existing Starlette HTTP422 deprecation warnings,241.92s,
  exit0, `full-backend.log/.exit`.
- New harness tests: **20 passed** in0.97s: five fresh-video/source-preservation
  cases and15 private-Redis safety cases. The video helpers first failed with the
  missing command. A later failing SQLite preservation assertion was corrected
  to allow only SQLite-created SHM and an empty WAL while checking all existing
  input files remain unchanged; an active-WAL visibility regression was added.
- Scoped Ruff passed for the fresh-video/Redis commands and tests, and for the
  ONNX command after the two grouping-only changes.
- The preceding audit's **162 frontend tests, build and eight browser tests**
  retain their earlier evidence date/candidate. No frontend/production behavior
  changed in this continuation, and they were not represented as freshly rerun.

New executable repository files are validation commands and focused harness
tests. No production engine, model, scoring, identity, threshold or frontend
change was required to close these two runtime prerequisites. User files,
Part2, unrelated dependency edits and the real Git index remain preserved.
The final transfer/preservation receipt is retained alongside the remote logs;
the primary runtime remains separate from the tested candidate.

The final source/test/configuration Git patch covers **80 paths**, SHA256
`9a4682f02b8f526ed2d32de70f9353645f6ae636eb0cd647ac17ae1c925ed3b2`.
Documentation is excluded from that fingerprint to avoid a self-referential
receipt. The complete scoped manifest contains **95 paths**: the earlier86
plus three validation commands, two harness test files, additive runtime pins,
the label-readiness audit, this report and the continuation plan. The final full
patch and temporary-index tree are compared with the isolated GPU checkout;
patches/manifests/receipts remain outside the repository.

`cleanup-receipt.json` records private Redis shutdown with its verified binary
and PID (empty database, no FLUSH), no remaining private-port listener, no
Cloudflared process, and the unchanged primary HEAD
`510b7039fee99b017a643bfcaf62804f0d9b7564`. Its actual `/api/health` endpoint
returned HTTP200 `{"status":"ok"}`; `/health` was only an SPA fallback and
was not used as the health assertion. The sole remaining GPU compute process
was the pre-existing port-8010 application PID762339. Its `apps/web/dist.old/`
and `client-website/` remain present. Dependency-file and Part2 reference hashes
match the starting local receipts; the real index is empty and no commit exists.
