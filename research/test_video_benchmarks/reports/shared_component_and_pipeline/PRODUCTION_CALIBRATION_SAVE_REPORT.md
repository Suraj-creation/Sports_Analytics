# Calibration Save ordering audit — 2026-11-05

The calibration page had a reproducible commit-to-passive-effect race: Save could become enabled with six rendered court points while its mutation observer still held the preceding empty-point closure. The approved repair passes session ID, points and proposal frame as explicit mutation variables at the click. Only `CalibratePage.tsx` and a new sibling regression test changed.

## Original observation and evidential limit

The first v4 full frontend run passed 222/223 tests; the first existing calibration test called the mocked API but `near_left` was undefined. The unmodified isolated calibration run passed 3/3 and an unchanged full repeat passed 223/223. All three logs remain intact:

- `artifacts/benchmarking/experiments/prod_20261105_frontend_release_v4/tests.log`
- `artifacts/benchmarking/experiments/prod_20261105_frontend_release_v4/tests_repeat.log`
- `artifacts/benchmarking/experiments/prod_20261105_failed_video_fix_v1/calibration_isolated.log`

The original failure did not record the full submitted object or observer-update ordering. Its particular cause therefore cannot be established retrospectively. Calling it an unexplained harmless timing failure would overstate the evidence. The subsequent controlled reproduction demonstrates the same missing-coordinate signature and a concrete software defect; it does not establish the original run's exact schedule or a human/browser recurrence rate.

## Causal reproduction

Before applying the fix, the audited component SHA256 was `73c36aff18279b85e194baf4fc1e15871995232d86025183a2cb75c9718a843c`, identical to both v4 full runs. The installed TanStack React Query is 5.104.1. Its `useMutation` creates an observer once and refreshes its options in `React.useEffect`; `MutationObserver.mutate` builds the mutation from its current options. The page previously captured `points` in that effect-refreshed mutation function, while enabling its button directly from the newly rendered fit.

A native DOM `MutationObserver` clicked the actual enabled button at its first enabled DOM commit. No mutation hook, query observer, scheduler or component state was mocked. The same API/router/media stubs as ordinary component tests isolated this from external services. The mutation-cache event log recorded the actual API receiving `{}` at frame 0 before the later observer-option update events. A copied-source candidate passing explicit mutation variables submitted all six expected coordinates under the same schedule.

Three contracts failed on the original actual component and passed on the candidate and subsequently on the repaired actual component:

1. Saved reference-frame geometry, clean revision 0: `near_left=[50,100]`.
2. The same saved geometry with matching-session revision 77: identical required result.
3. Saved geometry belonging to frame 500 with proposal frame 0: detected `near_left=[10,10]`.

This controls the independent analysis-revision/query-key explanation and verifies the automatic-proposal branch. Vitest's unchanged configuration retains default per-file isolation. The test fixture is not mutated, and controlled tests disconnect their DOM observers, unmount the page, clear their own query clients and restore the singleton store and mocks. Cross-file fixture leakage is not needed to reproduce this failure.

The DOM observer is a controlled way to exercise the exposed ordering, rather than a simulation of human reaction time. It also matches the mechanism through which testing-library `waitFor` can notice an enabled DOM state. Native browser scheduling frequency remains unmeasured. The backend's calibration endpoint validates the submitted point set with `fit_homography` and maps insufficient geometry to HTTP 422; the demonstrated product risk is a failed Save. This audit does not prove invalid geometry was persisted.

## Change and validation

The mutation function now receives `{sessionId, points, frame}`; the rendered button passes that object to `save.mutate`. An old mutation-function closure can therefore use the current click's explicit coordinates. The existing success handler and geometry seeding behavior remain outside this narrow fix.

Artifacts are in `artifacts/benchmarking/experiments/prod_20261105_calibration_test_audit_v1/`:

- `ordering_results.json`: API payload and mutation-cache ordering for original and copied candidate.
- `draft_red.log`: original actual component fails all three new contracts.
- `draft_green.log`: copied candidate passes all three.
- `actual_application.json`: original SHA check and exact two-file application receipt.
- `actual_focused.log`: actual repaired page passes the three existing and three new tests, **6/6**.
- `actual_typecheck.log`: TypeScript check exit 0.
- `actual_full_frontend.log`: first full run after this repair, **226/226**, 46 files, 5.92 seconds.
- `actual_validation.json`: actual source identities, related unchanged-source checks and log hashes.

The first experimental configuration attempt failed to load as CommonJS; switching the research-only configuration to `.mts` corrected the harness. The first event-log writer used a Vite-transformed URL that Node rejected; an explicit artifact path corrected that harness issue. Those failed setup logs remain preserved and are not counted as component-contract results.

The new production artifact build is `artifacts/benchmarking/experiments/prod_20261105_frontend_release_v5/build/`. Its build succeeded, and `build_receipt.json` verifies source-map `sourcesContent` byte equality for CalibratePage, VideoStage, Timeline and ExportTab, all 45 generated file hashes, and unchanged source during the build. The existing `apps/web/dist` was not a build target. The independent evidence agent's final actual-browser run, `prod_20261105_product_smoke_v5`, passed: six correct pixel seeks, four matching actual downloads, failed/unavailable recording handling, 17-column CSV contract (zero data rows in these two diagnostic sessions), public/private serialization and cleanup. Its 309-source, 45-build-file and input guards stayed unchanged; reported result SHA256 is `3c2bb9d86cc4165d1f0c7669bfedaa63afd38141b8fc9b24fc51dc6823751e78`. That browser smoke uses an isolated 67-frame fixture with neural models disabled and makes no sports-accuracy claim. It validates the final built product paths it exercises; the three controlled component contracts establish this calibration-ordering repair separately.

No neural inference, Python/API source change or deployment was required. The original v4 failed run remains a failure in the historical record; its green repeat does not erase it. The new 226/226 result applies to the repaired source and explicitly added regression coverage. Same-frame geometry refresh across analysis generations was observed as a separate possible limitation of the existing seed key, but has no demonstrated causal role here and was not changed.
