"""The experimental embedder must fail closed and not invent identities."""

import hashlib

import numpy as np
import pytest

from bai_badminton.perception import offline_reid


class FakeEmbedder:
    def __init__(self, *, variant, weights, device):
        self.last = None

    def __call__(self, image, boxes):
        self.last = (image.copy(), boxes.copy())
        value = np.zeros((len(boxes), 512), dtype=np.float32)
        value[:, :2] = [3.0, 4.0]
        return value


def make_reviewer(tmp_path, monkeypatch):
    path = tmp_path / "weights.pt"
    path.write_bytes(b"pinned test checkpoint")
    monkeypatch.setattr(offline_reid, "CHECKPOINT_SHA256", hashlib.sha256(path.read_bytes()).hexdigest())
    monkeypatch.setattr(offline_reid, "_vendor_embedder", lambda: FakeEmbedder)
    return offline_reid.OSNetReviewEmbedder(path, device="cpu", max_crops=4)


def test_corrupt_checkpoint_is_rejected_before_model_load(tmp_path, monkeypatch):
    path = tmp_path / "weights.pt"
    path.write_bytes(b"untrusted")
    monkeypatch.setattr(offline_reid, "_vendor_embedder", lambda: pytest.fail("must not load"))
    with pytest.raises(ValueError, match="checksum"):
        offline_reid.OSNetReviewEmbedder(path, device="cpu")


def test_rgb_preprocessing_and_normalized_embeddings(tmp_path, monkeypatch):
    model = make_reviewer(tmp_path, monkeypatch)
    bgr = np.zeros((20, 30, 3), dtype=np.uint8)
    bgr[..., 0] = 9
    features = model.embed(bgr, [[1, 2, 10, 15], [5, 2, 20, 18]])
    assert features.shape == (2, 512)
    assert np.linalg.norm(features, axis=1) == pytest.approx([1.0, 1.0])
    assert model._embedder.last[0][0, 0].tolist() == [0, 0, 9]


@pytest.mark.parametrize("boxes", [[[0, 0, 0, 2]], [[-1, 0, 5, 5]], [[0, 0, 5, 30]], [[0, 0, float("nan"), 5]]])
def test_invalid_crops_are_rejected(tmp_path, monkeypatch, boxes):
    model = make_reviewer(tmp_path, monkeypatch)
    with pytest.raises(ValueError):
        model.embed(np.zeros((20, 30, 3), dtype=np.uint8), boxes)


def test_crop_batch_is_bounded(tmp_path, monkeypatch):
    model = make_reviewer(tmp_path, monkeypatch)
    with pytest.raises(ValueError, match="limit"):
        model.embed(np.zeros((20, 30, 3), dtype=np.uint8), [[1, 1, 5, 5]] * 5)


def test_similarity_never_automatically_assigns_an_identity():
    result = offline_reid.compare_features(np.array([1.0, 0.0]), np.array([1.0, 0.0]))
    assert result["cosine_similarity"] == pytest.approx(1.0)
    assert result["identity_decision"] == "unresolved"
    assert result["calibrated_probability"] is None


@pytest.mark.parametrize("a,b", [([0.0, 0.0], [1.0, 1.0]), ([float("nan")], [1.0]), ([1.0], [1.0, 1.0])])
def test_invalid_features_cannot_produce_similarity(a, b):
    with pytest.raises(ValueError):
        offline_reid.compare_features(a, b)


def test_empty_and_oversized_frames_do_not_reach_the_model(tmp_path, monkeypatch):
    model = make_reviewer(tmp_path, monkeypatch)
    assert model.embed(np.zeros((4, 4, 3), dtype=np.uint8), []).shape == (0, 512)
    assert model._embedder.last is None
    with pytest.raises(ValueError, match="frame"):
        model.embed(np.zeros((3000, 3000, 3), dtype=np.uint8), [[1, 1, 10, 10]])
