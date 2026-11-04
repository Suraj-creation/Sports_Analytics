# Highlights UI implementation plan

**Goal:** Add a dedicated Highlights navigation destination and implement the ten
insight experiences with honest evidence, a local example and private draft picks.

**Architecture:** Sport-neutral display contracts, explicit presentation providers,
badminton-owned definitions and response adapters, existing source-frame playback
links. The browser does not become a second production analytics engine.

**Stack:** Existing React 19, TanStack Router/Query, Radix Dialog, Lucide and CSS.

**Spec:** `docs/superpowers/specs/2026-11-04-highlights-design.md`.

## Constraints

- Local Windows UI editing only; no remote system, pipeline, models or installs.
- No tests, builds, app execution or browser checks. Review source and Git diff only.
- No commits. Preserve unrelated dirty files and untracked directories.
- Default example is labelled synthetic; real data never inherits example metrics.
- Physical people, teams, scoring slots and review states remain distinct.
- Production calculations remain server/plugin responsibilities.

## Sequential delivery

### 1. Contracts, catalogue and example

- [x] Create `apps/web/src/features/highlights/types.ts` for display contracts.
- [x] Create `badminton/catalogue.ts` for ten definitions and requirements.
- [x] Create `badminton/example.ts` with internally consistent illustrative rallies,
  derived example-only comparisons, two/four participant formats and missing states.
- [x] Create `badminton/observed.ts` for existing server responses and explicit gaps.
- [x] Create `providers.ts` for registration/resolution without UI sport branches.

### 2. Navigation and source selection

- [x] Add lazy `/highlights` route and primary Highlights item, preserving Moments.
- [x] Adapt the existing mobile navigation for six destinations.
- [x] Create `HighlightsPage.tsx` and `useCollection.ts` with explicit example/live
  selection, session/participant controls, source notice, loading/error/empty states.
- [x] Keep API errors from blocking a local illustrative Highlights view while
  preserving successful authentication checks and backend access control.

### 3. Browse and inspect each insight

- [x] Create `HighlightArtwork.tsx` for labelled geometry, score, comparison and
  outcome visuals, driven by the display contract rather than invented figures.
- [x] Create `HighlightCard.tsx` for featured, compact and collection presentations.
- [x] Create `HighlightDetails.tsx` for a focus-managed evidence/definition sheet.
- [x] Implement rally/favourite, smile, comeback, personal record, save, partnership,
  halves, length buckets, doubles coverage and smash outcomes in that order.
- [x] Existing recordings link to their own canonical frames; examples do not claim
  source footage exists and never navigate to fictitious match IDs.

### 4. Personal picks

- [x] Create `usePersonalPicks.ts` with versioned, validated metadata-only local
  storage, separate example/live namespaces and explicit persistence feedback.
- [x] Create `PersonalPickDialog.tsx` for favourite, smile, save and partnership picks,
  selecting an existing rally or a bounded custom frame interval and optional note.
- [x] Add private draft collection, removal and error recovery. No API writes.

### 5. Craft and bounded source review

- [x] Create scoped `highlights.css`, preserving incumbent tokens and both themes.
- [x] Review desktop/tablet/mobile grid arithmetic and long-content constraints.
- [x] Review keyboard/focus semantics, form labels, unknowns, denied storage,
  stale revisions, no media, empty/error and unsupported-sport paths in source.
- [x] Apply Taste and Impeccable polish; apply Emil-style restraint to motion.
- [x] Inspect only changed-file diffs and imports; record runtime verification as
  deliberately not performed. Do not turn source review into a passing-test claim.

## Delivery note

The user authorized design followed by implementation in this chat. No additional
approval checkpoint, dependency installation, test cycle or commit is introduced.

## Implementation record

Implemented the lazy Highlights route and both navigation surfaces, ten insight
presentations, singles/doubles example collections, existing-recording adapters,
source/session/player filters, search, evidence/definition details and private
local picks. Source and session choices are represented in the URL for browser-back
navigation. Unsupported domains receive an explicit unavailable state.

Personal choices stay separate from factual claims. The longest rally is not
overwritten by a favourite. A selected save does not verify its sporting evidence.
Raw winning sides remain hypotheses; event-wide status does not verify each field.
Drafts carry source/revision context; older drafts are manageable and removal has undo.

Applied the existing source formatter with the frontend's explicit configuration;
no dependencies or configuration migrations were needed. Source review identified
three material issues (selector scope, stale-draft capacity and winner qualifiers).
All three were corrected and the reviewer confirmed those fixes in source.

No tests, typecheck, lint, build, app execution, browser screenshots, inference or
media processing were performed. No remote runtime was contacted. No visual or
runtime passing claim is made. All changes remain uncommitted.
