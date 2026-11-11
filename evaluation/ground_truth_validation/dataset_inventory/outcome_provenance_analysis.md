# Outcome annotation provenance and semantic readiness

Scope: all eight available Part2 match folders (Tests1,2,3,4,6,7,9,10), full contents of every primary outcome table, every win_predictions table, Test1 Full2, four alternative legacy label tables, and all four reference DOCX documents. Original data were read only. No inference, label repair, score reconstruction or pipeline change was performed. The companion JSON preserves all counts, hashes, row IDs and conflict records.

## What the files actually represent

| Family | Evidence from contents/producer | Evaluation role |
|---|---|---|
| TestN_Full.csv | Eight columns: coarse time spans, winner/reason, one ball_types value, loser reason and scores. Legacy documentation explicitly calls these hand-labelled. | Primary coarse human-origin reference candidate; quality issues and identities require explicit adjudication. Human-origin documentation is not per-row certification. |
| Test1_Full2.csv | 21 data records:20 numeric rows plus literal ellipsis row21. Eleven columns combine exact frame/time with semantics. Only10 of20 numeric boundary pairs equal the supplied rally table; rows19/20 disagree with primary semantics/scores. | Incomplete mixed/derived candidate. Preserve whole file and all bad rows; no full-match accuracy denominator and no automatic GT promotion. |
| *_rally.csv / *_T.csv / *_T4.csv | Seven-column boundary family is written by legacy detect_rallies.py from detected/merged/lookback rallies. | Original historical benchmark contract may continue separately; results are supplied-reference agreement, not certified physical timing truth. |
| win_predictions.csv | All416 rows across eight videos have frame pairs identical to their corresponding _rally rows. reason_src/fault_src/CNN fields identify inferred ML/rule decisions. Running scores increment from those inferred winners. | Earlier model outputs. Suitable for model-to-model disagreement and regression diagnosis, not independent winner/reason/score truth. |

Producer evidence: [legacy/pipeline/docs/10_evaluation.md:14](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/docs/10_evaluation.md:14) explicitly describes human-origin primary tables; [legacy/pipeline/analysis/detect_rallies.py:598](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/analysis/detect_rallies.py:598) constructs frame/time rally CSVs; [legacy/pipeline/win_predictor/predict.py:492](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/win_predictor/predict.py:492) builds score from inferred winner and [legacy/pipeline/win_predictor/predict.py:497](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/win_predictor/predict.py:497) writes prediction fields.

## Coverage and score continuity

| Test | Primary data rows | Valid coarse spans | Blank rows | Generated rally rows | Win-prediction rows | Win-pred frame pairs matching rally | Non-unit adjacent score transitions | Raw winner/unit-score disagreements |
|---|---|---|---|---|---|---|---|---|
| 1 | 36 | 36 | [] | 36 | 36 | 36 | 0 | 0 |
| 2 | 75 | 75 | [] | 73 | 73 | 73 | 26 | 0 |
| 3 | 22 | 22 | [] | 19 | 19 | 19 | 1 | 1 |
| 4 | 45 | 45 | [] | 41 | 41 | 41 | 20 | 0 |
| 6 | 42 | 42 | [] | 42 | 42 | 42 | 0 | 0 |
| 7 | 31 | 31 | [] | 30 | 30 | 30 | 0 | 1 |
| 9 | 88 | 78 | [79, 80, 81, 82, 83, 84, 85, 86, 87, 88] | 82 | 82 | 82 | 0 | 0 |
| 10 | 101 | 96 | [97, 98, 99, 100, 101] | 93 | 93 | 93 | 0 | 0 |

Across the eight primary files:440 data rows,425 nonblank time spans,15 completely blank records. All425 time spans are parseable and positive; that does not make every semantic row complete or reviewed. Test9 blank row IDs79–88 and Test10 row IDs97–101 remain explicit empty records, not negative rallies or silently discarded difficult cases.

Score checks are diagnostic only. They start from a declared0:0 and inspect adjacent supplied score rows. A delta(1,0)/(0,1) can be compared with symbolic winnerA/B; other deltas, missing fields, resets or omitted points stay unresolved. Test2 has26 and Test4 has20 non-unit transitions; these are not automatically annotation errors or model errors. There is no justified continuous-score ground-truth sequence until these intervals and any game resets/edited-out points are reviewed.

## Exact quality failures and ambiguous cases

### Test3

- Source data row 6 (CSV line7): `{"row": 6, "kind": "score_missing_nonfinite_or_unparseable"}`.
- Source data row 9 (CSV line10): `{"row": 9, "kind": "winner_disagrees_with_unit_score_increment", "previous_score": [3.0, 5.0], "score": [4.0, 5.0], "score_implied_winner": "Player A", "raw_winner": " Player A", "normalized_winner_matches": true, "discrepancy_type": "whitespace_only", "interval": [99.0, 102.0]}`.

### Test7

- Source data row 1 (CSV line2): `{"row": 1, "kind": "winner_disagrees_with_unit_score_increment", "previous_score": [0, 0], "score": [0.0, 1.0], "score_implied_winner": "Player B", "raw_winner": "Player A", "normalized_winner_matches": false, "discrepancy_type": "substantive_symbolic_winner_disagreement", "interval": [6.0, 15.0]}`.

Test3 row6/CSV line7 is `1:13,1:18,Player B,Opponent Out of Bounds,Opponent Failed to Return,2,4`: only7 cells for the8-column header. Parsed fields are ball_types=`Opponent Failed to Return`, lose_reason=`2`, roundscore_A=`4`, roundscore_B=null. A missing column cannot be guessed. Keep the timing interval usable, while outcome/reason/class/score fields for that row need field-specific eligibility and manual adjudication.

Test3 row9 has raw winner ` Player A` with a leading space. Its unit-score discrepancy is normalization-only, not evidence of a different physical winner. Preserve the original raw string; any whitespace normalization must be a declared adapter transformation with both raw and normalized values retained. Test7 row1’s winnerA versus score0:1 is a substantive symbolic inconsistency under the0:0 opening assumption.

### Test1 Full2

| Diagnostic | Observed |
|---|---|
| Data records | 21 |
| Numeric rows | 20 |
| Malformed source row | [{'source_row': 21, 'Start_Frame': '...', 'End_Frame': None, 'Start_Time_sec': None, 'End_Time_sec': None, 'Duration_sec': None, 'win_point_player': None, 'win_reason': None, 'ball_types': None, 'lose_reason': None, 'roundscore_A': None, 'roundscore_B': None}] |
| 30 FPS frame/time-consistent numeric rows | 20 |
| Exact _rally boundary pairs | 10 |
| Primary/Full2 same-position semantic differences | [{'row': 19, 'fields': {'win_point_player': {'primary': 'Player A', 'full2': 'Player B'}, 'win_reason': {'primary': 'Opponent Hit the Net', 'full2': 'Winner Shot'}, 'ball_types': {'primary': 'Hook Shot', 'full2': 'Lift Shot'}, 'lose_reason': {'primary': 'Hit the Net', 'full2': 'Opponent Failed to Return'}, 'roundscore_A': {'primary': '10', 'full2': '9'}, 'roundscore_B': {'primary': '9', 'full2': '10'}}}, {'row': 20, 'fields': {'roundscore_A': {'primary': '11', 'full2': '10'}, 'roundscore_B': {'primary': '9', 'full2': '10'}}}] |

Row19 is an illustrative concrete conflict: primary coarse table has winnerA, hit-net, Hook Shot, score10:9; Full2 has winnerB, winner-shot, Lift Shot, score9:10. Their durations/row correspondence must be checked by time and video, not assumed by position. Full2 only reaches numeric end9967 (332.233s), while Test1 video/primary annotations extend far beyond that. It is not a complete alternate36-rally ground truth. No producer or reviewer log certifying this specific file was located.

## Alternative legacy reference versions

| Test | Exact-time matched rows | Raw winner disagreements | Legacy table |
|---|---|---|---|
| 1 | 32 | 6 | /home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/vjepa_setup/dataset/labels/Test1_Full_rev.csv |
| 3 | 21 | 8 | /home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/vjepa_setup/dataset/labels/Test3_Full_Rev.csv |
| 6 | 40 | 1 | /home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/vjepa_setup/dataset/labels/Test6_Full.csv |
| 7 | 31 | 1 | /home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/vjepa_setup/dataset/labels/Test7_Full.csv |

Exact-span disagreements are6/32 for Test1,8/21 for Test3,1/40 for Test6 and1/31 for Test7. The companion JSON includes raw per-field differences; this does not decide which table is correct. Match-by-time sensitivity should retain conflicts and time-shifted/unmatched rows separately. Case changes and raw taxonomy wording differences are not silently mapped into new physical labels.

## Identity, taxonomy and matching policy

The legacy predictor CLI defines PlayerA as far and PlayerB as near ([legacy/pipeline/win_predictor/predict.py:541](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/win_predictor/predict.py:541)). This is that implementation’s spatial slot convention, not proof that all primary annotations use the same physical athlete/team identity through end changes and cuts. Resolve A/B from video evidence and explicit source-bound identity bindings; do not use the same winner labels to fit the binding and then claim unbiased winner accuracy.

For this new evaluation, prespecify interval matching before predictions. Recommended continuity with the preserved benchmark: maximum-cardinality then total temporal IoU at0.5, half-open intervals, full misses/extras and matched/all-reference denominators. Keep primary coarse references, generated rally references, Full2 partial candidate and earlier prediction comparisons as separate result families. The legacy evaluator uses greedy IoU≥0.3 and evaluates winner/reason only on matched rows ([legacy/pipeline/win_predictor/evaluate_predictions.py:35](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/win_predictor/evaluate_predictions.py:35)); its historical scores are not directly comparable to the new0.5 one-to-one benchmark or end-to-end accuracy.

Use numeric start_frame/end_frame from win_predictions only after source FPS/timebase validation. Its displayed start_time/end_time are minute:second strings inherited from the rally display fields and may be truncated; they are not more accurate event timestamps. Coarse primary MM:SS labels provide whole-second precision only. Do not fit offsets to maximize agreement.

One ball_types value per rally does not label every stroke/contact. Preserve class spellings/whitespace and reason-like values. A reviewed reason adapter can map the four documented free-text reason labels into legacy three-class reason space, but unmapped labels must remain unknown. Do not equate final rally ball type with all within-rally strokes.

## Reference DOCX provenance evidence

### Amateur_players_insights.docx

No selected primary-origin/corrections statement found. This document is product/research context, not a label-review ledger.

### Model_Exploration_History.docx

- Paragraph 106: This is where the “vk15b” / “vk15b2” naming actually comes from — it is not a vision or video model. It’s a 1.5-billion-parameter RWKV7 architecture causal language model (sportsvision/VK1.5B_CTX4096), prompted with the rally’s ball/player/court trajectory rendered as structured text, asked to output Winner: X / Reason: Y directly as generated text. (vk15b2/vk15b_dataset/ — the folder of hand-labeled ground truth — outlived this specific model and became the shared ground-truth dataset every later approach, including the shipped pipeline, evaluates against.)

### Pipeline_Quick_Reference.docx

- Paragraph 59: Review task: appears automatically once the pipeline finishes. Reviewer edits the rally table (winner/reason/times), timeline, comments — corrections saved separately from the model’s own output, so nothing original is overwritten.
- Paragraph 63: Measured against 8 real hand-labeled matches (399 total matched rallies):

### Badminton_Rally_Analysis_Pipeline_Formatted.docx

- Paragraph 70: Corrections are saved separately in corrections.json; the model’s original output remains preserved.
- Paragraph 171: fusion_layer.py and win_predictor/ combine the rule engine, trajectory Random Forest, and CNN ensemble to decide, per rally, who won and why. The source describes this as the most tuned part of the system; docs/10_evaluation.md records measured accuracy against real ground truth and a documented bug fix in which a fusion strategy was found to hurt accuracy rather than improve it.

Model_Exploration_History paragraph106 explicitly describes the primary vk15b2 dataset as hand-labelled and reused across later approaches. Pipeline_Quick_Reference paragraph63 likewise calls eight matches hand-labelled. This establishes documented legacy origin and prior exposure, not blind held-out status or a named reviewer for each row. The formatted pipeline reference paragraph70 and Quick Reference paragraph59 describe corrections saved separately from model output. No corrections.json or per-row review ledger exists under the inspected Part2 tree; do not infer that every CSV was corrected because a review UI exists. Related implementation: [legacy/pipeline/webapp/server.py:9](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/webapp/server.py:9) and [legacy/pipeline/docs/09_web_review_app.md:125](/home/administrator/Desktop/sport-analytics/Sports_Analytics/legacy/pipeline/docs/09_web_review_app.md:125).

## Component metric eligibility from these outcome families

| Component/metric | Can be evaluated now? | Conditions |
|---|---|---|
| Coarse rally P/R/F1/IoU | Yes, qualified supplied-reference agreement | All nonblank parseable spans; exact original source/timebase binding; preserve conflicts and blanks. |
| Frame-exact rally boundary errors | Historical generated-reference agreement only | Keep _rally/T/T4 provenance distinct; coarse labels do not certify one-frame accuracy. |
| Winner/reason classification | Conditional reference-agreement metric after alignment and identity resolution | Report matched-reference and end-to-end coverage, abstentions, field-validity exclusions and unresolved symbolic A/B cases; no invented winners. |
| Running score sequence | Not yet certified | Review Test2/Test4 nonunit transitions, Test3 malformed row and Test7 opening conflict; bind players and point order. |
| Per-contact/per-shot class metrics | No exhaustive outcome-family labels | Need reviewed timestamps, shot sequence taxonomy and hitter references; one ball_types entry is insufficient. |
| Player detection/pose/shuttle tracking metrics | Not supplied by outcome CSVs | Separate component schemas/provenance must establish reviewed GT; win_predictions are never GT for these components. |
| Highlights/player analytics | Bounded semantic/timing diagnostics only | No exhaustive highlight quality or player metric truth identified in these files. |

## Missing tests and next gated actions

No Test5 or Test8 annotation directory exists locally; Test5 has a historical video entry, while Test8 has no listed media in the historical supplied-folder listing. Recheck live discovery centrally, but do not invent datasets or auto-skip the new user-requested1→10 sequence. The orchestrator should stop at the first unavailable pairing and record the exact missing inputs.

For Test1 first: bind exact raw video hash/frame PTS; preserve original primary/Full2/rally/win-prediction families; run fresh current pipeline without annotation input; compare its outputs separately to coarse documented human references and historical generated references; inspect the Full2 row19 conflict and prior legacy conflicts on synchronized evidence. Only reviewed source-bound adjudications may become new physical GT, stored separately from originals. Identify evaluation-only adapters versus actual pipeline changes and establish a before/after baseline for every proposed fix.

