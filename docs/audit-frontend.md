# Frontend production audit — 23 October 2026

Owner: frontend integrity specialist. Authoritative checkout: `/home/administrator/Desktop/sport-analytics/Sports_Analytics`, branch `codex/production-audit-20261023`. The committed `apps/web/prototype.html`, `apps/web/src/prototype/` and `Design/production-prototype/DESIGN_DIRECTION.md` were read and inspected without modification. No real recording was reanalysed, corrected or deleted.

## Baseline and demonstrated defects

Baseline: 43 frontend tests passed; TypeScript passed; Biome passed with six pre-existing `noExplicitAny` warnings. Production implementation retained the prototype's warm paper, white panels, teal actions, persistent match player, player picker and analysis tabs.

| Severity | Evidence | Resulting change |
| --- | --- | --- |
| P1 | `match-video-stage` applied 16:9 and a 56vh maximum to a container that also held transport controls. The picture lost control height before the court was drawn. | The actual picture now owns the source aspect ratio. Controls have their own natural height and wrap. The picture can use up to 70svh on desktop and follows available width on narrow screens; `object-contain` retains the whole court. |
| P1 | `playEvidence` only emitted a transient custom event. There was no shared selected event, under-player context, or synchronized marker/chip. | Typed selected evidence and bounded clip state now live in the playback store. Source timestamp/frame, selected player, rally/counting/outcome context, clip interval and available event provenance appear directly below the player. |
| P1 | Manual timeline/frame/deep-link seeking left the previous bounded clip active, allowing it to snap playback back to the old end. Playback frame/selection could survive a recording change. | Manual seeks explicitly release clip/selection; media state resets on workspace mount/unmount. Repeated clicks on the same event remain independent playback requests. |
| P1 | An event clicked while media loaded could be overwritten by the arrival URL's default `f=0`. | Pending evidence survives metadata loading and takes precedence over an older arrival cue. An absent frame query no longer fabricates a seek request. |
| P1 | Nullable server distance could become `0 m` through numeric coercion. Steps used an unvalidated fixed stride; rate used entire rally time rather than accepted tracking time. | Missing distance renders as a dash in overview, movement and head-to-head. Steps explicitly report their missing prerequisite. Movement rate uses `distance_quality.observed_s`, labelled as partial tracked-interval evidence. A valid stationary zero is retained. |
| P1 | `stateAt(...).known === false` still rendered the initial 0:0 scoreboard after analysis completed. | Unknown game/point scores render as dashes with “Score unavailable” or “Score pending”; canonical point events still drive the known score without spoilers. |
| P2 | Shot previews used a fixed 45-frame tail; timeline slider advertised the out-of-range frame `n`; controls were 36px and could compete for narrow space. | Shot tails use canonical proxy FPS; slider maximum is `n - 1`, with Home/End and pointer-cancel support. Transport targets are 44px and reflow. |
| P2 | Landing and targeting labels could imply actual shuttle landing from receiver feet. | Separate “Shuttle landing” prerequisite from “Receiver positions”, explicitly identifying the latter as a receiver-foot proxy. |

## Timeline and data contracts

`MediaInfo.fps_num/fps_den` and event frame indices address the backend's canonical CFR proxy. The UI does not interpret array positions as time and does not substitute original-source VFR PTS for proxy coordinates. A preview cues the actual event frame; the bounded clip retains up to one second before that frame for replay. Again/Loop replay from the lead-in; playback stops at the inclusive end frame. The whole-match timeline highlights selected source evidence while its playhead follows presented frames. Manual navigation clears that selection, and the under-player “Now showing” context follows actual playback.

`PlayerStats.distance_m` is now `number | null`. Optional `distance_quality` is consumed compatibly; its accepted tracking span is the only denominator used for movement rate. No physiological measurement or validated step count is inferred. The frontend has no consumer of insight `score_after`; catalogue and momentum use canonical `score_timeline`, whose backend now omits unsupported points. Legacy missing `official` flags retain existing compatibility semantics, agreed with the lead.

Live event feed previews and known Ask citations also use the shared event playback path, preserving event identity, uncertainty and canonical frame/interval. If a citation's frame disagrees with a known event, the actual event frame wins. A timestamp-only citation remains a manual exact-frame seek, explicitly clears stale selection/clip state, and explains that full event details are unavailable.

The existing pair surface continues to describe two court-side identities and the missing four-person identity evidence. It does not relabel a side as a doubles athlete. Empty, processing, error and unavailable surfaces continue to use real API state rather than prototype fixture values.

## Verification

Commands run on the GPU server after sourcing `../gpu-env.sh`, with the existing runtime and without dependency upgrades:

```sh
pnpm --dir apps/web test
pnpm --dir apps/web typecheck
pnpm --dir apps/web lint
pnpm --dir apps/web build
pnpm --dir apps/web e2e
```

The final unit suite contains 53 tests, including ten new regressions for manual clip cancellation, same-frame requests, session reset, invalid timebases, event details/navigation, null/zero distance, the tracked-time denominator, unavailable score and canonical known-event citation precedence. The existing live-feed and timestamp-only citation regressions also verify the unified behavior. Typecheck and production build pass. Biome has the same six baseline warnings; the build retains the existing Settings static/dynamic import warning.

All six browser workflows pass on the final built source (24.9 seconds). The final production build completed in 6.80 seconds after the backend regression suite was finished, avoiding a race with tests mounting the static assets directory. The extended real upload workflow verifies range delivery, exact source-frame navigation, frame-105 bounded stop, repeated selection, keyboard Home releasing a clip and marker, slider bounds, picture proportions, transport controls, player/tab state, and 390px overflow. The separate fixture server uses a temporary data directory and a model-free synthetic clip; those results demonstrate integration, not trained perception accuracy.

The prototype was rendered in a separate temporary Vite process at 1440px and 390px. Its identity flow was exercised before final captures. An authenticated browser also opened an actual persisted recording at both widths, selected its source-frame-615 long serve (20.500 seconds), and displayed the real non-counted/unresolved rally context and `stroke_rules_v0` provenance immediately below the video. Both real-recording viewports had zero horizontal overflow and no page errors. Production screenshots retain the established visual language while giving the picture its own space and placing evidence immediately below it. The mechanical design scan found no findings in the changed player/workspace/style targets. No dependency, theme redesign, prototype edit or unrelated GPU process change was introduced.

Browser evidence is stored outside the repository on the GPU server:

- `/tmp/bai-audit-frontend-desktop.png` and `/tmp/bai-audit-frontend-narrow.png`: disposable API-backed integration views.
- `/tmp/bai-audit-prototype-1440.png` and `/tmp/bai-audit-prototype-390.png`: committed reference rendered at matching viewport widths.
- `/tmp/bai-audit-real-1440.png` and `/tmp/bai-audit-real-390.png`: authenticated actual-recording evidence selection, performed without modifying recording data.

## Limits and handoff

No screen-reader or physical-device pass was performed. Browser checks use Chromium; Safari/native HLS and Firefox remain additional platform checks. Full annotated model evaluation, four-player doubles attribution and calibrated physical accuracy are independent backend/model acceptance work. UI labels preserve those limits. A media-error state retains selected context but cannot promise playback until compatible media is available. The prototype and actual recordings are different content, so screenshots compare composition and interaction rather than pixel-identical analytics.

Changes are uncommitted and unpushed for lead integration. Relevant files: playback store, VideoStage, EvidenceDetails, clip helper, SessionPage, Timeline, RalliesTab, HeatmapsTab, StatsTab, SessionAnalytics, shared PlayerStats types, source styles, focused unit tests and `e2e/production.spec.ts`.
