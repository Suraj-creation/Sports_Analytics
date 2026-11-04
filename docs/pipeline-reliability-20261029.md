# Pipeline reliability audit — 29 October 2026

Baseline revision: `5d76ad6`. Runtime: local Linux, Python 3.12, RTX 4000 Ada,
CUDA 13, existing virtual environment. The historical Windows/Pascal deployment
notes do not describe this machine. User recordings and credentials are preserved.

## Initial failure map (before source changes)

| Component | Observed state and evidence | Root cause / dependency | Priority |
| --- | --- | --- | --- |
| Upload / YouTube / proxy | Current YouTube recording successfully decoded to 1280×720 CFR HLS; upload/playback smoke passed | Rotated-source dimensions and warm-start orientation are not normalized; source-PTS mapping is absent | P1 |
| Court and scene | Sampled current recording aligns with court; 10,326/10,380 inspected frames have valid geometry | All perception is gated when calibration is unavailable; camera tracking is stateful despite out-of-order previews | P1 |
| Player detection | 20,382 observations in the frozen 10,380-frame prefix, visually plausible boxes | BGR is passed into RGB-normalized RF-DETR; tracker time advances by detector calls | P0 |
| Pose | 18,137 finite 17-joint poses in the same prefix, visually plausible on six inspected frames | BGR/RGB contract is wrong; valid anonymous poses disappear in transport | P0 |
| Identity and doubles | Temporary tracks and identity uncertainty are preserved on disk | Wire protocol only emits P1/P2 rows; four anonymous doubles players cannot reach the overlay | P0 |
| Shuttle | 7,627 detections in inspected prefix; this is coverage, not accuracy | Stateful background/camera history can be changed by seek-ahead previews; interpolation must remain distinguished | P1 |
| Contact events | Real ledger contains adjacent duplicate hits at 259/260, 3919/3920, 6559/6560 and other segment boundaries | Contact NMS is local to each finalized chunk; contact is estimated, not visually verified racket impact | P0 |
| Shot classification | Installed runtime uses `stroke_rules_v0`, not the declared BST checkpoint | First contact of every exchange is forced into serve context; short geometric rules lack a trained temporal classifier | P0 |
| Rallies / phase | Temporal segmentation, uncertainty and review mechanisms exist | Upstream duplicate contacts and invented serves contaminate exchange boundaries; highlights are not exhaustive raw matches | P1 |
| Movement / heatmaps | Persisted rebuild has geometry/continuity guards | Live fold omits required frames, track IDs and validity, so movement can disagree with persisted results | P0 |
| Individual analytics | Provisional track episodes and reviewed roster mapping exist | No validated durable identity through all doubles crossings; team/individual uncertainty must remain explicit | P1 |
| Highlights / AI | Event-backed summaries and deterministic numeric tools exist | Class confidence and estimated-contact qualifications are not consistently propagated; citation checks do not prove every qualitative claim | P1 |
| API / frontend | The same real 60-frame window stores 120 posed player rows but returns `players: {}` | Anonymous wire loss; stale tracks/events across reanalysis; live progress/degradation omitted; backlog capped at 20k | P0 |
| Model configuration | Active shuttle, detector, pose and OCR execute | Racket, live shuttle, second opinion, InpaintNet and BST profile fields are not all wired into the runtime | P1 |
| Evaluation | 68 frontend baseline tests pass; published FineBadminton importer exists | Plain `pytest` cannot import repository research modules; tests alone do not establish real-video accuracy | P1 |

Baseline snapshots, code archive, logs and sampled images are in the ignored
`data/audit-20261029/` directory. The original user result was backed up before
reanalysis. Measurements above are observation counts and visual spot checks, not
labelled precision or recall.

## Final reference evaluation and remaining tracking gap

Candidate-v2 was run on real CUDA inference. On development clip 0044, it matched
10 of 41 published hit anchors (25 false positives, 31 misses; F1 0.263), compared
with 9 matches (19 false positives, 32 misses; F1 0.261) for the frozen baseline.
Known-shot macro F1 was 0.0536, with 3 correct matched families; court-side was
correct on 0 of 10 matched anchors and unresolved on 7. This is no meaningful
overall accuracy gain.

On reserved-for-this-pass clip 0046, candidate-v2 matched 21 of 72 anchors (40
false positives, 51 misses; F1 0.316), compared with 18 matches (29 false
positives, 54 misses; F1 0.303) for the frozen baseline. The candidate had 0.0067
known-shot macro F1, and 40 of 61 predictions were classified unknown. Court-side
was correct on 8 matched anchors, wrong on 3 and unresolved on 10. These provider
anchors are not independently verified physical contacts; prior project results
exist on this footage, so this is not a generalization claim. The higher event
agreement comes with more false detections and the shot classifier remains weak.

The exact BST-CG-AP checkpoint and preprocessing contract are now implemented and
tested as an explicit singles shadow adapter. BST is not the live classifier: the
candidate-v1 comparison assigned known families to 16 of 19 false contacts, versus
5 of 19 for the repaired rules, while family macro F1 was 0.0550 versus 0.0593.
The active model is honestly reported as `stroke_rules_v0`; no doubles BST mode or
racket-contact detector is available.

The first full user-session rerun completed at revision 1, but review found an
unresolved singles case: frame 1500 had two valid cached player detections and
calibrated geometry yet no emitted track rows. The code previously emitted
unassigned visual tracks only after the match had already been marked ambiguous.
Track output now preserves unassigned visible bodies in singles as anonymous
observations, disjoint from named-player statistics. A fresh reanalysis is required
for this late fix to appear throughout that existing session; an earlier completed
revision remains backed up. Stateful badminton reanalysis runs sequential
perception because its observation caches cannot restore private tracker state.

## Repair and validation plan

1. Correct model color contracts and tracker time, preserve chronological perception.
2. Transport/render anonymous observations without assigning names; clear stale data
   on analysis generations and disclose unavailable stages.
3. Repair contact boundary selection, evidence for serves and the live analytics fold.
4. Normalize source orientation and validate decode/frame boundaries and lifecycle.
5. Compare frozen baseline and repaired outputs on real video, use the published
   0044 development and 0046 reserved reference protocol, and retain all misses,
   spurious events and unknown classifications in evaluation denominators.
6. Run component/regression/API/frontend tests and browser checks. Report unimplemented
   research stages and data limitations explicitly; do not claim a trained shot
   classifier, four-person identity accuracy or complete reliability without evidence.

The final local Python suite passed 878 tests with 28 dependency deprecation
warnings in 335.42 seconds. The frontend suite passed 80 tests across 24 files,
and the production build passed. The final logs are kept under the ignored local
`data/audit-20261029/` directory.
