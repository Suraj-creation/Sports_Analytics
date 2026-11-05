# Physical contact and shot evidence: production-readiness workstream

Date: 2026-11-05. Initial audited HEAD: `181cb917dd923524c48772b55ecc71a49ae68518`, branch `Benchmarking`. This work preserves historical reports, ignored evidence, model assets, source video, annotations and the selected experimental profile. No new neural inference, labels or external video was used by this workstream. The orchestrator owns shared engine/schema/provider integration and any promotion decision.

**Current completed checkpoint:** source `85993259a3a2838881ed2b18658a07967058d191` has two completed fresh full-video runs and matching own-cache semantic replays. Typed physical evidence now uses policy `contact_physical_evidence_v2` and cache20 exact PF/RF execution identity. Association-only retains all36 prior selected intervals while removing the old12766 contact; scene additionally changes7 boundary rows. No automatic physical confirmation is produced. The completed counts and parity audit below supersede the initial policy1/legacy shadow coverage; the historical diagnoses remain intact as development evidence.

Rally agreement does not establish physical contact reliability. The earlier source-bound single-contact intervention fragmented GT27 before the upstream association correction, and contact/stroke lifecycle `confirmed` still does not mean physical certainty. The new typed assessment preserves that distinction while keeping candidate support, legacy ratio scoring and unknown identity explicit. The relative-impulse feature is not globally repaired or validated by the additional physical assessment.

## Reading and current-source audit

Read the complete repository instruction files, full handoff, current 5,316-line H01–H28 inventory and final report at `181cb91`, in addition to the earlier mandatory investigation reports, contact/scene evidence and source-bound experiments. Inspected current contact scoring/NMS, participant episode construction, delayed contact/stroke lifecycle, post-contact motion, rule and optional BST classifiers, analytics rebuild/counting, browser event folding, shot toast/evidence display and the shot annotation protocol.

Relevant production paths:

* `sports/badminton/src/bai_badminton/events/contact.py`: uncalibrated multi-cue scoring and bounded NMS.
* `sports/badminton/src/bai_badminton/participant_contact.py`: provisional track episodes; detector matches, racket availability and identity remain separate.
* `sports/badminton/src/bai_badminton/engine.py::_on_contact/_classify`: a delayed stroke, including an unknown stroke, finalizes the contact ledger entry.
* `sports/badminton/src/bai_badminton/events/stroke.py`: rules, observed post-contact motion, unknown handling and smash/jump heuristics.
* `sports/badminton/src/bai_badminton/events/bst.py`: an implemented optional singles-only pretrained shadow adapter with pinned weights and explicit temporal inputs. It is not the default rules component.
* `analytics/match.py`, `analytics/rebuild.py`, API product analytics and `apps/web/src/features/analytics/evidence.ts`: canonical correction/retraction handling and estimate-based shot aggregation.
* `apps/web/src/features/player/StrokeToast.tsx` and `EvidenceDetails.tsx`: already label machine contacts/shots as estimates. The issue is not a universal browser assertion of physical confirmation.

### What the selected fresh ledger actually contains

The immutable selected run is `artifacts/benchmarking/experiments/next_20261105_fresh_air_tracklet_v1`. Its 2,480 append-only entries fold to 1,850 current events. A source-bound audit retains the actual log/input hashes in `artifacts/benchmarking/experiments/prod_20261105_contact_audit/`.

| Current event | Count | Lifecycle statuses | Physical/classification limits |
| --- | ---: | --- | --- |
| Contact | 457 | 457 confirmed | All payloads say estimated; zero observed physical racket impacts; six geometric racket overlaps |
| Stroke | 457 | 457 confirmed | 313 unknown, 144 estimated known labels; all use `stroke_rules_v0` |
| Shuttle turn | 44 | 44 provisional | Explicit insufficient-proximity diagnostic events |

All 457 contact and stroke named actors are null. This preserves identity uncertainty; provisional participant episodes are independent evidence. Unknown stroke reasons are 308 missing required evidence and five unresolved initial contacts. Known estimates are push48, lift26, drive3, net_shot34, drop23, clear8 and smash2. These are output counts, not correct-class counts.

At frame12766 specifically, the stroke is unknown and its post-contact speed is withheld, yet its linked contact becomes lifecycle-confirmed. The generic ledger's `confirmed` means finalized after lookahead. It does not mean a physical impact or a known hitter was observed. The existing `contact_status=estimated`, confidence semantics and UI estimate labels are useful compatibility disclosures, but they cannot supply typed physical reliability for other consumers.

The engine also declares a POSE evidence window for every classified stroke even when pose is unavailable. The orchestrator owns the correction: a declared context range must remain distinct from observed pose evidence. This workstream does not modify shared event plumbing.

## Current-source GT27 causal reproduction

Before any production edits, reran the existing diagnostic suppression wrapper against the selected fresh run's **own** caches. Actual executor was `181cb91`; exact contact source SHA-256 was `d690890bfd53ae1cabdebcf9ac26ca24eb137294e62608a9dce92dd256a802f2`. Global replay source guard passed. Runtime was83.085 seconds of CPU semantic replay; this is not fresh model inference.

```sh
source ../gpu-env.sh
.venv/bin/python research/next_contact_scene_suppression_replay.py \
  --baseline artifacts/benchmarking/experiments/next_20261105_fresh_air_tracklet_v1 \
  --output artifacts/benchmarking/experiments/prod_20261105_contact12766_suppressed \
  --suppressed-frame 12766
```

The intervention removes one already-selected candidate **after unchanged scoring and NMS**. It does not rerank candidates, change any observation, infer a new contact label, alter a boundary or read annotations during replay. It is a manual causal negative control, never a production policy.

The contemporaneous unchanged control is `prod_20261105_baseline_semantic_v1`; its interval CSV and all 457 current contact signatures match the selected fresh run. New read-only verifier `research/prod_20261105_contact_audit.py` asserts:

* 496→495 selected contact calls, exactly frame12766 removed; all remaining call order is exact.
* 457→456 current contacts, exactly frame12766 removed; common coordinates, supports, component scores, models and attribution reasons are exact.
* All17,268 processed shuttle steps are identical.
* All35 other GT boundary rows remain unchanged.
* GT27 changes from `[12455,12954)` to `[12455,12748)` plus unmatched `[12772,12954)`: matched end error returns to−218frames.
* Detection becomes36TP/1FP/0FN (F1=.986301). This does not certify a physical false-positive contact; it proves the rally result depends critically on this particular uncertain candidate.

Unchanged evaluation, all36 rows, unmatched predictions and both historical-reference comparisons are preserved under `prod_20261105_contact12766_suppressed/`, `comparison_v1/` and `comparison_original/`. The original suppression results remain untouched.

### Why the ratio-only alternative did not solve the causal problem

Source pixels and own observations previously reviewed in `next_contact_scene_perception_findings.md` place the selected12766 observation on the painted T cluster. Legacy support is.787244, incoming speed.124670px/frame, outgoing fitted speed122.124083px/frame, redirect1 and relative impulse1. Racket overlap and swing are both zero. An observed racket elsewhere in the player's crop is not evidence that it overlapped this T point.

The outgoing fit includes the12769 switch from T to an upper airborne observation, with a406.79px step. A declared2.5/√12=.7216878365analysis-pixel sensitivity gives incoming slope sensitivity.326504 and outgoing49.813564px/frame. The new explanation retains the outgoing Euclidean spatial residual RMS111.384176px. Earlier reports gave78.760506px per-axis RMS; the √2 difference is a declared RMS convention, not new localization evidence. Both direction-support terms and bounded gain support are zero at12766.

The previous actual `contact-motion-reliability-v1` replay removes this candidate but still fragments GT27 because the upstream stream contains the static cluster followed by reacquisition. It is not sufficient to remove the old ratio or to call the detector's accepted point fresh physical motion. Association and terminal evidence must be repaired and re-evaluated together, without joining separate rallies or inventing coordinates.

## Implemented additive physical evidence contract

New `sports/badminton/src/bai_badminton/events/contact_evidence.py` defines immutable typed `ContactEvidence`, `ContactEvidenceInputs`, `ContactMotionEvidence`, `ContactReview`, `ReliabilityAssessment` and `Reliability` states:

`confirmed`, `probable`, `ambiguous`, `rejected`, `insufficient`.

The result deliberately separates:

1. **Trajectory change**: whether bounded same-scene observed samples support a turn or launch under an explicitly declared spatial sensitivity.
2. **Physical impact hypothesis**: whether coherent motion, a fresh body and fresh swing/geometric racket-overlap support a possible physical hit.
3. **Attribution**: whether a geometric participant hypothesis is supported, independently of named identity, team or scoring slot.

No automatic heuristic branch can emit physical `confirmed`. That state requires explicit source-bound external review identifying the canonical frame, source digest, reviewer and review ID. Its existence is an external assertion, not proof of annotation quality. No real reviews have been created. An external negative review can reject an impact while preserving a legitimate trajectory turn. `rejected` otherwise rejects the candidate evidence; it is not proof that no unseen impact happened.

`probable` is an uncalibrated evidence-policy state. The policy preserves the pre-existing.05 body-proximity and.5 geometric-overlap gates, uses the already declared motion-sensitivity diagnostics and requires a fresh independent contact cue. These thresholds have not been fitted on Test1 contacts. Their inherited values are not independently validated sporting criteria.

Static context alone does not reject a serve. A zero-incoming-speed, coherent weak launch plus fresh swing/racket cue remains probable. A near-zero incoming direction cannot alone produce a reliable turn. Static-to-airborne association switches without independent cues, unresolved reacquisition, body-only proximity, missing observations, stale/carried observations and rejected scene context remain explicit ambiguous/insufficient/rejected evidence.

Inputs accept null legacy provenance. Presence of a coordinate, body box, score or model name cannot fabricate freshness, association or identity. Exact observed frame tuples, half-open context bounds, available-through frame, source scorer, sensitivity assumptions, LS residuals and cue availability remain inspectable. Sample indices outside context/availability, malformed states, nonfinite supports and unbounded frame tuples are rejected. The schema is `badminton-contact-evidence:v1`, policy `contact_physical_evidence_v1`; all numeric supports remain explicitly uncalibrated.

`ContactCandidate` gains a final optional `evidence` field, preserving earlier positional construction. `detect_contacts` attaches the bounded immutable explanation after numerical NMS; candidate `p`, component scores, model, coordinates and competition remain exact. `build_contact_evidence(window,candidate,motion_reliability=...)` may diagnose a legacy-selected contact under an explicit sensitivity without relabelling the selected provider. The engine can enrich typed upstream freshness/association through `dataclasses.replace(evidence.inputs,...)` and reassess. Independent providers may omit evidence, which remains unknown.

No new default contact model, learned probability, identity assignment, contact deletion or rally gate is introduced by this workstream. The optional `contact-motion-reliability-v1` implementation remains separate from this explanatory contract.

### Recorded-contact shadow diagnostic

New `research/prod_20261105_contact_shadow.py` audits all457 selected timestamps using exact current-control processed positions and unchanged old component scores. It runs neither a perception model nor a semantic replay and reads no annotations. Exact executed module/script bytes, source hashes, input hashes and all457 bounded records are in `prod_20261105_contact_physical_shadow_v1/`.

All457 before/after fitted velocities reproduce recorded rounded component scores within1e−3; zero mismatches. The recorded global-max association is not certified temporal tracking, so all457 physical assessments remain ambiguous with association unknown. No person, pose or racket freshness is fabricated. This is an explicit information limitation, not457 human-labelled errors.

A separately labelled diagnostic assumption treats association as tracked to isolate numeric motion support:337 trajectory assessments are probable and120 insufficient. These counts are sensitivity/coverage only, not contact accuracy. At12766 even that assumption leaves trajectory change insufficient because of the unresolved incoming direction and poor outgoing fit. The tracked assumption never enters production inference.

## Shot-classification audit and compatibility

`post_contact_motion` already requires at least three noninterpolated finite observations after the contact, excludes the next contact, respects recorded scene/replay boundaries, uses robust slopes and withholds large residuals. Missing velocity or flight context remains unknown rather than zero-speed evidence. These controls remain intact.

Rules classify from hitter feet/court depth, image speed, flight time and limited above-head context. Their softmax and smash/jump fusion are uncalibrated heuristic scores, not learned class probabilities or physical-contact proof. A receiver's feet are retained under the legacy landing field with `landing_source=receiver_position`; they are not a 3D shuttle landing or speed measurement. The optional BST adapter requires verified weights, contiguous actual observations and singles capability; its class/side outputs cannot establish the existence of a physical impact or a named hitter.

Corrected only the stale `stroke.py` module docstring that said the optional adapter was unimplemented. Classification behavior is unchanged. The immutable selected run actually executed `stroke_rules_v0`, never BST.

Current analytics correctly resolve event lineage and retractions but count owned estimates without physical-reliability strata. The new additive field allows a compatible migration; removing analytics or silently converting historical counts to confident physical hits would be incorrect.

## Integration and consumption recommendations

The orchestrator owns these shared-file decisions:

* Keep event lifecycle (`provisional/confirmed/corrected/...`) separate from `contact_evidence.impact.reliability` and classifier reliability. Finalization must not upgrade physical impact or identity.
* Populate observation/association and fresh detector/pose/racket properties from actual per-frame provenance. A pose inferred on a carried box is a fresh pose observation only if it actually ran on this current frame; the carried detector state must remain separately visible. Do not infer any of these from a non-null series entry.
* Version declared contact output metadata and dependent semantic caches for the additive evidence contract. Preserve explicit decoding/migration of absent legacy evidence as unknown.
* Preserve existing estimated contact/stroke events and correction/retraction semantics. Add status partitions/unknown coverage to API analytics and exports while keeping legacy estimate counts explicitly labelled for existing clients. A geometric episode target is not a named athlete or team.
* Propagate the originating physical-impact reliability into stroke evidence. A known class or completed classification cannot validate its own parent impact. Unknown shots must remain unknown.
* Evaluate any stronger temporal-recovery gate as a separate controlled experiment. Simply suppressing ambiguous12766 loses GT27 continuity with current upstream observations. A successful upstream association correction must also retain real weak serves, apexes, terminals, occlusions, cuts, four-player attribution ambiguity and close separate rallies.
* Display physical review as reviewed evidence only with its source-bound reference; automatic probable/ambiguous/insufficient states remain estimates. The UI already has useful estimate language and should retain it.

## Validation and remaining limits

Red evidence is preserved in `prod_20261105_contact_evidence_red.log` (missing typed module) and `prod_20261105_contact_evidence_integration_red.log` (missing candidate integration). The final focused contact/shot suite passes206 tests in8.37s, including46 new physical-evidence contracts,32 previous numerical-reliability controls and existing attribution, pose-cadence, scene, streaming, post-contact, singles and four-player doubles controls. Changed-file Ruff checks pass. Synthetic fixtures establish software contracts; they are not real contact, doubles or shot accuracy labels.

The new controls cover automatic no-confirmation, explicit source-bound positive/negative review assertions, unknown legacy provenance, observed/reconstructed/missing/invalid/stale/carried/out-of-view states, scene invalidity, static reacquisition, zero-incoming weak launches, apex/quantization uncertainty, fresh versus stale swing/racket cues, independent attribution ambiguity, input causality/bounds, spatial scale, immutable JSON output, numerical selection parity, missing sample retention and partition-invariant NMS evidence.

Independent human-reviewed physical-impact timestamps, hitter identity, shot family and negative-contact labels remain unavailable in this scope. Test1 is exposed development footage; no generalization, probability calibration, physical-contact precision/recall, shot accuracy or production-readiness claim follows from these changes. H10 numerical instability is observable and separately testable; upstream static association and downstream terminal authority remain open. H11 cadence, H13 shot/evidence semantics and H23 independent labels still need their own source-bound validation.

No production promotion is recommended by this workstream. The additive evidence contract is suitable for integration and controlled validation. The decisive remaining experiment couples explicit association provenance to physical-contact consumption and checks both component labels and complete temporal behavior; without independent reviewed labels, its sporting accuracy must remain unknown.

## Independent integration review and red/green controls

The orchestrator subsequently integrated typed observation association/content epochs, cache19, contact-consumer freshness and shot parent references. An independent read-only review found and reproduced three defects before correction: disabled/unknown/unscheduled pose ticks were counted as fresh cue frames; stroke payloads omitted their parent impact reliability; and the FramePerception wire accepted association metadata from another composite shot/content epoch. The original red log records5failed/15passed. The orchestrator corrected all three, separated raw-image coordinates from internal registered association coordinates, and mapped malformed epoch cache evidence to StaleCacheError. Focused contact/cache/content/identity controls then passed148 tests.

The same independent review found two additional provider-contract gaps: an injected candidate could borrow explicit review evidence from a different canonical frame, and its evidence could claim context beyond the supplied WindowObs. Two new failing controls were captured before the orchestrator added frame-identity and actual-window/frontier validation. This is a contract failure reproduction using clearly synthetic review assertions, not a new real human review or contact label.

New `sports/badminton/tests/test_production_contact_consumer.py` contains22 controls for these cases, absence/exactness of POSE declarations, unknown legacy providers and all three cue-frame lists' causality/context bounds. All22 now pass; together with the separately assigned12 analytics-journal controls, the final combined suite passes34/34 in1.22s. Logs are `prod_20261105_contact_consumer_red.log`, `prod_20261105_contact_consumer_green.log`, `prod_20261105_contact_provider_frontier_red.log` and `prod_20261105_contact_and_journal_final_green.log`. These results establish consumer/schema contracts, not physical contact accuracy.

The assigned H21 analytics checkpoint work is documented separately in `research/ANALYTICS_CHECKPOINT_REPORT.md`; it fixes input aliasing and historical copying without changing perception, contact scores, rally boundaries or custom-provider checkpoint ownership. No additional neural inference was performed by this review.

### Actual pose execution identity

A final provider-contract audit established that scheduling plus non-null keypoints still cannot establish actual pose execution for independent providers. The orchestrator added optional canonical `pose_frame_idx` provenance to person/participant/track wires, cache20 and legacy-unknown decoding, and advanced physical-evidence policy to version2. The consumer requires the actual source frame as well as declared cadence; a legacy provider with coordinates alone stays unknown.

The assigned baseline `players.py::_attach` now stamps that source only after this frame's actual pose call returns valid COCO17×3 person output with at least one finite positive-support keypoint. Missing, invalid, all-zero, disabled and unscheduled outputs receive no stamp. A detector-carried box can still have genuinely current pose output, while a carried box does not inherit an old pose stamp. Output arrays are copied so a provider's reused buffer cannot rewrite an earlier observation. No neural weights, coordinates or scheduling defaults were changed.

New `test_pose_observation_provenance.py` has17 CPU/fake-provider controls, including per-person four-player success/dropout, carry/reset and legacy unknowns. All17 pass. The broader pose/racket/tracking/identity suite passes64 tests after the orchestrator's matching generic track-schema field was added; the earlier in-progress schema failure log remains preserved. The final logs are `prod_20261105_pose_producer17_green.log` and `prod_20261105_pose_provenance_final_green_v2.log`. This proves observation provenance contracts, not pose/contact sporting accuracy. No model inference was run for these tests.

## Completed fresh policy2 and own-cache parity

The two completed source8599325 runs use their own newly inferred288 cache20 segments and actual provider PF/RF source identity. Association-only has453 live contacts and453 linked strokes:84 probable physical hypotheses,140 ambiguous and229 insufficient. Scene has446/446:82 probable,136 ambiguous and228 insufficient. Neither run has a physical `confirmed` impact. All453/446 named hitter identities remain unknown. Shot labels are143estimated/310unknown and137estimated/309unknown respectively. These are coverage and machine-policy counts, not contact, hitter or classification accuracy. The original457-contact diagnostic and policy1 coverage above remain historical; they must not be substituted for these measurements.

Both own-cache replays independently pass `research/production_replay_parity_audit.py`. Final evidence is in `prod_20261105_association_replay_parity_audit_v4` and `prod_20261105_association_scene_replay_parity_audit_v4`. The script verifies all93 captured executed-source hashes, all288 own-cache digests, source commit and metadata/trace hashes, exactly17,268 ordered FSM step frames, EOF flush17267 and fresh frontier17267. It does not load GT, a model or the semantic engine. Every matched contact/stroke/end timestamp and pair of event IDs is retained in `audit.json`.

After explicitly resolving separate session/event/participant namespaces and retaining the actual numerical payloads, contact and stroke equality is exact453/453 and446/446. This includes coordinates, heuristic support, motion fits, source cue-frame lists, physical evidence/statuses, classification labels, parent lineage and temporal context. All36 final rally interval/reason payloads and seven-column CSV interval sequences are exact for each replay versus its own fresh run. The scene replay reproduces the **fresh**7-row change, rather than merely repeating the older cached4-row counterfactual.

The complete live export is not described as byte-identical. The final auditor retains38 association-only differences and51 scene differences:37/50 identity-ambiguity tracker-instance strings exactly satisfy the independently checked production formula `SHA256(isolated_session_id:reset_frame)[:16]`; one format-decision event per run has identical recorded payload but explicitly changes producer provenance from `sustained_target_court_format_v1` to `diagnostic:recorded-format`. The captured replay source calls `set_match_format` with that diagnostic provenance. No remaining numerical/contact/stroke/end payload difference is unexplained. Provenance profile labels are also reported separately (`experiment` versus replay's historical default `gpu-rtx4000`); they do not prove an inference backend or GPU execution.

The11 new parity controls cover final correction folding, historical parent references, repeated same-frame events, participant origin/track binding, physical/cue/label/numerical changes, retained producer provenance, supersession/evidence-ID lists and avoiding accidental replacement of ordinary text that happens to equal an ID. Development audit variantsv1–v3 remain preserved; v2's strict normalization did not yet resolve supersession IDs and v3 did not yet resolve highlight evidence-ID lists. Finalv4 has field-aware identity resolution and all11 controls pass. No production prediction changed during this independent review.

The GT27 own-cache rawT at12766 remains available with association ambiguity and no selected physical coordinate; the old selected contact is absent in both live exports while the association-only interval remains `[12455,12954)`. This is an upstream association mechanism improvement. It does not establish exhaustive physical impacts, true landing evidence or calibrated probabilities. Legacy ratio sensitivity, unknown observations/identities, shot errors and unreviewed scene/terminal authority remain quality limitations. Published external human anchor data was subsequently discovered and authorized, with draft frozen alignment; it is separate exposed reference-agreement evidence, not an independently reviewed Test1 physical-impact or blind validation set. The prepared external evaluator has not scored failed/unfinished external v1 runs.

## Completed exposed external anchor agreement: India and Denmark

Fresh isolated India_v2 and Denmark_v2 completed all4800/3300 frames with executor exit0 and frozen source guards. The failedv1 runs remain unscored. Offline evaluation uses all85/39 published human contact anchors and all89/33 live contacts across the entire prepared clip, including provisional eligibility and between-rally candidates. It preserves all four original partitions, annotation IDs, raw classes, draft/human-review-false binding and fixed −1/−3 pre-crop alignment. No reference window, class, hitter or outcome value entered inference. Native12 remains unchanged. These clips were previously exposed; the result measures agreement with published anchors under a draft timeline translation, not blind or exhaustively reviewed physical-impact accuracy.

| Full-clip result | India | Denmark |
|---|---:|---:|
| Published anchors / predicted live contacts |85 /89|39 /33|
| Matched / extra / missed, ±3 frames |64 /25 /21|25 /8 /14|
| Precision / recall / F1 |71.91% /75.29% /73.56%|75.76% /64.10% /69.44%|
| Matched timing MAE |0.546875frames|0.64frames|
| Correct native12 class / matched anchors |3 /64 (4.6875%)|1 /25 (4%)|
| Matched known-class coverage |10 /64 (15.625%)|3 /25 (12%)|
| Unknown predicted class / all contacts |70 /89 (78.65%)|30 /33 (90.91%)|
| Joint contact + class TP / FP / FN |3 /86 /82|1 /32 /38|
| Joint contact + class F1 |3.45%|2.78%|
| Named hitter unknown |89 /89|33 /33|
| Physical probable / ambiguous / insufficient |7 /34 /48|1 /14 /18|
| Automatic physical confirmed |0|0|

±6-frame results are identical to ±3 for both clips; the tolerance was not widened or fitted. India retains named source-reference support42P1/43P2 and Denmark20P1/19P2, with zero production named-hitter predictions. These labels are not assigned to raw tracks or scoring slots. India misses all4 short-serve anchors. The three correct India classes are drop2972, drop4294 and clear4352; Denmark's one correct class is net_shot637. A model-complete runtime does not meet the contact/classification/identity production gate.

All timing pairs, annotation IDs, missed anchors, extra contact records, raw class counts, full missed/spurious/unknown confusion cells and per-class end-to-end denominators are retained in `prod_20261105_external_india_reference_v1` and `prod_20261105_external_denmark_reference_v1`. `matching_inventory.json` materializes every miss/extra directly from the unchanged metric's saved match list; it does not change matching. `actual_model_coverage.json` preserves all capability/runtime/model hashes and recorded call/observation coverage. India completed124shuttle forwards,1391detector,2610pose and117OCR calls; Denmark75/593/1033/64. India has2135accepted raw shuttle frames and3447VALID calibration frames; Denmark1005 and1695. Both report no unavailable required stage or degraded runtime. Optional neural ReID remains disabled for these singles sessions; optional shuttle alternatives are unsupported and BST remains shadow-only. Loaded ORT provider lists do not establish every node ran on GPU.

The exact executed offline adapter is SHA`96717f4e3015854ac34d03b88a8b4f9d9972bfe29d7cf9c4ca809058067107a7`. The previously frozen39-test source was reconstructed and matches its historical SHA`7959596d5e863fbd38e62324f551c3485415cfdd6efe323875c07d3f437f2a4a` exactly. An AST comparison and saved unified diff show the only changed function is `run_test7`: stronger actual source-frame count/analysed-session/canonical-media refusal checks, with one new test. India/Denmark rebinding, contact extraction, class mapping, matching and metric mathematics are byte-for-byte unchanged functions. The40-test suite passes. Both result packages retain executable source, exact old digest-verified snapshot, pure archived metric source, unchanged matcher and test snapshots; original labels and immutable report hashes remain unchanged.

Initial bounded India review is in `prod_20261105_india_failure_review_v1/index.html`:136exact-PTS canonical proxy images across8cases, with matching own-cache states and nearby live events. Assistant pixel review remains diagnostic and does not promote the draft label alignment. The source-bound causal table and controlled optional-geometry experiment will distinguish observed weak peaks, camera/court validity, missed body observations, score gates and intentional classifier abstention before any fix is proposed. No threshold, offset, model, source observation or production default has been changed from these results.

## Completed doubles and Test7 coarse external evaluation

Doubles_v2 completed all3600frames before offline scoring. All45 published DShuttleNet anchors and35 live machine contacts are retained across the complete contiguous clip. At±3frames:21TP/14FP/24FN,precision60%,recall46.67%,F152.5%,matched timing MAE1.190476frames. At±6:27TP/8FP/18FN,precision77.14%,recall60%,F167.5%,timing MAE2.037037frames. Both tolerances are reported as frozen, with no offset search. Strict native12 and the previously frozen D9 projection happen to agree for this run because its predicted families contain no projection-changing class.

Only1 class is correct:drive2986. Conditional correctness is1/21=4.76% at±3 and1/27=3.70% at±6; full-clip joint contact+class is1TP/34FP/44FN,F12.5%. Unknown classes are27/35=77.14%. All4 published serve anchors remain missed. All35 named machine hitters remain unknown, and all source actor labels remain in the denominator:A7,B15,C8,D15. No P1/P2 or near/far track is assigned to any of those four source people. Physical evidence is7probable/12ambiguous/16insufficient,0confirmed. Optional neural ReID reports degraded/missing OSNet and the unavailable baseline player_reid provider; no weight was downloaded or identity fabricated. Shuttle81,detector639,pose1114 andOCR67 calls complete, with904accepted raw shuttle frames and1903VALID calibration frames. Complete strict12/D9 confusion, all matches/misses/extras, individual actor denominators, optional-stage failure and artifact/runtime provenance are in `prod_20261105_external_doubles_reference_v1`.

Test7_v2 independently completed full source10725frames/frontier10724. Only the primary eight-column31-row coarse reference's start/end seconds were consumed, after predictions were durable. `source_conversion_receipt.json` preserves every exact rational seconds×30 frame conversion with offset0 and no rounding; original outcome/score/class fields are not interpreted. All32 live predicted intervals remain. The unchanged IoU.5 evaluator gives29TP/3FP/2FN,precision90.625%,recall93.5484%,F192.0635%,meanIoU0.7748146442. Matched start/end MAE are33.8621/19.7586frames,RMSE55.1231/32.5931,maximum242/135. These are coarse-span agreement on exposed footage with unestablished match-disjointness, not precise impact or frame-level rally truth.

Primary GT22/23 are missed. The3 unmatched half-open predictions are[1491,1615),[6830,7018),[7586,7695). All31 GT comparisons and all unmatched prediction records are retained in `prod_20261105_external_test7_reference_v1`, alongside immutable inference/event/CSV hashes, actual proxy-byte verification, derived seven-column reference, unchanged evaluator and exact executed adapter/tests. High coarse rally recall does not rescue the poor external shot/contact/hitter result or establish any scoring accuracy. No production promotion follows.

## India frame-aligned root-cause readout before counterfactuals

The new `prod_20261105_india_failure_review_v1/all85_anchor_causal_readout.csv` and JSON retain all85 anchors, including matched/unmatched status, exact canonical/source annotation/decode frames, raw/model candidates, masks/threshold flags, scene/calibration, association, fresh detector/PF/RF, nearby raw velocity support and current classification. Only the explicitly inspected subset is pixel-reviewed by the assistant; other rows retain physical observability unknown. No annotation alignment or source point is changed. `index.html` contains136 exact-PTS source-proxy JPEGs across8 bounded cases with synchronized cache evidence. JPEG is a lossy diagnostic export, not new ground truth.

| Missed serve anchor | Source-frame diagnostic and recorded evidence | Distinguishing limitation |
|---|---|---|
|419|Wide court and near-server action visible. Peaks416–418 are unmasked but below.5 at.4292/.4321/.4531;419reacquires at.5054.|The scorer's416–419incoming window has only one fresh accepted point. Gap reconstruction is excluded from contact velocity fits. This is sparse launch evidence and fixed pose/detector cadence, not proof the serve is unobservable.|
|1569|Frame1568is a close-up;1569is first wide view with source-visible shuttle. Raw support1569/1570=.6216/.6943;calibrationREACQUIRING. No accepted people until1578.|No continuous incoming wide-view trajectory across the edit. Registered temporal geometry is withheld during reacquisition; first valid geometry1571still has no person. Exact physical impact across the edit remains unreviewed.|
|2714|Frame2713is a close-up; first wide2714contains a source-visible shuttle streak and.6372raw support. First2framesREACQUIRING; no accepted people until2724.|A genuine model observation exists, but registration and current person context are unavailable. Raw rejected detector boxes are not retained, so detector miss versus ROI admission cannot be separated from this cache alone.|
|3736|Close-up3731shows shuttle/racket preparation. Wide view returns3732;3736has.5435raw support,VALID court and no people until3738.|Slow/held/launch ambiguity plus absent current person/pose context; no exact physical impact time is asserted. Missing source-wide context is distinct from missing model evidence.|

The source-derived `_usable_camera_pose` predicate requires VALID registration for tracked temporal coordinates. Thus main-view raw observations duringREACQUIRING can remain model-visible while being unavailable to the registered temporal window. This is not permission to mix unregistered image coordinates with the old court reference. The causal CSV marks this as a source-derived gate rather than claiming an unrecorded internal FSM trace.

Current event payloads explain70 unknown classes:69`missing_required_evidence` and1`unresolved_initial_contact`. Of all89 strokes,64have no hitter court coordinate; **all64 occur on explicitly skipped detector frames with two carried person boxes**. The other25occur on detector-executed frames and have court coordinates. For53unknown strokes, speed, flight time and non-serve role are all available; missing admitted court geometry alone triggers abstention. The current classifier intentionally requires fresh detector evidence for anonymous singles geometry. This is a cadence/evidence-consumption restriction, not evidence that the visible people or their names are known. Relaxing the freshness guard or treating carried boxes as fresh would be incorrect.

The remaining unknown combinations are retained in `classification_gate_diagnosis.json`:3court+speed+flight missing,3court+serve-role,3court+speed,2speed-only,3flight-only,2court+flight and1serve-role-only. Known but wrong classes remain in the confusion matrix rather than being explained away as abstention. The extra621/1100 windows show player/flight activity, but assistant inspection does not establish whether a physical racket impact occurred; these are unmatched published anchors, not independently adjudicated false physical contacts.

A bounded one-variable test of the **existing** anonymous detector-bracket geometry provider is appropriate after exact own-cache baseline parity. It requires two fresh matched endpoint observations, stable episodes/track births, explicit skipped interiors, valid same-segment court context and at most.2seconds; it retains estimated source frames, synthesizes no shuttle/pose and assigns no named athlete. Any source frame after the actual decision-emission frontier must reject the test. A separate already-existing contact-motion-reliability provider is the higher-priority alternative and will use the unchanged declared.7216878px sensitivity. Neither experiment changes production source or defaults, and acceptance requires retained misses/extras/wrong classes and temporal controls.

## Controlled existing-provider experiments after exact external replay parity

New `research/production_external_semantic_replay.py` reconstructs semantic providers through the existing component registry from each completed external run's **actual** SID, media, captured profile and recorded calibration/format contracts. It verifies all retained cache digests and sport-source hashes and records source hashes before/after construction/execution. It loads no neural model and reads no annotations. Default replays reproduce all live semantic events for India/Denmark/doubles exactly after explicit event-ID resolution; no Test1 metadata, FPS, frame count or calibration is substituted. The actual generic source-delta map was empty. Bounded readout wrappers call the real contact provider first and return its results unchanged, then explain selected focus windows.

Actual baseline readouts confirm the four serve mechanisms:419has no incoming velocity but outgoing(-6.0534,-27.1612)px/frame;1569/2714have no admitted velocity and zero current bodies;3736has incoming/outgoing motion but proximity/swing0 and score.02085below the unchanged.35 gate. Miss441has neither short-window velocity;1070has motion/body evidence but score.17326below.35. Unmatched621has score.84160 with legacy impulse1.0 and swing1.0;1100has score.65559 and redirect.9066. These explain decisions; neither accepted score proves a physical hit. `contact_readouts.json` preserves each actual engine window and available frontier.

### P0: existing motion-reliability provider

The sole changed provider is `contact-evidence-v1`→existing`contact-motion-reliability-v1`, with identical explicit spatial sensitivity.7216878364870323px and all remaining parameters, caches, association and rally flags fixed. Source and injection guards pass. No low-speed floor or new threshold is introduced. The previous rejection is retested under the new association rather than assumed to transfer.

| Exposed reference | Original ±3 TP/FP/FN | Motion ±3 TP/FP/FN | Original F1 | Motion F1 | Motion ±6 TP/FP/FN |
|---|---|---|---:|---:|---|
|India|64/25/21|27/4/58|73.56%|46.55%|27/4/58|
|Denmark|25/8/14|10/1/29|69.44%|40%|11/0/28|
|Doubles|21/14/24|12/3/33|52.5%|40%|14/1/31|

Prediction counts drop89→31,33→11,35→15. Improved anchor precision comes with large recall losses; class correctness falls3→2,1→0,1→0 at±3. It is rejected for default promotion. All unchanged-match, lost-match, extra, miss, unknown and wrong-class rows remain in the three `prod_20261105_*_motion_reliability_reference_v1` packages.

Both Test1 own-cache arms independently retain36TP/0FP/0FN and GT27`[12455,12954)`, with154/152contacts versus453/446. GT19/20 remain endpoint-identical; GT2 remains matched but ends8frames earlier, worsening end error−7→−15. GT4 starts16frames later1803→1819, improving an early error−71→−55 while still starting early. Other regressions remain: GT6 start+11,GT25start+20,GT36end−24 and scene-GT23start+16. Association-only start/endMAE29/10.8333 and IoU.859872; scene29.6111/10.3056 and.861344. Full36-row unchanged-evaluator outputs, including every changed boundary, are in `prod_20261105_test1_motion_reference_review_v1`. Test1 perfect detection does not outweigh the exposed external contact failures or prove physical reliability.

### P1: existing anonymous detector-bracket geometry

A separate arm enables only the existing default`GeometryBracketPolicy`, preserving the baseline contact provider and all existing freshness, ambiguity, scene, scale and motion gates. Numerical contact coordinates/support/physical assessment, selected frames, raw cached observations, rally boundary/reason triples and unknown named actors are independently **exactly unchanged** for all3clips. Geometry stays explicitly estimated; it adds no shuttle coordinates, synthetic wrists/poses, source review or player names.

| Clip | Correct class on matched anchors, before→after | Known matched coverage, before→after | Unknown class/all contacts, before→after | New correct / new wrong matched labels |
|---|---|---|---|---|
|India ±3/±6|3/64→11/64|10/64→44/64|70/89→29/89|8/26|
|Denmark ±3/±6|1/25→6/25|3/25→18/25|30/33→13/33|5/10|
|Doubles ±3|1/21→3/21|6/21→12/21|27/35→16/35|2/4|
|Doubles ±6|1/27→4/27|7/27→15/27|27/35→16/35|3/5|

All previously correct matched classes remain correct. India selective known-class accuracy decreases30%→25%; Denmark remains33.33%; doubles increases16.67%→25% at±3 and14.29%→26.67% at±6. More coverage therefore exposes substantial rule-classification errors rather than proving a generally accurate model. Contact timing/precision/recall remain unchanged, all4 India serve misses remain, and named hitter coverage stays0 across all source actor labels. The strict12 and frozenD9 protocols and all confusion cells remain separate.

The actual logged geometry source frame is at most4frames later than the candidate timestamp in India/doubles and5 in Denmark. Every such source is already available before event emission, with minimum frontier margins41/41/39frames respectively. This is existing declared delayed classification; no unavailable future observation is borrowed for an already emitted decision. Fresh source detector observations remain separate from estimated interior geometry. Explicit refusal reasons include incomplete/mismatched brackets, ambiguous proximity, invalid context/geometry and implausible scale/court motion. All controls remain active.

Independent aggregate `prod_20261105_existing_provider_comparison_v1/comparison.json` verifies exact source/cache identity, unchanged numerical contacts/physical statuses/boundaries and all class transitions/old-correct retention for each arm. Default parity artifacts and every source/candidate/export/metric hash are retained. The existing motion-reliability and detector-bracket negative-control suites pass111tests, including weak launches, stationary reacquisition, quantization, cuts, failed detector ticks, episodes, four-player ambiguity and causality. These are software contracts, not new physical accuracy labels.

The existing geometry provider is a useful opt-in research explanation of the cadence/geometry admission gap. It remains a shadow experiment; no default change, new model, weight download or additional neural inference occurred. Full analytics quality is still insufficient and independent physical-impact/alignment/hitter/shot review remains necessary. Remaining raw detector-admission and exact impact observability gaps are explicitly unknown, not repaired by a threshold or annotation offset.

## Precommit replay-proof hardening and genuine Test7 causal replay

Independent orchestration review found that the first research runner bound baseline proof to source report and engine/sport hashes, but omitted research runner/helper identity. A changed research helper could therefore incorrectly reuse an old proof. This is a research evidence-contract defect; completed predictions and original data are preserved. The9 completed external baseline/motion/geometry runner archives independently hash to the same`cf63d08d...` source. Their measured results remain historical evidence under the recorded frozen workflow, with the explicit limitation that schema1 did not encode a full per-arm helper map. They cannot authorize a future run.

Future schema`cached-external-semantic:v2` captures exact bytes and SHA of the runner, external reference validator, parity audit and transitive contact-event fold helper before constructing the engine. It verifies them after execution and archives all four files. Optional arms require exact runner/helper/core/report equality, an actual Boolean baseline-parity true, and a plain baseline rather than another experimental arm. Old/missing/mismatched proof is rejected. Source-control tests preserve15red failures before implementation, then27passing controls covering stale/missing/direct/transitive helpers, detached capture, changed/added dependencies, typed proof and genuine full-upload completion/media/plan guards. Evidence is `prod_20261105_replay_provenance_controls_v1`; no historical artifact or neural run was overwritten/repeated.

The same adapter now reads the **actual** full-upload `inference.json`, `session.json`, executor and source-bound frozen plan, and `data/sessions/<actualSID>/perception/` layout. It creates no fake benchmark metadata. It verifies full source frame count/frontier, actual source/proxy hashes, plan hash,179 cache20 segments and contiguous decoded frame indices. Unlike the clip-validation harness, the original full-upload worker did not publish an at-inference cache-digest catalogue; its cache hashes are explicitly captured read-only after completion, with full default event parity required. This limitation remains visible.

`prod_20261105_test7_semantic_causal_v2` reproduces all10725steps/frontier10724 and every live event type exactly:248contacts,248strokes,32rally ends and all other machine payloads after recorded-ID resolution. No annotations or neural models enter replay. Bounded ranges1390–1629 and7500–7919 are **telemetry only**; they do not affect decisions. The four helper hashes and executed snapshots pass before/after guards. The only recorded generic-code delta from neural inference is the separately reviewed additive agent-budget Settings file; sport/event/FSM source hashes match. Full parity is established before interpreting the trace.

The new source-bound `prod_20261105_test7_causal_summary_v1` records exact transition line references, contact-scorer windows and hashes:

* **GT3 primary[1140,1590):** raw observations disappear1456–1487,32frames, despite main view,VALID registration and player movement. The engine proposes end1455 at1465,closes1470 and finalizes that FSM segment1478. Observation returns1488; reliable movement begins1491 and confirms1493, producing the separate[1491,1615)fragment. Thus the earlier135-frame end error is a real perception-loss/closure chain; final CSV overlap alone did not identify it. FSM source-frame index and the later actual available-through decision frontier are recorded separately; no claim of immediate source-frame publication is made.
* **GT22 primary[7560,7650):** accepted contact7557 starts a brief candidate, last raw point7559. Missing7560–7583 leads to ending7569,closed7574 and short-candidate cancellation7582. A new contact7586 starts the surviving[7586,7695)interval. Stationarity proposes7681 at7690; contact7695resumes it; the content barrier7706finalizes with cut reason. Its IoU64/135=.474074 fails the unchanged.5 matcher. Exact original source7705→7706PNG inspection confirms player-position discontinuity in the same court view, while registration staysVALID and content epoch7→8. This barrier has concrete diagnostic support and must not be bypassed to join separate points. The two new source images and exact PTS/hash receipt are in `prod_20261105_test7_content7706_review_v1`.
* **GT23 primary[7770,7860):** no raw selection7770–7793; first return7794 and movement7798,confirmed7800. Raw activity reaches7847,then missing7848–7859. Ending begins7857. Points return7860–7871 near(825,299),but near-static speed.026–.705px/frame does not validate renewed moving flight. The event closes7862 and cancels7870 because its observed span49frames is below the unchanged60-frame minimum. View invalidity starts7872 **after cancellation**; it did not cause the cancellation. Strong raw flight at7814(.8403)reaches the engine, but contact score.01967 with redirect/swing0 creates no accepted contact. A visible shuttle is not itself a racket impact. This source-bound chain separates onset perception loss, later missingness, slow-return ambiguity and minimum-duration cancellation.

Assistant inspection of the original source frames supports observable wide-view activity at the short-rally cases and a source-visible shuttle at7814; exact physical contact/landing times remain unreviewed. Coarse integer-second annotations are not precise physical event labels. No threshold, minimum duration, offset, manual boundary, merge rule, source coordinate, model or production default was changed to recover these rows. The next discriminating work is better observed onset/flight/association evidence and reviewed short-event/contact semantics, with adjacent separate-rally controls; simply lowering duration or extending a timeout is unsupported.

## Future cache-completion catalogue and final replay controls

The research full-upload executor now writes a versioned, exclusive-create `perception_completion_catalog.json` after analysis and before its completed-worker receipt. The parent verifies it after the worker closes. Its bounded catalogue binds the actual session, source/proxy SHA, canonical media, exact segment population, bytes, header hashes and contiguous frame coverage. This establishes file/header/extent identity; it does not attest physical accuracy or independent model origin.

When the completed full-upload input contains `perception_cache_catalog`, the replay calls that same real verifier before constructing an engine. Null, changed, missing or additional cache evidence is rejected; present-but-invalid evidence cannot fall through to legacy handling. The current runner/helper proof therefore includes a fifth file, `production_external_stress.py`, in addition to the four helpers archived by the completed causal replay above. All five are captured before validation, verified afterwards and archived for future executions. A changed catalogue helper invalidates an old baseline proof.

The current runner has36 passing controls, including real producer/verifier integration and pre-engine rejection, alongside27 catalogue controls:63 passed together, with changed-file Ruff passing. Exact source snapshots, before/after hashes and logs are retained in `prod_20261105_replay_catalogue_controls_v1`. Runner SHA is `d1f1676121cb4ddc9afd80c63ca3d3e6ba4718e3ed83df126af9a405a9b58b60`; the frozen reference adapter remains `96717f4e3015854ac34d03b88a8b4f9d9972bfe29d7cf9c4ca809058067107a7`.

The finished externalv2 Test7 worker predates this catalogue. Its absence remains explicit and is not backfilled: the original cache-origin limitation, post-completion hashes and full semantic-parity evidence above remain the truthful scope. The completed schema1 provider arms and four-helper schema2 causal replay are preserved unchanged. No model, inference, scoring protocol or historical result was rerun or rewritten for this provenance correction.
