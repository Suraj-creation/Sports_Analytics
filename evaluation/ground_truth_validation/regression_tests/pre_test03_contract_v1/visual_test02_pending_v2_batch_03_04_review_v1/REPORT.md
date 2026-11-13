# Independent Test2 source review: pending batches03/04

The two remaining lost baseline cut controls, **22416 and23279**, are actual same-camera edited jumps in the source. The current native run misses both epoch barriers. At22416it still returns two fresh athlete boxes; at23279it carries the old far-player box over empty court for one sampled frame. These are distinct consequences of the same missing temporal boundary.

All194requested frames in the closed03/04packages were reviewed across39aspect-preserving source/baseline/current sheets, with enlarged source and current panels for significant concerns. Physical ground truth remains **null**. Selected source checks do not establish exhaustive scene precision/recall, player AP, contact accuracy or stroke-class accuracy.

## Provenance and complete review coverage

Current producer is2418ab8cbe4cca74dd16b722b9727ffdc950294a; baseline is preserved Test2improved_v1. SourceSHA is4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a. Rehashed all2372rendered artifacts and2030recorded input bindings across both closed packages, plus582source/proxy pixel receipts (194original-source,194baseline-proxy and194current-proxy). There are1011unique recorded input paths. Visually reviewed582source/baseline/current panels; the582pixel receipts refer to the original source and proxy input PNGs, distinct from the overlay panels. No new video decode or inference occurred. All package provenance remains in [verification.json](verification.json).

[Machine readouts](machine_readouts.json), [freshness/view/calibration details](extended_freshness_readout.json), and [structured194-frame review](review.json) preserve the exact scope. Source1920×1080 and1280×890overlay-plus-text images use proportional scaling/letterboxing. No source image was stretched to overlay-panel aspect.

## Confirmed lost edits and genuine stale authority

At22415→22416both athletes abruptly relocate; current-game broadcast top/bottom8:11becomes9:12. Baseline epoch25→26withbarrier; current epoch34stays34. Current22416has two fresh admitted persons and three foreground regions. The extra old region is **image-only context**, not a third admitted person. Current22417carries the newly detected bodies, but lack of epoch change can still connect incompatible temporal evidence.

At23278→23279the athletes move from near-left walking/pickup positions to active near/far central positions in one source step. Display9:15is unchanged; unchanged scores do not establish camera continuity. Baseline epoch27→28clears people. Current epoch35stays35and keeps two admitted carried boxes. The old far-red region covers empty left/net area while the actual red athlete is far-centre. This produces159.167893pxnew-only disagreement with the legacy point reference and is independently visible, not merely a generated-score anomaly. At23280current detector observations replace the far episode and cover both athletes, while old foreground context remains separate.

[Source/cached packet lineage and overlap contract](../../../component_evaluations/pre_test03_scene_overlap_review_v1/REPORT.md) separately binds2928/11082. All four lost baseline cut controls have now been independently source-supported as edits. This report does not claim that these are all missed edits in the whole video, or that a proposed mask-policy experiment has fixed them.

## Global point outliers: reference agreement versus visible error

- **14453:** both arms carry the same empty near-left box while the actual near-red athlete is centre-right. The256.206844pxgenerated-reference disagreement is identical before/after and visually reflects an inherited localisation failure. Both arms report main/VALID, doFalse and fresh pose inference on the old carried crop; finite pose points in empty court do not prove a person. Current14454immediately births the near athlete; baseline still has only the far athlete.
- **23279:** new-only159.167893pxfar-region disagreement is the real stale-box consequence described above; never describe it as an extra player.
- **13436:** fresh box/reference disagreement57.522973pxis exactly unchanged across arms. Near/far athletes overlap in the image and the far feet are occluded. The box covers the visible athlete; this source alone cannot decide which generated foot coordinate is correct. This remains generated-reference agreement, not independently labelled localisation error.
- **13556/13558/16495:** newly scored fresh observations visibly cover the broad athlete regions, including extreme lunge/body shape. Addition to the fresh-scored population is not itself reduced accuracy or a physical TP claim. Raw racket contours over heads/branding/body remain unverified hypotheses.
- **15623:** current has one carried offset region and no near-athlete region while source returns from a dissolve to wide play. Calibration is REACQUIRING in both arms, and original has no people. This retained perception row must not be promoted to accepted geometry or an admitted active-play truth. Current fresh bodies reappear at15625.

## Visible play with sparse current cadence

At selected25689–25736frames, source shows active near-blue/far-red exchange postures, while current uses pose stride6and usually doFalse/carried boxes with no current pose. The original uses pose stride1and fresh detector matches on even frames. Both arms are main/VALID. Current carried near box lags at25719/20/21/32/36;25720/21were selected by the independent maximum common-pair point-error increase. By25743current pose stride1resumes, and25770has fresh bodies.

These are actual scheduling/coverage differences, not evidence that a neural model executed and failed on those same frames, and not excluded calibration. The root cause of the in-play/idle scheduling difference is not established by isolated source images; it needs the existing actual activity/FSM/chunk-hint trace. No profile or threshold was changed here. This limitation must remain visible when reporting contact/class changes.

## Three same-anchor class changes

| Frame | Before → current predicted class | Current episode reason | Flight time before → current, seconds |
|---|---|---|---|
| 22846 | drive → unknown | nearest_proximity | 0.7 → 0.7 |
| 25736 | drop → unknown | player_not_detector_matched | 0.5666666666666667 → 0.23333333333333334 |
| 26293 | unknown → net_shot | nearest_proximity | 0.8 → 0.8 |

At22846source shows a near-blue lunge/reach; despite fresh body observations, the current class feature set lacks an image-speed value and abstains. At25736visible near-blue overhead movement coincides with carried/no-pose current sampling, unresolved fresh target and changed next-contact interval. At26293far-red net-side action has current fresh episode availability versus old carry. These observations explain evidence availability differences; they do not certify drive/drop/net_shot labels. No shot-class ground truth is supplied by these sampled source postures, and no class TP/FP is invented. Exact event fields are linked in [structured review](review.json).

Unpaired contact/stroke anchors and anonymous actor-region changes are retained with their request reasons in the194-frame register. A visible swing posture cannot settle impact timing, actor identity or class. Phase/view transitions and partially visible off-court athletes are explicitly retained as diagnostic limitations.

## Complete page register

Every frame below was inspected in source, baseline and current columns. Notes describe sampled visual context, not physical labels or full-frame trajectory review. Adjacent source frames are only claimed where present; distant page rows are not treated as consecutive movement.

| Review page | Exact source frames | Source and output observations |
|---|---|---|
| [page01](page_01.png) | 13080, 13081, 13217, 13218, 13223 | 13080→13081 source jump; current immediate athlete births versus baseline empty at13081. Later near-blue overhead motion has carried-box context, without contact/class adjudication. |
| [page02](page_02.png) | 13436, 13451, 13452, 13457, 13458 | Close athlete image overlap at13436; side walking13451 jumps to central positions13452. Current fresh bodies restore coverage; old rectangles remaining cyan are scene context only. |
| [page03](page_03.png) | 13462, 13556, 13558, 13790, 13791 | Current fresh bodies at13556/58 visually cover athletes; far head/branding-like raw racket contours remain estimates.13790→13791 source reset to central play, current fresh bodies versus baseline carry. |
| [page04](page_04.png) | 13793, 14106, 14107, 14195, 14196 | Far-red athlete outside upper-right at14106 returns central at14107. Current immediate fresh births; subsequent near/far image overlap limits precise foot/contact assessment. |
| [page05](page_05.png) | 14201, 14293, 14294, 14295, 14369 | 14293→14294 genuine source jump with current fresh people versus baseline none.14369far-red extended posture carries forward; no class/contact truth. |
| [page06](page_06.png) | 14370, 14375, 14453, 14454, 14455 | 14370/75 fresh bodies generally cover visible active movement.14453has an empty carried near-left region in both arms while actual near-red is centre-right; current reacquires near-red at14454, baseline does not yet. |
| [page07](page_07.png) | 14889, 14890, 14891, 15035, 15036 | Near-red outside bottom edge at14889 returns central at14890edit; current two fresh bodies, baseline empty.15035/36near-red/far-blue active action; no impact label. |
| [page08](page_08.png) | 15041, 15415, 15416, 15417, 15621 | 15415partially visible near-red at lower-left has no admitted body; scene context alone persists.15416/17current bodies restored at source jump, baseline none.15621both visible bodies admitted. |
| [page09](page_09.png) | 15622, 15623, 15625, 15762, 15904 | 15622broadcast dissolve/view transition;15623current carried far-region offset and missing near athlete while calibration REACQUIRING.15625current fresh bodies return.15762lunge/15904opposite-side lunge source motion visible, no exact impact assertion. |
| [page10](page_10.png) | 15914, 15932, 15966, 16026, 16090 | Active near-red/far-blue stroke-like postures15914/32/66/16026; raw racket estimates remain unverified.16090closeup excluded from body analytics. |
| [page11](page_11.png) | 16091, 16211, 16212, 16217, 16495 | 16091wide-view reacquisition returns two current bodies while baseline empty.16211/12/17and16495fast lateral play has carry versus fresh cadence differences; no physical class truth. |
| [page12](page_12.png) | 16556, 16557, 17241, 17242, 17243 | 16556closeup excluded;16557return to wide view supplies current bodies versus baseline empty.17241→17242source jump and current fresh bodies;17243carry within new source scene. |
| [page13](page_13.png) | 17420, 17421, 17507, 17508, 17513 | 17420dissolve/excluded transition then17421wide source current reacquisition.17507/08/13far-blue lateral action has varying box freshness without physical contact adjudication. |
| [page14](page_14.png) | 17662, 17663, 17991, 17992, 17993 | 17662→17663same-camera source jump;17991offcourt near-red relocates central at17992. Current fresh bodies at resets versus baseline empty. |
| [page15](page_15.png) | 18369, 18370, 18371, 18992, 18993 | 18369far-blue outside right returns centre at18370edit; current fresh bodies while baseline absent.18992offscreen/partially visible near-red,18993source jump current bodies versus baseline old far box. |
| [page16](page_16.png) | 18995, 19109, 19110, 19115, 19207 | 18995remaining cyan old rectangles are scene-only.19109/10/15and19207visible continuous active near/far positions; raw racket/body cues do not label impacts. |
| [page17](page_17.png) | 19208, 19537, 19538, 19539, 20060 | 19537near-red outside left,19538/39source jump with current bodies.20060dissolve/close view is excluded; no treating detected absence there as player FN. |
| [page18](page_18.png) | 20061, 20909, 20910, 20911, 21071 | 20061return to wide source view supplies current bodies.20909→20910source jump;21071walking near-red and far-blue body carry. No match intent inferred. |
| [page19](page_19.png) | 21072, 21077, 21737, 21738, 21743 | 21072/77fresh/carry cadence differs across arms.21737far-red outside left not admitted,21738current retains near-blue while original drops both; scene context is not participant authority. |
| [page20](page_20.png) | 21791, 21792, 21797, 21821, 21822 | 21791/92/97and21821/22show slow preparation/positioning with carried/fresh pose variations. No contact truth from static readiness posture. |
| [page21](page_21.png) | 21827, 22415, 22416, 22417, 22608 | 22415→22416confirmed edited source jump, display8:11→9:12, baseline cut versus current no epoch change. Current fresh bodies are correct broad regions while old rectangles remain only foreground.22608active pair. |
| [page22](page_22.png) | 22617, 22634, 22654, 22656, 22724 | 22617/34/54similar preparation then22724active exchange; current/old bodies broadly correspond at these samples. No proposed threshold or physical labels. |
| [page23](page_23.png) | 22760, 22846, 22875, 22945, 22946 | 22760/22846visible athletic action;22846class change remains unlabelled.22875carry,22945walking,22946source reset with current fresh bodies versus baseline none. |
| [page24](page_24.png) | 22947, 23278, 23279, 23280, 23289 | 23278→23279source edited jump despite unchanged9:15display. Current admits two carried old boxes; old far box covers empty left area and misses relocated red athlete. Fresh current far birth at23280;23389carry inside new scene. |
| [page25](page_25.png) | 23305, 23394, 23407, 23408, 23486 | 23305/394/407/408/486show active exchanges; carry can lag during lunge and fresh observations recover body shape. Exact contact and stroke classes remain unsupported. |
| [page26](page_26.png) | 23525, 23526, 23629, 23696, 23697 | 23525/26near-blue overhead posture,23629near-blue bend/lunge;23696→23697source reset from edge positions to central play with current two fresh bodies. |
| [page27](page_27.png) | 23999, 24000, 24001, 24099, 24100 | 23999/24000/24001continuous visible action with freshness changes;24099dissolve excluded and24100current immediate wide-view births. |
| [page28](page_28.png) | 24101, 24390, 24391, 24779, 24780 | 24101carry in wide view;24390→24391source position/score jump, current fresh bodies versus baseline none.24779/80athletic postures cannot verify hit timing. |
| [page29](page_29.png) | 24781, 25207, 25208, 25209, 25317 | 24781body/pose cadence variation;25207→25208source reset with current immediate births.25317near-blue overhead preparation, unverified contact. |
| [page30](page_30.png) | 25318, 25319, 25523, 25529, 25689 | 25318/19carry/fresh variation;25523/29baseline stale left boxes while current bodies correspond to active central source positions.25689visible active source but current sparse cadence/no pose versus baseline active cadence. |
| [page31](page_31.png) | 25690, 25691, 25695, 25696, 25697 | 25690/91/95/96/97show active near-blue/far-red source; current holds boxes and lacks current pose sampling under ps6 while baseline ps1. This is sparse scheduling, not geometry exclusion. |
| [page32](page_32.png) | 25713, 25714, 25715, 25719, 25720 | 25713/14/15/19/20near-blue overhead/lateral movement continues; current carried box trails body versus original fresh/posed observations. No class confirmation. |
| [page33](page_33.png) | 25721, 25725, 25726, 25727, 25731 | 25721/25/26/27/31current carried bodies and absent current pose continue during visible action. Retain scheduling/coverage limitation without inventing detector outputs. |
| [page34](page_34.png) | 25732, 25733, 25736, 25743, 25770 | 25732/33/36carried near-blue box lag visible;25736class drop→unknown has unresolved fresh-player evidence. By25743current pose stride1 resumes and25770fresh bodies appear. |
| [page35](page_35.png) | 25898, 25936, 26016, 26057, 26058 | 25898/25936active pairs;26016walking with unverified raw racket contour over body.26057→26058source reset with current fresh athletes versus baseline absent. |
| [page36](page_36.png) | 26059, 26293, 26502, 26503, 26716 | 26059new-scene carry;26293far-red net-side action cannot certify net_shot class.26502→26503offcourt right-to-centre source reset with current fresh bodies.26716ordinary active pair. |
| [page37](page_37.png) | 26717, 27663, 27664, 27665, 27875 | 26717carry/fresh contrast;27663→27664source reset with current bodies, baseline none.27875near-blue lunge, exact shuttle contact unknown. |
| [page38](page_38.png) | 27876, 27881, 27954, 27955, 28706 | 27876/81source near-blue movement; baseline temporarily lacks near-body coverage while current has it.27954closeup excluded;27955wide current births.28706active source pair. |
| [page39](page_39.png) | 28707, 28977, 28978, 28979 | 28706→28707source edit with current immediate births;28977→28978clear edge-to-centre source/score jump, current bodies while baseline absent;28979carry consistent with newly acquired scene. |

## Acceptance boundary

This review preserves successful immediate birth controls after known edits and wide-view returns, confirms lost scene barriers and visible stale authority, and identifies genuine inherited and scheduling limitations. It does not equate lower model-person count with missed athletes, image-only foreground with admitted people, unchanged source score with no edit, or class availability with accuracy. The separately sealed five-interval official-region lineage and batch01/02 review cover earlier frames; this report does not silently extend194frames into664independently reviewed frames. No production, annotation, evaluator, profile, model or previous report was modified.
