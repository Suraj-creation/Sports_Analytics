# Independent review: Test 1 V5 reset at frame 14114

The new reset at **14114 (470.466667 s)** is supported by the actual source sequence. All nine frames 14110–14118 were inspected as source, original-baseline overlay and current overlay: 27 panels on three aspect-preserving sheets. The current producer is the completed fresh `5ae614826e6f909defb02445386962ac13b4641a` run. Baseline is the original Test 1 `improved_v1` full neural run; it is not the later cached semantic control.

At 14110–14113 both athletes are outside the right sideline. At 14114 both abruptly occupy central near/far court positions, while the court/background persists and the upper broadcast score graphic finishes disappearing. This displacement cannot represent continuous athlete motion over one 1/30-second interval. The footage contains a same-camera temporal edit. The disappearance of a graphic alone is not being used as edit proof; the discontinuous athlete positions provide the foreground evidence. The preceding graphic animation at 14112–14113 does not itself relocate the athletes.

| Frames | Original baseline | Current actual V5 |
|---|---|---|
| 14110–14113 | Epoch9; two right-side athlete boxes | Epoch9; two right-side athlete boxes and two scene-only foreground episodes |
| 14114 | Epoch9; no admitted people | Epoch10; two fresh, detector-matched athlete boxes at current central positions |
| 14115 | Epoch9; no admitted people | Epoch10; two carried boxes, **not fresh detector matches** |
| 14116–14118 | Two central athlete boxes recovered | Two central athlete boxes maintained |

See [before](sheet_01.jpg), [exact transition](sheet_02.jpg) and [continuation](sheet_03.jpg). These observations support this particular new reset and its immediate acquisition behavior. They do not establish physical scene precision/recall across all frames, named identity, contact timing, stroke accuracy, winners or scoring.

The raw V5 scene hypothesis at 14114 correctly remains **false**. Correspondence adaptive ratios are 22.1767 and 5.9119, but their mean intensity discontinuity is 14.0443, below the existing strong intensity floor15. Appearance does not jointly qualify either. Both independently measured regions nevertheless supply relative/acquisition witnesses. The V4 detector-layout decision records `relative_change_and_complete_court_replacement`: confirmed singles expects two participants, exactly two raw boxes lie in the strict current court, and both are unmatched to the two preceding foreground episodes under the unchanged IoU0.3 policy. It records a positive weak barrier without pretending the raw strong hypothesis is true.

The exact current detector-frame image SHA256 and shape equal the source-bound current proxy's decoded pixel receipt at 14114. The package's **142 artifact hashes**, **612 recorded input bindings**, and **27 source/proxy image pixel and shape receipts** all verify. Rational PTS agrees for both arms and source. Original and snapshot cache hashes, model declarations and source SHA256 are retained in [source verification](source_verification.json). No original video was decoded again and no neural model ran during this review.

The independent whole-run structural audit uses the **actual recorded native producer ROOT**, its unchanged normal completion loader, the actual native `BadmintonSession.decode_perception`, and `source-native-scene-epoch-audit:v4`. No ROOT/global reassignment or compatibility downgrade was used. The completed worker/parent/cache catalogue gates pass, as do the frozen producer source hashes. All **288 codec24 packets and 17,268 canonical frames** decode and audit. The audit validates V5 exclusive feature-origin regions against the actual prior-frame foreground stream, native court/calibration/format decision contracts, adjacent valid view/camera matrices and serialized relative transforms.

All **164 relative camera/layout proof frames** pass, including cross-packet cases1200,11040 and13920. There are 13 raw strong hypotheses and 14 actual epoch increments; the sole additional weak barrier is14114. No overlap-dependent unknown abstention occurs in this run, and no geometry/source invariant is rejected. This is structural consistency of recorded evidence, rather than a pixel-level physical accuracy audit of all17,268frames. See [whole native structural review](whole_native_structural_review.json) and [executed verifier](verify_and_prepare.py).

No production source, model, annotation, historical report or original run output was modified. Candidate tracked bytes remain clean at5ae6148; bytecode writing was disabled. Full numerical/population acceptance is independently owned by the annotation reviewer and orchestrator. This source/structural gate supplies no broader pipeline acceptance claim.
