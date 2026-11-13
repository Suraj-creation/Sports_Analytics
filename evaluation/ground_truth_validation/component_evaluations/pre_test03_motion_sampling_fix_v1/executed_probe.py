"""Read-only fixed-old-NN sampling-logic proof, not a fresh inference run."""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys

import msgpack
import numpy as np

OUT = Path(__file__).resolve().parent
CAND = Path('/home/administrator/Desktop/sport-analytics/pipeline-tracking-repair-20261112')
RUN = Path('/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/run')
HELPER = CAND / 'sports/badminton/src/bai_badminton/perception/acquisition.py'
TEST = CAND / 'sports/badminton/tests/test_pipeline_motion_acquisition.py'
PURE_TEST = CAND / 'sports/badminton/tests/test_motion_acquisition.py'
for package in ('sports/badminton/src', 'engine/src', 'agents/src', 'apps/api/src'):
    sys.path.insert(0, str(CAND / package))
from bai_badminton.perception import acquisition
from bai_badminton.perception.acquisition import MotionAcquisitionProof, ObservedMotionAcquisition
from bai_badminton.perception.association import CausalShuttleAssociation


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


assert Path(acquisition.__file__).resolve() == HELPER.resolve()
assert not (OUT / 'verification_receipt.json').exists(), 'refuse replacing a published receipt'
CAT = RUN / 'perception_completion_catalog.json'
INF = RUN / 'inference.json'
COMPLETION = RUN.parent / 'completion.json'
assert json.loads(INF.read_text())['status'] == 'completed'
catalog = json.loads(CAT.read_text())
assert catalog['frame_count'] == 29296 and catalog['file_count'] == 489
rows = {item['start']: item for item in catalog['files']}
inputs = {str(p): sha(p) for p in (HELPER, TEST, PURE_TEST, CAT, INF, COMPLETION)}
results = []
for start, target, expected in ((13440, 13500, (13488,13489,13490,13491)),
                                (25620, 25680, (25675,25676,25677,25678))):
    selected = rows[start]
    packet_path = RUN / selected['path']
    packet_sha = sha(packet_path)
    assert packet_sha == selected['sha256']
    inputs[str(packet_path)] = packet_sha
    packet = msgpack.unpackb(packet_path.read_bytes(), raw=False)
    assert packet['v'] == 24 and packet['start'] == start and packet['end'] == target - 1
    assert [frame['f'] for frame in packet['frames']] == list(range(start, target))
    native_next_path = RUN / rows[target]['path']
    assert sha(native_next_path) == rows[target]['sha256']
    inputs[str(native_next_path)] = sha(native_next_path)
    native_next = msgpack.unpackb(native_next_path.read_bytes(), raw=False)['frames'][0]
    target_epoch = (native_next['sh'] << 32) | native_next['ce']
    native_policy = packet['ci']['profile']['components']['shuttle_association']
    bounds = CausalShuttleAssociation(fps=packet['ci']['fps'], **native_policy['params'])
    minimum, maximum = bounds.minimum_motion_px_per_frame, bounds.maximum_age_frames
    assert minimum == 3.0 and maximum == math.ceil(2 * packet['ci']['fps']) == 60
    state = ObservedMotionAcquisition(minimum_motion_px_per_frame=minimum, maximum_age_frames=maximum)
    source_rows, positive_count = [], 0
    previous_candidate = None
    for frame in packet['frames']:
        epoch = (frame['sh'] << 32) | frame['ce']
        sa = frame['sa']
        assert sa['frame_idx'] == frame['f'] and sa['epoch'] == epoch
        valid = frame['cs'] == 'VALID' and frame['v'] == 'main' and not frame['r'] and frame['g'] is not None
        observed = valid and sa['status'] == 'observed' and sa['association_status'] in {'tracked','reacquisition'} and sa['selected_xy'] is not None
        registered = None
        if observed:
            G = np.asarray(frame['g'], dtype=float).reshape(3,3)
            assert np.isfinite(G).all()
            value = np.linalg.inv(G) @ np.r_[sa['selected_xy'], 1.0]
            assert np.isfinite(value).all() and abs(value[2]) >= 1e-12
            registered = tuple(float(v) for v in value[:2] / value[2])
        state.observe(frame['f'], epoch, registered, context_valid=valid, observed=observed)
        if state._candidate is not None and state._candidate != previous_candidate:
            positive_count += 1
            previous_candidate = state._candidate
        if frame['f'] in expected:
            source_rows.append({'frame':frame['f'],'epoch':epoch,'raw_xy':sa['raw_xy'],
                                'selected_xy':sa['selected_xy'],'registered_xy':registered,
                                'association_status':sa['association_status'],'status':sa['status'],
                                'calibration_state':frame['cs'],'view':frame['v'],'replay':frame['r'],
                                'G':frame['g']})
    state.complete_chunk(start, target - 1)
    proof = state.request(target, target_epoch)
    assert proof is not None and proof.source_frames == expected
    assert MotionAcquisitionProof.from_dict(json.loads(json.dumps(proof.to_dict()))) == proof
    assert proof.decision_frame - proof.source_frames[-1] in (9,2)
    # A cut/invalid context cannot use the previously positive lease. This is
    # an explicit injected negative contract control, not additional video GT.
    state.observe(target, target_epoch, None, context_valid=False, observed=False)
    state.complete_chunk(target, target)
    assert state.request(target + 1, target_epoch) is None
    results.append({'source_packet':str(packet_path),'source_packet_sha256':packet_sha,
                    'source_native_codec':packet['v'],'target_native_packet':str(native_next_path),
                    'target_epoch':target_epoch,'positive_windows':positive_count,
                    'proof':proof.to_dict(),'age_at_chunk_start_frames':target-proof.source_frames[-1],
                    'actual_source_rows':source_rows,'invalid_context_negative_control':'abstained',
                    'profile_sampling_rates':{'detector':packet['ci']['profile']['detector_rates'],
                                             'pose':packet['ci']['profile']['pose_rates']},
                    'loaded_models':packet['ci']['loaded_models']})
env = dict(os.environ)
env['PYTHONPATH'] = ':'.join(str(CAND / p) for p in ('sports/badminton/tests','sports/badminton/src','engine/src','agents/src','apps/api/src')) + ':' + str(CAND)
env.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='1', OPENBLAS_NUM_THREADS='1')
command = [str(CAND/'.venv/bin/python'),'-m','pytest','-q','-c',str(CAND/'pyproject.toml'),
           '--import-mode=importlib','--rootdir',str(CAND),str(PURE_TEST),str(TEST)]
with (OUT/'focused_tests.log').open('x') as log:
    proc = subprocess.run(command, cwd=CAND, env=env, stdout=log, stderr=subprocess.STDOUT, check=False)
assert proc.returncode == 0
assert '59 passed' in (OUT/'focused_tests.log').read_text()
assert all(sha(Path(path)) == digest for path,digest in inputs.items())
(OUT/'actual_helper_proofs.json').write_text(json.dumps(results,indent=2,allow_nan=False)+'\n')
receipt = {'status':'completed_fixed_old_nn_acquisition_logic_probe','scope':'Actual frozen 5ae Test2 NN/cache observations, new helper only; not fresh sampling outputs, physical accuracy, rally/contact evidence, or a completed new end-to-end run.',
           'source_producer_commit':'5ae614826e6f909defb02445386962ac13b4641a',
           'source_frames':120,'source_model_inference_repeated':False,'ground_truth':None,
           'cases':2,'proof_source_frames':[list(row['proof']['source_frames']) for row in results],
           'tests':{'passed':59,'pipeline_cases':15,'pure_helper_cases':44,'command':command},
           'input_sha256':inputs,'all_inputs_unchanged_after':True,
           'artifact_sha256':{str(p):sha(p) for p in (Path(__file__).resolve(),OUT/'actual_helper_proofs.json',OUT/'focused_tests.log')}}
(OUT/'verification_receipt.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n')
print(json.dumps({'status':receipt['status'],'proofs':receipt['proof_source_frames'],
                  'positive_windows':[r['positive_windows'] for r in results],
                  'ages':[r['age_at_chunk_start_frames'] for r in results],
                  'tests_passed':59,'receipt':str(OUT/'verification_receipt.json')}))
