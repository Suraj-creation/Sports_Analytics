"""Diagnostic model controls, not pipeline accuracy/regression acceptance."""
import numpy as np
import pytest
from probe_hypothesis_partition_v3 import Hypothesis

@pytest.mark.parametrize('players',[2,4])
@pytest.mark.parametrize('fps',[25,30,60])
@pytest.mark.parametrize('stride',[2,6])
def test_fresh_unique_hypothesis_can_continue_without_renewing_court_anchor(players,fps,stride):
    h=Hypothesis(fps)
    boxes=np.array([[20+i*150,100,60+i*150,220] for i in range(players)],float)
    h.step(0,boxes,[True]*players,True)
    for f in range(stride,2*fps+stride,stride):
        row=h.step(f,boxes,[False]*players,True)
        assert len(row['accepted'])==players
        assert all(r['anchor']==0 and r['last']==f for r in row['regions'])

@pytest.mark.parametrize('players',[2,4])
def test_articulated_width_changes_do_not_claim_discontinuous_height_or_center(players):
    h=Hypothesis();boxes=np.array([[20+i*150,100,60+i*150,220] for i in range(players)],float)
    h.step(0,boxes,[True]*players,True)
    wider=boxes+[-15,0,15,0]
    r=h.step(2,wider,[False]*players,True)
    assert len(r['accepted'])==players
    assert all(d['center_2d_d2']==0 and d['height_1d_d2']==0 for d in r['decisions'])
    assert any(d['width_1d_d2_diagnostic_only']>0 for d in r['decisions'])

@pytest.mark.parametrize('fps',[25,30,60])
def test_missing_frames_never_renew_origin_and_expire_by_elapsed_source_time(fps):
    h=Hypothesis(fps);b=[[100,100,140,220]];h.step(0,b,[True],True)
    assert len(h.step(fps,[],[],False)['regions'])==1
    assert h.step(fps+1,[],[],False)['regions']==[]


def test_mutually_ambiguous_current_boxes_do_not_update_time_or_choose_identity():
    h=Hypothesis();b=np.array([[100,100,140,220]],float);h.step(0,b,[True],True)
    row=h.step(2,np.vstack([b,b]),[False,False],True)
    assert row['accepted']==[] and row['regions'][0]['last']==0
    assert row['decisions'][0]['status']=='missing_or_ambiguous_no_renewal'


def test_contradictory_scale_cannot_return_by_growing_covariance():
    h=Hypothesis();b=np.array([[100,100,140,220]],float);h.step(0,b,[True],True)
    h.step(2,b,[False],True)
    small=np.array([[100,100,140,153]],float)
    first=h.step(4,small,[False],True)
    assert first['accepted']==[] and first['regions']==[]
    assert first['decisions'][0]['status']=='contradictory_unique_current_origin_revoked'
    for f in range(6,100,2):assert h.step(f,small,[False],True)['regions']==[]
    # Only actual new court observation may seed new unknown origin evidence.
    assert len(h.step(100,small,[True],True)['regions'])==1


def test_scene_reset_removes_all_context_while_time_remains_monotonic():
    h=Hypothesis();h.step(0,[[100,100,140,220]],[True],True);h.reset()
    assert h.step(2,[[100,100,140,220]],[False],True)['regions']==[]
