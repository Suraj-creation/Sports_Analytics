# Test 2 source-bound annotation and coordinate review

This is an **agent diagnostic review**, not newly adjudicated human ground truth, exhaustive physical accuracy evaluation or certification of any winner/contact/landing. Original video and Part2 annotations were read only. The inspected images are exact selected source frames decoded by the root orchestrator's [extractor](extract_annotation_panels.py); the review below independently inspected the declared images using the image-view tool.

## Source, frame and coordinate binding

Source: `test_02/inputs/Test2_Full_Rev.mp4`, SHA256 **4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a**, downloaded byte count **2,453,914,397**. The live video download is separate from the seven preserved local Part2 annotation originals; their hashes are recorded in [annotation_inventory.json](../../annotations/annotation_inventory.json).

The extractor decoded sequentially with PyAV, two decoder threads, source **1920×1080** BGR pixels, then resized to **1280×720** using OpenCV `INTER_AREA`. Original legacy coordinates were drawn unchanged in that analysis canvas. No temporal offset, fitted affine transform or annotation-dependent coordinate optimization was applied. [frame_metadata.json](frame_metadata.json) records source pixel hashes, source PTS/time base, canvas shapes, exact original annotation rows and rendered overlay hashes. Its 18 captured frames have time base **1/15360** and PTS **512 × frame index**, so every sampled time equals frame/30 exactly. A complete source/proxy PTS audit remains the run orchestrator's responsibility.

Yellow denotes legacy player slot 1; cyan slot 2; red denotes a legacy trajectory entry with Visibility=1; green the supplied manual court corners; magenta the net points/cable. Court geometry is declared only for frame 300 and is explicitly labelled as a static reference at other frames. Missing/outside image points are not invented or clipped into view. In particular an off-canvas red circle is naturally absent from the rendered image; that absence is not a visibility-zero annotation.

## Independently inspected evidence and findings

### Court frame 300 supports a singles-court interpretation

At [frame 300 / 10.000 s](frame_00300_legacy_overlay.png), TL(448,305), TR(829,304), BR(933,659), BL(347,659) follow the **inner singles sidelines and back baselines** to qualitative precision. The visible outer doubles boundaries extend farther left/right, especially at the near baseline. The supplied cable endpoints around y310 and post bases around y433 are visually plausible in the same canvas.

This warrants the explicit diagnostic interpretation `outer_singles_floor_corners` for comparison with the current pipeline's singles geometry at the declared frame. It does not establish millimetre/pixel click accuracy or validity through every camera cut, and it must not be compared directly to a doubles-court polygon without matching the rectangle semantics. The court homography is a floor transformation, not an airborne shuttle measurement.

![Declared calibration frame](frame_00300_legacy_overlay.png)

### Player slots swap while the visible people remain in place

[Frame 4 / 0.133333 s](frame_00004_legacy_overlay.png) places yellow slot1 near the **far blue** athlete's feet and cyan slot2 near the **near red** athlete. At [frame 6 / 0.200000 s](frame_00006_legacy_overlay.png), the athletes remain in those court areas, but yellow slot1 is now near red and cyan slot2 far blue. The points approximately follow detector box bottom centers, not annotated joint locations. A slot index therefore cannot be used as a persistent player ID or silently mapped to symbolic Player A/B.

The content agrees with the producer's detection-order assignment and the independently counted 2,407 adjacent relative-Y reversals. That count describes the supplied legacy slots; it is not an ID-switch metric for the current tracker. Point matching for diagnostic distances must be anonymous within each frame.

### The match shows a change of ends; fixed far/near identities are invalid

[Frame 53 / 1.766667 s](frame_00053_legacy_overlay.png) displays the broadcast introduction text **Viktor AXELSEN** above and **Anders ANTONSEN** below. The near red jersey also displays ANTONSEN/DENMARK text. This is direct on-screen text evidence, not face-based identity recognition. Frame 300 shows blue far/red near. At [frame 11346 / 378.200 s](frame_11346_source_resized.png), the blue athlete is **near** and red athlete **far**; the blue jersey's back bears AXELSEN/DENMARK text. Later [frame 16246 / 541.533333 s](frame_16246_legacy_overlay.png) shows blue far/red near again, and [frame 22924 / 764.133333 s](frame_22924_source_resized.png) blue near/red far.

Thus court side is not a permanent named-athlete identity even within this supplied clip. The legacy predictor's default A=far/B=near convention cannot be promoted into a full-video human-label identity mapping. Any accepted current-pipeline outcome must preserve roster/team versus side, source-dependent identity evidence, changes of ends, and unknowns. These samples identify an evaluation requirement; they do not prove a particular current-pipeline bug without its synchronized output.

### Scoreboard columns grow across games and must not become one continuous point count

The following literal score texts were readable in inspected resized source images:

| Frame / seconds | Top broadcast row | Bottom broadcast row | Observation |
|---|---|---|---|
| 1594 / 53.133333 | AXELSEN **1** | ANTONSEN **3** | Single numeric column |
| 7703 / 256.766667 | AXELSEN **14** | ANTONSEN **17** | Single numeric column |
| 11346 / 378.200000 | AXELSEN **16, 5** | ANTONSEN **21, 1** | Two displayed game-score columns |
| 16246 / 541.533333 | AXELSEN **16, 21, 2** | ANTONSEN **21, 5, 2** | Three displayed game-score columns |
| 22924 / 764.133333 | AXELSEN **16, 21, 9** | ANTONSEN **21, 5, 12** | Earlier columns remain fixed in this later sample |
| 27325 / 910.833333 | AXELSEN **16, 21, 16** | ANTONSEN **21, 5, 16** | Rightmost numbers have changed |
| 27349 / 911.633333 | AXELSEN **16, 21, 16** | ANTONSEN **21, 5, 16** | Same visible numbers as previous sampled frame |

These samples support a **rightmost current-game column** interpretation, with previous-game values retained to its left, and are consistent with the primary table's reset candidates at rows27 and45. They do not certify every intermediate update, the precise reset frames, whether a primary row is pre- or post-rally, or an A/B identity mapping. At frame1594, within coarse row4's 38–59 s interval, the display reads 1–3 while the row's terminal candidate is 2–3; comparing an arbitrary in-rally frame with an assumed terminal label would create an invalid error claim. Review continuous event/score timing before adjudication.

The supplied generated `win_predictions.csv` ends at 29–44 because its producer accumulates predicted winners; this is not a literal broadcast match score. Do not diagnose all 26 nonunit primary score changes as annotation errors or pipeline errors. Game segmentation, omitted points, identity, column selection and row conventions must be distinguished first.

### Shuttle point semantics are the analysis-image canvas; filled values can lie outside it

At [frame53](frame_00053_legacy_overlay.png) the red trajectory entry is drawn near the far athlete's racket/hand region; at [frame95 / 3.166667 s](frame_00095_legacy_overlay.png) it is drawn near the near athlete's raised racket region. These samples, the court/player alignment and the producer's source-coordinate export support `analysis_image_xy` for **diagnostic disagreement** after resizing the 1920×1080 source to 1280×720. They do not certify exact shuttle centers or contact times. At frame300 the red point is high over the advertising area; a rendered prediction is not proof of a physical shuttle.

At [frame1594](frame_01594_legacy_overlay.png), the actual image canvas remains 1280×720 while the supplied trajectory is `(544,737), Visibility=1, Confidence=0.7387`. At [frame16246](frame_16246_legacy_overlay.png), it is `(736,729), Visibility=1, Confidence=0.4094`. Both values lie below the analysis image and cannot be plotted as in-canvas physical points. Metadata preserves these raw values; no rescue clipping or rescaling was performed. The independently inventoried spans are frames1594–1635 and16246–16253, 50 entries total; the largest cited example is frame1614 `(551,929)`, which was **not separately visually reviewed** here.

The visual/canvas evidence rejects treating those rows as verified visible in-image shuttle coordinates. It does not identify the exact legacy cause—interpolation overshoot, coordinate corruption or another generated-estimate failure—without tracing its historical producer inputs. There is no evidence here for globally rescaling all legacy coordinates to make only these outliers fit; that would disrupt otherwise plausible court/player/trajectory overlays. Compare valid-canvas and invalid-canvas disagreement populations separately and retain every original row.

## Reviewed frame list and reproducibility certificate

The independent image review inspected overlays **4,6,53,95,300,1594,16246** and raw resized images **7703,11346,22924,27325,27349**. Other extraction samples are available but are not claimed as independently visually reviewed by this agent. Exact source metadata for each is retained in the extractor manifest.

[diagnostic_coordinate_binding.json](diagnostic_coordinate_binding.json) follows the Test1 component evaluator's certificate contract, agreed with the Test2 evaluator agent. It records source/reference hashes, frame/shape/time metadata and hashes of the actual inspected images. It declares **agent diagnostic** coordinate semantics only, with `independent_physical_accuracy=false` and no new named-athlete GT. Its purpose is to enable honestly labelled source-bound generated-output disagreement metrics while preventing silent mismatches. It cannot supply missing boxes, joints, physical contacts, exhaustive negatives, persistent identities or human-reviewed winners.

Original annotation hashes must still be verified after the run and after downloaded-video cleanup. The certificate retains the source identity and review evidence even when the user's downloaded Test2 video is eventually removed after all deliverables are verified.
