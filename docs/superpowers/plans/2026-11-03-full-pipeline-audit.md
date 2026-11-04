# Comprehensive pipeline audit execution plan

Build on the uncommitted, verified score-integrity candidate at `full_pipeline`
HEAD `cc73688630e40d534d94b7ef32bd0cbfed7e0571`. Preserve every unrelated change.
No commits, deployment, dependency installation, model download or saved-session
reanalysis. Author locally and transfer scoped Git patches; execute all tests and
media work on the existing GPU-server environment after sourcing `../gpu-env.sh`.

1. Record current Git state and preserve prior evidence (1,356 Python tests,
   149 frontend tests, score lifecycle browser test). Audit actual entry points.
2. Parallel inspection with exclusive ownership: backend/runtime agent owns
   registry archive handling and export fixes after RED; frontend/analytics agent
   owns product projections and frontend failure fixes after RED; perception agent
   owns background retention after RED. Principal owns media/runner, bus/config,
   shared contracts, final ledger/validation/report and all runtime execution.
3. Reproduce confirmed archive integrity, product projection, media stream,
   cancellation, timeout and export publication defects. Implement bounded fixes,
   preserving model baselines and uncertainty; inspect downstream effects.
4. Run critical API/event contracts and all supported browser workflows (upload,
   processing, playback, four-person identity/hitter/service review, score correction,
   history, missing-record/error/preferences). Use real API/media where available;
   label authentication UI mocks and controlled observations explicitly.
5. Integrate component inventory, event/dependency graph, contract matrix, feature
   readiness and unresolved risks into the requested phase-2 ledger and validation
   document. Keep historical reports clearly dated; do not substitute prior
   synthetic or unlabelled checks for independently reviewed footage.
6. Run final full Python/frontend suites, typecheck/build and scoped lint on the
   candidate. Review the diff, verify unchanged Git HEAD/index/unrelated files,
   and retain reproducible patches/logs outside user sessions.

Validation directory: `../full-pipeline-audit-validation-20261103` on the GPU server.
The isolated candidate remains `../event-score-integrity-20261103`; the primary
application and its session data remain untouched. All new regression tests are
unexecuted until their remote log records otherwise.
