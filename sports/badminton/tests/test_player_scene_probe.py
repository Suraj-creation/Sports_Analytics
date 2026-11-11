"""Current detector acquisition is independent of tracking and cadence."""

import numpy as np
import pytest

from bai_badminton.perception.players import PlayerPerception


class Detector:
    def __init__(self, count):
        self.count, self.calls = count, 0

    def __call__(self, image):
        self.calls += 1
        return np.asarray([[10 + i * 30, 10, 30 + i * 30, 60] for i in range(self.count)], float), np.full(
            self.count, 0.95
        )


class Tracker:
    def __init__(self):
        self.updates, self.resets = [], 0

    def update(self, boxes, scores, frame):
        self.updates.append(frame)
        return [(i, box, score) for i, (box, score) in enumerate(zip(boxes, scores, strict=True))]

    def reset(self):
        self.resets += 1


def perception(count):
    p = PlayerPerception(None, None, 30, det_stride=2, max_players=count)
    p.detector, p.tracker = Detector(count), Tracker()
    return p


@pytest.mark.parametrize("count", [2, 4])
def test_odd_source_cut_forces_one_fresh_detection_even_between_scheduled_ticks(count):
    p = perception(count)
    image = np.zeros((100, 180, 3), np.uint8)
    p.process(0, image)
    p.on_cut()
    people = p.process(1, image)
    assert len(people) == count
    assert p.detector.calls == 2
    assert p.tracker.updates == [0, 1]
    assert p.last_detector_observed
    assert all(person.detector_matched is True for person in people)


@pytest.mark.parametrize("count", [2, 4])
def test_probe_does_not_advance_or_reset_tracking_and_is_reused_once(count):
    p = perception(count)
    image = np.zeros((100, 180, 3), np.uint8)
    probe = p.probe_detection(1, image)
    assert p.detector.calls == 1
    assert p.tracker.updates == [] and p.tracker.resets == 0
    assert p._last == [] and p._last_detection_frame is None
    assert not p.last_detector_observed
    assert probe.frame_idx == 1 and probe.image_shape == image.shape
    people = p.process(1, image, detection_probe=probe)
    assert len(people) == count and p.detector.calls == 1
    assert p.tracker.updates == [1] and p.last_detector_observed
    with pytest.raises(ValueError, match="already consumed"):
        p.process(1, image, detection_probe=probe)
    assert p.detector.calls == 1 and p.tracker.updates == [1]


@pytest.mark.parametrize("wrong", ["frame", "pixels", "shape"])
def test_probe_cannot_be_reused_for_another_source_image(wrong):
    p = perception(2)
    image = np.zeros((100, 180, 3), np.uint8)
    probe = p.probe_detection(1, image)
    frame = 2 if wrong == "frame" else 1
    current = np.ones_like(image) if wrong == "pixels" else image[:90] if wrong == "shape" else image
    with pytest.raises(ValueError, match="source frame/image"):
        p.process(frame, current, detection_probe=probe)
    assert p.tracker.updates == [] and p.detector.calls == 1


def test_explicitly_disabled_detector_remains_disabled_after_cut():
    p = perception(2)
    p.on_cut()
    assert p.process(1, np.zeros((100, 180, 3), np.uint8), (0, 0)) == []
    assert p.detector.calls == 0 and p.tracker.updates == []
