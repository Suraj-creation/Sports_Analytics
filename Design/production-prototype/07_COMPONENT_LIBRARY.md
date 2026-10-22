# 07 — Component Library

**Status:** Build spec. Names are fixed by file 00 §6. Decisions are cited as **D#** (file 00 §3). Visual values come from file 08; copy comes from file 09.
**Stack assumed (verified):** Vite 7 · React 19 · TanStack Router/Query · Zustand · Tailwind v4 `@theme` tokens · Radix (`dialog`, `popover`, `tabs`, `tooltip`) · `lucide-react` · hand-drawn SVG/canvas for charts (no chart library is installed and none is needed).

---

## 0. How to read this file

1. §1 is the **inventory** (every component, layer, new/evolve, priority) and §2 the **composition map**.
2. §3 defines the **shared types and rules** every component uses (check states, capability labels, evidence refs, depth).
3. §4–§12 are the specs. The components that carry the product's trust and emotion get the **deep treatment** (anatomy, props, full state tables): `CheckChip`, `EvidenceChip`, `CoverageBar`, `InsightCard`, `HeroMoment`, `MomentCard`, `ClipPlayer`, `FixSheet`, `ChangeSummaryBanner`, `PlaceYourCourt`, `PickYourself`, `ConsentToggle`/`ConsentLedger`, `SharePreviewDialog`, `ProgressCard`/`TrendSmallMultiples`/`ComparabilityNote`, `PersonalBestCard`/`FirstBadge`, `JourneyTimeline`, `FocusCard`, `CourtMap`, `RallyTimeline`, `ProcessingStages` and the **state family**. Everything else is a compact spec card.
4. §13 is **implementation guidance** (folders, Radix/Tailwind/Query/Zustand usage, `frameClock`, fixtures, testing).

**Universal rules (apply to every component, never repeated below):**

- **R1 Evidence first (D16).** A component that states a claim receives an `EvidenceRef[]`; with none, it renders nothing or `NotEnoughToSay`. No component accepts a bare number.
- **R2 Words, not percentages (D5).** Certainty is `CheckState`, never `0.72`.
- **R3 You first (D8).** Anything per-player takes `me: PlayerId | null`; "you" is styled with `--you`, others neutral. `P1/P2` colours appear only when `variant="compare"` in Deep dive.
- **R4 Capability label (D10).** Any surface fed by a Preview metric renders `PreviewTag`. Any Not-yet metric renders nothing (or a quiet "coming" note in Advanced only).
- **R5 Never colour alone.** Icon + word + shape (file 08 §10).
- **R6 Honest denominators.** Rates show `n of m`; zero ≠ missing ≠ not measured ≠ not applicable (§3.5 `Absent` type).
- **R7 Depth is a prop, not a fork.** One component, three densities (`depth: Depth`), same data.
- **R8 Keyboard + SR parity.** Every pointer interaction has a keyboard path; every chart has a text summary and a table.
- **R9 No engine words.** `band`, `provisional`, `rally_end`, `P1` never appear in rendered text outside Advanced/Export.

---

## 1. Component inventory

Priority: **P0** = needed for the first clickable prototype · **P1** = needed for the pilot · **P2** = later. *Evolve* names the existing code to grow from (never rewrite what works).

### 1.1 Shell and navigation

| Component | Layer | New / Evolve | Pri |
|---|---|---|---|
| `AppShell` | shell | Evolve `components/AppShell.tsx` (add SideNav/BottomBar, theme, DemoBanner slot) | P0 |
| `SideNav` | shell | New | P0 |
| `BottomBar` | shell | New | P0 |
| `AddMatchButton` | shell | New | P0 |
| `PresetSwitcher` | shell | New | P1 |
| `PurposeChips` | shell | New | P1 |
| `DepthSwitcher` | shell | New | P0 |
| `PreviewTag` | trust | New | P0 |
| `DemoBanner` | shell | New | P0 |
| `AvatarMenu` | shell | New | P1 |
| `Breadcrumb` | shell | New (also replaces the lone `ArrowLeft` back link in `SessionPage` Header) | P1 |

### 1.2 Onboarding

| Component | Layer | New / Evolve | Pri |
|---|---|---|---|
| `ValueHero` | onboarding | New | P0 |
| `SampleRecapEmbed` | onboarding | New (renders the real recap components with demo fixtures) | P0 |
| `PurposePicker` | onboarding | New | P0 |
| `PresetCards` | onboarding | New | P1 |
| `RecordGuide` | onboarding | New | P0 |
| `FramingChecklist` | onboarding | New | P0 |
| `TestClipCheck` | onboarding | New (uses `POST /sessions` + first-seconds analysis; needs G-xx in file 11) | P1 |
| `SuitabilityResult` | onboarding | New | P0 |
| `PickYourself` | onboarding | New | P0 |
| `WhoIsWho` | onboarding | New (doubles; **Not yet**) | P2 |
| `PlaceYourCourt` | onboarding | Evolve `features/calibrate/CalibratePage.tsx` | P0 |
| `ConsentCards` | onboarding | New (composes `ConsentToggle`) | P0 |
| `UploadProgress` | onboarding | Evolve `UploadCard` in `features/library/LibraryPage.tsx` | P0 |
| `ProcessingStages` | onboarding | New (reads `useSession` status/ingest/frontier) | P0 |
| `FirstValueReveal` | onboarding | New | P0 |

### 1.3 Core loop

| Component | Layer | New / Evolve | Pri |
|---|---|---|---|
| `MatchCard` | core | Evolve `SessionCard` (+`Thumb`) in `LibraryPage.tsx` | P0 |
| `MatchStatusChip` | core | Evolve the status span + `STATUS_LABEL` | P0 |
| `RecapHeader` | core | Evolve `Header` in `SessionPage.tsx` | P0 |
| `HeroMoment` | core | New | P0 |
| `MomentCard` | core | Evolve the `<li>` in `HighlightsTab.tsx` | P0 |
| `MomentStrip` | core | New | P0 |
| `ClipPlayer` | core | Evolve `features/player/VideoStage.tsx` | P0 |
| `FactTrio` | core | New | P0 |
| `StoryParagraph` | core | New | P0 |
| `PersonalNote` | core | New | P1 |
| `RecapFeedback` | core | New | P1 |
| `NextStepRow` | core | New | P0 |

### 1.4 Evidence and trust

| Component | Layer | New / Evolve | Pri |
|---|---|---|---|
| `InsightCard` | trust | New | P0 |
| `EvidenceChip` | trust | Evolve the citation button in `AskTab.tsx` `Answer` | P0 |
| `CheckChip` | trust | Evolve `BandChip` in `components/ui.tsx` | P0 |
| `CoverageBar` | trust | New (data from `scene`, `calibration`, `degraded`, `frontier`) | P0 |
| `MetricPopover` | trust | New (Radix Popover) | P0 |
| `ReviewBanner` | trust | New (replaces the "Only rallies that need a look" checkbox as the entry point) | P0 |
| `FixSheet` | trust | Evolve `RallyRow` correction block in `RalliesTab.tsx` | P0 |
| `ChangeSummaryBanner` | trust | New (replaces the `corrected` keyframe in `styles.css` as the *explanation*) | P0 |
| `NotEnoughToSay` | trust | New | P0 |

### 1.5 Analysis

| Component | Layer | New / Evolve | Pri |
|---|---|---|---|
| `RallyTimeline` | analysis | Evolve `features/timeline/Timeline.tsx` (`Overview` + `Detail`) | P0 |
| `RallyRow` | analysis | Evolve `RallyRow` in `RalliesTab.tsx` | P0 |
| `RallyDetailPanel` | analysis | Evolve the `open` block of `RallyRow` | P1 |
| `ShotMix` | analysis | Evolve `StrokeMix` in `StatsTab.tsx` | P1 |
| `ShotRepertoireGrid` | analysis | New | P1 |
| `CourtMap` | analysis | Evolve `CourtView`/`prepareCanvas` (`geometry.ts`), `HeatCanvas` (`HeatmapsTab.tsx`), `CourtMinimap.tsx` | P0 |
| `HeatmapKindTabs` | analysis | Evolve the `KINDS` fieldset in `HeatmapsTab.tsx` | P1 |
| `ScoreStory` | analysis | New (score timeline as a sentence + minimal strip) | P1 |
| `MomentumChart` | analysis | Evolve `Momentum` in `StatsTab.tsx` | P2 |
| `HeadToHead` | analysis | Evolve `H2HRow` in `StatsTab.tsx` | P2 |
| `CompareMatchesPicker` | analysis | New | P1 |
| `AskPanel` | analysis | Evolve `AskTab.tsx` | P1 |
| `ExportList` | analysis | Evolve `ExportTab.tsx` | P1 |

### 1.6 Progress and identity

| Component | Layer | New / Evolve | Pri |
|---|---|---|---|
| `ProgressCard` | progress | New | P1 |
| `TrendSmallMultiples` | progress | New | P1 |
| `ComparabilityNote` | progress | New | P1 |
| `PersonalBestCard` | progress | New | P1 |
| `FirstBadge` | progress | New | P1 |
| `JourneyTimeline` | progress | New | P1 |
| `FocusCard` | progress | New | P2 |
| `ReflectionPrompt` | progress | New | P2 |
| `ChallengeCard` | progress | New | P2 |

### 1.7 Social, privacy, settings, states

| Component | Layer | New / Evolve | Pri |
|---|---|---|---|
| `PartnerCard`, `PairMemoryCard`, `InviteLink` | social | New (**Not yet**: need doubles + invites) | P2 |
| `SharePreviewDialog`, `ShareAudiencePicker` | social | New | P1 |
| `ConsentLedger`, `ConsentToggle` | privacy | New (`Toggle` in `VideoStage.tsx` is the switch to extract) | P0 |
| `NotificationPrefs`, `AccessibilityPrefs`, `DataExportRequest` | privacy | New | P1 |
| `DeleteConfirmDialog` | privacy | Evolve the Radix delete dialog in `SessionCard` | P0 |
| `EmptyState` | states | Evolve `Empty` in `ui.tsx` | P0 |
| `LoadingSkeleton` | states | New (replaces bare `Spinner` on page loads) | P0 |
| `PartialAnalysisNote`, `FailedState`, `LowCoverageState`, `UnsupportedFootageState` | states | New (absorbs `Banners` in `SessionPage.tsx`) | P0 |
| `PermissionRevokedState`, `OfflineState` | states | New | P1 |

---

## 2. Composition map

```
AppShell
 ├─ DemoBanner (demo/sample data only)
 ├─ SideNav (≥1024) | BottomBar (<1024) ── AddMatchButton
 ├─ AvatarMenu ── PresetSwitcher
 └─ <route outlet>
     ├─ Home ───────── ResumeCard(=NextStepRow) · HeroMoment · MomentStrip · ProgressCard(≤3) · MatchCard[]
     ├─ Matches ────── MatchCard[] (MatchStatusChip, Thumb)
     ├─ New match ──── RecordGuide(FramingChecklist, TestClipCheck→SuitabilityResult)
     │                 → UploadProgress → PickYourself → PlaceYourCourt → ConsentCards(ConsentToggle) → ProcessingStages
     ├─ Recap ──────── RecapHeader(DepthSwitcher, PurposeChips, MatchStatusChip, CoverageBar)
     │   ├─ ReviewBanner → FixSheet → ChangeSummaryBanner
     │   ├─ Moments:    HeroMoment · MomentStrip(MomentCard[]) ─ ClipPlayer(modal)
     │   ├─ My game:    FactTrio · StoryParagraph · InsightCard[] (CheckChip, EvidenceChip, MetricPopover)
     │   │              · PersonalBestCard/FirstBadge · PersonalNote
     │   ├─ Together:   PairMemoryCard (Not yet) · SharePreviewDialog
     │   └─ NextStepRow · RecapFeedback
     ├─ Deep dive ──── RallyTimeline · RallyRow[] → RallyDetailPanel · CourtMap(HeatmapKindTabs)
     │                 · ShotMix/ShotRepertoireGrid · ScoreStory · MomentumChart · HeadToHead
     │                 · CompareMatchesPicker · AskPanel(EvidenceChip) · ExportList
     ├─ Progress ───── ProgressCard · TrendSmallMultiples(ComparabilityNote) · PersonalBestCard · FirstBadge
     │                 · JourneyTimeline · FocusCard(ReflectionPrompt) · ChallengeCard
     └─ Settings ───── ConsentLedger(ConsentToggle) · NotificationPrefs · AccessibilityPrefs
                       · DataExportRequest · DeleteConfirmDialog
Everywhere: EmptyState · LoadingSkeleton · PartialAnalysisNote · FailedState · LowCoverageState
            · UnsupportedFootageState · PermissionRevokedState · OfflineState · PreviewTag · NotEnoughToSay
```

---

## 3. Shared types and rules

### 3.1 Core types (new file `apps/web/src/lib/trust.ts`)

```ts
import type { Band, EventStatus } from "@/lib/types";

export type Depth = "quick" | "guided" | "advanced";
export type Preset = "relax" | "explore" | "improve" | "compete";
export type Purpose = "moments" | "understand" | "practise" | "compete" | "discuss" | "justplay";
export type Capability = "available" | "preview" | "not_yet";

/** D5 — the only certainty vocabulary a player sees. */
export type CheckState = "checked" | "looks_right" | "worth_a_look" | "not_enough";

/** D16 — every claim resolves to footage. frames are the canonical unit (see lib/types.ts). */
export interface EvidenceRef {
  frameStart: number;
  frameEnd: number;
  eventIds: string[];
  label?: string;          // "Rally 14", "Cross-court net shot"
}

/** R6 — four kinds of "no number". Never render any of them as 0. */
export type Absent = { kind: "missing" | "not_measured" | "not_applicable" | "insufficient"; reason: string };
export type Measured<T> = T | Absent;

/** D5 mapping for a single event. Aggregates also need every dependency checked. */
export function checkStateOf(
  e: { band: Band; status: EventStatus },
  gate: { claimTypeValidatedOnThisFootage: boolean },
): CheckState {
  if (e.status === "retracted" || e.status === "provisional") return "not_enough";
  if (e.status === "human_verified" || e.status === "corrected") return "checked";
  if (e.band === "confirmed" && gate.claimTypeValidatedOnThisFootage) return "looks_right";
  if (e.band === "confirmed" || e.band === "probable") return "worth_a_look";
  return "not_enough";
}

/** A claim shown to a player (maps to Blueprint §8.1 InsightCard schema and Doc 06 metric contract). */
export interface Claim {
  id: string;
  type: "descriptive" | "comparison" | "hypothesis" | "recommendation";
  title: string;                   // task language, never trait language
  observation: string;             // bounded; includes n and denominator
  whyItMayMatter?: string;         // conditional wording only
  evidence: EvidenceRef[];         // length ≥ 1 or the claim is withheld
  n: number;                       // analysable sample
  denominator?: number;
  check: CheckState;
  checkReason?: string;
  coverage?: { followed: number; total: number; unit: "rallies" | "shots" | "matches" };
  alternatives?: string[];         // "What else could explain it"
  action?: { label: string; kind: "watch" | "focus" | "ask" | "save" };
  metricId: string;                // "m.rally_length" → MetricPopover
  capability: Capability;
  generatedAt: string;
  modelVersion: string;
}
```

### 3.2 Depth behaviour contract

| Depth | Density | Language | Evidence | Default charts |
|---|---|---|---|---|
| `quick` | airy (file 08 §8), 1 column on mobile | short sentences | one tap on any claim | none; clips and one court map at most |
| `guided` (default for Improve/Explore) | standard | plain + inline definitions | one tap | one court map or one trend |
| `advanced` | compact, tables available | full terminology | direct from table row | distributions, small multiples, event table |

Components take `depth` from a context (`useDepth()` reading a Zustand slice `prefs`); a prop override exists only for the sample embed.

### 3.3 Cross-cutting hooks (new)

| Hook | Purpose |
|---|---|
| `useDepth()`, `usePreset()`, `usePurpose()` | read/write the preference slice; persisted per match and default |
| `useMe(matchId)` | resolves `PlayerId` that is "you" in this match (from `PickYourself`); `null` until chosen |
| `useCapability(metricId)` | `Capability` for a metric from a static readiness table (file 00 §7 → `lib/capabilities.ts`) |
| `useEvidenceSeek()` | opens `ClipPlayer` at an `EvidenceRef` (shared by `EvidenceChip`, `MomentCard`, `RallyRow`) |
| `useComparable(metricId)` | whether two matches are comparable and why not (drives `ComparabilityNote`) |

### 3.4 Preview rule

`PreviewTag` is rendered by the **component**, not the screen: each metric-bearing component calls `useCapability(claim.metricId)` and shows the tag when `"preview"`. A screen cannot forget it.

### 3.5 Absence rule

Components that print numbers accept `Measured<number>`. A helper `fmt(n: Measured<number>)` returns `"—"` plus an `aria-label` carrying `reason`. Charts draw `Absent` as a hatched gap (file 08 §10 hatch pattern, §12 rule 3).

---

## 4. Trust components (deep treatment)

### 4.1 `CheckChip`

**Purpose.** The single visual for "how much should I trust this?" at the level of one event or claim (D5). Evolves `BandChip`, which today encodes `confirmed = solid`, `probable = outlined + word`, `uncertain = dashed + word`.

**Anatomy**

```
 ┌───────────────┐   ┌─────────────────┐   ┌──────────────────┐   ┌─────────────────────┐
 │ ✓✓ Checked    │   │ ✓ Looks right   │   │ ◔ Worth a look   │   │ ? Not enough to say │
 └───────────────┘   └─────────────────┘   └──────────────────┘   └─────────────────────┘
   solid fill         outlined, solid      outlined, dashed        dashed + hatch, muted
   double tick        single tick          half-filled dial        question mark
```

**Props**

```ts
interface CheckChipProps {
  state: CheckState;
  /** plain-language reason, shown in the popover and read by screen readers */
  reason?: string;
  size?: "sm" | "md";           // sm = 20px high (timeline/list), md = 28px (cards)
  showWord?: boolean;           // default true; false only inside a dense row that has a legend
  onActivate?: () => void;      // opens MetricPopover/“why” (defaults to showing `reason`)
}
```

**Variants.** `sm`/`md`; `onDark` (Arena Night) swaps to dark tokens automatically via CSS variables — no prop.

**States.** Rest · hover (border strengthens) · focus (2 px ring) · pressed · disabled (never used; a chip is always readable).

| State | Icon | Word | Border | Fill | Tooltip (tap on touch) |
|---|---|---|---|---|---|
| `checked` | double tick | Checked | solid | tint of `--strength`? no — **neutral ink tint** (checking is a human act, not "good") | "You or a reviewer confirmed this." |
| `looks_right` | tick | Looks right | solid | none | "This type of finding has been tested on footage like yours, but no person checked this one." Only after G-08/G-11 for that claim type and footage condition. |
| `worth_a_look` | half dial | Worth a look | dashed | none | "Our analysis isn't sure. Take a quick look." |
| `not_enough` | question | Not enough to say | dashed + hatch | hatch | "We couldn't tell reliably, so we left it out of your recap." |

Never green/red. `checked` uses ink, not `--strength`, so "checked" is never read as "good".

**Behaviour.** Click/Enter/Space opens a `MetricPopover`-style popover with the reason and a "Fix this" action (opens `FixSheet` for the underlying event). Tooltip content is also in `aria-describedby`.

**Accessibility.** `role="button"` when interactive else `role="img"`; accessible name `"{word}. {reason}"`. Hit area ≥ 44 px via padding on touch. Shape + icon + word carry meaning (R5).

**Copy rules.** Word only from the table; never "verified"/"confirmed"/"%". Hide the chip when `checked` and the surrounding card is a Checked-only list (reduce noise).

**Reuse.** `BandChip` in `components/ui.tsx`; CSS classes `.band-confirmed/.band-probable/.band-uncertain` in `styles.css` → rename `.check-*` and keep the old classes as aliases for one release. `checkStateOf()` replaces direct `band` reads in `RalliesTab`, `Timeline`, `StrokeToast`, `LiveFeed`.

**Used by.** `InsightCard`, `RallyRow`, `RallyTimeline` marks, `MomentCard`, `HeroMoment`, `ClipPlayer` toast, `ReviewBanner` list.

**Tests.** Mapping table (`checkStateOf` all 5 statuses × 4 bands); chip names are unique; no colour-only (a render test asserts an icon and word exist); axe pass.

---

### 4.2 `EvidenceChip` ("Watch this")

**Purpose.** The universal "show me" (D16). One tap opens footage at the exact claim. Evolves the numbered citation button in `AskTab.Answer` (`seekFrame(max(0, c.frame - round(fps)))`).

**Anatomy**

```
 ▶ Watch this         ▶ Watch 3 examples        ▶ Rally 14 · 0:42
```

**Props**

```ts
interface EvidenceChipProps {
  evidence: EvidenceRef[];                // ≥1
  variant?: "button" | "inline" | "citation";   // citation = small numbered chip in prose (AskPanel)
  label?: string;                         // overrides "Watch this"
  leadInSeconds?: number;                 // default 1 (existing behaviour: one second before)
  onOpen?: (ref: EvidenceRef, index: number) => void;
}
```

**Behaviour.** One ref → opens `ClipPlayer` (modal on mobile, side panel on desktop) at `frameStart − lead`, auto-paused at `frameEnd + 1 s`. Several refs → opens at the first with a "1 of 3" stepper. Frame range is deep-linkable as `?f=<frameStart>` (existing `SessionSearch`).

**States.** Default · loading (video not yet ready: chip disabled with spinner and "Preparing video") · unavailable (`ref` outside the analysed range: chip replaced by `NotEnoughToSay` inline — R1) · permission revoked (disabled; `PermissionRevokedState`).

**Accessibility.** Native `<button>`; name `"Watch this: {label}"`; opening moves focus into the player, closing returns focus to the chip (Radix Dialog does this); `aria-haspopup="dialog"`.

**Copy.** "Watch this" / "Watch {n} examples". Never "Evidence", "Citation", "Source".

**Used by.** `InsightCard`, `StoryParagraph`, `FactTrio`, `PersonalBestCard`, `FirstBadge`, `AskPanel`, `RallyRow`, `ProgressCard`.

**Tests.** Opens the player at the right frame for `fps=25/30`; withheld when `evidence=[]`; focus return; `?f=` round trip.

---

### 4.3 `CoverageBar`

**Purpose.** "What we could see" — recording coverage as a first-class part of every report (Blueprint §8.3). Distinct from `CheckChip` (per claim).

**Anatomy**

```
 We followed 31 of 36 rallies.                                        [Details ▾]
 ███████████████████████▒▒▒▒▒░░░                       (legend on expand)
  followed            other camera   not analysed
```

**Props**

```ts
interface CoverageBarProps {
  total: number;                       // rallies (or seconds for Social game)
  followed: number;
  segments?: { kind: "followed" | "other_camera" | "no_court" | "not_analysed" | "warmup"; weight: number; reason?: string }[];
  unit?: "rallies" | "seconds";
  courtQuality?: number | null;        // from calibration.quality.precision → words only ("Court fit: good")
  degraded?: { stage: string; reason: string }[];   // from StatusMsg.degraded
  compact?: boolean;                   // single line in RecapHeader
}
```

**Data.** `followed/total` from official rallies vs analysed frames; segments from `scene` events (`view: main|alt|none`, `analysed`), `calibration.coverage`, `StatusMsg.degraded[]`.

**States.** Full (≥ 90 %): single quiet line · Partial: amber ◆ icon + "We couldn't follow part of this match" + expand · Low (< 60 %): becomes `LowCoverageState` block · Unknown: "We're still working out what we could see." (processing).

**Accessibility.** The bar is `aria-hidden`; the sentence is the content; the expanded legend is a `<dl>`. Hatch pattern distinguishes `not_analysed` from `other_camera` (stripes vs dots), not colour.

**Copy.** "We followed 31 of 36 rallies." Never "Coverage 86%". Reasons in plain words: "Another camera was showing", "The court wasn't in view".

**Reuse.** The `Banners` component in `SessionPage.tsx` (court-not-found, degraded) is absorbed; the analysed-so-far green strip in `Timeline.Overview` becomes this bar in processing.

**Used by.** `RecapHeader`, `RallyTimeline` (mini), `PartialAnalysisNote`, `LowCoverageState`, `ProcessingStages`.

**Tests.** `followed > total` clamps; zero total renders "Nothing analysed yet"; degraded list rendering.

---

### 4.4 `InsightCard`

**Purpose.** The atomic unit of "My game" (Blueprint §8.1). It enforces the four epistemic layers: **Measured · Classified · Meaning · Suggestion**, visibly separated.

**Anatomy (Guided depth, mobile)**

```
┌────────────────────────────────────────────────────────┐
│ ◆ Something to look at                 (type tag)      │
│ These longer rallies often ended after a short return  │  ← headline: task language
│ ────────────────────────────────────────────────────── │
│ Seen in 6 of 9 long rallies we could follow.           │  ← Measured (n of m)
│ [▶ Watch 3 examples]                                    │
│ [thumb][thumb][thumb]                                   │
│ ✓ Looks right · 2 rallies partly hidden   (CheckChip)  │
│ ────────────────────────────────────────────────────── │
│ It may be leaving you with fewer options at the net.   │  ← Meaning (conditional, own block)
│ Other things that could explain it ▸                    │  ← alternatives (collapsed)
│ ────────────────────────────────────────────────────── │
│ If it helps: try one lift to the back corner next time │  ← Suggestion (own block, optional)
│ [Pick as my focus] [Not now]                            │
│ That seems right · Fix this · Not useful · Save   ⓘ    │  ← response row
└────────────────────────────────────────────────────────┘
```

**Props**

```ts
interface InsightCardProps {
  claim: Claim;
  depth?: Depth;                          // from context
  tag?: "moment" | "strength" | "opportunity" | "milestone" | "note";   // visual role (§ type tag table)
  onResponse?: (r: "confirm" | "correct" | "dismiss" | "save", claim: Claim) => void;
  onPickFocus?: (claim: Claim) => void;
}
```

**Type tags** (icon + word + shape, never colour alone; colours from file 08 §10)

| Tag | Icon | Word | Colour token | When |
|---|---|---|---|---|
| `strength` | ✓ in circle | Strength | `--strength` | verified, specific, with n; never after one rally |
| `opportunity` | ◆ | Something to look at | `--opportunity` (amber, never red) | recurring situation, n ≥ minimum |
| `moment` | ▶ | Moment | `--you` | a clip-led finding |
| `milestone` | ★ outline (not a trophy) | Personal best / First | `--you` | via `PersonalBestCard`/`FirstBadge` |
| `note` | ● | Note | `--uncertain` | descriptive, no action |

**Depth.** Quick: headline + one evidence line + `EvidenceChip`; alternatives, meaning and response row hidden (a single "More" disclosure). Guided: as drawn. Advanced: adds `metricId`, definition link, denominators table, model version, event ids.

**States**

| State | Render |
|---|---|
| Normal | as above |
| `claim.check = "worth_a_look"` | the observation sentence is prefixed "We think" and the card is **not** eligible for the first screen of the recap |
| `claim.check = "not_enough"` or no evidence | the card is **not rendered**; the claim goes to the Review list |
| `capability = "preview"` | `PreviewTag` beside the type tag |
| Dismissed | collapses to a one-line "Hidden — Undo" for 10 s, then removed; preference remembered (D16 transparent) |
| Corrected upstream | `ChangeSummaryBanner` above; the card shows "Updated after your fix" for the session |
| Loading | skeleton with the real layout |

**Behaviour.** "That seems right" and "Not useful" are feedback, not verdicts; "Fix this" opens `FixSheet` for the most uncertain underlying event. "Pick as my focus" creates a `FocusCard` (one active at a time; replace-confirm).

**Accessibility.** `<article aria-labelledby>`; the four layers are `<section>`s with visually-hidden headings ("What we measured", "What it may mean", "What you could try"); response row is a `role="group"`; keyboard order = reading order.

**Copy rules.** Headline is about a *situation*, not the person ("These rallies…", never "You are weak at…"). Meaning uses may/might/could. Suggestion starts "If it helps:". Never "must", "should", "always", "never" (file 09).

**Reuse.** Nothing exists; the evidence-line pattern and number validator logic of `AskTab.Answer` is the model: every digit shown must come from `claim`.

**Used by.** Recap *My game*, Deep dive Story, Progress, Home.

**Tests.** Cannot render without evidence; layer headings present; dismiss/undo; depth switching hides blocks without changing data; copy lint (file 09 §14) over rendered text.

---

### 4.5 `MetricPopover`

**Purpose.** Information scent for any number: definition, numerator/denominator, window, exclusions, limits (Blueprint §8.14).

**Anatomy.** Trigger = small `ⓘ` (44 px hit area) next to a metric label. Content (Radix Popover, 320 px): **What this is** (one sentence) · **How we count it** (numerator ÷ denominator, window) · **Left out** (e.g. warm-up rallies, other cameras) · **Limits** (Preview reasons) · **Version** (Advanced only) · "Report something wrong".

**Props.** `metricId: string; value?: Measured<number>; n?: number; denominator?: number; window?: string; depth?: Depth`.

**States.** Loading definition (skeleton) · unknown metric (shows "We don't have a definition for this yet" and logs a dev warning — a screen shipping this fails CI).

**A11y.** Popover with focus trap, `Esc` closes, returns focus. Works on tap (no hover dependency).

**Reuse.** Radix Popover already used in `VideoStage` Controls (layers menu). Definitions come from Doc 06 `metrics` registry → `lib/metrics.ts`.

**Tests.** Every `metricId` used in the app resolves (`vitest` iterates the registry).

---

### 4.6 `PreviewTag`

**Purpose.** D10 label. Anatomy: `◇ Preview` (outline diamond + word), small. Tooltip/popover: "Works, with limits. {reason}". Props: `reason: string; size?: "sm"|"md"`. Never red/amber (it is neutral `--uncertain`). Not dismissible. A11y: text exposed; `aria-describedby` the reason. Used by every metric component (§3.4).

### 4.7 `ReviewBanner`

**Purpose.** Entry to Review & fix (D11), friendly and contextual. Anatomy: icon + sentence + primary action: *"Two things in this recap are worth a quick check — it takes about a minute. [Check them]"*. Props: `items: { eventId: string; why: string }[]; onStart: () => void; dismissible?: boolean`. Shows only when ≥ 1 item exists among **claims currently displayed**. Dismissal stored per match. Replaces the `onlyDoubtful` checkbox in `RalliesTab` as the primary entry (the filter stays inside Review). A11y: `role="status"`.

### 4.8 `NotEnoughToSay`

**Purpose.** The honest empty claim (Blueprint §12). Anatomy: dashed-outline block, `?` icon, one sentence, one next action. Props: `reason: "too_few" | "low_label_reliability" | "not_comparable" | "no_footage" | "capability_not_yet"; next?: { label: string; onClick: () => void }`. Never shows a 0 or an empty chart. Copy per reason in file 09 §8.5. A11y: `role="note"`.

---

## 5. Clip and moment components (deep treatment)

### 5.1 `ClipPlayer`

**Purpose.** One player for two jobs: **clip mode** (a Moment, a rally, an evidence range) and **match mode** (the whole video with overlays and timeline, Deep dive). Evolves `VideoStage`; keeps `useHls`, the `frameClock` publisher (`requestVideoFrameCallback`), `drawOverlay`, `usePlayback` store and the keyboard map in `SessionPage.useShortcuts`.

**Anatomy (clip mode, mobile)**

```
┌──────────────────────────────────────────┐
│ ‹ Close        Rally 14 · 12 shots   ⋯   │
│ ┌──────────────────────────────────────┐ │
│ │            video (16:9)              │ │
│ │  [caption: Long rally — your recover │ │
│ │   y at the back corner]              │ │
│ └──────────────────────────────────────┘ │
│ ━━━━━●━━━━━━━━━  0:03 / 0:19  ↻ loop     │  ← scrubber limited to clip range
│ ⏮ ⏯ ⏭   0.5×  ⛶                          │
│ Checked? ✓ Looks right    [Fix this]     │
│ ♡ Save   ↗ Share…   ▶ Open rally in Deep │
└──────────────────────────────────────────┘
```

**Props**

```ts
interface ClipPlayerProps {
  matchId: string;
  mode: "clip" | "match";
  range?: { frameStart: number; frameEnd: number; leadFrames?: number; tailFrames?: number };  // clip mode
  title?: string;
  caption?: string;                          // text description for non-visual users (R8)
  check?: CheckState;
  overlays?: Partial<Layers>;                // default OFF in quick/guided clip mode; ON in advanced match mode
  showScoreBug?: boolean;                    // default false in clip mode; follows `layers.scoreBug` in match mode
  showStrokeToast?: boolean;                 // default false (amateur) — shot names are Preview
  autoPlay?: boolean;                        // never with sound; muted autoplay only when user opened a clip
  loop?: boolean;
  lowData?: boolean;                         // preview-quality stream (label: "Preview quality")
  onClose?: () => void;
}
```

**Behaviour**

- Clip mode seeks to `frameStart − lead` (default 1 s), pauses at `frameEnd + tail` (default 1 s), then offers "Watch again"; the scrubber, frame-step and J/L skips are clamped to the range; "Open in full match" releases the clamp.
- `waitForAnalysis` gating (`SEMANTIC_LEAD_S`) exists only in processing: for `status="analysed"` it is off and the "Analysis is catching up" pill never shows. For a match still analysing, clip mode is limited to ranges below `frontier − SEMANTIC_LEAD_S·fps`.
- Overlay layers (`shuttle, players, pose, court, labels, scoreBug`): `pose` and `players` boxes are **off by default** for amateurs (they read as surveillance — file 01); `court` lines and `shuttle` trail are on in Advanced only. State persists in `localStorage` key `bai.layers` as today.
- Playback rate list `0.25, 0.5, 1, 1.5, 2` retained; default `0.5×` is *offered*, not forced.
- Captions: if `caption` exists it is rendered as a persistent text strip (not an overlay) and read by assistive tech.
- Full-screen via `requestFullscreen` on `stageRef` (existing double-click).
- Keyboard: Space/K, ←/→ frame, Shift+←/→ 5 s, J/L 10 s, `[`/`]` previous/next rally, `S` next smash (Advanced only), `.` hide overlays, `?` help — unchanged.

**States**

| State | Render |
|---|---|
| Loading (`hls: loading/waiting/idle`) | existing spinner overlay; copy "Getting your clip ready" |
| Preparing (`status: ingesting/created`) | "Preparing the video — you can watch as soon as the first seconds are ready" (existing text, softened) |
| Error (`hls: error`) | "This browser can't play the video. Try a recent Chrome, Edge, Safari or Firefox." + download link if exports allowed |
| Out of analysed range | player works, overlays hidden, chip "Not analysed yet" |
| Permission revoked / expired link | `PermissionRevokedState` replaces the stage |
| Offline | video buffered continues; controls remain; `OfflineState` banner |
| Reduced motion | no auto-advance, no pulse on the gating pill |

**Accessibility.** `<video>` has `aria-label`; custom controls are real buttons with names and shortcuts in `title`; caption strip is a live region only when it changes; focus visible; touch targets ≥ 44 px (existing `IconButton` is 36 px → size up on touch).

**Copy.** Titles are descriptive and neutral ("Rally 14 · 12 shots"). Never superlatives unless the definition is verified ("Your longest rally in a match" only when `m.longest_rally` is Checked).

**Reuse.** `VideoStage.tsx` (all of it), `ScoreBug.tsx` (kept for match mode, off in clip mode), `StrokeToast.tsx` (off by default), `Controls`/`Toggle` (extract `Toggle` as `ConsentToggle`'s switch), `usePlayback`, `useSession`, `frameClock`, `useHls`.

**Used by.** `HeroMoment`, `MomentCard` (modal), Clip detail, Deep dive, `EvidenceChip`, `FixSheet` (preview of the event being fixed), shared page `/s/$token`.

**Tests.** Range clamping at both ends; `seekFrame` rounding (`(frame+0.5)/fps`); default overlays by depth; `analysed` match never shows gating; keyboard map; focus return from modal.

---

### 5.2 `HeroMoment`

**Purpose.** The emotional front door of the recap (D4, D17): one moment worth replaying. Large, calm, one primary action.

**Anatomy (mobile)**

```
┌──────────────────────────────────────────┐
│ ┌──────────────────────────────────────┐ │
│ │ poster frame (sprite thumb)    ▶     │ │
│ │ 0:19                                 │ │
│ └──────────────────────────────────────┘ │
│  A 14-shot rally                          │  ← title (neutral, specific)
│  Your longest in a match so far           │  ← why chosen (only if Checked/definition holds)
│  ✓ Looks right      Rally 14 · 12:42      │
│  [▶ Watch]   [♡ Save]   [↗ Share…]        │
│  Why this moment? ▾                       │  ← selection reasons in words
└──────────────────────────────────────────┘
```

**Props**

```ts
interface HeroMomentProps {
  moment: {
    id: string;
    title: string;
    reasonWords: string[];                  // from Highlight.reasons, translated (Doc 06 §7)
    evidence: EvidenceRef;
    check: CheckState;
    poster?: { sessionId: string; atSeconds: number };   // uses spriteStyle()
    forPlayer: PlayerId | null;             // the person it is chosen for
    saved: boolean;
    kind: "personal_best" | "long_rally" | "defence" | "net" | "comeback" | "chosen" | "fun";
  } | null;
  me: PlayerId | null;
  onPlay(): void; onSave(): void; onShare(): void;
}
```

**States**

| State | Render |
|---|---|
| Ready | as drawn |
| `moment = null` and analysis complete | `NotEnoughToSay reason="no_footage"`-style block: "We couldn't pick a moment we're sure about for this match." + "Choose one yourself" (opens the rally list) — D17: never invent |
| Processing | skeleton hero + `ProcessingStages` |
| `check = worth_a_look` | still shown if it is the only candidate, with the chip and "Is this the rally you remember?" `FixSheet` prompt |
| Loser/winner | identical component; the score is never shown inside it (D6) |
| Social game / Practice | no score references ever |
| Demo | `DemoBanner` visible on the page; chip "Sample" on the poster |

**A11y.** Poster is a `<button>` named "Watch: {title}"; title is the heading of its region; "Why this moment?" is a disclosure.

**Copy.** Titles come from a closed set built from facts: "A {n}-shot rally", "A long exchange at the net", "A save from the back corner". No "Amazing", "Epic", "Beast".

**Reuse.** `Thumb`/`useSprite`/`spriteStyle` for the poster; `HighlightsTab` ranking list for the candidates; `exportUrl(...,"clip.mp4")` for download.

**Used by.** Recap, Home, Clip detail header, sample recap.

**Tests.** Null moment path; poster fallback when sprite is not built (`Film` icon, as `Thumb` does); no score text inside the component.

---

### 5.3 `MomentCard` / `MomentStrip`

**Purpose.** A Moment in a list/grid. Evolves the `<li>` in `HighlightsTab` (rank number, category chips, "Why:" line, score, play and download buttons) into a memory card without ranks or scores.

**Anatomy**

```
┌───────────────────┐
│ [poster]      ▶   │
│ 0:19  ♡           │
├───────────────────┤
│ A 14-shot rally   │
│ Rally 14 · Aditi  │   ← who it is for (nickname or "You")
│ ✓ Looks right     │
└───────────────────┘
```

**Props**

```ts
interface MomentCardProps {
  moment: HeroMomentProps["moment"] & { matchTitle?: string; date?: string; visibility: "private" | "shared" | "approved_public" };
  variant?: "grid" | "row" | "strip";
  onOpen(): void; onToggleSave(): void;
  showScore?: false;                 // type-level: score is never shown (the engine's 0–10 stays internal)
}
```

**Rules.** No rank numbers, no 0–10 score, no "best". Visibility chip shown only when not private. **Never autoplay in a grid** (v1 rule). Saved = ♡ filled + "Saved" label (not colour alone). Funny/bloopers show a "Private — needs your OK to share" lock until approved (D15).

**`MomentStrip`.** Horizontally scrollable list of up to 6 `MomentCard variant="strip"`, snap points, arrow buttons on desktop, "See all moments" tail card. `role="list"`, scroll container `tabIndex=0` with `aria-label`.

**States.** Empty (EmptyState "Your moments will appear here") · loading (skeleton ×3) · one only · many (virtualise > 60).

**Used by.** Recap, Home, `/moments`, `/matches/$id/moments`, Journey.

**Tests.** No rank/score in DOM; lock chip for funny; keyboard arrow scroll.

---

## 6. Review and correction (deep treatment)

### 6.1 `FixSheet`

**Purpose.** The friendly correction flow (D11). Starts from *what we are about to show you*, asks at most three questions, shows the consequences. Evolves the correction block in `RalliesTab.RallyRow`, which calls `api.correctWinner`, `api.verifyEvent`, `api.setRallyOfficial`, `api.setMatchStart`.

**Anatomy (bottom sheet on mobile, side panel on desktop)**

```
┌──────────────────────────────────────────────┐
│ Is this right?                           ✕   │
│ ┌──────────────────────────────────────────┐ │
│ │ clip of the rally (ClipPlayer clip mode) │ │
│ └──────────────────────────────────────────┘ │
│ Who won this rally?                           │
│ (●) You   ( ) Aditi   ( ) Not sure / skip      │  ← winner (existing correctWinner)
│ Is this part of the game?                      │
│ (●) Yes   ( ) No — it was a warm-up or a break │  ← existing setRallyOfficial
│ ▸ Something else is wrong                      │  → wrong person / wrong shot / bad clip / other
│ ⚠ Changing the winner updates the score from   │
│   here on.                                     │
│ [Save fix]  [I checked this rally]  [Skip]      │
└──────────────────────────────────────────────┘
```

**Props**

```ts
type FixKind = "winner" | "official" | "match_start" | "wrong_player" | "wrong_shot" | "bad_clip" | "other";
interface FixSheetProps {
  matchId: string;
  eventId: string;                       // rally_end event id
  evidence: EvidenceRef;
  me: PlayerId | null;
  names: Record<PlayerId, string>;       // nicknames; "You" substituted for `me`
  currentWinner: PlayerId | null;
  currentCheck: CheckState;
  isOfficial: boolean;
  queuePosition?: { index: number; total: number };   // "2 of 3"
  onDone(result: FixResult): void;
}
interface FixResult { kind: FixKind; changed: boolean; summary: ChangeSummary | null }
interface ChangeSummary { affected: { label: string; before: string; after: string }[]; rescored: boolean }
```

**Behaviour**

1. "Looks right already" is offered only after the player watched the evidence and the action identifies the exact event being checked. It calls `api.verifyEvent` and changes only that event to `Checked`; dependent aggregate claims retain their own gate (D5).
2. Winner change calls `api.correctWinner`; the engine re-folds every later point. The UI waits for the next `analyticsVersion` bump (store counter) then computes the **before/after diff** from the cached analytics (`useAnalytics` previous data via `placeholderData`) → `ChangeSummaryBanner`.
3. "Not part of the game" → `api.setRallyOfficial(false)`; "Match starts here" → `api.setMatchStart(frame)` — offered only when the rally is the first in the list.
4. `wrong_player`, `wrong_shot`, `bad_clip`, `other` are **feedback events** until the API supports them (gap G-15 in file 11): the sheet says "Thanks — noted. This won't change your numbers yet." Never promise a fix that the backend cannot make (v1 rule).
5. **Undo:** 10-second `Undo` toast; requires a "supersede" endpoint (G-14). Until then the sheet warns "You can change it again any time."
6. A queue: `ReviewBanner` starts a queue of ≤ 3 items ordered by *how visible the item is in the recap* (hero moment first), not by lowest confidence.

**States**

| State | Render |
|---|---|
| Idle | as drawn |
| Saving | primary button busy (`Button busy`), controls disabled |
| Saved, unchanged | "Thanks — that matches what we found." |
| Saved, changed | closes and shows `ChangeSummaryBanner` |
| Error | `ErrorNote` inline, selections kept |
| No `me` chosen | first row asks "Which one are you?" via `PickYourself` inline |
| Doubles | **Not yet** — 4 players; sheet limited to winner = side/team once engine supports |
| Offline | "You're offline — we'll save this when you're back" (queue locally) |

**A11y.** Radix Dialog (modal sheet), radio groups with fieldset/legend, live region announces result; Esc cancels without saving; focus returns to the invoking row/chip.

**Copy.** Titles are questions, never verdicts. "Fix this" is the verb. No "Wrong!"; no "AI error". Thank briefly; never defend the model.

**Reuse.** `RallyRow` mutations (`useMutation` ×4), `ErrorNote`, `Button`, `PlayerDot` (replaced by `--you` marker), `Dialog` pattern from `SessionCard` delete.

**Tests.** Mutation calls per option; diff computation; 3-item cap; no promise copy for feedback-only kinds.

---

### 6.2 `ChangeSummaryBanner`

**Purpose.** "What changed and why" after any correction (Blueprint §8.11). Replaces the silent `corrected` keyframe animation as the *explanation* (the animation may stay as a 1 s cue).

**Anatomy**

```
 ✎ Updated after your fix        Today 18:42
 • Score after rally 14: 11–9  →  10–10      • 2 moments re-checked
 [See what changed ▾]                [✕]   (Undo only after G-14)
```

**Props.** `summary: ChangeSummary; at: string; onUndo?: () => void; onDismiss(): void`. **Rules:** persists until dismissed or until the next fix; lists affected claims by name (Doc 06 `metric` ids → labels); if the correction removes a Moment/claim, says so ("One moment was removed because it depended on that rally"). **A11y:** `role="status"`; `Undo` is a button with a visible countdown only if time-limited. **Copy:** "Updated after your fix"; "Thanks. Affected findings have updated." **Used by:** Recap, Deep dive, Progress (when a past match changes a trend: "This changes your Week 6 comparison").

### 6.3 `RallyRow` / `RallyDetailPanel`

`RallyRow` keeps the existing row grid (time button, label, chip, shot count text, expand chevron) with these changes: label "Rally 14" (warm-up → "Not counted — warm-up", with "Count it" reinstatement); winner chip text `"You won this one"` / `"{name} won"` colour-neutral; `CheckChip` replaces `BandChip`; shot pills show **Preview** shot names only when `depth≠quick`. `RallyDetailPanel` is the expanded body: shot chips (`seekFrame(frame-10)` retained), "Why it ended" in words (`OUTCOME_LABEL`), `FixSheet` launch, "Watch this" `EvidenceChip`. Props: `r: RallyView; session; depth; me`. A11y: row is `<li>` with an `aria-expanded` disclosure (existing). Tests: reinstate warm-up; winner chip never red/green.

---

## 7. Onboarding components (deep treatment where marked)

### 7.1 `PickYourself` (deep)

**Purpose.** D8: *"Which one is you?"* The engine only knows tracks (`P1` near side at start, `P2` far side); the player is a person. A single tap maps the track to their identity for every later sentence.

**Anatomy**

```
 Which one is you?
 ┌──────────────────────────────────────────────┐
 │  frame from the video (paused, with a rally) │
 │      ◯ ← P2 box (labelled "Far side")        │
 │                                              │
 │      ◯ ← P1 box (labelled "Near side")       │
 └──────────────────────────────────────────────┘
 Tap yourself.            [ I'm not in this video ]   [ Not sure ]
```

**Props**

```ts
interface PickYourselfProps {
  matchId: string;
  frame: number;                           // a mid-rally frame where both are visible (server picks; fallback = a third of the way in)
  boxes: { player: PlayerId; xywh: [number, number, number, number]; label: string }[];   // from tracks at `frame`
  onPick(me: PlayerId | "none" | "unsure"): void;
  nicknameDefault?: string;
}
```

**Behaviour.** The still comes from the HLS proxy via `useHls` (seek to `(frame+0.5)/fps`, as `CalibratePage` does) or a sprite cell. Player boxes come from `useSession().tracks.player(pid, frame)`. Selecting one dims the other, shows "You — {nickname}" and a "That's not me" undo. After the pick, ask the opponent label as optional free text (existing `player1`/`player2` upload fields).

**States.** Both visible · only one visible (offer another frame: "Show another moment") · none detected (**UnsupportedFootageState** or skip) · three or more people (doubles/bystanders: *Not yet*; banner "This looks like doubles. We can follow singles for now.") · loading · error.

**A11y.** The frame is `aria-hidden`; the real controls are two large radio buttons labelled "The player on the near side (bottom of the picture)" and "…far side (top)"; tapping the box is a shortcut. Keyboard: arrow keys move between options. **Copy:** "Which one is you?" / "Tap yourself." / "I'm not in this video". **Reuse:** frame display from `CalibratePage`, `usePlayback.seekFrame`, track buffer. **Tests:** radio fallback; mapping persisted in `me`.

### 7.2 `PlaceYourCourt` (deep)

**Purpose.** Replace a four-click developer tool with a guided, mostly automatic step; manual placement is the exception (D11 spirit; file 00 §2.4).

**Flow and states**

| Step | UI | Data | Success |
|---|---|---|---|
| 1 Detecting | spinner, "Finding the court lines…" (≈ seconds) | `GET /calibration/proposal` and `POST /calibration/auto` (existing) | proposal found |
| 2 Confirm | frame with the court drawn; **"Does this match your court?"** [Yes, that's it] [Adjust] | `calibration.quality.precision` → words ("Good fit") | one tap |
| 3 Adjust (only on failure/“Adjust”) | the existing 4 required corner handles + optional 6 points with loupe (`LOUPE=132`, `ZOOM=3`), undo history, `fitHomography`, `reprojectionError` | `POST /calibration` | fit error small |
| 4 Not found | `UnsupportedFootageState`-like block: "We couldn't find the court lines in this video." + camera tips + "Place it yourself" | — | manual or re-record |

**Props**

```ts
interface PlaceYourCourtProps {
  matchId: string;
  segment?: number;                      // existing multi-segment proposals
  mode: "wizard" | "settings";           // wizard inside New match; settings from the recap ("Court: auto")
  onDone(): void;
}
```

**Rules.** Never display `reprojection_error_px`. Wizard uses a mobile-friendly **drag-handles-on-corners** with the loupe; points order and labels are kept (`near_left … far_short_right`) but renamed in plain words ("Bottom-left corner of the court"). Camera moves: if `mode="lines"` say "We follow the lines through the video" (existing header chip "Court: auto"). Broadcast uploads with several cameras: "Other cameras aren't followed" (`scene`). **A11y:** corner handles are focusable with arrow-key nudging (1 px, Shift = 10 px) and live-region coordinates; the verbal description of what to click is on-screen text. **Reuse:** all of `CalibratePage.tsx` (loupe, `ORDER`, history, `useHls`); `COURT_LINES`, `project()` from `lib/court`. **Tests:** auto-success path needs zero handle interaction; keyboard nudge; manual path posts `calibration`.

### 7.3 `ConsentToggle` / `ConsentLedger` / `ConsentCards` (deep)

**Purpose.** Five distinct purpose decisions: four product permissions plus a separate model-improvement opt-in (D15). Never bundled, never pre-ticked beyond what is needed to run the requested analysis.

| Permission id | Plain label | Default | Why it exists |
|---|---|---|---|
| `analyse` | "Analyse this video" | **on at upload** (required to proceed; can decline = cancel) | essential service |
| `store` | "Keep the video so I can watch it again" | on | playback needs it; off = delete after analysis only after G-05 implements and verifies media deletion |
| `history` | "Add the results to my history" | **off** on first use | progress/journey; a prior explicit choice may pre-fill later uploads |
| `share` | "Let me share chosen moments with people I pick" | **off** | per-clip approval still required |
| `train` | "Help improve the product with this video" | **off, separate** | never bundled |

**`ConsentToggle` props**

```ts
interface ConsentToggleProps {
  id: "analyse" | "store" | "history" | "share" | "train";
  label: string; description: string;
  value: boolean; onChange(v: boolean): void;
  consequence?: string;                  // what turning it off changes, shown on change
  required?: boolean;
  lastChangedAt?: string;
}
```

Visual: the existing `Toggle` in `VideoStage.tsx` (`role="switch"`, `aria-checked`) extracted to `components/ui/Switch.tsx`; 44 px row; the label is always visible text. **`ConsentCards`** = the five toggles as cards in the upload flow, *at the moment of upload*, with "Private by default. Sharing is always your choice." and a "Read details" link. **`ConsentLedger`** (Settings) = table of permission · status · date · "Change" + history, plus bystander note ("People who appear in your video: you decide what is shared") and links to export/delete.

**States.** Normal · saving · failed (revert + `ErrorNote`) · revoked-with-consequence ("Sharing is now off. Existing links will stop working." — only if the backend does so; else "Demo action") · demo mode ("Demo — nothing is stored").

**A11y.** Each is a switch with a described-by consequence; changes announced via `role="status"`. **Copy:** file 09 §11. **Tests:** training toggle can never be changed by another toggle; defaults; ledger renders dates.

### 7.4 Compact onboarding specs

- **`ValueHero`** — Headline "Your game. Your moments. Your progress." + 20-second `SampleRecapEmbed`, primary "See an example", secondary "Analyse my match". Props: `onExample, onStart`. States: reduced-motion (no autoplay), small screen. Never an "AI coach" claim. Used by Landing.
- **`SampleRecapEmbed`** — renders the real `RecapHeader`, `HeroMoment`, `FactTrio`, `InsightCard` with the Alex fixture; persistent "Sample" `DemoBanner`; every control works locally, none persist. Props: `fixtureId: "alex-singles"`, `depth?`. Tests: renders without network.
- **`PurposePicker`** — up to two of six `Purpose` chips, "Not sure" allowed, skippable; copy "What would be useful today? You can change this any time." Props: `value: Purpose[]; max=2; onChange; onSkip`. A11y: checkbox group; `aria-describedby` for the limit. Skipping applies preset `relax`.
- **`PresetCards`** — four cards (Relax/Explore/Improve/Compete) each with "Best for…" and a one-line *example of what you'll see* (show, don't describe). Props: `value: Preset; onChange`. Compete is selectable, not recommended first. A11y: radio group.
- **`RecordGuide`** — 3-step visual guide (where to put the phone, framing, light) with a diagram of the court and the camera positions the engine supports; includes the consent reminder for the people on court. Props: `venue?: "indoor" | "outdoor" | "unknown"`. Tests: content from a typed `supportedViews` list so the page and the validator never disagree.
- **`FramingChecklist`** — four checks (court lines visible, both players in frame, steady camera, even light) as plain checkboxes the player ticks, plus auto-checks from the test clip; no scoring. Props: `autoResults?: Record<CheckId, "ok" | "warn" | "fail">`.
- **`TestClipCheck`** — upload ≤ 10 s, analyse, return a `SuitabilityResult`. Props: `onResult`. States: uploading, analysing (stages), result, cannot-test (offline). Needs backend G-11.
- **`SuitabilityResult`** — three outcomes with icon + word: **Suitable**, **Usable with limits** (lists exactly what will be unavailable, e.g. "Shot names"), **Not supported** (why + fix + "keep clips only"). Props: `outcome, limits: string[], fixes: { label; detail }[]`. "Try again" is never the only action.
- **`WhoIsWho`** — doubles roster (two per side), **Not yet**; spec reserved so `PickYourself` composes it later.
- **`UploadProgress`** — evolves `UploadCard`: drop zone (keyboard-activatable `button`), file name + size, `maxMb` check (existing message rephrased), resumable (needs G-12; until then "If your connection drops, start again — nothing is lost on our side" is **not** claimed), `Meter` progress with real bytes, cancel. Title/player fields move *after* upload (`PickYourself`) — they are optional. A11y: progress is `role="progressbar"` (existing `Meter`).
- **`FirstValueReveal`** — the moment between "Ready" and the Recap: 1 s calm transition that lands on `HeroMoment`; "Skip" always present; reduced-motion = instant. Never confetti.

### 7.5 `ProcessingStages` (deep)

**Purpose.** Honest progress (Blueprint §7.5; v1 rule: never fake percentages). Maps real engine states to named stages and lets the player watch early.

**Real signals available** (`useSession`/`Session`): `status` (`created | ingesting | ready_to_play | analysing | analysed | failed`), `ingestProgress` (0–1 from `ingest` socket msg), `frontier_frame / media.n_frames`, `status.rate_x` (× real time), `status.degraded[]`, `scene`/`calibration` events.

**Anatomy**

```
 Getting your match ready                       Keep this tab open unless the server confirms background processing (G-ONB-9).
 ✓ Video received
 ✓ Video prepared                  (ingesting 100 %)
 ● Following the players and shuttle   61 %  · about 4 min left   (frontier / n_frames; ETA from rate_x only if rate_x is stable)
 ○ Finding rallies and moments
 ○ Ready
 ────────────────────────────────────────────────
 Ready so far:  ▶ Watch the video   ·  12 rallies found
 ◆ Part of this match is a different camera angle — we skip those bits.     (degraded / scene)
```

**Props**

```ts
interface ProcessingStagesProps {
  status: SessionStatus;
  ingestProgress: number | null;
  frontier: number; total: number;       // frames
  rateX?: number;
  degraded?: { stage: string; reason: string }[];
  partial?: { rallies: number; canWatch: boolean; momentsReady: boolean };
  leavable: boolean;                     // true only if the server keeps processing (it does: runner is server-side)
  onWatchNow?: () => void;
}
```

**Stage table**

| Stage label | Active when | Progress source | Partial result offered |
|---|---|---|---|
| Video received | `created` | upload bytes (`UploadProgress`) | — |
| Video prepared | `ingesting` | `ingestProgress` | — |
| Ready to watch | `ready_to_play` | — | **Watch while it works** (existing progressive HLS) |
| Following the players and shuttle | `analysing` | `frontier/total` (real) | rallies found so far |
| Finding rallies and moments | `analysing` (final 10 %) | same | Moments appear as rallies finalise (`SEMANTIC_LEAD_S`) |
| Ready | `analysed` | — | `FirstValueReveal` |
| Stopped | `failed` | `status_detail` | `FailedState` |

**Rules.** A percentage appears only for ingest and frontier (both measured). ETA is shown only when `rate_x` has been stable ≥ 20 s ("about 4 minutes"); otherwise no ETA. "Leave and come back" copy is shown only when notifications are on or the user can find the match in Matches; never invent urgency. **A11y:** `role="list"` of stages with `aria-current="step"`; live region announces stage changes (polite, throttled to 10 s). **Reuse:** `Meter`, `STATUS_LABEL`, the `Header` status pill, `LibraryPage` polling (`refetchInterval` 3000). **Tests:** no percent for non-measured stages; ETA gating; degraded notes render.

### 7.6 `FactTrio`

Three facts, no more (v1 recap rule). Props: `facts: { id; label; value: Measured<string>; sub?: string; evidence: EvidenceRef[]; metricId }[]` (length 3 enforced by type tuple). Typical facts: "{n} rallies followed", "Longest rally: {k} shots", "{m} minutes of play". Each tile: label, one hero number, sub-line, `EvidenceChip variant="inline"`, `MetricPopover`. One hero number per view is a visual rule: the trio uses a **single** large numeral (the first) and normal-size for the rest (file 08 §5). Absent facts are dropped, not zeroed. Tests: tuple length; drops `Absent`.

---

## 8. Analysis components (deep for `CourtMap`, `RallyTimeline`)

### 8.1 `CourtMap`

**Purpose.** All top-down court drawing: live minimap, heatmaps, placement, a "where did this rally travel" thumbnail, and the non-interactive court in demos. Evolves `CourtView` (`geometry.ts`: `map/unmap/drawCourt`, `MARGIN_M`, `prepareCanvas`), `HeatCanvas` (`HeatmapsTab.tsx`) and `CourtMinimap`.

**Orientation (change from today).** Today `CourtView` lays the court **horizontally** (near end left, far end right). Amateur product rule (file 00 §8 + Blueprint §8.8): **near side at the bottom, fixed everywhere.** `CourtView` gains `orientation: "vertical" | "horizontal"` (default `"vertical"`) and swaps the axes inside `map/unmap`; `drawCourt`, heat cells and arrows use `map` already, so only the transform and the aspect ratio change. The live minimap beside the video (desktop Deep dive aside) renders vertical at ~200 px wide. The horizontal option stays only for wide analyst layouts inside Advanced, labelled.

**Anatomy**

```
        far end (opponent side)
   ┌─────────────────────────┐   legend (always):
   │  ░░ ░░ ░░  heat cells   │   ● Your position   (what each mark means)
   │ ─────────────────────── │
   │          NET            │   Showing: Where you stood while the shuttle was in play
   │ ─────────────────────── │   Based on 31 rallies · Court fit: good   [Preview]
   │  ▒▒ ▒▒ ▒▒               │   [Table view] [Text summary]
   └─────────────────────────┘
        near end (your side)
```

**Props**

```ts
interface CourtMapProps {
  layer: "presence" | "movement" | "origin" | "landing" | "targeting" | "rally_path" | "live";
  me: PlayerId | null;
  players?: PlayerId[];                         // default [me]; compare variant draws both
  variant?: "you" | "compare";                  // compare uses P1/P2 hues (Deep dive only)
  data?: Heatmap | RallyPath;                   // Heatmap type from lib/types (cell_m, origin_m, shape, values)
  width: number;                                // CSS px; height derives from orientation
  interactive?: boolean;                        // hover/tap cells → MetricPopover-like tip; selectable cells open EvidenceChip
  summary: string;                              // text summary (R8) — required prop
  caption: string;                              // "Where you stood while the shuttle was in play"
  coverage?: { followed: number; total: number };
  capability: Capability;                       // heatmaps are Preview
}
```

**Layers (what the mark means — the legend says exactly this)**

| Layer | Meaning | Source | Capability |
|---|---|---|---|
| `presence` | Where you stood while the shuttle was in play | `HeatmapSet.presence` (sampled every `fps//5`) | Preview |
| `movement` | Where you moved most (path density) | `add_path` | Preview (**no metres** shown; D10/§7) |
| `origin` | Where you hit from | `hitter_court_xy` | Preview |
| `landing` | Where the opponent played your shot back from (today: the receiver's feet — **not** the true landing point) | `landing_court_xy` | Preview — legend says so; true landing is ROADMAP #12 |
| `targeting` | Areas of the opponent's court you aimed at | same field | Preview |
| `rally_path` | The route of one rally, hitter to hitter | strokes `hitter_court_xy` | Preview |
| `live` | Frame-synced dots with trail (existing minimap) | `tracks.playerCourtTrail` | Available only while calibration is good |

**Rendering rules** (colour values in file 08 §11): sequential single-hue ramp in `--you` (others: `--other`; compare: P1/P2), `globalAlpha = 0.12 + 0.78·sqrt(v)` (existing), cells `≤ 0.02` skipped, court lines drawn on top so heat never hides them (existing two-pass `drawCourt`), net stroke 2 px. Cells with fewer than the minimum sample are **hatched**, not empty. Zone overlay (3 depth × 3 width per half, ontology `court_zones`) selectable as "Show areas": front/mid/rear × left/centre/right with counts.

**States**

| State | Render |
|---|---|
| Not calibrated | `EmptyState`: "We need to find your court first." + `PlaceYourCourt` link (replaces "Heatmaps need the court") |
| Calibrated, few samples (< threshold) | hatched map + `NotEnoughToSay too_few` |
| Low fit quality | map shown dimmed with `LowCoverageState` note; metric text suppressed |
| Preview | `PreviewTag` + legend text "Estimated from video" |
| Loading | skeleton court (lines only) |
| Error | `ErrorNote` |
| Reduced motion | `live` layer draws dots without trails |

**Behaviour.** Hover/tap shows "{x}% of your busiest area" (existing string rephrased to "Busier than most of the court" in Quick). Selecting a cell opens `EvidenceChip` for rallies with ≥ 1 sample in the cell (needs an index; optional P2). Keyboard: the canvas is `role="img"` with `aria-label={caption}`; the real controls are **Table view** (a 3×3 grid `<table>` with counts) and the **text summary**.

**A11y.** Never colour-only: ramp lightness varies monotonically and zones are labelled; legend always visible (no hover); table alternative; 3 px focus ring around the map region.

**Reuse.** `CourtView`, `prepareCanvas`, `HeatCanvas` draw loop, `CourtMinimap.drawShots/arrow`, `frameClock.subscribe` (live layer only; static layers do not subscribe).

**Used by.** Recap *My game* (one map), Deep dive Court, Progress (small multiples), Journey cards, shared pages.

**Tests.** `map/unmap` round trip in both orientations; hatched when `total < min`; summary prop required (TS); a11y table equals canvas totals.

### 8.2 `HeatmapKindTabs`

The existing five kinds (`presence, movement, origin, landing, targeting`) become five plain-language buttons: "Where I stood", "Where I moved", "Where I hit from", "Where my shots came back from", "Where I aimed". Quick shows **only "Where I stood"**; Guided adds "Where I hit from"; Advanced all five. Props: `value, onChange, depth`. `aria-pressed` (existing pattern). Hint sentence under tabs reuses the `KINDS[].hint` strings rewritten in file 09.

### 8.3 `RallyTimeline`

**Purpose.** Replay the shape of a match as a strip of rallies; jump to any rally. Evolves `Timeline.tsx` (`Overview` SVG with rally rects, game lines, highlight dots, analysed-so-far strip, hover sprite tooltip, slider semantics; `Detail` canvas 60 s two-lane shot view).

**Anatomy (Guided)**

```
 ▮▮ ▮▮▮ ▮▮ ▮ ▮▮▮▮ ▮▮ ▮▮ ▮▮▮ ▮ ▮▮ ▮▮▮      ← one mark per rally, width ∝ duration
  ·       ●          ●                   ← ● = a Moment; ring = yours
  ━━━━━━━━━━━●━━━━━━━━━━━━━━━━━━━━━━━━   playhead
  Rally 14 · 12 shots · 12:42                   (hover/focus tooltip with sprite thumbnail)
 [ Show shots lane ]  (Advanced)
```

**Props**

```ts
interface RallyTimelineProps {
  matchId: string;
  me: PlayerId | null;
  depth: Depth;
  marks: "neutral" | "winner";              // winner colouring only in advanced
  highlight?: { rallyIds: string[] };       // moments ringed
  showShotLane?: boolean;                   // the existing Detail canvas (Advanced)
  onSeek(frame: number): void;
}
```

**Changes from today**

| Today | Amateur rule |
|---|---|
| Mark colour = rally winner (`PLAYER_HEX`) and fill/opacity/dash by `band` | Neutral ink marks; certainty via `CheckChip` shapes in the tooltip; **winner colouring only in Advanced** (D6); marks for rallies *you* took part in unchanged (all rallies in singles) |
| `analysed` strip in `--signal` green | stays the "followed so far" strip while processing; becomes `CoverageBar` when done |
| `role="slider"` with `aria-valuetext=clock` | keep (good); add `aria-describedby` with "Rally 14 of 36" |
| Hover tooltip "Warm-up (not scored)" | "Not counted — warm-up" |
| Lane legend `shot/smash/jump smash` | Advanced only; shots are Preview |

**States.** Processing (frontier shading), partial (hatched region where `scene` ≠ main), empty ("Rallies appear as soon as they finish" → `EmptyState`), reduced motion (no playhead easing). **A11y:** keyboard ←/→ ±5 s (existing), `[`/`]` rally jump, visible focus; the strip is `aria-hidden` visuals under a slider; a **Rally list** (`RallyRow`s) is the accessible equivalent and is always one tap away. **Reuse:** the whole file; `useWidth` hook; `useSprite`/`spriteStyle` tooltip; `frameClock.subscribe` for the playhead (no React re-render per frame — keep). **Tests:** mark geometry; neutral by default; winner colour only when `marks="winner"`.

### 8.4 Compact analysis specs

- **`ShotMix`** (from `StrokeMix`): per-shot-type bars with counts. Amateur default is **"Shots you played"** (single colour `--you`), not P1/P2 pairs; opponent bars appear in `variant="compare"`. Always **Preview**; includes "Shot names can be wrong — tap a rally to check". Unknown shots are excluded and counted in a footnote ("12 shots we couldn't name"). Table view required.
- **`ShotRepertoireGrid`:** the 12-stroke ontology as a grid of tiles: *Spotted* (first date + clip) vs *Not spotted yet* (neutral, never "locked"). "Spotted ≠ mastered" line permanently visible. No count-based "completion %". Tiles open `EvidenceChip`. Preview.
- **`ScoreStory`:** the score timeline as one sentence + a minimal strip ("You led most of game 1; it tightened after 14–14") using `score_timeline`; shown only for Match type when the entire score dependency set is Checked; hidden otherwise (D6, D12).
- **`MomentumChart`** (from `Momentum`): kept as is in Advanced; copy "Rally-by-rally lead". Hover tooltip kept; add text summary; P1/P2 colours allowed (compare). Not shown in Quick/Guided.
- **`HeadToHead`** (from `H2HRow` table): Advanced only; labelled "Side by side"; win-rate row removed; points/winners/errors rows keep their labels but "Errors (out)" → "Shots that went out", "Errors (net)" → "Shots into the net"; colour pair P1/P2 allowed.
- **`CompareMatchesPicker`:** pick two *comparable* matches (same type, similar camera); incompatible choices are disabled with the reason ("Different camera angle — court positions aren't comparable"). Props: `matches: MatchSummary[]; value: [id,id]; onChange`. Uses `useComparable`.
- **`AskPanel`** (from `AskTab`): renamed "Ask about this match". Keeps grounded answers and `EvidenceChip variant="citation"`, `Bold` markup, provider-missing note (reworded: "Written answers need a language model on this server — you'll still get facts from your match."). Suggestions rewritten in file 09 (not "What should P1 change"). Never surfaces `provider`/`model` outside Advanced. Retains `[[ev:…]]`/`[[kb:…]]` parsing.
- **`ExportList`** (from `ExportTab`): "Take it with you": **Match story (PDF)**, **Rallies (spreadsheet)**, **Clip (video)** become Quick-visible only when G-05/G-28 export permissions and media handling are enforced; otherwise a technical-demo export remains in Advanced and is labelled. Event log and Summary JSON stay Advanced. Descriptions explain who appears and what cannot be recalled; downloads use `exportUrl` only after the gate passes. PDF content spec in Doc 06 §9.

---

## 9. Progress and identity (deep treatment)

### 9.1 `ProgressCard`, `TrendSmallMultiples`, `ComparabilityNote`

**Purpose.** Show change only when it can be believed (D7, Blueprint §7.11). A trend is a *claim*; it needs comparable matches, a sample, and honesty about noise.

**`ProgressCard` anatomy**

```
┌────────────────────────────────────────────┐
│ Longest rally in a match            [ⓘ]   │
│  14 shots      ← your personal best        │
│  Before: 11 shots (Sat 12 Oct)             │
│  Based on 4 matches like this one          │
│  ✓ Looks right      [▶ Watch this]         │
└────────────────────────────────────────────┘
```

Props: `{ claim: Claim; baseline?: { label: string; value: Measured<string>; matchId: string }; current: { value: Measured<string>; matchId: string }; comparable: ComparabilityResult }`. No up/down arrows coloured good/bad; the change is a sentence: "+3 shots since last time" with "Observed more often" language; a decrease reads neutrally ("A shorter longest rally this time") and is hidden from Home.

**`TrendSmallMultiples`** — one tiny chart per metric, each with the same x-axis (comparable matches, not calendar), points for **individual matches** with range bands, `n` per point, gaps (hatched) for missing, vertical break line when a model/metric version changes, annotations (new camera, break). No smoothing unless "rolling average over 3 matches" is stated; no gauge; no single "improvement score". Props: `series: { metricId; points: { matchId; date; value: Measured<number>; n: number; band?: [number, number] }[]; annotations?: Annotation[] }[]`. Needs ≥ 3 comparable points before drawing a line; with 2 it shows two dots and "Two matches isn't enough to call it a trend"; with 1 "Your first match is your starting point."

**`ComparabilityNote`** — one line beside any comparison: "Compared with 4 singles matches filmed from behind the baseline." or the reason it fails ("Not directly comparable: different camera angle"). Props: `result: { ok: boolean; reasons: ComparabilityReason[]; n: number }` with reasons from Doc 06 §6 (`format`, `camera`, `coverage`, `identity`, `definition_version`, `sample`). Always visible; never in a tooltip.

**States.** 0 matches (EmptyState "Your first match is your starting point") · 1 · 2 · ≥3 · non-comparable · after a long break (offers "Start a fresh baseline" — never a regression alert) · Preview metric.
**A11y.** Each chart has a text summary ("Longest rally: 9, 11, 14 shots across three matches") and a table toggle; points are focusable; color-independent markers (shape per series).
**Reuse.** The `Momentum` SVG pattern (axes, hover, tooltip) as the drawing base; `Meter` not used.
**Used by.** Progress, Home (≤ 3 cards), Recap (My game).
**Tests.** Thresholds (0/1/2/≥3); Absent drawn as gap; version-break line; no coloured arrows.

### 9.2 `PersonalBestCard` / `FirstBadge`

**Purpose.** Recognition tied to a **verified** event with a visible definition (D7). A "personal best" is relative to *your* comparable history; a "First" says *spotted*, not *mastered*.

**`PersonalBestCard` anatomy**

```
┌─────────────────────────────────────────┐
│ ★ Personal best                  (outline star, not a trophy)
│ Your longest rally in a match            │
│ 14 shots   · was 11 (12 Oct)             │
│ Counted as: shots in a rally we checked  │  ← definition one line
│ ✓ Checked   [▶ Watch this]   [♡ Save]    │
└─────────────────────────────────────────┘
```

Props: `{ metricId; value: string; previous?: string; definition: string; evidence: EvidenceRef; check: CheckState; date: string; comparableN: number }`. **Eligibility** (enforced in the component, `eligible()` pure function): `check ∈ {checked, looks_right}` **and** comparable history sample ≥ the metric minimum **and** the metric's capability is `available` or `preview` with the label shown. Otherwise returns `null` (never "almost a record").
**One restrained celebration (file 08 §9.3):** a 600 ms ring draw on the star, only the first time the card enters view for a **Checked** record, skippable and off under reduced motion. No confetti, no sound, no auto-escalated next target.

**`FirstBadge`** — anatomy: small pill `◇ First · Cross-court net shot` with date; opens an `EvidenceChip`. Props: `{ strokeId: string; firstSeen: string; evidence: EvidenceRef; check: CheckState }`. Copy: "Spotted for the first time", never "Unlocked/Earned". Shots are **Preview** (classifier) → tag shown; if `check = worth_a_look` the pill reads "Maybe a first — take a look" and is excluded from Journey until Checked.

**States.** Eligible · pending (waiting for Check) · retracted after a fix ("This record changed after your fix" via `ChangeSummaryBanner`) · demo.
**A11y.** The star is decorative; the heading carries "Personal best". Animation respects reduced motion.
**Tests.** `eligible()` truth table; retraction path; no trophy glyphs in DOM (lint).

### 9.3 `JourneyTimeline`

**Purpose.** "My story": a growing, private timeline of *verified* firsts, personal bests, saved Moments and chosen memories (user's Personal Highlight Identity). Never fabricates a milestone to fill space; no penalty for gaps.

**Anatomy**

```
 2026
 ● 12 Oct · First match saved                    ▶
 │
 ◇ 19 Oct · First: cross-court net shot          ▶   (Preview)
 │
 ★ 26 Oct · Personal best: 14-shot rally         ▶   (Checked)
 ┊  ← a gap of 3 weeks is drawn as a quiet break, no label like "inactive"
 ♡ 22 Nov · Saved: "The long one at the net"     ▶
```

Props: `{ entries: JourneyEntry[]; filter?: "all" | "mine" | "pairs"; onOpen(entry) }` where `JourneyEntry = { id; kind: "first_match" | "first" | "personal_best" | "saved" | "note" | "return" | "pair"; date; title; evidence?: EvidenceRef; check?: CheckState; visibility }`. `return` entries are *welcome-back* notes ("Back on court after 3 weeks — here's one match to start fresh"), only if the player wants participation milestones (setting). **States:** empty (EmptyState "Your story starts with your first match."), one entry, long (virtualised), pair entries need consent from both. **A11y:** `<ol>`, each entry a link with date text; the line/gap is decorative. **Tests:** gaps render no label; entries without evidence rejected except `note`/`return`.

### 9.4 `FocusCard` / `ReflectionPrompt` / `ChallengeCard`

**`FocusCard` anatomy (one active focus)**

```
┌───────────────────────────────────────────────┐
│ My focus                      [Edit] [Pause]  │
│ Reset the rally with a lift to the back corner│  ← editable process goal
│ I chose this because: “I keep getting rushed” │  ← the *user's* reason (editable)
│ Clips: [thumb][thumb]                         │
│ At the start of my next game I'll…  [plan]    │  ← cue-action sentence
│ What to notice: the shuttle going high & deep │  ← success cue (external focus, default)
│ Reviewed ● ─ Practised ○ ─ Shown in later play ○   ← status ladder (never skipped)
│ [Retire]  [Replace…]                           │
└───────────────────────────────────────────────┘
```

Props: `{ focus: { id; title; reason; clips: EvidenceRef[]; plan?: string; cue?: string; status: "reviewed"|"practised"|"shown"; createdFrom?: string /*claim id*/ }; onEdit; onPause; onRetire; onReplace }`. Rules: one active by default; status moves only by explicit user action (*practised*) or by evidence (*shown*, requires comparable later match) — **viewing never sets practised**; "Shown in later play" language is "appeared more often", never "mastered". Barrier check (COM-B) appears if a planned practice date passes: "What got in the way? [No court] [No partner] [No time] [Not a priority now]". **A11y:** inline edit fields have labels; status ladder is an ordered list with `aria-current`. **ReflectionPrompt:** single skippable question, variants `pre | post_feedback | post_practice`; props `{ variant; onSubmit(text|choice); onSkip }`; no guilt copy; at most once per match. **ChallengeCard:** `{ id; title; why; evidence: "needed"; difficulty: "easy"|"stretch"; state: "offered"|"accepted"|"done"|"dismissed" }`; always dismissible, no deadlines, no rewards beyond a `FirstBadge`/`PersonalBestCard`; challenges that depend on Not-yet capabilities are not offered. All **P2**.

---

## 10. Core-loop compact specs

- **`MatchCard`** (from `SessionCard`): `Thumb` poster (existing 35 % in), title, **type chip** (Match / Social game / Practice), date, duration `m:ss` (existing format), `MatchStatusChip`, Moments count ("3 moments"), *no score headline* (optional small "Score: 21–17" only for scored matches with Checked winners). Whole-card link via the existing `after:absolute after:inset-0` pattern. Delete moves into an overflow menu (`⋯`) that opens `DeleteConfirmDialog` (the current hover-only trash button fails touch/keyboard discovery — `opacity-0 group-hover:opacity-100`). Failed state shows `status_detail` rewritten in plain words. Props: `{ match: MatchSummary; demo?: boolean }`. Tests: card is one tab stop; overflow menu keyboard.
- **`MatchStatusChip`** (from the `STATUS_LABEL` span): words: Queued → "In the queue", Preparing video → "Getting ready", Ready to play → "Watchable now", Analysing → "Analysing", Analysed → "Ready", Failed → "Didn't work". Pulsing dot only for active states (`animate-pulse`, off under reduced motion); percent only from `frontier` (measured), shown on `md` size.
- **`RecapHeader`** (from `Header`): back/breadcrumb, title (editable inline), subtitle "You vs {opponent nickname}" (not "P1 vs P2"), date, `MatchStatusChip`, `DepthSwitcher`, `PurposeChips` ("Shown because you chose Keep the moments · Change · Reset · Show all" — mandatory, Blueprint §3.2), compact `CoverageBar`, overflow (Court settings, "Analyse again" (existing `reanalyse`), Share, Delete). Court chip "Court: auto" (existing logic: `calibration.mode`, `source`) moves into the overflow for Quick/Guided and stays visible in Advanced.
- **`StoryParagraph`:** 2–4 sentences of match story built from approved claims (templates in file 09 §3) with inline `EvidenceChip variant="inline"` after each factual clause. Props: `{ parts: { text: string; evidence?: EvidenceRef[]; claimId?: string }[] }`. Narration may be LLM-phrased **only** from the evidence packet; every digit must exist in a source claim (same validator idea as `bai_agents.validate`); on mismatch the paragraph falls back to the deterministic template. Never causal ("because") unless a claim of type `hypothesis` is explicitly labelled.
- **`PersonalNote`:** the player's own optional note on a match/moment (text, 280 chars, private). Props `{ value; onSave }`; empty state is a quiet "Add a note" link, never a nag.
- **`RecapFeedback`:** "Was this recap useful?" `Useful · Not useful · Report something` — small, dismissible, non-blocking (v1); stores locally in demo ("Demo — noted on this device").
- **`NextStepRow`:** up to three optional next steps as equal-weight links: **Keep this moment**, **Look at a pattern**, **Try something next**, **Done for now** — never forced; `Done for now` is always last and sets nothing. Also the Home "Resume" card: props `{ steps: { id; label; to; kind }[] }`.

---

## 11. Shell, navigation and onboarding-shell compact specs

- **`AppShell`** (evolve): wraps `<Outlet/>` with `SideNav|BottomBar`, `DemoBanner`, theme provider (`data-theme`), `Toaster` (a small custom toast: reuse `toast-in` keyframes), auth/`me` gating as today (`api.me`, `LoginPage` stays for operator mode). Remove the `Activity/System` link from the player nav (moves to `/admin/system`). Skip link "Skip to content" first in DOM.
- **`SideNav`** (≥ 1024 px): Home · Matches · Moments · Progress · Together (hidden until doubles/invites exist — D10) · Explore (hidden until challenges exist); active style from the existing `activeProps`; collapsible to icons (labels as tooltips + `aria-label`). `AddMatchButton` sits above the list.
- **`BottomBar`** (< 1024 px): Home · Matches · ＋ · Moments · Progress; labels always shown; 56 px high + safe-area inset; the ＋ is a raised 56 px button, not an icon-only unlabeled control (visible label "Add"). Hides on scroll-down only if the user has not focused a control (never when a dialog is open).
- **`AddMatchButton`:** `variant: "bar" | "side" | "inline"`; links to `/matches/new`; label "Add a match". One primary action per view rule: on `/matches/new` it disappears.
- **`PresetSwitcher`:** four-option segmented control in the avatar menu and first-run; changes `Purpose × Depth` per D3; shows what changes ("Relax: moments and a short recap"); never deletes data. A11y: radio group.
- **`PurposeChips`:** compact read-out of the match's purposes with `Change · Reset · Show all` (mandatory "Shown because…" line, Blueprint §3.2).
- **`DepthSwitcher`:** Quick · Guided · Advanced segmented control with one-line previews; changes density/language only (R7); keyboard arrow keys; announces "Showing more detail" via live region.
- **`DemoBanner`:** persistent, non-dismissible strip "Sample data — nothing here is a real match" shown on every sample/demo screen; also a "Demo" watermark chip on posters; demo actions confirm "Demo only — nothing saved/sent".
- **`AvatarMenu`:** nickname + initials avatar, Profile, Preferences (depth/preset/tone), Privacy, Notifications, Accessibility, Help, Sign out (only in operator mode), theme override (System/Light/Dark).
- **`Breadcrumb`:** `Matches › Saturday doubles › Deep dive › Court`; preserves filters/scroll via router `scrollRestoration` (already enabled) and search params.

---

### 11.1 `SharePreviewDialog` / `ShareAudiencePicker` (deep)

**Purpose.** Sharing is separate from analysis, storage and training (D15). The player always sees *exactly* what leaves, who gets it, for how long, and what cannot be taken back (Blueprint §8.12). Never a public link by default; never shares a funny/embarrassing moment without per-clip approval.

**Anatomy (Radix Dialog; full-height sheet on mobile)**

```
┌────────────────────────────────────────────────────┐
│ Share this moment                                ✕ │
│ 1 Who can see it?                                  │
│   (●) Only people I send the link to               │
│   ( ) A named person   [ Aditi ▾ ]   (Not yet)     │
│   ( ) Anyone with the link (needs extra OK)        │
│ 2 What's included                                  │
│   ┌ clip preview ┐  ☑ Clip   ☐ Score   ☐ Names     │
│   └──────────────┘  ☐ Court map   (analytics off)  │
│   People visible: you, Aditi (opponent) ⚠           │
│ 3 How long?   ( ) 7 days  (●) 30 days  ( ) No end  │
│   Downloads:  ☐ Allow download                      │
│ 4 Before you send                                   │
│   ☑ I have the OK of the people in this clip *      │
│   Once sent, a copy someone saves can't be recalled.│
│                  [ Cancel ]   [ Create private link ]│
└────────────────────────────────────────────────────┘
```

**Props**

```ts
interface SharePreviewDialogProps {
  open: boolean; onOpenChange(o: boolean): void;
  subject: { kind: "moment" | "match_story"; id: string; evidence: EvidenceRef; title: string };
  people: { id: string; label: string; role: "you" | "partner" | "opponent" | "bystander"; consent: "yes" | "no" | "unknown" }[];
  permissions: { share: boolean };       // from ConsentLedger
  isFunny?: boolean;                     // blooper/fun clip → requires explicit approval step
  onCreate(opts: ShareOptions): Promise<{ url: string; expiresAt: string | null } | { error: string }>;
}
interface ShareOptions { audience: "link" | "named" | "public"; include: { clip: boolean; score: boolean; names: boolean; analytics: boolean }; expiry: "7d" | "30d" | "never"; allowDownload: boolean; }
```

**Rules**

- Defaults: audience = private link; score off; names off (nicknames only); analytics off; expiry 30 days; download off. "Anyone with the link" and "No end" each need an extra confirm line.
- If `permissions.share = false` the dialog opens in a blocked state: "Sharing is off in your privacy settings. [Turn on sharing] [Keep private]" — it does **not** let the user proceed silently.
- If any visible person has `consent ∈ {no, unknown}` the checkbox is mandatory and the preview offers **"Blur other people"** (when the backend supports it, else "Share a version without faces — not available yet" disabled with reason). Funny clips add a step: "This one's a bit silly. Share it anyway?" with the clip replayed.
- Success shows the link, expiry, and "Stop sharing" control (revokes, `PermissionRevokedState` for recipients). Demo mode: "Demo only — no link was created."
- WhatsApp/other channels use the OS share sheet (`navigator.share`) with the same private link; no social network SDKs.

**States.** Editing · creating (busy) · created · failed (`ErrorNote`, selections kept) · blocked by consent · offline (queued? **no** — sharing needs the server; says so).
**A11y.** Radio/checkbox groups with fieldsets; the preview video has captions/description; focus returns to the Share button; result link is selectable text plus a Copy button (`aria-live` confirmation).
**Reuse.** Delete-dialog structure from `SessionCard`; `ClipPlayer` for the preview; `Switch`.
**Tests.** Default option set; blocked path; funny-clip extra step; never calls `onCreate` without consent when people are unknown.

### 11.2 Compact social, privacy and settings specs

- **`ShareAudiencePicker`** — the first block of the dialog as a standalone radio group (also used for "who can see my Moments" in settings). Props `{ value; onChange; namedPeople?: Person[]; publicAllowed: boolean }`.
- **`InviteLink`** (P2) — generates an expiring partner invite ("Aditi can see your shared rallies"), copy button, revoke, expiry text. Needs accounts (file 11). Hidden until then.
- **`PartnerCard`** (P2, **Not yet**) — nickname, number of shared matches, "Shared moments: 4" (only both-consented), permissions status, unlink. Never ranks partners; never shows a partner's private stats.
- **`PairMemoryCard`** (P2, **Not yet**) — a shared rally with *both* contributions described ("Both of you were in this rally"), with `EvidenceChip`; visible only if both users' `share` consent allows; no blame wording ever (file 09 §9).
- **`NotificationPrefs`** — per-trigger switches (analysis ready · coach comment · my own reminder · enough comparable matches to revisit a goal (separate opt-in)), quiet hours, digest, global pause. Defaults: *analysis ready* on only if the user chose a channel at upload; everything else off. No "come back" trigger exists in the list at all.
- **`DataExportRequest`** — Export (summary, clips, events) and **Delete** (account, one match, derived data) with honest limits ("Copies you already shared or downloaded stay with the people who have them. Backups are removed within 30 days." — numbers to be set by policy); status list with dates; demo = "Request simulated".
- **`DeleteConfirmDialog`** (from the delete dialog in `SessionCard`): names exactly what is removed (analysis, corrections, moments; **video** only if "Also delete the video"), what remains (shared copies), one danger button, one safe button labelled "Keep it" (existing). Requires typing nothing; two-step for account deletion. The existing text "The prepared video stays in the media cache" is reworded: "The video file is kept for 7 days in case you change your mind" **only** if true — otherwise omit.
- **`AccessibilityPrefs`** — reduced motion, text size (100/125/150 %), high contrast, caption default on, low-data video preview, "keep animations off" (also mirrors the OS setting). Preferences apply immediately.

---

## 12. State family (deep treatment)

All state components share one skeleton: **icon · one-sentence truth · optional detail · 1–2 actions · what is still usable**. "Try again" is never the only action when the *footage* is the problem (Blueprint §12).

```
 ┌──────────────────────────────────────────┐
 │  ◻ icon           Title (what happened)   │
 │  One sentence of why, in plain words.     │
 │  What you can still do:  [action] [action]│
 └──────────────────────────────────────────┘
```

```ts
interface StateProps {
  title: string; detail?: string;
  icon?: ReactNode;
  actions?: { label: string; onClick?: () => void; to?: string; variant?: "primary" | "secondary" | "ghost" }[];
  usable?: string;                       // "Your 12 moments are still here."
  tone?: "neutral" | "caution";          // caution = amber ◆, never red (red = system error only)
  compact?: boolean;                     // inline within a card
}
```

| Component | Trigger / data | Render | Actions | Role / a11y |
|---|---|---|---|---|
| `EmptyState` (from `Empty`) | no data yet | short explanation + **one** next step; illustration optional; never blames the user | the single next step | `role="status"` only if it appears after an action |
| `LoadingSkeleton` | route data pending | skeleton of the **real layout** (court lines, card grid), no fake numbers or percentages | none | `aria-busy="true"` on the region; `Spinner` (existing) only for inline mutations |
| `PartialAnalysisNote` | `status="analysing"` with partial data, or `degraded[]` | "Some results are ready. We're still checking the rest." + list of modules pending; each module's component shows its own skeleton | Watch now; Notify me (if enabled) | `role="status"` polite |
| `LowCoverageState` | followed/total < 60 % or court quality poor | "We could only follow part of this match." + what was lost ("shot names", "court map") + what remains | Place your court; Re-film tips; Keep moments only | metrics suppressed, not zeroed |
| `UnsupportedFootageState` | no court found / too few players / unsupported angle | why (angle, visibility, resolution) + **specific fix** + "keep clips only" path | Place your court yourself; See the recording guide; Keep the footage | never "Try again" alone |
| `FailedState` | `status="failed"` | "This didn't work" + cause in plain words (`status_detail` rewritten) + what was saved | Analyse again (`reanalyse`); Report; Keep video | `role="alert"` |
| `PermissionRevokedState` | link expired / consent revoked / not owner | who lost access and when | Ask for a new link; Go to Matches | no content leakage |
| `OfflineState` | `navigator.onLine=false` or WS closed (existing `connection !== "open"` pill) | "You're offline. Saved items still work." | Retry; Keep browsing | `role="status"` |

**Conflicts:** when several apply, priority is `PermissionRevoked > Unsupported > Failed > LowCoverage > Partial > Offline`. Only one **block** state per surface; secondary ones become inline notes.

**Copy** for each lives in file 09 §8; layouts here are final.

**Reuse.** `Banners`/`Banner` in `SessionPage.tsx`, `ErrorNote`, `Empty`, the "Reconnecting" pill, `STATUS_LABEL`.
**Tests.** Priority resolution table; each state has ≥ 1 action; none renders a red tone except `FailedState` icon (system error).

---

## 13. Implementation guidance (matched to this repo)

### 13.1 Folder layout (additions under `apps/web/src`)

```
components/
  ui/            Button, IconButton, Spinner, Meter, Field, Kbd, Switch (extracted Toggle), Sheet (Radix Dialog as bottom sheet), Tag
  trust/         CheckChip, EvidenceChip, CoverageBar, MetricPopover, PreviewTag, InsightCard, ReviewBanner, NotEnoughToSay, ChangeSummaryBanner
  states/        EmptyState, LoadingSkeleton, PartialAnalysisNote, FailedState, LowCoverageState, UnsupportedFootageState, PermissionRevokedState, OfflineState
  nav/           AppShell (moved), SideNav, BottomBar, AddMatchButton, AvatarMenu, Breadcrumb, PresetSwitcher, PurposeChips, DepthSwitcher
features/
  onboarding/    ValueHero, SampleRecapEmbed, PurposePicker, PresetCards, RecordGuide, FramingChecklist, TestClipCheck, SuitabilityResult, PickYourself, PlaceYourCourt (moved from calibrate/), ConsentCards, ProcessingStages, FirstValueReveal
  matches/       MatchCard, MatchStatusChip, UploadProgress, NewMatchFlow
  recap/         RecapHeader, HeroMoment, FactTrio, StoryParagraph, PersonalNote, RecapFeedback, NextStepRow
  moments/       MomentCard, MomentStrip, ClipDetail
  review/        FixSheet, review queue logic
  deep-dive/     RallyRow, RallyDetailPanel, ShotMix, ShotRepertoireGrid, ScoreStory, MomentumChart, HeadToHead, CompareMatchesPicker, AskPanel, ExportList
  court/         CourtMap, geometry.ts (+orientation), HeatmapKindTabs, CourtMinimap (live layer)
  player/        ClipPlayer (VideoStage evolved), overlay.ts, ScoreBug, StrokeToast, useHls
  timeline/      RallyTimeline
  progress/      ProgressCard, TrendSmallMultiples, ComparabilityNote, PersonalBestCard, FirstBadge, JourneyTimeline, FocusCard, ReflectionPrompt, ChallengeCard
  together/      PartnerCard, PairMemoryCard, InviteLink      (P2)
  share/         SharePreviewDialog, ShareAudiencePicker
  settings/      ConsentLedger, ConsentToggle, NotificationPrefs, AccessibilityPrefs, DataExportRequest, DeleteConfirmDialog
lib/
  trust.ts       (§3.1 types + checkStateOf)    capabilities.ts   metrics.ts    claims.ts (templates + validators)    comparable.ts
  demo/          fixtures (§13.6)
stores/
  prefs.ts       depth, preset, purposes, tone, me-per-match, dismissed items (persisted via localStorage with try/catch like `usePlayback.loadLayers`)
```

Existing files keep their paths until the recap routes land, then are moved with `git mv` so history survives. The `Session*` names remain internal; UI text says "match".

### 13.2 Radix and primitives

| Need | Use | Notes |
|---|---|---|
| Modal/sheet (FixSheet, SharePreview, DeleteConfirm, ClipPlayer on mobile) | `@radix-ui/react-dialog` | Mobile bottom sheet = Dialog content positioned `fixed inset-x-0 bottom-0` with drag handle optional; no new dependency |
| Popovers (MetricPopover, CheckChip, PreviewTag, layers menu) | `@radix-ui/react-popover` | Popover over Tooltip for anything with essential info (tap works) |
| Hover hints only | `@radix-ui/react-tooltip` | Never for essential info |
| Section tabs inside a screen | `@radix-ui/react-tabs` (existing) | **Deep dive sub-navigation uses router links** (deep-linkable), not Tabs |
| Switch | extracted `Toggle` (`role="switch"`) | `@radix-ui/react-switch` is not installed; do not add |
| Radio / checkbox groups | native inputs with `accent-color` token | as `RalliesTab` checkbox does |

### 13.3 Tailwind v4 tokens

Components never use raw hex. They use utility classes bound to `@theme` tokens (file 08 §3): `bg-surface`, `text-ink`, `text-muted`, `border-edge`, `text-you`, `bg-you/10`, `text-evidence`, `text-opportunity`, `bg-uncertain/10`… The old names (`mat`, `stand`, `seam`, `line`, `line-2`, `line-3`, `signal`, `p1`, `p2`) remain valid aliases during migration (file 08 §3.4) so existing code compiles unchanged. Theme switching is `data-theme="light|dark"` on `<html>`; **Deep dive video theatre forces `data-theme="dark"` on its subtree** (D13).

### 13.4 Data, state and performance rules

- **Server state:** TanStack Query with keys scoped by match and version counters, as today (`["analytics", id, analyticsVersion]`, `["highlights", id, player, v]`, `["heatmap", …]`). New keys: `["moments", userId]`, `["progress", userId, metricId]`, `["consent", userId]`, `["me", matchId]`. Use `placeholderData: (p) => p` (existing pattern) so charts don't flash when versions bump.
- **High-rate data stays out of React:** `frameClock` publishes the *presented* frame (via `requestVideoFrameCallback`); canvas components (`CourtMap live`, `RallyTimeline`) `frameClock.subscribe` and draw imperatively; React components read the **throttled** `usePlayback().frame` (~10 Hz). Do not call `useState` per frame.
- **Corrections** bump `analyticsVersion` (store counter). `ChangeSummaryBanner` diffs the previous and next analytics via a ref to the prior query result.
- **Preferences** live in a small Zustand slice persisted in `localStorage` with try/catch (mirror `usePlayback.loadLayers`); the server copy (when accounts exist, file 11) is the source of truth.
- **No chart library.** SVG/canvas, as in `Momentum`/`HeatCanvas`/`Timeline`. Keep bundle small; lazy-load `PlaceYourCourt` (already lazy as `CalibratePage`), Deep dive routes and `AskPanel`.
- **Lists > 60** items virtualise (CSS `content-visibility: auto` first; add a library only if profiling demands).

### 13.5 Accessibility plumbing

`useReducedMotion()` (reads `matchMedia`), `useLiveAnnounce()` (single polite live region in `AppShell`), `useFocusReturn()` helper where Radix does not. Every chart component takes a required `summary` string and exposes `Table view`. A dev-only check fails the test run if a component with `role="img"` lacks `aria-label`.

### 13.6 Fixtures and the dev gallery (Storybook-less)

- **Typed deterministic fixtures** in `lib/demo/`: the "Alex" scenario from the v1 spec — Match A (casual, completed, 9 rallies, 3 moments), Match B (singles, 14 rallies, 4 moments), Match C (partial: rallies ready, movement pending) — expressed as real `Session`, `BaiEvent[]`, `Analytics`, `Heatmap`, `Highlight` objects so **the same components render real and demo data** (no parallel "demo components"). Fixtures are generated by a script from the existing synthetic match generator (`sports/badminton/src/bai_badminton/testing/synth.py`) plus hand-set `Claim`s; seeded and committed.
- **Dev gallery route** `/dev/gallery` (included only when `import.meta.env.DEV`): renders every component × every state × both themes × three depths from fixtures, on one page with anchors. This replaces Storybook (no new tool), and is the target for visual-regression screenshots.
- **Demo mode** wraps queries with a fixture adapter (`api` object swap) and mounts `DemoBanner`; demo actions say "Demo only" (v1 §06).

### 13.7 Testing strategy

| Layer | Tool | What |
|---|---|---|
| Pure logic | Vitest (existing `derive.test.ts`, `homography.test.ts`) | `checkStateOf`, `eligible()` for records, `useComparable`, claim withholding, change-diff, copy lint (file 09 §14), `CourtView` map/unmap both orientations, ETA gating |
| Components | Vitest + Testing Library (existing `components.test.tsx`, `src/test/setup.ts`, `fixtures.ts`) | roles/names, keyboard, state tables, "no score in HeroMoment", "no rank in MomentCard", consent independence |
| Accessibility | optional `vitest-axe` (dev dependency, P1) + manual SR pass | every component × state in the gallery |
| Flows | Playwright (existing `smoke.spec.ts`, `e2e/server.py` seeded server) | onboarding → sample → upload (small fixture video) → pick yourself → place court (auto) → consent → processing → recap → open moment → fix → change summary; mobile viewport 360 and desktop 1440 |
| Visual | Playwright screenshots of `/dev/gallery` per theme | review diffs, not pixel-perfect gating at first |
| Contract | Vitest over `lib/metrics.ts` | every `metricId` used has a definition, capability and denominator rule |

**Definition of done for a component:** states table implemented and in the gallery · keyboard path · SR name · both themes · three depths · copy lint passes · test file present · uses tokens only · no engine words in rendered text outside Advanced.

---

## 14. Addendum — components introduced by the screen specs (05a–c)

The screen specs needed 32 components that file 00 §6 did not list. They are canonical from here on (file 00 §6 is extended by this section). They obey the universal rules R1–R9 at the top of this file. **Pri** as in §1. *Evolve* names existing code.

### 14.1 Core-loop additions (05a)

| Component | Purpose | Key props | Behaviour and states | A11y / copy | Evolve / new | Used by | Pri |
|---|---|---|---|---|---|---|---|
| `EntryChoice` | Gate on opening a recap: **Quick recap · Deep review · Review later** (R5) | `onChoose(choice)`, `remember?: boolean` | Shown on first open of a ready match independent of score or outcome; identical wording and layout for every result ("How would you like to look at this?"). *Review later* parks the match on Home with no nag. Never shows the score | Radio-card group, arrow keys; no result-dependent colour or confetti | New | Recap | P1 |
| `MatchTypePicker` | Choose **Match · Social game · Practice** (D12) | `value`, `onChange`, `disabledTypes[]` | Each card says what you will and will not get ("Social game: rallies and Moments, no score"). Until G-04 ships, Social/Practice are disabled on real uploads and may be explored only with labelled fixtures | Radio group; descriptions linked by `aria-describedby` | New | New match | P0 |
| `LensChips` | Filter Moments by lens (Longest · Saved it · Net duel · Variety · Close finish · First · Personal best · Fun · Partner) | `lenses`, `active[]`, `counts` | Multi-select; lenses with 0 items are hidden, not greyed; "Partner" absent until doubles (Not yet) | `aria-pressed`; counts in the accessible name | New | Moments, Clip detail | P0 |
| `ScoreChip` | The scoreline as **context** (D6): small, neutral, never a headline | `games: [number, number][]`, `check: CheckState`, `shown: boolean` | Neutral colours for both sides (no red/green); shown only for scored Match when the whole score dependency set is `checked`; otherwise show a review prompt without a numeric score. Hidden for Social/Practice | Text such as "Game 1: 21–17"; no colour-only encoding | Evolve `ScoreBug` styling (broadcast bug becomes a quiet chip) | Recap header, MatchCard | P0 |
| `FilterBar` | Matches / Moments filters (type, date, status, lens, player) | `facets`, `value`, `onChange`, `activeCount` | Desktop inline chips with active count and Clear; syncs with URL query (file 04 §6) | Visible "n filters active" text; Clear is a button | New | Matches, Moments | P0 |
| `FilterSheet` | Mobile bottom-sheet version of `FilterBar` | same as `FilterBar` | Radix Dialog as bottom sheet; Apply/Reset; focus returns to the trigger | Focus trap; Escape closes | New (Radix `dialog`) | Matches, Moments (mobile) | P0 |
| `FavouriteButton` | Save a Moment privately | `momentId`, `value`, `onChange` | Optimistic toggle with a 5-second undo toast; **saving never changes visibility** (copy: "Saved to your Moments. Only you can see it.") | `aria-pressed`, label "Save this Moment" | New | MomentCard, Clip detail | P0 |
| `WhyChosenPanel` | "How this Moment was picked" (R10, D16) | `lens`, `reasons: {label, weight?}[]`, `evidence`, `onSwap?` | Plain-language reasons from `Highlight.reasons` (never the 0–10 score below Advanced; D17); offers *Swap for another* and *Fix this*; Advanced adds the reasons breakdown | Collapsible disclosure; reasons as a list | New (reads `Highlight.reasons`) | Clip detail, HeroMoment | P0 |

### 14.2 Analysis and review additions (05b)

| Component | Purpose | Key props | Behaviour and states | A11y / copy | Evolve / new | Used by | Pri |
|---|---|---|---|---|---|---|---|
| `DeepDiveShell` | Layout and context for the per-match workspace: sticky video left, sub-view right; carries `?f=` | `matchId`, `children` | Dark theatre surfaces (D13); desktop two-column, mobile single column with sticky mini-player; remembers last sub-view; "Back to recap" always present | Landmarks `main` + `complementary`; skip-to-video link | Evolve the `SessionView` layout in `SessionPage.tsx` | Deep dive | P0 |
| `SubNav` | Story · Rallies · Shots · Court · Compare · Ask | `items`, `active` | Replaces the six tabs (Stats/Heatmaps/Highlights/Rallies/Ask/Export); Compare hidden when fewer than 2 comparable matches; Export moves to the match menu | Radix `tabs` semantics kept (`role=tablist`) | Evolve the `Tabs.Root` in `SessionPage.tsx` | Deep dive | P0 |
| `RallyFilterBar` | Filters for the rally explorer: game, who won, length, shot type, "needs a look" | `value`, `onChange` | Keeps the existing "Only rallies that need a look" toggle; Advanced adds score state and serve/receive; counts update live | Labelled controls; result count announced politely | Evolve the checkbox in `RalliesTab` | Rallies | P0 |
| `ShotSequenceTable` | Shows the **sequence before the ending** (Blueprint §7.9: not only the last shot) | `shots[]`, `me`, `onSeek` | Row per shot with player, shot name (plain-language group, G-24) and time; each row seeks; **Preview** tag on shot names; unknown shots shown as "Shot" | Real `<table>`; row buttons labelled "Jump to shot 3" | Evolve the shot chips in `RallyRow` | RallyDetailPanel, Shots | P1 |
| `ZoneTable` | Accessible table twin of a `CourtMap` (every chart has one, R8) | `zones[]`, `unit`, `n` | 3×3 zone grid as rows ("Front-left … Rear-right"), share of samples with `n`; null renders "not measured", never 0 | Table with caption and scope | New | Court | P0 |
| `QualityPanel` | Compact "What we could see" drawer: coverage, court fit, scene, degraded stages, model versions (Advanced) | `coverage`, `court`, `degraded[]`, `versions?` | Collapsed by default; one tap from any screen; plain words (Great / Good / Rough fit), never a percentage | Disclosure; text summary first | New (wraps `CoverageBar`, `CourtFitBadge`) | Recap, Deep dive | P0 |
| `EventTable` | Advanced workspace table with filters and export | `events[]`, `columns`, `onOpenEvidence` | Layout mode `?view=table`; every row has **Watch this**; shows status and check state; sortable; virtualised past ~100 rows (§13.4) | Sortable headers with `aria-sort`; keyboard row navigation | New; data from `GET …/events` | Deep dive (Advanced) | P1 |
| `FixQueue` | Review & fix list, ordered by what the recap will show (D11) | `items[]`, `onOpen` | Top 3 items first ("Is this the rally you remember?"); badge shows open count; completes to a calm "Nothing left to check" | List with status text; focus moves to the next item after a fix | New (wraps `FixSheet`) | Review & fix, Recap | P0 |
| `CourtFitBadge` | Plain-language court-fit status | `fit: "great" \| "good" \| "rough" \| "none"`, `mode` | Great/Good/Rough/None from `calibration.quality.precision` and `mode` (`lines`/`camera`/`static`); *Rough/None* offers **Place your court**; explains what it unlocks | Icon + word + shape; tooltip explains | Evolve the header "Court: auto" chip in `SessionPage` | Deep dive, Court, Recap | P0 |
| `AnswerFeedback` | Thumbs and "This is wrong" under each Coach-chat answer | `answerId`, `grounded` | Sends feedback; `grounded: false` answers show "Some statements couldn't be linked to match data" (the existing validator signal) | Buttons labelled; result announced | Evolve the footer in `AskTab.Answer` | Ask | P1 |

### 14.3 Progress, social and settings additions (05c)

| Component | Purpose | Key props | Behaviour and states | A11y / copy | Evolve / new | Used by | Pri |
|---|---|---|---|---|---|---|---|
| `FocusSheet` | Create/edit the one active Focus (title, reason, cue-action sentence, review rule) | `draft`, `evidence[]`, `onSave` | Prefilled from an accepted Insight; editable; "Not now" and "Ask my coach" available; saving never schedules a reminder unless the player opts in | Radix dialog/sheet; form errors tied to fields | New | Progress, Recap, Insight actions | P1 |
| `StatusLadder` | **Reviewed → Practised → Shown in later play** for a Focus | `status`, `evidence?` | Steps are never skipped; "Shown in later play" requires a comparable match and a verified event; viewing a clip never advances it | Ordered list with `aria-current`; each step has text | New | FocusCard | P1 |
| `MilestoneCard` | One verified entry in **My story** (a First, a personal best, a saved Moment) | `milestone`, `evidence` | Shows definition and date; **no celebration animation** unless a verified personal best (file 08 §8); player can hide it | Heading + date; Watch this | New (relative of `PersonalBestCard`) | My story | P1 |
| `BaselineNote` | "Your first match is the baseline" / "Start a fresh baseline" after a break | `kind: "first" \| "after_break"`, `onFreshStart` | Replaces any trend chart when n is below threshold; after-break copy never mentions streaks or regression | Plain text; button is secondary | New | Progress | P0 |
| `ChallengeModePicker` | Choose **Relax · Explore · Friendly** challenge mode | `value`, `onChange` | Friendly competition requires opt-in and shows who can see results; switching is instant and reversible | Radio group | New | Explore | P2 |
| `ActiveLinksList` | List of live share links with expiry and **Revoke** | `links[]`, `onRevoke` | Shows audience, expiry, download allowed; revoke states what cannot be recalled (copies already downloaded) | Table/list with explicit button labels | New | Privacy Centre, Share | P1 |
| `ConsentRow` | One row of the `ConsentLedger` (purpose, status, date, effect of change) | `record`, `onChange` | Composes `ConsentToggle`; on change states **what changes now** and what needs a backend job (in demo: "Simulated") | `role=switch`; effect text via `aria-describedby` | New (uses `ConsentToggle`) | Privacy Centre | P0 |
| `PauseAllToggle` | Global notification pause | `value`, `onChange` | One switch that overrides every trigger; shows when it ends if scheduled | `role=switch` | New | Notifications | P1 |
| `ToneSelector` | **Direct · Balanced · Coach-guided** wording preference | `value`, `onChange` | Live preview of the *same* sentence in all three tones; changes wording and order only, never the evidence (file 09 §3) | Radio cards with the sample as description | New | Preferences | P1 |
| `HelpArticle` | Help topic layout including `/help/metrics` definitions | `topic`, `blocks` | Plain-language definition first, then numerator/denominator, exclusions, limits, version history; linked from every `MetricPopover` | Heading hierarchy; anchor links | New | Help | P1 |
| `FeedbackForm` | Report an issue (inaccurate event, wrong player, poor Moment, confusing metric, privacy concern, other) | `ref?`, `onSubmit` | Prefills the context (match, Moment, metric), never the video; confirmation promises a reference ID **only if** a real review queue exists (G-32) | Inline errors; success announced | New | Help, every Fix this fallback | P1 |
| `SharedMomentPage` | The public `/s/$token` page | `token` | Consent-gated, expiring; shows the Moment, the sharer's chosen caption and a small "make yours" link; no names unless the sharer chose; **no raw analytics or other people's data**; expired and revoked states | Video with captions where available; clear expiry text | New | Share | P1 |
| `PairTimeline` | Shared timeline of a partnership (Pair memory) | `pairId`, `items[]` | **Not yet** until doubles (G-03): renders fixtures behind `DemoBanner`; items need both partners' consent; pair-first language ("both of you") | List with dates; no blame wording | New (relative of `JourneyTimeline`) | Together | P2 |
| `UnlinkDialog` | Remove a partner link / revoke pair sharing | `partner`, `onConfirm` | States exactly what disappears for each person and what stays (clips already shared); destructive styling reserved for this action | Radix `alertdialog`; focus on the safe button | Evolve the delete dialog pattern in `LibraryPage` | Together, Settings | P2 |

### 14.4 Composition additions

```
Recap            ─ EntryChoice, ScoreChip, WhyChosenPanel, QualityPanel, FixQueue (entry)
Moments          ─ FilterBar/FilterSheet, LensChips, MomentCard + FavouriteButton
Deep dive        ─ DeepDiveShell ▸ SubNav ▸ { Story | Rallies(RallyFilterBar, ShotSequenceTable) |
                   Shots | Court(CourtMap + ZoneTable + CourtFitBadge) | Compare | Ask(AnswerFeedback) }
                   Advanced: EventTable, QualityPanel(versions)
Review & fix     ─ FixQueue ▸ FixSheet ▸ ChangeSummaryBanner
Progress / story ─ BaselineNote, ProgressCard, FocusCard ▸ StatusLadder, MilestoneCard
Privacy Centre   ─ ConsentLedger ▸ ConsentRow ▸ ConsentToggle · ActiveLinksList · PauseAllToggle · ToneSelector
Share            ─ SharePreviewDialog · SharedMomentPage (public)
```

### 14.5 Tests added

Each component above ships with a keyboard path, an accessible name, both themes, three depths where relevant, and one assertion tied to its rule. Examples: `ScoreChip` renders no red/green and no headline; `FavouriteButton` never changes visibility; `StatusLadder` does not advance on a clip view; `ZoneTable` renders "not measured" for null; `FeedbackForm` never promises a reference without a real queue.
