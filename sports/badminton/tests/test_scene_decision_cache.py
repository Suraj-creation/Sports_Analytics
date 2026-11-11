"""Detector layout decisions retain raw observation/frame/model provenance."""

from dataclasses import replace

import msgpack
import pytest
from test_perception_diagnostic_provenance import _non30_cache_session

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.content import SceneDecisionEvidence
from bai_badminton.perception.scene_change import ForegroundRegion, RegionContinuity, SceneChangeEvidence
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import StaleCacheError


def source_frame():
    boxes = ((100.0, 100.0, 200.0, 300.0), (400.0, 100.0, 500.0, 300.0))
    regions = tuple(
        RegionContinuity(ForegroundRegion(24, f"track:{i}", box, True, True), 10, 0.9, 1.0, 1.0, 1.0, 1.0, 1.0)
        for i, box in enumerate(boxes)
    )
    raw = SceneChangeEvidence(25, 24, "hypothesis", True, ("appearance_discontinuity",), regions)
    decision = SceneDecisionEvidence(
        25,
        24,
        "no_barrier",
        "current_layout_matches",
        True,
        25,
        "detector@1",
        "a" * 64,
        (720, 1280, 3),
        boxes,
        (0.9, 0.9),
        (0, 1),
        ((0, 0), (1, 1)),
        previous_region_count=2,
    )
    return FramePerception(
        25,
        None,
        0.0,
        view="main",
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
        pose_stride=0,
        content_change=raw,
        content_decision=decision,
    )


def payload(session):
    return session.encode_perception(
        ChunkPerception(25, 25, [source_frame()], models={"player_detector": "detector@1"})
    )


def test_decision_roundtrip_preserves_raw_hypothesis_without_claiming_a_barrier(tmp_path):
    session = _non30_cache_session(tmp_path)
    try:
        frame = session.decode_perception(payload(session), diagnostic=True).frames[0]
        assert frame.content_change.hypothesis is True
        assert frame.content_decision.decision == "no_barrier"
        assert frame.content_decision.detector_frame == 25
        assert frame.content_decision.matched_pairs == ((0, 0), (1, 1))
    finally:
        session.close()


@pytest.mark.parametrize(
    "key,value",
    [
        ("frame", 26),
        ("detector_frame", 26),
        ("detector_model", "other@1"),
        ("raw_hypothesis", False),
        ("previous_region_count", 3),
        ("detector_image_shape", [1000, 2000, 3]),
        ("detector_boxes", [[600.0, 100.0, 700.0, 300.0], [800.0, 100.0, 900.0, 300.0]]),
    ],
)
def test_cross_frame_or_cross_model_decision_is_rejected(tmp_path, key, value):
    session = _non30_cache_session(tmp_path)
    try:
        record = msgpack.unpackb(payload(session), raw=False)
        record["frames"][0]["cd"][key] = value
        with pytest.raises(StaleCacheError):
            session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    finally:
        session.close()


def test_new_codec_requires_decision_field_while_old_diagnostics_keep_unknown(tmp_path):
    session = _non30_cache_session(tmp_path)
    try:
        record = msgpack.unpackb(payload(session), raw=False)
        del record["frames"][0]["cd"]
        with pytest.raises(StaleCacheError):
            session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
        record["v"] = 20
        frame = session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True).frames[0]
        assert frame.content_decision is None
    finally:
        session.close()


def test_direct_decision_cannot_disagree_with_its_raw_hypothesis():
    frame = source_frame()
    with pytest.raises(ValueError, match="raw hypothesis"):
        replace(frame, content_change=replace(frame.content_change, hypothesis=False))


def test_layout_profile_cannot_drop_required_decision_metadata(tmp_path):
    from types import SimpleNamespace

    from bai_badminton.plugin import BadmintonSession

    session = _non30_cache_session(tmp_path)
    try:
        record = msgpack.unpackb(payload(session), raw=False)
        record["ci"]["profile"]["components"]["content_continuity"] = {
            "implementation": "foreground-content-continuity-v2",
            "params": {"mode": "barrier_detector_layout_v2"},
        }
        record["frames"][0]["cd"] = None
        receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=record["cr"]), _isolation_id=lambda: record["ci"])
        with pytest.raises(StaleCacheError, match="mandatory source decision"):
            BadmintonSession.decode_perception(receiver, msgpack.packb(record, use_bin_type=True), diagnostic=True)
    finally:
        session.close()
