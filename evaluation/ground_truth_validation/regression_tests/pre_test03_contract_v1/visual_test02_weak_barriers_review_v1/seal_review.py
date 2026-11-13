"""Seal a diagnostic source review; no model or event-store access."""
from pathlib import Path
import hashlib
import json
import re

OUT = Path(__file__).resolve().parent
PACKAGE = OUT.parent / 'visual_test02_weak_barriers_v1'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as s:
        for b in iter(lambda:s.read(1024*1024),b''): h.update(b)
    return h.hexdigest()
def write(p,v):
    with p.open('x') as f: json.dump(v,f,indent=2,allow_nan=False);f.write('\n')
v=json.loads((OUT/'verification.json').read_text()); m=json.loads((OUT/'machine_readout.json').read_text())
weak={
355:('Near red athlete moves from bottom-left walk to near centre; far blue athlete relocates right.','0:0 → 0:1'),
699:('Near red athlete relocates from right to centre and far blue athlete from centre to left.','0:1 → 0:2'),
1095:('Near red athlete relocates right-to-left while far blue athlete relocates left-to-right.','0:2 → 1:3'),
3394:('Red athlete outside right runoff and blue athlete near far/net middle abruptly become near-centre red and far-right blue.','6:6 → 7:7'),
4581:('Both athletes relocate from left-side walking positions to central active positions.','9:9 → 9:10'),
5958:('Blue athlete outside far-left and red athlete near-left abruptly relocate into central active positions.','9:13 → 10:13'),
11691:('Near blue athlete relocates from left-side walk to centre; far red athlete relocates centre-to-right.','5:1 → 7:1'),
11985:('Near blue athlete relocates from left-side bend to centre; far red athlete relocates centre-to-right.','8:1 → 9:1'),
25521:('Near blue athlete changes from left-side bend/pickup to right-central position; far red athlete returns from far-left runoff to centre.','14:15 → 14:16'),
}
controls={
6151:('source_supported_edit','Abrupt athlete relocation and displayed10:13 → 10:14; strong current barrier returns two fresh athletes; baseline retains three stale/official-position boxes.'),
6307:('source_supported_edit','Abrupt relocation and displayed10:14 → 12:14; strong current barrier returns two fresh athletes; baseline carries prior three positions.'),
6492:('official_alias_countercontrol','Source sequence is continuous play. Both arms have two fresh boxes, but baseline includes seated official and misses near red athlete; current boxes cover the two visible athletes. Counts alone hide the error.'),
7703:('ordinary_motion_no_reset','Red athlete lunges during continuous play, display14:17 unchanged. Baseline raw hypothesis is vetoed by positive layout; current has no raw hypothesis/decision and carries two boxes without detector execution. No reset does not imply equal freshness or localisation.'),
11333:('additional_test2_context_only','Test2 athletes walk outside on right; both arms admit one far red person, current also retains near blue scene context. This is not Test1 frame11333 and cannot validate its carried-lunge error.'),
11346:('source_supported_edit_full_history','Abrupt relocation and current-game display4:0 → 5:1. Full-native current produces strong barrier and two fresh athletes; baseline has zero persons at11346 and11347. Earlier bounded cold-prefix unknown is a different history scope.'),
13153:('additional_test2_context_only','Ordinary Test2 context with two persons and no reset. This is not Test1 frame13153 and cannot validate its raw shoe alias.'),
23639:('ordinary_motion_positive_veto','Continuous bend/posture change, display9:15 unchanged. Both arms have raw hypothesis true and no_barrier positive layout; epochs remain stable. No shuttle/contact correctness follows.'),
}
cases=[]
for f,(obs,score) in weak.items():
    assert m[str(f)]['current']['raw_hypothesis'] is False
    assert m[str(f)]['current']['decision']=='barrier'
    assert m[str(f)]['current']['fresh_people']==2
    cases.append({'case_id':f'T2-WEAK-{f:05}', 'video':'Test2','frame':f,'timestamp_seconds':f/30,'review_frames':list(range(f-2,f+2)), 'ground_truth':None,'annotation_role':'agent-reviewed source diagnostic, not original CSV or physical ground truth','classification':'source_supported_same_camera_edited_jump','source_observation':obs,'manual_broadcast_top_bottom_current_column':score,'score_scope':'visual corroboration only; no named-player/winner/point ground truth','prediction':m[str(f)],'sheet':f'weak_{f:05}.png','source_evidence':str((PACKAGE/f'frame_{f:07}'/'evidence.json').resolve())})
for f,(kind,obs) in controls.items():
    cases.append({'case_id':f'T2-CONTROL-{f:05}','video':'Test2','frame':f,'timestamp_seconds':f/30,'review_frames':[f-1,f,f+1],'ground_truth':None,'annotation_role':'agent-reviewed source diagnostic only','classification':kind,'source_observation':obs,'prediction':m[str(f)],'sheet':f'control_{f:05}.png','source_evidence':str((PACKAGE/f'frame_{f:07}'/'evidence.json').resolve())})
g69=[int(k) for k in m if int(k)>=27300]
assert all(m[str(f)]['baseline']['shuttle']==m[str(f)]['current']['shuttle'] and m[str(f)]['baseline']['shuttle_support']==m[str(f)]['current']['shuttle_support'] for f in g69)
review={'schema':'independent-source-diagnostic-review:v1','native_producer_commit':'2418ab8cbe4cca74dd16b722b9727ffdc950294a','physical_ground_truth':None,'metrics_inferred_from_visuals':False,'review_scope':{'frames':75,'sheets':20,'visually_reviewed_panels':225,'rendered_package_pngs':600,'pixel_receipts_checked':225,'new_video_decode':False,'new_NN':False},'cases':cases,'g69':{'frames':g69,'ground_truth':None,'observation':'Partial upper-edge outgoing object at27326–28; flight outside image is unobservable. Accepted lower branch27348–53 follows visible near racket-head region; clear bright upper return27354 onward. These are diagnostic observations, not contact or trajectory labels. No edit is supported in selected sequence.','raw_xy_and_support_exact_between_arms':True,'scene_reset_in_selected_frames':False,'sheets':['g69_exit.png','g69_reacquisition_01.png','g69_reacquisition_02.png'],'not_established':['22 physical false negatives','physical flight across outside-image gap','current full FSM equality','G69 repair']},'all75_raw_readout_exact_count':sum(a['baseline']['shuttle']==a['current']['shuttle'] and a['baseline']['shuttle_support']==a['current']['shuttle_support'] for a in m.values()),'scope_correction':v['scope_correction'],'limitations':['Selected development contexts are not an exhaustive independently annotated scene-cut dataset.','Nine source-supported resets do not establish scene precision or recall.','No named identity, winner, contact, stroke class, pose, AP or physical tracking accuracy is inferred.','Full postprocessing completion and numeric evaluation have separate gates.']}
write(OUT/'review.json',review)
rows='\n'.join(f"| {f} / {f/30:.3f}s | {obs} | {score} | [sheet](weak_{f:05}.png) |" for f,(obs,score) in weak.items())
controls_md='\n'.join(f"- **{f} ({kind}):** {obs} [Source/baseline/current sheet](control_{f:05}.png)." for f,(kind,obs) in controls.items())
text=f'''# Independent Test2 source review: nine weak scene resets

All nine selected weak-reset contexts show an abrupt same-camera edited jump in the source sequence. The native current run returns two fresh visible-athlete boxes at each reset, instead of retaining the old scene positions. These are agent-reviewed diagnostic findings; physical ground truth remains **null**. Nine selected supported cases are not a precision/recall estimate.

## Bound evidence and scope

The current producer is `2418ab8cbe4cca74dd16b722b9727ffdc950294a`; baseline is the preserved Test2 `improved_v1` full run. The source SHA is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`. The [original sealed package](../visual_test02_weak_barriers_v1/completion.json) binds actual worker, model, source, proxy, configuration and per-frame provenance. The worker processed all29296frames; the historical outer analysis failure is separate from this review and is not relabelled completed here.

Rehashed905 rendered outputs and1015 recorded input bindings (1010unique paths), plus225 source/proxy pixel receipts. Visually reviewed75 source-frame contexts across20 aspect-preserving sheets:225 source/baseline/current panels. The original package contains600PNGs; this review does not claim all600 were separately visually inspected. Source1920×1080 and overlay1280×890 images are scale-fit with letterboxing and never stretched to a common aspect ratio. No video re-decoding or inference was performed. [Verification](verification.json); [machine readouts](machine_readout.json); [structured review](review.json).

## Selected weak resets

Every listed current packet has raw `hypothesis=False`, validated `barrier`, an epoch increment of one from its previous frame, and two fresh persons. The raw false flag remains false; the typed weak acquisition proof supplies reset authority. Source relocation supports an edit rather than ordinary motion in these examples.

Broadcast numbers below are manually observed top-row:bottom-row rightmost/current columns, used only as corroborating source context. Historical game columns, named player identity, point attribution and winner correctness are not inferred.

| Frame / source time | Source change | Display before → after | Evidence |
|---|---|---|---|
{rows}

## Controls and limitations

{controls_md}

**Plan scope correction:** the sealed frame plan combined previous carry/shoe rationale with Test2 frames11333/13153. Those numbers belong to different Test1 diagnostics. The rendered Test2 images are valid additional source context, but cannot validate the Test1 carried-lunge or shoe-alias findings. The original plan and artifacts remain unchanged.

The5958 source edit explains the historical official-context carryover in this selected sequence. It does not prove that a generic uninterrupted athlete-to-official handover is solved. Likewise, before3394 the source includes an off-court visible athlete while only one person is admitted; successful scene context is not universal player coverage.

## G69 remains unresolved

[Exit sheet](g69_exit.png), [lower return sheet](g69_reacquisition_01.png), [upper return sheet](g69_reacquisition_02.png) show the partial outgoing upper-edge object at27326–28, unobservable flight outside the image, the lower accepted racket-like branch at27348–53, and the bright upper return from27354. Both arms retain two persons and no scene reset in the15 selected frames. Their raw shuttle coordinates and support values are exactly equal on those15frames, including absence. This equality is scoped: only51/75 selected frame raw readouts are exactly equal overall.

The selected images do not establish22 physical false negatives, a continuous physical trajectory, a class/contact label, or current full FSM parity. No G69 repair is claimed. The earlier [source-bound gap diagnosis](../../../../component_evaluations/pre_test03_shuttle_gap_v1/REPORT.md) and [exit-recovery contract audit](../../../../component_evaluations/pre_test03_shuttle_gap_v1/exit_contract_audit_v1/REPORT.md) retain their distinct old-run scope.

## Acceptance boundary

These source controls support the selected scene-reset behavior and expose meaningful distinctions: official box versus athlete box, positive layout veto versus absent observer evidence, full-history versus cold-prefix behavior, and visible alias versus outside-image uncertainty. They do not establish physical tracking AP, named identity, winner accuracy, contact precision or stroke correctness. Full numeric evaluation, immutable-artifact verification and any final pipeline acceptance remain separate.
'''
# Relative links to component_evaluations are three parents above this report, not four.
text=text.replace('../../../../component_evaluations/', '../../../component_evaluations/')
with (OUT/'REPORT.md').open('x') as f:f.write(text)
completion=json.loads((PACKAGE/'completion.json').read_text())
for rel,digest in completion['artifact_sha256'].items(): assert sha(PACKAGE/rel)==digest,rel
for item in completion['input_bindings']:
    # Equal paths may be recorded multiple times by renderer; every binding must agree.
    assert sha(item['path'])==item['sha256'],item['path']
assert sha(PACKAGE/'completion.json')==v['package_completion_sha256']
links=[]
for target in re.findall(r'\]\(([^)]+)\)',text):
    path=(OUT/target).resolve();assert path.exists(),str(path);links.append(str(path))
write(OUT/'verification_receipt.json',{'status':'completed_independent_visual_diagnostic_review','package_completion_sha256':sha(PACKAGE/'completion.json'),'all905_rendered_artifacts_unchanged':True,'all1015_input_bindings_reverified':True,'225_pixel_receipts_preverified':True,'all_local_report_links_exist':True,'report_link_count':len(links),'source_physical_GT':None,'parent_pipeline_acceptance_claimed':False,'artifact_sha256':{str(p.relative_to(OUT)):sha(p) for p in sorted(OUT.rglob('*')) if p.is_file()}})
print('sealed',len(cases),'cases + G69;',len(links),'links')
