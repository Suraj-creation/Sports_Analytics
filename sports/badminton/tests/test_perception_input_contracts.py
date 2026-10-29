"""Checkpoint input contracts, elapsed-time tracking, and temporal scene isolation."""

from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.perception.players import PlayerDetector, PlayerPerception, PlayerTracker, PoseEstimator
from bai_badminton.perception.tracknet import HEIGHT, WIDTH, BackgroundModel, TrackNetV3


def test_rfdetr_receives_rgb_normalisation_and_preserves_person_class_and_box_scaling():
    from rtmlib import RFDETR

    detector = PlayerDetector.__new__(PlayerDetector)
    detector.kind = "rfdetr"
    tool = detector.tool = RFDETR.__new__(RFDETR)
    tool.model_input_size = (512, 512)
    tool.mean = np.array([0.485, 0.456, 0.406], np.float32)
    tool.std = np.array([0.229, 0.224, 0.225], np.float32)
    tool.score_thr = 0.35
    observed = []

    def inference(tensor):
        observed.append(tensor.copy())
        # Query 0 is person; query 1 has a strong background score only.
        return [
            np.array([[[0.5, 0.5, 0.5, 0.5], [0.2, 0.2, 0.1, 0.1]]]),
            np.array([[[-10.0, 10.0, -10.0], [10.0, -10.0, -10.0]]]),
        ]

    tool.inference = inference
    bgr = np.full((80, 160, 3), [5, 25, 200], np.uint8)
    boxes, scores = detector(bgr)
    expected = (np.array([200, 25, 5]) / 255 - tool.mean) / tool.std
    np.testing.assert_allclose(observed[0][256, 256], expected, atol=1e-6)
    np.testing.assert_allclose(boxes, [[40, 20, 120, 60]])
    assert scores.shape == (1,) and scores[0] > 0.99
    np.testing.assert_array_equal(bgr[0, 0], [5, 25, 200])


def test_rtmpose_receives_rgb_before_actual_affine_crop_and_normalisation():
    from rtmlib import RTMPose

    estimator = PoseEstimator.__new__(PoseEstimator)
    tool = estimator.tool = RTMPose.__new__(RTMPose)
    tool.model_input_size = (192, 256)
    tool.mean = (123.675, 116.28, 103.53)
    tool.std = (58.395, 57.12, 57.375)
    tool.to_openpose = False
    observed = []

    def inference(tensor):
        observed.append(tensor.copy())
        x, y = np.zeros((1, 17, 384)), np.zeros((1, 17, 512))
        x[:, :, 192], y[:, :, 256] = 1.0, 1.0
        return [x, y]

    tool.inference = inference
    bgr = np.full((256, 192, 3), [5, 25, 200], np.uint8)
    result = estimator(bgr, [np.array([32, 32, 96, 128], float)])
    expected = (np.array([200, 25, 5]) - tool.mean) / tool.std
    np.testing.assert_allclose(observed[0][128, 96], expected, atol=1e-6)
    assert result[0].shape == (17, 3)
    # SimCC centre must map back to the centre of the ORIGINAL image bbox.
    np.testing.assert_allclose(result[0][:, :2], np.tile([64, 80], (17, 1)))


@pytest.mark.parametrize("fps", [25, 30, 60])
def test_tracker_lost_identity_expires_after_one_video_second_independent_of_call_count(fps):
    tracker = PlayerTracker(fps)
    box, score = np.array([[20, 20, 80, 160]], float), np.array([0.95])
    assert tracker.update(box, score, 0) == []  # ByteTrack requires a second observation to admit a birth.
    first = tracker.update(box, score, 2)[0][0]
    short_gap = tracker.update(box, score, 6)[0][0]
    assert short_gap == first
    # Only a few detector calls, but more than one second since last observation.
    assert tracker.update(box, score, 6 + fps + 1) == []
    after_gap = tracker.update(box, score, 6 + fps + 3)[0][0]
    assert after_gap != first


def test_player_perception_passes_absolute_frames_across_changing_detector_cadence():
    seen = []
    players = PlayerPerception(lambda _: (np.empty((0, 4)), np.empty(0)), None, fps=30)
    players.tracker = SimpleNamespace(update=lambda boxes, scores, frame: seen.append(frame) or [])
    image = np.zeros((40, 40, 3), np.uint8)
    for frame, strides in ((60, (6, 0)), (61, (6, 0)), (66, (6, 0)), (68, (2, 0))):
        players.process(frame, image, strides)
    assert seen == [60, 66, 68]


@pytest.mark.parametrize("step", [4, 8])
def test_tracknet_temporal_windows_never_cross_a_camera_cut_and_cover_short_shots(step):
    model = TrackNetV3.__new__(TrackNetV3)
    model.seq_len, model.in_dim, model.batch, model.threshold = 8, 27, 2, 0.5
    model.bg = BackgroundModel()
    windows = []

    def forward(inputs):
        out = np.zeros((len(inputs), 8, HEIGHT, WIDTH), np.float32)
        for batch, tensor in enumerate(inputs):
            frames = tensor[3:].reshape(8, 3, HEIGHT, WIDTH)
            # All channels/pixels carry the shot marker. Padding must use this shot.
            markers = frames[:, 0, 0, 0]
            assert np.all(markers == markers[0])
            windows.append(float(markers[0]))
            x = round(float(markers[0]) * 255)
            out[batch, :, 40, x] = 0.9
        return out

    model._forward = forward
    shots = [0] * 3 + [1] * 14 + [2] + [3] * 10
    frames = [np.full((72, 128, 3), 20 + shot * 30, np.uint8) for shot in shots]
    detections = model.detect(frames, shots, step=step)
    assert len(detections) == len(frames)
    for shot, detection in zip(shots, detections, strict=True):
        assert detection is not None
        assert detection.x == pytest.approx((20 + shot * 30) / 4)
        assert detection.y == pytest.approx(10)
    assert len(set(round(value * 255) for value in windows)) == 4


def test_tracknet_rejects_camera_shot_metadata_of_the_wrong_length():
    model = TrackNetV3.__new__(TrackNetV3)
    with pytest.raises(ValueError, match="camera-shot"):
        model.detect([np.zeros((72, 128, 3), np.uint8)], shots=[0, 1])
