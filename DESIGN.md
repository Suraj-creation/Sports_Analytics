---
name: Rally Analytics
description: A calm match-review desk for badminton recordings and their source evidence.
colors:
  canvas: "#eef3ef"
  frame: "#e9f0ea"
  surface: "#ffffff"
  surface-raised: "#f5f8f5"
  edge: "#d6e1d9"
  edge-strong: "#9cb3a3"
  ink: "#172d25"
  muted: "#53685e"
  faint: "#596f62"
  primary: "#245c40"
  primary-hover: "#1b4932"
  primary-soft: "#e1ece3"
  on-primary: "#ffffff"
  field: "#ffffff"
  field-ink: "#172d25"
  field-placeholder: "#596f62"
  field-disabled: "#edf2ee"
  video-well: "#0c1913"
  you: "#216b50"
  partner: "#89652e"
  other: "#596c61"
  evidence: "#286448"
  strength: "#246343"
  opportunity: "#855b17"
  uncertain: "#5d7065"
  corrected: "#395e82"
  error: "#a82e35"
  live: "#276747"
  shuttle: "#ffffff"
  court-floor: "#e6eee7"
  court-line: "#38654c"
  player-1: "#2875b8"
  player-2: "#aa5624"
  dark-canvas: "#101a15"
  dark-frame: "#101a15"
  dark-surface: "#17251e"
  dark-surface-raised: "#203328"
  dark-edge: "#344c3e"
  dark-edge-strong: "#658370"
  dark-ink: "#edf3ee"
  dark-muted: "#b7c9bc"
  dark-faint: "#9ab2a2"
  dark-primary: "#d0e7a5"
  dark-primary-hover: "#e1efc5"
  dark-primary-soft: "#2b4433"
  dark-on-primary: "#173323"
  dark-field: "#1b2c22"
  dark-field-ink: "#edf3ee"
  dark-field-placeholder: "#a6bbad"
  dark-field-disabled: "#203127"
  dark-you: "#b8db9f"
  dark-partner: "#dfc08b"
  dark-other: "#adbbaf"
  dark-evidence: "#bddba7"
  dark-strength: "#abd39c"
  dark-opportunity: "#e0bf86"
  dark-uncertain: "#adbdaf"
  dark-corrected: "#a1bfdc"
  dark-error: "#f49b9c"
  dark-live: "#b8db9f"
  dark-court-floor: "#1a3627"
  dark-court-line: "#b2cfb9"
  dark-player-1: "#77b8ef"
  dark-player-2: "#e9af79"
typography:
  page-title:
    fontFamily: "\"Archivo Variable\", \"Archivo\", ui-sans-serif, system-ui, sans-serif"
    fontSize: "26px"
    fontWeight: 650
    lineHeight: 1.25
    letterSpacing: "-0.025em"
  section-title:
    fontFamily: "\"Archivo Variable\", \"Archivo\", ui-sans-serif, system-ui, sans-serif"
    fontSize: "18px"
    fontWeight: 600
    lineHeight: 1.4
    letterSpacing: "-0.015em"
  body:
    fontFamily: "\"Archivo Variable\", \"Archivo\", ui-sans-serif, system-ui, sans-serif"
    fontSize: "15px"
    fontWeight: 400
    lineHeight: 1.5
  control:
    fontFamily: "\"Archivo Variable\", \"Archivo\", ui-sans-serif, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 550
    lineHeight: 1.25
  label:
    fontFamily: "\"Archivo Variable\", \"Archivo\", ui-sans-serif, system-ui, sans-serif"
    fontSize: "14px"
    fontWeight: 550
  metadata:
    fontFamily: "\"Archivo Variable\", \"Archivo\", ui-sans-serif, system-ui, sans-serif"
    fontSize: "12px"
    fontWeight: 400
    lineHeight: 1.55
  figure:
    fontFamily: "\"Archivo Variable\", \"Archivo\", ui-sans-serif, system-ui, sans-serif"
    fontSize: "26px"
    fontWeight: 600
    lineHeight: 1.2
    letterSpacing: "-0.025em"
rounded:
  status: "4px"
  control: "8px"
  card: "12px"
  sheet: "16px"
  chip: "999px"
spacing:
  4: "4px"
  8: "8px"
  12: "12px"
  16: "16px"
  20: "20px"
  24: "24px"
  32: "32px"
  48: "48px"
  64: "64px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "{colors.on-primary}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
    height: "40px"
  button-primary-hover:
    backgroundColor: "{colors.primary-hover}"
    textColor: "{colors.on-primary}"
  button-secondary:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
    height: "40px"
  button-secondary-hover:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.ink}"
  button-ghost:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
    height: "40px"
  button-danger:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.error}"
    typography: "{typography.control}"
    rounded: "{rounded.control}"
    padding: "9px 14px"
    height: "40px"
  input:
    backgroundColor: "{colors.field}"
    textColor: "{colors.field-ink}"
    rounded: "{rounded.control}"
    padding: "10px 12px"
    height: "42px"
  navigation-active:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.primary}"
    rounded: "{rounded.control}"
    padding: "9px 12px"
    height: "42px"
  status:
    backgroundColor: "{colors.surface-raised}"
    textColor: "{colors.muted}"
    rounded: "{rounded.status}"
    padding: "3px 8px"
  card:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.card}"
    padding: "24px"
  video-mode-selected:
    backgroundColor: "{colors.dark-primary-soft}"
    textColor: "{colors.dark-ink}"
    rounded: "{rounded.control}"
    padding: "8px 12px"
    height: "40px"
---
# Design System: Rally Analytics

## Overview

**Creative North Star: "The Match-Review Desk"**

Rally is a working interface for reviewing badminton recordings and their source-linked evidence. The confirmed light appearance uses a pale sage frame around a white working sheet, with a deep forest video instrument. Dark appearance uses the same hierarchy and geometry.

The system is compact, calm and legible. Archivo carries headings, controls and comparable figures; fine borders and tonal surfaces separate information without ornamental depth. The approved Rally logo family supplies the identity.

Scope: the production analytics application in `apps/web`. The independent `client-website` and historical `apps/web/src/prototype` retain their own visual authority. This document records the built system; `apps/web/src/styles/tokens.css` and the production component styles are the implementation source. The frontmatter lists light roles first, followed by explicit `dark-` counterparts; runtime theme changes use the corresponding CSS variables.

**Key Characteristics:**

- Light sage frame, white working sheet and fixed dark video scope.
- Archivo typography with compact labels and tabular figures.
- Flat bordered groups, restrained green selection and explicit evidence states.
- Responsive navigation and a video workspace that preserves its mounted media.

## Colors

The palette is a family of forest and sage greens with quiet neutral surfaces. The frontmatter preserves the implemented color values.

### Primary

- **Forest Action** (`primary`, `primary-hover`, `on-primary`): deliberate actions and selected navigation; a pale leaf treatment takes this role in dark appearance.
- **Soft Sage Selection** (`primary-soft`): selected controls and restrained state backgrounds.

### Secondary

- **Evidence and Strength Greens** (`evidence`, `strength`, `live`): supported observations, strength and current activity.
- **Player Greens and Warm Partner** (`you`, `partner`, `other`): review perspective and comparison.
- **Warm Opportunity**, **Quiet Uncertainty**, **Correction Blue**, **Error Red** (`opportunity`, `uncertain`, `corrected`, `error`): semantic evidence and feedback roles. They are not general decorative accents.
- **Player Blue and Orange** (`player-1`, `player-2`): player identity in overlays and comparisons. Court floor, court line and shuttle tokens support the recording overlays.

### Neutral

- **Pale Sage Frame** (`canvas`, `frame`): page foundation and navigation chrome.
- **Working White** and **Raised Sage** (`surface`, `surface-raised`): content, groups and quiet emphasis.
- **Forest Ink**, **Muted Ink**, **Faint Ink** (`ink`, `muted`, `faint`): primary content, secondary explanation and metadata.
- **Soft Edge** and **Control Edge** (`edge`, `edge-strong`): group boundaries and readable field/control outlines.
- **Field Roles** (`field`, `field-ink`, `field-placeholder`, `field-disabled`): filled, empty, autofill and disabled controls.
- **Video Well** (`video-well`): the fixed deep green picture background shared by both appearances.

**The Field and Stage Rule.** Fields use field background, ink, placeholder and disabled roles. The video picture uses the fixed dark video well; the surrounding instrument resolves dark theme roles in either application appearance.

**The Evidence State Rule.** Semantic color accompanies words, line treatment or source context. Uncertain and unknown evidence remains visibly uncertain rather than borrowing the confirmed treatment.

## Typography

**Display and Body Font:** Archivo Variable, with Archivo and the system sans-serif fallback stack. Width is normally 100. Shared numeric utilities use tabular numerals; the condensed numeric utility uses width 75 and weight 700, while condensed text uses width 85.

**Character:** compact and practical, with modest size changes and selective weight. There is no separate promotional display face.

- **Page title:** `page-title`; phone catalogue pages reduce to 24px at 600px and below, while the match title remains 26px.
- **Section title:** `section-title`; supports grouped controls and analysis sections.
- **Body:** `body`; supporting copy often uses 14px, with long explanations limited to roughly 70–72 characters.
- **Controls and labels:** `control` and `label`; compact supporting navigation also uses 13px.
- **Metadata:** `metadata`; timestamps, hints, basis notes and secondary units.
- **Figures:** `figure` with tabular numerals. Context-specific values range from 20–28px; phone summary figures use 24px.

**The Working Type Rule.** Body copy stays at 15px. Page and section titles establish hierarchy while labels, captions and tabular figures keep repeated information easy to compare.

## Layout

The desktop frame has labelled navigation (224px) and a toolbar (56px). The main sheet has an 8px outer frame inset, a fluid content column and a maximum working width of 1440px. Catalogue pages use 32px horizontal gutters and 28px top spacing; match review uses 32px horizontal gutters and 24px top spacing. At widths up to 1100px the horizontal gutter becomes 24px.

Between 768px and 1100px, navigation becomes a compact icon rail (76px). Below 768px, a five-item bottom navigation replaces the sidebar, the sheet loses its outside corner radius, and the header retains a 56px height. The phone header exposes Settings; Help and System remain reachable through Settings. Bottom padding includes the device safe area.

Home and import columns stack at 900px and below. Catalogue layouts make their phone changes at 600px, using 16px gutters and stacked headings. Match review makes its phone changes at 640px with 16px gutters. Analysis grids stack below 768px, while metric groups retain two columns. Tables and tab strips scroll within their own bounds.

Spacing uses the frontmatter steps, with 16px and 24px as the common working intervals. Cards use 24px desktop padding; phone cards use 20px vertically and 16px horizontally. Analysis panels use 20px desktop and 16px phone padding. Standard controls have a 40px minimum height, shared fields are 42px, and the shared touch rules raise controls to at least 44px.

Body density remains 15px in the production pages. The token sheet also defines default density variables (16px padding/gap, 44px row), quick variables (24px padding/gap, 52px row), and advanced variables (12px padding/gap, 36px row). These are available density hooks, not a global text-size multiplier or a currently exposed production density setting.

## Elevation & Depth

Working surfaces use thin borders and tonal layering. Cards, summaries, settings groups and the sheet have no decorative resting shadow. The token sheet retains a popover shadow vocabulary: a soft green-black shadow in light appearance and a black shadow in dark appearance. Those values are captured in the sidecar; their presence does not make cards elevated. Field autofill uses an inset color fill to retain the field surface.

**The Flat Surface Rule.** Working sheets, cards and analysis groups are flat at rest. Borders and surface tones carry their structure.

## Shapes

Controls and small groups use gently curved corners (`control`); cards and major analysis panels use `card`; the desktop working sheet uses `sheet`. Compact status labels use the tighter `status` radius. Full pills are reserved for evidence certainty chips and similarly small state marks. The phone sheet has square outside corners.

One-pixel boundaries group related information. The recording instrument uses rounded top corners and joins its evidence description with rounded bottom corners. Selected tabs use a two-pixel underline; uncertainty chips use a dashed outline rather than a stronger solid fill.

## Components

### Buttons

Primary, secondary, ghost and danger variants share compact Archivo labels, an icon gap (8px), control corners, and padding (9px 14px). Primary actions use the action fill and on-action text. Secondary actions use the surface with a strong outline; ghost actions remove the resting fill and outline; danger actions retain the surface and semantic error ink. Small buttons use 13px text and a 34px minimum height before touch overrides.

Hover changes color and border without a lift. Disabled buttons use the disabled field surface and muted text at full opacity. Keyboard focus uses a two-pixel primary outline offset by three pixels. Busy buttons expose their busy state and disable repeated activation.

### Inputs / Fields

Shared fields use field-specific colors, a strong one-pixel outline, control corners and padding (10px 12px). Labels stay outside the control; hints use metadata styling. Placeholder and filled text remain explicit in both appearances. Disabled fields use muted ink and the disabled field surface; autofill pins text, caret and inset background to the field roles.

Shared input focus changes the border to primary and uses a two-pixel, 25%-primary outline offset by one pixel. Filter controls also inherit the global keyboard outline. Touch fields have at least a 44px target.

### Cards / Containers

Cards are flat surface panels with a one-pixel edge, card corners and working padding. Lists use rules instead of a separate card around every row. Summary figures sit in shared groups with internal dividers. Empty, loading and failed states use the same container language with a visible explanation or action.

### Chips / Status

Compact processing labels use raised surfaces, status corners and padding (3px 8px); wording carries the state. Failure uses error ink and active processing uses primary ink. Certainty chips are distinct full pills: confirmed has a subtle fill and border, probable is outlined and named, and uncertain/unknown is dashed and named.

### Navigation

Desktop navigation has a 42px minimum row, 18px icons and 14px labels. Active rows use a surface fill, edge border, primary ink and a stronger weight. Compact rails preserve icon targets. Phone bottom navigation has five equal columns, 58px rows and 12px labels; active items use the soft selection fill. The skip link becomes visible on focus. Route headings accept programmatic focus without an ornamental outline.

Analysis tab strips use muted text and a two-pixel primary underline for the current tab. Match tabs have a 48px minimum height and an inset keyboard outline; horizontal scrolling retains access when labels no longer fit.

### Recording Instrument

The recording instrument has a fixed dark scope with its own legible text, fields and controls. Its picture, playback controls, timelines and source description form one connected group. Standard mode shows the instrument and supplementary analysis, with a picture maximum of 52svh on larger screens and 50svh on phones.

Focus mode uses the same mounted video, hides surrounding header and supplementary content, reduces desktop navigation to 72px, and raises the picture maximum to 72svh (70svh on phones). Phone Focus also hides bottom navigation. The labelled Standard control returns to the working view; Escape returns focus to it.

Collapsed mode pauses playback, hides the instrument body, and leaves a compact restore control with source context. It preserves the media node, position and evidence selection. Restoring moves keyboard focus to Standard; source-linked evidence can reveal the recording again.

Mode controls use a selected soft fill and strong outline. Routine feedback uses 160ms color transitions; supported pointer-triggered mode changes use a 220ms source-only view transition with a decelerating curve. Operating-system reduced motion and the application setting suppress mode snapshots and reduce descendant animation/transition duration. The OS preference also removes smooth scrolling. State feedback remains visible.

## Do's and Don'ts

### Do:

- **Do** keep this contract scoped to apps/web and use the exact approved Rally logo assets.
- **Do** resolve field and video colors through their own semantic roles in light and dark appearances.
- **Do** use compact titles, tabular numerals and visible metric basis or uncertainty.
- **Do** preserve one mounted video and its position when changing Standard, Focus or Collapsed mode.
- **Do** retain keyboard focus feedback and honor both operating-system and application reduced-motion preferences.
- **Do** allow layouts, controls and long recording titles to wrap at narrow widths.

### Don't:

- **Don't** apply this contract to the independent client website or historical prototype.
- **Don't** use a dark video background token for ordinary input fields.
- **Don't** replace evidence or missing values with invented scores, accuracy or progress.
- **Don't** add decorative gradients, promotional panels or oversized metric tiles to the working interface.
- **Don't** turn routine hover feedback into lifted cards or decorative looping motion.
