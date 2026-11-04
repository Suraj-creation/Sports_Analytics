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

## Recorded exploratory decisions and next prespecified intervention

Fixed-input correctness controls: original49/30TP/F1.7059; contact-history-only
49/30TP/.7059 with slightly worse MAE; recovery-clock-only48/31TP/.7381;
combined48/31TP/.7381. Correctness and accuracy claims remain separate.

Paired actual TrackNet step8/4 on2160fixed frames:20.355/29.722seconds,
1582/1567 accepted detections, physical top gap0/17both. No detector replacement
is selected. Frozen-background/context differences are not attributed to step.

A generic interpolation pilot was rejected: F1 rose to.80 but a stationary/pickup
bridge joined adjacent labels33/34. The pilot also overlapped input-validation
hardening and is explicitly excluded from acceptance; its files remain preserved.
Strict moving-bracket support fixes that particular quality failure. A frozen
factorial comparison still rejects motion guarding: disabled F1.7381,
reconstruction-only.80, motion-only.6506, combined.7089. Higher matched IoU did
not outweigh missed rallies. No activity-only rule is promoted.

Next intervention, specified before its measurement: observed image-exit/return
support. Missing or reconstructed samples may support an already active exchange
only if independently observed moving brackets leave upward and return downward
within the top10%of the actual analysis image, remain in one coordinate/scene
context, and span at most2seconds. Existing5-frame anchor and3..120px/frame
motion bounds are retained. No XY values are filled or exposed as observations.
Camera transforms must map stabilized anchors back to their actual image frame.
No cue is supplied without available after-anchors; no extra lookahead is silently
introduced. A retained CLOSED gap candidate can recover before final publication,
but IDLE cannot start from this cue. The new switch defaults off. Test this cue
alone, then with strict short-gap reconstruction, using the same recorded inputs
and unchanged thresholds/matcher. Any full-video gain remains developmental.

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
