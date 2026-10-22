# 05b — Screens: Deep Dive, Review & Fix, Place Your Court

**Scope:** Deep dive shell and its six sub-screens (**Story · Rallies · Shots · Court · Compare · Ask**), **Review & fix**, **Place your court**, the **Advanced workspace**, and the **Quality panel**.
**Depends on:** `00` (D1–D18), `05a` (shared rules §0 apply here: state vocabulary, depth defaults, preset defaults, `PreviewTag`), `06`, `07`, `09`.
**Theme:** Video theatre defaults to **Arena Night**; the Deep dive workspace respects the player's explicit Light, Dark or High contrast setting (D13, file 08 §16).

> **The professional layer, made kind.** This is where the evidence lives. Every number is deterministic, versioned and traceable to events; the *presentation* is still plain, self-referenced ("you") and honest about what we could not see. Nothing here is hidden from an expert; nothing here is thrown at a beginner.

---

## 0. What carries over from the existing app

The existing `SessionPage` already has the right *engine-facing* bones: sticky video (`VideoStage`), `Timeline`, `RallyBar` ("Rally 47 · 9 shots · P1 serving from the right"), `CourtMinimap`, `LiveFeed`, tabs, keyboard shortcuts, `?f=` deep link, WebSocket status, calibration banners. Deep dive **keeps all of that** and changes the *shell, vocabulary and defaults*:

| Existing | Becomes | Why |
|---|---|---|
| Tabs `Stats · Heatmaps · Highlights · Rallies · Ask · Export` | Sub-nav `Story · Rallies · Shots · Court · Compare · Ask`; **Highlights** moves to **Moments** (05a §8); **Export** moves into the **Advanced workspace** | Organise around player questions (Blueprint §4), not engine modules |
| Header "Analyse again" | "Read this match again" (Advanced only) | Plain language; avoid accidental destructive reruns |
| "Court: auto / set + tracked / calibrated" | `CourtFitBadge` + link to **Place your court** | One plain concept (§8) |
| "Live feed" | Collapsed "What happened" rail (Guided+), open in Advanced | Not essential to amateurs |
| `h2h` table as the Stats landing | Moved behind a **Compare players** toggle in Story (D6) | No win/loss as headline |
| Bands `confirmed/probable/uncertain` | `CheckChip` words (D5) | Plain, honest |

### 0.1 Shell shortcuts (keep, add labels)
`Space/K` play·pause · `←/→` frame · `Shift+←/→` 5 s · `J/L` 10 s · `[` `]` previous/next rally · `S` next smash (labelled **Preview**) · `.` hide/show overlays · `?` shortcut list. Add: `G` jump to the **hero moment**, `F` open **Fix this** on the current rally.

---

## 1. Deep dive shell — `/matches/$matchId/deep-dive` (+ `/story /rallies /shots /court /compare /ask`)

### Purpose
One per-match workspace with **video always beside the data**, so any claim can be watched. It answers the player's *"why"* questions as **invitations to investigate**, never as verdicts.

### Who and when
- **Curious player** who opened "Deep review" from the Recap entry choice.
- **Improvement player** following a Focus ("show me the rallies where…").
- **Competitive player / coach** investigating patterns on desktop.

### Entry points
Recap header "Deep dive ▸", EntryChoice → *Deep review*, Clip detail "Open this rally in Deep dive", Ask citation, Home "Resume investigation" (Advanced).

### Default sub-screen by preset
| Preset | Opens on |
|---|---|
| Relax | **Story** (short, in Quick language) |
| Explore | **Shots** |
| Improve | **Story** with the Focus's evidence highlighted |
| Compete | **Rallies** |

> Opening Deep dive from a **Quick** recap upgrades the *screen's* density to **Guided** for the session (stored depth is not changed): *"Opening Deep dive in Guided. Back to Quick"*.

### Layout — mobile
```
┌────────────────────────────────┐
│ ← Recap   Thu evening   ⋯      │
│ ┌── mini-player (sticky) ────┐ │
│ │ ▶  0:23     Rally 22 · 9 sh│ │  RallyBar line under it
│ └────────────────────────────┘ │
│ [Story][Rallies][Shots][Court] │ SubNav (scroll)
│ [Compare][Ask]                 │
├────────────────────────────────┤
│ …active sub-screen…            │
├────────────────────────────────┤
│ ◐ What we could see ▸          │ → Quality panel (bottom sheet)
└────────────────────────────────┘
```

### Layout — desktop
```
┌ SideNav ┬───────────────────────────────────────────────────────────────────┐
│         │ ← Recap  Thu evening   CourtFitBadge   Depth [Q|G|A]  ⌨  ⋯        │
│         ├───────────────────────────────────────┬───────────────────────────┤
│         │ ClipPlayer (VideoStage) 16:9          │ CourtMap (minimap)        │
│         │ Timeline (rallies, scenes, phases)    │ What happened (LiveFeed)  │
│         │ RallyBar                              │ Quality panel (compact)   │
│         ├───────────────────────────────────────┴───────────────────────────┤
│         │ SubNav: Story · Rallies · Shots · Court · Compare · Ask · Advanced │
│         │ …active sub-screen (full width)…                                   │
└─────────┴───────────────────────────────────────────────────────────────────┘
```

### Components used
`DeepDiveShell`, `SubNav`, `ClipPlayer` (VideoStage), `RallyTimeline`, `CourtMap`, `QualityPanel`, `CourtFitBadge`, `DepthSwitcher`, `PreviewTag`, `LiveFeed` (as "What happened"), `ReviewBanner`, `PartialAnalysisNote`, `OfflineState`, `FailedState`, `EmptyState`.

### Data in
| UI field | Source (existing unless noted) |
|---|---|
| Session, status, progress | `GET /api/sessions/{id}`; WebSocket `StatusMsg` (`status`, `frontier_frame`, `n_frames`, `rate_x`, `degraded[]`) |
| Events (rallies, strokes, points, scenes, calibration, match_phase) | `GET …/events` + WebSocket; folded in `useSession` / `EventLog` |
| Tracks (players, shuttle) | `GET …/tracks` (MessagePack buffers) |
| Calibration | `calibration` event (`Calibration` type: `mode`, `quality`, `coverage`, `source`, `lines_check`) |
| Scene chip | `scene` events (`ScenePayload.view`, `analysed`, `court_quality`) |
| Current rally line | `currentRally(events, frame)`, `stateAt(events, frame)` → `MatchState` |
| Names, "me" | `Session.players`; mapping new — see G-01 |
| Analytics for sub-screens | `GET …/analytics` (`Analytics`, `PlayerStats`), refetched when `analyticsVersion` changes (existing) |

### Copy
- **Sub-nav labels:** Story · Rallies · Shots · Court · Compare · **Ask** (not "Coach"; the engine does not coach).
- **Banners (rewritten from the existing ones):**
  - *Not calibrated:* "We couldn't find your court automatically, so positions and where the shuttle landed will be rough. **Place your court** — it takes about a minute."
  - *Degraded:* "Part of this match was read with less detail: {stage} ({reason in plain words})."
  - *Failed:* "We couldn't finish reading this match. {cause}. **Read it again**, or tell us what happened."
- **Entry upgrade line:** "Opening Deep dive in Guided. Back to Quick."

### Interactions
- Any claim in any sub-screen has an `EvidenceChip` that seeks the video (`seekFrame(frame − 1 s)`) and stays in Deep dive.
- URL carries `?f=<frame>` for the playhead and sub-screen filters as search params (e.g. `/rallies?game=2&winner=me&len=6-`). Back preserves filters and scroll (`scrollRestoration` already on).
- **Return to analysis** link appears on Clip detail when the user arrived from here.
- `DepthSwitcher` changes density live; `PreviewTag` clicks open "What is Preview?".

### States
| State | Behaviour |
|---|---|
| loading | Shell skeleton; video poster; sub-screen skeleton |
| empty | "Rallies appear as they finish." (existing copy tone) while analysing |
| partial | `PartialAnalysisNote`; each sub-screen states what is missing |
| complete | Normal |
| low-coverage | Quality panel opens automatically **once** with the explanation; shell shows `CourtFitBadge: Rough` |
| failed | `FailedState`; analytics shown only for what exists |
| permission | `PermissionRevokedState` |
| offline | The existing "Reconnecting" chip → `OfflineState`; stale data labelled |
| demo | `DemoBanner`; fixture-driven |

### Depth / Preset behaviour
- **Quick (screen upgraded to Guided):** hides tables; shows the plain sentence and the clip. 
- **Guided:** sub-screens with one chart each + definitions inline.
- **Advanced:** adds filters, event table, coverage detail, exports.
- Preset determines the landing sub-screen (above) and the suggestion chips in **Ask**.

### Accessibility
SubNav = `role="tablist"` with arrow-key navigation; each sub-screen is a labelled `tabpanel`. The sticky mini-player has a skip link ("Skip video"). All overlays are optional with a legend. The `Timeline` is keyboard-operable (←/→ moves between rallies; Enter seeks).

### Telemetry
`deep_dive_opened` (source), `subscreen_viewed`, `filter_applied`, `evidence_clip_opened`, `shortcut_used`, `quality_panel_opened`, `depth_changed`, `return_to_analysis`.

### Acceptance criteria
- **AC-dd-1** Video is visible beside or above every sub-screen on mobile and desktop.
- **AC-dd-2** Every claim in every sub-screen opens its evidence in one action.
- **AC-dd-3** Filters live in the URL and survive back navigation.
- **AC-dd-4** Opening from Quick upgrades the screen to Guided without changing stored depth.
- **AC-dd-5** The shell shows a plain-language court-fit state and links to Place your court.
- **AC-dd-6** No engine vocabulary (`band`, `provisional`, `rally_end`) appears below Advanced.

---

## 2. Story — `/matches/$matchId/deep-dive/story`

### Purpose
Answer *"What actually happened?"* neutrally: the shape of the match (rally lengths, how the score moved), with **the scoreline as context, never a verdict** (D6).

### Who and when
A player who wants the narrative of the game. A competitive player scanning for turning points.

### Layout — mobile
```
┌────────────────────────────────┐
│ What happened                  │
│ 36 rallies · 31 followed       │
│ Longest 14 shots · average 7   │  FactTrio (rally-centric)
│ Score  21–17 · 21–19  [Checked]│  ScoreChip (Match type only)
├────────────────────────────────┤
│ How the rallies went           │  RallyTimeline (compact bars)
│ ▇ ▃ ▆ ▂ ▇ ▅ …  tap a bar       │
├────────────────────────────────┤
│ How the score moved  (Match)   │  ScoreStory (small line, both sides)
├────────────────────────────────┤
│ Rally length  ▁▂▅▇▅▂▁          │  distribution + n
├────────────────────────────────┤
│ [Compare players ⌄]            │  toggle → HeadToHead (P1/P2 colours)
│ (Advanced) Momentum ▸          │
└────────────────────────────────┘
```

### Layout — desktop
Two columns: left = FactTrio + ScoreStory + distribution; right = RallyTimeline full height with phases (warm-up, intervals, replays) shaded; below: **Compare players** panel (collapsed by default).

### Components used
`FactTrio`, `ScoreChip`, `ScoreStory`, `RallyTimeline`, `HeadToHead`, `MomentumChart`, `CheckChip`, `EvidenceChip`, `MetricPopover`, `CoverageBar`, `PreviewTag`, `NotEnoughToSay`.

### Data in
| UI field | Source |
|---|---|
| Rallies, longest, average | `Analytics.rallies`, `longest_rally_shots`, `avg_rally_shots` |
| Active play | `active_play_s` (API `to_public()`; add to TS `Analytics`) — copy: "The shuttle was in play for about 11 minutes" (it is **not** time on court) |
| Followed vs not counted | `unofficial_rallies` (API), `scene` `analysed` ratio; `match_phase` events |
| Scoreline, games | `GET …/state` → `MatchState.completed_games`, `games_won`; `Analytics.score_timeline[]` (`score`, `winner`, `game_no`, `rally_no`) |
| Rally timeline | `rallies(events)` (derive.ts): `start/stop`, `n_shots`, `winner`, `band`, `status`, `official`, `phase_reason` |
| Rally-length distribution | derived from `rally_end.payload.n_shots` (n shown) |
| Head-to-head rows | `Analytics.players.P1/P2` (`PlayerStats`) |
| Momentum | `Analytics.momentum[]` (EWMA −1…1), `momentum_shifts[]` — **Advanced only** |

### Head-to-head wording (replaces the existing `ROWS`)
| Existing row | Plain label | Notes |
|---|---|---|
| Points won | Points won | Context; no colour judgement |
| Winners | "Shuttle landed in on their side" | Plain; **Preview** (landing is approximate) |
| Errors (out) | "Went out" | Neutral; not "errors" |
| Errors (net) | "Into the net" | Neutral |
| Smashes / Jump smashes | Smashes (Preview) | Shot type is Preview |
| Points won with a smash | "Points that ended with a smash" | Preview |
| Points won on serve | "Points won after serving" | |
| Points won under pressure | "Points won at game point or deuce" | Only when scoreline Checked; Advanced |
| Distance covered | **Removed (Not yet)** | Metres are ungated (00 §7) |

Each row opens its definition and the rallies behind it. Colours: **P1/P2 blue/orange are used only here** (D8); the default Story view shows *you* with the `--you` colour and the other side neutral.

### Copy
- **Heading:** "What happened"
- **Sentence:** "36 rallies; we followed 31. The longest was 14 shots."
- **Score:** "Game 1 21–17, game 2 21–19 · Checked" (or "Score not checked — review rallies" if any dependency remains unverified)
- **No scoreline:** "This was a social game, so there's no score — here are the rallies."
- **Momentum caption (Advanced):** "How recent points leaned. This is a smoothed view of who won recent points, not a measure of who played better."
- **Banned:** "Dominated", "collapsed", "choked".

### Interactions
Tap a timeline bar → seeks the rally; long-press/Enter opens `RallyDetailPanel` (Rallies). **Compare players** toggles `HeadToHead`. Score chip tap → Review & fix if not Checked. Momentum point hover/focus shows rally, score, run length (existing tooltip).

### States
| State | Behaviour |
|---|---|
| loading | Skeleton of FactTrio and timeline |
| empty | "No completed rallies yet. Rallies appear as they finish." |
| partial | Timeline shows pending region hatched (not zero) |
| complete | Normal |
| low-coverage | Hatched gaps for unfollowed time; sentence states how much |
| failed | `FailedState` |
| permission / offline / demo | As shell |

### Depth / Preset behaviour
Quick(upgraded): FactTrio + timeline. Guided: + ScoreStory + distribution. Advanced: + momentum, head-to-head, `active_play_s`. Compete preset opens with the **Compare players** panel expanded.

### Accessibility
Charts have a text summary ("Rally length ranged 2–14 shots; most were 5–8") and a table alternative; the score line is a table by game; colour is paired with shape (P1 solid, P2 hatch) in Compare.

### Telemetry
`story_viewed`, `compare_players_toggled`, `momentum_opened`, `definition_opened`, `evidence_clip_opened`.

### Acceptance criteria
- **AC-story-1** No win-rate or "winner" label is shown by default.
- **AC-story-2** Momentum appears only in Advanced and carries the "not a measure of who played better" caption.
- **AC-story-3** P1/P2 colours appear only in the Compare players panel.
- **AC-story-4** Distance in metres is not shown.
- **AC-story-5** Missing time is hatched, never rendered as zero.
- **AC-story-6** Social/Practice matches show no scoreline or score chart.

---

## 3. Rallies — `/matches/$matchId/deep-dive/rallies`

### Purpose
The **rally explorer**: *"Why do I lose certain rallies?"* answered as **sequences, not last shots**. Every rally is inspectable, filterable and fixable.

### Who and when
Competitive/improvement players investigating a pattern; any player verifying "Is that the rally I remember?".

### Layout — mobile
```
┌────────────────────────────────┐
│ 36 rallies  [Filters (1)]      │
│ RallyTimeline (compact)        │
│ ┌ RallyRow ────────────────────┐│
│ │ 0:23  Rally 22 · 14 shots    ││
│ │ [Looks right] you · landed in││
│ │ ▾                            ││
│ └──────────────────────────────┘│
│ ┌ RallyRow (warm-up) ──────────┐│
│ │ 0:02  Not counted — warm-up  ││
```

### Layout — desktop
```
┌──────────────────────────────┬─────────────────────────────────────────────┐
│ RallyFilterBar               │ RallyDetailPanel                            │
│ [Game][Who won][Length]      │  clip · sequence · why it ended             │
│ [Shot][Outcome][Counted]     │  Is the winner right?  [Yes][Change]        │
│ Rally list (virtualised)     │  Not counted? [Count this rally]            │
│                              │  Match starts here                          │
└──────────────────────────────┴─────────────────────────────────────────────┘
```

### Components used
`RallyTimeline`, `RallyRow`, `RallyFilterBar`, `RallyDetailPanel`, `CheckChip`, `EvidenceChip`, `FixSheet`, `PreviewTag`, `MetricPopover`, `EmptyState`.

### Data in
| UI field | Source |
|---|---|
| Rally list | `rallies(events)`: `no`, `start`, `stop`, `winner`, `official`, `end.band`, `end.status` |
| Shots in rally | `rally_end.payload.shots[]` (`frame`, `player_id`, `stroke`, `subtype`, `event_id`) |
| Shot count | `payload.n_shots` |
| How it ended | `payload.outcome` (`out/net/winner/fault/unknown` → `OUTCOME_LABEL`), `payload.end_reason` |
| Winner source | `payload.winner_source` (`ocr` → "from the scoreboard") |
| Not counted reason | `payload.phase_reason`, `official` |
| Game, score after | `score_timeline[rally_no]` |
| Sequence **preceding** the last shot | shots[] order; "serve → … → last shot" |

### RallyDetailPanel (the sequence view)
A horizontal chip sequence of every shot, coloured by *who* (you vs them) with shape, each chip seeking its frame ± 10 frames. Above it a one-line plain description; below, **how it ended** and **what we're sure of**:

```
Rally 22 · 14 shots · 0:23–0:41
you ○ serve · them ● clear · you ○ drop · them ● lift · … · you ○ smash (Preview)
How it ended: the shuttle landed in on their side. We think you won it. [Looks right]
Why we think so: measured from where the shuttle came down. [Watch the last 3 seconds]
```
Crediting only the last shot is **explicitly avoided**: the panel always shows the preceding sequence (Blueprint §7.9; net shots can shape rallies even when smashes finish them).

### Filters (all in URL)
Game · Who won (me / them / unclear) · Length (1–5, 6–9, 10+) · Shot type (Preview) · Outcome (landed in / out / net / unclear) · **Counted** (counted / not counted — warm-up / replay) · **Needs a look** (band ≠ confirmed and not Checked). Doubles-only filters (role, partner) are **Not yet**.

### Copy
- **Row warm-up:** "Not counted — warm-up" (+ **Count this rally** if wrong)
- **Winner unclear:** "We couldn't tell who won this one. Watch it and tell us."
- **Changing the winner:** "Changing the winner re-counts every point after this one." (existing semantics, plain)
- **Panel title:** "This rally"
- **Empty:** "Rallies appear here as they finish."
- **Banned:** "You lost this because…"; "Your error". Use "ended with", "appeared alongside".

### Interactions
- Expand a row (or select in the master/detail layout) → detail.
- **Yes, {name} won** (`verifyEvent`), **{name} won it** (`correctWinner`), **Count this rally / Not part of the match** (`setRallyOfficial`), **Match starts here** (`setMatchStart(r.start)`) — all existing endpoints; after any, a `ChangeSummaryBanner` appears (see §7).
- **Only rallies that need a look** is a filter chip.
- Table toggle (Advanced) → compact table with columns *Time · Game · No. · Shots · Winner · Outcome · Check · Counted*.

### States
| State | Behaviour |
|---|---|
| loading | Row skeletons |
| empty | Message above |
| partial | Last rows "Still being read" |
| complete | Normal |
| low-coverage | Unfollowed time shown as gaps between bars; rally numbers have gaps explained |
| failed | `FailedState` |
| permission | n/a |
| offline | Cached list; fixes disabled with reason |
| demo | Corrections work but labelled demo |

### Depth / Preset behaviour
Quick(upgraded): list + plain sentence; no table. Guided: sequence chips + filters (game, who won, length). Advanced: all filters, table, event ids, bands as words under chip. Compete preset sorts by "most shots" and preselects "Needs a look".

### Accessibility
Row = `li` with a toggle button (`aria-expanded`); shot chips are buttons with labels ("Drop by you at 0:25"); the list is virtualised with correct `aria-setsize/posinset`; focus returns to the row after closing the panel on mobile.

### Telemetry
`rallies_viewed`, `rally_opened`, `rally_filter_applied`, `winner_confirmed`, `winner_changed`, `rally_counted_toggled`, `match_start_set`, `shot_chip_opened`.

### Acceptance criteria
- **AC-rally-1** The detail panel always shows the sequence preceding the last shot.
- **AC-rally-2** A not-counted rally explains why and can be reinstated.
- **AC-rally-3** Every winner change shows how many later points were re-counted and the new score.
- **AC-rally-4** Filters work and persist in the URL.
- **AC-rally-5** Shot-type filter and labels carry `PreviewTag`.
- **AC-rally-6** No copy attributes a lost rally to a personal trait.

---

## 4. Shots — `/matches/$matchId/deep-dive/shots`

### Purpose
Show **which shots we spotted** and let the player explore examples — *observed ≠ mastered*. Entire screen is **Preview** until a learned stroke classifier is validated on amateur footage.

### Who and when
An Explore-preset player who enjoys discovering their repertoire; an Improve player checking whether a shot even shows up.

### Layout — mobile
```
┌────────────────────────────────┐
│ Shots we spotted  [Preview ◔]  │
│ Based on 214 shots we could    │
│ classify (31 unclear, left out)│
│ ┌ ShotRepertoireGrid ────────┐ │
│ │ Smash ✓ 9   Drop ✓ 14      │ │
│ │ Clear ✓ 22  Lift ✓ 31      │ │
│ │ Net shot ✓ 12  Drive ✓ 8   │ │
│ │ Block –     Push –         │ │
│ └────────────────────────────┘ │
│ Tap a shot for 3 example clips │
│ ShotMix (you vs them) ▸        │
└────────────────────────────────┘
```

### Layout — desktop
Left: repertoire grid (12 types, grouped by family: serve · attack · lift · flat · net · defence). Centre: `ShotMix` bars (you vs them with shape coding). Right: examples panel (3 clips) and, in Advanced, `ShotSequenceTable` (common two-shot sequences).

### Components used
`ShotRepertoireGrid`, `ShotMix`, `ShotSequenceTable`, `EvidenceChip`, `CheckChip`, `PreviewTag`, `MetricPopover`, `NotEnoughToSay`, `FixSheet`.

### Data in
| UI field | Source |
|---|---|
| Counts by type | `PlayerStats.strokes` (`short_serve, long_serve, smash, drop, clear, lift, drive, push, rush, net_shot, cross_net, block, unknown`) |
| Unclear shots | `strokes.unknown` (excluded from totals; stated) |
| Smashes / jump smashes | `PlayerStats.smashes`, `jump_smashes` |
| Labels | `STROKE_LABEL`; family from ontology (`serve/attack/lift/flat/net/defence`) |
| Examples | `rally_end.payload.shots[]` filtered by `stroke`; frames for the clip |
| Per-shot band | `stroke` event `band`/`status` |
| Sequences | derived from consecutive shots in `rally_end.payload.shots` |

### Rules
- **Share, not score.** Show counts and "% of your classified shots" with n stated; never "accuracy", "effectiveness" or "best shot".
- **"Spotted" copy**, not "mastered"/"unlocked".
- A shot type with fewer than **3 examples** shows "Spotted once or twice" and is not eligible for a **First** badge until verified (06 sets the threshold).
- **Opportunity-adjusted** claims (e.g. "returned smashes") are *not* shown here (denominator not yet reliable).

### Copy
- **Heading:** "Shots we spotted" + `Preview` tag. **Tag explanation:** "We're still learning to tell shots apart on phone footage. Check the examples."
- **Totals line:** "Based on 214 shots we could classify. 31 were unclear and aren't counted."
- **Empty type:** "Not spotted in this match." (never "0%").
- **Wrong label:** "This label looks wrong" → `FixSheet` (Wrong shot).
- **Banned:** "You're good at smashes", "Your clears are weak".

### Interactions
Tap a shot type → 3 representative clips (highest `band`, spread across rallies) + "Show all 14"; `This label looks wrong` on every clip; toggle *You / Them / Both*. Advanced: sequence table (e.g. *clear → drop: 6 times*) with a denominator and a "Watch" link per row.

### States
| State | Behaviour |
|---|---|
| loading | Grid skeleton |
| empty | "We couldn't classify enough shots to show a repertoire." + manual alternatives |
| partial | Provisional shots excluded, noted |
| complete | Normal |
| low-coverage | "Most shots in this match were too far from the camera to classify." |
| failed | `FailedState` |
| permission / offline / demo | As shell |

### Depth / Preset behaviour
Quick(upgraded): repertoire grid only. Guided: + ShotMix. Advanced: + sequence table, per-shot band names, unclear count. **Explore** opens here; **Relax** hides the screen entry from the primary sub-nav (still reachable).

### Accessibility
Grid is a table (`Shot · Spotted? · Count`); ✓ is paired with the word "Spotted"; clips have text descriptions; colour never carries meaning alone.

### Telemetry
`shots_viewed`, `shot_type_opened`, `shot_example_played`, `label_corrected`, `preview_explained`.

### Acceptance criteria
- **AC-shots-1** The screen carries `PreviewTag` and an explanation of what Preview means.
- **AC-shots-2** Counts are shown with their denominator and unclear count.
- **AC-shots-3** No copy implies mastery from detection.
- **AC-shots-4** Every example clip has "This label looks wrong".
- **AC-shots-5** A type with no examples shows "Not spotted", not zero percent.

---

## 5. Court — `/matches/$matchId/deep-dive/court`

### Purpose
Show **where on the court** things happened — presence, movement, hit positions, where shots went — with **precise statements of what each mark means** and honest coverage notes.

### Who and when
A player curious about their positioning; a coach reviewing coverage. Only meaningful with a good court fit.

### Layout — mobile
```
┌────────────────────────────────┐
│ Where things happened  [Preview]│
│ [Where I stood][Where I moved] │ HeatmapKindTabs
│ [Where I hit from][Where my    │
│  shots went][Where I aimed]    │
│ "Time spent in each part of    │
│  the court while the shuttle   │
│  was in play."                 │
│ ┌ CourtMap (near side = bottom)┐│
│ │  heat over court lines       ││
│ └──────────────────────────────┘│
│ less ▁▃▅▇ more  · 1,420 samples │
│ Text: Most of your time was in  │
│ the middle of your half.        │
│ [Show table ▾]                  │
└────────────────────────────────┘
```

### Layout — desktop
Two `CourtMap`s side by side (you / them) with a shared legend; below: `ZoneTable` (3×3 per half). Orientation is fixed: **near side at the bottom everywhere** (Blueprint §8.8).

### Heatmap kinds (existing `KINDS`, renamed)
| Engine kind | Label | What a mark means (legend text) | Label |
|---|---|---|---|
| `presence` | Where I stood | **Player location** while the shuttle was in play | Preview |
| `movement` | Where I moved | **Player location**, weighted by distance moved there (relative) | Preview; **no metres** |
| `origin` | Where I hit from | **Contact location** — where the player was at each shot | Preview |
| `landing` | Where my shots went | **Approximate landing** — currently where the opponent played the shot (or it landed) | Preview |
| `targeting` | Where I aimed | **Landing areas on the opponent's side** | Preview |

### Components used
`CourtMap`, `HeatmapKindTabs`, `ZoneTable`, `CoverageBar`, `CourtFitBadge`, `PreviewTag`, `EvidenceChip`, `NotEnoughToSay`, `EmptyState`.

### Data in
| UI field | Source |
|---|---|
| Grid | `GET …/heatmap?player=&kind=` → `Heatmap` (`cell_m`, `origin_m`, `shape`, `total`, `values[][]` normalised 0–1) |
| Samples | `Heatmap.total` |
| Court fit | `Calibration.mode`, `quality.precision`, `coverage`, `lines_check` |
| Zone table | derived: aggregate cells into the ontology's 3 depth × 3 width zones per half (`court_zones`); shown as "% of the busiest area" (the tooltip semantics already used) |
| Examples under a zone | events with `hitter_court_xy` / `landing_court_xy` in the zone → clips |

### Gating
- **No calibration →** `EmptyState`: "Heatmaps need the court. **Place your court** so positions can be placed on the floor." (replaces the existing "Calibrate the court…").
- **Rough fit** (`precision` below the "Good" band, or `coverage` low) → map is shown dimmed with a banner "The court fit is rough, so treat these as a general idea."
- **Distance in metres: Not yet.** The `movement` kind is shown as *relative* intensity only.

### Copy
- **Heading:** "Where things happened" + `Preview`.
- **Caption per kind:** use the *legend* in the table above.
- **Text summary (generated, grounded):** "Most of your time was in the middle of your half, a little left of centre." (from `ZoneTable`; no causal text).
- **Tooltip:** "34 % of the busiest area" (existing semantics, reworded: "about a third as busy as your busiest spot").
- **Low samples:** "Only 120 samples — too few to draw a pattern." → `NotEnoughToSay`.

### Interactions
Kind tabs; You/Them/Both toggle; hover/focus a cell shows its share; click a zone → example clips list. **Show table** toggles `ZoneTable`. A legend explains "less … more" and the mark meaning.

### States
| State | Behaviour |
|---|---|
| loading | Court outline + shimmering cells |
| empty | Needs-court message |
| partial | Heat built from analysed frames only; states "so far" |
| complete | Normal |
| low-coverage | Dimmed map + banner; `ZoneTable` hidden if samples < threshold |
| failed | `FailedState` |
| permission / offline / demo | As shell |

### Depth / Preset behaviour
Quick(upgraded): one map ("Where I stood") + sentence. Guided: kind tabs + summary. Advanced: both players, `ZoneTable`, sample counts, calibration quality detail. Compete: opens on "Where I aimed".

### Accessibility
Canvas has `role="img"` and a computed `aria-label` plus the generated text summary; `ZoneTable` is the accessible equivalent; a pattern (stripe density) accompanies colour ramp for colour-blind users; legend is text.

### Telemetry
`court_viewed`, `heatmap_kind_selected`, `zone_examples_opened`, `table_toggled`, `court_fit_opened`.

### Acceptance criteria
- **AC-court-1** Each kind states precisely whether marks are player location, contact location or landing.
- **AC-court-2** Orientation is identical in every view and across screens.
- **AC-court-3** No distance in metres or speed is shown.
- **AC-court-4** Each map has a text summary and an accessible table.
- **AC-court-5** A missing or rough court fit gates the map with an actionable message.
- **AC-court-6** All kinds carry `PreviewTag`.

---

## 6. Compare — `/matches/$matchId/deep-dive/compare`

### Purpose
Answer *"Am I changing?"* by comparing **two comparable matches** of the same player, with ranges, sample sizes and **explicit comparability limits** — never a favourable-looking delta from incompatible matches.

### Who and when
An improvement-oriented player after two or three matches; a coach comparing before/after a practice block. (Longer-term trends live in **Progress**, 05c.)

### Layout — mobile
```
┌────────────────────────────────┐
│ Compare matches                │
│ This match ▾ vs Mon 12 ▾       │ CompareMatchesPicker
│ ✓ Comparable: both Matches,    │ ComparabilityNote
│   same court view, both        │
│   followed ≥ 70 %              │
│ Pick one thing: [Longest rally]│
│ ┌ small multiple ────────────┐ │
│ │ 9  → 14 shots  (n=31 / 28) │ │
│ └────────────────────────────┘ │
│ "More long rallies this time —  │
│  not enough matches to call it │
│  a trend yet."                 │
└────────────────────────────────┘
```

### Layout — desktop
Left: picker + ComparabilityNote; right: two small multiples per chosen metric with ranges and `n`; below: side-by-side rally timelines.

### Components used
`CompareMatchesPicker`, `ComparabilityNote`, `TrendSmallMultiples`, `ProgressCard`, `RallyTimeline` (two), `CheckChip`, `MetricPopover`, `NotEnoughToSay`.

### Data in
| UI field | Source |
|---|---|
| Two matches' analytics | two `GET …/analytics` calls (existing; client-side now) |
| Comparability inputs | `Session` (type — G-04), `Calibration.mode/coverage/quality`, `scene` coverage, "me" mapping (G-01) |
| Metrics available now | `longest_rally_shots`, `avg_rally_shots`, rally count, rallies ≥ 6 shots, rally-length distribution |
| Metrics later | Records/Progress metrics — G-02/G-07 |

### Comparability rules (from v1 §6; all must hold)
1. Same **match type** (Match vs Match, Social vs Social).
2. Same **format** (singles; doubles is Not yet).
3. Both matches **Followed ≥ 70 %** of rallies and a court fit at least "Good" for spatial metrics.
4. **Identity** of "you" confirmed in both.
5. Metric **definition version** identical (G-07).
6. Enough events (n ≥ 8 rallies for rally metrics).

If any fails: **"Not directly comparable"** + the reason, and the screen offers *pick another match* — it does not draw a delta.

### Copy
- **ComparabilityNote (pass):** "These two matches are comparable: both are scored matches, both followed at least 70 %."
- **(fail):** "Not directly comparable — one was filmed from another angle. Pick another match, or compare the moments instead."
- **Result:** "Your longest rally was 9 shots, then 14. That's two matches — not enough to call it a trend yet."
- **Banned:** "Improved by 55 %", "You're getting better" from two points.

### Interactions
Pick matches; pick **one** process metric (default: longest rally); open evidence for each value; **Save as my comparison** (private note). **Start a fresh baseline** is available (non-destructive) when matches span a long gap.

### States
| State | Behaviour |
|---|---|
| loading | Skeleton |
| empty | "Compare needs two comparable matches. Add another to see how this one sits." |
| partial | A processing match is not selectable |
| complete | Normal |
| low-coverage | Matches under threshold disabled with reason |
| failed | `FailedState` |
| permission / offline / demo | As shell |

### Depth / Preset behaviour
Quick(upgraded): sentence + one multiple. Guided: metric picker + note. Advanced: multiple metrics, distribution overlays, definitions/versions. **Improve** opens here when a Focus exists; **Relax** hides the entry.

### Accessibility
Pickers are native selects or listboxes; small multiples have text equivalents ("9 then 14; n 31 and 28") and a table; comparability is words + icon.

### Telemetry
`compare_viewed`, `compare_matches_selected`, `comparability_failed` (reason), `metric_selected`, `fresh_baseline_started`.

### Acceptance criteria
- **AC-compare-1** No delta is drawn unless all comparability rules pass.
- **AC-compare-2** Every value shows its sample size and range.
- **AC-compare-3** "Not directly comparable" always states the reason.
- **AC-compare-4** Two matches never produce the word "trend" or "improved".
- **AC-compare-5** The player picks the metric; no overall score is shown.

---

## 7. Ask — `/matches/$matchId/deep-dive/ask`

### Purpose
A **grounded** conversational way to ask about the match. The agent may only state facts that appear in its tool results; every fact is clickable to its moment. It **abstains** when evidence is thin.

### Who and when
A curious player who prefers asking to browsing; a coach looking for a specific rally ("Show every rally that ended on the net").

### Layout — mobile
```
┌────────────────────────────────┐
│ Ask about this match           │
│ ┌ suggestions (by preset) ───┐ │
│ │ What was my best rally?    │ │
│ │ Show my longest rallies    │ │
│ │ Which rally was the turning│ │
│ │ point?                     │ │
│ └────────────────────────────┘ │
│  you:  Show my longest rallies │
│  Rally: 14 shots ¹ and 12 ² …  │ numbered EvidenceChips
│  Every fact is linked ✓        │ grounded line
│ ┌────────────────────────────┐ │
│ │ Ask about rallies, shots…  ▲│ │
│ └────────────────────────────┘ │
└────────────────────────────────┘
```

### Components used
`AskPanel`, `EvidenceChip` (numbered citations), `AnswerFeedback`, `CheckChip`, `PreviewTag`, `NotEnoughToSay`, `EmptyState`, `OfflineState`.

### Data in
| UI field | Source |
|---|---|
| Answer | `POST …/ask` `{question, history}` → `AskAnswer` (`text`, `citations[]`, `grounded`, `issues[]`, `provider`, `model`) |
| Provider availability | `GET …/ask/provider` → `{available}` |
| Citation → clip | `citations[].frame` (`kind: "ev"`) → `seekFrame`; `kind: "kb"` = background knowledge (icon, not a match fact) |
| Grounded flag | `AskAnswer.grounded`, `issues[]` |

### Preset suggestion chips (rewritten to avoid imperative advice)
| Preset | Chips |
|---|---|
| Relax | "What was my best rally?" · "Show my longest rallies" · "Which shots did I use most?" |
| Explore | "What shots did I use for the first time?" · "Which rally had the most different shots?" |
| Improve | "When did I keep rallies alive from the back?" · "Show rallies that ended at the net" · "What do my rallies have in common?" |
| Compete | "Which rally was the turning point?" · "Show rallies after game point" · "How did my serve rallies go?" |

The existing suggestion *"What should {P1} change in the next game?"* is **removed**: it invites unevidenced advice (D16/D17, Blueprint §9.4). An advice-seeking question gets: *"I can show you the rallies where {pattern} appeared and what we could see. For what to change, a coach can help — I can build a short playlist to share."*

### Copy
- **Heading:** "Ask about this match".
- **Intro (Empty):** "Ask about rallies, shots or moments. Every fact links to the moment it came from."
- **Provider unavailable (replaces the `.env` text):** "Written answers aren't available here. You can still search your rallies and shots from the filters."
- **Grounded footer:** "Every match fact above is linked to its moment." / ungrounded: "Some statements couldn't be linked to match data, so treat them as general background."
- **Abstain:** "I can't tell from this match. Here's what I could see: …"
- **Feedback:** "Useful · Not useful · That's wrong".

### Interactions
Send (Enter), newline (Shift+Enter). Citation chip → seeks the clip, scrolls it into view. `AnswerFeedback` stores "wrong" as a **harm/accuracy signal**. Conversation is session-scoped; **Clear conversation** available. Answers never write to the match (read-only).

### States
| State | Behaviour |
|---|---|
| loading | "Looking through the match…" |
| empty | Suggestions |
| partial | "This match is still being read — answers may change" banner |
| complete | Normal |
| low-coverage | The agent states coverage in its answer when relevant |
| failed | `ErrorNote`, retry |
| permission | n/a (inherits match) |
| offline | Disabled with reason |
| demo | Canned answers, labelled |

### Depth / Preset behaviour
Quick(upgraded): suggestions only + free text. Guided: + grounded footer. Advanced: shows `provider/model`, `issues[]`, and event IDs in citations. Preset sets the suggestion chips.

### Accessibility
`aria-live="polite"` on the answer list; citation chips have labels ("Fact 1: watch at 0:23"); input is labelled; Enter/Shift+Enter documented; works with screen readers.

### Telemetry
`ask_opened`, `ask_submitted` (category only, not text), `ask_answer_grounded` (bool), `citation_opened`, `answer_feedback`.

### Acceptance criteria
- **AC-ask-1** Every numeric match fact has a citation or the answer is flagged ungrounded.
- **AC-ask-2** The screen never offers or gives "what you should change" advice from video alone.
- **AC-ask-3** Provider-missing state does not mention environment variables.
- **AC-ask-4** Citation chips seek the correct moment.
- **AC-ask-5** Suggestion chips vary by preset.

---

## 8. Review & fix — `/matches/$matchId/review`

### Purpose
Make **correcting the system feel good and quick** — the cornerstone of trust (D11). Starts from *what the Recap is about to show*, asks at most **three** questions, shows exactly **what changed**, and offers **undo**. "Corrections are valuable labels, not an embarrassing fallback."

### Who and when
- **Any player** nudged from the Recap ("Is this the rally you remember?"), especially after a Low-coverage or *Worth a look* state.
- **Competitive player / coach** reviewing a longer queue in Advanced.

### Entry points
Recap `ReviewBanner`, `ScoreChip` (not Checked), HeroMoment "Fix this", Clip detail, Rallies detail, Processing complete (when `needs a look` > 0), Matches card "Needs a look".

### Queue order (what the recap will show first)
1. **The hero moment's rally** — *"Is this the rally you remember?"* (also confirms the player in it).
2. **Rallies behind the FactTrio** — the longest rally and its winner.
3. **Scoreline-critical rallies** — those with `band ≠ confirmed` and `status ∉ {human_verified, corrected}` that change the current score.
4. **Not counted?** — rallies flagged warm-up/replay near the start.
5. **Match start** — "Did the match start here?" (only if warm-up detected).

Default batch = **3 items**. A *"Review 3 more"* button appears; Advanced shows the full queue.

### Layout — mobile
```
┌────────────────────────────────┐
│ ← Recap     Help us get it right│
│ 1 of 3 ●○○                     │
│ ┌── clip of the rally ────────┐│
│ │ ▶  0:23–0:41 (14 shots)     ││
│ └─────────────────────────────┘│
│ Is this the rally you remember?│
│ [ Yes ]  [ Not quite ]         │
│ Who won it?                    │
│ [ You ] [ Rahul ] [ Can't tell ]│
│ Skip for now                   │
└────────────────────────────────┘
```

### Layout — desktop
Left: sticky clip; right: the question card with keyboard hints (`Y`/`N`, `1`/`2`/`3`); under it the **Fix history** list (what has been changed so far, each with Undo).

### Components used
`FixQueue`, `FixSheet`, `ClipPlayer`, `ChangeSummaryBanner`, `CheckChip`, `EvidenceChip`, `ReviewBanner`, `RallyDetailPanel` (Advanced), `EmptyState`, `FailedState`.

### Data in / API mapping (existing)
| Action | Existing call |
|---|---|
| Yes, that winner is right | `api.verifyEvent(sessionId, rally_end.event_id)` → status `human_verified` |
| Change winner | `api.correctWinner(sessionId, event_id, "P1"|"P2")` (re-scores every later point) |
| Count / don't count rally | `api.setRallyOfficial(sessionId, event_id, bool)` |
| Match starts here | `api.setMatchStart(sessionId, startFrame)` |
| Wrong player / wrong shot / bad clip / not a rally | **new — G-15**; capture as feedback only if G-32 intake exists, with an honest receipt. Never say the result was fixed until a correction API applies and recomputes it |
| Undo | **new — G-14** (the existing API has no undo token or restoring operation; hide Undo until end-to-end reversal and downstream recomputation work) |
| Queue construction | derived client-side from events + `Highlight[]`; server-side ranking in G-29 |

### ChangeSummaryBanner (what changed)
After a persisted fix, a banner states **cause and the confirmed effect**. Show Undo only after G-14 provides a working reversal; otherwise offer "See what changed" without an undo promise:
```
Fixed: Rahul won rally 22 (you said so).
This re-counted 14 points after it. Score is now 21–18 (it was 21–17). Game 2 changed.
Moments updated: hero moment unchanged · 1 new moment.   [See what changed]
```
For a prototype, compute a before/after diff only after refetching the persisted event fold and mark it "Updated results". The production contract is G-14; G-15 covers additional correction kinds. Do not claim that an optimistic client diff is a saved server result.

### Explanation of re-scoring (plain)
> "Badminton scoring depends on every point before it — who serves, and from which side. So if one rally's winner is wrong, every point after it has to be counted again. That's why changing a winner can change the score."

### Copy
- **Title:** "Help us get it right" (never "Fix errors").
- **Question:** "Is this the rally you remember?" · "Who won it?" · "Did the match start here?"
- **After fix:** "Thanks. Affected findings updated."
- **Skip:** "Skip for now" (no guilt; items return later, deduped).
- **Done:** "That's the important ones. You can fix anything else from the Rallies view."
- **Banned:** "AI mistake", "Our model got this wrong", defending the system.

### Interactions
- Keyboard: `Y/N`, `1/2/3`, `S` skip, `Z` undo last.
- **Skipped** items are not repeated in the same session; counted as "later".
- A fix on a rally in the hero moment immediately refreshes the Recap behind it.
- **Report something else** → free text + category (wrong player / wrong shot / poor clip / privacy concern / other).

### States
| State | Behaviour |
|---|---|
| loading | Queue skeleton |
| empty | "Nothing needs a look. Everything we show is something we're confident in." |
| partial | Match still analysing → queue limited to rallies finished so far |
| complete | Normal |
| low-coverage | Adds "Part of the match wasn't followed — fixes only apply to the part we followed" |
| failed | Fix failed → keep the user's choice, show retry; never lose input |
| permission | Only the match owner (or an authorised coach) can fix |
| offline | Fix is queued locally with "Will apply when online" |
| demo | "Demo action — nothing was saved" |

### Depth / Preset behaviour
Quick: 3 items, yes/no wording. Guided: + "Why we're not sure". Advanced: full queue, event ids and evidence list. There is **no bulk Checked action**: each dependent claim needs explicit evidence review. A bulk dismissal may clear reminders without changing trust state. Compete preset surfaces **scoreline-critical** items first.

### Accessibility
One question per screen on mobile with a clear heading and focus management; buttons ≥ 44 px; keyboard shortcuts documented and optional; the clip has a text description; undo is announced (`aria-live`).

### Telemetry
`review_opened` (source), `review_item_answered` (kind), `winner_confirmed`, `winner_changed`, `fix_undone`, `review_skipped`, `review_completed`, `label_corrected`, `change_summary_viewed`.

### Acceptance criteria
- **AC-review-1** The queue starts with the hero moment's rally.
- **AC-review-2** A batch contains at most three questions by default.
- **AC-review-3** A persisted fix shows its confirmed cause and effect after refetch; Undo appears only after G-14 implements a working reversal and downstream recomputation.
- **AC-review-4** Changing a winner explains the re-count in plain language.
- **AC-review-5** Skipping never penalises or nags.
- **AC-review-6** Fixes persist and survive re-analysis (existing deterministic refold).
- **AC-review-7** Without a verified offline queue, an offline fix is not accepted and is clearly marked unsent. If a queue is built, it must reconcile against event versions before claiming success.

---

## 9. Place your court — `/matches/$matchId/court`

### Purpose
Get the court geometry right **without ever making an amateur feel they failed a technical test**. Auto-detect first; one-tap confirm; manual adjust only if needed. Shares the **`PlaceYourCourt`** component with onboarding (03).

### Who and when
- **Onboarding** (during New match) — usually auto-confirmed.
- **Later**, when the Recap says *"We couldn't find your court"* or the fit is Rough.
- **Advanced users** wanting to refine net posts and service lines.

### Entry points
New match step 4, Deep dive banner, `CourtFitBadge`, Recap `ReviewBanner`. (Replaces `/sessions/$id/calibrate`.)

### Layout — mobile (auto-found)
```
┌────────────────────────────────┐
│ ← Place your court             │
│ ┌── frame with court overlay ─┐│
│ │  ◇ ─────────────── ◇        ││ 4 corner handles
│ └─────────────────────────────┘│
│ Here's the court we found.     │
│ Fit: Great ✓  (lines match)    │
│ [ Looks right ]  [ Adjust ]    │
│ Different camera angle later?  │
│ Pick another moment ▸          │
└────────────────────────────────┘
```

### Layout — mobile (adjust)
```
│ Drag each corner onto the court │
│ ┌ frame ──────────────────────┐│
│ │   [loupe ◉ above finger]    ││
│ └─────────────────────────────┘│
│ ● Near left  ○ Near right ○ …  │ step chips (4 required)
│ Undo  Reset  [ Save court ]    │
```

### Layout — desktop
Frame left (large, paused); right panel: **Fit state**, point list (4 required + optional net posts and service lines), segment picker for multi-camera videos, history/undo, **Re-detect automatically for the whole video**.

### Components used
`PlaceYourCourt`, `CourtFitBadge`, `ClipPlayer` (frame), `FramingChecklist` (hints), `UnsupportedFootageState`, `ChangeSummaryBanner`, `FailedState`, `PreviewTag`.

### Data in / API mapping (existing)
| UI field | Source |
|---|---|
| Frame + proposal | `GET …/calibration/proposal?segment=` → `{frame, width, height, reference_points, …}` |
| Current calibration | `calibration` event (`Calibration.mode`, `source`, `quality`, `coverage`, `lines_check`) |
| Auto re-detect | `POST …/calibration/auto` (202) |
| Save manual | `POST …/calibration` (202) with points; client-side homography fit/reprojection (`fitHomography`, `reprojectionError`) |
| Points order | existing `ORDER`: 4 required corners (near-left, near-right, far-right, far-left), then net posts, then short-service-line ends |
| Fit wording | `quality.precision` bands → **Great / Good / Rough** (thresholds set in 06; words only) |

### Mode wording (replaces `lines/camera/static` jargon)
| `Calibration.mode` | Plain label |
|---|---|
| `lines` | "Following the court lines in every frame" |
| `camera` | "Following the camera as it moves" |
| `static` | "One fixed view" |
| `source: human` | "Set by you and then followed" |

### Copy
- **Heading:** "Place your court".
- **Auto success:** "Here's the court we found. Does it sit on the lines?"
- **Auto fail:** "We couldn't find the court lines. Drag the four corners onto the court. It takes about a minute."
- **Why it matters (collapsible):** "Positions, heatmaps and where the shuttle landed depend on the court. A better fit means more reliable maps."
- **After save:** "Updating your match with the new court. Your fixes stay."
- **Different cameras:** "This video shows more than one camera. We follow the main one and skip the rest."
- **Banned:** "Calibration error", "reprojection", pixel numbers (below Advanced).

### Interactions
- **Looks right** → confirms (clears banner, may trigger a re-fold).
- **Adjust**: drag handles; loupe shows a 3× magnified view (fine-pointer and touch); **arrow keys** nudge ±1 px, **Shift** ±10 px; **Tab** moves between handles; **Undo/Reset** available.
- **Pick another moment** loads a different `segment` for a clearer frame.
- Advanced: add net posts and service-line points (optional); show reprojection error and `lines_check` text.
- After saving, a `ChangeSummaryBanner` states which analytics will update (positions, heatmaps, in/out).

### States
| State | Behaviour |
|---|---|
| loading | Frame skeleton; proposal pending |
| empty | n/a |
| partial | Proposal found with low precision → "We found a court but it's Rough — adjust or continue" |
| complete | Fit chip Great/Good |
| low-coverage | `coverage` low (court visible in part of the video) → explains which parts won't be mapped |
| failed | Unsupported footage → `UnsupportedFootageState` with reasons (cropped, too dark, moving camera) and a filming tip |
| permission | Only owner can change |
| offline | Save disabled with reason |
| demo | Demo only; no calibration saved |

### Depth / Preset behaviour
Quick/Relax: auto + one tap; manual hidden behind "Adjust". Guided: adds fit explanation. Advanced: all points, numbers, mode readout, segment list. Compete: always shows numeric fit and segments.

### Accessibility
Handles are focusable buttons with labels ("Near left corner, 312, 548"); keyboard nudging as above; the loupe is decorative (`aria-hidden`) with numeric position announced; the fit state is text; no timed interactions.

### Telemetry
`court_confirmed`, `court_manual_started`, `court_manual_saved`, `court_redetect`, `court_failed` (reason), `court_segment_changed`.

### Acceptance criteria
- **AC-court-place-1** With a good auto-fit the user confirms in one tap.
- **AC-court-place-2** Manual placement works with touch, mouse and keyboard.
- **AC-court-place-3** The fit is described in words (Great/Good/Rough), not numbers, below Advanced.
- **AC-court-place-4** An unsupported frame explains why and offers a filming tip.
- **AC-court-place-5** Saving does not discard the player's earlier fixes.
- **AC-court-place-6** The same `PlaceYourCourt` component is used in onboarding and here.

---

## 10. Advanced workspace — layout mode of Deep dive (`?view=table`, Advanced depth)

### Purpose
Give serious players and coaches **event-level access, filters, coverage and export** without a separate product. It is **not** a new top-level section (Blueprint §5.1): it is Deep dive with dense layouts and an extra tab.

### Who and when
Competitive players, coaches, researchers; desktop.

### Layout (desktop)
```
┌──────────────────────────────────────────────────────────────────────────────┐
│ Deep dive · Advanced   Story Rallies Shots Court Compare Ask  [Events] [Export]│
├────────────────────────────────┬─────────────────────────────────────────────┤
│ Filters (saved)                │ EventTable (virtualised)                    │
│ type · player · shot · check · │ Time │ Type │ Player │ Shot │ Check │ Status │
│ status · game · counted        │  …   │ …    │ …      │ …    │ …     │ …      │
├────────────────────────────────┴─────────────────────────────────────────────┤
│ Quality panel (open) · Corrections made · Exports                             │
└──────────────────────────────────────────────────────────────────────────────┘
```

### Components used
`EventTable`, `RallyFilterBar`, `QualityPanel`, `ExportList`, `EvidenceChip`, `CheckChip`, `MetricPopover`, `DepthSwitcher`.

### Data in
| UI field | Source |
|---|---|
| Events | `GET …/events` (`BaiEvent`: `type`, `frame_start/end`, `actors`, `payload`, `band`, `status`, `evidence[]`, `provenance`, `supersedes`, `seq`) |
| Event types | ontology (`contact, stroke, serve, rally_start, rally_end, point, game_end, match_end, interval, side_switch, camera_cut, replay_start/end, highlight, insight, degraded, calibration, scene, match_phase`) |
| Corrections | events with `status ∈ {corrected, human_verified, retracted}` and `supersedes` chains |
| Exports | `exportUrl(sessionId, kind)`: `report.pdf`, `rallies.csv`, `legacy.csv`, `events.jsonl`, `summary.json`, `clip.mp4?from&to` |

### Exports (rewritten)
| Kind | Plain label | Audience note |
|---|---|---|
| `report.pdf` | **Match story (PDF)** | Currently an analyst table; an amateur *shareable story* variant is specified in 06 |
| `rallies.csv` | Rallies table | |
| `events.jsonl` | **Event log (source of truth)** | One JSON event per line, with evidence, check state and corrections |
| `summary.json` | Summary | |
| `legacy.csv` | Classic CSV | Hidden unless the old tool is in use |
| `clip.mp4` | Clip | Per moment, in the Share dialog |

### Copy
"Event log — every event with its evidence, check state and corrections. This is the source of truth the rest of the app is built from." · "Exports include everything analysed so far." (while analysing).

### Interactions
Column sort/filter; click a row → seeks and opens `RallyDetailPanel`; save/restore filters (Compete: *Saved filters*); copy link to frame; select rows → "Make a playlist" (share with a coach, 05c). Event IDs are copyable.

### States
Same as Deep dive. Empty filter: "No events match these filters. Clear filters".

### Depth / Preset behaviour
Visible only at **Advanced**. Compete preset enables it by default.

### Accessibility
A real `<table>` with sortable headers (`aria-sort`), virtualisation exposes correct row counts, keyboard row navigation, visible focus.

### Telemetry
`advanced_opened`, `event_table_filter`, `event_row_opened`, `export_downloaded` (kind), `playlist_started`.

### Acceptance criteria
- **AC-adv-1** Every number shown elsewhere is traceable to rows in the event table.
- **AC-adv-2** Corrections and their `supersedes` lineage are visible.
- **AC-adv-3** Exports state what they include and whether the match was still analysing.
- **AC-adv-4** Advanced views never remove evidence or caveats.

---

## 11. Quality panel — compact in the shell, full on demand

### Purpose
Make **uncertainty a designed part of the interface** by separating three different things that are usually blurred into one badge (Blueprint §8.3).

### Layout
Compact line in the shell: **`◐ We followed 31 of 36 rallies · Court fit: Good · 2 things to check ▸`**. Tap/Enter opens a bottom sheet (mobile) or side panel (desktop).

```
What we could see
  ● Recording coverage     Followed 31 of 36 rallies. 3 on another camera; 2 out of view.
  ● Court                  Good fit · Following the court lines in every frame
  ● Shots                  Preview · 31 of 245 shots were unclear and aren't counted
  ● Score                  Looks right · 8 of 21 rallies Checked
  ● Reading                Some detail reduced: shot types (running on a lighter setting)
What isn't counted
  Warm-up 5 rallies · Replays 1 · Other camera 3 min   [Count it]
Things we changed with you
  Rally 22 winner · Rally 31 counted      [See history]
Technical (Advanced)
  Profile cpu-dev · models … · calibration id … · ontology v1
```

### Three distinct uncertainties (never merged)
| Type | Question | Example label |
|---|---|---|
| **Recording coverage** | How much was analysable? | "Followed 31 of 36 rallies" |
| **Label reliability** | Is this shot/rally label likely right? | "Shot types are a Preview" / "Worth a look: 3 rallies" |
| **Interpretive support** | Does the data support this explanation? | "Several explanations fit — a coach can help" |

### Components used
`QualityPanel`, `CoverageBar`, `CourtFitBadge`, `CheckChip`, `PartialAnalysisNote`, `ChangeSummaryBanner`, `MetricPopover`.

### Data in
| UI field | Source |
|---|---|
| Rallies followed / skipped | `rally_end` events + `scene` events (`ScenePayload.view`, `analysed`, `duration_s`) |
| Other-camera/none durations | sum of `ScenePayload.duration_s` by `view` |
| Court | `Calibration` (`mode`, `quality.precision`, `coverage`, `adjusted_px`, `lines_check`) |
| Not counted | `rally_end.payload.official=false` + `phase_reason`, `match_phase` events |
| Degradations | `StatusMsg.degraded[]` and `degraded` events (`stage`, `reason`) |
| Checked count | events with `status ∈ {human_verified, corrected}` |
| Provenance (Advanced) | `BaiEvent.provenance.model/profile`, `Session.profile` |
| Calibrated confidence bands | Until calibrated → shown only as the word-states of D5 |

### Copy
Use the lines in the layout above. **Never** show raw model confidence or "92 % sure".

### Interactions
Open/close; **Count it** reinstates uncounted rallies (`setRallyOfficial`); **See history** opens corrections; Advanced reveals technical rows.

### States
loading skeleton · empty: "We followed everything we could see." · partial: "Still reading — numbers may change" · failed: cause · offline: stale label · demo: sample.

### Depth / Preset behaviour
Quick(upgraded): compact line only. Guided: full panel with plain rows. Advanced: + technical rows and provenance.

### Accessibility
Each row is a definition list (`dt/dd`); status uses icon + word + shape; the sheet traps focus and returns it on close.

### Telemetry
`quality_panel_opened`, `uncounted_reinstated`, `corrections_history_opened`.

### Acceptance criteria
- **AC-quality-1** The three uncertainty types are always separate rows.
- **AC-quality-2** No percentage confidence appears.
- **AC-quality-3** Every "not counted" item can be reinstated.
- **AC-quality-4** The compact line is visible on every Deep dive screen.

---

## 12. Cross-screen telemetry and state matrix (this file)

| Screen | loading | empty | partial | complete | low-cov | failed | permission | offline | demo |
|---|---|---|---|---|---|---|---|---|---|
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

## 13. Gaps referenced (proposed IDs; `11` is authoritative)

| Gap | Used here for |
|---|---|
| G-04 | True unscored processing for Social/Practice, including insights and exports; hiding scores alone is insufficient |
| G-01 | "Which one is you" mapping used in every Deep dive sentence |
| G-07 | Metric definitions/versions for Compare and MetricPopover |
| G-29 | Insight/narration service behind StoryParagraph and Ask-adjacent claims |
| G-14 / G-15 | G-14: saved change summary and reversible undo. G-15: extra correction kinds, including shot/identity; feedback alone never mutates results |
| G-20 | Court-fit and coverage in plain language (Great/Good/Rough; followed N of M) |

## 14. Components named here that are not in `00 §6`

`DeepDiveShell`, `SubNav`, `RallyFilterBar`, `ShotSequenceTable`, `ZoneTable`, `QualityPanel`, `EventTable`, `FixQueue`, `CourtFitBadge`, `AnswerFeedback`. Add to Doc 07. (`QualityPanel` and `CoverageBar` are in 00 §6 as `CoverageBar`; `QualityPanel` is new.)

## 15. Contradictions with `00` found while writing

- 00 §7 lists **"Active play / movement variety — Preview"** while the existing `PlayerStats.distance_m` is ungated; this file shows *no distance in metres* and keeps `movement` heatmaps relative (consistent with "distance — Not yet").
- 00's route map has no route for the Advanced workspace; this file specifies it as a **layout mode of Deep dive** (`?view=table`), not a new route.
- The existing **HighlightsTab** shows `Highlight.score` (0–10); 05a removes it below Advanced. Doc 06 must define the "Rank score" label for Advanced.
