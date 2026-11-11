# Current Test 2 scene/OCR review — completed baseline evidence

This review consumes published complete MessagePack files and retained source
images without opening live SQLite or changing production. Separate standalone
CPU OCR experiments are disclosed in `ROI_ACQUISITION_REVIEW.md`; they do not
replace the baseline's predictions. Immutable per-window snapshots retain their
original hashes and prefix status. Their separate strict completed-run binding
has now passed, as recorded at the end of this report.

## Acquisition

`inspect_atomic_prefix.py` samples windows0–120,7698–7708,11335–11358,
22890–22960 and23634–23644 once the complete relevant cache chunks exist.
`prefix_status.json` records readiness; `prefix_watcher.log` records capture
progress. It reads only overlapping60-frame chunks, verifies stable stat/bytes
and complete ordered frame ranges, and retains every consumed chunk SHA256.
The initial prefix is not an independently verified run frontier.

Original-source frames were preserved by the annotation reviewer, supplemented
by eleven small exact-PTS samples in `extra_source_panels/`. The supplemental
decoder used one thread and keyframe seeks. Every retained frame's rational PTS
exactly identifies its zero-origin30fps frame, with source/output pixel hashes.
No large auxiliary video was created. Current720p positions over resized original
source pixels are a review overlay, not proof that inference proxy pixels are
byte-identical to the original resize.

## Source-supported controls reviewed before current windows mature

- **7701–7704 /256.700–256.800s:** the red near player continues a lunge while
  the blue far player moves continuously. Court/background and displayed14:17
  remain consistent. These adjacent images support the inherited no-reset
  control at7703; the agent interpretation is diagnostic, not an independent
  exhaustive scene label.
- **11345→11346 /378.166667→378.200000s:** the red player at the far-right court
  exit and blue player near the lower-right boundary abruptly become centered
  on court. The apparent current scoreboard column changes4:0→5:1 while the
  historical-game column remains16:21. This supports a same-camera edited source
  transition. A one-frame source change does not specify which omitted points
  occurred or establish PlayerA/B mapping.
- **23638–23640 /787.933333–788.000000s:** the near blue player continues walking
  with head lowered while the far red player waits/repositions, displayed9:15
  unchanged. This supports the inherited no-reset control at23639. The images
  look close in motion but are not byte-identical; no exact duplicate is claimed.
- **22924 /764.133333s:** the retained original fixed-crop panel visibly contains
  AXELSEN/ANTONSEN and separate SXFI/LIVE branding. The recorded historical OCR
  lacks the upper current digit; current deterministic parser appropriately
  abstains on that fixture. Actual fresh readouts are reviewed separately when
  the new cache reaches this time.

## Current published startup window

The immutable `startup/prefix_snapshot.json` covers0–120 and was captured when
the highest published cache ended1499. The content epoch remains0 across the
examined frames53/77/82/95/96/101/120. Raw shuttle is absent at53 and present with
observed association at77,82,95,96,101 and120. Two current tracker rows exist at
those post-start frames; a fresh detector ran at96 and120, whereas several
intermediate rows are propagated. No OCR readout occurs in the overlapping
initial chunks.

This is a perception/cache observation only. It does not prove that candidate
format confirmation preserved or canceled a semantic rally: the final event
ledger and source-bound semantic trace are required to verify that behavior.
No live database was opened to obtain an early event answer.

## Completion gate

After the worker and parent receipts report genuine completion, use
`research.production_external_semantic_replay.load_finished_input()` against the
actual run/session. Verify every captured chunk digest against that completed
catalogue and verify actual final source/session/proxy bindings. Retain prefix
snapshots unchanged; add a separate completion receipt and final scene/OCR
summary. Do not call the current windows completed merely because their own
frames are present.

## Current prefix7703: inherited scene veto executes correctly

The immutable `false_barrier_7703/prefix_snapshot.json` covers7698–7708 and was
captured from published caches. At7703 the actual raw hypothesis is true, but
the source-bound current detector decision is `no_barrier` with reason
`complete_current_layout_correspondence`, matched pairs`[[0,0],[1,1]]`, and
detector frame7703. Content epoch9 is unchanged across the entire reviewed
window. Track episodes4 and2 remain, with fresh detections at7698,7703 and7704;
the other rows retain their explicit propagated status. Raw shuttle and selected
association remain observed throughout this window.

The source overlay at7703 shows boxes around the two playing athletes during
the continuous near-player lunge. The current source-bound OCR rows at7684 and
7714 read `AXELSEN14 / ANTONSEN17`, consistent with the visible displayed column
in the selected source frames. This is sampled text/continuity agreement, not
independent all-frame OCR accuracy or sporting identity validation.

Thus the new actual execution confirms the inherited false-reset correction in
this window. No additional code repair is justified for7703. Full-run completion
and exact final catalogue binding remain pending; this section remains prefix
diagnosis.

## Current prefix11346: missed source edit persists

`missed_edit_11346/prefix_snapshot.json` retains11335–11358. Current view is
`main`, calibration `VALID` and content epoch13 throughout. Track0 is the sole
returned person through11345; its overlay follows the red athlete exiting near
the far-right court boundary. The blue athlete is visibly partly outside the
near-right court area and is not returned as a track in that final pre-edit view.
There are no returned tracks at11346/11347, followed by new episodes3 and4 at
11348. Raw shuttle is missing through11347, then observed after11348.

The passive-diagnostic frames11335–11341 explicitly retain raw scene
`status=unknown`, `hypothesis=false` and reason
`two_to_four_prior_regions_required`. At11346 there is no retained raw hypothesis
or layout decision. Absence of detailed passive telemetry at that exact frame
does not prove every internal scalar was retained; it does establish that no
positive raw hypothesis/decision was published. Content epoch remains unchanged
across the visible edit.

Source11345→11346 shows the abrupt athlete-position and displayed4:0→5:1 change
described above. The actual current prefix therefore still exhibits the
documented missed-acquisition limitation. The selected observer cannot trigger
current detector corroboration from only one prior tracked region. This is a
source-supported missed observation-episode boundary, not evidence that its
unchanged court homography is geometrically wrong in the same camera view.

No threshold/minimum-region change is proposed from this one example. The
visibly out-of-court athlete also illustrates why blindly treating a missing
track or single actor motion as a cut would be unsafe. A new independently
supported cue and explicit negative controls remain necessary. No OCR reading is
present in the two cache chunks overlapping this narrow window; a score-change
observation was not invented from the visible pixels.

## Current prefix22924: actual crop improves OCR over the full-corner probe

`branding_22924/prefix_snapshot.json` retains22890–22960 plus the OCR records
from overlapping chunks. The actual current run returns `AXELSEN9 /ANTONSEN12`
at22864,22894 and22924;22924 confidence is0.96547. The selected source image
visibly agrees with9:12. This confirms the inherited branding ownership repair
in actual new execution and preserves a positive control: standalone full-corner
22924 does not recognize the upper current digit and abstains, whereas the
actual successful current crop returns the digit.

The returned9:14 at22954 is source-supported, not an established OCR error.
`score_jump_22946/` preserves original frames22945,22946 and22954 with exact PTS
and pixel hashes. At22945 the athletes walk toward the right and the displayed
current column is9:12. At22946 they abruptly reappear centrally preparing to play
and the column is9:14;22954 retains9:14. Actual cache has a raw hypothesis and
`barrier/raw_change_and_current_layout_discontinuity` at **22946**, changing
content epoch26→27. This is an additional source-supported positive edit control
for the current scene policy. A visible+2 across an edit is not one accepted
point or a justification to invent two intervening rally winners.

The ROI counterfactual should therefore **not be adopted as a Test 2 fix**:
scheduled gap replay produces no new readings, and full-corner-only acquisition
would lose this actual22924 positive readout on the sampled pixels. Its generic
crop hazard remains a separate future engineering issue, with current numeric
fusion/missing-digit and layout ambiguity limits explicitly retained.

## Current prefix23639: second inherited scene veto executes correctly

The final requested immutable window23634–23644 is retained. At23639 raw
`hypothesis=true` again receives an exact-current `no_barrier` decision with
`complete_current_layout_correspondence` and matched pairs`[[0,0],[1,1]]`.
Content epoch28 stays unchanged across the window; episodes0 and1 persist.
Fresh detector observations exist at23634,23636,23638,23639,23640,23642 and23644,
with propagation explicitly retained in the intervening rows. The observed
reset-veto action agrees with the reviewed continuous waiting/walking source.

Overlapping source-bound OCR records23584,23614,23644 and23674 read9:15, matching
the displayed sampled column. Five supplementary overlays23637–23641 were
created from exact-PTS original panels; their independent hash receipt is
`false_barrier_23639/additional_source_overlay_receipt.json`. The original prefix
snapshot remains unchanged.

The watcher exited cleanly after retaining all five requested windows. This
completion describes **the requested prefix evidence capture only**. The full
29,296-frame execution and strict completed-catalogue binding remain separate
gates; no all-video score or component accuracy is inferred here.

## Later G69 assignment

The requested window27290–27400 was subsequently added and retained, bringing
the snapshot total to six. Its dedicated report is `g69_gap_extended/REVIEW.md`.
Actual raw-provider absence spans27326–27347, with all15 retained candidate peaks
below the unchanged0.5 threshold and allowed by the mask; association has no
accepted raw coordinate to reject. Reacquisition is27348, followed by a lower
branch and a competing upper/lower raw selection at27354. Source samples support
ongoing player activity and unchanged16:16, but no independently labelled shuttle
trajectory. Completed semantic terminal/reopen behavior is the root orchestrator's
separate trace investigation.

## Strict completion binding: passed

The actual worker `run/inference.json` and parent `run.executor.json` both report
completed, with parent worker exit0. On2026-11-11,
`verify_completed_snapshot_binding.py` successfully invoked the existing strict
`load_finished_input()` guard for `UPLOADTEST2`, validating the original source,
canonical proxy, genuine parent/worker receipts, **29,296 frames and489 complete
catalogue chunks**. It then verified that every consumed chunk SHA256 from all
**six immutable snapshots** equals its corresponding completed catalogue digest
and unchanged file bytes.

The receipt is `completed_snapshot_binding.json`; the execution log is
`completed_snapshot_binding_execution.log`. Source/proxy hashes, completed input
receipts, each snapshot hash/window and separate standalone CPU report hashes
are retained. No original prefix snapshot or baseline output was rewritten.
The earlier “prefix” labels remain truthful capture-time provenance; these
observations are now additionally bound to the finished baseline.

The supported completed-baseline findings are therefore:

1. Inherited current-detector vetoes work at7703 and23639 without erasing track
   continuity. The visible source controls support those no-reset decisions.
2. The visible edit22946 is positively detected with epoch26→27; source9:12→9:14
   explains the later OCR reading without inventing unobserved points.
3. Actual current OCR22924 returns athlete-labelled9:12. The old branding21:12
   failure is resolved in current execution; full-corner-only is a worse sampled
   alternative here and is rejected.
4. Missed edit11346 persists under the one-prior-region acquisition limitation.
   Detector execution occurred; absent returned tracks are not automatically
   raw detector misses. No new safe scene threshold repair was established.
5. The G69 raw dropout/competing-selection issue remains source-bound perception
   evidence, with final temporal consequences evaluated separately.
6. ROI growth has a real generic engineering hazard, but105-call scheduled
   actual-pixel replay reproduces this baseline's gap exactly and rejects stale
   ROI as that gap's explanation. The isolated alternative yields no coverage
   gain and is not adopted. Fused/missing numeric columns remain unresolved OCR
   acquisition/recognition limitations, not fabricated sporting scores.

No new production repair was made by this reviewer. Existing deterministic
parser/provenance tests37pass and scene/cache/probe tests54pass. The isolated
full-corner controls3pass; the explicitly retained current ROI-expansion RED
contract has1failure/2controls passing and documents a separate unfixed generic
hazard. None of these counts is physical component precision, recall or score
accuracy. Root-owned baseline matrices, code changes and regression evaluations
remain separate deliverables.
