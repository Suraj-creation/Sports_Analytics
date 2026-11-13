# Independent visual review — Test 1 fresh 2418ab8 run

The closed 88-frame evidence set supports the documented restoration of the seven historical coverage-loss intervals and preservation of all 13 recorded edit barriers. The reviewed point-change examples show the intended athletes, without an additional gross wrong-person or empty-court-box regression. **This is a diagnostic source review, not independent player/contact/classification accuracy validation or final pipeline acceptance.** Known carry lag, suspicious shuttle localization and uncertain contact/class/identity hypotheses remain.

The executed candidate is **2418ab8cbe4cca74dd16b722b9727ffdc950294a**. The [original completed render](../visual_test01_v4/completion.json) and all its files remain unchanged. This review writes only this new sibling directory, runs no inference, changes no pipeline/model/config/annotation/evaluation method, and accesses no Test 3 data.

## Artifact verification and review scope

[verification.json](verification.json) independently verifies **1,094 output hashes**, **613 input hashes and declared byte counts**, the executed renderer hash and the local Markdown index links. For all **88 frames**, decoded retained PNG pixels and shapes match their original-source and both arm proxy receipts: **264 pixel bindings**. This checks preserved render pixels against receipts; it is not another video inference or a new original-video decode.

All 88 source/current/baseline views were inspected using **44 derived aspect-correct viewing sheets**, including all seven interval before/start/end groups, every edit's adjacent frame pair, all six additional contact anchors, all three changed-class anchors, all five anonymous actor-change anchors and the selected outliers. [sheet_manifest_aspect_v2.json](sheet_manifest_aspect_v2.json) records every sheet, source frame and hash. The initial sheet attempt is preserved separately in `sheets/`; it resized the renderer's 170-pixel footer with the image, compressing vertical aspect. The reviewed `sheets_aspect_v2/` uses only the exact 1280×720 image area before resizing to640×360 and supplies its own diagnostic caption. Neither attempt modifies source images or overlays. Full-resolution originals remain available in [the render index](../visual_test01_v4/index.md).

The left sheet column is the original source resized by the completed renderer. The middle is current raw-perception overlay. The right is the **original full-neural raw baseline**, whose historical semantic output had446contacts. Semantic counts/differences below use the **later preserved dacc05e cached-perception control with445contacts**, as recorded by [event_differences.json](../test01_independent_v4/event_differences.json). The two baselines share source but must not be conflated. Neither baseline is sporting ground truth.

Green/orange person boxes retain fresh-versus-carried provenance; pose joints, racket ellipses and shuttle positions are model outputs. Blue image-context rectangles have **no participant, named-identity, current-contact, point or physical-truth authority**. An empty or overlapping blue region is not a newly admitted athlete. Review does not turn pose/racket estimates into independent observations.

## Restored coverage across all seven intervals

| Interval | Visual findings in before/start/end frames | Evidence |
|---|---|---|
| 753–800 | Near dark-clad athlete remains boxed while standing/walking beyond the near-left court edge. Far athlete remains separate. | [752/753/800](sheets_aspect_v2/coverage_01.png) |
| 3413–3449 | Near athlete at the right/bottom court edge remains present; no substitution by staff. | [3412/3413/3449](sheets_aspect_v2/coverage_02.png) |
| 6365–6381 | White-clad athlete outside the far-right court/net area remains boxed; central dark-clad athlete remains separate. | [6364/6365/6381](sheets_aspect_v2/coverage_03.png) |
| 7801–7805 | Far white-clad athlete beyond the far baseline remains represented by carried estimates. | [7800/7801/7805](sheets_aspect_v2/coverage_04.png) |
| 7812–7856 | Both visible athletes remain represented during the pause, including the far athlete beyond the baseline. | [7811/7812/7856](sheets_aspect_v2/coverage_05.png) |
| 8087–8105 | Near dark-clad athlete at/beyond the near-right edge remains represented. | [8086/8087/8105](sheets_aspect_v2/coverage_06.png) |
| 14103–14113 | Departing dark-clad athlete near the right sideline/umpire remains represented separately from the white-clad athlete. | [14102/14103/14113](sheets_aspect_v2/coverage_07.png) |

These source examples agree with the component review's [all182 row comparison](../test01_independent_v4/all_182_coverage_review.json): all182saved model boxes match exactly, with72fresh and110carried matches. The targets are historical model boxes. The source review supports intended population restoration but creates no exhaustive player boxes, AP, physical recall or identity metric. Carried estimates do not become fresh detections because their source athlete is visible.

## All 13 edit barriers

The source pairs show abrupt athlete position/layout changes that support an agent diagnostic interpretation of edited footage. Scoreboard changes are corroborating visible text only, not the sole basis for this finding or accepted scoring increments. There is no new human scene-ground-truth set. The native component review records the same13barrier frames as the original and prior candidate, with no additions/losses.

| Boundary | Source observation and current overlay | Evidence |
|---:|---|---|
| 2195 | Near athlete moves from far left/outside to central ready position; current fresh boxes reacquire both. | [2194→2195](sheets_aspect_v2/cut_02195.png) |
| 4837 | Athletes change from walking/turning positions to ready exchange positions abruptly. | [4836→4837](sheets_aspect_v2/cut_04837.png) |
| 7503 | Near-left athlete and far athlete abruptly return to central exchange layout. | [7502→7503](sheets_aspect_v2/cut_07503.png) |
| 7857 | Paused near-right/far-baseline layout changes to central ready positions. Current returns both athletes immediately; no retained empty near-right person box. | [7856→7857](sheets_aspect_v2/cut_07857.png) |
| 8106 | Near-right departing athlete returns centrally and far athlete changes position in one frame. Current fresh boxes fit the new source layout. | [8105→8106](sheets_aspect_v2/cut_08106.png) |
| 10023 | Athletes change ends/positions and the graphic layout changes; current reacquires the new positions. | [10022→10023](sheets_aspect_v2/cut_10023.png) |
| 10604 | Departing/turning positions change to central play positions abruptly. | [10603→10604](sheets_aspect_v2/cut_10604.png) |
| 10770 | Both athletes jump from near-net positions to a ready/exchange layout despite unchanged visible score values. | [10769→10770](sheets_aspect_v2/cut_10770.png) |
| 11903 | Walking near-left/far positions jump to central exchange positions. | [11902→11903](sheets_aspect_v2/cut_11903.png) |
| 15579 | Far-baseline and near-center pause changes to exchange positions. | [15578→15579](sheets_aspect_v2/cut_15579.png) |
| 15985 | Near-left walking athlete relocates centrally; far athlete relocates as well. | [15984→15985](sheets_aspect_v2/cut_15985.png) |
| 16446 | Walking/paused positions abruptly change to ready/exchange layout. | [16445→16446](sheets_aspect_v2/cut_16446.png) |
| 17069 | Both source positions change abruptly into a new exchange layout. | [17068→17069](sheets_aspect_v2/cut_17069.png) |

The immediate current reacquisition versus temporarily empty original raw baseline at several cut frames is a source-supported behavioral difference, not an accuracy score. Follow-on7858–7860 and8107–8111 show current boxes continuing on the visible athletes in [other sheets](sheets_aspect_v2/other_02.png).

## Contact, class and anonymous actor changes

Compared with the latest445-contact semantic control, current has451contacts and451strokes. The six additional anchors are1438,3015,3558,6471,8108and10676; no original exact anchor is removed. The retained source/overlays show:

| Frame | Source appearance | Review limit |
|---:|---|---|
| 1438 | Near athlete raises the racket/arm in an overhead action. | Compatible action, but exact impact/shuttle association remains unverified. |
| 3015 | Near athlete lunges/extends in a stroke-like movement. | A single selected source frame cannot independently prove a contact; event physical status is insufficient. |
| 3558 | Far athlete raises racket during an overhead action. | Raw racket estimate exists but recorded racket-overlap support is zero; no verified impact or lift label. |
| 6471 | Near athlete makes a low lateral lunge with extended racket arm. | Source action is plausible; carried-person/association uncertainty remains. |
| 8108 | Near athlete makes a forward racket action just after the acquired edit. | Reacquisition context and physical impact remain ambiguous. |
| 10676 | Near white-clad athlete is in a racket-ready/action posture. | Exact impact cannot be independently established; retained physical status is insufficient. |

Evidence: [1438/3015](sheets_aspect_v2/contacts_01.png), [3558/6471](sheets_aspect_v2/contacts_02.png), [8108/10676](sheets_aspect_v2/contacts_03.png). Payload `event_status=confirmed` is an **internal pipeline state**, while separate `physical_event_status` remains ambiguous/insufficient and named `actor_player_id` is null. These are not six demonstrated true positives. A restored body series can change candidate competition without adding new raw shuttle observations.

At [3540](sheets_aspect_v2/classes_01.png) the near athlete lunges low; `lift→push` remains a prediction change. At6456 the far athlete makes an overhead action; `clear→drop` remains unverified. Earlier causal evidence links those changes to new3558/6471next-candidate flight intervals; this visual review does not independently rerun that causal experiment. At [16600](sheets_aspect_v2/classes_02.png), the far athlete is near the forecourt making a racket action; fresh current person boxes replace carried baseline geometry and the label changes `unknown→net_shot`. This supports a context/freshness change, not class correctness. No class-wise physical metric is available.

Anonymous actor changes at [1522/1534](sheets_aspect_v2/actors_01.png) and [1654](sheets_aspect_v2/actors_02.png) keep exactly the same selected bbox while episode3becomes2: this is an ID-label change, not visible person substitution. At5459 and16600, current fresh boxes replace carried baseline boxes and unresolved attribution becomes a provisional track1hypothesis. Both source athletes remain visible. No named identity, roster or team binding is established by these changes.

## Point comparisons and unresolved source cases

The component agent reports61common generated-reference distances worse,234better and33171identical. All13,966original fresh-detector pair errors remain exactly unchanged. Additional current detector frames therefore change comparison population; neither a lower aggregate mean nor a few worse pairs establishes physical accuracy. This review uses the supplied decomposition without changing matching rules or recalculating metrics.

The largest common increases are16552slot2:4.58695→8.57464px(+3.98769),16553slot2:6.35324→10.29546px(+3.94222), and14561slot2:.90200→2.61191px(+1.70991). [16551/16552](sheets_aspect_v2/outliers_06.png) and [16553/14561](sheets_aspect_v2/outliers_07.png) show the same intended visible athletes, with modest bbox/foot-anchor differences rather than an official replacing an athlete. The first two are carried estimates in both arms;14561current is fresh and baseline carried. The exact independent anatomical foot position is not labelled, so these are **legacy point-agreement regressions**, not proved physical pixel errors or proof that current is better. At16600 the larger legacy-distance improvement similarly coincides with fresh geometry but does not certify physical localization.

Other reviewed newly scored/extreme/control frames1340,3667,5076,5472and7845–7847 show the visible athletes and explain additional comparison coverage, with no extra gross population error found in this selected evidence. Overlap/occlusion around13466–13469 remains visually difficult and inherited; a good numeric assignment is not a reviewed physical identity.

Two important unresolved cases remain:

- **11331–11333:** the near white-clad athlete lunges beyond the carried orange box. Current preserves the athlete population versus the original raw baseline's missing near person, but the box/foot anchor visibly lags. `do=false` and `dm=false` preserve that uncertainty. Blue stale image-context regions do not repair or authorize this player estimate. [Evidence](sheets_aspect_v2/outliers_01.png), [11333](sheets_aspect_v2/outliers_02.png).
- **13152–13154:** the athlete raises the racket while the recorded shuttle remains beside the near shoe/ground region. This remains a suspicious inherited localization/association example, identical in the current and baseline raw rows, not a newly repaired shuttle detection. Exact physical shuttle location remains unlabelled. [Evidence](sheets_aspect_v2/outliers_03.png). Classical racket ellipses also remain qualitative estimates and include visibly questionable locations elsewhere.

The source review adds no new blocking gross regression to the component findings. It leaves the documented minor legacy-agreement changes and all unsupported physical/event/identity metrics explicit. Test 1 acceptance is the orchestrator's decision using native completion, full regressions, matrices and these visual limitations; this review does not authorize Test 3 or claim the whole pipeline is accurate.
