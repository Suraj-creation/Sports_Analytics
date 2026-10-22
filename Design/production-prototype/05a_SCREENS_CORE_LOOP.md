# 05a — Screens: The Core Loop

**Scope:** Landing, Sample recap, Home, Matches, New match, Processing, **Match Recap**, Moments (per match and all), Clip detail.
**Depends on:** `00` (decisions D1–D18, vocabulary, routes, component names) · `01` (behaviour model) · `06` (metric definitions) · `07` (component anatomy) · `09` (copy).
**Sister files:** `05b` (Deep dive, Review & fix, Place your court) · `05c` (Progress, Social, Settings).

> The core loop is: **Add a match → see what we could follow → watch your best moment → understand one thing (optionally) → save or share what you choose → leave.** Everything on these screens is judged against the question *"Did the player get something they value in under a minute, without being graded?"*

---

## 0. Shared rules for every screen in this file

### 0.1 State vocabulary (used in every "States" table)

| State | Meaning | Component |
|---|---|---|
| **loading** | Waiting for data; layout is known | `LoadingSkeleton` shaped like the real layout (never a spinner on a blank page) |
| **empty** | No data exists yet (not an error) | `EmptyState` with one next step |
| **partial** | Some stages/rallies analysed, rest pending or skipped | `PartialAnalysisNote` + whatever is usable |
| **complete** | All requested stages finished | — |
| **low-coverage** | Analysed, but we followed too little to say much | `LowCoverageState` (preserve valid moments) |
| **failed** | Pipeline failed; may be retryable | `FailedState` (cause, what was saved, next step) |
| **permission** | Access revoked / not allowed | `PermissionRevokedState` |
| **offline** | Server unreachable / socket down | `OfflineState` (the existing "Reconnecting" chip generalised) |
| **demo** | Fixture data | `DemoBanner` ("Sample data — not a real match") + `PreviewTag` where relevant |

### 0.2 Depth behaviour (default meaning; overridden per screen)

| Depth | Language | Density | Evidence access |
|---|---|---|---|
| **Quick** | Short sentences, no jargon, no metric tables | Airy; large clips; ≤ 3 facts | One tap ("Watch this") |
| **Guided** (default for Explore/Improve) | Plain with inline definitions | Moments + one strength + one optional opportunity | One tap, definition one more |
| **Advanced** | Full terminology; definitions on demand | Compact tables, filters, coverage | Direct from table rows |

Depth changes **order, wording and density — never the facts or the evidence standard** (00 §1). A visible line *"Shown because you chose Quick — Change · Reset · Show all"* appears wherever depth hides something.

### 0.3 Preset behaviour (default meaning; overridden per screen)

| Preset | Reorders / emphasises | Hides by default |
|---|---|---|
| **Relax** (default) | Moments first, short story, saving and sharing | Metrics, focus, challenges, opportunity cards |
| **Explore** | Moments + "firsts" + personal bests + shot spotting | Opportunity cards, tactical views |
| **Improve** | Moments + one strength + one *editable* Focus | Compare-to-others, tactical filters |
| **Compete** | Rally sequences, score-state filters, deeper tables | Celebration-style copy |

### 0.4 `PreviewTag` rules (D10)

A `PreviewTag` is attached to **any surface that depends on a Preview capability** (00 §7): shot types, placement, relative court presence, scoreline *until Checked*, anything calibration-gated. The tag is a word + icon ("Preview ◔"), opens a short explanation ("Works with limits. Here's what to double-check."), and is never colour-only. A surface that depends on a **Not yet** capability is not rendered; a quiet one-line note may say what will appear later.

### 0.5 Data-source shorthand

`Session` / `Analytics` / `PlayerStats` / `Highlight` / `BaiEvent` / `Calibration` / `ScenePayload` / `MatchState` / `StatusMsg` / `AskAnswer` are the types in `apps/web/src/lib/types.ts`. API paths are the existing ones: `GET /api/sessions`, `GET /api/sessions/{id}`, `GET …/analytics`, `GET …/highlights?k&player`, `GET …/heatmap`, `GET …/events`, `GET …/state`, `GET …/exports/clip.mp4?from&to`, `POST …/corrections`, `POST …/calibration`, `POST …/calibration/auto`. **`new — see G-xx`** marks a field or endpoint that does not exist yet; gap IDs are proposed here and finalised in `11`.

Gap IDs in this file are the canonical IDs from `11_DATA_CONTRACTS_AND_BACKEND_GAPS.md` (this file's early draft IDs were remapped): **G-01** identity/profile and *which one is you* · **G-02** cross-match store · **G-03** doubles · **G-04** free-play match type · **G-05** consent, share links, retention, export/deletion · **G-06** Moment entity · **G-07** metric registry · **G-12** stages API / draft / resumable upload · **G-13** notifications · **G-14/G-15** correction undo, change summary, extra kinds · **G-18** amateur highlight ranker · **G-20** coverage API / court-fit in plain language · **G-29** insight service · **G-30** preferences and focus store · **G-31** Moment thumbnails / poster frames · **G-32** feedback intake with reference IDs. Fixture needs are in `12` §4.

---

## 1. Landing — `/welcome`

### Purpose
Let a visitor decide in under a minute whether this is for them, what it needs, and what it cannot do — **by showing, not claiming**. No account, no camera permission, no autoplay sound.

### Who and when
First-time visitor (referred by a friend's shared moment, a club WhatsApp group, a search). Skeptical or curious. Often on a phone. May be a returning user who bookmarked it (they skip straight to sign-in).

### Entry points
Direct URL, `/s/$token` footer ("Make your own"), referral link, sign-out. A signed-in user hitting `/welcome` sees a "Go to your matches" button in the hero.

### Layout — mobile (360)
```
┌────────────────────────────────┐
│ ◔ Rally                  Sign in│  (AvatarMenu absent)
├────────────────────────────────┤
│ Your best rally,               │
│ without scrubbing a video.     │  H1 (question-led, plain)
│ Upload a match. Get your       │
│ moments, your game, a next step│
│ — or just the moments.         │
│ [ See a 20-second example ]    │  primary
│ Upload my match                │  secondary (text)
├────────────────────────────────┤
│ ▶ Sample moment (poster)       │  ValueHero media; tap to play,
│   "14-shot rally · Sample"     │  muted, captions on
├────────────────────────────────┤
│ What would you like today?     │  PurposePicker (read-only teaser)
│ [Keep my moments]              │  each chip opens a different
│ [Understand my game]           │  tab of the sample recap
│ [Choose something to practise] │
│ [Prepare to compete]           │
│ [Discuss with someone]         │
├────────────────────────────────┤
│ How it works                   │
│ ① Record  ② Upload  ③ Check    │
│ what we saw  ④ Choose what     │
│ to do — or nothing             │
├────────────────────────────────┤
│ Inspect a sample report ▸      │
├────────────────────────────────┤
│ What we can and can't do yet   │  capability table (Available /
│ [expand]                       │  Preview / Not yet)
├────────────────────────────────┤
│ Private by default             │
│ Analyse · Keep · Share · Train │  four separate switches shown
├────────────────────────────────┤
│ What it costs & needs          │
│ FAQ · Recording guide · Privacy│
└────────────────────────────────┘
```

### Layout — desktop (1280)
```
┌───────────────────────────────────────────────────────────────────────────┐
│ ◔ Rally     How it works  Sample  What we can do  Privacy  Pricing  Sign in│
├───────────────────────────────────────┬───────────────────────────────────┤
│ Your best rally, without scrubbing    │ ┌───────────────────────────────┐ │
│ a video.                              │ │ ▶  Sample moment (muted)      │ │
│ Upload a match. Get your moments,     │ │    14-shot rally · Sample data│ │
│ your game and an optional next step.  │ └───────────────────────────────┘ │
│ [See a 20-second example]  Upload     │   caption: "Real-looking sample.  │
│                                       │   Every number opens its clip."   │
├───────────────────────────────────────┴───────────────────────────────────┤
│ What would you like today?  [Keep moments][Understand][Practise][Compete]… │
│ ┌ interactive 20-second example (SampleRecapEmbed) ─────────────────────┐ │
│ │ tab content changes with the chosen purpose — see §1.5                │ │
│ └───────────────────────────────────────────────────────────────────────┘ │
├──────────────┬──────────────┬──────────────┬──────────────────────────────┤
│ Record       │ Upload       │ Check        │ Choose                       │
├──────────────┴──────────────┴──────────────┴──────────────────────────────┤
│ Inspectable sample report ▸    │ What we can and can't do yet (table)     │
├────────────────────────────────┴──────────────────────────────────────────┤
│ Private by default (4 permissions)  │  Cost & equipment  │  FAQ           │
└───────────────────────────────────────────────────────────────────────────┘
```

### Components used
`ValueHero`, `SampleRecapEmbed`, `PurposePicker` (teaser mode), `PresetCards` (not on landing), `PreviewTag`, `DemoBanner`, `ClipPlayer` (sample), `CheckChip`, `EvidenceChip`, `FramingChecklist` (teaser), `ConsentCards` (read-only four-permission strip), `EmptyState` (none), `Breadcrumb` (none).

### Data in
All **demo fixtures** (new — see file 12 §4): a 40-rally singles sample, its highlight list, one deliberately *uncertain* rally, one Fixed correction. Shape = the real `Analytics` + `Highlight[]` + `BaiEvent[]` so the same components render real data later. No API call is required; static JSON bundled with the app.

### Copy
- **H1:** "Your best rally, without scrubbing a video."
- **Sub:** "Upload a match. Get your moments, how your game looked, and an optional next step. Or keep just the moments."
- **Primary CTA:** "See a 20-second example". **Secondary:** "Upload my match".
- **Capability intro:** "Here's what we can and can't do yet." Rows: *Rallies and moments — Available · Shot types — Preview · Where your shots land — Preview · Distance run — Not yet · Doubles — Not yet.*
- **Never:** "AI coach", "become elite", fabricated testimonials, invented user counts.

### Interactions
1. **See a 20-second example** scrolls to / opens `SampleRecapEmbed` (no navigation, no data entry).
2. A **purpose chip** switches the embed to the matching view: *Keep my moments* → HeroMoment + MomentStrip; *Understand my game* → FactTrio + `ScoreStory`; *Practise* → InsightCard (one strength, one opportunity) + FocusCard preview; *Compete* → mini rally timeline + filter chips; *Discuss with someone* → annotated moment + "share with a coach" preview.
3. **Inspect a sample report** opens `/welcome/sample` (§2).
4. Any embedded **Watch this** plays the sample clip (muted, captioned). **Fix this** in the embed opens the real `FixSheet` in demo mode ("Demo action — nothing is saved").
5. **Upload my match** → `/start` (§ in 03).

### States
| State | Behaviour |
|---|---|
| loading | Static page; media posters render first; embed lazy-loads on scroll |
| empty | n/a |
| partial | n/a |
| complete | Normal |
| low-coverage | n/a |
| failed | If the sample clip fails to load: poster stays, caption "Preview video unavailable — the recap below still works" |
| permission | n/a |
| offline | Page is static and works; "Upload" shows an `OfflineState` toast if the server is unreachable |
| demo | Entire embed is demo; `DemoBanner` is persistent in the embed frame ("Sample data") |

### Depth behaviour
Not applicable (anonymous). The embed uses **Guided** language.

### Preset behaviour
Not applicable. Purpose chips preview what each preset emphasises.

### Accessibility
- Video never autoplays; if the user taps play it is **muted, captioned** and respects `prefers-reduced-motion` (poster only, no looping).
- All purpose chips are `role="tab"` in a `tablist`; arrow keys move between them.
- The capability table is a real `<table>` with `Available/Preview/Not yet` as words + icons.
- 44 px targets; body ≥ 16 px; contrast AA.

### Telemetry
`example_opened`, `purpose_selected` (landing teaser), `sample_report_opened`, `evidence_clip_opened` (sample), `capability_table_opened`, `landing_cta_clicked` (which one), `privacy_summary_opened`.

### Acceptance criteria
- **AC-landing-1** A visitor on a 360 px phone can reach the sample embed with one tap and no input.
- **AC-landing-2** No audio plays unless the user presses play, and then it is muted by default.
- **AC-landing-3** Capability table shows Available/Preview/Not yet using text + icon, not colour alone.
- **AC-landing-4** The embed is labelled "Sample data" at all times and contains no real-user imagery.
- **AC-landing-5** The four permissions (analyse, keep, share, train) are shown as four items; training is shown as *off*.
- **AC-landing-6** No claim of accuracy, popularity or "AI coach" appears anywhere.
- **AC-landing-7** A signed-in user sees "Go to your matches" and is never forced through the pitch.

---

## 2. Sample recap — `/welcome/sample`

### Purpose
The **inspectable** version of the real recap, built from the *same components* (so the user learns the real interface), with visible limits and a working **Fix this**. Proves *expectation comprehension*, not activation (tracked as a separate funnel).

### Who and when
A skeptical evaluator who clicked "Inspect a sample report" or "Explore the sample". Also used by new users from `/start` Step "First value" while their own match processes.

### Entry points
Landing, `/start` (First value), Help ("What does a recap look like?"), empty Home.

### Layout
Identical to **§7 Recap** (mobile + desktop) with three differences: a persistent `DemoBanner` at the top, a **"What this sample shows"** side note on desktop (collapsible on mobile), and a **"This is a sample; real accuracy depends on your recording — see What we can do"** line under the coverage bar.

### Components used
Everything in §7, plus `DemoBanner`, `PreviewTag`, `CoverageBar` (always shown, set to 38/40 rallies), `FixSheet` (demo mode).

### Data in
Demo fixtures (new — see file 12 §4). The fixture includes: one rally with `band: "probable"` ("Worth a look"), one with `status: "corrected"` ("Checked"), a Preview shot-type surface, and a deliberately **withheld** insight with `NotEnoughToSay`, so users see abstention.

### Copy
- **Banner:** "Sample match — made-up players, real-looking results. Nothing here is a measurement of you."
- **Coverage line:** "We followed 38 of 40 rallies. The other 2 were out of view."
- **Withheld card:** "We couldn't tell who won rally 23, so it isn't counted yet. Watch it and tell us."

### Interactions
Same as Recap; destructive/save/share actions say **"Demo action — nothing was saved."** No toasts claim success of a real operation. A closing card offers **Upload my own match** and **Back to the example**.

### States
| State | Behaviour |
|---|---|
| loading | Skeleton of recap |
| empty / partial / low-coverage | Seeded as variants via a "Show me a rough recording" toggle (swaps to a low-coverage fixture) so users see honest degraded states before they upload |
| failed | Fixture failed → "Sample unavailable" with link to landing |
| demo | Always |

### Depth / Preset behaviour
The **DepthSwitcher** and **PresetSwitcher** work in the sample so users feel the difference; the choice is *not* persisted to the profile.

### Accessibility
As Recap. `DemoBanner` is `role="note"`.

### Telemetry
`sample_report_opened`, `finding_opened`, `coverage_opened`, `evidence_clip_opened`, `label_corrected` (demo), `sample_depth_changed`, `sample_exit_to_upload`.

### Acceptance criteria
- **AC-sample-1** Every claim in the sample opens a clip and a definition.
- **AC-sample-2** The sample contains at least one visible uncertainty and one withheld claim.
- **AC-sample-3** "Fix this" works and shows *what changed* via `ChangeSummaryBanner`, labelled demo.
- **AC-sample-4** Switching Depth/Preset changes density and order but not any displayed fact.
- **AC-sample-5** No share action creates a link.

---

## 3. Home — `/`

### Purpose
Orient the player and surface **one** meaningful next action. Continue the sporting loop; never a metric wall, never a global score, never a streak.

### Who and when
Any signed-in player, typically after a game (mobile, tired, a minute of attention) or before the next one (retrieving a Focus).

### Entry points
Sign-in, logo, nav, notification ("Your match is ready"), back from Recap.

### Content by situation (matrix)

| Situation | Primary content | Secondary | Do not show by default |
|---|---|---|---|
| **New, no footage** | `ValueHero` mini + "See a sample" and "Add your first match" | Recording guide link, privacy summary | Empty charts, any score, "Level 1" |
| **Processing** | Honest `ProcessingStages` card with what is already viewable | "Notify me when ready" (opt-in), "Leave safely" note | Fake percentage or countdown |
| **Returning recreational (Relax)** | `HeroMoment` from the latest match + "Watch your moments" | Saved moments strip, "Add another match" | Deficit list, compulsory Focus |
| **Improvement (Improve)** | Latest recap resume + the player's chosen **Focus** | Relevant moments for that Focus, one next opportunity | All metrics, rankings |
| **Competitive (Compete)** | "Resume investigation" (last Deep dive view + filters) | Saved filters, compare pair | A simplified grade that hides coverage |
| **After a break (≥ 21 days)** | "Welcome back — resume with one match" + latest moment | "Start a fresh baseline" option (never an alarm) | Streak or regression language |
| **Failed last match** | `FailedState` card with specific fix and what was saved | Re-upload, report issue | Silence |

### Home hierarchy (top → bottom, per Front-End Blueprint §5.2)
1. **Continue the sporting loop** — one card: *"Review Saturday's match"* / *"Add a match"* / *"Resume with one match"*.
2. **Your Focus** — only if the user chose one (FocusCard, collapsed).
3. **Latest meaningful evidence** — `HeroMoment` or an InsightCard with its clip.
4. **Progress signal** — only if ≥ 3 comparable matches exist (one small card, otherwise absent).
5. **Explore** — collapsed; optional challenge, dismissible.
6. **Recent matches** — 3 `MatchCard`s + "All matches".

### Layout — mobile
```
┌────────────────────────────────┐
│ ◔ Rally                  (avatar)│
├────────────────────────────────┤
│ Good to see you, Ana           │  (no assumptions on first run)
│ ┌────────────────────────────┐ │
│ │ ▶ Review Saturday's match  │ │  primary card (continue loop)
│ │   Your longest rally: 14   │ │
│ │   shots · Looks right      │ │
│ │ [ Watch your moments ]     │ │
│ └────────────────────────────┘ │
│ Your focus (if chosen)         │
│ ▸ Reset to the middle after a  │
│   back-court shot              │
│ Saved moments  ▸               │
│ [▶][▶][▶]                      │
│ Recent matches                 │
│ [MatchCard][MatchCard]         │
├────────────────────────────────┤
│ Home  Matches  ＋  Moments  Progress │ BottomBar
└────────────────────────────────┘
```

### Layout — desktop
```
┌ SideNav ┬────────────────────────────────────────────────────────────────┐
│ Home    │ Good to see you, Ana                    [＋ Add a match]       │
│ Matches ├───────────────────────────────┬────────────────────────────────┤
│ Moments │ ┌ Continue ─────────────────┐ │ Your focus (collapsed)         │
│ Progress│ │ HeroMoment + [Watch]      │ │ Progress signal (if enough)    │
│ Together│ └───────────────────────────┘ │ Explore (collapsed)            │
│ Explore │ Saved moments strip           │                                │
│         │ Recent matches (3 cards)      │                                │
└─────────┴───────────────────────────────┴────────────────────────────────┘
```

### Components used
`AppShell`, `SideNav`, `BottomBar`, `AddMatchButton`, `HeroMoment`, `MomentStrip`, `MatchCard`, `MatchStatusChip`, `ProcessingStages`, `FocusCard`, `ProgressCard`, `ChallengeCard`, `EmptyState`, `FailedState`, `PreviewTag`, `PresetSwitcher` (header), `DemoBanner`.

### Data in
| UI field | Source |
|---|---|
| Latest match + status | `GET /api/sessions` (`Session.status`, `created_at`, `title`, `media.duration_us`, `analysed_frames/media.n_frames`) |
| Hero moment | `GET …/highlights` → first fair-ranked (new ranker — see G-18); clip range from `Highlight.frame_start/frame_end`; poster — new, see G-31 |
| "Looks right" chip | `BaiEvent.band` + `status` of the rally_end (D5 mapping) |
| Focus | new — see G-30/G-02 |
| Progress signal | new — see G-02/G-07 |
| Name, preset | new — see G-01/G-30 |
| Time since last match | derived from `Session.created_at` |

### Copy
- **Greeting:** "Good to see you, {nickname}" (first run: "Welcome to Rally").
- **Continue card (match ready):** "Your match is ready. Start with your moments whenever you like."
- **Continue card (after break):** "Welcome back. Resume with one match — no catching up needed."
- **Empty (new):** "Your badminton story starts with one match. Want to see an example first?"
- **Processing:** "We're reading your match. You can watch it now; shots and rallies fill in as we go."
- **Never:** "You haven't played in X days", "Don't lose your streak", "Level up".

### Interactions
- Continue card primary → `/matches/$matchId` (Recap). Secondary "Review later" snoozes the card for this match until next visit (no reminder).
- Add-a-match (`AddMatchButton`) → `/matches/new` from anywhere.
- Moments strip tile → `/moments/$clipId`.
- Focus card actions: **Edit · Postpone · Retire · Ask coach** (see 05c Focus flows).
- Dismiss on any card persists ("Not useful" reasons: *not relevant · too much · already know*).

### States
| State | Behaviour |
|---|---|
| loading | `LoadingSkeleton` of the six hierarchy slots |
| empty | New-user variant (above) |
| partial | Processing card + whatever moments are already available |
| complete | Normal |
| low-coverage | Continue card says "We could follow part of this match — your moments are ready; the rest is limited." |
| failed | `FailedState` as the primary card |
| permission | Revoked share/consent → card hidden; Settings link |
| offline | `OfflineState` banner; cached cards shown with "last updated" |
| demo | `DemoBanner`; demo matches marked "Sample" on `MatchCard` |

### Depth / Preset behaviour
- **Quick:** hierarchy items 1, 3, 6 only; Progress signal and Explore hidden.
- **Guided:** all items; Focus visible if chosen.
- **Advanced:** adds "Resume investigation" (last Deep dive route + filters) and shows *what we could follow* (coverage) on the latest match card.
- **Relax:** Continue = moments. **Explore:** adds "firsts". **Improve:** Focus is slot 2. **Compete:** "Resume investigation" is slot 1.

### Accessibility
Landmarks: `nav`, `main`, headings H1 (greeting) → H2 per card. Cards are single focusable links, not nested interactive soup. Live region announces "Your match is ready" only when the user is on Home.

### Telemetry
`home_viewed` (with situation), `continue_card_opened`, `moment_opened`, `card_dismissed` (reason), `add_match_clicked`, `resume_after_lapse`.

### Acceptance criteria
- **AC-home-1** A user with no matches sees no numbers about themselves.
- **AC-home-2** A user returning after ≥ 21 days sees no regression, streak or guilt wording.
- **AC-home-3** Exactly one primary action per state.
- **AC-home-4** Progress signal is absent unless ≥ 3 comparable matches exist.
- **AC-home-5** Dismissing a card persists across sessions.
- **AC-home-6** Processing card never shows a fabricated percentage.

---

## 4. Matches — `/matches`

### Purpose
The library: find a match, see its state honestly, start a new one. **Results are context, not a verdict**: no win-rate headline, no ranking.

### Who and when
A player looking for a specific game ("last Thursday with Rahul"), or checking whether an upload finished.

### Entry points
Nav, Home "All matches", after upload.

### Layout — mobile
```
┌────────────────────────────────┐
│ Matches            [Filters (2)]│
│ [All][Matches][Social][Practice]│  type chips
├────────────────────────────────┤
│ ┌ MatchCard ──────────────────┐│
│ │ ▢ poster    Thu · Evening   ││
│ │ vs Rahul · 18:42            ││
│ │ 36 rallies · 14 shots longest││
│ │ [Ready] [Followed 31/36]    ││
│ │ 3 moments saved             ││
│ └─────────────────────────────┘│
│ ┌ MatchCard (processing) ─────┐│
│ │ …Reading your match         ││
│ └─────────────────────────────┘│
│ ┌ MatchCard (sample) ─────────┐│
│ │ SAMPLE ·                    ││
└────────────────────────────────┘
```

### Layout — desktop
Grid of 3–4 `MatchCard`s, filters in a left rail or top `FilterBar` with active-filter chips and count. A "Sample" section is visually separated and collapsible.

### Components used
`MatchCard`, `MatchStatusChip`, `FilterBar`, `FilterSheet` (mobile), `AddMatchButton`, `EmptyState`, `FailedState`, `DemoBanner`, `DeleteConfirmDialog`, `PreviewTag`.

### Data in
| UI field | Source |
|---|---|
| Title, date | `Session.title`, `Session.created_at` |
| Duration | `Session.media.duration_us` |
| Status chip | `Session.status` via `STATUS_LABEL` (rename: *Queued → "Waiting", Preparing video → "Getting your video ready", Ready to play → "Watch now", Analysing → "Reading your match", Analysed → "Ready", Failed → "Needs attention"*) |
| Progress (processing only) | `analysed_frames / media.n_frames` — shown as a bar only because it is **measured**, never as a time estimate |
| Rallies, longest | `Analytics.rallies`, `longest_rally_shots` (per-match fetch, cached) |
| Coverage "Followed 31/36" | derived: analysed rallies / (rallies + unofficial) — new — see G-20 |
| Opponent / partner name | `Session.players[].name` (+ "me" mapping — new, see G-01) |
| Match type | new — see G-04 |
| Saved moments count | new — see G-06 |

### MatchCard states
`Waiting · Getting your video ready · Watch now · Reading your match (bar) · Ready · Ready with limits (coverage < 70 %) · Needs attention · Sample · Deleted (hidden)`. **A failed or low-coverage match is never rendered as zero performance** — it simply shows its state.

### Copy
- **Title:** "Matches". **Empty:** "No matches yet. Upload one, or look at a sample first."
- **Filtered-empty:** "Nothing matches these filters. Clear filters"
- **Delete dialog (existing, reworded):** "Delete this match? This removes the analysis and your fixes for this match. Your saved moments stay unless you remove them too."
- **No** "Won 21–17" in the card headline. If the scoreline is Checked, it appears as a small neutral chip "21–17".

### Interactions
- Filter by **type** (Match/Social/Practice), **date range**, **partner/opponent**, **state** (Ready · Processing · Needs attention), **with coach** (later), **has saved moments**. Filters sync to the URL (`?type=match&state=ready`).
- Sort: newest (default), longest rally, most moments.
- Card: whole-card link; kebab: *Rename · Fix players · Share · Delete*.
- Search by title/opponent (optional for prototype).

### States
| State | Behaviour |
|---|---|
| loading | 6 card skeletons |
| empty | New-user message + sample |
| partial | Mixed processing/ready cards |
| complete | Normal |
| low-coverage | "Ready with limits" chip on card |
| failed | "Needs attention" + one-line cause |
| permission | Shared-with-me matches whose access expired show `PermissionRevokedState` |
| offline | Cached list + `OfflineState` |
| demo | Samples separated, `SAMPLE` chip, not counted in "N matches" |

### Depth / Preset behaviour
- **Quick/Relax:** cards show title, date, status, moments count.
- **Guided/Explore/Improve:** + rallies, longest rally.
- **Advanced/Compete:** + coverage ("Followed 31/36"), scoreline chip, model/calibration quality icon.

### Accessibility
List semantics (`ul/li`); card is one link with a visible focus ring; delete is a button with `aria-label="Delete {title}"` not hover-only (the current opacity-0 pattern must become focus/touch-visible). Status is a word + icon.

### Telemetry
`matches_viewed`, `match_opened`, `filter_applied`, `match_deleted`, `deletion_requested`, `match_renamed`.

### Acceptance criteria
- **AC-matches-1** No card shows win-rate, rank or a colour-coded win/loss.
- **AC-matches-2** Demo/sample matches are visually distinct and excluded from counts.
- **AC-matches-3** Delete requires confirmation and states what is kept.
- **AC-matches-4** Processing bar appears only when `analysed_frames` is reported.
- **AC-matches-5** Filters persist in the URL and survive back navigation.
- **AC-matches-6** Delete control is reachable by keyboard and touch.

---

## 5. New match — `/matches/new`

### Purpose
Get usable footage into the system with **informed consent and minimum friction**: a stepper that is honest about effort and never asks a question before it is needed. (Detailed first-run copy and capture-readiness flows live in `03`; this spec is the screen.)

### Who and when
A player right after a game on a phone, or later at a desktop. Fatigue and impatience are expected.

### Entry points
`AddMatchButton` (everywhere), Home empty state, `/start` final step.

### Steps (single route, state held in the page; each step is back-able without loss)

| # | Step | Question | Skippable? |
|---|---|---|---|
| 1 | **Source** | "Where is the video?" Upload file · Import from YouTube (feature-flagged) · Use a sample | — |
| 2 | **Type** | "What kind of game was it?" **Match** (scored) · **Social game** (rallies, no score) · **Practice** (drills) | Default: Social game |
| 3 | **Who's who** | `PickYourself` + `WhoIsWho`: tap yourself on a frame; name the other side | Names optional; "me" required for personalised recap |
| 4 | **Your court** | `PlaceYourCourt`: auto-detect → one-tap confirm; manual only on failure | Auto-accepted if quality gate passes |
| 5 | **Permissions** | `ConsentCards`: Analyse (required) · Keep video (default on, optional) · Share (off) · Train (off) | Only Analyse is required |
| 6 | **Go** | Summary + "Start analysing" | — |

### Layout — mobile (step 2 shown)
```
┌────────────────────────────────┐
│ ← New match            2 of 6  │
│ ●●○○○○                         │
│ What kind of game was it?      │
│ ┌────────────────────────────┐ │
│ │ ○ Match   Scored to 21      │ │
│ │   We'll follow the score.   │ │
│ ├────────────────────────────┤ │
│ │ ● Social game  Just rallies │ │
│ │   No score. Best for fun.   │ │
│ ├────────────────────────────┤ │
│ │ ○ Practice  Drills, feeding │ │
│ └────────────────────────────┘ │
│ You can change this later.     │
│ [ Continue ]        Back       │
└────────────────────────────────┘
```

### Layout — desktop
Two columns: left = step content; right = **live preview** (video frame with court overlay once available, or the recording-guide diagram before upload), plus a "What happens next" box ("Reading usually takes about as long as the video; you can watch while it runs" — only if measured rate is known, else omitted).

### Components used
`MatchTypePicker`, `RecordGuide`, `FramingChecklist`, `TestClipCheck`, `SuitabilityResult`, `UploadProgress`, `PickYourself`, `WhoIsWho`, `PlaceYourCourt`, `ConsentCards`, `ConsentToggle`, `PurposeChips`, `PreviewTag`, `FailedState`, `UnsupportedFootageState`.

### Data in
| UI field | Source |
|---|---|
| Upload limit text | `GET /api/system` → `limits.max_upload_mb` (existing) |
| Create session | `POST /api/sessions` (multipart: `file`, `title`, `player1`, `player2`) — existing; type & "me" mapping are **new — see G-04, G-01** |
| YouTube import | `POST /api/sessions/youtube` (`url`, `player1`, `player2`, `acknowledge_rights`) — existing; enabled by `system.youtube_ingest` |
| Court proposal | `GET …/calibration/proposal`, `POST …/calibration/auto`, `POST …/calibration` — existing |
| Test-clip suitability | new — see G-20 (runs auto-calibration + player detection on ~5 s and returns Suitable / Usable with limits / Not supported + reasons) |
| Consent | new — see G-05 |

### Copy
- **Step 1:** "Add a match. Upload a clip, or try a sample. Nothing is shared with anyone."
- **Suitability:** *Suitable* "We can see the whole court and both players." · *Usable with limits* "We can follow rallies, but shots and placement will be limited because …" · *Not supported* "We can't find the court in this clip because it's cropped at the top. Here's how to film it ↗" (**never just "Try again"**).
- **Consent:** "Private by default. Analysing a video doesn't mean sharing it or using it to train anything."
- **Rights (YouTube):** keep the existing acknowledgement, reworded: "I'm allowed to use this video."
- **Never:** a single "I have everyone's consent" checkbox; a notification-permission prompt.

### Interactions
- Upload: drag-drop or file chooser; resumable transfer; progress is **measured** (`XHR upload` progress) and labelled "Sending 62 %"; a distinct later phase "Checking your video"; **Cancel** at any time.
- On selecting a file, run the **TestClipCheck** automatically on the first ~5 seconds after transfer (when available) and show *Suitable / Usable with limits / Not supported* before the user commits to full analysis.
- Interruption: "Resumed where it stopped." No duplicate session.
- Leaving mid-flow keeps a **Draft** (resume banner on Home).

### States
| State | Behaviour |
|---|---|
| loading | Step skeleton |
| empty | Step 1 |
| partial | Draft resume |
| complete | Go → navigate to `/matches/$matchId` (Processing state of the Recap) |
| low-coverage | "Usable with limits" result lists exactly what will be unavailable; user may proceed |
| failed | Upload/ingest failure with cause, what was kept, retry/another file |
| permission | Consent not given for Analyse → cannot proceed; explains why |
| offline | Upload paused; "We'll continue when you're back online" |
| demo | "Use a sample" creates no server session; labelled sample |

### Depth / Preset behaviour
- **Quick/Relax:** steps 2–5 are single screens with defaults pre-selected; step 4 is skipped when auto-calibration passes.
- **Advanced/Compete:** adds *Profile* (hardware/pipeline profile from `/api/profiles`), calibration mode readout, retention choice, and the ability to enter both names.

### Accessibility
Stepper uses `aria-current="step"` and announces "Step 2 of 6". File drop zone has a keyboard-reachable button; progress uses `role="progressbar"`; errors are `role="alert"` and tied to fields. Mobile: large primary action pinned only when it does not cover content.

### Telemetry
`new_match_started`, `suitability_checked` (result), `upload_started`, `upload_interrupted`, `upload_resumed`, `match_type_selected`, `identity_selected`, `court_confirmed` / `court_manual`, `consent_changed`, `analysis_started`, `draft_saved`.

### Acceptance criteria
- **AC-new-1** The player can reach "Start analysing" with ≤ 5 taps on defaults for a suitable clip.
- **AC-new-2** An unsuitable clip shows reasons and a fix, never just "Try again".
- **AC-new-3** Analyse is the only required permission; Share and Train are off and separately toggleable.
- **AC-new-4** Interrupting the upload and returning resumes without duplicating the match.
- **AC-new-5** No question is asked while the video is being processed.
- **AC-new-6** No notification permission is requested on this screen.
- **AC-new-7** "Which one is you?" is answerable by tapping a player on a frame, with names optional.

---

## 6. Processing — `/matches/$matchId/processing`

### Purpose
Say honestly what is happening, let the player **watch immediately** (progressive playback already exists), and show what is already usable. Processing is **also an in-page state of the Recap**; this route is the focused view and the target of the "Your match is ready" notification before completion.

### Who and when
The player who just uploaded; often leaves and returns.

### Entry points
After upload, Home processing card, Matches card, notification.

### Layout — mobile
```
┌────────────────────────────────┐
│ ← Thursday evening   Reading…  │
│ ┌── video (plays now) ───────┐ │
│ └────────────────────────────┘ │
│ We're reading your match       │
│ ✓ Video ready                  │
│ ✓ Found the court              │
│ ◔ Following rallies   (31 so far)│
│ ○ Spotting shots (Preview)     │
│ ○ Picking your moments         │
│ You can leave — we'll keep going│
│ [ Notify me when it's ready ]  │
│ Ready so far: 3 moments ▸      │
└────────────────────────────────┘
```

### Layout — desktop
Video left; `ProcessingStages` and "Ready so far" right; the lower area previews the Recap skeleton, filling in as sections complete.

### Components used
`ProcessingStages`, `ClipPlayer`, `MomentStrip`, `PartialAnalysisNote`, `FailedState`, `OfflineState`, `PreviewTag`, `LoadingSkeleton`.

### Data in
| UI field | Source |
|---|---|
| Stage status | `Session.status` (`created/ingesting/ready_to_play/analysing/analysed/failed`) and WebSocket `StatusMsg` (`n_frames`, `frontier_frame`, `rate_x`, `degraded[]`) — existing |
| Measured progress | `frontier_frame / n_frames` — existing |
| Per-stage detail (court found, rallies so far, shots, moments) | derived from events (`calibration`, `scene`, `rally_end`, `stroke`, `highlight`) now; proper stage model — new, see G-12 |
| Degradation reasons | `StatusMsg.degraded[].stage/reason` — existing |
| ETA | Only `rate_x` ("2.4× faster than the video"), shown as "about N minutes" **only when `rate_x` is stable**; otherwise omitted |

### Copy
- **Heading:** "We're reading your match."
- **Stages (plain):** *Video ready · Found the court · Following rallies · Spotting shots · Picking your moments.*
- **Leave:** "You can close this. We'll keep going and your match will be waiting."
- **Partial:** "Some results are ready. We're still checking the rest. Not ready yet: shots."
- **Degraded:** "Part of this match was filmed from another angle, so we skipped it." (derived from `scene` segments with `analysed: false`).
- **Never:** a made-up percentage, "almost there!", countdown.

### Interactions
- Playback starts as soon as the first segment is ready (existing HLS behaviour).
- **Notify me when it's ready** is *opt-in* and triggers the notification-permission flow for the first time **here**, with a reason (see `10`).
- Tapping "Ready so far" opens available moments; any moment shown is flagged "provisional" until the stage completes (`status: provisional` → "Worth a look").
- Failure → `FailedState`: cause (`Session.status_detail`, translated), what was saved (the video and anything analysed), actions *Try again* (`POST …/reanalyse`) and *Report an issue*.

### States
| State | Behaviour |
|---|---|
| loading | Skeleton |
| empty | n/a |
| partial | Primary state; `PartialAnalysisNote` |
| complete | Auto-navigate to Recap with a gentle "Your match is ready" banner (never forced) |
| low-coverage | Complete with a note about what could not be followed |
| failed | `FailedState` |
| permission | Revoked → `PermissionRevokedState` |
| offline | "Reconnecting…" chip; progress resumes via WebSocket re-sync |
| demo | Simulated stages, labelled "Simulated progress" |

### Depth / Preset behaviour
- **Quick/Relax:** four plain stages; no technical detail.
- **Advanced/Compete:** + stage names with the real model/profile, `rate_x`, degraded list, and a link to `/admin/system` only for operators.

### Accessibility
`ProcessingStages` is an ordered list with `aria-live="polite"` announcing stage changes (not every tick). Progress uses a real `progressbar` only for measured values. Skeletons are `aria-hidden`.

### Telemetry
`analysis_started`, `analysis_stage_viewed`, `analysis_partial`, `analysis_completed`, `analysis_failed`, `notify_opt_in`, `processing_left_early`, `retry_clicked`.

### Acceptance criteria
- **AC-proc-1** No percentage or ETA is shown that is not measured.
- **AC-proc-2** Video plays before analysis completes.
- **AC-proc-3** Partial results are labelled provisional and are excluded from Records/Progress.
- **AC-proc-4** Failure explains cause and what was saved.
- **AC-proc-5** Leaving and returning restores the same stage view.
- **AC-proc-6** No questions are asked during processing.

---

## 7. Match Recap — `/matches/$matchId`  *(the most important screen)*

### Purpose
Give the player **something they value in the first screen** — a moment worth replaying — then one understandable truth about their game, then (optionally) a shared memory. It must work for a player who will read nothing else, for a player who lost, and for a player whose recording was imperfect.

### Who and when
The player minutes to hours after the game, usually on a phone, tired, curious about *"Was it as good as it felt?"* and *"Show me the good bit."* Also revisited weeks later.

### Entry points
Home continue card, Matches card, notification, Processing completion, shared link (owner view).

### Section order (D4)
**① Moments → ② My game → ③ Together**, then **Deep dive ▸**. Each section is reachable without consuming the others. On first open, an **EntryChoice** appears (§7.3).

### Layout — mobile
```
┌────────────────────────────────┐
│ ← Matches   Thu evening  ⋯     │ RecapHeader (title, date, type chip)
│ vs Rahul · 36 rallies · 21–17? │ ScoreChip is small & neutral
│ [Followed 31 of 36 rallies ▸]  │ CoverageBar (tap → What we could see)
├────────────────────────────────┤
│ ① Your moments                 │
│ ┌── HeroMoment ──────────────┐ │
│ │ ▶  poster                  │ │
│ │ A 14-shot rally            │ │
│ │ Your longest today.        │ │
│ │ [Looks right] [Watch this] │ │
│ │ ♡ Save   ⤴ Share           │ │
│ └────────────────────────────┘ │
│ [▶ Defence ][▶ Net battle][▶ …]│ MomentStrip
├────────────────────────────────┤
│ ② My game                      │
│ ┌ FactTrio ──────────────────┐ │
│ │ 14  longest rally (shots)  │ │
│ │ 9   rallies of 6+ shots    │ │
│ │ 5   shot types spotted ◔   │ │
│ └────────────────────────────┘ │
│ What stood out                 │ StoryParagraph (≤ 3 sentences)
│ "You kept more neutral rallies │
│  alive in the second half."    │
│ [Watch this]  Why we say this ▸│
│ (Guided) One thing to try ▸    │ optional
├────────────────────────────────┤
│ ③ Together  (Not yet · doubles)│
│ Invite someone to see this     │
├────────────────────────────────┤
│ NextStepRow: Keep the moments · │
│ Understand the pattern · Try   │
│ something · Done               │
│ Was this recap useful? 👍 👎 ⚑ │ RecapFeedback
│ Deep dive ▸    Fix something ▸ │
├────────────────────────────────┤
│ Home  Matches  ＋  Moments  Progress │
└────────────────────────────────┘
```

### Layout — desktop
```
┌ SideNav ┬──────────────────────────────────────────────────────────────────┐
│         │ RecapHeader … Preset ▾  Depth [Quick|Guided|Advanced]  Deep dive ▸│
│         ├───────────────────────────────────────────┬──────────────────────┤
│         │ ① HeroMoment (large ClipPlayer)           │ ② FactTrio           │
│         │   why chosen · Watch this · Save · Share  │ StoryParagraph       │
│         │ MomentStrip (6)                           │ One thing to try (G) │
│         │                                           │ What we could see    │
│         ├───────────────────────────────────────────┴──────────────────────┤
│         │ ③ Together · NextStepRow · RecapFeedback                          │
└─────────┴──────────────────────────────────────────────────────────────────┘
```
The sticky video sits left on wide screens; clicking any claim seeks it (existing `?f=` / `seekFrame`).

### 7.1 Section contract

**① Moments**
- `HeroMoment`: the single best verified moment *for the chosen purpose and for this player*; a one-line plain description of **why it was chosen** ("Your longest rally today — 14 shots"). Never a superlative without a definition.
- `MomentStrip`: up to 5 more moments from distinct lenses (longest · defence · net exchange · big point (only if scoreline Checked) · variety). Diversity enforced (existing MMR; see G-18 for amateur weighting).
- **Fair-to-everyone rule (D17):** at least one verified positive moment per player in view when evidence permits. If none is reliable: *"We couldn't find a moment we're sure about in this recording. Pick one to keep →"* (manual selection from the rally list).
- **Social/funny moments:** never in this strip unless the player has opted in per clip.

**② My game**
- `FactTrio`: **at most three facts**, chosen by purpose (Quick/Relax: rally-centric). Each: number + unit + plain label + `CheckChip`; each opens its definition (`MetricPopover`) and clips (`EvidenceChip`).
- `StoryParagraph`: 1–3 neutral sentences built from verified claims only (G-29). No causal claim; "appeared alongside", "more often than".
- **One thing to try** (Guided and Improve only): an *Opportunity* `InsightCard` (amber ◆, never red) with a **Focus** action (Accept · Edit · Not now). Absent if no clear opportunity: *"Nothing stands out as a clear opportunity here."*
- Everything with a Preview dependency carries `PreviewTag`.

**③ Together**
- Doubles/pair surfaces are **Not yet** (G-03). Until then this section shows a single quiet card: *"Playing with a friend? Invite them to see this match."* (`InviteLink`, Preview). For Social games it shows the other player's positive moment **only if** that player is a Rally user who consented, or if the match owner chose *Both players* and the other player is anonymous-labelled.

### 7.2 Data in
| UI field | Source |
|---|---|
| Title, date, type | `Session.title`, `created_at`, type (new — G-04) |
| Names, "me" | `Session.players`, mapping (new — G-01) |
| Scoreline chip | `Analytics.score_timeline[-1].score`, `MatchState.completed_games` via `GET …/state`; shown only for a **Match** type; chip carries Checked/Looks right |
| Coverage | derived from `scene` events (`ScenePayload.analysed`), `StatusMsg.degraded`, `Calibration.coverage` / `quality` — plain-language form (G-20) |
| Hero + strip | `Highlight[]` (existing) re-ranked (G-18); clip file `GET …/exports/clip.mp4?from=&to=` (existing); posters (G-31) |
| FactTrio values | `Analytics.longest_rally_shots`, `avg_rally_shots`, `rallies`; rallies ≥ 6 shots from `rally_end.payload.n_shots`; shot types spotted from `PlayerStats.strokes` (Preview); `active_play_s` (in API `to_public()`; **add to the TS `Analytics` type**) |
| CheckChip | `BaiEvent.band`, `status` (D5 mapping) |
| StoryParagraph / InsightCard | new — see G-29 (claim, claim_type, evidence_refs, metric_definition_id, sample_size, coverage) |
| Metric definition | new — see G-07 |
| Feedback | new — see G-30 |

### 7.3 Entry choice (first open)
A short card above ① on the **first open** of a match whose scoreline is *Checked or Looks right*. It is **identical for every outcome**: no result-dependent copy, no colour, no emoji.

> **How would you like to see this?**  
> ○ **Quick recap** — your moments, in two minutes  
> ○ **Deep review** — rallies, shots and the court  
> ○ **Review later** — I'll come back to it

- Picking **Review later** collapses the recap to the Hero moment and a *Come back when you like* note; **no reminder is scheduled** unless the player sets one.
- The choice is remembered per player (as a default) and is editable in Settings → Preferences.
- We never infer mood from the result (D5, Blueprint §3.5).

### 7.4 Loss vs win parity
Same layout, same sections, same animation budget. **No confetti, glow, trophy or colour change tied to the match result.** The scoreline is a small neutral `ScoreChip`. A restrained acknowledgement (a quiet ring on the badge) is allowed **only for a verified Personal best** (05c), never for winning. After a loss the copy never reframes the result ("Great effort!"); it simply offers the same three choices and specific verified moments.

### 7.5 Depth behaviour
| Depth | What changes |
|---|---|
| **Quick** | ① + FactTrio + one StoryParagraph. "One thing to try" hidden. Definitions on tap only. |
| **Guided** | + "One thing to try" if supported, inline definitions on first view, "What we could see" visible |
| **Advanced** | + compact table of per-rally results (shots, outcome, state), coverage detail, link to Deep dive prominent; terminology: *rally, shot, contact*; shows band names under CheckChip on hover/focus |

### 7.6 Preset behaviour
| Preset | Order / emphasis |
|---|---|
| **Relax** | ① first, short ②, ③ prompt; no Opportunity |
| **Explore** | ① then "Firsts spotted" and Personal bests in ② |
| **Improve** | ② gains the Opportunity + Focus; ① shows the moment that illustrates it |
| **Compete** | ② becomes "Rally sequences": longest rallies, sequence preview, filters; ① uses tactically interesting lens |

A line *"Shown because you chose Improve — Change · Reset · Show all"* sits under the header.

### 7.7 Copy
- **Header sub:** "36 rallies · we followed 31" (not "You won").
- **Hero why:** "Your longest rally today — 14 shots."
- **CheckChip titles:** "Looks right" · "Worth a look" · "Checked by you".
- **FactTrio labels:** "Longest rally (shots)" · "Rallies of 6+ shots" · "Shot types spotted (Preview)".
- **Withheld:** "Not enough to say yet" with a reason.
- **Low-coverage banner:** "We could follow 18 of 40 rallies — mostly the ones near the camera. Your moments are real; the numbers are partial."
- **After-fix toast:** "Thanks — affected findings updated." plus `ChangeSummaryBanner` and Undo.
- **Banned:** "You dominated", "your footwork is poor", "you lost because", "Congratulations, winner!", any percentage confidence.

### 7.8 Interactions
- **Watch this** (on any claim) → seeks the clip with a 1-second lead-in; stays on the recap (inline sheet on mobile; docked player on desktop).
- **♡ Save** → adds to My Moments (private); **⤴ Share** → `SharePreviewDialog` (05c).
- **CheckChip** tap → popover with plain reason (e.g. "Partly hidden behind the net post") — never %.
- **CoverageBar** tap → "What we could see" panel (rallies followed/skipped, other cameras, court quality, why).
- **Fix this** (global and per card) → `FixSheet` → result in `ChangeSummaryBanner` with Undo; high-value fixes are suggested first (see 05b Review & fix).
- **NextStepRow:** *Keep the moments* (save hero) · *Understand the pattern* (open the insight's evidence) · *Try something next* (create a Focus) · *Done*. One may be chosen or none; "Done" is a success state.
- **Depth/Preset** switch in the header; effect is immediate and reversible.

### 7.9 States
| State | Behaviour |
|---|---|
| loading | Skeleton of ①②③ |
| empty | n/a (a processed match always has a recap or a reason) |
| partial | Processing state of the recap; sections fill in; provisional marked "Worth a look" |
| complete | Normal |
| low-coverage | `LowCoverageState` banner under header; ① uses only verified moments; ② facts limited; "Review & fix" suggested |
| failed | `FailedState`; if some results exist they are shown |
| permission | `PermissionRevokedState` for a recipient whose access ended |
| offline | `OfflineState`; recap cached |
| demo | `DemoBanner`; labelled sample |

Special variants:
- **No scoreline (Social/Practice or uncertain):** `ScoreChip` absent; FactTrio is rally-only.
- **No positive moment verified:** manual pick prompt (see 7.1).
- **Unsupported recording after analysis:** "We could find the court but not follow the shuttle in most rallies. Your video still plays; here's how to film for next time." Keeps footage-only moments (manually chosen).

### 7.10 Accessibility
- Reading order: Header → EntryChoice → ① → ② → ③ → NextStepRow → Feedback.
- Every `Watch this` is a button with `aria-label="Watch: {claim}"`; the clip has a text description and captions/metadata ("14-shot rally; you hit a drop at 0:23").
- `CheckChip` = icon + word + shape; coverage is also a sentence.
- Charts (if any in Advanced) have a text summary and an accessible table.
- Reduced motion: no autoplay, no staggered reveal.

### 7.11 Telemetry
`recap_viewed` (depth, preset, coverage), `first_insight_viewed`, `entry_choice_selected`, `coverage_opened`, `finding_opened`, `evidence_clip_opened`, `evidence_played`, `insight_response` (confirm/correct/dismiss/save), `moment_saved`, `share_previewed`, `label_corrected`, `focus_chosen`, `next_step_selected`, `recap_feedback` (useful/not/incorrect), `depth_changed`, `preset_changed`, `report_comprehension` (teach-back when sampled).

### 7.12 Acceptance criteria
- **AC-recap-1** The first screen on mobile shows a playable moment above any number.
- **AC-recap-2** FactTrio shows ≤ 3 facts; each opens a definition and a clip.
- **AC-recap-3** Win and loss produce identical layout; no result-dependent colour, icon or animation.
- **AC-recap-4** The EntryChoice offers the same three options regardless of outcome.
- **AC-recap-5** Every claim has "Watch this"; a claim with no resolvable evidence is not shown.
- **AC-recap-6** Preview-dependent surfaces carry a `PreviewTag`.
- **AC-recap-7** Low-coverage and partial states keep valid moments visible and explain limits.
- **AC-recap-8** Switching Depth/Preset never changes a displayed fact, only density and order.
- **AC-recap-9** Each player with enough evidence has at least one positive moment, otherwise a stated reason.
- **AC-recap-10** No percentage confidence appears; CheckChip uses words.
- **AC-recap-11** "Done" is a valid completion; no forced Focus, share or challenge.

---

## 8. Moments of this match — `/matches/$matchId/moments`

### Purpose
All the moments from one match, grouped by lens, so a player can pick favourites or build a share without the recap's narrative.

### Who and when
A player who liked the hero moment and wants "the others", or wants to pick the best three for friends.

### Entry points
Recap "All moments ▸", MomentStrip header, Clip detail "More from this match".

### Layout — mobile / desktop
```
┌────────────────────────────────┐
│ ← Recap     Moments · Thu eve  │
│ [All][Longest][Defence][Net][…]│ LensChips
│ ┌─ MomentCard ─┐ ┌─ MomentCard ┐│
│ │ poster 0:23  │ │ poster 1:12 ││
│ │ 14-shot rally│ │ Defence     ││
│ │ Looks right  │ │ Worth a look││
│ │ ♡  ⤴         │ │ ♡  ⤴        ││
│ └──────────────┘ └─────────────┘│
│ Can't see one you remember?    │
│ Add a moment from the video ▸  │ manual add
└────────────────────────────────┘
```
Desktop: 3–4 column grid; selecting multiple tiles shows a bar *"3 selected — Save · Share"* (share only if every clip's consent allows).

### Components used
`MomentCard`, `LensChips`, `MomentStrip`, `ClipPlayer` (quick preview), `FavouriteButton`, `SharePreviewDialog`, `EmptyState`, `PreviewTag`, `CheckChip`.

### Data in
| UI field | Source |
|---|---|
| Moments | `GET …/highlights?k=&player=` (existing); each has `categories[]`, `reasons{}`, `score`, `player`, `frame_start/frame_end` |
| Lens | derived from `categories` → plain lenses: `longest_rally`→"Longest rally" · `best_defence`→"Defence" · `net_battle`→"Net exchange" · `smash_winner`/`jump_smash`→"Power (Preview)" · `comeback`/`match_point`/`game_point`/`deuce`/`clutch`/`momentum_shift`→"Big points (needs a Checked score)" |
| Poster/duration | new — see G-31/G-06 |
| Favourite/visibility | new — see G-06 |
| Why chosen | `Highlight.reasons` translated: `length→"a long rally"`, `defence→"you kept it alive from the back"`, `net_play→"a close net exchange"`, `variety→"you used several shot types"` |

### Copy
- **Title:** "Moments from this match". **Empty:** "We couldn't find a moment we're sure about. You can add one from the video."
- **Why (per card):** "Why this one: you kept it alive from the back."
- **Preview note:** "Shot-based moments are a Preview."
- **No scores displayed** on cards (`Highlight.score` is internal ranking, **not shown**; the existing UI shows `h.score.toFixed(1)` — remove for amateurs; keep in Advanced as "Rank score").

### Interactions
Tap card → `/moments/$clipId`. Heart toggles favourite. Long-press (mobile) or checkbox (desktop) selects. **Add a moment** → pick a time on the video → creates a manual moment (`Verified: chosen by you`). Lens chips filter. Download via `clip.mp4` (Advanced only; Share dialog covers normal use).

### States
| State | Behaviour |
|---|---|
| loading | Card skeletons |
| empty | Message above + manual add |
| partial | Provisional moments marked "Worth a look" |
| complete | Normal |
| low-coverage | Notes which lenses are unavailable and why |
| failed | `FailedState` for clip generation, individually per card (retry) |
| permission | `PermissionRevokedState` |
| offline | Cached cards, uploads disabled |
| demo | Samples |

### Depth / Preset behaviour
Quick: ≤ 6 cards; Guided: all, lens chips; Advanced: + rank-score and *reasons* breakdown table; Compete preset starts on "Tactically interesting".

### Accessibility
Cards are a list of links with titles; selection mode announces counts; each clip has a text description. No autoplay; hover-preview is replaced by tap-to-preview for touch/keyboard.

### Telemetry
`moments_viewed`, `lens_selected`, `moment_saved`, `moment_added_manual`, `moment_opened`, `share_previewed`.

### Acceptance criteria
- **AC-moments-1** Lens chips map to documented categories and hide lenses with no evidence.
- **AC-moments-2** No numeric rank score is shown below Advanced.
- **AC-moments-3** Each moment shows a one-line reason in plain language.
- **AC-moments-4** Funny/social moments are absent unless the player approved them.
- **AC-moments-5** A player can add a moment manually when none is verified.

---

## 9. All Moments — `/moments`

### Purpose
The **personal memory** surface ("My Moments"): saved, favourited and shared moments across matches. The emotional core of retention that does not depend on analytics.

### Who and when
A player who wants to relive or share; also a player who just wants to keep a few clips and leave.

### Entry points
Nav, Home saved strip, Recap save.

### Layout — mobile
```
┌────────────────────────────────┐
│ My Moments                     │
│ [For you][Favourites][Together]│ tabs
│ [Lens ▾] [Match ▾] [Person ▾]  │ FilterBar
│ ── This month ──               │
│ [MomentCard][MomentCard]       │
│ ── Last month ──               │
│ ...                            │
└────────────────────────────────┘
```
Desktop: left rail filters; grid with month groupings; a side drawer previews the selected moment.

### Tabs
- **For you:** verified moments from all matches, ordered by the player's chosen purpose (recent first by default). *Not* ranked by "excitement".
- **Favourites:** the player's saved set; reorderable; "My top 5" collection optional.
- **Together:** shared or pair moments (**Not yet** for doubles; for single-player shares it shows moments *you shared* and *shared with you*, subject to consent).

### Components used
`MomentCard`, `LensChips`, `FilterBar`, `FilterSheet`, `FavouriteButton`, `SharePreviewDialog`, `EmptyState`, `PermissionRevokedState`, `PreviewTag`.

### Data in
| UI field | Source |
|---|---|
| Moments across matches | new — see G-06/G-02 (a `Moment` store; today moments exist only per session through `highlights`) |
| Filters: lens, match, person, date, favourites, shared | G-06 |
| Share status | new — see G-05 |

### Copy
- **Empty:** "Moments you save will live here. Save one from any match — it only takes a tap."
- **Together empty:** "Moments shared with you or by you will appear here."
- **Removed (consent revoked):** "This moment is no longer available. The person who owns it stopped sharing."

### Interactions
Tap → Clip detail. Heart toggles favourite. Multi-select for Save/Share/Remove; Share is only enabled if every selected clip's consent allows. "Remove from favourites" is undoable.

### States
| State | Behaviour |
|---|---|
| loading | Month-grouped skeletons |
| empty | Message per tab |
| partial | Moments from a still-processing match marked "Provisional" |
| complete | Normal |
| low-coverage | n/a |
| failed | Per-card thumbnail failure fallback |
| permission | Revoked shared moments show a tombstone card |
| offline | Cached thumbnails; playback disabled |
| demo | Sample moments in a labelled group |

### Depth / Preset behaviour
Quick/Relax: simple grid, lenses: Longest, Defence, Favourites. Guided: + Firsts. Advanced: + match/time/lens/shot filters, exports, "Used in Deep dive" backlinks.

### Accessibility
Tabs are `role="tablist"`; month groups are headings; keyboard Space to select; focus returns to the invoking card after closing a drawer.

### Telemetry
`moments_library_viewed`, `moment_favourited`, `moment_removed`, `filter_applied`, `moment_shared_from_library`.

### Acceptance criteria
- **AC-library-1** Sorting never uses an "excitement score" as a visible rank.
- **AC-library-2** Every item shows its match and date.
- **AC-library-3** A moment whose consent was revoked is replaced by a tombstone with a reason.
- **AC-library-4** Multi-share is blocked if any selected clip lacks consent.
- **AC-library-5** Removing from favourites is undoable.

---

## 10. Clip detail — `/moments/$clipId`

### Purpose
Watch a moment properly, understand **why it was chosen**, and decide what to do with it: save, share, fix, or dive into the rally. The place where *evidence* is concrete.

### Who and when
A player tapping a moment from the Recap, library or a shared link.

### Entry points
Recap, Moments, Deep dive (Rallies), Ask citations, notification.

### Layout — mobile
```
┌────────────────────────────────┐
│ ← Back to recap                │
│ ┌── ClipPlayer ───────────────┐│
│ │  0:23–0:41  ▶  ⏮ ⏭  0.5×    ││
│ └──────────────────────────────┘│
│ A 14-shot rally                 │
│ Thu eve · rally 22 · with Rahul │
│ [Looks right] Why this one ▸    │
│ ♡ Save  ⤴ Share  ⚑ Fix this     │
│ What happened                   │
│ You hit a drop at 0:23 and kept │
│ the rally going from the back.  │
│ [Open this rally in Deep dive]  │
│ Related moments ▸               │
└────────────────────────────────┘
```

### Layout — desktop
Player left (sticky); right column: title, `CheckChip`, `WhyChosenPanel`, actions, `InsightCard` for any claim, related moments; below: shot list for this rally as chips (existing `RallyRow` shot chips) with times.

### Components used
`ClipPlayer`, `CheckChip`, `EvidenceChip`, `WhyChosenPanel`, `FavouriteButton`, `SharePreviewDialog`, `FixSheet`, `ChangeSummaryBanner`, `MomentStrip`, `RallyDetailPanel` (read-only mini), `PreviewTag`, `PermissionRevokedState`.

### Data in
| UI field | Source |
|---|---|
| Clip range | `Highlight.frame_start/frame_end` (existing) → time via `clock()` |
| Video | HLS proxy + `?f=` deep link; downloadable `clip.mp4` |
| Rally facts | `rally_end` event payload: `n_shots`, `winner`, `outcome`, `end_reason`, `shots[]` (existing) |
| CheckChip | `band` + `status` |
| Why chosen | `Highlight.reasons` translated (see 8) |
| Shot labels | `strokeLabel(payload)`; shown with `PreviewTag` |
| Participants / attribution | `actors.player_id` (+ "me" mapping — G-01) |
| Visibility, share state | new — see G-06/G-05 |
| Related moments | `Highlight[]` of same match with overlapping categories (G-06) |

### Copy
- **Why chosen:** "We picked this because it's your longest rally today and you kept it going from the back of the court."
- **Attribution uncertain:** "We're not sure which player hit shots 8–10. Tell us →"
- **Fix this options:** *Wrong player · Wrong shot · Wrong winner · This isn't a rally · Bad clip · Something else.*
- **Share (default state):** "Private — only you can see this."
- **Never:** "Best shot ever", "Perfect", "Amazing!" tied to winning.

### Interactions
- **ClipPlayer:** play/pause, frame step (←/→), speed (0.5×, 1×), loop clip, keyboard shortcuts (existing Space/←/→/J/L), overlays **off by default** with legend; "Show where the shuttle went" toggles trail (existing overlay layers).
- **Save/Favourite**: immediate, undoable.
- **Share**: opens `SharePreviewDialog` (05c); funny/social moments require explicit per-clip approval.
- **Fix this** → `FixSheet`; result in `ChangeSummaryBanner`; undo.
- **Open this rally in Deep dive** → `/matches/$matchId/deep-dive/rallies?f=<frame>`; **Return to analysis** appears when arriving from Deep dive and navigates back with filters and scroll preserved (`scrollRestoration` already enabled).
- **Edit boundaries** (Guided+): drag clip start/end ± 3 s; saved as the moment's range.

### States
| State | Behaviour |
|---|---|
| loading | Player poster + skeleton text |
| empty | n/a |
| partial | "Provisional — this match is still being read" ribbon |
| complete | Normal |
| low-coverage | "Part of this rally was out of view" note over the timeline |
| failed | Clip render failed → plays from the match video at the range; retry download |
| permission | Revoked → `PermissionRevokedState` ("This moment isn't shared with you any more") |
| offline | Cached poster; "Reconnect to play" |
| demo | Sample banner |

### Depth / Preset behaviour
Quick: player, why-chosen sentence, three actions. Guided: + shot chips, boundary editing. Advanced: + evidence list (`Evidence[]` kinds/frames), event ids, band names, "Copy link to frame", download. Compete preset opens with sequence view.

### Accessibility
Player controls ≥ 44 px, labelled; keyboard operable; transcript-like text description "Rally of 14 shots; hits: drop (you), clear (Rahul)…"; captions/text for any audio; focus returns to the invoking card on close; overlays have a legend and are optional.

### Telemetry
`clip_opened`, `evidence_played`, `clip_boundaries_edited`, `moment_saved`, `share_previewed`, `share_initiated`, `label_corrected`, `open_in_deep_dive`, `return_to_analysis`.

### Acceptance criteria
- **AC-clip-1** The clip always shows *why it was chosen* in plain language.
- **AC-clip-2** Overlays are off by default and have a legend.
- **AC-clip-3** Save is immediate and undoable; share never creates a link without `SharePreviewDialog`.
- **AC-clip-4** Fix this offers the six categories and shows what changed afterwards.
- **AC-clip-5** Arriving from Deep dive shows "Return to analysis" and restores filters and scroll.
- **AC-clip-6** A revoked shared clip shows a permission state, not an error.
- **AC-clip-7** Shot labels on the clip carry `PreviewTag` until the classifier is validated.

---

## 11. Cross-screen telemetry glossary (this file)

| Event | Fired on | Notes |
|---|---|---|
| `example_opened` | Landing embed | Funnel separate from activation |
| `purpose_selected` / `purpose_skipped` | Landing, onboarding | Never infer identity |
| `suitability_checked` | New match | Result included |
| `upload_started/interrupted/resumed` | New match | |
| `analysis_started/partial/completed/failed` | Processing | |
| `first_insight_viewed` | Recap | **Activation proxy:** player opened the first moment/claim |
| `coverage_opened` | Recap / Sample | |
| `finding_opened`, `evidence_clip_opened`, `evidence_played` | Recap, Clip | Comprehension signals |
| `insight_response` | InsightCard | confirm / correct / dismiss / save |
| `label_corrected` | FixSheet | |
| `moment_saved`, `share_previewed`, `share_initiated` | Moments | audience type only, never recipient id |
| `harm_signal` | Recap feedback "This made me uncomfortable" | Guardrail |

Required context on every event: report/model version, match format, analysis coverage band, device/network class, experiment assignment. No raw video, no recipient identities.

## 12. State-coverage matrix (this file)

| Screen | loading | empty | partial | complete | low-cov | failed | permission | offline | demo |
|---|---|---|---|---|---|---|---|---|---|
| Landing | ✓ | – | – | ✓ | – | ✓ | – | ✓ | ✓ |
| Sample recap | ✓ | – | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ |
| Home | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Matches | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| New match | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Processing | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Recap | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Moments (match) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Moments (all) | ✓ | ✓ | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ |
| Clip detail | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |

## 13. Components named here that are not in `00 §6`

`EntryChoice` (Recap first-open card), `MatchTypePicker`, `LensChips`, `ScoreChip`, `FilterBar`, `FilterSheet`, `FavouriteButton`, `WhyChosenPanel`. Add to Doc 07.

## 14. Contradictions with `00` found while writing

None blocking. One tension to resolve in Doc 06/11: the current `Highlight.score` (0–10) is an internal rank used for diversity; D17 forbids showing it below Advanced, and the current `HighlightsTab` displays it — flagged for removal in the amateur UI.
