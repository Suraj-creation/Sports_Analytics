# Practical semantic effects of the anatomical-alias admission fix

This review independently compares original live events with the changed-engine
replays on **unchanged recorded perception**. These are semantic regressions,
not fresh neural inference or independent physical accuracy evaluation. Original
events, raw observations, videos, annotations and previous reports are unchanged.

Test1 and Test2 fixed-perception reviews are complete below. Test2 uses the
recovered guarded completion receipt after safe report-only recovery; the child
replay was not rerun. Its missing schedule-feedback witness at frontier119
remains explicit uncertainty. The separate fresh post-fix Test2 neural run is
needed before claiming full-pipeline preservation.

## Test1: headline effects

| Output | Before | Changed-engine replay | Meaning |
|---|---:|---:|---|
| Live contact events | 446 | 445 | Net count alone hides temporal anchor changes. |
| Live stroke events | 446 | 445 | Same changed anchors as contacts. |
| Exact old anchors absent | — | 14 | Thirteen have nearby replacement candidates. |
| New exact anchors | — | 13 | Paired diagnostically as possible shifts, not new physical GT. |
| Nearby temporal shift pairs | — | 13 | Changes range−3 to+6frames; largest absolute shift0.2s. |
| Unpaired removed anchor | — | 15801/526.700s | Its own support is unchanged; neighborhood competition explains disappearance. |
| New anatomical ambiguity events | 0 | 2047 | Raw candidate retained; specific equipment cue withheld. |
| Rally intervals | 36 | 36 | All six saved reference metric sets are identical. |
| Canonical accepted point events | 0 | 0 | No winner/score accuracy improvement established. |
| Live highlight events | 3 | 4 | Heuristic selection changed despite identical rally boundaries. |

The controlling regression also verifies287 nonterminal perception-driver
frontiers unchanged. This supports fixed-perception isolation. It does not make
the changed contact/classification/attribution outputs independently correct.

Independent evidence: [compact event diff](semantic_effect_evidence/test_01/event_diff.json),
[complete changed events](semantic_effect_evidence/test_01/complete_changed_event_evidence.json).
Matching pairs absent old/new contact anchors within15frames/0.5s and the same
containing rally interval, maximizing cardinality then minimizing frame distance.
All observed pairs here are within6frames. This associates nearby estimates;
it does not certify that two estimates describe the same physical impact.

## Test1: changed contact/stroke anchors

| Before frame | After frame | Delta frames | Before predicted stroke | After predicted stroke |
|---:|---:|---:|---|---|
| 2796 | 2798 | +2 | unknown | unknown |
| 3876 | 3877 | +1 | push | unknown |
| 6151 | 6152 | +1 | unknown | lift |
| 6629 | 6630 | +1 | unknown | unknown |
| 7679 | 7680 | +1 | unknown | drive |
| 8883 | 8882 | −1 | unknown | push |
| 10963 | 10964 | +1 | unknown | drop |
| 11865 | 11862 | −3 | unknown | unknown |
| 14316 | 14322 | +6 | unknown | unknown |
| 15031 | 15030 | −1 | unknown | drive |
| 15415 | 15414 | −1 | unknown | drop |
| 16213 | 16214 | +1 | unknown | net_shot |
| 16908 | 16910 | +2 | net_shot | net_shot |

Eight of these thirteen nearby pairs have different predicted stroke labels.
One changes from known to unknown; the others are not automatically improvements
because per-contact stroke truth is absent. The unpaired old15801 stroke was
unknown and has no replacement within the declared pairing window.

## Test1: same-anchor classification and provisional actor changes

At2404/80.133333s, unknown becomes `net_shot`; the provisional hitter changes from
unresolved to visual track1. The contact's physical status changes from
insufficient to ambiguous. The source-bound ambiguity event withholds track1's
head-like equipment candidate at513.967,359.930: it encloses all five facial
landmarks of **the other visible person, track0**. This is a real cross-person
anatomical alias, not just an own-head case. Another surviving contour is still
only a raw estimate. The changed proximity anchor can alter attribution without
establishing the true hitter or stroke.

At8172/272.400s, `drop` becomes `push` and the provisional hitter changes from
track0 to track1. Both visible head ellipses are withheld from specific racket
evidence. The image shows live rally action; no supplied independent per-contact
label resolves the class or hitter. See
[raw versus semantic overlay](semantic_effect_evidence/test_01/frame_08172_raw_vs_semantic.png).

At12874/429.133333s, the predicted label stays `push`, but the provisional hitter
changes from track2 to track1 and the internal physical status changes from
ambiguous to probable. The near head ellipse is withheld while a far/background
candidate remains. This demonstrates that removing one misleading cue can
**increase** a downstream heuristic assessment by changing its selected actor.
It is not a verified physical contact or calibrated correctness probability.

The other same-anchor provisional track switches occur at7414(0→1),7730(2→1),
8222(0→1),14626(0→1). These are visual tracker episodes, not named athletes.
No canonical player/team identity or accepted point was created.

| Predicted stroke class | Before count | After count |
|---|---:|---:|
| unknown | 309 | 301 |
| push | 47 | 48 |
| lift | 27 | 28 |
| drive | 2 | 4 |
| net_shot | 30 | 32 |
| drop | 21 | 22 |
| clear | 8 | 8 |
| smash | 2 | 2 |

Reduced unknown coverage is an observed behavior change, not a class-accuracy
gain. Predicted unknown rate changes309/446=69.28% to301/445=67.64%; these
denominators are emitted predictions, not independently labelled contacts.
Scores, class labels and provisional attribution remain model/rule outputs.

## Test1: exact removed-anchor mechanism

The removed15801/526.700s candidate had no racket observation on that frame.
Its original physical-impact assessment was insufficient because no current
detector-matched player was recorded. Neither fact proves there was no physical
impact. The source image shows live action and a far player's extended racket
near the predicted shuttle region:
[frame15801](semantic_effect_evidence/test_01/frame_15801_raw_vs_semantic.png).

A bounded CPU score/NMS probe uses the exact frozen person/pose observations and
the original processed shuttle trace over15755–15899. It reproduces the original
contact-eligible peaks15801,15809,15843 and the new peaks15809,15843, including
their exact stored confidence values. It performs no neural inference.

| Frame | Original support | Admission-policy support | Explanation |
|---:|---:|---:|---|
| 15801 | 0.4502698471 | 0.4502698471 | Candidate's own score is unchanged. |
| 15806 | 0.2841034673 | 0.4610637889 | Replacing anatomical racket anchors with wrists changes proximity0.3682→0.5941; score crosses unchanged0.35threshold. |
| 15808 | 0.7783656885 | 0.8351438998 | Proximity changes0.3789→0.4866. |
| 15809 | 0.9373433904 | 0.9373433904 | Stronger retained neighboring peak is unchanged. |

The existing local-maximum suppression radius is6frames/0.2s. New15806
suppresses15801, but15808 and15809 in turn suppress15806. Thus15801 disappears
through a neighborhood competition cascade even though the competing15806 is
not ultimately retained. This is the behavior of the existing local-maximum
rule, not evidence that NMS is defective. No NMS rule or threshold was changed.

[Exact bounded score/NMS evidence](semantic_effect_evidence/test_01/temporal_competition_v2.json),
[executed CPU probe](semantic_effect_evidence/test_01/executed_temporal_probe.py),
[probe output](semantic_effect_evidence/test_01/temporal_probe_v2.log).

The practical implication is important: a conservative equipment admission rule
can still remove or shift a potentially real contact through downstream peak
selection. Without independently reviewed impact times, this cannot be called
false-contact removal or a recall improvement. The preserved source and raw
observations allow later adjudication.

## Test1: highlights and unchanged rally metrics

Live highlight events increase3→4. The additional selected interval is
14430–15171, heuristic score4.2, with length3.0 and predicted shot-variety1.2
contributions. This is distinct from the downstream exporter's fixed top-k
highlight list. No highlight relevance labels certify that the added selection
is better.

All six interval-reference metric sets remain unchanged, so Test1 rally timing
regression is preserved under this fixed-perception comparison. That statement
does not imply unchanged contacts, strokes, provisional hitters or highlights.

## Limits and required next evidence

- Anatomical ambiguity is a narrow semantic-admission safeguard. Background and
  torso ellipses remain unresolved; surviving candidates are not certified rackets.
- The source overlays use the exact original neural-analysis proxy and raw
  cached predictions. They show the same pixels before/after; the distinction
  comes from recorded admission events, not regenerated detections.
- Contact timing, hitter identity and class accuracy require reviewed per-impact
  labels; filled shuttle trajectories and two generated player slots cannot
  supply that truth.
- Test2 report recovery is complete, but its one unobserved schedule frontier
  remains unresolved in these recorded observations. A fresh full Test2 pipeline
  run is separate from these semantic replays and supplies current end-to-end
  evidence only after its own completed guards and evaluation.
- No additional pipeline fix, NMS adjustment, threshold tuning or production
  helper change was made by this review.


## Test2: scope, recovered completion and practical counts

The completed regression consumes all **29,296 canonical frames at30fps** on the
exact Test2 source. Recovery preserved the initial failure log and old helper,
validated the already-completed child artifacts, and regenerated reporting only.
[Recovered completion](../regression/test2_semantic_regression_v1/completion.json),
[saved full reference matrices](../regression/test2_semantic_regression_v1/semantic_regression_metrics.json).
It did not repeat replay or neural inference. Of488 requested nonterminal
schedule frontiers,487 are observed and agree; **frontier119 is unknown** because
the retained original trace resets from95 to179 around a format change. There
is no claim that the unobserved scheduling input matches. Fresh Test2 inference
is required for full end-to-end preservation.

| Output | Original Test2 baseline | Changed-engine fixed-perception replay |
|---|---:|---:|
| Live contact events | 819 | 816 |
| Live stroke events | 819 | 816 |
| Exact old anchors absent | — | 22 |
| New exact anchors | — | 19 |
| Nearby candidate shift pairs | — | 16 |
| Unpaired old anchors | — | 6 |
| Unpaired new anchors | — | 3 |
| Anatomical ambiguity events | 0 | 4239 |
| Rally intervals | 75 | 75 |
| Canonical accepted point events | 0 | 0 |
| Broadcast-score observation events | 708 | 708 |
| Live highlight events | 6 | 5 |

[Final Test2 event diff](semantic_effect_evidence/test_02_v2/event_diff.json)
records input/source/cache/proxy hashes, complete changed-event values, admission
references, and sampled-image hashes. [Raw changed-contact and nearby ambiguity
events](semantic_effect_evidence/test_02_v2/complete_changed_event_evidence.json)
retain complete payloads. Unmodified raw observations remain in the original
perception cache. These ambiguity-event counts are policy emissions, not false
positive counts, rejected physical impacts, or independent equipment labels.

The diagnostic matcher pairs absent/new anchors within15frames/0.5s and the same
chronological containing rally ordinal, maximizing cardinality then minimizing
absolute displacement. It first requires equal rally populations and overlap
IoU≥0.5 for every same-ordinal interval. Every observed pair moves just1frame.
The earlier preserved Test2 review required identical boundary tuples; that
prevented four valid *diagnostic* associations when boundaries changed. Final
v2 uses ordinal context; neither association proves physical event identity.
The original v1 evidence remains preserved and is not the final pairing count.

## Test2: all nearby anchor changes

| Before frame | After frame | Delta frames | Before predicted stroke | After predicted stroke |
|---:|---:|---:|---|---|
| 623 | 624 | +1 | unknown | unknown |
| 1279 | 1278 | -1 | unknown | push |
| 3769 | 3770 | +1 | unknown | push |
| 8627 | 8626 | -1 | unknown | unknown |
| 11562 | 11563 | +1 | lift | unknown |
| 12370 | 12371 | +1 | push | unknown |
| 14337 | 14338 | +1 | unknown | lift |
| 16927 | 16928 | +1 | unknown | push |
| 18595 | 18594 | -1 | unknown | unknown |
| 20767 | 20768 | +1 | unknown | drive |
| 22157 | 22158 | +1 | unknown | net_shot |
| 22802 | 22803 | +1 | drive | unknown |
| 25156 | 25155 | -1 | unknown | unknown |
| 25908 | 25907 | -1 | drop | unknown |
| 26727 | 26728 | +1 | unknown | lift |
| 28310 | 28311 | +1 | push | unknown |

These shifts change both sampling time and downstream temporal context. A new
anchor can have fresh player evidence where the old odd frame was propagated;
this can alter physical-status heuristics or provisional attribution without
establishing a new true impact. Twelve of sixteen pairs change predicted class.

## Test2: unpaired anchors and source evidence

| Change | Frame/time seconds | Predicted stroke | Same-frame admission evidence | Physical interpretation |
|---|---:|---|---|---|
| Removed | 3754 /125.133 | drop | Own-face track3; five fresh facial landmarks | Old physical status ambiguous; no verified negative impact label. |
| Removed | 5446 /181.533 | unknown | Own-face track1; five fresh facial landmarks | Shortens predicted rally16; true ending requires annotation comparison. |
| Removed | 14066 /468.867 | unknown | Own-face track5; three fresh facial landmarks | Head cue withheld; far/body contour survives. |
| Removed | 14078 /469.267 | unknown | Own-face track5; three fresh facial landmarks | Head cue withheld; far/banner contour survives. |
| Removed | 19494 /649.800 | push | Large track4 ellipse contains five fresh own-face landmarks | Face/equipment/shuttle-region overlap is ambiguous; do not certify this as false equipment or false contact. |
| Removed | 25629 /854.300 | unknown | No raw racket or ambiguity on this frame; nearby25632 track2 head cue withheld | Context/temporal effect, not direct same-frame rejection; exact local NMS cause not probed here. |
| Added | 8746 /291.533 | unknown | Own-face track6 cue withheld | Contact can appear despite removal of specific equipment evidence; still physical ambiguous. |
| Added | 27625 /920.833 | unknown | No raw racket or same-frame admission | Physical insufficient; no new true-contact claim. |
| Added | 28819 /960.633 | unknown | No raw racket or same-frame admission | Physical insufficient; no new true-contact claim. |

The nine unpaired-anchor overlays were individually inspected. All show normal
match action on the preserved source; the withheld contours at3754,5446,14066
and14078 align with the player's head. The retained far/background contours
show why this narrow safeguard is not a complete racket detector repair.
[3754](semantic_effect_evidence/test_02_v2/frame_03754_raw_vs_semantic.png),
[5446](semantic_effect_evidence/test_02_v2/frame_05446_raw_vs_semantic.png),
[14066](semantic_effect_evidence/test_02_v2/frame_14066_raw_vs_semantic.png),
[14078](semantic_effect_evidence/test_02_v2/frame_14078_raw_vs_semantic.png).

At19494 the withheld ellipse extends well beyond the face toward the predicted
shuttle region. This is an especially important abstention-risk example: visible
face overlap is sufficient for semantic ambiguity under the policy but does not
establish absence of real equipment or impact.
[19494 source overlay](semantic_effect_evidence/test_02_v2/frame_19494_raw_vs_semantic.png).
At25629 the absence of a raw racket contrasts with the nearby recorded25632
own-head ellipse, demonstrating that contact removal need not be a same-frame
veto. [25629](semantic_effect_evidence/test_02_v2/frame_25629_raw_vs_semantic.png),
[25632](semantic_effect_evidence/test_02_v2/frame_25632_raw_vs_semantic.png).

Added-anchor evidence:
[8746](semantic_effect_evidence/test_02_v2/frame_08746_raw_vs_semantic.png),
[27625](semantic_effect_evidence/test_02_v2/frame_27625_raw_vs_semantic.png),
[28819](semantic_effect_evidence/test_02_v2/frame_28819_raw_vs_semantic.png).
Exact candidate geometry, source frames, detector-match state, face joint IDs
and confidence values are preserved beside each overlay as JSON. Removed-event
correctness, added-event correctness, contact recall and racket precision remain
**unavailable**, rather than zero or improved, without physical per-event truth.

## Test2: all same-anchor semantic changes

Across unchanged anchors,87 contact records and102 stroke records have at least
one retained numeric/support/context difference. Of these,7 contacts and9 strokes
have the explicit key semantic changes below; the other differences include
proximity/support values and flight durations affected by shifted neighbors.

| Frame | Predicted class before→after | Provisional visual track before→after | Other changed interpretation |
|---:|---|---|---|
| 4474 | lift→unknown | 1→unresolved | class status estimated→unknown; attribution provisional→unresolved |
| 5344 | push→push | 1→0 | Provisional selection/context changed; no independently verified identity. |
| 5432 | push→unknown | 0→0 | class status estimated→unknown |
| 8734 | unknown→push | 6→6 | class status unknown→estimated |
| 10404 | push→net_shot | 1→0 | Provisional selection/context changed; no independently verified identity. |
| 12456 | drop→unknown | 1→unresolved | physical ambiguous→insufficient; class status estimated→unknown; attribution provisional→unresolved |
| 22656 | unknown→unknown | 0→1 | Provisional selection/context changed; no independently verified identity. |
| 27618 | drop→push | 0→1 | Provisional selection/context changed; no independently verified identity. |
| 28828 | push→net_shot | 0→1 | physical ambiguous→probable |

At4474 and12456, attribution becomes unresolved and the class becomes unknown;
these are explicit evidence abstentions. At28828, the internal physical status
increases ambiguous→probable because the selected visual track/swing support
changes. The policy therefore does not merely lower confidence everywhere.
All nine same-anchor key-semantic cases were inspected on source overlays.
The first five are preserved in the original evidence directory:
[4474](semantic_effect_evidence/test_02/frame_04474_raw_vs_semantic.png),
[5344](semantic_effect_evidence/test_02/frame_05344_raw_vs_semantic.png),
[5432](semantic_effect_evidence/test_02/frame_05432_raw_vs_semantic.png),
[8734](semantic_effect_evidence/test_02/frame_08734_raw_vs_semantic.png),
[10404](semantic_effect_evidence/test_02/frame_10404_raw_vs_semantic.png).
Supplemental source-bound overlays cover
[12456](semantic_effect_evidence/test_02_supplement/frame_12456_raw_vs_semantic.png),
[22656](semantic_effect_evidence/test_02_supplement/frame_22656_raw_vs_semantic.png),
[27618](semantic_effect_evidence/test_02_supplement/frame_27618_raw_vs_semantic.png),
[28828](semantic_effect_evidence/test_02_supplement/frame_28828_raw_vs_semantic.png),
with a separate [guarded rendering receipt](semantic_effect_evidence/test_02_supplement/receipt.json).
At28828 the surviving far-player ellipse lies on the torso region rather than
clearly isolating visible equipment. The higher physical heuristic is therefore
particularly unsuitable as an accuracy claim. At5432 there is no same-frame
head withholding, but the changed class context remains observable downstream.

An engine event status `confirmed` or physical heuristic `probable` is not a
human-confirmed impact, named athlete, or calibrated probability of correctness.

| Predicted stroke class | Before | After |
|---|---:|---:|
| unknown | 587 | 586 |
| push | 105 | 104 |
| clear | 16 | 16 |
| drop | 51 | 47 |
| lift | 22 | 22 |
| net_shot | 26 | 29 |
| smash | 1 | 1 |
| drive | 11 | 11 |

Predicted unknown rate **increases** from587/819=71.67% to586/816=71.81%,
despite one fewer unknown emission. Classification counts and coverage are not
class accuracy. No supplied independent per-impact stroke labels certify these
changes. The shifted-pair and same-anchor tables must not be added to count
physical changes: they describe emitted estimates with different contexts.

## Test2: every changed rally boundary and all three interval references

| Rally ordinal | Original start–end frames | Replay start–end frames | Start delta frames | End delta frames |
|---:|---|---|---:|---:|
| 16 | 5224–5446 | 5224–5432 | +0 | -14 |
| 25 | 8627–8734 | 8626–8751 | -1 | +17 |
| 42 | 13856–14079 | 13856–14045 | +0 | -34 |
| 55 | 18595–18947 | 18594–18947 | -1 | +0 |
| 66 | 24711–25156 | 24711–25155 | +0 | -1 |
| 68 | 25629–26018 | 25650–26018 | +21 | +0 |

All other69 predicted intervals have identical boundaries. Largest end change
is−34frames/−1.133s; largest start change is+21frames/+0.700s. These are engine
prediction changes, not independently adjudicated timing errors. Full immutable
before/replay reference matrices contain matching, row-level TP/FP/FN, tolerance
counts and complete error distributions; the following selective comparison
uses their saved numbers without recomputing baseline against current code.

| Reference | TP/FP/FN before=after | Precision/recall/F1 before=after | Mean IoU before→after | Start MAE s before→after | End MAE s before→after | Duration MAE s before→after |
|---|---|---|---|---|---|---|
| Test2_Full.csv | 69/6/6 | 0.920000/0.920000/0.920000 | 0.833215→0.830665 | 0.810145→0.820290 | 0.574879→0.584541 | 1.096135→1.126570 |
| Test2_Full_rally.csv | 68/7/5 | 0.906667/0.931507/0.918919 | 0.848135→0.849311 | 0.796078→0.805392 | 0.705392→0.695588 | 1.302451→1.300980 |
| win_predictions.csv | 68/7/5 | 0.906667/0.931507/0.918919 | 0.848135→0.849311 | 0.796078→0.805392 | 0.705392→0.695588 | 1.302451→1.300980 |

Thus coarse Full.csv mean IoU **decreases0.833215→0.830665**, while generated
Full_rally.csv mean IoU **increases0.848135→0.849311**. Detection F1 is unchanged
for all three references. Generated-reference start MAE worsens while end MAE
improves; coarse-reference start/end/duration MAE all worsen. This mixed result
must not be presented as uniform rally improvement. `win_predictions.csv` has
the same interval population as generated rally timing here; interval agreement
does not establish winner accuracy or scoring accuracy.

The live highlight interval3430–3823 (heuristic score4.2) disappears; the other
five remain. This is a heuristic event-selection change and is distinct from
exported top-k lists. No highlight quality labels make its removal an improvement.
Both runs emit zero canonical accepted points;708 broadcast-score observations
are unchanged and do not become verified reconstructed scoring by executing.

## Review provenance and interpretation

- Test1 source SHA256: `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`.
- Test2 source SHA256: `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`.
- Applied code, before/after source hashes and regressions are recorded in
  [applied fix receipt](applied_fix_receipt.json). This review changes none of it.
- Completed semantic input/event/cache/proxy hashes and exact executed diagnostic
  helper are preserved in each evidence directory. Test2 final pairing uses
  `test_02_v2`; earlier `test_02` artifacts are retained for provenance.
- Review confirms a narrow correction in the evidence contract: equipment that
  overlaps reliable facial evidence is retained raw and explicitly withheld from
  semantic equipment use. It does not validate every abstention or detect the
  true racket. Real overhead rackets can overlap faces, and background contours
  remain unresolved.
- Both videos exhibit practical downstream effects beyond racket counts:
  temporal peak changes, provisional hitter selection, class abstention or new
  labels, and highlights. Test2 also changes six rally boundaries. The exact
  Test1 score/NMS probe explains one cascade; other changed contacts are not
  claimed to share that exact mechanism without a separate local probe.
- No contact/racket/stroke/identity accuracy gain is claimed. All original
  videos, annotations, prediction baselines and raw caches remain unmodified.
  No new pipeline fix, threshold tuning or production/helper edit was made by
  this review. The separate fresh Test2 run must pass its own completion and
  metric guards before it can support a fresh before/after conclusion.
