# Test 2 annotation inventory, semantics and evaluation contract

Independent read-only inspection of **all seven files** in `Part2/dataset/Test2_Full` on 2026-11-11. No video inference, annotation correction or production change was performed by this inventory step. The local originals are the inspected population; the orchestrator separately verifies Drive discovery, video hash and source/proxy alignment. The orchestrator reports that the live supplied Drive root currently exposes `video_raw`, with the downloaded Test 2 video hash and byte count verified; the annotation provenance here remains the preserved **local Part2 originals**, not a newly downloaded or live-revalidated annotation folder. The reproducible [inventory script](inventory_test02.py) produces [annotation_inventory.json](annotation_inventory.json), including SHA256, byte size, complete columns, missing-field counts, first/last samples, coverage and exact issue rows/frames.

The Test 1 provenance methodology carries forward, but the counts and checks below were recomputed from Test 2 contents. **There is no Test2 Full2 file locally.** A missing file is not silently substituted with Test1 Full2 or an inferred annotation.

## Complete file-to-component mapping

| Original file | Population and actual content | Pipeline comparison | Evidence status |
|---|---|---|---|
| `Test2_Full.csv` | 75 coarse intervals, 00:02–16:16; 8 outcome/score columns | Qualified rally overlap; conditional outcome/reason agreement once identities and source intervals are bound | Documented legacy human-origin reference candidate; no supplied per-row review ledger |
| `Test2_Full_rally.csv` | 73 frame/time intervals, frames 53–29273 | Preserve prior timing benchmark; compare fresh pipeline only as needed for before/after regression | Legacy generated interval reference, not independently certified frame-exact physical truth |
| `Test2_Full_ball_filled.csv` | 29,296 rows, frames 0–29295; X/Y/visibility/confidence | Source-bound trajectory disagreement, availability and gap diagnostics | Generated and gap-filled trajectory; no reliable observed-versus-filled flag |
| `Test2_Full_Rev_ball_filled.csv` | Same 29,296 rows and **byte-identical** to the preceding file | Record alias and checksum; do not count twice | Not an independent second label population |
| `player_detections.csv` | 29,296 rows, frames 0–29295; two player point/confidence slots | Anonymous per-frame bottom-center agreement and presence diagnostics | Generated detection-order slots; no boxes, persistent person identities or visibility review |
| `Test2_Full_court.json` | Manual-source declaration at frame 300; 1280×720 corners and net | Bound calibration point/line disagreement at its valid source frame | Single manual calibration candidate; scope across edits/camera changes is unverified |
| `win_predictions.csv` | 73 generated outcome rows; exact same frame pairs as rally CSV | Legacy prediction disagreement and diagnostic provenance | ML/rule outputs and reconstructed running score, not winner/score ground truth |

All three framewise CSVs have one row for every index 0–29295, without missing or duplicate frame indices. This supports a **29,296-frame pairing candidate**; it does not replace the decoded source-video/PTS audit. At 30 fps that population spans 976.5333 seconds, with the last index at 976.5 seconds. No per-contact, pose, racket, exhaustive stroke, reviewed tracking identity, heatmap or highlight-quality annotation exists among these seven originals.

## Schemas and conventions, verified from content and producers

### Coarse outcome table

`start_time,end_time` are whole-second `MM:SS` strings; all 75 spans are parseable, positive and ordered without adjacent overlap. They are coarse sporting intervals, not exact one-frame boundaries. `win_point_player` is symbolic `Player A` or `Player B` (27 A, 48 B). `win_reason` has 32 `Opponent Out of Bounds`, 22 `Winner Shot`, and 21 `Opponent Hit the Net`; `lose_reason` has the complementary three strings. `ball_types` has **15 distinct values** and one entry per rally: Lift Shot, Smash, Lob, Net Shot, Drive Defense, Drive, Clear, Net Kill, Cross Net Shot, Push Shot, Long Serve, Slice, Block, Stick Smash and Defensive Slice. It is not an exhaustive contact sequence or a direct replacement for the current stroke taxonomy. `roundscore_A,roundscore_B` parse as integer-valued scores.

Legacy documentation [`legacy/pipeline/docs/10_evaluation.md`](../../../../legacy/pipeline/docs/10_evaluation.md) identifies the eight primary `<match>.csv` tables as hand-labelled, separately from generated support files. This establishes documented origin, not certification that every row is correct or a held-out prospective test. Retain the originals and record any new reviewed interpretation separately.

The documented legacy reason adapter is:

| Supplied coarse label | Legacy class | Restriction |
|---|---|---|
| Opponent Out of Bounds | out_of_bounds | Outcome reason, not a physical landing coordinate label |
| Opponent Hit the Net | hits_net | Outcome reason, not an exhaustive racket/contact sequence |
| Winner Shot / Opponent Failed to Return | wins_by_landing | Legacy taxonomy mapping; does not certify a precise landing event |

The legacy winner predictor declares `Player A=far`, `Player B=near` in [`win_predictor/README.md`](../../../../legacy/pipeline/win_predictor/README.md), and maps a near fault to A and a far fault to B in `predict.py`. **That producer convention does not independently prove that the primary human-origin A/B labels follow persistent athletes, camera sides or scoreboard rows throughout this edited multi-game clip.** Bind source players, changes of ends, game resets and scoreboard rows before named-identity or score accuracy claims. Current unknown identities must remain unknown.

### Generated rally and outcome tables

Rally columns: `Start_Frame,End_Frame` are integer indices; `Start_Time_sec,End_Time_sec,Duration_sec` are floating-point seconds; `Start_Time,End_Time` are coarse display strings. All 73 exact time pairs equal frame indices divided by 30 within 1e-6; all durations equal end minus start. Use exact frame/seconds fields for comparisons; do not reparse the truncated display strings as exact times or add an undocumented inclusive-end frame. The generating code `legacy/pipeline/analysis/detect_rallies.py` writes the same schema after detection, merging and lookback.

Winner columns: `rally_idx` is zero based; `start_frame,end_frame` identify the interval; `start_time,end_time` are display strings; `winner,loser` are symbolic labels; `win_reason,reason_src,fault_side,fault_src,cnn_class` are generated categorical outputs; `cnn_conf,cnn_oob,cnn_hn,cnn_wbl` are model scores; `score_Player A,score_Player B` are reconstructed cumulative points. Their presence does not make those scores calibrated probabilities or independently reviewed results.

All **73 of 73** winner frame pairs equal the corresponding rally rows. Generated winners are 29 A and 44 B, with final running score **29–44**; `predict.py` increments from predicted winners without a game-aware GT ledger. These values must not be compared blindly with primary scores or called actual match scores. Reason sources are 52 `ML_RF`, 14 `ML_HN_I`, 6 `ML_HN`, 1 `ML_STRAT_F`; fault sources are 50 `RULE`, 23 `WBL_Y`. Temporal matching, not row-number matching, is required because the coarse table has 75 intervals.

### Player points

Schema: `frame_no` integer; `player_1_x,player_1_y,player_1_conf,player_2_x,player_2_y,player_2_conf` floating point or empty. Pixel X increases right and Y increases down in the expected image canvas; verify source dimensions before registration. Producer `legacy/pipeline/analysis/player_detection.py` exports **bounding-box bottom-center**, not torso center or actual annotated foot joints. It writes whichever first two filtered detections exist in detector order. Slot numbers are neither permanent IDs nor guaranteed near/far assignments.

Slot 1 is present in 29,266 rows; slot 2 in 28,573; both in 28,573. On those paired rows, slot 1 is lower in the image 24,648 times and slot 2 3,925 times. Relative Y order changes on **2,407 adjacent frame pairs**, starting at frames 4, 6, 11 and 12. This confirms the need for anonymous per-frame assignment; it is **not a measured current-pipeline ID-switch count**. No bounding-box extents, human visibility labels, exhaustive negatives, roster bindings or persistent GT IDs are supplied. Any point-matching gate must be declared; unmatched generated points are disagreements, not certified detector FP/FN.

### Shuttle trajectory

Schema: `Frame` integer; `X,Y` numeric image coordinates; `Visibility` binary; `Confidence` floating point. Zero X/Y consistently accompanies the 4,745 visibility-zero rows; the 24,551 visibility-one rows are all nonzero. The legacy sequence `predict → filter_trajectory → fill_gaps` produces these files. Filled coordinates and visibility share the same schema as observed points, while no interpolation flag is included. `Visibility=1` therefore means retained/generated trajectory availability, not independently verified physical visibility.

At the explicitly diagnostic threshold **Confidence <0.5**, 1,249 visibility-one rows fall below threshold. This is a distribution check only; it neither changes reference visibility nor defines an accuracy denominator. Other historical audits may use other thresholds and must retain their own definitions.

There are **50 rows outside the supplied court JSON's 1280×720 canvas**, at frames **1594–1635** and **16246–16253**. For example frame 1614 is `(551,929)`, and frame 16253 `(721,805)`. Verify the video's actual canvas and coordinate registration first; then inspect these windows visually to distinguish annotation/source scaling mismatch, fill overshoot or other legacy prediction errors. Do not clip or delete them silently, and do not use them as confirmed physical shuttle truth. Preserve these rows in all disagreement denominators with explicit validity categories.

### Court calibration

`frame_no=300` (candidate 10.0 s at 30 fps); `frame_size={width:1280,height:720}`; `source="manual"`. Corners are ordered **TL(448,305), TR(829,304), BR(933,659), BL(347,659)**. `net_Y=433.5`, `net_top_Y=310.0`; bottom endpoints `(370,435),(908,432)` and cable endpoints `(365,311),(912,309)` retain slight slope. These are image points/lines, not world-metre coordinates. Verify exact source-frame identity, corner interpretation and full-court/singles-court meaning before fitting a homography. A floor homography cannot certify airborne shuttle height, speed, contact, landing or line calls. One manual frame is not a scene-wide calibration truth after cuts.

## Score-quality and identity review queue

Using only the supplied primary rows and an explicit initial diagnostic 0–0, there are **26 nonunit adjacent score transitions**, including unchanged scores, multi-point jumps and resets. All **49 unit increments** agree with the supplied symbolic winner; this is internal consistency, not independent outcome accuracy. Exact rows, before/after scores and deltas are retained in the inventory JSON.

| Data row (CSV line) | Interval | Supplied score change | Review purpose |
|---|---|---|---|
| 4 (5) | 00:38–00:59 | 1–2 → 2–3 | Both sides increment; inspect edits/omitted point/score convention |
| 5 (6) | 01:07–01:20 | 2–3 → 4–5 | Multiple missing increments possible |
| 8 (9) | 01:38–01:43 | 5–6 → 5–6 | Winner B but unchanged adjacent score |
| 27 (28) | 05:18–05:40 | 16–21 → 0–1 | Game-reset candidate; do not enforce continuous match score |
| 45 (46) | 08:04–08:15 | 5–19 → 0–1 | Another reset candidate; preceding game may omit points |
| 75 (76) | 16:10–16:16 | 17–19 → 17–21 | Multi-point gap near end |

These are **annotation/sequence ambiguities pending video adjudication**, not 26 proven annotation errors or pipeline defects. The latest code's one-vote-per-source-score-transition fix remains required; repeated OCR readings must not create artificial independent identity corroboration. A score reset or side change must not be resolved by inventing hidden winners.

## Metric eligibility for the fresh Test 2 run

| Component | Available comparison | Unavailable accuracy claim / required evidence |
|---|---|---|
| Rally segmentation | Coarse-reference overlap with 75 spans; preserved 73-row generated timing reference separately | Generated frame boundaries do not certify physical frame-exact accuracy |
| Player detection | Anonymous bottom-center distance/presence disagreement, source-bound overlays | AP/mAP/box IoU need independent reviewed boxes and exhaustive coverage |
| Tracking and identity | Current track continuity and slot-order diagnostics | IDF1/HOTA/ID switches/fragmentation accuracy need reviewed persistent person IDs and visibility |
| Pose/movement | Execution coverage and source overlays | PCK/OKS, joint/movement accuracy lack independent keypoints or movement labels |
| Shuttle | Availability/localization/trajectory disagreement to generated filled values; separate invalid-canvas rows | Physical precision/recall/localization error require independently reviewed observed coordinates/visibility |
| Racket/contact | Candidate coverage and source-bound frame/event failure review | Precision/recall/F1/temporal error lack exhaustive reviewed contact/racket truth |
| Stroke | Label/unknown distributions; cautiously map rally-level semantics only with explicit role | Per-contact class metrics/confusion cannot use one rally-level `ball_types` value as every contact label |
| Winner/reason | Conditional agreement to primary labels after interval and A/B adjudication, plus abstention/end-to-end coverage | Generated `win_predictions` is never GT; unresolved A/B mapping prevents verified named-winner accuracy |
| Scoring | OCR/transition evidence and primary score consistency review | Continuous/game-level accuracy requires reset, omitted-point, source identity and score-convention resolution |
| Analytics/heatmaps/highlights | Actual output persistence, bounds, coverage, anonymous consistency and source review | No independent named-player movement/heatmap/highlight-relevance labels |

Use **unavailable/null with the reason**, never a fabricated zero. Separate stage-conditional denominators from full-pipeline coverage and abstention. Keep matching methods, thresholds, source/proxy clocks, model/version/configuration and runtime resource evidence in the run manifest. Reuse earlier rally benchmarks without overwriting or treating this new run as an unchanged historical result. This inventory is the evaluation contract, not a declaration that inference or all requested component accuracy metrics have completed.

## Preservation and reproducibility

Original files were opened read only; the inventory records SHA256 for all seven, including the duplicate trajectory alias. Recompute and compare those hashes after evaluation/cleanup. The inventory helper scans **only Test2_Full**, does not download videos, does not write under Part2 and does not use annotations as inference inputs. Any adjudicated labels must be a separate source-bound review artifact with reviewer/provenance status. Existing Test 1 outputs, prior eight-video benchmarking matrices and all original data remain outside this step's write scope.
