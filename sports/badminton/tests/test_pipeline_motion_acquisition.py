"""Causal scheduling integration with weightless NN ports, not physical GT."""

import numpy as np
import pytest
from test_content_pipeline_integration import chunk, perception

from bai_badminton.perception.acquisition import ObservedMotionAcquisition
from bai_badminton.perception.association import CausalShuttleAssociation
from bai_badminton.perception.diagnostics import HeatmapCandidate, ShuttleDiagnostic
from bai_badminton.perception.scene_change import SceneChangeEvidence
from bai_badminton.perception.tracknet import ShuttleDetection
from bai_engine.config import ModelChoice, Rates
from bai_engine.runtime.registry import ModelRegistry


class MovingObservedShuttle:
    seq_len = 8
    supports_diagnostics = True
    bg = None

    def __init__(self, *, moving=True):
        self.moving = moving

    def detect(self, frames_bgr, shots, *, step, masks):
        raise AssertionError("candidate evidence must use normal diagnostic port")

    def detect_with_diagnostics(self, frames_bgr, shots, *, step, masks, selection, indices):
        detections, diagnostics = [], []
        for image in frames_bgr:
            frame = int(image[0, 0, 0]) - 10
            point = (30.0 + 4 * frame if self.moving else 30.0, 40.0)
            detections.append(ShuttleDetection(*point, 0.9))
            candidate = HeatmapCandidate(1, point, point, 0.9, 20, 3.0, True, True, True)
            diagnostics.append(ShuttleDiagnostic(
                (candidate,), 0.9, 0.9, 0.5, 0.1, "accepted", 1,
                decoded_xy=point, selected_masked_peak_xy=point,
            ))
        return detections, diagnostics


def configured(tmp_path, monkeypatch, *, count=2, content=True, moving=True):
    p, ports, _ = perception(tmp_path, monkeypatch, count=count, enabled=content, barrier=False)
    p.profile.detector_rates = Rates(in_play=2, idle=6, replay=0)
    p.profile.pose_rates = Rates(in_play=1, idle=6, replay=0)
    p.shuttle = MovingObservedShuttle(moving=moving)
    p.shuttle_association = CausalShuttleAssociation(fps=30)
    p._motion_acquisition = ObservedMotionAcquisition(
        minimum_motion_px_per_frame=p.shuttle_association.minimum_motion_px_per_frame,
        maximum_age_frames=p.shuttle_association.maximum_age_frames,
    )
    rates = []
    original = p.players.process

    def record(frame, image, strides):
        rates.append((frame, strides))
        return original(frame, image, strides)

    p.players.process = record
    return p, ports, rates


@pytest.mark.parametrize("count", [2, 4])
@pytest.mark.parametrize("content", [True, False])
def test_observed_completed_chunk_requests_next_configured_rates_without_future_peeking(
    tmp_path, monkeypatch, count, content
):
    p, _, rates = configured(tmp_path, monkeypatch, count=count, content=content)
    first = p.process(chunk(0, 8), in_play=False)
    assert all(strides == (6, 6) for _, strides in rates)
    assert all(frame.acquisition_request is None for frame in first.frames)
    rates.clear()
    second = p.process(chunk(8, 8), in_play=False)
    assert all(strides == (2, 1) for _, strides in rates)
    for frame in second.frames:
        proof = frame.acquisition_request
        assert proof.decision_frame == 8 and proof.completed_chunk_end == 7
        assert proof.source_frames == (4, 5, 6, 7)
        assert proof.source_frames[-1] < second.start
        assert proof.authority == "configured_sampling_request_only"
    assert len(second.frames[-1].persons) == count
    p.close()


def test_stationary_model_observations_do_not_request_dense_acquisition(tmp_path, monkeypatch):
    p, _, rates = configured(tmp_path, monkeypatch, moving=False)
    p.process(chunk(0, 8), in_play=False)
    second = p.process(chunk(8, 8), in_play=False)
    assert all(strides == (6, 6) for _, strides in rates)
    assert all(frame.acquisition_request is None for frame in second.frames)
    p.close()


@pytest.mark.parametrize("det_idle,pose_idle,expected", [(0, 0, (0, 0)), (0, 6, (0, 1)), (6, 0, (2, 0))])
def test_hint_cannot_enable_profile_disabled_sampling(tmp_path, monkeypatch, det_idle, pose_idle, expected):
    p, _, rates = configured(tmp_path, monkeypatch)
    p.profile.detector_rates.idle = det_idle
    p.profile.pose_rates.idle = pose_idle
    p.process(chunk(0, 8), in_play=False)
    rates.clear()
    second = p.process(chunk(8, 8), in_play=False)
    assert all(strides == expected for _, strides in rates)
    if expected == (0, 0):
        assert all(frame.acquisition_request is None for frame in second.frames)
    p.close()


def test_content_cut_revokes_request_for_remaining_chunk(tmp_path, monkeypatch):
    p, ports, rates = configured(tmp_path, monkeypatch)
    p.process(chunk(0, 8), in_play=False)
    ports["content_continuity"].barrier_enabled = True
    ports["content_continuity"].observe = lambda frame, image, **kw: SceneChangeEvidence(
        frame, frame - 1, "hypothesis" if frame == 10 else "measured", frame == 10,
        ("controlled_cut" if frame == 10 else "controlled_continuity",),
    )
    rates.clear()
    second = p.process(chunk(8, 8), in_play=False)
    assert [strides for _, strides in rates] == [(2, 1)] * 2 + [(6, 6)] * 6
    assert all(frame.acquisition_request is None for frame in second.frames[2:])
    assert second.frames[-1].content_epoch == 1
    p.close()


def test_view_invalidation_permanently_cancels_hint_within_same_chunk(tmp_path, monkeypatch):
    p, _, rates = configured(tmp_path, monkeypatch)
    p.process(chunk(0, 8), in_play=False)
    original_scene = p._scene

    def interrupted(chunk, cuts):
        scene = original_scene(chunk, cuts)
        scene.views[2] = "alt"
        return scene

    monkeypatch.setattr(p, "_scene", interrupted)
    rates.clear()
    second = p.process(chunk(8, 8), in_play=False)
    assert second.frames[-1].calibration_state.value == "VALID"
    assert all(frame.acquisition_request is None for frame in second.frames[2:])
    assert all(strides == (6, 6) for frame, strides in rates if frame >= 10)
    p.close()


def test_failed_downstream_chunk_never_publishes_motion_evidence(tmp_path, monkeypatch):
    p, _, _ = configured(tmp_path, monkeypatch)

    def fail(*args, **kwargs):
        raise RuntimeError("controlled OCR failure")

    monkeypatch.setattr(p, "_read_scoreboard", fail)
    with pytest.raises(RuntimeError, match="controlled OCR"):
        p.process(chunk(0, 8), in_play=False)
    with pytest.raises(ValueError, match="incomplete"):
        p._motion_acquisition.request(8, 7 << 32)
    p.reset_components()
    assert p._motion_acquisition.request(8, 7 << 32) is None
    p.close()


def test_actual_registry_constructor_derives_motion_policy_from_association(tmp_path, monkeypatch):
    p, _, _ = perception(tmp_path, monkeypatch)
    assert p.motion_acquisition_policy is None
    p.profile.components["shuttle_association"] = ModelChoice(
        model="none", backend="none", implementation="coobserved-static-hypotheses-v1",
    )
    models = tmp_path / "models"
    actual = type(p)(
        p.profile, ModelRegistry(models), 30.0, models, (180, 120), component_registry=p.component_registry,
    )
    assert actual.motion_acquisition_policy["minimum_motion_px_per_frame"] == 3.0
    assert actual.motion_acquisition_policy["maximum_age_frames"] == 60
    assert actual.motion_acquisition_policy["authority"] == "configured_sampling_request_only"
    actual.close()
    p.close()


def test_motion_in_image_due_only_to_camera_registration_cannot_request_sampling(tmp_path, monkeypatch):
    p, _, rates = configured(tmp_path, monkeypatch)
    original_scene = p._scene

    def moving_camera(chunk, cuts):
        scene = original_scene(chunk, cuts)
        scene.poses = [np.array([[1.0, 0.0, 4.0 * (chunk.start + i)], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
                       for i in range(len(chunk.frames))]
        return scene

    monkeypatch.setattr(p, "_scene", moving_camera)
    p.process(chunk(0, 8), in_play=False)
    second = p.process(chunk(8, 8), in_play=False)
    assert all(strides == (6, 6) for _, strides in rates)
    assert all(frame.acquisition_request is None for frame in second.frames)
    p.close()


def test_request_never_slows_already_faster_idle_rates(tmp_path, monkeypatch):
    p, _, rates = configured(tmp_path, monkeypatch)
    p.profile.detector_rates = Rates(in_play=6, idle=1)
    p.profile.pose_rates = Rates(in_play=6, idle=1)
    p.process(chunk(0, 8), in_play=False)
    second = p.process(chunk(8, 8), in_play=False)
    assert all(strides == (1, 1) for _, strides in rates)
    assert all(frame.acquisition_request is None for frame in second.frames)
    p.close()


def test_existing_in_play_schedule_needs_no_additional_request(tmp_path, monkeypatch):
    p, _, rates = configured(tmp_path, monkeypatch)
    p.process(chunk(0, 8), in_play=False)
    rates.clear()
    second = p.process(chunk(8, 8), in_play=True)
    assert all(strides == (2, 1) for _, strides in rates)
    assert all(frame.acquisition_request is None for frame in second.frames)
    p.close()
