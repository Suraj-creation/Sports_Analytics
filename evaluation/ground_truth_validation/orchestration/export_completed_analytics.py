"""Offline export of actual canonical folds from a verified completed neural run.

Only a new detached ledger/tracks copy is opened. No original SQLite connection,
neural inference, LLM call, annotation input, score invention or server is used.
"""
from __future__ import annotations
import argparse,collections,dataclasses,hashlib,json,shutil,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from research.production_external_semantic_replay import load_finished_input
from bai_engine.schema import Event,Session
from bai_engine.store import EventStore,TrackStore
from bai_badminton.analytics.rebuild import build,rally_records
from bai_badminton.analytics.individual import build_individual_analytics
from bai_badminton.analytics.automatic_individual import build_estimated_individual_analytics

def sha(p:Path)->str:
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def dump(p:Path,obj):
 with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
def export(run:Path,output:Path,recovery:Path|None=None):
 run=run.resolve(strict=True);output=output.resolve()
 if output.exists() or ROOT==output or ROOT in output.parents or run in output.parents or output in run.parents:
  raise ValueError('Requires a new external output directory, separate from repository and source run')
 session_file=run/'session.json';raw_session=json.loads(session_file.read_text());sid=raw_session['session_id']
 # Guard genuine completion and source/config/model/cache hashes before exporting anything.
 finished=load_finished_input(run,sid,completion_recovery=recovery)
 session=Session.model_validate(raw_session);media=finished.media;fps=media['fps_num']/media['fps_den'];n=media['n_frames']
 tracks_source=run/'data/sessions'/sid/'tracks'
 if not tracks_source.is_dir():raise ValueError('Completed run lacks observation tracks; do not invent spatial analytics')
 source_files=set(finished.input_paths)|{finished.report_path,finished.events_path,session_file}
 source_files.update(p for p in tracks_source.rglob('*') if p.is_file())
 # Side-effect audit also binds original SQLite/WAL/SHM bytes without opening any DB.
 source_files.update(p for p in (run/'data').rglob('*') if p.is_file() and (p.suffix in ('.sqlite','.db') or p.name.endswith(('-wal','-shm'))))
 before={str(p.resolve()):sha(p) for p in source_files}
 events=[Event.model_validate_json(line) for line in finished.events_path.read_text().splitlines() if line.strip()]
 if len({e.event_id for e in events})!=len(events):raise ValueError('Duplicate event IDs in original ledger export')
 events.sort(key=lambda e:e.seq if e.seq is not None else -1)
 if any(e.seq is None or e.session_id!=sid for e in events):raise ValueError('Original event export lost session/sequence identity')
 output.mkdir(parents=True,exist_ok=False);detached=output/'detached';detached.mkdir()
 shutil.copyfile(session_file,detached/'session.json');shutil.copytree(tracks_source,detached/'tracks')
 started=time.monotonic();store=EventStore(detached/'events.sqlite',sid)
 try:
  copied=store.append_many(events)
  # Exact IDs and payloads retained; integer local seq may be dense but preserves ordering.
  for original,restored in zip(events,copied,strict=True):
   if original.model_dump(exclude={'seq'})!=restored.model_dump(exclude={'seq'}):raise ValueError('Detached event identity/payload changed')
  live=store.query();live_ids={e.event_id for e in live};tracks=TrackStore(detached/'tracks')
  folded=build(store,tracks,fps);analytics=folded.to_public();highlights=[h.to_public() for h in folded.highlights(k=12)]
  checks=[]
  for h in highlights:
   refs=h['evidence_ids'];valid=bool(refs) and set(refs)<=live_ids
   in_range=0<=h['frame_start']<h['frame_end']<n
   if not valid or not in_range:raise ValueError('Highlight lost live same-session evidence or frame bounds')
   checks.append({'rally_id':h['rally_id'],'evidence_ids':refs,'all_ids_live_same_session':valid,'bounds_valid':in_range})
  analytics['highlights']=highlights;dump(output/'analytics.json',analytics);dump(output/'highlights.json',{'highlights':highlights,'checks':checks,'clip_rendering_performed':False,'relevance_accuracy_validated':False})
  records=[]
  for record in rally_records(store):
   value=dataclasses.asdict(record)
   if not value['score_available']:value['score_after']=None
   records.append(value)
  dump(output/'rally_outcome_records.json',{'rallies':records,'unavailable_score_policy':'score_after=null when no canonical accepted point; no implicit0-0'})
  dump(output/'individual_analytics.json',build_individual_analytics(store,session.roster,max_frame=n-1,fps=fps))
  dump(output/'estimated_individual_analytics.json',build_estimated_individual_analytics(store,tracks,session.roster,max_frame=n-1,fps=fps,frame_width=media['width'],frame_height=media['height']))
  with (output/'live_events.jsonl').open('x') as f:
   for e in live:f.write(e.model_dump_json()+'\n')
  grouped={kind:[e.model_dump(mode='json') for e in live if e.type==kind] for kind in ('point','broadcast_score','score_observation','score_correction','match_phase','rally_end','identity_ambiguity')}
  dump(output/'scoring_outcome_evidence.json',{'events_by_type':grouped,'live_event_counts':dict(collections.Counter(e.type for e in live)),'certified_ground_truth_accuracy':None,'winner_identity_mapping_validated':False})
  dump(output/'unavailable_and_limits.json',{'session_degraded':raw_session.get('meta',{}).get('degraded',[]),'source_worker_degraded':json.loads(finished.report_path.read_text()).get('degraded',[]),'ground_truth_accuracy':None,'neural_inference_performed':False,'semantic_observation_replay_performed':False,'llm_calls':0,'official_score_policy':'Only original canonical point events count; unknown winners remain unknown. Numerical empty counts are not verified0-0 score.','individual_policy':'Canonical reviewed identities and separately labelled model estimates are exported independently.','highlights':'Actual canonical heuristic ranks/evidence references; no relevance labels or rendered highlight video claimed.'})
 finally:store.close()
 for name,h in before.items():
  if sha(Path(name))!=h:raise ValueError('Original completed artifact changed during export: '+name)
 dump(output/'export_receipt.json',{'status':'completed','source_run':str(run),'session_id':sid,'source_completion_receipt':str(finished.report_path),'source_completion_sha256':sha(finished.report_path),'explicit_historical_completion_recovery':str(recovery) if recovery else None,'frames':n,'input_sha256':before,'original_sqlite_opened':False,'original_artifacts_unchanged':True,'detached_ledger_policy':'Recreated from verified complete JSONL, original event IDs/payloads/correction lineage and order preserved. No original SQLite opened.','sequence_remapping':[{'event_id':a.event_id,'original_seq':a.seq,'detached_seq':b.seq} for a,b in zip(events,copied) if a.seq!=b.seq],'exported_live_events':len(live),'original_append_only_events':len(events),'highlights':len(highlights),'elapsed_export_s':time.monotonic()-started,'exporter_sha256':sha(Path(__file__)),'output_sha256':{p.name:sha(p) for p in output.iterdir() if p.is_file()}})
 return {'status':'completed','session_id':sid,'output':str(output),'live_events':len(live),'highlights':len(highlights)}
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--run',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--completion-recovery',type=Path,help='Explicit historical known catalogue-finalization proof; omit for ordinary successful fresh run');a=p.parse_args()
 print(json.dumps(export(a.run,a.output,a.completion_recovery)),flush=True)
