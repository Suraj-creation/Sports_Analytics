"""Seal already performed independent visual review; never changes rendered packages."""
from pathlib import Path
import hashlib,json,re,subprocess
P=Path(__file__).resolve().parent;MAIN=P.parents[4];BASE=MAIN/'evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_text())
def save(n,d):
 with(P/n).open('x')as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
ver=load(P/'input_verification.json');sheets=load(P/'sheet_index.json');frames=load(P/'frame_register.json')
assert len(frames)==197 and len(sheets)==25
for s in sheets:assert sha(P/s['path'])==s['sha256']
# Bind the independent completed reviews used to reconcile coverage; no claims of redoing their visual work.
prior=[('visual_test02_weak_barriers_review_v1','verification_receipt.json'),('visual_test02_pending_v2_batches_01_02_review_v1','completion.json'),('visual_test02_pending_v2_batch_03_04_review_v1','verification_receipt.json')]
prior_receipts={}
for name,filename in prior:
 p=BASE/name;d=load(p/filename)
 for rel,h in d['artifact_sha256'].items():assert sha(p/rel)==h,(name,rel)
 prior_receipts[str(p/filename)]=sha(p/filename)
names=['visual_test02_weak_barriers_v1','visual_test02_delayed_start_row03_v1','visual_test02_lost_short_event_v1']+[f'visual_test02_pending_v2_batch_{i:02d}'for i in range(1,5)]
u=set();counts={};bindings={}
for n in names:
 f=BASE/n/'completion.json';d=load(f);s=set(d['frames']);u|=s;counts[n]=len(s);bindings[str(f)]=sha(f)
plan=BASE/'test02_postprocessing_independent_v1/source_frame_plan.json';planned={x['frame']for x in load(plan)['frames']};assert len(planned)==664 and not(planned-u)
save('coverage_reconciliation.json',{'status':'all_requested_positions_have_completed_visual_review','source_sha256':'4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a','planned_unique_frames':664,'rendered_rows_across_packages':sum(counts.values()),'reviewed_unique_positions':len(u),'additional_context_positions':len(u-planned),'missing_requested_positions':[],'current_direct_review_frames':197,'direct_review_panels':591,'package_counts':counts,'package_completion_sha256':bindings,'prior_closed_visual_review_receipts_sha256':prior_receipts,'requested_plan_sha256':sha(plan),'physical_accuracy_claimed':False,'newest5ae_run_acceptance':False})
current=MAIN.parent/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_postprocessing_v1';before=MAIN.parent/'ground-truth-validation-artifacts-20261110/test_02/improved_v1'
cmp=load(current/'comparison.json');a=load(before/'bound_reference_diagnostics/reference_row_comparisons.json');b=load(current/'bound_reference_diagnostics/reference_row_comparisons.json')
snapshot={'scope':'copy of original completed2418 numeric results, no reevaluation or relabelling','metric_inputs_sha256':{str(f):sha(f)for f in [current/'comparison.json',before/'bound_reference_diagnostics/reference_row_comparisons.json',current/'bound_reference_diagnostics/reference_row_comparisons.json']},'all_interval_reference_detection_overlap':{n:{'role':v['role'],**{arm:{'detection':v[arm]['detection'],'overlap':v[arm]['overlap']}for arm in ['baseline','candidate']}}for n,v in cmp['interval_references'].items()},'selected_rows':{}}
for n in a:
 ids=[3,33]if n=='Test2_Full.csv'else[3]
 snapshot['selected_rows'][n]={str(i):{arm:next(z for z in d[n]['comparison']if z.get('gt_rally')==i)for arm,d in [('baseline',a),('candidate',b)]}for i in ids}
save('preserved_metric_extract.json',snapshot)
observations=[{'id':'row03_preparation','frames':[800,899],'visual_diagnostic':'Continuous walking/settling then held service preparation; no independent outgoing rally event established at809.','physical_gt':None}, {'id':'row03_action','frames':[900,910],'visual_diagnostic':'Near red athlete makes service-like forward racket action and far blue athlete prepares/reacts; visible departure near904–907.','draft_boundary_uncertainty_frames':[900,907],'exact_impact_gt':None,'class_gt':None}, {'id':'short_edit','frames':[11690,11691],'visual_diagnostic':'Abrupt relocation of both athletes with fixed camera/background; real same-camera temporal edit. Current resets20→21 and returns fresh boxes; baseline retains epoch13 and stale prior near position at11691.','physical_gt':None}, {'id':'short_preparation','frames':[11691,11712],'visual_diagnostic':'Near blue athlete holds/prepares racket while far red athlete approaches ready position.','physical_gt':None}, {'id':'short_departure','frames':[11710,11721],'visual_diagnostic':'Near blue action and small bright airborne trace rising away toward far red athlete. Exact impact unresolved.','draft_boundary_uncertainty_frames':[11710,11716],'exact_impact_gt':None,'class_gt':None}, {'id':'short_reply','frames':[11722,11745],'visual_diagnostic':'Far red athlete adjusts and performs return-like racket movement while near blue athlete reacts forward. Missing raw11732–33 retained;11734 is reacquisition. No additional visible edit.','exact_impact_gt':None,'class_gt':None}, {'id':'short_aftermath','frames':[11746,11775],'visual_diagnostic':'Near blue athlete continues toward net; both settle at front court; no further visible edit. Exact end/winner unresolved.','winner_gt':None,'end_boundary_gt':None}]
save('visual_observations.json',{'status':'completed_independent_agent_visual_diagnostics','all197_frames_source_baseline_current_reviewed':True,'all25_sheets_reviewed':[x['path']for x in sheets],'additional_detail_sheets':['row03_service_detail.jpg','short_launch_detail.jpg'],'selected_original_size_frames':[904,11715,11718,11740],'cases':observations,'no_physical_ground_truth_created':True,'no_accuracy_metrics_recomputed':True})
root=MAIN.parent/'test03-scene-overlap-20261112';assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()=='5ae614826e6f909defb02445386962ac13b4641a';assert subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=root,text=True)==''
report='''# Test 2: complete contiguous source review

All 111 frames at **800–910 (26.667–30.333 s)** and all 86 at **11690–11775 (389.667–392.500 s)** were visually inspected with their preserved baseline and current overlays: 197 distinct source positions and 591 panels across 25 aspect-preserving sheets. Selected original-size sources (904, 11715, 11718, 11740) and two closer source-crop sequences supplement the sheets. This is an independent agent diagnostic review; physical contact, class, winner and exact boundary ground truth remain unavailable.

Here “baseline” means the completed Test 2 `improved_v1` fresh neural run; “current” means the completed `2418ab8` candidate-v4 neural run. These are the actual two producer caches used by the closed renderer. They are **not** outputs from the newer frozen `5ae6148` candidate whose Test 1 validation is underway. The retained model metadata identifies TrackNetV3@3.0, RF-DETR small@1.4.2, RTMPose@1.0 and the geometric racket observer. The current scene/tracking policy versions differ from the baseline, as recorded per frame. Appearance, track numbers and scoreboard row names do not establish physical named identity.

The closed packages pass all **2,263 artifact hashes**, **2,030 recorded input bindings**, and **591 image pixel/shape receipts**. Every source/canonical proxy timestamp agrees at the rational frame time; each original cache segment agrees with its frozen snapshot. The two packages bind the same source SHA256 `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`. PNG pixels were read back and hashed as BGR arrays, consistent with the original decoder receipt. This review performs no new video decoding, neural inference, numeric evaluation or pipeline edit. See [input verification](input_verification.json), [frame register](frame_register.json) and [sheet index](sheet_index.json).

## Window 800–910: preparation and later action

Across every frame, court/background and both athletes evolve continuously; there is no visible temporal edit. At 800–823 the athletes take small settling steps. From about 824 onward, the near red athlete holds the service posture while the far blue athlete waits. Frame 809 remains part of that preparation. A high contact-fusion value there is insufficient to establish physical impact or rally onset.

The near athlete's forward racket movement and departing bright trace become apparent around 904–907, with the far athlete in a receiving posture and subsequently reacting. A deliberately broad **draft action-onset review range of 900–907** is reasonable for a future labelled review. It is not an exact service/contact label, accepted benchmark correction or calibrated confidence interval. See [all final service frames](row03_13.jpg), [904–910](row03_14.jpg) and [closer source sequence](row03_service_detail.jpg). The independent source review does not determine the full rally end because this source window stops at 910.

The recorded metric difference must remain visible. Against generated rally row 3 `[807,1040)`, baseline `[809,1039)` has IoU **0.9871244635**, while current `[904,1039)` has **0.5793991416**; start error increases from +2 to +97 frames. Against coarse row 3 `[900,1080)`, the same predictions have IoU **0.5129151292 → 0.75**, with start error −91 → +4 frames. These conflicting reference agreements are preserved, rather than redefining reference start 807 from visual interpretation. The source sequence explains why agreement with the earlier generated boundary need not measure physical service accuracy.

## Window 11690–11775: edit, preparation, short exchange

The transition **11690→11691** abruptly relocates both athletes while court and broadcast layout remain fixed. It is a real same-camera temporal edit. Current scene epoch changes **20→21**, invokes fresh detection, removes the old near-position context and returns two athlete boxes. Baseline stays in epoch 13 at that instant, with the old near box over the previous location. This is a scene-state distinction; it does not prove that either subsequent contact timestamp is correct. See [edit and immediate continuation](short_01.jpg).

From 11691 through roughly 11712, the near blue athlete prepares/holds the racket and the far red athlete moves into readiness. Around 11713–11718 the near athlete's action is followed by a small bright airborne trace departing toward the far athlete. A broad **draft first-action review range of 11710–11716** preserves uncertainty about the exact impact. The source at 11715 already contains a small free bright trace above the near athlete; accepting that frame as exact impact solely because an older fusion score peaked there would be unjustified. See [launch source detail](short_launch_detail.jpg) and [11714–11721](short_04.jpg).

Through 11722–11745 the far athlete adjusts and makes a return-like racket movement as the near athlete reacts forward. Frame 11740 gives useful full-size evidence of this action and a nearby bright projectile. The original raw observations remain missing at 11732–11733, followed by reacquisition at 11734; this review does not turn those frames into observed coordinates. The near athlete then continues toward the net and the athletes settle near the front court through 11775. **There is no further visible temporal edit anywhere in 11691–11775.** Exact impacts, number of valid shots, shot classes, point winner and legal rally end remain unlabelled. See [reply](short_06.jpg), [return movement](short_07.jpg) and [aftermath](short_08.jpg).

The coarse reference row 33 `[11700,11760)` was matched by baseline `[11715,11751)` at IoU **0.6** and is missed by current. The source supports a genuine short action sequence in this region, so the lost coarse event remains a material diagnostic limitation. It does not justify promoting the unreliable 11715 candidate to a physically probable impact or lowering a global candidate threshold. Existing bounded probes show its score **0.905434 → 0.282427**, below unchanged 0.35 selection; old incoming direction was below measured localization uncertainty. Current later candidates alone do not provide the old two-opponent short-exchange proof. This review adds visual chronology to that causal investigation and leaves the physical contact verdict unknown.

## Retained metrics and review coverage

| Reference | Baseline F1 → current F1 | Mean matched IoU before → after |
|---|---:|---:|
| Coarse `Test2_Full.csv` | 0.920000 → 0.912752 | 0.830665 → 0.838095 |
| Generated `Test2_Full_rally.csv` | 0.918919 → 0.925170 | 0.849311 → 0.830790 |
| Generated `win_predictions.csv` interval agreement | 0.918919 → 0.925170 | 0.849311 → 0.830790 |

These are copied from the completed comparison, with original matching policy and conditional IoU denominators; no metric was recalculated or relabelled. Winner accuracy is not inferred from the interval agreement. Exact detection counts, per-row boundary/duration errors and source JSON hashes are in [preserved metric extract](preserved_metric_extract.json).

The separate sealed reviews cover the 75 initial controls and all four pending batches (128+128+128+66). Adding this actual contiguous review closes the earlier visual-coverage gap. Their seven package frame sets contain 722 rendered rows but **719 distinct positions**, covering all **664 requested plan positions** plus 55 additional context positions. This is set-based coverage of a diagnostic selection, not 664 independent labelled examples, exhaustive video review or aggregate physical accuracy. Existing review receipts and artifact hashes were checked; [coverage reconciliation](coverage_reconciliation.json) preserves their separate authorship and lineage.

No original annotation, rendered evidence, candidate source, active worker output or previous result changed. The newer Test 1/Test 2 acceptance and eventual merge/cleanup remain separate gates.
'''
(P/'REPORT.md').write_text(report)
links=re.findall(r'\]\(([^)]+)\)',report)
assert all((P/x).exists() for x in links)
art={x.name:sha(x)for x in P.iterdir()if x.is_file()}
save('verification_receipt.json',{'status':'completed_independent_contiguous_source_review','frames_visually_reviewed':197,'source_baseline_current_panels_reviewed':591,'aspect_preserving_sheets_reviewed':25,'additional_detail_sheets_reviewed':2,'original_size_source_frames_reviewed':[904,11715,11718,11740],'all2263_closed_artifacts_verified':True,'all2030_recorded_inputs_verified':True,'all591_image_pixel_receipts_verified':True,'physical_ground_truth':None,'new_NN':False,'new_source_decode':False,'metrics_recomputed':False,'candidate5ae_tracked_source_unchanged':True,'parent_pipeline_acceptance_claimed':False,'all_local_report_links_exist':True,'artifact_sha256':art})
print('sealed',len(art),'owned artifacts;197frames591panels;664plan covered719unique incl55extra')
