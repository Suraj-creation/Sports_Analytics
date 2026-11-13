# Isolated OSNet court-origin crop probe

**The existing pinned OSNet checkpoint does not rescue the182withheld Test1athlete rows under the frozen positive-appearance gates. Do not adopt it as the solution to that coverage regression.** This is a real checksum-verified, GPU-executed crop probe with all requested cases retained, not a fake-vector test. It changes no production code, profile, model registry/cache/lock, annotations or baseline predictions. No threshold was fitted to these results. No named identities, physical ground truth or accepted points were created.

## Actual artifact, loader and execution

[Download receipt](download_receipt.json) binds the explicitly authorized1,001,683-byte checkpoint at [immutable publisher revision](https://huggingface.co/LibreYOLO/LibreReID-osnet/resolve/98f8d8651b6c18772a8b2879f1d740b3278a1a3d/osnet_ain_x0_25.pt), SHA256`ce171fe160b3608f5e4c19489774991419be965b1d6f4bdccc4b4cfd2ef95347`. It lives only in `inputs/`, outside shared models/cache and lock files. Exact digest/length were verified before the existing `OSNetAppearanceEmbedder` loaded its vendored weights-only state-dict loader. No unsafe pickle workaround or environment/package installation was needed.

[Real-model smoke receipt](real_model_smoke_receipt.json) records normalized, finite1×512output on physicalGPU1 (`CUDA_VISIBLE_DEVICES=1`,visible`cuda:0`), NVIDIA GTX1080Ti, Torch2.14.1+cu126, FP32. It took0.737s. The full initial crop run took68.926s; the separately corrected known-scene Test2control took28.050s. Peak Torch-allocated tensor memory was23,957,504bytes, **not**whole-process GPU memory or total CUDA-context usage. These isolated timings are not end-to-end throughput benchmarks; CPU/RSS/power were not independently profiled here. Private descriptors were bounded in memory and never written to evidence/events/cache outputs.

The [earlier license investigation](../reid_investigation/REPORT.md) retains primary publisher MIT weight declaration, both MIT code licenses, exact upstream provenance, packaged dependency notices, actual restrictive MSMT17release agreement and inaccessible primary CUHK03/Duke dataset-term gaps. This permission is for an isolated research checkpoint probe; it is not production adoption or commercial/data-rights clearance. No training datasets were downloaded.

## Method and evidence boundaries

- Original [driver](run_probe.py), [execution log](execution.log), [summary](summary.json) and [completion receipt](completion.json) are preserved. [Known-scene child driver](run_known_scene_probe.py), [intervention plan](known_scene_reset_v2/reset_intervention.json), [child summary](known_scene_reset_v2/summary.json), [child completion](known_scene_reset_v2/completion.json) and [child log](known_scene_reset_v2_execution.log) preserve the later correction separately.
- Galleries use only **past**, fresh detector-matched, confidence≥0.5, strictly in-court, nonoverlapping observed player crops. Each anonymous raw-track hypothesis stores at most4descriptors, at most16live galleries and8sretention. Outside continuations never update the gallery or original court anchor. Gallery creation does not prove a reviewed athlete identity; raw IDs are only episode hypotheses. Queries are scored before the current frame's eligible seeds are added.
- Crop preprocessing uses the unchanged existing BGR→RGB,128×256normalization and512-Dembedding adapter. Each query and gallery seed records source/proxy/frame/PTS/image/crop hashes; descriptors themselves remain private. Inputs include original completed perception bytes and exact camera geometry. Original source/proxy full-rational PTS audits, retained RF-DETR proposal artifact/model digest and prefix artifact catalogue are verified in [additional provenance](additional_provenance_verification.json). No detector, pose, shuttle or pipeline neural inference was rerun.
- Live cosine≥0.8and row/column cosine separation≥0.05were fixed controls; dormant matches after1s additionally require≥0.9. **The cosine-gap diagnostic is not the existing production joint score's0.05margin**, which combines0.65appearance+0.35motion+0.02rawcontinuity. Motion/admission gates were deliberately not applied. Output `appearance_support` is conditional support, not a production association, participant admission or calibrated probability.
- All182Test1withheld boxes are scored on their current images:72have recorded fresh detector support;110are **carried boxes cropped on current pixels**, not new observations. Current confidence is available for9and remainsnull for173. Complete raw competing proposals are not retained for most of those frames. No old person confidence was substituted for current support. Therefore these are conditional crop diagnostics, not a fully reproduced182-row pre-ROI gate evaluation.
- For Test2, all retained raw candidates are included at every retained detector call from5956through6492:929proposals over186calls, including the extra5956control. The requested5958–6492range contains925proposals over185calls. Missing detector frames are not invented. Every retained detector crop hash and full proxy-frame hash agrees with the original source-bound prefix. Test2seeding uses the declared historical source-probe player/ROI records, not a fresh c585fullTest2run.

[All original comparisons](comparison_rows.jsonl), [past gallery seed receipts](gallery_seed_receipts.jsonl), [decoded frame receipts](decoded_frame_receipts.jsonl), [all corrected Test2comparisons](known_scene_reset_v2/comparison_rows.jsonl) and [machine-readable final readout](final_review_summary.json) retain every failure, ambiguity and missing-seed case.

## Test1: all seven coverage-loss groups

No target achieves the complete frozen appearance/dormant/margin support condition. Statuses are mutually exclusive diagnostic outcomes; **they are not physicalFNcounts**. Best-gallery cosine refers to the top anonymous gallery, which may itself be the wrong visible athlete.

|Withheld frames|Rows|Fresh / carried|Known current confidence|Cosine<0.8|Dormant<0.9 after live+margin pass|Margin ambiguous|Supported|Cosine min / median / max|
|---|---:|---:|---:|---:|---:|---:|---:|---|
|753–800|48|24 / 24|0|24|23|1|0|0.754457 / 0.800619 / 0.875408|
|3413–3449|37|18 / 19|0|32|5|0|0|0.764255 / 0.784791 / 0.820851|
|6365–6381|17|8 / 9|4|17|0|0|0|0.644240 / 0.697644 / 0.748102|
|7801–7805|5|0 / 5|0|5|0|0|0|0.761196 / 0.783272 / 0.795417|
|7812–7856|45|8 / 37|5|42|3|0|0|0.724932 / 0.762427 / 0.809604|
|8087–8105|19|9 / 10|0|0|18|1|0|0.805413 / 0.825498 / 0.846079|
|14103–14113|11|5 / 6|0|3|7|1|0|0.782495 / 0.813286 / 0.833482|

Overall:123below0.8,56below the dormant0.9requirement after passing live/margin checks,3margin ambiguities,0supported. No target lacks all past galleries. Ignoring the dormant requirement would conceal a failure of the declared retention policy rather than demonstrate improvement. Changing gallery policy, threshold, checkpoint or model is a separate future experiment.

**6376white athlete:** raw current support0.896068156and a valid image crop do not establish distinctive appearance. The highest cosine is0.710875690to the dark-shirt athlete's gallery; the source-consistent white-shirt gallery has only0.655042112. Both are below0.8, so the wrong top-ranked candidate is withheld. [Query crop](review_evidence/test01_frame_06376_crop_0.png), [dark-shirt seed6374](review_evidence/test01_frame_06374_crop_1.png) and [white-shirt seed6330](review_evidence/test01_frame_06330_crop_2.png) were visually inspected. The white seed gallery is four past strict-court frames6324/26/28/30; no outside crop is learned. This does not support appearance-based renewal of its participant authority.

The independent motion-failure control6338was also probed using the exact same checkpoint/defaults and reconstructed past strict-court galleries from the immutable seed receipts. [Additional result](additional_6338_diagnostic.json): current dark-athlete region supports0.951036930; source-reviewed white-athlete region is below0.8at0.757962525. Confidence/full competitor availability remain explicitly limited. This is another failure to complement that case, not evidence for tuning a new cutoff.

## Test2: all candidates and the source-known reset control

The initial run inherited cached/prefix scene barriers and missed the already source-known5958and6151edits. **That reset omission belongs to the diagnostic driver, not a production fix.** Its complete output is preserved as an inherited-missed-reset control. The separate child explicitly clears private galleries at5958,6151and6307; this is an **oracle diagnostic control based on source-reviewed edits**, not a claim that production detected those boundaries and not an automatic scoreboard rule.

|Corrected control outcome|Strict-court raw proposals|Outside strict-court raw proposals|Total|
|---|---:|---:|---:|
|Appearance support|312|11|323|
|Below live cosine0.8|0|559|559|
|Below dormant cosine0.9|0|26|26|
|Margin ambiguity|6|0|6|
|No past seed after reset|6|9|15|
|Total|324|605|929|

These geometry partitions are not labelled athlete/official classes. All11outside appearance-supported crops at6054,6060,6062,6064,6066,6068,6070,6072,6074,6076,6078were visually reviewed in the [complete source sheet](review_evidence/all_11_outside_appearance_support_source_sheet.png): each shows the red-shirt athlete walking near the near baseline. Scores range0.820343554–0.899656415. This shows limited short-term appearance support in those source cases, not physical precision or a solution to the182women's-match losses. Rejected outside proposals include genuine visible athletes too; geometry alone must not turn every rejection into a correct official exclusion.

|Explicit source control|Actual candidate behavior|Interpretation|
|---|---|---|
|[5956](review_evidence/test02_frame_05956_proposal_status.png)|Near red athlete0.898281932supports; far blue athlete0.786723733is rejected; other two retained background candidates below0.8.|An actual visible athlete is missed by the frozen appearance criterion before the edit. No universal positive-appearance guarantee follows from successful staff rejection.|
|[5958](review_evidence/test02_frame_05958_proposal_status.png)|All5raw candidates are `no_past_seed`after the source-known reset.|Correctly abstains across the edit; no cross-cut identity match is certified. The inherited control's comparisons are diagnostic evidence of why scene scope matters.|
|[6492](review_evidence/test02_frame_06492_proposal_status.png)|Red/blue athlete regions support0.810231209 /0.886682689. Three retained seated/staff-region candidates score0.617752433 /0.576931953 /0.535121202and are below0.8.|These independently viewed crops support useful separation at this frame, while all identity/name/point authority remainsnull. No exhaustive physical accuracy metric is claimed.|

###5957→5958 is a genuine edited jump

The [independent adjacent-frame review](known_scene_review/REVIEW.md) retains exact [5957](known_scene_review/frame_05957_exact_proxy.png) and [5958](known_scene_review/frame_05958_exact_proxy.png) images. Blue athlete moves abruptly from behind far-left baseline to central far court; red athlete moves abruptly from near-left/net area to central near court, with changed movement phase in1/30s. The fixed background remains aligned. The9:13→10:13score update corroborates the body-position discontinuity; score alone did not determine the edit.

Original rawTest2video is no longer local. These are exact retained original-run **proxy** decodes, checked against original source/proxy identity, full prior rational PTS audit, individual frame hashes and source-bound prefix image hashes, not a newly decoded original raw source. Receipt records PTS3049984→3050496,timebase1/15360.

The old athlete-to-official screen-position handover at5958begins across this missed edit. It cannot alone establish continuous-scene physical identity handover. The bounded membership lease addressed a downstream symptom here; its182withheld-athlete cost must be evaluated separately. Real continuous-scene handover safety is still needed, but source-reset acquisition and participant authority should not be conflated.

## Disposition and remaining requirements

No pipeline improvement was made in this probe and c585is not accepted on these results. The current adapter can run on the existing server without installs, but post-ROI placement still prevents it from seeing rejected rows; moving it upstream would not make these frozen appearance scores succeed. No tuning was performed after observing failures.

Retain the source-confirmed edit/acquisition fixes, investigate missed-source-reset causes, and separate image continuity from participant authority. Any future appearance-supported continuity port must preserve court-origin provenance, full competitors, one-to-one ambiguity, bounded private memory, no outside self-learning, explicit confidence/missing data and resets. It must be tested on singles/doubles, similar uniforms, pose/view changes, adjacent courts, true continuous runoffs, occlusions and genuine edits. This isolated singles probe cannot validate doubles.

PhysicalIDF1/HOTA/AP, named identity, winner/score correctness and athlete-continuity precision/recall remainunavailable: no independently reviewed exhaustive identity/box labels were created. The evidence provides observed conditional distributions and exact source diagnostics, not inventedTP/FP/FN or evidence that all182rows should be force-admitted. Final artifact/source validation preserves originals and verifies shared source/model/profile files unchanged.

Finalization detail: the first driver's original completion hashed `execution.log` immediately before printing its final JSON summary. The log therefore has one expected later line. The independent final verification checks that its old prefix hash matches exactly and its sole appended line equals the saved summary; the original log/completion are retained, not rewritten. The final receipt binds the full closed log and all later review/child artifacts. Every other original artifact and every known-scene child artifact matches its original receipt. This is a reporting-finalization detail, not a rerun or a pipeline/source change.
