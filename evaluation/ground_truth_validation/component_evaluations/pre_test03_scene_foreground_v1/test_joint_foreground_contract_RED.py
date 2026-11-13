"""Proposed scene-only witness contract; synthetic measurements, never identity GT.

Run against frozen c7cf871: the first two tests MUST fail until the proposed
versioned visual-witness policy is implemented. No production files are patched.
"""
import numpy as np
import pytest
from bai_badminton.perception.scene_change import ForegroundRegion, SceneContinuityDetectorV2


def replay(monkeypatch, actors, static):
    count = actors + static
    calls = 0
    def flow(*args):
        nonlocal calls
        pair, region = divmod(calls, count + 1)
        calls += 1
        if region == 0:
            return 80, 1.0, 1.0, 0.0
        changed = pair == 2 and region <= actors
        return 40, .1 if changed else .95, 100.0 if changed else 3.0, .1
    monkeypatch.setattr('bai_badminton.perception.scene_change._flow', flow)
    source = np.random.default_rng(761).integers(20, 220, (240, 480, 3), dtype=np.uint8)
    detector = SceneContinuityDetectorV2()
    result = None
    for frame in range(4):
        regions = [ForegroundRegion(frame - 1, f'visual:{k}', (20 + k*55, 20, 55 + k*55, 150), True, True) for k in range(count)] if frame else []
        result = detector.observe(frame, source, previous_regions=regions, previous_view_valid=True, current_view_valid=True)
    return result


def test_two_joint_actor_innovations_not_vetoed_by_static_extra(monkeypatch):
    result = replay(monkeypatch, 2, 1)
    assert len(result.regions) == 3
    assert result.correspondence_hypothesis, 'Static visual context currently vetoes both independent actor innovations'


def test_four_actor_doubles_plus_static_extra_remains_measurable(monkeypatch):
    result = replay(monkeypatch, 4, 1)
    assert len(result.regions) == 5, 'Current observer drops all five visual regions before measuring'
    assert result.correspondence_hypothesis


def test_one_changed_actor_plus_static_extra_is_insufficient(monkeypatch):
    result = replay(monkeypatch, 1, 2)
    assert not result.correspondence_hypothesis
    assert not result.hypothesis


def test_two_actor_supported_change_remains_positive_control(monkeypatch):
    result = replay(monkeypatch, 2, 0)
    assert result.correspondence_hypothesis
    assert result.authoritative is False
