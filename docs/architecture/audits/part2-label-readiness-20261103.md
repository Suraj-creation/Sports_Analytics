# Part2 annotation readiness audit — 2026-11-03

## Recommendation

Use **`Test7_Full.mp4` paired with `Part2/dataset/Test7_Full/Test7_Full.csv` for a bounded rally/score review**, preserving the conflicting legacy CSV as a separate version. This is the smallest video in the historical Drive manifest and the only candidate for which the inspected notes provide a previously checked video hash, frame rate, frame count and visual timeline review. It is a useful diagnostic pair, **not an independently verified accuracy benchmark**.

First check the existing remote copy at `/home/administrator/Desktop/sport-analytics/Sports_Analytics/data/task2-review/Test7_Full.mp4`. A 2026-10-28 audit records it there. Download one copy only if it is absent or does not match the recorded identity. Current remote presence and the Drive listing are the integration owner's checks; this worker did not access/download/process media.

| Item | Recorded identity / evidence |
|---|---|
| User-supplied folder | `https://drive.google.com/drive/folders/1_2QWSYd_X_BojdRwbu-AMKdx74cIQvGp?usp=sharing` |
| Video name | `Test7_Full.mp4` |
| Drive file ID | `1WS9suAtgbuwB2qc4IteGgFL6xf5hs0Gq`, from the local historical download manifest; current availability not independently checked here |
| Video size | 664,899,136 bytes, historically recorded |
| Video SHA-256 | `1ad1eac44150a0a23e2bad1f3d4204bd41f2d257ff6b35156234d38cfa2b9d9c`, historically recorded |
| Historical media probe | H.264, 1920×1080, 30 fps, 10,725 frames, 357.5 seconds; not reprobed in this audit |
| Primary annotation | `Part2/dataset/Test7_Full/Test7_Full.csv`: 31 nonblank rally rows, first start 6 seconds, final end 357 seconds |
| Primary annotation SHA-256 | `5f1ebabcc0a66dae579bf7ad35ddc48a97e88d1277cc7afa5e7d369a3fcbd9ea`, read from the current local file |
| Conflicting reference | `legacy/pipeline/vjepa_setup/dataset/labels/Test7_Full.csv` |
| Reference SHA-256 | `f4eb326b2021882ec99f33bb439e2aac43bb4f67f124c72f379c654910fc1f1e`, read from the current local file |

Confidence is **high in the intended filename-to-annotation pairing once the video hash is verified**, moderate in its usefulness for coarse rally alignment, and insufficient for treating its winner/outcome/shot labels as adjudicated truth. A/B identity mapping, edited-broadcast continuity, exact rally boundaries and label-version disagreements remain material limits. This singles broadcast does not validate amateur or four-player doubles performance.

## What is actually present locally

Read-only inspection found eight dataset directories, 56 CSV/JSON data files and four reference DOCX files. `Part2/video_raw` currently contains only `.gitkeep`; there are no local media files in the inspected Part2 tree. A historical progress note says nine videos were downloaded there, so that statement describes a past state and must not be used to claim local media is currently available.

All eight primary `<match>.csv` files have this eight-column schema:

```text
start_time,end_time,win_point_player,win_reason,ball_types,lose_reason,roundscore_A,roundscore_B
```

| Primary match CSV | Parsed rows | Nonblank rows | First start → final end | Historical Drive basename |
|---|---:|---:|---|---|
| Test1_Full | 36 | 36 | `0:08` → `9:33` | `Test1_Full_rev.mp4` |
| Test2_Full | 75 | 75 | `00:02` → `16:16` | `Test2_Full_Rev.mp4` |
| Test3_Full | 22 | 22 | `0:05` → `4:39` | `Test3_Full_Rev.mp4` |
| Test4_Full | 45 | 45 | `00:11` → `11:05` | `Test4_Full_Rev.mp4` |
| Test6_Full | 42 | 42 | `0:04` → `9:36` | `Test6_Full.mp4` |
| Test7_Full | 31 | 31 | `6` → `357` | `Test7_Full.mp4` |
| Test9_Full | 88 | 78 | `0:04` → `18:24` | `test_9.mp4` |
| Test10_Full | 101 | 96 | `0:04` → `20:37` | `Test_10.mp4` |
| **Total** | **440** | **425** | 15 blank records must not count as labelled rallies | |

The manifest additionally lists `Test5_Full.mp4`, but Part2 has no corresponding Test5 annotation directory. Revision suffixes and the Test9/Test10 basename differences require explicit mapping; automatic basename equality would miss them. The table records annotation endpoints, not verified video durations for those other recordings.

## Label candidates versus generated outputs

| File family | Observed schema / provenance | Appropriate interpretation |
|---|---|---|
| `<match>.csv` | Eight columns above. Legacy evaluation documentation calls these hand-labelled rally annotations. No annotator, review date, adjudication, source hash, fps or source/proxy timeline ID is embedded. | Legacy rally-label candidates with unverified provenance and known conflicts. One `ball_types` entry per rally is not an exhaustive per-shot sequence. |
| `Test1_Full2.csv` | Frame/time fields plus winner/reason/type/score fields. Its boundaries differ from both the primary manual-looking seconds table and some generated rally boundaries. | Mixed/derived annotation candidate. Do not promote its finer numeric precision into independent frame-level truth without provenance. |
| `<match>_rally.csv`, `*_T.csv`, `*_T4.csv` | `Start_Frame,End_Frame,Start_Time_sec,End_Time_sec,Duration_sec,Start_Time,End_Time`. Legacy scripts explicitly use `_T.csv` as detected rallies; documentation describes rally segmentation output. | Generated rally proposals/variants. A `_Rev` or `_T4` filename alone does not prove human review. |
| `*_ball_filled.csv`, `*_Rev_ball_filled.csv` | `Frame,X,Y,Visibility`, with `Confidence` in six primary matches. Legacy README describes TrackNetV3 followed by interpolation. | Model observations plus filled/estimated trajectory samples. No per-row reviewed coordinate or independent visibility label is established. |
| `player_detections.csv` | `frame_no,player_1_x,player_1_y,player_1_conf,player_2_x,player_2_y,player_2_conf`. Reference notes describe YOLO person output and arbitrary position slots. | Predicted two-slot detections, not athlete identity labels or four-player identity truth. |
| `<match>_court.json` | One `frame_no`, dimensions, four corners and net coordinates. Test7 declares 1280×720 at frame 5362. | Calibration candidate for a specific processed view. Human or automatic origin and validity over camera cuts are not recorded in the JSON. |
| `win_predictions.csv` | Rally frame/time, winner/loser, reason, `reason_src`, fault side/source, CNN class/confidence/probabilities and running score. Test7 rows explicitly contain `ML_RF`, `ML_HN_I`, `RULE`. | Generated predictions. Comparing current output against these measures agreement with an earlier pipeline, not accuracy against independent labels. |

## Concrete problems in the selected pair

1. **The opening winner label is unresolved.** The current Part2 row for 6–15 seconds says `Player A` with score A:B `0:1`. The current legacy row for the same interval says `Player B` with the same score. This is a source disagreement, not a reason to choose either version silently. The earlier visual note supports Carolina Marín as the physical opening-rally winner from subsequent scoreboard evidence, but does not establish which annotation's A/B convention was intended.
2. **The recording is edited.** The earlier visual note reports score Tai 0 / Marín 1 at frames 510 and 900, followed by Tai 2 / Marín 5 at frame 1005 across a visible cut. Consecutive annotated rows therefore cannot be assumed to cover every point in the original match. Score jumps alone are not proof of an individual row's winner error.
3. **Time and geometry are different contracts.** The primary Test7 values are seconds, while other primary files use `MM:SS`. The generated Test7 rally table shows `199 / 30 = 6.633…` seconds and `454 / 30 = 15.133…`, but the primary row is the coarser 6–15 seconds. The legacy quick reference says preprocessing normalizes to 30 fps and 1280×720; the historical Test7 source is 1920×1080. Its court JSON is 1280×720. Coordinate scaling and frame mapping must be established before importing any generated geometry; current canonical proxy frames must not be assumed identical to original source observations merely because nominal fps agrees.
4. **There is no exhaustive event sequence.** The CSV contains rally boundaries, one winner/reason/type and two score columns. It has no per-contact frame/time, serve/hit sequence, athlete-specific hitter, independent shuttle visibility/position, four-player identities, occlusion labels, or negative/no-contact intervals. It cannot support contact precision/recall, frame-accurate shot timing, per-shot classification accuracy or four-player attribution accuracy without new review.
5. **Taxonomy is inconsistent.** Across the set, `ball_types` mixes families and variants (`Smash`, `Stick Smash`, `Jump Smash`, `Slice`, `Defensive Slice`, `Clear`, `Clear Shot`) and includes `Opponent Failed to Return` in Test3. Preserve raw labels. Any normalized taxonomy needs a documented mapping and ambiguity handling before scoring.
6. **Independence is unestablished.** `Model_Exploration_History.docx` and the legacy evaluation notes describe these eight matches being reused across several model/threshold experiments. No new frozen holdout or per-row review trail is identified. Published legacy metrics in those notes are historical claims, not fresh validation of the current application or evidence that this set is unseen.

## Provenance and license findings

There is no `README`, `LICENSE`, `LICENCE` or `COPYING` file inside Part2. Its `.gitattributes` only declares `dataset/** -text`. Text inspection of the four reference documents found descriptions of hand-labelled matches and a pipeline review workflow, but no dataset-specific license grant, named annotation protocol, per-row reviewer record or independent adjudication record. The source broadcast license and rights for derived annotations therefore remain undocumented in the inspected material. The user's authorization supports this diagnostic investigation; it does not establish a redistribution or training-data license.

Reference documents describe optional human correction saved separately from model output, but no associated reviewed `corrections.json` or review ledger exists in the inspected Part2 tree. The legacy winner predictor README defines its own `--player_a` as far and `--player_b` as near. That implementation convention does not resolve the conflicting primary annotation convention, especially after end changes/camera edits.

## Useful next step and reporting boundary

The integration owner can verify the existing Test7 video hash, or use the authorized single download for that exact file if needed. Preserve both annotation versions and start with the opening 0–40 seconds as a **diagnostic review**: verify video alignment, identify the visible athletes and the intended A/B convention, examine the 6–15 second rally and the post-rally score/cut. Record review decisions in a new versioned artifact with source hash, explicit timebase, reviewer identity/type, uncertainty and raw-row references. Do not overwrite Part2.

Before numerical accuracy reporting, freeze the mapping and matching protocol, distinguish unobservable/disputed rows, review all evaluated intervals, report unmatched predictions and annotations rather than dropping them silently, and disclose that this is edited broadcast singles from a previously used development set. A coarse rally-overlap diagnostic can proceed while these limits remain explicit. Shot/contact/identity metrics need additional independent labels.

## Inspection evidence and limits

Inspected read-only: all Part2 filenames and CSV/JSON headers, the eight primary CSV row inventories and hashes, the full Test7 primary CSV, samples of generated tables, Test7 court JSON, Test1 alternate table examples, current conflicting legacy Test7 rows/hash, the historical download manifest/video review/progress notes, legacy evaluation/README and merge/evaluation source. Relevant text was read in memory from the four DOCX archives; no rendered-page/layout claim is made. No videos were decoded, tests executed, SSH commands issued, downloads made, dependencies installed or Part2 files edited. The only authored file is this audit.

Key sources:

- `docs/testing/task2/drive-video-download-manifest.json`
- `docs/testing/task2/part2-video-review.md`
- `docs/testing/task2/progress-20261028.md`
- `Part2/dataset/Test7_Full/Test7_Full.csv`
- `legacy/pipeline/vjepa_setup/dataset/labels/Test7_Full.csv`
- `legacy/pipeline/docs/10_evaluation.md`
- `legacy/pipeline/win_predictor/README.md`
- `legacy/pipeline/analysis/evaluate_rallies_unified.py`
- `legacy/pipeline/vjepa_setup/merge_labels.py`
- `Part2/Refernce/Pipeline_Quick_Reference.docx`
- `Part2/Refernce/Model_Exploration_History.docx`
- `Part2/Refernce/Badminton_Rally_Analysis_Pipeline_Formatted.docx`
- `Part2/Refernce/Amateur_players_insights.docx`
