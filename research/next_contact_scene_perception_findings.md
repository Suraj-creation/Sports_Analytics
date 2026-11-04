# Source-frame review of background, competing candidates and flight-mask losses

Read-only specialist review,2026-11-05. No production code, model, mask, label, original video or historical result was changed by this review. The component inference was executed separately by the orchestrator; this specialist inspected its source-bound JSONL and decoded exact-PTS original-frame crops.

## Main conclusion

The GT27 painted-T attractor and GT31 visibility gap have different upstream mechanisms. Rolling background reinforces a static court marking in GT27; fixing that background alone removes the attractor without recovering a valid observation through most of the high flight. Separately, the finite flight mask rejects strong source-visible airborne hypotheses at early re-entry in GT27 and at both exit and re-entry in GT31. The earlier explanation that these complete runs were model absence is now too broad: the raw network already observes many of the missed streaks, and filtering discards them.

For the specific question about top-k candidates during the GT27 T lock: **mostly no retained alternative localizes the airborne shuttle through12744–12767**. Fifteen of those24frames retain only the T component above the diagnostic floor0.1; remaining components are weak body/context peaks. Source snapshots show the earlier upward flight leaving the image, so an absent observation must remain unknown. At12769–12771, however, a strong moving top-edge component is retained and visually agrees with re-entry; it is rejected by the mask while the T remains the accepted point. Multi-hypothesis preservation exposes that distinction, but does not invent the missing airborne track.

## Exact experiment identity and what was held fixed

Input component record: `artifacts/benchmarking/experiments/next_20261105_shuttle_background_probe/`. It contains5,433frame/variant rows:1,811selected canonical frames for each of rolling, fixed-startup and zero-background variants. The same verified TrackNetV3 weights, CUDA0 FP16 execution, eight-frame sequence, step8, batch4,512×288model input,1280×720proxy, recorded60-frame chunks, scene IDs and flight masks were used. Variants change only the background channel source. Rolling state follows chronological preceding frames; fixed-startup uses the same24warm-start source samples; zero-background zeros this checkpoint's concat channels and is not a separately trained background-free model.

TrackNet SHA256: `df867641a02712b021f04548ff4b1208ddfdb47f629ab2094ceb978667e83b1a`. Source SHA256: `877c6d39d34ccfb302865ed44f7e08949b0f72be2833f71777066f837e6b8bd6`. Proxy SHA256: `d352d684fb5399d804b8f50c785a3605346e7f03987ecb1d9a73ef3482535a97`. Model fallback=false. The executor snapshot and all source/input/cache hashes remain in the component manifest.

An independent literal-value comparison confirms that the rolling arm reproduces every recorded accepted coordinate and support over all1,811selected frames:0coordinate-value differences,0support differences, maximum coordinate delta0.0. This anchors the diagnostic to actual production observations and isolates background effects without changing chunk size/resize/checkpoint simultaneously. It is fresh component inference, not a fresh whole analytics pipeline run and not independently labelled shuttle-localization accuracy.

Per-arm model/diagnostic wall aggregates were: rolling28.048s, fixed-startup25.899s, zero-background26.610s. They exclude the full decode/warm-start/history-reconstruction path and do not establish end-to-end throughput. Variants alternated execution order by chunk.

## GT27: static painted-T attraction and early masked re-entry

GT27 is annotated12451–12966. The component probe covers12420–12979. Across its515half-open GT frames the rolling arm accepts482points; fixed-startup434; zero-background393. Those counts measure acceptance coverage, not accuracy. The rolling diagnostic retains a component within10proxy pixels of(645,393) on301frames and selects that location on53frames. This geometric count is not a claim that every such sample is incorrect; a true trajectory can cross the same image region. Fixed-startup retains no component in that10pxcluster above the0.1diagnostic floor.

The causal local block is clearer:

| Frame or block | Rolling observation / competing components | Fixed-startup result |
| --- | --- | --- |
|12733–12738|Moving upward trajectory from(482.3,309.7) to(485.7,39.2). T also competes near(645,395).|Moving trajectory retained with nearly identical coordinates.|
|12739|Raw top-edge component(485,12.5),support0.441,maskFalse; staticT0.473 and body/context competitors. No accepted point.|No accepted point; raw edge component0.442also below0.5.|
|12744–12767|All24accepted points sit on T. Fifteenframes retain no other floor-component; later weak alternatives near(560,305),support≈0.12–0.16.|All24have no accepted point;23have no retained component atfloor0.1. RemovingT does not recover a new shuttle observation.|
|12768|Tselected0.533; weak top-edge hypothesis(520,5),0.152,maskFalse.|Same weak top-edge hypothesis0.149,maskFalse.|
|12769|Raw movingpeak(517.5,10),0.671,maskFalse; T0.550accepted.|Raw movingpeak remains0.684 but mask rejects it.|
|12770–12771|Raw movingpeak(522.5,22.5),support0.684/0.671,maskFalse; T0.558/0.548accepted.|Strong movingpeak persists; no accepted point because ofmask.|
|12772|Rawmovingpeak(525,35),0.651is itself masked; componenttail inside the mask yields acceptedcentroid(522.10,38.19),support0.6277.|Acceptedcentroid(522.10,38.18),support0.6370.|
|12777–12790|Moving trajectory is accepted while T can persist as lower-ranked competing component.|Moving trajectory retained;Tcomponent absent.|

For the handoff's exact12748–12771window, rolling accepts24/24Tpoints; fixed-startup accepts0/24(21belowthreshold,3maskrejected); zero-background accepts2/24. Thus changing background causally suppresses the T attractor under matched neural context, but a lower acceptance count does not establish correct shuttle localization. Zero-background also retains a different static distractor near(1072.5,397.5) outside the court mask, and occasionally promotes other context peaks. It is not a reliable universal replacement.

Exact original crops confirm a bright ascending streak at12738/12739and a bright descending streak at12769/12771above the far player. No visible streak is established by the sampled12744/12748/12753/12763upper crops. The entire flight is not labelled frame-by-frame; absent visual confirmation in a crop does not prove universal physical absence. The stable accepted T points correspond to painted court-line geometry, while the far player continues overhead preparation/action. A static court mark is not a landing observation.

The earlier accepted estimated contact12771 is located on the T, while a stronger raw moving hypothesis appears near the image top. Its subsequent large outgoing fitted velocity mixes the static location with reacquisition. This links the static distractor/mask/association chain to the previously measured unstable contact score. Contact-only numerical correction was separately rejected for rally accuracy because it cannot repair the upstream observation sequence.

An earlier accepted re-entry at12769instead of12772can change the existing bounded recovery clock; whether it resolves the rally end must be measured by inference/semantic evaluation. This review does not increase the merge allowance, manually bridge the interval or inject source-reviewed coordinates.

## GT31: strong model observations discarded by the finite flight mask

The raw component trace changes the historical loss classification. The model does not simply fail to see every source-visible streak. All four ascending frames14647–14650have raw support>=0.5and reason=mask_rejected. All twelve descending frames14683–14694have raw support0.68457–0.86768and reason=mask_rejected, with masked maxima below0.5. Across background arms these blocks remain rejected by the same mask.

| Frame | Raw moving component(proxy xy) | Raw support | Masked maximum | Decision |
| --- | --- | ---: | ---: | --- |
| 14646 | [877.5, 87.5] | 0.756348 | 0.756348 | accepted |
| 14647 | [885.0, 55.0] | 0.645996 | 0.223022 | mask_rejected |
| 14648 | [890.0, 17.5] | 0.743164 | 0.099670 | mask_rejected |
| 14649 | [890.0, 2.5] | 0.536133 | 0.090393 | mask_rejected |
| 14650 | [892.5, 2.5] | 0.535156 | 0.089600 | mask_rejected |
| 14651 | [895.0, 0.0] | 0.163208 | 0.094849 | below_threshold |
| 14652 | none≥0.1 | 0.099976 | 0.094360 | below_threshold |
| 14683 | [945.0, 5.0] | 0.693359 | 0.117554 | mask_rejected |
| 14684 | [942.5, 25.0] | 0.762207 | 0.118408 | mask_rejected |
| 14685 | [940.0, 45.0] | 0.781738 | 0.159912 | mask_rejected |
| 14686 | [940.0, 47.5] | 0.820801 | 0.171753 | mask_rejected |
| 14687 | [937.5, 70.0] | 0.815430 | 0.255127 | mask_rejected |
| 14688 | [940.0, 92.5] | 0.867676 | 0.167236 | mask_rejected |
| 14689 | [942.5, 115.0] | 0.806152 | 0.182739 | mask_rejected |
| 14690 | [940.0, 142.5] | 0.760254 | 0.168823 | mask_rejected |
| 14691 | [937.5, 165.0] | 0.684570 | 0.166626 | mask_rejected |
| 14692 | [937.5, 165.0] | 0.696045 | 0.163818 | mask_rejected |
| 14693 | [937.5, 190.0] | 0.735596 | 0.193298 | mask_rejected |
| 14694 | [937.5, 215.0] | 0.723633 | 0.424194 | mask_rejected |
| 14695 | [937.5, 240.0] | 0.686768 | 0.686768 | accepted |

The original unoverlaid crops show the same bright rising streak at14647/14648and a descending streak at14683/14684/14685/14688/14690/14691/14694. These source pixels spatially and temporally agree with the rejected high-support component. This is strong diagnostic evidence of filter-induced visible-shuttle loss. It is not an independently reviewed pixel annotation or proof of the exact physical entry/exit frame.

At14651the remaining edge component isweak0.163and14652has no component≥0.1; later high-flight snapshots remain ambiguous or outside the image. A mask change can recover discarded visible points but cannot create observations during genuine physical nonvisibility. At14695the descending shuttle reaches(937.5,240)where the existing finite mask admits it, explaining why a model-based top-band cue sees late re-entry far below the physical image edge.

The current finite upward sweep is an image-region heuristic derived from floor projection plus a fixed fraction of image height. Floor geometry does not define the maximum airborne image elevation. A separately tested vertical-to-image-ceiling column policy is therefore a more relevant experiment than widening a GT31-specific ythreshold. It still does not prove target-court ownership or3Dtrajectory accuracy and can admit spectators, lights, graphics, adjacent-court objects or line-like distractions. Preserve horizontal/floor restrictions, invalid-view gates, same-camera context and opt-in selection; evaluate every row and unmatched prediction before any promotion.

## Real terminal/floor evidence is a necessary negative control

The original GT27 terminal crops12945,12950,12954,12960,12966,12979show a compact bright shuttle-like object moving toward/along the near-right sideline and remaining near the floor. The rolling model tracks the corresponding region from(871.5,403.2)through(916.8,578.8)over these frames. This image sequence is different from a fixed painted-T point and shows why neither all near-line peaks nor all slow floor motion should be discarded globally. Exact landing, bounce/roll semantics and the annotation's stopping convention remain unreviewed; these stills do not define a replacement end label or winner.

Static T, real floor/shuttle-like objects, high flight, weak entry, apex/exit and mask rejection must remain separate test classes. A line-aware background score can qualify or retain ambiguous observations; it must not automatically reject legitimate line-adjacent shuttle motion or reinterpret a stale point as a fresh impact.

## Preserved review artifacts and limitations

New read-only review package: `artifacts/benchmarking/experiments/next_20261105_contact_scene_perception_review/`. `review_extract.py` is the exact CPU extraction script;36PNG original-pixel crops have no model marks; four montages put headings outside source pixels. `frame_evidence.json` pairs every inspected frame/ROI/exact sourcePTS with all three candidate records. `manifest.json` pins source/probe/candidate/script SHA256. The original video and historical reviews are unchanged.

The component candidate records retain top-k **connected components above a diagnosticfloor**, not every local maximum or full heatmap. A missed component below0.1or outside the topfivecannot be ruled out; no heatmap tensor was fabricated. Confidence remains raw uncalibrated model support. This review adds no contact/pixel/cut labels, ground-truth-driven interval edit, full-video rally score, generalization claim, model replacement or production default change. Candidate telemetry now makes the background and mask causes directly inspectable, where historical `(None,0)` observations could not.
