"""Read all count-loss rows without equating model regions to labelled people."""
from collections import Counter
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
SOURCE=OUT.parent/'test02_postprocessing_independent_v1'
VISUAL=OUT.parent/'visual_test02_weak_barriers_review_v1'
NAMES=('all_current_gross_population_losses.json','all_historical_regions_without_overlap.json')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(name,x):
    with (OUT/name).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
def iou(a,b):
    inter=max(0,min(a[2],b[2])-max(a[0],b[0]))*max(0,min(a[3],b[3])-max(a[1],b[1]))
    return inter/((a[2]-a[0])*(a[3]-a[1])+(b[2]-b[0])*(b[3]-b[1])-inter)
inputs={str((SOURCE/n).resolve()):sha(SOURCE/n) for n in NAMES}
rows=json.loads((SOURCE/NAMES[0]).read_text())['rows']
unmatched=json.loads((SOURCE/NAMES[1]).read_text())['rows']
assert len(rows)==754
compact=[]
for row in rows:
    old0=[p for p in row['historical_people'] if p['t']==0]
    assert len(old0)==1
    assert row['old_count']==3 and row['fresh_count']==2
    best=lambda p:max((iou(p['b'],q['b']) for q in row['fresh_people']),default=0)
    compact.append({'frame':row['frame'],'old_count':3,'current_count':2,'historical_official_position_region_raw_id':0,'old_region_bbox':old0[0]['b'],'old_region_best_current_iou':best(old0[0]),'other_historical_regions':[{'raw_id':p['t'],'bbox':p['b'],'best_current_iou':best(p)} for p in row['historical_people'] if p['t']!=0],'current_bboxes':[p['b'] for p in row['fresh_people']]})
summaries=[]
for s,e in [(5960,6023),(6030,6151),(6154,6307),(6310,6491),(6498,6729)]:
    group=[r for r in compact if s<=r['frame']<=e]
    assert len(group)==e-s+1
    summaries.append({'start':s,'end_inclusive':e,'frame_count':len(group),'old_current_counts':[3,2],'constant_historical_raw_id':0,'old_bbox_coordinate_ranges':[[min(r['old_region_bbox'][j] for r in group),max(r['old_region_bbox'][j] for r in group)] for j in range(4)],'max_old_region_iou_to_current':max(r['old_region_best_current_iou'] for r in group),'min_other_historical_region_iou':min(p['best_current_iou'] for r in group for p in r['other_historical_regions']),'frames_with_other_region_iou_below_diagnostic_half':[r['frame'] for r in group if any(p['best_current_iou']<.5 for p in r['other_historical_regions'])],'source_semantic_scope':'same small upper-left seated-official position at reviewed5958/6151/6307/6492controls; not754 independently labelled official identities','ground_truth':None})
historical0=[r for r in unmatched if 5958<=r['frame']<=6729 and r['historical_person']['t']==0]
assert len(historical0)==772 and [r['frame'] for r in historical0]==list(range(5958,6730))
lossframes={r['frame'] for r in compact}
other18=[r['frame'] for r in historical0 if r['frame'] not in lossframes]
assert len(other18)==18
result={'schema':'model-region-population-lineage-diagnostic:v1','physical_ground_truth':None,'count_loss_is_not_physical_miss':True,'whole_population_scope':'All754 rows in five lower-count intervals; all772consecutive unmatched historical t0 rows5958–6729','diagnostic_overlap_threshold':.5,'threshold_source':'existing independent population audit; not an admission rule or calibrated physical metric','intervals':summaries,'all_count_loss_rows':compact,'additional18_unmatched_old_official_position_frames_without_count_decrement':other18,'other_unmatched_historical_raw_id_counts_5958_6729':dict(Counter(str(r['historical_person']['t']) for r in unmatched if 5958<=r['frame']<=6729)),'pending_source_questions':['Non-official localisation/carry differences at6238/6239,6484/6485,6490/6491,6502/6503,6538/6539 require additional rendered source/cadence context.','6151and6307 other-region disagreement is source-supported scene edit in sealed visualreview.','No claim that all754frames have independently verified athlete localisation or named identity.']}
dump('lineage.json',result)
table='\n'.join(f"| {g['start']}–{g['end_inclusive']} | {g['frame_count']} | 3 → 2 | {g['max_old_region_iou_to_current']:.6f} | {', '.join(map(str,g['frames_with_other_region_iou_below_diagnostic_half'])) or 'none'} |" for g in summaries)
text=f'''# Test2 lower-count population: old-region lineage

The five lower-count intervals are consistently the removal of one historical upper-left region at the seated-official position. Every one of the754rows has old3/current2 regions and historical raw track0 around `[447,153,485,206]`. This explains the count decrement; it is not evidence of754 missed athletes. It differs from the rejected Test1 strict-court-TTL182visible-athlete withholdings.

## Complete numerical lineage

The two original independent whole-population tables are read unchanged. This review checks all754lower-count rows and all772consecutive historical unmatched raw0 rows5958–6729. [Compact full row ledger](lineage.json) contains only boxes, track-episode IDs and image IoU; it omits raw pose arrays. Track0 is a model episode identifier, not a physical identity label.

| Inclusive source frames | Rows | Model region counts | Highest removed-region/current IoU | Other historical-region overlap below0.5 |
|---|---:|---|---:|---|
{table}

No existing current-athlete box overlaps the old official-position box in the first four intervals. Its maximum overlap in the final interval is0.010570. The remaining historical boxes usually agree closely with current; the exception list is explicitly retained rather than declaring every athlete position correct. The0.5 diagnostic overlap is inherited from the independent population audit and is not a new tracker/admission threshold or physical accuracy metric.

## What the source controls establish

The [5958 source sheet](../visual_test02_weak_barriers_review_v1/weak_05958.png) shows a genuine edited jump and the historical stale/official context. [6151](../visual_test02_weak_barriers_review_v1/control_06151.png) and [6307](../visual_test02_weak_barriers_review_v1/control_06307.png) show additional edited jumps; current resets to two fresh athletes while old outputs retain previous positions and the small official-position box. At [6492](../visual_test02_weak_barriers_review_v1/control_06492.png), the old arm has two boxes but one is the official and the visible near athlete is missing. Current has two athlete boxes. Model count equality there hides the semantic difference.

The old official-position region is unmatched throughout772frames5958–6729, including18frames outside the five lower-count intervals: `{other18}`. On those frames another old athlete region is also absent or stale; counting the same total regions does not establish equal participant coverage. The historical official position is supported visually at these selected controls; this is not772independent physical identity labels.

The true edit at5958 is the observed initiating context for this old alias. A generic uninterrupted physical athlete-to-official handover remains a separate unsupported identity-continuity problem. No named identity, physical AP/recall, or universal nonedit continuity fix is inferred.

## Explicit unresolved detail

Other-region disagreement at6151/6307 has already been source-reviewed as edited jumps. Additional source/cadence review is still required at6238–39,6484–85,6490–91,6502–03 and6538–39. The pending larger renderer may establish carry/localisation differences; this sealed lineage report does not pretend those frames were inspected. Counts alone cannot adjudicate them.

Original tables, completed producer outputs and annotations remain unchanged. [Sealed source review](../visual_test02_weak_barriers_review_v1/REPORT.md) preserves the nine weak reset cases, provenance and Test2/Test1 frame-number scope correction. No inference, source decoding, annotation construction, threshold change or pipeline modification was performed for this report. Physical ground truth is null throughout.
'''
with (OUT/'REPORT.md').open('x') as f:f.write(text)
for p,h in inputs.items():assert sha(p)==h
for n in ['verification_receipt.json','review.json','REPORT.md']:
    inputs[str((VISUAL/n).resolve())]=sha(VISUAL/n)
dump('verification_receipt.json',{'status':'completed_full_count_loss_lineage_diagnostic','ground_truth':None,'all754_count_loss_rows_checked':True,'all772_historical_unmatched_t0_frames_checked':True,'original_inputs_unchanged':True,'new_NN':False,'new_source_decode':False,'pending_further_source_review_explicit':True,'input_sha256':inputs,'artifact_sha256':{p.name:sha(p) for p in sorted(OUT.iterdir()) if p.is_file()}})
print('sealed five intervals,754countloss rows,772unmatched oldt0 rows; no physicalGT')
