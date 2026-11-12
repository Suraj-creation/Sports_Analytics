"""Current observed alternatives keep their own support and raw provenance."""

import msgpack
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception.association import (
    CURRENT_ASSOCIATION_METHOD,
    CURRENT_ASSOCIATION_SCHEMA,
    ShuttleObservationEvidence,
)
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.diagnostics import HeatmapCandidate
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import StaleCacheError
from bai_engine.store import EventStore


def _alternative(frame, *, support=0.61, threshold=0.5):
    candidates = (
        HeatmapCandidate(1, (500.0, 400.0), (500.0, 400.0), 0.92, 4, 2.0, True, True, True),
        HeatmapCandidate(2, (80.0, 80.0), (79.0, 79.0), support, 3, 2.0, True, True, False),
    )
    return ShuttleObservationEvidence(
        frame_idx=frame,
        epoch=0,
        status="observed",
        association_status="tracked",
        raw_xy=(500.0, 400.0),
        selected_xy=(80.0, 80.0),
        raw_model_support=0.92,
        candidates=candidates,
        competing_motion_frames=tuple(range(frame - 4, frame - 1)),
        hypothesis_id=1,
        schema=CURRENT_ASSOCIATION_SCHEMA,
        method=CURRENT_ASSOCIATION_METHOD,
        selected_candidate_rank=2,
        selected_model_support=support,
        selection_coordinate_source="current_candidate_peak",
        selection_witness_frames=tuple(range(frame - 4, frame)),
        selection_model_threshold=threshold,
        selection_hypothesis_id=2,
        raw_masked_peak_xy=(500.0, 400.0),
    )


@pytest.mark.parametrize("support,threshold,activity_visible", [(0.61, 0.5, True), (0.4, 0.3, None)])
def test_engine_consumes_selected_point_and_support_without_rewriting_raw_track(
    tmp_path, support, threshold, activity_visible
):
    engine = BadmintonMatchEngine(
        "A", EngineConfig(fps=30, frame_width=1280, frame_height=720), EventStore(tmp_path / "events.sqlite", "A")
    )
    seen = []
    update = engine.activity.update

    def capture(observation):
        seen.append(observation)
        return update(observation)

    engine.activity.update = capture
    for index in range(4):
        point = (float(40 + index * 10), float(40 + index * 10))
        engine._append(FramePerception(index, point, 0.8))
    evidence = _alternative(4, support=support, threshold=threshold)
    frame = FramePerception(4, evidence.raw_xy, 0.92, shuttle_observation=evidence)
    engine._append(frame)
    assert (engine._sx[-1], engine._sy[-1]) == (80.0, 80.0)
    assert engine._sconf[-1] == support
    assert seen[-1].shuttle_visible is activity_visible
    assert frame.shuttle_xy == (500.0, 400.0) and frame.shuttle_conf == 0.92
    raw = [row for row in engine.drain_tracks() if row.obj.value == "shuttle"]
    assert (raw[-1].x, raw[-1].y, raw[-1].conf) == (500.0, 400.0, 0.92)


def _encoded_selection(tmp_path):
    from test_perception_diagnostic_provenance import _non30_cache_session

    session = _non30_cache_session(tmp_path)
    session.perception._component_metadata["shuttle_association"] = {
        "contract": {
            "implementation": "coobserved-static-hypotheses-v1",
            "version": "2",
            "output_schema": CURRENT_ASSOCIATION_SCHEMA,
        },
        "fingerprint": "1" * 64,
    }
    session.perception.runtimes["shuttle"] = {"inference_threshold": 0.5}
    frame = FramePerception(
        25,
        (500.0, 400.0),
        0.92,
        view="main",
        calibration_state=CalibrationState.VALID,
        detector_observed=False,
        pose_stride=0,
        shuttle_observation=_alternative(25),
    )
    return session, msgpack.unpackb(session.encode_perception(ChunkPerception(25, 25, [frame])), raw=False)


def test_codec_preserves_raw_and_distinct_current_selected_peak(tmp_path):
    session, record = _encoded_selection(tmp_path)
    assert record["v"] == 25
    decoded = session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True).frames[0]
    assert decoded.shuttle_xy == (500.0, 400.0)
    assert decoded.shuttle_conf == 0.92
    assert decoded.shuttle_observation.selected_xy == (80.0, 80.0)
    assert decoded.shuttle_observation.selected_model_support == 0.61
    session.close()


@pytest.mark.parametrize(
    "field,value",
    [
        ("selected_xy", [81.0, 80.0]),
        ("selected_candidate_rank", 3),
        ("selected_model_support", 0.92),
        ("selection_model_threshold", 0.7),
        ("selection_coordinate_source", "forecast"),
        ("selection_witness_frames", [25]),
        ("raw_masked_peak_xy", None),
    ],
)
def test_codec_rejects_detached_alternative_selection(tmp_path, field, value):
    session, record = _encoded_selection(tmp_path)
    record["frames"][0]["sa"][field] = value
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    session.close()


def test_codec_does_not_downgrade_selected_alternative_to_legacy_header(tmp_path):
    session, record = _encoded_selection(tmp_path)
    record["v"] = 24
    with pytest.raises(StaleCacheError, match="downgraded"):
        session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    session.close()


def test_codec_requires_unavailable_evidence_instead_of_null_for_enabled_association(tmp_path):
    session, record = _encoded_selection(tmp_path)
    record["frames"][0]["sa"] = None
    with pytest.raises(StaleCacheError, match="explicit observed or unavailable"):
        session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    session.close()


def test_codec_binds_non_diagnostic_alternative_to_actual_model_threshold(tmp_path):
    session, record = _encoded_selection(tmp_path)
    assert record["frames"][0]["dg"] is None
    # Still below selected support, so local candidate validation alone passes.
    record["frames"][0]["sa"]["selection_model_threshold"] = 0.6
    with pytest.raises(StaleCacheError, match="producer model policy"):
        session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    session.close()


def test_codec_rejects_runtime_and_selection_thresholds_that_disagree_with_compiled_model(tmp_path):
    session, record = _encoded_selection(tmp_path)
    session.perception._component_metadata["shuttle"] = {
        "contract": {"implementation": "baseline", "version": "1"},
        "fingerprint": "2" * 64,
        "configuration": {"model": "tracknetv3", "params": {"threshold": 0.5}},
    }
    session.perception.runtimes["shuttle"]["inference_threshold"] = 0.6
    record["ci"] = session._isolation_id()
    record["frames"][0]["sa"]["selection_model_threshold"] = 0.6
    with pytest.raises(StaleCacheError, match="threshold sources disagree"):
        session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    session.close()
