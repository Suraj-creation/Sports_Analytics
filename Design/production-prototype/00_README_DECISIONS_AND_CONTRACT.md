# 00 — Production Prototype: Decisions, Vocabulary and Shared Contract

**Status:** Source of truth for every other file in this folder. If another file disagrees with this one, this one wins and the other file has a bug.
**Audience:** product designers, frontend engineers, backend/CV engineers, anyone writing a screen or component spec.
**Working product name:** **Rally** (placeholder from the v1 spec; the code and login screen still say "Badminton AI").

---

## 1. What this folder is

The three files in `Design/` (the Front-End Blueprint, the Amateur Product Blueprint v2 and the Complete Product Design Spec v1) are **research-grade strategy**. They agree on almost everything that matters, and disagree on a handful of details. The existing `apps/web` is a **working analyst's cockpit**: dark, dense, built for someone who already understands rallies, bands and event logs.

This folder turns both into **a build-ready spec for a production-grade design prototype aimed at amateur players**, while keeping the analytics underneath as deterministic, evidence-linked and professional-grade.

> **The governing split.** *Analytics* stay professional: deterministic, versioned, evidence-linked, abstain-when-unsure. *Presentation* is built for an amateur: warm, short, self-referenced, never judging. Presentation changes order, wording and density — **never the factual standard.**

### 1.1 Reading order

| # | File | Answers | Status |
|---|---|---|---|
| 00 | `00_README_DECISIONS_AND_CONTRACT.md` | What was decided, what words and names we use, what exists today | Drafted |
| 01 | `01_FIRST_PRINCIPLES_AND_BEHAVIOUR_MODEL.md` | Who the amateur is, what they feel and fear, and the rules that follow | Drafted |
| 02 | `02_CURRENT_STATE_AUDIT.md` | What the current UI/API/engine produce, and what to keep, reshape, hide or drop | Drafted |
| 03 | `03_ONBOARDING_AND_FIRST_RUN.md` | Every step from "never heard of it" to "first moment saved" | Drafted |
| 04 | `04_INFORMATION_ARCHITECTURE_AND_NAVIGATION.md` | Sitemap, routes, navigation, shell, presets, roles | Drafted |
| 05a | `05a_SCREENS_CORE_LOOP.md` | Landing, Home, Matches, New match, Processing, Recap, Moments, Clip | Drafted |
| 05b | `05b_SCREENS_ANALYSIS_AND_REVIEW.md` | Deep dive (Story, Rallies, Shots, Court, Compare, Ask), Review & fix | Drafted |
| 05c | `05c_SCREENS_PROGRESS_SOCIAL_SETTINGS.md` | Progress, Records, Shots, Journey, Explore, Together, Share, Settings, Help | Drafted |
| 06 | `06_ANALYTICS_CATALOGUE_AND_TRANSLATION.md` | Every metric: engine source → plain label → component → depth → readiness | Drafted |
| 07 | `07_COMPONENT_LIBRARY.md` | Every reusable component: anatomy, props, states, a11y | Drafted |
| 08 | `08_VISUAL_DESIGN_SYSTEM.md` | Look and feel, tokens, type, motion, data-viz, responsive | Drafted |
| 09 | `09_COPY_AND_VOICE.md` | Voice, microcopy by state, claim templates, banned phrases | Drafted |
| 10 | `10_ENGAGEMENT_SOCIAL_AND_PRIVACY.md` | Return mechanics, notifications, sharing, consent, privacy centre | Drafted |
| 11 | `11_DATA_CONTRACTS_AND_BACKEND_GAPS.md` | What the UI needs vs what the API has; new entities and endpoints | Drafted |
| 12 | `12_BUILD_PLAN_QA_AND_RESEARCH.md` | Phased build order, demo fixtures, acceptance tests, user research | Drafted |

---

## 2. Reality check — what the repository actually contains (verified in code)

This section exists because the design docs were written against an *imagined* product and the code is a *real, narrower* one. Design for the destination; **build in the order the evidence layer allows**.

### 2.1 Stack (not Next.js)

`apps/web` is **Vite 7 + React 19 + TanStack Router + TanStack Query + Zustand + Tailwind v4 + Radix primitives + Archivo (variable) + hls.js**, with Biome, Vitest and Playwright. There is **no Next.js** in the repo. Consequences:

- All route and component specs are written **framework-neutral**, with route paths in **TanStack Router** syntax (`/matches/$matchId`).
- The current app is a client-rendered SPA served by FastAPI. That is fine for the signed-in product. The **public landing page needs SEO and a fast first paint**; if that matters, host it as a separate static/Next site later. Not required for the prototype. (Decision D1.)
- Reuse what exists: `Button`, `IconButton`, `BandChip`, `Meter`, `Empty`, `ErrorNote`, `Field`, `Kbd`, `Spinner`, `PlayerDot`, `VideoStage`, `Timeline`, `CourtMinimap`, `CourtView` canvas geometry, `frameClock`, `usePlayback`, `useSession`, the `?f=<frame>` deep link.

### 2.2 What exists today (screens)

| Route | Screen | Audience it was built for |
|---|---|---|
| `/` | **Library** — upload card, YouTube import card, match grid | Analyst / developer |
| `/sessions/$sessionId` | **Session** — video + timeline + court minimap + live feed; tabs **Stats · Heatmaps · Highlights · Rallies · Ask · Export** | Analyst |
| `/sessions/$sessionId/calibrate` | **Calibrate** — click 4–10 court points with a loupe | Developer |
| `/system` | **System** — GPU, host, runtime, profiles, models | Operator |
| (gate) | **Login** — shared passphrase from `.env` | Operator |

### 2.3 What the engine produces today (all of it is deterministic and evidence-linked)

- **Per player (`PlayerStats`)**: points won/lost, win rate, winners, errors out/net, strokes by type, smashes, jump smashes, points won with a smash, serves, serve points won, distance (m), points won under pressure.
- **Per match**: rally count, average and longest rally (shots), active play seconds, momentum (EWMA) with shifts, score timeline, unofficial (warm-up/replay) rallies kept on the timeline but unscored.
- **Highlights**: scored 0–10 with a *reasons* decomposition; categories `longest_rally, smash_winner, jump_smash, best_defence, net_battle, comeback, momentum_shift, deuce, game_point, match_point, clutch`; diversity-re-ranked (MMR).
- **Heatmaps** per player: `presence, movement, origin, landing, targeting`.
- **Court geometry**: per-frame line-based calibration with a quality record; scene segments (main camera / other camera / no court).
- **Events** with `band` (`confirmed` ≥0.85 / `probable` ≥0.60 / `uncertain`), `status` (`provisional / confirmed / corrected / retracted / human_verified`), `evidence[]`, `provenance`.
- **Corrections** (human-in-the-loop): confirm winner, change winner (re-scores everything after), mark a rally official/not, "match starts here". Re-fold is deterministic.
- **Ask** (grounded LLM agent): every number must come from a tool result; citations `[[ev:ID]]` open the moment.
- **Exports**: PDF match report, rallies CSV, legacy CSV, events JSONL, summary JSON, per-rally `clip.mp4`.
- **Stroke taxonomy**: 12 strokes (`short_serve, long_serve, smash, drop, clear, lift, drive, push, rush (net kill), net_shot, cross_net, block, unknown`) + subtype `jump_smash`; court zones 3 depth × 3 width per half.

### 2.4 What the design docs assume that does **not** exist yet

| Assumption in the design docs | Reality | Where it is handled |
|---|---|---|
| Player accounts, profiles, nicknames, history across matches | Shared passphrase auth; `P1`/`P2` are *tracks* (near/far side), not people | Doc 11 (entities), Doc 03 ("Pick yourself") |
| Doubles | `PlayerId = Literal["P1","P2"]` everywhere; doubles is P2 in `docs/architecture/ROADMAP.md` | Docs 05a/06 mark every doubles surface **Not yet**; designed now, built later |
| Longitudinal progress, personal records, journey, partners | No cross-match store; analytics are per session | Doc 11; Progress screens ship with demo fixtures first |
| Consent ledger, sharing, retention controls | None | Doc 10/11 |
| Free play with no scoring | Rule engine is BWF-scored; unscored rallies exist only as "unofficial" | Doc 11 gap **G-04** (needs a *free-play* match type) |
| A phone clip filmed by an amateur | Validated on **broadcast** footage (8-min match): 41 predicted vs 36 true rallies, **winner accuracy 61.5 %** before OCR was wired; amateur footage has no scoreboard | Doc 03 (capture readiness), Doc 06 (readiness ladder), Doc 05b (Review & fix) |
| Shot classification you can trust | Rule-based fallback classifier; learned model is a placeholder | Every shot-level surface carries **Preview** |
| One-tap court setup | Calibration is a manual 4-click page (auto-detect exists via line fitting) | Doc 03 ("Place your court" redesign) |

> Honest reading: the **evidence layer is strong for rallies, contacts, geometry and event provenance** and **weak for amateur-footage winner attribution, shot types, doubles and anything longitudinal**. The prototype must therefore *lead with moments and rallies*, treat shots/placement as Preview, and make **Review & fix** a first-class, friendly feature rather than a back-office tool.

---

## 3. Decisions log

Each decision records what the three source documents said, what we chose, and why. Later files cite these as **D#**.

| ID | Decision | Source conflict / reason |
|---|---|---|
| **D1** | **Build on `apps/web` (Vite/React/TanStack).** Specs are framework-neutral. Public landing may later be a separate static/Next site. | User assumed Next.js; repo isn't. Rewriting the stack adds risk with no user value. |
| **D2** | **Two orthogonal axes: Purpose × Depth.** *Purpose* (what the player wants today): Keep the moments · Understand my game · Choose something to practise · Prepare to compete · Discuss with someone · Just play. *Depth*: Quick · Guided · Advanced. Both editable per match, never identity labels. *Refinement (file 03):* "Just play" is not on the first-run picker (a first-time player has nothing to "just play" with yet); it appears in Settings → Preferences after the first match. | Blueprint/v2 use Purpose + Depth; v1 uses four "modes". |
| **D3** | **Four friendly Presets bundle the axes** for first-run and the header switch: **Relax** = Keep moments + Quick · **Explore** = Understand + Guided-light · **Improve** = Practise + Guided · **Compete** = Compete + Advanced. A preset is a shortcut; the two axes remain editable. Default preset: **Relax**. | v1's preset names are friendlier to amateurs; blueprint's axes are more correct. Both honoured. |
| **D4** | **Recap has three sections: Moments → My game → Together**, then a link to **Deep dive**. Deep dive is a separate per-match workspace (Story, Rallies, Shots, Court, Compare, Ask). | v2 "Emotional/Personal/Social recap" and Blueprint "Story/Learning/Analysis" are the same idea. |
| **D5** | **Confidence is shown in words, never percentages.** User-facing states: **Checked** (human-verified/corrected) · **Looks right** (engine `confirmed` band) · **Worth a look** (`probable`) · **Not enough to say** (`uncertain`/`unknown` → hidden from recap, listed in Review). A **coverage** line is separate from per-claim state. Until bands are calibrated on target footage, the whole surface carries a small **Preview** tag. | Engine bands come from raw model confidence (uncalibrated). Blueprint and v2 both forbid raw softmax as probability. |
| **D6** | **The scoreline is context, not a verdict.** No "winner" crown, no win-rate headline, no red/green for you vs them. Momentum chart, points-won head-to-head and win rate live in **Deep dive → Story**, off by default in Quick. | Engine's `PlayerStats` is win/loss-centric; every design doc says loss ≠ failure. |
| **D7** | **No XP, levels, streaks, leaderboards, loot, daily goals.** Allowed: **personal bests, firsts, personal records, optional challenges, pair memories**. A streak may be *tested later* only as weekly, opt-in, forgiving. | Blueprint: reject streaks. v1/v2: milestones and optional challenges. Gamification evidence is small and fades. |
| **D8** | **"You" is the anchor.** The first thing the product asks about the video is *"Which one is you?"* (tap yourself on a frame). Every metric thereafter is *"you"* first. `P1/P2` blue/orange remain **only** in Deep dive when comparing players. | Self-reference by default (all three docs). The engine only knows tracks, so this is a required onboarding step. |
| **D9** | **Value before configuration.** The very first screen after landing is a **sample match recap** with no questions. At most two skippable questions happen before the player sees *their own* first result. Consent is **just-in-time at upload**, not a wall at signup. | Blueprint §7.3, v2 §1.3; v1 puts consent before first value — we invert it. |
| **D10** | **Capability labels everywhere:** **Available** (validated on target footage) · **Preview** (works with limits; shown with a *Preview* tag and reasons) · **Not yet** (hidden, or a quiet "coming" note — never a confident guess). Shots, placement, distance, doubles, and anything calibration-gated start at Preview or Not yet. | Blueprint §7.10/§17; ROADMAP gap matrix. |
| **D11** | **Review & fix is a friendly feature, not an admin tool.** It starts from the *moments we are about to show you* ("Is this the rally you remember?"), asks at most three questions, shows what changed, and offers undo. Backed by the existing correction API. | Winner accuracy on non-broadcast footage is uncertain; trust depends on easy correction. |
| **D12** | **Match types: Match (scored) · Social game (rallies, no score) · Practice (drills).** The UI supports all three; the engine must add *free play* (gap G-04). Until then, Social game and Practice hide score-derived surfaces. | Most amateur sessions are not scored to BWF rules; the BWF fold would fabricate a score. |
| **D13** | **Two visual themes, one token set:** **Court Daylight** (light, warm, default on light-mode systems) for the recreational product, and **Arena Night** (the existing dark mat theme) for **video theatre and Deep dive**. Detailed in Doc 08. | v1 asks for warm off-white + one badminton accent; existing app is dark; analysis on video needs dark contrast. |
| **D14** | **Mobile-first for capture and recap, desktop-first for Deep dive.** Responsive web; no native app until capture/offline/notification need is proven. Mobile bottom bar: Home · Matches · **＋** · Moments · Progress. | Blueprint §5.3. |
| **D15** | **Private by default; analyse ≠ store ≠ share ≠ train.** Four separate permissions; model-training reuse off and separate. Funny/embarrassing clips are never shared without per-clip approval. Adult-only pilot. | All three docs. |
| **D16** | **Every claim opens its evidence in one tap** ("Watch this"), with definition, sample size and coverage one tap further. A claim with no resolvable evidence is withheld. | Core trust rule; existing `?f=` deep link and citation chips already do this. |
| **D17** | **Every player gets at least one verified positive moment per match when evidence permits; otherwise we say why — never invent one.** Highlight ranking is rebuilt to be fair to the loser and to defence (see Doc 06 §7). | v1/v2 non-negotiable. Current `score_rally` over-rewards length, smash winners and pressure points. |
| **D18** | **Plain-language names for engine terms** (Section 4). The engine vocabulary (`rally_end`, `band`, `provisional`) never reaches an amateur screen; it remains in Deep dive → Advanced and in exports. | v1 §4 content voice. |

---

## 4. Canonical vocabulary (use these words, in code and copy)

| Concept (code) | What the player sees | Notes |
|---|---|---|
| session | **Match** (or *Social game* / *Practice* by type) | Route `/matches/$matchId` maps 1:1 to `session_id` |
| highlight / clip | **Moment** | The unit of memory. "My Moments" is the personal collection (user's "Personal Highlight Identity") |
| rally | **Rally** | Always with shot count: "a 14-shot rally" |
| stroke / shot | **Shot** | Shot *names* from the 12-stroke ontology, lower-case in sentences |
| `band` + `status` | **Checked · Looks right · Worth a look** | D5. Never "confidence 0.72" |
| evidence / citation | **Watch this** | Button label; opens the exact frame range |
| coverage | **What we could see** | "We followed 31 of 36 rallies" |
| correction | **Fix this** | "Fix" is friendly; "Correct" appears in settings/logs |
| personal record | **Personal best** | Always scoped: "your longest rally in a match" |
| new shot type observed | **First** ("First cross-court net shot") | Observed ≠ mastered; copy says "spotted" |
| practice focus | **Focus** | One at a time, optional |
| pair history | **Pair memory** | "Together" section; both partners' consent |
| depth mode | **Quick · Guided · Advanced** | Switcher in the report header |
| preset | **Relax · Explore · Improve · Compete** | D3 |
| capability state | **Preview** tag | D10 |
| calibration | **Place your court** | Auto first; one-tap confirm; manual only on failure |
| scene (main/alt/none) | "Other camera — not followed" | Only matters for broadcast uploads |
| unofficial rally | "Not counted — warm-up" | Reinstatable |

---

## 5. Canonical route map

Paths are TanStack-Router style. `$matchId` = `session_id`. A route marked **(alias)** keeps working for bookmarks.

| Route | Screen | Doc |
|---|---|---|
| `/welcome` | Landing + interactive sample | 05a |
| `/welcome/sample` | Sample match recap (read-only, labelled "Sample") | 05a |
| `/start` | Onboarding (steps in query/state, not separate pages) | 03 |
| `/` | **Home** | 05a |
| `/matches` | Matches list | 05a |
| `/matches/new` | New match (record guide → upload → who's who → court → consent) | 03, 05a |
| `/matches/$matchId` | **Recap** (Moments → My game → Together) | 05a |
| `/matches/$matchId/processing` | Processing (also an in-page state of the recap) | 05a |
| `/matches/$matchId/moments` | Moments from this match | 05a |
| `/matches/$matchId/deep-dive` | Deep dive shell, with sub-routes: `/story` `/rallies` `/shots` `/court` `/compare` `/ask` | 05b |
| `/matches/$matchId/review` | **Review & fix** queue | 05b |
| `/matches/$matchId/court` | Place your court (replaces `/calibrate`) | 03, 05b |
| `/moments` | All my Moments (For you · Favourites · Together) | 05a |
| `/moments/$clipId` | Clip detail | 05a |
| `/progress` | Progress overview (self-baseline, comparable matches) | 05c |
| `/progress/records` | Personal bests | 05c |
| `/progress/shots` | Shot Explorer (what we've spotted) | 05c |
| `/progress/story` | **My story** (Journey timeline) | 05c |
| `/explore` | Optional challenges & skills | 05c |
| `/together` , `/together/$partnerId` | Pair memories | 05c |
| `/s/$token` | Shared moment/match page (consent-gated, expiring) | 05c, 10 |
| `/settings` + `/profile`, `/preferences`, `/privacy`, `/data`, `/notifications`, `/accessibility` | Settings & Privacy Centre | 05c, 10 |
| `/help` , `/help/$topic` , `/feedback` | Help, metric definitions, report an issue | 05c |
| `/admin/system` | Existing System page, moved out of the player's nav | 02 |
| `?f=<frame>` | Existing deep link — **keep**, on any match route | 04 |
| `?view=table` | Advanced workspace is a *layout mode* of Deep dive (event table, filters, exports), not a separate route | 05b |
| `/help/metrics` | Metric definitions as a Help topic (target of every `MetricPopover`) | 05c, 07 |

Settings sub-pages are `/settings/profile`, `/settings/preferences`, `/settings/privacy`, `/settings/data`, `/settings/notifications`, `/settings/accessibility`. The practice **Focus** has no route of its own: it is a `FocusSheet` plus a "My focus" section of `/progress`.

Primary navigation (desktop sidebar): **Home · Matches · Moments · Progress · Together · Explore** and an avatar menu (Profile, Settings, Help). **Mobile bottom bar:** Home · Matches · ＋ (Add a match) · Moments · Progress. Together and Explore appear as Home cards and Moments filters on mobile. Full detail in Doc 04.

---

## 6. Canonical component names

Specs in Doc 07 and screen docs must use exactly these names. (✱ = already exists in `apps/web` and should be *evolved*, not rewritten.)

**Shell & navigation:** `AppShell`✱, `SideNav`, `BottomBar`, `AddMatchButton`, `PresetSwitcher`, `PurposeChips`, `DepthSwitcher`, `PreviewTag`, `DemoBanner`, `AvatarMenu`, `Breadcrumb`.

**Onboarding:** `ValueHero`, `SampleRecapEmbed`, `PurposePicker`, `PresetCards`, `RecordGuide`, `FramingChecklist`, `TestClipCheck`, `SuitabilityResult`, `PickYourself`, `WhoIsWho`, `PlaceYourCourt`, `ConsentCards`, `UploadProgress`✱ (from `UploadCard`), `ProcessingStages`, `FirstValueReveal`.

**Core loop:** `MatchCard`✱ (from `SessionCard`), `MatchStatusChip`, `RecapHeader`, `HeroMoment`, `MomentCard`, `MomentStrip`, `ClipPlayer`✱ (from `VideoStage`), `FactTrio` (the three facts), `StoryParagraph`, `PersonalNote`, `RecapFeedback`, `NextStepRow`.

**Evidence & trust:** `InsightCard`, `EvidenceChip` ("Watch this"), `CheckChip` (Checked / Looks right / Worth a look)✱ (from `BandChip`), `CoverageBar`, `MetricPopover`, `ReviewBanner`, `FixSheet`, `ChangeSummaryBanner`, `NotEnoughToSay`.

**Analysis:** `RallyTimeline`✱ (from `Timeline`), `RallyRow`✱, `RallyDetailPanel`, `ShotMix`✱ (from `StrokeMix`), `ShotRepertoireGrid`, `CourtMap`✱ (from `CourtMinimap`/`HeatCanvas`), `HeatmapKindTabs`, `ScoreStory`, `MomentumChart`✱ (from `Momentum`), `HeadToHead`✱ (from `H2HRow`), `CompareMatchesPicker`, `AskPanel`✱ (from `AskTab`), `ExportList`✱.

**Progress & identity:** `ProgressCard`, `TrendSmallMultiples`, `ComparabilityNote`, `PersonalBestCard`, `FirstBadge` (a "First", not a trophy), `JourneyTimeline`, `FocusCard`, `ReflectionPrompt`, `ChallengeCard`.

**Social:** `PartnerCard`, `PairMemoryCard`, `SharePreviewDialog`, `ShareAudiencePicker`, `InviteLink`.

**Privacy & settings:** `ConsentLedger`, `ConsentToggle`, `NotificationPrefs`, `DataExportRequest`, `DeleteConfirmDialog`✱ (from the delete dialog), `AccessibilityPrefs`.

**Added by the screen specs (specified in file 07 §14):** `EntryChoice`, `MatchTypePicker`, `LensChips`, `ScoreChip`, `FilterBar`, `FilterSheet`, `FavouriteButton`, `WhyChosenPanel`, `DeepDiveShell`, `SubNav`, `RallyFilterBar`, `ShotSequenceTable`, `ZoneTable`, `QualityPanel`, `EventTable`, `FixQueue`, `CourtFitBadge`, `AnswerFeedback`, `FocusSheet`, `StatusLadder`, `MilestoneCard`, `BaselineNote`, `ChallengeModePicker`, `ActiveLinksList`, `ConsentRow`, `PauseAllToggle`, `ToneSelector`, `HelpArticle`, `FeedbackForm`, `SharedMomentPage`, `PairTimeline`, `UnlinkDialog`. File 07 §1 also lists further components (about 88 in total) — file 07 is the full inventory; this list is the minimum vocabulary.

**States:** `EmptyState`✱ (`Empty`), `LoadingSkeleton`, `PartialAnalysisNote`, `FailedState`, `LowCoverageState`, `UnsupportedFootageState`, `PermissionRevokedState`, `OfflineState`.

---

## 7. Capability readiness (what may ship at which label)

| Surface / metric | Label today | Gate to move up |
|---|---|---|
| Rally segmentation, rally length, active play time | **Available** on fixed or broadcast main-camera video with a found court | Validate on amateur phone footage (behind-baseline, side-on, high) |
| Moments from rallies (longest, close score) | **Available** | — |
| Winner of a rally / scoreline | **Preview** until the player has Checked it; **Available** once Checked | OCR/scoreboard absent on amateur video → rely on Review & fix |
| Shot types, shot mix, shot "firsts", smash counts | **Preview** | Learned stroke classifier validated on amateur footage |
| "Where the other player met your shot" (`m.place.opponent_met_map`) | **Preview** (needs a good court fit; today's `landing_court_xy` is the receiver's feet, so it is named for what it is) | Court-fit coverage gate (G-09) |
| True landing zone share ("where your shots land") | **Not yet** | True landing point from trajectory (ROADMAP #12, G-10) |
| Any shot read as "Looks right" | **Not possible today**: rule-based stroke confidence is capped at 0.7, below the 0.85 `confirmed` band, so shots are *Worth a look* until a person checks them | Learned classifier + calibration (G-08) |
| Court presence heatmap (relative) | **Preview** | Geometry gates on metric analytics (ROADMAP P0 #7) |
| Distance in metres, speed | **Not yet** (foot jitter inflates distance; ungated) | Geometry gates + smoothing + coverage |
| Active play / movement variety | **Preview** (relative, labelled "while the shuttle was in play") | Calibration coverage |
| Personal bests, firsts, progress, journey | **Preview** with demo fixtures; real data needs a cross-match store | Doc 11 entities |
| Doubles (any surface) | **Not yet** | `PlayerId` generalisation (ROADMAP #9) |
| Partner/pair memory | **Not yet** | Doubles + consent + invites |
| Activity / fitness estimates (calories, load, readiness) | **Not yet — and never from video alone** | Out of scope; self-reported only |
| Ask ("Coach chat") | **Available** (grounded) | Keep citation validation |

---

## 8. Conventions every spec file follows

**Screen spec template:** Purpose · Who and when · Entry points · Layout (wireframe, mobile + desktop) · Components used · Data in (API field → UI) · Copy (headline, empty, error) · Interactions · States (loading / empty / partial / complete / low-coverage / failed / permission / offline / demo) · Depth behaviour (Quick/Guided/Advanced) · Preset behaviour · Accessibility · Telemetry events · Acceptance criteria (IDs `AC-<screen>-<n>`).

**Component spec template:** Purpose · Anatomy · Props (TypeScript-ish) · Variants · States · Behaviour · Accessibility · Copy rules · Reuse from existing code · Used by · Tests.

**Wireframes** are ASCII and are *layout and hierarchy*, not visual design (Doc 08 owns visual design).

**IDs:** decisions `D#` (this file) · gaps `G-##` (Doc 11) · acceptance `AC-…` · metrics `m.*` (Doc 06) · experiments `X#` (Doc 12).

---

## 9. Open questions for the product owner (the design proceeds on the stated defaults)

| # | Question | Default used |
|---|---|---|
| Q1 | Keep Vite, or move the signed-in app to Next.js? | Keep (D1) |
| Q2 | Is the first launch market India? (Informs WhatsApp-first sharing, apartment/academy court contexts, data-light uploads, languages) | Assume yes for *hypotheses only*; Doc 12 lists it as research to validate |
| Q3 | Adults only for the pilot? | Yes (D15) |
| Q4 | Can amateurs *film* in-app, or only upload a clip? | Upload only for the prototype; Record guide covers filming |
| Q5 | Is Doubles in the first public prototype, or after the engine generalises `PlayerId`? | After; designed now, **Not yet** |
| Q6 | Product name — is "Rally" acceptable as a working name? | Yes, placeholder |
| Q7 | Is a free-play (unscored) match type acceptable for the engine team to build? | Needed (G-04) |

---

## 10. Status of this folder

All 15 files are drafted. They are **proposals for review**, not signed-off requirements. Known follow-ups: the gap register in file 11 is the single numbering authority (G-01 → G-32 plus G-ONB-1 → 9); the 32 components added by the screen specs are specified in file 07 §14; the fixture set is in file 12 §4; open questions Q1–Q7 above need the product owner.
