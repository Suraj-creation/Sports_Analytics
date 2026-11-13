# Test 2 V5: persistent missed short exchange

**The coarse-reference miss is confirmed; V5 still detects the short activity and then cancels it.** This is a rally-admission limitation, not evidence that the new scene-origin correction failed or that this window needs denser pose inference. The source images support a short exchange, while exact impact, hand release, hitter identities, and official point remain unverified. No production fix is justified merely by restoring the older high contact score.

The completed fresh run is producer `test03-scene-overlap-20261112`, commit `5ae614826e6f909defb02445386962ac13b4641a`, all29,296frames. Genuine worker/parent/native-producer completion and its complete own-run semantic replay pass before current data consumption. This review performs no neural inference, new replay, threshold/configuration change, source change, or annotation modification. [Guarded extraction](extraction_receipt.json), [actual ordered traces](actual_ordered_trace.json), [append-only versus live events](actual_case_events.json), [raw window](actual_case_cache.json).

## Confirmed benchmark and source behavior

`Test2_Full.csv` reference data row33 is `[11700,11760)`, 390–392s. Current matching records `missed` and no predicted interval. The original preserved run returned11715–11751, IoU0.6; both2418 and5aeomit it. The generated timing reference has a different positive population, so its higher aggregateF1 cannot resolve this coarse-reference miss.

Source frames11715,11731,11740 and11751 show the near blue athlete initiating an action, the far red athlete responding, and continuing movement across the court. This is more than the early preparation convention that explained another interval's start shift. However, these are agent visual observations, not newly manufactured physical contact labels. The coarse row's exact onset/end remain a convention, and frame11714 model reacquisition cannot establish a physical release. Original source pixels were reused from the already source-bound [contiguous visual package](../../regression_tests/pre_test03_contract_v1/visual_test02_lost_short_event_v1/completion.json); no video was downloaded or decoded by this review.

## Actual current causal chain

| Frame | Actual V5 operation | Consequence |
|---:|---|---|
| 11691 | Correct source discontinuity, idle→idle | New content epoch23; incompatible prior context is cleared. |
| 11711–11713 | Shuttle missing | A continuous observed origin chain is unavailable. |
| 11714 | Fresh selected point, `reacquisition`; speed unavailable | Observed model point, not observed hand release/impact. |
| 11715 | Tracked point; speed0.262073px/frame | No current contact candidate enters the actual event ledger. |
| 11716/17/18 | Observed speeds17.111990/12.985903/11.500129px/frame | The unchanged three-observation motion gate opens at11718, with start11716. Body-motion cue remainsfalse. |
| 11731 | Contact callback, score0.754812445; impact/trajectoryambiguous | Typed contact target is the far anonymous episode, even though public participant hypothesis is unresolved because its selected person is carried. |
| 11740 | Contact callback, score0.879731379; impact/trajectoryprobable | Same far episode target, with provisional anonymous attribution. These labels are algorithm assessments, not verified impacts. |
| 11761 | In-play→ending after the missing-observation policy | Tentative end11751. |
| 11766 | Ending→closed | Segment11716..11751, reason`gap`. |
| 11774 | Closed→idle; `cancelled_start=11716` | Admission reason`duration_policy`, no opposite-episode witness pair, no finalized interval. Engine retracts the provisional start and contacts. |

The FSM's segment length is inclusive:11751−11716+1=36frames, below its unchanged60frame/2second minimum. The benchmark exporter/matcher separately uses half-open time intervals; these two conventions must not be conflated.

The short-exchange exception needs qualifying contact-motion witnesses from opposite, simultaneously observed episodes. The two current typed targets at11731 and11740 are **the same far episode**. Their source motion samples are disjoint, and the later assessment isprobable, but those facts cannot supply the missing opposite-episode proof. An unresolved public hitter hypothesis is not the same thing as absent typed target; the actual payloads preserve both distinctions. After cancellation, neither contact survives in the live ledger. Counting append-only candidates as accepted extra contacts would be incorrect.

The original run retained this short segment through witnesses11715 and11740, whose typed targets were opposite episodes. Its11715 contact score0.905434 was sensitive to a nearly stationary incoming heading with zero incoming directional support. The preserved2418 conditional score study yielded0.282427, below the unchanged0.35 acquisition cutoff. Current V5 does not emit11715 either. This review does not restore it, infer a new exact V5 fused score from its absence, or promote its old confidence into physical evidence.

## What changed, and what did not

For every frame11690–11775, raw shuttleXY/support, all returned-player payloads, detector execution, pose stride, camera, view and calibration are **exactly equal between2418 and5ae**. FSM opening, callbacks, closing and cancellation frames also match. Content epoch changes20/21→22/23 because earlier real cuts were recovered; source epoch/birth identifiers remain separate and are not physical identities. The corrected V5 scene policy neither repairs nor worsens this local failure through a changed neural input in this window.

This case is already at pose stride1, with fresh boxes on the relevant even frames including11714/16/18/20/40. Frame11731 itself is a carried-player frame. The separately observed sparse stride6/whole-chunk feedback issue around25680–25739 remains a different confirmed acquisition limitation. A future independent-motion request for dense perception is an acquisition hypothesis requiring neural/cost validation; it cannot be claimed to fix11715 or this admission failure.

## Responsible interfaces and minimum reusable proposal

The causal interfaces are the registered rally component in `components.py`, `RallyObservation`/`EvidenceRallyFSM._short_exchange_witnesses` and `_finalize` in `events/rally_evidence.py`, the duration/gap/merge state machine in `events/rally_fsm.py`, `simultaneous_opponents` in `events/exchange_evidence.py`, and engine `_handle_fsm` cancellation/retraction. The code behaves consistently with its declared conservative policy. The limitation is that short **activity** survival is coupled to sufficient contact/actor attribution.

The smallest feasible research extension is a separately versioned **typed activity witness through the existing registered rally/admission boundary**, retaining the current policy as baseline. It could combine the existing observed-motion span with sustained source-observed selected-point flight outside **all** complete fresh target-court actor body/pose envelopes, plus a later independently supported trajectory turn/contact whose motion samples do not recycle the same launch support. It must remain an activity hypothesis: no fabricated `ContactEvidence`, increasedcontactscore, forced impact, handrelease, serve, named hitter, opposite origin, team, winner or point. Retain an unknown origin set rather than picking the nearest wrist as truth.

Required caller contracts are complete/unique current populations for knownN=2or4; all four doubles actors must be considered. Unknown format, occluded/hidden actor, duplicate source/track observations, unavailable body/pose envelope, competing point hypotheses, rejected association, or camera/coordinate/content break must abstain. Stable source identities, actual adjacent camera states, measured point support and explicit gaps are necessary. Existing motion and geometry gates can bound a study; **no new numerical departure threshold can be selected from11715 alone**. Joint/box uncertainty is not provided by the current data and must not be borrowed from shuttle sensitivity.

The present retained geometry supports feasibility but is insufficient to certify that proposed predicate:11714 follows a gap and is about56px from its nearest fresh wrist in the earlier descriptive study. Held-current controls can move tens of pixels while remaining body-carried. A wrong model peak can also appear to leave every box. Thus no safe validated production rescue is established yet. The minimum immediate change remains a documented failure and a reviewable activity proposal, not forced admission.

## Validation before any implementation/adoption

Preserve a baseline and assemble source-reviewed, match-disjoint temporal-activity positives and hard negatives: held shuttle/body carry, pickup, static head/racket/shoe/banner aliases, moving racket without flight, actor overlap/occlusion, background peaks, duplicate CFR/source observations, gaps/reacquisition, camera changes, cuts/replays, unknown format, and complete four-player doubles. Keep contact/hitter labelsunknown wherever the source does not establish them. Test all-actor completeness and independent support composition, then report activity false admissions/misses separately from contact accuracy and interval boundary metrics.

If later authorized, a semantic-only candidate may be replayed over the preserved5aeperception. Record the original nativeNNproducer/decoder and the new semantic execution root/commit/configuration/source hashes separately; never rebase an importedROOT or describe cached replay as freshNN. Compare full traces, every previous activity/reference row, all callbacks, contacts, classes, unknown outputs and retractions, including held/alias negatives and both complete videos.

A narrow finalization-versus-cancellation change may leave both pathsidleat the same frame, but this is a hypothesis to verify: compare every frame's FSMstate/in-play and every actual perception hint at each chunk frontier, plus calibration, format, model/profile and source-context inputs. Only identical feedback supports a fixed-perception comparison. Any altered demand, scheduling, calibration, format, context, or acquisition request requires fresh neural evaluation. Do not apply the separate dense-perception idea inside a semantic-only claim.

No fix, new contact label, physical accuracy gain, or final aggregate acceptance is claimed. The unresolved short miss remains in the current matrix. Prior completed [departure feasibility](../pre_test03_rally_departure_feasibility_v1/REPORT.md) and [regression diagnosis](../pre_test03_test02_regression_diagnosis_v1/REPORT.md) remain unchanged; this report adds the completed current-run causal check.
