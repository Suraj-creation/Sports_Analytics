"""Bind new scene measurements to real cache policy; never reinterpret codec23."""

from copy import deepcopy
from types import SimpleNamespace

import msgpack
import numpy as np
import pytest
from test_perception_diagnostic_provenance import _non30_cache_session

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.scene_change import SceneContinuityDetectorV4, SceneContinuityDetectorV5
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import CODEC_VERSION, BadmintonSession, StaleCacheError


def record(session, *, legacy=False):
    observer = (SceneContinuityDetectorV4 if legacy else SceneContinuityDetectorV5)(analysis_width=480)
    raw = observer.observe(
        0,
        np.zeros((720, 1280, 3), dtype=np.uint8),
        previous_regions=(),
        previous_view_valid=True,
        current_view_valid=True,
    )
    frame = FramePerception(
        0,
        None,
        0.0,
        cam=np.eye(3),
        view="main",
        calibration_state=CalibrationState.VALID,
        detector_observed=False,
        pose_stride=0,
        content_change=raw,
    )
    value = msgpack.unpackb(session.encode_perception(ChunkPerception(0, 0, [frame], models={})), raw=False)
    value["ci"]["profile"]["components"]["content_continuity"] = {
        "implementation": "foreground-content-continuity-v2",
        "params": {"mode": "barrier_detector_layout_v2", "analysis_width": 480},
    }
    return value


def decode(value):
    policy = deepcopy(value["ci"])
    receiver = SimpleNamespace(perception=SimpleNamespace(ref_id=value["cr"]), _isolation_id=lambda: policy)
    return BadmintonSession.decode_perception(receiver, msgpack.packb(value, use_bin_type=True), diagnostic=True)


@pytest.fixture
def session(tmp_path):
    value = _non30_cache_session(tmp_path)
    yield value
    value.close()


@pytest.mark.parametrize("version", [24, 25, 26])
def test_new_origin_measurement_roundtrips_actual_source_and_analysis_dimensions(session, version):
    assert CODEC_VERSION == 26
    value = record(session)
    value["v"] = version
    result = decode(value).frames[0]
    assert result.content_change.version == "foreground-scene-hypothesis:v5"
    assert result.content_change.source_frame_size == (1280, 720)
    assert result.content_change.analysis_frame_size == (480, 270)
    assert result.content_change.hypothesis is False
    assert result.persons == []


@pytest.mark.parametrize("version", [17, 18, 19, 20, 21, 22, 23])
def test_new_measurement_cannot_acquire_authority_by_downgrading_header(session, version):
    value = record(session)
    value["v"] = version
    with pytest.raises(StaleCacheError):
        decode(value)


@pytest.mark.parametrize("case", ["source_width", "source_height", "raster_width", "raster_height", "policy_width"])
def test_measurement_dimensions_are_bound_to_actual_producer_policy(session, case):
    value = record(session)
    raw = value["frames"][0]["cc"]
    if case == "source_width":
        raw["source_frame_size"][0] += 1
    elif case == "source_height":
        raw["source_frame_size"][1] += 1
    elif case == "raster_width":
        raw["analysis_frame_size"][0] += 1
    elif case == "raster_height":
        raw["analysis_frame_size"][1] += 1
    else:
        value["ci"]["profile"]["components"]["content_continuity"]["params"]["analysis_width"] = 481
    with pytest.raises(StaleCacheError):
        decode(value)


def test_current_layout_policy_does_not_silently_relabel_old_measurement_basis(session):
    value = record(session, legacy=True)
    assert value["frames"][0]["cc"]["version"] == "foreground-scene-hypothesis:v4"
    with pytest.raises(StaleCacheError):
        decode(value)
    value["v"] = 23
    result = decode(value).frames[0]
    assert result.content_change.version == "foreground-scene-hypothesis:v4"


def adjacent_record(session):
    from bai_badminton.perception.scene_change import ForegroundRegion

    pixels = np.random.default_rng(42).integers(0, 255, (720, 1280, 3), dtype=np.uint8)
    regions = (
        ForegroundRegion(0, "controlled-a", (400, 200, 510, 400), True, True),
        ForegroundRegion(0, "controlled-b", (480, 350, 600, 550), True, True),
        ForegroundRegion(0, "controlled-context", (800, 200, 900, 400), False, False),
    )
    observer = SceneContinuityDetectorV5(analysis_width=480)
    raw0 = observer.observe(0, pixels, previous_regions=(), previous_view_valid=True, current_view_valid=True)
    raw1 = observer.observe(1, pixels, previous_regions=regions, previous_view_valid=True, current_view_valid=True)
    frames = [
        FramePerception(
            0,
            None,
            0.0,
            cam=np.eye(3),
            view="main",
            calibration_state=CalibrationState.VALID,
            content_change=raw0,
            foreground_regions=regions,
            detector_observed=True,
            pose_stride=0,
        ),
        FramePerception(
            1,
            None,
            0.0,
            cam=np.eye(3),
            view="main",
            calibration_state=CalibrationState.VALID,
            content_change=raw1,
            detector_observed=False,
            pose_stride=0,
        ),
    ]
    return msgpack.unpackb(session.encode_perception(ChunkPerception(0, 1, frames, models={})), raw=False)


def test_exclusive_origins_bind_all_actual_previous_foreground_regions(session):
    value = adjacent_record(session)
    result = decode(value)
    assert tuple(row.region for row in result.frames[1].content_change.regions) == result.frames[0].foreground_regions


@pytest.mark.parametrize("case", ["omit_context", "relabel", "shift_box", "reorder"])
def test_self_consistent_mask_rewrite_cannot_change_actual_previous_foreground(session, case):
    from dataclasses import replace

    from bai_badminton.perception.content import scene_change_from_dict, scene_change_to_dict
    from bai_badminton.perception.scene_change import exclusive_feature_origin_masks

    value = adjacent_record(session)
    raw = scene_change_from_dict(value["frames"][1]["cc"])
    regions = list(raw.regions)
    if case == "omit_context":
        regions.pop()
    elif case == "relabel":
        regions[-1] = replace(regions[-1], region=replace(regions[-1].region, key="substituted"))
    elif case == "shift_box":
        regions[-1] = replace(regions[-1], region=replace(regions[-1].region, bbox=(820, 200, 920, 400)))
    else:
        regions.reverse()
    _, masks = exclusive_feature_origin_masks(
        [row.region for row in regions], raw.source_frame_size, raw.analysis_frame_size
    )
    changed = replace(raw, regions=tuple(regions), origin_masks=masks)
    # Recompute every declared mask: self-consistency is not source binding.
    value["frames"][1]["cc"] = scene_change_to_dict(changed)
    with pytest.raises(StaleCacheError, match="actual previous-frame foreground"):
        decode(value)
