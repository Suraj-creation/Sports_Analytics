# Full pipeline validation — 3 November 2026

This is the executed record for the uncommitted full-system audit on
`full_pipeline` at HEAD `cc73688630e40d534d94b7ef32bd0cbfed7e0571`, including the
earlier score-integrity candidate. It is not a claim of independent real-footage
accuracy or production readiness. The [ledger](full-pipeline-phase-2-ledger.md),
[contracts](full-pipeline-contracts-20261103.md) and three linked component audits
separate implemented, tested, missing and blocked behavior.

**Later continuation on the same date:** the user approved four additive exporter
packages and a private Redis build. The [real-video/runtime record](real-video-runtime-validation-20261103.md)
supersedes this record's missing-ONNX and unexecuted-Redis gates: fresh export,
CPU/CUDA parity and13 Redis/external-process stages passed, as did1,418 backend
tests. Fresh whole-video SampleRally/Test7 and a bounded A02 prefix were analyzed.
The sections below retain the earlier phase's actual commands, counts and
no-installation statements; they are not descriptions of the later environment.
Independent semantic accuracy and crash-safe command acknowledgement remain open.

## Runtime, isolation and reproducibility

- Authoring: local Windows checkout. Tests, builds, checks, media work and model
  execution: existing Remote GPU Server environment only. Browser: installed
  Windows Chrome controlled by the GPU-side Playwright runner over SSH/CDP.
- Candidate: `/home/administrator/Desktop/sport-analytics/event-score-integrity-20261103`.
  Primary checkout/runtime: `../Sports_Analytics`; it was not switched/reset or
  deployed. Existing `apps/web/dist.old/`, models, baselines and user sessions are
  preserved. No new dependency, model, dataset or external source was downloaded.
- Existing Python3.12.12, Torch2.14.1+cu126, ORT1.29.0; Pascal GPU environment is
  supplied by `../gpu-env.sh`. There is no available `onnx`/`onnxscript` exporter
  stack in that environment. Existing web dependencies are reused through the
  isolated checkout's node_modules link.
- Logs/artifacts: `/home/administrator/Desktop/sport-analytics/full-pipeline-audit-validation-20261103`.
  Code is transferred via Git binary patches using a temporary local index.
  The real index remains empty; no commit/push was performed. Patches and their
  hashes distinguish candidates despite unchanged HEAD.
- Full Python run: `round4.patch` (saved on server); subsequent production edits
  are style-only `lint.patch` (exception suppression syntax/line wrapping).
  `web-typing.patch` corrects a test-only TypeScript assertion. Focused tests and
  `evidence-copy.patch` completes canonical-frame labels; `browser-timing.patch`
  observes short replay transitions inside the browser. Focused tests and the
  rebuilt browser run cover those final source changes. No model selection,
  threshold, weights, lockfile or dependency change is part of this task.

Bootstrap used in the isolated checkout:

```bash
source ../gpu-env.sh
export GPU_PY=/home/administrator/Desktop/sport-analytics/Sports_Analytics/.venv/bin/python
export PYTHONPATH="$PWD/engine/src:$PWD/sports/badminton/src:$PWD/agents/src:$PWD/apps/api/src:$PWD"
```

## Executed failure reproductions

These are deliberately failing regressions against the relevant pre-fix
candidate. Counts overlap when a later run includes preservation controls; they
must not be added into a total test-coverage claim. Source inspection preceded
each production correction. All logs below are in the artifact directory above.

| Log | Executed scope / result | What it establishes |
|---|---|---|
| `audit-red-backend.log` | Archive6, Redis3, stream selection2, initial background3, product6, initial export4: **21 failed,3 passed** | Stale/partial model extraction; timeout truncation; artwork mismatch; old-shot retention; mixed/unsupported analytics; partial export publication. |
| `audit-red-frontend.log` | HLS4 + upload3: **5 failed,2 passed** |401/403 stuck waiting; pending timer survived auth; upload unmount failed to abort/guard continuations; transient controls pass. |
| `audit-extra-red.log` | Initial stop4 + external lifecycle2 + CLI2: **8 failed** | Media cancellation/start race/unreported failure; disconnected external mode; unsafe delete; host guard bypass. Expected worker warning reflects injected uncaught OSError. |
| `reviewed-errors-red.log` | Reviewed panel failures/empty controls: **2 failed,2 passed** | HTTP errors hidden as no data. |
| `cache-generation-red.log` | Completed reset, FFmpeg probe, export8-at-that-stage: **4 failed,5 passed** | Old database handle, interactive probe, stale proxy/FPS clip keys. Five initial export repairs already pass. |
| `movement-refresh-red.log` | Same-generation support10→0 and0→10: **2 failed** | Analysed sessions retained stale movement evidence after committed corrections. |
| `clip-race-red.log` | Proxy replaced while mocked encoder succeeds: **1 failed** | Publication accepted obsolete input; fixed by fingerprint/recheck. |
| `review-races-red.log` | Generation3 + media cleanup5: **4 failed,4 passed** | Detected reset could mix/close an active snapshot; progress callback left encoder unreaped; dead media worker skipped cancellation. |

The added audit cases are 42 Python cases and13 frontend cases beyond the prior
score candidate. They test meaningful boundaries/faults with real SQLite
connections and controlled dependency failures. Fake encoder/model/Redis calls
are explicitly not evidence of real model, network service or Redis behavior.

## Integrated results

| Command, in candidate checkout unless specified | Actual result / log | Interpretation |
|---|---|---|
| `"$GPU_PY" -m pytest -q engine/tests sports/badminton/tests agents/tests apps/api/tests research/tests` | **1,398 passed**,19 existing Starlette HTTP422 deprecation warnings,221.93s, exit0; `full-backend.log/.exit` | Includes all new audit regressions, prior score/temporal/cache/evaluation coverage, real FFmpeg upload/proxy/HLS/clip/PDF integration and API/WS tests. Not end-to-end trained-model accuracy. |
| `cd apps/web; pnpm exec vitest run` | **162 passed in 40 files**, 5.28s, exit0; `frontend-final.log/.exit` | Includes all new HLS/upload/error/movement cases and final evidence labels. Earlier full run also passed in 5.81s. |
| `cd apps/web; pnpm build` | Initial failure TS2532 in new test fixture; corrected to return its actual QueryClient. Final TypeScript+Vite build **passed**, exit0, Vite6.39s; `build-verified.log/.exit` | Initial failure retained in `build.log`; no false first-run success. Production dependency files unchanged. |
| `"$GPU_PY" -m pytest -q engine/tests/test_runtime_stop_integrity.py engine/tests/test_ffmpeg_probe_isolation.py engine/tests/test_model_archive_integrity.py apps/api/tests/test_export_publication_integrity.py` | **20 passed**,2.59s, exit0; `final-focused.log/.exit` | Rechecked files affected by final style-only edits. |
| `xargs -r "$GPU_PY" -m ruff check < ../full-pipeline-audit-validation-20261103/ruff-paths.txt` | **All checks passed**, exit0; `ruff-final.log/.exit` | Scoped changed/new Python files. Three initial style findings corrected; original `ruff.log` retained. |
| `cd apps/web; … pnpm exec biome check --formatter-enabled=false --assist-enabled=false` for recorded `biome-final-paths.txt` | **31 files checked, no errors, 9 non-null-assertion warnings**, exit0; `biome-final.log/.exit` | Scoped lint only, not a repository-wide formatting claim. Warnings are test fixture indexing, including prior score work. |
| `cd apps/web; pnpm typecheck` | **Passed**, exit0; `typecheck-final.log/.exit` | Final TypeScript check after the browser assertion update. |
| Git temporary-index `git diff --cached --check` | Passed during patch construction | Whitespace/inclusion check only; not a runtime test. |

## Browser end-to-end execution

The installed computer-use launcher failed before opening a surface with Windows
error `0x80070020`. The fallback keeps execution on the GPU server and uses the
already installed Windows Chrome156.0.8078.79 via a temporary profile and SSH
reverse CDP forward. No browser/dependency installation was performed.

The disposable server is started with its own recorded PID, port8011 and an
isolated temporary data directory:

```bash
"$GPU_PY" apps/web/e2e/server.py 8011 > ../full-pipeline-audit-validation-20261103/browser-server-final.log 2>&1 </dev/null &
# With local browser remote-debugging-port19224 and SSH -L8011:127.0.0.1:8011 -R19224:127.0.0.1:19224:
cd apps/web
BAI_E2E_PORT=8011 PW_CDP_ENDPOINT=http://127.0.0.1:19224 pnpm exec playwright test
```

An initial baseline run was interrupted after1 pass/2 failures/1 interrupted/4
not run: FFmpeg's NVENC probe suspended the background SSH process group with
SIGTTOU, leaving upload status ingesting. The stopped server/child process and
browser errors are retained in `browser-baseline.log` and
`browser-baseline-interruption.txt`. That is not counted as a passing browser run.
The probe regression failed before `-nostdin` was added. The final server also
detaches stdin.

The next run (`browser-final.log`) passed seven checks and exposed one remaining
source-frame label in EvidenceDetails. The label and other progress/help/moment
references now say analysis proxy/frame. `browser-verified.log` passed seven
checks but its repeat-cue assertion missed the entire half-second replay between
CDP polling calls. `clip-diagnostic.cjs/.json` recorded three repeated cues, each
emitting play/playing and stopping at frame105 about500ms later. The test now
attaches a playing listener before dispatch inside the browser, asserts the
playback position and verifies the final bound. **No playback production change
was justified or made.** Failure traces/screenshots are preserved separately.

Final browser result: **8 passed in 2.6 minutes**, exit0;
`browser-accepted.log/.exit`. All eight checks ran in one fresh disposable-server
run. They cover: empty production routes desktop/mobile; real upload/HLS/range/frame
navigation and tabs; mocked sign-in failure; missing-record state; preference
reload/catalogue filtering; reviewed four-player identity flow; durable score
correction/reload; upload/playback/export smoke. Traces/screenshots are preserved
in `browser-accepted-results/`. The final server used
`browser-server-accepted.log` and its recorded PID; it was stopped after the run.

The score flow uses controlled observations and the real domain engine, SQLite,
HTTP, WebSocket and browser. It verifies1–1→2–0 after an explicit winner correction,
two effective point records, durable API state and reload rendering. Backend
restart/app recreation is verified separately in API tests. Identity review uses
explicit seeded tracks; authentication rejection is deliberately mocked in the
browser and separately API-tested. None is a real-footage perception benchmark.

## Acceptance matrix and unexecuted gates

| Feature / required invariant | Evidence-based status | Remaining limitation / next gate |
|---|---|---|
| Point decision → exact-once application → durable history/state → API/UI | Unit/integration-tested; controlled score browser gate recorded separately | Independent target outcome labels absent. Logical duplicate/transaction/retry tests do not create a durable command queue. |
| Reload and backend restart | API app/repository recreation and prior browser reload covered; current browser rerun recorded above | Real external-worker crash during Redis BLPOP processing untested. |
| Unknown/missing winner, provisional point, wrong side, stale/retracted packets | Regression-tested; accepted point criteria enforced in restore, analytics and frontend | Complete sport officiating for lets/faults/retirement not implemented. |
| Singles/doubles mapping, four-person review, service setup | Unit/API integration; controlled review browser gate | Automatic visual identity accuracy and same-camera multi-court ambiguity unlabelled. |
| Ingest/proxy/decoder/HLS/range/clip/PDF | Real FFmpeg/PyAV/report API integration in intended runtime | Real artwork-first mux fixture not exercised; probe/PyAV selection contract is mocked. External YouTube download not exercised. |
| Temporal/camera/calibration/contact/stroke/outcome boundaries | Regression-tested, current bounded Torch GPU parity/proxy diagnostic below, and historical cached-observation replay | No independently reviewed raw-video accuracy run; source observation duplication map and content replay detection absent. |
| Registry/download/archive/ONNX/TRT caches | Integrity/publication/provider-contract unit tests, concurrency faults; current trusted Torch GPU path exercised | No download or native TensorRT build. Fresh ONNX export attempted and unavailable because onnxscript is missing; onnx also absent. Whole TrackNet module digest changes with retention code, so old export key cannot be asserted reusable. |
| Local embedded lifecycle and media cancellation | Unit/integration-tested; own process cleanup verified by test/run logs | No global GPU admission scheduler. General multiple-process reset/write ownership and command acknowledgement incomplete. External deletion intentionally409. |
| Redis external runtime | Adapter timeout contract unit-tested; external/no-Redis rejected | No Redis listener available on6379 in this session; real separate API/worker/Redis/crash recovery not run. |
| Q&A/fallback/grounding | Existing tool/validator/fallback tests; truthful UI labels | No external/local provider requests; numeric/citation checks are not semantic grounding proof; raw handle lifetime across asynchronous reset unvalidated. |
| Auth/CSRF/isolation | API tests plus host guard regression; browser rejection UI fixture | Single-user deployment only. No tenant/RBAC isolation feature exists. No public deployment tested. |
| Performance/accuracy | No new claim | Need source/proxy fingerprints, independently reviewed exhaustive annotations, match-level held-out split, annotation version, code patch hash, weights/config/runtime identity and per-component metrics. Current suite durations are not inference benchmarks. |

## Current bounded real-GPU/model diagnostic

After checking both GPU allocations, the current check used otherwise idle
physical GPU1 (GTX1080Ti; CUDA maps it to logical cuda:0). The primary application
on GPU0 remained running. Reused the existing checked-in harness and trusted
pinned checkpoint; no environment/model change:

```bash
CUDA_VISIBLE_DEVICES=1 "$GPU_PY" research/validate_phase2_tracknet_runtime.py \
  --models-dir ../Sports_Analytics/models \
  --output-dir ../full-pipeline-audit-validation-20261103/tracknet-runtime \
  --baseline-commit cc73688630e40d534d94b7ef32bd0cbfed7e0571 \
  --proxy /home/administrator/Desktop/sport-analytics/Sports_Analytics/data/media/06a5cb888e58c64421114fecc582f60b85466900efec6db0bbf99420f4f6c010/proxy.mp4
```

`tracknet-runtime/report.json` records source/harness/checkpoint/input hashes,
runtime versions, actual backend, outputs and failure. Overall exit **2/partial**
is deliberate: Torch checks pass while fresh ONNX export is unavailable.

- Model `tracknetv3@3.0`, checkpoint SHA256
  `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`.
- Candidate TrackNet source SHA256
  `801f150b61b2711c1904a7d151e1243de0fa37c6bbcaf16bbf108a2ac739d2760`;
  baseline source `f1801f39e3cd7351e08cef18671943c32321bb68dac5e76f8816831b66730e031`.
- Finite FP32 CUDA outputs `[1,8,288,512]`, exact equality;
  maximum and mean absolute difference **0**. One warmup and one measured forward
  per candidate:20.747ms baseline /20.829ms candidate; peak allocated bytes
  374,857,728 each. This sample is **not a throughput or speedup benchmark**.
- Eight existing proxy frames decoded; one detector call returned three finite
  detections and five missing observations. Decoded-frame SHA256
  `1f394b58fc43505f3cb800f84260048a6dcc607c6894a18842846945632c55ff`.
  This proves bounded decoder/model execution, **not detection accuracy**.
  Complete proxy SHA256: `ca1fb9357fbc54cbe82aebc9c429d813671bd63b2e5984bd0b810d8c83ea0bc3`
  (`tracknet-proxy.sha256`).
- Fresh ONNX export failed with `ModuleNotFoundError: onnxscript`; no graph was
  published and no dependency was installed. Real ONNX numerical parity and
  TensorRT execution remain unverified.

Historical real-video evidence remains in the phase-2 report:27,744 cached frames
replayed from three recordings, outcomes unresolved; one bounded real TrackNet
Torch comparison also had identical tensors. Those earlier artifacts are not
relabeled as fresh current accuracy. Geometric target-court exclusion is not shuttle/event
accuracy. Labels, missing provider/export infrastructure and cross-process
orchestration are explicit blockers to broader validation; nothing was installed
or silently fabricated to clear them.

## Final preservation receipt

Final source/test-only Git patch SHA256:
`637b4202ecfece965391024ca089fbe42d55994b6df56a23a1ee1613acb846f2`.
It covers 74 source/test/harness files; docs are excluded to keep the fingerprint
independent of this receipt. The complete 86-path task manifest is in the final
[audit report](full-pipeline-audit-20261103.md). HEAD/branch and the real index are
unchanged. Package/lockfile hashes match the starting receipt; 17 unrelated tracked
deletions and user folders are preserved. The primary server remains at
`510b7039fee99b017a643bfcaf62804f0d9b7564` with `dist.old/` and `client-website/`
untracked; its port8010 health endpoint still returns `ok`. Cloudflared is absent.
Only the recorded disposable server, browser and SSH forwards are shut down.
