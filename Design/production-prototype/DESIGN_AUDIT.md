# Design audit — amateur badminton product

**Reviewed:** 22 October 2026. **Scope:** all 15 specifications in this folder, the current Vite/React app, API routes, engine contracts, and the existing validation report. **Outcome:** the specifications have been corrected in place; this report records the remaining implementation gates and research questions. P0/P1/P2/P3 below refer to *player harm and prototype credibility*, not development effort.

## Executive verdict

The Moment-first concept is coherent and worth prototyping. Its strongest design choice is a player-controlled path from a replayable rally to evidence, correction and optional depth. It can be tested now with explicitly labelled fixtures. **It is not ready to present as an end-to-end live amateur service.** The current app is an analyst-oriented session viewer (`apps/web/src/router.tsx`) with shared-passphrase access; the API begins analysis on upload (`apps/api/src/bai_api/routes/sessions.py`), and it lacks server consent, personal identity, unscored processing, resumable transfer and safe share links. The only cited real-video winner check was 61.5% on broadcast footage (`docs/testing/REALTIME_BADMINTON_VALIDATION_REPORT.md`); phone footage remains unvalidated. The biggest risks are a confident wrong result, a false privacy promise and a demo that appears to be a real user history.

**Readiness:** fixture-led usability prototype **yes**; limited live scored-singles technical demonstration **with explicit constraints**; public amateur release **no**. Doubles matters to the social-play proposition, but the engine's two-track identity type makes a doubles recap dishonest today. Excluding doubles from the first *implementation* is acceptable if the entry flow states the limit before upload, the research sample includes doubles players, and the team measures how many prospective users are excluded.

## Findings and corrections

| Priority | Evidence and exact place | Player impact | Action and disposition |
|---|---|---|---|
| **P0** | `00` D5 and §7, `06` §1.4, `07` §4.1, `11` §3.1 mapped raw `confirmed` to “Looks right”; `11` §8 reports 61.5% winner accuracy and uncalibrated bands. | A reassuring phrase can make a wrong winner or score look vetted. | Reserve “Looks right” for a claim type and capture condition validated under G-08/G-11. Before that, winner/shot candidates are “Worth a look”; “Checked” attaches only to what a human reviewed. Corrected in `00`, `02`, `06`, `07`, `08`, `09`, `11`. |
| **P0** | `03` §0 and §6 had consent after upload in prose but before bytes in the flow. The current `POST /api/sessions` uploads and starts processing; `11` G-05/G-12 are absent. | The player may believe the video remains private or deletable when the service cannot enforce the promise. | Keep consent before any upload. Treat the real upload journey as gated by server consent, retention and draft lifecycle. Keep delete-after-analysis disabled until all media derivatives are deleted. Corrected in `00`, `03`, `10`, `11`, `12`; implementation pending. |
| **P0** | `03` §5.3 placed a remote 10-second suitability probe before the §6.2 consent step. A probe still transmits identifiable footage. | Video could leave the device before the player agrees to processing and temporary retention. | Allow local metadata guidance before consent; offer a bounded server probe only afterward, with its own retention and cancellation explanation (G-ONB-2/G-05). Corrected in `03`; endpoint pending. |
| **P0** | `00` D12, `03` §6.1, `05a` New match and `12` Phase 1 offered Social game/Practice while the engine always performs a BWF score fold (`11` G-04). | Hiding score in the UI does not stop score-dependent moments, Ask or exports from using a fabricated result. | Real processing supports scored singles only until G-04 provides true unscored logic and downstream suppression. Social/Practice are sample-only or disabled with a reason. Corrected in `00`, `03`, `12`; downstream API work pending. |
| **P0** | `05a` Recap/Matches, `06` §2, `07` `ScoreStory`, and `09` examples sometimes treated one checked winner as a checked final score. | A single correction could falsely validate an entire match narrative. | A checked score requires review of all contributing winner/official decisions and match start, with recomputation after each correction. Omit score-dependent prose otherwise. Corrected in shared rules and key examples; enforce with a dependency graph in the product API. |
| **P0** | `05c` Share, `07` `SharePreviewDialog`, `10` §5 and `11` G-05/G-28: current `clip.mp4` is an export, while consented links, participant approvals, redaction and audio controls are proposed. | An opponent or bystander may be exposed even when names are hidden. | Fixture-only share preview until server checks every participant and clip, strips/redacts audio as chosen, enforces expiry/revocation, and confirms the exact preview. Corrected in `05c`, `10`, `12`; implementation pending. |
| **P1** | `05b` §Review & fix and `07` `FixSheet` promised Undo and offered bulk “Checked”; `apps/web/src/lib/api.ts` only exposes verify/winner/official/match-start corrections. | Players may think they reversed a fix or checked events they never watched. | Hide Undo until G-14 supports persisted reversal and downstream recomputation. Remove bulk Checked. Feedback on unsupported correction kinds is not a saved fix (G-15/G-32). Corrected in `05b`, `07`; the example summary now omits Undo. |
| **P1** | `05a` Matches used `rallies + unofficial` as “followed” denominator; `11` G-20 had no defined coverage API. | A coverage bar can imply the system saw more play than it did. | Define candidate rallies, tracked duration, court-valid frames, unknown intervals and replay handling independently of official status. Do not show “31 of 36 followed” from the current aggregate. Corrected in `05a`, `06`, `11`. |
| **P1** | `06` §2 labels several counts Available while `00` §2.4 and G-11 say phone footage is unvalidated. | False precision may make an amateur compare sessions captured under different conditions. | Treat phone-footage counts and Moments as Preview until G-11 validates by angle, lighting and coverage; withhold trends until G-02/G-07/G-20 enable comparable definitions. Corrected in `00`, `06`, `11`. |
| **P1** | `05c` §0 and §14 reused G-05 several times and labelled Help/Feedback Available though feedback intake is G-32; `05a` labelled Feedback G-30. | Engineers may build the wrong dependency or make a “we’ll look” promise without a queue. | Canonical register is `11`: G-30 preferences/focus; G-32 feedback; G-05 consent/share/deletion; G-28 export audio. Consolidated `05c` references and corrected `05a`. |
| **P1** | `12` Phase 1 proposed a real share and all-purpose upload before its dependencies; `03` upload visual included Pause though the current request is one XHR. | Prototype users may mistake a simulated capability for reliable recovery or sharing. | Keep sample data on a clearly entered demo path; label non-resumable restart and avoid Pause until G-12. Corrected in `03`, `05c`, `12`. |
| **P2** | `04` presets and `05a` Recap risk four experiences with overlapping purpose/depth controls. | A casual player may not know whether changing mode changes facts or loses their place. | One Recap, one claim/evidence model; presets only reorder and set depth. Preserve match, scroll context and corrections on switch. Corrected in `04`; test with a preset-change task. |
| **P2** | `01` opening assumed a fixed weekly pattern and a result “within seconds”; `03` gives time targets despite potentially long processing. | A player with sporadic play or slow uploads may feel the service failed. | Describe those as research hypotheses/targets; make waiting and no-reliable-Moment states first-class. Corrected in `01`, `03`. |
| **P2** | `08` §16 forced Deep dive dark even when the player chose Light/High contrast. | Can reduce readability and perceived control. | Respect explicit theme/accessibility settings in Deep dive; theatre may default dark. Corrected in `08`. |
| **P2** | `09` loss example opened with score and “tough”, while D6 makes score context optional. | The product can reframe a casual session as a failure. | Start with an inspectable Moment and make score an optional destination. Corrected in `09`; test after a seeded loss. |
| **P3** | `07` inventory has many specialised components and `05c` future screens; current app has a small primitive set. | Implementation can fragment into one-off cards and inconsistent states. | Consolidate `CheckChip`, `EvidenceChip`, `CoverageBar`, state shells and clip actions before building variant screens. Use the same components in sample and real data. Validate reuse during Phase 0. |

### Product and behavioural judgment

Moment → My game → Together is the right emotional hierarchy for a casual recap, provided “Together” stays quiet when no consented social data exists. Deep dive is a separate workspace for players who ask for it. A poor performance should still offer an inspectable exchange, a neutral account of what was observed, and an easy exit; it must not manufacture praise. The “positive Moment for everyone” rule is a *selection aim*, bounded by evidence, not a guaranteed output. `06` now filters for consent before ranking and again before export.

The product's autonomy and self-reference choices are plausible from self-determination research, and learner control over feedback timing has support in motor-learning experiments. Neither establishes that this particular recap will improve badminton performance or retention. Treat emotional safety, preference for Moment-first, and useful return as hypotheses. See [autonomy-support review](https://doi.org/10.1080/1750984X.2022.2031252) and [self-controlled video feedback experiment in tennis](https://pmc.ncbi.nlm.nih.gov/articles/PMC11147453/); the latter is an adjacent sport and should not be generalized without player testing.

### Screen and component decisions

- **Landing and sample (`03` §2–3; `05a` Landing):** show one credible sample with a persistent Sample label, one visible limitation and a direct route to analysing a video. Test whether users understand that the example is fictional. No “20 seconds to your own result” promise.
- **Capture and upload (`03` §5–8; `05a` New match):** suitability is a proposed service, not a validated phone-footage classifier. Provide a manual filming checklist now; show server-confirmed upload and processing states. Track mapping may arrive after analysis has started, so suppress “you” claims until persisted identity and recomputation complete.
- **Recap/Moments (`05a` §7–10):** show a clip first when the rally boundary and playback are usable. The reason for selection must be observable. No scored “big point,” personal best, share or first-shot label without its separate gate. Empty/partial/error screens should say what is ready, what remains unknown and what action is possible.
- **Deep dive/Review (`05b`):** keep court, shots and score as opt-in analysis; expose denominators and supported capture conditions. Verify only the event the player viewed. After a correction, refetch the persisted fold before saying what changed.
- **Progress/social/settings (`05c`):** real history requires G-02; Together requires identity and G-05, with doubles additionally G-03. A profile preference for doubles is harmless but must not suggest support. Privacy and deletion controls must show actual server state, not local-only toggles.
- **Components/tokens (`07`–`09`):** trust state, capability readiness and coverage are distinct signals. Do not hide any behind hover or rely on colour. Make 320 px reflow, 200% text, keyboard playback/court adjustment, focus return and reduced motion release checks; `08` targets WCAG 2.2 AA. A raw-band chip with a Preview tag fails the trust rule.

### Screen-by-screen disposition

| Spec section / screen | Finding and required treatment |
|---|---|
| `05a` §1–2 Landing, Sample | Keep the sample-first path; distinguish fictional values from measured capability and show singles/footage limits before upload. |
| `05a` §3 Home | A hero and progress signal cannot come from a missing user history. Use a clear first-match empty state and suppress progress until G-02/G-07. |
| `05a` §4 Matches | A neutral score chip is still a score claim. Require the complete checked fold; show coverage only after G-20 defines it. |
| `05a` §5 New match | Restrict live input to scored singles; remote test-clip checks happen after consent. Disable Social/Practice until G-04. |
| `05a` §6 Processing | Separate transfer percentage, server receipt and analysis progress; never promise background continuation or Resume without server confirmation. |
| `05a` §7 Recap | Preserve Moments → My game → Together, with Deep dive separately. Provide no-reliable-Moment and low-coverage states; withhold score-derived lenses when unchecked. |
| `05a` §8–10 Match Moments, All Moments, Clip detail | A player-selected clip is not a verified finding. Save needs G-06; download/share need G-05/G-28 and clear audience/audio review. |
| `05b` §1–3 Deep dive, Story, Rallies | Keep evidence adjacent to the claim; make score-state filters conditional on checked score and maintain playback/frame links. |
| `05b` §4–5 Shots, Court | Shot names are candidates; receiver position is not shuttle landing. Hide true landing and metric distance until G-10/G-09 respectively. |
| `05b` §6–7 Compare, Ask | Compare only same-definition, comparable matches; Ask must refuse unsupported coaching and cite the exact video evidence for match claims. |
| `05b` §8–9 Review & fix, Place your court | Confirm one event at a time; refetch after mutation; gate Undo and unsupported correction kinds. Court fitting needs keyboard/touch parity and a clear unsupported-footage exit. |
| `05b` §10–11 Advanced, Quality | Expose event lineage without implying all events are reliable; separate coverage, label reliability and score reliability. |
| `05c` §1–4 Progress, Records, Shot Explorer, My story | Fixture-only until history, comparable metrics, identity and corrected firsts exist. A zero, missing value and excluded match need distinct states. |
| `05c` §5–6 Explore, Focus | Keep optional and dismissible; a practice suggestion is a hypothesis and should not mark itself achieved from a view or a single match. |
| `05c` §7 Together | Singles friendship still needs two people's approval; doubles requires G-03. Keep the real route as a quiet Not yet state. |
| `05c` §8 Share | Preview the actual media and people, not just labels. Fixture demo creates no link; real controls require server enforcement and revocation. |
| `05c` §9 Settings/Privacy | Show persisted consent and deletion-job status. A local toggle cannot claim to revoke server access; explicit theme choice must carry into Deep dive. |
| `05c` §10–11 Help, Feedback | Static help can ship now; metric definitions need G-07 and a feedback receipt needs G-32. Privacy reports need an immediate stop-sharing path. |

## Prototype validation

Recruit 12–18 adults across first-time, casual singles, frequent improvers, club competitors and doubles-heavy/social players; include lower-bandwidth phones, varied filming angles and people using larger text or assistive technology. This is formative coverage, not a statistically representative sample. Use labelled fixtures, including a loss, one wrong winner, no reliable Moment, low coverage and a privacy request. Do not use real opponents' footage without their permission.

| Task | Observe | Probe afterward |
|---|---|---|
| Landing → sample → own upload decision | Can state the benefit and a current limit; can distinguish Sample from personal data | “What do you think this can tell from your video?” |
| Set up a phone recording and choose match type | Whether they notice singles/scored limit and can predict what happens to a social game | “What would you expect from a casual doubles video?” |
| Find first Moment after a seeded loss | Time to clip, affect, whether praise sounds credible | “Did any part feel judging or forced?” |
| Explain a seeded uncertain claim, then watch and correct it | Whether they distinguish Checked, Looks right, Worth a look and can predict what changed | “What exactly did you check? What is still uncertain?” |
| Save privately, inspect share preview, revoke permission | Whether they predict who can see the video and what copies remain | “If you revoke now, what happens to a download?” |
| Switch Relax → Improve and compare two sessions | Whether they understand preset changes and reject an invalid trend | “Which facts changed, if any? Are these matches comparable?” |

Measure unaided teach-back, critical errors (wrong certainty, accidental share, false data deletion belief), task completion, time to inspectable Moment, perceived pressure/enjoyment, and willingness to use it after the next match. Interview people who say “I would not return”; successful one-time use is legitimate. Proposed pass bars in `12` are team targets, not established literature thresholds. Stop or redesign a surface after any unconsented exposure or systematic misreading of an uncertain claim.

## Implementation readiness and ten actions in order

1. **Lock the claim gate and data-source boundary** (`00`, `06`, `11`): Sample / Preview / Not yet; raw bands never authorize “Looks right.”
2. **Build reusable trust, evidence and state components** (`07`–`09`), with keyboard and responsive acceptance.
3. **Create the labelled fixture suite** (`12` §4) with loss, uncertainty, no Moment, correction, deletion and doubles-exclusion cases.
4. **Test the core sample journey with players** before coding more screens; use teach-back and privacy tasks above.
5. **Implement server consent, draft upload and truthful retention/deletion** (G-05/G-12) before opening a live upload journey.
6. **Persist the “which one is you” mapping and correction propagation** (G-01/G-25); gate every “you” sentence on it.
7. **Validate amateur footage and coverage definitions** (G-11/G-20), then calibrate bands by claim type and filming condition (G-08).
8. **Ship the narrow live scored-singles Moment/Recap path** with fair selection (G-18), resolvable evidence (G-19), and withholding for unsupported claims.
9. **Add unscored processing and metric definitions** (G-04/G-07/G-09) before real Social/Practice, court maps or quantitative comparisons; build cross-match history (G-02) only after comparable metrics exist.
10. **Add share and Together only after participant consent, safe media exports and revocation work** (G-05/G-28); doubles needs G-03 and its own validation. Add Undo only after G-14.

**Current stack fit:** TanStack Router can host the new routes and preserve `?f=` evidence links. Existing clip playback, event provenance and correction calls are useful foundations. None of the pending gates requires a framework migration. No application code was changed in this audit.
