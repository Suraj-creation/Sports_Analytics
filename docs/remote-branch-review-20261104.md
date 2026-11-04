# Remote branch review and differential validation — 2026-11-04

Baseline: `09b376acf8d88144b6184e87dc25375dd8772f9f`.
Remote heads were verified through GitHub before review:

| Branch | Head | Decision |
| --- | --- | --- |
| `fix/pipeline-tracking-reliability` | `c9293016d5d129e14de6f307bb5d10bd45790c2e` | Integrate remaining compatible changes through the review branch, which contains this commit. |
| `review/pipeline-reliability` | `c4b1b96a5cc6a45014a608f40207766d511cab36` | Integrate the reviewed resolution; no new failing cases in the differential suites. |
| `client-website-immersive` | `4654ae30afffdd4de75fc98b84473dfee1e86f9d` | Do not merge or delete: clean-checkout build fails on a missing video. |

## Review findings and resolutions

Both pipeline branches overlap newer mainline work and produce 36 conflict paths.
Their original tracking, identity-successor repair and research probes are already
represented in main. Blindly restoring their older files would overwrite newer
component boundaries, score reconciliation, media/model integrity and anonymous
participant handling. The resolution retains the mainline versions of those
conflicting files, including intentional removal of the obsolete participant UI.
The resolved tracking and review candidates initially have identical trees.

The useful remaining changes tighten assistant grounding and citation-scoped
numbers, withhold unsupported repaired answers, and attach explicit evidence
metadata to tool results. Tool reads and answer publication check a consistent
analysis revision so a reset cannot publish an answer from replaced results.
Frontend changes make calibration query keys revision-aware, resolve corrected
event selections, distinguish estimated events from human review and show
anonymous court tracks without naming them. These checks are consistency guards,
not a claim that every cited sentence is semantically or physically verified.

The inherited branch regression test found a real mainline score-display gap:
seeking beyond the current analysis frontier still displayed an earlier score
and game-point flag. The resolution restores the frontier gate while retaining
main's newer broadcast/accepted-score precedence. It withholds both accepted and
broadcast scores outside the analysed interval and restores them when seeking
back. Two frontend tests cover those paths. Three additional API tests cover
stable citation publication and resets before and after tool reads.

The candidate changes no file under `engine/`, `sports/badminton/`, `models/`,
`config/` or `research/`: each subtree was compared against baseline and is
byte-identical. Analysis algorithms, model adapters, weights/manifest, profiles,
scoring rules, registry lifecycle and detector/participant contracts therefore
remain unchanged by this merge. The new launcher also passes Bash syntax checking.

## Differential testing

Tests used detached temporary worktrees, the existing configured Python/Node
runtime, explicit candidate source paths and private temporary test data. Original
application sessions, benchmark datasets and installed model assets were not
reanalysed or modified. Cloudflare was not used.

| Check | Baseline | Resolved candidate |
| --- | --- | --- |
| Engine, badminton, agent and research suites, excluding marked GPU/slow/network tests | 1,754 passed; 58 failed; 8 setup errors | 1,758 passed; the same 58 failed and 8 setup errors |
| Direct API score snapshot, export integrity and product projection tests | 6 passed; 9 failed | 6 passed; the same 9 failed |
| Additional answer revision guard tests | Absent | 3 passed |
| Frontend | Prior main baseline: 184 passed | 186 passed across 40 files |
| Frontend TypeScript and production build | Prior main baseline passed | Passed |
| Ruff on modified Python implementation and added API tests | — | Passed |

Machine-readable results were compared by test node ID and phase, rather than
by aggregate counts alone: no previously passing test failed and four new agent
tests passed. The frontend was rerun after the final score-frontier fixes.
The direct API revision guards exercise the actual worker-thread path and real
repository resets; a periodic async task also remains alive through executor
shutdown because idle-loop thread wakeups are unreliable in this executor.

The broad baseline is already failing, mostly in synthetic contact/identity/score
fixtures and dependent analytics. The identical failures remain unresolved;
this review does not certify overall pipeline correctness. A 20-second per-test
deadline bounded both broad runs; the same court-line plugin test exceeded that
deadline in both. Raw outcomes and logs are retained outside Git under
`backups/branch-review-20261104/`, including `differential-summary.json`.

## Website branch: blocked

The website merge has 13 conflict paths, all under `client-website/`. Its resolved
candidate uses that branch's complete website directory, and leaves engine/API
code unchanged. Brief, catalogue and vision test files pass. The full tooling
test file fails in this executor, as it also did for the prior main website.
Independently of that runtime limitation, its static reference check fails with:

```text
index.html: Missing or not public file assets/tracking-reference.mp4:
./assets/tracking-reference.mp4
```

The branch's asset provenance describes a user-supplied basketball reference
film remuxed from `Design/references/video-111.mp4`. Neither the source nor the
required public video is available in the reviewed checkout. Do not fabricate
replacement footage or publish a broken reference. Restore the intended asset
with its provenance, or explicitly redesign the section, then rerun the build
and tooling checks before merging or deleting this branch.

## Limits and deletion

NVIDIA-SMI cannot communicate with the driver in this session. Fresh GPU
inference, labelled real-video accuracy/latency evaluation, production browser
end-to-end tests and full HTTP/WebSocket integration were not validated here.
Byte-identical badminton/engine subtrees and differential tests establish only
that this reviewed resolution introduces no observed regression against the
tested main baseline; they do not establish absolute accuracy or deployment
readiness.

After the published main merge is verified, the tracking and review branches
are fully contained in main and eligible for deletion. The connected GitHub
tools do not expose branch deletion, repository auto-deletion is disabled, and
ordinary Git/GitHub CLI network access fails in this executor. Do not claim a
remote branch was deleted unless a subsequent remote listing verifies it.
Keep the blocked website branch.
