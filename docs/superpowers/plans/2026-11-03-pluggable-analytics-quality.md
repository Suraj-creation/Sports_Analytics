# Pluggable Analytics and Badminton Quality Implementation Plan

> **For agentic workers:** Root owns shared schemas, pipeline contracts and
> integration. Assign exclusive production files before parallel implementation.
> Use GPU RED/GREEN evidence for each change. Do not commit.

**Goal:** Make the existing platform's pipelines and components replaceable,
support singles/doubles and repair the diagnosed score/acquisition failures with
honest comparable evaluation of contacts and shots.

**Architecture:** Extend `SportPlugin`/`SportSession`, sport-owned component ports
and configurable provider factories. Preserve the generic host, durable event
authority and evidence provenance. Keep research models behind capability and
adoption gates until validated.

**Tech stack:** Existing Python3.12/.venv, PyTorch/ORT/Pascal runtime, SQLite/
Parquet, React/TypeScript. No managed runtime replacement.

**Spec:** `docs/superpowers/specs/2026-11-03-pluggable-analytics-quality-design.md`.

## Global constraints

- Edit in the current Windows checkout; tests/inference/media only on GPU after
  `source ../gpu-env.sh`. Preserve original runtime/other jobs and untracked data.
- Keep changes uncommitted and the real Git index unchanged. Transfer scoped Git
  patches; record source/model/input/configuration fingerprints.
- Back up original sessions before reanalysis. Keep Cloudflare off during tests.
- Singles and four-player doubles, uncertain identity and multi-court scenes are
  required cases. No forced identities, fabricated contacts, labels or points.
- External repositories remain outside this codebase; verify licenses and record
  notices/provenance separately for source, weights, data and dependencies.

## Task 1 — Instructions, baseline and reference audit

- [x] Update AGENTS.md, CODEX.md and CLAUDE.md with the platform contract.
- [x] Clone source-only BadmintonAI outside the application and pin its commit.
- [x] Assign separate score, contact/perception and shot/evaluation studies.
- [x] Extract Hylo baseline counts and preserve session data before experiments.
- [ ] Finish the three source-grounded studies and adoption/evaluation matrix.
- [ ] Record authoritative public benchmark annotation and source-video bindings.

## Task 2 — Acquisition and score integrity regressions

Files: `sports/badminton/tests/test_racket_observation_acquisition.py`,
`test_score_alias_transition_integrity.py`, related existing tests;
`perception/pipeline.py`, `score_ocr.py` only after RED.

- [ ] Transfer the two new regression files and instruction files with a temporary
  index patch. Check patch applicability before applying.
- [ ] GPU RED:
  `"$GPU_PY" -m pytest -q sports/badminton/tests/test_racket_observation_acquisition.py sports/badminton/tests/test_score_alias_transition_integrity.py`.
- [ ] Repair independent racket acquisition while preserving current person,
  pose, main-view and disabled-stage controls.
- [ ] Add OCR-in-play/cadence regression, then remove the unintended dependency on
  rally state while retaining configured sampling and view eligibility.
- [ ] Repair conservative aliases with singles/doubles collision controls.
- [ ] Implement explicit unique score-transition association and transactional
  claim/retry behavior; test nonofficial/ambiguous candidates cannot steal a point.
- [ ] Run affected score, temporal, perception and persistence suites and inspect
  actual Hylo OCR/attribution diagnostics after fresh inference.

## Task 3 — Component and pipeline composition

Files: new generic component contracts/tests in `engine/`; existing
`engine/src/bai_engine/sport.py` and `config.py`; sport-owned provider registration
and `perception/pipeline.py`, `events/stroke.py`, `engine.py` integration.

- [ ] Write a failing contract test that registers an independent analytics
  pipeline and replaces one stage without badminton model settings/imports.
- [ ] Define provider metadata and per-session factory lifecycle. Reject unknown,
  duplicate, incompatible and unsupported-format selections explicitly.
- [ ] Preserve legacy profiles with a compatible generic component configuration
  route; register badminton baseline factories in the badminton package.
- [ ] Wire actual perception/contact/classifier choices through those factories;
  keep baseline implementations and model pins unchanged.
- [ ] Verify component replacement, fresh state, cache/version identity,
  unsupported-format behavior and the existing sport entry-point lifecycle.

## Task 4 — Format understanding and identity-safe contexts

Files: sport-owned format component and tests, plugin/perception integration and
format configuration UI/API only where required by the declared contract.

- [ ] RED tests: sustained four-player evidence, occluded doubles, adjacent-court
  exclusion, unknown state, explicit override and epoch reset.
- [ ] Infer unspecified format from raw fresh target-court evidence before player
  truncation. Propagate the decision/capability/extra-configuration requirements.
- [ ] Keep track episodes, participants, teams and scoring slots distinct across
  changes; validate singles and doubles without forcing a named actor.
- [ ] Audit the persistent ambiguity latch and classification context failures
  using actual event/track evidence; preserve conservative naming while making
  usable provisional context reviewable.

## Task 5 — Benchmark and candidate methods

Files: research evaluation adapters/harnesses, versioned sport providers and
separate generated outputs outside Git.

- [ ] Freeze public development/evaluation windows, annotation/source/proxy
  hashes, rational FPS/time mapping and one-to-one metric definitions.
- [ ] Run the unchanged observation/model baseline and candidate on identical
  windows; record full-window and conditional metrics, confusion and abstention.
- [ ] Evaluate versioned gap/onset contact proposals with observed anchor frames;
  never turn reconstructed positions into observed physical contact.
- [ ] Run the existing CG-AP classifier shadow with explicit format and verified
  weights; compare on labels where available, keeping actor uncertainty intact.
- [ ] Add BST-0/stacked alternatives only when the actual artifact, input contract,
  training split and licensing are available. Missing artifacts remain explicit.
- [ ] Select defaults only on measured improvement; retain baseline and rejected
  alternatives with their results.

## Task 6 — Delayed scoring, visual evidence and final validation

- [ ] Test delayed OCR after finalized candidates, stale unchanged boards,
  competing rallies, cuts/row changes and unknown player/team bindings.
- [ ] Integrate bounded reconciliation and source-board transitions without tail
  completion or double-awarding. Keep accepted versus observed score explicit.
- [ ] Verify UI evidence navigation for contacts, shots and point/score changes
  at canonical frames, including unbound named broadcast values.
- [ ] Run affected suites, full backend/frontend/build checks, independent code
  review and bounded real-video comparisons on the GPU server.
- [ ] Update studies/ledger with exact results and limitations; verify local/GPU
  source identity, preservation and empty real indexes. Restore the requested
  preview only after checks; keep all changes uncommitted.
