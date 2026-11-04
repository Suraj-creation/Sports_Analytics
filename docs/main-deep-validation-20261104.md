# Main: component validation and fixes — 2026-11-04

GitHub main and local main were verified at
`80d8c0a86da4157d546f33e6e3b2d67a4e25e9c0` before work. There were no newer
remote commits to import; the GitHub connector confirmed this again before
publication. Ordinary Git networking cannot resolve GitHub in this executor.
All changes and tests were made on the primary `main` checkout.

## Final results

- **1,948 Python tests passed**, with no failures, errors or skips, in 297.49 s.
  This is one combined run across engine, badminton, agents, API and research.
- **186 frontend tests passed** across 40 files; TypeScript and production build
  passed. These are component/DOM tests, not a browser deployment test.
- Ruff passes on every modified or added Python file; diff whitespace and both
  shell launchers pass their checks. The server wrapper's `--help` path works.
- A fresh, complete **480-frame CPU inference run passed** its runtime and score
  consistency checks, with no degraded or unavailable component. Original
  recordings, application sessions, reviews and model assets were not modified.
- The combined Python run emits 19 existing Starlette deprecation warnings about
  the older HTTP 422 constant. They are not failures.

The former synthetic/score failures were fixed through explicit input evidence
and review labels, not by allowing the production pipeline to invent names,
contacts or points. The historical consolidation/review reports describe the
earlier checkpoints; this report records the subsequent fixes and final run.

## Production fixes

1. **Shutdown ownership fence.** Engine shutdown now rejects late starts, joins
   the command consumer and session writers within one timeout budget, and
   reports a timeout instead of implying a writer has stopped. Command fallback
   rechecks ownership after a recursive start; shutdown or a deleted session
   cannot cause a missing-runner `KeyError` or forward a late command.
2. **API lifecycle cleanup.** Exceptional application exit and partially failed
   engine startup stop the engine before releasing shared handles. If shutdown
   times out, repository and transport remain open for the active writer and
   explicit retry. After successful shutdown, a transport-close error does not
   prevent repository cleanup. Regression tests cover each boundary.
3. **Executable stroke profiles.** All four built-in profiles explicitly select
   `stroke-rules-v0`; they no longer advertise an unavailable BST checkpoint.
   The actual rule algorithm is unchanged. A singles/doubles contract test runs
   the selected classifier with an empty artifact registry and verifies honest
   abstention without hidden checkpoint dependencies.
4. **Launcher consistency.** The versioned launcher sources the existing
   Pascal/FFmpeg environment when present. The local `../start-server.sh` wrapper
   delegates to it instead of forcing invalid external-engine/no-Redis settings
   and disabling the engine. Neither a real listener nor the production server
   was started during validation.

## Test and fixture repairs

- Synthetic perception declares actual detector matches, fresh observation
  cadence and model provenance. An integration test verifies that real default
  ingestion yields anonymous contacts/classification while awarding no points.
- Legacy tests that isolate named downstream geometry/scoring explicitly supply
  their synthetic actor labels through a pre-ingest, singles-only test seam.
  That seam is not a production identity-review API or automatic identity proof.
- API and assistant fixtures use explicit reviewed contact/span/winner labels,
  real score refolding and reviewed provenance. Replaced inferred strokes are
  retracted, avoiding duplicate canonical shot records. Serve timestamps retain
  the first labelled contact, and event replay follows append sequence rather
  than frame order after corrections move event boundaries.
- Older monkeypatches were migrated to the actual injected component ports.
  Unspecified-format tracking retains four-person capacity. Identity uncertainty,
  geometry freshness, score transition uniqueness and transactional rollback
  regressions remain enforced.
- Threaded LocalBus tests retain real producer threads and exact delivery/order
  checks, with deterministic subscription cleanup and bounded async polling.
  Production transport was not changed to accommodate this executor.

## Component coverage

| Area | Exercised behavior |
| --- | --- |
| Generic host and components | Independent non-badminton pipeline execution, component replacement, typed configuration, capabilities, checkpoint/reset/close and failed construction cleanup. |
| Acquisition and media | Real FFmpeg upload/probe/proxy/HLS, canonical frame identity, rotation, seeking, shared preparation locks, cancellation and child-process cleanup. |
| Models and caches | Verified snapshot bytes, atomic/concurrent pin publication, archive extraction, graph/cache identity and offline CPU model loading. |
| Perception and tracking | Detector/pose/racket/OCR contracts, observation freshness, calibration loss/reacquisition, camera cuts, multi-court exclusion, four-person capacity and identity epochs. |
| Contacts and classification | Anonymous contacts, raw-turn versus body-supported evidence, replaceable providers, missing-evidence abstention and cancelled-exchange retraction. |
| Format, rallies and scores | Singles/doubles/unknown format, interval-bound decisions, match phase, legal score state, observed OCR transitions, replay/ambiguity gates, correction/refolding and restore. |
| Persistence and scheduling | Event transactions, generation refresh, reanalysis preservation, writer ownership, stop/delete/start races and partial startup. |
| API and assistant | In-process HTTP, auth, uploads/playback, WebSocket revisions, review routes, exports, analytics snapshots, citation grounding and stale-analysis answer rejection. |
| Frontend | Playback/selection state, score frontier and broadcast precedence, evidence/review components, revision-aware queries and production bundling. |

## Fresh real-video evidence

The full SampleRally run processed 480/480 frames in 157.90 s on CPU, using copied
and SHA-verified TrackNet, RF-DETR and pose artifacts. Existing OCR package weights
were used without downloads. It completed 64 shuttle forwards, 80 detector calls,
76 pose calls and 8 OCR calls. Coverage included 95 observed shuttle frames,
762 player rows and 119 racket rows; 478 frames had valid calibration.

There were **three provisional anonymous contact hypotheses**, not zero contact
execution. They were retracted when six provisional exchanges lasted only
2, 19, 42, 2, 12 and 11 frames, below the configured 60-frame minimum. One exchange
also ended at an inferred-format boundary. The resulting canonical log contains
no accepted contacts/strokes/rallies/points. Read-only replay of retained
observations reproduces the source ledger: sparse shuttle coverage and absent
two-body proximity support explain rejection. No model thresholds, identity
guards or minimum-duration checks were relaxed to increase output counts.

A separate configured-doubles 64-frame prefix also ran without unavailable or
degraded components and preserved consistent state. Its opening had no eligible
main-court view, so detector/pose/shuttle forwarding were not exercised and its
report correctly remains **partial**, not successful doubles accuracy evidence.

These runs verify execution and conservative evidence handling. They do not
establish physical contact truth, hitter/classification accuracy or scoring
accuracy. Improving sparse predictions requires a comparable source-bound
labelled evaluation; runtime completion and green tests cannot substitute for it.

## Reproduction and environment limits

Source `../gpu-env.sh` and use the existing `.venv`; do not resync the pinned
Pascal runtime. The combined command was:

```bash
export PYTHONPATH="/tmp:$PWD:$PWD/engine/src:$PWD/sports/badminton/src:$PWD/apps/api/src:$PWD/agents/src:$PWD/research"
.venv/bin/python -m pytest engine/tests sports/badminton/tests agents/tests \
  apps/api/tests research/tests -p deep_api_selector -q --tb=short
```

`deep_api_selector` is a validation-only `/tmp` plugin that polls the asyncio
selector every 10 ms. This executor does not reliably deliver idle cross-thread
selector wakeups. It does not replace HTTP, WebSocket, storage or model behavior;
in-process TestClient calls still exercise the actual application. Its exact
source is retained with the test logs, not installed in production.

NVIDIA-SMI cannot communicate with the driver and Torch reports CUDA unavailable.
AF_INET socket creation raises `PermissionError`, preventing a real TCP listener
and browser/network-listener end-to-end tests. GPU inference, GPU throughput,
full reserved-video accuracy and real-browser deployment behavior remain
unverified. No claim of universal correctness or production readiness is made.

Logs, the selector plugin, launcher evidence and compact inference reports are in
`../backups/main-deep-validation-20261104/`. Component logs and read-only contact
diagnostics are in `../backups/deep-main-20261104/`. Full fresh observations remain
in the isolated `/tmp/sport-main-cpu-full-resumed-20261104/` run directory.
