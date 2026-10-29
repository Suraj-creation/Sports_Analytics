"""Pretrained BST preprocessing and class-order regressions, without downloads."""

from dataclasses import replace

import numpy as np
import pytest
import torch

from bai_badminton.court import Homography
from bai_badminton.events.bst import (
    BONE_PAIRS,
    CLASS_LABELS,
    BSTClassifier,
    BSTFrame,
    BSTPlayer,
    contact_window,
    prepare_sequence,
)


def sample_frame(index=0):
    homography = Homography(np.array([[100.0, 0.0, 640.0], [0.0, -40.0, 400.0], [0.0, 0.0, 1.0]]), 0.0, 4)
    far = np.zeros((17, 3))
    far[:, :2] = np.array([650.0, 240.0])
    far[:, 2] = 0.8
    far[15, :2], far[16, :2] = [640.0, 280.0], [660.0, 280.0]
    far[7, :2], far[9, :2] = [660.0, 220.0], [680.0, 210.0]
    near = far.copy()
    near[:, 1] += 240.0
    return BSTFrame(
        index,
        [
            BSTPlayer(np.array([600.0, 360.0, 700.0, 560.0]), near),
            BSTPlayer(np.array([600.0, 100.0, 700.0, 300.0]), far),
        ],
        (320.0, 180.0),
        homography,
    )


def test_exact_coordinate_normalization_sort_bones_and_padding():
    frame = sample_frame()
    seq = prepare_sequence([frame], (1280, 720), match_format="singles")
    expected = (frame.players[1].keypoints[:, :2] - [650.0, 200.0]) / np.hypot(100.0, 200.0)
    np.testing.assert_allclose(seq.pose[0, 0, :34].reshape(17, 2), expected, atol=1e-7)
    # Court positions use projected ankles, never bbox feet or shuttle homography.
    np.testing.assert_allclose(seq.positions[0], [[3.15 / 6.1, 3.7 / 13.4], [3.15 / 6.1, 9.7 / 13.4]], atol=1e-7)
    np.testing.assert_allclose(seq.shuttle[0], [0.25, 0.25])
    a, b = BONE_PAIRS[8]
    expected_bone = np.where((expected[a] != 0) & (expected[b] != 0), expected[b] - expected[a], 0)
    np.testing.assert_allclose(seq.pose[0, 0, 34:].reshape(19, 2)[8], expected_bone, atol=1e-7)
    assert seq.video_len == 1 and seq.usable_frames == 1 and seq.source_frames == (0,)
    assert not seq.pose[1:].any() and not seq.positions[1:].any() and not seq.shuttle[1:].any()


@pytest.mark.parametrize(
    "count,expected_indices",
    [
        (99, tuple(range(99))),
        (100, tuple(range(100))),
        (101, tuple(range(100))),
        (150, tuple(range(100))),
        (151, tuple(range(0, 151, 2))),
        (201, tuple(range(0, 200, 2))),
    ],
)
def test_exact_official_temporal_sampling_not_uniform_interpolation(count, expected_indices):
    frames = [sample_frame(i) for i in range(count)]
    seq = prepare_sequence(frames, (1280, 720), match_format="singles")
    assert seq.source_frames == expected_indices
    assert seq.video_len == len(expected_indices)
    assert seq.pose.shape == (100, 2, 72)


def test_missing_and_reused_pose_frames_are_zeroed_in_all_modalities():
    good = sample_frame(0)
    missing = replace(sample_frame(1), players=[good.players[0]])
    reused = replace(sample_frame(2), players=[replace(good.players[0], observed=False), good.players[1]])
    uncalibrated = replace(sample_frame(3), homography=None)
    seq = prepare_sequence([good, missing, reused, uncalibrated], (1280, 720), match_format="singles")
    assert seq.usable_frames == 1 and seq.video_len == 4
    assert not seq.pose[1:].any() and not seq.positions[1:].any() and not seq.shuttle[1:].any()


def test_low_confidence_missing_joint_uses_official_centered_sentinel():
    frame = sample_frame()
    frame.players[1].keypoints[0, 2] = 0
    seq = prepare_sequence([frame], (1280, 720), match_format="singles")
    np.testing.assert_allclose(seq.pose[0, 0, :2], -np.array([50.0, 100.0]) / np.hypot(100.0, 200.0))


def test_invalid_ankle_prevents_invented_court_position():
    frame = sample_frame()
    frame.players[1].keypoints[15, 2] = 0
    with pytest.raises(ValueError, match="no observed two-player"):
        prepare_sequence([frame], (1280, 720), match_format="singles")


@pytest.mark.parametrize(
    "frames,match_format,error",
    [
        ([sample_frame()], "doubles", "singles only"),
        ([sample_frame(2), sample_frame(4)], "singles", "contiguous"),
        ([sample_frame(2), sample_frame(1)], "singles", "contiguous"),
        ([sample_frame(2), replace(sample_frame(3), shot_id=1)], "singles", "camera shots"),
    ],
)
def test_unsupported_context_rejected(frames, match_format, error):
    with pytest.raises(ValueError, match=error):
        prepare_sequence(frames, (1280, 720), match_format=match_format)


def test_training_contact_bounds_do_not_expand_past_next_context_limit():
    assert contact_window(100, 30, 90, 110) == (90, 117)
    assert contact_window(100, 30, 5, 250) == (55, 152)
    assert contact_window(100, 30, None, None) == (85, 115)
    assert contact_window(10, 30, None, None) == (0, 25)
    with pytest.raises(ValueError, match="chronological"):
        contact_window(100, 30, 101, None)


def test_exact_25_class_mapping_retains_side_uncertainty():
    classifier = BSTClassifier.__new__(BSTClassifier)
    classifier.device = torch.device("cpu")
    raw = np.full(25, 0.1 / 22)
    raw[0], raw[3], raw[15] = 0.1, 0.5, 0.3  # unknown, Top_smash, Bottom_smash

    class FixedLogits:
        def __call__(self, *args):
            return torch.tensor(np.log(raw)[None], dtype=torch.float32)

    classifier.model = FixedLogits()
    sequence = prepare_sequence([sample_frame()], (1280, 720), match_format="singles")
    result = classifier.predict_sequence(sequence)
    assert result.prediction.top[0] == "smash"
    assert result.prediction.probs["smash"] == pytest.approx(0.8)
    assert result.prediction.probs["unknown"] == pytest.approx(0.1)
    assert result.side_probabilities["far"] == pytest.approx(0.55)
    assert result.side_probabilities["near"] == pytest.approx(0.35)
    assert sum(result.prediction.probs.values()) == pytest.approx(1)
    assert CLASS_LABELS[3] == "Top_殺球" and CLASS_LABELS[15] == "Bottom_殺球"
    assert CLASS_LABELS[11] == "Top_發短球" and CLASS_LABELS[24] == "Bottom_發長球"


def test_wrong_checkpoint_cannot_silently_initialize_random_weights(tmp_path):
    checkpoint = tmp_path / "wrong.pt"
    checkpoint.write_bytes(b"wrong")
    with pytest.raises(ValueError, match="digest"):
        BSTClassifier(checkpoint)
