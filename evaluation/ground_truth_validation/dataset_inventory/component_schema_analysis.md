# Part2 component annotation semantics and measurement readiness

Read-only complete CSV/JSON scan of all eight available test folders. Original inputs were not changed. Tests5/8 have no local annotation folder. This report distinguishes direct file contents, plausible legacy producer contracts, and unresolved physical review provenance.

## Main findings

1. `player_detections.csv` stores two point slots and confidence, not boxes, poses, or persistent person identities. The inspected legacy writer explicitly exports YOLO detector bottom-center coordinates, enumerating filtered detections in current detector order; it does not sort into stable identities. Treat this as a producer-contract hypothesis for these exported files until source-frame overlays certify the executed lineage. A downstream legacy consumer inconsistently calls the points centers and adds50pixels for a synthetic bottom: this is a concrete coordinate-contract hazard, not measured current-pipeline failure.
2. Shuttle `Visibility=1` is not certified physical visibility: these are final filtered/filled model trajectories. The legacy gap filler sets interpolated points visible; confidence may remain below the raw acceptance threshold. There is no per-row filled/observed marker in the supplied CSVs. Do not use invisible rows as reviewed negatives or filled coordinates as measured physical truth.
3. Six court JSONs (Tests1,2,3,4,9,10) explicitly declare `source: manual`; Test6 and Test7 have no `source` field and their origin remains unspecified. All eight declare one frame number and1280×720 image size. The six explicit assertions are positive manual-origin evidence, stronger than filename inference, but are not source-hash bindings, all-frame calibration or independent reviewer receipts. Missing source values are never imputed.
4. Every `win_predictions.csv` binds exactly to its corresponding generated rally table by start/end frames. Its `reason_src`, `fault_src`, CNN class/probability and generated cumulative scores demonstrate a model output, not independent sporting truth. It can support reproducible legacy/current disagreement analysis.
5. `Test1_Full2.csv` has20 complete semantic/timing rows plus a literal single-cell `...` placeholder at data row21 (all later fields missing). This incomplete file is a semantic/timing candidate, not additional point/box/keypoint labels. Exact joins and semantic-row checks are recorded below. Its limited/mixed alignment must be resolved before winner accuracy.
6. Primary coarse CSVs mix minute:second strings and raw seconds (Test7); labels/taxonomies and PlayerA/B scores need source-bound adjudication. Preserve both coarse and generated frame-precise interval families, never substitute a higher-scoring reference silently.

## Full-file inventories and measured coverage

| File | Family | Rows | Frame span | Content notes |
|---|---|---|---|---|
| Part2/dataset/Test10_Full/Test10_Full.csv | coarse rally outcome/score label candidate | 101 | [None, None] | {} |
| Part2/dataset/Test10_Full/Test10_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 37133 | [0, 37132] | {"visibility_counts":{"0":7639,"1":29494},"visible_low_confidence_count":856,"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":0} |
| Part2/dataset/Test10_Full/Test10_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":300,"frame_size":{"width":1280,"height":720},"corners":{"TL":[474,264],"TR":[803,263],"BR":[936,657],"BL":[344,659]},"net":{"net_Y":402.0,"net_top_Y":285.0,"left_bottom":[392,403],"right_bottom":[889,401],"cable_left":[388,285],"cable_right":[894,285]},"source":"manual"}} |
| Part2/dataset/Test10_Full/Test10_Full_rally.csv | generated interval reference/proposal | 93 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test10_Full/player_detections.csv | two-slot player point prediction | 37133 | [0, 37132] | {"both_slots_present_rows":35209,"slot1_lower_than_slot2_rows":30817,"slot2_lower_than_slot1_rows":4392} |
| Part2/dataset/Test10_Full/win_predictions.csv | generated winner/reason/score predictions | 93 | [None, None] | {} |
| Part2/dataset/Test1_Full/Test1_Full.csv | coarse rally outcome/score label candidate | 36 | [None, None] | {} |
| Part2/dataset/Test1_Full/Test1_Full2.csv | mixed label/timing candidate | 21 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test1_Full/Test1_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 17268 | [0, 17267] | {"visibility_counts":{"0":3254,"1":14014},"visible_low_confidence_count":759,"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":0} |
| Part2/dataset/Test1_Full/Test1_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":8634,"frame_size":{"width":1280,"height":720},"corners":{"TL":[448.2036268535751,303.93440816070006],"TR":[825.6641539592964,300.2458838012018],"BR":[930.1727689559945,653.1147141932057],"BL":[344.9245249744852,655.5737304328712]},"net":{"net_top_Y":306.3934244003656,"net_Y":429.958990393559,"left_bottom":[367.05576109143306,429.3442363836422],"right_bottom":[904.3529934862221,430.573744503475],"cable_left":[359.67868238578376,306.3934244003656],"cable_right":[906.8120197214384,306.3934244003656]},"source":"manual"}} |
| Part2/dataset/Test1_Full/Test1_Full_rally.csv | generated interval reference/proposal | 36 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test1_Full/Test1_Full_rev_T.csv | generated interval reference/proposal | 35 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test1_Full/Test1_Full_rev_T4.csv | generated interval reference/proposal | 38 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test1_Full/player_detections.csv | two-slot player point prediction | 17268 | [0, 17267] | {"both_slots_present_rows":16732,"slot1_lower_than_slot2_rows":14829,"slot2_lower_than_slot1_rows":1903} |
| Part2/dataset/Test1_Full/win_predictions.csv | generated winner/reason/score predictions | 36 | [None, None] | {} |
| Part2/dataset/Test2_Full/Test2_Full.csv | coarse rally outcome/score label candidate | 75 | [None, None] | {} |
| Part2/dataset/Test2_Full/Test2_Full_Rev_ball_filled.csv | shuttle trajectory prediction/filled estimate | 29296 | [0, 29295] | {"visibility_counts":{"0":4745,"1":24551},"visible_low_confidence_count":707,"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":50} |
| Part2/dataset/Test2_Full/Test2_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 29296 | [0, 29295] | {"visibility_counts":{"0":4745,"1":24551},"visible_low_confidence_count":707,"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":50} |
| Part2/dataset/Test2_Full/Test2_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":300,"frame_size":{"width":1280,"height":720},"corners":{"TL":[448,305],"TR":[829,304],"BR":[933,659],"BL":[347,659]},"net":{"net_Y":433.5,"net_top_Y":310.0,"left_bottom":[370,435],"right_bottom":[908,432],"cable_left":[365,311],"cable_right":[912,309]},"source":"manual"}} |
| Part2/dataset/Test2_Full/Test2_Full_rally.csv | generated interval reference/proposal | 73 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test2_Full/player_detections.csv | two-slot player point prediction | 29296 | [0, 29295] | {"both_slots_present_rows":28573,"slot1_lower_than_slot2_rows":24648,"slot2_lower_than_slot1_rows":3925} |
| Part2/dataset/Test2_Full/win_predictions.csv | generated winner/reason/score predictions | 73 | [None, None] | {} |
| Part2/dataset/Test3_Full/Test3_Full.csv | coarse rally outcome/score label candidate | 22 | [None, None] | {} |
| Part2/dataset/Test3_Full/Test3_Full_Rev_T4.csv | generated interval reference/proposal | 19 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test3_Full/Test3_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 8414 | [0, 8413] | {"visibility_counts":{"0":1353,"1":7061},"visible_low_confidence_count":257,"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":0} |
| Part2/dataset/Test3_Full/Test3_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":4207,"frame_size":{"width":1280,"height":720},"corners":{"TL":[445.7446006183587,302.7049000408673],"TR":[824.4346408416882,301.47539192103454],"BR":[930.1727689559945,650.6556979535401],"BL":[352.30160368013446,653.1147141932057]},"net":{"net_top_Y":310.0819487598639,"net_Y":432.41800668872196,"left_bottom":[365.8262479738248,431.80325262330774],"right_bottom":[910.5005590742632,433.0327607431405],"cable_left":[363.3672217386084,311.31145687969666],"cable_right":[912.9595853094795,308.85244064003115]},"source":"manual"}} |
| Part2/dataset/Test3_Full/Test3_Full_rally.csv | generated interval reference/proposal | 19 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test3_Full/player_detections.csv | two-slot player point prediction | 8414 | [0, 8413] | {"both_slots_present_rows":8323,"slot1_lower_than_slot2_rows":8071,"slot2_lower_than_slot1_rows":252} |
| Part2/dataset/Test3_Full/win_predictions.csv | generated winner/reason/score predictions | 19 | [None, None] | {} |
| Part2/dataset/Test4_Full/Test4_Full.csv | coarse rally outcome/score label candidate | 45 | [None, None] | {} |
| Part2/dataset/Test4_Full/Test4_Full_Rev_ball_filled.csv | shuttle trajectory prediction/filled estimate | 20034 | [0, 20033] | {"visibility_counts":{"0":4685,"1":15349},"visible_low_confidence_count":579,"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":34} |
| Part2/dataset/Test4_Full/Test4_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 20034 | [0, 20033] | {"visibility_counts":{"0":4685,"1":15349},"visible_low_confidence_count":579,"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":34} |
| Part2/dataset/Test4_Full/Test4_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":300,"frame_size":{"width":1280,"height":720},"corners":{"TL":[450,304],"TR":[831,304],"BR":[932,658],"BL":[347,662]},"net":{"net_Y":435.5,"net_top_Y":311.0,"left_bottom":[369,436],"right_bottom":[908,435],"cable_left":[367,312],"cable_right":[911,310]},"source":"manual"}} |
| Part2/dataset/Test4_Full/Test4_Full_rally.csv | generated interval reference/proposal | 41 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test4_Full/player_detections.csv | two-slot player point prediction | 20034 | [0, 20033] | {"both_slots_present_rows":18629,"slot1_lower_than_slot2_rows":16938,"slot2_lower_than_slot1_rows":1691} |
| Part2/dataset/Test4_Full/win_predictions.csv | generated winner/reason/score predictions | 41 | [None, None] | {} |
| Part2/dataset/Test6_Full/Test6_Full.csv | coarse rally outcome/score label candidate | 42 | [None, None] | {} |
| Part2/dataset/Test6_Full/Test6_Full_T4.csv | generated interval reference/proposal | 43 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test6_Full/Test6_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 17915 | [0, 17914] | {"visibility_counts":{"0":706,"1":17209},"visible_but_zero_xy":2,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":0} |
| Part2/dataset/Test6_Full/Test6_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":8957,"frame_size":{"width":1280,"height":720},"corners":{"TL":[445.7446006183587,301.47539192103454],"TR":[826.8936670769046,300.2458838012018],"BR":[930.1727689559945,655.5737304328712],"BL":[344.9245249744852,655.5737304328712]},"net":{"net_top_Y":305.1639162005988,"net_Y":429.95899444350977,"left_bottom":[364.59673485621664,430.573744503475],"right_bottom":[906.8120197214384,429.3442363836422],"cable_left":[360.908195503392,307.62293252019833],"cable_right":[910.5005590742632,302.7049000408673]}}} |
| Part2/dataset/Test6_Full/Test6_Full_rally.csv | generated interval reference/proposal | 42 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test6_Full/player_detections.csv | two-slot player point prediction | 17915 | [0, 17914] | {"both_slots_present_rows":17480,"slot1_lower_than_slot2_rows":14535,"slot2_lower_than_slot1_rows":2945} |
| Part2/dataset/Test6_Full/win_predictions.csv | generated winner/reason/score predictions | 42 | [None, None] | {} |
| Part2/dataset/Test7_Full/Test7_Full.csv | coarse rally outcome/score label candidate | 31 | [None, None] | {} |
| Part2/dataset/Test7_Full/Test7_Full_T4.csv | generated interval reference/proposal | 33 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test7_Full/Test7_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 10725 | [0, 10724] | {"visibility_counts":{"0":2979,"1":7746},"visible_but_zero_xy":0,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":0} |
| Part2/dataset/Test7_Full/Test7_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":5362,"frame_size":{"width":1280,"height":720},"corners":{"TL":[445.7446006183587,301.47539192103454],"TR":[824.4346408416882,299.01637568136897],"BR":[928.9432558383863,650.6556979535401],"BL":[344.9245249744852,654.3442223130385]},"net":{"net_top_Y":305.7786693404492,"net_Y":429.9589904415599,"left_bottom":[363.3672217386084,430.573744503475],"right_bottom":[905.5825066038302,429.3442363836422],"cable_left":[359.67868238578376,306.3934244003656],"cable_right":[909.2710459566549,305.1639162805328]}}} |
| Part2/dataset/Test7_Full/Test7_Full_rally.csv | generated interval reference/proposal | 30 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test7_Full/player_detections.csv | two-slot player point prediction | 10725 | [0, 10724] | {"both_slots_present_rows":10318,"slot1_lower_than_slot2_rows":9557,"slot2_lower_than_slot1_rows":761} |
| Part2/dataset/Test7_Full/win_predictions.csv | generated winner/reason/score predictions | 30 | [None, None] | {} |
| Part2/dataset/Test9_Full/Test9_Full.csv | coarse rally outcome/score label candidate | 88 | [None, None] | {} |
| Part2/dataset/Test9_Full/Test9_Full_ball_filled.csv | shuttle trajectory prediction/filled estimate | 33157 | [0, 33156] | {"visibility_counts":{"0":7722,"1":25435},"visible_low_confidence_count":862,"visible_but_zero_xy":1,"invisible_but_nonzero_xy":0,"coordinates_outside_1280x720":0} |
| Part2/dataset/Test9_Full/Test9_Full_court.json | court calibration candidate | JSON | [None, None] | {"court":{"frame_no":300,"frame_size":{"width":1280,"height":720},"corners":{"TL":[473,264],"TR":[804,264],"BR":[939,659],"BL":[345,659]},"net":{"net_Y":401.0,"net_top_Y":283.0,"left_bottom":[393,402],"right_bottom":[888,400],"cable_left":[388,283],"cable_right":[894,283]},"source":"manual"}} |
| Part2/dataset/Test9_Full/Test9_Full_rally.csv | generated interval reference/proposal | 82 | [None, None] | {"timestamp_frame_inconsistency_at_30fps":[]} |
| Part2/dataset/Test9_Full/player_detections.csv | two-slot player point prediction | 33157 | [0, 33156] | {"both_slots_present_rows":30678,"slot1_lower_than_slot2_rows":27457,"slot2_lower_than_slot1_rows":3221} |
| Part2/dataset/Test9_Full/win_predictions.csv | generated winner/reason/score predictions | 82 | [None, None] | {} |

## Byte-identical exports

```json
[
  [
    "Part2/dataset/Test2_Full/Test2_Full_Rev_ball_filled.csv",
    "Part2/dataset/Test2_Full/Test2_Full_ball_filled.csv"
  ],
  [
    "Part2/dataset/Test3_Full/Test3_Full_Rev_T4.csv",
    "Part2/dataset/Test3_Full/Test3_Full_rally.csv"
  ],
  [
    "Part2/dataset/Test4_Full/Test4_Full_Rev_ball_filled.csv",
    "Part2/dataset/Test4_Full/Test4_Full_ball_filled.csv"
  ]
]
```

## Full2 exact joins

```json
{
  "malformed_rows": [
    {
      "row": 21,
      "values": {
        "Start_Frame": "...",
        "End_Frame": null,
        "Start_Time_sec": null,
        "End_Time_sec": null,
        "Duration_sec": null,
        "win_point_player": null,
        "win_reason": null,
        "ball_types": null,
        "lose_reason": null,
        "roundscore_A": null,
        "roundscore_B": null
      }
    }
  ],
  "usable_numeric_rows": 20,
  "rows": 21,
  "rally_rows": 36,
  "exact_interval_matches_to_rally": 10,
  "exact_interval_matches_to_rally_rows": [
    [
      1,
      1
    ],
    [
      4,
      4
    ],
    [
      6,
      6
    ],
    [
      7,
      7
    ],
    [
      12,
      12
    ],
    [
      16,
      16
    ],
    [
      17,
      17
    ],
    [
      18,
      18
    ],
    [
      19,
      19
    ],
    [
      20,
      20
    ]
  ],
  "semantic_exact_match_to_first_N_primary_rows": false
}
```

## Winner-to-rally binding

```json
{
  "1": {
    "win_rows": 36,
    "rally_rows": 36,
    "win_and_rally_frame_intervals_identical": true
  },
  "2": {
    "win_rows": 73,
    "rally_rows": 73,
    "win_and_rally_frame_intervals_identical": true
  },
  "3": {
    "win_rows": 19,
    "rally_rows": 19,
    "win_and_rally_frame_intervals_identical": true
  },
  "4": {
    "win_rows": 41,
    "rally_rows": 41,
    "win_and_rally_frame_intervals_identical": true
  },
  "6": {
    "win_rows": 42,
    "rally_rows": 42,
    "win_and_rally_frame_intervals_identical": true
  },
  "7": {
    "win_rows": 30,
    "rally_rows": 30,
    "win_and_rally_frame_intervals_identical": true
  },
  "9": {
    "win_rows": 82,
    "rally_rows": 82,
    "win_and_rally_frame_intervals_identical": true
  },
  "10": {
    "win_rows": 93,
    "rally_rows": 93,
    "win_and_rally_frame_intervals_identical": true
  }
}
```

## Annotation-to-component metric mapping

| Component | Defensible use now | Not defensible as independent GT accuracy |
|---|---|---|
| player_detection | anonymous point-to-point disagreement / coverage after source alignment | AP/mAP/IoU: no boxes; accuracy PR lacks reviewed positives/negatives |
| player_tracking | slot continuity and switching diagnostics only | HOTA/IDF1/ID switches against GT: no reviewed persistent identities/boxes; two slots cannot establish doubles support |
| pose | None | PCK/OKS: no keypoints/joint visibility |
| shuttle | legacy trajectory agreement/continuity/coverage at bound 1280x720 timeline | physical localization error/visibility precision/recall because generated and interpolated rows have no independent labels or fill flag |
| court | pixel corner/net disagreement at annotated frame; single-frame manual candidate | all-frame calibration accuracy and 3D/airborne court accuracy |
| contact_racket | None | no independent racket/contact timing/negative labels |
| stroke | coarse rally-family semantic comparison only after explicit taxonomy and event aggregation | per-shot confusion: one coarse family label per rally is not a hit sequence |
| rally | legacy interval agreement and coarse-label temporal agreement, separately | independently adjudicated boundary physical accuracy absent review |
| winner_score | coarse reference comparison only after explicit source-bound A/B identity and rally association; full2 incomplete20-row candidate can help adjudicate | win_predictions.csv is a competing model output, not independent winner truth; exact official score sequence is incomplete on edited video |
| highlights | temporal overlap with valid rally annotations as a proxy only | semantic highlight desirability/importance: no highlight labels |

## Time, coordinates and identity binding protocol

- All dense point CSVs must have complete zero-origin frame coverage verified against the selected source’s decoded frame count and rational PTS before use. Numeric interval frame/time checks assume30FPS and are explicitly recorded; this does not itself bind a source video hash.
- The supplied court reference uses image pixels with x rightwards and y downwards in1280×720. Legacy shuttle code rescales model positions to the processed input resolution; confirm that the matching processed input was1280×720 from a synchronized overlay. Do not compare1920×1080 source pixels directly against1280×720 points.
- Slot1/2 are current two-slot detections, not named athletes or permanent near/far teams. Legacy side inference estimates near/far from average Y and court geometry. Its winner predictor defaults PlayerA=far and PlayerB=near; the primary CSV convention remains unresolved and can conflict with scores/edited sequences.
- Preserve missing player coordinates as missing, not zero; preserve invisible shuttle(0,0) sentinels separately from real coordinates. No fill/observed flags may be invented.
- Manual court corner error can be measured only on the annotated view/frame after media binding. Court images must not be injected as run calibration before a genuinely automatic-calibration baseline unless the run is explicitly labelled as externally calibrated.

## Concrete producer evidence

- `legacy/pipeline/analysis/player_detection.py:297–365`: frame-by-frame YOLO detection, court filter, bottom_center export and current first-two enumerated slots. Confidence filter defaults0.4; confidence is model output, not annotator certainty.
- `legacy/pipeline/analysis/extract_features_novideo.py:140–190`: global side inference and inconsistent center-plus50 bottom surrogate.
- `legacy/pipeline/TrackNetV3/shuttle_predict.py:91–96`: rescaling to actual processed video dimensions.
- `legacy/pipeline/docs/03_shuttle_tracking.md`: raw detection→filter→fill stages and confidence/visibility conventions.
- `legacy/pipeline/TrackNetV3/fill_gaps.py`: cubic spline/linear estimate, gated with player confidence and motion; no per-row filled indicator in supplied schema.
- `legacy/pipeline/win_predictor/predict.py:254–260, 288–305, 448–526`: far/near naming and generated outcome/reason/probability/score fields.
- `legacy/pipeline/analysis/evaluate_rallies_unified.py:8`: `_T.csv` explicitly configured as detected rallies.
- `docs/architecture/audits/part2-label-readiness-20261103.md`: earlier provenance caution, useful context but no substitute for the present full-content scan.

## Full numerical detail

The companion JSON contains every file hash, exact columns, examples, missing-value counts, numeric min/max/mean/P50/P95, all categorical counts, contiguous-frame checks, geometry/visibility/slot diagnostics, duplicate groups and binding checks. Any metric claim should cite a file hash plus its declared evidence role. No neural inference, new model adoption, annotation editing or production change was performed.

## Exact diagnosis candidates from the full-content scan

- Test1 dense trajectory is17,268 rows, frame0…17,267; player detections have the same extent. All dense datasets in this scan are zero-origin and contiguous; the JSON records each extent and duplicate count. Matching a filename is insufficient: bind to decoded video count/PTS and source hash before comparison.
- Test1 trajectory has14,014 visible estimates and3,254 zero-visibility rows. Of visible estimates,759 carry Confidence<0.25, consistent with postprocessing/fill semantics and incompatible with naively treating Confidence as a reviewed visibility probability. Filling cannot be uniquely identified row-by-row from this final table alone.
- Test1 player slot1 has larger Y than slot2 in14,829 frames, and smaller Y in1,903 frames (16,732 both-present). Across every match both orderings occur. Slot numbering cannot be fixed to far/near or an athlete based only on majority ordering. Crossings could also include detection noise; these are not certified ID switches.
- Test1 Full2 has20 usable numeric records, with only10 exact interval matches to the36-row rally table; its row21 is a literal`...` placeholder with missing other fields. The twenty numeric rows are not simply a complete independently reviewed alternative. Against primary coarse rows by position, row19 reverses winner PlayerA→PlayerB and changes reason/shot/score; row20 changes the supplied score. The JSON stores exact raw differences. Do not silently choose the version that makes current predictions look correct.
- Test2 filled trajectory has50 coordinates outside1280×720; Test4 has34. Preserve these as reference diagnostic rows, not clipped or automatically discarded ground-truth errors. They can reflect off-screen estimates, interpolation overshoot or coordinate binding problems. Exact frame/value examples are in the JSON.
- Test6 has2 visible rows with a zero coordinate component; Test9 has1. A zero coordinate component at an image border is distinct from an invisible(0,0) sentinel. Do not reject all zero-x or zero-y visible points by an unreviewed policy.
- Test2 normal/Rev ball exports are byte-identical; Test4 normal/Rev ball exports are byte-identical; Test3 Rev_T4 and rally files are byte-identical. Other timing variants may have equal numeric intervals but differing bytes/text formatting; exact duplicate and numeric interval comparison must remain separate.

## Immediate readiness decision for Test1

The fresh automatic Test1 baseline may run using the retained matched raw source with no annotations supplied to inference. Run output comparison afterward should keep three reference roles distinct: coarse outcome labels, legacy interval/trajectory/player predictions, and one-frame court geometry (Test1 explicitly declares manual; Test6/Test7 origin remains unspecified). Initial point comparisons should use anonymous per-frame assignment of current predicted bottom centers and legacy point slots at equal1280×720 canonical frames, report distance/coverage/disagreement, and leave player AP/mAP, IDF1/HOTA and independently labelled physical shuttle accuracy unavailable. Visual overlays must first certify point semantics and source/frame alignment; they are diagnostic, not automatically new ground truth. Court calibration supplied in a separate controlled arm must not be confused with the automatic baseline. No schema ambiguity blocks ordinary fresh baseline execution; it does constrain which comparisons can be called accuracy.

## Court provenance correction

Direct JSON contents distinguish **six explicit manual-origin assertions** (Tests1,2,3,4,9,10) from **two unspecified origins** (Tests6,7 omit `source`). Earlier blanket wording that all eight were manual was incorrect and is superseded here. No `source` field was inserted into an original JSON; unknown provenance remains unknown. Frame-specific geometry can be compared diagnostically after alignment for all eight, while any manual-reference claim is restricted to the six explicit assertions and still requires source/review binding.
