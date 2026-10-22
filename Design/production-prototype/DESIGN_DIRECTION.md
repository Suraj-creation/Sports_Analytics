# DESIGN_DIRECTION — Rally

**Status:** The design direction for the production prototype, rewritten after the first version was rejected for hiding the analytics.
**Scope:** design only. No backend, API, model, auth or production application code is changed.
**Built at:** `apps/web/prototype.html` + `apps/web/src/prototype/**`.

---

## 0. The correction this document exists to record

The first version of this direction made one mistake, and it ran through everything: it treated
"amateur" as "needs less". It withheld numbers behind trust labels, reduced the match to three
facts and a video card, marked most of the engine's output as *Preview* or *Not enough to say*,
and shipped an overlay instead of a player.

That was wrong about the audience and wasteful of the product. The people who play on these
courts are adults paying for a recreational activity. They are not analysts, but they are not
incapable of reading a chart — and the analysis they are paying for is the reason they are here.
Hiding it is not kindness.

**The corrected principle: present everything the engine knows, and do the work of making it
legible.** The design problem is representation, not restraint. If a metric is technical,
translate it; if it is uncertain, say where it gets soft; if it is dense, give it a layer of its
own. Do not remove it.

Two other corrections of the same kind:

- **The player is the product's spine, not a modal.** The old build opened clips in an overlay
  with no transport controls. The player is now a real one — play/pause, frame step, rally step,
  scrubber over the whole match, speed, overlay layers, fullscreen, keyboard — and it lives at the
  top of the match page. Every number, insight and moment anywhere in the product seeks *that*
  player and scrolls it into view.
- **Doubles is a first-class discipline.** The engine's two-track `PlayerId` was allowed to become
  a product decision. The prototype's model is N players with sides, so a doubles match carries
  four players, per-player analytics, and a pair surface of its own.

---

## 1. What the engine actually produces

This is the inventory the design is built to present. It is taken from the live app
(`StatsTab`, `HeatmapsTab`, `HighlightsTab`, `RalliesTab`, `VideoStage`) and the engine contracts,
not from a specification.

| Group | What exists |
|---|---|
| **Per player** | points won/lost, winners, errors out, errors net, shot counts across 12 stroke types, smashes, jump smashes, points won with a smash, serves, serve points won, distance covered, points won under pressure |
| **Per match** | rally count, average and longest rally, active play time, EWMA momentum with run length, momentum shifts, full score timeline, warm-up/replay rallies kept but uncounted |
| **Per rally** | frame boundaries, shot-by-shot sequence with stroke and subtype, winner, outcome (winner/out/net), why it ended, whether it counted, score after |
| **Court** | five heatmap kinds per player — presence, movement, shot origin, where shots were met, targeting — on a calibrated floor, plus the 3 × 3 zone ontology |
| **Moments** | 0–10 excitement score with a **reasons decomposition**, eleven categories, MMR diversity re-ranking |
| **Movement** | distance in metres; steps derived from it at an average stride |
| **Agent** | grounded answers where every number traces to an event |

The prototype derives all of this from generated rallies and shots rather than hand-writing
figures, so every number on every screen can be traced back to the rally that produced it.
That is also the honesty mechanism: if a card says 22 shots, rally 80 has 22 shots in it.

---

## 2. Design philosophy

**P1 — Depth, made legible.** Show the whole catalogue. Earn the right to show it by naming
what each number means, in the player's language, right next to it.

**P2 — Every number opens its evidence.** A figure you cannot watch is a figure you cannot check.
Charts, tiles, rally rows, shot chips and insight lines all seek the player.

**P3 — Narration under every analytic.** Each panel carries one to four generated sentences that
say what its own numbers mean, with the frame attached. The sentences are produced from the data
deterministically — the agent phrases, it never invents the figure.

**P4 — The player is the subject.** Comparisons are against the player's own history and against
the people actually on court. No ranking, no grade, no score out of ten shown to a player.

**P5 — Say where it gets soft, then show it anyway.** Shot naming is rule-based; placement is the
receiver's position, not a landing point; distance carries tracking jitter. Each is marked
*Preview* with the specific reason — and then the full chart is drawn.

**The anti-brief.** Not a dashboard of gauges, not a coaching app that tells you what you did
wrong, not a fitness tracker, not a game with points.

---

## 3. Information architecture

Eight routes. The depth lives in tabs and query state, not in more pages.

| Route | What it is |
|---|---|
| `/` | Home — the latest match with its real numbers, week totals, trends, bests, people |
| `/matches` | Every match, each card carrying rallies, longest rally, shots, distance, moments |
| `/matches/$id` | **The match workspace** — the player plus nine analysis tabs |
| `/moments` | Every moment across every match, filterable by category and by player |
| `/progress` | Trends · Personal bests · Shot repertoire · Your story |
| `/people` | Partners (with pair chemistry) and opponents |
| `/settings` | Privacy · Your data · Display · Notifications |
| `/help` | What each metric means, how it is measured, where it stops being reliable |

### The match workspace

```
┌──────────────────────────────────────────────────────────────┐
│ title · date · venue · discipline · score · coverage         │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│                    THE PLAYER (16:9, ≤56vh)                  │
│         court reconstruction · overlays · score bug          │
│                                                              │
│  ◆──▮▮▮─◆─▮▮▮▮──│──▮▮─◆──▮▮▮▮▮──  scrubber: rallies,        │
│                                   moments, game breaks       │
│  ▶ ⏮ ‹ › ⏭  0:00 / 49:39  frame 0      1× 🔇 ☰ ⛶           │
├──────────────────────────────────────────────────────────────┤
│ Showing: [Alex (you)] [Priya] [Rahul] [Meera]                │
├──────────────────────────────────────────────────────────────┤
│ Overview │ Moments │ Rallies │ Shots │ Court │ Movement │    │
│ Head to head │ Your pair │ Ask                               │
├──────────────────────────────────────────────────────────────┤
│ panels: chart + table toggle + generated narration + watch   │
└──────────────────────────────────────────────────────────────┘
```

**Overview** — four stat tiles, the moment of the match, the momentum chart, and a strengths
panel with six counts and generated narration.
**Moments** — every ranked moment with its categories, its credits, and the ranker's own reason
decomposition behind a disclosure. Filterable.
**Rallies** — the full list with filters (8+ shots, under pressure, points you won), each row
expanding to the complete shot sequence as clickable chips, plus a rally-length histogram.
**Shots** — shot mix across all players, attack/neutral/defend split per player, which shots ended
rallies, serve conversion.
**Court** — all five heatmap kinds, every player side by side, plus the 3 × 3 zone tables.
**Movement** — distance, steps, active time, work rate, per-player comparison, movement maps, and
the cross-match trend.
**Head to head** — fourteen mirrored rows per side (summed for a doubles pair), with a who-is-who
panel.
**Your pair** (doubles) — rallies both partners built, times one covered the other, attack-then-net
combinations, the front/rear split, both presence maps side by side, and the shared moments.
**Ask** — grounded answers with watch chips; refuses rather than guesses.

**The whose-numbers picker** sits above the tabs. In doubles it is the most important control on
the page, and it drives every tab at once.

---

## 4. The player

| Control | Behaviour |
|---|---|
| Stage | 16:9, click to play/pause, double-click fullscreen, max 56vh |
| Transport | play/pause, previous/next frame, previous/next **rally**, time and frame readout |
| Scrubber | the whole match: one bar per rally (taller = longer), amber diamonds for moments, ticks for game breaks, hover tooltip, click to seek |
| Speed | 0.25× to 4× |
| Layers | shuttle, trail, player markers, name labels, court lines, score bug, analysis zones — persisted |
| Score bug | live score as of the last completed rally, never ahead of the picture |
| Keyboard | Space/K play · ←/→ frame · Shift+←/→ second · J/L rally · F fullscreen |
| Context | current rally number, whether it counted, and the stroke just played |

**There is no footage in the prototype.** Rather than a black rectangle, the stage renders the
match from its own rally and shot data: four players moving between the positions their shots were
played from, the shuttle crossing between them, the trail, the overlays. It says so on screen. Every
control and every overlay behaves exactly as it would over real video, because the overlays are
drawn from the same events.

---

## 5. Visual direction

**Court Daylight** for reading — warm paper `#F6F3EC`, white panels, hairline borders, deep court
teal for action. **Arena Night** for the player stage, always, so overlays stay readable.

Token set adopted from `08_VISUAL_DESIGN_SYSTEM.md` §3 verbatim: those hexes were computed against
WCAG contrast and re-checked under protan/deutan/tritan simulation.

**Identity is colour *and* shape**, because four players need separating and colour alone will not
do it: **you = circle (teal) · partner = diamond (orchid) · opponent 1 = square (charcoal) ·
opponent 2 = triangle (light slate)**. The same glyph is used on the stage, in every legend, on
every chart and in every list.

**Chart rules.** Every panel's heading is the question it answers. Every panel has a table behind
it. Missing is hatched, never zero. No gauges, no radar, no dual axes, no red/green for good/bad.
Flat elevation: a panel is a 1 px border, shadows only on things that float.

---

## 6. Narration

`data/insights.ts` generates the sentences, from the derived numbers, with the evidence frame
attached. Examples the code produces:

> "You kept 363 of your 394 returns in play — 92% of the shots you had a chance to play."
> "Long rallies were more common later on — 21 in the first half of the match, 28 in the second."
> "You covered about 1713 m on court — roughly 2,194 steps — in 17.2 minutes of actual play."
> "You and Priya both hit the shuttle in 57 of your rallies. The longest you built together ran to 22 shots."
> "You favoured their left side — 57% of your shots went there."

Each carries a tone (neutral, strength, worth a look) shown as a dot, never as a colour-coded
verdict. This is the deterministic layer an LLM sits on top of: it may choose and phrase, it may
not invent the number.

---

## 7. Honesty, without suppression

Three signals, kept separate and all visible as text:

- **Coverage** — "We followed 100 of 119 rallies", with the reason, in the match header. Rallies
  the camera could not follow are excluded from every figure rather than estimated.
- **Preview** — a tag on a *capability*, not a number: shot naming (rule-based, uncalibrated),
  placement (the receiver's position, not a landing point), distance (tracking jitter). The tag
  explains the specific limit; the full chart is drawn underneath it.
- **Counted vs not** — warm-up and replayed rallies stay on the timeline and the scrubber, marked,
  and out of every statistic.

What is still never done: no confidence percentages, no ranking against other people, no fitness
or medical claim, no causal sentence, no invented moment. The moment ranker's 0–10 score stays
internal; its *reasons* are shown instead, because the reasons are checkable and the score is not.

---

## 8. Doubles

- Four players, two sides. `PlayerId` is a string, not a two-value union.
- Every per-player analytic works for all four; the picker switches them together.
- Head to head sums a side, so singles and doubles read the same way.
- The pair surface measures what a single camera can actually see: who hit in which rallies, who
  took the next shot after their partner was under pressure, rear-attack-then-net-interception
  sequences, and the front/rear split. It does not claim to know communication or intent, and it
  never assigns fault for a lost point.
- `/people` carries pair chemistry across matches.

---

## 9. Accessibility

WCAG 2.2 AA as the floor, plus three deliberate extras: identity never carried by colour alone
(shape everywhere), a data table behind every chart, and 44 px touch targets rather than the 24 px
minimum. Full keyboard parity including frame stepping and rally stepping; lead changes on the
momentum chart are real buttons rather than a tabbable SVG. One `h1` per route, focus moved to it
on navigation. `prefers-reduced-motion` honoured, plus an in-app switch.

---

## 10. Running it

```bash
cd apps/web && pnpm dev
```

Then **http://localhost:5173/prototype.html**. A second Vite entry point; it shares no code, no
stylesheet and no route with the production app, so nothing in it can change that app's behaviour.
No dependency was added and nothing was committed.

| What to see | Link |
|---|---|
| Doubles, four players, pair analytics | `#/matches/m2?tab=pair` |
| Every heatmap kind, all four players | `#/matches/m2?tab=court&kind=targeting` |
| Distance, steps, work rate, movement maps | `#/matches/m2?tab=movement` |
| Shot mix and attack/defend split | `#/matches/m2?tab=shots` |
| Rally list with full shot sequences | `#/matches/m1?tab=rallies&rally=14` |
| Head to head, 14 rows | `#/matches/m1?tab=h2h` |
| A singles match the player lost | `#/matches/m1?tab=overview` |
| Moment ranking with its reasons | `#/matches/m1?tab=moments` |
| Grounded chat, including a refusal | `#/matches/m1?tab=ask` |
| Deep link straight into the player | `#/matches/m2?tab=overview&f=9000` |
| Partners and pair chemistry | `#/people` |

### Verified

In a browser at 1440 and 375 px, light and dark: all eight routes and all nine match tabs render
with **no console errors**; playback runs in real time and the clock advances; the scrubber,
frame step, rally step, speed, layers and fullscreen all work; `?f=` opens the player already
seeked; every watch control in every tab seeks the player and scrolls it into view. `tsc --noEmit`
passes for the whole app, `biome check` passes for the prototype, and the existing 29 unit tests
still pass.

**Not verified:** no screen-reader pass, no automated contrast run against the rendered DOM, no
200 % zoom pass, no testing with players.

### Known gaps

- Clip download is disabled — it needs the server's `clip.mp4` export.
- Corrections (confirm/change a rally winner) are not wired into this build; the API supports them
  and the rally rows are the right home for them.
- Steps are derived from distance at a fixed stride, not counted from footfalls. Labelled as such.

---

## 11. What was taken from the source blueprints

The three research documents in `Design/` — the Front-End Design Blueprint, the Amateur Product
Blueprint v2 and the Complete Product Design Spec v1 — were read after the rebuild and produced a
further pass. These are the ideas taken, and where each came from.

| From | Idea | Where it landed |
|---|---|---|
| Blueprint §7.9 | **"Sequence view, not terminal-shot view."** Crediting only the last stroke misleads — the document cites a badminton analysis where net shots produced many positive perturbations even though smashes dominated direct winners. | **Tactics → What led to the point.** The last three shots of each rally, split by who won it. The old "which shots ended rallies" panel survives but now points at it, because a finishing shot is rarely the one that made the opening. |
| Blueprint §7.10 | **"Counts AND rates with opportunity denominators; frequency ≠ effectiveness."** | **Shots → What happened when each shot was played.** Times played, times it finished a rally won or lost, and rallies won among rallies it appeared in — every rate with its denominator, and rates suppressed below five opportunities. |
| Blueprint §7.9 | Filters for game, score state, serve/receive, rally length, outcome. | **Rallies → the filter bar**, with a derived score state (level / ahead / behind / 19-all or beyond) and a clear-filters count. |
| v2 §5.7 | Serve and return patterns; attack/defence transitions. | **Tactics → serve and return** (rallies won against the serve that started them, and what the return was) and **→ defence into attack**. |
| Blueprint §7.13 | **"Include counterexamples in analytical reports to avoid highlight bias."** | **Moments → And the ones that got away.** Long rallies that ended on the player's racket, so the reel is not only the flattering half. |
| v1 §15 | Every chart carries title, unit, time window, **sample size or coverage**, explanation, a text alternative and a link to a clip. | A `basis` line on every panel: "Measured over 117 counted rallies." |
| v2 §5.5 | Doubles roles rotate front/rear; both partners serve and receive. | A generator fix — the first build always gave the receive to the same partner, which left the receive analysis empty. |
| Blueprint §7.11 | Singles and doubles are not comparable sessions. | Trend charts mark them with different shapes and say to read them separately. |
| v1 §19 | "In the observed rallies…" rather than claims about a player's whole ability. | Insight phrasing throughout, and the association-not-cause note under shot effectiveness. |

**Deliberately not taken.** The capability ladder as a *presentation* device (Available / Preview /
Not yet applied to whole surfaces) — the first build did that and it hid the product. Only the
genuinely young capabilities carry a Preview tag now, and the chart is drawn underneath it.
Gamified awards (Smash King, Net Ninja) are also left out: v2 marks them optional, and they pull
against the rest of the design.

---

## 12. The gap-closing pass

An audit against everything asked for found roughly a quarter missing. This pass closed it.

| Gap | What was built |
|---|---|
| **"Which one is you?"** had been dropped in the rebuild | A sheet that opens the first time you open a match: the court as the camera sees it with every player tappable, then a list with each player's shot count, then nicknames for the others. The choice re-centres the whole match — `applyIdentity` remaps who is "you", who is the partner, the colours, the shapes and the side labels, so picking Priya switches every tab to Priya's numbers. |
| **Clip-bounded playback** | `playClip(from, to, label)` is now what every Watch calls. Playback stops at the clip's end instead of running on; a clip bar names it, shows progress, and offers **Again**, **Loop** and **Watch on ›**. The scrubber shades the clip's range. A one-second lead-in means a clip starts just before the thing it is about. |
| **Corrections** | The engine's four correction kinds, inside the expanded rally row: confirm the winner, change it, mark the rally in or out of the match, or set where the match starts. Each one states its knock-on — changing a winner says how many later rallies shift — and a banner at the top of the match lists what changed. No undo is offered, because the server cannot reverse a refold. |
| **Sharing** | A preview showing the actual clip, everyone visible in it (not only the credited player), an approval toggle per person that genuinely blocks the button, an audience choice, and sound stripped by default. |
| **Quality panel** | Coverage, capability and corrections listed separately so one is not read as another, plus provenance: camera, frame rate, frames analysed, shots detected. |
| **Export** | Rallies CSV, events JSONL and summary JSON are generated and downloaded for real. The PDF report and MP4 clips are marked server-only. |
| **Settings buttons** | Both now work. Download produces a real JSON of everything this device holds; delete shows exactly what goes, wipes it, and says plainly that the venue's recording is untouched. |
| **Low-coverage state** | A fixture where the camera was repositioned mid-session: 33 of 74 rallies followed. The match carries an amber banner, and it is excluded from trends and records with a named reason and a link. |
| **Landing page** | Venue-framed, leading with the real numbers from a real match rather than a promise, and a section on where each figure stops being reliable. |
| **Focus bridge** | Set a focus from a match. The ladder is the Blueprint's: reviewed → practised → seen again in play, each rung labelled with what it actually means, and the copy says marking something practised does not mean it worked. |
| **Challenges** | Five optional, dismissible challenges whose progress is computed from the matches — never awarded for opening a screen, never penalising a gap. |
| **Coach playlists** | Pick moments, name the playlist, write **one question**. Access is per playlist and expires. |
| **Reflection prompt** | "Before you look — how did it feel?" above the numbers on a match, asked once, skippable. |
| **Progress annotations** | Singles and doubles are now plotted as separate series. With one match in a discipline it says "that is the baseline, not a trend" rather than drawing a line. |

### Bugs this pass exposed

- The doubles generator always gave the return to the same partner, so the receive analysis was empty and one partner never served. Roles now rotate as the serve changes hands.
- "(you)" followed the fixture rather than the identity choice, so picking Priya still showed Alex's numbers in the picker.
- A shot-mix insight excluded jump smashes from its denominator while the tile above it included them.

### Verified in a browser

Identity end to end (header, picker and every stat switch to the chosen player) · a clip stopping exactly at its end and pausing rather than running on · a correction landing with its knock-on · the share gate blocking on approvals · all three exports producing real files (8.5 KB CSV, 175 KB JSONL, 8.4 KB JSON) · the Settings download producing a real file · the low-coverage banner and its exclusion from trends · the singles/doubles split refusing to draw a one-point trend. No console errors. `tsc`, `biome` and the 29 existing tests all pass.

### Still not done

Match-level refold after a correction (the prototype records the correction and says so, but does not recompute the numbers — that needs the server). Real share links, MP4 clip export and the PDF report, all server-side. No screen-reader pass, no automated contrast run, no 200% zoom pass, no testing with players.
