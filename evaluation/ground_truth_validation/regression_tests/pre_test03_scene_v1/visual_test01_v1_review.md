# Test 1 codec22 visual evidence review

The completed 44-frame rendering is intact. The reviewed source-confirmed edits at frames 7857 and 8106 now reset the content epoch and immediately admit both visible athletes. The stale empty-court box seen in the failed c7 control at 7857–59 is absent. This supports those specific repairs; it does not establish full pipeline acceptance or physical accuracy across Test 1.

This is an independent, read-only source diagnostic review. No inference, metric recomputation, physical ground truth creation, production edits, helper edits, annotation edits, or writes inside the completed render directory were performed. The outer orchestration and its semantic replay are separate from the already-completed fresh inference and rendering.

## Artifact and frame verification

[Verification receipt](visual_test01_v1.verification.json) independently rehashed all **574 output artifacts** and **613 input bindings**, including exact original source video, staged/cache evidence and execution metadata. It decoded all **132 retained original/current-proxy/baseline-proxy PNGs** and verified their recorded uncompressed BGR pixel hashes, shapes, rational timestamps and PTS×time-base agreement. The 44 requested frame IDs are unique; every frame directory, evidence record and both indexes are accounted for. Hash verification took 8.605 seconds. The source and proxies use the same zero-origin frame/30 time basis; source and compressed proxy pixels are not claimed to be identical.

Render completion SHA256: `02031725ca7706ab8453375a6c5c31c5332ca68bde2e46970a1678ba68430544`. Executed renderer SHA256: `27e9464a4e37131d3059867829eb10c759ca2ee14a3f1da04589e03af2876442`. Original Test1 source SHA256: `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`.

[Panel-review receipt](visual_test01_v1.review.json) lists the exact hashes of 26 visually inspected panels covering 15 distinct frames. All 44 frames received artifact/timing/raw-record accounting; the other 29 frames are **not** represented as physically adjudicated. The original completed [Markdown index](visual_test01_v1/index.md) and [HTML index](visual_test01_v1/index.html) retain all panels, request captions and raw predictions.

The actual current arm is commit `c585e3507a2fef9ff393a8cfbba575a979345f53`; baseline is the original Test1 improved_v1 full-neural run at `caa91761948d09f2cfe4937b0db743fff8643a12`. Each processed all 17,268 frames without cached perception. Their effective/source profile, manifest, canonical model pin values and RF-DETR/RTMPose/TrackNet artifact SHAs agree. Tracking/content implementations and cache schema intentionally differ; identical neural weights do not imply identical cadence, player population or derived events. Model pin semantic hashes and raw lock-file hashes are retained separately. Both arms report missing OSNet weights and an unavailable baseline ReID provider, so these numeric track IDs cannot establish reviewed athlete identities.

## Source-checked findings

| Frames / exact timeline | Visible source and prediction evidence | Interpretation and limit |
|---|---|---|
| 7856→7857; 261.866667→261.900000 s | Scoreboard changes from AN S.Y.18 / INTANON16 to20 /18 and both athletes abruptly relocate. Current content epoch3→4, detector runs, two boxes are detector-matched at7857 over the two visible athletes. Original baseline also resets epoch4 but returns no players at7857. | The edit is visibly supported; current player acquisition at the reset is repaired. The earlier c7 control failed to reset and carried the near-right old box onto empty court. That box is absent here. |
| 7858–7859; 261.933333–261.966667 s | Current epoch4 retains the two **new** post-edit boxes; `detector_matched=false`, no detector execution, no current pose/racket frames. Baseline still has no players. | These are carried boxes from7857, not fresh per-frame detector observations. Their placements follow the current visible athlete positions; this does not prove subpixel localization or continuity beyond the inspected frames. |
| 8105→8106; 270.166667→270.200000 s | Visible20:18→20:20 score change and abrupt relocation; current epoch4→5 and two fresh, detector-matched boxes with current pose/racket frame8106. Baseline also resets5 but has no players at8106. | Restored boundary plus immediate post-edit acquisition. The current raw racket ellipse near each head remains an estimate, not certified equipment or a verified strike. |
| 7806 /7812;260.200000 /260.400000 s | Near dark-shirt athlete has a fresh green admitted box. The white-shirt athlete walking behind the far court is represented by blue image context only. At7812 the original baseline additionally admits that far athlete with pose/racket estimates; current does not. | This is an explicit admission/authority difference, not a claim the far person is nonexistent or a false physical detection. Scene context can preserve evidence of image changes after court authority expires without silently granting athlete/identity authority. |
| 13153;438.433333 s | Both arms have identical raw player records, raw shuttle(472.380212,615.638298) and epoch9. The overlay puts the shuttle estimate near the near athlete's lower-left image region. | Inherited shuttle/generated-reference disagreement remains unresolved. One image with no reviewed physical localization cannot establish shuttle error, PR or continuity. Dense legacy-filled points are not physical truth. |
| 13467;448.900000 s | Source shows athletes overlapping near the left side of the net. Both arms have identical raw player records and epoch9; carried boxes overlap and pose joints are current-frame estimates. No raw shuttle observation. | The inherited extreme anonymous legacy player-point disagreement is not a new candidate player-box difference at this frame. Occlusion, slot association and generated point errors need reviewed labels; neither forced assignment distance nor this thumbnail supplies AP or IDF1. |
| 15801,15806,15808,15809,15843;526.700000–528.100000 s | Both arms have exactly identical raw player records, raw shuttle coordinates and epoch10 at each selected frame. Source shows a continuing rally; current pose is present, detector freshness varies as recorded. At15808 the large near-player raw racket ellipse is visibly displaced onto the lower body/leg region while the actual racket extends to image right. | The continuing raw classical racket failure remains visible in both arms. Rendering deliberately retains raw estimates; it does not prove those estimates were admitted as semantic contacts. Contact/stroke adjudication requires synchronized event evidence and reviewed impact/class labels. These controls do not support a claim that the racket detector is fixed. |

Selected panel links: [7857 current](visual_test01_v1/frame_0007857/current_source_overlay.png), [7857 baseline](visual_test01_v1/frame_0007857/baseline_source_overlay.png), [7858](visual_test01_v1/frame_0007858/current_source_overlay.png), [7859](visual_test01_v1/frame_0007859/current_source_overlay.png), [8106 current](visual_test01_v1/frame_0008106/current_source_overlay.png), [8106 baseline](visual_test01_v1/frame_0008106/baseline_source_overlay.png), [7812 current](visual_test01_v1/frame_0007812/current_source_overlay.png), [7812 baseline](visual_test01_v1/frame_0007812/baseline_source_overlay.png), [13153](visual_test01_v1/frame_0013153/current_source_overlay.png), [13467 source](visual_test01_v1/frame_0013467/source_original.png), [15808 source](visual_test01_v1/frame_0015808/source_original.png), [15808 current](visual_test01_v1/frame_0015808/current_source_overlay.png).

## Image context and ground-truth boundaries

The blue overlay explicitly says **IMAGE CONTEXT ONLY**; the footer says it is not athlete admission, identity or truth. All44 current evidence records independently confirm `athlete_or_GT_authority:false`; baseline legacy context stays unknown rather than being invented. Current raw `fg` preserves detached context key/box/freshness, while raw `p` separately records admitted players. In particular the far athlete at7806/7812 remains blue without a green current admitted-person box. At edit7857 both athletes acquire new boxes; their new context keys are distinct from the witnesses used to decide the7856→7857 transition. The decision preserves supporting witness keys and full raw-layout indices without this review recomputing them.

The source expectation in this report is a bounded visual observation, not new reviewed dataset labels. No independent exhaustive boxes, keypoints, racket/impact labels, athlete roster identities or shuttle coordinates were created. AP/mAP, HOTA/IDF1, PCK/OKS and physical racket/contact/localization accuracy remain unavailable from these panels alone. A successful renderer or matching raw records is not an accuracy result.

All six interval metric families must be read in the completed evaluator output, separately from this review. Unchanged TP/FP/FN can coexist with changed endpoints and IoU. The aggregate anonymous player-point disagreement must also be decomposed over common/new/removed populations; a changed all-row mean is not proof of no regression or physical improvement. This report does not approve the candidate globally and does not conflate original full-neural baseline events with a later cached-semantic control.

## All44-frame accounting

Each row links its immutable evidence record. Counts below are admitted player predictions, not a count of physical people. Fresh counts mean `dm=true`; blue contexts are a separate current-image channel. Only the marked15 frames were visually inspected in this review.

|Frame|Time(s)|Current players/fresh|Baseline players/fresh|Current blue contexts|Visual inspection|Evidence|
|---:|---:|---:|---:|---:|---|---|
|0|0.000000|2/2|0/0|2|artifact/raw only|[record](visual_test01_v1/frame_0000000/evidence.json)|
|1|0.033333|2/0|0/0|2|artifact/raw only|[record](visual_test01_v1/frame_0000001/evidence.json)|
|6|0.200000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0000006/evidence.json)|
|59|1.966667|2/0|2/0|2|artifact/raw only|[record](visual_test01_v1/frame_0000059/evidence.json)|
|60|2.000000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0000060/evidence.json)|
|243|8.100000|2/0|2/0|2|artifact/raw only|[record](visual_test01_v1/frame_0000243/evidence.json)|
|300|10.000000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0000300/evidence.json)|
|6152|205.066667|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0006152/evidence.json)|
|7414|247.133333|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0007414/evidence.json)|
|7730|257.666667|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0007730/evidence.json)|
|7770|259.000000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0007770/evidence.json)|
|7800|260.000000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0007800/evidence.json)|
|7801|260.033333|1/0|2/0|2|artifact/raw only|[record](visual_test01_v1/frame_0007801/evidence.json)|
|7806|260.200000|1/1|1/1|2|yes|[record](visual_test01_v1/frame_0007806/evidence.json)|
|7812|260.400000|1/1|2/2|2|yes|[record](visual_test01_v1/frame_0007812/evidence.json)|
|7854|261.800000|1/1|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0007854/evidence.json)|
|7856|261.866667|1/0|2/0|2|yes|[record](visual_test01_v1/frame_0007856/evidence.json)|
|7857|261.900000|2/2|0/0|2|yes|[record](visual_test01_v1/frame_0007857/evidence.json)|
|7858|261.933333|2/0|0/0|2|yes|[record](visual_test01_v1/frame_0007858/evidence.json)|
|7859|261.966667|2/0|0/0|2|yes|[record](visual_test01_v1/frame_0007859/evidence.json)|
|7860|262.000000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0007860/evidence.json)|
|7975|265.833333|2/0|2/0|2|artifact/raw only|[record](visual_test01_v1/frame_0007975/evidence.json)|
|8049|268.300000|2/0|2/0|3|artifact/raw only|[record](visual_test01_v1/frame_0008049/evidence.json)|
|8056|268.533333|2/2|2/2|3|artifact/raw only|[record](visual_test01_v1/frame_0008056/evidence.json)|
|8087|269.566667|1/0|2/0|2|artifact/raw only|[record](visual_test01_v1/frame_0008087/evidence.json)|
|8105|270.166667|1/0|2/0|2|yes|[record](visual_test01_v1/frame_0008105/evidence.json)|
|8106|270.200000|2/2|0/0|2|yes|[record](visual_test01_v1/frame_0008106/evidence.json)|
|8108|270.266667|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0008108/evidence.json)|
|8111|270.366667|2/0|2/0|2|artifact/raw only|[record](visual_test01_v1/frame_0008111/evidence.json)|
|8132|271.066667|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0008132/evidence.json)|
|8172|272.400000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0008172/evidence.json)|
|8222|274.066667|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0008222/evidence.json)|
|8380|279.333333|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0008380/evidence.json)|
|8634|287.800000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0008634/evidence.json)|
|9000|300.000000|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0009000/evidence.json)|
|12874|429.133333|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0012874/evidence.json)|
|13153|438.433333|2/0|2/0|2|yes|[record](visual_test01_v1/frame_0013153/evidence.json)|
|13467|448.900000|2/0|2/0|2|yes|[record](visual_test01_v1/frame_0013467/evidence.json)|
|14626|487.533333|2/2|2/2|2|artifact/raw only|[record](visual_test01_v1/frame_0014626/evidence.json)|
|15801|526.700000|2/0|2/0|2|yes|[record](visual_test01_v1/frame_0015801/evidence.json)|
|15806|526.866667|2/2|2/2|2|yes|[record](visual_test01_v1/frame_0015806/evidence.json)|
|15808|526.933333|2/2|2/2|2|yes|[record](visual_test01_v1/frame_0015808/evidence.json)|
|15809|526.966667|2/0|2/0|2|yes|[record](visual_test01_v1/frame_0015809/evidence.json)|
|15843|528.100000|2/0|2/0|2|yes|[record](visual_test01_v1/frame_0015843/evidence.json)|

The verification/report receipts are siblings of the completed render. Existing failed c7 visuals and historical reports were not edited.
