# Full pipeline phase 2 ledger

## Starting state and authorization

- Local branch `full_pipeline` began at `32a8295d9645d81bd1586a777541bb2f72c08bed`.
  Existing phase-1 changes were inspected and committed as `27e2a20` (22 scoped
  files), then pushed to `origin/full_pipeline` at the user's explicit request.
- Unrelated tracked deletions under `Design/production-prototype/`, web dependency
  edits, and untracked user folders remain local and uncommitted.
- The latest direct user request authorizes SSH, updating an isolated server checkout,
  and server tests/inference. It supersedes the phase brief's default no-SSH restriction.
  No credentials may be written into Git, scripts, documents or application logs.
- Server primary checkout remains on `main` at `510b7039fee99b017a643bfcaf62804f0d9b7564`,
  with untracked `apps/web/dist.old/` and `client-website/`; it was not switched or reset.
- Isolated server worktree: `/home/administrator/Desktop/sport-analytics/full-pipeline-phase2-20261102`,
  tracking `origin/full_pipeline`; each scoped correction was committed locally,
  pushed and pulled before server validation.
- Validation uses the existing `Sports_Analytics/.venv`, sources `../gpu-env.sh`, and
  explicitly places this worktree's packages first in `PYTHONPATH`. No environment
  installation/upgrade, model download, data replacement or deployment is authorized.
- Server runtime inventory: Python 3.12.12; PyTorch 2.14.1+cu126; ORT 1.29.0; two
  GTX 1080 Ti GPUs, 11 GiB each, with no compute jobs reported at initial inspection.
  Cloudflare PID 701600 was stopped before broader tests; it required SIGKILL after TERM.
- Phase-1 targeted tests: **44 passed**. Baseline including research tests:
  **1,148 passed**, 12 existing Starlette deprecation warnings. Server logs are
  under `../full-pipeline-validation-20261102/`.

## Ownership and dependency order

Author code locally; transfer commits through Git. The orchestrator exclusively owns
`bai_badminton/engine.py`, perception integration, shared contract decisions, evidence
reports and server execution. Agents author focused tests first and wait for recorded
server red results before changing production code. No agent installs or runs inference,
uses SSH independently, commits shared work or edits another owner's files.

| Issue | Evidence classification and existing behavior | Expected correction / owner | Regression and runtime gates | Status |
|---|---|---|---|---|
| Reconstructed shuttle visibility reaches rally FSM | Confirmed by server RED: reconstruction could start/extend play | Rally agent plus root: observed mask `vis & ~interp`; velocity requires adjacent observed positions | Initial temporal RED: 33 failed / 4 passed; subsequent focused gates passed | Implemented; final suite passed |
| Non-replay cuts retain stationary/rally state | Confirmed by server RED: old scene history survived | Rally agent: `on_discontinuity(frame)` closes pre-boundary evidence before new contacts, prevents merges, clears history | Open/closed exchange, tentative end, replay, short/long gaps | Implemented; final suite passed |
| Post-contact flight/receiver context crosses cuts | Confirmed by server RED | Temporal agent/root: shared half-open segment bounds, clipped motion, unknown cross-segment flight/receiver; next hit remains an exclusion bound | New segment cases plus existing stroke/contact suites; 28-test correction gate passed | Implemented; final suite passed |
| Raw/stabilized coordinates mix during recovery | Confirmed by server RED; mismatched chunk reference was treated as raw fixed-camera input | Root: private coordinate epoch/context and temporal validity; preserve raw overlay rows; reject incompatible camera pose | Pose loss/recovery, singular/nonfinite transforms, references, calibration, alternate views | Implemented; 24 camera/outcome tests passed |
| Delayed outcomes use replacement calibration | Independent review found old pixels reinterpreted through new homography; RED changed in to out | Root: retain each frame's actual calibration reference and trim with buffers | Shifted recalibration reproducer failed, then passed with camera/outcome gate | Implemented; final review closed |
| Bounded history and preceding cut | New integration review found trimmed start crash and overly broad outcome lookback | Root: unavailable start context stays unknown; outcome lookback begins within current rally | Long motion-only exchange and short completed post-cut rally regressions | Implemented; integration gate passed |
| ONNX/checkpoint artifact lifecycle | 27 cache/snapshot/provider cases failed before correction | Cache agent/root: verified snapshot handoff, digest and ORT IO validation, content-addressed graph plus atomic manifest, lazy graph-digest provider selection | 62 cache/integration tests passed; real Torch CUDA tensor parity exact | Implemented; fresh real ONNX export blocked by missing `onnxscript`/`onnx` |
| First-use pin publication | Separate RED reproduced failed-write and cross-process races | Cache agent: OS advisory transaction lock and fsynced atomic pin replacement | 6 pin/snapshot tests passed, including independent processes | Implemented |
| Native TensorRT engine/timing caches | Compatibility directory alone could not guarantee native build publication safety | Cache agent: persistent caches explicitly disabled by default; internal compatibility namespace requires complete build identity and a lifecycle-aware owner | Version/hardware/model/precision and incomplete-identity tests; no native engine built | Safe default implemented; native cache lifecycle unvalidated |
| Evaluation eligibility and label readiness | RED: unknown/partial review semantics ignored, invalid winners accepted, annotation file reread, media bytes unchecked | Evaluation agent/root: strict v1 semantics, optional timeline/proxy bindings, actual source/proxy hashes, one annotation snapshot | 73 failed / 45 passed before fix; 118 passed after fix | Implemented; split independence still a protocol requirement |
| Full-video accuracy | Existing weights/proxies/caches inventoried; no new independent reviewed target labels | Root: same cached observations replayed into fresh baseline/candidate stores; 27,744 frames complete | Diagnostic counts changed; all compared outcomes unresolved; no accuracy claim | Labelled accuracy unavailable |
| Integrated application | Isolated localhost test server, fresh disposable data, no production reanalysis | Root: build, upload, proxy/HLS, engine, API export and browser playback | Build passed; 240/240 frames analysed; browser readyState 4, no media/console error | Smoke and final Python suite passed |
| Legacy archive extraction | Source audit: `onnx-zip` extraction can reuse stale files; lexical containment is weak | Existing path API unchanged; new snapshot API rejects archives | Separate digest-bound extraction and traversal regression work required | Explicitly outside completed TrackNet cache scope |

## Validation plan

1. Run phase-1 focused tests and broader server baseline before further changes.
2. Commit only new focused regressions, pull them into the isolated worktree, and record
   expected failures. Implement the smallest coordinated fixes locally.
3. Commit/push/pull each scoped correction; rerun its tests, then related suites.
4. Inspect model/export/provider behavior using existing trusted weights and bounded
   synthetic inputs; do not infer model accuracy from tensor parity.
5. Exercise the integrated application on localhost/SSH forward, with existing session
   results preserved and new validation artifacts outside user sessions. Report missing
   labels, unsupported providers and runtime failures explicitly.

## Evidence and current limits

The final integrated command is `python -m pytest -q engine/tests
sports/badminton/tests agents/tests apps/api/tests research/tests`; **1,307 passed**
with 12 existing Starlette deprecation warnings in 203.20 s, exit 0, at code revision
`5f9d0a4`. Evidence is in `phase2-verified-full.log` and
`phase2-verified-full.exit`. An earlier default-path run exposed four
fixtures without required timeline/camera evidence; their 45-test gate passed after
correction. The negative attribution fixtures now also retain valid flight context,
so unknown results must arise from the person-evidence condition under test.

The real GPU probe used the existing pinned TrackNet checkpoint, no download or
installation. Both revisions returned finite FP32 `[1,8,288,512]` heatmaps with
maximum and mean absolute difference **0**. One measured forward after one warmup
was 21.189 ms baseline / 20.892 ms candidate; this is not a throughput benchmark.
Eight existing proxy frames decoded and one detector call completed. Real fresh
ONNX export failed with `ModuleNotFoundError: onnxscript`; no graph was published.

See [full-pipeline-phase-2-report.md](full-pipeline-phase-2-report.md) for exact
commands, replay counts, evidence paths, schema migration and remaining gates.
