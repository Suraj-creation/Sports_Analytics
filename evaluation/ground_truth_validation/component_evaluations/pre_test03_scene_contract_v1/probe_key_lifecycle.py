"""Read-only object lifecycle control, no production source writes or inference."""
from pathlib import Path
from dataclasses import asdict
from hashlib import file_digest
import json
import numpy as np
from bai_badminton.perception.players import PlayerPerception
from bai_badminton.perception import scene_change as scene

OUT=Path(__file__).resolve().parent
NATIVE=Path('/home/administrator/Desktop/sport-analytics/test03-scene-acquisition-20261112')
assert Path(scene.__file__).resolve().is_relative_to(NATIVE)
p=PlayerPerception(None,None,30);memory=p._foreground
boxes=np.array([[20.,20.,50.,100.],[80.,20.,110.,100.]])
image=np.random.default_rng(22).integers(20,220,(240,600,3),dtype=np.uint8)
original_flow=scene._flow
scene._flow=lambda *_args:(40,.95,1.,.1)
try:
    observer=scene.SceneContinuityDetectorV4()
    for f in range(4):
        previous=memory.at(f-1) if f else ()
        raw=observer.observe(f,image,previous_regions=previous,previous_view_valid=True,current_view_valid=True)
        memory.update(f,boxes,np.array([True,True]))
    before=memory.at(3);counter_before=memory._next
    p.on_cut()
    assert p._foreground is memory
    memory.update(3,boxes,np.array([True,True]));after=memory.at(3)
    fresh=observer.observe(4,image,previous_regions=after,previous_view_valid=True,current_view_valid=True)
    assert {r.key for r in before}.isdisjoint({r.key for r in after})
    assert all(r.previous_mean is None and r.appearance_previous_mean is None for r in fresh.regions)
    memory.carry(4)
    middle=observer.observe(5,image,previous_regions=memory.at(4),previous_view_valid=True,current_view_valid=True)
    memory.carry(5)
    rebuilt=observer.observe(6,image,previous_regions=memory.at(5),previous_view_valid=True,current_view_valid=True)
    assert all(r.appearance_previous_mean==1. for r in rebuilt.regions)
    result={'scope':'Deterministic lifecycle control, not real-footage scene metric','same_foreground_memory_object_after_on_cut':True,'keys_before':[r.key for r in before],'keys_after':[r.key for r in after],'next_before':counter_before,'next_after':memory._next,'keys_disjoint':True,'observer_frames_contiguous':list(range(7)),'new_key_rebuilt_appearance_means':[r.appearance_previous_mean for r in rebuilt.regions],'fresh_key_previous_means':[r.previous_mean for r in fresh.regions],'fresh_key_appearance_previous_means':[r.appearance_previous_mean for r in fresh.regions],'conclusion':'Current on_cut reset preserves serial allocator, so the proposed same-key history reuse path is not present in this implementation','production_modified':False}
finally:scene._flow=original_flow
with (OUT/'key_lifecycle_control.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps(result,indent=2))
