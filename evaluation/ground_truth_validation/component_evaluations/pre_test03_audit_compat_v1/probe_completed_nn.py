"""Read-only structural diagnosis, native loader/decoder, no report recovery."""
import copy
import importlib.util
import json
from hashlib import file_digest
from pathlib import Path
from types import SimpleNamespace

import msgpack

NATIVE = Path('/home/administrator/Desktop/sport-analytics/test03-scene-evidence-contract-20261112')
ART = Path('/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4')
OUT = Path(__file__).resolve().parent


def sha(p):
    with Path(p).open('rb') as f:
        return file_digest(f, 'sha256').hexdigest()


def validate_epoch_authority(wire, decoded):
    """Proposal only: typed native proof, never a caller-supplied validity flag."""
    all_frames = [f for packet in wire for f in packet['frames']]
    typed = {f.frame_idx: f for c in decoded for f in c.frames}
    assert sorted(typed) == [f['f'] for f in all_frames]
    weak = []
    previous_epoch = None
    for f in all_frames:
        raw, d = f.get('cc'), f.get('cd')
        hypothesis = bool(raw and raw.get('hypothesis'))
        barrier = previous_epoch is not None and f['ce'] > previous_epoch
        previous_epoch = f['ce']
        if d and d['decision'] == 'no_barrier' and barrier:
            raise ValueError('no_barrier contradicts epoch')
        if d and d['decision'] in {'barrier', 'unknown'} and hypothesis and not barrier:
            raise ValueError('strong selected reset/fallback missing epoch')
        # Legacy strong behavior remains intact. No weak unknown fallback.
        if barrier and not hypothesis:
            t = typed[f['f']]
            if not (
                raw and raw['version'] == 'foreground-scene-hypothesis:v4'
                and d and d['version'] == 'detector-layout-scene-decision:v3'
                and d['decision'] == 'barrier' and d['raw_hypothesis'] is False
                and t.content_change and t.content_change.hypothesis is False
                and t.content_decision and t.content_decision.decision == 'barrier'
                and t.content_decision.raw_hypothesis is False
            ):
                raise ValueError('rawfalse reset lacks native validated positive weak proof')
            weak.append(f['f'])
        if d and d['decision'] == 'barrier' and not hypothesis and not barrier:
            raise ValueError('positive weak reset missing actual epoch')
    return weak


def main():
    import research.pipeline_repair_run_analysis as original
    from bai_badminton.plugin import BadmintonSession
    assert Path(original.__file__).resolve() == NATIVE/'research/pipeline_repair_run_analysis.py'
    assert original.ROOT.resolve() == NATIVE
    bound = original.load_analysis_input(ART/'run', None)
    assert bound['completion_mode'] == 'normal_completed_worker'
    assert bound['media']['n_frames'] == 29296
    plan = json.loads(Path(bound['plan_path']).read_text())
    inputs = {str(p): sha(p) for p in bound['input_paths']}
    for p, h in plan['source_files_sha256'].items():
        assert sha(p) == h
        inputs[p] = h
    consumed = {}
    packets, frames = original.load_chunks(Path(bound['cache_dir']), bound['cache_sha256'], consumed)
    inputs.update(consumed)

    def decode(packet):
        receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=packet['cr']), _isolation_id=lambda: packet['ci'])
        return BadmintonSession.decode_perception(receiver, msgpack.packb(packet, use_bin_type=True), diagnostic=True)

    decoded = [decode(p) for p in packets]
    try:
        original.audit_frames(frames, 29296)
    except ValueError as e:
        old_error = str(e)
        assert old_error == 'content epoch reset lacks raw source hypothesis'
    else:
        raise AssertionError('Expected real RED not reproduced')
    weak = validate_epoch_authority(packets, decoded)
    resets, previous = [], None
    for f in frames:
        if previous is not None and f['ce'] > previous:
            resets.append({'frame': f['f'], 'raw_hypothesis':bool(f.get('cc') and f['cc']['hypothesis']),
                           'decision':f.get('cd')})
        previous = f['ce']
    specimen = next(p for p in packets if any(f['f'] == weak[0] for f in p['frames']))
    controls = []
    for change in ['missing_decision', 'legacy22_downgrade', 'unknown', 'no_barrier', 'rawfalse_no_acquisition',
                   'wrong_current_polygon', 'wrong_camera', 'unconfirmed_format']:
        p = copy.deepcopy(specimen)
        f = next(f for f in p['frames'] if f['f'] == weak[0])
        if change == 'missing_decision': f['cd'] = None
        elif change == 'legacy22_downgrade': p['v'] = 22
        elif change == 'unknown': f['cd']['decision'] = 'unknown'
        elif change == 'no_barrier': f['cd']['decision'] = 'no_barrier'
        elif change == 'rawfalse_no_acquisition': f['cc']['acquisition_region_keys'] = []
        elif change == 'wrong_current_polygon': f['cd']['court_polygon'][0][0] += 1
        elif change == 'wrong_camera': f['cd']['previous_to_current'][2] += 1
        elif change == 'unconfirmed_format': p['ci']['layout_format_context']['confirmed'] = False
        try:
            # For structural controls use full original chronology with changed
            # one packet; decode validates its source proof before epoch audit.
            c = decode(p)
            i = packets.index(specimen)
            modified_packets = list(packets); modified_packets[i] = p
            modified_decoded = list(decoded); modified_decoded[i] = c
            validate_epoch_authority(modified_packets, modified_decoded)
        except Exception as e:
            controls.append({'case':change, 'rejected':True, 'type':type(e).__name__, 'reason':str(e)})
        else:
            raise AssertionError('Forged structural reset accepted: '+change)
    # Actual saved Test1 strong reset control; no claim of fresh source-video
    # revalidation here. Every retained payload remains catalogue-hash-bound.
    t1 = ART.parent/'test01_candidate_v4/run'
    cat = json.loads((t1/'perception_completion_catalog.json').read_text())
    t1frames=[]
    for entry in cat['files']:
        p=t1/entry['path']; assert sha(p)==entry['sha256']; inputs[str(p)]=entry['sha256']
        t1frames.extend(msgpack.unpackb(p.read_bytes(),raw=False)['frames'])
    original.audit_frames(t1frames,17268)
    spec=importlib.util.spec_from_file_location('new_pure_camera_diagnostic',OUT.parents[1]/'regression_tests/pre_test03_contract_v1/test02_independent_v4/audit_acquisition_coverage.py')
    camera=importlib.util.module_from_spec(spec);spec.loader.exec_module(camera)
    proof=camera.audit_camera_proofs(packets)
    assert all(sha(p)==h for p,h in inputs.items())
    result={'status':'diagnostic_only_complete_NN_old_audit_RED_native_decode_and_proposed_structural_gate_GREEN',
        'producer_root':str(NATIVE),'producer_commit':plan['code_commit'],'tool_root':str(OUT),
        'original_outer_analysis_status':'failed_preserved','original_worker_status':bound['worker_info']['status'],
        'original_parent_status':bound['original_parent_status'],'frames':len(frames),'native_decoded_packets':len(decoded),
        'original_audit_error':old_error,'first_failure_frame':weak[0],'weak_barrier_frames':weak,
        'all_epoch_resets':resets,'negative_controls':controls,'retained_Test1_original_audit_control':{'frames':17268,'passed':True,'source_video_revalidated':False},
        'crosschunk_camera_proofs':{k:v for k,v in proof.items() if k not in {'all_claims','format_context_per_chunk'}},
        'evaluation_metrics_computed':False,'ground_truth_loaded':False,'NN_rerun':False,'original_bytes_modified':False,
        'inputs_sha256':inputs,'original_audit_source_sha256':sha(original.__file__),'script_sha256':sha(__file__)}
    with (OUT/'diagnostic_receipt.json').open('x') as f:json.dump(result,f,indent=2,allow_nan=False);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k not in {'inputs_sha256','all_epoch_resets','crosschunk_camera_proofs'}},indent=2))

if __name__=='__main__':main()
