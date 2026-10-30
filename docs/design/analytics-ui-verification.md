# Analytics UI verification — 2026-10-30

The redesign applies to `apps/web`. It uses the existing Rally identity and actual
GPU-server recordings. The independent client website and unrelated local drafts
were preserved.

## Automated checks

Run in the isolated GPU-server checkout with `source ../gpu-env.sh`:

- `pnpm --dir apps/web test`: 26 files, 96 tests passed.
- `pnpm --dir apps/web typecheck`: passed.
- `pnpm --dir apps/web build`: passed.
- Biome checks for all 27 changed or new source files: passed.
- Impeccable detector on changed source: no findings.

Eight video-workspace tests cover the mounted source, playback position, selected
evidence, participant drafts, Escape, queued playback while collapsed, delayed
metadata, intentional evidence playback, and the app's reduced-motion preference.
The two playback/motion regressions were observed failing on the GPU server before
their fixes. Independent code review marked both fixes resolved.

## Browser evidence

Read-only Chromium checks used the local frontend and the GPU API through an SSH
forward. No non-authentication API writes were made.

- 88 route/theme/viewport checks across 11 routes, light and dark, at widths
  1440, 1280, 768, and 390.
- 32 confirmation views, plus current phone Settings navigation in both themes.
- URL typing, clipboard paste, keyboard selection/focus, video modes, and phone
  links to Settings, Help, and System passed.
- Twelve video-mode transitions kept one media element and its 6-second position.
- Timeline SVG/canvas widths follow their container at all four widths. Clock and
  processing labels fit; phone labels wrap.
- Confirmed field text contrast was at least 13.05:1; placeholders at least 5.42:1.
- No route, console, HTTP, or document-overflow failures were recorded.

The fresh Impeccable finish reviewer inspected 30 saved images across every core
route, login, both themes, and all four widths. Its disposition was **ship**, with
no material design fixes requested. This was a code-led visual review, not a
pixel-replication or model-accuracy assessment.

Native browser autofill was not seeded. The autofill check was a forced CSS-state
probe. These checks do not measure model, shuttle, event, or score accuracy.

The reusable harness is `apps/web/e2e/rally-review.mjs`. Supply `BAI_UI_PASSPHRASE`
and a saved recording's `BAI_UI_SESSION_ID` through the environment; it never
saves authentication state. Reports and
recording screenshots stay in the ignored `.impeccable/review/` directory.
