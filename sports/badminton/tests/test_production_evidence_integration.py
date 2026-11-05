"""Real cached-candidate regression and controlled provider/consumer contracts."""

import json
from pathlib import Path

import msgpack
import numpy as np
import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception.association import CausalShuttleAssociation, ShuttleObservationEvidence
from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.diagnostics import FrameDiagnostic
from bai_badminton.perception.tracknet import ShuttleDetection
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import StaleCacheError
from bai_engine.config import ModelChoice, Profile
from bai_engine.store import EventStore


def test_source_bound_gt27_competing_peak_cannot_be_admitted_as_fresh_contact_coordinate():
    fixture = json.loads((Path(__file__).parent / "data/gt27_candidates_v1.json").read_text())
    provider = CausalShuttleAssociation(fps=30)
    rows = {}
    for raw in fixture["frames"]:
        evidence = provider.update(
            raw["f"],
            epoch=raw["sh"],
            raw_xy=raw["s"],
            raw_support=raw["c"],
            diagnostic=FrameDiagnostic.from_dict(raw["dg"]).shuttle,
            image_valid=not raw["r"],
            image_to_reference=np.linalg.inv(np.asarray(raw["g"]).reshape(3, 3)),
        )
        rows[raw["f"]] = evidence
    for frame in (12744, 12748, 12751, 12760, 12766):
        assert rows[frame].status == "ambiguous" and rows[frame].selected_xy is None
        assert rows[frame].raw_xy is not None
        assert max(rows[frame].competing_motion_frames) < frame
    assert rows[12738].status == rows[12769].status == "observed"
    assert rows[12769].association_status == "reacquisition"


@pytest.mark.parametrize("match_format", ["singles", "doubles", "unknown"])
def test_optional_candidate_association_executes_once_and_retains_raw_detections(tmp_path, monkeypatch, match_format):
    from test_perception_component_selection import StatefulShuttle, _chunk, _perception, _register, _registry
    from test_shuttle_association_evidence import diagnostic

    class Shuttle(StatefulShuttle):
        supports_diagnostics = True
        calls = 0

        def detect_with_diagnostics(self, images, shots, *, step, masks, selection, indices):
            self.calls += 1
            assert indices == set(range(20))
            points = [(100.0 + 12 * i, 150.0 - 6 * i) if i < 15 else (500.0, 400.0) for i in range(20)]
            return (
                [ShuttleDetection(*point, 0.8) for point in points],
                [diagnostic(point, ((500.0, 400.0),) if i < 15 else ()) for i, point in enumerate(points)],
            )

        def detect(self, *args, **kwargs):
            pytest.fail("candidate preservation must not repeat model inference")

    registry = _registry()
    _register(registry, "shuttle", lambda c, p: Shuttle(), stateful=True)
    profile = Profile(
        name="association",
        components={
            "shuttle": ModelChoice(model="none", backend="none", implementation="controlled"),
            "shuttle_association": ModelChoice(
                model="none", backend="none", implementation="coobserved-static-hypotheses-v1"
            ),
        },
    )
    pipeline = _perception(tmp_path, monkeypatch, profile, registry, match_format=match_format)
    result = pipeline.process(_chunk(count=20), in_play=True)
    assert pipeline.shuttle.calls == 1
    assert result.frames[15].shuttle_xy == (500.0, 400.0)
    assert result.frames[15].shuttle_observation.status == "ambiguous"
    assert all(frame.diagnostic is None for frame in result.frames)
    pipeline.reset_components()
    assert pipeline.shuttle_association.retained_samples == 0
    pipeline.close()


def test_ambiguous_sample_is_not_interpolated_but_raw_image_observation_is_preserved(tmp_path):
    engine = BadmintonMatchEngine(
        "E", EngineConfig(fps=30, frame_width=1280, frame_height=720), EventStore(tmp_path / "events.sqlite", "E")
    )
    frames = []
    for frame in range(9):
        point = (float(100 + frame * 5), 200.0)
        evidence = ShuttleObservationEvidence(
            frame,
            0,
            "ambiguous" if frame == 4 else "observed",
            "static_candidate" if frame == 4 else "tracked",
            point,
            None if frame == 4 else point,
            0.9,
        )
        frames.append(FramePerception(frame, point, 0.9, shuttle_observation=evidence))
    engine.ingest(ChunkPerception(0, 8, frames))
    window = engine._window(0, 8)
    assert not window.shuttle.vis[4] and not window.shuttle.interp[4]
    assert window.shuttle_evidence[4].raw_xy == frames[4].shuttle_xy
    raw = [sample for sample in engine.drain_tracks() if sample.obj.value == "shuttle"]
    assert raw[4].visible and raw[4].x == 120.0


def test_image_visibility_and_geometry_authority_remain_independent(tmp_path):
    engine = BadmintonMatchEngine(
        "E", EngineConfig(fps=30, frame_width=1280, frame_height=720), EventStore(tmp_path / "events.sqlite", "E")
    )
    evidence = ShuttleObservationEvidence(0, 0, "observed", "tracked", (20.0, 20.0), (20.0, 20.0), 0.9)
    frame = FramePerception(
        0,
        (20.0, 20.0),
        0.9,
        cam=np.eye(3),
        view="main",
        calibration_state=CalibrationState.REACQUIRING,
        shuttle_observation=evidence,
    )
    engine._append(frame, tracked=True, reference_matches=True)
    assert frame.shuttle_observation.status == "observed"
    assert engine._temporal_valid == [False] and engine._geometry_valid == [False]
    assert not engine._window(0, 0).shuttle.vis[0]
    assert engine.drain_tracks()[0].visible


@pytest.mark.parametrize("field,value", [("frame_idx", 24), ("raw_model_support", 0.8), ("raw_xy", [1.0, 1.0])])
def test_codec_rejects_detached_association_frame_or_raw_observation(tmp_path, field, value):
    from test_perception_diagnostic_provenance import _non30_cache_session

    session = _non30_cache_session(tmp_path)
    evidence = ShuttleObservationEvidence(25, 0, "observed", "tracked", (20.0, 20.0), (20.0, 20.0), 0.9)
    frame = FramePerception(
        25,
        (20.0, 20.0),
        0.9,
        view="main",
        calibration_state=CalibrationState.VALID,
        detector_observed=False,
        pose_stride=0,
        shuttle_observation=evidence,
    )
    record = msgpack.unpackb(session.encode_perception(ChunkPerception(25, 25, [frame])), raw=False)
    record["frames"][0]["sa"][field] = value
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    session.close()
