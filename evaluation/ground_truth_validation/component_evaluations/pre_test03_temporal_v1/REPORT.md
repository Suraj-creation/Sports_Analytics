# Pre-Test3 temporal chain: confirmed reconstruction integration defect

The approved isolated candidate fixes a reusable provenance/dataflow defect in
the current engine. It does **not** change profile thresholds, make missing
shuttle frames observed, classify unknown strokes by guessing, or establish
physical contact/trajectory accuracy. Full cached Test1–2 engine regression was
**not performed**: the existing runner's source-root/raw-input guards remain
enforced, and Test2's downloaded raw source was intentionally cleaned up after
the completed benchmark. Root will validate integrated changes with genuine
candidate-native fresh Test1/2 plans/runs. No Test3 data was accessed.

Candidate checkout:
`/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111`,
starting at `dacc05e`. Main baselines, annotations, evaluation logic and prior
reports remain untouched. Read `AGENTS.md`, `CODEX.md` and `CLAUDE.md` as required.

## Verified defect and exact dataflow

1. Perception emits raw image shuttle evidence with `status="missing"` and
   `selected_xy=None` when no shuttle is accepted. This correctly invents no
   coordinate. `FramePerception` and the retained cache preserve that raw fact.
2. Engine `_append()` buffers selected observed pixels separately from the typed
   raw evidence. `_window()` runs the existing bounded `shuttle_post.process()`:
   spike removal, at most25 missing frames, at least two observed anchors per
   side within five frames, bounded implied speed and moving anchors.
3. That independent postprocessor explicitly sets `interp=True` for estimated
   temporal context. Contacts, post-contact speed and outcome decisions exclude
   these samples from their observed masks.
4. The old `_window()` then cleared **both** visibility and interpolation whenever
   raw evidence status was anything other than `observed`. Ordinary valid raw
   absence was erased alongside conflicting/invalid evidence. Consequently
   modern raw-missing samples could never reach the existing typed
   `RECONSTRUCTED`/`continuation_supported` branch. Identical legacy frames without
   association metadata retained that context.
5. Existing `EvidenceRallyFSM`/`rally-evidence-v2` explicitly supports optional
   independently bracketed reconstruction; its default factory enables it.
   The current benchmark instead selects tracklet evidence with
   `use_reconstruction=False`, which is preserved unchanged. The failure is an
   integration inconsistency, not a reason to switch that policy for these videos.

Source anchors:

- [Engine window composition](../../../../../test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/engine.py)
  (candidate `_window`, around1420).
- [Postprocessor contract](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/perception/shuttle_post.py)
  (`Track`, `fill_gaps`, `process`).
- [Explicit reconstructed continuation](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/events/rally_evidence.py)
  (`step_evidence`, around294).
- [Observed-only trajectory/contact contract](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/src/bai_badminton/events/contact.py)
  (`score_frame`: `t.vis & ~t.interp`).

## Approved narrow correction

The candidate engine preserves marked bounded reconstruction for ordinary raw
absence. It builds a **private postprocessing barrier** before and after each
ambiguous, invalid or association-rejected sample and each temporally invalid
frame. This also stops neighboring missing samples from interpolating across a
contradictory frame. Merely clearing that one contradictory point after filling
would leave its neighboring estimates contaminated.

These interpolation barriers do not alter the original scene/coordinate
`break_before` array returned to temporal consumers: no invented camera cut,
FSM reset or episode change. Raw caches, selected coordinates, current detector
flags, pose/racket stamps and actor identities are untouched. The existing
25-frame/five-anchor/speed policies are unchanged. Raw absence remains absent;
derived context remains reconstructed and cannot produce observed contact,
post-contact velocity or terminal landing evidence.

See [engine-only patch](candidate_engine_only.patch) and
[final source/test receipt](candidate_receipt_v2.json). Root exclusively owns
`plugin.py` and the semantic pipeline identity bump; no conflicting plugin edit
was made by this agent.

## Deterministic RED/GREEN evidence

The original current production source gives **2 failures /11 passing controls**:
the same bounded coherent raw-missing gap loses reconstruction in both singles
and doubles. Legacy no-association input retains it; conflicting states remain
excluded. [Original RED output](expanded_contract_RED.log).

The new17-test regression file adds actual engine/provider output checks:
explicit reconstruction enabled yields one continuously supported rally through
a24-frame gap; disabled preserves two intervals. Both singles and doubles behave
the same and emit no fabricated contacts, strokes or points. Additional negative
controls cover ambiguous/invalid/rejected samples inside missing runs, scene
cuts, content epochs, replay changes and invalid views.

The current candidate passes **204 focused tests in4.88s**, including existing
engine context, typed rally support, observed motion, shuttle association,
physical-contact provenance and post-contact stroke-motion tests.
[Final GREEN output](focused_GREEN_v2.log). Ruff checks pass for the changed
engine and new test. The new regression is
[test_missing_association_reconstruction.py](/home/administrator/Desktop/sport-analytics/test03-pipeline-improvements-20261111/sports/badminton/tests/test_missing_association_reconstruction.py).

## Full retained-cache window diagnostics

This is a hash-verified **full-array source-cache window diagnostic**, not full
streaming engine replay or fresh neural inference. It uses retained selected
pixels, exact source context and registered camera transforms, with the original
postprocess and continuation functions. Full engine/FSM/state-feedback proof
must come from the separately orchestrated cached regression.

| Population | Frames | Old reconstructed samples | Candidate reconstructed samples | Supported groups /samples under existing continuation rule | Observed-mask changes |
|---|---:|---:|---:|---:|---:|
| Test1 preserved improved source |17268|1|827|177 /553|0|
| Test2 completed fresh improved source |29296|9|2204|335 /1321|0|

There are206 candidate reconstructed groups in Test1 and468 in Test2; not all
pass the existing stricter continuation rule. The old1/9 reconstructed samples
come from originally observed samples removed by spike processing and replaced
by estimates. Thus the precise defect concerns **modern raw-missing** samples,
not every possible reconstructed sample. Counts measure derived-context
availability, not recovered true shuttle detections or contact recall.

[Test1 diagnostic](test01_cache_window_review_v1.json),
[Test2 diagnostic](test02_cache_window_review_v1.json),
[executed helper](review_cached_reconstruction.py).
Every consumed cache digest is retained; no source video, cache, annotation or
prediction was edited.

## G69: what changes and what does not

The original Test2 reference interval is [26616,27668). The preserved pipeline
has a22-frame raw gap [27326,27348), ends the first prediction at27325 and starts
a second at27349. These machine observations remain documented in the
[temporal baseline diagnosis](../../test_02/diagnostics/temporal_root_cause/REPORT.md).

Under the candidate's corrected window contract, all22 gap samples carry
`interp=True`, `observed=False`, with the **existing** continuation predicate
supported. No source pixel or peak was recovered, no midpoint contact was
invented, and the lower reacquired branch remains a possible racket/head/hand
distractor from source review. The diagnostic cannot certify a real airborne
shuttle trajectory through the gap.

The benchmark profile's `use_reconstruction=False` remains false. This patch
therefore does not by itself authorize claiming the G69 split repaired or a
higher benchmark F1. Changing that option would be a separate experimental
policy intervention requiring the same positive/negative cases, source review,
full metrics and regression scope. A larger merge timeout was not proposed.

## Contact → classification → outcome limits

The actual latest Test2 fresh output has816 estimated contacts/strokes,
586 unknown strokes and230 heuristic class estimates. Its unknown reasons are
576 `missing_required_evidence` and10 `unresolved_initial_contact`.
Physical-impact evidence reports426 insufficient fresh-player cases,
160 unresolved association cases,71 lacking coherent motion-change support,
46 without a fresh swing/racket-overlap cue and113 probable heuristic impacts.
Attribution is527 insufficient versus289 geometrically probable; this does not
identify named athletes. These are policy/reason counts, not independent impact
or hitter ground truth.

The current dataflow explains why filling a temporal gap is not a class fix:

- Contact candidates require a real noninterpolated shuttle at the exact frame
  and observed incoming/outgoing motion. Reconstruction cannot create them.
- Named actors remain unknown without verified roster/track binding. Provisional
  geometry can support classification only with current or explicitly bracketed
  source context; propagated boxes are not fresh detections.
- Rules require observed post-contact speed, valid flight duration, supported
  hitter geometry for a non-serve, and resolved initial-contact context. Missing
  inputs remain unknown. Reconstructed samples are excluded from speed fitting.
- Outcomes exclude cut/EOF-only terminal intervals, invalid geometry and terminal
  motion without consecutive observed rest. OCR observations, anonymous sides
  and generated winner annotations do not independently authorize named points.

All75 Test2 winners and the accepted score sequence remain unknown/empty in the
preserved fresh run. This fix does not manufacture winners or call that0–0.
Original Part2 has no exhaustive physical contact/hitter/stroke/landing labels.

## Already solved mechanisms and remaining priorities

The earlier Test1 stale recovery frontier defect is already fixed and must not
be investigated as new. Its proof explicitly did not establish that it caused
the14 Test1 boundary cases. Source-invalid openings, preparation/pickup spans,
short-candidate cancellation, independently unsupported terminal events and
annotation variants remain distinct.

The original quality design already requires acquisition independence and
observed-versus-reconstructed evidence separation. Current
`perception/pipeline.py` already runs the racket stage when permitted people are
present even if the shuttle is missing; the old contact-study conjunction is
historical and is **not** another pending code fix. Its observed gap/onset ideas
remain optional candidate methods with explicit timing uncertainty, not a reason
to mark a midpoint or wrist swing as a confirmed touch.

Next work should preserve this order:

1. Root reviews the narrow patch, versions the semantic composition and runs
   genuine fresh Test1/2 evaluations with NEW plans rooted in the isolated
   candidate, including exact contact, stroke, rally and scheduling differences.
   Compare preserved original metrics read-only; do not rebase an old plan or
   bypass its source/raw-input guards. Cached replay was not performed here.
2. Independently investigate the actual upstream G69 raw absence/branch conflict,
   Test2 wrong-player population and propagated-box failures. Preserve default
   policies while evaluating any validated perception change with fresh inference.
3. Use reviewed physical target-person/contact/trajectory subsets and hard
   negatives before adopting reconstruction policy, gap/onset contact models,
   looser temporal gates or class/outcome interventions. Do not suppress difficult
   ambiguous candidates solely to improve counts.

## Cache/provider identity and preservation

The raw perception payload schema did not change; re-encoding or overwriting its
codec cache would obscure preserved evidence. Window composition **did** change,
so prior semantic checkpoints/events must not silently resume under the new
implementation. Root owns the explicit badminton pipeline-version/fingerprint
bump and corresponding stale/fresh identity regression. Pure provider math and
thresholds did not change; artificially renaming a neural checkpoint would be
incorrect. Record the exact engine/test hashes and full candidate diff even if
Git HEAD remains the same during development.

Production diagnostic decode remains explicit `diagnostic=True`; the ordinary
runtime still requires sequential fresh perception. A later full cached replay
must declare the source intervention and retain original completion/cache/model
bindings, reference populations, old metrics, new outputs and every failure log.

The initially considered source-copy replay was stopped before execution:
the old helper resolves recorded absolute source paths against its repository
root and requires the original raw video hash. Changing those bindings or
asserting fresh completion from retained caches would misstate its verification
scope. No alternate loader, metadata rebasing or synthetic completion receipt
was implemented. The retained Test1 raw file still exists at
`data/benchmarking/test1/Test1_Full_rev.mp4`; Test2 must be restored for the later
genuine fresh run, sequentially under root's orchestration.
