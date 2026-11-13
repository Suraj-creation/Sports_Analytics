"""Trace completed saved cadence/FSM feedback. No inference or engine replay."""
from pathlib import Path
import csv,hashlib,json,subprocess
import msgpack

OUT=Path(__file__).resolve().parent
MAIN=OUT.parents[3]
WORKSPACE=MAIN.parent
NATIVE=WORKSPACE/'test03-scene-evidence-contract-20261112'
RUNS={'before':WORKSPACE/'ground-truth-validation-artifacts-20261110/test_02/improved_v1','current':WORKSPACE/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4'}
TRACES={'before':RUNS['before']/'diagnostic_replay/bounded_fsm_trace.jsonl','current':RUNS['current'].parent/'test02_postprocessing_v1/diagnostic_replay/bounded_fsm_trace.jsonl'}
INPUTS={}
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def bind(p):INPUTS[str(p.resolve())]=sha(p)
def read(p):bind(p);return json.loads(p.read_text())
def save(n,x):
    with (OUT/n).open('x') as f:json.dump(x,f,indent=2,allow_nan=False);f.write('\n')
packets=[];all_frames={};traces={};event_rows=[];source_bindings={}
source_names=['sports/badminton/src/bai_badminton/plugin.py','sports/badminton/src/bai_badminton/perception/pipeline.py','sports/badminton/src/bai_badminton/perception/tracknet.py','sports/badminton/src/bai_badminton/engine.py','engine/src/bai_engine/runtime/runner.py','engine/src/bai_engine/sport.py','sports/badminton/src/bai_badminton/events/activity.py']
for arm,root in RUNS.items():
    plan=read(root/'protocol/plan.json');worker=read(root/'run/inference.json');session=read(root/'run/session.json');catalogue=read(root/'run/perception_completion_catalog.json')
    assert worker['status']=='completed' and worker['frames_processed']==29296
    assert session['media']['n_frames']==29296 and session['meta']['frames_per_segment']==60
    bind(root/'run.executor.json')
    profile=read(root/'protocol/plan.json')['profile_source_sha256']
    source_bindings[arm]={'code_commit':plan['code_commit'],'session_segment_frames':60,'worker_profile':worker['profile'],'source_implementations':{}}
    if arm=='current':
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=NATIVE,text=True).strip()==plan['code_commit']
        for name in source_names:
            path=NATIVE/name;expected=plan['source_files_sha256'][str(path)];assert sha(path)==expected
            bind(path);source_bindings[arm]['source_implementations'][name]={'recorded_sha256':expected,'actual_native_file_matches':True}
    else:
        for name in source_names:
            expected=plan['source_files_sha256'][str(MAIN/name)]
            content=subprocess.check_output(['git','show',f'{plan["code_commit"]}:{name}'],cwd=MAIN)
            actual=hashlib.sha256(content).hexdigest();assert actual==expected,(name,actual,expected)
            source_bindings[arm]['source_implementations'][name]={'recorded_sha256':expected,'recorded_commit_blob_matches':True}
    fdict={}
    for entry in catalogue['files']:
        if entry['end']<25500 or entry['start']>25799:continue
        path=root/'run'/entry['path'];assert sha(path)==entry['sha256'];bind(path)
        wire=msgpack.unpackb(path.read_bytes(),raw=False)
        assert wire['start']==entry['start'] and wire['end']==entry['end']
        for f in wire['frames']:fdict[f['f']]=f
        diag=[{'frame':f['f'],'background_sha256':f['dg']['shuttle']['background_sha256'],'raw_peak':f['dg']['shuttle']['raw_peak'],'reason':f['dg']['shuttle']['reason']} for f in wire['frames'] if f['dg'] is not None and f['dg']['shuttle'] is not None]
        packets.append({'arm':arm,'start':wire['start'],'end':wire['end'],'packet_sha256':entry['sha256'],'same_profile_rates':{k:wire['ci']['profile'][k] for k in ['detector_rates','pose_rates','shuttle_rates']},'pose_stride_values':sorted({f['ps'] for f in wire['frames']}),'detector_observed_frames':[f['f'] for f in wire['frames'] if f['do']],'fresh_keypoint_row_count':sum(p['pf']==f['f'] and p['k'] is not None for f in wire['frames'] for p in f['p']),'per_frame_diagnostic_bg':diag})
    assert len(fdict)==300;all_frames[arm]=fdict
    bind(TRACES[arm]);selected=[]
    for line in TRACES[arm].open():
        r=json.loads(line)
        if 25450<=r['frame']<=25800:selected.append(r)
    traces[arm]=selected
    bind(root/'run/events.jsonl')
    for line in (root/'run/events.jsonl').open():
        e=json.loads(line)
        if e['type']=='activity_interval' and e['frame_start']<=25800 and e['frame_end']>=25450:event_rows.append({'arm':arm,'start':e['frame_start'],'end':e['frame_end'],'payload':e['payload'],'ledger_status':e['status']})
# Step snapshots exactly available after each completed prior ingest.
boundary=[]
for start in range(25500,25800,60):
    final_prior=start-41
    for arm,trace in traces.items():
        row=next((r for r in trace if r['call']=='step' and r['frame']==final_prior),None)
        if row is None:continue
        assert row['available_through']==start-1
        packet=next(p for p in packets if p['arm']==arm and p['start']==start)
        expected_in_play=row['after']['state']!='idle'
        expected_ps=1 if expected_in_play else 6
        assert packet['pose_stride_values']==[expected_ps]
        boundary.append({'arm':arm,'next_chunk_start':start,'next_chunk_end':start+59,'last_folded_frame_before_acquisition':final_prior,'actual_available_through':row['available_through'],'actual_FSM_state':row['after']['state'],'actual_FSM_start':row['after']['start'],'source_defined_in_play':expected_in_play,'expected_pose_stride':expected_ps,'observed_packet_pose_stride':packet['pose_stride_values'][0],'detector_observed_count':len(packet['detector_observed_frames'])})
transitions=[]
for arm,trace in traces.items():
    for r in trace:
        if r['call']=='step':
            b,a=r['before'],r['after'];u=r['update']
            if b['state']!=a['state'] or u.get('started') is not None or u.get('cancelled_start') is not None or r['frame'] in [25519,25579,25639,25699,25759]:
                transitions.append({'arm':arm,'frame':r['frame'],'available_through':r['available_through'],'observation':r['observation'],'processed_xy':r['processed_xy'],'before':b,'after':a,'update':u})
        else:
            if r['call'] not in ['step','exit_support']:transitions.append({'arm':arm,**r})
# Literal observed model/association changes are not a causal ablation.
compare=[]
for lo,hi in [(25500,25520),(25521,25559),(25560,25619),(25620,25679),(25680,25739),(25740,25799)]:
    frames=list(range(lo,hi+1));before=all_frames['before'];after=all_frames['current']
    raw_equal=lambda f:before[f]['sa']['raw_xy']==after[f]['sa']['raw_xy'] and before[f]['sa']['raw_model_support']==after[f]['sa']['raw_model_support']
    selected_equal=lambda f:before[f]['s']==after[f]['s'] and before[f]['c']==after[f]['c']
    compare.append({'start':lo,'end':hi,'frames':len(frames),'same_raw_xy_and_support':sum(raw_equal(f) for f in frames),'same_selected_xy_and_support':sum(selected_equal(f) for f in frames)})
save('packet_cadence.json',packets);save('boundary_states.json',boundary);save('actual_fsm_transitions.json',transitions);save('activity_intervals.json',event_rows);save('raw_readout_comparison.json',compare);save('source_binding.json',source_bindings)
with (OUT/'frame_cadence.csv').open('x',newline='') as f:
    w=csv.writer(f);w.writerow(['frame','arm','pose_stride','detector_observed','person_count','fresh_detector_matched_rows','fresh_keypoint_payload_rows','view','calibration','content_epoch','shot'])
    for frame in range(25500,25800):
        for arm,fdict in all_frames.items():
            p=fdict[frame];w.writerow([frame,arm,p['ps'],p['do'],len(p['p']),sum(x['dm'] is True for x in p['p']),sum(x['pf']==frame and x['k'] is not None for x in p['p']),p['v'],p['cs'],p['ce'],p['sh']])
for p,h in INPUTS.items():assert sha(p)==h,p
save('input_receipt.json',{'status':'completed_readonly_actual_trace_and_cache_feedback_audit','new_NN':False,'new_engine_replay':False,'source_changes':False,'ground_truth':None,'original_and_native_source_binding_checked':True,'input_sha256':INPUTS})
print(json.dumps({'boundaries':boundary,'literal_raw_comparison':compare},indent=2))
