# 05c — Screens: Progress, Social, Share, Settings, Help

**Scope:** Progress, Personal bests, Shot Explorer, My story, Explore (challenges), the Focus and Reflection flows, Together (singles friends → doubles pair), Share (dialog and public page), Settings & Privacy Centre, Help, Feedback — plus the **navigation-flow table for the six core journeys** and the **consolidated state-coverage matrix** for all three screen files.
**Depends on:** `00` (D1–D18), `05a`/`05b` (shared rules: state vocabulary §0.1, depth §0.2, preset §0.3, `PreviewTag` §0.4), `06`, `07`, `09`, `10`.

> **The retention layer that is not a trap.** These screens exist so a player can *see themselves over time, keep what they love, share with people they choose, and stay in control* — with no streaks, no ranks, no guilt, and no surprise sharing. Every item either rests on a verified event, a stable metric, or the player's own explicit confirmation.

---

## 0. Availability — read this first

Almost everything in this file needs data that **does not exist yet**: a profile, a cross-match store, consent records, share links, and (for the Together section) doubles. The prototype ships these screens **with demo fixtures** and the real data layer follows (`11`).

| Screen | Availability | Gate |
|---|---|---|
| Progress / Records / Shot Explorer / My story | **Preview** (demo fixtures); real data needs G-02 | Cross-match store, "me" mapping (G-01), metric registry (G-07) |
| Explore (challenges) | **Preview** | G-02 + G-07; Doubles Duo is **Not yet** (G-03) |
| Focus + Reflection | **Preview** | G-30 (preferences/focus store), G-29 (insights) |
| Together (singles friends) | **Not yet** | G-01 profiles, G-05 consent ledger, G-05 share/invite |
| Together (doubles pair) | **Not yet** | + G-03 doubles |
| Share dialog / `/s/$token` | **Fixture-only preview**; existing `clip.mp4` is a raw local export, not consented sharing | G-05 participant approval, redaction and server-enforced links; G-28 audio safety |
| Settings & Privacy Centre | **Preview** (UI + local state) | G-05, G-30, G-05 |
| Help | **Available** as static content | Metric definitions need G-07 |
| Feedback | **Not yet** until intake exists; fixture form may demonstrate it | G-32 |

**Rule for Not-yet screens:** the route shows its purpose and a quiet "Coming later" note. Interactive fixture journeys live only in an explicitly entered sample/demo area with a persistent `DemoBanner`; a real player route must not quietly switch to fictional personal data. No Not-yet screen ever shows real-looking personal data as if it were real.

Canonical gap IDs used here (file 11): **G-01** identity/profile · **G-02** cross-match store · **G-03** doubles · **G-05** consent, sharing and deletion · **G-06** Moment entity · **G-07** metric registry · **G-13** notification delivery · **G-28** export audio safety · **G-29** insight service · **G-30** preferences/focus · **G-32** feedback intake. G-01 also covers the "me" mapping; repeated IDs here refer to the same gap, not new work.

---

## 1. Progress — `/progress`

### Purpose
Answer *"Am I changing?"* **honestly**: against the player's **own comparable history**, with ranges and sample sizes, and with an honest "not enough yet" state. Never an overall score, never a rank.

### Who and when
A player who has played ≥ 2 matches and is curious; an Improve-preset player with a Focus; a returning player who wants a **fresh baseline** without erasing the past.

### Entry points
Bottom bar / SideNav, Home progress signal, Recap NextStepRow, Compare ("see more matches").

### Layout — mobile
```
┌────────────────────────────────┐
│ Progress                [Preview]│
│ Compared with: [Your past self ▾]│  reference picker (self default)
│ Looking at: [Last 6 matches ▾]  │
│ Pick one thing: [Longest rally ▾]│
│ ┌ TrendSmallMultiples ────────┐ │
│ │ • • ─• •──• ◦   n per point │ │  points per match; gaps for missing
│ │ 9 11 8 14 12     range bars │ │
│ └─────────────────────────────┘ │
│ ComparabilityNote: 5 of 6 matches│
│ comparable (1 filmed from another│
│ angle — left out)               │
│ "Your longest rally ranged 8–14 │
│  over 5 matches. Early days —   │
│  not enough to call a trend."   │
│ ── My focus ──                  │
│ FocusCard (if chosen)           │
│ ── Notes on this chart ──       │
│ + Add a note (new racket, break)│
└────────────────────────────────┘
```

### Layout — desktop
Left column: pickers (reference · window · metric) and notes. Centre: `TrendSmallMultiples` (2–4 small multiples at once in Advanced). Right: `FocusCard` + `StatusLadder` and milestones for the selected metric. Model-version breaks drawn as vertical lines.

### Components used
`ProgressCard`, `TrendSmallMultiples`, `ComparabilityNote`, `FocusCard`, `StatusLadder`, `PersonalBestCard` (link), `CheckChip`, `MetricPopover`, `PreviewTag`, `NotEnoughToSay`, `EmptyState`, `BaselineNote`.

### Data in
| UI field | Source |
|---|---|
| Per-match metric values | per-session `Analytics` (existing) → cross-match series needs **G-02**; metric definition and `n` need **G-07** |
| Available metrics (v1) | `longest_rally_shots`, `avg_rally_shots`, rallies of 6+ shots (from `rally_end.payload.n_shots`), shot types spotted (Preview), zone coverage (Preview), shuttle-in-play time (`active_play_s`), matches played (participation, not a streak) |
| Comparability | match type (G-04), coverage (`scene`/`analysed`), court fit (`Calibration`), "me" mapping (G-01), definition version (G-07) |
| Annotations | new — G-02 (equipment, opponent level, break/injury/return, model-version break) |
| Reference picker | **My past self (default) · A similar group · An expert example · Nothing** — the second and third are **Not yet** |
| Focus + ladder | new — G-30 |

### Rules (D6, D7, D10)
- **Comparable matches only** (05b §6 rules) — singles vs singles, scored vs scored; a match that isn't comparable is drawn faded with the reason, not silently dropped.
- **Points per match with ranges and `n`**, optional rolling mean with the window stated; missing matches are **gaps**, never zero; no smoothing "to look authoritative"; no gauges.
- **Minimum evidence:** 0–1 comparable matches → baseline note (no chart); 2 → two-point view only (no line); ≥ 3 → line with ranges. The word **"trend"** is used only at ≥ 5 comparable matches *and* when the interval excludes noise by the rule in 06; otherwise "early days".
- **Language:** "changed after", "associated with" — never "caused by this drill", never "improved by X %".
- **Status ladder per Focus:** **Reviewed → Practised → Shown in later play.** A step is reached only by an explicit action or a verified later event; watching a clip never marks a skill mastered.
- **After a break** (≥ 21 days): *"Welcome back. Start a fresh baseline?"* creates a new baseline segment; the past stays visible, **no regression alarm**.
- A player picks the process metric; **no overall score exists**.

### Copy
- **Title:** "Progress". **Tag:** "Preview — based on matches we could compare."
- **Empty (0–1 matches):** "Your first match is your starting point. After a few more, you'll see how your game moves — in your own terms."
- **Not comparable:** "Left out: filmed from another angle, so spatial numbers aren't comparable."
- **Result sentences:** "Your longest rally ranged 8–14 shots over 5 comparable matches. That's early days — not enough to call a trend."
- **Break:** "It's been a while — welcome back. Resume with one match; we can start a fresh baseline whenever you like."
- **Banned:** "You're improving!" on two points; "regressing"; "streak"; "level".

### Interactions
Metric/window/reference pickers; point tap → that match's Recap (`?f=` to the rally); **Add a note** (annotation); **Start a fresh baseline** (non-destructive, undoable); **Hide metrics I don't care about**.

### States
| State | Behaviour |
|---|---|
| loading | Chart skeleton |
| empty | 0–1 comparable matches (above) |
| partial | A processing match shown as a hollow point |
| complete | Normal |
| low-coverage | Low-coverage matches faded with reason |
| failed | `FailedState` for the chart; other cards still show |
| permission | n/a |
| offline | Cached series; "last updated" |
| demo | Fixture series, `DemoBanner` |

### Depth / Preset behaviour
Quick: one metric, one sentence. Guided: picker + note + Focus. Advanced: small multiples (up to 4), distributions, annotation layers, version breaks, exports. **Relax** hides the screen from the home signal unless ≥ 3 comparable matches; **Improve** opens on the Focus metric; **Compete** opens on a multi-metric view.

### Accessibility
Each chart has a one-sentence summary and an accessible table (match, date, value, n, range); points differ by **shape** as well as colour; keyboard focus moves point-to-point with a live-region description.

### Telemetry
`progress_viewed`, `comparison_opened`, `metric_selected`, `baseline_started`, `annotation_added`, `report_comprehension` (sampled teach-back), `resume_after_lapse`.

### Acceptance criteria
- **AC-progress-1** With fewer than two comparable matches, no trend chart is drawn.
- **AC-progress-2** Every point shows its sample size; missing matches are gaps, not zeros.
- **AC-progress-3** No overall score, rank, streak or "improvement %" appears.
- **AC-progress-4** After a ≥ 21-day gap the copy offers a fresh baseline with no regression language.
- **AC-progress-5** The status ladder cannot skip a step.
- **AC-progress-6** Non-comparable matches are shown faded with the reason.

---

## 2. Personal bests — `/progress/records`

### Purpose
Celebrate **real, defined, verified** bests — the player's own, under stable definitions — and never rank incomparable matches against each other.

### Who and when
A player who just saw "a new personal best" and wants to relive it; an Explore-preset player collecting their story.

### Entry points
Progress, Recap (a restrained acknowledgement on a verified best), My story, Home.

### Layout — mobile
```
┌────────────────────────────────┐
│ Personal bests         [Preview]│
│ [All][Rallies][Shots][Matches] │
│ ┌ PersonalBestCard ───────────┐│
│ │ Longest rally in a match    ││
│ │ 14 shots · Thu 23 Oct       ││
│ │ [Checked] ▶ Watch  ▸ Details││
│ └─────────────────────────────┘│
│ ┌ PersonalBestCard ───────────┐│
│ │ Most shot types spotted     ││
│ │ 7 types · Preview           ││
└────────────────────────────────┘
```
Desktop: card grid with a detail drawer showing definition, source match, replay, conditions and the **history of the record** (previous holders: "was 11 shots on 2 Oct").

### Components used
`PersonalBestCard`, `FirstBadge`, `EvidenceChip`, `CheckChip`, `MetricPopover`, `PreviewTag`, `ComparabilityNote`, `EmptyState`.

### Data in
| UI field | Source |
|---|---|
| Record value + source match | max of the metric across comparable matches (G-02/G-07); the underlying rally from `rally_end.payload.n_shots` and its clip (`Highlight.frame_start/frame_end`) |
| Check state | `band` + `status` of the source event |
| Definition, conditions | G-07 (name, definition version, supported setups) |
| Replay | `clip.mp4` / `?f=` deep link (existing) |

### Records catalogue (each with an exact definition in 06)
| Record | Scope | Label |
|---|---|---|
| Longest rally in a match | shots, verified rally boundaries | Preview until amateur-footage validation; a personal best additionally needs checked event evidence and comparable history |
| Rallies of 6+ shots in a match | count | Available |
| Most shot types spotted in a match | distinct types with ≥ 3 verified examples | Preview |
| Longest defensive sequence (from the back, kept alive) | shots | Preview |
| Closest net exchange | shots in a net rally | Preview |
| Most matches in a month | participation, only if the player enables it | optional |

### Rules
- A record needs a **stable definition**, a **reliable source event** (never `provisional`), and **enough history to know the baseline**: the first match sets a **starting point**, not a record.
- **No cross-setup records:** a record is scoped to its conditions (camera setup, match type); incompatible matches don't compete.
- **Corrections propagate:** if a fix invalidates a record, the card says *"This changed because you fixed rally 22"* via `ChangeSummaryBanner`; the previous best is restored visibly.
- **No auto-escalated next target**; no "beat this!" nudges.
- **Restrained acknowledgement** for a verified new best: a quiet ring on the card and one line. **No confetti**, no sound; tied to a verified personal best, never to winning.

### Copy
- **Title:** "Personal bests". **Card:** "Your longest rally in a match — 14 shots."
- **First match:** "This is your starting point. Your next matches can build on it."
- **Preview note:** "Shot-based bests are a Preview."
- **Never:** "Champion", "King/Queen", "Elite".

### Interactions
Tap card → drawer; **Watch** opens the clip; **History** shows previous values with dates; **This doesn't look right** → `FixSheet`; **Hide this record** (autonomy).

### States
| State | Behaviour |
|---|---|
| loading | Card skeletons |
| empty | "Your first match sets your starting point." |
| partial | Provisional values excluded and noted |
| complete | Normal |
| low-coverage | Records from low-coverage matches marked "Worth a look" and excluded from the headline |
| failed | `FailedState` |
| permission / offline | Cached cards |
| demo | `DemoBanner` |

### Depth / Preset behaviour
Quick: 3 cards. Guided: all + definition. Advanced: + conditions, version, event ids, history table. **Explore** highlights Records at the top of Recap; **Relax** shows only the latest verified.

### Accessibility
Cards are headings + definition lists; acknowledgement ring has a text equivalent; no motion-only celebration.

### Telemetry
`records_viewed`, `record_opened`, `record_history_opened`, `record_hidden`, `label_corrected`.

### Acceptance criteria
- **AC-records-1** The first match never claims a record.
- **AC-records-2** Every record shows its exact definition, source match and replay.
- **AC-records-3** A correction that invalidates a record updates it and explains why.
- **AC-records-4** No record is derived from a provisional or incompatible match.
- **AC-records-5** No confetti or sound accompanies a record.

---

## 3. Shot Explorer — `/progress/shots`

### Purpose
The **across-matches** view of which shots the player has been *spotted* playing — a tool for curiosity, not a skill rating. **Observed ≠ mastered.**

### Who and when
An Explore-preset player; anyone who enjoys "I hadn't noticed I played that shot".

### Layout — mobile / desktop
```
┌────────────────────────────────┐
│ Shots I've been spotted playing│
│ [Preview ◔]                    │
│ ── Serves ──                   │
│ Short serve ✓ first Thu 2 Oct  │
│ Long serve  ✓                  │
│ ── Attack ──                   │
│ Smash ✓ · Drop ✓              │
│ ── Net ──                      │
│ Net shot ✓ · Cross-court –     │
│ Tap a shot: first spotted,     │
│ latest example, "I can do this"│
└────────────────────────────────┘
```
Desktop: family-grouped grid; right drawer for the selected shot (first spotted clip, most recent verified example, matches where it appeared, counts with `n`).

### Components used
`ShotRepertoireGrid`, `FirstBadge`, `EvidenceChip`, `CheckChip`, `FixSheet`, `PreviewTag`, `MetricPopover`, `NotEnoughToSay`.

### Data in
| UI field | Source |
|---|---|
| Spotted shot types over time | per-session `PlayerStats.strokes` aggregated (G-02); stroke events with `band`/`status` |
| First spotted date/clip | earliest verified stroke event of the type in the player's history |
| Most recent verified example | latest stroke event, band ≥ `confirmed` or `human_verified` |
| Counts | across matches, with n and unclear excluded |
| Self-report "I can do this shot" | new — G-30 (explicit, separate from detection) |

### Rules
- **Two separate facts:** *Spotted in video* (system, with evidence) and *I can do this* (player's own tick). Never merged; never "mastered".
- A **First** needs ≥ 3 verified examples *or* one Checked example, otherwise "Spotted once".
- A wrong label → **This label looks wrong** (`FixSheet`); the Shot Explorer recomputes.

### Copy
- **Title:** "Shots I've been spotted playing" + `Preview`. 
- **Tag:** "We're still learning to tell shots apart on phone footage. Check the examples."
- **Card:** "Cross-court net shot — first spotted 12 Oct. Seen in 3 matches."
- **Self-report:** "I can do this ✓ (your own note)".
- **Never:** "Unlocked", "Mastered", "Level".

### Interactions
Tap a shot → drawer; **Watch** first/latest example; **I can do this** toggle (private); **This label looks wrong**; **Hide a shot I don't care about**.

### States
| State | Behaviour |
|---|---|
| loading | Grid skeleton |
| empty | "We haven't been able to classify shots yet — they'll show up as we spot them." |
| partial / complete | Normal |
| low-coverage | "Most shots in your recent matches were too far from the camera to classify." |
| failed | `FailedState` |
| permission / offline / demo | As above |

### Depth / Preset behaviour
Quick: grid only. Guided: drawer + examples. Advanced: per-match counts, bands as words, sequence stats. **Explore** shows it prominently; **Compete** hides self-report.

### Accessibility
Grid is a table (`Shot · Spotted · First · Latest`); ✓ plus word; clips have text.

### Telemetry
`shot_explorer_viewed`, `shot_opened`, `self_report_toggled`, `label_corrected`.

### Acceptance criteria
- **AC-shotx-1** "Spotted" and "I can do this" are separate and never combined into a mastery claim.
- **AC-shotx-2** A First requires the evidence rule.
- **AC-shotx-3** The screen carries `PreviewTag`.
- **AC-shotx-4** Every example has "This label looks wrong".

---

## 4. My story — `/progress/story`

### Purpose
A personal **timeline of verified milestones and saved memories** — a growing sports story, not a points ledger. The "Personal Highlight Identity": the player's own signature moments.

### Who and when
A player who wants to relive their season, or a player who just wants to keep moments and ignore numbers.

### Layout — mobile
```
┌────────────────────────────────┐
│ My story                       │
│ Rally Explorer · since Sept    │  a quiet descriptor the player can edit
│ ── October ──                  │
│ ● Longest rally so far: 14 shots│  MilestoneCard
│   ▶ Watch   Checked            │
│ ● First cross-court net shot   │
│   spotted ▶                    │
│ ● You added a note: "new grip" │
│ ── September ──                │
│ ● Your first saved moment      │
│ ● Your first match             │
│ Favourite moments  ▸           │
└────────────────────────────────┘
```
Desktop: vertical timeline left, favourite-moments grid right; a "My top five" collection the player curates.

### Components used
`JourneyTimeline`, `MilestoneCard`, `FirstBadge`, `PersonalBestCard`, `MomentStrip`, `EvidenceChip`, `CheckChip`, `ReflectionPrompt` (optional note), `EmptyState`.

### Data in
| UI field | Source |
|---|---|
| Milestones | derived events (G-02): first match, first saved moment, first Checked rally, first verified shot type, personal bests, first approved share |
| Moments | `Moment` store (G-06) |
| Notes | player-written (G-30) |

### Rules
- **Each milestone needs** a verifiable event, a stable metric, or an explicit player confirmation. **Nothing is invented** to fill the timeline.
- **No inactivity rendering:** gaps in time are simply blank; no "you missed…", no streak counters. A *welcome back* entry appears **only if the player opted in** to participation milestones.
- Milestone types: *First match · First saved moment · First Checked rally · First spotted shot (per type, Preview) · Personal best · First approved share · Returned after a break (opt-in) · Player note.*
- **Story export** (optional): a shareable card built via `SharePreviewDialog`; consent-gated.

### Copy
- **Title:** "My story". **Empty:** "Your badminton story starts with your first match."
- **Welcome back (opt-in):** "Welcome back — your first match since August."
- **Never:** "Level 3", "Streak", "You've lost your progress".

### Interactions
Tap milestone → its Recap/clip; **Add a note** to any milestone; **Pin to favourites**; **Hide a milestone** (autonomy; undo); **Edit my descriptor**.

### States
| State | Behaviour |
|---|---|
| loading | Timeline skeleton |
| empty | Message above |
| partial | Provisional milestones not shown |
| complete | Normal |
| low-coverage | Milestones from low-coverage matches are marked "Worth a look" or withheld |
| failed | `FailedState` |
| permission / offline / demo | As above |

### Depth / Preset behaviour
Quick/Relax: moments + firsts only. Guided/Explore: + personal bests. Advanced/Compete: + definitions and event links. 

### Accessibility
Timeline is a list grouped by month headings; each milestone has a clear heading and action; no time-based animation.

### Telemetry
`story_viewed`, `milestone_opened`, `milestone_hidden`, `note_added`, `story_exported`.

### Acceptance criteria
- **AC-story-j-1** Every milestone links to its evidence or states "your own note".
- **AC-story-j-2** No gap in time is labelled or coloured as absence.
- **AC-story-j-3** A returning player is welcomed only if they opted into participation milestones.
- **AC-story-j-4** A milestone can be hidden and restored.

---

## 5. Explore (optional challenges) — `/explore`

### Purpose
Offer **small, optional, achievable** things to try that fit natural play — "something to be curious about", not obligations. The player chooses the *mode* and can switch it off completely.

### Who and when
An Explore-preset player; an Improve player looking for variety; **never** shown unprompted to a Relax-preset player.

### Entry points
SideNav "Explore", Home Explore card, Recap NextStepRow "Try something next".

### Modes
- **Relax** — no challenges at all (default for Relax preset).
- **Explore** — personal milestones only.
- **Friendly competition** — head-to-head with *a named friend who consents* (**Not yet**, G-01/G-05).

### Layout — mobile
```
┌────────────────────────────────┐
│ Explore            Mode: Explore▾│
│ ┌ ChallengeCard ──────────────┐ │
│ │ Rally Explorer              │ │
│ │ Beat your own longest rally │ │
│ │ (14 shots). No rush.        │ │
│ │ Evidence: Available ✓       │ │
│ │ [Try it] [Not now] [Never]  │ │
│ └─────────────────────────────┘ │
│ ┌ Shot Explorer (Preview) ────┐ │
│ │ Spot a shot type you haven't│ │
│ └─────────────────────────────┘ │
│ Paused all challenges ▢ [Pause]│
└────────────────────────────────┘
```
Desktop: card list with an "Active (max 2)" rail and "Done" collapsed.

### Challenge catalogue
| Challenge | Goal (player-facing) | Evidence needed | Availability |
|---|---|---|---|
| **Rally Explorer** | Keep a rally alive for a new personal-best length | Rally segmentation + verified rally | **Available** |
| **Shot Explorer** | Spot a shot type you haven't been spotted playing | Stroke classification | **Preview** |
| **Court Explorer** | Play in more areas of the court | Court fit Good + zone presence | **Preview** |
| **Doubles Duo** | A rally both partners contribute to | Doubles + attribution | **Not yet** (G-03) |
| **Just Showed Up** | Celebrate completing a match you chose to play | Session detected | **Available** (participation only; no penalty) |
| **Personal Best** | Exceed your own earlier result on a metric you pick | Stable metric + history | **Preview** |
| **Calm Review** | Look at your match later, or not at all | — | **Available** |

### Components used
`ChallengeCard`, `ChallengeModePicker`, `FirstBadge`, `PersonalBestCard`, `PreviewTag`, `EmptyState`.

### Data in
Challenge definitions (static config), eligibility from metric availability (G-07), progress from per-match `Analytics` + cross-match store (G-02). Mode, paused, dismissed lists — G-30.

### Rules
- **Opt-in, dismissible, pauseable**, max **2 active**; "Never show this" is remembered.
- **No auto-escalation** of difficulty after a success; no unsafe or unnatural-play challenges (never "play through pain", never strenuous, no age-based assumptions).
- **A challenge never requires changing how you play.** Copy: *"Just play — we'll notice if it happens."*
- **Completion** = a restrained acknowledgement + a link to the evidence. No points, no XP.
- **Rewards recognise participation and personal bests**, not absolute performance.

### Copy
- **Title:** "Explore". **Intro:** "Small things you might enjoy trying. Ignore them any time."
- **Rally Explorer:** "Beat your own longest rally (14 shots). No rush — just play."
- **Completed:** "You kept a rally alive for 16 shots — your new longest. Watch it."
- **Paused:** "Challenges are paused. You can turn them on whenever you like."
- **Never:** "Don't break your streak", "Only 2 days left".

### Interactions
**Try it / Not now / Never**; **Pause all**; switch mode (confirm what changes); progress is passive (the system checks after matches).

### States
| State | Behaviour |
|---|---|
| loading | Skeletons |
| empty | "No challenges right now. Explore will suggest small ones after a few matches." |
| partial / complete | Normal |
| low-coverage | Challenges requiring unavailable evidence are hidden with an explanation |
| failed | `FailedState` |
| permission / offline / demo | As above |

### Depth / Preset behaviour
**Relax:** screen shows only the mode picker and "Just showed up"/"Calm review". **Explore:** full list. **Improve:** challenges linked to the Focus. **Compete:** hidden by default.

### Accessibility
Cards are actionable lists; buttons ≥ 44 px; progress is textual ("3 of 5 rallies longer than 10 shots") not just a bar.

### Telemetry
`challenge_viewed`, `challenge_accepted`, `challenge_dismissed` (reason), `challenges_paused`, `challenge_completed`, `harm_signal`.

### Acceptance criteria
- **AC-explore-1** A Relax-preset player sees no active challenges unless they switch mode.
- **AC-explore-2** No challenge uses points, streaks or countdowns.
- **AC-explore-3** Dismissing "Never" persists.
- **AC-explore-4** A challenge never auto-increases difficulty.
- **AC-explore-5** Not-yet challenges (Doubles Duo) are shown as "Coming later", not as active.

---

## 6. Focus and Reflection flows (the "Practice bridge")

> There is **no `/practice` route** in `00 §5`. The Practice loop lives as a **Focus sheet** reachable from the Recap, Home and Progress, and as a **"My focus" section of `/progress`**. No separate top-level navigation item.

### Purpose
Turn *one* supported pattern into **one editable, feasible experiment**, with a plan the player writes in their own words, and a respectful review rule. Reflection comes *before* the reveal.

### Who and when
An Improve-preset player (or anyone who taps "Try something next"). Never forced; "Done" is a success state.

### Entry points
Recap InsightCard "Try this", NextStepRow, Home FocusCard, Progress.

### Flow
1. **Offer.** An *Opportunity* `InsightCard` shows evidence (clips, n/denominator, coverage) and a suggested focus: *"Reset to the middle after a back-court shot."* Actions: **Accept · Edit · Not now**. (A claim with no evidence or low support is **never** converted into a drill.)
2. **Make it yours.** `FocusSheet`: editable **title**; **reason** ("I chose this because…", pre-filled, editable); **linked clips**; **cue-action sentence** ("At the start of my next match I will …"); **success cue** ("I'll notice …", external-focus wording by default, coach may override); **review rule** ("I'll look at this after my next 3 matches" — event-based, not a daily timer); **optional reminder** (user-set time, opt-in).
3. **Practice** (off-app). The product stays silent. No push unless the player set a reminder.
4. **Reflect before the reveal.** After the next match: `ReflectionPrompt` — *"What changed?"* (one question, skippable) **before** showing any metric.
5. **Reveal & ladder.** Show the evidence; the `StatusLadder` moves only on explicit action: **Reviewed → Practised → Shown in later play**.
6. **Close.** Actions: *Continue · Modify · Replace · Pause · Retire.* One active default Focus; more are opt-in.

### Barrier check (if planned practice didn't happen)
*"What got in the way?"* — **I didn't understand the task · No court or partner · No time · It isn't a priority now** → offer: a clearer explanation, an alternative, rescheduling, or letting it go. Reminders cannot create court access.

### Layout — FocusSheet (mobile)
```
┌────────────────────────────────┐
│ Your focus                     │
│ Reset to the middle after a    │
│ back-court shot            ✎   │
│ I chose this because  ✎        │
│ "Several of my long rallies    │
│  ended after I stayed back."   │
│ Examples: [▶][▶][▶]            │
│ At my next match I will…  ✎    │
│ Look at this after: [3 matches]│
│ ○ Reviewed ○ Practised ○ Shown │  StatusLadder
│ [Save focus]  Not now  Ask coach│
└────────────────────────────────┘
```

### Components used
`FocusCard`, `FocusSheet`, `StatusLadder`, `ReflectionPrompt`, `InsightCard`, `EvidenceChip`, `CheckChip`, `NotEnoughToSay`.

### Data in
| UI field | Source |
|---|---|
| Opportunity claim, evidence, n, coverage | new — G-29 (`claim`, `claim_type`, `evidence_refs`, `sample_size`, `coverage`, `limitations`) |
| Focus store, ladder, reminders | new — G-30 |
| Linked clips | `Highlight`/rally frames (existing) via `?f=` |

### Copy
- **Offer:** "If this fits your goal, you could try: **reset to the middle after a back-court shot.** It showed up in 6 of 9 long rallies (Worth a look). **Watch 3 examples.**"
- **Plan:** "At the start of my next match I will …"
- **Reflection:** "What changed?" (skippable) / "Does this fit what you noticed?"
- **Barrier:** "What got in the way? That's useful to know — no judgement."
- **Never:** "You must practise this next", drills prescribed from uncertain evidence, unsafe physical changes.

### Rules
Process goals, not outcome goals ("reset to the middle", not "win more rallies"). Offer a **coach-confirmation** option. No training load or dose is prescribed from video alone. Reflection is **A/B-testable** against no prompt (burden vs calibration).

### States
| State | Behaviour |
|---|---|
| loading | Sheet skeleton |
| empty | No focus: "Nothing to practise right now. That's fine." |
| partial | Provisional claims never offered |
| complete | Normal |
| low-coverage | No Opportunity offered; "Not enough to say" |
| failed | Save failure keeps input |
| permission / offline / demo | As above |

### Depth / Preset behaviour
**Relax:** never shown unless asked. **Improve:** slot 2 on Home. **Compete:** hypotheses list (several candidate explanations with a next question each, per Blueprint §9.4).

### Accessibility
All fields are labelled; reflection is a single question with a "Skip" button of equal size; focus order top→bottom; no timers.

### Telemetry
`practice_focus_chosen`, `focus_edited`, `focus_retired`, `reflection_answered/skipped`, `barrier_selected`, `ladder_advanced`.

### Acceptance criteria
- **AC-focus-1** A Focus cannot be offered without resolvable evidence and a stated sample.
- **AC-focus-2** Every Focus is editable, postponable and retirable without penalty.
- **AC-focus-3** The ladder advances only by explicit action or a verified later event.
- **AC-focus-4** Reflection appears *before* the metric and can be skipped.
- **AC-focus-5** Missing practice triggers the barrier check, not a guilt message.

---

## 7. Together — `/together`, `/together/$partnerId`  *(Not yet)*

> **Availability: Not yet.** v1 = **friends playing singles** (needs G-01/G-05); v2 = **doubles pair** (adds G-03). The screen is designed now; the prototype renders it from fixtures.

### Purpose
Celebrate **shared memories** — best rallies together, joint milestones, approved clips — **without blame** and **without exposing anyone's private stats**. "Pair memory" is the shared unit; individual and pair data are always visually and structurally distinct.

### Who and when
Regular playing partners / friends; a doubles pair (later). Most valuable right after a shared match.

### Layout — `/together` (mobile)
```
┌────────────────────────────────┐
│ Together                [Not yet]│
│ People you play with           │
│ ┌ PartnerCard ────────────────┐│
│ │ ◔ Rahul · 6 matches together││
│ │ 3 shared moments            ││
│ └─────────────────────────────┘│
│ Invite someone                 │
│ [ Copy invite link ]           │
│ How sharing works ▸            │
└────────────────────────────────┘
```

### Layout — `/together/$partnerId`
```
┌────────────────────────────────┐
│ ← Together   Rahul             │
│ Shared with you both (private) │
│ ── Pair timeline ──            │
│ ● Best shared rally · 16 shots │
│ ● First match together         │
│ Approved moments  [▶][▶]       │
│ Pair records (when enough data)│
│ Permissions ▸  Unlink ▸        │
└────────────────────────────────┘
```
Desktop: timeline left; right: approved moments, pair records, permissions panel.

### Components used
`PartnerCard`, `PairMemoryCard`, `PairTimeline`, `InviteLink`, `ConsentRow`, `UnlinkDialog`, `SharePreviewDialog`, `PersonalBestCard`, `EmptyState`, `PermissionRevokedState`.

### Data in
All new: partner entities, invitations, shared-moment approvals, pair records — G-01, G-05, G-06, G-05 (+ G-03 for doubles roles).

### Consent model (see `10`)
- A Pair memory exists **only after both people accept an invitation**.
- Each person has **their own four permissions** (analyse · keep · share · train); a shared item appears in the pair view only when **each** person marked it shareable.
- **Individual stats are never visible to a partner**; pair views show *pair* facts only ("both of you contributed to this rally").
- **Unlink** stops future sharing; items the partner already has remain with them (stated plainly); the unlinking person's items become tombstones for the other person.
- A bystander appearing in a clip suppresses it from sharing unless approved (privacy policy).

### Rules
- **No blame:** pair analytics never assign a lost point to one partner; "partner rescue" is a *sequence event*, not intent.
- **Doubles surfaces** (rotation, coverage, coordinated attack) are **Not yet** and, when shipped, are confidence-rated *observations*, not facts.
- Pair trends only when a sample rule is met (06), otherwise "Not enough shared matches yet".
- **Friendly rivalry** (singles) is opt-in and never shown as a leaderboard.

### Copy
- **Title:** "Together". **Not-yet note:** "Pair memories are coming later. Here's how they'll work."
- **Invite:** "Invite {name} to keep your shared moments. They'll choose what to share too."
- **Pair fact:** "You both contributed to this 16-shot rally."
- **Unlink dialog:** "Stop sharing with Rahul? You'll both keep what's already been shared. Future moments won't appear for either of you."
- **Never:** "Rahul lost this point", "weaker partner".

### Interactions
Invite link (copy/WhatsApp share via OS share sheet), accept/decline invites, approve moments for the pair, unlink, remove one moment.

### States
| State | Behaviour |
|---|---|
| loading | Skeletons |
| empty | "Playing with someone? Invite them to keep your moments together." |
| partial | Pending invites shown as "Waiting for Rahul" |
| complete | Normal |
| low-coverage | n/a |
| failed | `FailedState` |
| permission | `PermissionRevokedState` ("Rahul stopped sharing") |
| offline | Cached view |
| demo | `DemoBanner`; fixtures |

### Depth / Preset behaviour
Quick/Relax: moments only. Guided: + pair records. Advanced: + sequence definitions and evidence. **Compete** may show pair tactical sequences (Not yet).

### Accessibility
Consent rows are switches with descriptive labels; unlink uses an accessible dialog with focus return; partner names are always text, never colour-only.

### Telemetry
`together_viewed`, `invite_created`, `invite_accepted`, `pair_moment_approved`, `unlinked`, `access_revoked`, `harm_signal`.

### Acceptance criteria
- **AC-together-1** No partner can see another person's individual statistics.
- **AC-together-2** A pair moment requires both approvals.
- **AC-together-3** Unlink states what remains with each person.
- **AC-together-4** No copy assigns blame to a partner.
- **AC-together-5** The screen is labelled Not yet until G-01/G-05 ship.

---

## 8. Share — `SharePreviewDialog` and `/s/$token`

### 8.1 SharePreviewDialog

**Purpose:** a **three-question, no-surprise** dialog — *What am I sharing? With whom? For how long?* — and a truthful preview. Default is **private**; nothing is shared by an accident.

**Who and when:** a player who tapped ⤴ Share on a Moment, Recap, Story card or Pair memory.

**Entry points:** HeroMoment, MomentCard, Clip detail, Moments library (multi-select), Recap NextStepRow, My story export, Together.

**Layout — mobile (bottom sheet) / desktop (centred dialog):**
```
┌ Share this moment ──────────────┐
│ ┌ preview (what they'll see) ─┐ │
│ │ ▶ 14-shot rally · 0:18      │ │
│ └─────────────────────────────┘ │
│ Included                        │
│  ☑ Video   ☐ Score  ☐ My name   │
│  ☐ Stats (never by default)     │
│ Who can see it                  │
│  ○ Only me                      │
│  ● Anyone with the link (7 days)│
│  ○ Save to my phone (no link)   │
│ People in this clip: you, Rahul │
│  ⚠ Rahul hasn't approved       │
│ Download allowed ☐             │
│ You can stop sharing any time.  │
│ Copies already downloaded can't │
│ be taken back.                  │
│ [ Cancel ]   [ Create link ]    │
└─────────────────────────────────┘
```

**Components used:** `SharePreviewDialog`, `ShareAudiencePicker`, `ConsentRow`, `ClipPlayer` (preview), `ActiveLinksList` (in Settings), `PreviewTag`.

**Data in:** the `Moment` (G-06); clip file `GET …/exports/clip.mp4?from&to` (existing raw export; gated for player download by G-05/G-28); link creation `POST /api/…/share` — new (G-05: token, audience, expiry, download flag, redactions); participant approvals (G-05).

**Rules:**
- **Default audience = Only me.** The dialog never pre-selects a public link.
- **Show exactly** what is included: footage, whether score/stats/names appear, identifiable people, recipients/access, expiry, download permission, how to revoke and what can't be recalled.
- **Strip by default:** hidden analytics and the score are **off**; the player opts them in.
- **Consent gates:** funny/embarrassing moments need **explicit per-clip approval** (a separate tick); an opponent/partner in the clip who hasn't approved → warning and a *"Blur / trim / share only me"* option (blur where feasible); **sharing a clip never changes the analysis or training consent** (copy states this).
- **Save to phone** is a local-copy choice only after the player sees who appears, hears any audio, and the G-05/G-28 export gate passes. It is never described as permission to forward the file. In fixture demos it is simulated.
- Link default expiry **7 days**; options 24 h / 7 d / 30 d / never (never requires an extra confirm).

**Copy:**
- **Title:** "Share this moment". **Subline:** "Sharing doesn't change your analysis or model-training settings."
- **Warning:** "Rahul is in this clip and hasn't said yes. Share only with yourself, or ask Rahul?"
- **Success (truthful):** "Link created. It stops working on {date}." / demo: "Demo action — no link was created."
- **Never:** public link pre-selected; "Share to everyone!"; shame-based social prompts.

**Interactions:** change inclusions/audience/expiry; **Create link** → copy / OS share sheet (WhatsApp etc.); **Stop sharing** in the confirmation and later in Settings → Privacy → Active links.

**States:** loading (preview generating) · empty (n/a) · partial (clip not yet rendered → "Preparing your clip") · complete · low-coverage (provisional moment → "Worth a look — share anyway?") · failed (link failed → nothing created, say so) · permission (a missing approval blocks) · offline (disabled except save-to-phone if clip cached) · demo (no link created).

**Depth / Preset:** Quick: 3 controls. Guided/Advanced: + redactions, download, per-person approvals, copy of audit line.

**Accessibility:** dialog with focus trap and return; radio group for audience with descriptions; warnings are text + icon; the preview has a text description.

**Telemetry:** `share_previewed`, `share_initiated` (audience type only — **never recipient identity**), `share_blocked` (reason), `access_revoked`, `save_to_phone`.

**Acceptance criteria:**
- **AC-share-1** The default audience is "Only me".
- **AC-share-2** The dialog lists exactly what will be visible, including people and score/stat inclusion.
- **AC-share-3** A funny/embarrassing clip cannot be shared without a separate per-clip approval.
- **AC-share-4** A missing partner/opponent approval produces a visible warning and a safe alternative.
- **AC-share-5** Success messages are truthful; demo actions say so.
- **AC-share-6** No link is created in demo mode.

### 8.2 Shared page — `/s/$token`

**Purpose:** a minimal, respectful page for *a recipient who may never use Rally*: watch the moment, see who shared it, and leave. **No analytics, no account wall.**

**Who and when:** a friend opening a WhatsApp link; also the sender previewing "what they'll see".

**Layout (mobile; desktop centres a 560 px column):**
```
┌────────────────────────────────┐
│ ◔ Rally                        │
│ ┌── player (muted, captions) ─┐│
│ └─────────────────────────────┘│
│ A 14-shot rally                │
│ Shared by Ana · 23 Oct         │
│ This link works until 30 Oct.  │
│ Make your own ▸    ⚑ Report    │
└────────────────────────────────┘
```
**Components:** `SharedMomentPage`, `ClipPlayer`, `PermissionRevokedState`, `DemoBanner`, `FailedState`.

**Data in:** `GET /api/s/{token}` — new (G-05): clip stream (signed, expiring), title, sender's chosen display name (if allowed), expiry, download flag, redactions applied.

**Rules:** `noindex`; no download unless the sender allowed it; no stats unless the sender included them; bystander/opponent **report** button; **no tracking of recipient identity**; footer CTA must not be pushy.

**Copy:** *Expired:* "This link has expired. Ask {name} to share it again." *Revoked:* "{name} stopped sharing this." *Not found:* "This link isn't valid."

**States:** loading · complete · expired · revoked (`PermissionRevokedState`) · failed (clip unavailable) · offline · demo.

**Telemetry:** `shared_page_viewed` (audience type), `shared_page_reported`, `make_your_own_clicked`.

**Acceptance criteria:**
- **AC-s-1** The page works with no account and no JavaScript-required sign-in.
- **AC-s-2** Expired and revoked links show distinct, kind messages.
- **AC-s-3** The page is `noindex` and never exposes stats unless included by the sender.
- **AC-s-4** Download is available only when allowed.
- **AC-s-5** A report control is always present.

---

## 9. Settings & Privacy Centre — `/settings` (+ `/settings/profile`, `/preferences`, `/privacy`, `/data`, `/notifications`, `/accessibility`)

### Purpose
Give the player **real control** — over how Rally looks and speaks, who can see what, what is kept, and how to leave — in plain language, with consequences explained *before* a change.

### Who and when
Any player; most visits are short ("turn that off", "delete this match"), some are anxious ("what's stored?").

### Entry points
AvatarMenu, Recap "Shown because you chose… Change", Share dialog, Help, notification settings link, onboarding "You can change this later".

### Layout — mobile (index) / desktop (two-pane)
```
┌────────────────────────────────┐
│ Settings                       │
│ Profile                      ▸ │
│ How Rally shows things       ▸ │  Preferences
│ Privacy & sharing            ▸ │
│ Notifications                ▸ │
│ Accessibility                ▸ │
│ My data (export · delete)    ▸ │
│ Help & feedback              ▸ │
└────────────────────────────────┘
```
Desktop: left list, right panel; each panel ends with a "What changes if I…?" note.

### 9.1 Profile — `/settings/profile`
**Fields:** nickname (editable anywhere; used in recaps), optional avatar (only if supported), **preferred play mode** (singles · doubles · both; preference does not imply analysis support), **self-described level** (new · casual · regular · competitive · coach/other — optional, used for *wording*, never as a rank), **language**. **Not asked:** age, health, dominant hand (only if a validated analysis needs it — none today), gender. **Data:** new (G-01).

### 9.2 Preferences — `/settings/preferences`
| Control | Options | Effect |
|---|---|---|
| **Preset** | Relax · Explore · Improve · Compete | Bundles Purpose + Depth (D3); shown as "Shown because you chose …" with **Change · Reset · Show all** |
| **Purpose** (up to two) | Keep my moments · Understand my game · Choose something to practise · Prepare to compete · Discuss with someone · Just play | Orders and emphasises content |
| **Depth** (default) | Quick · Guided · Advanced | Density and language; editable per match |
| **Tone** | **Direct · Balanced · Coach-guided** | **Wording and ordering only; same evidence and limits** in all three |
| **Recap length** | Short · Standard | |
| **Home modules** | toggles for Focus, Progress signal, Explore | Reorders/hides; never hides consent or evidence |
| **Challenge suggestions** | On/Off | Off removes Explore cards |
| **Social memories** | On/Off | Together prompts |
| **Entry choice default** | Ask me · Quick recap · Deep review · Review later | See 05a §7.3 |
| **Units** | Metric (default) | Distance is Not yet |

"**Show all**" overrides every hide with one tap. A line explains: *"These settings change order, wording and detail — never the facts."* Data: G-30.

### 9.3 Privacy & sharing — `/settings/privacy` (the **Privacy Centre**)
Layout:
```
Your permissions
 ConsentRow  Analyse my videos           On  (required to use Rally)   ▸
 ConsentRow  Keep my videos              On                             ▸
 ConsentRow  Save my stats to my history On                             ▸
 ConsentRow  Share selected moments      Off by default                 ▸
 ConsentRow  Help improve the models     Off  (separate, never bundled) ▸
Each row: what it means · what changes if you turn it off · date changed · policy version
Sharing
 Active links (ActiveLinksList): moment · audience · expires · [Stop sharing]
 What can't be recalled: copies already downloaded or sent
People
 Coach/partner access (Not yet) · Revoke
Retention
 Video kept for: [30 days ▾] · Derived stats: kept until you delete
```
**Rules:** five separate decisions (analyse · keep media · save history · share · improve models) + per-clip share approvals; **model-improvement is off by default and separate**; every switch shows **what changes now** vs **what needs a background job**; revoking *share* blocks future shares immediately and offers to **stop active links**; analysis consent is required for processing (turning it off stops new analyses; existing results stay until deleted).
**Data:** consent ledger (G-05: `purpose`, `status`, `captured_at`, `policy_version`, `revoked_at`); active links (G-05); retention (G-05).
**Copy:** *"Private by default. Analysing a video doesn't mean sharing it or using it to train anything."*; *"Turning this off stops new matches being analysed. Your past results stay until you delete them."*

### 9.4 Notifications — `/settings/notifications`
Per-trigger switches, **all off until the player has a reason** (no permission prompt before then); each with quiet hours, a frequency cap and *digest* option; **Pause all** and one-tap unsubscribe.
| Trigger | Default | Notes |
|---|---|---|
| Your match is ready | Offered at upload ("Notify me") | Delivers what was requested; no urgency |
| A time *you* set to review or practise | Off | User sets time; snooze/disable; no guilt after a miss |
| There's enough comparable evidence to revisit your Focus | Off (separate opt-in) | Explains why it's noteworthy; never for noise |
| Coach comment / review request | Off | **Not yet** |
| Inactivity | **None, ever by default** | Not offered as a toggle |
Data: G-30/G-13. Copy: *"Your review is ready. Start with the moments you saved whenever you want."* No "come back", countdown, rank-drop or streak messages exist.

### 9.5 Accessibility — `/settings/accessibility`
Reduced motion · text size (up to 200 %) · high contrast · caption defaults for clips · lower-bandwidth preview (labelled "preview quality" — does not imply lower analysis quality) · shortcut list · "Describe clips in text" (always on for screen readers). Follows OS preferences by default. Data: G-30.

### 9.6 My data — `/settings/data`
Layout: **Export my data** (request → status → download), **Delete a match**, **Delete everything** (typed confirmation), **Clear sample data**, **Corrections I've made** (list with undo, from the event log), **Metric definitions** (link to `/help/metrics`), **Pause my account** (stop analysing; keep history), **Switch to "Keep my moments" mode** (stop analytics, keep clips).
**Rules:** irreversible actions need confirmation that states **what is removed** (match, derived clips, embeddings and exports under our control) and **what can't be** (backups for a stated period; copies others already hold). Leaving is **two clear steps**, no guilt screens. Demo mode: *"Request simulated"* — never claims real deletion.
**Data:** `DELETE /api/sessions/{id}` (existing, deletes analysis and corrections; video stays in cache — **the copy must say so or the cache policy must change**, flagged G-05); export/delete jobs (G-05).

### Components used (Settings)
`ConsentLedger`, `ConsentRow`, `ConsentToggle`, `ActiveLinksList`, `NotificationPrefs`, `PauseAllToggle`, `ToneSelector`, `PresetCards`, `PurposeChips`, `DepthSwitcher`, `AccessibilityPrefs`, `DataExportRequest`, `DeleteConfirmDialog`, `EmptyState`, `PreviewTag`.

### Interactions
Changes apply immediately with an inline confirmation ("Saved") and, where relevant, a *what changes* line; destructive actions use `DeleteConfirmDialog`; a change that affects others (revoking a share) lists them.

### States
| State | Behaviour |
|---|---|
| loading | Skeleton |
| empty | n/a |
| partial | Deletion/export job "In progress" with status |
| complete | Normal |
| low-coverage | n/a |
| failed | Save failure keeps the control in its previous state with a message |
| permission | Coach/partner items show who and what they can see |
| offline | Changes queued or blocked with a reason |
| demo | "Request simulated" on export/delete |

### Depth / Preset behaviour
Quick: preferences and privacy in plain language. Advanced: + metric definitions, corrections log, model-reuse details, retention specifics.

### Accessibility
Settings are standard forms; each switch has a visible label and description; focus returns to the invoking control; errors are associated with fields.

### Telemetry
`settings_viewed`, `privacy_changed` (which, not value of anything sensitive), `preset_changed`, `purpose_selected`, `tone_changed`, `reminder_enabled`, `reminder_paused`, `data_exported`, `deletion_requested`, `access_revoked`.

### Acceptance criteria
- **AC-settings-1** Model-improvement consent is separate, off by default, and never required.
- **AC-settings-2** Every permission states what changes immediately and what needs a job.
- **AC-settings-3** Changing Tone changes wording/order only; evidence and limits are identical.
- **AC-settings-4** No notification permission is requested without a reason; no inactivity notification exists.
- **AC-settings-5** Delete states actual originals, derived media, cache and backup retention; it never says "deleted" while media remains in cache. The control is gated on G-05 server deletion jobs.
- **AC-settings-6** Demo export/delete says "simulated".
- **AC-settings-7** "Show all" restores everything personalisation has hidden.

---

## 10. Help — `/help`, `/help/$topic`

### Purpose
Make the product's limits and logic **understandable** in plain language — where to look when a metric is missing, a label looks wrong, or the player wants to know how film a better clip.

### Who and when
A confused or skeptical player; a coach; someone about to upload and worried about footage.

### Layout
```
┌────────────────────────────────┐
│ Help                [search ⌕] │
│ Getting started                │
│  • How to film your match      │  → Record guide
│  • What Rally can and can't do │
│ Understanding your results     │
│  • How we read a match         │
│  • Checked · Looks right · Worth a look │
│  • Why a number is missing     │
│  • What "Preview" means        │
│  • Metric definitions          │  → /help/metrics
│ Fixing things                  │
│  • How to fix a rally          │
│  • Place your court            │
│ Privacy & sharing              │
│ Troubleshooting                │
│ Contact / report an issue ▸    │
└────────────────────────────────┘
```

### Topics (each a short article with a "Was this helpful?" and a link to the relevant screen)
1. **How analysis works** — video → court → players → shuttle → rallies → moments; what is deterministic; where uncertainty comes from.
2. **Why some numbers are missing** — not enough of the court visible; other camera; low light; shuttle hidden; what to do.
3. **How "Checked / Looks right / Worth a look" works** — plain explanation of D5 (no percentages; coverage separate).
4. **What "Preview" means** — capability labels (Available/Preview/Not yet) and the list.
5. **How to film** (Record guide) — where to place the phone (behind or high behind the baseline, whole court and both players in frame, steady, good light), singles vs doubles caveats, test clip.
6. **How to fix a rally** — Review & fix, undo, what re-scoring means.
7. **How privacy and sharing work** — four permissions, links, what can't be recalled.
8. **Metric definitions** (`/help/metrics`) — one entry per registry metric: plain definition, numerator/denominator, time window, exclusions, minimum sample, supported conditions, version history, known limits. (Data: G-07.)
9. **Troubleshooting** — court not found, match stuck, upload interrupted, clip won't play.

### Components used
`HelpArticle`, `MetricPopover` (deep-linked), `EmptyState`, `Breadcrumb`, `PreviewTag`.

### Data in
Static content; metric definitions from the registry (G-07). `MetricPopover` links to `/help/metrics#<metricId>`.

### Copy
Plain, short, no jargon; each article opens with *"In short:"* and ends with *"If this didn't answer it, tell us."*

### Interactions
Search; breadcrumbs; "Was this helpful?" (👍/👎 + optional comment); contextual **Help** links from any state (e.g. Low-coverage → "Why some numbers are missing").

### States
loading (skeleton) · empty search ("No help for that yet — tell us what you were looking for") · failed (static fallback) · offline (cached) · demo (n/a).

### Depth / Preset behaviour
Not applicable; **Advanced** shows extra "Technical details" blocks in articles.

### Accessibility
Headings in order, descriptive link text, article skip link, 200 % text reflow, searchable by keyboard.

### Telemetry
`help_opened` (topic), `help_search`, `help_helpful`, `metric_definition_opened`.

### Acceptance criteria
- **AC-help-1** Every metric in the product has an entry in `/help/metrics`.
- **AC-help-2** Each low-coverage or missing-number state links to the matching article.
- **AC-help-3** The filming guide includes a test-clip tip and singles/doubles caveats.
- **AC-help-4** Help is reachable from every screen in ≤ 2 actions.

---

## 11. Feedback and report-an-issue — `/feedback`

### Purpose
Let the player say **"this is wrong"**, **"this made me uncomfortable"** or **"this is confusing"** in two taps, and give them an honest confirmation.

### Who and when
Anyone, from a `RecapFeedback` thumbs-down, a Fix sheet, a Share dialog, or Help.

### Layout
```
┌────────────────────────────────┐
│ Tell us what happened          │
│ ○ Something looks wrong        │
│ ○ Wrong player / wrong shot    │
│ ○ A moment I didn't want kept  │
│ ○ A number is confusing        │
│ ○ A privacy concern            │
│ ○ This made me uncomfortable   │
│ ○ Something else               │
│ Anything to add? (optional)    │
│ ☑ Include this match & moment  │  (context, only with a tick)
│ [ Send ]                       │
└────────────────────────────────┘
```

### Components used
`FeedbackForm`, `FixSheet` (link for corrections), `EmptyState`, `PreviewTag`.

### Data in / out
`POST /api/feedback` — new (G-32): `type`, `text?`, `context? {matchId, frame, screen}`, returns `reference_id?`. **Corrections** (wrong winner, official, match start) already have real endpoints and are **not** funnelled through feedback.

### Rules
- **Honest confirmation:** show a reference number **only if the backend returns one**; otherwise "Thanks — we'll read this." Never promise a fix.
- **Privacy concern** and **uncomfortable** types are priority-routed, link to **Settings → Privacy** and **Share → stop sharing**, and emit `harm_signal`.
- Context (match/frame) is attached **only with the player's tick**; never raw video.
- No forced free text.

### Copy
- **Title:** "Tell us what happened". **Sent:** "Thanks. We'll read this." / with ref: "Thanks. Reference {id}."
- **Privacy concern:** "If a moment shouldn't be shared, you can stop it now: **Stop sharing**."

### States
loading · complete · failed (keep text; retry) · offline (queued: "Will send when you're back online") · demo ("Demo action — nothing was sent").

### Depth / Preset behaviour
Not applicable.

### Accessibility
Radio group with legend, labelled textarea, confirmation in an `aria-live` region.

### Telemetry
`feedback_submitted` (type only), `harm_signal`, `feedback_context_attached`.

### Acceptance criteria
- **AC-feedback-1** The form takes two taps to send.
- **AC-feedback-2** No promise of a fix; reference shown only when real.
- **AC-feedback-3** Privacy/uncomfortable types offer the immediate stop-sharing path.
- **AC-feedback-4** Context is attached only with consent.

---

## 12. Navigation-flow table — the six core journeys

| # | Journey | Steps (routes) | Success | Failure / branch handled |
|---|---|---|---|---|
| **A** | **Casual player wants a great clip** | `/` Home continue card → `/matches/$id` Recap (EntryChoice → Quick) → HeroMoment **Watch this** → `/moments/$clipId` → **Save** or **Share** (dialog or *Save to phone*) → back to Recap | Sees a relevant moment in ≤ 3 interactions; keeps it private or shares intentionally | No verified moment → manual pick; low coverage → still real moments; share blocked by missing approval → safe alternative |
| **B** | **"Am I improving?"** | `/` → `/progress` → pick metric → ComparabilityNote → point → `/matches/$id?f=` evidence → read explanation → optional **Focus** (FocusSheet) | Understands the comparison **and its limits** | < 2 comparable matches → baseline note; non-comparable → faded + reason; gap → fresh baseline |
| **C** | **Doubles pair wants shared memories** *(Not yet)* | `/matches` → doubles match Recap ③ **Together** → `/together/$partnerId` → approve moment → **Share** to pair | Pair celebrated without blame or privacy leak | One partner hasn't consented → warning + safe option; unlink → tombstones |
| **D** | **Competitive player wants tactical detail** | `/` (Compete) → **Resume investigation** → `/matches/$id/deep-dive/rallies` (filters) → RallyDetailPanel sequence → **Advanced** `?view=table` → **Export** | Finds a filtered sequence with evidence and exports it | Preview shot labels visible; coverage panel; `Needs a look` filter |
| **E** | **User finds an incorrect event** | Any clip/rally → **Fix this** → `FixSheet` → (winner/official/start via API; wrong player/shot via feedback) → `ChangeSummaryBanner` → **Undo** or **See what changed** | Corrects without contacting support; sees the downstream change | Offline → queued; unsupported correction type → feedback with honest message |
| **F** | **User wants privacy control** | AvatarMenu → `/settings/privacy` → open a permission row → read *what changes* → switch / **Stop sharing** → `/settings/data` → **Export** or **Delete** | Understands what is stored, what changed now, what needs a job | Demo → "simulated"; irreversible → confirm with explicit scope; backups noted |

**Global navigation rules**
- Back preserves filters and scroll; Clip → Deep dive → **Return to analysis**.
- Filters sync to the URL; `?f=<frame>` works on every match route.
- Every empty state offers one next step; every error offers a feasible next action (never only "Try again").
- The mode/preset/depth switch updates **density and order only**.
- Every page has a route back to its parent (Match → Matches; Moment → Match/Library).

---

## 13. Consolidated state-coverage matrix (all screens in 05a, 05b, 05c)

Legend: **✓** designed · **–** not applicable · **N** screen is *Not yet* (state designed, rendered from fixtures).

| Screen | loading | empty | partial | complete | low-cov | failed | permission | offline | demo |
|---|---|---|---|---|---|---|---|---|---|
| Landing | ✓ | – | – | ✓ | – | ✓ | – | ✓ | ✓ |
| Sample recap | ✓ | – | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Home | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Matches | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| New match | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Processing | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| **Recap** | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Moments (match) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Moments (all) | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ |
| Clip detail | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Deep dive shell | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Story | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Rallies | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Shots | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Court | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Compare | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Ask | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Review & fix | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Place your court | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Advanced workspace | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Quality panel | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Progress | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Personal bests | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Shot Explorer | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| My story | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Explore | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Focus + Reflection | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Together (list / partner) | N | N | N | N | – | N | N | N | N |
| Share dialog | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Shared page `/s/$token` | ✓ | – | – | ✓ | – | ✓ | ✓ | ✓ | ✓ |
| Settings (all panes) | ✓ | – | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ |
| Help | ✓ | ✓ | – | ✓ | – | ✓ | – | ✓ | – |
| Feedback | ✓ | – | – | ✓ | – | ✓ | – | ✓ | ✓ |

---

## 14. Gaps referenced (proposed IDs; `11` is authoritative)

| Gap | Used here for |
|---|---|
| G-01 | Profile, nickname, "me" mapping and partner identity |
| G-03 | Doubles (Together v2, Doubles Duo) |
| G-02 | Cross-match store: Progress, Records, Shot Explorer, My story, Explore |
| G-05 | Consent ledger, participant approvals, share links/invites, data export/deletion jobs and media-cache deletion semantics |
| G-06 | `Moment` entity (library, favourites, visibility) |
| G-07 | Metric registry (definitions, versions, n, denominators) |
| G-29 | Insight service (claims with evidence) for Focus offers |
| G-30 | Preferences, focus store, notification settings |
| G-13 | Notification delivery |
| G-32 | Feedback intake with reference IDs |
| G-28 | Audio stripping/redaction for exported or shared clips |

## 15. Components named here that are not in `00 §6`

`FocusSheet`, `StatusLadder`, `MilestoneCard`, `BaselineNote`, `ChallengeModePicker`, `ActiveLinksList`, `ConsentRow`, `PauseAllToggle`, `ToneSelector`, `HelpArticle`, `FeedbackForm`, `SharedMomentPage`, `PairTimeline`, `UnlinkDialog`. Add to Doc 07. (`ShareAudiencePicker`, `PairMemoryCard`, `PartnerCard`, `InviteLink`, `ConsentLedger`, `ConsentToggle`, `NotificationPrefs`, `DataExportRequest`, `DeleteConfirmDialog`, `AccessibilityPrefs`, `FocusCard`, `ReflectionPrompt`, `ChallengeCard`, `PersonalBestCard`, `FirstBadge`, `JourneyTimeline`, `ProgressCard`, `TrendSmallMultiples`, `ComparabilityNote` are in `00 §6`.)

## 16. Contradictions with `00` found while writing

- `00 §5` has **no Focus/Practice route**; this file embeds Focus as a sheet and a section of `/progress` (consistent with the route map, but Doc 04 must record it).
- `00 §5` lists settings sub-pages as `/profile`, `/preferences`, … under "`/settings` +"; this file uses `/settings/profile` etc. Doc 04 should confirm.
- `00 §5` includes `/help/$topic`; this file adds **`/help/metrics`** as a topic (metric definitions) — no new route, but 06 must supply the registry content.
- `00 §7` marks "Personal bests, firsts, progress, journey" as **Preview with demo fixtures**; this file applies that and additionally marks **Together** as **Not yet** even for singles friends, because profiles, consent and invites don't exist.
