# Real doubles pipeline diagnostic — 2026-10-29

A 15-second public doubles clip completed the real pipeline locally on the RTX
4000 Ada with the existing `.venv` and `gpu-rtx4000` profile. This is a narrow
integration and sampled localization diagnostic, not a general accuracy result.
No user session was changed.

## Source and review protocol

Source: [BWF TV — Men's doubles showdown as Rankireddy/Shetty contest
Kedren/Puavaranukroh](https://www.youtube.com/watch?v=u1214klm42s), source interval
60–75 seconds. The downloaded 720p clip has 375 frames at 25 fps. Media SHA-256:
`fb51eae2db75f554c0521e726dd6c8bc8e81f514ff531733dffc9ecd44d7018b`.
The source overview shows four visible court players and one continuous camera
view. A rally ends near the end of this interval; the clip starts during play.
Media is retained locally under `data/audit-20261029/doubles/`, not committed.

Frames 0, 125, 250 and 350 were selected before inference, then visually inspected
at native resolution. The committed [draft labels](doubles-20261029-labels-draft.json)
contain approximate visible-body boxes for court players, excluding racket extent,
officials and crowd. Their exact pre-inference SHA-256 is
`bde551128c57e00a09cfcb29465ecc7df8028c6faceccc7644d1a84020bbd0b7`.
Labels are explicitly AI draft, with `human_verified=false`, no durable person IDs
and no keypoint ground truth. The [source record](doubles-20261029-source.json)
binds source, selection and scope. The analysis proxy preserves the dimensions,
frame rate and frame count; its SHA-256 is
`c8eda488ce461aabf95cb8968b61c5201c5c8d0e9c60b1f2cf81867dfd3a312b`.

## Completed run

The first attempt was interrupted with the parent task and has no completed
result. The successful fresh run is
`data/audit-20261029/doubles/candidate-rerun/`. It freezes a copy and hashes of all
pipeline source files, profile, registered model artifacts and source/label bytes.
RF-DETR, RTMPose and TrackNetV3 loaded actual weights; court calibration was
automatic, without supplied corners. The score bug was read by the configured OCR.

| Observation | Result |
| --- | ---: |
| Analysis frontier / total frames | 374 / 375 |
| Elapsed time including model and OCR startup | 59.40 seconds |
| Frames with four visible stored player boxes | 346 |
| Frames with three / two boxes | 8 / 6 |
| Frames without stored player boxes | 15 |
| Player rows / rows with pose keypoints | 1,420 / 1,291 |
| Shuttle rows / visible shuttle estimates | 375 / 293 |
| Finalized heuristic contact and stroke candidates | 19 each |
| Named player rows | 0 |
| Official rallies / preliminary rallies | 0 / 1 |
| Anonymous movement episodes with samples | 7 |

These counts measure available output, not detection or pose recall. Frame 0 has
no tracks because calibration is reacquiring; frames 0–5 have no admitted players,
and four appear at frame 6. Additional missing/partial coverage remains in this
short clip. The completed run reports no missing runtime capability degradation,
which does **not** mean every frame has complete evidence.

All four players match the pre-inference draft boxes at IoU ≥ 0.5 on each of
frames 125, 250 and 350. Frame 0 contributes four misses. Across the declared
sample there are 12 matches, four misses and no extra predicted boxes. The
evaluator sets `accuracy_claim_eligible=false` and identity eligibility false.
No labels were edited after seeing predictions. Four distinct temporary tracker
keys on the three successful sample frames do not establish durable identity.
The saved `sampled-overlays.jpg` was visually inspected: boxes locate the court
players; observed pose points are visible, but joint-level correctness is not
quantified, particularly under overlap and rapid motion.

Anonymous episode movement is available, including four longer temporary episodes
with 320–358 accepted samples; seven episodes show that tracker birth/reacquisition
still occurs. Distances and position samples remain qualified as partial
heuristic court-plane estimates, never named-player or whole-match distances.
All 19 candidate strokes belong to the preliminary rally; no unlinked stroke is
left behind. No score, winner or official match statistic is manufactured from
this mid-rally excerpt. Shot-family and contact accuracy were not labelled here.

## Reproduction

Use the existing authorized GPU environment, coordinate exclusive inference access,
and choose a new output directory. The harness snapshots pipeline sources before
running, copies the media, creates an isolated doubles session, verifies the
source-bound labels and writes coverage, draft agreement, match analytics and
anonymous episode analytics. Do not modify labels to improve agreement.

```bash
.venv/bin/python research/evaluation/run_doubles_probe.py \
  --source data/audit-20261029/doubles/source-60-75.mp4 \
  --labels docs/testing/doubles-20261029-labels-draft.json \
  --provenance docs/testing/doubles-20261029-source.json \
  --output data/audit-20261029/doubles/new-run
```

The same downloaded clip is required for exact source hashing. A later download
can produce different compressed bytes and requires a newly bound source review;
never bypass the digest check. The saved run's pipeline snapshot is immutable;
subsequent harness improvements only added explicit provenance input and automatic
export of the same episode folds, which were also computed read-only for this run.
