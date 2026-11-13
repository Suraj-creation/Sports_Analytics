"""Synthetic regressions for the observed-context overhaul; no media or model assets."""

import json
from dataclasses import dataclass

import numpy as np
import pytest
import torch

from bai_badminton.perception import tracknet
from bai_badminton.perception.players import PlayerDetector, PlayerPerception, PoseEstimator
from bai_badminton.perception.shuttle_post import Track, fill_gaps
from bai_badminton.perception_types import PersonObs
from bai_engine.trace import trace_frames, trace_session


def synthetic_detector(batch=2):
    model = tracknet.TrackNetV3.__new__(tracknet.TrackNetV3)
    model.seq_len, model.in_dim, model.batch, model.threshold = 8, 27, batch, 0.5
    model.bg = tracknet.BackgroundModel()
    return model


def test_temporal_input_stacks_are_built_only_for_the_current_batch(monkeypatch):
    model = synthetic_detector()
    concatenate = np.concatenate
    constructed = 0
    executed = []

    def stack(*args, **kwargs):
        nonlocal constructed
        constructed += 1
        return concatenate(*args, **kwargs)

    def forward(inputs):
        nonlocal constructed
        assert constructed == len(inputs) <= model.batch
        executed.append(len(inputs))
        constructed = 0
        return np.zeros((len(inputs), 8, tracknet.HEIGHT, tracknet.WIDTH), np.float32)

    monkeypatch.setattr(tracknet.np, "concatenate", stack)
    model._forward = forward
    outputs = model.detect([np.zeros((36, 64, 3), np.uint8) for _ in range(24)])
    assert len(outputs) == 24 and executed == [2, 1]


@pytest.mark.parametrize("bad", ["shape", "nonfinite"])
def test_invalid_heatmap_contract_fails_before_point_decoding(bad):
    model = synthetic_detector()

    def forward(inputs):
        channels = 7 if bad == "shape" else 8
        output = np.zeros((len(inputs), channels, tracknet.HEIGHT, tracknet.WIDTH), np.float32)
        if bad == "nonfinite":
            output[0, 0, 0, 0] = np.nan
        return output

    model._forward = forward
    with pytest.raises(ValueError, match="invalid heatmaps"):
        model.detect([np.zeros((36, 64, 3), np.uint8)])


@pytest.mark.parametrize("bad", [np.zeros((36, 64), np.uint8), np.zeros((36, 64, 3), np.float32)])
def test_invalid_frame_storage_is_rejected_before_forward(bad):
    model = synthetic_detector()
    model._forward = lambda _: pytest.fail("invalid image reached model execution")
    with pytest.raises(ValueError, match="frames must"):
        model.detect([bad])


def test_export_does_not_mutate_live_model_device_or_precision(monkeypatch, tmp_path):
    @dataclass
    class Model:
        device: str = "cuda:1"
        dtype: str = "float16"

        def float(self):
            self.dtype = "float32"
            return self

        def cpu(self):
            self.device = "cpu"
            return self

    exported = []
    monkeypatch.setattr(torch, "zeros", lambda *_: object())
    monkeypatch.setattr(torch.onnx, "export", lambda model, *_args, **_kwargs: exported.append(model))
    model = synthetic_detector()
    live = model._torch = Model()
    model.export_onnx(tmp_path / "synthetic.onnx")
    assert live.device == "cuda:1" and live.dtype == "float16"
    assert exported[0] is not live
    assert exported[0].device == "cpu" and exported[0].dtype == "float32"


def test_real_spline_overshoot_cannot_bypass_endpoint_speed_gate():
    # Both observed anchor runs move at120px/frame, while gap endpoints imply100.
    # The natural spline would create an interior161.75px/frame edge.
    x = np.array([240, 120, 0, np.nan, np.nan, 300, 180, 60], dtype=float)
    raw = Track.from_arrays(x, np.where(np.isfinite(x), 100.0, np.nan), np.isfinite(x), np.full(8, 0.9))
    repaired = fill_gaps(raw)
    assert not repaired.vis[3:5].any() and not repaired.interp[3:5].any()
    np.testing.assert_array_equal(repaired.x, raw.x)
    np.testing.assert_array_equal(repaired.conf, raw.conf)


def test_reconstruction_support_cannot_exceed_weakest_contributing_anchor():
    x = np.array([0, 10, 20, np.nan, 40, 50, 60], dtype=float)
    raw = Track.from_arrays(x, np.where(np.isfinite(x), 100.0, np.nan), np.isfinite(x),
                            np.array([0.9, 0.8, 0.2, 0, 0.9, 0.8, 0.7]))
    repaired = fill_gaps(raw)
    assert repaired.vis[3] and repaired.interp[3]
    assert repaired.conf[3] == pytest.approx(0.2)
    assert not raw.vis[3] and raw.conf[3] == 0


@pytest.mark.parametrize("bad_conf", [np.nan, np.inf, -0.1, 1.1])
def test_visible_shuttle_requires_finite_unit_interval_support(bad_conf):
    with pytest.raises(ValueError, match="visible shuttle support"):
        Track.from_arrays(np.array([1.0]), np.array([2.0]), np.array([True]), np.array([bad_conf]))


def test_shuttle_arrays_cannot_broadcast_different_frame_populations():
    with pytest.raises(ValueError, match="aligned one-dimensional"):
        Track.from_arrays(np.arange(3.0), np.array([2.0]), np.ones(3, bool))


def test_pose_crop_rejection_preserves_four_person_output_ownership():
    estimator = PoseEstimator.__new__(PoseEstimator)
    boxes = np.array([[1, 2, 10, 20], [20, 2, 10, 20], [np.nan, 2, 10, 20], [31, 2, 40, 20]], float)
    seen = []

    def tool(rgb, *, bboxes):
        seen.extend(bboxes)
        np.testing.assert_array_equal(rgb[0, 0], [30, 20, 10])
        return np.array([np.full((17, 2), box[0]) for box in bboxes]), np.ones((len(bboxes), 17))

    estimator.tool = tool
    output = estimator(np.full((30, 50, 3), [10, 20, 30], np.uint8), boxes)
    assert seen == [boxes[0].tolist(), boxes[3].tolist()]
    assert len(output) == 4 and output[1:3] == [None, None]
    assert output[0][0, 0] == 1 and output[3][0, 0] == 31


def test_missing_pose_joint_has_zero_support_without_remapping_person():
    estimator = PoseEstimator.__new__(PoseEstimator)

    def tool(_image, *, bboxes):
        kps = np.ones((len(bboxes), 17, 2))
        support = np.ones((len(bboxes), 17))
        kps[0, 9, 0] = np.nan
        support[1] = 0
        return kps, support

    estimator.tool = tool
    output = estimator(np.zeros((30, 50, 3), np.uint8), [np.array([1, 2, 10, 20])] * 2)
    assert output[0].shape == (17, 3) and output[1] is None
    assert np.isnan(output[0][9, :2]).all() and output[0][9, 2] == 0


def test_pose_provider_person_count_mismatch_is_explicit():
    estimator = PoseEstimator.__new__(PoseEstimator)
    estimator.tool = lambda *_args, **_kwargs: (np.ones((1, 17, 2)), np.ones((1, 17)))
    with pytest.raises(ValueError, match="COCO17 outputs per crop"):
        estimator(np.zeros((30, 50, 3), np.uint8), [np.array([1, 2, 10, 20])] * 2)


def test_real_detector_adapter_emits_bounded_shape_count_and_frame_trace(tmp_path):
    detector = PlayerDetector.__new__(PlayerDetector)
    detector.kind = "rfdetr"
    detector._rfdetr = lambda _image: (np.array([[1, 2, 10, 20]], float), np.array([0.9]))
    with trace_session(tmp_path, "synthetic-run", "a" * 64), trace_frames(12, 12):
        detector(np.zeros((30, 50, 3), np.uint8))
    record = json.loads(next(tmp_path.glob("*.jsonl")).read_text())
    assert record["component"] == "player_detector" and record["frame_start"] == record["frame_end"] == 12
    assert record["attributes"]["boxes_shape"] == [1, 4]
    assert record["attributes"]["output_finite"] is True
    assert record["error"] is None and record["timing_semantics"] == "host_wall_time_no_device_sync"


def test_pose_trace_preserves_each_persons_missing_output_and_current_match(tmp_path):
    def pose(_image, _boxes):
        return [np.ones((17, 3)), None]

    pipeline = PlayerPerception(None, pose, 30)
    persons = [PersonObs(i, np.array([1, 2, 10, 20], float), 0.9, detector_matched=bool(i)) for i in range(2)]
    with trace_session(tmp_path, "synthetic-pose", "a" * 64):
        pipeline._attach(12, np.zeros((30, 50, 3), np.uint8), persons, 1)
    record = json.loads(next(tmp_path.glob("*.jsonl")).read_text())
    assert record["component"] == "pose" and record["frame_start"] == record["frame_end"] == 12
    assert record["attributes"]["missing_count"] == 1
    assert record["attributes"]["current_detector_matches"] == 1
    assert [person.pose_frame_idx for person in persons] == [12, None]


def test_shuttle_trace_reports_actual_batches_without_tensor_payloads(tmp_path):
    model = synthetic_detector()
    model._forward = lambda inputs: np.zeros((len(inputs), 8, tracknet.HEIGHT, tracknet.WIDTH), np.float32)
    with trace_session(tmp_path, "synthetic-shuttle", "a" * 64), trace_frames(0, 23):
        model.detect([np.zeros((36, 64, 3), np.uint8) for _ in range(24)])
    records = [json.loads(line) for line in next(tmp_path.glob("*.jsonl")).read_text().splitlines()]
    forwards = [record for record in records if record["component"] == "shuttle_forward"]
    assert [record["attributes"]["input_shape"] for record in forwards] == [[2, 27, 288, 512], [1, 27, 288, 512]]
    assert all(record["frame_start"] == 0 and record["frame_end"] == 23 for record in forwards)
    assert all(len(json.dumps(record)) < 2000 for record in records)
