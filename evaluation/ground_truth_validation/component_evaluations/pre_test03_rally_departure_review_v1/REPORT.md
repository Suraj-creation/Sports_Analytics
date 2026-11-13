# Contact-independent short-activity departure: paused design note

A distinct short-rally activity witness is scientifically preferable to relabelling Test2 frame11715 as a physical contact. The current pipeline already opens a provisional rally at11716 after three adjacent observed movements; the loss is short-duration retention because its two remaining selected contacts both refer to the far episode. There is no need to fabricate a contact or a new start.

This review is paused for higher-priority confirmed scene regressions. No algorithm, threshold, candidate channel, event or label was changed. The following is an engineering proposal, not validated physical improvement.

## Existing implementation and actual current evidence

`RallyFSM.step` independently opens on the existing3observed frames above3analysis px/frame. Current actual trace11716–18 has observed speeds17.111990,12.985903,11.500129. It opens11716 when11718 arrives. The initial observed run continues through11720;11721slows and breaks that moving-run predicate. These are raw-observed rather than interpolated coordinates. Shuttle association is tracked at11716–20; actual fresh player matches exist11716/18/20. Current source epoch21/shot3 is stable.

`EvidenceRallyFSM._short_exchange_witnesses` can retain a short interval using two selected contact explanations and existing `simultaneous_opponents` proof, independently of probable physical impact for both. Its only witness acquisition path is `on_contact_evidence`, so the near episode's below-threshold fusion score never enters. Current11731 is ambiguous, and11740 has probable trajectory and impact; both target the far episode. Existing non-overlapping motion fits and simultaneous opposite-episode observations cannot establish two different targets from those two far cues.

General `ActivityTracker` already supplies contact-independent ACTIVE_PLAY from sustained moving people and shuttle trajectory. Its default2swindow plus1shold is deliberately conservative, has no typed episode-origin proof, and cannot simply be substituted to rescue this sub2sexchange. No existing module found implements a projectile departure from one anonymous episode paired with a later opposite episode for short-rally retention.

The recorded current source shows active near-side movement followed by far-side racket action; exact impact frame, shot class, named person, service and winner remain unlabelled. Three original source frames11715/11718/11740 were independently viewed here. This is agent diagnostic evidence, not new ground truth.

## Smallest plausible component extension

A separately typed, immutable `RallyDepartureWitness` could identify the first observed motion span already responsible for a provisional start. It would contain canonical anchor/span, available-through, observed sample references, declared motion sensitivity, uniquely proximal anonymous episode, fresh participant provenance and source shot/content/coordinate epochs. It would assert departure/activity only. It would not be a `ContactEvidence` clone or contact/stroke event.

The engine should build it from existing participant-window and observation data, through the replaceable rally/activity component boundary. It must not construct a fictitious low-score contact to reuse the callback. Existing same-context spatial projection and participant-context assembly may be factored into shared helpers. A new optional rally port or typed rally-observation field would need explicit compatibility, version, state/reset/restore and cache identity.

Retention could then require that independent departure plus the existing later far witness, with exactly the same simultaneous-opponents identity/epoch/birth checks and bounded original short-event horizon. Keep the existing provisional start11716 and boundary policy. Preserve physical contact11715 as absent/below-threshold and ambiguous impact; preserve all current raw scores, selected contacts/strokes, winner abstention and identity uncertainty.

## Unresolved scientific predicate: leaving the body

Image motion alone is not projectile departure: a held object, racket/head/shoe alias or moving person can move quickly. The candidate must show observed object motion relative to the source body's actual observed motion, plus persistent increasing separation from its uniquely proximal episode. An independent source-cache measurement is being prepared by the component agent; this note does not declare that predicate satisfied.

Reuse declared existing start-speed/run-length, contact proximity ambiguity, observed-only and context-boundary controls where their meanings apply. The0.7217pixel shuttle sensitivity is not wrist/body localization covariance. It cannot be silently reused as a calibrated threshold on body-relative distance. Positive numerical separation alone can be jitter; containment alone fails when a shuttle is already outside a detector box near a wrist. A defensible typed witness needs an explicit uncertainty/unknown policy instead of a new fitted body-radius or video-specific rule.

The actual observed flight is not continuously tracked all the way to11740:11732–33are missing and11734is reacquisition. A complete continuous-observation requirement would fail this case. Existing bounded ordinary-gap semantics may preserve an already observed activity hypothesis, but missing coordinates cannot become observed flight or prove branch identity across the gap. The later probable far witness can corroborate activity without retroactively labelling the hidden path.

## Required falsification controls before adoption

- Baseline809held/preparation: ordinary image movement or a zero incoming-direction artifact must not qualify. Current809has no accepted raw shuttle observation. Keep904actual later source activity separate; no generated start807-as-contact truth.
- Stationary object, moving-body-held object, racket/head/shoe alias, discarded/reacquired branch, missing/interpolated samples, unresolved direction and ordinary off-field activity.
- Fresh near departure followed by the same episode only must fail opposite-episode retention; two different track keys without simultaneous stable birth/provenance must fail.
- Scene/format/court/camera changes, replay, identity ambiguity and reference-image transforms must break the proof. The first span and later witness must share actual epochs.
- Doubles must retain all four players and abstain on ambiguous teammate proximity. Opposite image/court halves do not establish a named person or team. Unknown format cannot silently force singles.
- Only retention of an existing provisional short activity interval may change. No new contact, service, class, winner, score, unknown-flight coordinates or gap-timeout enlargement.
- Full frozen-cache or fresh before/after controls across Test1/Test2 with all original references and source cases are required. A recovered generated row alone cannot validate the policy.

The proposal is an explicit activity-evidence extension, rather than a repair of a falsely promised existing departure API. It deserves a controlled test only after the body-relative predicate and negative controls are established. Confirmed scene-reset defects have priority.
