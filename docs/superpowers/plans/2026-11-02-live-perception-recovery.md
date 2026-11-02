# Live badminton perception recovery

**Goal:** Restore the existing video overlays and evidence-based score pipeline on the actual GPU deployment, preserving source videos, saved analyses, participant input and the shuttle trail.

**Architecture:** Retain SessionRunner → BadmintonPerception → BadmintonMatchEngine → SQLite/Parquet → REST/WebSocket → frame-indexed canvas and scoreboard. Source and tests are edited in the Windows checkout; an isolated GPU-server Git checkout supplies all execution and validation. No model/package installation or architecture replacement.

**Spec:** User attachment `1372a10d-94af-450a-a69d-03af1e606ade/Pasted text.txt`, 2 November 2026. Its feature list is the repair scope, not evidence that a component is actually broken.

## Protected state

- Preserve the existing Design deletions, web dependency-file edits, research note, Part2/, SportsVideoAnalysis/, client-website/, and server apps/web/dist.old/.
- Keep credentials out of Git. Use the existing server .venv and source ../gpu-env.sh; leave CUDA/FFmpeg and unrelated processes unchanged.
- Disable the task's Cloudflare tunnel during validation; use SSH forwarding/localhost. Restore public access without a passphrase after validation.
- Copy session results and use SQLite's backup API before any reanalysis. Never infer participant names or point winners merely to populate the UI.

## Investigation evidence

- Production HEAD is `510b703`; local HEAD is `fd11525`, including undeployed recovery commits `74a200a` and `9e105e9`.
- Affected recording: `01M56T2EED5Z7W9VTGG19FHNTF`, He/Ren vs Rankireddy/Shetty, 12,148 canonical frames at 25 fps, 1280×720.
- Stored player rows: 27,296; named player rows: zero; rows with poses: 19,560. Production wire encoder omits anonymous players, so neither their boxes nor poses reach the canvas.
- The existing 1–0 point at frame 849 is a human correction. It is not proof of an automatically observed opening score. Existing saved analysis has no broadcast-score event in the first 2,000 frames.
- Independently, the current overlay loops over players only when boxes or poses are on, incorrectly hiding name labels when their own toggle is on alone.
- EventLog.latestBefore selects the first event at a tied frame rather than the highest sequence; a late older packet can select stale authoritative score/calibration data.

## Execution

- [x] Read the supplied mission, production source, recovery history, wire boundaries and real session metadata without reanalysis.
- [ ] Transfer local HEAD and new failing regression tests with a Git bundle to an isolated server checkout. Share only existing runtime/model assets, not mutable test data.
- [ ] Run the anonymous-player transport fixture, detector/pose/court/scoring regressions and new frontend regressions on the GPU server before production changes.
- [ ] Fix independent labels and equal-frame event ordering; test labels/boxes/poses/court/shuttle independently, including letterboxing and unknown identities.
- [ ] Run broad backend/frontend tests, typecheck, build and real installed-model inference on backed-up representative video windows. Record actual model/provider/observation counts separately from synthetic test results.
- [ ] Inspect real court alignment, identity continuity, OCR/name mapping and accepted score transitions. Repair additional demonstrated defects with focused failing tests before implementation.
- [ ] Verify protected local work, commit only this task's source/tests/report, and deploy the tested Git revision and built frontend without deleting user files.
- [ ] Confirm public REST/WebSocket delivery, visible model-derived overlays, bounded analysis playback, accepted/corrected scoring, no passphrase and the restored Cloudflare URL.

## Primary validation commands (server only)

Source `../gpu-env.sh`; activate the existing `.venv` and put this isolated checkout's engine, badminton, API, agents and research source directories first in PYTHONPATH.

Backend: `python -m pytest -q engine/tests sports/badminton/tests apps/api/tests agents/tests research/tests -m 'not network and not slow'` (explicit real GPU checks are reported separately).

Frontend, with existing dependencies: `pnpm exec vitest run`, `pnpm exec tsc -b --noEmit`, `pnpm exec vite build`; use the existing Playwright browser on localhost through an SSH forward for actual workflow verification.

Keep a defect register and exact pass/fail/skip counts in `docs/testing/live-perception-recovery-20261102.md`. No geometric or adapter check is labelled model/event accuracy.
