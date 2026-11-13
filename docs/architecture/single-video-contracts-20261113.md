# Single-video validation: synthetic temporal-contract workstream — 13 November 2026

Base source: `e558fd9`, branch `engineering/deep-pipeline-overhaul-20261113`.
Owner: `validation_contracts`. The root integration owner controls the selected
video, application, shared contracts and final acceptance. This workstream used
only synthetic arrays and temporary SQLite stores. It performed no media decode,
frame extraction, inference, historical-video reprocessing or cached-video replay.

## Context and ownership

Read `AGENTS.md`, `CLAUDE.md`, `CODEX.md`, the deep-overhaul report and all three
linked workstream reports. Reviewed the prior class-context causal finding,
freshness/identity requirements, missing-data behavior and current implementations
of participation, singles identity, contact windows, contact reliability,
classification/jump features and rally state. Historical reports are diagnostic
evidence, not fresh validation results.

Exclusive edits:

- `sports/badminton/src/bai_badminton/events/rally_fsm.py`
- `sports/badminton/tests/test_overhaul_temporal_contracts.py`
- This report.

No edits to the root-owned `engine.py`, `plugin.py`, shared components,
perception implementations, frontend, model profiles or historical artifacts.

## Residual-issue entry and implemented repair

| ID | Component | Evidence | Root cause | Severity | Dependencies | Improvement | Validation | Status |
|---|---|---|---|---|---|---|---|---|
| CONTRACT-RALLY-CONFIG-01 | Rally configuration/state | Source inspection and eleven failing synthetic cases | `RallyParams` validated FPS/stationarity but accepted zero/fractional start counts, zero/bool end gaps, negative lookahead/durations and nonfinite speed/merge values. Configurable component factories construct it from profile parameters. | Medium: invalid configuration can silently change or disable state transitions, or fail later | Every rally provider using shared `RallyParams`; downstream boundaries/outcomes | Require positive integer start-visible/end-gap counts; nonnegative integer lookahead; finite nonnegative speeds/durations; reject boolean FPS | Retained red11 failures, then green192 including existing temporal and integration controls | Fixed and validated for synthetic configuration contract; selected-video behavior belongs to parent run |

All valid defaults and numeric policies are unchanged. Zero lookahead, zero
minimum duration or zero merge duration remain explicitly supported nonnegative
configurations. This is fail-fast configuration validation, not frame/rally tuning
or an asserted cause of a historical sporting FP/FN.

## Overhaul regression coverage

The new test file contains25 synthetic cases:

- Four separate doubles episodes need the configured count of actual person
  observations; scheduled carries neither create episodes nor advance birth votes.
- A real detector tick without a matching person breaks a pending entry; a
  scheduled unsampled tick does not.
- Carry-only startup does not misclassify the first observed participant as a
  later entrant.
- Renderable carries cannot extend spatial rebind leases or teach appearance;
  a later replacement beyond the original observed lease remains unresolved.
- Anonymous but independently supported physical next-impact evidence can qualify
  a flight endpoint; missing/weak/reconstructed/stale/carried evidence cannot.
- Only exact-frame-stamped pose/racket data enters temporal arrays; original
  raw snapshots remain intact.
- A new motion-opened rally cannot terminate from pre-start idle rest.
- Jump evidence has consistent duration at25/30/60FPS and abstains with missing hips.
- Eleven invalid rally configurations fail before temporal state executes.

These are software/contract checks. They do not label physical athletes, contacts,
shots, rally boundaries, winner decisions or scores on any real video. They also
do not measure inference or end-to-end latency.

## Commands and retained execution evidence

All commands ran from
`/home/administrator/Desktop/sport-analytics/Sports_Analytics`, after
`source ../gpu-env.sh`, using the existing `.venv`.

Baseline inspected files were checked for video/model-loading/decoder access
before execution. No project-level `conftest.py` exists; the API-only conftest was
outside the selected tests.

```bash
source ../gpu-env.sh
.venv/bin/python -m pytest \
  sports/badminton/tests/test_participation.py \
  sports/badminton/tests/test_identity.py \
  sports/badminton/tests/test_participant_contact_evidence.py \
  sports/badminton/tests/test_contact_physical_evidence.py \
  sports/badminton/tests/test_rally_temporal_correctness.py \
  sports/badminton/tests/test_stroke_temporal_motion.py \
  sports/badminton/tests/test_contact_scene_boundaries.py \
  sports/badminton/tests/test_contact_pose_sampling.py \
  sports/badminton/tests/test_rally_recovery_cut_frontier.py \
  sports/badminton/tests/test_synthetic_observation_contract.py -q --tb=short

# New regression file against the original constructor:11 failures,14 passes.
.venv/bin/python -m pytest \
  sports/badminton/tests/test_overhaul_temporal_contracts.py -q --tb=short

# After the constructor repair, run the baseline list above together with:
# sports/badminton/tests/test_overhaul_temporal_contracts.py
# Result:192 passed in2.26s.

.venv/bin/ruff check \
  sports/badminton/tests/test_overhaul_temporal_contracts.py \
  sports/badminton/src/bai_badminton/events/rally_fsm.py --output-format concise
git diff --check
```

| Phase | Result | Retained log |
|---|---|---|
| Existing focused baseline |167 passed in2.33s | [baseline-focused.log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/baseline-focused.log) |
| New controls before constructor repair |11 failed,14 passed in1.01s; every failure was an expected missing configuration rejection | [overhaul-red.log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/overhaul-red.log) |
| Combined after repair |192 passed in2.26s | [overhaul-green.log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/overhaul-green.log) |
| Static lint and whitespace | Ruff and Git checks passed | Command output retained in task transcript |

The parent integrates these changes with the selected-video experiment. Focused
unit completion is not a replacement for real component initialization, source
inspection, frontend evidence or a fresh integrated video run. Full regression
suites were not run by this workstream because tests opening other videos would
violate the single-video restriction. No physical-accuracy or speed improvement
is claimed from these test timings.

## Follow-up: execution trace and analytics contracts

The root owner subsequently added `bai_engine.trace` for opt-in real-session
observability. This workstream owns only the new
`engine/tests/test_execution_trace_contract.py`; the trace implementation remains
root-owned. Source review identified inherited parent/frame context across nested
sessions, disabled inner sessions writing into active outer sessions, and an
uncaught stream-close error that could fail or mask analysis. Those findings were
sent to the root owner, who repaired them before the first test execution. Thus
there is **no reproduced failing trace run**; a historical filename containing
`red` must not be interpreted as a failed execution.

The13 trace cases exercise:

- Disabled tracing creates no artifacts.
- Source/session binding, frame range, input shape/dtype summaries, output counts,
  span parent references, nonnegative monotonic duration and honest host-wall semantics.
- Original provider exceptions are recorded and re-raised unchanged, and parent
  context is restored after exceptions.
- Large attributes are omitted within the metadata bound, and invalid/nonfinite
  metadata produces a visible write warning without failing analysis.
- Filesystem open/write failures remain visible; failed tracing does not retry
  noisy writes for each following span.
- New/disabled nested sessions do not inherit another video's context or emit
  into another video's trace. Outer context is restored afterwards.
- Stream-close failure neither fails otherwise-successful analysis nor masks an
  original processing exception, and emits an explicit close warning.
- Threaded sessions remain isolated and untrusted session IDs cannot escape the
  trace directory through path traversal.

The existing movement-direction tests and accepted-point analytics tests were
inspected before execution: they use synthetic coordinates and temporary SQLite
stores, with no videos or model forward calls. Movement direction, speed, elapsed
time, missing/teleport/track-switch handling and public units passed. Canonical
analytics and restoration preserve accepted versus provisional/unknown points.

```bash
source ../gpu-env.sh
.venv/bin/python -m pytest \
  engine/tests/test_execution_trace_contract.py \
  sports/badminton/tests/test_movement_direction.py \
  sports/badminton/tests/test_analytics_point_acceptance.py -q --tb=short
.venv/bin/ruff check engine/tests/test_execution_trace_contract.py --output-format concise
git diff --check
```

First combined run:36 passed in1.38s. The unchanged-behavior rerun after test-only
lint corrections also passed36 tests in1.30s. Logs:
[first passing execution](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/trace-movement-red.log)
and [final execution](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/trace-movement-green.log).
The `red` filename is historical naming only; its retained content reports36
passes. There was no trace/movement/point-acceptance regression in these checks.

These tests validate synthetic trace contracts and selected analytics boundaries;
they do not establish that real inference produced a trace, that UI rendering is
correct, or that any sporting prediction is accurate. Root-selected video and
browser evidence remain necessary for those acceptance decisions.

## Native-thread policy and broader synthetic regression

The root added `Settings.opencv_threads` and sets the native OpenCV pool before
interruption recovery or command-worker startup. New
`engine/tests/test_native_thread_policy.py` uses actual `LocalBus`, a temporary
`SessionRepository`, an empty model manifest and the real command thread. It
instruments the native setter, rather than changing global pools while checking
call order. Positive1/2/8 settings, invalid0/negative/fractional/text/nonfinite
settings and startup order at1/3 threads all pass: **11 tests in1.78s**.
[Native-thread log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/native-thread.log).

The initial broader selection statically excluded direct source-video access,
FFmpeg, model loading, retained fixture reads and real network/GPU tests. A
defensive `av.open` guard additionally prevented indirect media creation. It
selected132 modules but was gracefully interrupted after85.56s to release CPU
for video run02. **420 passed,27 failed,15 warnings** before interruption; this
was not a completed suite. One of those failures was the guard correctly blocking
`test_score_synchronization`'s indirect `create_score_fixture(media=True)` call
before opening or creating any media. That module is excluded from later runs.

| Failure group | Confirmed cause | Test-fixture repair and independent negative controls |
|---|---|---|
|22 automatic-individual assertions | Previously positive synthetic detector-run rows lacked per-person match proof; current `_continuous` correctly abstains on unknown matches | Declare matched observations only in the controlled positives; preserve carried/unknown inputs; add False/None person-match and missing/changed context negatives. Named output scope asserts actual unique match, while anonymous frame-only scope remains unchanged. |
| Reviewed four-player motion | Positive rows lacked detector-run/context fields; camera rows lacked context, so new geometry/provenance gates withheld travel | Explicit controlled camera/person context and current-match/run fields; parameterize missing match, unknown match, missing detector run, missing person/camera context and low camera quality. Invalid one-person evidence does not erase supported teammates. |
| Anonymous singles classification | Existing positive supplied no next physical endpoint, so new endpoint contract correctly abstained | New test-only `endpoint_support.py` supplies typed controlled-provider probable endpoint evidence and corresponding observed synthetic incoming/outgoing positions. The positive still requires a known class with no named hitter; missing/unsupported endpoint negatives retain valid geometry but require unknown class. |
| Doubles classification context | Positive fixture had no calibration, unknown person matches and no supported next endpoint; it also asserted the old underclaiming scope label | Initialize real synthetic calibration, explicitly declare current snapshots, supply typed endpoint and preserve nonunknown positive; independently remove match/birth/geometry or detector execution and assert abstention. |
| Moving-camera geometry | Test `move()` reconstructed `PersonObs` and dropped its `detector_matched=True` provenance, unlike the untransformed control | Use `dataclasses.replace` to transform geometry without erasing evidence ownership. Add an explicit transformed-provenance assertion. No homography algorithm or measurement tolerance changed. |
| Generated-media score fixture | Indirect media call escaped the initial lexical selection | Guard blocked it before media open; exclude the whole module rather than permit another video. This is a selection failure, not a product score failure. |

The five corrected fixture suites plus added controls completed: **103 passed
in29.96s**, using
`OPENCV_FOR_THREADS_NUM=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1` and the AV
media guard. All prior substantive failures in those five modules are resolved
without production-source changes or weakening their intended positive outputs.

The first correction attempt reported41 passes and3 API setup errors because a
concurrent frontend build removed `apps/web/dist/assets`; it stopped after the
third error. After the frontend build was complete/frozen, all103 cases passed.
That transient artifact race and its original log remain visible; no fake assets
or mocked successful app startup were substituted.

Changed test-only files: `test_automatic_individual.py`,
`apps/api/tests/test_four_player_review.py`, `test_anonymous_singles_context.py`,
`test_doubles_contact_fusion.py`, `test_engine_camera.py`, plus the controlled
test helper `endpoint_support.py`. The helpers declare synthetic observations;
they do not manufacture real-video outputs or certify sporting accuracy.

Retained evidence:
[initial broader log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/broad-synthetic.log),
[partial receipt and exact27 failed nodes](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/broad_synthetic_receipt.json),
[initial selection](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/synthetic_selection.json),
[transient build-race run](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/corrected-fixtures-first.log),
[corrected fixture run](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/corrected-fixtures-second.log).

The later curated stable selection defers29 concurrently changing perception/
scene/image modules and the generated-media module, and records individual test
outcomes immediately. Its separate result is reported by the root integration
owner; selection or collection alone does not imply a passing suite.

The curated stable run selected103 modules and completed1200 cases:
**1198 passed,2 failed,8 warnings in101.01s**. Both remaining failures are in
`test_streaming_contact_integrity.py`: later-shot known-class coverage and initial
service formation. Its generator's current joints lacked source stamps; generated
shuttle positions lacked observed-association provenance, and the baseline contact
provider supplied no explicit motion sensitivity. The test-only fixture now
declares those actual synthetic sources and selects the existing contact-evidence
adapter. That fixture repair remained unexecuted while controlled video run03
was active; no passing result is claimed yet.

An earlier curated attempt stopped after186 recorded passes because the external
per-node result writer used `Path.open` during the trace tests' intentional
filesystem failure injection. The writer now captures `builtins.open` before
test mocks. That was a diagnostic-harness error; its log is preserved and not
presented as a completed product-regression run.

[Completed curated run with two failures](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/stable-synthetic-attempt2.log),
[per-node outcomes](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/stable-synthetic-attempt2-node-results.jsonl),
[exact curated selection and exclusions](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/stable_synthetic_selection.json),
[preserved external-recorder failure](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/stable-synthetic.log).

## Rejected-rally interval provenance

After controlled video run03 completed, the root authorized one bounded change:
rejected short exchanges must remain diagnosable without becoming accepted
rallies. `RallyUpdate` now appends optional `cancelled_segment` after its existing
fields, preserving positional construction. `RallyFSM._finalize` retains the
exact rejected `RallySegment` with inclusive start/end, first contact and terminal
reason. `EvidenceRallyFSM` clears both cancellation fields when independent
short-exchange witnesses legitimately accept the segment.

A discontinuity at the exchange start has no preceding interval. It retains
`cancelled_start` with `cancelled_segment=None`, rather than invent a zero/negative
interval or include a frame from the new context. No duration, contact, gap,
merge or score threshold changes. Root owns persistence of these details on the
original provisional start's retraction; this workstream does not implement or
claim validation of that separate consumer until its focused tests execute.

New `test_rally_cancellation_provenance.py` covers8 cases: exact gap/cut/flush
rejections, boundary-without-prior-interval, old cancellation plus new start in one
update, ordinary accepted rally, accepted short exchange clearing both fields,
and legacy positional compatibility. Together with the two repaired streaming
positive cases, the targeted run passed **10 tests in1.55s**.
[Targeted cancellation/streaming log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/cancellation-streaming-first.log).

The streaming fixture repair is now exercised: source-stamped current synthetic
poses, exact generated observed shuttle coordinates and declared diagnostic
motion sensitivity restore the original positive service and later-shot behavior.
It does not substitute reference contact times, set class outputs or weaken any
production evidence gate.

The external result recorder now requires a distinct output path via
`BAI_SYNTHETIC_NODE_RESULTS` for each invocation. Ten targeted outcomes had been
appended by the earlier one-path recorder after the original1200-case run. The
combined bytes are retained, the original1200-row prefix restored, and the ten
new outcomes preserved separately; the recovery receipt discloses this explicitly.
[Recorder append recovery](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/node-recorder-append-recovery.json).

The first complete-selection retry stopped at its five-failure cap after **973
passes and 5 failures in 87.06s**. All failures were parameterizations of one
terminal-rest assertion comparing `asdict(RallyUpdate)` with the old three-field
dictionary. The expected dictionary now explicitly includes
`cancelled_segment=None`; the test still demands no start, no cancellation, no
finalization, unchanged state/history and rejection of the unsupported contact.
No terminal-state policy was changed to satisfy this assertion.
[Preserved capped retry](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/final-synthetic.log).

The admission record now also preserves additive `short_exchange_evidence`:
whether the existing option is enabled, the first retained observed-motion span
(or null), whether that span belongs to the candidate interval, retained eligible
contact-witness frames within that interval, and the policy status
`qualified_pair`, `disabled`, `motion_span_unavailable` or
`independent_pair_unavailable`. These describe retained policy inputs; they do not
claim exhaustive explanations for contacts rejected upstream. No admission
threshold or short-exchange override rule changed. Six additional cases exercise
disabled support, absent motion, ambiguous or missing contact motion, missing
simultaneous opponents and out-of-interval retained history.

Focused current-source checks, including the root's append-only cancellation
persistence integration tests, completed **56 passed in 7.91s**. The first
diagnostic assertions expected motion to begin at contact frame 5, but the
synthetic exchange actually starts from observed motion at frame 0; assertions
were corrected to the recorded span `[0, 2]`. That failed fixture-development
attempt remains visible separately.
[Current-source focused log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/cancellation-policy-corrected.log),
[fixture-development log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/cancellation-policy-final.log).

One subsequent command wrapper used unavailable `python` before sourcing the GPU
environment. Its preparation failed, leaving an empty module array; pytest then
default-collected the repository and the defensive AV guard blocked five
generated-media lifecycle fixtures before their media open. That rejected
invocation reported **194 passes and 5 setup errors in 4.61s** and is neither a
product-regression result nor a completed curated run. The wrapper now enforces
`set -euo pipefail`, uses the existing `.venv/bin/python` for preflight and refuses
to invoke pytest unless the module array contains exactly 105 entries.
[Rejected wrapper log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/rejected-empty-module-selection.log).

The final curated invocation uses this exact configuration, with a unique result
file and the media guard retained:

```bash
set -euo pipefail
source ../gpu-env.sh
artifacts=/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests
mapfile -t synthetic_modules < "$artifacts/final_synthetic_selection_v2.txt"
if (( ${#synthetic_modules[@]} != 105 )); then exit 2; fi
OPENCV_FOR_THREADS_NUM=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
BAI_SYNTHETIC_NODE_RESULTS="$artifacts/final-synthetic-v2-node-results.jsonl" \
PYTHONPATH="$artifacts:$PWD${PYTHONPATH:+:$PYTHONPATH}" \
timeout -s INT -k 10 170 .venv/bin/python -m pytest \
  -p synthetic_media_guard "${synthetic_modules[@]}" -q --tb=short --maxfail=5 \
  > "$artifacts/final-synthetic-v2.log" 2>&1
```

The exact module list, explicit deferrals, thread settings and source hashes are
retained in
[final selection v2](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/final_synthetic_selection_v2.json).
This run exercises synthetic contracts, APIs and temporary persistence. It does
not establish real-video accuracy, model invocation, browser behavior or coverage
of deferred scenarios.

Final result: **1,216 passed, 8 warnings in 108.33s**, completing all 105 selected
modules. The result recorder contains exactly 1,216 passing call outcomes. All
eight warnings are FastAPI's deprecation of the old HTTP 422 constant. The
original 27-failure interrupted run, two streaming fixture failures and additive
dataclass assertion failures are resolved in this curated set; no unexplained
failure remains among these cases. Deferred modules and real-video accuracy are
not promoted to validated by this result.

[Final passing log](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/final-synthetic-v2.log),
[individual outcomes](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/final-synthetic-v2-node-results.jsonl),
[final receipt and owned-source hashes](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/final_synthetic_receipt_v2.json),
[rejected-wrapper receipt](/home/administrator/Desktop/sport-analytics/single-video-validation-20261113/contract-tests/rejected-empty-module-selection-receipt.json).

The workstream released CPU and froze production/test source after this run for
the root's controlled video run 04. Report and receipt writing afterward do not
change the exercised implementation.
