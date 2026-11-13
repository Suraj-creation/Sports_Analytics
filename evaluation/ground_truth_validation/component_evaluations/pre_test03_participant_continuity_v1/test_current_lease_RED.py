"""Expected RED against frozen c585: genuine repeated image support exceeds lease."""
import numpy as np
from bai_badminton.perception.players import PlayerPerception,CourtROI

class Detector:
    def __init__(self):self.frame=0
    def __call__(self,image):
        # Same full-height athlete remains uniquely near the baseline, then
        # runs outside. This is a synthetic geometry control, no video labels.
        return np.array([[40.,10.,60.,100. if self.frame==0 else 102.]]),np.array([.95])

def test_current_participant_continuity_should_use_positive_observation_beyond_court_anchor_lease():
    d=Detector();p=PlayerPerception(d,None,30,det_stride=2,pose_stride=0)
    p.set_roi(CourtROI(np.array([[0.,0.],[100.,0.],[100.,100.],[0.,100.]],np.float32),pad_px=0))
    image=np.zeros((160,160,3),np.uint8)
    for f in range(0,33,2):
        d.frame=f;out=p.process(f,image)
    assert len(out)==1,'Current strict lease discards this continuously observed synthetic athlete after1s'
