# 11 — Data Contracts and Backend Gaps

**Purpose.** Tell the frontend what it can call **today**, tell the backend what it must build for the amateur product, and fix the **shape** of every payload so the UI can be built against fixtures now and the real API later without rewrites.

**Rule of the whole file.** The UI never branches on "demo vs real". A `DataSource` interface has two implementations — `ApiDataSource` and `FixtureDataSource` — returning the *same* DTOs. A payload carries `meta.demo: true` when it is sample data, and the single `DemoBanner` reads that flag. (v1 doc 06 §2.)

---

## 1. Layering: engine API underneath, product API on top

```
 apps/web  ──►  Product API (BFF)   /api/matches · /api/me · /api/moments · /api/s/…       ← NEW
                    │  composes, ranks, applies consent + claims policy, never invents facts
                    ▼
               Engine API           /api/sessions/{id}/…  events · analytics · heatmap …   ← EXISTS
                    │
                    ▼
               Engine store         events.sqlite (append-only) · Parquet tracks · media    ← EXISTS
```

- **Engine API stays stable.** It is deterministic and evidence-linked; it keeps speaking `session`, `P1/P2`, `band`, `status`.
- **Product API (BFF)** is a thin FastAPI router set inside `apps/api` that speaks *match, moment, you, check-state*. It performs **ranking, fairness, comparability, consent filtering and claim gating** — all deterministic. The LLM never sits in this layer; it only narrates an evidence packet (file 06 §8).
- A `match` **is** a `session` (1:1 id). The product API adds fields; it does not fork storage.

---

## 2. What the UI can use **today** (existing endpoints → new surfaces)

| Need in the amateur UI | Existing endpoint / source | Gap |
|---|---|---|
| Matches list | `GET /api/sessions` (+ polling while busy) | Match type, coverage, hero-moment thumbnail, recap-ready flag → product API |
| Create from file | `POST /api/sessions` (multipart; **starts analysis immediately**) | Needs a **draft** state and consent gate (G-12, G-05) |
| Import from link | `POST /api/sessions/youtube` (with `acknowledge_rights`) | Keep behind *Advanced/Import*; not for amateurs' main path |
| Rename / name players | `PATCH /api/sessions/{id}` (`title`, `player1`, `player2`) | Needs **"which one is me"** mapping (G-01) |
| Progress while analysing | WebSocket `StatusMsg` (`frontier_frame`, `rate_x`, `degraded[]`) + `Session.status` | Stage names/ETA contract (G-12) |
| Playback | `GET …/hls/index.m3u8`, `…/proxy.mp4`, `…/sprite/{name}` | — |
| All events | `GET …/events` (`last_seq`) | — |
| Match numbers | `GET …/analytics` (`Analytics`, `PlayerStats`) | Denominators, units, `n`, coverage per metric (G-07) |
| Heatmaps | `GET …/heatmap?player&kind` (`presence, movement, origin, landing, targeting`) | Geometry gates + coverage (G-09, G-10) |
| Highlights | `GET …/highlights?k&player` | Fairness; `player` currently filters by rally **winner** (file 06 §7) |
| Court | `GET …/calibration/proposal`, `POST …/calibration`, `POST …/calibration/auto` | Product wrapper that explains quality (G-09) |
| Corrections | `POST …/corrections` (`winner`, `official`, `match_start`, `verify`) | Response must return a **ChangeSummary** (what moved) |
| Ask | `POST …/ask`, `GET …/ask/provider` | — (already grounded; keep citation validator) |
| Exports | `…/exports/report.pdf · rallies.csv · legacy.csv · events.jsonl · summary.json · clip.mp4?from&to` | Amateur Match Story card/PDF (file 06 §6) |
| Auth | `GET /api/auth/me`, `POST /api/auth/login` (shared passphrase), CSRF header | Real accounts / guest-first (G-01) |
| System | `GET /api/system`, `/api/models`, `/api/profiles`, `/metrics` | Moves to `/admin/system` |

---

## 3. Core DTOs (TypeScript, the contract between product API and UI)

All DTOs carry `schema_version`, `generated_at` and `meta` (`demo`, `model_versions`, `definition_versions`).

```ts
// ---------- trust primitives ----------
type CheckState =            // D5. Derived server-side; the UI never maps engine bands itself.
  | "checked"                // EventStatus human_verified | corrected, or claim built only from such events
  | "looks_right"            // Band confirmed  (UI shows a Preview tag until bands are calibrated, G-08)
  | "worth_a_look"           // Band probable
  | "not_enough_to_say";     // Band uncertain|unknown, or sample below minimum → not shown in recap

type Readiness = "available" | "preview" | "not_yet";            // file 00 D10 / §7

interface EvidenceRef {                                           // one tap: "Watch this"
  event_id: string;
  match_id: string;
  frame_start: number; frame_end: number;                         // engine frames are canonical
  lead_in_s: number;                                              // seek slightly before
  label: string;                                                  // "Rally 14 · 11 shots"
}

interface Coverage {                                              // "What we could see"
  analysed_rallies: number; total_rallies: number;                // 31 of 36
  analysed_s: number; total_s: number;
  court_quality: number | null;                                   // calibration.quality.precision (0..1) — not shown as %
  scene_note: string | null;                                      // "Other camera not followed for 2 min"
  degraded: { stage: string; reason: string }[];                  // from StatusMsg.degraded
}

interface MetricValue {                                           // file 06 registry entry instance
  metric_id: string;                                              // "m.longest_rally"
  definition_version: number;
  value: number | string | null;                                  // null = not measured (never 0)
  unit: "shots" | "s" | "count" | "ratio" | "m" | "zone";
  numerator?: number; denominator?: number;                       // for rates; UI renders "6 of 9"
  n: number;                                                      // eligible observations
  readiness: Readiness;
  check: CheckState;
  coverage: Coverage;
  evidence: EvidenceRef[];                                        // may be empty only for pure descriptives
  limitations: string[];                                          // plain language
  comparison?: { baseline: "self_comparable" | "previous_match" | "none";
                 baseline_value: number | null; baseline_n: number; comparable: boolean;
                 reason_not_comparable?: string };
}

// ---------- the amateur product objects ----------
interface Moment {                                                // a "highlight/clip" the player can keep
  moment_id: string; match_id: string; rally_event_id: string;
  frame_start: number; frame_end: number;
  lens: "longest" | "saved_it" | "net_duel" | "variety" | "close_finish"
      | "first" | "personal_best" | "fun" | "partner";
  title: string;                                                  // "Saved it: 6 defensive returns"
  why_chosen: string;                                             // plain-language, evidence-bound
  players: { player_ref: PlayerRef; role: "you" | "partner" | "opponent" | "other" }[];
  check: CheckState; readiness: Readiness;
  visibility: "private" | "named_people" | "link";                // D15
  approved_to_share: boolean;                                     // funny/blooper clips: default false
  favourite: boolean;
  thumb_url: string; clip_url: string | null;                     // clip rendered on demand
  evidence: EvidenceRef[];
}

interface Recap {                                                 // GET /api/matches/{id}/recap
  match: MatchSummary;
  state: "processing" | "partial" | "ready" | "low_coverage" | "failed";
  hero: Moment | null;                                            // null → honest "why not" below
  hero_absent_reason?: string;
  facts: MetricValue[];                                           // ≤ 3 (FactTrio)
  positive_per_player: { player_ref: PlayerRef; moment: Moment | null; why_not?: string }[]; // D17
  story: { text: string; claims: Claim[] };                       // grounded narration
  moments: Moment[];                                              // 3–5, lens-diverse
  my_game: Insight[];                                             // Guided+ only
  together: Insight[];                                            // doubles: Not yet
  scoreline: { shown: boolean; per_game: [number, number][]; check: CheckState; note: string | null };
  review: { open_items: number; top_item_event_id: string | null };
  coverage: Coverage;
  preview_flags: string[];                                        // which surfaces carry a Preview tag
}

interface Insight {                                               // file 06 §5, Blueprint §8.1
  insight_id: string;
  claim: string; claim_type: "descriptive" | "comparison" | "hypothesis" | "recommendation";
  metric_ids: string[]; evidence: EvidenceRef[];
  n: number; denominator?: number; coverage: Coverage;
  check: CheckState; readiness: Readiness;
  alternatives: string[];                                         // other explanations, plain words
  next_action?: { kind: "watch" | "try_focus" | "ask_coach" | "save" | "ignore"; label: string };
  comparison_context?: string;                                    // "vs. your last 3 comparable matches"
  user_response?: "confirm" | "correct" | "dismiss" | "save";
  model_versions: Record<string, string>;
}

interface ChangeSummary {                                         // returned by POST /corrections
  applied: boolean;
  changed: { kind: "scoreline" | "moment" | "metric" | "insight" | "record"; id: string; before: string; after: string }[];
  rescored_from_rally_no: number | null;
  undo_token: string | null;                                      // expires; undo = inverse correction
  explain: string;                                                // "Changing this re-scored 6 points after it."
}

interface PlayerRef { player_ref_id: string; track: "P1" | "P2"; nickname: string; is_you: boolean; }

interface CaptureCheck {                                          // POST /api/capture/test-clip
  verdict: "suitable" | "usable_with_limits" | "not_supported";
  findings: { code: "court_visible" | "court_partly_cut" | "players_found" | "camera_moves"
              | "too_dark" | "too_far" | "angle_extreme" | "cuts_detected";
              ok: boolean; message: string; fix: string | null }[];
  unlocks: string[];                                              // what works at this quality
  unavailable: string[];                                          // what won't, and why
  example_frame_url: string;
}

// ---------- me, consent, preferences ----------
interface Preferences {
  preset: "relax" | "explore" | "improve" | "compete";            // D3
  purposes: ("keep_moments" | "understand" | "practise" | "compete" | "discuss" | "just_play")[]; // ≤2
  depth: "quick" | "guided" | "advanced";
  tone: "direct" | "balanced" | "coach_guided";
  notifications: Record<"analysis_ready" | "coach_comment" | "reminder" | "trend", boolean> & { quiet_hours?: [string, string]; paused: boolean };
  accessibility: { reduce_motion: boolean; text_scale: number; high_contrast: boolean; low_bandwidth_preview: boolean };
}

interface ConsentRecord {                                         // D15: four permissions + a separate improvement opt-in
  consent_id: string; purpose: "analyse" | "keep_video" | "save_to_history" | "share" | "improve_models";
  scope: { match_id?: string; moment_id?: string; audience?: string[] };
  status: "granted" | "revoked" | "not_asked"; captured_at: string; policy_version: string; revoked_at: string | null;
}
```

### 3.1 Mapping engine values → UI states (the BFF owns this table)

| Engine | → | UI |
|---|---|---|
| `Band` `confirmed` | → | `looks_right` (+ Preview until calibrated) |
| `Band` `probable` | → | `worth_a_look` |
| `Band` `uncertain`/`unknown` | → | `not_enough_to_say` (not shown in recap; listed in Review) |
| `EventStatus` `human_verified`, `corrected` | → | `checked` |
| `EventStatus` `provisional` | → | excluded from recap; shown in Review queue as "needs a look" |
| `EventStatus` `retracted` | → | never shown |
| `Session.status` `created`/`ingesting` | → | `Uploading/Preparing` (separate from analysis) |
| `ready_to_play` | → | "Ready to watch — still finding rallies" (**play now**) |
| `analysing` + `frontier_frame/n_frames` | → | "Finding rallies" with real fraction; `rate_x` only in Advanced |
| `analysed` | → | `ready` (or `low_coverage` if Coverage thresholds fail) |
| `failed` + `status_detail` | → | `FailedState` with cause and what's kept |
| `StatusMsg.degraded[]` | → | `PartialAnalysisNote` |
| `scene.view != "main"` segments | → | Coverage.scene_note |
| `calibration.mode` `lines`/`camera`/`static` + `quality` | → | PlaceYourCourt status copy; Court surfaces gate |
| rally `official: false` | → | "Not counted — warm-up" (reinstatable) |

### 3.2 Mapping today's `PlayerStats` → metrics (full table in file 06)

`points_won/lost, win_rate, winners, errors_out/net` → **Advanced only** (D6). `strokes`, `smashes`, `jump_smashes` → **Preview**. `serves`, `serve_points_won` → Guided/Advanced, Preview. `points_won_under_pressure` → Advanced. `distance_m` → **Not yet** (G-09). `Analytics.longest_rally_shots`, `avg_rally_shots`, `rallies`, `active_play_s` → **Available** and drive the Quick `FactTrio`.

---

## 4. Product API surface (proposal)

`★` = new. Paths use `/api/…` like the existing app. All mutating calls require the existing CSRF header; all object access is **server-side authorised** (the frontend never enforces privacy).

### 4.1 Identity, preferences, consent

| Method + path | Purpose |
|---|---|
| `★ GET/PATCH /api/me/profile` | nickname, optional avatar, play mode(s) |
| `★ GET/PUT /api/me/preferences` | `Preferences` |
| `★ GET /api/me/consents`, `PUT /api/me/consents/{purpose}` | consent ledger; PUT changes status and returns what changes *now* |
| `★ POST /api/me/data-exports`, `POST /api/me/data-deletions`, `GET …/{id}` | request + status (deletion removes derived clips, tracks, embeddings, exports under platform control; honest limits on backups/downloaded copies) |
| `★ POST /api/auth/guest` | guest-first session; upgrade by email/phone later (G-01) |

### 4.2 Matches and capture

| Method + path | Purpose |
|---|---|
| `★ POST /api/capture/test-clip` | analyse a 5–10 s clip → `CaptureCheck` (court found? both players? camera moving? light?) — built from existing court-line fit + player detection |
| `★ GET /api/matches` | list with `type` (`match|social|practice`), coverage, recap-ready, hero thumbnail, `demo` flag |
| `★ POST /api/matches` | create **draft** (no auto-start): `type`, `discipline` (`singles` now; `doubles` Not yet), consent snapshot, source |
| `★ PUT /api/matches/{id}/upload` | **resumable** upload (tus-style/chunked); returns `Match` |
| `★ POST /api/matches/{id}/start` | begin analysis once consent + draft complete |
| `★ GET /api/matches/{id}` | `MatchSummary` + stage model (§5) |
| `★ GET /api/matches/{id}/players/candidates` | best frames with the `P1/P2` boxes (tap-to-pick) |
| `★ PUT /api/matches/{id}/players/me` | `{track:"P1"|"P2", nickname}` → creates `PlayerRef` link |
| `PATCH/DELETE /api/sessions/{id}` | existing; wrapped |
| existing calibration endpoints | wrapped by `★ GET /api/matches/{id}/court` returning *plain-language* status (auto/set/tracked, line match, what it unlocks) |

### 4.3 Recap, moments, review

| Method + path | Purpose |
|---|---|
| `★ GET /api/matches/{id}/recap?depth=&purposes=` | the `Recap` object. Deterministic composition; cached by `last_seq` (reuse `AnalyticsCache`) |
| `★ GET /api/matches/{id}/moments?lens=&player=` | lens-ranked Moments with fairness (file 06 §7) |
| `★ GET/PATCH /api/moments/{id}` | favourite, rename, visibility, `approved_to_share` |
| `★ POST /api/moments/{id}/clip` | render (wraps existing `clip.mp4`), returns URL when ready |
| `★ GET /api/matches/{id}/insights?depth=&purposes=` | ranked `Insight[]` with suppression |
| `★ GET /api/matches/{id}/review` | **Review queue**: items ordered by what the recap will show |
| `POST /api/sessions/{id}/corrections` | existing; **returns `ChangeSummary`** (★ response change) |
| `★ POST /api/corrections/{undo_token}/undo` | inverse correction |
| `★ GET /api/matches/{id}/metrics` | all `MetricValue`s for Deep dive (Advanced) |
| `★ GET /api/metrics/registry` | definitions/popover content (versioned) |

### 4.4 Progress, story, explore, together, sharing

| Method + path | Purpose |
|---|---|
| `★ GET /api/me/progress?metric=&since=` | comparable-match series with ranges and `n`; honest empty |
| `★ GET /api/me/records` | personal bests (`definition`, `source_moment`, `check`) |
| `★ GET /api/me/shots` | Shot Explorer (first spotted, most recent verified, observed≠mastered) |
| `★ GET /api/me/story` | `Milestone[]` (verified, player-confirmed) |
| `★ GET/POST/PATCH /api/me/focus` | one active Focus; status ladder Reviewed → Practised → Shown later |
| `★ GET /api/me/challenges`, `PATCH …/{id}` | optional; dismiss/pause |
| `★ GET /api/partners`, `POST /api/partners/invites`, `GET /api/partners/{id}/memories` | **Not yet** (needs doubles + consent) |
| `★ POST /api/moments/{id}/share-links` | preview + create (expiring, revocable); `GET /api/s/{token}` public read (consent-gated) |
| `★ DELETE /api/share-links/{id}` | revoke |

### 4.5 Feedback

`★ POST /api/feedback` — `{type: inaccurate_event|wrong_player|poor_highlight|confusing_metric|privacy_concern|other, ref, text?}`; returns a reference **only if** real review exists (v1 doc 04 §8: never promise a fix the backend can't keep).

---

## 5. Processing stage model

The UI shows **named stages with real progress or none** (no fabricated percentage).

```ts
type StageId = "upload" | "prepare_video" | "find_court" | "find_players" | "find_rallies" | "find_moments" | "summary";
interface StageStatus {
  id: StageId; label: string;
  status: "pending" | "running" | "partial" | "done" | "skipped" | "failed";
  fraction?: number;           // only when truly measured (upload bytes; frontier_frame / n_frames)
  started_at?: string; completed_at?: string;
  result_count?: number;       // "12 rallies found so far"
  retryable?: boolean; user_message?: string;   // safe text, never stack traces
}
```

Mapping from today's engine: `ingesting` ≙ `prepare_video`; `ready_to_play` ≙ playback available; court and player detection are emitted via `calibration`, `scene`, `degraded` events; rallies/moments grow with `frontier_frame`. **Progressive value is a feature:** video plays when `ready_to_play`; Moments appear as rallies finish.

---

## 6. Gap register (backend/engine work the design depends on)

Effort: S ≤ 3 days · M ≈ 1–2 weeks · L ≥ 3 weeks. Priority: **P0** blocks the amateur loop · P1 blocks a core screen · P2 later.

| ID | Gap | Why the UI needs it | Owner | Effort | Pri | **Prototype workaround** |
|---|---|---|---|---|---|---|
| **G-01** | **Player identity + accounts**: `PlayerRef`, "which track is me", nicknames, guest-first auth (today: shared passphrase; `P1/P2` are near/far tracks) | *Pick yourself*, "you" anchor (D8), history | API | M | **P0** | Local profile in browser storage; `players[].name` via PATCH |
| **G-02** | **Cross-match store**: per-user match history, comparable-match selection, records, journey, focus | Progress, Records, Story, Explore | API/engine | L | P1 | `FixtureDataSource`; later SQLite tables keyed by user |
| **G-03** | **Doubles / `PlayerId` generalisation** (ROADMAP #9: `Literal["P1","P2"]` in rules, identity, contact alternation, buffers, API, ~20 web files) | Together, Pair memory, doubles recap | engine+all | L | P2 (P1 if near-term) | Surfaces specced; labelled **Not yet** |
| **G-04** | **Free-play (unscored) match type** + `Social game`/`Practice` | Most amateur sessions are unscored; BWF fold would fabricate a score (D12) | engine | M | **P0** | Hide score surfaces when `type != match`; count rallies only |
| **G-05** | **Consent ledger, retention, share links, deletion/export jobs** | Consent cards, Privacy Centre, sharing | API | M–L | **P0 (consent)** / P1 | Client ledger with "simulated" labels in demo |
| **G-06** | **Moment entity**: saved/favourite/visibility/approved-to-share/per-clip consent | Moments, Clip detail, Share | API | M | P1 | Derive from highlights; store flags client-side in demo |
| **G-07** | **Metric registry** (id, unit, numerator/denominator, `n`, coverage, status, evidence ids; one fold, not two) — ROADMAP #14 | Every number the UI renders (D16) | engine | M | **P0** | Client `derive.ts` computes the few Quick facts with explicit `n` |
| **G-08** | **Calibrated confidence**: bands are raw model confidence (thresholds 0.85/0.60) | CheckState honesty (D5) | engine/ML | M | P1 | Show **Preview** on all `looks_right` claims |
| **G-09** | **Geometry gates on metric analytics** (ROADMAP P0 #7): only validated main-camera frames feed distance/heatmaps/zones; foot-jitter smoothing; coverage reported | Court surfaces, distance | engine | S–M | **P0** | Court surfaces Preview; distance **Not yet** |
| **G-10** | **True landing point from trajectory** (today `landing_court_xy` ≈ receiver's feet) | "Where your shots go" | engine | M | P2 | Preview with caveat copy |
| **G-11** | **Amateur-footage validation set** (phone, behind-baseline / side-on / high; no scoreboard) with ground truth for rallies, winners, contacts | Capability labels (D10), release gates | ML/QA | L | **P0** | Honest Preview labels; capture guide |
| **G-12** | **Stages API + draft state + resumable upload**: `POST` today auto-starts analysis; no draft/consent gate; upload is a single XHR | New match flow, honest processing | API | M | **P0** | Client gates consent before the POST; stage mapping from `StatusMsg` |
| **G-13** | **Notifications** (analysis-ready channel chosen at upload; coach comment; user-set reminder) | Opt-in notifications | API | M | P2 | In-app only |
| G-14… | **Appended by the audit (file 02) and the analytics catalogue (file 06) — see §8** | | | | | |

### 6.1 Minimum backend set for a **credible first amateur release** (P0)

G-01 (guest + identity link), G-04 (free play), G-05 (consent gate + share links), G-07 (metric registry for ≈12 Quick/Guided metrics), G-09 (geometry gates), G-11 (validation set + thresholds), G-12 (draft + stages + resumable upload). Everything else can ship as **Preview** or on fixtures.

---

## 7. Cross-cutting API principles

1. **Never `{ "value": 0.83 }` alone.** Every metric carries unit, `n`, denominator, coverage, check state, readiness, evidence (v1 doc 07 §4).
2. **Null means "not measured"** — never 0. The UI hatches it (file 08).
3. **Idempotent and versioned.** Deterministic event ids (ROADMAP #4/#5) so re-analysis does not duplicate moments or records; DTOs carry `definition_version` and `model_versions`; breaking metric definition changes are visible in trends as a version break.
4. **Corrections propagate and explain.** Every correction returns a `ChangeSummary`; derived Moments, records and insights recompute from the event log (the fold already supports this) and the UI shows *what changed*.
5. **Consent is enforced server-side**, per purpose and per clip; share pages never expose raw tracks or other people's data; media URLs are signed and expiring.
6. **Cache by scope.** Recap/metrics keyed by `(user, match, last_seq, depth, purposes)`; never serve one user's private clip/analytics from a shared cache.
7. **Fast path first.** `GET /recap` must be answerable from cache without touching Deep-dive aggregates; Deep dive loads lazily (v1 doc 07 §7).
8. **No internals in user messages.** Stack traces, model names and GPU data stay server-side or in `/admin/system`.
9. **Observability** (Blueprint §14.3 + v1 doc 07 §10): stage durations, partial/fail rates, correction rate, blocked-share attempts, recap latency, definition versions; no raw video or sensitive identifiers in logs.

---

## 8. Appendix: gaps added by the audit and the analytics catalogue

Merged from `02_CURRENT_STATE_AUDIT.md` (G-14 → G-28, with code locations there) and `03_ONBOARDING_AND_FIRST_RUN.md` §17 (G-ONB-1 → 9). Priority: **H** = blocks a core screen or breaks a trust rule · M · L · **B** = blocks fairness decision D17. Any gap named in a screen spec but missing here must be added before build planning.

### 8.1 From the audit (file 02)

| ID | Gap | Pri |
|---|---|---|
| **G-14** | Correction **undo + change summary**: `/corrections` returns only `{"status":"accepted"}`; the UI needs a `ChangeSummary` (§3) and `undo_token` | **H** |
| **G-15** | Corrections limited to `winner / official / match_start / verify`; none for *who is me*, shot type, rally boundary, score override | **H** |
| **G-16** | Heatmaps are **not retractable**: `on_stroke_retracted` does not undo `origin/landing/targeting` cells; presence has no undo | M |
| **G-17** | Duplicate/misleading heatmap kinds: `targeting` ≡ `landing`; `landing` is the receiver's feet (see G-10) | **H** |
| **G-18** | **Highlight ranker excludes the loser** (`highlights(player=…)` filters by rally winner) and is pro-calibrated (`longest_rally` needs ≥ 12 shots; pressure/deuce/comeback need a verified score) | **B** |
| **G-19** | Analytics numbers carry **no `evidence_ids`** (the class docstring promises it; `to_public()` doesn't deliver) | **H** |
| **G-20** | **Session coverage** ("we followed X of Y rallies / court found on N % of frames") has inputs but no single API | **H** |
| **G-21** | `momentum` truncated to 60 points in `to_public()` while `score_timeline` is full | L |
| **G-22** | Developer-facing strings reach the UI (`.env`, `bai serve`, "server log", raw API `detail`) | M |
| **G-23** | Name handling: `shortName` = last whitespace token; no nickname distinct from legal name | M |
| **G-24** | Stroke taxonomy needs a **plain-language grouping** for beginners (`rush` = "Net kill" confuses) | L |
| **G-25** | No **`me`-relative aggregation**: all stats are per `P1/P2`; "you vs your usual" needs a participant-centric view | **H** |
| **G-26** | Active-play, rally-count and rally-length denominators **undefined for unscored/practice clips** (extends G-04) | M |
| **G-27** | Rally "shots" counts **detected contacts**, including misses/unknown strokes — "14-shot rally" can overstate (contact F1 0.941 is synthetic; unmeasured on amateur video) | M |
| **G-28** | **Audio retained in exported clips** — bystander speech can be shared | M |

Two findings from the audit that matter for trust copy: (1) rule-based stroke confidence is capped at 0.7 (`MAX_CONF`), below the 0.85 `confirmed` threshold, so **no shot can ever read "Looks right"** until a person checks it — shot claims are *Worth a look* at best; (2) rally outcomes score 0.85 (the `confirmed` band) while measured winner accuracy was 61.5 % — the band is miscalibrated (G-08). The delete dialog also states the prepared video stays in the media cache after "Delete match" — contradicts D15 and must be fixed under G-05.

### 8.2 From onboarding (file 03)

| ID | Gap | Prototype workaround |
|---|---|---|
| **G-ONB-1** | Resumable / chunked upload (same work as G-12) | Retry restarts; copy says so |
| **G-ONB-2** | `POST /api/probe`: 10-second suitability probe (court fit + person detection on ~24 frames) — the engine of `CaptureCheck` (§3) | On-device metadata check + post-hoc "Usable with limits" |
| **G-ONB-3** | `GET /api/sessions/{id}/players/proposal` (frame + two boxes + sides) for *Pick yourself* | Derive from `/tracks` + sprite frame client-side |
| **G-ONB-4** | **Identity-segment correction** ("swap from here") for track ID flips | Mark affected rallies *Worth a look*; exclude from "you" metrics |
| **G-ONB-5** | Track whitelist when > 2 people are visible (bystanders) | Block with a clear message |
| **G-ONB-6** | Trim before upload / server-side trim | Warn; offer wait-for-Wi-Fi |
| **G-ONB-7** | Guest workspace (device-bound token, claim-on-signup, retention window) — same work as G-01 | Passphrase demo mode |
| **G-ONB-8** | Persisted consent ledger with `policy_version` (same work as G-05) | Local ledger labelled "Prototype" |
| **G-ONB-9** | Server-confirmed "processing continues after you leave" flag | Show "keep this tab open" |

### 8.3 From the screen specs (files 05a–c; their draft IDs were remapped to this register)

| ID | Gap | Pri | Prototype workaround |
|---|---|---|---|
| **G-29** | **Insight / recap service** (the BFF composer): ranked `Insight[]` and `Recap` with `claim_type`, evidence refs, suppression and "not enough to say" — deterministic; the LLM only narrates | **H** | Client-side composer over `analytics` + `highlights` + events, same DTOs |
| **G-30** | **Preferences + focus store** (preset, purposes, depth, tone, notification settings, one active Focus with status ladder) | M | Browser storage behind `DataSource` |
| **G-31** | **Moment thumbnails / poster frames** per rally (sprite sheets exist per session, not per Moment) | M | Cut from existing sprites client-side |
| **G-32** | **Feedback intake with reference IDs** — only promise "we'll look" if a real review queue exists | L | Local "simulated" receipt |

`HighlightsTab` currently shows the raw 0–10 `Highlight.score`; the 05a spec removes it below Advanced (D17). 05a also assumes a **sample-match fixture pack** — a frontend deliverable (file 12 §4), not a backend gap.

**Overlaps to collapse during planning:** G-ONB-1 = G-12; G-ONB-7 = G-01; G-ONB-8 = G-05; G-26 extends G-04; G-17 depends on G-10. **Minimum P0 set** (§6.1) now also needs **G-18** (fairness), **G-19/G-20** (evidence + coverage on every number), **G-14** (undo/ChangeSummary for Review & fix) and **G-25** (me-relative stats).

## 9. Demo / fixture contract

The fixture dataset reproduces the **exact DTOs above**, generated deterministically from real engine output where possible (the synthetic match generator `sports/badminton/src/bai_badminton/testing/synth.py` and the existing test fixtures in `apps/web/src/test/fixtures.ts` are the starting point), then hand-shaped into the persona set in file 12 §4. Rules:

- Every fixture DTO has `meta.demo = true`.
- Fixtures include **every state**: processing, partial, low coverage, failed, unsupported footage, corrected-with-ChangeSummary, no comparable matches, a match with no reliable hero moment (to test the honest "why not").
- Fixtures never contain fabricated *claims* the UI could not have derived from fixture events — the same validator that guards the Ask agent should run over fixture insights in CI.
