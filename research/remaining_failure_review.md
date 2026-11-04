# Remaining Test 1 failures: original-frame visual review

Read-only diagnostic review by Auditor B, 2026-11-05. The original video,
annotations, frozen baseline, production source and running candidate were not
changed. New images and measurement JSON are under
`artifacts/benchmarking/investigation/remaining_visual_review/`.

All source images were decoded by PyAV at exact source presentation timestamps
`frame_index*512` in time base1/15360, with an assertion that the returned frame
PTS equals the requested PTS. No source trimming, transcoding, clock correction
or frame-offset fitting was performed. Model circles are cached proxy observations
mapped to the original at spatial factor1.5; they are not newly annotated shuttle
or contact ground truth. The supplementary upper-image crops contain **original
pixels without model overlays**, with their headings outside the image content.

## 1. GT22/GT23: a real break and a missed same-camera source edit

The supplied intervals are GT22 `10607–10708` and GT23 `10733–11078`. The
25-frame difference between end and next start is0.8333s on the unchanged source
timeline. The baseline interval `10601–10737` spills4frames into GT23, then
separate fragments occur later. Those facts do not establish that the sporting
exchange was continuous across the short annotated gap.

Original frames10690,10700,10708,10716,10724,10732,10733,10745,10760,10778 were
reviewed in `gt22_23_break.jpg`. They show the near player finishing an action,
recovering/walking, and the players repositioning during the later quiet period.
At source10733, the near player is still walking/repositioning with a lowered
racket rather than visibly executing a new launch/contact. A still cannot
establish an exact first-contact label, but the footage does not support simply
joining these intervals because their annotated gap is short.

### Directly visible source edit at10769→10770

A short contiguous decode of10680–10790 was compared frame to frame. The
largest whole-image grayscale change (at960×540) is at **10769→10770**:

| Pair | Whole-image gray MAE | Pixels changing by>30 intensity levels |
| --- | --- | --- |
|10769→10770|2.75376|7343|
|10761→10762, next-largest change in the inspected region|0.52691|2792|

The image pair in `gt22_23_possible_edit_pairs.jpg` shows players jumping from
floor/pickup and resting positions into exchange-ready/active positions between
two consecutive encoded frames, while the camera and court background remain
nearly the same. This is strong direct visual evidence of a **same-camera hard
edit in the supplied source**, not a source/proxy offset or decoder omission.
The source presentation timestamps remain consecutive and valid; their content
can nevertheless contain a broadcast/editorial time jump.

The cached perception `shot_id` remains25 throughout. Running the existing
`CutDetector` on the **actual proxy frames10769 and10770** produces:

```text
HSV-histogram correlation: 0.9959220991
Production cut threshold: 0.55
Cut detected: False
```

This result is saved in `same_camera_edit_cut_probe.json`. The detector in
`sports/badminton/src/bai_badminton/perception/scene.py`, `CutDetector._hist` and
`CutDetector.update`, compares coarse global HSV histograms. A fixed-camera
edit can preserve that histogram even when players' temporal continuity breaks.
This particular miss is established by the source pair, cache ID and direct
controlled invocation; one case does not justify raising a global correlation
threshold or introducing an unvalidated pixel-difference cut rule.

### Annotation and boundary implications

GT23's supplied start10733 is **37frames before** the observed edit10770. Its
early annotated span includes the preceding walking/preparation content. This
creates a **boundary-definition / source-edit ambiguity** requiring human
annotation-convention review: does a rally interval include preparatory footage
before an edit, or begin at the first visible exchange evidence after it? No
replacement label is proposed, and the existing benchmark must continue using
10733 exactly. The original annotation may intentionally follow a broader
interval convention; these images alone do not establish that it is erroneous.

Potential causes therefore remain distinct:

1. The histogram detector demonstrably misses a fixed-camera edit.
2. The supplied annotation starts before that edit and before clearly visible
   exchange in the inspected frames; exact intended start semantics are unknown.
3. Static/shuttle-on-floor observations can persist during a genuine between-play
   period. They do not prove rally continuation, and they are different from an
   airborne shuttle temporarily leaving the visible frame.

The baseline's several later GT23 fragments still require continuity investigation;
the annotation ambiguity does not excuse or remove them from evaluation.

## 2. GT31's early boundary includes an excluded close-up

The annotation starts at14404. Original frames14395,14404,14412,14420,14425,
14430,14440,14455,14475,14491 are in `gt31_early.jpg`.

| Source frame | Visible image content / recorded model context |
| --- | --- |
|14395|Wide court view; players between visible actions.|
|14404,14412,14420|Close-up of a player approaching/collecting a shuttle clearly visible on the floor, with a lowered racket. Cached view=`none`, shot34, replay flag=True.|
|14425|Back to wide court view, shot35; far player in overhead exchange posture. Raw shuttle observation exists near proxy(613.7,223.0).|
|14430–14440|Raw observations continue during the visible exchange, with the far player active.|
|14455,14475|Near player prepares for an overhead action; cached shuttle is missing.|
|14491|Shuttle observation reacquires near proxy(555.1,64.9), then a lasting predicted segment begins.|

The baseline's **replay flag here must not be described as verified replay**.
The perception source documentation uses that flag for excluded/non-court views
as well as replay suppression. The visible frames establish close-up/coverage
loss; they do not establish a replay of an earlier sporting exchange.

The exact baseline semantic trace records a provisional start14430 at processing
frame14432, cancellation of that short segment at14467, and a new provisional
start14491 at processing frame14493. Thus the final late start is a combination
of camera/view exclusion and loss/cancellation/reacquisition after returning to
the wide view. It is not simply failure to inspect source frame14404 or an
87-frame clock offset.

The manually supplied start14404 falls in pickup/close-up content, not a visible
first launch in this review. As with GT23, this is an annotation-semantic and
observability limitation, **not permission to change or discard the annotation**.
A detector based on reliable target-court observations cannot infer a precise
earlier sporting onset inside excluded footage without additional observed
evidence. Physically backdating predictions to match this label would fabricate
timing. Improving the later missing-observation chain can still recover the
first supported post-cut onset without inventing what happened in the close-up.

## 3. GT31's14647–14694 missing run mixes physical exit and model misses

`gt31_gap.jpg` reviews original frames14640,14646,14652,14660,14668,14676,
14684,14690,14695,14701. It shows a continuous wide view and players continuing
an overhead exchange. The far player plays upward from the right court region;
the near player moves back and prepares overhead. There is no visible between-point
reset or camera cut in this short inspected span.

The recorded model detects frame14646 near proxy `(879.22,87.84)` with confidence
0.756, then misses14647–14694, returning at14695 near `(936.07,240.61)` with
confidence0.687. A conservative rule requiring both boundary detections close
to the top band can therefore fail even when the *underlying flight* visits
the top boundary: the last/first model observations need not coincide with the
last/first physically visible shuttle image.

To avoid hiding this crucial region behind image headings, the supplementary
`gt31_gap_upper_original_pixels.jpg` crops original x900..1699,y0..539 at frames
14646,14648,14650,14684,14688,14690,14694,14695. The heading is outside the
original pixels and there are no model circles. Diagnostic visual observations:

- A bright moving shuttle-like streak is visible at14648 while the model reports
  no shuttle. At14650 it reaches the extreme upper image area. This supports
  **loss before physical exit**, rather than treating14646 as the exact exit.
- A similar bright descending streak is clearly visible again at14684, and
  lower by14688/14690, while the model remains missing until14695. This supports
  **missed early re-entry observations**, rather than treating14695 as the exact
  first visible return.
- The intervening high-flight portion can be outside the image; the sampled
  images do not establish the exact physical exit/re-entry frames or classify
  every missing frame. The entire48-frame model gap must not be equated with
  either continuous physical absence or continuous visible detection failure.

These are diagnostic source-image facts, not newly accepted shuttle pixel labels
or manually verified contacts. In particular, this review does **not** produce a
new trajectory, image coordinate ground truth, or substitute predicted boundaries.

### What this establishes for the conservative continuation cue

The strict top-band test can have false negatives when a detector drops an
ascending shuttle before it reaches the band and reacquires a descending shuttle
after it has left that band. The recorded y87.84/y240.61 endpoints are model
sampling endpoints, not a physical description of the entire flight. This
explains why conservative edge conditions may retain this failure even while
protecting legitimate between-rally breaks elsewhere.

The evidence motivates a separately controlled experiment using validated
trajectory direction/uncertainty or improved temporal shuttle detection near
entry/exit. It does **not** justify expanding the band to include y240.61 because
that happens to recover this Test1 case, or merging every48-frame gap. The same
mechanism must be tested against real breaks such as the GT22/23 source edit.

## 4. GT27 reference: a static painted-T attractor remains a different failure

The earlier independently reviewed image
`artifacts/benchmarking/investigation/audit_b/gt27_stationary_point.jpg` shows
repeated low-confidence model points near proxy(645,393), on the painted
center-service T, while a player performs overhead action. This is compatible
with a static-court-line attractor, not proof that play or players are stationary.
It differs from the GT31 mixed visibility gap: one needs stationary-observation
validity checks; the other needs visibility/trajectory uncertainty handling.
Neither can be solved safely by interpreting every player movement as continued
play or every missing/static shuttle sample as a verified ending.

## Evidence files and limits

- `frame_evidence.json`:exact requested original PTS plus frozen cached observations
  for30 reviewed snapshots.
- `gt22_23_break.jpg`, `gt31_early.jpg`, `gt31_gap.jpg`:wide-view diagnostic montages.
  Their title bands cover a small upper-image region; use the supplementary
  unoverlaid upper crop for physical top-of-frame visibility claims.
- `gt31_gap_upper_original_pixels.jpg`:8 additional exact-PTS original crops,
  preserving all top pixels in the stated ROI.
- `gt22_23_frame_differences.json`:contiguous source-frame differences10680–10790.
- `gt22_23_possible_edit_pairs.jpg`:consecutive original source frames around the
  largest change and a lower-change control pair, with headings outside the image.
- `same_camera_edit_cut_probe.json`:actual existing CutDetector invocation on the
  two corresponding proxy frames.

No new model inference, GPU workload, production edit, source transcode, annotation
change or benchmark recomputation was performed for this review. These findings
must remain diagnostic until incorporated into controlled component tests and
the unchanged full-video evaluation. Test1 remains development footage; no
generalization or annotation-error rate is inferred from these examples.
