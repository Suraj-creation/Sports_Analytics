"""Seal independent completed known-case source review; original evidence remains immutable."""
from pathlib import Path
import hashlib,json,subprocess,os,re
P=Path(__file__).resolve().parent;PKG=P.parent/'visual_test02_v5_known_cases_v1';MAIN=P.parents[4];CAND=MAIN.parent/'test03-scene-overlap-20261112'
def read(p):return json.loads(Path(p).read_text())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(n,d):
 with(P/n).open('x')as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
r=read(P/'frame_register.json');by={x['frame']:x for x in r};sheets=read(P/'sheet_index.json');v=read(P/'verification.json');assert len(r)==108 and len(sheets)==18
for s in sheets:assert sha(P/s['path'])==s['sha256']
assert sha(PKG/'executed_tool.py.source')==sha(CAND/'evaluation/ground_truth_validation/orchestration/render_validation_evidence.py')
centres={'recovered_prior_candidate_edits':[2928,11082,22416,23279],'earlier_weak_edit_cases':[355,699,1095,3394,4581,5958,11691,11985,25521],'other_edit_controls':[6151,6307,11346],'continuous_negative_controls':[7703,23639]}
cases=[]
for role,indices in centres.items():
 for n in indices:
  row=by[n];cut=role!='continuous_negative_controls';cur=row['arms']['current'];dec=cur['decision'];assert dec['decision']==('barrier'if cut else'no_barrier');assert len(cur['players'])==2 and all(p['detector_matched']for p in cur['players'])
  if cut:assert cur['epoch']==by[n-1]['arms']['current']['epoch']+1
  else:assert cur['epoch']==by[n-1]['arms']['current']['epoch']
  cases.append({'component':'foreground_scene_observer→current_detector_layout→epoch_reset→player_birth','video':'Test2','frame':n,'seconds':n/30,'role':role,'physical_ground_truth':None,'agent_visual_diagnostic':'same-camera temporal edit: discontinuous athlete locations'if cut else'continuous athlete motion/posture, no visible edit','actual_current':{'epoch':cur['epoch'],'raw_strong_hypothesis':cur['raw_scene']['hypothesis'],'decision':dec['decision'],'reason':dec['reason'],'players':2,'all_current_detector_matched':True},'baseline_people':len(row['arms']['baseline']['players']),'source_png':str(PKG/f'frame_{n:07d}'/'source_original.png'),'current_overlay':str(PKG/f'frame_{n:07d}'/'current_source_overlay.png'),'baseline_overlay':str(PKG/f'frame_{n:07d}'/'baseline_source_overlay.png')})
save('case_register.json',{'status':'completed_agent_review_of_predeclared_known_cases','physical_ground_truth':None,'case_count_is_not_failure_frequency':True,'cases':cases})
table='\n'.join(f"| {x['frame']} | {x['role'].replace('_',' ')} | {'edit'if x['actual_current']['decision']=='barrier'else'continuous'} | {'strong'if x['actual_current']['raw_strong_hypothesis']else'relative/court'} | {x['actual_current']['decision']} | {x['baseline_people']} → 2 fresh |"for x in sorted(cases,key=lambda x:x['frame']))
report='''# Test 2 V5: independent known-case source review

All **108 predeclared frames** were inspected as original source, preserved baseline overlay and actual current overlay: **324 panels on 18 aspect-preserving sheets**. The current run is the genuinely completed fresh Test 2 run from frozen commit `5ae614826e6f909defb02445386962ac13b4641a`; baseline is the original completed `dacc05e` Test 2 `improved_v1` neural run. This review covers selected known cases, not every new reset or every frame of the video.

Rendering waited for the actual worker and parent to complete, the catalogue to contain all **29,296 frames**, and timestamp auditing to finish with exit0, exact source/proxy PTS equality and a matching source-frame CSV hash. The readiness transition is retained in [observations](readiness_observations.jsonl). The frozen producer's original renderer then passed its genuine full-run/source guards; no guard was bypassed, ROOT rebased, header changed or receipt fabricated. The exact owned Test 2 source SHA256 is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`.

The completed package verifies **1,284 artifact hashes**, **1,015 recorded input bindings**, and **324 decoded image pixel/shape receipts**. Every source time equals the rational canonical time for both actual proxy arms. Original and frozen cache segments agree, and model/config/producer provenance is retained. The executed renderer bytes equal the frozen candidate's renderer. See [verification](verification.json), [frame register](frame_register.json), [sheet index](sheet_index.json) and [closed rendered bundle](../visual_test02_v5_known_cases_v1/index.md). This CPU-only work decoded source/proxy images and performed no neural inference or numerical benchmark recalculation.

## Scene reset and continuity controls

All four previously lost candidate resets—**2928, 11082, 22416 and 23279**—coincide with real same-camera source edits. The athletes abruptly change position while the court/broadcast view persists. Current records a strong scene hypothesis, a layout-confirmed barrier and two fresh detector-matched athletes at each. The original baseline also resets at these four locations, but emits no admitted people at the cut frame; current immediately acquires the visible pair. The older2418 candidate's loss of these resets was diagnosed separately; this package compares actual5ae with originaldacc, not with2418.

At2928 the near athlete jumps from a bent central posture into a leftward playing position while the far athlete relocates. At11082 both athletes move abruptly from the left side into central play. At22416 a near-net/bent state jumps into a separated near/far service-like layout, with a scoreboard transition. At23279 the overlapping near-net pair abruptly separates into a central near/far layout; current has no carried far-athlete box over the previous empty region. See [2928](sheet_04.jpg), [11082](sheet_10.jpg), [22416](sheet_15.jpg) and [23279](sheet_16.jpg).

The nine earlier weak-reset contexts remain source-supported edits:355,699,1095,3394,4581,5958,11691,11985 and25521. Current preserves the raw strong-hypothesis value **false** and uses the explicit relative-change/complete-current-court replacement proof. These are not strong hypotheses relabelled after the fact. Walking/off-court athletes jump to current central positions; several transitions also show scoreboard changes. At5958 the actual source edit is visible and current acquires the two athletes; the baseline retains the earlier background-region/official context before later acquisition. This evidence does not solve unrestricted identity handover during otherwise continuous footage.

Other source-supported strong controls6151,6307 and11346 also produce current barriers and two fresh athletes. Full-run11346 has enough genuine preceding foreground history to recover this edit; it must not be equated with the old cold-start prefix's unknown scene status. This package preserves the actual complete-run history.

At **7703** the near athlete continues a lunge and the far athlete maintains a coherent response. At **23639** the near athlete bends/walks toward the camera while the far athlete remains consistent. Both source sequences are continuous. Current records a raw strong hypothesis but **no_barrier** because the current layout positively corresponds to the preceding regions. Both controls keep two fresh athlete boxes at the centre frame. They remain useful controls against converting every foreground innovation into a cut. See [7703](sheet_09.jpg) and [23639](sheet_16.jpg).

| Frame | Predeclared role | Source diagnostic | Current evidence | Current decision | Baseline → current people |
|---|---|---|---|---|---|
'''+table+'''

The table contains **16 selected edit contexts and two selected continuity controls**. These are deliberately selected diagnostic examples, not a sampled physical scene precision/recall denominator. Source expectations are agent observations; original CSV annotations are untouched and no new physical GT labels were created. Exact source/overlay links and typed decision reasons are in [case register](case_register.json).

## Preparation, short exchange and cadence limitations

The early809/850 source frames still show preparation/held positioning. Frames900/904/907 show the later near-athlete service-like movement and departure. Current's raw shuttle association is unknown at809/850, with reacquisition at900 and tracked observations904/907. Neither an old high contact score nor a new tracked point establishes exact physical impact, class, named hitter or a legal point.

The sampled short-event sequence11700/11710/11715/11716/11731/11740/11751/11774 retains two source-aligned people with current-source pose in both arms. Source preparation progresses to near-athlete action/departure, far-athlete return-like action and forward movement/aftermath. No obvious athlete-hypothesis break is visible in these selected frames. Exact impacts and rally boundaries remain unlabelled. This source package does not decide whether the formal short-event admission is correct, recover11715 as a physically probable impact, or replace the independent numerical event/IoU comparison. See [short exchange](sheet_13.jpg). The previously sealed continuous197-frame source review remains a separate historical source study; it is not being represented as a fresh5ae full-timeline semantic result.

The **cadence limitation persists** in the actual current run. At sampled25680,25681,25710 and25739, current uses perception stride6 while original baseline uses stride1, despite visible active play. Current has fresh detection/pose at25680 and25710 but carried boxes and no current pose at25681/25739. At25740 both return to stride1 and fresh detection/pose. The selected carried boxes still cover the moving athletes with ordinary lag; this does not remove the lost temporal pose coverage. These five samples confirm the scheduling difference; they do not independently reproduce the complete FSM feedback cause or certify physical player accuracy. See [cadence samples](sheet_18.jpg).

## Scope and preservation

The initial predeclared source controls pass their specific visual expectations, while sparse scheduling and physical contact/classification uncertainty remain. Whole-video component metrics, all newly changed regions, additional reset contexts, raw shuttle quality and final Test 2 acceptance belong to the separate completed-run numerical and source reviews. This package makes no blanket claim of unchanged shuttle output, aggregate physical accuracy or pipeline acceptance.

Every original source video, annotation, prediction, historical evaluation and active downstream output remains intact. Candidate source files were not modified. The parent orchestrator retains control of acceptance, merge/push and eventual cleanup.
'''
(P/'REPORT.md').write_text(report)
links=re.findall(r'\]\(([^)]+)\)',report);assert all((P/x).exists()for x in links)
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=CAND,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'},text=True).strip()=='5ae614826e6f909defb02445386962ac13b4641a';assert subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=CAND,env={**os.environ,'GIT_OPTIONAL_LOCKS':'0'},text=True)==''
art={q.name:sha(q)for q in P.iterdir()if q.is_file()}
save('verification_receipt.json',{'status':'completed_independent_predeclared_known_case_source_review','frames_visually_reviewed':108,'source_baseline_current_panels_reviewed':324,'aspect_preserving_sheets_reviewed':18,'all1284_artifacts1015_inputs324_pixels_verified':True,'selected_source_supported_edits':16,'selected_continuity_controls':2,'physical_ground_truth':None,'physical_scene_precision_recall_claimed':False,'new_neural_inference':False,'source_proxy_decode':'CPU only frozen renderer after actual completion and timestamp gates','new_metrics_computed':False,'all_candidate_source_unchanged':True,'parent_pipeline_acceptance_claimed':False,'all_local_report_links_exist':True,'artifact_sha256':art,'frame_plan_sha256':sha(P.parent/'test02_v5_known_cases_frame_plan_v1.json'),'closed_render_completion_sha256':sha(PKG/'completion.json')})
print('sealed',len(art),'owned artifacts; report',sha(P/'REPORT.md'),'receipt',sha(P/'verification_receipt.json'))
