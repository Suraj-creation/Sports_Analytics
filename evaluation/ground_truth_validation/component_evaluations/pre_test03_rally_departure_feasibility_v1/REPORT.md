# Short-rally departure witness: CPU-only feasibility

**A separate activity-departure hypothesis is technically plausible, but the retained evidence does not yet justify a production short-rally rescue.** No contact score, impact status, duration threshold, rally decision, production source, profile, model, or current frozen V5 worker was changed. This study uses the archived completed **V4/2418 Test2** observations, not results from the active V5 run.

The relevant distinction is activity versus impact. The FSM already opens at11716 from three observed moving frames and later cancels the short11716–11751 interval under the existing duration policy. Adding a departure witness would change the evidence allowed to retain that interval. It would not establish a racket impact at11715, a serve, named hitter, team, winner, or point.

## Measured source-cache geometry

All876 previously generated body-relative rows and their14 source/catalogue bindings were read without modification. Measurements below use fresh matched boxes and fresh poses only. Distances are registered image pixels, not airborne floor coordinates. Box and wrist uncertainty is unavailable; shuttle sensitivity was not reused as joint or box covariance.

| Archived case | Fresh frames | Point displacement | Actor-center displacement | Box gap, first→last | Wrist distance, first→last |
|---|---|---:|---:|---:|---:|
| Old held control |810,816,822|0.84px|0.47px|0→0px|8.46→7.66px|
| Current later held control |822,828,834|25.66px|3.34px|0→0px|8.61→10.28px|
| Short-exchange origin→flight |11714,16,18,20,22,24|70.44px|2.90px|5.75→73.27px|56.26→142.32px|
| Short FSM’s first three fresh boxes |11716,18,20|40.28px|0.70px|23.13→61.66px|69.14→114.68px|
| Later source-reviewed serve |904,906,908,910|205.80px|7.81px|0→139.72px|8.12→166.70px|

The held-current control is particularly useful: body-relative displacement is23.69px despite the prediction remaining inside the box and about9–12px from a wrist. Speed or body-relative displacement alone therefore cannot establish departure. In the short sequence the point separates progressively from both the near body box and its wrists, then approaches the other actor’s geometry. That is supportive descriptive geometry, not an independently labelled shuttle trajectory.

At11714 the near actor is closest by box distance5.75px versus61.91px for the other actor, and by wrist distance56.26px versus85.94px. At11716 the wrist-distance difference is only2.65px; the other actor becomes the nearer wrist later in the flight. A future policy must preserve the source-origin hypothesis and its uncertainty, rather than retargeting a flight to whichever actor becomes nearest. No calibrated uniqueness margin is available. The56px initial wrist distance also does **not** demonstrate a hand release or racket impact.

Frame11714 is a shuttle **reacquisition** after missing11711–11713; frames11715–11731 are observed/tracked in the retained selected model output. Fresh boxes exist at11714/16/18/20 and later even frames. The positive serve control has missing905 followed by reacquisition906. Blanket rejection of every gap or reacquisition would reject that source-reviewed positive too. Gaps may break the evidence chain; they must not be silently interpolated into observed flight.

The former11715 fusion score remains0.2824266945, below the unchanged0.35 acquisition threshold. Its physical impact remains ambiguous. This study does not restore or rescore it.

## Later opposite-side evidence

The append-only ledger contains a provisional11740 far-episode contact with fresh player observations11736/38/40/42, same shot3/content21/coordinate1, tracked shuttle association, probable trajectory and probable physical-evidence assessment. These are uncalibrated algorithm assessments. Both near and far episode observations occur simultaneously in its source context.

That event is **absent from the final live contact ledger after rally cancellation**. It may be retained as causal evidence when researching a new admission policy, but must not be described as an additional accepted live contact or independent human ground truth. Avoid a circular design in which a rally validates a witness whose sole authority is that same rally’s acceptance.

The876-row geometry export does not contain actual origin participant birth-context objects. Raw track0 and source epoch continuity are insufficient substitutes. The existing engine buffers retain source participant snapshots and can supply the proper context in a future implementation. This study did not fabricate an origin `ContactParticipantContext` or run another full replay to produce one.

## Existing contracts and minimal research proposal

Reuse the replaceable **rally-admission** boundary, leaving contact acquisition and physical evidence unchanged. If later authorized, introduce a separately versioned typed activity witness with:

1. Source frame/PTS references, observed selected point samples, association status, temporal/coordinate epoch, valid current camera/view, and explicit missing/rejected observations. Count unique source observations; repeated CFR samples or repeated observation identities must not create extra support.
2. A retained source-origin episode hypothesis from simultaneously fresh target-court participants, with box/pose provenance and uncertainty. Departure describes increasing separation from that actor’s actual body and relevant observed joints, while distinguishing body-carried motion. A nearest-box point alone cannot certify origin.
3. Sustained observed flight, with its measured temporal support separate from any later contact’s motion samples. Missing association, camera transitions, epoch breaks, body occlusion, competing point hypotheses, and ownership ambiguity remain unknown.
4. A later independently source-observed opposite episode/trajectory witness. Reuse `simultaneous_opponents` and the existing bounded participant context for this pair proof. Do not manufacture `ContactEvidence`, set contact confidence, or reinterpret the departure as impact.
5. Explicit singles/doubles/unknown-format treatment. The pair helper proves only two opposite episodes; it does not check that four-player candidate ownership is complete. Doubles requires considering all four relevant candidate actors. A hidden partner, duplicate track, same-side ambiguity, or uncertain roster must not be resolved by forcing a singles origin.
6. A separate reviewable admission reason and complete witness payload. Any optional short-duration policy consuming it needs its own component/configuration/cache identity and before/after regressions. Existing duration/contact policies remain the baseline.

No numerical departure/uniqueness threshold is proposed from these evaluation examples. Source-bound labelled positive and hard-negative departure examples, error characterization of body/joint localization, and match-disjoint validation are missing. Selecting a cutoff to rescue11716 here would be tuning on the evaluation case.

## Controls and readiness

Ten CPU synthetic controls exercise the **unchanged** native episode-pair helper. It accepts consistent observed opposite episodes with singles or four visible doubles actors, and rejects unknown context/target, cross-epoch context, same-track or same-birth collisions, same-side targets, and duplicate source participant rows. A deliberately partial doubles population still produces a pair proof: the caller therefore needs a separate complete/unique-origin policy rather than assuming that helper supplies it. These are contract tests, not measured video accuracy.

Before adoption, additionally test static background peaks; racket, head, shoe and banner aliases; a held object moving with a wrist; a moving racket without projectile flight; multiple candidate actors; duplicate source frames; camera/epoch breaks; missing/rejected associations; actor occlusion; all four doubles participants; and unknown identities. A wrong model point can satisfy convincing image-plane motion. The current data cannot prove physical object identity from geometry alone.

The corrected V5 scene resets may alter background/association history and thus the actual upcoming Test2 inputs. Reassess this archived case after the genuine V5 completion before planning any additional change. No fix to the missed coarse-reference interval is claimed.

Evidence: [descriptive measurements](window_measurements.json), [actual cached short context and causal ledger excerpt](actual_short_context.json), [measurement receipt](measurement_receipt.json), [unchanged native pair-contract controls](context_controls.json), [measurement tool](measure_departure.py), and [synthetic control tool](probe_context_contracts.py).
