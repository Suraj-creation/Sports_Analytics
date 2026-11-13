"""Seal the completed visual review without modifying producer artifacts."""
from pathlib import Path
import hashlib,json,re

OUT=Path(__file__).resolve().parent
ROOT=OUT.parent
NUMERIC=ROOT/'test02_postprocessing_independent_v1'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def save(n,x):
    with (OUT/n).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
verified=json.loads((OUT/'verification.json').read_text())
rows=json.loads((OUT/'machine_readouts.json').read_text())
page_notes={
1:'13080→13081 source jump; current immediate athlete births versus baseline empty at13081. Later near-blue overhead motion has carried-box context, without contact/class adjudication.',
2:'Close athlete image overlap at13436; side walking13451 jumps to central positions13452. Current fresh bodies restore coverage; old rectangles remaining cyan are scene context only.',
3:'Current fresh bodies at13556/58 visually cover athletes; far head/branding-like raw racket contours remain estimates.13790→13791 source reset to central play, current fresh bodies versus baseline carry.',
4:'Far-red athlete outside upper-right at14106 returns central at14107. Current immediate fresh births; subsequent near/far image overlap limits precise foot/contact assessment.',
5:'14293→14294 genuine source jump with current fresh people versus baseline none.14369far-red extended posture carries forward; no class/contact truth.',
6:'14370/75 fresh bodies generally cover visible active movement.14453has an empty carried near-left region in both arms while actual near-red is centre-right; current reacquires near-red at14454, baseline does not yet.',
7:'Near-red outside bottom edge at14889 returns central at14890edit; current two fresh bodies, baseline empty.15035/36near-red/far-blue active action; no impact label.',
8:'15415partially visible near-red at lower-left has no admitted body; scene context alone persists.15416/17current bodies restored at source jump, baseline none.15621both visible bodies admitted.',
9:'15622broadcast dissolve/view transition;15623current carried far-region offset and missing near athlete while calibration REACQUIRING.15625current fresh bodies return.15762lunge/15904opposite-side lunge source motion visible, no exact impact assertion.',
10:'Active near-red/far-blue stroke-like postures15914/32/66/16026; raw racket estimates remain unverified.16090closeup excluded from body analytics.',
11:'16091wide-view reacquisition returns two current bodies while baseline empty.16211/12/17and16495fast lateral play has carry versus fresh cadence differences; no physical class truth.',
12:'16556closeup excluded;16557return to wide view supplies current bodies versus baseline empty.17241→17242source jump and current fresh bodies;17243carry within new source scene.',
13:'17420dissolve/excluded transition then17421wide source current reacquisition.17507/08/13far-blue lateral action has varying box freshness without physical contact adjudication.',
14:'17662→17663same-camera source jump;17991offcourt near-red relocates central at17992. Current fresh bodies at resets versus baseline empty.',
15:'18369far-blue outside right returns centre at18370edit; current fresh bodies while baseline absent.18992offscreen/partially visible near-red,18993source jump current bodies versus baseline old far box.',
16:'18995remaining cyan old rectangles are scene-only.19109/10/15and19207visible continuous active near/far positions; raw racket/body cues do not label impacts.',
17:'19537near-red outside left,19538/39source jump with current bodies.20060dissolve/close view is excluded; no treating detected absence there as player FN.',
18:'20061return to wide source view supplies current bodies.20909→20910source jump;21071walking near-red and far-blue body carry. No match intent inferred.',
19:'21072/77fresh/carry cadence differs across arms.21737far-red outside left not admitted,21738current retains near-blue while original drops both; scene context is not participant authority.',
20:'21791/92/97and21821/22show slow preparation/positioning with carried/fresh pose variations. No contact truth from static readiness posture.',
21:'22415→22416confirmed edited source jump, display8:11→9:12, baseline cut versus current no epoch change. Current fresh bodies are correct broad regions while old rectangles remain only foreground.22608active pair.',
22:'22617/34/54similar preparation then22724active exchange; current/old bodies broadly correspond at these samples. No proposed threshold or physical labels.',
23:'22760/22846visible athletic action;22846class change remains unlabelled.22875carry,22945walking,22946source reset with current fresh bodies versus baseline none.',
24:'23278→23279source edited jump despite unchanged9:15display. Current admits two carried old boxes; old far box covers empty left area and misses relocated red athlete. Fresh current far birth at23280;23389carry inside new scene.',
25:'23305/394/407/408/486show active exchanges; carry can lag during lunge and fresh observations recover body shape. Exact contact and stroke classes remain unsupported.',
26:'23525/26near-blue overhead posture,23629near-blue bend/lunge;23696→23697source reset from edge positions to central play with current two fresh bodies.',
27:'23999/24000/24001continuous visible action with freshness changes;24099dissolve excluded and24100current immediate wide-view births.',
28:'24101carry in wide view;24390→24391source position/score jump, current fresh bodies versus baseline none.24779/80athletic postures cannot verify hit timing.',
29:'24781body/pose cadence variation;25207→25208source reset with current immediate births.25317near-blue overhead preparation, unverified contact.',
30:'25318/19carry/fresh variation;25523/29baseline stale left boxes while current bodies correspond to active central source positions.25689visible active source but current sparse cadence/no pose versus baseline active cadence.',
31:'25690/91/95/96/97show active near-blue/far-red source; current holds boxes and lacks current pose sampling under ps6 while baseline ps1. This is sparse scheduling, not geometry exclusion.',
32:'25713/14/15/19/20near-blue overhead/lateral movement continues; current carried box trails body versus original fresh/posed observations. No class confirmation.',
33:'25721/25/26/27/31current carried bodies and absent current pose continue during visible action. Retain scheduling/coverage limitation without inventing detector outputs.',
34:'25732/33/36carried near-blue box lag visible;25736class drop→unknown has unresolved fresh-player evidence. By25743current pose stride1 resumes and25770fresh bodies appear.',
35:'25898/25936active pairs;26016walking with unverified raw racket contour over body.26057→26058source reset with current fresh athletes versus baseline absent.',
36:'26059new-scene carry;26293far-red net-side action cannot certify net_shot class.26502→26503offcourt right-to-centre source reset with current fresh bodies.26716ordinary active pair.',
37:'26717carry/fresh contrast;27663→27664source reset with current bodies, baseline none.27875near-blue lunge, exact shuttle contact unknown.',
38:'27876/81source near-blue movement; baseline temporarily lacks near-body coverage while current has it.27954closeup excluded;27955wide current births.28706active source pair.',
39:'28706→28707source edit with current immediate births;28977→28978clear edge-to-centre source/score jump, current bodies while baseline absent;28979carry consistent with newly acquired scene.',
}
assert set(page_notes)==set(range(1,40))
classes=json.loads((NUMERIC/'event_differences.json').read_text())['stroke']['same_anchor_changes']
class_extract=[]
for c in classes:
    if c['frame'] in (22846,25736,26293):
        keys=['stroke','classification_status','classification_abstention_reason','physical_event_status','hypothesis_status','hypothesis_reason','flight_time_s','speed_px_s']
        class_extract.append({'frame':c['frame'],**{a:{k:c[a].get(k) for k in keys} for a in ['before','after']},'physical_ground_truth':None})
extended=[]
for row in rows:
    d=Path(row['evidence_json']).parent;extra={}
    for arm in ['baseline','current']:
        raw=json.loads((d/f'{arm}_raw_frame.json').read_text())
        extra[arm]={'view':raw['v'],'calibration':raw['cs'],'detector_observed':raw['do'],'pose_stride':raw['ps'],'people':[{'raw_track':p['t'],'detector_matched':p['dm'],'pose_frame':p['pf'],'pose_present':p['k'] is not None} for p in raw['p']]}
    extended.append({'frame':row['frame'],'arms':extra,'ground_truth':None})
save('extended_freshness_readout.json',extended)
case_rows=[]
for i,page in enumerate(verified['pages'],start=1):
    for frame in page['frames']:
        raw=next(r for r in rows if r['frame']==frame)
        case_rows.append({'frame':frame,'source_time_seconds':frame/30,'review_page':page['page'],'source_diagnostic_context':page_notes[i],'request_reasons':raw['reasons'],'ground_truth':None,'classification':'agent_visual_diagnostic_only','physical_contact_or_class_verdict':'unavailable','source_evidence_json':raw['evidence_json']})
summary={'schema':'independent-source-comparison-review:v1','status':'completed_selected194_source_review','source_GT':None,'current_commit':'2418ab8cbe4cca74dd16b722b9727ffdc950294a','reviewed_frames':194,'reviewed_source_baseline_current_panels':582,'pages':39,'enlarged_current_panels':[13436,13556,13558,14453,16495,23279],'fullsize_original_source_pairs':[22415,22416,23278,23279],'all_frame_reviews':case_rows,'same_anchor_class_changes':class_extract,'unsupported_claims':['physical detection/tracking AP','contact TP/FP','stroke class accuracy','named identity or winner accuracy','exhaustive scene precision/recall'],'material_findings':{'confirmed_source_edits_current_missed':[22416,23279],'current_stale_admitted_far_box_at23279':True,'current_fresh_people_at22416_does_not_prove_epoch_continuity':True,'inherited_both_arm_empty_carried_region_14453':True,'visible_active_current_sparse_pose_stride6_samples':[25689,25690,25691,25695,25696,25697,25713,25714,25715,25719,25720,25721,25725,25726,25727,25731,25732,25733,25736],'sparse_scheduling_root_cause_not_yet_proven':True}}
save('review.json',summary)
page_table='\n'.join(f"| [page{i:02}]({p['page']}) | {', '.join(map(str,p['frames']))} | {page_notes[i]} |" for i,p in enumerate(verified['pages'],start=1))
class_table='\n'.join(f"| {x['frame']} | {x['before']['stroke']} → {x['after']['stroke']} | {x['after']['hypothesis_reason']} | {x['before']['flight_time_s']} → {x['after']['flight_time_s']} |" for x in class_extract)
report=f'''# Independent Test2 source review: pending batches03/04

The two remaining lost baseline cut controls, **22416 and23279**, are actual same-camera edited jumps in the source. The current native run misses both epoch barriers. At22416it still returns two fresh athlete boxes; at23279it carries the old far-player box over empty court for one sampled frame. These are distinct consequences of the same missing temporal boundary.

All194requested frames in the closed03/04packages were reviewed across39aspect-preserving source/baseline/current sheets, with enlarged source and current panels for significant concerns. Physical ground truth remains **null**. Selected source checks do not establish exhaustive scene precision/recall, player AP, contact accuracy or stroke-class accuracy.

## Provenance and complete review coverage

Current producer is2418ab8cbe4cca74dd16b722b9727ffdc950294a; baseline is preserved Test2improved_v1. SourceSHA is4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a. Rehashed all2372rendered artifacts and2030recorded input bindings across both closed packages, plus582source/proxy pixel receipts (194original-source,194baseline-proxy and194current-proxy). There are{verified['unique_recorded_inputs']}unique recorded input paths. Visually reviewed582source/baseline/current panels; the582pixel receipts refer to the original source and proxy input PNGs, distinct from the overlay panels. No new video decode or inference occurred. All package provenance remains in [verification.json](verification.json).

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
{class_table}

At22846source shows a near-blue lunge/reach; despite fresh body observations, the current class feature set lacks an image-speed value and abstains. At25736visible near-blue overhead movement coincides with carried/no-pose current sampling, unresolved fresh target and changed next-contact interval. At26293far-red net-side action has current fresh episode availability versus old carry. These observations explain evidence availability differences; they do not certify drive/drop/net_shot labels. No shot-class ground truth is supplied by these sampled source postures, and no class TP/FP is invented. Exact event fields are linked in [structured review](review.json).

Unpaired contact/stroke anchors and anonymous actor-region changes are retained with their request reasons in the194-frame register. A visible swing posture cannot settle impact timing, actor identity or class. Phase/view transitions and partially visible off-court athletes are explicitly retained as diagnostic limitations.

## Complete page register

Every frame below was inspected in source, baseline and current columns. Notes describe sampled visual context, not physical labels or full-frame trajectory review. Adjacent source frames are only claimed where present; distant page rows are not treated as consecutive movement.

| Review page | Exact source frames | Source and output observations |
|---|---|---|
{page_table}

## Acceptance boundary

This review preserves successful immediate birth controls after known edits and wide-view returns, confirms lost scene barriers and visible stale authority, and identifies genuine inherited and scheduling limitations. It does not equate lower model-person count with missed athletes, image-only foreground with admitted people, unchanged source score with no edit, or class availability with accuracy. The separately sealed five-interval official-region lineage and batch01/02 review cover earlier frames; this report does not silently extend194frames into664independently reviewed frames. No production, annotation, evaluator, profile, model or previous report was modified.
'''
with (OUT/'REPORT.md').open('x') as f:f.write(report)
for link in re.findall(r'\]\(([^)]+)\)',report):assert (OUT/link).resolve().exists(),link
# Reverify closed rendered artifacts and metadata after visual review. Large
# recorded source/model inputs were verified once in the preparation pass.
for package in verified['packages']:
    p=ROOT/f'visual_test02_pending_v2_batch_{package["batch"]:02}'
    assert sha(p/'completion.json')==package['completion_sha256']
    c=json.loads((p/'completion.json').read_text())
    for rel,h in c['artifact_sha256'].items():assert sha(p/rel)==h,rel
inputs={str((NUMERIC/n).resolve()):sha(NUMERIC/n) for n in ['event_differences.json','point_population_decomposition.json']}
save('verification_receipt.json',{'status':'completed_independent_visual_diagnostic_review','physical_ground_truth':None,'frames_reviewed':194,'source_baseline_current_panels_reviewed':582,'aspect_preserving_pages_reviewed':39,'all2372_closed_rendered_artifacts_reverified':True,'all2030_recorded_inputs_verified_during_preparation':True,'all582_pixel_receipts_verified_during_preparation':True,'new_NN':False,'new_source_decode':False,'production_changes':False,'pipeline_acceptance_claimed':False,'input_sha256':inputs,'artifact_sha256':{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}})
print('sealed194frames582panels39pages; physicalGTnull')
