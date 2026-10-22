# 12 — Build Plan, Fixtures, QA and User Research

**Purpose.** Turn the spec into an ordered build, make it testable without waiting for the backend, and define how we learn whether real amateur players value it. Build order follows **evidence readiness** (file 00 §7, file 11 §6), not feature glamour: *a privacy or accuracy foundation can outrank a promising feature* (Blueprint §15).

> **What "production-grade design prototype" means here.** A clickable, accessible, responsive product in `apps/web` that (1) runs entirely on **deterministic fixtures** so every screen and state is demonstrable and testable, (2) can demonstrate the existing engine on explicitly supported test footage, with an isolated real-data path gated by consent and capability checks, and (3) labels everything else honestly (**Preview / Not yet / Sample**).

---

## 1. Principles for the build

1. **Vertical slices over layers.** Each phase ends with an end-to-end journey a real person can complete.
2. **Fixtures first, API second, same DTOs** (file 11 §9). No screen waits on a backend gap.
3. **Reuse before rewrite.** Evolve the existing components named in file 00 §6; keep `?f=` deep links, playback store, frame clock, HLS player, calibration maths.
4. **Honesty is a feature flag you can't turn off.** Preview/Coverage/Checked chips ship in Phase 0, before the first real screen.
5. **Measure value, not activity.** Instrumentation (file 12 §9) ships with each slice.
6. **Every phase has a kill/rollback criterion** for harm (shame, false claims, privacy).

---

## 2. Phased build plan

Sizes: S ≤ 1 week · M ≈ 2–3 weeks · L ≥ 4 weeks (one small team; treat as relative, re-estimate after Phase 0).

### Phase 0 — Foundations (S–M)
**Goal:** a shell and a vocabulary nobody can accidentally misuse.

| Work | Detail | Docs |
|---|---|---|
| Tokens + themes | Court Daylight + Arena Night on one token set; migrate `styles.css` names with a mapping | 08 |
| `AppShell` v2 | `SideNav`, `BottomBar` with centre ＋, `AvatarMenu`, `PresetSwitcher`, `DepthSwitcher`, `DemoBanner`, `PreviewTag` | 04, 07 |
| Trust primitives | `CheckChip`, `EvidenceChip`, `CoverageBar`, `MetricPopover`, `NotEnoughToSay`, state family (`EmptyState`, `LoadingSkeleton`, `PartialAnalysisNote`, `FailedState`, `LowCoverageState`, …) | 07 |
| `DataSource` + fixtures | `ApiDataSource`/`FixtureDataSource`; fixture generator; all states represented | 11 §9, §4 below |
| Copy + lint | Copy constants module; banned-phrase unit test (file 09 lint rules) | 09 |
| Route skeleton | New route map + redirects from `/`, `/sessions/$id`, `/sessions/$id/calibrate`, `/system` | 04 |
| A11y harness | Axe in Vitest/Playwright, keyboard-trace helper, reduced-motion switch | 07, 08 |

**Exit:** every state of every primitive renders from fixtures; axe clean; banned-phrase test green; shell works at 360/768/1024/1440.

### Phase 1 — The Joy loop on fixtures, then a gated scored-singles pilot (M–L)
**Goal:** prove that a player can reach an inspectable Moment, understand its limits and correct a result. Fixture journeys come first. The real upload path opens only after G-01/G-05/G-11/G-12/G-18/G-19/G-20/G-25 meet their gates; real sharing waits for G-05/G-28, and real Social/Practice waits for G-04.

| Slice | Existing technical-demo source (not proof of release readiness) | Fixture-only parts and release gate |
|---|---|---|
| Landing + sample recap | — (Sample is a fixture, labelled) | all |
| Onboarding (value → optional purpose → record guide → local check → consent → optional probe) | on-device metadata only before consent | G-ONB-2 probe fixture until a server consent gate and G-11 validation exist |
| New match (source, type, who's who, court, consent, go) | existing scored-singles upload only after server consent gate | guest/consent flow is fixture-only until G-01/G-05/G-12; Social/Practice fixture-only until G-04 |
| Processing + progressive playback | `Session.status`, `StatusMsg`, HLS | stage names mapped (file 11 §5) |
| **Recap** (Moments → My game) | `analytics`, `highlights`, events; client-derived `FactTrio` | lens ranking runs client-side first (file 06 §7) |
| **Review & fix** | existing winner/official/match-start/verify calls | Refetch persisted before/after state for a provisional ChangeSummary; no Undo until G-14 |
| Moments library + Clip detail | rallies + `clip.mp4?from&to` | favourite/visibility flags local |
| Share preview | none on real user footage until G-05/G-28 | fixture-only link creation, persistently labelled Sample; no active external link |
| Deep dive v1 (Story, Rallies, Court, Ask) | existing playback and events | Court metrics hidden until G-09/G-20; Ask limited to cited descriptive facts |

**Exit (value):** ≥ 80 % of pilot players state the recap's main finding correctly unaided; median **active effort to first Moment ≤ 90 s** (target, to be validated); no critical privacy task failure; Review & fix completes a wrong-winner correction in ≤ 3 taps.
**Exit (honesty):** zero un-tagged Preview surfaces; every claim opens evidence.

### Phase 2 — Progress layer (M–L)
Needs the cross-match store (G-02). Build **on fixtures first**, then SQLite-backed.

Progress, Personal bests, Shot Explorer, My story, comparability rules, honest empty states, "fresh baseline". **Exit:** players can name one meaningful change *and* one limit of the comparison; no "improvement" claim from a single match.

### Phase 3 — Explore + Focus (M)
`FocusCard`, `ReflectionPrompt`, optional challenges (Rally Explorer, Shot Explorer, Court Explorer, Just Showed Up, Personal Best), Relax/Explore/Friendly modes, notification preferences (analysis-ready only until reminders are validated). **Exit:** opt-in challenge arm shows value *without* higher pressure/dismissal-harm scores.

### Phase 4 — Together (L) — gated by G-03 (doubles)
Doubles engine, pair identity, invites, Pair memory, consented sharing, `/s/$token`. **Exit:** partner-comfort and privacy-comfort scores ≥ target; zero unconsented exposure.

### Phase 5 — Advanced and Coach (M–L)
Compare matches, event table, filters, exports, coverage/limitations panel, coach workspace (athlete-owned access, annotated playlist, one question not a list of faults). **Exit:** expert users reach event-level evidence in one clear action and can challenge a result.

### 2.1 Dependencies at a glance

```
Phase 0 ─► Phase 1 ─► Phase 2 ─► Phase 3
              │            └──────────► Phase 5
              └─ real scored-singles pilot needs G-01/G-05/G-11/G-12/G-18/G-19/G-20/G-25
Phase 4 needs G-03 (doubles)  ·  Phase 2 needs G-02
Social/Practice needs G-04; numeric Quick facts need G-07; court metrics need G-09; sharing needs G-05/G-28.
```

### 2.2 What not to build yet (copied from Blueprint §15.1, still binding)
Universal player rating · daily streaks · default public rankings · public feed · real-time tactical instruction · injury prediction or medical advice · public opponent dossiers · autonomous technique coaching from unvalidated pose · generative advice that cannot cite match evidence · badge economies · native app by default.

---

## 3. Prototype scope cut (what "done" looks like for the first design-complete prototype)

**Must be clickable and honest (P0):** Landing + Sample · Onboarding (purpose, preset, record guide, test-clip result states) · New match · Processing (all states) · **Recap** · Moments · Clip detail · Review & fix · Deep dive (Story, Rallies, Court, Ask) · Place your court · Settings & Privacy Centre · Help.
**Clickable on fixtures, labelled Sample/Preview (P1):** Progress · Records · Shot Explorer · My story · Explore · Share preview.
**Designed, marked Not yet (P2):** Together/doubles · coach workspace · notifications beyond analysis-ready.

---

## 4. Fixture dataset ("the persona set")

Deterministic, versioned, reproducible; generated from the synthetic match generator plus hand-shaped metadata. Fictional people, no resemblance intended.

| Fixture | Purpose | Key properties |
|---|---|---|
| **Sample match** (labelled *Sample*) | Landing and first-run | 3 inspectable Moments and one honest uncertain item; scores, shot types and coverage marked as illustrative fixture values, not claimed engine performance |
| **Alex — Weekend Social** (singles ×3 matches) | Core loop and Progress | M-A: ready · M-B: ready, lost, still has a verified positive Moment · M-C: partial (movement pending) |
| **Match with no reliable hero** | Honest "why not" | Low confidence on all candidates; recap says why |
| **Low-coverage match** | Capture failure UX | 40 % rallies analysed; court lost mid-match; "what we could see" |
| **Unsupported footage** | Suitability result | Extreme angle; `not_supported` with fixes |
| **Interrupted upload** | Distinguish server-confirmed resumable draft from restart-only transfer | Stage `upload` partial → resumed only after G-12 |
| **Failed analysis** | Failure copy and retry | Retryable; what was kept |
| **Corrected match** | Review & fix | Wrong winner → `ChangeSummary` with rescored points and undo |
| **Warm-up detected** | "Not counted" | Unofficial rallies reinstatable |
| **No comparable matches** | Progress empty state | n = 1, honest baseline message |
| **After a break** | Return flow | 9-week gap; fresh-baseline offer, no regression alarm |
| **Social game / Practice** | D12 | No score; rally-only metrics |
| **Doubles sample** | Together (Not yet) | Visible only behind the "Not yet" preview; both partners' consent states |
| **Advanced user (Kabir-like)** | Deep dive/export | 20 matches, opponent repeat, filters |

Rules: every fixture marks `meta.demo = true`; every Insight in fixtures passes the same grounding validator as production (file 11 §9); fixture Preview tags match the readiness table in file 00 §7.

---

## 5. Test strategy

| Layer | Tool | What |
|---|---|---|
| Unit | Vitest | Metric formatting (n of m, units, null≠0), lens ranking, comparability, CheckState mapping, copy lint, `derive.ts` facts |
| Component | Vitest + Testing Library | Every component state in file 07; keyboard and ARIA; Preview/Check/Coverage always rendered together |
| Contract | zod/valibot (or TS) schema tests | DTOs from fixtures **and** from the real API validate identically |
| E2E | Playwright | The six core journeys (§6) + failure injection (kill network mid-upload, correction + undo) |
| Accessibility | axe + manual | WCAG 2.2 AA; keyboard-only; screen reader (NVDA/VoiceOver) on Recap, Review & fix, Consent; 200 % zoom; reduced motion |
| Visual | Playwright screenshots | Light/dark × 360/768/1440 for every P0 screen; regression diff on tokens |
| Performance | Lighthouse CI + custom | Budgets below |
| Security/Privacy | tests + review | Object-level authorisation, IDOR on matches/moments/share links, signed URLs, consent enforcement, no PII in logs |
| Content | CI | Banned-phrase and sentence-length lint; every `claim` has an evidence ref or `general_guidance` label |

### 5.1 Performance budgets (proposed — set with engineering after Phase 0)

| Budget | Target |
|---|---|
| Recap first content (cached) | ≤ 1.5 s on a mid-range phone, 4G-class network |
| Recap JS (route chunk) | ≤ 180 KB gz; Deep dive and Ask lazy |
| Moment thumbnails | Lazy, sprite-based; **no autoplay in grids** |
| Interaction latency (tab/filter) | ≤ 100 ms perceived |
| Upload | Resumable; no restart from zero; background on request |
| Long lists | Virtualised past ~100 rows |

### 5.2 Consolidated acceptance gates

- **Gate A — Coherence:** onboarding choices change the experience; consistent navigation; every route reachable; empty states guide forward; demo data labelled.
- **Gate B — Core loop:** open → recap → play → favourite → return; metric → evidence in one tap.
- **Gate C — Trust & consent:** every share checks clip-level consent; nothing public by default; permissions separate; low-confidence claims withheld or tagged; incorrect labels fixable; demo actions never claim real success.
- **Gate D — Accessibility & responsive:** keyboard-only works; focus visible and logical; dialogs accessible; charts have text and table; colour never the only signal.
- **Gate E — Metric integrity:** definitions exist; missing ≠ zero; trends use comparable matches; denominators shown; corrected results propagate with explanation.
- **Gate F — Harm check:** shame/pressure survey item below threshold; no unconsented exposure; no false record shipped.

Screen-level acceptance IDs live in files 03 and 05a–c (`AC-…`).

---

## 6. The six core journeys (E2E scripts)

| # | Journey | Pass condition |
|---|---|---|
| J1 | **Casual: landing → sample → my first match → Hero Moment → save → back** | First Moment visible without a table; saved privately |
| J2 | **After a loss:** open recap → choose Quick/Deep/Later | Same layout and quality as a win; no celebration tied to result |
| J3 | **Fix it:** wrong winner → Fix this → ChangeSummary → undo | Re-scored points explained; undo works |
| J4 | **Am I improving?** Progress → comparable matches → open evidence | Limits named; no trend if n < threshold |
| J5 | **Privacy:** open Privacy Centre → revoke share → try to share | Blocked with clear reason; ledger shows change |
| J6 | **Deep dive:** switch to Advanced → rally filter → evidence → export | Event-level evidence reachable; coverage visible |
| J7 | *(Not yet)* **Partner:** invite → consent → pair memory | Specced; tested when doubles lands |

---

## 7. User research plan

### 7.1 Recruitment
Cover: age groups; beginners, recreational regulars, restarters, club players; singles and doubles; digital confidence; phone quality and connectivity; **people who tried similar apps and stopped**; coaches/organisers. Include players with accessibility needs. Avoid friends of the team (Blueprint §16.1). Adult-only for the pilot.

### 7.2 Studies (in order)
1. **Context interviews + court observation (before more design).** Ask about *recent behaviour*: "Tell me about the last time you wanted to play again." · "What made a session worth remembering?" · "What would feel embarrassing or intrusive in a sports app?" · "When would you prefer not to see analysis?" · "Which statistic would you trust least?" · "What would make you delete the video?" · "Would you still value this if you did not improve?" (v2 §13.3). **Observe real capture:** where the phone goes, who films, scoring habits, group-chat sharing.
2. **Footage collection** (also G-11): ≥ 30 sessions across angles, courts, light, singles/doubles, with and without scoreboards; labelled rallies/winners/contacts. Gate for capability labels.
3. **Concept test** of the Sample recap and landing (5-second test, expectation-match, "what would you do next?").
4. **Prototype usability** (moderated, then unmoderated) with the task list below.
5. **Diary / longitudinal pilot** (4–6 weeks): what they do between sessions; return, non-return reasons (the five states, Blueprint §6); successful non-use.
6. **Accessibility testing** with assistive-tech users.

### 7.3 Usability tasks and pass criteria (from Blueprint §16.2 and v1 doc 06 §8)

| Task | Observable success | Likely failure |
|---|---|---|
| Explain the product after the landing | States a realistic benefit **and** one limit | Repeats "AI coach" |
| Choose sample vs own footage | Picks correctly and unaided | Can't judge suitability or cost |
| Set up a recording (record guide + test clip) | Passes `suitable` without help | Ignores guide; unusable footage |
| Complete an upload after interruption | Recovers without loss/duplicate | Restarts or assumes done |
| Pick yourself on the frame | Selects themselves first try | Mis-maps P1/P2 |
| Find the best moment | ≤ 15 s on phone | Wanders the metric list |
| Explain one number | Names the denominator and what it means | Confuses volume with success; zero vs missing |
| Open the evidence | Taps "Watch this" and describes it | Treats summary as unchallengeable |
| **Detect a seeded wrong finding** | Uses evidence to reject/qualify | Accepts because it sounds confident |
| Fix a wrong winner | Completes in ≤ 3 taps and explains the re-score | Cannot find Fix this |
| Save a clip without sharing | Predicts who can see it | Thinks hiding names = privacy |
| Change from Relax to Improve | Understands what changes | Believes the segment is permanent |
| Compare two matches | Names one comparability limit | Calls any favourable change "improvement" |
| Find the Privacy Centre and revoke a permission | Without reading policy | Misses it |
| Interpret missing data | States what cannot be concluded | Certainty or total distrust |

**Launch bar (proposed, not a literature standard):** ≥ 80 % state the recap's main finding accurately without help; evidence/uncertainty/correction controls findable; critical privacy tasks succeed without reading policy; advanced users reach event-level evidence without complicating novice defaults; no systematic reading of hypotheses as facts. Record **critical errors** separately from speed (a fast privacy mistake is a failure).

### 7.4 Experiments (hypotheses to test, each with a guardrail)

| ID | Hypothesis | Comparison | Primary outcome | Guardrail |
|---|---|---|---|---|
| **X1** | A Moment-first recap beats a metric-first report | Moment-first vs metrics-first | Correct teach-back; time-to-value | Time, frustration |
| **X2** | Sample-first landing reduces expectation mismatch | Sample before upload vs direct upload | Accurate expectations → activation | Overpromise, abandonment |
| **X3** | A test-clip check raises usable footage | Test clip + guide vs existing instructions | Usable-recording rate | Burden, drop-off |
| **X4** | One skippable purpose question improves fit | One question vs neutral default | Confirmed value | Setup drop-off, stereotyping |
| **X5** | Coverage + withholding improves interpretation | Coverage explanation vs plain report | Correct scope reading | Confusion, unjustified confidence |
| **X6** | Fix-this-first (Review & fix) increases trust | Review queue before recap vs after | Trust calibration; acceptance of correct, rejection of wrong | Burden |
| **X7** | Personal-baseline comparison is understood and trusted | None vs baseline vs baseline+clips | Interpretation accuracy | Rumination, pressure |
| **X8** | Opt-in challenges add value without pressure | Challenge vs none | Voluntary return; enjoyment | Dismissal, shame, pressure |
| **X9** | Shareable Moments drive consented sharing | Moment share vs none | Approved shares; invites | Privacy comfort |
| **X10** | Graceful resume improves reactivation | "Welcome back" vs progress-loss framing | Meaningful return | Guilt |
| **X11** | Default depth by preset fits numbers-fluent users | Quick vs Guided default for Compete | Satisfaction; Advanced adoption | Overload |
| **X12** | Feedback timing control improves comprehension | Self-chosen timing vs immediate | Retention; perceived interruption | Delayed-use drop |

Methods: pre-specified primary outcome and minimum worthwhile effect; cluster-aware assignment where clubs/coaches are involved; long enough to separate novelty from sustained value; **stop any experiment that raises engagement but worsens understanding, pressure or privacy concern** (Blueprint §14.4). Do not redefine success after a failed primary outcome.

---

## 8. KPIs, guardrails, kill criteria

| Dimension | Primary measure | Guardrail / kill criterion |
|---|---|---|
| **Value** | % of sessions where the player views a Moment or understands an insight (**north star**) | — |
| **Activation** | First useful session: can state one finding or saves a Moment | Setup events (signup, tour) never count |
| **Trust** | Event accuracy by condition; identity-error rate; correction rate; false-record rate | **Any false personal best/record shipped → pause the Records surface** |
| **Comprehension** | Teach-back accuracy | < threshold → redesign the surface |
| **Enjoyment/comfort** | Recap rated useful/enjoyable; embarrassment/pressure item | Pressure/shame above threshold → pull the mechanic |
| **Return** | Voluntary 7- and 28-day return; sessions per active player; successful non-use | Notification opt-out spike → reduce triggers |
| **Social** | Approved shares viewed; pair opt-in | Any unconsented exposure → pause sharing |
| **Accessibility** | Task completion across access needs | Any blocker on Recap/Consent → release stop |
| **System** | Coverage, latency, cost/session, failure rate | Recap p95 above budget → fix before features |
| **Harm** | Reported shame, pressure, unwanted comparison, unsafe interpretation | Pre-agree thresholds; rollback plan per feature |

Never optimise daily active use, time-in-app or badges issued as standalone goals.

---

## 9. Instrumentation

Event taxonomy: Blueprint §14.3, extended by file 03 (onboarding) — `example_opened · purpose_selected · purpose_skipped · suitability_checked · upload_started · upload_interrupted · upload_resumed · analysis_started · analysis_partial · analysis_completed · first_insight_viewed · coverage_opened · evidence_clip_opened · evidence_played · insight_response · label_corrected · finding_rejected · clip_saved · focus_selected · comparison_opened · report_comprehension · share_previewed · share_initiated · access_granted · access_revoked · privacy_changed · reminder_enabled · reminder_paused · resume_after_lapse · data_exported · deletion_requested · harm_signal`.

Required context on every event: report/definition/model version, match type, coverage band, device/network class, experiment assignment. **Minimise personal data**; share events record audience *type*, never recipient identity; never log raw sensitive content. Distinguish exploratory from confirmatory analysis.

---

## 10. Release gates (Blueprint §14.3, v2 §14.3)

1. **Private internal evaluation** — no public claims; fixtures + real engine on the validation set.
2. **Closed player pilot** — consented adult sessions, visible uncertainty, manual review where needed, harm monitoring.
3. **Limited release** — only capabilities validated on amateur footage (G-11); rollback plan.
4. **Broader release** — evidence of reliable detection **and** positive user value.
5. **Advanced metrics / coach** — separate validation and expert review before exposure.

A feature is **downgraded or disabled** when false-claim, identity-error, privacy or harm reports exceed thresholds defined *before* the experiment.

---

## 11. Definition of done (screen, component, insight)

**Screen:** purpose and primary action clear · matches IA · populated/empty/loading/error/partial/low-coverage/permission/offline/demo states · works 360→1440 and light/dark · all controls work · data from typed fixtures or API · metric definitions and check states reachable · privacy respected · keyboard + screen-reader basics tested · at least one E2E covers its journey · nothing fabricated presented as real.

**Component:** all states in file 07 · keyboard/ARIA · tokens only (no raw hex) · reduced-motion respected · copy from the constants module · unit + a11y test.

**Insight (Blueprint v2 §16):** purpose-relevant · event/identity reliable enough · versioned metric · numerator/denominator/exclusions known · evidence one tap away · coverage and uncertainty shown · observation before interpretation · no unsupported causality · recommendation optional and feasible · permissions allow display · can be corrected/dismissed/hidden · corrections propagate · failure and insufficient-evidence states designed · has a user-value hypothesis and harm test.

---

## 12. Risks and mitigations

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Engine is validated on broadcast, not amateur phone footage | **High** | Wrong rallies/winners erode trust | G-11 validation set; Preview labels; Review & fix; capture guide with test clip |
| Winner attribution wrong without scoreboard | **High** | Scoreline arguments | Withhold scoreline until its complete dependency set is Checked; do not rely on Preview to excuse a wrong score; free-play mode (G-04) |
| Shot types mislabelled | High | Cringe/distrust | Preview; per-shot Fix this; never in a headline |
| Consent/analyse gate absent (upload auto-starts) | Certain today | Compliance/trust | G-12 draft state; client gate as stopgap |
| Doubles absent but most amateur play is doubles | **High** | Product misses the central use case | Make G-03 an explicit P1 decision (Q5 in file 00); ship singles/social-game value first |
| Over-building engagement | Medium | Pressure, harm | D7; mechanic harm tests; no streaks |
| Scope creep from three large spec docs | High | Never ships | Prototype scope cut (§3); vertical slices |
| Light/dark double theme doubles QA cost | Medium | Delay | One token set; visual regression on tokens; dark limited to theatre/Deep dive first |
| LLM narration drifts from evidence | Medium | False claims | Narration contract (file 06 §8); validator; fixtures run through it in CI |

---

## 13. Next actions (first two weeks)

1. Product owner answers file 00 Q1–Q7 (stack, market, doubles priority, free play).
2. Start **Phase 0**; in parallel start **footage collection** (G-11) and **context interviews** (§7.2.1) — these de-risk everything else.
3. Engine team scopes **G-04 (free play)**, **G-07 (metric registry)**, **G-09 (geometry gates)**, **G-12 (draft + stages + resumable upload)**.
4. Design produces comps for the six mood descriptions in file 08 and the Recap hero; test with the 5-second test before building Phase 1.
