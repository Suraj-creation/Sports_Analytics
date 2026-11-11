"""Fresh outside hypotheses, true geometric anchors and strict probes differ.

Weightless detector/tracker ports isolate state and metadata contracts. These
cases do not establish physical identity, official rejection or scene accuracy.
"""

from dataclasses import replace
from hashlib import sha256

import numpy as np
import pytest

from bai_badminton.perception.players import CourtROI, PlayerDetectionProbe, PlayerPerception, strict_court_indices


class FullFrameROI(CourtROI):
    """Keep test offcourt pixels visible to the detector without padded feet."""

    def crop_box(self, width, height, top_margin=0.25):
        return 0, 0, width, height


class EchoTracker:
    def update(self, boxes, scores, frame):
        return [(i, box.copy(), float(score)) for i, (box, score) in enumerate(zip(boxes, scores, strict=True))]

    def reset(self):
        pass


def setup(count=2):
    state = {"bottom": 95.0, "left": 0.0, "missing": False, "calls": 0}

    def detector(_image):
        state["calls"] += 1
        if state["missing"]:
            return np.empty((0, 4)), np.empty(0)
        return np.array(
            [
                [10.0 + i * 45 + state["left"], 10.0, 30.0 + i * 45 + state["left"], state["bottom"]]
                for i in range(count)
            ]
        ), np.full(count, 0.95)

    p = PlayerPerception(detector, None, 30, det_stride=1, pose_stride=0, max_players=count)
    p.tracker = EchoTracker()
    p.set_roi(FullFrameROI(np.array([[0, 0], [350, 0], [350, 100], [0, 100]], np.float32), pad_px=0))
    return p, state, np.zeros((160, 360, 3), np.uint8)


@pytest.mark.parametrize("count", [2, 4])
def test_continuously_fresh_outside_hypothesis_then_carry_expires_without_actual_anchor_renewal(count):
    p, state, image = setup(count)
    assert len(p.process(0, image)) == count
    state["bottom"] = 105.0
    for frame in range(1, 61):
        assert len(p.process(frame, image)) == count
        assert set(p._court_anchor_frames.values()) == {0}
    for frame in range(61, 91):
        carried = p.process(frame, image, (1000, 0))
        assert len(carried) == count and not any(x.detector_matched for x in carried)
        assert set(t for t, _ in p._court_tracks.values()) == {60}
        assert set(p._court_anchor_frames.values()) == {0}
    assert p.process(91, image, (1000, 0)) == []
    assert p._court_tracks == {} and p._court_anchor_frames == {}


def test_empty_fresh_model_frames_expire_origin_and_outside_cannot_rebootstrap():
    p, state, image = setup()
    p.process(0, image)
    state["bottom"] = 105.0
    for frame in range(1, 41):
        p.process(frame, image)
    state["missing"] = True
    for frame in range(41, 72):
        p.process(frame, image)
    assert p._court_tracks == {} and p._court_anchor_frames == {}
    state["missing"] = False
    assert p.process(72, image) == []
    assert p._court_tracks == {} and p._court_anchor_frames == {}


@pytest.mark.parametrize("count", [2, 4])
def test_cut_rechecks_outside_admission_even_when_reusing_prior_inherited_probe(count):
    p, state, image = setup(count)
    p.process(0, image)
    state["bottom"] = 105.0
    p.process(1, image)
    probe = p.probe_detection(2, image)
    assert probe.admitted_indices == tuple(range(count))
    assert probe.court_indices == ()
    p.on_cut()
    assert p._court_tracks == {} and p._court_anchor_frames == {}
    assert p.process(2, image, detection_probe=probe) == []
    assert p._court_tracks == {} and p._court_anchor_frames == {}


def test_raw_probe_court_indices_do_not_inherit_outside_continuity_and_probe_is_read_only():
    p, state, image = setup()
    p.process(0, image)
    before = {k: (v[0], v[1].copy()) for k, v in p._court_tracks.items()}
    state["bottom"] = 105.0
    probe = p.probe_detection(1, image)
    assert probe.admitted_indices == (0, 1) and probe.court_indices == ()
    assert p._court_anchor_frames == {0: 0, 1: 0}
    assert all(p._court_tracks[k][0] == v[0] and np.array_equal(p._court_tracks[k][1], v[1]) for k, v in before.items())
    assert state["calls"] == 2
    p.process(1, image, detection_probe=probe)
    assert state["calls"] == 2
    assert set(t for t, _ in p._court_tracks.values()) == {1}
    assert set(p._court_anchor_frames.values()) == {0}


def strict_probe():
    image = np.zeros((160, 360, 3), np.uint8)
    polygon = ((0.0, 0.0), (350.0, 0.0), (350.0, 100.0), (0.0, 100.0))
    boxes = ((10.0, 10.0, 30.0, 105.0), (60.0, 10.0, 80.0, 95.0))
    return PlayerDetectionProbe(
        1,
        image.shape,
        sha256(image.tobytes()).hexdigest(),
        boxes,
        (0.95, 0.95),
        (0, 0, 360, 160),
        (0, 1),
        polygon,
        (1,),
    )


def test_strict_polygon_boundary_is_inclusive_without_padded_admission():
    polygon = ((0.0, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0))
    assert strict_court_indices(((10.0, 10.0, 30.0, 100.0), (10.0, 10.0, 30.0, 100.0001)), polygon) == (0,)


@pytest.mark.parametrize("indices", [(0,), (0, 1), (1, 1), (2,), ()])
def test_forged_strict_indices_disagreeing_with_geometry_are_rejected(indices):
    with pytest.raises(ValueError, match="strict court"):
        replace(strict_probe(), court_indices=indices)


@pytest.mark.parametrize("indices", [(True,), (1.0,), (np.int64(1),)])
def test_strict_indices_require_canonical_integer_types_not_numeric_aliases(indices):
    with pytest.raises(ValueError):
        replace(strict_probe(), court_indices=indices)


@pytest.mark.parametrize(
    "polygon",
    [
        ((0.0, 0.0), (100.0, 0.0)),
        ((0.0, 0.0), (100.0, 100.0), (0.0, 100.0), (100.0, 0.0)),
        ((0.0, 0.0), (100.0, 0.0), (50.0, 20.0), (100.0, 100.0), (0.0, 100.0)),
        ((0.0, 0.0), (10.0, 0.0), (20.0, 0.0)),
        ((False, 0.0), (100.0, 0.0), (100.0, 100.0), (0.0, 100.0)),
        ((0.0, 0.0), (float("nan"), 0.0), (100.0, 100.0), (0.0, 100.0)),
        ((0.0, 0.0), (float("inf"), 0.0), (100.0, 100.0), (0.0, 100.0)),
    ],
)
def test_malformed_or_forged_polygon_cannot_supply_strict_membership(polygon):
    with pytest.raises(ValueError):
        replace(strict_probe(), court_polygon=polygon)


def test_changed_valid_polygon_requires_recomputed_indices_before_any_geometry_binding():
    probe = strict_probe()
    # This only proves internal pixel geometry. A consistent but foreign court
    # requires the separate frame/calibration binding, never a name/role claim.
    with pytest.raises(ValueError, match="strict court"):
        replace(probe, court_polygon=((0.0, 0.0), (350.0, 0.0), (350.0, 140.0), (0.0, 140.0)))
