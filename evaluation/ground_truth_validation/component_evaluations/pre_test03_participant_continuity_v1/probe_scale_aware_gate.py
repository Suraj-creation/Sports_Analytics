"""Untuned installed BoTSORT motion alternative; same fixed gate, cached inputs.

No BoTSORT appearance, CMC or association engine is executed. This measures its
published installed default state/noise model as a standalone origin hypothesis.
"""
import json
from pathlib import Path
from hashlib import file_digest
import probe_backend_gate as probe
from trackers.core.botsort.tracklet import BoTSORTTracklet

OUT = Path(__file__).resolve().parent / 'scale_aware_v1'
OUT.mkdir(exist_ok=False)
probe.HERE=OUT
probe.ByteTrackTracklet=BoTSORTTracklet
original_gate=probe.gate

def gate(track,box):
    # The installed tracklet refreshes R from predicted box immediately before
    # measurement update. Project the identical R for a hypothetical update.
    track._refresh_measurement_noise_from_state()
    return original_gate(track,box)

probe.gate=gate
original_save=probe.save

def save(name,obj):
    if name=='summary.json':
        obj['scope']='Untuned installed BoTSORT XCYCWH scale-aware covariance, fixed4D95%9.4877. Conditional and raw-shadow arms are distinct; not BoTSORT full association/CMC/appearance, not physical accuracy or calibrated confidence.'
        p=Path(__file__).resolve()
        with p.open('rb') as f:obj['input_sha256'][str(p)]=file_digest(f,'sha256').hexdigest()
        p=Path(__import__('inspect').getfile(BoTSORTTracklet)).resolve()
        with p.open('rb') as f:obj['input_sha256'][str(p)]=file_digest(f,'sha256').hexdigest()
        obj['noise_sigma_constants']={'position':.05,'velocity':.00625,'measurement':.05}
    # Original output name used XYXY because it measured ByteTrack. Retain raw
    # 4D projection here under truthful model-specific field names.
    def rename(value):
        if isinstance(value,list):return [rename(v) for v in value]
        if isinstance(value,dict):return {('predicted_xcycwh' if k=='predicted_xyxy' else k):rename(v) for k,v in value.items()}
        return value
    original_save(name,rename(obj))

probe.save=save
probe.main()
