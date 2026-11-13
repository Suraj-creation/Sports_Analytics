"""Observe only genuine completion/timestamp receipts; no live cache or metrics reads."""
from pathlib import Path
import datetime,json,hashlib
P=Path(__file__).resolve().parent;ROOT=Path('/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5')
def read(rel):
 p=ROOT/rel
 if not p.exists():return None
 return json.loads(p.read_text())
w=read('run/inference.json');parent=read('run.executor.json');catalogue=read('run/perception_completion_catalog.json')if w and parent else None;timestamps=read('timestamps/timestamp_audit.json')if w and parent else None;result=read('timestamps.result.json')if w and parent else None
ready=bool(w and parent and catalogue and timestamps and result and w.get('status')=='completed'and parent.get('status')=='completed'and parent.get('worker_exit_code')==0 and w.get('frames_processed')==29296 and w.get('frontier_frame')==29295 and catalogue.get('frame_count')==29296 and timestamps.get('frames_decoded')==29296 and timestamps.get('exact_pts_frames')==29296 and timestamps.get('source_proxy_full_rational_pts_equal')is True and result.get('exit_code')==0 and(ROOT/'timestamps/source_frame_pts.csv').exists())
if ready:assert hashlib.sha256((ROOT/'timestamps/source_frame_pts.csv').read_bytes()).hexdigest()==timestamps['source_pts_csv_sha256']
x={'at_utc':datetime.datetime.now(datetime.UTC).isoformat(),'status':'ready_for_original_renderer_guards'if ready else'waiting_actual_completion_and_timestamp_gates','worker':w.get('status')if w else None,'parent':parent.get('status')if parent else None,'catalogue_frames':catalogue.get('frame_count')if catalogue else None,'timestamp_result_exit_code':result.get('exit_code')if result else None,'outer_completion_not_required_or_claimed':True,'no_render_launched_by_poll':True,'no_live_cache_opened':True,'no_metrics_read':True}
with(P/'readiness_observations.jsonl').open('a')as f:f.write(json.dumps(x)+'\n')
print(json.dumps(x))
