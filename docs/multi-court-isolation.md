# Multi-court camera isolation

The incident recording is `A02_20261010205221.mp4`, session
`01M5EXGZNEVGYAJ3AR6CJS5ZG9`. Its 1920x1088, variable-rate 15 fps source is
normalised to 1270x720 at 30 fps; duplicated frames add no temporal information.
The intended court is the large right-hand court, with adjacent courts visible
on both sides and its near baseline outside the frame.

## Evidence and architecture

The initial calibration does match the selected court's visible painted lines.
The downstream failures were independent: TrackNet selected the strongest blob
anywhere in the frame; player admission used a 60-pixel margin independent of
depth; reacquisition searched every court; cached results survived code changes.

Processing order is court candidates → primary selection → temporal validation
→ camera/court tracking → feet admission and shuttle flight-region selection
→ identity, trajectory and event inference. Court geometry must remain in full
analysis-frame coordinates; a floor homography does not describe airborne depth.

Select candidates using painted-line support and physically plausible geometry
first, then visible area and centrality. Centrality alone can select an aisle;
area alone can select a false fit spanning multiple courts. Confidence and a
manual named-landmark calibration remain necessary for ambiguous scenes.

For a fixed installation, stable background correspondences across the sampled
frames identify the stationary camera and lock the selected court. Court fits
alone are not used to infer camera motion: neighbouring courts can produce
different plausible fits even when the camera has not moved.
Line verification continues; a lost or shifted calibration produces an
unanalysed frame, rather than searching for another active court. Moving
broadcast cameras retain their existing camera-head tracking.

New player tracks must first enter the selected court. Established tracks can
use a 0.35 m side and 0.75 m end tolerance, including carried tracks. Admission
expires after two seconds without observations and resets on cuts/calibration.
Shuttle heatmaps are masked *before*
choosing a peak so a stronger neighbouring shuttle cannot suppress a weaker
target peak. The flight region includes space above the floor; it is a prior,
not proof of which court an airborne object belongs to.

## Research and limits

- [OpenCV calibration and projection](https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html)
  describes projective geometry and lens distortion. Wide-angle distortion
  cannot be corrected exactly by a single floor homography. A measured lens
  calibration is needed if residuals show systematic curvature.
- [MonoTrack](https://github.com/jhwang7628/monotrack) combines court geometry,
  pose, shuttle tracking and physical trajectory inference for broadcast video.
- [TrackNetV3](https://github.com/qaz812345/TrackNetV3) uses temporal frames and
  background information. Its published broadcast-dataset accuracy is not a
  guarantee for small shuttles in a wide CCTV image.
- [CourtAlign](https://github.com/Madou10-lab/CourtAlign) provides learned court
  registration and optional motion-triggered updates. New weights need their
  own evaluation on this camera before replacing the existing line detector.

Two airborne shuttles may project onto the same allowed image region. A mask
alone cannot resolve that ambiguity. Full production accuracy additionally
needs labelled target-shuttle trajectories, contact/trajectory association,
and evaluation of precision and recall on this camera. No geometric filtering
test establishes smash or score accuracy by itself. The existing pipeline's
singles/team identity model also requires separate validation for four
individual doubles players. This change does not implement a new RTSP ingest
service; it applies at the shared decoded-frame perception boundary.

## Validation

Run `pytest sports/badminton/tests/test_court_isolation.py` for deterministic
regressions, the existing badminton/engine/API suite for compatibility, and
`python research/evaluate_court_isolation.py` (after sourcing `../gpu-env.sh`)
for real-video sample metrics and annotated frames in `data/court-evaluation`.
Codec version 6 rejects older perception caches and fingerprints the selected
homography, geometry mode, and fixed-camera policy even for static manual
calibrations. Recalibration cannot silently reuse another court's observations.
Legacy line calibrations are classified during seeding; manual recalibration
and restarts preserve a known fixed-camera lock.
Preserve the previous session directory before the
application's reanalyse operation replaces its generated events and tracks.

## Incident evaluation — 22 October 2026

The complete recording finished successfully. The comparison uses all 22,802
available decoded frames, not the runner's 22,860-frame padded frontier.

| Geometric check | Before | After |
| --- | ---: | ---: |
| Frames accepted as the selected court | 7,640 | 22,797 |
| Player observations outside court plus permitted runoff | 1,196 | 0 |
| Camera identities for this stationary installation | 8 | 1 |
| Shuttle observations outside the full-resolution flight mask | 1,854 | 21 |
| Maximum distance outside that mask | 558 px | 1.4 px |

The 21 remaining edge exceptions are within 1.4 pixels of the full-resolution
mask; inference uses a 512x288 mask, so its discretised edge is slightly
different. They are not evidence of distant neighbouring-court leakage.
These counts are observations over frames, not distinct people or shuttles.
Annotated comparisons at frames 0, 900, 3,600, 7,200, 12,000, 18,000 and 22,000
were inspected. In particular, the aisle passerby at frame 900 is excluded,
while the four target-court detections remain available to the existing engine.

The complete inference run used codec 5 and the final isolation/admission
algorithm. The later codec-6 changes affect cache identity and calibration
lifecycle, not that inference algorithm. They were separately validated with
restart, manual recalibration, static-court changes and missing-calibration
regressions. All 204 badminton/engine/API tests passed (two existing Starlette
deprecation warnings); the changed files passed Ruff and `git diff --check`.

Evidence is in `data/court-evaluation/comparison.json`, `comparison-*.jpg`,
and `final-all-tests.log`. Original session results and a database backup are
retained in `data/court-evaluation/before-fixing-one/`.

End-to-end throughput on the existing GPU configuration was approximately
10–15 normalised frames/second. This validates offline recorded-video handling,
not 30 fps real-time service capacity. Live ingest and throughput tuning remain
separate work, alongside labelled shuttle and event-accuracy validation.
