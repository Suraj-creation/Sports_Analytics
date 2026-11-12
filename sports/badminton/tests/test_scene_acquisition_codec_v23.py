"""Native codec23 source/geometry proofs; synthetic Session, no neural/media IO."""

from copy import deepcopy
from dataclasses import replace
from types import SimpleNamespace

import msgpack
import numpy as np
import pytest
from test_perception_diagnostic_provenance import _non30_cache_session
from test_scene_acquisition_v4 import raw_relative
from test_scene_decision_cache import source_frame as legacy_source_frame

from bai_badminton.court import REFERENCE_POINTS, Homography
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.camera import project
from bai_badminton.perception.content import ContentContinuityProviderV2
from bai_badminton.perception.pipeline import lines_ref_id
from bai_badminton.perception.players import PlayerDetectionProbe, strict_court_indices
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import CODEC_VERSION, BadmintonSession, StaleCacheError

CURRENT = np.array([[1.0, 0.0, 2.0], [0.0, 1.0, 3.0], [0.0, 0.0, 1.0]])
PREVIOUS = np.array([[1.0, 0.0, 1.0], [0.0, 1.0, 1.0], [0.0, 0.0, 1.0]])
REFERENCE = np.array([[1000 / 6.1, 0.0, 600.0], [0.0, -600 / 13.4, 350.0], [0.0, 0.0, 1.0]])


@pytest.fixture
def session(tmp_path):
    value = _non30_cache_session(tmp_path)
    yield value
    value.close()


def native_record(session, *, count=2, include_previous=False):
    assert CODEC_VERSION >= 23
    raw = raw_relative(count, changed=2)
    raw = replace(
        raw,
        frame=25,
        previous_frame=24,
        regions=tuple(replace(r, region=replace(r.region, frame=24)) for r in raw.regions),
    )
    names = ("far_left", "far_right", "near_right", "near_left")
    reference = (
        Homography(REFERENCE, 0.0, 4).court_to_image(np.array([REFERENCE_POINTS[n] for n in names])).astype(np.float32)
    )
    polygon = tuple(tuple(float(v) for v in row) for row in project(CURRENT, reference).astype(np.float32))
    boxes = tuple((400.0 + 100 * i, 200.0, 430.0 + 100 * i, 400.0) for i in range(count))
    probe = PlayerDetectionProbe(
        25,
        (720, 1280, 3),
        "0" * 64,
        boxes,
        (0.95,) * count,
        (0, 0, 1280, 720),
        (),
        polygon,
        strict_court_indices(boxes, polygon),
    )
    decision = ContentContinuityProviderV2(mode="barrier_detector_layout_v2").layout_decision(
        raw,
        probe,
        detector_model="controlled-detector@1",
        geometry_valid=True,
        expected_participants=count,
        previous_camera=tuple(float(v) for v in PREVIOUS.ravel()),
        previous_to_current=tuple(float(v) for v in (CURRENT @ np.linalg.inv(PREVIOUS)).ravel()),
    )
    assert not raw.hypothesis and decision.decision == "barrier"
    frame = FramePerception(
        25,
        None,
        0.0,
        cam=CURRENT.copy(),
        view="main",
        calibration_state=CalibrationState.VALID,
        detector_observed=True,
        pose_stride=0,
        content_change=raw,
        content_decision=decision,
    )
    frames = [frame]
    if include_previous:
        frames.insert(
            0,
            FramePerception(
                24,
                None,
                0.0,
                cam=PREVIOUS.copy(),
                view="main",
                calibration_state=CalibrationState.VALID,
                detector_observed=False,
                pose_stride=0,
            ),
        )
    record = msgpack.unpackb(
        session.encode_perception(
            ChunkPerception(frames[0].frame_idx, 25, frames, models={"player_detector": "controlled-detector@1"})
        ),
        raw=False,
    )
    # This suite remains a legacy codec23 control. A new producer header must
    # not silently relabel these whole-ROI V4 measurements as exclusive origins.
    record["v"] = 23
    record["ci"]["layout_court_reference"] = REFERENCE.tolist()
    record["ci"]["court"] = lines_ref_id(REFERENCE)
    record["ci"]["match_format"] = "singles" if count == 2 else "doubles"
    record["ci"]["layout_format_confirmed"] = True
    record["ci"]["layout_format_context"] = {"match_format": "singles" if count == 2 else "doubles", "confirmed": True}
    record["ci"]["profile"]["components"]["content_continuity"] = {
        "implementation": "foreground-content-continuity-v2",
        "params": {"mode": "barrier_detector_layout_v2"},
    }
    return record


def receiver(record, policy=None):
    expected = deepcopy(record["ci"]) if policy is None else deepcopy(policy)
    return SimpleNamespace(perception=SimpleNamespace(ref_id=record["cr"]), _isolation_id=lambda: expected)


def decode(record, policy=None):
    return BadmintonSession.decode_perception(
        receiver(record, policy), msgpack.packb(record, use_bin_type=True), diagnostic=True
    )


@pytest.mark.parametrize("count", [2, 4])
@pytest.mark.parametrize("include_previous", [False, True])
def test_codec23_binds_weak_proof_to_calibrated_source_camera_and_court(session, count, include_previous):
    record = native_record(session, count=count, include_previous=include_previous)
    result = decode(record).frames[-1]
    assert result.content_decision.expected_participants == count
    assert result.content_decision.court_indices == tuple(range(count))
    assert result.content_decision.previous_camera == tuple(PREVIOUS.ravel())
    assert np.array_equal(result.cam, CURRENT)
    assert result.content_change.hypothesis is False and result.content_decision.decision == "barrier"
    assert result.persons == []  # Scene proof never manufactures athlete identities.


@pytest.mark.parametrize(
    "case",
    [
        "reference_missing",
        "reference_hash",
        "reference_nan",
        "polygon_shift",
        "polygon_other_court",
        "current_camera_missing",
        "current_camera_changed",
        "relative_changed",
        "previous_camera_missing",
        "model",
        "source_frame",
        "source_image_shape",
        "geometry_false",
        "view",
        "replay",
        "calibration",
    ],
)
def test_codec23_rejects_cross_source_or_forged_geometry_proofs(session, case):
    r = native_record(session)
    f = r["frames"][-1]
    d = f["cd"]
    if case == "reference_missing":
        r["ci"]["layout_court_reference"] = None
    if case == "reference_hash":
        r["ci"]["layout_court_reference"][0][2] += 1.0
    if case == "reference_nan":
        r["ci"]["layout_court_reference"][0][0] = float("nan")
    if case == "polygon_shift":
        d["court_polygon"] = [[x + 1.0, y] for x, y in d["court_polygon"]]
    if case == "polygon_other_court":
        d["court_polygon"] = [[250.0, 100.0], [950.0, 100.0], [950.0, 550.0], [250.0, 550.0]]
    if case == "current_camera_missing":
        f["g"] = None
    if case == "current_camera_changed":
        f["g"][2] += 1.0
    if case == "relative_changed":
        d["previous_to_current"][2] += 1.0
    if case == "previous_camera_missing":
        d["previous_camera"] = None
    if case == "model":
        r["models"]["player_detector"] = "another-detector@1"
    if case == "source_frame":
        d["detector_frame"] = 24
    if case == "source_image_shape":
        d["detector_image_shape"] = [721, 1280, 3]
    if case == "geometry_false":
        d["geometry_valid"] = False
    if case == "view":
        f["v"] = "alt"
    if case == "replay":
        f["r"] = True
    if case == "calibration":
        f["cs"] = "LOST"
    with pytest.raises(StaleCacheError):
        decode(r)


def test_codec23_binds_serialized_previous_camera_to_adjacent_cached_source(session):
    r = native_record(session, include_previous=True)
    d = r["frames"][-1]["cd"]
    fake = PREVIOUS.copy()
    fake[0, 2] = 5.0
    d["previous_camera"] = fake.ravel().tolist()
    d["previous_to_current"] = (CURRENT @ np.linalg.inv(fake)).ravel().tolist()
    # Internally invertible/consistent pair still disagrees with frame24.
    with pytest.raises(StaleCacheError):
        decode(r)


def test_codec23_rejects_current_camera_pair_even_at_chunk_start(session):
    r = native_record(session)
    r["frames"][0]["cd"]["previous_to_current"][2] += 1.0
    with pytest.raises(StaleCacheError):
        decode(r)


def test_ci_identity_is_receiver_bound_even_if_forged_court_and_hash_agree(session):
    r = native_record(session)
    original = deepcopy(r["ci"])
    fake = REFERENCE.copy()
    fake[0, 2] += 100.0
    r["ci"]["layout_court_reference"] = fake.tolist()
    r["ci"]["court"] = lines_ref_id(fake)
    with pytest.raises(StaleCacheError):
        decode(r, policy=original)


@pytest.mark.parametrize("case", ["null", "missing"])
def test_codec23_requires_weak_acquisition_decision_even_without_strong_hypothesis(session, case):
    r = native_record(session)
    if case == "null":
        r["frames"][0]["cd"] = None
    else:
        del r["frames"][0]["cd"]
    assert r["frames"][0]["cc"]["hypothesis"] is False
    with pytest.raises(StaleCacheError):
        decode(r)


@pytest.mark.parametrize("version", [21, 22])
def test_new_weak_families_cannot_be_downgraded_under_historical_codec(version, session):
    r = native_record(session)
    r["v"] = version
    if version == 21:
        r["frames"][0].pop("fg")
    with pytest.raises(StaleCacheError):
        decode(r)


@pytest.mark.parametrize("fmt,confirmed", [("doubles", True), ("unknown", True), ("singles", False), ("singles", None)])
def test_weak_expected_count_requires_confirmed_matching_producer_format(session, fmt, confirmed):
    r = native_record(session)
    r["ci"]["layout_format_context"] = {"match_format": fmt, "confirmed": confirmed}
    with pytest.raises(StaleCacheError):
        decode(r)


@pytest.mark.parametrize("version", [21, 22])
def test_actual_legacy_families_remain_readable_without_new_geometry_claims(session, version):
    r = msgpack.unpackb(
        session.encode_perception(
            ChunkPerception(25, 25, [legacy_source_frame()], models={"player_detector": "detector@1"})
        ),
        raw=False,
    )
    r["v"] = version
    if version == 21:
        r["frames"][0].pop("fg")
    raw = r["frames"][0]["cc"]
    decision = r["frames"][0]["cd"]
    for key in ["acquisition_region_keys", "relative_region_keys"]:
        raw.pop(key, None)
        decision.pop(key, None)
    for key in [
        "court_polygon",
        "court_indices",
        "expected_participants",
        "geometry_valid",
        "previous_to_current",
        "previous_camera",
    ]:
        decision.pop(key, None)
    result = decode(r).frames[0]
    assert result.content_change.version == "foreground-scene-hypothesis:v2"
    assert result.content_decision.version == "detector-layout-scene-decision:v1"


def test_chunk_start_format_proof_survives_later_observed_format_transition(session):
    r = native_record(session)
    r["ci"]["match_format"] = "doubles"
    r["ci"]["layout_format_confirmed"] = True
    assert r["ci"]["layout_format_context"] == {"match_format": "singles", "confirmed": True}
    assert decode(r).frames[0].content_decision.expected_participants == 2


def test_codec_rejects_camera_explained_replacement_even_with_consistent_source_camera_pair(session):
    r = native_record(session)
    f = r["frames"][0]
    d = f["cd"]
    transform = np.array([[1.0, 0.0, 200.0], [0.0, 1.0, 20.0], [0.0, 0.0, 1.0]])
    current = transform @ PREVIOUS
    f["g"] = current.ravel().tolist()
    d["previous_to_current"] = transform.ravel().tolist()
    for i, region in enumerate(f["cc"]["regions"]):
        region["region"]["bbox"] = [200.0 + i * 100, 180.0, 230.0 + i * 100, 380.0]
    names = ("far_left", "far_right", "near_right", "near_left")
    reference = (
        Homography(REFERENCE, 0.0, 4).court_to_image(np.array([REFERENCE_POINTS[n] for n in names])).astype(np.float32)
    )
    d["court_polygon"] = project(current, reference).astype(np.float32).tolist()
    # Raw prior boxes are disjoint, all current boxes remain in the real court,
    # and the source camera pair is consistent. Alignment restores both people.
    with pytest.raises(StaleCacheError):
        decode(r)


def test_missing_start_of_chunk_format_proof_cannot_authorize_weak_reset(session):
    r = native_record(session)
    r["ci"].pop("layout_format_context")
    with pytest.raises(StaleCacheError):
        decode(r)
