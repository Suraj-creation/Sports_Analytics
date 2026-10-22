# 02 — Current-State Audit: the existing prototype vs the amateur-first direction

**Scope:** every screen, panel, component, hook, store, API route, analytic and export that exists in `apps/web`, `apps/api`, `sports/badminton`, `engine` and `agents` as of branch `upgrading` (HEAD `b8c1c27`).
**Method:** each file named below was read; each code claim cites the file. Verdicts are tied to decisions **D1–D18** in `00_README_DECISIONS_AND_CONTRACT.md` (file 00).
**Gap IDs:** `G-01 … G-13` are fixed by the main author (used in file 11). `G-14+` are added here (list at the end, §9).

### Verdict legend

| Verdict | Meaning |
|---|---|
| **KEEP** | Ship in the production prototype essentially as is (may be restyled by file 08 tokens) |
| **RESHAPE** | The idea and the engine are right; the surface, copy or defaults must change for an amateur |
| **ADVANCED** | Move behind Depth = Advanced / Deep dive / Compete preset; not on any Quick or Guided surface |
| **DROP** | Remove from the player product (may survive in `/admin`, tests or developer tooling) |

---

## 1. Executive summary — ten findings that shape everything else

1. **It is a good analyst's cockpit, not a player's companion.** Dark "Arena Night", frame numbers in the control bar (`frame 12,043`), per-frame skeleton/shuttle overlays, GPU status page, a passphrase login that tells the user to read `.env`. Every one of these is correct for its first audience and wrong for an amateur (D2, D13, D18).
2. **The evidence layer is genuinely strong and should be kept intact.** Append-only event log with `supersedes`, `band`, `status`, `evidence[]`, `provenance`; deterministic BWF fold; `lineage_ids` re-fold after corrections; grounded Ask agent with a citation validator; frame-exact `?f=` deep links. These are exactly what D16 ("every claim opens its evidence in one tap") needs.
3. **Everything is win/loss-centric.** `PlayerStats` is `points_won / points_lost / win_rate / winners / errors`; the headline component (`StatsTab` → `H2HRow`) is a red-vs-blue head-to-head; `Highlights` are filtered by *who won the rally* (`match.py: highlights(player=…)` → `r.winner == player`). Under D6 and D17 this must be inverted: the loser must get moments too.
4. **The "confirmed" band is not trustworthy as a user-facing signal.** Rally outcomes from the rule cascade return `outcome_confidence` = 0.85 for `HIGH` (→ `confirmed`, ≥ 0.85) while the measured rally-winner accuracy on the validation match was **61.5 % (8/13)** (`docs/testing/accuracy_results.json`). Bands are raw, uncalibrated (G-08). D5 therefore keeps the whole surface under a **Preview** tag.
5. **Shot labels can never be "confirmed".** `RuleStrokeClassifier.MAX_CONF = 0.7` (`events/stroke.py`) with the `confirmed` threshold at 0.85 (`ontology.yaml`), so every rule-classified shot is `probable` at best → "Worth a look" under D5. Shot-level claims stay out of the recap unless a human checked them (D10, G-08).
6. **The "landing" and "targeting" heatmaps are not what their labels say.** `landing_court_xy` is the **receiver's feet position at their contact** (`engine.py:648-650`), not where the shuttle landed; `on_stroke` adds the *same point* to both `landing` and `targeting` (`match.py:131-136`), so the two maps are near-duplicates. The UI hints ("Where their shots go") over-claim (G-10).
7. **Distance and heatmap-from-metres have no geometry gate.** `distance_m` sums per-sample path length (`heatmaps.py: add_path`, `seg > 1.5 m` dropped per step) with no smoothing and no `court_q` check — foot jitter inflates it (ROADMAP gap #7, G-09). It appears in the Stats table and the PDF as a plain number.
8. **The session/player model is a two-track match.** `Session.players` = `P1`,`P2`; the single user is `"u":"local"` (`auth.py`); there is no person, no history, no "me" (G-01, G-02, D8). The upload form asks for "Player 1 · starts on the near side" free text.
9. **Privacy controls are absent and one is misleading.** Delete says "the prepared video stays in the media cache" (`LibraryPage.tsx` dialog) — i.e. delete ≠ delete (G-05, D15). `clip.mp4` re-encodes with the audio track and no consent check. There is no analyse/store/share/train separation.
10. **Correction tooling already exists and is the most amateur-relevant feature in the app** — confirm/flip a winner, mark not-official, "match starts here" (`RalliesTab.tsx` + `/corrections`). It is buried in a developer-style row list. Reshaping it into Review & fix (D11) is the single highest-leverage UI change.

---

## 2. Inventory

### 2.1 Routes / screens (`apps/web/src/router.tsx`)

| Route | Component (file) | What it does today | Verdict | Reason · decisions |
|---|---|---|---|---|
| `/` | `LibraryPage` (`features/library/LibraryPage.tsx`) | Upload card + YouTube card + grid of matches | **RESHAPE** | Becomes `/matches`; upload becomes the guided New match flow; the product Home (`/`) is a new screen · D9, D14 |
| `/sessions/$sessionId` | `SessionPage` (`features/session/SessionPage.tsx`) | Video + timeline + minimap + live feed + 6 tabs | **RESHAPE** | Split into **Recap** (new, `/matches/$matchId`) and **Deep dive** (this page, restyled) · D4 |
| `/sessions/$sessionId/calibrate` | `CalibratePage` (`features/calibrate/CalibratePage.tsx`) | Click 4–10 court points with a 3× loupe, auto-proposal seed, undo, "Re-detect for whole video" | **RESHAPE** | Becomes "Place your court": auto-detect + one-tap confirm; manual clicking only on failure · D9 |
| `/system` | `SystemPage` (`features/system/SystemPage.tsx`) | GPU util/memory/power, host, runners, profiles, model registry (polled every 3 s) | **DROP** (to `/admin/system`) | Operator tool; not for players · D18 |
| (gate) | `LoginPage` (`features/auth/LoginPage.tsx`) | One passphrase field; error text tells the user it is `BAI_PASSPHRASE` in `.env` | **DROP** (replace) | Replaced by accounts/profile (G-01); copy is developer-facing · D9, D18 |
| `*` | `NotFound` (`AppShell.tsx`) | 404 | **KEEP** | Restyle only |

Deep link: `SessionSearch { f?: number }` → `useDeepLink` seeks to a frame. **KEEP** — it is the backbone of "Watch this" (D16).

### 2.2 App shell (`components/AppShell.tsx`)

| Element | Today | Verdict | Reason |
|---|---|---|---|
| `Logo` (shuttle SVG) | Shuttle seen from above in `#18221f` | **KEEP** (re-colour) | Brand mark worth keeping · D13 |
| `NavLink` (Matches/System) | 2 links, `h-8` pills | **RESHAPE** | Becomes `SideNav` / `BottomBar` per file 04 · D14 |
| `AppShell` guard states | Spinner; "Can't reach the Badminton AI server — Start it with `bai serve`" | **RESHAPE** | Developer copy → `OfflineState` · D18 |
| Sign-out | `LogOut` icon | **RESHAPE** | Moves into `AvatarMenu` |

### 2.3 Library page parts

| Part | Today | Verdict | Reason |
|---|---|---|---|
| `UploadCard` | Dashed dropzone, title, "Player 1 / Player 2" names, XHR upload with progress + cancel; limit read from `/api/system` | **RESHAPE** | Keep drop/upload/progress mechanics (`uploadVideo`); replace names with `PickYourself` (D8); add `RecordGuide`, `SuitabilityResult`, consent step · D9, D15 |
| Upload transport | One multipart `POST /api/sessions`, **not resumable** (`routes/sessions.py:create_upload`), error "check your connection and try again" | **RESHAPE** | Blueprint §7.5 requires resumable uploads · G-12 |
| `YouTubeCard` | URL + rights checkbox; disabled copy tells user to set `BAI_YOUTUBE_INGEST=true` in `.env` | **ADVANCED** | Irrelevant to most amateurs; legally sensitive; keep as an explicit "Import a link" option for Compete/demo only · D15 |
| `SessionCard` | Poster (sprite frame at 35 %), title, "P1 vs P2", status chip, `Meter` while analysing, delete on hover | **RESHAPE** → `MatchCard` | Replace "P1 vs P2" and status jargon with date, type, moment count, `CheckChip`; delete must be reachable without hover (touch) · D14, D18 |
| Delete dialog | "…The prepared video stays in the media cache, so adding the same file again doesn't re-encode it." | **RESHAPE** | A player reading "delete" expects deletion; cached copy contradicts D15 · G-05 |
| `Thumb` + `useSprite` + `spriteStyle` | Sprite-sheet poster/scrub thumbnails via `/sprite/*`, polling until built | **KEEP** | Good, cheap poster source for `MatchCard`, `MomentCard` and scrub preview |
| Empty state | "Upload a match video or import one from YouTube to start analysing." | **RESHAPE** | → sample recap + record guide (D9) |

### 2.4 Session page: video, timeline, side panels

| Component (file) | What it does | Verdict | Reason · decisions |
|---|---|---|---|
| `VideoStage` (`player/VideoStage.tsx`) | HLS `<video>` + rVFC presented-frame clock + canvas overlay; "Wait for analysis" gate that pauses playback at the analysis frontier (`SEMANTIC_LEAD_S = 3`); controls: play, ±1 frame, time + `frame N`, speed 0.25–2×, mute, overlay-layer popover, fullscreen | **RESHAPE** → `ClipPlayer` | Core tech is excellent. For Quick/Guided: hide frame counter, layers popover behind "Overlays", **default "Wait for analysis" off** for amateurs (a paused video with "Analysis is catching up" reads as broken) — show recap only when ready · D9, D13 |
| `overlay.ts` `drawOverlay` | Per-frame draw: court lines, shuttle trail, player boxes, 17-point pose skeleton (`SKELETON`), name labels, score bug; honours `scene` (dashed on other cameras) | **ADVANCED** | Skeletons/boxes read as surveillance to a casual player; keep shuttle trail + court lines as optional "Overlays" · D2, D10 |
| `ScoreBug` | Broadcast-style 2-row score, serve dot, game/point flags ("Game point", "Deuce", "wins the match"); state derived for the *presented* frame (no spoilers) | **RESHAPE** | Keep the no-spoiler derivation. Show only for scored matches (D12); hide flags in Relax; "wins the match" removed from Quick (D6) |
| `StrokeToast` | "Jump smash · Axelsen · probable" and "Point Axelsen · shuttle landed out" for 1.4 s | **ADVANCED** | Live shot labelling is Preview and band-qualified; point toast is win-centric · D5, D6 |
| `Timeline` → `Overview` | Whole-match SVG strip: rally rects coloured by winner & band, game boundaries, highlight dots, analysed-so-far bar, hover sprite thumbnail + "Rally N · shots · winner", draggable `role="slider"` | **RESHAPE** → `RallyTimeline` | Excellent a11y base (keyboard ←/→ ±5 s, `aria-valuetext`). Replace winner colouring with neutral rally bars + "you" colour; keep band as fill style · D6, D8 |
| `Timeline` → `Detail` | 60 s canvas, one lane per player, smash/jump-smash glyphs, shot hover tip | **ADVANCED** | Dense; useful in Deep dive → Rallies |
| `RallyBar` | "Rally 47 · 9 shots · P1 serving from the right · Game 2 · 11–9" | **RESHAPE** | Keep shot count; drop server/court wording and game line from Quick · D18 |
| `CourtMinimap` | Live top-down court, player dots with 1.6 s trails, rally path hitter→hitter, in-flight arrow; "near end ← → far end" | **KEEP** (as `CourtMap`) | The signature visual, frame-synced. Recolour: you = `--you`; opponent neutral (D8). Hide "Positions appear once the court is calibrated" dev wording |
| `LiveFeed` | Newest-first list of rally_end, smashes, highlights, game/match end, interval, side switch ≤ playhead (no spoilers) | **ADVANCED** | Analyst running commentary; the amateur equivalent is the Recap · D4 |
| `Header` | Title, "● P1 vs ● P2", status pill with `%` and "× real time", court chip ("Court: auto/set + tracked/calibrated"), "Analyse again", shortcuts | **RESHAPE** | Status → `ProcessingStages`; "× real time" and "Analyse again" → Advanced; court chip → "Court ✓ / Place your court" · D18 |
| `Banners` | Failed (+ "see the server log"), uncalibrated court, degraded stages | **RESHAPE** | Keep the *honesty*; rewrite into `FailedState` / `LowCoverageState` / `PartialAnalysisNote` (file 12 state catalog) · D10 |
| `ShortcutHelp` + `useShortcuts` | Space/K play, ←/→ frame, Shift+←/→ 5 s, J/L 10 s, [ ] prev/next rally, S next smash, `.` hide overlays, `?` | **KEEP** | Keep all; hide "next smash" label in Relax (smash is Preview) |

### 2.5 Session tabs

| Tab / component | Today | Verdict | Amateur home · reason |
|---|---|---|---|
| **Stats** `StatsTab` + `H2HRow` | 10-row head-to-head bar table (points won, winners, errors out/net, smashes, jump smashes, smash points, serve points, pressure points, distance) | **ADVANCED** | Deep dive → Story, "Compare players" off by default. Red/blue winner framing violates D6; distance violates D10 (Not yet) |
| `Momentum` (EWMA chart, hover tooltip, shift markers) | Area chart above/below axis, "momentum over the last points" (API keeps last 60) | **ADVANCED** | Deep dive → Story only, Compete preset. Momentum language implies who is "winning the match" · D6 |
| `StrokeMix` | Paired bars per shot type per player | **RESHAPE** | Becomes `ShotMix` for *you only* + "spotted" wording, Preview · D8, D10 |
| **Heatmaps** `HeatmapsTab` + `HeatCanvas` | 5 kinds × 2 players on a canvas court; sequential single-hue ramp; hover "% of busiest area"; empty until calibrated | **RESHAPE** | Keep `presence` ("Where you stood", Preview). `movement` duplicates presence at lower value → ADVANCED. `landing` and `targeting` → merge into one Preview map (G-10) and rename. Fix hover wording ("busiest area") · D10 |
| **Highlights** `HighlightsTab` | Ranked list (1…12), category pills, "Why:" top-3 reasons, score `0–10` as a big number, play (seek + play) and download (`clip.mp4`); filter Both / P1 / P2 | **RESHAPE** → Moments | Remove the numeric score (false precision, D5); replace "Ranked by excitement" with lenses (file 06 §7); "P1/P2" filter is by *winner* — wrong semantics (D17) |
| **Rallies** `RalliesTab` + `RallyRow` | Per-rally rows: clock, "Rally N"/"Warm-up", winner chip with band, shot count, "shuttle landed out", expand to shot chips (jump to shot), end reason, "Count this rally / Not part of the match", "Match starts here", "Is the winner right?" confirm/flip; "Only rallies that need a look" filter | **RESHAPE** → Review & fix + Deep dive → Rallies | The best amateur-relevant feature (D11). Needs friendlier prompts, ≤3 questions, change summary + undo (not present today) |
| **Ask** `AskTab` + `Answer` | Chat, 4 suggestion chips, `[[ev:ID]]` citation chips that seek, "background source" chips, grounded/ungrounded footer, provider banner ("Set BAI_LLM_PROVIDER … in .env") | **RESHAPE** → Coach chat | Keep grounding + chips. Suggestions are win-centric ("How did X win most of their points?") and prescriptive ("What should X change in the next game?") — rewrite per preset (file 06 §9). Remove `.env` copy |
| **Export** `ExportTab` | PDF report, rallies CSV, "Classic CSV" (Streamlit), events JSONL, summary JSON | **RESHAPE** | Add shareable *Match story* card; keep analyst exports under Advanced (file 06 §8) |

### 2.6 UI primitives (`components/ui.tsx`, `styles.css`)

| Item | Today | Verdict | Note |
|---|---|---|---|
| `Button` (primary/secondary/ghost/danger, sm/md, busy) | `h-8`/`h-10` | **KEEP** | Raise targets to 44 px on touch (file 08) |
| `IconButton` (label required) | `size-9`, `aria-label` + `title` + `aria-pressed` | **KEEP** | Enforce ≥ 44 px on mobile |
| `Spinner`, `Meter` (progressbar role) | | **KEEP** | `Meter` must never show a fabricated percentage (see §6 R-12) |
| `BandChip` | solid = confirmed, outlined + "probable", dashed + "uncertain" | **RESHAPE** → `CheckChip` | Same shape language (non-colour encoding ✓). Words become Checked / Looks right / Worth a look (D5) |
| `PlayerDot` | P1 blue / P2 orange | **ADVANCED** | Only in Deep dive compare (D8) |
| `Empty`, `ErrorNote` | Title+body; red alert box with raw `error.message` | **RESHAPE** | `ErrorNote` echoes `detail` strings from the API ("see the server log") — needs a friendly-error mapper · D18 |
| `Field`, `inputClass`, `Kbd` | | **KEEP** | |
| Tokens: `--color-mat #103129`, `stand #18221f`, `seam`, `line/2/3`, `p1 #4290e0`, `p2 #e2701f`, `signal #3ddc97`, `alert`, `caution`, `radius-card 14px`, Archivo variable (wdth axis), `.numerals`, `.tabular`, `.panel`, `.band-*` | "Arena Night" | **KEEP** as the dark theme | Becomes one of two themes (D13); `signal` stays "system/AI activity only" |
| `prefers-reduced-motion` rule, `:focus-visible` ring | Present | **KEEP** | Already meets part of D-accessibility |

### 2.7 Shared libs, stores, hooks

| Module | Role | Verdict | Note |
|---|---|---|---|
| `lib/api.ts` (`api`, `uploadVideo`, `exportUrl`, `hlsUrl`, CSRF double-submit, `ApiError`) | Typed REST client | **KEEP** + extend | Add profile/consent/clip/progress endpoints (file 11). `req()` surfaces `detail` verbatim |
| `lib/types.ts` | Mirrors pydantic contracts; `PlayerId = "P1" \| "P2"` | **RESHAPE** | Generalise `PlayerId` (G-03); add `MetricValue`, `Insight`, `Clip` (G-06, G-07) |
| `lib/format.ts` | `clock`, `playerName`, `shortName`, `STROKE_LABEL`, `OUTCOME_LABEL`, `CATEGORY_LABEL`, `STATUS_LABEL`, `PLAYER_HEX` | **RESHAPE** | Becomes the single plain-language dictionary (D18); `shortName` takes the *last token* of a name — breaks for nicknames ("Big Raj") and single-name Indian names |
| `lib/frameClock.ts`, `lib/tracks.ts` (`TrackBuffer`), `lib/events.ts` (`EventLog`, client fold of `supersedes`/retracted), `lib/socket.ts` (msgpack WS, lossless resume by `last_seq`), `lib/homography.ts` (DLT preview), `lib/court.ts` (13.4 × 6.1 m, singles 5.18) | Real-time engine room | **KEEP** | Do not rewrite; all of it supports Deep dive and `ClipPlayer` |
| `lib/court.ts` `WIDTH_SINGLES = 5.18` | | **KEEP** | Needed for the singles in/out rule already used by the engine |
| `stores/session.ts` (`useSession`) | Mutable buffers + version counters; WS message reducer (`hello`, `events`, `tracks`, `status`, `ingest`, `state`) | **KEEP** | Version-counter pattern is right; add a *profile/preferences* store separately |
| `stores/playback.ts` (`usePlayback`) | `frame`, `playing`, `layers` (persisted in `localStorage` key `bai.layers`), `waitForAnalysis` (default **true**), `seekFrame` | **RESHAPE** | Default layers: pose/players off for non-Advanced; `waitForAnalysis` default off outside Advanced |
| `features/session/derive.ts` (`stateAt`, `rallies`, `currentRally`, `isSmash`, `isJumpSmash`, `INITIAL_STATE`) | Pure derivations | **KEEP** | `INITIAL_STATE` assumes `server: "P1"`, 0–0 — must not render for unscored match types (D12, G-04) |
| `features/player/useHls.ts` | EVENT-playlist HLS that grows during encode, `startPosition: 0`, retries 404 | **KEEP** | Gives first-seconds-playable behaviour; reuse in `ClipPlayer` |
| `useAnalytics` (in `StatsTab.tsx`) | Query keyed by `analyticsVersion` | **KEEP** | Move to its own module |
| Tests: `components.test.tsx`, `derive.test.ts`, `buffers.test.ts`, `homography.test.ts`, `stores/session.test.ts`; Playwright `e2e` | | **KEEP** | Extend per acceptance criteria (file 12) |

### 2.8 API surface (`apps/api/src/bai_api`)

| Route | Used by | Verdict | Production role · gap |
|---|---|---|---|
| `GET /api/auth/me`, `POST /login`, `POST /logout` | AppShell/Login | **RESHAPE** | Single `"u":"local"` principal, 14-day cookie, brute-force throttle (10/5 min), double-submit CSRF. Replace with per-user accounts (G-01); **keep the CSRF + throttle patterns** |
| `POST /api/sessions` (multipart upload: file, title, player1, player2, profile) | UploadCard | **RESHAPE** | Needs match type, "who am I", consent snapshot, resumable transfer (G-04, G-05, G-12) |
| `POST /api/sessions/youtube` | YouTubeCard | **ADVANCED** | Rights acknowledgement present; keep |
| `GET /api/sessions` (limit ≤ 500), `GET /{id}`, `PATCH /{id}` (title, player1, player2), `DELETE /{id}` (204) | Library/Session | **RESHAPE** | PATCH can only rename players; needs `me`, match type, notes, privacy. DELETE does not remove cached media (G-05) |
| `POST /{id}/start`, `/stop`, `/reanalyse` (202) | Header | **KEEP** (Advanced) | Re-analyse after calibration/rule change. "Resumes from the perception cache, never redoes GPU work" |
| `GET /{id}/events` (since `last_seq`, filters), `GET /{id}/state`, `GET /{id}/tracks` | WS/overlay | **KEEP** | Evidence backbone |
| `POST /{id}/calibration` (points, frame), `GET /calibration/proposal` (segment, frame), `POST /calibration/auto` | Calibrate | **RESHAPE** | Wrap in "Place your court"; proposal quality drives pass/fail (G-11) |
| `POST /{id}/corrections` kinds `winner`, `official`, `match_start`, `verify` | RalliesTab | **KEEP** + extend | Needs `undo`, a **change summary** (which stats moved), batch, and `strokes`/`identity` kinds (G-14, G-15) |
| `GET /{id}/analytics` (`MatchAnalytics.to_public()`) | StatsTab | **RESHAPE** | Replace with a metric-registry response (G-07) |
| `GET /{id}/heatmap?player&kind` | HeatmapsTab | **RESHAPE** | Add coverage/valid-frame count (G-09) |
| `GET /{id}/highlights?k&player&diversity` | HighlightsTab | **RESHAPE** | Replace with `/moments` (lens, fairness, consent) (G-06) |
| `GET /{id}/hls/{name}`, `/sprite/{name}`, `/proxy.mp4` | Player/Thumb | **KEEP** | Add per-clip signed URLs when sharing exists (G-05) |
| `GET /{id}/exports/events.jsonl` (`live=true`), `/rallies.csv`, `/legacy.csv`, `/clip.mp4` (from, to, pad_s ≤ 10; libx264 CRF 20, AAC audio, ≤ 10 min, cached by range), `/report.pdf`, `/summary.json` | ExportTab/Highlights | **RESHAPE** | `clip.mp4` keeps audio + no consent check + no watermark/story card; add Match-story image/PDF (file 06 §8) |
| `POST /{id}/ask`, `GET /{id}/ask/provider` | AskTab | **KEEP** | Grounded; rewrite prompts/suggestions for Coach chat |
| `GET /api/health`, `/api/system`, `/api/models`, `/metrics` | System/ops | **DROP** from player UI | `/api/system` still supplies `limits.max_upload_mb`, `max_duration_min` — surface these in the Record guide |
| `WS /ws/sessions/{id}` (`hello`, `events`, `tracks`, `status`, `state`, `reply`; client `playhead`, `seek`, `tracks`) | useSession | **KEEP** | `status` already carries `degraded[]` and `rate_x` — feed `ProcessingStages` honestly (G-12) |
| `GET /{path:path}` SPA fallback | | **KEEP** | |

### 2.9 Engine, rules and agent modules the UI depends on (read-only for design)

| Module | What it gives the product | Design note |
|---|---|---|
| `events/rally_fsm.py`, `events/contact.py` (`contact_fusion_v0` F1 0.941 on synthetic) | Rally boundaries, contacts | The reliable core; lead with it (D10) |
| `events/rally_outcome.py` `analyze_rally_end` | Cascade CHECK 0–7 → `out/net/winner/unknown`; fault side; `HIGH/MEDIUM/LOW` → 0.85/0.7/0.4 (`unknown` 0.2) | Ported from a legacy rule engine "85.7 % on 399 rallies"; depends on a calibrated court and a visible shuttle; singles in/out uses singles sidelines |
| `events/match_phase.py` | Official vs warm-up/replay, reviewer markers, scoreboard seeding | Great for broadcast; amateur "casual rally" has no scoreboard → phase falls back to serve-formation evidence (needs calibrated court + both players' feet) |
| `events/stroke.py` `RuleStrokeClassifier` (`stroke_rules_v0`, `MAX_CONF = 0.7`) | 12 strokes + `jump_smash` subtype | Always `probable` at best (finding 5) |
| `rules/bwf.py` | Deterministic 21-point singles state machine | Not appropriate for unscored games (D12, G-04) |
| `perception/court_lines.py` | Per-frame line-based court fit, camera identity | Strong; quality record drives `Place your court` |
| `perception/scoreboard.py` + `score_ocr.py` | Reads score bug (RapidOCR ~1.2 s/read CPU) | Absent on amateur video |
| `analytics/match.py`, `rebuild.py`, `heatmaps.py` | Fold → stats/highlights/heatmaps | Detailed in §3 |
| `agents/tools.py` | 8 grounded tools (§3.8) | Keep; add a coaching-evidence tool later |

---

## 3. Everything the system computes today → amateur translation

Conventions: **Home** = where the amateur sees it (file 00 route/component names). **Label** per file 00 §7: A = Available, P = Preview, N = Not yet.

### 3.1 `PlayerStats` (per player; `analytics/match.py`)

| Field | Computed from | Amateur translation | Home | Depth · Preset | Label | Note |
|---|---|---|---|---|---|---|
| `points_won`, `points_lost`, `win_rate` | `RallyRecord.winner/loser` of official rallies | "Points" shown as the **scoreline in a context chip**, never as win-rate | `RecapHeader` chip; Deep dive → Story | Scoreline Quick+; win-rate Advanced/Compete | P until winners Checked | `win_rate` suppressed below ~10 scored rallies (file 06) |
| `winners` | rally outcome `winner` (landed in) | "Rallies that ended with the shuttle landing in" — **drop the word *winner*** | Deep dive → Story | Advanced | P | Equates "opponent failed to return" with a skill act |
| `errors_out`, `errors_net` | outcome `out`/`net` against the loser | "Shuttle went out / into the net" as a *neutral rally ending*, not "your errors" | Deep dive → Rallies (rally end reason) | Advanced | P | "Errors" is a judgment; copy rule file 09 |
| `strokes{}` (counter by type) | `stroke` events | **Shots spotted** (set, not count) → `ShotRepertoireGrid`; shares in `ShotMix` | Progress → Shots; Deep dive → Shots | Guided+ | P | Never "confirmed" (finding 5) |
| `smashes`, `jump_smashes` | stroke `smash` / `subtype: jump_smash` | "Smashes spotted" in repertoire; jump-smash only as a Moment lens | Moments lens | Guided+ | P | Smash assessment `assess_smash` uses speed/above-head/jump features |
| `smash_points` | last shot of winner's rally is smash | Deep dive only ("Rallies ended with your smash") | Story | Advanced | P | |
| `serves`, `serve_points_won` | first shot `is_serve` | Serve metrics → Advanced; `m.serve_*` | Deep dive → Shots | Advanced | P | Serve ownership relies on BWF server state |
| `distance_m` | sum of per-sample path (no smoothing) | **Not shown** | — | — | **N** | Inflated by jitter (finding 7, G-09) |
| `points_won_under_pressure` | `flags_before.game_point/deuce` | Not shown to amateurs | Deep dive → Story (Compete) | Advanced | P | "Pressure" is read from the score; meaningless without a verified score |

### 3.2 Match-level numbers (`MatchAnalytics.to_public()`)

| Field | Meaning | Amateur translation | Home | Label |
|---|---|---|---|---|
| `rallies` | official rally count | "N rallies" | `FactTrio`, `MatchCard` | A |
| `unofficial_rallies`, `unofficial_play_s` | warm-up/replay, not scored | "N not counted — warm-up" (reinstatable) | `ReviewBanner` | A |
| `active_play_s` | Σ official `duration_s` ("shuttle in play") | "Shuttle in play for 14 min" — **not** "time exercising" | Recap fact | A |
| `avg_rally_shots`, `longest_rally_shots` | mean/max `len(shots)` | "Your longest rally: 14 shots" | `HeroMoment`, `FactTrio` | A (count of *detected contacts*, see file 06 for the denominators) |
| `momentum[]` (last 60) + `momentum_shifts[]` | EWMA α = 0.3 of ±1 per point; shift when sign flips and prior \|v\| > 0.25 | Hidden in Quick/Guided | Deep dive → Story | P, Advanced |
| `score_timeline[]` | per-point `{rally_no, game_no, score, winner, frame, rally_id}` | Scoreline strip with each point openable | `ScoreStory` | P until Checked |

### 3.3 Highlight categories (`ontology.yaml: highlight_categories`) → Moment lenses

| Engine category | Rule in `score_rally` | Amateur lens (file 06 §7) | Problem to fix |
|---|---|---|---|
| `longest_rally` | needs `n_shots ≥ max(12, longest)` **and** `== longest` | **Longest** | Threshold 12 suits pros; many amateur rallies are 5–9 shots, so the tag never fires |
| `smash_winner` | last shot smash by rally winner (+1.5) | folded into **Best variety**/optional "Smash" | Rewards only winners |
| `jump_smash` | any `jump_smash` in rally (+1.2) | **Fun/Wow** (opt-in) | Preview-labelled |
| `best_defence` | winner made ≥ 4 `lift`/`defence`-family shots (+ up to 1.5) | **Saved it** (defence) | Credits only the *winner*; the player who defended well and lost gets nothing |
| `net_battle` | ≥ 4 `net`-family shots in the rally (+ up to 1.2) | **Net duel** | Fine, but both players share it |
| `comeback` | winner trailed ≥ 5 in the game then levelled/led | **Comeback** (scored matches only) | Needs a verified score |
| `momentum_shift` | EWMA sign flip | Advanced only | Meaningless for amateurs |
| `deuce`, `game_point`, `match_point`, `clutch` | `flags_before` | **Close finish** (scored matches only) | Needs a verified score; fabricated if the BWF fold started at 0–0 on a mid-game clip |

`reasons` keys (`length`, `variety`, `smash_winner`, `jump_smash`, `defence`, `net_play`, `pressure`, `deuce`, `momentum`, `comeback`) are summed and capped at **10** — a **numeric 0–10 score shown in the UI** (`HighlightsTab`). Verdict: the decomposition is useful (explainability, D16) but the number must not be shown (false precision, D5).

### 3.4 Heatmaps (`HeatmapSet`, 0.25 m cells, doubles court + 1 m margin; normalised to the busiest cell)

| Kind | What it really contains | Amateur translation | Label | Home |
|---|---|---|---|---|
| `presence` | foot positions during official rallies, subsampled ≈ 5 Hz | "Where you stood" | P (needs `court_q` gating, G-09) | Recap "My game" (one map), Deep dive → Court |
| `movement` | path-length-weighted presence | Merge into `presence` | — (ADVANCED) | Deep dive only |
| `origin` | feet at each contact (`hitter_court_xy`) | "Where you hit from" | P | Deep dive → Court |
| `landing` | **receiver's feet at their contact** (`engine.py:648-650`) | "Where your opponent met the shuttle" (honest name) until G-10 | P | Deep dive → Court |
| `targeting` | **same point as `landing`** (`match.py:131-136`) | **DROP** (duplicate) | — | — |

Retraction gap: `on_stroke_retracted` decrements `strokes`/`smashes`/`serves` but **does not remove** the stroke's contribution to `origin`/`landing`/`targeting` grids; a corrected/retracted shot stays on the heatmap until a rebuild (G-16).

### 3.5 Event vocabulary available as evidence (`ontology.yaml`)

`contact, stroke, serve, rally_start, rally_end, point, game_end, match_end, interval, side_switch, camera_cut, replay_start/end, highlight, insight, degraded, calibration, scene, match_phase`. Statuses `provisional | confirmed | corrected | retracted | human_verified`; bands `confirmed ≥ 0.85`, `probable ≥ 0.60`, else `uncertain`. Event payloads used by the UI: `rally_end.payload` = `{rally_no, winner, loser, outcome, shots[], duration_s, n_shots, official, phase_reason, winner_source ("ocr"…), end_reason}`; `stroke.payload` = `{stroke, subtype, label, probs, is_serve, hitter_court_xy, landing_court_xy, receiver_id, flight_time_s, p_smash, p_jump}`.

### 3.6 Reports and exports

| Artifact | Contents today | Amateur translation | Home |
|---|---|---|---|
| `report.pdf` (ReportLab) | Title; "P1 vs P2 · N rallies"; **players table** (10 rows incl. distance); **highlights table** (#, rally, **score**, why); **full rally table** (rally, game, time, winner, outcome, shots, score); footer "Labels marked probable or uncertain… are model estimates" | → **Analyst report** under Advanced. New default: **Match story** PDF/card (file 06 §8) | `ExportList` |
| `rallies.csv` | `match_id, game_id, rally_id, frame_start/end, start_time/end_time, duration_s, winner, loser, outcome, shots (space-joined strokes), n_shots, score_P1, score_P2, rally_event_id` (official only) | ADVANCED export | `ExportList` |
| `legacy.csv` | 8 columns for `legacy/streamlit`; rows without a winner skipped | **DROP** from the player UI | — |
| `events.jsonl` | Live event view, one JSON per line ("source of truth") | ADVANCED / data portability (G-05 export request) | Settings → Data |
| `summary.json` | session + analytics (+ more) | ADVANCED | Settings → Data |
| `clip.mp4` | Frame-exact cut, 1 s pad (≤ 10), libx264 CRF 20 + AAC audio, cached by range | **Moment share file** — needs consent gate, optional audio strip, optional story card (G-05, G-06) | `ClipPlayer`, `SharePreviewDialog` |

### 3.7 Calibration, scene, coverage (all present, none user-facing as coverage)

`calibration` event: `mode (lines|camera|static)`, `method`, `validity`, `quality{precision, support, lines, area, rms_px}`, `camera{focal_px, centre_m}`, `coverage`, `reprojection_error_px`. `scene` events: `view main|alt|none`, `analysed`, `court_quality`. **Translate** into one `CoverageBar` ("We followed X of Y rallies / court found on N % of the video") — no coverage number is shown to a user today other than `Banners`.

### 3.8 Ask agent tools (`agents/tools.py`)

| Tool | Returns | Amateur use | Note |
|---|---|---|---|
| `match_overview` | players, status, official/unofficial rally counts, score state, phase, observation window, `score_basis`, games, data quality (`degraded`, `calibrated`) | First call; feeds "What we could see" | Includes `score_basis` — reuse verbatim in coverage copy |
| `list_rallies` | filter by winner/outcome/min_shots/game | "Show my long rallies" | `winner` filter exists; add a *participant* filter (fair to losers) |
| `get_rally` | shots with `band`, outcome, `winner_source`, score before/after, pressure flags | Moment narration | |
| `player_stats` | `PlayerStats.to_public()` + `rally_ids_won`, `smash_event_ids` | Keep behind Advanced intents | Win-centric |
| `find_strokes` | strokes by player/type/subtype with band | "Show my drop shots" | Preview |
| `top_highlights` | `Highlight.to_public()` + time + player | Replaced by `top_moments` (lenses) | |
| `momentum` | shifts + recent | Advanced only | |
| `rules_and_background` | KB passages (rules, terminology, **player biographies**) | Rules explainer ("what is a let?") | Background only; never match facts |

Behaviour already right: strict JSON tools, every number must appear in a tool result, `[[ev:ID]]` citations validated, abstention allowed, JSON-text tool calls repaired (DEF-13).

---

## 4. Gap table — what the three Design documents require vs the code

**Severity:** **B** = blocks a stated principle or ships a false claim · **H** = required for the core loop · **M** = required for a later layer · **L** = polish.
**Sources:** FE = Front-End Blueprint · V2 = Amateur Blueprint v2 · V1 = Complete Spec v1.

| ID | Requirement (source) | What exists | Gap | Sev | Needed by |
|---|---|---|---|---|---|
| **G-01** | Player accounts, display name/nickname, play mode, "which one is you?" (V1 §3 steps 3–5; D8) | Single local principal; `PlayerInfo{player_id, name, color}`; free-text "Player 1/2" | No user entity, no profile, no mapping of track → person; `shortName` takes last word | **B** | Onboarding, every "you" metric |
| **G-02** | Cross-match history: progress, personal records, journey, first-seen shots, comparable baselines (FE §7.11, V2 §5.2, V1 §5E) | `MatchAnalytics` is rebuilt per session; no cross-session store | No history store, no `comparable` rule engine, no records ledger | **H** | Progress, Records, My story |
| **G-03** | Doubles: pair vs individual metrics, partner roles, 4 tracks (V2 §5.5, V1 §5F) | `PlayerId = "P1"\|"P2"` in rules, identity, contact alternation, engine buffers, API, ~20 web files (ROADMAP #9); `PlayerInfo.player_id` allows `"P1a"` in schema comment only | Not generalised anywhere | **H** (later layer) | Together, Pair memory |
| **G-04** | Unscored social games and practice (D12; V1 §7 Session types) | `bwf.py` fold always scores; unscored exchanges only exist as `official:false` warm-up | No *free-play* match type; BWF fold would invent a score and pressure flags | **B** | Social game/Practice types |
| **G-05** | Consent ledger; analyse ≠ store ≠ share ≠ train; retention; export/deletion jobs; signed expiring links (V1 §7.8, FE §13.2–13.3, V2 §9) | Delete removes analysis but keeps cached media; clip export unrestricted; HLS/sprite/proxy served to any authenticated user | No consent model, no share links, no deletion/export job status, no retention policy | **B** | Upload step, Share, Settings |
| **G-06** | Clip entity: save/favourite, per-clip visibility/approval, funny-clip opt-in, nicknames in clips (V1 §3.14, V2 §5.1) | `highlight` events only; `clip.mp4` is generated ad hoc | No clip table, no favourites, no approval state, no audience | **H** | Moments, Share |
| **G-07** | Metric registry: id, definition, unit, numerator/denominator, n, coverage, status, comparison eligibility, evidence refs (V2 §8.4, V1 doc 05, ROADMAP #14) | `PlayerStats.to_public()` returns bare numbers; two folds can disagree | No registry, no `MetricValue`, no denominators | **H** | InsightCard, MetricPopover |
| **G-08** | Calibrated confidence; no raw softmax shown (V2 §8.5, FE §8.3) | Band = threshold on raw `confidence`; `outcome_confidence` 0.85 for HIGH while winner accuracy measured 61.5 % | No calibration on target footage | **B** | `CheckChip` meaning |
| **G-09** | Geometry gates: metric analytics only from validated frames; publish coverage (ROADMAP P0 #7) | `presence`/distance/origin use whatever `court_x/y` exist; `court_q`/`scene` not applied | Ungated distance/heatmaps; no coverage number | **B** | Court map, "Where you stood" |
| **G-10** | True landing point from trajectory (ROADMAP #12; FE §7.10) | `landing_court_xy` = receiver's feet; `targeting` duplicates it | No shuttle floor-landing estimate | **H** (for placement) | Placement metrics |
| **G-11** | Amateur-footage validation set (FE §15, V2 §14) | One 8-min broadcast match (`Test1_Full_rev.csv`); synthetic generators | No labelled phone/club footage, no per-condition accuracy | **B** | Readiness labels (file 00 §7) |
| **G-12** | Honest processing stages, resumable upload, leave-safely, partial results (FE §7.5, V1 doc 03 §10) | WS `status{status, frontier_frame, rate_x, degraded[]}`, `ingest.progress`, `analysed_frames`; upload is one POST | No named stage list, no per-module result counts, no resumable transfer, no retry-per-stage | **H** | `ProcessingStages` |
| **G-13** | Notifications: analysis ready, user-set reminders, opt-in only (FE §11.3, V2 §3.7) | None | No notification service or preferences | **M** | Settings, Home |

### Gaps added by this audit (G-14 onward)

| ID | Gap | Evidence | Sev |
|---|---|---|---|
| **G-14** | **Correction undo + change summary.** FE §8.11 requires a banner showing *which summaries changed* with undo; `/corrections` returns only `{"status":"accepted"}` | `routes/sessions.py:correct` | **H** |
| **G-15** | **Corrections limited to winner/official/match_start/verify.** No correction for *who is me* (track→person), shot type, rally boundary or score override | `Correction` model kinds | **H** |
| **G-16** | **Heatmaps not retractable.** `on_stroke_retracted` does not undo `origin/landing/targeting` cells; `on_presence` has no corresponding undo | `match.py:138-151` | M |
| **G-17** | **Duplicate/misleading heatmap kinds.** `targeting` ≡ `landing` in content; `landing` mislabelled (feet, not landing) | `match.py:131-136`, `engine.py:648-650` | **H** |
| **G-18** | **Highlight ranker excludes the loser and is pro-calibrated.** `highlights(player=…)` filters by winner; `longest_rally` needs ≥ 12 shots; pressure/deuce/comeback need verified score | `match.py:score_rally, highlights` | **B** (D17) |
| **G-19** | **No per-claim evidence model.** `Highlight.reasons` and `Evidence[]` exist, but analytics numbers carry no `evidence_ids` (the class docstring promises "every number carries the event ids"; `to_public()` does not) | `match.py` docstring vs `to_public` | **H** |
| **G-20** | **Session-level coverage not computed.** "We followed X of Y rallies / court found on N % of frames" has inputs (`scene`, `calibration.coverage`, `rallies_without_winner` in `match_overview`) but no single API | `tools.py:match_overview`, calibration payload | **H** |
| **G-21** | **Analytics `momentum` truncated to 60 points** in `to_public()` (UI says "last points") while `score_timeline` is full — inconsistent windows | `match.py:to_public` | L |
| **G-22** | **Developer-facing error strings reach the UI.** `ErrorNote` prints API `detail`; copy references `.env`, `bai serve`, "server log" | `ui.tsx`, `LoginPage`, `AppShell`, `SessionPage.Banners`, `YouTubeCard`, `AskTab` | M |
| **G-23** | **Name handling.** `shortName` = last whitespace token; names capped at 80 chars; no nickname/privacy label separate from legal name | `format.ts`, `SessionPatch` | M |
| **G-24** | **Stroke taxonomy lacks plain-language grouping** (family exists: serve/attack/lift/flat/net/defence) but UI shows 12 raw names; `rush` = "Net kill" confusing for beginners | `ontology.yaml` | L |
| **G-25** | **No `me`-relative aggregation in the engine.** All stats are per `P1`/`P2`; "you vs your usual" and "your rally with your partner" need a participant-centric view | `MatchAnalytics.players` | **H** |
| **G-26** | **Active-play, rally-count and rally-length denominators are not defined for unscored/practice clips** (what counts as a rally in a drill?) | `rally_fsm` + `match_phase` assumptions | M |
| **G-27** | **Rally "shots" counts detected contacts, which include misses/unknown strokes**; copy "14-shot rally" can overstate if contacts are false positives (F1 0.941 on synthetic, unmeasured on amateur video) | `contact` fusion; `RallyRecord.n_shots = len(shots)` | M |
| **G-28** | **Audio in exported clips** (AAC retained) — bystander speech can be shared | `exports.py:clip` | M |

---

## 5. Where today's UI would **violate** the design principles (concrete)

| # | Today | Violates | Fix lives in |
|---|---|---|---|
| V-1 | First screen = upload + YouTube import + empty grid | D9 (value before configuration) | 03, 05a |
| V-2 | Win/loss colour (blue vs orange bars) on the main Stats table | D6, D8 | 05b, 08 |
| V-3 | Highlight score `0.0–10.0` printed large | D5, D16 | 06 §7 |
| V-4 | "Winner unclear" chips with band wording `probable/uncertain` | D5 | 07 `CheckChip` |
| V-5 | Distance in metres in Stats and PDF | D10 | 06 |
| V-6 | "What should P1 change in the next game?" suggestion chip | D2, D8 (prescriptive, uncited, win-centric) | 06 §9 |
| V-7 | `StrokeToast` "probable" shot labels on live video | D5, D10 | 05b |
| V-8 | `waitForAnalysis` default on → playback pauses with "Analysis is catching up" | D9 | 05a |
| V-9 | Delete dialog says media stays cached | D15 | 05c, 10 |
| V-10 | Keyboard-only affordances (`?`) are the sole route to frame stepping/rally nav; no touch equivalents | D14 | 07 |
| V-11 | Hover-only delete button on cards | D14, a11y | 07 |
| V-12 | Header "× real time" and `frame 12,043` in the control bar | D18 | 07 |

---

## 6. Risk list — UI claims the engine cannot support yet

| # | A UI element that would imply… | Why the engine cannot back it today | Mitigation (label) |
|---|---|---|---|
| R-1 | "You won / lost" as a headline | Rally-winner accuracy 61.5 % (8/13) on the only real-video check, before OCR; amateur video has no scoreboard | Scoreline shown only after **Checked** or labelled Preview (D5, D11) |
| R-2 | Shot names ("you hit 11 smashes") | Rule classifier `MAX_CONF 0.7`; learned model is a placeholder | Preview; "spotted"; never counts in headlines |
| R-3 | "Where your shots land" | `landing_court_xy` is the receiver's feet | Rename or hide until G-10 |
| R-4 | "You covered 1.2 km" | Ungated, unsmoothed distance | **Not yet** (N) |
| R-5 | Doubles anything | `PlayerId` is `P1/P2` | **Not yet** |
| R-6 | "Personal best / first / improved" | No cross-match store; no comparable-session rule | Demo fixtures only; Preview (G-02) |
| R-7 | "Longest rally" | Needs ≥ 12 shots today; shot counts are detected contacts | Re-define (file 06); disclose denominator |
| R-8 | "Clutch / pressure / comeback / deuce" | Depend on a verified BWF score; fabricated when the fold starts at 0–0 | Hide for unscored/unverified (G-04) |
| R-9 | "Best defence" for the player who lost | Defence credit goes to the rally *winner* only | New lens (file 06 §7) |
| R-10 | "Checked ✓" | `human_verified` exists only for events a person confirmed; bulk "verify" not offered | Only show when status is `human_verified`/`corrected` |
| R-11 | "We found your court" on a phone clip | Court-line fit is tuned on broadcast; amateur geometry (behind baseline, high, side-on) untested; auto-calibration samples 24 frames and picks the most-seen camera | `SuitabilityResult` (Suitable / Usable with limits / Not supported) + manual fallback (G-11) |
| R-12 | A progress bar for "analysing" | `analysed_frames / n_frames` is real; `ingest.progress` real; but after-analysis stages (highlights, narration) have no progress | Named stages only; no fabricated % (FE §7.5) |
| R-13 | "Live" feel | Non-causal look-ahead ~40 frames (validation report: True-Live 2.5/5) | Post-session recap, not live |
| R-14 | Ask "knows" coaching | Agent has no coaching-evidence tool; local 8B model had citation hallucinations (DEF-05, mitigated) | Descriptive answers only; refuse prescriptive advice (file 06 §9) |
| R-15 | Warm-up detection on casual courts | Official/unofficial decision depends on serve formation + calibrated court + both players' feet; casual rallies often start from non-legal positions | Reviewer marker UX (D11); treat all as "Social game" by default (D12) |

---

## 7. What to reuse in the production prototype (summary)

**Reuse as is (≈ 70 % of the code that matters):**
- Evidence plumbing: event store contract, `EventLog` client fold, `supersedes`/retraction, `/corrections`, `?f=` deep links, WebSocket resume (`last_seq`), `TrackBuffer`, `frameClock` + rVFC overlay clock, HLS EVENT playlist player, sprite thumbnails.
- Deterministic analytics fold (`MatchAnalytics`/`rebuild`) — extend, do not replace; make every number carry `evidence_ids` (G-19).
- Grounded Ask agent and its validator.
- `CourtView`/`CourtMinimap`/`HeatCanvas` court rendering, `lib/court.ts` geometry (singles 5.18 m, doubles 6.1 m).
- Accessibility primitives: `role="slider"` timeline with `aria-valuetext`, `aria-label` on icon buttons, `prefers-reduced-motion`, `:focus-visible`, tabular numerals, Radix Dialog/Popover/Tabs/Tooltip, keyboard shortcuts.
- Auth hygiene: CSRF double-submit, throttle, HttpOnly SameSite=Strict cookie (carry into real accounts).
- UI primitives (`Button`, `IconButton`, `Field`, `Meter`, `Empty`, `Spinner`, `Kbd`) and the "Arena Night" tokens as the dark theme.

**Reshape (same engine, new surface):** Library → Matches + New match; Session → Recap + Deep dive; Calibrate → Place your court; Highlights → Moments; Rallies → Review & fix; Stats → Deep dive → Story; Ask → Coach chat; Export → Match story + analyst exports; `BandChip` → `CheckChip`; `SessionCard` → `MatchCard`; `ScoreBug`/`StrokeToast` → optional overlays.

**Retire from the player product:** `SystemPage` (to `/admin`), passphrase `LoginPage`, `legacy.csv` export, `targeting` heatmap, numeric highlight score, `distance_m`, `.env`/`bai serve` strings.

**Build new (no precedent in code):** Landing + sample recap, Home, onboarding (`PurposePicker`, `PresetCards`, `RecordGuide`, `SuitabilityResult`, `PickYourself`, `ConsentCards`), `HeroMoment`/`FactTrio`, `InsightCard`, `ReviewBanner`/`ChangeSummaryBanner`, Progress/Records/Shots/My story, Explore, Together, Share dialog + `/s/$token`, Settings & Privacy Centre, notification preferences.

---

## 8. Quick wins available without backend work

1. Rename and re-order surfaces (Matches/Recap/Deep dive) behind a feature flag; keep every existing component.
2. Replace `BandChip` words with Checked / Looks right / Worth a look and add the Preview tag.
3. Default overlay layers and `waitForAnalysis` by Depth.
4. Hide `distance_m`, `targeting`, numeric highlight score, `legacy.csv`.
5. Build the **fixture-driven** Home, Progress, Records, My story, Explore, Together screens with `DemoBanner` — they need no engine change and let research start.
6. Move `SystemPage` under `/admin/system`.
7. Add a friendly-error mapper over `ApiError`.

---

## 9. Gaps added (for merge into file 11)

`G-14` correction undo + change summary · `G-15` extra correction kinds (me/track, shot type, rally boundary, score override) · `G-16` heatmaps not retractable · `G-17` duplicate/mislabelled `landing`/`targeting` · `G-18` highlight ranker excludes the loser, pro-calibrated thresholds · `G-19` analytics numbers carry no `evidence_ids` · `G-20` no session-level coverage API · `G-21` momentum truncated to 60 points · `G-22` developer-facing error strings in UI · `G-23` name handling (`shortName`, nickname vs legal name) · `G-24` stroke taxonomy needs plain-language grouping · `G-25` no participant-centric ("me") aggregation · `G-26` undefined rally/active-play semantics for unscored clips · `G-27` shot counts are detected contacts (false-positive exposure) · `G-28` audio retained in exported clips.
