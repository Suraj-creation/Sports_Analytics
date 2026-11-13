from pathlib import Path
import hashlib, json, re
import numpy as np
P = Path(__file__).resolve().parent
B = P.parent / 'visual_test02_v5_additional_cut13452_v1'
rows = json.loads((P / 'frame_register.json').read_text())
c = next(x for x in rows if x['frame'] == 13452)['arms']['current']
d = c['decision']
raw = c['raw_scene']
prior = json.loads((B / 'frame_0013451/current_raw_frame.json').read_text())
now = json.loads((B / 'frame_0013452/current_raw_frame.json').read_text())
assert np.array_equal(np.asarray(d['previous_camera']), np.asarray(prior['g']))
assert np.allclose(np.asarray(d['previous_to_current']).reshape(3,3), np.asarray(now['g']).reshape(3,3) @ np.linalg.inv(np.asarray(prior['g']).reshape(3,3)), rtol=0, atol=1e-9)
assert prior['cs'] == now['cs'] == 'VALID' and prior['v'] == now['v'] == 'main'
assert not prior['r'] and not now['r']
receipt = Path('/home/administrator/Desktop/sport-analytics/ground-truth-validation-artifacts-20261112/pre_test03_v5/test02_candidate_v5/analysis/structural_compatibility_receipt.json')
a = json.loads(receipt.read_text())
assert 13452 in a['structural_proof']['weak_barrier_frames']
assert 13452 in a['structural_proof']['relative_camera_proof_frames']
def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name, obj):
    with (P/name).open('x') as f:
        json.dump(obj, f, indent=2, allow_nan=False)
        f.write('\n')
save('decision_review.json', {'status':'source_supported_edit_with_bound_positive_weak_proof','physical_ground_truth':None,'frame':13452,'seconds':13452/30,'raw_hypothesis':False,'raw_status':raw['status'],'relative_region_keys':raw['relative_region_keys'],'region_features':{x['region']['key']:x['features'] for x in raw['regions']},'decision':d,'adjacent_camera_and_valid_main_view_checked':True,'actual_detector_pixels_equal_current_proxy_receipt':True,'completed_whole_native_structural_receipt':str(receipt),'completed_whole_native_receipt_sha256':sha(receipt)})
report = '''# Additional Test 2 V5 reset: frame 13452

**13451→13452 is a genuine same-camera temporal edit.** Before it, both athletes occupy the right sideline: near blue is bent forward and far red stands near the officials' side. At 13452 they abruptly occupy separated central near/far positions. Court/background and scoreboard remain stable. The source conclusion rests on discontinuous athlete positions, not a score change or epoch counter. No further visible edit occurs through 13455. See [before](sheet_01.jpg), [transition](sheet_02.jpg) and [continuation](sheet_03.jpg).

All seven source frames 13449–13455 were inspected with actual current 5ae and original dacc overlays: 21 panels. Current epoch changes 28→29 at 13452 and immediately returns two fresh detector-matched athlete boxes at the visible new positions. Subsequent 13453–13455 boxes are carried, not fresh. Original dacc stays at epoch 17 and emits no admitted people at 13452–13455. The 2418 arm was not rendered here; its absence of this reset was established by the separate full numeric/source metadata review.

Raw V5 strong hypothesis remains **false**, with `status=unknown` and `insufficient_region_features`. All three regions remain recorded. Extra context 79 has only four features and unknown history; it is not counted as a witness. Independently qualified relative witnesses 80/81 have 24/18 features, correspondence adaptive ratios 13.220993/6.520020 and valid histories. Background has 80 features with consistent fraction 1.0. Their mean correspondence intensity is below unchanged strong floor 15; appearance does not jointly qualify either. No strong hypothesis was manufactured.

The V4 decision instead records `relative_change_and_complete_court_replacement`: confirmed singles expects two, strict current-court indices are [0,1], and both athletes are unmatched to all prior foreground regions under unchanged IoU 0.3. All five raw proposals remain recorded, including three background officials. Geometry is valid. Actual previous camera equals the serialized claim; relative transform equals current G multiplied by inverse previous G. Both adjacent frames have VALID calibration, main view and no replay. Actual detector image hash equals the current proxy's decoded pixel receipt. The completed native whole-run structural audit also lists 13452 among validated weak barriers and camera proofs; its receipt is hashed in [decision review](decision_review.json).

The frozen renderer passed genuine completed worker/parent/catalogue, source and timestamp guards. **120 artifact hashes, 1,014 input bindings and 21 source/proxy pixel/shape receipts** verify, including rational PTS and original/frozen cache equality. Executed renderer bytes and model/config/producer metadata remain in the [closed bundle](../visual_test02_v5_additional_cut13452_v1/index.md) and [verification](verification.json). Source SHA256 is `4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a`.

This reset is source-supported and acquires the athletes immediately in this selected case. It is not aggregate physical scene precision/recall, named-identity proof, contact/class/winner GT or full pipeline acceptance. No benchmark was recomputed, production source/model/profile changed or neural model run. Existing 108-frame evidence and all completed runs remain immutable. The separately requested five-frame cadence study uses 2418 as comparator and retains that different lineage.
'''
(P/'REPORT.md').write_text(report)
assert all((P/x).exists() for x in re.findall(r'\]\(([^)]+)\)', report))
files = {x.name:sha(x) for x in P.iterdir() if x.is_file()}
save('verification_receipt.json', {'status':'completed_independent_additional_reset_source_review','source_supported_edit13452':True,'frames_visually_reviewed':7,'source_baseline_current_panels_reviewed':21,'all120_artifacts1014_inputs21_pixels_verified':True,'raw_strong_hypothesis_remains_false':True,'court_camera_actual_detector_pixel_binding_checked':True,'physical_ground_truth':None,'new_NN':False,'candidate_modified':False,'pipeline_acceptance_claimed':False,'artifact_sha256':files})
print('sealed', sha(P/'REPORT.md'), sha(P/'verification_receipt.json'))
