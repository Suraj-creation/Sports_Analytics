# 01 — First Principles and Behaviour Model: The Amateur Badminton Player

**Purpose.** Everything visible in the product — a button label, an empty state, the order of a screen, whether a chart exists — is a decision about how a real person *feels and behaves* a few minutes after a game. This file states, from first principles, who that person is, what they want, what they fear, and the design rules that follow. Later files cite these rules as **R#**.

**Evidence discipline.** Findings from sport psychology, motor learning, HCI and gamification are used as *constraints and hypotheses*, never as proof that a specific badminton feature works. Every "we believe" below is labelled **[H]** (hypothesis to validate with real players — see file 12) or **[E]** (supported by converging evidence in the three Design docs). No study validates this exact product (Blueprint §0.2).

---

## 1. The one-paragraph model

An amateur does not "use a sports analytics platform". They **play badminton with friends or at a club, once to three times a week, in a time-boxed court slot, then go home tired.** Playing is the point. The product is a *guest* in that life: it earns a place only if (a) it asks almost nothing of them on court, (b) it gives them something **delightful and personal within seconds** when they glance at their phone later, (c) it **never makes them feel judged** — by the machine, by friends, or by their own past self — and (d) it quietly offers more depth to the minority who want it. The analytics must be professional-grade *underneath* precisely so that the surface can be **short, kind and trusted**.

> **Design thesis.** *Sport first, app second. Moment before metric. Mirror, not judge. Depth by invitation.*

---

## 2. Who they are (and are not)

### 2.1 The six archetypes (working hypotheses, [H])

Archetypes are **session-level jobs**, not identity labels. The same person is "Weekend social" on Saturday and "Improver" on Tuesday (Blueprint §3.1: *store purposes as editable defaults, never labels*). Names are fictional; none of these people is a data subject.

| Archetype | A typical week | Why they open the app | What they want to see first | What would make them leave |
|---|---|---|---|---|
| **Weekend Social** (doubles with friends, society or office court) | One 45-min slot, 4 players, lots of banter | "Send the best rally to the group chat" | A trimmed reel; one big number ("a 17-shot rally!") | Homework, scores that start arguments, setup chores |
| **Restarter / Beginner** (returning after years, or new) | Plays rarely, is quietly self-conscious | "Can I still do this?" | One thing they did *well*, in plain words | Jargon, a "weakness" list, being compared to others or to their former self |
| **Improver** (academy/YouTube-coached, wants to get better) | 2–3 sessions, watches coaching videos | "What should I fix?" | A strength, one thing to try, the clips that show it | Generic advice, ten metrics, advice the clip doesn't support |
| **Social Competitor** (friendly rivalries, bragging rights) | Keeps score informally; rematches | "Settle the argument. Who really won that rally?" | The scoreline, key rallies, fair evidence | Public rankings that expose friends, wrong calls with no appeal |
| **Club / League** (tactical, wants rigour) | Matches, opponents repeat | "Find patterns; prepare" | Filters, sequences, exports, coverage and limits | A black box, a simplified grade that hides coverage |
| **Older / Returning-to-activity player** (health and social motivation) | Regular, sociable, sensible about rest | "Remind me this is good for me and fun" | Large, clear, calm; participation recognised | Small text, speed pressure, any fitness scoring, medical claims |

**Design consequence.** The **default experience serves the first two rows** (Relax preset, Quick depth). Rows three to five are reached by *choosing*, not by being classified. The sixth row is served by **accessibility and tone**, not a separate mode — age is not a proxy for ability or motivation (Blueprint §3.1; v2 §5.6).

### 2.2 The motivation portfolio [E: SDT; H: weights]

People play for different mixes of **enjoyment, social connection, health, mastery, achievement/recognition, stress relief, routine**. Enjoyment without measurable improvement is a **legitimate, successful outcome** (Blueprint §3.3). Three needs predict sustained participation — and every screen must serve at least one without harming another:

| Need | In badminton terms | The product serves it by | The product harms it by |
|---|---|---|---|
| **Autonomy** | "I choose what I look at and whether I look" | Purpose chips, Depth switch, skippable questions, *Just play* mode, per-clip sharing | Forced goals, bundled consent, "you should practise…" |
| **Competence** | "I can see I did something well / am getting somewhere" | A verified positive moment every match, honest personal bests, attainable *Focus* | Praise without evidence, impossible targets, single-match "improvement" claims |
| **Relatedness** | "This is shared with my people, and nobody's embarrassed" | Pair memory, consented sharing, friendly language about partners | Rankings, blame in doubles, exposing a friend's mistake |

Six outcomes the product is *for* (from the amateur brief): **enjoyment · personal progress · social connection · physical activity (qualified) · confidence and comfort · sustainable participation.** Section 8 maps each to surfaces and measures.

---

## 3. The context of use (design for the real situation)

### 3.1 Where the person actually is

| Moment | State of the person | Implication |
|---|---|---|
| **Before play** | Packing a bag; late; phone has 40% battery | Recording must be *one decision*: "phone on a bench/tripod, behind the baseline." No app interaction needed on court. |
| **During play** | Breathless, sweaty hands, looking at the shuttle | **Zero** on-court interface. No live prompts (Blueprint §3.4: default no interruptions). |
| **Right after play** | Tired, hungry, chatting, packing up | A 20-second **glance** is the most they will give. Anything that needs reading fails. |
| **That evening / next morning** | Relaxed on a sofa or in the car; **curiosity peak** | This is the **main use moment**: a 2–3-minute recap on a phone, one thumb. |
| **Weekend deep-dive** (minority) | Laptop, coffee, curiosity or a plan | Desktop *Deep dive*: video beside data, filters, exports. |
| **Before the next game** | Remembering one thing | A saved *Focus* surfaces once, if the player chose one. |

### 3.2 The three attention budgets (the recap's structure)

| Budget | Where | What they must get | Screen |
|---|---|---|---|
| **20 seconds** (glance) | Notification-free; opened from Home | One delightful Moment + one verified positive line | Recap top: `HeroMoment` + `FactTrio` |
| **3 minutes** (couch) | Phone, one hand | A personal read: what stood out, a personal best, who did what | Recap: *Moments → My game → Together* |
| **20 minutes** (curious) | Desktop or tablet | Rally-by-rally exploration with evidence | *Deep dive* |

**Rule R1.** *Every screen must pay off inside its budget.* If the 20-second glance contains a table, the design has failed.

### 3.3 Physical and technical reality [H, validate on court]

- **One-handed, thumb-reach, glare outdoors, sweaty fingers** → 44 px minimum targets, primary actions in the thumb zone, high-contrast daylight theme, no precision gestures (drag handles only as fallback).
- **Spotty or costly data** → uploads must resume, run in the background on Wi-Fi if the user chooses, and never restart from zero. A preview-quality option (lower bandwidth) is labelled as *preview quality*, not lower analysis quality.
- **Bench-propped, side-on, behind-the-baseline or high-corner phone footage**, no scoreboard, variable light, maybe a net-curtain of passers-by → this is a *different distribution* from the broadcast footage the engine was validated on (docs/testing). The capture guide is therefore **part of the product**, not an appendix (Blueprint §7.4).

---

## 4. The emotional journey (and what the interface must do at each beat)

The Blueprint's emotional-moment table (§3.4) is the backbone; below it is extended with the amateur-specific beats and the **peak-end** design.

| # | Beat | Likely feeling [H] | Risk | Interface response (rule) |
|---|---|---|---|---|
| 1 | **Hears about it** (friend shares a clip) | Curiosity, mild scepticism ("is this a gimmick?") | Vague "AI coach" promise | Show a *real* shared Moment with the "make yours" link; landing starts with an example, not a pitch (R6) |
| 2 | **Landing / evaluating** | "Is this worth the effort? Is it safe?" | Hidden cost/limits | Sample recap first; requirements and privacy in plain words *before* any upload (R7) |
| 3 | **Sets up the phone** | Effort aversion; fear of "doing it wrong" | Unusable footage discovered later | Record guide + 10-second **test clip** check *before* the match is filmed (R8) |
| 4 | **Uploads** | Impatience; "is my video safe?" | Interrupted upload, duplicate, loss | Resumable, background, honest status; separate *upload* from *analysis* (R9) |
| 5 | **Waits for analysis** | Anxiety/boredom | Fake progress, dead time | **Play the video immediately** while rallies fill in (existing progressive playback); named stages, no fake %; leave-safely message (R9) |
| 6 | **First reveal** | Curiosity + *cringe* at seeing oneself | Metric wall; shame | One Moment, one verified positive, no grades (R2, R3) |
| 7 | **Sees a flattering moment** | Delight, pride | Over-claiming ("elite!") | Specific, evidence-bound praise; restrained, skippable celebration only for a *verified personal best* (R4) |
| 8 | **Sees something off** (wrong winner, wrong person) | Distrust — *the most dangerous beat* | One visible error kills the product | "Fix this" in one tap; changes explained; undo (R10, R11) |
| 9 | **Sees a weakness** | Defensiveness, shame | Trait language ("you lack…") | Observation language, clip first, optional action, alternatives listed (R12) |
| 10 | **After a loss** | Disappointment, avoidance | Deficit-only report; forced cheer | Same layout and care as after a win; entry choice *Quick recap / Deep review / Review later* (R5) |
| 11 | **Wants to share** | Social reward *and* social risk | Embarrassing a friend/opponent | Share preview with exact audience; per-clip approval for funny ones; private by default (R13) |
| 12 | **Plateau** | Doubt | "Am I wasting time?" | "Not enough comparable matches to say" is a normal state; variability shown; goal revisit offered (R14) |
| 13 | **Break (injury, travel, busy)** | Guilt, vulnerability | Streak-loss language | "Welcome back. Start fresh with one match?" Nothing is lost (R15) |
| 14 | **Return** | Fresh-start motivation | Punitive comparison with former self | New baseline offered; no regression alarm (R15) |
| 15 | **Wants out** | Neutral to annoyed | Guilt screens, hard cancel | Export, delete, pause in two clear steps (R16) |

**Peak–end design [E: peak-end effect widely replicated; H: magnitude here].** People remember the *peak* and the *end* of an experience. The recap must **peak on a Moment** (the video, the person) and **end on a next step the player chose or on quiet** — not on a table, a nag, or a data-quality warning. Warnings live in a compact **Quality** drawer, one tap away.

---

## 5. What amateurs likely want to see, in order of pull [H]

This ordering is the **default information hierarchy** of the recap. It must be tested (file 12, X1/X4) because stats-literate markets (e.g., a cricket-stats culture, [H]) may *like* more numbers than assumed — which is why Advanced is a proud, visible, one-tap option, never hidden.

| Rank | Want | Product answer | Depth |
|---|---|---|---|
| 1 | **See myself at my best, trimmed** | Auto-reel of 3–5 Moments from rallies; best-moment hero | Quick |
| 2 | **Something to send to friends** | Shareable Moment / Match Story card with the player's consent | Quick |
| 3 | **A few fun, honest numbers** | `FactTrio`: longest rally, rallies played, one personal best — each with "Watch this" | Quick |
| 4 | **"Am I getting better?" — answered simply and honestly** | *Personal best*, *First*, comparable-match trend with n | Guided |
| 5 | **Where I stood / where my shots went** | Court presence (relative), Preview-tagged placement | Guided |
| 6 | **One thing worth trying** | Optional Focus with evidence clips | Guided |
| 7 | **Tactics and patterns** | Shot sequences, rally explorer, filters, exports | Advanced |

---

## 6. The behavioural rules (R1–R20)

Each rule: **Insight → Rule → Where it applies → Anti-pattern → How to test.** Mechanism evidence sources are in Design/Front-End Blueprint §19.

| R# | Insight | Rule | Applies to | Anti-pattern | Test |
|---|---|---|---|---|---|
| **R1** | Attention is the scarcest resource after play | Every screen pays off within its attention budget (20 s / 3 min / 20 min) | Recap, Home, Moments | A table above the first Moment | Time-to-first-meaningful-thing; 5-second test |
| **R2** | Cognitive load caps comprehension (progressive disclosure helps) | One hero, ≤3 facts, rest on demand: **Summary → Evidence → Workspace** | Recap, Deep dive | Metric wall; every available stat | Teach-back: "what was the main point?" ≥80% |
| **R3** | Self-image is fragile on video; unrequested evaluation backfires | Mirror, don't judge: no grades, no universal score, no ranking vs others by default | Everywhere | "Your footwork is poor", "badminton IQ" | Pressure/embarrassment survey item |
| **R4** | Confidence must come from credible mastery, not inflated praise [E: self-efficacy] | Praise is specific, verified, evidence-bound; celebration only for a verified personal best, once, skippable | Recap, Progress, Records | Confetti on a win; "You're becoming elite!" | False-praise rate; seeded-error test |
| **R5** | Loss is not failure; attribution to ability harms later effort [E] | Same layout, same care after a loss; offer *Quick recap / Deep review / Review later*; scoreline is context (D6) | Recap, Home | Deficit-only reports; forced cheer | Compare engagement and affect after wins vs losses |
| **R6** | People trust friends' clips more than ads | **Show, don't tell**: landing leads with a real example; shared Moments carry a consent-respecting "make yours" link | Landing, Share | "AI coach" slogans | Landing → sample-open rate; expectation-match survey |
| **R7** | Hidden cost and privacy risk kill trials | State effort, cost, privacy and limits *before* any upload | Landing, New match | Surprises after upload | Informed-trial-decision task |
| **R8** | Capture is the habit loop's weakest link | Capture readiness is a product feature: record guide, framing checklist, **test clip** check | Onboarding, New match | "Try again" with no reason | Usable-recording rate |
| **R9** | Waiting under uncertainty feels longer; fake progress erodes trust | Play video *while* analysing; named stages; honest ETA only if real; separate upload from analysis | Processing | Fabricated percentage | Perceived-wait survey; drop-off during processing |
| **R10** | One visible error destroys trust faster than ten correct claims build it [H] | **Show → Prove → Correct**: every claim opens its evidence; "Fix this" in one tap; corrections propagate visibly | InsightCard, Review & fix | Silent repair; defending the AI | Seeded-error detection rate ≥ target |
| **R11** | Amateurs tend to trust device numbers *more* than elite athletes do [E, qualitative] | Beginner UI simplifies **explanation**, never hides **uncertainty**; expert UI exposes detail and invites disagreement | CheckChip, Coverage | Confident number with no coverage | Trust calibration: accept right, question wrong |
| **R12** | Feedback that turns attention to the self reduces performance in >⅓ of interventions [E] | Describe the **performance episode**, never the person; clip first; optional action | Insights, Copy | "You lack composure", "weakness" | Copy lint; user read-aloud test |
| **R13** | Sharing is social reward *and* social risk | Private by default; exact-audience preview; per-clip approval for funny; teammates/opponents never exposed by inference | Share, Moments | Public link default; auto-posted clips | Privacy-task success without reading policy |
| **R14** | Plateaus are normal; single-match change is mostly noise [E] | "Not enough comparable matches" is a *designed* state; show ranges and n; offer goal revisit | Progress | Smooth fake trend; "improvement" from one match | Interpretation accuracy ("name one limit") |
| **R15** | Fresh starts motivate; guilt demotivates [E: habit formation tolerates missed opportunities] | Welcome back, never "streak lost"; offer a new baseline; nothing is lost | Home, Progress, Notifications | Streak, "you're falling behind" | Reactivation vs guilt measures |
| **R16** | Control over exit builds trust to enter | Pause, export, delete, cancel in two clear steps; no guilt screens | Settings | Hidden cancellation | Time-to-delete task |
| **R17** | Autonomy supports sustained motivation [E: SDT] | Everything personal is chosen, editable, skippable: purpose, depth, tone, focus, challenges, notifications | Onboarding, Settings | Controlling defaults | Perceived autonomy scale |
| **R18** | People compare upward and downward unpredictably | Default comparison is **your own comparable history**; peer comparison is opt-in, bounded, explained | Progress, Explore, Together | Global leaderboard | "Reference picker" adoption and harm reports |
| **R19** | In doubles the relationship outweighs the analytics | Pair-first language ("both of you"); never blame a partner from aggregate outcomes; pair data needs both partners' consent | Together, Recap | "Your partner caused the loss" | Partner-comfort survey |
| **R20** | Rewards can inform *or* control; gamification effects are small and fade [E] | Only rewards tied to a verified, definable sporting event; no XP, levels, streaks, loot; every mechanic needs a value theory + harm test + opt-out | Records, Explore | Badge economies | Mechanic-level harm metric; kill criteria |

---

## 7. The trust model for people who trust numbers too easily

The people least able to challenge a statistic are the people most likely to believe it [E, qualitative]. The product therefore teaches trust calibration through **interaction design**, not disclaimers.

### 7.1 The trust ladder (Show → Prove → Correct)

```
SHOW      "You kept this rally alive for 14 shots."                  ← a claim in plain words
PROVE     [ ▶ Watch this ]  ·  how it's counted  ·  what we could see ← one tap each, always present
CORRECT   [ Fix this ]  → "Was it 14 shots?"  → updated, with undo   ← never defended, never hidden
```

### 7.2 Four layers, visibly separate (Blueprint §9.1)

| Layer | Example | Typical wording |
|---|---|---|
| **Measurement** | The rally lasted 11.4 s | "This rally lasted 11 seconds." |
| **Model classification** | A shot was labelled *cross-court net shot* | "We think this was a cross-court net shot." (**Preview**) |
| **Interpretation** | The sequence may have left few options | "This may be worth a look." |
| **Recommendation** | A suggested experiment | "If it fits your goal, you could try…" |

A lost rally after a shot does not show the shot caused the loss. Use *associated with / appeared alongside*. (File 09 owns the full copy rules.)

### 7.3 The error budget by beat

| If wrong… | Severity | Mitigation |
|---|---|---|
| A **Moment** that isn't really good | Low | "Why this was picked" + swap; no claim of "best" without a definition |
| **Which person is you** | **High** | Mandatory *Pick yourself* with visible confirmation; easy re-map |
| **Rally winner / scoreline** | **High** (arguments start here) | Scoreline shows **Preview** until Checked; Review & fix first; "from the scoreboard" label when OCR-derived |
| **Shot type** | Medium | **Preview**; per-shot *Fix this*; never in a headline |
| **Distance, speed, calories** | High | **Not yet**; calories/fitness never from video |
| **A personal best that isn't** | High (public pride) | Needs verified events and a stable definition; delay recognition until Checked |

---

## 8. The six outcomes → surfaces → measures

| Outcome | Surfaces that serve it | Primary measure (never badges issued) | Guardrail |
|---|---|---|---|
| **Enjoyment** | HeroMoment, MomentStrip, Match Story card, shared reels | Recap rated useful/enjoyable; clips saved or shared (approved) | Shame/pressure reports |
| **Personal progress** | Personal bests, Firsts, comparable-match trends, Focus | Players who can name one meaningful, correct change | Over-interpretation of noise |
| **Social connection** | Together, Pair memory, shared Moments, Invite | Approved shares viewed; partner opt-in rate | Unwanted exposure; blame |
| **Physical activity (qualified)** | *Active play* time, relative coverage (Preview) | Understood, optional; never a target | No calories/fitness claims; no playing-through-pain |
| **Confidence & comfort** | Verified positive moment per player; neutral language; private default | Self-reported comfort; low embarrassment | False praise; identity errors |
| **Sustainable participation** | Calm return flows; no streaks; user-set reminders only | Voluntary return at 7/28 days; successful non-use counted as value | Notification fatigue; guilt |

---

## 9. Acquisition and attraction (why a player tries it and tells a friend)

Growth must come from **value shown**, not pressure applied. Hypotheses to test [H]:

1. **The shareable Moment is the growth engine.** A 10-second rally, captioned plainly, with a small "made with Rally — make yours" link. Consent-aware: the sharer controls audience; people in the clip are never named without their say. (Doc 10 owns the sharing rules.)
2. **Sample-first landing.** A real 20-second recap people can play with *before* any sign-up — "proof of value" instead of a promise.
3. **Fastest-possible first win.** Target: **upload → first Moment in a few minutes of wall-clock, under ~90 seconds of active effort.** (Targets are proposals; measure them. File 12.)
4. **Partner pull.** Pair memory *needs* a partner; the invite is a natural, consented referral — not an incentive scheme.
5. **Zero-friction trial.** Guest-first: the player's work is saved under a lightweight account only when needed to protect it.
6. **No dark patterns.** No countdown timers, scarcity, guilt, "friends are ahead of you", or pre-checked sharing — ever (R20).

---

## 10. Cultural and contextual hypotheses to validate (do not assume)

| Hypothesis [H] | Why it matters | How to validate |
|---|---|---|
| Group chats (e.g., WhatsApp) are the primary sharing channel | Share format, link previews, file size | Interviews + share-flow prototype |
| Many sessions are **unscored social games**, doubles-heavy, on rented/apartment/academy courts | Free-play match type (G-04); doubles priority | Observe 10 real sessions |
| Phone is **propped on a bench/bag or held by a friend**, often side-on or behind one end | Capture guide and engine validity | Capture-in-the-wild study |
| Numbers-fluent audiences (sports with rich stats) may want **more** depth earlier | Depth defaults; visibility of Advanced | A/B depth defaults by preset |
| Data cost and storage anxiety are real | Resumable uploads; "keep video?" consent; preview quality | Upload telemetry; interviews |
| Regional-language and code-mixed copy improve comfort | Localisation scope | Copy tests in target languages |
| Parents/coaches may want to film minors | Adult-only pilot (D15) | Policy review before any youth feature |

---

## 11. Psychological anti-patterns (never build)

| Anti-pattern | Why it harms | Alternative |
|---|---|---|
| Streaks, daily goals, "don't break your chain" | Guilt; mismatched with weekly play [E] | Weekly, opt-in, forgiving only if ever tested |
| Leaderboards by default | Upward comparison discourages; downward breeds complacency | Self-baseline; opt-in bounded peers later |
| One "player score" / rating | Collapses incommensurate things; ranks incomparable people | Separate, defined metrics |
| Confetti on every win | Ties worth to the result; teaches that losing is failure | Restrained celebration for verified personal bests only |
| "AI says your weakness is…" | Authority without evidence; trait language | InsightCard with evidence, alternatives, optional action |
| Loss-aversion nudges ("you'll lose progress") | Manipulation; punishes breaks | Nothing is lost; welcome-back copy |
| Hidden sharing defaults | Unwanted exposure; betrays trust | Private by default; audience preview |
| Emotion inference from posture/face | Unreliable; invasive | Ask, never infer (v2 §3.5) |
| Blaming a doubles partner | Damages the relationship the sport depends on | Sequences and "both of you" |
| Medical/fitness claims from video | Unsafe, unvalidated | Self-reported energy only; general warm-up education |

---

## 12. How this file feeds the others

| This file → | Decision it drives |
|---|---|
| Archetypes (§2) | Presets and default depth (file 00 D2–D3), Home hierarchy (file 05a) |
| Attention budgets (§3.2) | Recap structure (file 05a) and Moments-first layout |
| Emotional journey (§4) | Onboarding steps and every state's copy (files 03, 09) |
| Want ranking (§5) | Information hierarchy; first experiment X1 (file 12) |
| Rules R1–R20 (§6) | Component rules (file 07), screen acceptance criteria (files 05a–c) |
| Trust model (§7) | CheckChip, Review & fix, Preview tags (files 06, 07, 05b) |
| Outcomes (§8) | KPIs and guardrails (file 12) |
| Hypotheses (§10) | Research plan and open questions (files 00, 12) |
