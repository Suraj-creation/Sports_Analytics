# Test1–2 source-driven player perception corrections before Test3

Two concrete implementation defects were reproduced and corrected in the isolated
`test03-pipeline-improvements-20261111` candidate worktree. The main baseline,
original annotations, prediction matrices, checkpoints, numerical profile and
installed environment remain unchanged. This report covers unit regressions and
bounded real-source component probes; complete fresh Test1/Test2 end-to-end
regression remains a separate requirement before promotion or Test3.

## The actual path and verified causes

The selected tracking provider composes RFDETR proposals → court admission →
ByteTrack episodes → pose/appearance. The perception pipeline supplies preceding
returned people to the content-continuity observer, which can acquire a detached
current detector probe before erecting a temporal/tracking barrier. Thus losing
or admitting a person can affect both current player evidence and later scene
acquisition. Raw track episodes are not named athlete identities.

### 1. The configured first observation was discarded

`PlayerTracker` requests `minimum_consecutive_frames=1`. Installed trackers2.6.1
counts a newborn detection as successful observation1, but its birth hook always
returns an unassigned ID; the application discards negative IDs. A new high-
confidence court detection therefore disappears until another matched detector
call, despite already meeting the requested observation count.

The independent [upstream ByteTrack documentation](https://github.com/roboflow/trackers/blob/develop/docs/trackers/bytetrack.md)
states that a setting of1 gives immediate confirmation. That mutable branch is
contract corroboration; the actual installed implementation/version and file
hashes are pinned in [upstream_contract.json](upstream_contract.json). The
existing dependency's [official license](https://github.com/roboflow/trackers/blob/develop/LICENSE)
is Apache2.0. No package or environment was replaced.

The correction is a small backend adapter. It calls the original birth hook,
verifies the exact ordered binding between appended detections and newly created
tracklets, and uses the original allocator only when the existing configured
observation minimum is met. Backend association, low-confidence recovery,
timestamps, lost-track pruning and minima≥2 remain unchanged. An incompatible
birth mapping fails explicitly rather than assigning another observation's ID.
It creates a visual episode ID, not a verified person identity.

### 2. Outside continuity renewed its own court authority

`_court_tracks` retained a timestamp and observed box. Every unique fresh match
updated both fields, even if the current box passed only through an earlier
outside-continuity exception. Consequently the nominal one-second court history
could renew indefinitely on a spectator after an episode handover.

The source chain is exact. At5956, the far athlete's box is approximately
438.1,153.1–491.9,274.2. After the same-camera edit, the official's5958 box is
447.2,153.2–484.5,206.0. Their IoU clears the unchanged0.3 continuity gate. The
fresh official lies outside both strict and padded court, but its inherited
history subsequently renews every observation through6492 and beyond.

The correction distinguishes the **last actual court-supported timestamp** from
the **latest matched spatial continuity box**. A current matched detection within
the existing padded court renews the timestamp. An outside observation can move
the continuity box while the original lease is valid; it cannot renew that lease.
No ROI creates no court anchor. Both detector ticks and scheduled carried frames
expire the same existing one-second lease. No court dimensions, IoU threshold,
confidence threshold or duration was fitted to a test video.

This preserves moving airborne/runoff continuity: successive outside boxes can
match each other even after they no longer overlap the original anchor box.
The positive tests explicitly exercise that motion. In the inspected source,
the far athlete's last padded-court observation before the handover is5924;
its timestamp is not refreshed by subsequent outside boxes. Candidate5958 therefore
contains the two current athletes and excludes the official. A different handover
within a valid lease could still be temporarily ambiguous; no claim of complete
spectator/identity classification is made.

## Exact-source detector evidence

[Sixteen isolated RFDETR probes](detector_frame_probe_v1/probe.json) cover both
Tests1 and2. Each uses the pinned current detector, exact retained proxy PTS,
source-pixel hash and the actual calibrated court crop. Proposals and strict/
padded membership results are preserved separately. This is component inference,
not full pipeline or independently labelled precision/recall.

At6492, RFDETR already supplies the near athlete with confidence0.939 and box
563.5,415.1–692.4,604.8, and the far athlete with0.930. The missing near athlete
is therefore not a detector miss on this source image. The official's0.878
proposal is also correctly a person proposal, but fails the target court gate.
At11346, both athlete proposals exist with0.937/0.905; the original tracking
adapter returns neither on this detector tick.

Ordinary Test1 frames243/300/6152/9000 show both athlete proposals passing the
court while visible officials fail it. They are retained controls, not an AP
sample or match-disjoint validation set.

## Sequential component interventions

Seven chronological prefixes cover Test1 0–80,235–310,9000–9060 and Test2
300–365,5505–6510,11300–11360,25206–25540. Real `PlayerPerception`, court ROI,
tracking and unchanged `ContentContinuityProviderV2` execute on exact pixels.
Both variants share detector observations. The original recorded detector-rate
schedule is held fixed; no pose/shuttle/engine or downstream FSM feedback rerun
is claimed. The longer5505–6510 prefix starts at the original observation epoch
and reproduces the actual official handover and6492 failure.

- [Birth-only intervention](tracking_prefix_probe_v1/summary.json) isolates the
  first defect and preserves its complete source snapshot.
- [Combined lease/birth intervention v2](tracking_prefix_probe_v2/summary.json)
  adds bounded court authority and preserved moving spatial continuity.
- [Final combined intervention v3](tracking_prefix_probe_v3/summary.json)
  additionally applies lease expiry on carried frames, closing the detector-
  cadence corner case. All source guards passed; it reuses retained exact
  proposals, with zero additional neural detector calls. The before controls
  are exactly equal to v2 on every recorded row.

[Original-prefix alignment](prefix_baseline_alignment.json) checks the original
backend's returned box populations against original cached outputs at0.001px
numerical tolerance, after catalog verification. Prefix startup differences are
listed explicitly: two new detection ticks can be needed to rebuild original
state, and Test1 235–245 begins without its prior episode history. Failure
focus6492/11346 and edited-jump focus355/25521 agree with the original output.
All before-control rows in v1 and v2 are exactly equal, as recorded in
[prefix_intervention_alignment.json](prefix_intervention_alignment.json).

| Source instant | Original behavior | Birth-only | Combined candidate |
|---|---|---|---|
| 355 | Carries pre-edit positions | Same | Same; edit acquisition remains unresolved. |
| 356 | Returns one athlete | Both fresh athletes | Both fresh athletes. |
| 5958 | Official only | Both athletes plus official | Both athletes; official excluded. |
| 6307 | Holds two old athlete boxes plus official | Same; no raw hypothesis | Two fresh athletes and a source-supported scene barrier. |
| 6492 | Far athlete plus official; near athlete absent | Both athletes plus official | Exact two current athletes. |
| 11346 | No returned people | Both fresh athletes | Both fresh athletes; no scene barrier yet. |
| 25521 | Carries pre-edit positions | Same | Same; edit acquisition remains unresolved. |
| 25524 | No returned people on first new detector tick | Both fresh athletes | Both fresh athletes. |

Counts across a prefix are coverage, not accuracy: removing the repeated official
reduces emitted person rows even while restoring missing athlete observations.
No generated player points were used to select thresholds or manufacture labels.

## Corrected diagnosis of propagated-box outliers

Consecutive pixels show **354→355** and **25520→25521** are same-camera edited
jumps, with athlete relocation and displayed-score changes. The cached354 and
25518 boxes correctly follow the earlier source positions. The subsequent held
boxes become stale because the edit was not acquired before the next detector
tick. These examples do not establish smooth-motion Kalman drift.

Evidence: [354](detector_frame_probe_v1/test2_frame_00354.png),
[355](detector_frame_probe_v1/test2_frame_00355.png),
[25520](tracking_prefix_probe_v1/test2_25206_25540_frame_25520.png),
[25521](tracking_prefix_probe_v1/test2_25206_25540_frame_25521.png).
The11345→11346 source edit remains outside the observer's multi-prior-region
trigger: only one prior target person is returned. Restoring current births fixes
current observations, not retrospective edit detection or every stale carry.
No scene-threshold/minimum-region code was changed to hide that limitation.

A separate useful downstream effect is independently visible at**6306→6307**.
The source changes both athlete positions and displayed AXELSEN10→12 while the
camera stays fixed. With the static official removed, the existing observer now
has two usable athlete regions and acquires a raw correspondence hypothesis.
The detached current detector confirms changed layout and the unchanged policy
erects a barrier. Before/birth-only, the admitted official creates an insufficient-
feature third region and suppresses acquisition.
[6306 exact source](additional_transition_review/frame_06306_source_proxy.png),
[6307 exact source](additional_transition_review/frame_06307_source_proxy.png),
[exact rendering receipt](additional_transition_review/receipt.json).
This source-supported edit is diagnostic evidence, not adjudicated point timing
or a verified reconstruction of the skipped displayed scores.

## Code, cache identity and validation scope

Only owned candidate tracking files/tests were modified: `perception/players.py`,
new `perception/_bytetrack.py`, the tracking entry in `perception/components.py`,
and two focused regression files. Root-owned engine/plugin changes are a separate
intervention and excluded from this tracking patch.

Tracking contract version/model record advances to2, raw ByteTrack policy identity
is `bytetrack_birth_activation_v2`, and court membership identity is
`observed_court_anchor_lease_v2`. This distinguishes new raw episode/continuity
behavior in existing cache fingerprints. The pipeline's overall version change
is managed by the parent integration. No annotation/output schema migration or
model checkpoint change is needed; accepted old results remain preserved.

Birth RED:11failed/5passed on the initial16-case subset; GREEN16passed.
Additional cutoff/order/duplicate/cache-contract cases bring that family to19.
Court-anchor RED:6failed/1passed; moving-box positives and other controls pass
after repair. A final detector-cadence test is RED1failed/9passed before carry
expiry and passes after the same lease rule is applied on every source frame.
The final combined player/tracking/ROI/doubles suite passes **121tests** and Ruff
passes; [final test log](tracking_family_final_v3.log),
[final lint log](tracking_lint_v3.log).
Controls include2/4simultaneous athletes,6births, minimum≥2, low-confidence
nonbirths/recovery, source-time expiry, resets, independent providers, absent ROI,
never-inside outsiders, moving runoff, valid reentry, stale carries and real
retained airborne/runoff examples. Normal Test1 prefixes show no new barriers.

These controls establish two implementation corrections and source-specific
behavior changes. They do not establish AP/mAP, physical tracking IDF1/HOTA,
stroke/contact accuracy or full match generalisation. Named identities remain
unverified and no accepted points are invented. Full fresh Test1 andTest2
before/after matrices, component diagnosis and downstream regressions are still
required because perception and scene populations change. Test3 is untouched.


## Final candidate handoff

[Final source receipt](candidate_source_receipt_v3.json),
[owned production/test patch](tracking_candidate_v3.patch),
[archived exact final sources](final_candidate_source_v3/sports/badminton/src/bai_badminton/perception/players.py).
The unchanged original-before rows were checked across v1→v2→v3. V3 reuses all
629 previously evaluated exact detector inputs, including v2's one extra6307
probe; it performs no additional detector calls. Both variants use identical
source images, numerical thresholds and frozen cadence inputs. The new6307
barrier and all primary restoration cases persist in v3; no Test1 control
prefix gains a barrier. The source/code/model/proposal hashes remain bound in
its summary, and the previous interventions are retained separately.

This is a **candidate source and bounded-regression handoff**, not a declaration
that all Test1/Test2 accuracy problems are fixed or that full fresh pipeline
regression has completed. The parent orchestrator owns broad integration and
fresh end-to-end runs. No Test3 source or annotation was accessed here.
