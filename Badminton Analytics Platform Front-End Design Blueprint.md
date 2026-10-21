# Badminton Analytics Platform: Front-End Design Blueprint

*Consolidated from six research documents (behavioral science, motor learning, product patterns, trust/UX, and the technical pipeline report) into one build guide for the website, prototype and every user-facing component.*

---

## 0. How to Use This Document

**Purpose.** The research was never an end in itself. It exists so that every page, control, chart, sentence and state in the product is a deliberate decision about how players think, feel, learn and decide. This blueprint turns that research into: UX principles, user journeys, page structures, interaction patterns, component specifications and visual-system rules that frontend work can start from.

**How to read it.** Each section ends with *Design decisions* (what to build). Where the research is only a hypothesis, it is marked so the team knows what to test rather than assume.

### 0.1 Source map: what each research file contributed

| # | Source file | Main contribution to the front end |
| --- | --- | --- |
| 1 | Behavioral Research and Product Design Foundation (largest) | Onboarding sequence, IA, home-screen state matrix, match-review spec, interaction/data states, design-system implications, 12 product case studies, anti-pattern register, experiment backlog, roadmap |
| 2 | Badminton Analytics Behavioral Research | Three-layer match report, InsightCard schema, confidence presentation, onboarding table, personalization layers, permissions, empty/failure states |
| 3 | Designing Badminton Analytics Around Players, Not App Usage | Motivation portfolio, player-question map, emotional-journey table, capability gating, insight component, visualization-by-decision, voluntary return and successful non-use, accessibility and privacy at launch |
| 4 | Designing Badminton Analytics That Build Motivation and Skill | Mechanism-by-mechanism guidance (SDT, goals, efficacy, attribution, emotion, flow, deliberate practice, motor feedback, self-regulation, comparison, identity, habit, rewards, cognitive load, trust) with explicit transfer cautions |
| 5 | Badminton Analytics Behavioral Research (short synthesis) | Compact framework summary, SwingVision/Strava/Hudl/WHOOP comparison, phased roadmap |
| 6 | Deep Research Report (technical) | What the models can and cannot reliably produce, event ledger and lifecycle states, match-phase engine, deployment modes and graceful degradation. These decide what the UI is allowed to claim |

### 0.2 Evidence labels used here

- **Strong**: converging reviews or meta-analyses. **Moderate**: credible but heterogeneous or indirect. **Limited**: narrow, product-authored or indirect. **Hypothesis**: plausible, needs testing with badminton players.
- Important honesty note carried over from every source: **no study validates this exact platform.** Most psychological evidence comes from general sport, exercise, education or HCI. So the UI must make the ideas *testable* and *reversible*, and never over-claim.

### 0.3 Where the sources disagree, and the decision taken

| Topic | Disagreement | Decision for the front end |
| --- | --- | --- |
| Feedback frequency | One file favors bandwidth/self-controlled feedback; another cites a meta-analysis (61 papers) finding no significant benefit of reduced frequency, and self-controlled benefits shrink after bias correction | Let players choose when and how deeply to see feedback. Do not hard-code fading or a universal schedule. A/B test timing against delayed, unassisted performance |
| Streaks | One file allows weekly streaks with freezes; others reject streaks as guilt-inducing and mismatched with weekly play | **No streaks at launch.** If ever tested: opt-in, weekly or event-based, forgiving, never punishing missed play |
| Confidence display | Levels (High/Medium/Low) vs. rejecting numeric confidence unless calibrated | Plain-language reasons always. Labelled levels only once calibrated on target footage. No raw softmax percentages |
| Leaderboards | Segmented leaderboards outperform global ones vs. comparison can discourage | Private self-baseline by default. Opt-in, bounded peer groups only, later phase |
| Growth-mindset copy | Light framing vs. heavy reliance | Strategy-specific, conditional language only; never a headline mechanic |
| External attentional focus | Often favored in badminton studies, but bias-adjusted reanalysis near zero | Offer external-focus cues as a default *option*; coach can override; test by skill |
| Gamification | Moderate effects (e.g., g≈.42 bundled) vs. worse motivation in some bundled studies | Narrow, optional, evidence-backed milestones only |

---

## 1. Product Foundation

### 1.1 The product in one paragraph

A **player-controlled performance companion**: it turns badminton video into understandable, inspectable evidence; helps the player decide what is worth noticing, what to believe, and what (if anything) to do next; and preserves enjoyment and memory. It is not a statistics dashboard with engagement mechanics attached, not a replacement for a coach, and not a score that defines a player’s worth.

### 1.2 The core loop (drives every screen)

**Chosen purpose → trustworthy evidence → understandable meaning → optional next action → later reflection.**

The home and report must answer four questions in order: **What happened? Why might it matter? What should I inspect? What can I try next?** And three trust questions: **What is worth noticing? Why should I believe it? What could I do with it?**

### 1.3 North star and activation

- **North star:** a player obtains and understands one credible, personally relevant insight (or saves a meaningful moment) and can choose to act on it. It is *not* daily opens, time in app or uploads.
- **Activation (proposed):** the player completes a real match loop and can correctly state one finding or saves a clip that matters to them. Account creation, tour completion and dashboard views are setup events.
- **Adoption equation (product model, not psychometric):** perceived value = credible insight × relevance × actionability − capture effort − interpretation effort − emotional cost − privacy risk.

### 1.4 Product roles the UI should support (priority order)

1. **Trustworthy mirror**: shows what happened, with evidence and honest limits.
2. **Contextual learning companion**: connects pattern → meaning → feasible experiment.
3. **User-controlled record of play**: highlights, memories, notes, saved focus; useful even with no analysis.
4. Later: **development tool** (comparable-session progress) and **performance assistant** (tactical co-analysis with coaches). Never an autonomous AI coach claiming to explain every “why”.

### 1.5 Non-goals (build nothing that implies these)

Injury diagnosis or medical advice; inferring mental state, anxiety or personality from footage; a universal “badminton IQ”/ability score; guaranteed improvement; certified line calling; shuttle speed claims from arbitrary footage; public opponent dossiers; automated biomechanical correction from unvalidated pose estimates; real-time tactical instruction during competition.

### 1.6 Five outcome layers (never merge into one score)

| Layer | Example | What it does *not* prove |
| --- | --- | --- |
| Technical success | Footage processed correctly | The player understood anything |
| Product value | Player finds a useful pattern or meaningful clip | The player improved |
| Learning process | Player selects and revisits a focus | The focus caused improvement |
| Sporting outcome | Reliable measures improve in comparable conditions | Analytics caused the change |
| Well-being and participation | Enjoyment, voluntary involvement | More screen time is good |

**UI consequence:** keep these visibly separate (reviewed / practiced / demonstrated in later play). Never show a single “improvement score”.

---

## 2. Design Principles (the rules every screen is reviewed against)

| # | Principle | What it means in the UI | Rejected pattern |
| --- | --- | --- | --- |
| 1 | **Sport first, app second** | Optimize the player’s time on court. Shorter review that produces a better decision counts as success; no engagement quotas | Daily-open targets, time-in-app goals |
| 2 | **Value before configuration** | Show a realistic sample before asking for preferences; first result before any long profile | Long questionnaire before relevance |
| 3 | **Evidence before authority** | Every claim opens clips, definition, denominator and coverage | “AI says your biggest weakness is…” |
| 4 | **One useful priority beats ten metrics** | Rank and suppress. One headline finding; the rest is on-demand | Metric wall |
| 5 | **Choice with structure** | Suggested focus plus edit / swap / dismiss, with a reason shown | Forced goals, blank configuration, controlling defaults |
| 6 | **Self-reference before social comparison** | Default to personal, context-matched baselines | Global ranking by default |
| 7 | **Confidence must be earned** | Praise only verified, specific evidence; show sample size | “You’re becoming elite!” on one match |
| 8 | **Uncertainty is part of the interface** | Coverage, label reliability, sample size and abstention are visible design elements | False precision, silent guesses in empty panels |
| 9 | **Loss is not failure** | Result and learning value are separate dimensions; no celebration animation tied only to winning | Deficit-only review after defeats |
| 10 | **Intermittent use is legitimate** | Resume without penalty; pause, export, leave gracefully | Streak loss, “you’re falling behind” |
| 11 | **Depth available, never imposed** | Summary → Evidence → Workspace; experts reach event-level evidence in one clear action | Simplification that hides evidence experts need |
| 12 | **Humans stay accountable** | Coach and player can annotate, correct, dispute | AI as final authority |
| 13 | **Privacy is a feature** | Private by default; analyze ≠ share ≠ train | Hidden sharing defaults, bundled consent |
| 14 | **Every mechanic needs a user-value theory and a harm test** | Gamification/social/notifications are experiments tied to sporting value | Points and badge economies |
| 15 | **Correctability is infrastructure** | Any finding can be corrected; affected summaries visibly update and explain why | Silent repair of errors |

---

## 3. Users: Segments, Depth Modes and Emotional Moments

### 3.1 Working segments (hypotheses to validate, not market clusters)

Purpose, context, expertise, coaching access and desired effort are **separate attributes**. Users may move between rows by session. Store these as editable defaults, never identity labels.

| Segment | Primary job | Default depth | First value | What the first screen emphasizes | Main risk |
| --- | --- | --- | --- | --- | --- |
| Recreational / social | Enjoy and remember play | Quick | A saved meaningful rally | Clips and a short plain-language recap | Turning leisure into evaluation |
| New / restarting | Feel welcome, understand something achievable | Quick | One observation and one selected rally | Plain language, no grading | Embarrassment, jargon |
| Improvement-oriented amateur (likely beachhead) | Know what to practice | Guided | One strength, one priority, supporting clips | Evidence-linked finding, optional focus | Generic or overwhelming advice; overtrust |
| Competitive club / tournament | Diagnose patterns and prepare | Advanced | Filtered rally sequences and a testable tactical question | Filters, score-state, opponent context | Inaccurate tagging destroys trust |
| Advanced / professional | Add evidence beyond coaching | Advanced | Audit and correct a finding; export | Definitions, coverage, event table | Opaque aggregation; loss of control |
| Coach / training partner | Turn evidence into a short conversation | Collaborative | A shared, annotated playlist | Authorized athlete matches, annotations | Evidence becoming surveillance |
| Returning / adapting | Resume on appropriate terms | Quick–Guided | A fresh baseline | “Resume with one match”, no old-peak comparison | Punitive comparison with a former self |

**Important interpretation finding (source 3):** amateurs tend to trust device numbers *more* than elite athletes do, so the person least able to interpret a statistic is least likely to challenge it. **Beginner UI simplifies explanation but never hides uncertainty. Expert UI exposes detail and invites disagreement.**

### 3.2 Three depth modes (same truth, different density)

|  | Quick | Guided (default) | Advanced |
| --- | --- | --- | --- |
| Language | Short sentences, plain words | Short + inline definitions | Full terminology, definitions on demand |
| Report opens with | Match story + best moments | Story + one strength + one opportunity | Event table, filters, coverage |
| Charts | Annotated clips, minimal charts | Court map, timeline, one trend | Distributions, small multiples, raw event table |
| Recommendation | Optional, hidden unless asked | One editable focus | Hypotheses and alternatives listed |
| Evidence access | One tap on any claim | One tap | Direct from table row |

Rule: **personalization changes order, wording and density, never the factual standard.** A visible “Shown because you chose tactical review” with **Change / Reset / Show all** is mandatory.

### 3.3 Motivation portfolio → “purpose” choices in the UI

Players value different things; enjoyment without measurable improvement is a legitimate successful outcome. The purpose selector (multi-select, up to two, always skippable, editable per session):

- **Keep the moments** (enjoyment, memory, identity)
- **Understand my game** (curiosity, self-understanding)
- **Choose something to practice** (mastery, improvement)
- **Prepare to compete** (tactics, opponent context)
- **Discuss with someone** (coach, partner, club)

Evidence anchor: autonomous motivation (SDT) predicts participation; identified regulation is more relevant to adoption, intrinsic enjoyment to long-term adherence (66-study review). Process goals showed larger pooled effects than outcome goals (27 studies), with heterogeneity. Mastery climates show more adaptive correlates (104 studies), but competition is a legitimate option, not a default enemy.

### 3.4 Emotional moments → required UI behavior

These are possibilities to investigate, never labels auto-assigned to users, and mood must never be inferred from a loss.

| Moment | Risk | UI response |
| --- | --- | --- |
| First recording / watching oneself | Embarrassment | Private start; user-selected clips; controlled replay and sharing |
| After a loss | Disappointment, avoidance | Entry choice: **Quick recap / Deep review / Review later** (no guilt copy); neutral facts; no forced celebration |
| After a win | Uncritical confidence | Still show evidence; recognize specific moments, not outcome-triggered confetti |
| Seeing weaknesses | Defensiveness, shame | Observation language; clip first; an optional action; separate event from self-worth |
| Mistakes mid-session | Irritation | No blame during play; optional reset cue |
| Plateau | Doubt | Show noise vs delayed learning; revisit goal; “no improvement detected” is allowed with context |
| Return after a break | Vulnerability | “Resume with one match”; fresh baseline; no regression alarm |
| Comparing with others | Inspiration or inadequacy | Player picks the reference: self, similar peer, expert example |
| Coach criticism | Hurt or insight | Preserve evidence, allow response, never public |
| Personal best | Satisfaction | Show definition and context; do not auto-escalate next target |

Optional neutral prompt: *“What would help most now: understand the match, choose a practice idea, or keep the moments?”* Never mandatory emotional disclosure.

---

## 4. The Questions Players Actually Ask → Where They Live in the UI

Organize navigation and reports around **questions the player picks**. “Why” questions are invitations to investigate, never permission for the system to invent a cause.

| Player question | Home in the UI | Evidence required | Boundary in the copy |
| --- | --- | --- | --- |
| What actually happened? | Match story | Reliable rally/score segmentation | Neutral, bounded observations |
| What am I good at? | Verified strength card | Repeated examples with denominators | Name strengths with clips, even after a loss |
| What is holding me back? | Opportunity card | Recurring pattern + context | “Candidate bottleneck”, not a diagnosis |
| Why do I lose certain rallies? | Rally explorer / sequence view | Correct segmentation and preceding shots | Show sequences, not only the last shot |
| Am I improving? | Progress | Repeated comparable sessions, uncertainty | Do not equate one win with improvement |
| What should I practice next? | Practice (focus card) | Supported pattern + chosen goal + time/partner | Experiment the player can accept, edit or decline |
| Am I making better decisions under pressure? | Advanced analysis | Explicit pressure definition, comparable opportunities | Compare choices; never read internal state |
| How do I compare with my previous self? | Progress / comparison | Stable definitions, context | Include a new-baseline option |
| What can I realistically improve in a few weeks? | Goal setting | Baseline, constraints, practice exposure | Agree a controllable target; no predicted rate |
| What should I be proud of after losing? | Strength + meaningful moments | Genuine process evidence | Recognize evidence without pretending the result was good |
| Can I enjoy this and still improve? | Purpose selector, no-analysis sessions | Player-defined goals | Allow “just keep the moments” |
| Can my coach and I look at the same thing? | Coach/Team shared playlist | Permissioned sharing, annotation | Disagreement and correction are visible |

---

## 5. Information Architecture

### 5.1 Sitemap

**Public website (no login)**

- Landing → *Interactive 20-second example* → **Inspectable sample report** (with visible limits)
- “What we can and can’t analyze yet” (supported-conditions statement)
- Recording guide (court placement, framing, lighting, permission)
- Pricing (clear cost and equipment dependencies *before* upload)
- Privacy and data (plain language), Accessibility statement

**Signed-in product**

- **Home**: resume the most relevant task
- **Matches**: record/upload, processing status, match library, reports, clips, comparisons
- **Progress**: chosen focus, context-matched history, comparable sessions
- **Practice**: current focus, clips, plan, reflection
- **Library**: highlights, playlists, annotations, saved moments (start as a view inside Matches; promote only if cross-match retrieval proves frequent)
- **Coach / Team** (role-gated): authorized athletes, reviews, notes, permissions
- **Settings**: purpose and depth, accessibility, notifications, privacy, access, export/delete, billing, metric definitions, model corrections

**Persistent primary action:** *Analyze a match* (always one tap away).

**Advanced analysis lives inside a match**, not as a top-level warehouse of charts.

### 5.2 Home screen: content by situation

| Situation | Primary content | Secondary | Do not show by default |
| --- | --- | --- | --- |
| New, no footage | Realistic example or upload route | Recording and privacy explanation | Empty charts, arbitrary skill score |
| Processing | Honest status, recovery option | What will be available; optional notify | Fabricated percentage or fake countdown |
| Recreational return | Latest meaningful clip or match | Saved moments; analyze another | Deficit list, compulsory focus |
| Improvement return | Latest review + chosen focus | Relevant evidence, next opportunity | Every metric |
| Competitive / advanced | Resume investigation or match workspace | Saved filters, comparisons | A simplified grade hiding coverage |
| Coach | Reviews awaiting attention | Athlete-chosen priorities | Access to unrelated personal data |

**Home hierarchy (top to bottom):** (1) continue the sporting loop (“Review Saturday’s match” / “Prepare today’s practice”); (2) current focus (the one the *user* chose); (3) latest meaningful evidence; (4) progress signal only if enough comparable data exist; (5) Explore (advanced, optional achievements).

### 5.3 Device and context

| Context | Optimize for | Behavior |
| --- | --- | --- |
| Mobile at court | Speed, permission, capture suitability | Large labeled actions, short checklist, defer long review |
| Right after play | Fatigue, limited attention | Save/upload, glance at result, review later |
| Desktop review | Evidence comparison | Video beside data, keyboard-accessible filters |
| Coach session | Shared interpretation | Annotated playlist, visible disagreement/correction |
| Before practice | Recall one intention | One focus + relevant clip; no exploration required |
| During training | Minimal distraction | Optional concise cue; no continuous interaction unless validated |
| Before competition | Relevant preparation | Saved tactical questions, reliable context only |

**Platform decision:** responsive web first, mobile-priority for capture/resume and desktop-priority for comparison. Build a native app only when capture, offline or notification needs are demonstrated.

---

## 6. End-to-End User Journey

| Stage | Player goal / possible feeling | UI answer | Success signal | Failure state to design |
| --- | --- | --- | --- | --- |
| 1. Awareness | “What will this do for me?” Curious or skeptical | Concrete example, not “AI coach” slogans | Can explain benefit and requirement | Vague promise |
| 2. Evaluation | “Is it worth the effort and risk?” | Sample report, suitability checklist, cost and privacy summary | Informed trial decision | Hidden cost/limits |
| 3. Onboarding | Start without commitment | Optional purpose (skippable), neutral default | Reaches suitable next action | Questionnaire fatigue |
| 4. Capture | Get usable footage without disrupting play | Placement guide, framing preview, quick test clip, permission reminder | Suitable recording | Unsupported angle, missing consent |
| 5. Upload and processing | “Is my work safe?” | Separate upload from analysis; resumable; honest stages; leave-safely message | Known status or clean recovery | Interrupted upload, long wait |
| 6. First report | “What did I get?” | Scope/coverage first, then one finding or clip | Correct understanding of scope | Metric wall; claims beyond coverage |
| 7. First insight | Learn or enjoy something | Evidence-linked observation with clips | Confirms, corrects or rejects it | Untraceable claim |
| 8. First action | “What do I do?” | **Keep the moment / Understand the pattern / Try something next**: pick one or none | Chosen action, or informed non-action | Forced commitment |
| 9. Next opportunity | Revisit at the right moment | Saved focus + relevant clips before practice | Voluntary useful return | Irrelevant reminders |
| 10. Longitudinal review | “Am I improving?” | Comparable sessions with ranges and context | Accurate interpretation | Single smooth fake trend |
| 11. Deeper / coached use | Investigate or discuss | Workspace, playlists, correction | Useful analysis or conversation | Missing permissions/definitions |
| 12. Pause / leave / return | Keep control | Pause, export, delete, resume — no penalty | Respectful exit or reactivation | Guilt, lost history, hard cancellation |

**Successful non-use** (source 3): a player who internalizes a cue and goes to the club without opening the app is receiving value. Support silence, pause and graceful exit; track *benefit*, not only returns.

**Distinguish five different “not returning” states** before any outreach: (1) didn’t play, (2) played but didn’t record, (3) recorded but couldn’t upload, (4) got a report without value, (5) found value and has no reason to return yet. Never infer these from inactivity alone.

---

## 7. Page-by-Page Specifications

### 7.1 Public landing page

**Job:** let a visitor judge in under a minute whether this is for them, what it needs, and what it cannot do.

| Block (top to bottom) | Content | Rules |
| --- | --- | --- |
| Hero | Question-led headline, e.g. “Turn one match into clips, patterns and a next step.” plus a 20-second interactive example | Never an unexplained “AI coach” promise |
| Purpose cards | Keep the moments · Understand my game · Choose something to practice · Prepare to compete · Discuss with someone | Cards route to different sample views; none is “the real one” |
| How it works | Record → Upload → Check the evidence → Choose what to do (or nothing) | Show effort honestly, including recording setup |
| Inspectable sample report | Real-looking report with visible coverage, confidence reasons and a correction button | Clearly labelled sample; limitations visible; never implies typical accuracy |
| What we can and can’t analyze yet | Supported camera positions, singles/doubles, lighting, devices; features in preview | Capability status written from validated performance, not benchmarks on broadcast footage |
| Privacy in plain language | Private by default; analyze ≠ share ≠ model-training | Three separate permissions shown |
| Cost | Charges and equipment dependencies before any upload | No hidden limits after payment |
| FAQ | Opponent consent, accuracy, recording tips, data deletion | Links to recording guide |

**CTAs:** primary *See an example*; secondary *Analyze my match*. Use permissioned real examples, not invented popularity or fabricated testimonials.

### 7.2 Sample report

Built from the **same components** as the real report so users learn the real interface. Engagement with the sample proves *expectation comprehension*, not activation. Track it as a separate funnel.

### 7.3 Onboarding sequence (smallest coherent version)

Optional example → optional purpose → supported footage workflow → credible first result → optional next action.

| Step | User question | Interaction | Copy direction | Skip / exit | Success criterion |
| --- | --- | --- | --- | --- | --- |
| 1. Value page | “Is this worth considering?” | No personal data; example or own footage | Concrete benefit and supported limits | Leave freely | Can explain benefit and requirement |
| 2. Purpose | “What would be useful today?” | Pick up to two; “not sure” allowed | “Choose what matters now; change anytime.” | Skip → balanced default | Purpose captured without forcing a goal |
| 3. Depth | “How technical should this be?” | Quick / Guided / Advanced with one example of each | Show, don’t describe | Default Guided | Report density matches preference |
| 4. Readiness and permission | “Can I use this recording?” | Singles/doubles mode, framing check, short test clip, consent reminder (opponents, partners) | Practical requirements, exact privacy implications | Use example or return later | Suitable task and informed decision |
| 5. Privacy | “Who can see this?” | Plain-language choices, private default | “Private by default. Sharing is always your choice.” | Defaults apply | Explicit, informed consent |
| 6. Upload and processing | “Is my work safe?” | Resumable transfer, honest stages, optional completion channel | State what can still be delivered if analysis is partial | Cancel / retry / resume | Successful transfer or clean recovery |
| 7. First report | “What did I get?” | One finding or clip, scope visible first, optional guidance | Observation → evidence → limit | Explore freely | Segment-specific value confirmed |
| 8. Next step | “What now?” | Keep the moment / Understand the pattern / Try something next / Finish | No forced commitment | Dismiss | Chosen action understood |

**Hard rules:** no notification permission request before there is a reason to notify · account creation only when needed to protect the player’s work · no questions while waiting · no tour that blocks exploration · progressive profiling *after* first insight · never infer ambition, mood, age, willingness to share, skill or health from behavior.

### 7.4 Capture readiness

Capture is part of the product value, not a technical prerequisite hidden after signup (source 3, SwingVision lesson). A report cannot compensate for footage the system cannot interpret.

- **Framing preview:** court lines visible, both players in frame, tripod/placement guidance, lighting and visibility checks.
- **Test clip:** a few seconds analysed immediately so failures show up *before* a full match is recorded.
- **Result states:** *Suitable* · *Usable with limits* (list what will be unavailable) · *Not supported* (explain why and show a fix). “Try again” alone is never enough.
- **Doubles mode:** warn about occlusion and that analysis reliability is lower; the research datasets are mostly elite singles.
- **Consent block:** short, specific reminder about opponents, partners and venue rules; never a generic “I have everyone’s consent” checkbox standing in for a policy.
- **Minors:** adult-only pilot unless a reviewed youth safeguarding workflow exists (guardian permissions, club authorization, restricted sharing, no recording in changing rooms).
- **Mobile at court:** large labelled actions, short checklist, defer long reading.

### 7.5 Upload and processing

| State | What the player sees | Why |
| --- | --- | --- |
| Queued / transferring | Upload separate from analysis; resumable; interruption recovery | Preserve effort; no duplicates |
| Analyzing | Named stages (finding rallies → locating players → classifying shots), measured estimates only | No fabricated percentage or countdown |
| Partial | “These games/rallies were analyzed. These were not, because…” plus what remains usable | Never imply full-match coverage |
| Failed | Cause, what was saved, feasible next step | Preserve work |
| Complete | Notification only if opted in; message: “Your review is ready. Start with the moments you saved whenever you want.” | No invented urgency |

**Technical-reality mapping (source 6):** the pipeline runs as video-on-demand batch by default; buffered-live and strict-streaming modes degrade analytics (for example rally count and winner only, no shot types). The UI must show degradation honestly (“Movement analysis unavailable for part of this match”) and log it; never fill a gap with a guess. If the platform ever supports live, show a visible mode badge: *Live (reduced detail)*.

### 7.6 Home

See 5.2. Components on Home: **Resume card** (primary action), **Focus card** (only if chosen), **Latest evidence card**, **Progress signal** (only if comparable data exist), **Explore** (collapsed). Never a global player score; never a streak; never an empty chart wall.

### 7.7 Matches library

- **Match card:** opponent/event/score/duration (editable), video-quality chip, processing/coverage chip, purpose tag, saved-moment count.
- **Filters:** singles/doubles, practice/match/tournament, date, with-coach, analysis state.
- **No win-rate headline**; results are context, not the verdict.
- **Actions:** analyze, correct context, share, archive, delete. Missing sessions are simply absent, never displayed as zero performance.

### 7.8 Match report (the core page): three layers

- **Layer 1, Match story:** score context, momentum-neutral narrative, 3–5 neutral observations, key moments, a user-selected highlight.
- **Layer 2, Learning:** one verified strength, one high-leverage opportunity, supporting clips, optional focus.
- **Layer 3, Analysis:** rally, shot, position, movement and tactical exploration for people who want depth.

| Section | What the player sees | Data dependency | Action | If data are weak |
| --- | --- | --- | --- | --- |
| Scope and quality | Match identity, analyzed portions, exclusions, recording limits | Coverage assessment | Inspect exclusions, correct identity | State partial analysis plainly |
| Your reflection (optional) | “How did it feel?” or “Anything you want to look at?” | User input | Compare perception with evidence | Skippable; no guilt |
| Match story | 3–5 neutral observations | Reliable event/rally data | Open evidence | Show clips only, withhold unsupported claims |
| Meaningful moments | Tactical, resilient, clean-execution, longest-rally, player-chosen, coach-chosen | Video-linked events | Save / share / annotate | Offer footage-only highlight experience |
| Verified strength | Specific behavior with examples and denominators | Adequate sample and reliability | Preserve or extend | “No clear strength can be shown reliably yet” is allowed |
| Opportunity | One prioritized pattern | Contextual analysis | Choose focus / dismiss / ask coach | Say so when no clear opportunity exists; never invent criticism |
| Practice bridge | Small process goal, editable | Recommendation rules | Accept / edit / ask coach / decline | Do not generate a drill from uncertain evidence |
| Deep analysis | Rally, shot, court, movement, sequence | Higher-quality labels | Filter / build playlist / export | Unknown stays unknown, never zero |
| Quality panel | Coverage, label reliability, interpretive support, model version, corrections | Model diagnostics | Correct / reprocess | Compact by default, one tap to open |
| Share / export | Audience preview | Permissions | Share privately | Default off |

**Insight ranking (editorial, not “largest negative percentage wins”).** An insight appears only if: the measurement is supported under this recording condition; evidence is sufficient; it connects to the stated purpose; the player can understand it and its limits; there is a feasible action or a good reason to inspect; importance is proportionate to confidence and effort; and no counterexample is being concealed. Rank by purpose-relevance, confidence and sample adequacy, actionability, repetition/impact, novelty versus baseline, and emotional-cost/framing risk. Priority buckets: *Essential* (scope plus one supported finding) · *Useful secondary* · *Optional advanced* · *Interesting but non-actionable* (labelled descriptive).

**Layout.** Desktop: sticky video left, narrative/evidence right; clicking a claim seeks the video. Mobile: single column with a sticky mini-player; Quality panel as a bottom sheet. Evidence is **one clear action away** at every level.

**Storytelling pattern for every finding:** What happened? (bounded observation) → What supports it? (clips, counts, definitions, coverage) → Why might it matter? (conditional) → What else could explain it? (opponent quality, score state, partner role, fatigue, sample selection, labelling error) → What could you do next? (investigate, discuss, practice, save, or ignore).

### 7.9 Rally explorer

- **Timeline** of games/rallies linked to the video; hover/focus shows score state and rally length.
- **Filters:** game, score state, serve/receive, rally length, shot type, who won, outcome, opponent, singles/doubles role.
- **Sequence view, not terminal-shot view:** crediting only the last stroke can mislead (in one badminton analysis net shots produced many positive perturbations even when smashes dominated direct winners). Show the preceding sequence, then the ending.
- **Result list = clips**, each with a definition link, uncertain-label flag and correct button; table toggle for experts.
- **Doubles:** label roles (front/back, server/receiver); avoid blaming one partner from aggregate outcomes.

### 7.10 Spatial, tactical and movement views (capability-gated)

| View | Use | Mandatory safeguard |
| --- | --- | --- |
| Court map | Spatial patterns | State whether marks show player location, contact location or landing location; consistent orientation |
| Shot distribution | Compare shot choices | Counts **and** rates with opportunity denominators; frequency ≠ effectiveness; uncertain labels visible |
| Movement / recovery replay | Inspect routes and recovery | Distance or pose alone is not a quality judgement |
| Paired replay (doubles) | Coverage and coordination | No blame from aggregates |
| Technical overlay | Short guided replay | No biomechanical diagnosis from unvalidated pose estimates |

**Capability status pattern (every analytic):** *Available* (validated on target footage) · *Preview* (works with limits, shown with reasons) · *Not yet* (hidden or marked, never shown as a confident guess). Release progressively: dependable capture/replay and correction → guided questions and evidence-linked reports → longitudinal/coached workflows → predictive or prescriptive claims only after outcome testing. Published work shows rally and hit extraction can be strong while fine-grained shot classification is notably weaker (one 69-match study: 89.7% hit extraction, 54–72% shot classification depending on threshold), and the largest public datasets are elite singles, so **doubles and casual phone footage start in Preview**.

### 7.11 Progress

- **Player chooses** a process metric and, optionally, a subjective measure; the page never invents an overall score.
- **Comparable sessions only** (singles vs doubles, practice vs tournament separated); small multiples; ranges and session count shown.
- **Annotations:** equipment, opponent level, injury/return, model-version break.
- **Honest empty state:** “There aren’t enough comparable sessions to describe a trend yet. Here are the clips.”
- **Milestones** only after a predeclared sample rule and with the definition shown.
- **Status ladder** for each focus: *Reviewed* → *Practiced* → *Shown in later play*. Never skip steps or call a skill mastered because a clip was watched.
- Language: “associated with”, “changed after”, never “caused by this drill”. Opponent strength, fatigue, practice volume and recording quality all change results.
- **After a break:** offer a new baseline without erasing the past or showing a regression alarm.

### 7.12 Practice

**Recommendation anatomy (all seven parts):** Evidence (pattern and clips) · Meaning (why it may matter) · Uncertainty (confidence and alternatives) · Action (one feasible behavior) · Dose (only if coach-configured or sourced) · Success cue (what to notice) · Review rule (when and how it will be reassessed).

- **Focus card:** editable title, reason (“I chose this because…”), linked clips, planned cue-action sentence (“At the start of my next session I will…”), fallback if cancelled (reschedule or discuss, never pretend practice happened).
- **Barrier check (COM-B):** if planned practice isn’t done, ask what got in the way: didn’t understand the task / no court or partner / no time / not a priority now → offer instruction, an alternative, rescheduling or goal reconsideration. Reminders cannot create court access.
- **Reflect before the reveal (test):** after practice, ask “What changed?” *before* showing the metric.
- **Actions on a focus:** continue, modify, replace, pause, retire. No endless goal accumulation.
- **Coach confirmation option** on every drill idea; no unsafe physical changes or training load prescribed from video alone.
- **Process goals over outcome goals:** translate “win more rallies” into “recover to a balanced base after rear-court shots”.

### 7.13 Library (highlights and memory)

Highlight lenses (never just “biggest smash”): **Memorable** (player-chosen), **Illustrative** (supports a finding), **Tactically interesting** (worth investigating, not necessarily optimal), **Defensive sequence**, **Cleanest execution**, **Longest or most unusual rally**, **Coach-selected teaching clip**, **Verified personal milestone**. Include counterexamples in analytical reports to avoid highlight bias. Collections and playlists are private by default. Do not label every clip an achievement; speed estimates are not verified records.

### 7.14 Coach / Team (role-gated)

- **Access:** athlete-owned; scoped by athlete, team, match and time; links expire and are revocable; audit log.
- **Playlist builder:** pick clips, add **one question rather than a long list of faults**; the athlete responds with what they see and chooses the focus together.
- **Visible disagreement:** coach or player can dispute a label; correction history is shown.
- **Team view (hypothesis to test):** indicator of mastery vs performance language balance; need-support signals per athlete, never surveillance or ranking of low performers.
- **Role views:** player, coach, and (only if youth is ever supported) parent, each with its own permissions.
- Coach access never becomes permanent access to all future footage.

### 7.15 Settings and Privacy Centre

| Area | Contents |
| --- | --- |
| Purpose and depth | Editable defaults; tone: direct / balanced / coach-guided; “Show all” |
| Notifications | Per-trigger controls, quiet hours, digest mode, global pause, one-tap unsubscribe |
| Privacy | Three separate decisions: permission to record/process, who can access in product, what can be shared; retention periods; model-training reuse as a separate opt-in |
| Sharing | Active links, expiry, revoke; what cannot be recalled after export |
| Data | Export, delete (propagates to derived clips, embeddings and exports under platform control), pause |
| Metric definitions | Plain-language definitions and version history |
| Corrections | All corrections made, affected findings, model versions |
| Accessibility | Reduced motion, text size, high contrast, caption defaults, lower-bandwidth preview |

---

## 8. Component Library

### 8.1 InsightCard (the atomic unit of the report)

Every coaching-style insight contains six elements: **Question · Observation · Interpretation · Player context · Optional action · Recheck**.

```text
InsightCard
- title
- observation            (bounded; includes count and denominator)
- why_it_may_matter      (conditional wording)
- evidence_event_ids[]
- analyzable_sample_n
- denominator_n
- confidence_level       (plain-language label; levels only when calibrated)
- confidence_reason
- alternative_explanations[]
- recommended_action?
- target_segment[]
- user_goal_alignment
- user_response          (confirm | correct | dismiss | save)
- model_version
- generated_at
```

**Anatomy (top to bottom):** type tag (Observation / Interpretation / Suggestion) · headline · one-sentence evidence line with count/denominator · evidence thumbnails (play) · confidence chip with reason · action row: **Watch examples · That seems right · Correct this · Not useful · Save**. Interpretation and recommendation sit in separate, visibly different blocks from the measured fact.

**Worked example (illustrative, not a finding):** “In long rallies, you were often late returning to a balanced base after rear-court shots. This appeared in 6 of 9 analyzable long rallies. Confidence: medium, because two sequences were partially occluded.” \[Watch the 3 clearest examples\] \[That seems right\] \[Correct this\] \[Not useful\]

**Rules:** never use a headline that labels the person (“You lack composure”); use task language (“These rallies show a recurring situation worth reviewing”); every personalized suggestion either links to evidence or is labelled *general guidance*.

### 8.2 Evidence Clip Player

Wraps every “show me”. Jump to clip start with a short lead-in; frame step; speed control; caption/text description of the observation; overlays (court lines, player marker, shuttle path) off by default with a legend; keyboard and screen-reader operable; lower-bandwidth preview option; per-clip **Definition** link and **Report a mislabel**. For technique clips, add concise knowledge-of-performance cues (external-focus wording by default, coach override) rather than long paragraphs. Guided replay beats unguided replay: pair every clip with a cue to attend to.

### 8.3 Coverage and Confidence Chip + Quality Panel

Three distinct uncertainties, never merged into one badge:

| Type | Question | Example label |
| --- | --- | --- |
| **Recording coverage** | How much of the match was analyzable? | “Analyzed 14 of 17 rallies in game 2” |
| **Event-label reliability** | Is this shot/rally label likely right? | “Shot type uncertain in 3 clips: review labels” |
| **Interpretive support** | Does the data support this explanation? | “Several explanations fit; check with your coach” |

Chip = icon + word + shape (never color alone). Levels: **High** (clear footage, validated event type, adequate repeated sample) · **Medium** (partial occlusion, ambiguous context or modest sample) · **Low** (exploratory only; never default into coaching advice) · **Unavailable** (metric suppressed with the reason). Do not map confidence from softmax output; calibrate on held-out target footage and include upstream quality, sample adequacy and out-of-distribution flags. Until calibrated, use plain-language reasons only.

### 8.4 Event Status Badge (from the technical event ledger)

The pipeline gives every event a lifecycle: *candidate → provisional → confirmed → corrected* (or *suppressed*). Only **confirmed** and **corrected** events feed official analytics. Translate for players:

| Internal status | Player-facing label | Behavior |
| --- | --- | --- |
| Candidate | (not shown) | Never in stats |
| Provisional | “Needs review” (only in review mode) | Excluded from trends; shown in the review queue |
| Confirmed | no badge | Default; feeds metrics |
| Corrected | “Corrected by you/coach” | Affected findings recompute; show what changed |
| Suppressed | “Not counted: warm-up / replay / unclear” | Explain why; allow reinstatement |

Match-phase rules should be visible as context: warm-up hits, replays and breaks are **not counted**, and the match phase (warm-up / official / break / replay / ended) appears on the timeline. Warn when a metadata conflict arises (for example only three players visible in a doubles match).

### 8.5 Focus Card

Title (editable) · reason (“Chosen because…”, user-editable) · linked clips · cue-action plan · success cue · review rule · status ladder (Reviewed → Practiced → Shown in later play) · actions (edit, postpone, ask coach, retire). One active default focus; additional ones are opt-in.

### 8.6 Reflection Prompt

Optional, single question, skippable, no guilt copy. Variants: pre-analysis (“What felt important?”), post-feedback (“Does this fit what you noticed?”), post-practice (“What changed?”). A/B test against no prompt (burden vs calibration benefit).

### 8.7 Highlight Card

Clip thumbnail, lens label (see 7.13), one-line plain description of why it was chosen, editable boundaries, save / private share. No superlatives without verified definitions; no celebration animation tied to winning alone.

### 8.8 Court Map

Top-down badminton court with singles and doubles line sets, fixed orientation across the product (near side at the bottom), a legend that states exactly what a mark means, filter chips above, selectable marks that open clips, an accessible data-table alternative and a text summary of the pattern. Density: sparse marks for Quick, binned for Advanced.

### 8.9 Timeline

Horizontal rally timeline per game; marks for rally outcome, score state and flagged-uncertain rallies; match-phase bands; click/Enter jumps to video; zoom for long matches.

### 8.10 Trend and Distribution Charts

Points for individual comparable sessions with range bands, n per point, optional rolling average with the window explained, missing sessions drawn as gaps, annotation markers, model-version break lines. Use uncertainty intervals only with a defensible method (rallies cluster within matches). Never smooth to look authoritative; never use a gauge to dress up a weak metric.

### 8.11 Correction Flow

One-tap “Correct this” from any clip or finding → choose what’s wrong (shot type, player identity, rally boundary, score, other) → apply → **a banner shows which summaries changed and why**, with undo. Corrections are valuable labels, not an embarrassing fallback; the UI thanks the user briefly (“Thanks. Affected findings will update.”) and never defends the AI.

### 8.12 Share Preview Dialog

Before sharing show: exact footage and statistics included; identifiable people and names; recipients and access duration; whether download is allowed; how access is revoked and what cannot be recalled after export. Options to strip score or identity; hidden analytics stripped by default; teammate and opponent consent prompts. Never make sharing another player’s mistake a default engagement action.

### 8.13 Notification Preferences Panel

Allowed triggers only: analysis ready; coach comment or review request; user-scheduled practice reminder; enough comparable evidence to revisit a goal (separate opt-in); an opponent or event workflow the user follows. Each has its own switch, quiet hours, frequency limit and digest option, plus a global pause. No generic “come back”, shame, countdown or rank-drop messages, and no repeat alerts after dismissal.

### 8.14 Metric Definition Popover (information scent)

Tap any metric label → plain-language definition, numerator/denominator, time period, exclusions, model version, limits. Replace vague section names (“Advanced Insights”) with question-labelled sections (“Return situations to review before your next session”) and say which examples are inside and why.

### 8.15 State templates

Every state has a truthful explanation and a feasible next action. See the full catalog in section 12.

### 8.16 Purpose and Depth Switcher

Always visible in the report header: current purpose chips and a Quick / Guided / Advanced toggle, with “Shown because you chose…” and **Change · Reset · Show all**.

---

## 9. Feedback Language and Copy System

The same finding can support competence or threaten it. A major feedback meta-analysis found positive average effects but performance *decreases* in more than one-third of interventions, partly because attention shifts from the task to the self. So copy describes a **performance episode**, never the person. Kindness must never become false reassurance: confidence-safe design is not the suppression of inconvenient evidence.

### 9.1 Four epistemic layers (always visually and verbally distinct)

| Layer | Meaning | Example wording |
| --- | --- | --- |
| Measurement | A recorded or computed quantity under a definition | “This report includes the rallies listed below.” |
| Model classification | An algorithm’s label, subject to error | “These shots were classified as backhand lifts.” |
| Interpretation | A possible meaning of a pattern | “This sequence may be leaving fewer attacking options.” |
| Recommendation | A proposed action, conditional on context | “You could review recovery position with a coach before changing the shot.” |

A lost rally after a shot does not show the shot caused the loss. Use “associated with”, “appeared alongside”, “changed after”.

### 9.2 Copy by situation

| Situation | Use | Avoid |
| --- | --- | --- |
| Clear success | Specific recognition tied to a visible sequence (“You returned 7 of 9 deep clears in game two, compared with 4 of 10 in game one.”) | “Amazing! You’re becoming elite!” |
| Difficult pattern | Name the situation, not the person (“These rallies show a recurring difficulty after this response.”) | “Your defense is terrible”; “You lack composure” |
| Sparse data | “There are too few comparable examples to describe a trend yet.” | A precise percentage presented as stable ability |
| Low label reliability | “Some shots couldn’t be classified reliably. Review these labels.” | A confidence badge with no explanation |
| Conflicting sessions | “The pattern differs across these matches; context may matter.” | Showing only the most flattering result |
| Optional suggestion | “If this fits your goal, consider…” | “You must practice this next” |
| Missing footage | “This part of the match was not analyzed.” | Filling gaps with zeros or inferred outcomes |
| User disagrees | “Thanks. Review or correct the label; affected findings will update.” | Defending AI authority |
| No improvement detected | Show variability and context; offer to continue or change focus without blame | Implying failure or effort deficit |
| No clear opportunity | “Nothing stands out as a clear opportunity here.” | Inventing criticism to fill the card |
| After a loss | Keep the score; add “Which situations were handled well? Which recurring situation deserves practice?” | Forced positivity or deficit-only list |
| Return after break | “Resume with one match.” “Start a fresh baseline?” | “You broke your streak” |

**Vocabulary rules:** task language over trait language; “recurring situation” over “weakness”; “to review” over “to fix”; “try” over “must”; counts with denominators over adjectives; never “always”, “never”, “elite”, “unstoppable”, “mastered” unless a validated definition supports it.

### 9.3 Tone setting

User-selected **Direct · Balanced · Coach-guided** changes wording and ordering only. All three show the same evidence and the same limits. Players who want blunt technical detail get it.

### 9.4 Explaining outcomes without inventing causes (attribution)

When a pattern appears (for example short lifts), offer several candidate explanations rather than one verdict, each with a useful next question:

| Candidate | Question to ask | Next step |
| --- | --- | --- |
| Available effort/capacity | Was the action feasible under fatigue or recovery limits? | Discuss workload and conditions, not moral worth |
| Strategy | Was a different response appropriate? | Compare options in similar situations |
| Skill execution | Does a coach see a repeatable technical issue? | Coach-selected task |
| Opponent pressure | Did the opponent create unusually hard opportunities? | Compare like situations |
| Conditions | Court, equipment, visibility differences? | Annotate context before comparing |
| Chance or measurement error | Is the pattern small, unstable or inconsistently labelled? | Gather observations or correct labels |

Experiments show that how failure is explained changes later efficacy and performance, so the UI should prefer explanations that open a changeable next action and never label a loss as simply insufficient effort or deficient technique.

### 9.5 Feedback timing and form (player-controlled, then tested)

The evidence on feedback schedules is contested, so offer controls rather than a fixed doctrine:

- **Self-requested** (“Show me”), **after a block** (summary), **delayed after self-assessment**, **coach-coordinated**, and, for supervised drills only, **concurrent** cues.
- Prefer **quantitative** knowledge of results where precision matters (placement error, contact timing) over long qualitative paragraphs; pair video with brief performance cues.
- Invite self-assessment first (“What did that feel like?”) before supplying the answer.
- Do not use continuous real-time feedback that creates dependency; do not hard-code fading.
- Evaluate against **delayed, unassisted** performance, because the best assisted session is not evidence of learning.
- Separate drill scores from match transfer: one badminton anticipation study improved video-task accuracy but not real-match performance.

---

## 10. Visual Design System (proposed starting point)

**Honest scope note:** the research dictates *constraints and behaviors* (hierarchy, non-color encoding, honest loading, no celebration for dubious achievement, readable numbers, density modes). It does not prescribe brand, palette or typeface. The concrete values below are **proposed defaults** to unblock prototyping; verify every color pair against WCAG 2.2 AA with automated and manual checks before shipping.

### 10.1 Visual personality

Calm, credible, sport-forward. Clarity over spectacle: the interface should feel like a trustworthy analyst sitting next to the player, not a game. Footage and the court are the visual heroes; chrome stays quiet.

### 10.2 Hierarchy rule for every screen

**Scope → finding → evidence → action.** Test: can a first-time user name the main point before reading detail? Only one primary finding gets large type; supporting numbers are secondary.

### 10.3 Semantic color (never the only signal)

| Role | Proposed light value | Always paired with | Notes |
| --- | --- | --- | --- |
| Surface / surface-alt / border | #FFFFFF / #F4F6F8 / #D5DAE0 | n/a | Provide a true dark theme with the same roles |
| Text primary / secondary | #111827 / #4B5563 | n/a | Body text meets 4.5:1 |
| Primary action (court teal) | #0B6E6E | Label | One primary action per view |
| Evidence / link / info | #1D4ED8 | Play icon, underline for links | Marks anything that opens clips or definitions |
| Verified strength | #166534 | ✓ icon and the word “Strength” |  |
| Opportunity | #B45309 | ◆ icon and the word “Opportunity” | Amber, **not red**: avoids shame and threat framing |
| Uncertain / partial coverage | #475569 + hatch pattern | “?” icon and the words “Partial coverage” / “Uncertain” | Hatching also marks missing data on charts |
| Corrected | #6D28D9 | Pencil icon and “Corrected” |  |
| Error / destructive | #B91C1C | Icon and text | **Reserved for system errors and destructive actions, never for performance** |

Red/green is never the only good/bad signal. Do not color a player’s statistic red to imply failure.

### 10.4 Token starter (CSS custom properties)

```css
:root {
  --color-surface: #FFFFFF;
  --color-surface-alt: #F4F6F8;
  --color-border: #D5DAE0;
  --color-text: #111827;
  --color-text-muted: #4B5563;
  --color-primary: #0B6E6E;
  --color-evidence: #1D4ED8;
  --color-strength: #166534;
  --color-opportunity: #B45309;
  --color-uncertain: #475569;
  --color-corrected: #6D28D9;
  --color-error: #B91C1C;

  --space-1: 4px;  --space-2: 8px;  --space-3: 12px;
  --space-4: 16px; --space-6: 24px; --space-8: 32px;

  --radius-card: 12px;
  --target-min: 44px;        /* recommended touch target; WCAG 2.2 AA floor is 24px */
  --font-body: 16px;         /* never smaller for body text */
  --motion-fast: 150ms;
  --motion-base: 250ms;
}
@media (prefers-reduced-motion: reduce) {
  :root { --motion-fast: 0ms; --motion-base: 0ms; }
}
```

### 10.5 Typography

- Humanist sans-serif UI face with **tabular numerals** for stats and tables; scale 14 / 16 / 18 / 22 / 28 / 36; body never below 16px; line-height about 1.5; line length 65–75 characters.
- Every number shows its unit and, for rates, numerator and denominator (“6 of 9 rallies”), not just a percentage.
- Support 200% text resize, long translated labels and wrapping; avoid idioms in core feedback copy.
- One large “hero number” per view at most, and only for a verified, defined metric.

### 10.6 Layout, density and responsive behavior

| Aspect | Rule |
| --- | --- |
| Breakpoints (proposed) | 360 / 768 / 1024 / 1440; report is two-column from 1024 |
| Mobile priorities | Capture, upload status, resume, quick recap; evidence in bottom sheets |
| Desktop priorities | Video beside data, comparison, keyboard-accessible filters |
| Density modes | Quick (airy, large clips), Guided (default), Advanced (compact tables, dense filters), tied to the depth switcher |
| Consistency | Same underlying data and permissions across layouts |

### 10.7 Data-visualization grammar

- **Court maps** for spatial patterns; **timelines** for score and rally progression; **distributions** for variability; **small multiples** for session comparison; **tables** for event lists.
- Show denominators, sample size, period, exclusions; label units and baselines.
- Never a gauge to make a weak metric look authoritative; never a single smooth “improvement score”.
- Missing data = hatched gap, never zero. Model-version changes = vertical break line.
- Categorical palette limited to 5 hues, always doubled with shape or pattern; a text summary and an accessible data table accompany every chart.
- Court orientation identical everywhere; legend states precisely what each mark represents.

### 10.8 Motion

Motion supports orientation, not excitement. Functional transitions only (150–250ms); no looping animation; **no confetti or celebration tied to winning or to unverified achievements**; video never autoplays with sound; honor reduced-motion; loading uses skeletons of the real layout and honest stage names, never fake progress bars.

### 10.9 Imagery and iconography

Real match thumbnails, not stock athletes. Offer face/bystander blurring where feasible. Icons accompany labels for critical actions (never icon-only). No mascots, trophies or level crests in the core product.

### 10.10 Video player UI

Large, labelled controls; keyboard shortcuts (space, arrows, frame-step); captions/transcripts for any audio; text description of what the clip shows; overlays off by default; consistent clip-boundary markers on the scrubber; lower-bandwidth preview mode with a clear “preview quality” label that does not imply lower analysis quality.

---

## 11. Engagement, Social and Return Mechanics

**Governing test for every mechanic:** it needs (1) a user-value theory, (2) a harm test, (3) an opt-in path, and (4) a sporting reason. Gamification evidence is mixed and modest (a 16-trial meta-analysis found g≈.42 for physical activity but bundled many components; a course study with badges and a leaderboard found *lower* motivation, satisfaction and empowerment). Rewards can inform or control (128-experiment meta-analysis), and a competition arm in a 602-person walking trial raised steps but activity fell afterwards and the result concerns steps, not badminton learning. So: test, never assume.

### 11.1 Decision table

| Mechanic | Decision | If used |
| --- | --- | --- |
| Points / XP | **Do not build** | Rewards activity, not value |
| Levels / universal rating | **Do not build** until a construct is validated | Separate exposure, practice and demonstrated performance |
| Badges | Rare, optional, evidence-backed | Tied to a verified milestone with its definition shown |
| Milestones | Build after sample thresholds | Stable definitions; “personal best” shows context; no auto-escalated next target |
| Personal challenges | Opt-in, editable, pauseable | Player/coach-defined process goals; no unsuitable volume |
| Streaks | **Reject at launch** | If ever tested: opt-in, weekly or event-based, forgiving, never punishing unrecorded play |
| Leaderboards | **Defer**; global never by default | Opt-in, bounded peer groups with explained matching; test against private and cooperative alternatives |
| Collections / playlists | Build | Private by default; memory and retrieval value |
| Social recognition | Later, consent-based | Starts with private coach/partner sharing; measure useful exchange, not likes |
| Club challenges | Phase 4 experiment | Tied to participation or learning, not only winning; include low-ranked and disengaging users in evaluation |

### 11.2 Comparison is the player’s choice

Offer a reference picker: **My past self (default) · A similar peer group · An expert example · Nothing**. Always explain the population and context behind a benchmark, allow hiding it, and show a learning question next to any gap (“What does this player do differently in the same situation?”). Upward comparison can inspire or discourage; downward can create superiority or complacency; so never surface others’ weaknesses as content. Public profiles require deliberate consent; a teammate’s consent is never inferred from an upload.

### 11.3 Notification policy (all opt-in unless delivering a requested result)

| Trigger | Purpose | Control | Guardrail |
| --- | --- | --- | --- |
| Analysis completed | Deliver what was requested | Channel chosen at upload | No urgency |
| User-set review/practice time | Enact their own intention | User sets time; snooze/disable | No guilt after a miss |
| Planned practice | Retrieve a chosen focus | Explicit opt-in tied to that plan | Don’t invent a schedule |
| Meaningful new trend | Alert to a supported change | Separate opt-in; explains why noteworthy | Never for noise or every metric movement |
| Coach comment / review request | Collaboration | Per-coach control | Quiet hours respected |
| Pending reflection | Resume a voluntary task | In-product invitation by default | No repetitive push escalation |
| Inactivity | Usually no new value exists | **None by default** | Ask about pausing only respectfully |

Suitable example: “Your review is ready. Start with the moments you saved whenever you want.” Provide per-trigger switches, quiet periods, frequency limits, digest mode and a global pause. Evaluate by useful action, fatigue, pressure and opt-outs, never open rate alone. Do not ask for notification permission until a notification has a clear reason.

### 11.4 Return, lapse and graceful exit

| Situation | Design |
| --- | --- |
| Returns after weeks away | “Resume with one match.” History intact; no reset, no lost-streak language |
| Resumes viewing without new recording | Allowed: review old information without collecting new data |
| Injury, season end, no suitable camera | Pause gracefully; no deficiency framing |
| Goal achieved or learned enough | Offer export and a light “keep my moments” mode; count it as success |
| Wants to leave | Export, delete, cancel in two clear steps; no guilt screens |
| Subscription decisions | Transparent value; no fear-based upsell right after a poor performance |

Use the five “not returning” states (section 6) to choose a response; never run a generic “we miss you” campaign. Where tracking stops, ask lightly whether the reason was burden, unreliable data, changed circumstances or having learned enough, so the product learns without assuming failure.

### 11.5 Social features: private first

Order of build: private coach/partner review → permissioned shared playlists → private collections → opt-in peer cohorts → club challenges. A public feed, public rankings and public weakness reports are not in scope. Club belonging can both support and constrain (in-group clubs sustain identity but may limit intergroup contact), so study real clubs, not isolated users.

---

## 12. State Catalog (every state has a truthful explanation and a feasible next action)

| State | What to say | Next action offered |
| --- | --- | --- |
| No footage yet | “Start with an example or upload a match.” | Sample report; recording guide |
| Unsupported / unsuitable footage | Why it can’t be analyzed (angle, visibility, resolution) | Setup fix, re-record, keep footage-only highlights |
| Permission uncertainty | What consent is needed from whom | Consent guide; proceed privately; return later |
| Upload queued / transferring | Progress and that it is safe to leave | Pause, cancel, notify when done |
| Upload interrupted / recovered | “Resumed where it stopped.” No duplicate | Resume; retry on another network |
| Analysis pending | Named stages and measured estimate | Notify me; review later |
| Analysis partial | What was and wasn’t analyzed and why | Open what is available; re-record gaps |
| Analysis failed | Cause, what was saved | Retry, support, footage-only mode |
| Low-quality footage | Cause, what remains usable | Setup fix |
| Insufficient sample | “Too few examples for a trend claim.” | Show clips without a trend |
| Uncertain labels awaiting review | Which labels and why | Review queue; correct |
| Conflicting signals | Present both, invite review | Open each; ask coach |
| Model disagreement | Abstain or request correction | Correct this |
| No clear opportunity | “Nothing stands out.” | Explore freely; save moments |
| No improvement detected | Variability and context, no blame | Continue, change focus, pause |
| Corrected result affecting earlier findings | What changed, which findings updated, version | Undo; view history |
| No comparable sessions | “Compare after another suitable session.” | Sample or recording help |
| Shared access expired / revoked | Who lost access and when | Re-share, adjust expiry |
| Paused / exported / deleted | Confirm, state what is retained and for how long | Resume; download |
| Replay / warm-up detected | “These shots are not counted: warm-up/replay.” | Reinstate if wrong |
| Metadata conflict | “Only three players are visible in this doubles match.” | Confirm players; adjust mode |

Empty states never show fake data. “Try again” is never the only option when the footage itself cannot support the analysis.

---

## 13. Accessibility, Privacy, Trust and Safety (launch requirements, not later polish)

### 13.1 Accessibility: WCAG 2.2 AA target

Meeting AA means meeting every Level A and AA criterion; an automated scan alone is not conformance. Test manually and with assistive technology.

- Keyboard operation for every control, including clip scrubbing, frame stepping, annotations and drag alternatives; visible focus; logical reading order.
- Text alternatives for charts and clips; **every chart has a plain-language summary and an accessible data table**.
- Non-color encodings (icon, shape, pattern, word); contrast for text, UI components and chart marks.
- Adequate target sizes; text resizing and reflow; reduced-motion; captions for audio.
- Plain-language metric explanations and an in-context glossary; no unexplained expert jargon.
- Small screens, low-end devices, limited bandwidth, interrupted uploads; lower-resolution preview and deferred download.
- Multilingual copy expansion; test terminology with real players.
- Include adaptive/para-badminton players in research if they are in scope, and do not assume models trained on one movement context generalize.
- Do not assume a tripod, premium phone, smartwatch or private venue.

### 13.2 Privacy and consent: three separate decisions

1. **Permission to record and process** (opponents, partners, coaches, spectators, venue rules, applicable law).
2. **Access inside the product** (who can inspect footage, labels, notes, reports).
3. **Sharing or publication** (what can leave the original context and under what authorization).

Do not bundle optional publication or model training into essential service access; consent to analyze never silently becomes consent to train or publish. Consent is not the only legal basis for every activity, so obtain jurisdiction-specific legal advice.

### 13.3 Data governance (explain before accepting footage)

- What is collected, purposes, processors, storage regions; retention for original footage, derived clips, labels, reports, backups, logs.
- Role-based access, authentication, encryption in transit and at rest; audit log for coach access.
- Export and deletion, including derived clips, embeddings and exports under platform control, with honest limits on backups and on copies already downloaded.
- Bystander handling and removal requests; separate opt-in for model-training reuse.
- Never choose indefinite retention just because storage makes future engagement possible.
- A hidden name or map in one product does not protect every downstream copy (the Strava privacy lesson): explain what exported clips and reports can leak.

### 13.4 Minors and safeguarding

Run an **adult-only pilot** unless a properly reviewed youth workflow exists: guardian and participant permissions, club/school authorization, rules for authorized devices, accommodation when someone does not consent, no recording in sensitive locations, restricted sharing, identity minimization, retention and incident handling.

### 13.5 Trust operations (NIST-style loop, made visible in the UI)

1. Define supported conditions and metrics. 2. Evaluate on independently labelled, representative footage. 3. Report performance by condition, not one average. 4. Detect poor-quality or out-of-scope input. 5. Withhold unsupported conclusions. 6. Allow correction and disagreement. 7. Update affected reports and comparisons. 8. Explain material corrections and version changes. 9. Monitor deployed performance and emerging harms.

Monitor by camera setup, venue, lighting, clothing, handedness, event type and playing category where lawful and ethical. Publish intended use and known failure modes. Explanations alone do not prevent over-reliance, so pair them with evidence access, easy correction and abstention.

### 13.6 Non-manipulative engagement

Reject artificial scarcity, shame-based comparisons, guilt notifications, compulsory streak protection, hidden sharing defaults and unnecessary friction designed to inflate engagement. Do not reward more recording if it disrupts play, increases unwanted exposure or does not serve the player’s purpose.

---

## 14. Measurement and Instrumentation

### 14.1 Measurement families (keep separate; never one blended score)

| Family | Measures | Limit |
| --- | --- | --- |
| Product | Suitable upload rate, analysis success, active effort and wall-clock time to value, repeat analysis, evidence access | Activity ≠ understanding |
| User value | Perceived usefulness, correct teach-back, meaningful clip found, feasible priority chosen, review satisfaction | Self-report ≠ behavior or learning |
| Longitudinal | Continued voluntary value, goal progress, self-regulated review, reliable sporting measures | Many possible causes |
| Guardrails | Confusion, statistical misinterpretation, over-reliance, pressure, privacy concern, notification fatigue, recording disruption | Few complaints can mean silent exit |
| Psychological mediators (leading indicators) | Perceived autonomy, competence, relatedness; mastery vs performance goal endorsement; task-specific self-efficacy | Survey-based; sample, not stream |

### 14.2 Operational definitions

- **Time to first meaningful value:** from a defined start event to segment-specific confirmed value; report active effort separately from upload/processing time; include people who never reach value; separate sample and personal funnels.
- **Technical analysis success:** supported input reaches a usable result with known coverage (separate unsupported input, infrastructure failure, partial analysis, classification quality).
- **Comprehension:** a predefined teach-back or decision task, not opening an explanation.
- **Trust calibration:** accept correct findings, question incorrect or weak ones; maximum trust is not the target.
- **Meaningful return:** a voluntary visit that produces an appropriate review, saved moment, focus retrieval, comparison or coaching exchange.
- **Opportunity-adjusted continuation:** relate use to known playing/recording/review opportunities; keep unknown opportunity states explicit.
- **Improvement:** a reliable, goal-relevant measure with context and delayed observation; never a rising proprietary score.

### 14.3 Event taxonomy (frontend telemetry)

`example_opened` · `purpose_selected` · `purpose_skipped` · `suitability_checked` · `upload_started` · `upload_interrupted` · `upload_resumed` · `analysis_started` · `analysis_partial` · `analysis_completed` · `first_insight_viewed` · `coverage_opened` · `finding_opened` · `evidence_clip_opened` · `evidence_played` · `insight_response` (confirm / correct / dismiss / save) · `label_corrected` · `finding_rejected` · `clip_saved` · `practice_focus_chosen` · `focus_selected` · `focus_edited` · `focus_retired` · `comparison_opened` · `report_comprehension` · `share_previewed` · `share_initiated` · `access_granted` · `access_revoked` · `privacy_changed` · `reminder_enabled` · `reminder_paused` · `resume_after_lapse` · `data_exported` · `deletion_requested` · `harm_signal`

**Required context:** report/model version, match format, analysis coverage, device/network class where appropriate, experiment assignment. Minimize personal data; never log raw sensitive content just because it could be useful. Share events record audience type, never recipient identity.

### 14.4 Causal discipline

Funnels locate drop-off but don’t explain it; cohorts describe continuation, not cause; pre/post comparisons suffer practice, maturation, seasonality and regression to the mean; A/B tests need pre-specified outcomes, minimum worthwhile effect, guardrails, assignment unit (cluster-aware for clubs and coaches), stopping rule and analysis. Distinguish exploratory from confirmatory analysis, and stop any experiment that raises harmful advice, privacy concern or guilt even if engagement rises. Do not redefine success after a failed primary outcome.

---

## 15. Front-End Build Order and Roadmap

Prioritize by evidence strength, consequence of failure, dependency on analytics, effort, psychological/privacy/safety risk, and reversibility. **A privacy or accuracy foundation can outrank a promising feature even without proof it raises retention.**

| Phase | Build (front end) | Why now | Exit evidence |
| --- | --- | --- | --- |
| **0. Trustworthy feasibility** | Supported-recording spec and readiness flow; coverage/quality panel; private access; retention/deletion/export; recoverable uploads; accessible video playback; correction flow; state catalog; design tokens and component shells | All later value depends on usable, legitimate data | Representative footage works; critical errors understood; privacy and accessibility checks pass |
| **1. First meaningful value** | Landing + inspectable sample; optional purpose/depth; guided upload; short evidence-linked match report (story, moments, one strength, one opportunity); save clip; optional focus; restricted coach share; instrumentation for comprehension and harm | Tests the core proposition without growth complexity | Users reach segment-specific value, can state a finding, understand limits |
| **2. Learning loop and recurring value** | Editable practice focus and cue-action plan; comparable-session progress; focus retrieval before practice; optional reflection; user-set reminders; private collections; coach annotation; graceful return after lapses | Needs repeated real opportunities and stable measures | Useful voluntary return without pressure; accurate trend interpretation |
| **3. Tactical depth** | Rally explorer with sequence view; opponent and score-state filters; singles/doubles-specific views; custom tags; advanced export; recommendations only in validated domains | Depends on demonstrated expert need and reliable labels | Expert task success; measurable workflow benefit |
| **4. Selective social and personalization** | Opt-in peer cohorts; club challenges tied to participation or learning; sharing templates with audience preview; recovery/load proxies (only if validated); adaptive depth; experimentation framework | Weak direct evidence, so only after core value is proven | Net benefit with guardrails intact |

### 15.1 Do not build yet

Universal player rating marketed as ability truth · daily streaks · default public rankings · public feed · universal skill score · real-time tactical instruction during competition · injury prediction or medical advice · public opponent dossiers assembled without consent · autonomous technique coaching from unvalidated pose estimates · generative advice that cannot cite match evidence · elaborate point/badge economies · broad hardware ecosystem · native app by default.

### 15.2 Pre-pilot checklist

- [ ] Supported input and analytical claims documented on the public page
- [ ] Ground-truth labelling and evaluation process exist; performance reported by condition
- [ ] Partial and failed analysis represented honestly in the UI
- [ ] Every finding links to evidence and definitions
- [ ] Users can disagree, correct and see what updated
- [ ] Costs, retention, access and sharing explained before commitment
- [ ] Opponent/partner and minor-related procedures reviewed
- [ ] Critical flows pass keyboard, screen-reader, mobile and interrupted-network testing
- [ ] Activation defined by user value, separate from technical completion
- [ ] Event instrumentation and guardrail measures ready
- [ ] Research includes non-users and leavers
- [ ] No engagement mechanic pressures use without a sporting reason

---

## 16. Validation Plan: Test the Prototype, Not the Assumption

Every pattern here is a hypothesis grounded in general evidence. Build **one coherent prototype** covering: entry page, optional sample, readiness/upload flow, partial-analysis state, evidence-linked report, saved focus, comparison and privacy settings. Test it with the working segments and observe capture in real venues, then revise IA and instrumentation before expanding scope.

### 16.1 Recruitment

Current analytics users, interested non-users, skeptical non-users and **people who stopped using similar products** (non-adoption reveals what enthusiast samples hide). Cover the segments, singles and doubles, ages and genders in scope, digital literacy, device quality, connectivity and coaching access. Include coaches and club organizers; add adaptive badminton if in scope. Avoid friends of the team.

### 16.2 Usability tasks and pass criteria

| Task | Observable success | Likely failure |
| --- | --- | --- |
| Explain the product after the entry page | States a realistic benefit and a key limit | Repeats “AI coach” |
| Choose sample vs own footage | Picks an appropriate route unaided | Can’t tell suitability or cost |
| Complete an upload after interruption | Recovers without losing work or duplicating | Restarts or assumes completion |
| Find a relevant finding | Locates one tied to stated purpose | Wanders the metric list |
| Explain a visualization | Identifies denominator, context, direction | Confuses volume with success, or missing with zero |
| Inspect the evidence | Opens clips, identifies scope | Treats summary as unchallengeable |
| Detect a seeded incorrect finding | Uses evidence to reject or qualify it | Accepts because it sounds confident |
| Choose a practice priority | Selects a feasible, understood focus or declines | Copies generic advice |
| Compare sessions | Names at least one comparability limit | Calls any favorable change “improvement” |
| Change personalization | Edits purpose/depth and understands the effect | Believes the segment is permanent |
| Control sharing and notifications | Predicts recipients, content and reminder behavior | Thinks hiding names equals privacy |
| Interpret uncertainty/missing data | States what cannot be concluded | Turns uncertainty into certainty or total distrust |

Pre-define the rubric and acceptable assistance. Record critical errors separately from speed (a fast privacy mistake is a failure). **Proposed launch bar (not a literature standard):** at least 80% of target users state the report’s main finding accurately without help; evidence, uncertainty and correction controls are findable; critical privacy tasks succeed without reading policy; advanced users reach event-level evidence without complicating novice defaults; no systematic reading of hypotheses as facts.

### 16.3 Highest-priority experiments

| # | Hypothesis | Comparison | Primary outcome | Guardrail |
| --- | --- | --- | --- | --- |
| 1 | Quality-aware withholding improves interpretation | Coverage explanation + withholding vs ordinary bounded report | Correct scope interpretation | Confusion, unjustified confidence |
| 2 | Contextual setup support improves usable footage | Short suitability guide vs existing instructions | Usable-recording rate | Burden, permission failures |
| 3 | An optional example reduces expectation mismatch | Example before upload vs direct upload | Accurate expectations, then personal activation | Overpromising, abandonment |
| 4 | Evidence-first reports improve comprehension | Short observation + clips vs statistics-first | Correct teach-back | Time, frustration |
| 5 | One editable focus increases action | One suggested focus vs equal unprioritized findings | Feasible chosen priority | Autonomy, overlooked needs |
| 6 | Skippable purpose improves fit | One optional question vs neutral default | Perceived/confirmed value | Setup drop-off, stereotyping |
| 7 | Short coach playlists improve shared understanding | Annotated clips vs usual review | Athlete explanation quality | Pressure, access mistakes |
| 8 | Personally selectable highlights add value | Candidate clips + selection vs automatic list | Meaningful moment found | Irrelevance, sharing errors |
| 9 | Optional reflection calibrates reliance | Pre/post reflection vs none | Discrimination of supported vs unsupported findings | Burden |
| 10 | Graceful resume improves reactivation | Neutral “resume” vs progress-loss framing | Return to meaningful action | Guilt, pressure |
| 11 | Review-to-practice workflow improves learning | Full workflow vs review-only vs usual practice | Independently assessed delayed outcome | Injury risk, over-reliance |

Pair behavioral data with comprehension, trust, autonomy and pressure measures. Re-run key effects with actual badminton players before platform-wide rollout. When an experiment raises engagement but worsens understanding, pressure or privacy concern, **reject it**.

---

## 17. Feature Feasibility Map: What the Technical Pipeline Lets the UI Claim

The technical report (source 6) shows which parts of the analysis are mature and which are gaps. The front end must mirror this: **a panel never looks more certain than the model behind it.**

| Capability | Technical basis and status | UI treatment |
| --- | --- | --- |
| Shuttle tracking | TrackNetV3-class models report about 98.6% F1 on a broadcast-heavy dataset at roughly 25 FPS; casual phone footage faces domain shift | Available only after validation on target footage; otherwise Preview; show “shuttle not tracked here” gaps |
| Player detection and identity | Detector plus tracker is strong; identity flips are likely with similar clothing, occlusion, doubles | One-time player identity confirmation; “player identity uncertain in these clips”; doubles in Preview |
| Pose / movement | Real-time pose models exist but are run at lower rate or around events to save compute | Movement and technique overlays are Preview; no biomechanical diagnosis |
| Racket detection | No known open pretrained detector | No racket-dependent claims |
| Contact (hit) detection | **Biggest gap:** no pretrained model; must be trained; about ±3 frame tolerance | Limit timing-sensitive claims; link shots by tolerance windows; no contact height or speed claims |
| Shot classification | No public badminton model; training data from rich but mostly elite singles datasets (about 18 stroke classes in the largest) | Shot type is Preview with per-class uncertainty and an easy correct button; never a confident label without reliability |
| Smash / jump-smash | Rule-plus-classifier fusion | Separate “event recognized” from “technique quality” |
| Court calibration | One-time homography; breaks if camera moves | Court maps valid only while calibration holds; “court lines not detected” state with fix |
| Scoreboard OCR | Works only when a scoreboard is visible; amateur footage rarely has one | Manual score entry fallback; user can correct score |
| Rally and score engine | Deterministic BWF rules; match-phase state machine (warm-up, official, break, replay, ended); winner confirmed only when visibility is sufficient | Show phase on timeline; uncounted segments explained; allow score correction |
| Agentic assistant | A constrained agent may flag, re-run models or draft summaries from stored events, but **never changes score or confirmed state** | Every AI summary cites specific events and opens them; label it “Generated from analyzed events”; correctable |
| Deployment modes | Batch VOD (richest), buffered live (about 2s), strict streaming (cheapest models) with graceful degradation | Visible mode badge; reduced-detail messaging; degradations logged and explained |

**Consequence for the roadmap:** until the contact detector and shot classifier are validated on user-generated footage, the honest MVP is *dependable capture → rally segmentation → clip navigation → highlights → correction*, with shot-level analytics labelled Preview. This is also the research’s own recommendation: reliable review and correction before generalized coaching.

---

## 18. Design Review Checklist (apply to every screen before build)

1. **Purpose:** does it answer a question the player chose or would plausibly ask?
2. **Value first:** does the player get something useful before configuration or commitment?
3. **One priority:** is there a single primary finding or action, and is the rest on demand?
4. **Evidence:** is every claim one action away from clips, definition, denominator and coverage?
5. **Uncertainty:** are coverage, label reliability and interpretive support visible and in plain words?
6. **Layers:** are measurement, classification, interpretation and recommendation visibly distinct?
7. **Language:** is it about the episode, not the person; conditional where causal; free of unearned praise?
8. **Agency:** can the player edit, decline, defer, correct or skip without penalty?
9. **Emotion:** has the post-loss, first-recording and return-after-break experience been walked through?
10. **Comparison:** is the default self-referenced and any social comparison opt-in and explained?
11. **Privacy:** is it private by default, with sharing previewed and separate from analysis and training?
12. **Accessibility:** keyboard, screen reader, non-color cues, reflow, reduced motion, low bandwidth?
13. **States:** are empty, partial, failed, corrected and no-data states designed and honest?
14. **Pressure:** does any element create guilt, urgency, streak loss or public judgement?
15. **Measurement:** which understanding, action and guardrail events does it emit, and what would make us reject it?

---

## 19. Key Evidence at a Glance (and What Each Means for the UI)

| Finding | Strength | UI consequence |
| --- | --- | --- |
| Autonomous motivation is consistently linked to exercise; identified regulation matters for adoption, intrinsic motivation for adherence (66-study review) | Strong association; limited UI causality | Editable goals with rationale; make the reason for playing visible |
| Coach autonomy support relates to autonomous motivation and need satisfaction (131 samples, 38,844 participants; corrected r≈.39) | Mostly cross-sectional | Coach tools support, not control; athlete owns access |
| Mastery climates show more adaptive correlates (104-study review) | Associative | Default framing is personal improvement, with results preserved |
| Pre-event self-efficacy relates to performance, r≈.31–.38, wide prediction intervals | Moderate | Task-specific evidence panels; no global confidence score |
| Process goals showed larger pooled effects than outcome goals (27 studies, overall d≈.47, heterogeneous) | Moderate | Translate outcomes into one controllable process focus |
| Feedback improves performance on average but lowers it in more than one-third of interventions | Strong caution | Task-focused, specific, user-timed feedback |
| Reduced feedback frequency showed no significant advantage (61 papers); self-controlled benefits shrink after bias correction | Contested | Offer timing control; do not hard-code fading; test on delayed performance |
| Guided video feedback helps in PE settings (11 studies, fewer than half tested retention) | Limited transfer | Pair clips with cues and a chance to test understanding |
| One badminton anticipation study (42 participants): task accuracy improved, real-match performance did not | Small but pointed | Keep drill scores and match transfer separate |
| Habit formation takes a median of about 66 days with very wide individual variation; missing one opportunity did not reset it | Moderate | Event-based routines, no daily-streak pressure |
| Growth-mindset effects are very small on average (d≈.05–.14) | Contested | Strategy-specific copy only; not a core mechanic |
| Gamified bundles show mixed, modest effects; one badge-and-leaderboard course lowered motivation | Mixed | Narrow, optional, evidence-backed recognition |
| Competition raised steps most in a 602-person trial but activity declined afterwards | Specific to steps | Test opt-in competition vs private and cooperative options |
| Social comparison raised exercise attendance by 62% in a randomized network experiment | Single context | Comparison is a controllable instrument, not a default leaderboard |
| Amateurs tended to trust device data; elite athletes questioned it (20 athletes) | Qualitative | Simplify explanation, never hide uncertainty; support expert disagreement |
| Users stop tracking because of burden, discomfort, unreliable data, changed circumstances or having learned enough (193 surveyed, 12 interviewed) | Qualitative | Pause, export, successful non-use |
| Hit extraction can be strong (89.7% in a 69-match study) while shot classification is much weaker (54–72%) | Technical | Gate shot-level claims; show confidence and correction |
| Explanations alone do not prevent over-reliance on AI | Moderate | Evidence access, easy correction, abstention, seeded-error tests |

---

## 20. Open Questions to Resolve with Real Players

1. Which post-match questions matter most to amateur players in different countries and club cultures?
2. Do recreational players want technical analytics, or mostly highlights and simple reflection?
3. What minimum accuracy is acceptable for each event type and segment?
4. How should uncertainty be shown so novices understand it without abandoning useful evidence?
5. Which corrections are feasible on mobile without creating a tagging burden?
6. Does choosing one process goal change practice behavior, or only report satisfaction?
7. When does self-comparison motivate and when does it produce rumination?
8. How do doubles partners negotiate footage ownership, attribution and shared goals?
9. What coach workflows fit small clubs with limited time?
10. Which metrics stay stable across camera positions and opponents for longitudinal claims?
11. What pricing fits low-frequency use without pressuring more recording?
12. Does any workflow improve delayed learning beyond usual practice?

**Governing decision rule (from the research):** build what helps people *understand, verify, enjoy, or act on* their own play; defer what mainly makes the product look sophisticated or keeps people returning without a sporting reason.
