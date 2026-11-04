# Real-video, ONNX and Redis Validation Plan

> **For agentic workers:** Continue the existing isolated GPU checkout; author code locally, transfer through Git patches, and verify each task before recording completion. Keep all changes uncommitted.

**Goal:** Remove the missing ONNX exporter and Redis service blockers, exercise real server/model boundaries and run fresh real-video analysis with reproducible evidence.

**Architecture:** Keep the configured Pascal CUDA/FFmpeg runtime and existing `.venv`. Add only missing exporter support after inspecting a dry-run resolution. Use a private loopback Redis instance and disposable API/worker data. Reuse trusted weights and copy/back up session inputs before fresh analysis.

**Tech stack:** Existing Python, PyTorch, ONNX Runtime, Redis adapter, FastAPI, badminton plugin and evaluation tools.

**Spec:** User continuation request dated 3 November 2026 and `AGENTS.md`; prior evidence in `docs/architecture/full-pipeline-phase-2-validation.md`.

## Constraints

- No commits, production deployment, unrelated changes or replacement of CUDA, Torch, FFmpeg, ORT, existing weights or baselines.
- Execute tests, inference, dependency resolution and media work on the GPU server after `source ../gpu-env.sh`.
- Use idle GPU1 when available; preserve unrelated processes and keep Cloudflare disabled.
- Verify licenses for added dependencies/service. Record package versions and before/after environment inventory.
- Treat reviewed target labels separately from runtime diagnostics. Do not promote drafts or synthetic observations into ground truth.

## Task 1 — Establish runtime and label inventory

- [x] Verify local and isolated-server HEAD, working trees and prior patch identity.
- [x] Record all installed distributions, GPU use, tools/listeners, trusted artifacts and source/proxy/session identities.
- [x] Search existing annotations for reviewed status, exhaustive windows, media binding and independent review. User supplied Drive/Part2; matching Test7 is already on the server. Raw references are diagnostic only.

## Task 2 — Resolve ONNX export and execution

**Relevant files:** `engine/pyproject.toml`, `sports/badminton/src/bai_badminton/perception/tracknet.py`, `research/validate_phase2_tracknet_runtime.py`, focused TrackNet cache tests and a new bounded parity harness if required.

- [x] Capture the missing-dependency failure and inspect official exporter requirements.
- [x] Resolve additive exporter packages without upgrading the configured inference stack; user approved four exact additions. Record artifacts/licenses and exact install command.
- [x] Export the existing pinned checkpoint into a fresh validation cache and check graph contract, CPU execution, CUDA execution, dynamic batch and cache reuse.
- [x] Compare actual Torch and ONNX heatmaps plus real-frame detections using explicit tolerances; do not infer accuracy from parity.
- [x] Reproduce any discovered exporter/contract defect before the smallest correction and focused regression. No new production defect was found; dependency readiness was the blocker.

## Task 3 — Resolve Redis service and external runtime

**Relevant files:** `engine/src/bai_engine/bus.py`, `runtime/runner.py`, `apps/api` external settings/routes, new opt-in integration harness/tests.

- [x] Inspect existing Redis binaries/container images before adding a service. Build approved Redis7.2.12 outside the repository; use loopback16379 and own data directory.
- [x] Verify real fractional BLPOP timeout, command transfer and pub/sub across independent connections/processes.
- [x] Start separate API and engine processes using existing Python and the same disposable data/Redis instance. All13 upload/state/WebSocket/restart/reanalysis stages passed.
- [x] Record acknowledgement/crash-recovery limits explicitly. No new production correction was required; crash-safe acknowledgement and general writer/reset fencing remain unverified.
- [x] Stop only owned processes and retain logs/receipts. No forced process cleanup; verified private Redis shutdown with an empty database.

## Task 4 — Fresh real-video validation

**Relevant files:** current evaluation/runner interfaces, new reproducible harness under `research/`, optional focused harness regressions.

- [x] Select existing broadcast/singles and four-player multi-court recordings from the server catalogue.
- [x] Preserve original results. Create separate candidate sessions/data and record source/proxy hashes, calibration/roster provenance, model digests, profile and runtime.
- [x] Run continuous fresh inference through the existing sport/engine boundary rather than replaying only cached perception. SampleRally480 and Test7 10,725 frames complete; A02 1,800-frame prefix partial. Required stages exercised and implemented consistency checks passed.
- [x] Evaluate eligible independent labels if available; otherwise retain unknown accuracy and provide reviewable output and annotation readiness. Part2/Test7 intervals used only for a hash-bound diagnostic table; winner/accuracy evaluation withheld for documented provenance/mapping gaps.
- [x] Inspect representative video/overlay evidence; run affected regressions and integration checks.20 harness tests and full1,418-test backend suite passed; scoped Ruff passed.

## Task 5 — Evidence and preservation

- [x] Add a dated runtime/real-video validation report with exact commands, results, failures, remaining limits and artifact paths.
- [x] Update the current validation ledger without rewriting historical results.
- [x] Review the final diff, preserve unrelated files/index and compare final source patches between local and GPU checkouts. All95 scoped paths and80 source/test/configuration paths matched by Git tree and patch bytes; real indexes remain empty.
- [x] Keep all changes uncommitted; record service cleanup and continued primary-service health. Primary `/api/health` returned200 `status=ok`, primary PID/HEAD/folders preserved, Cloudflared absent.

Executed evidence: [runtime/real-video report](../../architecture/real-video-runtime-validation-20261103.md).
Local/GPU source-patch and temporary-index tree equality are recorded with the
remote transfer receipts. Missing reviewed accuracy and advanced Redis guarantees
are recorded limitations, not completed capabilities.
