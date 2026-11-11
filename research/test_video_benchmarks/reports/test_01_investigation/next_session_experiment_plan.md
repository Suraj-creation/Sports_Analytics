# Next-session controlled experiments — 2026-11-05

All experiments use new directories under `artifacts/benchmarking/experiments/`
with prefix `next_20261105_`. Predictions and all historical artifacts are
immutable. Test1 is exposed development footage. The unchanged matching policy,
seven-column schema, zero-origin actual-FPS arithmetic and half-open spans apply.

| Experiment | Hypothesis and exact component | Expected observable change | Negative control / risk | Evidence class |
| --- | --- | --- | --- | --- |
| v1 evaluator reproduction | Historical arithmetic remains valid | Complete metrics equality and byte-identical comparison | Original 36 rows, null misses, all extras | Read-only evaluation |
| Independent fresh v1 control | Unchanged source/profile reproduces actual inference | Compare own observations, contacts, 39 interval/reason triples, hashes and cost | Preserve checkpoint/backend/fallback and canonical alignment; measure differences rather than assume determinism | Actual full production inference |
| Bounded diagnostic parity | TrackNet and player summaries explain discarded evidence without altering predictions | Top-k raw components, masked peaks, reasons, vote/background identities and bounded rejection counters | Legacy independent providers; disabled mode; masks, weak peaks, cut/tail windows; schema/cache lifecycle | Synthetic numerical contracts, then actual paired component and full pipeline |
| Coherent exit tracklets | An isolated competing provider observation blocks an otherwise valid upper exit/return | New continuation support only with coherent observed moving brackets | Same top10%, 2s, speed and cut limits; no valid low/floor tracklet skipped; no new contacts/coordinates/idle starts; no unavailable future anchors | Cached conditional FSM/semantic, then fresh production if accepted |
| Contact motion reliability | Relative ratios amplify unresolved near-zero velocity and static-to-track switches | Finite independently inspectable per-side fit/residual/reliability; less tiny-jitter support | Weak low-speed serve, apex, strong redirect, stop, interpolation, pose dropout, independent contact port; lost legitimate hits possible | Synthetic sensitivity plus current cached windows/semantic; opt-in only without contact labels |
| Background-only | Per-shot startup/rolling median contributes to painted-line attraction | Heatmap/candidate distribution changes with identical frames, masks, checkpoint, resize and 60-frame context | Real floor shuttle, stationary line, ascent/apex/fast flight, good-control windows; fewer points alone is insufficient | Actual component inference |
| Resize-only | INTER_AREA versus reference interpolation changes weak candidate support | Paired candidates change with frozen background/context | Same controls; no larger window or step confound | Actual component inference if preceding evidence warrants |
| Foreground scene continuity | Same-camera cuts preserve global color but disrupt player motion | LK tracking/patch continuity distinguishes 10769/10770 from inspected normal fast play | Lighting, pan, blur, partial occlusion, player leap; no tuned global cut threshold promoted | Exact source pixels, diagnostic CPU probe |
| Tool correctness | Empty comparison headers and inherited executor identity are implementation defects | Header exists for empty GT; executor/trace source separated; resets derived from recorded epochs | All36 nonempty metric/comparison bytes; missing trace identity, varying epochs, overwrite refusal | Red/green focused contracts and fixed-input replay |

Initial experiments change one variable. A factorial is justified only after
component evidence identifies an interaction. Source/config/harness and input
hashes must be frozen before execution; production source is not edited during
the active fresh control. Research-only drafts may be developed separately.
Every candidate records failed/rejected outcomes as well as gains.

Each complete candidate comparison reports TP/FP/FN/precision/recall/F1; mean,
median, minimum and distribution of IoU; start/end MAE/RMSE/median/bias/P90/max;
all ±1/3/5/10/15/30 frame tolerances with matched/all-GT denominators; duration
distribution; all36 rows and unmatched predictions; common/new matches,
fragmentation, coverage and cross-run topology. Compare separately against both
original baseline and v1. Retain GT2/19/20 and all previously recovered labels.

Any accepted perception change requires fresh complete production inference,
its own cached-observation exact semantic trace and new failure packages. Replay
does not reproduce cadence feedback. Resource/stage measurements declare scope
and overlap; actual runtime records establish backend and fallback, not profile
names. Tests cover host/provider replacement, resets/rollback/EOF, singles/four
players, invalid geometry, contacts and temporal barriers. No production default
promotion occurs without independent reviewed match-disjoint validation.

## Discriminating mask experiment after bounded telemetry

The first actual component experiment reproduces all 1,811 selected rolling
observations and raw support values exactly, then exposes a previously invisible
gate: strong model peaks on GT31's source-visible ascent and return are rejected
by the finite upward mask sweep. This replaces the untested assumption that all
such provider misses are neural-model failures. GT27 also has strong early
re-entry peaks rejected while the service-T distractor remains admitted.

Before the new full component run, prescribe one change: sweep the horizontally
clipped visible court columns to the image ceiling, preserving the floor extent,
edge tolerance, view exclusion, weights, resize, threshold, background history,
60-frame context and all other providers. The optional policy has no fitted
height fraction or case IDs. Keep the existing finite sweep as the default.
Invalid/offscreen geometry and neighboring-court columns remain negative controls;
airborne image overlap still does not prove physical court ownership.

`next_shuttle_mask_experiment.py` performs fresh TrackNet inference over the
entire source timeline with cached scene/player/pose observations held fixed.
Its output is explicitly a hybrid component stream. Semantic replay can screen
the one-variable mask change and its interaction with qualified continuation;
it cannot establish full pipeline quality or cadence feedback. No labels enter
this component executor. Only a subsequent complete production run may validate
an accepted perception change. A better detector count alone is insufficient.

External screening checked original TrackNetV3 documentation, the ByteTrack
paper, WASB authors' repository and the 2026 TOTNet paper. ByteTrack motivates
retaining weak alternatives for association, but its person-box results are not
shuttle accuracy evidence ([paper](https://www.ecva.net/papers/eccv_2022/papers_ECCV/papers/136820001.pdf)).
TOTNet explicitly targets offline temporal tracking; its future context and new
runtime/weight/data grants require separate adoption work ([author-hosted paper](https://rbouadjenek.github.io/assets/pdf/YCVIU_104657.pdf)).
WASB remains a possible independent challenger with separate weight/data checks
([official repository](https://github.com/nttcom/WASB-SBDT)). No external code,
model or dataset was installed. Existing small deterministic association and
diagnostic changes are evaluated first.
