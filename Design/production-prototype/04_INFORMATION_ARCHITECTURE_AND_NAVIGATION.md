# 04 — Information Architecture and Navigation

**Status:** Build-ready IA, routing and navigation specification.
**Depends on:** `00_README_DECISIONS_AND_CONTRACT.md` (D1–D18; route map §5; component names §6). Cited as **D#**.
**Related:** `03` (first run), `05a/b/c` (screens), `07` (components), `10` (permissions, sharing).

---

## 0. Principles

1. **Organise around the player's questions, not the engine's modules** (Blueprint §4, v2 §10.2). Nothing in the navigation is named after a model, a tracker or an event type.
2. **Depth is a layer, not a destination.** Advanced analysis lives **inside a match** as *Deep dive*, never as a top-level warehouse of charts (Blueprint §5.1).
3. **One persistent primary action:** *Add a match* (the ＋) is one tap away on every screen (Blueprint §5.1).
4. **Few top-level places.** Five on mobile, six on desktop. Everything else is reachable from a card, a filter or the avatar menu.
5. **The URL is the state.** A player can paste a link to a recap, a filter, or an exact frame (`?f=`), and land in the same place — subject to permission.
6. **No dead ends.** Every empty, partial, failed or revoked route offers one next step (v1 §6 navigation rules).
7. **Navigation never creates pressure.** No unread counts, no "streak" badges, no red dots for inactivity. The only indicator is a quiet *ready* dot when an analysis the player started has finished.
8. **Presets and depth change what is *shown*, never what is *true*** (D2). Relax, Explore, Improve and Compete are shortcuts over one Recap and one evidence model, not separate products. Switching keeps the current match, scroll context and corrections; it changes ordering and depth only. The same permissions and trust gates apply on every layout.

---

## 1. Sitemap

```
PUBLIC (no sign-in)
├── /welcome                      Landing + interactive example
│   └── /welcome/sample           Sample match recap (labelled "Sample")
├── /start                        Onboarding (two optional questions)
├── /s/$token                     Shared moment / match (view-only, expiring)
└── /help, /help/$topic           Help, metric definitions, "what we can and can't do"

PLAYER (guest or signed-in)
├── /                             HOME  — resume the loop
├── /matches                      MATCHES — library
│   ├── /matches/new              New match  (record guide → file → consent → upload → who's who → court)
│   └── /matches/$matchId         RECAP  (Moments → My game → Together)
│       ├── /processing           Processing (also an in-page state of the recap)
│       ├── /moments              Moments from this match
│       ├── /review               Review & fix queue
│       ├── /court                Place your court
│       └── /deep-dive            DEEP DIVE shell
│           ├── /story            Match story (scoreline, momentum — Advanced emphasis)
│           ├── /rallies          Rally timeline + list
│           ├── /shots            Shots (Preview)
│           ├── /court            Court maps (Preview)
│           ├── /compare          Compare matches (comparable only)
│           └── /ask              Ask about this match (grounded)
├── /moments                      MOMENTS — all my moments
│   └── /moments/$clipId          Clip detail
├── /progress                     PROGRESS — self-baseline, comparable matches
│   ├── /progress/records         Personal bests
│   ├── /progress/shots           Shot Explorer ("what we've spotted")
│   └── /progress/story           My story (journey)
├── /together, /together/$partnerId   TOGETHER — pair memories (Not yet; designed)
├── /explore                      EXPLORE — optional challenges and skills
├── /feedback                     Report an issue
└── /settings                     SETTINGS (avatar menu)
    ├── /profile  /preferences  /privacy  /data  /notifications  /accessibility

OPERATOR (not in the player's navigation)
└── /admin/system                 GPU, host, runtime, profiles, models
```

---

## 2. Route table (exactly the routes of file 00 §5, plus implementation notes)

| Route | Screen | Access | Nav highlight | Params / search | Notes |
|---|---|---|---|---|---|
| `/welcome` | Landing | Public | — | `?src=` (campaign, no PII) | Redirect to `/` if signed in with ≥ 1 real match |
| `/welcome/sample` | Sample recap | Public | — | `?purpose=` `?depth=` | Same components as the real Recap (AC-ONB-8) |
| `/start` | Onboarding | Public | — | `?step=purpose\|preset` | State stored in a guest draft; **not** separate pages |
| `/` | Home | Player | Home | — | Content depends on situation + preset (§9) |
| `/matches` | Matches list | Player | Matches | `?type=&when=&state=&with=` | Filters in URL |
| `/matches/new` | New match | Player | ＋ | `?step=guide\|file\|consent\|upload\|who\|court\|ready` | Wizard; Back preserves state |
| `/matches/$matchId` | Recap | Owner / invited viewer | Matches | `?f=<frame>` `?depth=` `?preset=` | `$matchId` = `session_id`. Opens at `ready_to_play` (D4, §9 of doc 03) |
| `/matches/$matchId/processing` | Processing | Owner | Matches | — | Redirects to Recap when `ready_to_play`; the page is retained for direct links |
| `/matches/$matchId/moments` | Match moments | Owner | Matches | `?lens=&player=&f=` | Lenses: all · yours · saved |
| `/matches/$matchId/review` | Review & fix | Owner | Matches | `?focus=<eventId>&only=doubtful` | Queue starts from what the Recap shows (D11) |
| `/matches/$matchId/court` | Place your court | Owner | Matches | `?segment=` | Replaces `/sessions/$id/calibrate` |
| `/matches/$matchId/deep-dive` | Deep dive shell | Owner | Matches | `?f=` | Redirects to `/story` (Quick/Guided) or `/rallies` (Compete preset) |
| `…/deep-dive/story` | Match story | Owner | Matches | `?game=&f=` | Momentum/head-to-head live here (D6) |
| `…/deep-dive/rallies` | Rally timeline & list | Owner | Matches | `?game=&who=&len=&outcome=&doubtful=1&f=` | |
| `…/deep-dive/shots` | Shots | Owner | Matches | `?who=&shot=` | Preview |
| `…/deep-dive/court` | Court maps | Owner | Matches | `?kind=presence\|origin\|opponent-met&who=` | Preview; calibration-gated |
| `…/deep-dive/compare` | Compare matches | Owner | Matches | `?with=<matchId>` | Only comparable pairs offered |
| `…/deep-dive/ask` | Ask | Owner | Matches | `?q=` | Grounded; citations deep-link `?f=` |
| `/moments` | All moments | Player | Moments | `?tab=for-you\|favourites\|together&q=&match=` | |
| `/moments/$clipId` | Clip detail | Owner / permitted viewer | Moments | `?from=match\|moments&return=<url>` | "Return to analysis" uses `return` |
| `/progress` | Progress | Player | Progress | `?metric=&window=` | Suppresses trend when < 2 comparable matches |
| `/progress/records` | Personal bests | Player | Progress | `?kind=` | |
| `/progress/shots` | Shot Explorer | Player | Progress | `?shot=` | Preview |
| `/progress/story` | My story | Player | Progress | — | Verified milestones only |
| `/explore` | Challenges | Player | Explore (desktop), Home card (mobile) | — | All optional |
| `/together`, `/together/$partnerId` | Pair memories | Player | Together | — | **Not yet** — placeholder |
| `/s/$token` | Shared page | Token holder | — | `?f=` (clip start) | Consent-gated, expiring, revocable |
| `/settings` + `/profile /preferences /privacy /data /notifications /accessibility` | Settings | Player | Avatar menu | — | |
| `/help`, `/help/$topic`, `/feedback` | Help/Feedback | Public/Player | Avatar menu | `?topic=` | |
| `/admin/system` | System | Operator | — | — | Not linked from player navigation |

**Implementation (TanStack Router):**
- One `rootRoute` with the `AppShell`; **layout routes** for `/matches/$matchId` (header + status) and `/deep-dive` (sub-tab bar).
- `validateSearch` on every route with search params (existing `SessionSearch { f }` pattern); invalid values are dropped, not errored.
- `defaultPreload: "intent"` and `scrollRestoration: true` stay (already configured).
- Heavy routes lazy-loaded with `lazyRouteComponent` (as `CalibratePage`/`SystemPage` are today): Deep dive tabs, Court, Compare.
- Route `beforeLoad` enforces *presentation* guards only; **authorisation is server-side** (v1 §7.1).

---

## 3. Navigation model

### 3.1 Primary navigation

| Slot | Label | Icon (lucide) | Destination | Desktop | Tablet | Mobile |
|---|---|---|---|---|---|---|
| 1 | **Home** | `House` | `/` | SideNav | Rail | BottomBar |
| 2 | **Matches** | `LibraryBig` | `/matches` | SideNav | Rail | BottomBar |
| ＋ | **Add a match** | `Plus` | `/matches/new` | Prominent button above SideNav | Rail top | **Centre BottomBar slot** |
| 3 | **Moments** | `Clapperboard` | `/moments` | SideNav | Rail | BottomBar |
| 4 | **Progress** | `TrendingUp` | `/progress` | SideNav | Rail | BottomBar |
| 5 | **Together** | `Users` | `/together` | SideNav | Rail | Home card + Moments filter (not in bar) |
| 6 | **Explore** | `Compass` | `/explore` | SideNav | Rail | Home card |
| — | **Avatar menu** | `CircleUser` | Profile · Settings · Privacy · Help · Switch preset · Sign out | Header | Header | Header |

> **Why Progress, not Journey, on the bar:** progress and "my story" are one concept to a player (*"how am I doing, and what have I done?"*). "My story" is a tab inside Progress (`/progress/story`) — one fewer top-level place (v1 listed both).

### 3.2 `SideNav` (≥ 1024 px)

```
┌───────────────┐
│ ◇ Rally       │
│ [ ＋ Add a match ]│  ← primary button
│───────────────│
│ ⌂ Home        │
│ ▤ Matches     │
│ ▶ Moments     │
│ ↗ Progress    │
│ 👥 Together   │  ← "Soon" tag while Not yet
│ ✦ Explore     │
│───────────────│
│ (sample)      │  ← only if the player has no real match
│───────────────│
│ ◉ Alex   ▾    │  ← AvatarMenu
└───────────────┘
```
- Width 220–260 px (v1 §3). Active item = filled background + `aria-current="page"` (never colour alone).
- "Together" carries a **Soon** `PreviewTag` while doubles/partner features are **Not yet** (D10). It opens a placeholder, never a broken page.
- A **ready dot** (●, with visually hidden "ready") appears on *Matches* only when an analysis the player started has completed since they last opened it. It clears on open. No numeric badge.

### 3.3 `Rail` (768–1023 px)
Icons + labels collapsed to icons with tooltips; ＋ at the top; avatar at the bottom. Expand to SideNav via a toggle that remembers its state.

### 3.4 `BottomBar` (< 768 px)

```
┌──────────────────────────────────────┐
│  ⌂        ▤        (＋)       ▶    ↗  │
│ Home   Matches    Add      Moments Progress
└──────────────────────────────────────┘
```
- Five slots, **centre ＋ raised** but within the safe area; 56 px min height; labels always visible (no icon-only critical actions, Blueprint §10.9).
- Hidden on **video theatre** states (§4.4) and while a keyboard is open; never covers the primary action (v1 §3 mobile rule).
- Together/Explore appear as cards on Home and as chips in Moments (`Together`).

### 3.5 `AddMatchButton`
Opens `/matches/new` at the first step the player needs: *guide* for first-time, *file* for returning (the guide is remembered as seen). Long-press/secondary: "Sample match", "How to film it". It is the **only** persistent call-to-action; no second floating button.

---

## 4. `AppShell` behaviour

### 4.1 Regions
```
┌─────────────────────────────────────────────────────────────┐
│ DemoBanner (only when Sample/Demo data is on screen)        │
├────────┬────────────────────────────────────────────────────┤
│ SideNav│ Header: Breadcrumb · page title · status · controls│
│        ├────────────────────────────────────────────────────┤
│        │ Content (max-width per page type; Deep dive is wide)│
│        │                                                    │
├────────┴────────────────────────────────────────────────────┤
│ BottomBar (mobile only)                                     │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Content widths
| Page type | Max width | Why |
|---|---|---|
| Home, Matches, Moments, Progress, Settings | 1120 px | Scannable, calm |
| Recap | 1280 px; two-column ≥ 1024 (video sticky left, narrative right) | Blueprint §7.8 |
| Deep dive | up to 1680 px (existing `max-w-[1680px]`) | Video + data side by side |
| Forms (new match, consent, court) | 640 px | Focus |

### 4.3 Global status
A single **status pill** in the header lists the player's *running* analysis: "Sunday game · Analysing 64 %" (real value, §9.2 of doc 03) → links to the match. If more than one, "2 matches analysing". It disappears when none. It is the only cross-page persistent progress indicator (replaces the per-page header chip used today).

### 4.4 Themes inside the shell (D13)
- **Court Daylight** (light) is the default surface for Home, Matches, Moments, Progress, Settings, Help.
- **Arena Night** (dark) is the surface for **video theatre** — the video player stage and Deep dive — regardless of system theme, because overlays and heatmaps need dark contrast. Entering a match recap on mobile keeps Daylight for the narrative and shows the player in a dark stage block.
- A "Theatre" toggle (and key `T`) lets the player dim the whole match view.
- The shell never flashes between themes on navigation: the route's theme is known before paint.

### 4.5 Global banners (priority order; max one visible at a time)
1. `DemoBanner` — "Sample match — fictional players." (non-dismissable)
2. Offline — "You're offline. You can still read what you've opened." 
3. Reconnecting (existing live-feed pill)
4. Processing degraded — "Some parts have reduced detail." (per match)
5. Review nudge — "Place the court to unlock heatmaps." (per match, dismissible, never repeated after dismissal)

### 4.6 Error boundary and `NotFound`
Route-level error boundary shows a friendly recoverable message with **Back** and **Home**; `NotFound` (existing `AppShell` export) is extended with the 404/permission pages in §14.

### 4.7 Accessibility of the shell
Skip link ("Skip to content"); landmarks (`nav`, `main`, `header`); one `h1` per route; focus moves to the `h1` on route change (announced via a polite live region "Matches, page loaded"); `aria-current` on active nav; BottomBar items are links, not buttons; nav usable with keyboard and switch controls; no hover-only information.

---

## 5. Header contents

### 5.1 General pages
`Breadcrumb` (desktop only; mobile shows a back chevron) · page title · optional primary action · `AvatarMenu`.

### 5.2 Match pages (Recap, Deep dive, Moments of a match, Review, Court)

```
┌─────────────────────────────────────────────────────────────────┐
│ ‹ Matches   Sunday evening game            ● Analysing 64 %     │
│ You (Alex, near) vs Opponent  ·  Match · Singles · 12 Jun       │
│ [Relax ▾]  Purpose: Keep the moments ▾  Depth: Quick|Guided|Adv │
│ Shown because you chose Keep the moments · Change · Reset · Show all│
│ [Preview] [Court ✓ ·  Change]            [Share ▾] [⋯]          │
└─────────────────────────────────────────────────────────────────┘
```

| Element | Behaviour |
|---|---|
| **Match title** | Editable inline (pencil). Default from file name |
| **Players line** | "You (Alex, near)" · "Opponent" — uses the nicknames the player gave (D8). A "Change" link opens `WhoIsWho`. The raw `P1/P2` strings never appear outside Advanced |
| **`MatchStatusChip`** | Words + shape, never colour alone. States: *In the queue · Getting your video ready · Ready to watch · Analysing {n} % · Done · Couldn't finish · Needs a look* (§9.2 of doc 03). `Analysing` shows the real % from `frontier_frame/n_frames` and optionally `{rate}× real time` in Advanced |
| **`PresetSwitcher`** | Relax · Explore · Improve · Compete (D3). Per-match; offers "Make this my default?" after the second change |
| **`PurposeChips`** | Up to two; editable; "Shown because you chose …  Change · Reset · Show all" is **mandatory** copy (Blueprint §3.2) |
| **`DepthSwitcher`** | Quick · Guided · Advanced (segmented control, `role="radiogroup"`); the *current* depth's description is available as a tooltip and live-announced |
| **`PreviewTag`** | A small tag appears once for the whole page when any visible surface is **Preview** (D10); opens a popover listing which parts and why |
| **Court status** | "Court ✓ · Change" or "Court needs a look · Place it" (links to `/matches/$id/court`) |
| **`DemoBanner`** | Only on Sample/Demo matches |
| **Share** | Opens `SharePreviewDialog`; **disabled with reason** if sharing consent is off or the player is a guest ("Add an email to share safely") |
| **⋯ menu** | Rename, Change who's who, Analyse again, Export, Delete match |

On mobile the header collapses to: back chevron · title · status chip · `⋯`; preset/purpose/depth live in a bottom sheet opened by a **"View: Quick · Relax"** chip so the video stays visible (Blueprint §5.3).

### 5.3 Deep dive sub-tab bar
`Story · Rallies · Shots (Preview) · Court (Preview) · Compare · Ask`; tabs that the current depth hides are **not shown** (no disabled-looking tabs). A "Show all" link on the bar reveals the hidden ones.

---

## 6. Roles and permission views

| Role | Who | Sees | Can | Cannot |
|---|---|---|---|---|
| **Guest owner** | Player without an account (device-bound token) | Their own matches on this device | Everything in the first run; keep Moments for the retention window | Share, save to history, use another device (prompt for email — doc 03 §13) |
| **Player (owner)** | Signed-in | Own matches, Moments, progress | Everything | See anyone else's private data |
| **Partner viewer** | Holder of an invite/share link, or an accepted pair partner | Only the artefacts shared with them | View, "That's me", request removal, make own moments | Download (unless allowed), see other matches, see the owner's stats |
| **Coach** | **Not yet** (designed) | Athlete-approved matches/playlists, scoped by athlete, match, time; expiring and revocable | Annotate with *one question*, see correction history | Permanent access to future footage; see unshared data (Blueprint §7.14) |
| **Operator** | Server admin | `/admin/system` | View runtime | — (not part of the player's product) |

**Permission-aware navigation rules**
- A viewer's shell is **stripped**: no SideNav/BottomBar for token holders; a single header with the owner's name (or nickname), expiry and "Make your own moments".
- A partner-viewer sees a **view-only** Recap: no Fix, no Share, no Deep dive unless the owner granted it.
- Coach views reuse the same components with an annotation layer; every coach action is in an audit log (Doc 10). Entire section is marked **Not yet** and routes to a placeholder.
- Revoking access mid-view turns the page into the `PermissionRevokedState` (§14) on the next request; the page does not keep serving cached video.
- **Server enforces everything;** the client's hiding of controls is a courtesy (v1 §7.1).

---

## 7. Preset × Purpose × Depth behaviour matrix

### 7.1 How the three controls combine
- **Purpose** (what the player wants) changes **ordering and emphasis** and which optional cards appear.
- **Depth** (how technical) changes **density, vocabulary, and which tabs/columns exist**.
- **Preset** is a named bundle: *Relax* = Keep moments + Quick · *Explore* = Understand + Guided-light · *Improve* = Practise + Guided · *Compete* = Compete + Advanced.
- **Rule of precedence:** an explicit Depth or Purpose choice wins over the preset's default; the preset badge shows "Custom" when they differ.
- **Facts never change.** The same events, the same `CheckChip` states, the same coverage line are available at every combination; hidden ≠ removed (**Show all** always works).

### 7.2 Screen-by-screen visibility matrix

Legend: ● shown by default · ○ available behind "Show more / Show all" · — not shown · **P** carries a *Preview* tag · **N** *Not yet*.

| Surface | Relax | Explore | Improve | Compete | Quick | Guided | Advanced |
|---|---|---|---|---|---|---|---|
| **Home** | | | | | | | |
| Resume card (loop in progress) | ● | ● | ● | ● | ● | ● | ● |
| Latest Moment | ● | ● | ● | ○ | ● | ● | ○ |
| Current Focus card | — | ○ | ● | ○ | — | ● | ○ |
| Progress signal (≥ 2 comparable matches) | ○ | ● | ● | ● | ○ | ● | ● |
| "Saved filters / resume investigation" | — | — | — | ● | — | — | ● |
| Explore card (challenges) | ○ | ● | ○ | — | ○ | ● | — |
| **Recap** | | | | | | | |
| HeroMoment | ● | ● | ● | ● | ● | ● | ● |
| FactTrio (3 facts) | ● | ● | ● | ○ | ● | ● | ○ |
| Match story paragraph | ○ | ● | ● | ● | ○ | ● | ● |
| Verified strength | ○ | ● | ● | ● | ○ | ● | ● |
| Opportunity ("worth exploring") | — | ○ | ● | ● | — | ○ | ● |
| Practice bridge / Focus suggestion | — | — | ● | ○ | — | ● | ○ |
| Scoreline chip (context) | ● | ● | ● | ● | ● | ● | ● |
| Head-to-head table, win rate, points won | — | — | — | ● | — | — | ● |
| Momentum chart | — | — | ○ | ● | — | — | ● |
| Coverage line ("We followed 31 of 36 rallies") | ● | ● | ● | ● | ● | ● | ● |
| `CheckChip` on each claim | ● | ● | ● | ● | ● | ● | ● |
| Numeric/raw band, event IDs, model version | — | — | — | ○ | — | — | ● |
| Together section | **N** | **N** | **N** | **N** | **N** | **N** | **N** |
| **Moments** | | | | | | | |
| Lenses: Memorable, Longest rally, Kept alive | ● | ● | ● | ● | ● | ● | ● |
| Lenses: Cleanest execution, Tactically interesting | — | ○ | ● | ● | — | ● | ● |
| Fun/blooper lens (explicit opt-in per clip) | ○ | ○ | — | — | ○ | ○ | — |
| Download clip (`clip.mp4`) | ○ | ○ | ○ | ● | ○ | ○ | ● |
| **Deep dive tabs** | | | | | | | |
| Story | ○ | ● | ● | ● | ○ | ● | ● |
| Rallies | ● | ● | ● | ● | ● | ● | ● |
| Shots **P** | — | ● | ● | ● | — | ● | ● |
| Court **P** | — | ○ | ● | ● | — | ● | ● |
| Compare | — | — | ○ | ● | — | ○ | ● |
| Ask | ● | ● | ● | ● | ● | ● | ● |
| Event table / raw log | — | — | — | ○ | — | — | ● |
| Exports (PDF, CSV, JSONL, JSON) | ○ | ○ | ○ | ● | ○ | ○ | ● |
| **Rally list** | | | | | | | |
| Winner chip + shuttle outcome | ○ | ○ | ● | ● | ○ | ● | ● |
| "Only rallies that need a look" filter | ● | ● | ● | ● | ● | ● | ● |
| Per-rally shot chips | — | ○ | ● | ● | — | ● | ● |
| "Why the rally ended", "Counted / not counted" | — | — | ○ | ● | — | ○ | ● |
| **Progress** | | | | | | | |
| Personal bests | ● | ● | ● | ● | ● | ● | ● |
| Shot Explorer **P** | ○ | ● | ● | ● | ○ | ● | ● |
| Trend small-multiples | — | ○ | ● | ● | — | ● | ● |
| My story (journey) | ● | ● | ○ | — | ● | ● | — |
| **Settings & other** | | | | | | | |
| Metric definition popovers | on tap | on tap | on tap | on tap | on tap | inline | inline + version |
| Keyboard shortcut help | ○ | ○ | ○ | ● | ○ | ○ | ● |
| `/admin/system` | operator only |

### 7.3 Purpose effects (ordering and optional cards)

| Purpose | First thing on Recap | Added cards | Suppressed |
|---|---|---|---|
| Keep the moments | HeroMoment → MomentStrip | Save/Share affordances | Opportunity, Focus |
| Understand my game | Match story → strength | Coverage detail | — |
| Choose something to practise | Strength → one Opportunity → **Focus** suggestion | FocusCard, ReflectionPrompt | — |
| Prepare to compete | Story → rallies by score state | Compare, filters | Fun lens |
| Discuss with someone | Moments with notes | Share-to-one-person, "Add a question" | — |
| Just play | Hero only (Settings → Preferences) | — | Analysis cards and recommendations beyond the basic record |

### 7.4 Per-match vs default scope
Changes apply **to the match being viewed** immediately; defaults live in `/preferences`. The header shows "Custom for this match" when they differ, with **Reset to my default**.

### 7.5 Accessibility and honesty rules for the matrix
- Hidden items are announced by a single "Show all (7 more)" control; they are never removed from the DOM-accessible tree by `display:none` while the "Show all" is active.
- A **Quick** player never loses access to evidence: "Watch this" and the coverage line exist at every depth (D16).
- **Preview** tags are never hidden by depth.

---

## 8. URL and query-state rules

| Rule | Detail |
|---|---|
| **Everything restorable is in the URL** | Filters, selected lens, selected rally (`?rally=`), depth/preset overrides, the playhead (`?f=`). No hidden filter state |
| **`?f=<frame>`** (existing) | Deep-links the video to an exact frame on any match route; produced by citations, highlights, exports and share links. `validateSearch` accepts only integers ≥ 0; the player seeks when metadata is ready (existing `useDeepLink`). Frames, not seconds, are canonical (`fps_num/fps_den`); URLs stay stable across proxy re-encodes |
| **`?depth=` `?preset=`** | Optional overrides; **never** persisted from a shared link into the recipient's preferences |
| **Filters** | Short keys, arrays as comma lists; a "Clear filters (n)" control shows the active count (v1 filter bar) |
| **Defaults omitted** | Absence means default; the URL doesn't carry defaults |
| **No PII** | Never put names, nicknames, emails, tokens (except `/s/$token`, which is a random opaque id) or file names in a URL (Blueprint privacy rule: "never place personal data in URL parameters") |
| **Share URLs** | `/s/$token` only; token is revocable and expiring; the match id is never the share token |
| **Replace vs push** | Filter changes `replace`; navigating to a different destination `push`; seeking the playhead during playback does **not** write to history (only an explicit "link to this moment" does) |
| **Stale links** | A link to a deleted match shows the `PermissionRevokedState`/not-found variant (§14), never a blank page |

### 8.1 Back navigation and scroll restoration
- Back restores **filters and scroll position** (TanStack `scrollRestoration: true`) on Matches, Moments, Rallies, Progress.
- Route transitions inside a wizard (`/matches/new?step=`) use `replace` so Back leaves the wizard rather than stepping through each substep; an in-wizard **Back** button steps backwards and preserves state.
- Opening a Moment **from a chart or the rally list** keeps context via `?from=` and `?return=` (internal path only; validated to be same-origin and a known route). The clip detail shows **"‹ Return to analysis"** and Back does the same.
- Closing a dialog/sheet returns focus to the invoking control (v1 AC 39).
- From the Recap, "Open in Deep dive" preserves `?f=` so the video stays where it was.

---

## 9. Home — information hierarchy by situation and preset

**Home answers one question: *what is the next thing worth doing?*** It contains **at most five modules** in a fixed hierarchy; the situation decides which exist, the preset decides their weight (Blueprint §5.2; v1 §7).

### 9.1 Hierarchy (top → bottom)
1. **Continue the loop** — a single card (Resume / Review / Start).
2. **Current focus** — only if the *player* chose one.
3. **Latest meaningful evidence** — one Moment.
4. **Progress signal** — only if ≥ 2 comparable matches.
5. **Explore** — collapsed, optional.

Never on Home: a global player score, a streak, a leaderboard, an empty chart wall, "performance score", unread counters.

### 9.2 By situation

| Situation | Module 1 | Module 2 | Module 3 | Module 4 | Module 5 | Do **not** show |
|---|---|---|---|---|---|---|
| **New, no footage** | "Your game starts here." → See the sample / Add my first match | — | — | — | Record guide link | Empty charts, scores |
| **Processing** | Real `ProcessingStages` + "Watch while we work" | — | Moments so far | — | — | Fake % or countdown |
| **Returning — Relax (recreational)** | "Your Sunday game is ready — watch your best moment" | — | Latest Moment (large) | Progress signal only if comparable | Explore (collapsed) | Deficit list, compulsory Focus |
| **Returning — Explore** | Latest match recap | Optional: "Shots we spotted" | Latest Moment | Personal best (if any) | Explore card | Rankings |
| **Returning — Improve** | "Review Sunday's game" / "Prepare today's practice" | **Focus card** (player-chosen) | Evidence clip for the focus | Progress for the focus metric | — | Every metric |
| **Returning — Compete** | "Resume your investigation" / latest match workspace | Saved filters | Rally sequence of interest | Comparisons | — | A simplified grade that hides coverage |
| **After a break (≥ 3 weeks)** | "Resume with one match" (fresh baseline offered) | — | A past favourite Moment | — | — | Regression alarm, old-peak comparison, "we miss you" |
| **Error / low coverage** | What happened + what is still valid + fix | — | Valid Moments | — | — | Making the player repeat work without explanation |

### 9.3 Wireframes (mobile)

```
Returning — Relax                       Improve                          Processing
┌──────────────────────────┐   ┌──────────────────────────┐   ┌──────────────────────────┐
│ Good to see you          │   │ Review Sunday's game     │   │ Sunday game              │
│ ┌ Resume ──────────────┐ │   │ ┌ Resume ──────────────┐ │   │ ┌ Getting it ready ───┐ │
│ │ Sunday game is ready │ │   │ │ 12 rallies to look at│ │   │ │ ▢ video ready       │ │
│ │ [ Watch best moment ]│ │   │ │ [ Open recap ]       │ │   │ │ ▢ court found       │ │
│ └──────────────────────┘ │   │ └──────────────────────┘ │   │ │ ▢ rallies (7 so far)│ │
│ ┌ Moment ──────────────┐ │   │ ┌ Focus (you chose) ───┐ │   │ └─────────────────────┘ │
│ │ ▶ 12-shot rally      │ │   │ │ Recover to the middle│ │   │ Moments so far           │
│ └──────────────────────┘ │   │ │ after back-court shots│ │   │ [ ▶ ] [ ░ ] [ ░ ]       │
│ Progress (if comparable) │   │ │ [ Watch examples ]   │ │   └──────────────────────────┘
│ ▾ Explore                │   │ └──────────────────────┘ │
└──────────────────────────┘   │ Progress on this focus   │
                               └──────────────────────────┘
```
Desktop: modules 1–3 in a two-column grid (resume left, moment right); 4–5 below.

### 9.4 Acceptance
- **AC-IA-1** Home never shows more than five modules.
- **AC-IA-2** Each situation row above renders exactly its modules (snapshot per situation × preset).
- **AC-IA-3** No streak, rank, global score or inactivity message exists anywhere on Home.

---

## 10. Keyboard shortcut map

**Rules:** shortcuts fire only when focus is not in an input, textarea, select or contenteditable, and no modifier (Ctrl/Meta/Alt) is held (existing `useShortcuts` guard). Every shortcut has a visible button equivalent. `?` opens the help dialog (existing).

### 10.1 Video (kept exactly as today)
| Keys | Action |
|---|---|
| `Space` / `K` | Play / pause |
| `←` / `→` | Previous / next frame (pauses) |
| `Shift` + `←` / `→` | Back / forward 5 s |
| `J` / `L` | Back / forward 10 s |
| `[` / `]` | Previous / next rally |
| `S` | Next smash |
| `.` | Hide/show all overlays |
| `?` | Shortcut help |

### 10.2 Added for the new IA
| Keys | Action | Where |
|---|---|---|
| `M` | **Save this moment** at the playhead (opens a tiny sheet: name optional, boundaries editable) | Match pages |
| `F` | **Fix this rally** (opens `FixSheet` at the current rally) | Match pages |
| `W` | **Watch this** — jump to the evidence of the focused insight | When an `InsightCard` is focused |
| `T` | Toggle theatre (dim the page) | Match pages |
| `N` | New match (`/matches/new`) | Anywhere except wizard text fields |
| `G` then `H` / `M` / `O` / `P` | Go to Home / Matches / Moments / Progress | Anywhere (chord, 1.5 s window; discoverable in `?`) |
| `/` | Focus search (when search exists, §12) | List pages |
| `Esc` | Close dialog/sheet/popover; return focus to trigger | Everywhere |
| `1` `2` `3` | Depth Quick / Guided / Advanced | Match pages |

**Conflicts checked:** `S` (next smash) vs nothing in IA; `M`/`F`/`T`/`N` do not clash with the video set; `G`-chords are the only two-key shortcuts. Shortcuts are **off** on touch layouts (no help button there).

### 10.3 Accessibility
Shortcuts can be disabled in `/accessibility` (WCAG 2.1.4 character-key shortcuts); the help dialog is keyboard-accessible, trapped, and returns focus to the invoker.

---

## 11. Breadcrumbs

Desktop only (mobile uses a back chevron to the parent). Rules: always show the **parent chain to the nearest list page**; the final crumb is not a link; match names are truncated to 32 characters with the full name in a tooltip/`title`; never expose ids.

| Route | Breadcrumb |
|---|---|
| `/matches/$id` | Matches › Sunday evening game |
| `…/deep-dive/rallies` | Matches › Sunday evening game › Deep dive › Rallies |
| `/moments/$clipId` | Moments › 12-shot rally *(if opened from a match: Matches › Sunday evening game › Moments › 12-shot rally)* |
| `/progress/records` | Progress › Personal bests |
| `/settings/privacy` | Settings › Privacy |

Structured as `<nav aria-label="Breadcrumb"><ol>`; current page has `aria-current="page"`.

---

## 12. Search (optional)

Not required for the prototype; specified so it can be added without re-architecting. **Scope:** matches (title, date, type, nickname), moments (title, match), help topics. **Not** a search over private statistics or other people. Entry: `/` key and a header icon on `/matches` and `/moments`. Results grouped by type; keyboard navigable; highlights query; no personal data in telemetry (`search_used {scope, result_count}` only). Empty result: "Nothing matches "{q}". Try the match name or a date." Server-side search must respect object-level permissions.

---

## 13. Deep links, sharing URLs and what each reveals

| URL | Visible to | Contains | Never contains |
|---|---|---|---|
| `/matches/$matchId?f=1234` | Owner (and permitted viewers) | Match id (opaque uuid), frame | Names, emails |
| `/moments/$clipId` | Owner | Clip id | — |
| `/s/$token?f=…` | Anyone with the link until expiry/revoke | Opaque token, optional start frame | Match id, owner id, nicknames in the URL |
| Citation chips (Ask) | Owner | `?f=` frame | Event ids in the visible URL |
| Export links (`/api/sessions/{id}/exports/*`) | Owner session only | Server-authorised | — |

**Share metadata (Open Graph)** for `/s/$token` must be **safe by default**: generic title ("A moment from a Rally match"), no thumbnail unless the owner chose one, `noindex`, no personal names. Previews in chat apps otherwise leak the very thing the player chose to keep private.

---

## 14. Journeys — the navigation traces

Counts are *taps from the entry point*; **targets**, to be verified in the tree test (§17).

### 14.1 Journey A — "I want a great clip" (casual)
`/` → *Watch best moment* (1) → Recap hero plays → `♡ Keep` (2) → optional `Share` (3, sheet) → back to Recap.
Success: relevant Moment in ≤ 2 taps; kept privately by default.

### 14.2 Journey B — "Am I improving?"
`/` → **Progress** (1) → choose metric chip (2) → comparison panel + `ComparabilityNote` → `Watch this` on a point (3) → Clip detail with `Return to analysis`.
Success: player can state the comparison and its limit.

### 14.3 Journey C — "Doubles pair memories" — **Not yet**
`Together` → placeholder "Doubles and partner memories are on the way" → *Share a moment privately* (singles opponent invite works today).

### 14.4 Journey D — "Competitive detail"
Header preset → **Compete** (1) → `/deep-dive/rallies` (auto) → filter score/shot/player (2–3) → open rally (4) → `RallyDetailPanel` + evidence → `Export` (5).

### 14.5 Journey E — "Something looks wrong" → **Review & fix**
Any claim or clip → `Fix this` → `FixSheet` offers only API-backed fixes (winner, official, match start, verify). Unsupported kinds are labelled feedback only after G-32. After persistence, `ChangeSummaryBanner` shows the refetched change; Undo appears only after G-14. G-15 is required for wrong-player/shot/boundary corrections. From the Recap's `ReviewBanner`: **Check what we show you** → `/review` queue ordered by what the Recap displays (hero first), max three questions to start.

### 14.6 Journey F — "Privacy control"
Avatar (1) → **Privacy** (2) → `ConsentLedger` → toggle/revoke (3) → effect explained inline → `Export my data` / `Delete` (separate confirm).

### 14.7 New — Review & fix (friendly)
Recap hero → "Is this the rally you remember?" **Not quite** → `FixSheet` (≤ 3 questions) → done; or `ReviewBanner` → `/review` → one question at a time; top of list = what the recap currently shows; progress "2 of 3 checked".

### 14.8 New — Invite a partner/opponent
Moment → `Share ▾` → `ShareAudiencePicker` → "Someone I played" → `SharePreviewDialog` (what's included, who, expiry, download allowed?) → `InviteLink` created → copy link / system share. Recipient opens `/s/$token` (doc 03 §12): view → "That's me" → optional removal request → "Make your own moments".

### 14.9 Journey: first-run (reference)
`/welcome` → sample → `/start` → `/matches/new` (guide → file → consent → upload → who → court → ready) → `/matches/$id` (processing in-page) → hero. (Doc 03.)

---

## 15. Error, not-found and permission routes

| Case | Route / trigger | What the player sees | Next actions |
|---|---|---|---|
| Unknown URL | `NotFound` | "We can't find that page." | Home · Matches · Help |
| Match deleted / never existed | `/matches/$id` 404 | "This match isn't here any more. It may have been deleted." | Matches · Add a match |
| No permission | 403 | "You don't have access to this." (no hint of what exists) | Home · Sign in as the owner |
| **Permission revoked** (share expired/revoked, partner unlinked) | `PermissionRevokedState` | "{Owner} stopped sharing this, or the link expired." — shows **when** | Make your own moments · Ask for a new link |
| Analysis failed | In-page `FailedState` | What failed (safe), what was saved, retry | Analyse again · Keep video · Report |
| Unsupported footage | In-page `UnsupportedFootageState` | Why + fix | How to film · Try another · Keep video |
| Low coverage | In-page `LowCoverageState` | "We could follow 41 % of this video" + still-valid Moments | Place court · Fix · Re-film |
| Offline | `OfflineState` banner | "You're offline — here's what you've already opened." | Retry |
| Server unreachable | Existing "Can't reach the server" screen, reworded | Friendly + what to do | Retry |
| Expired session/sign-in | Soft prompt in place | "Sign in again to keep going" — **draft preserved** | Sign in |
| Sample in an invalid state | Reset sample | — | — |

**Never:** a blank page, a raw status code, a stack trace, or "Try again" as the only option when the cause is the footage (Blueprint §12).

---

## 16. Redirects from the existing prototype

| Existing | New | Behaviour |
|---|---|---|
| `/` (Library with upload + YouTube cards + match grid) | `/` is Home; the library is `/matches`; upload is `/matches/new` | First visit after upgrade: show a one-line "Your library is now under Matches" toast |
| `/sessions/$sessionId` | `/matches/$matchId` | **301-style client redirect**, preserving `?f=` |
| `/sessions/$sessionId?f=N` | `/matches/$matchId?f=N` | Preserved |
| `/sessions/$sessionId/calibrate` | `/matches/$matchId/court` | Redirect |
| Session **tab** `Stats` | `/matches/$id/deep-dive/story` (+ Recap FactTrio for Quick) | Tab keys mapped; stored `tab` preference migrated |
| Session tab `Heatmaps` | `…/deep-dive/court` | Same |
| Session tab `Highlights` | `/matches/$id/moments` | Same |
| Session tab `Rallies` | `…/deep-dive/rallies` | Same |
| Session tab `Ask` | `…/deep-dive/ask` | Same |
| Session tab `Export` | Deep dive → Exports (Advanced/Compete) and Recap `⋯ › Export` | Same data |
| `/system` | `/admin/system` | Redirect; removed from player navigation; visible to operators only |
| Login (shared passphrase gate) | Unchanged for the operator prototype; guest-first flow replaces it for players (doc 03 §13) | Passphrase remains the *prototype* gate until accounts exist |
| API: `/api/sessions/*` | Unchanged | Routes rename in the UI only; API naming is not part of the player surface |

The `?f=` deep link, `useDeepLink`, `frameClock`, `usePlayback` and `useSession` stores are **kept**; they are the backbone of evidence navigation (D16).

---

## 17. IA test plan

### 17.1 Method
1. **Open card sort** (n ≈ 15 amateur players across the working segments; moderated 15 min): ~45 cards drawn from the feature catalogue — e.g. "My longest rally", "Shots I've tried", "How I did vs last month", "Who can see my video", "Fix a wrong winner", "Download a clip", "Compare two games", "Ask a question about the match", "Heatmap of where I stood", "Invite someone I played". Observe grouping, labels, vocabulary.
2. **Closed card sort** against the proposed top level: *Home · Matches · Moments · Progress · Together · Explore · Settings* — measure mis-placements.
3. **Tree test** (≥ 30 remote participants; Treejack-style) on the sitemap of §1.
4. **First-click test** on the mobile Home and Recap wireframes.
5. **Moderated prototype walk-through** (Journeys A–F, E, new-invite) — covered by the usability tasks in Doc 12.

### 17.2 Tree-test tasks and pass criteria

| # | Task (phrased as the player would) | Correct destination | Pass bar |
|---|---|---|---|
| T1 | "You want to watch the best rally from last night." | Matches › match › Recap hero, **or** Moments | ≥ 85 % direct success |
| T2 | "Find out if you're getting better." | Progress | ≥ 80 % |
| T3 | "You think the system counted the wrong winner." | Match › Fix this / Review | ≥ 75 % |
| T4 | "Send a clip to the person you played." | Moment › Share | ≥ 80 % |
| T5 | "Check who can see your video." | Avatar › Privacy | ≥ 80 % |
| T6 | "See where on the court you spent your time." | Match › Deep dive › Court | ≥ 70 % (expected lower; Preview) |
| T7 | "Compare this game with last week's." | Deep dive › Compare / Progress | ≥ 70 % |
| T8 | "Ask a question about the match." | Match › Deep dive › Ask | ≥ 80 % |
| T9 | "Delete a match you don't want." | Match › ⋯ › Delete | ≥ 85 % |
| T10 | "Stop all reminders." | Avatar › Settings › Notifications | ≥ 85 % |
| T11 | "Add your first match." | ＋ | ≥ 95 % |
| T12 | "Change how technical the report is." | Header Depth / Preset | ≥ 80 % |

### 17.3 Success measures
Directness (no backtracking), time on task, first-click correctness, label-comprehension interviews ("What do you expect under *Moments*?"), and **vocabulary match** (do players say "match / moment / rally" naturally?). A label with < 70 % correct first click is renamed and re-tested.

### 17.4 Decisions the test can overturn
- Whether **Progress** and **My story** belong together (D-IA-1).
- Whether **Together** should be a nav item while **Not yet** (D-IA-2) — alternative: Home card only.
- Whether **Explore** earns a nav slot on desktop or lives as a Home card only (D-IA-3).
- Whether **Moments** and **Matches** are understood as different (D-IA-4) — alternative: single "Library" with a toggle.
- Whether "Deep dive" is the right name (alternatives to test: "Full game", "Analysis").

---

## 18. Telemetry (navigation)

`nav_item_clicked {item, surface}` · `add_match_clicked {from}` · `preset_changed` · `depth_changed` · `purpose_changed` · `show_all_clicked {surface}` · `deep_dive_opened {from}` · `return_to_analysis_clicked` · `shortcut_used {key}` (key only) · `search_used {scope, result_count}` · `not_found_viewed {kind}` · `permission_revoked_viewed` · `redirect_legacy_route {from}` · `ready_dot_cleared`.

Context on every event: route name (not URL with ids), preset, depth, device class, experiment assignment. No match titles, nicknames or tokens.

---

## 19. Acceptance criteria

| ID | Criterion |
|---|---|
| AC-IA-1 | Home shows ≤ 5 modules; none are a score, streak, rank or inactivity message |
| AC-IA-2 | Each Home situation × preset renders exactly the modules in §9.2 (snapshot tests) |
| AC-IA-3 | The ＋ AddMatchButton is reachable in one tap from every signed-in route |
| AC-IA-4 | Mobile BottomBar has exactly five slots with visible labels and does not cover primary actions |
| AC-IA-5 | Preset, Purpose and Depth can be changed from the match header in ≤ 2 taps; "Shown because… Change · Reset · Show all" is always present |
| AC-IA-6 | Hidden surfaces are reachable via "Show all"; evidence ("Watch this") and the coverage line exist at every depth |
| AC-IA-7 | `?f=` deep links work on every match route and survive reload and redirect |
| AC-IA-8 | Back restores filters and scroll on Matches, Moments, Rallies and Progress |
| AC-IA-9 | Opening a Moment from analysis shows "Return to analysis" and returns to the same filtered view |
| AC-IA-10 | Legacy URLs (`/sessions/...`, `/calibrate`, `/system`) redirect as in §16 with `?f=` preserved |
| AC-IA-11 | Share URLs contain only an opaque token; Open Graph previews are generic and `noindex` |
| AC-IA-12 | A viewer-role shell has no player navigation and no Fix/Share controls |
| AC-IA-13 | Revoked/expired access renders `PermissionRevokedState` on next load; no cached video is served |
| AC-IA-14 | Every error/empty route offers at least one next action; none is a blank page |
| AC-IA-15 | Keyboard: all existing video shortcuts unchanged; added shortcuts do not fire inside inputs; shortcuts can be disabled |
| AC-IA-16 | Route changes move focus to the page `h1` and announce the page name |
| AC-IA-17 | Deep dive tabs hidden by depth are absent (not disabled); "Show all" restores them |
| AC-IA-18 | `Together` shows a **Soon** tag and a placeholder while doubles is Not yet; no broken link |
| AC-IA-19 | Tree-test pass bars of §17.2 are met before the IA is frozen for build |
| AC-IA-20 | `/admin/system` is not linked from the player's navigation |
