# 08 — Visual Design System

**Status:** Build spec for the amateur product's look and feel. Decisions cited as **D#** (file 00). Components are named per file 07. Words per file 09.
**One-line summary:** a **calm, warm, sport-forward daylight product** (Court Daylight) that drops into a **dark, video-first theatre** (Arena Night) the moment footage or analysis takes over — on **one token set**, with **"you" as the anchor colour** and **certainty expressed in icon + word + shape**.

All colour numbers below were **computed**, not estimated: WCAG 2.x relative-luminance contrast, and CIE76 ΔE after Machado-2009 colour-vision-deficiency simulation (severity 1.0) in linear sRGB. The script is in Appendix A so engineering can re-run it whenever a hex changes.

---

## 0. The three sources, reconciled

| Topic | v1 spec (Design Spec §04) | Blueprint §10 | Existing app (`styles.css`) | **Decision** |
|---|---|---|---|---|
| Canvas | warm off-white | white surface `#FFF`, alt `#F4F6F8` | dark mat green `#103129` | **Daylight** canvas warm `#F6F3EC`, white cards; **Night** keeps the existing mat greens (D13) |
| Accent | one vivid badminton accent + a cool analytics accent | court teal `#0B6E6E` primary | `signal #3DDC97` (system/AI only) | Primary = **court teal `#0B6E6E`** (light). **`--you`** is a separate teal-green so "you" is never confused with a button. `signal` is demoted to a *live/processing* dot (`--live`) |
| Green | reserved for verified positive | `#166534` for "Strength" with ✓ | signal green used decoratively | Green = **strength only** (with ✓ and the word) |
| Amber vs red | amber = uncertainty/attention; red = destructive/error only | amber opportunity, **not red** | `caution #E8B04A`, `alert #F0605D` | Same: amber `◆` for "something to look at"; red only for **system errors and destructive actions** |
| Uncertainty | amber | slate `#475569` + **hatch pattern** for missing | `.band-*` solid/outlined/dashed | **Slate + hatch** (`--uncertain`) for not-enough/partial; amber stays for opportunity |
| Corrected | — | violet `#6D28D9` + pencil | animation only | Violet `✎` kept |
| Player colours | — | — | P1 blue `#4290E0` / P2 orange `#E2701F` (validated protan ΔE 25.5) | Kept **only in Deep dive compare** (`variant="compare"`); everywhere else **you / partner / others** (D8) |
| Typeface | highly readable UI sans | humanist sans, tabular numerals | **Archivo Variable** (wdth+wght) | **Keep Archivo Variable**; it already gives tabular figures and the condensed "scoreboard" numerals |
| Radius | rounded cards, restrained borders | 12 px | 14 px (`--radius-card`) | Keep **14 px** cards (continuity), 10 px controls |
| Celebration | no confetti for ordinary metrics; restrained for records | none for winning/unverified | none | **One** restrained, skippable moment for a *Checked* personal best (§9.3) |

---

## 1. Brand personality

**Rally feels like:** a thoughtful friend who filmed your game, watched it with you, and only says what they can show you.

| It is | It is **not** |
|---|---|
| **Calm** — generous space, quiet chrome, one primary action per view | A casino or loot app: no coins, levels, flames, shields, confetti storms |
| **Credible** — numbers carry units and `n of m`; claims carry a "Watch this" | A surveillance dashboard: no dense red/green grids, no pose skeletons by default, no "performance score" |
| **Warm** — off-white paper, real thumbnails, plain words | A pro-broadcast clone: Arena Night's drama is for the *video theatre* only |
| **Sport-forward** — the court, the shuttle, rally rhythm are the visual motifs | Generic fitness-app: no neon gradients, no athletes in stock photos |
| **Respectful** — you are the hero of every chart; others are quiet | Competitive by default: no leaderboards, no crowns, no "winner" colour |
| **Honest** — Preview, hatched gaps, "not enough to say" are *designed* states | Falsely precise: no gauges, no smooth fake trends, no decimals beyond what the data supports |

**Three adjectives for design reviews:** *calm, credible, courtside.*

**Visual motifs (use sparingly):** court-line corner, the shuttle mark (existing `Logo`), a rally "heartbeat" strip (rally marks along a line), a dashed outline for "not sure".

---

## 2. The "You" colour concept (D8)

The product's most important colour decision: **identity colours belong to relationships, not to engine tracks.**

| Role | Meaning | Mark (shape) | Where it appears |
|---|---|---|---|
| **You** `--you` | You, always | filled **circle** | your dot on court maps, your lane, your heat ramp, your rally ring, "You" labels |
| **Partner** `--partner` | Your doubles partner (**Not yet**; reserved) | **diamond** | pair surfaces |
| **Others** `--other` | Opponent(s), other people | **square**, neutral charcoal/slate | opponent dots, opponent heat |
| P1 `--p1` / P2 `--p2` | Engine tracks (near / far side at start) | circle / square | **only** Deep dive with `variant="compare"` and Advanced tables |

**Why:** an amateur reading a heat map must never have to remember "P2 is orange, I'm P2 this time". The engine's `P1/P2` swap meaning per match; the *person* does not. `useMe(matchId)` (file 07 §3.3) resolves which track is you; a single helper `roleColor(pid, me)` returns `--you`, `--other` or the compare hues.

**Rules**
1. `--you` never appears on buttons, links or status tags. Buttons use `--primary` (teal), links `--primary` underlined. (They are intentionally *near* each other in hue so the brand is coherent, but differ in lightness: `--you` `#0B7466` vs `--primary` `#0B6E6E` — shape and context separate them: you = dots/lines/fills in charts; primary = solid button fill.)
2. `--other` is **dark charcoal in light theme, mid slate in dark theme** — chosen by computation (§4) so it separates from `--you` under colour-vision deficiency by lightness, not hue.
3. Opponent marks are never "bad red"; there is no good/bad coding of you versus them (D6).
4. In a shared/exported image, "You" is replaced by the nickname and the colour roles stay.

---

## 3. Tokens — one set, two themes

### 3.1 Court Daylight (light, default on light-mode systems)

Contrast = WCAG 2.x ratio. "Need" is the threshold for the role (text 4.5, marks/UI 3).

**Surfaces, text, borders**

| Token | Hex | Use |
|---|---|---|
| `--canvas` | `#F6F3EC` | page background (warm paper) |
| `--surface` | `#FFFFFF` | cards, sheets |
| `--surface-raised` | `#EDE8DC` | hovered/selected row, chips background, empty-state panels |
| `--edge` | `#D6CFBF` | hairline card borders (decorative) |
| `--edge-strong` | `#7E7869` | input borders, focus-adjacent UI edges |
| `--ink` | `#14211D` | primary text (matches the PDF report `INK`) |
| `--muted` | `#47544F` | secondary text |
| `--faint` | `#5E6B66` | tertiary text, axis labels (still ≥ 4.5:1) |
| `--primary` | `#0B6E6E` | primary action, links (court teal) |
| `--primary-hover` | `#095A5A` | hover/pressed |
| `--on-primary` | `#FFFFFF` | text on primary |

**Identity and status**

| Token | Hex | Role (always with icon + word) |
|---|---|---|
| `--you` | `#0B7466` | you |
| `--partner` | `#A415C1` | partner (reserved) |
| `--other` | `#3A3F4A` | others |
| `--evidence` | `#1D4ED8` | "Watch this", definitions, links into footage |
| `--strength` | `#166534` | ✓ Strength |
| `--opportunity` | `#9A4A07` | ◆ Something to look at (deepened from Blueprint `#B45309` to pass on tints) |
| `--uncertain` | `#475569` | ? not enough, Preview, hatched gaps |
| `--corrected` | `#6D28D9` | ✎ Corrected |
| `--error` | `#B91C1C` | system errors and destructive actions **only** |
| `--court-floor` | `#E4EFE6` | court map floor (light) |
| `--court-line` | `#1F6F5B` | court lines (light) |
| `--p1` / `--p2` | `#2D7FD3` / `#C55A12` | Deep dive compare marks (light variants; text uses ink) |

**Computed contrast — Court Daylight**

| Pair | Ratio | Need | Result |
|---|---|---|---|
| `--ink` `#14211D` on `--canvas` `#F6F3EC` | 14.98 | 4.5 | pass |
| `--ink` on `--surface` `#FFFFFF` | 16.60 | 4.5 | pass |
| `--muted` `#47544F` on `--canvas` | 7.15 | 4.5 | pass |
| `--muted` on `--surface` | 7.93 | 4.5 | pass |
| `--faint` `#5E6B66` on `--canvas` | 5.03 | 4.5 | pass |
| `--faint` on `--surface-raised` `#EDE8DC` | 4.56 | 4.5 | pass |
| `--on-primary` `#FFFFFF` on `--primary` `#0B6E6E` | 6.05 | 4.5 | pass |
| `--primary` on `--canvas` (links) | 5.46 | 4.5 | pass |
| `--primary` on `--surface` | 6.05 | 4.5 | pass |
| `--evidence` `#1D4ED8` on `--surface` | 6.70 | 4.5 | pass |
| `--strength` `#166534` on `--surface` | 7.13 | 4.5 | pass |
| `--opportunity` `#9A4A07` on `--surface` | 6.26 | 4.5 | pass |
| `--opportunity` on `--canvas` | 5.65 | 4.5 | pass |
| `--uncertain` `#475569` on `--surface` | 7.58 | 4.5 | pass |
| `--corrected` `#6D28D9` on `--surface` | 7.10 | 4.5 | pass |
| `--error` `#B91C1C` on `--surface` | 6.47 | 4.5 | pass |
| `--you` `#0B7466` on `--surface` | 5.67 | 4.5 | pass |
| `--partner` `#A415C1` on `--surface` | 6.08 | 4.5 | pass |
| `--other` `#3A3F4A` on `--surface` | 10.55 | 4.5 | pass |
| `--edge-strong` `#7E7869` on `--surface` | 4.40 | 3 (UI) | pass |
| `--edge-strong` on `--canvas` | 3.97 | 3 (UI) | pass |
| `--court-line` on `--court-floor` | 5.11 | 3 | pass |
| `--p1` `#2D7FD3` on `--surface` | 4.13 | 3 (marks) | pass — **not for text** |
| `--p2` `#C55A12` on `--surface` | 4.33 | 3 (marks) | pass — **not for text** |
| `--you` on `--canvas` | 5.12 | 3 | pass |
| `--partner` on `--canvas` | 5.48 | 3 | pass |

**Status text on its own 12 % tint** (chips and banners)

| Status | Ratio | Result |
|---|---|---|
| strength on tint `#e3ede7` | 5.95 | pass |
| opportunity on tint `#f3e9e1` | 5.23 | pass |
| uncertain on tint `#e9ebed` | 6.34 | pass |
| corrected on tint `#ede5fa` | 5.82 | pass |
| error on tint `#f7e4e4` | 5.29 | pass |
| evidence on tint `#e4eafa` | 5.57 | pass |

> Finding that changed a value: `--you` as `#0B7A6C` read 4.43 on its 12 % tint (fail); darkening to `#0B7466` fixes it (5.07 on an 8 % tint). **Rule: `--you` tints are ≤ 8 %** (`bg-you/8`). Blueprint's `--opportunity #B45309` was deepened to `#9A4A07` to keep ≥ 5.2 on tint.

### 3.2 Arena Night (dark; video theatre and Deep dive)

The existing dark palette is kept **as is** for continuity and extended with semantic roles.

| Token | Hex | Existing name | Use |
|---|---|---|---|
| `--canvas` | `#103129` | `--color-mat` | page background |
| `--well` | `#0C2620` | `--color-mat-deep` | video well, inputs, deepest layer (**same in both themes** for the theatre) |
| `--surface` | `#18221F` | `--color-stand` | cards/panels |
| `--surface-raised` | `#1F2B27` | `--color-stand-raised` | hover/raised |
| `--edge` | `#2A3833` | `--color-seam` | hairlines |
| `--edge-strong` | `#74877F` | `--color-line-3` | UI edges |
| `--ink` | `#E8EFEA` | `--color-line` | primary text, court lines |
| `--muted` | `#A9BAB2` | `--color-line-2` | secondary |
| `--faint` | `#8DA098` | (new; was `line-3 #74877F`, 4.3:1 on surface — see note) | tertiary text (≥ 4.5) |
| `--primary` | `#E8EFEA` | (button `bg-line`) | primary button fill |
| `--on-primary` | `#0C2620` | (`text-mat-deep`) | text on primary |
| `--you` | `#4FD6C4` | new | you |
| `--partner` | `#E27BF2` | new | partner (reserved) |
| `--other` | `#7C8794` | new | others |
| `--evidence` | `#7DA7FF` | new | "Watch this", links |
| `--strength` | `#5FD38A` | new | strength |
| `--opportunity` | `#F0B454` | `--color-caution` (`#E8B04A`) | something to look at |
| `--uncertain` | `#9FB0C4` | new | not enough / preview / hatched |
| `--corrected` | `#B79CFF` | new | corrected |
| `--error` | `#F26B68` | `--color-alert` (`#F0605D`) | system errors / destructive (lightened for tint contrast) |
| `--live` | `#3DDC97` | `--color-signal` | the pulsing "working" dot only; always beside a word |
| `--shuttle` | `#FFFFFF` | `--color-shuttle` | the shuttle, playhead, the only pure white |
| `--court-floor` | `#14382F` | `drawCourt` default | court map floor |
| `--court-line` | `rgba(232,239,234,.55)` | `drawCourt` default | court lines |
| `--p1` / `--p2` | `#4290E0` / `#E2701F` | `--color-p1/p2` | compare marks |

**Computed contrast — Arena Night**

| Pair | Ratio | Need | Result |
|---|---|---|---|
| `--ink` `#E8EFEA` on `--canvas` `#103129` | 12.03 | 4.5 | pass |
| `--ink` on `--surface` `#18221F` | 13.95 | 4.5 | pass |
| `--ink` on `--well` `#0C2620` | 13.68 | 4.5 | pass |
| `--muted` `#A9BAB2` on `--canvas` | 6.93 | 4.5 | pass |
| `--muted` on `--surface` | 8.04 | 4.5 | pass |
| `--faint` `#8DA098` on `--canvas` | 5.10 | 4.5 | pass |
| `--faint` on `--surface` | 5.91 | 4.5 | pass |
| `--on-primary` `#0C2620` on `--primary` `#E8EFEA` | 13.68 | 4.5 | pass |
| `--evidence` `#7DA7FF` on `--surface` | 6.87 | 4.5 | pass |
| `--strength` `#5FD38A` on `--surface` | 8.68 | 4.5 | pass |
| `--opportunity` `#F0B454` on `--surface` | 8.82 | 4.5 | pass |
| `--uncertain` `#9FB0C4` on `--surface` | 7.36 | 4.5 | pass |
| `--corrected` `#B79CFF` on `--surface` | 7.16 | 4.5 | pass |
| `--error` `#F26B68` on `--surface` | 5.50 | 4.5 | pass |
| `--you` `#4FD6C4` on `--surface` | 9.13 | 4.5 | pass |
| `--partner` `#E27BF2` on `--surface` | 6.49 | 4.5 | pass |
| `--other` `#7C8794` on `--surface` | 4.47 | 3 (marks) | pass |
| `--edge-strong` `#74877F` on `--surface` | 4.28 | 3 (UI) | pass |
| `--live` `#3DDC97` on `--surface` | 9.23 | 3 | pass |
| `--p1` on `--surface` | 4.89 | 3 | pass |
| `--p2` on `--surface` | 5.10 | 3 | pass |
| `--you` / `--partner` / `--other` on `--well` | 8.94 / 6.36 / 4.38 | 3 | pass |

**Status text on its own 12 % tint (dark)**

| Status | Ratio | Result |
|---|---|---|
| strength on `#21372c` | 6.78 | pass |
| opportunity on `#323425` | 6.87 | pass |
| uncertain on `#283333` | 5.88 | pass |
| corrected on `#2b313a` | 5.75 | pass |
| error on `#322b28` | 4.68 | pass (was 4.41 with `#F0605D` — lightened) |
| evidence on `#24323a` | 5.55 | pass |

> Note on the old `--color-line-3 #74877F`: it is 4.28:1 on `--surface` — fine for UI edges (≥ 3) but **below 4.5 for text**. Existing code uses `text-line-3` for small text (e.g. timeline "Not analysed yet", axis labels). Migration replaces text uses with `--faint #8DA098` (5.91). Edges keep `--edge-strong`.

### 3.3 Drop-in CSS (extends `apps/web/src/styles.css`; no existing name breaks)

Add **below** the existing `@theme` block. The existing `@theme` (`--color-mat`, `-mat-deep`, `-stand`, `-stand-raised`, `-seam`, `-line`, `-line-2`, `-line-3`, `-p1`, `-p2`, `-shuttle`, `-signal`, `-alert`, `-caution`, radii, `--ease-snap`, font) is **left untouched**: every current screen stays Arena Night exactly as today.

```css
/* ───────── tokens.css — import after @import "tailwindcss" and the existing @theme ───────── */

/* Raw theme variables. Light is the default; dark applies to [data-theme="dark"] subtrees
   and, when no explicit choice exists, to prefers-color-scheme: dark. */
:root,
:root[data-theme="light"] {
  color-scheme: light;
  --c-canvas: #F6F3EC;   --c-well: #0C2620;
  --c-surface: #FFFFFF;  --c-surface-raised: #EDE8DC;
  --c-edge: #D6CFBF;     --c-edge-strong: #7E7869;
  --c-ink: #14211D;      --c-muted: #47544F;   --c-faint: #5E6B66;
  --c-primary: #0B6E6E;  --c-primary-hover: #095A5A;  --c-on-primary: #FFFFFF;
  --c-you: #0B7466;      --c-partner: #A415C1; --c-other: #3A3F4A;
  --c-evidence: #1D4ED8; --c-strength: #166534; --c-opportunity: #9A4A07;
  --c-uncertain: #475569; --c-corrected: #6D28D9; --c-error: #B91C1C;
  --c-live: #0B7466;     --c-shuttle: #FFFFFF;
  --c-court-floor: #E4EFE6; --c-court-line: #1F6F5B;
  --c-p1: #2D7FD3;       --c-p2: #C55A12;
  --shadow-pop: 0 8px 24px rgb(20 33 29 / 0.14), 0 1px 0 rgb(20 33 29 / 0.06);
}
:root[data-theme="dark"],
[data-theme="dark"] {           /* video theatre / Deep dive subtree */
  color-scheme: dark;
  --c-canvas: #103129;   --c-well: #0C2620;
  --c-surface: #18221F;  --c-surface-raised: #1F2B27;
  --c-edge: #2A3833;     --c-edge-strong: #74877F;
  --c-ink: #E8EFEA;      --c-muted: #A9BAB2;   --c-faint: #8DA098;
  --c-primary: #E8EFEA;  --c-primary-hover: #FFFFFF;  --c-on-primary: #0C2620;
  --c-you: #4FD6C4;      --c-partner: #E27BF2; --c-other: #7C8794;
  --c-evidence: #7DA7FF; --c-strength: #5FD38A; --c-opportunity: #F0B454;
  --c-uncertain: #9FB0C4; --c-corrected: #B79CFF; --c-error: #F26B68;
  --c-live: #3DDC97;     --c-shuttle: #FFFFFF;
  --c-court-floor: #14382F; --c-court-line: rgb(232 239 234 / 0.55);
  --c-p1: #4290E0;       --c-p2: #E2701F;
  --shadow-pop: 0 8px 24px rgb(0 0 0 / 0.45);
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) {      /* system dark, no explicit choice */
    color-scheme: dark;
    --c-canvas: #103129; --c-well: #0C2620; --c-surface: #18221F; --c-surface-raised: #1F2B27;
    --c-edge: #2A3833; --c-edge-strong: #74877F;
    --c-ink: #E8EFEA; --c-muted: #A9BAB2; --c-faint: #8DA098;
    --c-primary: #E8EFEA; --c-primary-hover: #FFFFFF; --c-on-primary: #0C2620;
    --c-you: #4FD6C4; --c-partner: #E27BF2; --c-other: #7C8794;
    --c-evidence: #7DA7FF; --c-strength: #5FD38A; --c-opportunity: #F0B454;
    --c-uncertain: #9FB0C4; --c-corrected: #B79CFF; --c-error: #F26B68;
    --c-live: #3DDC97; --c-shuttle: #FFFFFF;
    --c-court-floor: #14382F; --c-court-line: rgb(232 239 234 / 0.55);
    --c-p1: #4290E0; --c-p2: #E2701F;
    --shadow-pop: 0 8px 24px rgb(0 0 0 / 0.45);
  }
}

/* Semantic utilities: bg-canvas, text-ink, border-edge, text-you, bg-you/8 … (opacity modifiers work) */
@theme inline {
  --color-canvas: var(--c-canvas);          --color-well: var(--c-well);
  --color-surface: var(--c-surface);        --color-surface-raised: var(--c-surface-raised);
  --color-edge: var(--c-edge);              --color-edge-strong: var(--c-edge-strong);
  --color-ink: var(--c-ink);                --color-muted: var(--c-muted);   --color-faint: var(--c-faint);
  --color-primary: var(--c-primary);        --color-primary-hover: var(--c-primary-hover);
  --color-on-primary: var(--c-on-primary);
  --color-you: var(--c-you);                --color-partner: var(--c-partner); --color-other: var(--c-other);
  --color-evidence: var(--c-evidence);      --color-strength: var(--c-strength);
  --color-opportunity: var(--c-opportunity); --color-uncertain: var(--c-uncertain);
  --color-corrected: var(--c-corrected);    --color-error: var(--c-error);
  --color-live: var(--c-live);
  --color-court-floor: var(--c-court-floor); --color-court-line: var(--c-court-line);
  --shadow-pop: var(--shadow-pop);
}

/* Typography, radius, spacing, motion, breakpoints */
@theme {
  --font-sans: "Archivo Variable", "Archivo", ui-sans-serif, system-ui, sans-serif; /* unchanged */
  --text-xs: 0.8125rem;   /* 13 — metadata only */
  --text-sm: 0.875rem;    /* 14 */
  --text-base: 1rem;      /* 16 — body, never smaller */
  --text-lg: 1.125rem;    /* 18 */
  --text-xl: 1.375rem;    /* 22 */
  --text-2xl: 1.75rem;    /* 28 */
  --text-3xl: 2.25rem;    /* 36 */
  --text-hero: 3.5rem;    /* 56 — one hero number per view */
  --radius-card: 14px;    /* unchanged */
  --radius-control: 10px;
  --radius-sheet: 20px;
  --radius-chip: 999px;   /* unchanged */
  --ease-snap: cubic-bezier(0.2, 0.9, 0.25, 1);  /* unchanged */
  --duration-fast: 150ms;
  --duration-base: 250ms;
  --breakpoint-md: 48rem;   /* 768  */
  --breakpoint-lg: 64rem;   /* 1024 */
  --breakpoint-xl: 90rem;   /* 1440 */
}
@media (prefers-reduced-motion: reduce) {
  :root { --duration-fast: 0ms; --duration-base: 0ms; }
}

/* Density (tied to the Depth switcher; set data-depth on the report root) */
:root, [data-depth="guided"] { --d-pad: 16px; --d-gap: 16px; --d-row: 44px; --d-body: 1rem; }
[data-depth="quick"]    { --d-pad: 24px; --d-gap: 24px; --d-row: 56px; --d-body: 1.125rem; }
[data-depth="advanced"] { --d-pad: 12px; --d-gap: 12px; --d-row: 36px; --d-body: 0.9375rem; }

/* Certainty shapes (never colour alone) */
.check-checked      { border: 1.5px solid currentColor; background: color-mix(in oklab, var(--c-ink) 8%, transparent); }
.check-looks-right  { border: 1.5px solid currentColor; }
.check-worth-a-look { border: 1.5px dashed currentColor; }
.check-not-enough   { border: 1.5px dashed currentColor; background: var(--hatch); }
:root { --hatch: repeating-linear-gradient(45deg, transparent 0 4px,
                color-mix(in oklab, var(--c-uncertain) 35%, transparent) 4px 5px); }
.hatch { background-image: var(--hatch); }
```

> Implementation note: Tailwind v4 `@theme inline` emits utilities that reference the variables at use-site, so wrapping a subtree in `data-theme="dark"` re-themes every new-token utility inside it. Old tokens (`bg-mat`, `text-line`, …) keep their fixed dark hexes, so legacy screens render unchanged until they migrate.

### 3.4 Old → new name map (migration aid)

| Existing | New semantic | Notes |
|---|---|---|
| `bg-mat` / `--color-mat` | `bg-canvas` | page |
| `bg-mat-deep` / `--color-mat-deep` | `bg-well` | video well and inputs stay dark in both themes |
| `bg-stand` (`.panel` background) | `bg-surface` | `.panel` becomes `bg-surface border-edge` |
| `bg-stand-raised` | `bg-surface-raised` | |
| `border-seam` | `border-edge` | |
| `text-line` | `text-ink` | primary text |
| `text-line-2` | `text-muted` | |
| `text-line-3` (text) | `text-faint` | **text only**; edge uses stay `border-edge-strong` |
| `bg-line text-mat-deep` (primary `Button`) | `bg-primary text-on-primary` | teal in light, near-white in dark |
| `text-signal`, `bg-signal` | `text-live`, `bg-live` | pulsing dot only; links use `text-primary` |
| `text-alert`, `border-alert/…` | `text-error`, `border-error/…` | system errors, destructive only |
| `text-caution`, `bg-caution/10` | `text-opportunity`, `bg-opportunity/10` | banners for partial/low coverage |
| `bg-p1`, `bg-p2`, `PLAYER_HEX` | unchanged | **compare variant only**; elsewhere `roleColor(pid, me)` |
| `.numerals`, `.condensed`, `.tabular`, `.panel` | unchanged | `.panel` re-skinned via the map |
| `.band-confirmed/-probable/-uncertain/-unknown` | `.check-checked/-looks-right/-worth-a-look/-not-enough` | keep old classes as aliases for one release |

---

## 4. Colour-vision-deficiency verification (you / partner / other)

Method: Machado 2009 matrices (protanopia, deuteranopia, tritanopia, severity 1.0) applied in linear sRGB, then **CIE76 ΔE** in Lab. Targets: ΔE ≥ 15 between any two identity colours under every simulation (they also differ by **shape**: circle / diamond / square, and by lightness), ΔE ≥ 20 where a pair is the primary comparison (you vs other).

**Court Daylight**

| Pair | Normal | Protan | Deutan | Tritan | Min |
|---|---|---|---|---|---|
| you `#0B7466` / partner `#A415C1` | 118 | 70 | 50 | 74 | **50** |
| you / other `#3A3F4A` | 36 | 22 | 16 | 31 | **16** |
| partner / other | 88 | 60 | 48 | 52 | **48** |

**Arena Night**

| Pair | Normal | Protan | Deutan | Tritan | Min |
|---|---|---|---|---|---|
| you `#4FD6C4` / partner `#E27BF2` | 107 | 57 | 35 | 85 | **35** |
| you / other `#7C8794` | 46 | 28 | 21 | 45 | **21** |
| partner / other | 69 | 44 | 34 | 47 | **34** |

**Compare marks:** P1 `#4290E0` / P2 `#E2701F` ΔE = 114 normal, 102 protan, 113 deutan, 103 tritan (min 102) — the existing validated pair.

**What the numbers decided**
- First proposal (`you #0B7A6C` / `partner #B0306A` berry / `other #5B6670` slate) **failed**: teal vs berry collapsed to ΔE 5.9 under deuteranopia and teal vs slate to 4.5 — they differ in hue only. Fix: **separate by lightness** — `other` became dark charcoal `#3A3F4A` in light (mid slate `#7C8794` in dark) and `partner` moved to an orchid `#A415C1` whose deutan ΔE vs `you` is 50.
- Light-theme `you` vs `other` is the tightest pair (16 under deutan). Mitigation is **mandatory shape redundancy** (circle vs square) and a legend that is always visible; never rely on colour alone (R5).
- `--you` vs `--live` (`#3DDC97`) in dark has tritan ΔE 4.3: they never co-occur as marks (live is a pulsing dot beside the word "Analysing").

---

## 5. Typography

**Face:** Archivo Variable (already installed; `wdth` 62–125, `wght` 100–900). Keep `font-variation-settings: "wdth" 100` as the body default. One family, three personalities through the width axis: normal text (wdth 100), condensed labels (wdth 80, `.condensed`), scoreboard numerals (wdth 62 + wght 800, `.numerals`).

**Scale** (mobile → desktop)

| Role | Size / line | Weight | Use |
|---|---|---|---|
| Hero number | 56 / 56 (`--text-hero`), `.numerals` | 800 | **one per view**, only a Checked/defined metric (e.g. "14 shots") |
| H1 | 28→36 / 1.15 | 700 | page title |
| H2 | 22 / 1.25 | 650 | section ("Moments", "My game") |
| H3 | 18 / 1.3 | 600 | card title |
| Body | 16 / 1.5 (Quick 18 / 1.55) | 400 | all reading text; measure 65–75 characters |
| Label | 14 / 1.4 | 500 | buttons, chips, form labels |
| Meta | 13 / 1.4 | 450 | timestamps, n-of-m footers (≥ 4.5:1 only via `--muted`/`--faint`) |
| Axis / legend | 13 (never < 12) | 450 | chart text; rendered in SVG/DOM, not canvas where possible |

Rules: body text is never below 16 px; interactive labels never below 14 px; **12 px exists only in dense Advanced tables** (the existing `text-[11px]` in `Timeline` and `ScoreBug` must go up to 13). All numbers use **tabular figures** (`.tabular`) so columns align; the hero number and score bug use `.numerals`.

**Number and unit formatting**

| Case | Format | Example |
|---|---|---|
| Counts with a unit | number + space + noun | `14 shots`, `9 rallies` |
| Rates | **`n of m`**, percentage optional and secondary | `6 of 9 long rallies` (not "67 %" alone) |
| Comparisons | difference in the metric's unit | `+3 shots since last match` |
| Duration | `m:ss` for clips (`0:19`), words for totals | `12 minutes of play`, "about 12 minutes" |
| Estimates | prefix "about" and round to the data's precision | `about 4 minutes left`; never `4.37` |
| Missing | em dash `—` with `aria-label` of the reason | `—` (not measured) |
| Ranges | en dash, units once | `9–14 shots` |

One hero number per view prevents the "metric wall"; every other figure is body size. Never animate counting-up numbers (implies false precision).

---

## 6. Spacing, radius, elevation

| Scale | Values |
|---|---|
| Space (4-pt) | 4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 |
| Card padding | 16 (Guided), 24 (Quick), 12 (Advanced) — `--d-pad` |
| Section gap | 32 mobile, 48 desktop; page gutters 16 / 24 / 32 |
| Radius | cards 14, controls 10, chips 999, bottom sheets 20 (top corners), video 14 |
| Elevation | **flat by default** (1 px `--edge` border). `--shadow-pop` only for popovers, sheets, menus. Dark theme relies on border, not shadow |
| Touch targets | **≥ 44 × 44 px** (recommended; WCAG 2.2 AA floor is 24). The existing `IconButton size-9` (36 px) becomes `size-11` below `lg` |
| Focus ring | 2 px `--primary` (light) / `--live`→`--ink` (dark) with 2 px offset; never removed. The existing `outline: 2px solid var(--color-signal)` stays for legacy |

---

## 7. Layout grid and breakpoints

| Width | Name | Columns | Gutters | Chrome |
|---|---|---|---|---|
| 360 | design minimum (phone) | 4 | 16 | `BottomBar`, single column, bottom sheets |
| 768 | tablet (`md`) | 8 | 24 | `BottomBar` or collapsed rail; 2-column cards |
| 1024 | desktop (`lg`) | 12 | 24 | `SideNav` (240 px), report becomes two-column: sticky video/hero left, narrative right |
| 1440 | wide (`xl`) | 12 (max content 1280; Deep dive up to 1680, as today) | 32 | extra room for Advanced tables, never extra widgets |

- Reading column max 720 px (Quick recap) so lines stay 65–75 characters.
- **Report two-column from 1024:** left 7/12 sticky `ClipPlayer`/`HeroMoment`; right 5/12 scrolling narrative; clicking a claim seeks the video (Blueprint §7.8). Mobile: one column, sticky 56 px mini-player, `Sheet` for evidence.
- Respect `env(safe-area-inset-*)` for `BottomBar` and sheets.

---

## 8. Density modes (tied to Depth, D2)

| | Quick | Guided (default) | Advanced |
|---|---|---|---|
| Body | 18 px | 16 px | 15 px (tables 13) |
| Card padding / gap | 24 / 24 | 16 / 16 | 12 / 12 |
| Row height | 56 | 44 | 36 |
| Evidence | `Watch this` large, thumbs 16:9 | thumbs 16:10 | table rows with inline `Watch` |
| Charts | clips, at most one court map | one court map **or** one trend | distributions, small multiples, event table |
| Imagery | large posters | medium | small, many |
| Whitespace | generous | standard | tight but never < 8 px between interactive controls |

`data-depth` on the report root sets `--d-*`; components read the variables, so one component serves all three (R7).

---

## 9. Motion

### 9.1 Principles
Motion **orients**, it never excites. Allowed: state change, spatial continuity (sheet slides from where it was invoked), progress, focus. Forbidden: looping decoration, parallax, number count-ups, shake/bounce, auto-advancing carousels.

| Use | Duration | Easing |
|---|---|---|
| Hover/press, chip state | 150 ms (`--duration-fast`) | `--ease-snap` |
| Disclosure, popover, sheet | 250 ms (`--duration-base`) | `--ease-snap` |
| Page/route | none beyond an instant swap + focus move (existing `scrollRestoration` handles position) | — |
| Playhead / court dots | frame-synced (not CSS) | — |
| Skeleton shimmer | none (static skeleton); a 1.2 s opacity pulse allowed on `MatchStatusChip` dot only | — |

### 9.2 Reduced motion
`@media (prefers-reduced-motion: reduce)` sets durations to 0 (kept: the existing global rule), disables the status-dot pulse, trails on the live court dots, the first-reveal transition and the record ring. An in-app **"Keep animations off"** setting (`AccessibilityPrefs`) mirrors it for devices where the OS flag isn't set.

### 9.3 Celebration policy (non-negotiable)

| Event | Allowed motion |
|---|---|
| Match won / lost, any score | **none** — no confetti, glow, fanfare, colour flash (D6) |
| Moment saved (♡) | icon fill 150 ms; text "Saved" |
| Unverified or Preview claim ("maybe a First") | none |
| **Verified personal best** (`check = checked`, eligible per file 07 §9.2) | **one** restrained moment: the outline star's ring draws once over **600 ms**, `--you` stroke, no sound, no particles; appears only the first time the card is in view; **Skip** is implicit (any interaction cancels) and it is off under reduced motion |
| Correction applied | 1 s background tint (`corrected` keyframe in `styles.css`) *plus* the `ChangeSummaryBanner` text — the animation is a cue, the banner is the explanation |
| Return after a break | none — a plain welcome sentence |

No streak flames, level-ups, trophies, badges that "unlock", or sound effects. Video never autoplays with sound.

---

## 10. Certainty and status treatments (icon + word + shape, never colour alone)

| State | Icon | Word | Shape / fill | Colour | Use |
|---|---|---|---|---|---|
| **Checked** | double tick ✓✓ | "Checked" | solid 1.5 px border, 8 % ink tint | `--ink` (neutral — checking is not "good") | human-confirmed or corrected |
| **Looks right** | tick ✓ | "Looks right" | solid 1.5 px border, no fill | `--ink` | validated and calibrated claim type on a supported footage condition; unchecked |
| **Worth a look** | half dial ◔ | "Worth a look" | **dashed** border | `--ink` | engine `probable` |
| **Not enough to say** | question ? | "Not enough to say" | dashed border + **diagonal hatch** | `--uncertain` | `uncertain/unknown`; also missing data |
| **Preview** | outline diamond ◇ | "Preview" | small pill, 1 px border, no fill | `--uncertain` | any metric not yet validated (D10) |
| **Coverage — followed** | — | "We followed 31 of 36 rallies" | solid bar segment | `--ink`/`--you` | CoverageBar |
| **Coverage — other camera** | camera icon | "Another camera" | **dotted** segment | `--uncertain` | `scene` alt |
| **Coverage — not analysed / no court** | dash | "Not followed" | **diagonal hatch** segment | `--uncertain` | gaps |
| **Strength** | ✓ in circle | "Strength" | tint 12 % | `--strength` | InsightCard tag |
| **Something to look at** | ◆ | "Something to look at" | tint 12 % | `--opportunity` (amber, never red) | InsightCard tag |
| **Corrected** | pencil ✎ | "Corrected" | tint 12 % | `--corrected` | after a fix |
| **Not counted** | strike dash | "Not counted — warm-up" | dashed neutral | `--muted` | warm-up/replay rallies |
| **Sample / Demo** | flask/flag | "Sample" | diagonal corner ribbon + persistent banner | `--opportunity` tint | demo data |
| **Saved** | heart (filled) | "Saved" | fill + word | `--you` | MomentCard |
| **Private / Shared** | lock / link | "Private" / "Shared with…" | outline pill | `--muted` | visibility |
| **System error** | octagon | "Didn't work" | solid tint | `--error` | FailedState only |

**Hatch pattern** (`--hatch`): 45° stripes, 1 px lines every 5 px at 35 % `--uncertain`. Used for missing data on charts, hatched heat cells below the minimum sample, and not-analysed regions of timelines. A chart legend names it ("Hatched = not enough to say").

---

## 11. Court rendering spec

Source geometry stays in `lib/court.ts` (`LENGTH` 13.4 m, `WIDTH_DOUBLES` 6.1 m, singles 5.18 m, `HALF`, `NET`, `COURT_LINES`); `CourtView` (`features/court/geometry.ts`) owns metres↔pixels with `MARGIN_M = 0.7`.

| Aspect | Spec |
|---|---|
| **Orientation** | **Near side at the bottom, far side at the top, identical on every surface** (Blueprint §8.8). `CourtView` gains `orientation: "vertical" (default) | "horizontal"`; `map/unmap` swap axes. Seen from the near baseline, the court's left (x < 0) is on the **left**. The legacy horizontal layout (near end left) is kept only inside Advanced wide analyst panels, labelled |
| Aspect | vertical: width = (6.1 + 1.4) m, height = (13.4 + 1.4) m → ≈ 1 : 1.97; at 200 px wide the court is ≈ 395 px tall (fits the desktop Deep dive aside) |
| Floor | `--court-floor` (light `#E4EFE6`, dark `#14382F`) — a calm green, same family in both themes |
| Lines | `--court-line` 1.5 px (existing 1 px → 1.5 for legibility on phones), pixel-snapped (`+0.5`); singles and doubles sidelines both drawn; the active discipline's lines are 2 px |
| Net | 2 px line spanning posts ± 0.25 m (existing), label "Net" outside the court at the left edge |
| Zones | optional overlay: 3 depth × 3 width per half (ontology `court_zones`: front/mid/rear × left/centre/right) as thin dotted lines + labels on demand ("Front left") |
| Labels | "Far end — opponent side" top, "Near end — your side" bottom, both always visible (not tooltips) |
| Marks | you = filled circle `--you` (r 6, 2 px floor-colour halo — existing 8/6 dots); partner = diamond; others = square `--other`; compare uses P1 circle / P2 square |
| Trails | 1.6 s, alpha ramp 0.1→0.6 (existing); off under reduced motion |
| Shot path | dashed hitter-to-hitter (`3 3`), fading with age (existing); arrow to landing only for Advanced and labelled "where it was played back from" until true landing exists |
| Heat | single-hue ramp of the role colour; `alpha = 0.12 + 0.78·√v` (existing); cells ≤ 0.02 skipped; **insufficient-sample cells hatched**; court lines redrawn on top (existing two-pass) |
| Heat legend | five discrete steps with a text range ("fewer visits → more visits"), plus the exact meaning ("Where you stood while the shuttle was in play") |
| Legend placement | always under the map, never hover-only |
| Alternative | "Table view": 3 × 3 grid per half with counts; **text summary** sentence |
| Uncalibrated | no court is drawn; the empty state offers "Place your court" |

---

## 12. Data-visualisation grammar

**Choose the chart by the decision it supports** (Blueprint §11.2):

| Player question | Chart | Never |
|---|---|---|
| What happened in order? | `RallyTimeline` (rally strip) | a table of timestamps alone |
| Where did I play / where do I tend to be? | `CourtMap` | a bar chart of zones |
| Which shots did I play? | `ShotMix` bars (Preview) | pie chart |
| Did a measure change across comparable matches? | `TrendSmallMultiples` | a smoothed "progress curve" or gauge |
| What did I do differently here vs there? | two aligned clips (`EvidenceChip`) | percentages without clips |
| Where did a rally travel? | `CourtMap layer="rally_path"` | animated 3-D |
| For experts: event-level audit | table with filters and export | charts that hide denominators |

**Rules**

1. **Every chart answers a stated question** (its title is the question or a neutral subject — "Where you stood", not "Analytics").
2. **Axes and units:** counts start at zero; time axes are *comparable matches*, not calendar days, unless stated; unit in the axis label; `n` per point.
3. **Missing ≠ zero:** missing points are **hatched gaps**; not-measured series are omitted with a reason line.
4. **No gauges, no radar charts, no single "score" ring, no dual axes, no 3-D.**
5. **Categorical colours ≤ 5, each doubled with a shape/pattern:**

| Series | Colour (light / dark) | Shape | Pattern for fills |
|---|---|---|---|
| You | `#0B7466` / `#4FD6C4` | circle | solid |
| Partner | `#A415C1` / `#E27BF2` | diamond | cross-hatch |
| Others | `#3A3F4A` / `#7C8794` | square | diagonal hatch |
| Extra A (e.g. a reference) | `#1D4ED8` / `#7DA7FF` | triangle | dots |
| Extra B | `#9A4A07` / `#F0B454` | plus | horizontal lines |

   Deep dive compare may swap to P1/P2 (circle/square).
6. **Never red/green for good/bad.** Direction of change is a **word and a sign** ("+3 shots"), not a colour; decreases are neutral ink.
7. **Small multiples** for comparable sessions: same scale per metric, one chart per metric, a shared x order, vertical dashed break lines at camera/model changes, annotation icons for context (new camera, break, new partner).
8. **Direct labels** over legends where possible; legends are persistent and keyboard-reachable.
9. **Interaction:** hover and tap/focus reveal values; selection opens `EvidenceChip`. Nothing essential is hover-only.
10. **Text summary + data table** for every chart (R8): a sentence ("Your longest rally: 9, 11, 14 shots across three matches") and a `Table view` toggle. SVG charts set `role="img"` with `aria-labelledby` the title and `aria-describedby` the summary.
11. **Uncertainty:** ranges as light bands with the method named only in Advanced; no error bars unless defensible (rallies cluster within matches).
12. **Coverage and Preview** are part of the chart frame (a footer line and tag), not an afterthought.

---

## 13. Video theatre spec

The one place the product gets **dramatic**: video, court overlay and rally replays sit on Arena Night regardless of the user's theme (the theatre subtree is `data-theme="dark"`).

| Aspect | Spec |
|---|---|
| Stage | black letterbox (`#000`) inside a `--well` frame, 14 px radius, 16:9, `object-contain` (existing `VideoStage`); max-height 68 vh desktop |
| Chrome | quiet: 48 px control bar (56 px on touch) with large labelled buttons: Play/Pause, previous/next frame, time, speed, layers, full screen; thin `--edge` separators |
| Overlays | **off by default for amateurs**: pose skeletons, player boxes, name labels, score bug, stroke toast. On in Advanced: court lines, shuttle trail. Persisted in `localStorage` (`bai.layers`). Overlay legend appears the first time any layer is turned on |
| Caption strip | permanent text description under the video ("12-shot rally. You recover at the back corner at 0:07.") — not an overlay; readable at 18 px in Quick |
| Markers | scrubber shows clip boundaries and rally segments; the playhead is the only pure white (`--shuttle`) |
| Autoplay | never with sound; clip opened by the user plays muted, with an unmute button |
| Low data | "Preview quality" label (never implies lower analysis quality) |
| Touch | tap = play/pause (existing), double-tap = fullscreen (existing), 56 px controls, no hover-only affordance |
| Safe area | respect notches; controls above the home indicator |
| Keyboard | existing map (Space/K, ←/→, Shift+←/→, J/L, `[`/`]`, S, `.`, `?`) retained |
| States | loading (spinner, "Getting your clip ready"), preparing, error, gating pill (processing only), "Not analysed yet" chip |

---

## 14. Iconography

- **Library:** Lucide (already installed), 20 px default (24 in nav), 1.75 px stroke; icons inherit `currentColor`.
- **Always paired with a label** for critical actions (Save, Share, Fix this, Delete, Add match, Place court). Icon-only is allowed only for universally known controls (close ✕, play/pause, previous/next frame) and each has an `aria-label` + `title` (the existing `IconButton` already requires `label`).
- **Semantic set (fixed):** ✓ check, ✓✓ checked, ◔ worth a look (custom half-dial), ? not enough, ◇ preview, ◆ opportunity, ✎ corrected, ▶ watch, ♡ save, ↗ share, lock private, camera other-camera, flag sample.
- **Forbidden:** trophies, medals, crowns, flames, shields, level crests, mascots, confetti, thumbs-down on a player's own shot. "Star" appears only as an **outline** in `PersonalBestCard` and is a *label for a verified record*, not a reward.
- **Custom marks:** the shuttle `Logo` (existing SVG: shuttle from above, `--signal` arc → recolour arc to `--primary` in light); the court-corner glyph for "Place your court".

---

## 15. Imagery

- **Real match thumbnails** (existing `Thumb`: a frame ~35 % in, from the sprite sheet) for matches and moments; never stock athletes. A moment's poster is the frame at the rally's peak (the middle shot) when the sprite has it.
- **Privacy in imagery:** optional **face/bystander blur** (blurred copy for share/export when the backend supports it); thumbnails in shared contexts show the blurred version by default; nicknames, not real names, on exports.
- **Illustration** (empty/partial/failed): simple line art built from court lines, a shuttle, a film strip, a dashed circle with "?" — in `--faint` on `--surface-raised`. No characters, no humour at the player's expense.
- **Logo:** the existing shuttle `Logo` (rounded square `#18221F`, shuttle outline, white cork, arc). Light theme variant: square `--primary`, outline white. Favicon unchanged (`public/favicon.svg`).
- **Sample content** is visibly labelled (`DemoBanner`, "Sample" ribbon on posters).

### 15.1 Empty / partial / failed illustration approach

| State | Motif | Tone |
|---|---|---|
| Empty (no match yet) | an empty court outline with a single shuttle above the net | inviting, not apologetic |
| Loading | skeleton of the real layout; no illustration | quiet |
| Partial | court with one half drawn solid and one half hatched | "some of it is ready" |
| Low coverage / unsupported footage | camera icon over a hatched court | explains, offers a fix |
| Failed | the shuttle outline with a dashed trajectory that stops | neutral, not alarming; `--error` only on the small icon |
| Not enough to say | dashed circle with "?" | calm; never a sad face |
| Offline | court with a broken line | brief |

Each is one reusable inline SVG (< 1 KB) that follows `currentColor`, so it themes automatically.

---

## 16. Dark/light switching rules

1. **Default = system** (`prefers-color-scheme`); explicit choice (System / Light / Dark) in `AvatarMenu`; stored in `localStorage` with try/catch; sets `data-theme` on `<html>`. No flash: a 3-line inline script in `index.html` sets it before paint.
2. **Video theatre may default to dark** for focus. Deep dive follows the player's explicit System / Light / Dark choice, including high contrast; forcing dark over a saved preference breaks readability. Leaving theatre returns the chosen page theme.
3. **Share cards, PDF report, exports and the public `/s/$token` page render in light** (print-safe tokens: ink `#14211D`, canvas white, `--you`, P1/P2 light variants) regardless of the viewer's theme — except the embedded video player, which is dark.
4. Court maps and charts take their colours from the **surrounding** theme tokens, never hard-coded hex (the current `PLAYER_HEX` and the canvas literals in `drawCourt`/`HeatCanvas`/`Timeline` are replaced by values read once via `getComputedStyle` and cached per theme change).
5. Do not mix themes inside one card. A `ClipPlayer` modal opened from a light page is dark (theatre) with its own chrome.
6. Images (posters) are not tinted; overlays on them use `--well` at 80 % for legibility.

---

## 17. Responsive behaviour per component family

| Family | < 768 (phone) | 768–1023 | ≥ 1024 |
|---|---|---|---|
| Shell | `BottomBar` (56 px + safe area), `AvatarMenu` top-right, `AddMatchButton` raised centre | rail or `BottomBar` | `SideNav` 240 px (collapsible to 72 px icons) |
| Recap | single column; `HeroMoment` full-width; sticky mini-player; evidence in bottom `Sheet` | 2-col cards | two-column report: sticky video/hero left, narrative right |
| Cards (`MatchCard`, `MomentCard`) | 1 col (grid of 2 for Moments) | 2–3 col | 3–4 col |
| Tables / rally list | become labelled rows (time · rally · result) with the detail in a `Sheet` | table with 4 columns | full table, inline expand |
| `CourtMap` | full width, ≤ 340 px wide vertical court | 280 px beside text | 200 px live minimap beside the video; 320 px for analysis |
| `RallyTimeline` | horizontal strip with horizontal scroll *only* for matches > 40 rallies; tap to seek | full width | full width + shot lane (Advanced) |
| Charts | one per row, text summary first | 2 per row | small multiples grid |
| Filters | open in a `Sheet`; active-filter count on the trigger | inline chips | inline chips + saved filters (Advanced) |
| Dialogs | bottom sheets, full height for Share | centred modal 480 px | centred modal / side panel for `FixSheet` |
| Video | 16:9 full-width; controls 56 px | 16:9 | 16:9 up to 68 vh |
| Onboarding | one question per screen, large cards, progress dots | same | centred 560 px column; the sample recap beside it |

Never hide consent, coverage or confidence behind hover; all three are visible text on every size.

---

## 18. Accessibility checklist (WCAG 2.2 AA target)

- [ ] All text pairs ≥ 4.5:1 (large ≥ 3:1) in **both** themes — the tables in §3 are the reference; re-run Appendix A after any hex change.
- [ ] UI components, focus rings, input borders and chart marks ≥ 3:1 against adjacent colours.
- [ ] Meaning never by colour alone: every status has icon + word + shape (§10); charts double colour with shape/pattern.
- [ ] Identity colours separate under protan/deutan/tritan (§4) and by shape.
- [ ] Target size ≥ 44 × 44 px on touch (24 px minimum even in dense Advanced tables); ≥ 8 px between adjacent targets.
- [ ] Visible focus ring on every interactive element; logical order; focus returns to the invoker when a dialog/sheet closes; `Esc` closes dialogs.
- [ ] Keyboard parity for everything including clip scrubbing, frame stepping, court-handle nudging and chart selection; no drag-only interactions (alternatives provided).
- [ ] Every chart has a text summary and a data table; every clip has a caption/description; video has captions where audio exists.
- [ ] Text resizes to 200 % without loss; layouts reflow at 320 CSS px; no horizontal page scroll except intentional timelines.
- [ ] `prefers-reduced-motion` honoured; no flashing; no auto-playing sound.
- [ ] Forms: labels associated, errors programmatically associated and described in words, not colour.
- [ ] Language tag set; copy at about grade 6–8 reading level (file 09); no reliance on idioms.
- [ ] Do not assume a tripod, premium phone or fast connection: low-data preview, interrupted upload recovery, large touch controls.
- [ ] Manual pass with a screen reader (VoiceOver + NVDA) on onboarding, recap, FixSheet, and ConsentLedger **before** any pilot.

---

## 19. Visual QA checklist (per screen, before review)

1. **One primary action** visible; one hero number at most.
2. Hierarchy reads **scope → finding → evidence → action** in a 3-second glance.
3. Both themes screenshotted at 360, 768, 1024, 1440; no clipped text at 200 % zoom.
4. No raw hex outside the token file; no `text-line-3` for text; no `text-[11px]`.
5. No red anywhere except a system error or destructive action; no red/green pairing.
6. Every status shows icon + word + shape; Preview tag present on every Preview metric.
7. Every rate shows `n of m`; every number has a unit; missing values are hatched/`—`, never `0`.
8. Court maps: near side bottom, legends visible, text summary + table present.
9. Motion: nothing loops; reduced-motion verified; celebration only on a Checked personal best.
10. Video theatre: overlays off by default for amateurs; caption strip present; controls ≥ 44 px.
11. Skeletons match the real layout; empty states have exactly one next step.
12. Demo/sample content is labelled on the screen, on posters and in exports.
13. Copy lint passes (file 09 §14); no engine words (`band`, `P1`, `provisional`).
14. Contrast script (Appendix A) passes for any new colour.

---

## 20. Six screen mood descriptions (for comps)

**1 — Landing.** Warm paper canvas with a lot of air. A single calm headline, *"Your game. Your moments. Your progress."*, in Archivo 36 px, left-aligned, ink on `#F6F3EC`. To its right (below on phones), a 20-second **sample recap** playing in a rounded white card with a "Sample" ribbon: a real rally poster, the title "A 14-shot rally", one *Worth a look* chip (unless the sample explicitly depicts a checked claim). A thin court-line drawing runs behind the hero at 8 % opacity — the only decoration. One teal primary button ("See an example"), one text link ("Analyse my match"). Below: three quiet cards (Relive moments · See your progress · Celebrate together) with line icons, then "What we can and can't analyse yet" in plain text. Nothing flashes, nothing sells.

**2 — Home.** Paper canvas, white cards, 24 px rhythm. The top card is **"Pick up where you left off"** with Saturday's match poster, a teal "View recap" and a quiet "Add a match". Under it a single **HeroMoment** strip (one poster, one title, one chip). A row of at most **three** progress cards ("Longest rally: 14 shots — your best so far"), each with "Watch this". Recent matches as small cards with status words, no scores. A bottom bar with five labelled tabs and a raised teal ＋. If the player has been away, the greeting is just "Good to see you" — no streaks, no counters. Feels like a photo album that happens to know some stats.

**3 — Recap hero.** The page opens on a **large poster** with a single ▶ in a white circle, 16:9, rounded 14 px. Beneath: "A 14-shot rally" at 28 px, a reason tied to the evidence, and a claim-specific trust chip. **Watch** is primary; **Save** requires a persistent Moment store; **Share** appears only after G-05 participant approval and an enforceable audience check. No score, no confetti. Scrolling reveals three sections with generous space: **Moments** (a horizontal strip), **My game** (a three-fact row with one 56-px hero numeral, then one InsightCard with a thumbnail trio) and **Together** (empty and honest if solo). It reads like a letter from a friend, with the evidence one tap away.

**4 — Deep dive.** Night falls: Arena Night mat green, a large dark video theatre on the left with the white playhead, a vertical court on the right (200 px wide) with your teal dot and a short trail; beneath, the **rally strip** with neutral marks and a few rings. Tabs (as links) for Story · Rallies · Shots · Court · Compare · Ask. Denser type (15 px), tables available, P1 blue and P2 orange allowed, hatched gaps and *Preview* tags visible. Calm precision — the cockpit the analyst has today, tidied and kinder.

**5 — Progress.** Back on paper. Top: a plain sentence — "Based on 4 matches like this one." A **small-multiples** grid of tiny charts, each a few dots with light range bands, a hatched gap where a match had no data, one dashed vertical line where the camera changed. Where there isn't enough, a dashed card says "Two matches isn't enough to call it a trend" with the two clips. Personal bests are outlined-star cards with definitions; **no arrows, no red or green, no levels.** It should feel like a lab notebook kept by someone who likes you.

**6 — Privacy Centre.** Quiet and exact. White cards on paper: five switches with 44 px rows, each with a plain consequence sentence under it ("If you turn this off, shared links stop working."). A visible line at the top — "Private by default. Sharing is always your choice." — then a **ledger** table (permission · status · last changed) and a straightforward Export/Delete block with honest limits. No legalese, no dark patterns, no guilt. The only teal on the page is the focus ring and the save button.

---

## Appendix A — Re-runnable contrast and colour-vision check

Save as `apps/web/scripts/check_colors.py` and run `python check_colors.py`; extend `LIGHT`/`DARK` with any new token. (The values above were produced by exactly this logic.)

```python
import itertools
def h2r(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16)/255 for i in (0,2,4))
def lin(c): return c/12.92 if c<=0.04045 else ((c+0.055)/1.055)**2.4
def lum(h): r,g,b=[lin(x) for x in h2r(h)]; return 0.2126*r+0.7152*g+0.0722*b
def contrast(a,b):
    la,lb=lum(a),lum(b); return (max(la,lb)+0.05)/(min(la,lb)+0.05)
def mix(fg,bg,a):
    f,b=h2r(fg),h2r(bg); c=[f[i]*a+b[i]*(1-a) for i in range(3)]
    return '#%02x%02x%02x'%tuple(round(x*255) for x in c)
M={'protan':[[0.152286,1.052583,-0.204868],[0.114503,0.786281,0.099216],[-0.003882,-0.048116,1.051998]],
   'deutan':[[0.367322,0.860646,-0.227968],[0.280085,0.672501,0.047413],[-0.011820,0.042940,0.968881]],
   'tritan':[[1.255528,-0.076749,-0.178779],[-0.078411,0.930809,0.147602],[0.004733,0.691367,0.303900]]}
def sim(h,k):
    r=[lin(x) for x in h2r(h)]; m=M[k]
    return [max(0,min(1,sum(m[i][j]*r[j] for j in range(3)))) for i in range(3)]
def lab(rgb):
    r,g,b=rgb
    X=(0.4124*r+0.3576*g+0.1805*b)/0.95047; Y=0.2126*r+0.7152*g+0.0722*b; Z=(0.0193*r+0.1192*g+0.9505*b)/1.08883
    f=lambda t: t**(1/3) if t>0.008856 else 7.787*t+16/116
    fx,fy,fz=f(X),f(Y),f(Z); return (116*fy-16,500*(fx-fy),200*(fy-fz))
def de(a,b,k=None):
    A=lab([lin(x) for x in h2r(a)]) if k is None else lab(sim(a,k))
    B=lab([lin(x) for x in h2r(b)]) if k is None else lab(sim(b,k))
    return sum((x-y)**2 for x,y in zip(A,B))**0.5
LIGHT=dict(canvas='#F6F3EC',surface='#FFFFFF',ink='#14211D',muted='#47544F',faint='#5E6B66',primary='#0B6E6E',
           you='#0B7466',partner='#A415C1',other='#3A3F4A',evidence='#1D4ED8',strength='#166534',
           opportunity='#9A4A07',uncertain='#475569',corrected='#6D28D9',error='#B91C1C')
DARK=dict(canvas='#103129',surface='#18221F',ink='#E8EFEA',muted='#A9BAB2',faint='#8DA098',primary='#E8EFEA',
          you='#4FD6C4',partner='#E27BF2',other='#7C8794',evidence='#7DA7FF',strength='#5FD38A',
          opportunity='#F0B454',uncertain='#9FB0C4',corrected='#B79CFF',error='#F26B68')
for name,T in (('light',LIGHT),('dark',DARK)):
    for k in ('ink','muted','faint','primary','evidence','strength','opportunity','uncertain','corrected','error','you','partner','other'):
        assert contrast(T[k],T['surface'])>=(3 if k=='other' and name=='dark' else 4.5),(name,k)
        if k in ('strength','opportunity','uncertain','corrected','error','evidence'):
            assert contrast(T[k],mix(T[k],T['surface'],0.12))>=4.5,(name,k,'tint')
    for a,b in itertools.combinations(('you','partner','other'),2):
        m=min(de(T[a],T[b],k) for k in (None,'protan','deutan','tritan'))
        assert m>=15,(name,a,b,round(m,1))
print('ok')
```
