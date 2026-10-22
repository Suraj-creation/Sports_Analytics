# 03 — Onboarding and First Run

**Status:** Build-ready specification for the first-run and capture experience.
**Depends on:** `00_README_DECISIONS_AND_CONTRACT.md` (decisions D1–D18, vocabulary, routes, component names). Cited as **D#**.
**Related:** `04` (routes/nav), `05a` (Recap, Processing), `05b` (Review & fix, Place your court in the workspace), `07` (components), `09` (copy), `10` (consent, sharing), `11` (data gaps).

---

## 0. The one-paragraph version

An amateur player arrives curious and a little wary: *"Will this make me look bad? Is it a hassle? What are you doing with my video?"* The first run therefore does five things in this order: **(1)** show a realistic **sample recap** before asking anything (D9); **(2)** ask at most **two skippable questions**; **(3)** teach how to film so the footage is usable — as part of the product, not fine print; **(4)** after upload, ask only what the machine cannot know — **which one is you** and **where the court is** — in one tap each when possible; **(5)** get consent **at the moment it matters**, in four separated cards, and hand the player a **first Moment** while the rest of the match is still being analysed. Everything beyond that (nickname, partner, depth, notifications, account) is deferred until the player has seen something worth keeping.

> **Success is not "completed onboarding".** It is **activation (D9, Blueprint §1.3):** after the first usable match, the player either *saves a Moment they value* or can *correctly state one finding from its evidence*. Sign-up, tour completion and dashboard views are setup events, not success.

---

## 1. End-to-end funnel and effort budget

### 1.1 The funnel

```
Awareness ──► Landing ──► Sample recap ──► Two questions ──► Record guide ──► Choose video
 (outside)   /welcome    /welcome/sample   /start (skip OK)  /matches/new     file picker
                                                                  │
   ┌──────────────────────────────────────────────────────────────┘
   ▼
 Consent cards ──► Upload ──► Pick yourself ──► Place your court ──► Ready-to-start ──► Processing
 (JIT, at upload)  (resumable*) (tap on frame)  (auto, 1 tap)       (summary, 1 tap)   (live, watchable)
                                                                                           │
   ┌───────────────────────────────────────────────────────────────────────────────────────┘
   ▼
 First value reveal ──► Next step (Keep it · See my game · Fix something · Done)
 (hero Moment)           /matches/$matchId
```
\* Resumable upload does not exist yet (gap **G-ONB-1**, see §17). The UI is specified for it; until built, "Retry" restarts and the copy says so.

### 1.2 Time and effort budget (design targets to *measure*, not promises)

"Active effort" = seconds the player is doing something. "Wall time" = includes waiting. Targets assume a phone-filmed 15–25 min match on the GPU profile (`gpu-rtx4000`, ~2.4× real time in active rallies; on `cpu-dev` expect far slower — the processing screen must show real measured speed, never a promised ETA).

| # | Step | Active effort target | Hard ceiling | Skippable | Needs account | Emotional goal |
|---|---|---|---|---|---|---|
| 0 | Awareness (outside the product) | — | — | — | No | Curiosity |
| 1 | Landing `/welcome` | ≤ 20 s to understand | 45 s | — | No | "This is for people like me" |
| 2 | Sample recap `/welcome/sample` | ≈ 45 s | 3 min | Yes | No | "I'd want this after my game" |
| 3 | Two questions `/start` | ≤ 10 s | 30 s | **Both** | No | Feel in control |
| 4 | Record guide | ≤ 40 s first time; 0 s thereafter | 90 s | Yes ("I know how") | No | Reassured it will work |
| 5 | Choose video | ≈ 10 s | — | — | No | Low friction |
| 6 | Consent cards | ≈ 15 s | 45 s | Optional cards default off | No | Safe, not trapped |
| 7 | Upload | ≈ 5 s active, rest is wall time | — | Cancel/leave safely | No | "My work is safe" |
| 8 | Pick yourself | ≈ 8 s (1 tap + optional nickname) | 30 s | Nickname skippable | No | "It recognises *me*" |
| 9 | Place your court | ≈ 5 s auto / ≤ 60 s manual | 2 min | Skip → limited results | No | "That's my court" |
| 10 | Ready-to-start summary | ≈ 3 s | — | Edit any choice | No | Confident |
| 11 | Processing | 0 s (watchable) | — | Leave safely | Soft prompt after first value | Anticipation without anxiety |
| 12 | First value reveal | ≈ 10 s | — | — | No | Delight, kept honest |
| 13 | Next step | ≈ 5 s | — | Done | Soft prompt: "Keep this safe" | Choice, no pressure |

**Total active effort from "Choose video" to "analysis running": target ≤ 90 s (ceiling 3 min with manual court).** Anything over the ceiling is a design defect, not user error.

### 1.3 The rules that govern every step (restating D9, D15, D16, Blueprint §7.3 hard rules)

1. **Value before configuration.** The sample recap comes before any question. Nothing is asked that is not used in the next screen.
2. **No questions while waiting.** Processing and upload screens ask nothing (Blueprint hard rule).
3. **No notification permission request** before a notification has a reason (analysis > ~2 min *and* the player taps "Tell me when it's ready").
4. **Account creation only when needed to protect the player's work** — guest-first (§14).
5. **Nothing is inferred** about ambition, mood, age, ability, willingness to share or health from behaviour (Blueprint, D15).
6. **No tour that blocks exploration.** Coach-marks are one-shot, dismissible, never modal over content.
7. **Every step has Back and a safe Exit.** Choices persist in session storage and server draft; Back never loses anything.
8. **Demo/Sample is never confused with real data** — labelled and visually distinct (§3).
9. **Adult-only pilot (D15):** an unobtrusive age line at consent, not a date-of-birth form (§9.4).

---

## 2. Step 1 — Landing (`/welcome`)

**User's question:** "What is this and is it for me?" **Feeling:** curious, slightly sceptical ("AI coach" fatigue).
**Entry points:** shared link, search, club/WhatsApp share (`/s/$token` is separate — §13), direct.
**Exit:** to Sample (primary), to Start (secondary), to Sign in (tertiary text link).

### 2.1 Wireframe — mobile (360 px)

```
┌──────────────────────────────────────┐
│ ◇ Rally                     Sign in  │  ← logo + text link only
├──────────────────────────────────────┤
│                                      │
│  Your game.                          │
│  Your moments.                       │
│  Your progress.                      │
│                                      │
│  Turn a badminton video into the     │
│  rallies worth replaying and a       │
│  clear picture of your own game.     │
│                                      │
│  ┌────────────────────────────────┐  │
│  │ ▶  See a sample match   (45 s) │  │  ← PRIMARY
│  └────────────────────────────────┘  │
│  Analyse my video  →                 │  ← secondary text button
│                                      │
│  ┌──────── SampleRecapEmbed ───────┐ │
│  │  [court + ball loop, 12 s,      │ │
│  │   muted, no audio, reduced-     │ │
│  │   motion → static frame]        │ │
│  │  "A 14-shot rally"   SAMPLE     │ │
│  └─────────────────────────────────┘ │
│                                      │
│  How it works                        │
│  1 Film  2 Upload  3 Watch your      │
│  moments  4 Choose what to do next   │
│                                      │
│  Pick what matters to you (preview)  │
│  [Keep the moments] [Understand my   │
│   game] [Choose something to         │
│   practise] [Prepare to compete]     │  ← each opens a different sample view
│                                      │
│  What we can and can't do yet  ▸     │
│  Private by default  ▸               │
│  Works on phone footage?  ▸          │
└──────────────────────────────────────┘
```

**Desktop note:** two columns ≥1024 px — copy left, `SampleRecapEmbed` right; "How it works" as a horizontal 4-step row; the three accordion rows become a footer trio. Keep the same order of importance; do not add a second hero.

### 2.2 Copy (exact)

| Element | Copy |
|---|---|
| H1 | Your game. Your moments. Your progress. |
| Sub | Turn a badminton video into the rallies worth replaying and a clear picture of your own game. |
| Primary | **See a sample match** |
| Secondary | Analyse my video |
| Sample caption | A sample match — not a real player |
| How it works | **1** Film a game · **2** Upload it · **3** Watch your best moments · **4** Pick what to do next — or nothing |
| Purpose cards | Keep the moments · Understand my game · Choose something to practise · Prepare to compete |
| Accordion: limits | **What we can and can't do yet.** Works best with the whole court in view from behind one baseline. Singles only for now. Shot types and shot placement are in *Preview*. |
| Accordion: privacy | **Private by default.** Analysing a video is not sharing it, and never means we train on it. You decide each one separately. |
| Accordion: footage | **Will my phone video work?** Usually yes, if the whole court and both players stay in frame. We'll check a few seconds first. |
| Footer | Adults only for now. Privacy · Accessibility · Help |

**Do not** use: "AI coach", "unlock your potential", "level up", countdown timers, invented testimonials or player counts, stock-athlete imagery (Blueprint §7.1, §10.9).

### 2.3 Interactions
- Primary → `/welcome/sample`. Secondary → `/matches/new` (starts as guest, §14).
- Purpose cards route to *different* sample views (Moments-first, My-game-first, Focus-first, Tactics-first); none is "the real one".
- `SampleRecapEmbed` loop is **muted, 12 s, paused when off-screen, replaced by a still frame under `prefers-reduced-motion` or data-saver**.
- Accordions: keyboard-operable; one open at a time not required.

### 2.4 States
| State | Behaviour |
|---|---|
| Loading | Static HTML first; embed lazy-loads; skeleton the same size as the embed (no layout shift) |
| Offline | Page renders; sample button says "Sample needs a connection" and is disabled with a retry |
| Returning (has account/guest data) | Skip landing: `/` Home (see §12) |
| Unsupported browser | Plain-text message + link to Help; no blank page |

### 2.5 Accessibility
Single `h1`; landmark regions; embed has a text description ("A rally of 14 shots between two players, replayed from behind the court") and a pause control; primary CTA ≥ 44 px; contrast ≥ 4.5:1 (Doc 08).

### 2.6 Telemetry
`landing_viewed` · `example_opened` · `purpose_card_opened {purpose}` · `landing_cta_clicked {which}` · `limits_opened` · `privacy_opened`.

### 2.7 Acceptance
- **AC-ONB-1** A first-time visitor can state, after 20 s, one benefit and one limit (usability test, pass ≥ 80 %, Blueprint §16.2).
- **AC-ONB-2** No account, camera, microphone or notification prompt appears on this page.
- **AC-ONB-3** The embed never autoplays with sound and honours reduced motion.
- **AC-ONB-4** Cost/equipment requirements are visible (or "Free during the pilot") before any upload step.

---

## 3. Step 2 — Sample recap (`/welcome/sample`)

**User's question:** "What would *I* get?" **Feeling:** evaluating; wants proof it's useful and not creepy.
**Principle:** the sample is built from the **same components as the real Recap** (`RecapHeader`, `HeroMoment`, `FactTrio`, `MomentStrip`, `CheckChip`, `CoverageBar`) so the player learns the real interface (Blueprint §7.2). Engagement with the sample proves *expectation comprehension*, not activation — track it as a separate funnel.

### 3.1 Sample behaviour spec

| Aspect | Rule |
|---|---|
| Label | A persistent `DemoBanner`: **"Sample match — fictional players. Nothing here is yours."** Cannot be dismissed; sticky on scroll. |
| Data | Deterministic fixture (Doc 12). Fictional nicknames ("Alex", "Sam"). No real people's footage unless explicitly permissioned and labelled. A rendered court replay of tracked data is preferred over real video. |
| Content | The same three sections as a real Recap: **Moments → My game → Together**. Together is shown as **"Coming with doubles"** (**Not yet**, D10) — not hidden, not faked. |
| It must also show the uncomfortable truth | One `CheckChip` "Worth a look", one "Not enough to say" state, and a `CoverageBar` ("We followed 31 of 36 rallies") — so expectations are honest. |
| Interactions allowed | Play the hero clip; open "Watch this" evidence on any claim; open `MetricPopover`; open `FixSheet` (demo result: "Demo — nothing changed"); switch Depth (Quick/Guided/Advanced) to *see* the difference; switch Preset. |
| Interactions blocked | Save, share, favourite (show "This is a sample — try it with your own video"). |
| Reset | A "Reset sample" action in the banner overflow restores fixture state and Preset/Depth. |
| Persistence | Sample interaction state is **not** stored in the player's account, never counts toward records, journey, progress or telemetry about the player's own sessions. |
| After first real match | The sample moves to Help → "See the sample again". It never appears in the Matches list. |
| Hint-free | No coach-marks in the sample; if the player stalls > 20 s, show one inline hint chip ("Tap *Watch this* on any claim"), once. |

### 3.2 Wireframe — mobile

```
┌──────────────────────────────────────┐
│ ‹ Back          SAMPLE · fictional   │  ← DemoBanner (sticky)
├──────────────────────────────────────┤
│ Alex vs Sam · Sample match           │
│ [Relax ▾]  Depth: Quick Guided Adv.  │
│                                      │
│ ┌──── HeroMoment ─────────────────┐  │
│ │ ▶  [court replay thumbnail]     │  │
│ │ "A 14-shot rally"               │  │
│ │ Alex kept this one alive.       │  │
│ │ Looks right ✓  ·  Watch this    │  │
│ └─────────────────────────────────┘  │
│                                      │
│ Three things                         │
│  14  shots in your longest rally     │
│  9   rallies of 6+ shots             │
│  5   shot types spotted  [Preview]   │
│                                      │
│ Moments  [• • • •  →]  MomentStrip   │
│                                      │
│ My game · Together (Coming)          │
│                                      │
│ ┌──────────────────────────────────┐ │
│ │ Try it with your own video  →    │ │  ← sticky bottom CTA (does not cover content)
│ └──────────────────────────────────┘ │
└──────────────────────────────────────┘
```
**Desktop note:** video left (sticky), narrative right (Blueprint §7.8); banner spans both columns.

### 3.3 Copy
- CTA: **Try it with your own video** · secondary: **Not now** (returns to landing).
- Hint chip: *Tap "Watch this" on any claim to see exactly where it comes from.*
- Together placeholder: *Doubles recaps are on the way. For now we analyse singles.*

### 3.4 Telemetry
`sample_opened {from: landing|purpose_card}` · `sample_depth_changed` · `sample_evidence_opened` · `sample_fix_opened` · `sample_completed` (scrolled to end *or* played hero) · `sample_exit_to_start`.

### 3.5 Acceptance
- **AC-ONB-5** The sample is visibly labelled on every sample screen and in the document title; a screenshot of any sample screen cannot be mistaken for a player's data.
- **AC-ONB-6** Sample shows at least one non-"Looks right" state and a coverage line.
- **AC-ONB-7** Sample interactions never write to the player's data store (verified by network-log test).
- **AC-ONB-8** Sample uses the same component implementations as the real Recap (no sample-only look-alikes).

---

## 4. Step 3 — Two optional questions (`/start`)

**User's question:** "Do I have to tell you things?" **Feeling:** wary of a questionnaire.
**Rule:** maximum **two** screens, both skippable, both editable forever. Asked *after* the sample (they have context) and *before* the first upload (it changes what we show first).

### 4.1 Question 1 — Purpose ("What would be nice today?")

Up to **two** selections; "Not sure" is a valid answer; Skip → balanced default (Keep the moments + Understand my game, Quick depth).

```
┌──────────────────────────────────────┐
│  1 of 2                         Skip │
│                                      │
│  What would be nice today?           │
│  Pick up to two. Change it anytime.  │
│                                      │
│  ┌─────────────┐ ┌─────────────┐     │
│  │ ◉ Keep the  │ │ ◯ Understand│     │
│  │   moments   │ │   my game   │     │
│  └─────────────┘ └─────────────┘     │
│  ┌─────────────┐ ┌─────────────┐     │
│  │ ◯ Choose    │ │ ◯ Prepare   │     │
│  │ something to│ │ to compete  │     │
│  │ practise    │ │             │     │
│  └─────────────┘ └─────────────┘     │
│  ┌──────────────────────────────┐    │
│  │ ◯ Discuss with someone       │    │
│  └──────────────────────────────┘    │
│  Not sure — surprise me with a mix   │
│                                      │
│  [ Continue ]                        │
└──────────────────────────────────────┘
```
(`PurposePicker`.) "Just play" (Doc 00 D2) is offered as the sixth card **only after** the first match, in Settings → Preferences — a first-time player has nothing yet to "just play" with.

| Selection | Effect on the first Recap |
|---|---|
| Keep the moments | Hero Moment first; no "opportunity" card; no practice suggestion |
| Understand my game | Match story paragraph + one verified strength; coverage visible |
| Choose something to practise | One optional Focus suggestion appears *after* a strength |
| Prepare to compete | Opens Depth = Advanced suggestion; Deep dive link prominent |
| Discuss with someone | Share/annotate affordances surface; coach view is **Not yet** → "Share a moment privately" |
| Not sure / Skip | Balanced default |

### 4.2 Question 2 — Preset ("How much detail?")

Show **what each looks like** (a one-line mini-preview), not a description. Default **Relax**. "Decide later" is equal-weight to the cards.

| Preset (D3) | Mini-preview line | Best for |
|---|---|---|
| **Relax** | "Your best moments, short and friendly." | Social players, new/returning |
| **Explore** | "Moments plus the shots and personal bests we spot." | Curious players |
| **Improve** | "Moments, one strength, one idea to try." | Players who want one focus |
| **Compete** | "Rally-by-rally detail with filters." | Club/competitive (not recommended as a first default for casual players — say so) |

Copy: **"You can change this on any match."**  Buttons: **Use Relax** (label updates to the chosen preset) · **Decide later**.

### 4.3 Behaviour
- Back returns to Q1 with selection retained; Exit returns to the sample.
- Choices write to a **guest draft** immediately (local + server draft once a guest workspace exists, §14).
- Never block Continue; never validate.
- After Q2 → `/matches/new`.

### 4.4 Telemetry
`purpose_selected {values}` / `purpose_skipped` · `preset_selected {preset}` / `preset_skipped` · `start_exit {step}`.

### 4.5 Acceptance
- **AC-ONB-9** Both questions can be skipped in one tap each; skipping produces the documented balanced default.
- **AC-ONB-10** No more than two question screens precede the record guide; no third appears later in onboarding.
- **AC-ONB-11** Preset and Purpose are editable from the match header within two taps after onboarding.
- **AC-ONB-12** The player is never labelled ("You're a competitive player") anywhere in the UI.

---

## 5. Step 4 — Record guide, framing checklist, test clip, suitability (`/matches/new`, step 1)

**User's question:** "How do I film this so it actually works?" **Feeling:** unsure, possibly embarrassed about setup; wants a quick, doable checklist.
**Why it matters:** capture is part of the product value (Blueprint §7.4). The pipeline was validated on **broadcast** footage; amateur phone clips are the weakest-evidence case, and **a report cannot compensate for footage the system cannot interpret**. The cheapest quality gain in the whole product is getting the camera in the right place.

### 5.1 `RecordGuide` — wireframe (mobile)

```
┌──────────────────────────────────────┐
│ ‹ Back        New match      (1 of 4)│
├──────────────────────────────────────┤
│  Film it so it works                 │
│  Takes 40 seconds to read. Skip if   │
│  you've done this before.            │
│                                      │
│  ┌──── court diagram (top-down) ───┐ │
│  │         far baseline            │ │
│  │   ┌─────────────────────────┐   │ │
│  │   │           net           │   │ │
│  │   └─────────────────────────┘   │ │
│  │        near baseline            │ │
│  │            📱  ← here           │ │
│  │   2–3 m behind, centred, high   │ │
│  └─────────────────────────────────┘ │
│                                      │
│  ✓ Behind one baseline, in the       │
│    middle, as high as you can        │
│  ✓ Whole court in frame, both        │
│    players always visible            │
│  ✓ Phone landscape, steady, don't    │
│    zoom or pan                       │
│  ✓ Court well lit, no glare          │
│  ✓ Film the game, not the warm-up    │
│                                      │
│  Who's playing? ( ) Singles (•)      │
│                 ( ) Doubles — soon   │
│                                      │
│  Before you film:  tell the people   │
│  playing and check the venue allows  │
│  filming.                            │
│                                      │
│  [ I'm ready — check my video ]      │
│  I already have a video              │
└──────────────────────────────────────┘
```

**Desktop note:** two columns — diagram + checklist left; "Check my video" drop-zone right (this is where a laptop user usually has the file).

### 5.2 `FramingChecklist` — the rules, their reasons, and what the system verifies

| # | Rule (plain words) | Why (one line shown on tap) | Can we verify it? | How |
|---|---|---|---|---|
| F1 | Behind one baseline, centred, 2–3 m back | "From behind, near and far player never swap places — it keeps *you* identifiable." | Partly | Court fit gives camera position (`camera.centre_m`) once the court is found — compare to the baseline-centred band |
| F2 | As high as you can (a chair, a bench, a tripod) | "Height lets us see the far corners and where shots land." | Yes | Camera elevation from the homography (ROADMAP: physics filter requires ≥ 3° elevation) → "very low" warning below ~8° (threshold to be set from validation) |
| F3 | Whole court in frame | "If the corners are cut off we can't map where you stood." | Yes | Court-line fit `support`/`area`; four-corner presence |
| F4 | Both players in frame at all times | "We can't follow someone who leaves the picture." | Yes | Person detections per frame in the test clip |
| F5 | Landscape, steady, no zoom/pan | "Moving cameras make the court shift." | Yes | Camera tracker mode `static` vs `camera`; rotation residual |
| F6 | Well lit, no strong glare | "Dark or washed-out lines are hard to find." | Yes | Line-pixel count / top-hat yield |
| F7 | No cuts or other cameras | "Edits break the court view." | Yes | Scene segments (`main/alt/none`) |
| F8 | Singles for now | "Doubles has more players and more overlap; we're not ready to analyse it responsibly." | Yes | > 2 persons on court in test clip |
| F9 | Film the game, not the warm-up | "Warm-up hits would be counted as rallies." | Partly | Match-phase model (formation test); reviewer can mark "Match starts here" |
| F10 | Tell people and check the venue | "Everyone in the frame should know." | No — human | Consent reminder text (§9) |

### 5.3 `TestClipCheck` — check *before* the whole upload

Goal: failures surface **before** a 2 GB upload (Blueprint §7.4).

| Mode | How | Needs |
|---|---|---|
| **A. On-device pre-check (instant)** | Read file metadata: resolution, orientation, duration, size, codec. Warn: portrait video, < 720p, < 1 min, > server limit (`system.limits.max_upload_mb`), unsupported container. | Nothing new |
| **B. 10-second probe (≈ 5–15 s)** | Upload only the **first 10 s after the first rally-like movement** (or a 10 s slice picked by the player scrubbing locally), call a probe that runs court-line fitting + person detection on ~24 sampled frames, returns a `SuitabilityResult`. | New endpoint (**G-ONB-2**): `POST /api/probe` → `{court: {found, precision, support, elevation_deg}, players: {n_on_court, both_visible}, scene: {main_share}, light: {line_yield}}`. Reuses `propose_corners` / `court_lines` and the 24-frame sampling in `_auto_calibrate`. |
| **C. Skip** | "Just upload it" → analyse; if bad, `UnsupportedFootageState` appears after court detection with the same fixes | — |

The player picks A+B by default; C is always available and unpunished.

### 5.4 `SuitabilityResult` — three outcomes, always with a fix

```
┌──────────────────────────────────────┐
│  ✓ Looks good                        │   ← Suitable
│  We can see the whole court and both │
│  players. Upload the full video.     │
│  [ Continue ]                        │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  ◐ Usable, with limits               │   ← Usable with limits
│  • The far corners are cut off, so   │
│    "where shots went" will be rough. │
│  • You'll still get rallies and      │
│    moments.                          │
│  Fix next time: tilt the phone down  │
│  a little or step back 1–2 m.        │
│  [ Continue anyway ]  [ Re-record ]  │
└──────────────────────────────────────┘

┌──────────────────────────────────────┐
│  ✕ We can't follow this video yet    │   ← Not supported
│  The camera is very low and the net  │
│  hides the far player.               │
│  Try: raise the phone (a chair or    │
│  bench works) and film from behind   │
│  the baseline.                       │
│  [ How to film it ]  [ Keep video    │
│    for later ]  [ Try another video ]│
└──────────────────────────────────────┘
```

| Outcome | Rule (derived from probe) | What is promised | What stays available |
|---|---|---|---|
| **Suitable** | court found (precision ≥ 0.6, support ≥ 0.9 frame widths), 2 persons, main-camera share ≥ 90 % | Full Moments, rallies; shots/placement labelled Preview | Everything |
| **Usable with limits** | Court found but low area/elevation, or 1–2 short gaps, or light marginal | Moments + rally list; lists exactly which surfaces will be missing (heatmaps, "where shots went") | Moments, rallies, Ask |
| **Not supported** | No court found, 3+ persons (doubles/crowd) *or* camera moving/cutting > 50 % *or* portrait/tiny | Nothing analysed; offer **footage-only** keep (no analysis), Record guide, try another video | Keep video privately; the file is not analysed |

"Try again" alone is never the only action (Blueprint §12). Doubles message: *"This looks like doubles. We can't analyse doubles responsibly yet — we'll tell you when we can. You can keep the video."*

### 5.5 States
| State | Behaviour |
|---|---|
| Probe running | Named stage "Looking for the court… Looking for players…", measured; no fake %. Cancel available |
| Probe failed (server) | "We couldn't check this just now. You can upload anyway — we'll check as it processes." |
| Offline | Record guide readable offline; "Check my video" disabled with reason |
| Oversize | "This video is 4.1 GB; this server accepts up to {max_upload_mb} MB." + options (trim on device, lower quality) — existing error wording from `LibraryPage.pick` |
| Portrait | "Turn the phone sideways next time — your video is portrait." Offered: continue with limits |
| Unsupported container | "We accept MP4, MOV, MKV or WebM." |

### 5.6 Accessibility
Diagram has a text alternative ("The phone sits two to three metres behind the middle of the baseline, held high, pointing at the whole court"); checklist items are real checkboxes (informational, not required); result states use icon + word + shape, never colour alone; drop-zone reachable by keyboard (existing `UploadCard` pattern).

### 5.7 Telemetry
`record_guide_viewed` · `record_guide_skipped` · `framing_item_expanded {id}` · `suitability_checked {mode}` · `test_clip_result {suitable|limited|unsupported, reasons[]}` · `upload_started_anyway {after: limited|unsupported}` · `discipline_selected {singles|doubles}` · `doubles_interest_logged`.

### 5.8 Acceptance
- **AC-ONB-13** A player can skip the guide in one tap and still reach upload.
- **AC-ONB-14** The probe/pre-check returns a result whose every "limit" names a *specific missing surface* and a *specific fix*.
- **AC-ONB-15** "Not supported" never dead-ends: Keep video, How to film, Try another are all present.
- **AC-ONB-16** Choosing Doubles shows the "Not yet" explanation and offers to log interest; it does not start a singles analysis silently.
- **AC-ONB-17** The consent reminder (opponents, venue) is visible on the guide *and* repeated at the consent step — it is not a single generic checkbox.

---

## 6. Step 5 — Choose video, consent cards, upload (`/matches/new`, steps 2–3)

### 6.1 Choose video

```
┌──────────────────────────────────────┐
│ ‹ Back        New match      (2 of 4)│
│  Add your video                      │
│  ┌ - - - - - - - - - - - - - - - - ┐ │
│  │      ⬆  Choose a video          │ │
│  │  MP4, MOV, MKV or WebM · up to  │ │
│  │  {max} MB                       │ │
│  └ - - - - - - - - - - - - - - - - ┘ │
│  Import from YouTube  ▸  (only if the│
│  server allows; own videos only)     │
│                                      │
│  Name this match (optional)          │
│  [ Sunday evening game        ]      │
│  Type: (•) Match  ( ) Social game    │
│        ( ) Practice                  │
└──────────────────────────────────────┘
```
Match type (D12): **Match (scored)** default; **Social game** and **Practice** are offered but, until the engine supports free play (**G-04**), they hide score-derived surfaces and the copy says so: *"We'll find your rallies and moments. We won't keep score."* Title defaults from the file name (existing behaviour: `name.replace(/\.[^.]+$/,"").replace(/[_-]+/g," ")`) and stays editable.

YouTube import: kept for parity (`YouTubeCard`), moved behind a disclosure; requires the existing rights acknowledgement; **not** shown on the landing path to avoid implying that analysing other people's matches is the core use.

### 6.2 `ConsentCards` — just-in-time, separated (D15)

Shown **once, when the file is chosen and before any bytes are uploaded.** Five cards, each its own toggle, each saying what it means in one sentence; the first two are *required to proceed*, the last three are *off by default*.

```
┌──────────────────────────────────────┐
│ Before we upload                     │
│ Four separate choices. Change them   │
│ any time in Privacy.                 │
│                                      │
│ ┌ Analyse this video          [ON ]┐ │  required
│ │ We find rallies, shots and       │ │
│ │ moments. Needed to do anything.  │ │
│ └──────────────────────────────────┘ │
│ ┌ Keep the video so I can watch [ON]┐│  required (can choose "delete after analysis" in Privacy)
│ │ Stored privately so Moments can  │ │
│ │ play. Only you can see it.       │ │
│ └──────────────────────────────────┘ │
│ ┌ Save my results to my history[OFF]┐│  optional
│ │ Lets Progress compare matches.   │ │
│ │ Without it, this match stands    │ │
│ │ alone.                           │ │
│ └──────────────────────────────────┘ │
│ ┌ Let me share selected moments[OFF]┐│  optional
│ │ Nothing is ever public. You pick │ │
│ │ each person and each clip.       │ │
│ └──────────────────────────────────┘ │
│ ┌ Help improve the product     [OFF]┐│  optional, separate
│ │ Allow us to learn from this      │ │
│ │ video to make analysis better.   │ │
│ │ Doesn't affect your results.     │ │
│ └──────────────────────────────────┘ │
│                                      │
│ ⓘ Everyone in the frame should know  │
│   you're filming, and the venue      │
│   should allow it.                   │
│ ⓘ Rally is for people 18 and over.   │
│                                      │
│ [ Continue ]    Read privacy details │
└──────────────────────────────────────┘
```

| Card | Default | Required | What changes if declined |
|---|---|---|---|
| Analyse this video | On | **Yes** | Nothing is analysed; offer "Keep the video only" (needs card 2) or cancel |
| Keep the video | On | **Yes** to watch Moments | If off: analyse then discard the video; Moments cannot play; Recap shows stats only; offered as "Delete after analysis" |
| Save to my history | **Off** | No | Match is analysed but excluded from Progress/Journey/Records; can be added later from the match |
| Share selected moments | **Off** | No | Share buttons are disabled with a one-line reason + "Turn on in Privacy" (never silently enabled) |
| Help improve the product | **Off** | No | No difference to the player; never bundled |

**Design rules** (Blueprint §13.2, v1 §6): consent to analyse never becomes consent to store, share or train; defaults conservative; **no dark patterns** — equal-weight accept/decline, no pre-ticked optional cards, "Continue" never labelled "Accept all". Required cards show *why required* and *what the alternative is*. The wording about people in the frame is specific, not a generic "I have everyone's consent" checkbox.

**Revocation:** every card shows what revoking does (Doc 10 §8). Policy version is recorded (`policy_version`) with each decision (v1 consent record).

**Legal/safety notes shown in "Read privacy details"** (plain language, then a link to the full policy; jurisdiction-specific legal review required — Blueprint §13.2): who processes the video; where stored; retention for original footage, derived clips, labels, reports, backups, logs; deletion/export; bystander removal requests; model-training reuse is a separate opt-in; adults only; no recording in changing rooms or sensitive spaces.

States: *Already decided on a previous match* → cards pre-filled with the saved defaults and collapsed to a one-line summary "Same choices as last time — Change"; **never** silently re-apply a *revoked* choice.

### 6.3 `UploadProgress` — honest, recoverable

Reuses the current `UploadCard` upload (XHR multipart, `uploadVideo(form, onProgress)` with abort) and `Meter`.

```
┌──────────────────────────────────────┐
│ Uploading "Sunday evening game"      │
│ ████████░░░░░░░░  48%  ·  1.1 / 2.3GB│
│ You can leave this page — keep the   │
│ tab open until it reaches 100%.      │  ← true for current XHR upload
│ [ Pause ]  [ Cancel ]                │
└──────────────────────────────────────┘
```

| State | What the player sees | Why / dependency |
|---|---|---|
| Queued/transferring | Real percentage from upload progress; "Uploading" vs "Checking video" (existing labels) | `uploadVideo` |
| Interrupted | "Connection lost at 48%." **[Resume]** (if resumable) or **[Start again]** with a plain explanation | Resumable upload = **G-ONB-1**; until then the Resume button is absent and copy says "We'll need to start again" |
| Mobile data | Before starting on a cellular connection: "This is 2.3 GB. Wait for Wi-Fi?" **[Upload now] [Wait for Wi-Fi]** (uses `navigator.connection` where available, else asks once) | Low-bandwidth consideration (§15) |
| Cancelled | "Cancelled. Nothing was kept." (or what *was* kept, truthfully) | v1 session lifecycle |
| Duplicate file | "You've already added this video — open it?" (SHA-256 exists in `source.sha256`; the media cache avoids re-encoding) | Prevent duplicates |
| Server error | Safe message + retry; never stack traces | v1 §6 |

After the transfer, status moves through the engine's states (see §10). The player is taken to **Pick yourself** as soon as the *video is playable* (`ready_to_play`), **not** when analysis ends.

### 6.4 Telemetry
`consent_viewed` · `consent_changed {purpose, value}` · `consent_optional_declined {purpose}` · `consent_continue` · `upload_started {size_mb, network_class}` · `upload_interrupted {at_pct}` · `upload_resumed` · `upload_cancelled` · `upload_completed {duration_s}`.

### 6.5 Acceptance
- **AC-ONB-18** Required and optional cards are visually and verbally distinct; the three optional cards are **off** on first use.
- **AC-ONB-19** Tapping Continue with only required cards on is a normal path with no warning copy.
- **AC-ONB-20** No bytes leave the device before Continue on the consent step.
- **AC-ONB-21** Decline of any optional card never blocks analysis or changes the quality of the recap.
- **AC-ONB-22** An interrupted upload shows the true state; no duplicate match is created on retry.
- **AC-ONB-23** The consent record stores purpose, status, timestamp, policy version for each card.

---

## 7. Step 6 — Pick yourself / Who is who (`PickYourself`, `WhoIsWho`)

**User's question:** "Does it know which one is me?" **Feeling:** this is the moment of *being seen* — the first time they watch themselves analysed. Embarrassment risk is highest here (Blueprint §3.4: first recording / watching oneself). Keep it private, instant and forgiving.

### 7.1 Why this step exists (engine reality)
The engine knows **tracks**: `PlayerId = "P1" | "P2"`; P1 starts on the **near** side, P2 on the **far** side; `session.players[].name` is free text set at upload (`player1`, `player2`). It has no concept of *the signed-in person*. D8 requires **"you" to be the anchor of every metric**, so the product must learn, once per match, **which track is the user**.

### 7.2 Flow
1. As soon as the video is playable, the server returns a **players frame**: a poster frame with the two tracked people (boxes from `/api/sessions/{id}/tracks` for the first frames where both are on court, or from the `RF-DETR` detections). Can be assembled today from `/tracks` + the HLS/sprite frame (**no new analytics needed**; a small helper endpoint is a convenience, **G-ONB-3**).
2. Show the frame with two tappable outlines, labelled only "Near side" / "Far side" (never "Player 1/2").
3. Prompt: **"Tap yourself."** → the chosen track becomes `me`. The other becomes "Opponent".
4. Optional second line: **nickname** for you (pre-filled from the guest/account display name) and for the opponent (optional; private to you).

### 7.3 Wireframe — mobile

```
┌──────────────────────────────────────┐
│ ‹ Back        New match      (3 of 4)│
│  Which one is you?                   │
│  Tap yourself on the picture.        │
│ ┌──────────────────────────────────┐ │
│ │                                  │ │
│ │        ┌─┐  far side             │ │
│ │        │ │  (opponent?)          │ │
│ │        └─┘                       │ │
│ │  - - - - - - - net - - - - - - - │ │
│ │              ┌──┐                │ │
│ │              │  │  near side     │ │
│ │              └──┘                │ │
│ └──────────────────────────────────┘ │
│  [ That's me (near) ] [ That's me (far)]│  ← buttons duplicate the tap for accessibility
│                                      │
│  Not sure — I'll pick later          │
│  I see 3–4 people ▸                  │
└──────────────────────────────────────┘

After tapping:
│  You're on the near side ✓           │
│  Your name for this match (optional) │
│  [ Alex          ]  ← nickname       │
│  Opponent (optional, only you see)   │
│  [               ]                   │
│  [ Looks right ]   Switch            │
```
**Desktop note:** picture 16:9 left, controls right; hover highlights the outline; click = tap.

### 7.4 Copy
| Element | Copy |
|---|---|
| Title | Which one is you? |
| Helper | Tap yourself on the picture. We use this to tell you what *you* did. |
| Confirm | You're on the near side. Looks right? |
| Nickname label | What should we call you? *(you can use a nickname)* |
| Opponent label | Opponent *(optional — only you see this)* |
| Deferral | Not sure — I'll pick later. We'll show moments from both players until you do. |
| Privacy line | Names stay on your account. They're never added to a shared clip unless you choose. |

### 7.5 "What if I got it wrong?"
- **During the flow:** "Switch" flips the mapping instantly.
- **After analysis:** the match header shows "You: near side · Change". Changing remaps `me` and **recomputes the "you" views**; underlying events are unchanged (the engine tracks are fixed), so nothing is re-analysed. A `ChangeSummaryBanner` states what changed ("Your Moments now show the far-side player").
- **If the identity switched mid-match** (tracker ID flip, likelier from side-on or crowded footage — Blueprint §17): Review & fix lists "Player labels may have swapped around 14:32" with **[Watch this]** and **[Swap from here]** (needs *identity segment correction*, **G-ONB-4**; until then show "Worth a look" and exclude the affected rallies from *you*-attributed metrics, never guess).
- If the player picks "I'll pick later", Recap shows moments from both players with a "Which one is you?" card at the top; nothing is attributed to "you" and **no personal best or First is issued** until chosen.

### 7.6 Edge cases
| Case | Behaviour |
|---|---|
| Only one person detected | "We can only see one player. Is the other one out of frame?" → fixes from Record guide; continue with limits |
| 3–4 people (doubles / bystanders) | "We can see more than two people. Rally analyses singles. Pick the two players, or save the video for when doubles arrives." Bystander picks are supported (select 2 of N); selection feeds the track whitelist (**G-ONB-5**) |
| Both players on the same side / fixed side-on camera | Label by left/right instead of near/far; explain "from the side" |
| Players change ends | Engine handles `side_switch`; mapping is by track, not side — copy never promises a side beyond the first rally |
| Photo not representative (empty court) | "Pick another moment" scrubs to the next frame with both players (arrow buttons) |

### 7.7 Privacy and naming
- Nicknames are the display label everywhere; the real name is never required.
- The **opponent's nickname is private to the owner**; it is not stored on the opponent and not shown on shared artefacts without that person's consent (Doc 10 §7).
- Do **not** infer age, gender or any attribute from the picture. Do not label the people in the frame automatically. The frame is not saved as a thumbnail of the player's face without consent — use a **court-replay silhouette** thumbnail for Matches and Moments by default; real frames only inside the private player.

### 7.8 States
Loading: skeleton frame + "Finding the players…"; Detection failed: "We couldn't find the players yet. Try another moment ▸" (scrub), fallback "Skip — I'll pick later"; Offline: queued choice with "Saved on this device — we'll sync when you're back".

### 7.9 Accessibility
Tap targets ≥ 44 px; outlines + labels ("Near-side player"); the two buttons duplicate the tap for screen-reader and switch users; focus moves to the confirmation on selection; live region announces "You're the near-side player".

### 7.10 Telemetry
`pick_yourself_shown` · `pick_yourself_completed {side}` · `pick_yourself_deferred` · `pick_yourself_switched {before_analysis|after}` · `who_is_who_edited {field}` · `more_than_two_people_detected {n}`.

### 7.11 Acceptance
- **AC-ONB-24** The player can finish this step with one tap and no typing.
- **AC-ONB-25** Until "me" is chosen, no metric or milestone is attributed to the player.
- **AC-ONB-26** Changing "me" later updates every "you" surface without re-running analysis and says what changed.
- **AC-ONB-27** Names are optional; the UI works entirely with "You" and "Opponent".
- **AC-ONB-28** The opponent's nickname is not displayed on any shared artefact by default.

---

## 8. Step 7 — Place your court (`PlaceYourCourt`) — replaces `/sessions/$id/calibrate`

**User's question:** "Is that my court?" **Feeling:** wants it to *just work*; will abandon a technical-looking page (the current page asks for 4–10 clicks with a loupe — an expert tool).

### 8.1 What exists and what changes

| Today | In the production prototype |
|---|---|
| Page asks the player to click `near_left, near_right, far_right, far_left` (required) + 6 optional points, with a 3× loupe and undo | **Default: automatic.** Proposal from `GET /api/sessions/{id}/calibration/proposal?segment=` (court detected from the exact frame's lines) shown as an overlay. The player taps **"That's the court"** (1 tap). |
| Header shows "Calibrate court" / "Court: auto" / "Court: set + tracked" | Replaced by a friendlier status: **Court placed ✓** or **Court needs a look** |
| "Re-detect automatically for the whole video" (`POST /calibration/auto`) is a secondary action | It is the **primary background action** after the first tap |
| Manual clicks for everyone | Manual drag-handles **only on failure or on request**, reusing the existing loupe + `fitHomography` + reprojection error |

### 8.2 Flow (decision tree)

```
video playable
   │
   ├─ proposal found, quality ok  ──► show overlay ──► [That's the court] ──► POST /calibration (accept) ──► POST /calibration/auto (whole video, background)
   │                                         └─► [Adjust] ──► drag handles (4 corners) ──► save
   │
   ├─ proposal found, quality low (precision 0.6–0.8 / area small) ──► overlay + "Check the lines" ──► Adjust or Accept
   │
   ├─ no court found ──► explain why (dark / lines faded / blocked / moving camera) ──► [Place it by hand] (4 corners, big handles) or [Try another moment] or [Skip for now]
   │
   └─ camera moves / cuts (broadcast-like) ──► "This video changes cameras — we follow the main one." (info, no action)
```

### 8.3 Wireframe — auto success (mobile)

```
┌──────────────────────────────────────┐
│ ‹ Back        New match      (4 of 4)│
│  Is this your court?                 │
│ ┌──────────────────────────────────┐ │
│ │   ╱ ─────────────────────── ╲    │ │
│ │  ╱  court lines drawn on     ╲   │ │
│ │ ╱   the video frame (teal)    ╲  │ │
│ │ ╲___________net______________╱   │ │
│ │  ◉ corner handles hidden until   │ │
│ │    you tap Adjust                │ │
│ └──────────────────────────────────┘ │
│  Playing singles? We'll use the inner│
│  side lines for in/out.              │
│                                      │
│  [ That's the court ]                │
│  Adjust the lines   ·  Try another   │
│  moment                              │
└──────────────────────────────────────┘
```

### 8.4 Wireframe — manual fallback

```
│  Place the court corners             │
│  Drag each corner onto the court's   │
│  outer line. Zoom shows exactly where.│
│ ┌──────────────────────────────────┐ │
│ │  ①────────────────────────②     │ │
│ │   ╲        net               ╱  │ │
│ │  ④──────────────────────────③   │ │
│ │   ┌────┐  ← loupe 3× at finger  │ │
│ └──────────────────────────────────┘ │
│  Corner 2 of 4 · Undo · Reset        │
│  Sharper results (optional): net     │
│  posts, short service line ▸         │
│  [ Save court ]  (enabled at 4)      │
```
Required: the **four corners**. The six extra points in today's `ORDER` become one optional "Sharper results" disclosure.

### 8.5 Quality gate and wording (from the existing calibration record)

| Signal (existing field) | UI wording |
|---|---|
| `quality.precision` ≥ 0.8 and `support` ≥ 0.9 | **Court placed ✓** |
| `precision` 0.6–0.8, or `adjusted_px` > 3 % frame width | **Court placed — worth a quick look.** Heatmaps and "where shots went" will be rough. |
| `mode: "lines"` | (no extra copy; "We follow the lines through the video") |
| `mode: "camera"` | "We follow the court as the camera moves." |
| `mode: "static"` | "One court placement for the whole video." |
| no calibration after ≥ 30 s of analysis (existing banner condition `analysingLong`) | **"We couldn't find the court automatically."** + Place it by hand |
| scene `alt` / `none` | **"Other camera — not followed"** / **"No court in view here"** with the reason; only shown if present (broadcast uploads) |
| `lines_check` text | Shown under "Details" for Advanced depth only |

### 8.6 What it unlocks — in plain words

> **Placing the court lets us measure where things happened.** Without it you still get your rallies and Moments.

| With the court placed | Without it |
|---|---|
| Where you stood (relative heatmap) *[Preview]* | Not shown |
| Where shots went *[Preview]* | Not shown |
| In/out for the shuttle *(Preview; judged against singles lines for singles)* | Winner/loser may be less reliable → more "Worth a look" |
| Distance in metres | **Not yet** at all, with or without the court |
| Rallies, Moments, shot count in a rally | **Available** either way |

Skip is allowed: **"Skip for now — I just want my moments."** The match analyses; a persistent but quiet `ReviewBanner` offers "Place the court to unlock heatmaps" (no nagging; dismissible per match).

### 8.7 Interactions and validation
- Handles: drag, or arrow keys with 1 px / 10 px (Shift) steps; double-tap handle to reset.
- Validation: reprojection error computed with `reprojectionError`; if corners form a non-convex quad or reproject > threshold, show "That shape doesn't look like a court — check the corner order." Save disabled until valid.
- Singles vs doubles lines: the overlay shows **which** lines will be used; changing the match discipline updates it.
- "Try another moment" requests the proposal for another `segment` / frame.
- **Back** keeps placed points; **Cancel** keeps the previous calibration.
- Acceptance writes the calibration (`POST /calibration`, `202`), then **starts** analysis; the whole-video line tracking runs via `POST /calibration/auto` in the background.

### 8.8 States
Loading proposal: skeleton + "Looking for the court lines…" (measured); proposal timeout: manual fallback; permission/offline: draft kept; mid-analysis re-place (from the Recap header "Court ✓ · Change"): shows "Changing the court re-measures positions — your rallies stay." and offers a re-analysis (existing "Analyse again").

### 8.9 Accessibility
Overlay is also described in text ("Court found; corners at near-left… quality good"); handles have labels ("Near-left corner handle, use arrow keys to move"); loupe is decorative with the exact coordinates readable; no gesture needs precision beyond handle size (≥ 44 px hit area).

### 8.10 Telemetry
`court_proposal_shown {quality}` · `court_auto_accepted` · `court_adjusted {n_handles_moved}` · `court_manual_started` · `court_failed {reason}` · `court_skipped` · `court_changed_after_analysis`.

### 8.11 Acceptance
- **AC-ONB-29** On a suitable video the player completes this step with **one tap** and no manual point placement.
- **AC-ONB-30** If no court is found, the explanation names a likely cause and a fix, and manual placement requires exactly four corners.
- **AC-ONB-31** The copy never says "homography", "reprojection" or "calibration" outside Advanced detail.
- **AC-ONB-32** Skipping the court never blocks Moments or the rally list.
- **AC-ONB-33** The overlay states whether singles or doubles lines are used.

---

## 9. Step 8 — Ready-to-start summary, then Processing

### 9.1 Ready-to-start (3 s, one tap)
A confirmation card summarising choices — it is the **second consent moment** the player can *see* (not a new question):

```
│  Ready to analyse                    │
│  Sunday evening game · Singles       │
│  You: near side (Alex)               │
│  Court: placed ✓                     │
│  ✓ Analyse   ✓ Keep video            │
│  ✗ History   ✗ Sharing   ✗ Improve   │
│  [ Start analysing ]  Edit           │
```
"Edit" jumps to the relevant step. This is also where the **preset/purpose chips** are visible and editable. If the court was skipped: "Court: skipped — heatmaps won't be available. [Place it now]".

### 9.2 Engine states → player-facing stages (`ProcessingStages`)

The engine's status is `created | ingesting | ready_to_play | analysing | analysed | failed`, with `frontier_frame` / `n_frames` (progress), `rate_x` (× real time), `lead_ms`, `degraded[]` (`{stage, reason}`), and `ingestProgress` while ingesting. The UI must **never invent a percentage or an ETA** (Blueprint §7.5). Percentage shown is exactly `(frontier_frame+1)/n_frames` as the current header computes, and rate is `status.rate_x`.

| Engine state | Stage label (player) | What's shown | Watchable? |
|---|---|---|---|
| `created` | **In the queue** | "Waiting for a free slot." No %. | No |
| `ingesting` | **Getting your video ready** | `ingestProgress` as a real bar | No |
| `ready_to_play` | **Ready to watch — finding rallies** | Video player appears; empty Moments with skeletons | **Yes** |
| `analysing` | **Finding rallies and shots** | `{pct}% of the video · {rate_x}× real time`; named checklist below | **Yes** (events stream in) |
| `analysed` | **Done** | Normal Recap | Yes |
| `failed` | **Couldn't finish** | `status_detail` rewritten safely + what was saved + **Analyse again** / **Keep video** / **Report** | Partial if any |

Named checklist (derived from real events, not a timer):

| Item | Marked done when |
|---|---|
| Video ready | `status ≥ ready_to_play` |
| Court and players found | a `calibration` event exists **and** tracks exist (or "skipped") |
| Rallies found | ≥ 1 `rally_end` event (count shown: "12 so far") |
| Moments picked | `highlight` events exist (count) |
| Score checked | match phase `official` resolved or "not scored" (match type) |

### 9.3 The progressive advantage — design around it
The engine lets the video **play as soon as the first segment is prepared** while shots, rallies and score "fill in while you watch" (current Library copy). This is a real differentiator: **the player's wait becomes watching**. Therefore:

- At `ready_to_play` the **Recap page opens**, not a spinner page. The video plays; a quiet progress strip shows "We've followed 3 of ~14 min — more moments appear as we go."
- **Moments arrive one by one** into `MomentStrip` (no layout shift; reserved slots with skeletons; new arrivals get a brief highlight, no sound).
- The frontier limits what is *claimed*: only events at or before the frontier **and** past the engine's semantic lead (3 s today; the roadmap says too short with OCR wait) are shown; provisional events are labelled "Still checking" and **excluded** from counts and records.
- The player can leave: *"You can leave this page — we'll keep going."* shown **only** once the product has confirmed that processing persists server-side (a verified capability; otherwise show "Keep this tab open until it's done").
- **"Tell me when it's ready"** appears only if the projected remainder > ~2 min *and* the player taps it; this is the first (and only) moment a notification permission or email channel is requested (D9; Blueprint §11.3). Default channel: in-app + email; push never requested here.

### 9.4 Wireframe — processing as part of the Recap (mobile)

```
┌──────────────────────────────────────┐
│ Sunday evening game      ● Analysing │
├──────────────────────────────────────┤
│ ┌──────── video ──────────────────┐  │
│ │ ▶  (plays now)                  │  │
│ └─────────────────────────────────┘  │
│ We've followed 6 of 18 min · 2.4×    │
│ real time.  Tell me when it's ready  │
│ ▢ Video ready                        │
│ ▢ Court and players found            │
│ ▢ Rallies found (7 so far)           │
│ ▢ Moments picked                     │
│                                      │
│ Your moments so far                  │
│ [ 11-shot rally ] [ ░░░ ] [ ░░░ ]    │
│                                      │
│ You can leave this page — we'll keep │
│ going.                               │
└──────────────────────────────────────┘
```

### 9.5 Partial, failed and degraded states
| State | Copy | Next action |
|---|---|---|
| Partial analysis | "These parts were analysed. These weren't, because the camera changed (6:10–8:40)." (from `scene` events) | Open what's available; re-film gaps |
| `degraded[]` present | "Some parts have reduced detail: shot types unavailable while the player was hidden." (`degraded.map(stage, reason)` rewritten) | None needed |
| No court after 30 s | Same banner as §8 | Place the court |
| Failed | "We couldn't finish. {safe cause}. Your video is safe." | **Analyse again** (existing `reanalyse`), Keep video, Report |
| Interrupted socket | `Reconnecting` pill (existing); data on screen is not cleared | Auto |
| Stalled > 3× expected | Honest message: "This is taking longer than usual." — no new estimate invented | Keep waiting / Notify me / Cancel |

### 9.6 Telemetry
`analysis_started` · `analysis_stage_reached {stage}` · `processing_left_page {at_pct}` · `notify_me_tapped` · `analysis_partial {reason}` · `analysis_failed {code}` · `analysis_completed {duration_s, rate_x}` · `first_moment_arrived {t_since_start_s}`.

### 9.7 Acceptance
- **AC-ONB-34** No progress percentage or ETA appears that is not derived from `frontier_frame/n_frames` or `rate_x`.
- **AC-ONB-35** The Recap opens at `ready_to_play`; the player can watch while analysis continues.
- **AC-ONB-36** Provisional events never contribute to counts, records or the hero Moment.
- **AC-ONB-37** Notification permission/email is requested only after "Tell me when it's ready" is tapped.
- **AC-ONB-38** A failed analysis states what was saved and offers at least two next actions.

---

## 10. Step 9 — First value reveal (`HeroMoment` + `FirstValueReveal`)

**User's question:** "What did I get?" **Feeling:** the emotional peak — pride, curiosity, a little dread about being judged. The reveal must be *specific, kind and true*.

### 10.1 What the reveal is
**One Moment, played in-place, within seconds of the first reliable one existing** — not a dashboard. Under it: **one verified positive thing about *you***, a **sentence of context**, and **one way out** ("Watch this"). No metric wall, no "weakness", no streak, no score headline (D6, D17).

### 10.2 Selection rule for the *first* hero (D17 applied; full ranking in Doc 06 §7)
1. Eligible = rallies with `status ∈ {confirmed, human_verified, corrected}` **and** band `confirmed`, **attributed to a track that is "me"** (or both, if "me" is deferred).
2. Candidate kinds in order of *first-reveal safety*: **your longest rally in this match** → **a rally you kept alive after a hard position** (long, defensive shots by you) → **a close-score rally** (only if the score is Checked) → **a rally with variety** (many distinct shots, Preview-tagged).
3. **Never** pick on winning alone. **Fairness:** if the player lost the match or the point, the hero is still chosen by the rules above; the copy does not mention the result.
4. **Eligible-minimum:** a rally of ≥ 6 shots with ≥ 3 shots by the player. Below that → no hero; use §10.4.

### 10.3 Wireframe

```
┌──────────────────────────────────────┐
│ Here's one worth replaying           │
│ ┌──────── HeroMoment ─────────────┐  │
│ │ ▶ [clip autoplays muted 1 time, │  │
│ │    then waits; reduced-motion:  │  │
│ │    poster only]                 │  │
│ │ A 12-shot rally                 │  │
│ │ You kept this one alive —       │  │
│ │ watch the recovery at the end.  │  │
│ │ Looks right ✓ · Watch this      │  │
│ │ ♡ Keep  ·  Share ▸ (off)        │  │
│ └─────────────────────────────────┘  │
│ This is your longest rally in this   │
│ match so far.                        │
│                                      │
│ What next?                           │
│  [ Keep this moment ]                │
│  [ See my game ]                     │
│  [ Something looks off — fix it ]    │
│  I'm done for now                    │
└──────────────────────────────────────┘
```

### 10.4 When there is no reliable moment
Never invent one (D17, v1 global rules). Instead:

| Situation | What we show |
|---|---|
| Rallies found but none ≥ 6 shots with clear attribution | "We found 14 rallies but none we can describe confidently yet. Here are the three longest — take a look and **tell us which one you remember.**" → manual pick lets the player **create a Moment** from any rally |
| Court/players failed | "We couldn't follow this video well enough to pick a highlight. You can still watch it and **save any moment yourself.**" (scrub + **Save this as a Moment**) + fix tips |
| Still analysing, none yet | Skeletons + "We'll pop the first one in here as soon as we find it." |
| "Me" not chosen | Show the best moment per player, side by side, with "Which one is you?" on top |
| Doubles-like footage | "Doubles Moments are coming. For now we can't pick them reliably." + manual Moment creation |

### 10.5 Copy templates (conditional wording; Doc 09 owns the full set)
- "You kept this rally alive for **{n} shots**. Watch the recovery at the end."
- "This is the longest rally in this match **so far**." (while analysing) / "…in this match." (after)
- "A new **personal best** — your longest rally in a match." — **only** if history is saved, comparable, and ≥ 1 prior match exists; **otherwise nothing** (first match = baseline: "Your first match is your baseline").
- Never: "Amazing! You're becoming elite!", "You dominated", confetti on a win.

### 10.6 Checking the hero (Review & fix, lightly — D11)
Under the Moment, one optional line: **"Is this the rally you remember?"** [Yes] [Not quite]. *Yes* upgrades the event to `human_verified`; *Not quite* opens `FixSheet` with three questions max (wrong rally boundary / wrong player / not a rally). This is the player's first correction experience and must feel like helping, not auditing. Telemetry: `review_prompt_shown`, `review_confirmed`, `review_fix_opened`.

### 10.7 Next step (`NextStepRow`) — "Keep the moment / Understand the pattern / Try something next / Finish" (Blueprint §7.3 step 8)

| Option | Result |
|---|---|
| **Keep this moment** | Saved to My Moments; if "save to history" was off, a one-line reminder "This stays only on this match" |
| **See my game** | Scrolls to My game section (one strength, coverage, optional opportunity if purpose = practise/understand) |
| **Something looks off — fix it** | Review & fix queue limited to what the recap shows |
| **I'm done for now** | Closes with a neutral "Your recap is saved. Come back whenever." — **no** streak, reminder or rating ask; offers (once) "Keep this safe — add an email" (§14) |

### 10.8 Telemetry
`first_insight_viewed` · `hero_moment_viewed {kind}` · `hero_moment_played` · `hero_moment_saved` · `hero_none_reason {reason}` · `next_step_chosen {option}` · `recap_useful {yes|no}` (a single, dismissible "Was this useful?" — never blocking).

### 10.9 Acceptance
- **AC-ONB-39** Time-to-first-hero is measured (target: report p50/p90; no promise in UI).
- **AC-ONB-40** The hero is never chosen on winning alone and never contains a result headline.
- **AC-ONB-41** If no reliable moment exists the screen says so, explains why in plain words and offers manual Moment creation.
- **AC-ONB-42** "A new personal best" never appears on a first match.
- **AC-ONB-43** The hero can be kept, fixed or dismissed in ≤ 2 taps; every option is optional.

---

## 11. Returning users and "resume after a break"

### 11.1 Returning (played recently, has data)
Home (`/`) hierarchy (Doc 04 §9): (1) the thing in progress ("Your Sunday game is ready" / "Sunday game: analysing 64 %"), (2) latest meaningful Moment, (3) current Focus if chosen, (4) a progress signal only if ≥ 2 comparable matches, (5) Explore collapsed. **No** greeting that assumes ("Welcome back!" is fine; "You've missed 6 days" is not).

### 11.2 Resume after a break (≥ 3 weeks since last match, or the player taps "I haven't played in a while")
Blueprint §3.4/§11.4; v2 "Returning after a break" row.

| Rule | Behaviour |
|---|---|
| Tone | "Good to see you. Resume with one match." |
| Baseline | Offer **"Start a fresh baseline"** (keeps history, compares only new matches) *and* "Compare with before" — default **fresh baseline**, no regression alarm |
| Forbidden | "You broke your streak", "You're behind", old-peak comparisons, "we miss you" campaigns |
| Allowed | Review old matches without recording new data; export/pause/delete |
| Reminders | None by default; one *user-set* reminder only |
| Copy | "Welcome back. Your moments are all here. Want to start fresh with your next match, or keep comparing with before?" |

Telemetry: `resume_after_lapse {days_away}` · `fresh_baseline_chosen` · `compare_with_before_chosen`.

### 11.3 Re-onboarding / changing preset, purpose, depth later
- **Where:** match header `PresetSwitcher` + `DepthSwitcher` + `PurposeChips` (always visible on the Recap, Blueprint §8.16); Settings → Preferences for defaults.
- **Rule:** a change is **per match first**, then "Make this my default?" (a one-time inline offer after the 2nd change — not a modal).
- **Always visible:** "Shown because you chose *Understand my game*. **Change · Reset · Show all**" (Blueprint §3.2 mandatory line).
- **Never** a re-run of onboarding; a "Take the quick tour again" link lives in Help and re-opens the **sample**, not the questions.
- Changing preset changes **order, wording and density only** — never the facts shown or the evidence standard (D2).
- Telemetry: `preset_changed {from,to,scope: match|default}` · `purpose_changed` · `depth_changed`.

---

## 12. Invite flow — a partner opens a shared link (`/s/$token`)

**Hypothesis:** the strongest organic growth in a recreational sport is *"look at this rally"* sent to the person you played with (to be validated, Doc 12). The invite must be **consent-first and view-only first**.

### 12.1 What the recipient sees (no account needed)

```
┌──────────────────────────────────────┐
│ ◇ Rally                              │
│ Alex shared a moment with you        │
│ ┌────────── clip (muted) ─────────┐  │
│ │ ▶ A 12-shot rally               │  │
│ └─────────────────────────────────┘  │
│ From "Sunday evening game".          │
│ Only you and Alex can see this.      │
│ Link expires 14 Jun.                 │
│                                      │
│ Are you in this clip?                │
│  [ That's me ]   [ Not me ]          │
│                                      │
│ Make your own moments  →             │
│ Don't want this?  Report / Remove me │
└──────────────────────────────────────┘
```

| Rule | Behaviour |
|---|---|
| Access | Tokenised, expiring, revocable; **view-only**; no download unless the owner allowed it |
| Identity | "That's me" is *self-claimed* and marks the opponent/partner label as claimed-by-link-holder; it **does not** merge accounts or reveal the owner's other matches |
| Their consent | The recipient can **ask to be removed** from the clip/blurred (Doc 10 §7); this is one tap and the owner is told "Someone in this clip asked to be removed" *without naming them if they didn't claim* |
| Their own analysis | "Make your own moments" → `/welcome` (guest), not auto-account |
| Pair memory | Only after the recipient has their own account **and** both accept an explicit "Link as partners" prompt (Doc 05c, Doc 10) — **Not yet** while doubles is Not yet; singles opponents can still be invited |
| What the owner sees | `InviteLink` list with expiry/revoke; never a vanity "N views" count by default |
| Funny/embarrassing clips | Cannot be shared without per-clip approval (D15) |

### 12.2 Telemetry
`invite_created {audience}` · `invite_opened` · `invite_claimed_me` · `invite_removal_requested` · `invite_to_start`.

### 12.3 Acceptance
- **AC-ONB-44** A shared link works with no account, is view-only, and clearly states who can see it and when it expires.
- **AC-ONB-45** The recipient can request removal in one tap, and the request reaches the owner.
- **AC-ONB-46** No link is ever public/indexable by default.

---

## 13. Account creation timing — guest-first

**Today:** a single shared passphrase (`BAI_PASSPHRASE`) for the whole server; no user accounts. **Production:** the player can complete the *entire* first run — sample, upload, recap, save a Moment — **as a guest**.

| Moment | Account prompt? | Copy |
|---|---|---|
| Landing, sample, questions, record guide, upload, processing | **No** | — |
| First value reveal / "I'm done for now" | **Soft, once** | "Keep this safe. Add an email so you can find your moments on another device. Skip — they're stored on this device for 30 days." *(30 days = hypothesis; policy to be set)* |
| Tapping **Share** | **Required** (to own the link and revoke it) | "To share safely we need to know it's yours — add an email." |
| Turning on "Save my results to my history" | **Required** | "History lives in an account so only you can see it." |
| Opening on a second device | Required | OTP/magic-link; no password creation |
| Account method | Email magic link or phone OTP (market-dependent, Q2); **no password**, no social login required | — |
| Guest data lifecycle | Guest data is owned by a device-bound token; on account creation it is **claimed**, not copied; abandoned guest data auto-deletes after the stated window | Doc 10 retention |

**Never:** gate the sample, gate the first upload, or require a name, age, phone or photo. **Do not** claim an account was created if the flow is simulated (v1 §2).

Acceptance: **AC-ONB-47** a guest can reach and keep a first Moment without an account; **AC-ONB-48** any prompt states the exact reason and offers a no-account alternative where one exists.

---

## 14. Empty-state and no-footage variants

| Where | Variant | Content |
|---|---|---|
| Home — brand-new | "Your game starts here." | **See the sample** (primary) · **Add my first match** · Record guide · no metrics, no charts |
| Home — has footage prompt but none processed | "Your video is being prepared" | Real `ProcessingStages` |
| Matches — empty | "No matches yet." | Add a match; sample link |
| Moments — empty | "Moments appear after your first match. They're the rallies worth replaying." | Add a match; "How Moments are chosen" (Help) |
| Progress — < 2 comparable matches | "Your first match is your baseline." | Shows that match's baseline facts; **no trend chart** (v1 §20) |
| Together — empty / doubles not yet | "Doubles and partner memories are on the way. For now, share a moment privately." | Share (needs account) |
| **No footage at all** | "Don't have a video yet? That's fine." | **How to film it** (Record guide) · **See the sample** · optional **Remind me before my next game** (user-set, opt-in, one reminder) · "I'll film next time" (neutral dismiss) |
| Player lost the match | Same recap, same options. No celebratory or consoling copy specific to the result | D6/D17 |

Rules: empty states never show fake data, never blame the player (v1 §4), always offer exactly one primary next step.

---

## 15. Localisation, low bandwidth and data-light considerations

| Concern | Decision |
|---|---|
| **Hypothesis (validate, Q2)** | First market may be India: large video files on mobile data, WhatsApp-first sharing, courts in apartments/academies/clubs, multilingual users. These are **assumptions to test in research (Doc 12)**, not facts |
| Copy | All strings externalised (ICU message format); plan for +40 % length; avoid idioms ("worth replaying" is acceptable but test), no puns in claims; Hindi and a second Indian-language pilot are candidates, validated by native players, not machine translation alone |
| Numbers/dates | Locale formatting; `tabular` numerals preserved; 12/24 h per locale; units metric |
| Fonts | Archivo has no Devanagari — define a Noto Sans fallback stack in Doc 08; test line-height and baseline alignment of numerals |
| Bandwidth | Landing ≤ ~300 KB before the embed; the embed loads on demand; Data-saver mode (detected or toggled in Accessibility) → still frames instead of loops, lower-res previews (clearly labelled *preview quality*, Blueprint §10.10) |
| Upload size | Pre-check warns before a multi-GB upload; on-device trim (start/end) offered **before** upload (gap **G-ONB-6**, use `<video>`+`MediaRecorder`/WebCodecs only if feasible; else server-side trim after upload); "Wait for Wi-Fi" option; resumable (G-ONB-1) |
| Offline | Record guide and previously loaded recaps readable; queued decisions sync later; honest `OfflineState` |
| Low-end devices | No heavy canvas on first run; overlays off by default; court overlay is a static SVG during PlaceYourCourt |
| Right-to-left | Layout mirrors; court diagram and video controls do **not** mirror (they are spatial) |
| Time-zone/locale on shared links | Expiry shown in the viewer's locale |

---

## 16. Instrumentation, experiments and success measures

### 16.1 Event taxonomy (extends Blueprint §14.3)
Full list added by this file: `landing_viewed`, `example_opened`, `purpose_card_opened`, `landing_cta_clicked`, `sample_opened`, `sample_depth_changed`, `sample_evidence_opened`, `sample_fix_opened`, `sample_completed`, `sample_exit_to_start`, `purpose_selected`, `purpose_skipped`, `preset_selected`, `preset_skipped`, `start_exit`, `record_guide_viewed`, `record_guide_skipped`, `framing_item_expanded`, `suitability_checked`, `test_clip_result`, `upload_started_anyway`, `discipline_selected`, `doubles_interest_logged`, `consent_viewed`, `consent_changed`, `consent_optional_declined`, `consent_continue`, `upload_started`, `upload_interrupted`, `upload_resumed`, `upload_cancelled`, `upload_completed`, `pick_yourself_shown`, `pick_yourself_completed`, `pick_yourself_deferred`, `pick_yourself_switched`, `who_is_who_edited`, `more_than_two_people_detected`, `court_proposal_shown`, `court_auto_accepted`, `court_adjusted`, `court_manual_started`, `court_failed`, `court_skipped`, `court_changed_after_analysis`, `analysis_started`, `analysis_stage_reached`, `processing_left_page`, `notify_me_tapped`, `analysis_partial`, `analysis_failed`, `analysis_completed`, `first_moment_arrived`, `first_insight_viewed`, `hero_moment_viewed`, `hero_moment_played`, `hero_moment_saved`, `hero_none_reason`, `review_prompt_shown`, `review_confirmed`, `review_fix_opened`, `next_step_chosen`, `recap_useful`, `resume_after_lapse`, `fresh_baseline_chosen`, `compare_with_before_chosen`, `preset_changed`, `purpose_changed`, `depth_changed`, `invite_created`, `invite_opened`, `invite_claimed_me`, `invite_removal_requested`, `invite_to_start`, `account_prompt_shown`, `account_created`, `account_prompt_dismissed`, `harm_signal`.

**Required context on every event** (Blueprint §14.3): app/report version, match type, discipline, analysis coverage, device/network class, experiment assignment. **Minimise personal data:** no names, nicknames, frame images or file names in telemetry; share events record audience *type* only.

### 16.2 Funnel and measures
Primary: **activation rate** = % of first matches where the player *saves a Moment or correctly states a finding* (teach-back in research; proxy in analytics: `hero_moment_saved` or `review_confirmed`). Report separately: sample funnel (expectation comprehension) vs personal funnel; time-to-first-value split into **active effort** vs **wait**; include non-completers.

| Metric | Definition |
|---|---|
| Active-effort time | Sum of foreground interaction time from file-chosen to analysis-started |
| Time to first hero | `first_moment_arrived` − `analysis_started`; p50/p90 |
| Usable-footage rate | % of uploads rated Suitable or Usable-with-limits |
| Court one-tap rate | % who accept the auto proposal unchanged |
| Pick-yourself first-time-correct | % who never switch afterwards |
| Consent opt-in rates | per optional card, with **no** target to maximise |
| Abandon points | step with the largest drop, with reasons from short optional exit chips |

**Guardrails (reject a variant even if engagement rises):** confusion, pressure/embarrassment reports, privacy concern, consent-comprehension failures, notification opt-outs, any growth in unsupported-footage uploads caused by hiding the guide.

### 16.3 Hypotheses and experiments (aligned with Blueprint §16.3)

| ID | Hypothesis | Comparison | Primary outcome | Guardrail |
|---|---|---|---|---|
| **H-ONB-1** | A sample recap before any question reduces expectation mismatch and raises personal activation | Sample-first vs direct upload | Correct teach-back of benefit + limit, then activation | Over-promise, abandonment |
| **H-ONB-2** | A skippable purpose question improves perceived fit without hurting completion | Question vs neutral default | Perceived/confirmed value | Setup drop-off, stereotyping |
| **H-ONB-3** | A short Record guide + 10-s probe raises the usable-footage rate | Guide+probe vs existing instructions | Usable-recording rate | Burden, exits at guide |
| **H-ONB-4** | Auto court placement with a one-tap confirm beats manual clicking | Auto+confirm vs manual 4-click | Completion, time, court quality | Wrong auto-accepts (measured vs reference) |
| **H-ONB-5** | "Tap yourself" before analysis gives more relevant first Moments than naming at upload | Pick-yourself vs text names | Hero relevance rating, switch rate | Mis-selection |
| **H-ONB-6** | Just-in-time consent with separated cards improves consent comprehension vs a signup wall | JIT cards vs upfront wall | Teach-back of "who can see my video" | Opt-in manipulation, drop-off |
| **H-ONB-7** | Watching while analysing (progressive Recap) reduces perceived wait and abandonment vs a wait screen | Progressive vs processing page | Abandon rate during analysis; satisfaction | Misreading provisional results |
| **H-ONB-8** | A hero Moment first (no metrics) yields more saves and better comprehension than stats-first | Moment-first vs stat-first | Save rate + teach-back | Time, "so what?" |
| **H-ONB-9** | Guest-first with a soft account prompt after value gets more first matches completed than sign-up-first | Guest vs sign-up wall | Completion of first match | Data loss, abuse |
| **H-ONB-10** | "Resume with one match" and a fresh baseline outperforms progress-loss framing for reactivation | Neutral vs loss framing | Return to meaningful action | Guilt, pressure |
| **H-ONB-11** | A "Fix this" prompt on the hero builds trust more than hiding uncertainty | Prompt vs none | Seeded-error detection, trust calibration | Burden |
| **H-ONB-12** | Wait-for-Wi-Fi + trim-before-upload lifts upload completion on mobile data | Offered vs not | Upload completion | Confusion |

Each experiment pre-registers its primary outcome, minimum worthwhile effect, guardrails, assignment unit and stopping rule (Blueprint §14.4). **Stop** any experiment that raises harmful advice, privacy concern or guilt even if engagement rises.

---

## 17. Dependencies and gaps this file creates (to be numbered in Doc 11)

| Handle | Need | Why | Fallback until built |
|---|---|---|---|
| **G-ONB-1** | Resumable / chunked upload | "Resumed where it stopped" | Retry restarts; honest copy |
| **G-ONB-2** | `POST /api/probe` (10-s suitability probe) | Fail before a 2 GB upload | On-device metadata check + post-hoc "Usable with limits" after court detection |
| **G-ONB-3** | `GET /api/sessions/{id}/players/proposal` (frame + two boxes + sides) | Pick yourself | Derive from `/tracks` + sprite frame client-side |
| **G-ONB-4** | Identity-segment correction ("swap from here") | Track ID flips | Mark affected rallies "Worth a look" and exclude from "you" metrics |
| **G-ONB-5** | Track whitelist when > 2 people visible | Bystanders | Block with a clear message |
| **G-ONB-6** | Trim before upload / server-side trim | Data-light | Warn and offer Wi-Fi wait |
| **G-04** (Doc 00) | Free-play match type | Social game / Practice | Hide score-derived surfaces |
| **G-ONB-7** | Guest workspace (device-bound token, claim-on-signup, retention window) | Guest-first | Passphrase demo mode for the prototype |
| **G-ONB-8** | Persisted consent ledger with `policy_version` | JIT consent | Local-only ledger labelled "Prototype" |
| **G-ONB-9** | Server-confirmed "processing persists after leaving" flag | "You can leave" claim | Show "keep this tab open" |

---

## 18. Master acceptance checklist (summary)

| ID | One-line criterion |
|---|---|
| AC-ONB-1…4 | Landing: benefit + limit understood; no prompts; embed safe; cost visible |
| AC-ONB-5…8 | Sample: always labelled; includes uncertainty; never writes player data; uses real components |
| AC-ONB-9…12 | Questions: skippable, ≤ 2 screens, editable, no labelling |
| AC-ONB-13…17 | Record guide: skippable; results name missing surface + fix; no dead end; doubles honest; consent reminder specific |
| AC-ONB-18…23 | Consent: separated, defaults off, no bytes before Continue, declining optional is harmless, recorded with version |
| AC-ONB-24…28 | Pick yourself: one tap; nothing attributed until chosen; reversible; names optional; opponent private |
| AC-ONB-29…33 | Court: one tap on suitable video; failure explained; no jargon; skippable; lines type stated |
| AC-ONB-34…38 | Processing: honest numbers; watch while analysing; provisional excluded; notify on request; failed has two exits |
| AC-ONB-39…43 | First value: measured; never on winning alone; honest when none; no PB on first match; optional actions |
| AC-ONB-44…46 | Invite: view-only, removal in one tap, never public |
| AC-ONB-47…48 | Guest-first and honest account prompts |

**Definition of done for the whole first run:** a usability session with the working segments (Blueprint §16.2) in which ≥ 80 % of target users state the report's main finding accurately, no critical privacy task fails, advanced users can reach evidence without complicating the novice defaults, and no participant reads a hypothesis as a fact.
