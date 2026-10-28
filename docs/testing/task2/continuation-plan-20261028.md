# Task 2 continuation: verified evidence recovery

This continuation addresses existing processing defects. It does not install an untrained classifier, merge ambiguous track episodes, or change live session results. The backend and Cloudflare tunnel remain stopped at the user's request. Work uses the authoritative server repository's isolated worktree, the existing virtual environment and GPU environment, and read-only source sessions.

- [x] Reproduce Real Video's rejected fixed-court frames. Record line-fit quality and compare visible projection errors with the extrapolated offscreen corners.
- [x] Change only the locked-court consistency check to compare reference-visible painted-line samples. Preserve the locked homography, existing pixel tolerance, line-quality checks, and neighboring-court rejection. Test invalid projections and camera shifts. Reject old perception caches.
- [x] Repair contact evidence for valid wrists with an occluded nose, invalid keypoint coordinates/confidence, and sparse pose schedules. Preserve actual elapsed-frame normalization and refuse to bridge missing scheduled observations or missing track boxes.
- [x] Carry pose cadence through perception, cache version 8, engine buffers, participant windows and historical replay. Keep unknown and disabled schedules explicit.
- [x] Stop detector-unavailable frames from extending trusted episode continuity or asserting observed absence. Keep short carries provisional and require a new epoch after the existing two-second outage threshold.
- [x] Complete the final regression suite and fresh baseline/new GPU runs on isolated copies of the same full Real Video source and calibration. Bind results to source and implementation hashes. Report candidate counts and resource use without claiming accuracy.
- [x] Inspect resulting evidence and reconcile the latest findings with the prior audit. Commit the incremental fixes and reports; keep deployment and original results unchanged.

Remaining Task 2 requirements after these bounded fixes: exhaustive independently reviewed contact/family/hitter annotations split by recording; validated persistent four-person identities across crossings and occlusion; trained temporal alternatives and class-specific accuracy comparisons. AI motion drafts and rally-level CSV rows do not supply those labels. A lower unknown rate or a higher candidate count does not establish a correct classification.

## Further identity and evaluation continuation

- [x] Reproduce named propagation through competing overlapping player boxes;
  abstain for involved people, preserve anonymous candidates and support re-seeding
  after separation. Keep the 0.3 IoU threshold explicitly uncalibrated.
- [x] Add source-bound sampled tracking evaluation with one global identity map,
  ambiguity-aware switch counts, stale-birth/revision checks and missed-frame
  denominators. Add known-family, per-person event P/R and joint shot/hitter scores.
- [x] Review sixteen four-person source frames and fifty consecutive action frames
  independently of predictions. Preserve both box drafts and the partial motion
  review, with AI provenance and accuracy eligibility false.
- [x] Run fresh matched GPU inference on the saved doubles clip with main versus
  denser detection. Retain production cadence because the dense experiment adds
  sampled switches despite slightly better draft box agreement.
- [x] Run regression checks, preserve original sessions and save the complete
  [validation report](validation-20261028/README.md) and reproduction artifacts.

The full Task 2 requirements listed above remain open. Neither sampled AI
agreement nor the overlap abstention guard demonstrates uninterrupted automatic
four-person identity or independently measured shot-family/hitter accuracy.
