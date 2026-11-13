# Source-bound weak scene-acquisition design shadow

**The proposed separate acquisition cue can expose Test2edit5958without lowering the existing15intensity floor.** Across10retained windows and2,399frames, the camera-aligned complete-current-layout shadow adds5958only where scheduled/probed raw proposals are retained. Two separately retained actual detector probes also support355and25521. All three have independently viewed adjacent source-image body relocations; this is agent diagnostic evidence, not measured scene precision/recall or new human ground truth.

No production or historical evaluator/source/annotation output was modified. No model was loaded, no new detector inference was performed, and no weights/data were downloaded. These are **one-step counterfactuals at recorded states**, not a chronological rerun that applies new resets and recomputes later tracking, scene history or engine feedback.

## Prespecified branches and independent evidence

The existing strongV3hypothesis/decision path is preserved exactly, including15floor, ratio3, existing supporting-key semantics and positive complete raw-layout veto. The shadow weak cue is a distinct acquisition question, not a relabelled strong hypothesis:

1. Recorded stable background (`features≥6`,consistent fraction≥0.5) plus at least two nonoverlapping previous-image region witnesses with≥6features, finite correspondence values and existing adaptive ratio≥3. This alone has no reset authority and does not change the strong absolute floor.
2. A causally available recorded format decision suppliesN=2(singles)orN=4(doubles); current observation count does not infer format. Test1format is recorded known at120andTest2at96. Earlier unknown-format frames remain unknown.
3. A source-bound current **raw detector** observation must exist. Select current boxes using strict `CourtROI.contains_feet(...,allow_runoff=False)`, independently of inherited track admission or expired court leases. ExactlyNdistinct current strict-court boxes are required. All retained raw proposals, including outside officials, remain available for positive correspondence vetoes.
4. Every current strict box must have no0.3IoUcorrespondence to **all**previous image boxes. The literal positive-area-disjoint alternative is also recorded separately. A full positive one-to-one raw correspondence veto is checked for the weak witness cohort; one outside official matching one old region is insufficient to veto a complete displacedN-population.
5. The updated camera safeguard additionally requires adjacent recordedVALIDcalibration/main-viewGmatrices. Project all four corners of every prior box with `Gcurrent @ inverse(Gprevious)`and form its axis-aligned image bbox. Every current strict box must also remain unmatched at existing0.3IoUto these camera-aligned prior boxes. Unknown/singular/nonfinite geometry abstains; stable background LK is never substituted for identityG. Full camera-aligned positive correspondence is retained as a veto too.

Court-side balance and mutual current-box nonoverlap are **additional diagnostics**, not assumed productionAPIgates. All observed added cases happen to haveone box on each side, but that fact is not silently installed as a new rule.

## What was checked

[Shadow driver](probe_design.py), [closed execution log](execution.log), [per-frame records](all_frame_design_records.jsonl) and [summary](summary.json) preserve every examined frame and unknown. Exact pure geometry classASTs match between the imported MAINimplementations and original executed candidate source snapshots;[geometry equivalence](geometry_source_equivalence.json) records both file/class hashes without rebasingROOTor loading the new worktree's changing production source.

[Source verification](verify_sources_and_supplement.py) decoded all2,399exact original-run proxy frames with rationalframe/30PTSchecks, matched every full-image pixel hash to the immutable prefix, and independently verified**911retained detector crop hashes**against reconstructed original geometry. The original RF-DETRmodel digest is`fcd3c3c4e0d3d5533ee9c3a174deb7f02dfe4b042b6fdd3d29040f3c6da7845e`. [Every retained proposal verification](all_retained_proposal_pixel_verification.json) and[source PNG receipts](source_evidence_receipts.json) preserve the bindings. Missing proposal frames remainunknown, never replaced by carried tracks.

The two supplemental observations come from the separately retained actual `detector_frame_probe_v1`,not from the prefix schedule. Their whole-image hashes, original crop coordinates and model digest agree; their raw boxes/scores and source provenance are explicit in[supplemental retained cases](supplemental_retained_detector_cases.json). This represents already measured on-demand inputs at355/25521, not a claim that those scheduled prefixes had executed a detector at those odd frames.

|Source window|Frames|Weak ratio-cohort frames|Scheduled/probed new camera-aligned candidate|Separate retained probe|
|---|---:|---|---|---|
|test1_00000_00080|81|none|none|none|
|test1_00235_00310|76|none|none|none|
|test1_07650_08150|501|7857, 8106|none|none|
|test1_09000_09060|61|none|none|none|
|test2_00300_00365|66|355|none|355|
|test2_05505_06510|1006|5958, 6151, 6307|5958|none|
|test2_07640_07740|101|none|none|none|
|test2_11300_11360|61|none|none|none|
|test2_23570_23680|111|none|none|none|
|test2_25206_25540|335|25521|none|25521|

The7weak ratio-cohort opportunities include four already-strong controls (Test17857/8106;Test26151/6307),one new scheduled opportunity5958,and two missing-prefix opportunities355/25521. The precise case list is Test17857,8106andTest2355,5958,6151,6307,25521. No detector call, expectedN or failed geometry is manufactured to turn an unknown into a negative/positive.

##5958 and the two supplemental edited jumps

|Frame|Stored overall correspondence discontinuity|Raw proposals / strict-current count|No camera-aligned0.3match /literal nonintersection|Positive complete raw veto|Source conclusion|
|---|---:|---|---|---|---|
|355|7.807646987|5 /2|yes /no (oneIoU0.107892765)|false|[354](source_evidence/test2_frame_00354_exact_proxy.png)→[355](source_evidence/test2_frame_00355_exact_proxy.png): red athlete jumps from bottom-left courtside to center-near court; blue athlete changes position/posture to central far active play in1/30s.|
|5958|9.059624680|5 /2|yes /yes|false; one prior matches official|[5957](source_evidence/test2_frame_05957_exact_proxy.png)→[5958](source_evidence/test2_frame_05958_exact_proxy.png): blue athlete relocates from far-left runoff to central far court and red athlete from left/net to center-near.|
|25521|14.618745542|5 /2|yes /yes|false|[25520](source_evidence/test2_frame_25520_exact_proxy.png)→[25521](source_evidence/test2_frame_25521_exact_proxy.png): both athletes relocate from left courtside/baseline to central positions abruptly.|

At5958the two correspondence adaptive ratios are3.312612216and14.806637144; mean discontinuity9.059624680does not pass15. The strict current proposals are raw indices0/1, with detector supports0.950283533and0.919631783. Both are disjoint from both old image boxes. The seated official at raw index2overlaps the old far-athlete box withIoU0.302741728,just over the existing0.3gate. It matches **one**old witness only; it is not a complete2-person current-layout correspondence and must not veto the independent displaced two-box acquisition evidence. This is precisely why inherited admission and all-raw layout evidence must stay distinct.

Frame355is an important definition control: the old/current far-athlete boxes still intersect withIoU0.107892765,so the existing0.3correspondence test regards them as displaced while a stricter literal-zero-intersection variant would abstain.5958and25521passbothvariants. No numeric matching gate was changed silently.

For all three cases the recorded adjacent camera transform is numerically identity (with floating-roundoff terms), derived from real storedG, not inferred from background consistency. The camera-aligned and unaligned predicates therefore agree here. In more general footage this agreement is not guaranteed.

Scoreboards change too, but the source classification here rests on simultaneous body-position/posture jumps. No automatic scoreboard-driven reset or new winner label is proposed. Original rawTest2video is no longer local: these are exact preserved source-bound **analysis-proxy** images,not newly decoded raw-source frames. Full prior source/proxy time audits and original sourceSHAremain part of the immutable run provenance.

## Negative controls, old cuts and counterexamples

- At5956there is onlyone strict-court current proposal (the other athlete is outside),and no weak cohort.5957has no retained current detector call and no weak cohort. Neither adds a reset. This is a concrete before-edit population control, not an assertion that an athlete ceases to exist outside the court.
-7703and23639remain new-weak negatives.23639has a stored strong raw hypothesis but its existing positive current-layout correspondence vetoes a barrier; the new weak branch does not override that decision.11346also has no two-witness weak cohort in its bounded startup context,even though current raw targets exist. It remains unresolved by this shadow; a longer anchored prefix/full run is needed.
- All**13**genuine completed freshTest1content cuts2195,4837,7503,7857,8106,10023,10604,10770,11903,15579,15985,16446,17069are individually audited from their actual completedc585cache records in[all13cut audit](all13_completed_test1_cut_audit.json). Every one stores strong`raw.hypothesis=true`and`decision=barrier`; weak-only acquisition does not reinterpret them. Some overall raw means are below15because V3qualifies selected independent cohorts per channel; the overall mean is not a replacement for that existing witness algorithm. This structural/read-only preservation is not a fresh full-pipeline nonregression result.
- [Witness-veto/camera controls](witness_veto_and_camera_controls.json) separately checks complete correspondence for selected eligible witness keys and all-prior records; the observed candidate outcomes agree. A **synthetic**large camera translation makes raw old/current boxes disjoint while camera-aligned boxes match completely. OmittingGwould falsely permit a weak reset; the aligned safeguard abstains. Another synthetic control has displaced strict targets plus enough raw extras matching all old witnesses; the fullrawcomplete veto abstains. These are design counterexamples,not real-video or doubles accuracy evidence.

## Limits and next validation

No additional false candidate is observed in the retained2399-frame/911-call source scope. This is not measured scene precision,absence of all false resets or an exhaustive scene benchmark. The design was investigated after seeing these failures,so it is development evidence rather than held-out generalisation.

The distinct-current-count rule does not establish physical roster occupancy: hallucinated/duplicated detections,wrong calibration,simultaneous occlusions,airborne box bottoms,nearby courts and role substitutions can still falsely complete a strict-court population. There are no real four-player doubles clips in these windows. Synthetic count/cardinality controls cannot substitute for source-reviewed doubles,pan/zoom and camera-registration-failure coverage. Missing or uncertain geometry,format,current observations or independent witnesses must remainunknown.

The original prefix schedule/history is frozen. A real new5958reset would change later tracker/foreground memories and potentially engine cadence; cached one-step6151/6307and13oldcut records cannot prove their behavior after that intervention. Before accepting production changes, run native contract tests and chronological guarded prefixes with actual on-demand detector acquisition,then complete freshTest1andTest2through unchanged evaluators. Preserve both confirmed acquisition repairs and the182-row participant-coverage regression; this weak-scene design alone neither fixes all participant authority issues nor justifies Test3progression.

An initial shadow-only NumPy integer JSON-serialization failure and its executed helper/partial output are preserved in `initial_serializer_failure/`. It was corrected in the new research helper; no production component or historical evaluation method was debugged or changed.
