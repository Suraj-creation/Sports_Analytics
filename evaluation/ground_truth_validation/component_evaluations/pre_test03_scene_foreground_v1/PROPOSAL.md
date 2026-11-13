# Test 1 scene-context regression: verified cause and isolated remedy

The fresh c7cf871 Test 1 run fails an acceptance control. Its bounded last-in-court lease correctly limits participant authority, but the scene-continuity input is constructed exclusively from admitted participants. Real athletes outside the playable court therefore disappear from image-context evidence. A source edit then loses the required second region and can leave stale participant boxes on the new image.

This is an integration defect between two independently reasonable component contracts. It is not evidence that court dimensions, the lease duration, detector confidence, rally timeouts, or player identities should change.

## Source-bound reproduction

The [independent scene/lease ledger](../../regression_tests/pre_test03_v1/test01_independent_review/scene_lease_diagnostics.json) records exact completed cache hashes, source/proxy identities, 288 frozen production-plan source hashes, native CourtROI/Homography predicates, and selected before/after regions. Private lease timestamps were not serialized; the ledger explicitly distinguishes source reconstruction from private-state observation. The [failure register](../../regression_tests/pre_test03_v1/test01_independent_review/structured_failure_cases.json) and source-evidence images contain the physical diagnostic examples. Agent visual review is not a labelled scene-accuracy dataset.

| Case | Existing evidence | Actual candidate behavior | Required acceptance behavior |
|---|---|---|---|
| Test1, frame7801 / 260.033s | Far athlete's latest fresh in-court anchor7770; fresh outside observation7800 | Lease expires at7770+31, athlete withheld from participant and scene inputs | Keep participant authority withheld; retain separately qualified observed image context |
| Test1,7857 /261.900s | Same-camera edit; real prior far athlete still offcourt | Single scene region, no acquired joint change or layout probe; near box from7854 carried through7859 into visibly empty image region | Acquire multi-region source evidence, force current detection/reset if existing corroboration supports it; do not carry old athlete box |
| Test1,8087 /269.567s | Near athlete's last fresh in-court anchor8056; outside observation8086 | Second lease expires, scene input becomes one region | Preserve scene-only image context without renewing participant authority |
| Test1,8106 /270.200s | Another actual edit | Missed content barrier; active detector cadence happens to acquire current athletes immediately | Recover source-bound cut acquisition independent of current rally/detector cadence |
| Test2,5958→6492 | Earlier overlapping athlete-to-official handover | Correct current lease rejects stationary official; immediate birth restores both current athletes | Preserve both improvements; image continuity must not grant official player/team identity |
| Test2,6307 | Two athletes relocate across edit; static official previously vetoed joint screen | Candidate correctly acquires barrier after official exclusion | Preserve acquisition even when static image context is also retained |

Baseline13 content barriers become11; only7857 and8106 are removed. This count is a regression diagnostic, not a target number of cuts. Numeric track/epoch changes do not establish physical edits or identity accuracy.

## Exact data-flow failure

At frozen c7cf871, `pipeline.py` constructs `previous_regions` from `previous[1].persons` only (lines654–665). `PlayerPerception` applies the authority lease to fresh and carried observations, so the content provider never receives the real offcourt region. The V2 observer can measure a single region, but the provider and layout contract deliberately require at least two regions to support a tracking barrier. There is no alternative raw image-context port.

Simply passing every raw person proposal is insufficient. The existing observer combines every supplied region with an `all(...)` conjunction and accepts at most four regions. A static official therefore vetoes two genuine source innovations, and four doubles athletes plus one official cause all scene telemetry to be dropped. A deterministic [existing-API RED test](test_joint_foreground_contract_RED.py) reproduces both limitations with fixed flow observations: [2 failed,2 passed](joint_contract_RED.log). These failures are proposed scene-only contract tests, not physical detection/tracking scores.

## Approved implementation boundary

1. Introduce a separate, optional scene-foreground port. Seed image episodes only from fresh detections with a positive existing court-origin predicate. Refresh image boxes from uniquely corresponding raw current detections using the existing0.3 IoU gate, before participant filtering. The stream must never create persons, poses, participant IDs, rosters, teams, contact actors or points. Keys identify visual context episodes only. Carry remains explicitly unobserved and cannot renew fresh-observation age.
2. Keep the existing one-second bounded missing-fresh limit, clear on reset/cut/view invalidation, detach snapshots, and cap at eight regions. Overflow must abstain until reset rather than select convenient survivors or silently truncate doubles.
3. Add a versioned V3 observer with unchanged intensity/adaptive-history parameters. Retain every bounded region's telemetry. A channel qualifies only when at least two nonoverlapping image regions independently meet that channel's existing prior-history/adaptive criteria, and their joint mean meets the existing intensity floor. Never combine a single appearance witness with a different single correspondence witness. Record the explicit supporting region keys; union them only if both channels independently qualify.
4. Bind the current detector-layout decision to those actual supporting keys. Complete injective positive correspondence of every support region vetoes a reset even if other current detections exist. Ambiguous overlap/count/source/geometry remains explicit unknown; the experimental raw fallback must be reported, not described as verified edit truth.
5. Version the tracking/foreground, scene evidence/decision, serialized frame, dependent provider and pipeline cache identities. Preserve strict historical V2 decoding and original baselines. Full candidate regression must use a new output directory and source-native source/model/profile guards.

The root orchestrator owns production implementation. This agent owns only new focused tests and diagnosis/probe artifacts. No annotation, evaluation matching, reference timestamps, profile thresholds, neural weights, participant authority policy or Test3 data changes are authorized by this proposal.

## Rejected shortcuts and architectural limits

- Restoring rolling offcourt membership reproduces the measured official-handover defect.
- Lowering the joint region count to one turns an occluded individual into multi-actor edit evidence.
- Renewal from HSV or LK alone would convert image correspondence into athlete identity authority. Existing HSV torso signatures and reversible feature flow are available, but neither is a calibrated physical-identity verifier. No new identity confidence is justified by these controls.
- A separate visual stream can itself follow an official after a spatial handover. That must remain harmless to participant authority and visible in provenance. It cannot prove the person is the original athlete. Requiring two independent joint innovations limits single-person contamination; it does not establish exhaustive scene accuracy.
- Supporting subsets change the false-reset surface: two unrelated region occlusions can resemble an edit. Positive current-layout correspondence, overlap rejection and negative scene controls are therefore required. Do not adopt from two recovered Test1 cuts alone.

## Focused tests and real-source acceptance plan

New candidate tests are `test_player_foreground.py`, `test_scene_witness_v3.py`, and `test_pipeline_foreground.py`. The [initial RED v2 receipt](new_contract_RED_v2.log) records22 failures and1 legacy-fallback pass against the unchanged missing API. Failures from the new named API are distinct from the two existing-API behavior reproductions above.

Focused contracts cover singles/doubles, expiry without authority renewal, observed outside court-origin continuity, never-inside outsiders, no calibration, reset, empty fresh proposals, stale source queries, unobserved carries, unique matching, overflow/reset, detached snapshots, independent channel witnesses, overlap rejection, one-region abstention, four-athlete-plus-static context, and the optional-provider fallback. Tests must not assert physical identity from opaque episode keys.

Chronological exact-pixel prefixes must reproduce both removed Test1 barriers after the lease-expiry instants (before7770 and8056), then verify empty old near-box output at7857–7859. Reuse retained exact detector outputs when source/crop hashes match; record every fresh detector call and do not label a prefix as full end-to-end inference. Required Test2 controls are5958/6492 authority rejection and current athletes, true edit6307, unchanged no-barrier controls7703/23639, and11346 acquisition. Existing natural-motion, exposure/pan, one-person occlusion, missing pixels/features, hard-cut/view reset and doubles cases remain negative controls. Recovered barriers alone do not justify changed threshold values or new winner/class labels.

After bounded source controls and focused tests pass, run complete fresh Test1 and Test2 through the unchanged native evaluator in new directories, preserving original references and before outputs. Compare every applicable reference and component metric, short/walking rally controls, contact timing/class shifts, observed versus estimated masks, and unknown/outcome coverage before claiming an improvement. Physical AP/IDF1/HOTA/contact/stroke accuracy remains unavailable without independently reviewed appropriate labels.
