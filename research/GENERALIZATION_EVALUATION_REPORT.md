# Generalization evaluation — 5 November 2026

**No new blind generalization claim is established.** The current protocol inventories 15 existing recordings/materials and zero eligible prospective held-out recordings. Four current-profile runs on available exposed recordings have completed. Their results will be reported as frozen-profile stress/reference agreement, with every miss/extra/unknown retained.

## Available data and corrected audit scope

The initial 12-entry metadata-only snapshot was incomplete as an inventory of usable existing project references. A deeper source/provenance audit found the complete Test7 recording plus continuous India, Denmark and men's doubles clips with published human shot anchors/classes. The user's mission authorizes related local badminton analysis; missing rights/review metadata is not a new permission barrier to that analysis. Separate redistribution/training/deployment rights, human adjudication and blind-split evidence remain factual requirements for those claims.

| Material | Role / reference | Current evidence limitation |
| --- | --- | --- |
| Test1 | Exposed development; 36 user-designated immutable rally intervals | Onset/terminal annotation convention not independently adjudicated; no dense component truth. |
| Test7 full | Exposed historical evaluation; 31 primary legacy hand-marked coarse rally intervals | Primary `Test7_Full.csv` retained; generated 30-row `_rally.csv` is not GT. Whole-second timing, conflicting legacy winner/A-B conventions and unknown full-recording match identity limit claims. |
| India continuous clip | Exposed published-reference singles; 4,800 frames, 85 anchors across 4 partitions | Publisher-human origin; project source alignment remains draft. The four contiguous partitions are not rally-boundary GT. |
| Denmark continuous clip | Exposed published-reference singles; 3,300 frames, 39 anchors across 4 partitions | Use prepared-v2; prior project evaluation means no new blind claim. Draft source alignment retained unchanged. |
| DShuttleNet v7 doubles clip | Exposed published-reference doubles; 3,600 frames, 45 anchors, 4 hitters / 2 teams | Published anchor/class/hitter and separate rally spans; project timeline binding remains draft. No dense identity/box/movement truth. |
| FineBadminton 0044/0046 | Historical exposed development/evaluation respectively | Original media not found in inspected current/known retired roots; no new inference/download. Existing reference/role/protocol preserved. |
| Task2 250-frame doubles excerpt | Exposed development; 64 AI-draft boxes on 16 frames | No independently human-reviewed four-person accuracy or full continuity labels. |
| Remaining Test2–10 metadata candidates | Known related materials, incomplete present source/review linkage | Filenames/download manifests do not establish present files, match independence or exhaustive labels. No new blind role assigned. |

Exact paths, hashes, labels, original-source/crop bindings, published taxonomy and prior exposure are in [PRODUCTION_ADDITIONAL_DATA_PROVENANCE.md](PRODUCTION_ADDITIONAL_DATA_PROVENANCE.md), `production_readiness_dataset_manifest.json`, `production_readiness_exposure_history.json` and `prod_20261105_data_provenance_discovery_v1/additional_available_materials.json`. Current `prod_20261105_dataset_metadata_freeze_v3/` preserves 15 entries and adds explicit camera, format, FPS, dimensions, game type and annotation-status fields; unavailable facts remain unknown. Test1 and Test7 source properties were checked against their actual media headers. This metadata enrichment changes no split, exposure, reference alignment or inference configuration. The earlier 12-entry and pre-inference 15-entry freezes remain intact.

## Frozen inference and reference protocol

The new clean sessions use the verified continuous prepared clip as the uploaded source, or the complete Test7 source. They contain no reference interval, anchor, class, player name, old calibration, source crop or reviewed identity. Empty rosters declare only singles/doubles format. The fixed primary experimental association+scene configuration is identical across the four inputs; only optional public diagnostic ranges become empty. Internal candidate preservation remains active independently.

Each clip is inferred in full, including gaps, using only its own clip history. This differs from old full-original background seeding/external calibration; old and new measurements cannot be interpreted as a one-variable improvement comparison. The exact protocol_v2 source/model/input/profile hashes and launch commands live at `/home/administrator/Desktop/sport-analytics/production-readiness-runs-20261105/protocol_v2/`. Root NN source and public evaluation labels are frozen independently. Both v1 launches failed before NN on an obsolete research settings hook; failed logs remain preserved. The current staged-registry hook correction has an actual model-free pipeline smoke, not a mock-only claim.

Offline evaluation may rebind only new SID/source/proxy identity. It preserves every annotation ID, timestamp/frame, class, hitter, uncertainty/review flag, taxonomy and frozen earlier source transform. Existing draft offsets are India −1 and Denmark −3 before fixed crop subtraction; doubles 0. No offset is fitted to these outputs. Report ±3/±6-frame chronological one-to-one anchor agreement with all predicted candidates and full clip gaps, class confusions/unknowns, every miss/extra and unchanged evaluator contracts. Test7 uses exact seconds×actualFPS conversion of all 31 coarse primary rows and the unchanged IoU 0.5 evaluator, with both boundary denominators and unmatched predictions.

Named match metadata and the reviewed Test1 women's scoreboard windows support different-source context; they do not independently seal whole edited Test1/Test7 match identity. All three published clips were already exposed to the project. Provider training overlap is unknown. These results therefore cannot establish prospective held-out generalization, amateur coverage or independent physical-contact accuracy. Events within one match are correlated; event-count confidence intervals must not masquerade as match-level uncertainty.

## Release-critical evidence still needed

Freeze a genuinely new, match-disjoint, authorized representative set before prediction inspection, with source/recording identities, canonical mapping, reviewer/adjudicator provenance and exhaustive per-component labels. Include amateur singles/doubles, cameras/FPS/resolutions, court/light/background variations, multiple courts, similar clothing, occlusion, edits/motion, compression and VFR. Report per-match/per-condition singles/doubles metrics, macro/micro results, meaningful match-level intervals and worst cases. Do not reuse a tuned or previously exposed recording as blind, or pseudo-label missing physical truth.

The protocol tooling rejects split aliases/leakage, missing reviewed identity/use claims, changed source hashes and output reuse. These software checks cannot independently verify a human attestation or license. [PRODUCTION_READINESS_ANNOTATION_PROTOCOL.md](PRODUCTION_READINESS_ANNOTATION_PROTOCOL.md) provides the review package requirements. Completed current-profile metrics follow after complete source/frontier checks and offline evaluation.

## Completed current-profile stress/reference agreement

All four workers completed their entire source, with unchanged frozen source/input/profile/model guards: India 4,800, Denmark 3,300, doubles 3,600 and Test710,725 frames. The source profile is the fixed association+scene candidate measured on Test1. No parameters were tuned using these outputs.

| Recording | Published anchors / predicted candidates | ±3frame TP / FP / FN | Precision / recall / F1 at±3 | F1 at±6 | Correct known class on±3matches | Unknown predicted classes |
| --- | --- | --- | --- | --- | --- | --- |
| India singles |85 /89|64 /25 /21|71.91% /75.29% /73.56%|73.56%|3 /64|70 /89|
| Denmark singles |39 /33|25 /8 /14|75.76% /64.10% /69.44%|69.44%|1 /25|30 /33|
| Published doubles |45 /35|21 /14 /24|60.00% /46.67% /52.50%|67.50%|1 /21|27 /35|

Full157 prediction candidates,169 truth anchors, raw class confusions, unknowns, all misses/extras and all matched timing errors remain in `prod_20261105_external_{india,denmark,doubles}_reference_v1/`. Named-hitter prediction coverage is zero because no source-bound human identity mapping was supplied; anonymous geometry/track evidence remains distinct. Unknown predictions were not dropped from joint metrics.

Contact micro F1 across these three exposed recordings is 67.48% at±3 and71.17% at±6; recording macro F1 is65.17%/70.17%. Matched timing MAE is.6909/.9138frames respectively, conditional on110/116 matches; it does not hide59/53 missed anchors. Class/taxonomy results are not pooled across different published semantics. These are recording-level descriptive averages, not newly blind match-level validation. Small selected/exposed samples and unsealed match identities do not support meaningful generalization confidence intervals.

Test7 coarse rally agreement is29TP/3FP/2FN,F192.0635%,mean/median/minimumIoU.774815/.775161/.584013; startMAE33.8621,endMAE19.7586,durationMAE1.12299seconds. Maxstart242frames and maxend135frames remain. All 31 rows, unmatched predictions and both matched/all-GT tolerance denominators are in `prod_20261105_external_test7_reference_v1/`. The frozen Test1 scene arm remains36/0/0 with start28.25/end 10.4722 frames. Different recording bytes/annotation conventions and prior exposure limit this comparison; no blind generalization conclusion follows.

The independently reproduced Test7 chains expose two different missed-rally mechanisms. GT22's provisional 7557 candidate cancels after raw loss 7560–7583; the recreated `[7586,7695)` only overlaps the coarse reference below IoU .5. A real source edit7705→7706 correctly separates the next point. GT23's moving candidate 7798 lasts 49 evidence frames before closure/cancellation 7870 against the existing 60-frame duration gate; source becomes LOST only at 7872, so a later close-up does not explain that cancellation. GT3 splits after a 32-frame raw gap 1456–1487 under main/valid view with moving players. Original frames, own-cache/full-event baseline parity and bounded FSM traces are preserved in `prod_20261105_test7_semantic_causal_v2/` and the Test7 source-review packages. No global timeout, duration, fitted offset or merge rule was changed.

Two existing-provider alternatives were tested only through labelled, own-cache counterfactuals after exact baseline reproduction. Motion-reliability scoring collapses external recall and is rejected. Anonymous geometry brackets increase correct classes but also many wrong labels; selective accuracy remains 25–33%, so it stays shadow/opt-in. Their raw counts, source/frontier controls and rejections are in `prod_20261105_existing_provider_comparison_v1/`. These conditional cached studies are not additional neural runs or proof of physical calibration.

Measured failures therefore remain in contact/onset observability, shot coverage/accuracy, terminal continuity and identity. Independent physical labels and prospective match-disjoint validation remain missing as well. The honest release decision is FAIL/blocked, even though Test1 rally F1 is 1.0 and software contracts pass.
