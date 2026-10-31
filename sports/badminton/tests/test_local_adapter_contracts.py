"""Model-boundary regressions with explicit controlled adapters, no weights."""

from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.perception.pipeline import BadmintonPerception
from bai_badminton.perception.players import PlayerDetector, PoseEstimator
from bai_badminton.perception.tracknet import heatmap_to_point
from bai_engine.config import ModelChoice


def test_person_adapter_converts_bgr_once_and_decodes_original_coordinates():
    seen = []
    detector = PlayerDetector.__new__(PlayerDetector)
    detector.kind = "rfdetr"

    def preprocess(image):
        seen.append(image.copy())
        return image, image.shape[:2]

    detector.tool = SimpleNamespace(
        preprocess=preprocess,
        inference=lambda _: [
            np.array([[[0.5, 0.5, 0.5, 0.5]]]),
            np.array([[[-20.0, 20.0, -20.0]]]),
        ],
        score_thr=0.35,
    )
    image = np.full((80, 160, 3), [5, 25, 200], np.uint8)
    boxes, scores = detector(image)
    np.testing.assert_array_equal(seen[0][0, 0], [200, 25, 5])
    np.testing.assert_array_equal(image[0, 0], [5, 25, 200])
    np.testing.assert_allclose(boxes, [[40, 20, 120, 60]])
    assert scores[0] > 0.99


def test_pose_adapter_converts_bgr_once_and_preserves_scores():
    seen = []
    estimator = PoseEstimator.__new__(PoseEstimator)

    def pose(image, *, bboxes):
        seen.append((image.copy(), bboxes))
        return np.ones((1, 17, 2)) * 12, np.ones((1, 17)) * 0.8

    estimator.tool = pose
    image = np.full((80, 160, 3), [5, 25, 200], np.uint8)
    result = estimator(image, [np.array([10, 20, 50, 70])])
    np.testing.assert_array_equal(seen[0][0][0, 0], [200, 25, 5])
    assert seen[0][1] == [[10, 20, 50, 70]]
    assert result[0].shape == (17, 3)
    np.testing.assert_allclose(result[0][:, 2], 0.8)


@pytest.mark.parametrize("stage", ["shuttle", "detector", "pose", "reid"])
def test_disabled_backend_never_resolves_weights_or_degrades(stage, tmp_path):
    perception = BadmintonPerception.__new__(BadmintonPerception)
    perception.models, perception.degraded = {}, []

    def forbidden(*args, **kwargs):
        raise AssertionError("disabled inference stage accessed the model registry")

    registry = SimpleNamespace(path=forbidden, get=forbidden)
    choice = ModelChoice(model="configured-but-disabled", backend="none")
    loader = getattr(perception, f"_load_{stage}")
    result = loader(choice, registry) if stage == "reid" else loader(choice, registry, tmp_path)
    assert result is None
    assert perception.degraded == [] and perception.models == {}


def controlled_detector(boxes, logits):
    detector = PlayerDetector.__new__(PlayerDetector)
    detector.kind = "rfdetr"
    detector.tool = SimpleNamespace(
        preprocess=lambda image: (image, image.shape[:2]),
        inference=lambda _: [np.asarray(boxes), np.asarray(logits)],
        score_thr=0.35,
    )
    return detector


def test_detector_drops_nonfinite_and_degenerate_boxes_and_clips_image_edges():
    detector = controlled_detector(
        [[[0.0, 0.5, 0.5, 0.5], [np.nan, 0.5, 0.2, 0.2], [0.5, 0.5, -0.2, 0.2], [0.5, 0.5, 0.2, 0.2]]],
        [[[-20.0, 20.0], [-20.0, 20.0], [-20.0, 20.0], [-20.0, np.nan]]],
    )
    boxes, scores = detector(np.zeros((80, 160, 3), np.uint8))
    np.testing.assert_allclose(boxes, [[0, 20, 40, 60]])
    assert len(scores) == 1 and np.isfinite(scores).all()


def test_detector_reports_output_shape_mismatch_at_the_adapter():
    detector = controlled_detector(np.zeros((1, 3, 4)), np.zeros((1, 2, 3)))
    with pytest.raises(ValueError, match=r"RF-DETR.*shape"):
        detector(np.zeros((80, 160, 3), np.uint8))


@pytest.mark.parametrize("bad", [np.nan, np.inf, -np.inf])
def test_nonfinite_heatmap_is_rejected_without_fabricating_a_point(bad):
    heatmap = np.zeros((4, 4), np.float32)
    heatmap[1, 1] = bad
    with pytest.raises(ValueError, match=r"heatmap.*finite"):
        heatmap_to_point(heatmap, 0.5)


def test_zero_heatmap_with_zero_threshold_still_has_no_detection():
    assert heatmap_to_point(np.zeros((4, 4), np.float32), 0.0) is None


def test_disabled_player_detection_does_not_import_optional_tracker(monkeypatch):
    import sys

    from bai_badminton.perception.players import PlayerPerception

    monkeypatch.setitem(sys.modules, "trackers", None)
    players = PlayerPerception(None, None, fps=30)
    assert players.process(0, np.zeros((10, 10, 3), np.uint8)) == []
    players.on_cut()


@pytest.mark.parametrize("raw", [False, True])
def test_yolox_preserves_real_confidence_and_original_coordinates(raw):
    class ControlledYOLOX:
        score_thr, nms_thr, model_input_size = 0.35, 0.45, (32, 32)

        def __call__(self, _):
            return np.array([[24, 24, 40, 40]], float)

        def preprocess(self, image):
            return image, 0.5

        def inference(self, _):
            if not raw:
                return [np.array([[[12, 12, 20, 20, 0.6], [1, 1, 2, 2, 0.2]]])]
            output = np.zeros((1, 21, 6), float)
            # First stride-8 cell: centre=(2,2)*8, size=exp(0)*8.
            output[0, 0] = [2, 2, 0, 0, 0.8, 0.75]
            return [output]

    detector = PlayerDetector.__new__(PlayerDetector)
    detector.kind, detector.tool = "yolox", ControlledYOLOX()
    boxes, scores = detector(np.zeros((64, 64, 3), np.uint8))
    np.testing.assert_allclose(boxes, [[24, 24, 40, 40]])
    np.testing.assert_allclose(scores, [0.6])
