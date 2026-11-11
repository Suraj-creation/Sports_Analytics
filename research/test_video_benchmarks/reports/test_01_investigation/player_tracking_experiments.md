# Player/court/pose diagnostic experiments

All work is exploratory diagnostic analysis of Test 1. No production model,
configuration, interface, ground truth or baseline artifact was changed. No new
weights were fetched, and no fresh video-model inference was performed by Audit D.

## D0 — Frozen observation coverage and scheduling

Command:

```bash
source ../gpu-env.sh
python research/audit_d_player_observations.py \
  --output artifacts/benchmarking/investigation/audit_d/final
```

Use a new path for a repeat. The read-only helper checks all 288 cache chunks and
the chronological frame sequence, folds superseded/retracted raw events, and
creates global and per-rally coverage summaries. Annotation access is strictly
for diagnostic grouping; the helper never generates predictions or edits labels.
Cache file hashes are included in the JSON. The orchestrator separately pins
original media, annotation, source and checkpoint fingerprints in
`research/evidence_registry.json`.

Observed result: every canonical frame is present; zero off-schedule pose rows;
zero detector-cadence mismatches under the actual stride-1/stride-6 pose regimes.
The 33,550 player rows are explicit ByteTrack episodes. 19,947 are carried or
tracker-only rows and must not be relabeled fresh observations. 25,594 pose rows
are produced on their actual scheduled frames, including fresh current-image
poses on carried boxes. 432 live contacts still exist without named identities
or OSNet; all have two returned players at the contact frame.

This establishes chronology/provenance behavior. It does not establish person
localization, pose, identity, contact or geometric accuracy against human labels.

## D1 — Existing production component/contract suite

Executed on the configured GPU-server virtual environment:

```bash
source ../gpu-env.sh
pytest -q \
  sports/badminton/tests/test_player_reid_configuration.py \
  sports/badminton/tests/test_player_identity_provenance.py \
  sports/badminton/tests/test_pose_schedule_provenance.py \
  sports/badminton/tests/test_player_roi_continuity.py \
  sports/badminton/tests/test_four_player_retention.py \
  sports/badminton/tests/test_contact_pose_sampling.py \
  sports/badminton/tests/test_activity_false_evidence.py \
  sports/badminton/tests/test_participant_activity_integration.py \
  sports/badminton/tests/test_invalid_court_projection.py \
  sports/badminton/tests/test_engine_format_boundary.py \
  sports/badminton/tests/test_player_association.py \
  sports/badminton/tests/test_locked_court_visibility.py
```

**141 passed in 4.04 seconds.** Complete log:
`artifacts/benchmarking/investigation/audit_d/component_tests.log`.
No test was skipped in this invocation. These are controlled unit/integration
tests, many using synthetic observations or mocked inference adapters. They do
not establish the quality of a real detector, RTMPose checkpoint, OSNet model,
or actual four-player footage. Their behavior checks include:

- Explicit ReID configuration and failure provenance; raw/canonical identity
  namespaces do not silently swap after a runtime failure.
- Detector observation versus individual track matches; carried rows remain
  distinct from fresh detections.
- Pose cadence survives engine buffering, participant windows, cache round trips
  and buffer trimming; unsupported or stale schedules are rejected.
- Sparse scheduled wrist motion can be used without inventing poses at skipped
  frames, while missing scheduled observations do not become valid motion.
- Known players can jump/run outside the immediate projected floor footprint
  through unique box continuity without admitting unrelated people generally.
- Four-player retention and overflow uncertainty; unsupported extra participants
  are not silently reduced to a verified singles scene.
- Invalid court projections clear authority; locked-court visibility and view
  transitions retain explicit failure states.
- Walking plus a stationary/spurious/discontinuous shuttle does not prove active
  play. Consistent trajectories preserve time-based behavior at different FPS.
- Format changes isolate incompatible state; player/activity outputs preserve
  evidence and unknowns rather than becoming official match decisions.

## D2 — Does activity explain termination?

This is a source-and-recorded-event falsification test, not a tuned intervention.
The current FSM input has no player-moving or activity-state argument. Stationary
ending is based on observed shuttle motion. There are zero inactive activity
frames in the complete frozen event fold. Therefore the hypothesis that this
run ended rallies because the activity tracker declared players inactive is
rejected for the current direct segmentation path.

The helper groups activity intervals by annotation spans: 8,045 active-play
frames lie inside labels, 1,625 outside; 4,484 inside-label frames are unknown,
and GT24 has no active-play activity despite a good interval match. Both results
reject using this existing activity state as a hard positive or hard negative
rally criterion. No human player-activity labels were fabricated.

## D3 — Camera and identity degradation association

The six policy-FN labels are GT5,23,25,28,29,31. GT5,23,25,29 have no camera-lost
frames; GT28 has two calibration-reacquiring frames without a lost camera pose;
GT31 has 21 camera-lost frames and 23 non-VALID geometry frames. The pattern
rejects a universal camera-loss cause, while preserving a concrete GT31 review
target. GT2 and GT27 also have no camera loss and strong two-player coverage.

The missing OSNet checkpoint and disabled learned association are observed
degradations. Their causal effect is **not measured**: there is no restored-weight
run or annotated identity sequence. Raw track IDs 0..10, 37 reset ambiguity events
and participant episode churn are reproducibility evidence, not identity-error
labels. Do not report an OSNet restoration benefit without an actual ablation.

## Next controlled experiments, not performed here

| ID | Single intervention | Primary evidence / acceptance | Main risk |
| --- | --- | --- | --- |
| D4 | Event-triggered fresh pose around uncertain boundary windows | Pin detector/shuttle/segmentation; compare actual pose availability, contact timing, seven-column errors and cost | More compute or incorrect extra contacts; needs reviewed contacts for contact-accuracy claims |
| D5 | Restore the pinned OSNet provider only | Same source/profile except availability; record model hash/device and compare association, contact context, intervals | Appearance/domain mismatch and wrong identity association; Test 1 has no independent identity labels |
| D6 | Bounded frame-aligned body-motion support for doubtful stationary-shuttle end | Use existing ParticipantSnapshot/episode_window at decision time; keep starts, contacts and arbitrary-missing behavior unchanged; ablate support alone | Walking/recovery movement during legitimate breaks could merge separate rallies |
| D7 | Add compact pre/post-ROI admission/rejection telemetry only | Numerically identical predictions; counters explain whether failure arose before detector output, geometry admission, tracking or capacity gate | Cache/schema growth; do not log private embeddings or promote counters to accuracy |

D6 must never consult the current activity tracker state while deciding a frame
40 frames behind the ingest frontier. It should compute its cue from existing
aligned snapshots within a stable temporal segment, retain unknown on missing
evidence, and explicitly distinguish carried boxes from fresh poses/detections.
For all interventions retain singles/four-player component contracts, evidence
provenance and the frozen matching rules. Test 1 results remain exploratory until
independently held-out annotated footage is available.
