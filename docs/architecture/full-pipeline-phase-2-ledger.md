# Full pipeline phase 2 ledger

## Starting state and authorization

- Local branch `full_pipeline` began at `32a8295d9645d81bd1586a777541bb2f72c08bed`.
  Existing phase-1 changes were inspected and committed as `27e2a20` (22 scoped
  files), then pushed to `origin/full_pipeline` at the user's explicit request.
- Unrelated tracked deletions under `Design/production-prototype/`, web dependency
  edits, and untracked user folders remain local and uncommitted.
- The latest direct user request authorizes SSH, updating an isolated server checkout,
  and server tests/inference. It supersedes the phase brief's default no-SSH restriction.
  No credentials may be written into Git, scripts, documents or application logs.
- Server primary checkout remains on `main` at `510b7039fee99b017a643bfcaf62804f0d9b7564`,
  with untracked `apps/web/dist.old/` and `client-website/`; it was not switched or reset.
- Isolated server worktree: `/home/administrator/Desktop/sport-analytics/full-pipeline-phase2-20261102`,
  tracking `origin/full_pipeline`, pulled at `27e2a20`.
- Validation uses the existing `Sports_Analytics/.venv`, sources `../gpu-env.sh`, and
  explicitly places this worktree's packages first in `PYTHONPATH`. No environment
  installation/upgrade, model download, data replacement or deployment is authorized.
- Server runtime inventory: Python 3.12.12; PyTorch 2.14.1+cu126; ORT 1.29.0; two
  GTX 1080 Ti GPUs, 11 GiB each, with no compute jobs reported at initial inspection.
  Cloudflare PID 701600 was stopped before broader tests; it required SIGKILL after TERM.
- Phase-1 targeted tests: **44 passed**, server log
  `../full-pipeline-validation-20261102/phase1-targeted.log`. Broader baseline pending.

## Ownership and dependency order

Author code locally; transfer commits through Git. The orchestrator exclusively owns
`bai_badminton/engine.py`, perception integration, shared contract decisions, evidence
reports and server execution. Agents author focused tests first and wait for recorded
server red results before changing production code. No agent installs or runs inference,
uses SSH independently, commits shared work or edits another owner's files.

| Issue | Evidence classification and existing behavior | Expected correction / owner | Regression and runtime gates | Status |
|---|---|---|---|---|
| Reconstructed shuttle visibility reaches rally FSM | Confirmed source path: `fill_gaps` sets internal `vis`; `_advance` passes it to `RallyFSM.step` | Use observed evidence for start/end/motion while tolerating ordinary short gaps; rally agent owns `events/rally_fsm.py`, root owns engine wiring | Reconstruction-only motion cannot start/extend play indefinitely; short missing observations tolerated | Investigating |
| Non-replay cuts retain stationary/rally state | Confirmed source path: prior mask resets contact suppression but not FSM history | Explicit cut policy with no cross-cut merge/history, no inferred winner; rally agent | Open rally cut, history reset, replay, short/long gaps; related engine regressions | Investigating |
| Post-contact flight/receiver context crosses cuts | Confirmed source path: `_shuttle_around`, `post_contact_motion`, `_classify` | Shared contiguous-segment bounds and unknown context on boundary; temporal agent owns `observations.py`, `events/contact.py`, `events/stroke.py`, dedicated tests; root integrates engine | Velocity, next-hit flight and receiver cannot use another segment; no-boundary parity | Investigating |
| Raw/stabilized image coordinates can mix during recovery | Confirmed risk in `_append`: transform availability changes while shot/replay may stay fixed | Explicit temporal coordinate-context barriers and valid-transform gating; root owns engine/camera integration | Loss/recovery, invalid transforms, camera-reference changes; raw persisted image evidence retained | Investigating |
| ONNX artifact lifecycle | Existing content key and atomic graph publication, untested real export; cached graph only checked by existence | Validate/cache graph contract and digest; verified checkpoint handoff; cache agent owns `perception/tracknet.py`, `engine/runtime/registry.py`, dedicated tests | Corrupt graph, failed/concurrent publication, replaced checkpoint, first export/parity on existing trusted model | Investigating |
| TensorRT cache compatibility | Plausible risk: provider cache directory lacks complete graph/runtime/device binding | Inspect actual ORT-managed cache; scoped namespace/manifest or explicit safe fallback; cache agent owns `engine/runtime/device.py`; root wires callers | Controlled provider tests; actual Pascal provider run if supported, no environment replacement | Investigating |
| Evaluation eligibility and label readiness | Phase-1 gate passes focused tests; attestation is not independently verified truth | Audit source/split/exhaustive/unknown semantics in existing tooling; root | Invalid manifest and unknown labels; no manufactured ground truth | Investigating |
| Full-video accuracy | Independent target footage labels not yet established | Inventory trusted existing assets and reviewed labels before evaluation | Identical baseline/candidate footage, per-component metrics, GPU timing, no official line-call claims | Pending asset inventory |

## Validation plan

1. Run phase-1 focused tests and broader server baseline before further changes.
2. Commit only new focused regressions, pull them into the isolated worktree, and record
   expected failures. Implement the smallest coordinated fixes locally.
3. Commit/push/pull each scoped correction; rerun its tests, then related suites.
4. Inspect model/export/provider behavior using existing trusted weights and bounded
   synthetic inputs; do not infer model accuracy from tensor parity.
5. Exercise the integrated application on localhost/SSH forward, with existing session
   results preserved and new validation artifacts outside user sessions. Report missing
   labels, unsupported providers and runtime failures explicitly.
