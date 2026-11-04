# Test 1 investigation and experiment governance

Status: all seven specialist audits reviewed; consolidated diagnosis exists and
the orchestrator has closed the investigation gate before production changes.
Test 1 is development footage. Every result from this mission is exploratory;
there is no independently held-out rally-boundary dataset available here.

Frozen production: `301baf08be5e989dd0ed93cb885733c3cf6f356a`.
Frozen benchmark evidence: `b773e20c62d1c398cddc3d23510bd4adf823325b`.
`research/evidence_registry.json` pins every existing baseline artifact and
perception-cache file, original media/annotations, production source, and active
checkpoint bytes. Nothing below `outputs/benchmarking/test1` may be written.

## Controls

| ID | Intervention | Role | Acceptance / interpretation |
| --- | --- | --- | --- |
| audit-baseline | None; recompute evaluator into new directory | Verify measurement | Exact complete metrics JSON equality, unchanged matcher |
| replay-baseline | None; production semantic engine on recorded perception | Trace decisions | All 49 interval endpoints must reproduce exactly before causal use; explicitly not fresh inference |
| temporal-audit | None; source/proxy PTS, counts and visual comparisons | Rule out timebase error | No fitted offsets; investigate any mismatch rather than correcting labels |
| failure-cases | None; recorded observations, events, transitions and source images | Review errors and controls | All six misses, eleven multi-segment labels, outliers, nineteen unmatched predictions and controls retained |

## Candidate interventions awaiting specialist diagnosis

| Candidate | Single variable / mechanism | Required control |
| --- | --- | --- |
| motion-confirmation-clock | Merge based on motion-run onset rather than its delayed confirmation | Closely spaced distinct rallies, contact starts, cut barriers |
| stationarity-buffer | Configured stationarity window must size the history buffer | Defaults identical; windows below/above ten work |
| supported-occlusion | Valid reconstructed trajectory supports continuation without becoming an observed shuttle/contact | No new starts from interpolation; legitimate breaks remain separate; view/cut barriers |
| TrackNet window overlap | Change step only, same checkpoint and precision | Full-frame outputs already exist at step8; measure cost and downstream metrics rather than assuming frame skipping |
| temporal evidence fusion | Independently inspect observed/missing/reconstructed motion and contact evidence | Player movement alone cannot start/extend play; no invented observations |

The final matrix will record actual executed configurations and ablations after
the audits. Candidate names are hypotheses, not preselected fixes.

## Acceptance and regression gates

Use the frozen maximum-cardinality one-to-one matching at IoU >=0.5. Retain all
seven primary columns. Report detection, start/end bias/MAE/RMSE/p90/max,
duration, IoU and both tolerance denominators. Add raw duration/IoU distributions,
fragmentation/coverage and no-overlap prediction counts without replacing metrics.

For a boundary-improving candidate, require baseline-or-better detection F1,
mean IoU and both start/end MAEs, and inspect every newly missed/extra rally and
every worsened severe outlier. A neutral correctness fix must pass its focused
counterexample, retain default baseline behavior where relevant, and pass the
existing component/plugin/integration tests. An interacting change requires
separate ablations. A replay improvement is not accepted as end-to-end evidence:
the selected candidate must run the original full video through production.

Record exact code fingerprints and working-tree diff, configuration, checkpoint
and input hashes, versions, device/precision, resource measurements, logs,
predictions, unchanged evaluator outputs and baseline comparisons per run under
`artifacts/benchmarking/experiments/<id>/`. Do not install/replace the server
environment or stop other workloads. Missing baseline per-stage resource data
must remain unavailable rather than reconstructed as if measured.
