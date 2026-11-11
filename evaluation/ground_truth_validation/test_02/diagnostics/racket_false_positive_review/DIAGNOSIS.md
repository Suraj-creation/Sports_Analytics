# Racket candidate false positives: source-bound diagnosis

The current classical detector selects a person's head and advertising contours
as racket observations on Test2. The same head alias recurs in preserved Test1
outputs. This is a verified component evidence weakness; the inspected examples
do not provide a physical precision/recall denominator or establish that each
downstream contact/rally was wrong.

No production source, model, threshold, baseline, original video or annotation
was changed by this investigation. All probes run the CPU image detector with
frozen existing poses. They are neither neural inference nor a new full pipeline
evaluation.

## Exact reproduction and visual evidence

The actual canonical proxy pixels matter. Running the unmodified
`RacketDetector.detect` on proxy frames300 and1594 plus their frozen person/pose
observations reproduces **all four complete cached racket dictionaries exactly**
(center, axes, angle, support, wrist and method). See
[receipt](exact_reproduction_receipt.json) and
[complete probe](probe_v2/probe_results.json).

Original-source resized PNGs produce slightly different contour fits, and the
near candidate at1594 disappears. Those source-panel probes are preserved
separately; they must not be described as exact production-input reproduction.

| Test/frame/time | Track | Selected geometry | Evidence |
|---|---:|---|---|
| Test2/300/10.000s | 0 | Center581.521,418.342; support0.908796; wrist10 | The green contour surrounds the near athlete's visible head. All five confident facial keypoints lie inside the ellipse. |
| Test2/300/10.000s | 1 | Center678.948,230.320; support0.824646; wrist10 | The contour follows part of the advertising logo beside the far athlete's head. |
| Test2/1594/53.133s | 4 | Center577.522,507.639; support0.853130; wrist9 | Torso/wrist-region candidate; the still does not certify a physical racket head. |
| Test2/1594/53.133s | 5 | Center437.342,226.741; support0.949343; wrist10 | Advertising-letter contour; high geometric support does not establish equipment. |
| Test1/300/10.000s | 0 | Center656.31,389.53; wrist9 | A visible head contour; five confident facial landmarks enclosed. |
| Test1/9000/300.000s | 0 | Center589.53,422.77; wrist10 | A visible head contour; four confident facial landmarks enclosed. |

Evidence crops show raw pixels on the left and accepted contour/sample support
on the right. They are diagnostic overlays, not human-adjudicated labels:

- [Test2 head](probe_v2/test2_frame00300_analysis_proxy_track0_wrist10.png)
- [Test2 advertising logo](probe_v2/test2_frame00300_analysis_proxy_track1_wrist10.png)
- [Test2 advertising letters](probe_v2/test2_frame01594_analysis_proxy_track5_wrist10.png)
- [Test1 head at300](contract_study_v3/test1_frame00300_track0_wrist9.png)
- [Test1 head at9000](contract_study_v3/test1_frame09000_track0_wrist10.png)

## Why the current gates admit them

Source: `sports/badminton/src/bai_badminton/perception/racket.py`, method
`opencv_ellipse_shaft_v1`.

1. Fresh person detection and same-frame pose are present. This is not a stale
   source-frame or missing-detector explanation for these examples.
2. A wrist-centered search extends0.75 body heights. Heads, clothing, advertising
   and real rackets all fall inside plausible search windows.
3. Accepted diameters span0.07–0.5 body heights with aspect ratio≥0.35. These
   geometric ranges also admit heads and lettering.
4. Median radial fit error≤0.16 and angular coverage≥0.75 measure ellipse-like
   contours, not racket semantics. The selected near head has fit error0.03837,
   coverage1.0, center-to-nose distance1.3895px and wrist distance77.2378px.
5. The shaft test samples24 positions over the interior15–90% of the rim-to-wrist
   gap. It accepts≥65% occupancy after5×5 edge dilation. It does not require a
   connected or consistently oriented shaft reaching both rim and hand.
6. Proposals rank by geometric support, without distinguishing equipment from
   anatomy/background. A better-fitting head can displace a real racket.

| Selected candidate | Dilated shaft occupancy | Exact sampled-edge occupancy |
|---|---:|---:|
| Test2/300/track0 head | 0.8750 | 0.1250 |
| Test2/300/track1 logo | 1.0000 | 0.2917 |
| Test2/1594/track4 torso/wrist | 1.0000 | 0.2083 |
| Test2/1594/track5 lettering | 1.0000 | 0.2917 |

Exact edge occupancy alone is not a replacement gate: a real thin shaft's edges
can sit beside its centerline. The contrast demonstrates that the existing
dilated occupancy does not certify a connected shaft.

The support formula is `0.5 + 0.25*(1-fit_error/0.16) + 0.25*shaft`.
It is an uncalibrated geometric score, not an equipment correctness probability.

## Downstream risk and limits

`events/contact.py::_player_point` substitutes a racket center for the posed
wrists whenever a racket object exists. The contact scorer also uses
`RacketObservation.overlap` and describes equipment overlap as more specific
than another athlete's wrist/body proximity.

`events/contact_evidence.py` can treat fresh racket overlap≥0.5 as an impact cue.
It still applies trajectory, association, current-person and temporal gates;
these examples do not prove a false accepted impact or official point. They
show that a geometric alias can move the proximity anchor or supply misleading
equipment support. The frame-by-frame effect must be measured against the
preserved complete baseline before any pipeline improvement is claimed.

## Diagnostic contract experiments

[Study](contract_study_v3/contract_study.json) contains both Test2 frames,
Test1 frames243/300/9000, and19 synthetic controls. Exact source/helper/cache
hashes are recorded. The controls exercise rotation, scale, blur, partial shaft
occlusion, clean overhead positioning, face overlap, another person's face, and
unconnected transverse clutter. They are engineering controls, not sporting GT.

**Anatomical alias:** an ellipse enclosing at least three confident facial
landmarks identifies positive evidence that the candidate may depict a head.
The prototype checks all fresh detected people's faces, including another
participant in doubles. It does not exclude a player box or a fixed head area.
Clean overhead/near-head rackets outside the facial landmarks remain available.
If a real racket overlaps the face, the correct interpretation is ambiguous
equipment/anatomy, not a claim that the object is definitely a head.

This catches the recurring selected head aliases, but does **not** solve the
detector. Test2/300 has seven accepted candidates: removing the best head still
leaves jersey/body contours. The far logo and lettering remain separate errors.

**Straight shaft evidence:** exploratory Hough-line diagnostics measure straight
edge support in a rim-to-wrist corridor across several angle/corridor widths.
The original fixed2.5px corridor finds no straight support for the four selected
Test2 candidates, while clean scale1 controls retain strong support. It also
rejects unconnected transverse clutter admitted by the current dilation test.
However, that fixed corridor loses scale2 shaft edges; body-relative widths
recover them but can also admit clutter. Short shaft occlusion lowers support.
No threshold in this sensitivity study is validated for production adoption.

The head/arm and real-racket-over-face synthetic examples intentionally contain
the same pixels and posed face. A purely geometric single-frame method cannot
know which physical interpretation is true. Anatomy abstention and straight-line
support are complementary diagnostics, not complete object recognition.

## Proposed acceptance contract and priorities

1. **Preserve candidate provenance and ambiguity.** Generic contour/shaft fits
   remain racket candidates with geometric support. Anatomical-alias or
   unresolved object evidence must not silently become verified equipment or a
   uniquely specific impact cue. Preserve unknown and rejection reasons.
2. **Add a narrow, auditable anatomical-alias abstention** if root authorizes it:
   require multiple confident facial landmarks inside the fitted ellipse,
   respect current pose/person source stamps, and check all target participants.
   Retain the candidate for review rather than declaring a physical negative.
3. **Strengthen independent shaft/object evidence before promotion.** Study
   connected, directional image support with scale/blur/occlusion controls and
   temporal ownership. A straight contour alone can still depict an arm or
   banner. Do not choose a cutoff from these isolated examples.
4. **Evaluate a trained racket detector/temporal association alternative** using
   independently reviewed equipment boxes/centers and ownership/contact labels.
   See the separate alternative-model review; no missing model is claimed loaded.
5. **Measure pipeline effects:** preserve this full baseline; add negative/positive
   contract regressions; rerun affected Test2 and retained Test1 before comparing
   contacts, abstention, segmentation, identity and outcome coverage. A decrease
   in racket observations is not automatically an accuracy improvement.

Risks: facial pose errors may falsely create ambiguity; true racket/face overlap
will lose an equipment cue; small/blurred/edge-on shafts may not support a line;
remaining body/logo candidates can survive. Abstention can reduce false evidence
while increasing unknown coverage. Report both explicitly.

## Validation and provenance

`test_candidate_contract_probes.py`: **12 passed**, covering clean/rotated racket
positives, near-head preservation, explicit face overlap, low-confidence face
landmarks, another participant's face, current-person evidence, transverse hard
negative clutter and straight/blurred shaft positives.

The initial studyv1 hit an OpenCV line-array shape mismatch and was retained;
studyv2 normalized Hough output; studyv3 added scale sensitivity and Test1
controls. Probev1's selected marker initially also marked a duplicate same-center
other-wrist proposal; probev2 requires exact wrist plus center. These were
diagnostic-tool corrections only. Earlier probe outputs remain preserved.

Production `racket.py`, `events/contact.py`, annotations and completed Test1
records remain unchanged by this investigation. This report proposes work;
it does not report a shipped pipeline fix or a physical metric gain.
