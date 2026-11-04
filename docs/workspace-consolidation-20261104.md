# Workspace consolidation — 2026-11-04

## Preserved development

The main checkout consolidates the full-pipeline reliability history through
`cc736886`, the pluggable-pipeline checkpoint `5c9b0f52`, the latest score,
format, identity and component work from `event-score-integrity-20261103`,
and the evidence-aware top-ten highlights from `84428a3f`.
The existing local client website is retained as source with its static build tools.
Older UI, identity, baseline and candidate variants were compared against this
combined tree; superseded source remains recoverable in a Git bundle.
Missing October 29 research probes and their evidence reports are retained.

Consolidation restored the verified TrackNet snapshot loader and graph-specific
provider caching from the earlier full-pipeline branch; the newer worktree had
accidentally restored an older loader. An unknown-format regression expectation
now also respects the independent physical-identity requirement for geometric
winner attribution. No automatic physical identity binding was restored.

## Validation and unfinished work

- Web: all 40 test files / 184 tests pass; TypeScript and production Vite build pass.
- Engine excluding the existing thread-fanout timing test file: 316 tests pass.
- Focused new component, score, format, identity and research coverage: 412 pass
  on the first run, with one obsolete geometry-winner expectation corrected.
- Verified-loader and unknown-format follow-up: 10 tests pass.
- Client website: static reference check and production build pass; the full
  tooling suite fails in this restricted runtime. Preview/listen tests need an
  environment that permits sockets.
- The initial broad badminton run reports 1,168 passed, 50 failed and 8 fixture
  errors. Two failing cases were corrected during consolidation. Many remaining
  fixtures expect automatic named identities / geometry scoring or use synthetic
  observations without the newer detector/participant evidence. These require
  follow-up; this commit does not claim the entire suite or production readiness.
- The existing LocalBus thread fanout test times out in this session; the same
  transport succeeds in a direct standalone asynchronous smoke check. The broad
  API run stalls in this runtime and was stopped. GPU inference, real-video
  accuracy evaluation and full browser end-to-end validation were not rerun.

This is a preservation and cleanup checkpoint. Passing runtime/unit checks do not
establish contact, shot-label, winner or score accuracy. The measured limitations
in the pipeline research report remain applicable.

## Workspace after cleanup

`Sports_Analytics` is the sole project checkout and `main` the sole local branch.
Primary application data, model assets and the configured Python/Node runtime
are retained. Private recent benchmark inputs, evaluations, licenses and profiles
are retained under `Sports_Analytics/data/research/`; they are not published.
Older task application data and pre-reanalysis session evidence are retained
under `Sports_Analytics/data/recovery/`, separate from the active session database.

Recovery history, source snapshot commit IDs, validation logs and the cleanup
inventory are retained under `backups/workspace-cleanup-20261104/`.
The verified `recent-development.bundle` contains the retired worktree commits.
Recover with `git bundle list-heads <bundle>` and fetch a selected recorded ref
into a separate checkout when needed. Source snapshot IDs are listed in
`source-snapshots.json`; retired worktree refs are recorded in the bundle itself.
Obsolete checkouts, generated validation runs, duplicate archives, preview data,
Cloudflare logs and tunnel PID files are removed. Remote feature branches are
retained as an additional recovery source.
