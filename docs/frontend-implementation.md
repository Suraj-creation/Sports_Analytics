# Rally production integration

Branch `front-end` starts at remote `origin/main` commit `13b3d10`. The committed design reference is `apps/web/prototype.html` and `apps/web/src/prototype/`; it remains an independent reference entry. Existing untracked `apps/web/dist.old/` is preserved.

## Architecture and implementation plan

- [x] Serve an authenticated catalogue projection in `bai_api.product_analytics`, using the canonical event/track analytics cache. Return explicit availability and event lineage. Aggregate people only from explicit session names; P1/P2 are local tracks, not global identities.
- [x] Add `features/product` for the catalogue query, typed contracts, focused route screens, shared presentation, and filters. Home, matches, moments, people and progress share one query instead of per-card network waterfalls.
- [x] Retain production video, socket, upload, correction, calibration, exports and grounded ask workflows. Extend the match workspace with prototype navigation and per-player analysis. Keep clip seeking in canonical frames.
- [x] Adopt the committed warm-paper/teal design tokens and navigation without importing fixture generators in production. Route pages preserve the prototype's hierarchy, card structure and information architecture.
- [x] Independently verify API aggregation, partial processing, authentication, video range delivery, frame links, filters, player selection and narrow screens. Run backend tests, frontend tests, typecheck, lint, build and browser workflows.

## Data and ownership map

| Area | Implementation boundary | Authoritative source |
| --- | --- | --- |
| Catalogue, history, people | Backend product analytics projection | Persisted sessions plus canonical events and tracks |
| Match metrics | Existing AnalyticsCache and analytics API | Corrected/retracted event folding; official rallies |
| Court maps | Existing heatmap endpoint | Calibrated tracks and shot evidence |
| Video | Existing HLS, progressive media, playback store | Stored source/proxy, media FPS and frame boundaries |
| Upload, calibration, corrections | Existing production workflows | Authenticated API and CSRF validation |
| UI | Production components and route modules | Committed prototype design; no fixture imports |

Frontend specialist owns the match workspace, video integration, shell and theme. Backend specialist owns projection routes and API tests. Pipeline/quality specialist traces evidence and independently verifies browser and pipeline behavior. Lead owns catalogue route integration, shared contracts, review, documentation and final acceptance.

## Evidence limits

The current player identity contract is P1/P2. Four-person doubles attribution, partner identity, pair chemistry and independent per-partner movement require additional tracking/identity evidence. The UI must explain this limitation. Rule-based shot naming is a preview. Receiver positions are not shuttle landing coordinates. Movement metrics require calibrated tracks and carry tracking jitter. Cross-match names are explicit labels, not verified person IDs. Processing outputs must not be represented as completed results.

No session reanalysis is needed for this integration. Any future reanalysis requires a result backup per AGENTS.md. Geometric exclusion is not labelled event/shuttle accuracy.

## Reliability and security changes

The analytics cache now invalidates on event database generation, event revisions, track publication and media timebase changes, including an equal-event-count rebuild. Public session responses and WebSocket initialization omit private source URIs; the persisted original source and authorized media endpoints remain intact. Upload cancellation rejects its pending operation instead of leaving it unresolved.

Before semantic reanalysis, the engine takes a consistent SQLite backup and copies tracks, exports and session metadata into `data/backups/<session_id>/<UTCtimestamp>-<ULID>/`. Media and perception are retained in their existing locations. Backup failure or a writer that does not stop prevents reset. Incomplete snapshots use `.incomplete`; existing backups are never overwritten. Backups are retained independently of recording deletion; no automatic retention/pruning policy is implemented.

The control API's HTTP 202 means that a request was accepted. It does not mean processing completed. Reanalysis startup rejection preserves previous results and status, publishes a generic visible error, and leaves detailed diagnostics in server logs.

## Running the integrated application

```sh
cd /home/administrator/Desktop/sport-analytics/Sports_Analytics
source ../gpu-env.sh
pnpm --dir apps/web build
../start-server.sh
```

The API serves the built application on port 8010. For frontend development, run `pnpm --dir apps/web dev`; Vite proxies existing API and WebSocket requests. The old upload workflow is at `/library`; `/sessions/<id>` links remain valid alongside `/matches/<id>`. Calibration remains at `/sessions/<id>/calibrate`.

## Remaining capability limits

Four-person doubles attribution, verified persistent athlete identity, pair history/chemistry, measured shuttle speed and longitudinal challenge rules require additional evidence or domain models. Their surfaces explain the missing input. Existing doubles footage still supports real playback, rallies and court-side analysis. The source prototype remains available for design comparison and is not the production data provider.

The catalogue serves up to the latest 500 recordings and explicitly reports truncation; when truncated, the interface identifies the scope of totals and histories. People grouping is based on explicit names, so two different people using the same label are not distinguishable automatically. A production deployment beyond the current server would also need an agreed backup-retention and recovery policy.

Detailed pipeline lineage, available real recordings, test coverage and browser evidence are in `docs/pipeline-validation-notes.md`. GPU model accuracy was not re-evaluated; test-profile media and existing persisted analyses verify application integration, not detector/shot/event accuracy.

## Final verification, 23 October 2026

- Complete CPU regression: 228 passed, two pre-existing deprecation warnings, 129.20 seconds. Command: `.venv/bin/python -m pytest engine/tests sports/badminton/tests agents/tests apps/api/tests -q -m 'not gpu and not slow and not network' --disable-warnings`.
- Frontend: 43 tests passed; TypeScript passed; Biome passed with six existing `noExplicitAny` warnings in legacy contracts/utilities. Production build passed.
- Browser: six end-to-end tests passed in 19.6 seconds against a separate temporary model-free server. Read-only checks on four actual stored recordings reconciled 98 official rallies and 636.1 seconds of active play; bounded seeking was independently verified on the singles footage.
- Responsive court layout was checked at 390 px after fixing the intrinsic-width canvas overflow. Prototype and production screenshots were compared with identity dialogs dismissed.
- Automatic backup failure, an unresponsive reanalysis writer, duplicate reanalysis, visible async failure and an unresponsive deletion writer are covered by temporary-session regression tests. No real recording was reanalysed or deleted.
- GPU-, slow- and network-marked model tests were not part of the CPU command. Existing model accuracy was not relabelled or inferred from interface tests.
