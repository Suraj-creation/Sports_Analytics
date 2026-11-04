"""Camera-shot background history stays bounded without changing live-shot input."""

import numpy as np
import pytest

from bai_badminton.perception.tracknet import HEIGHT, WIDTH, BackgroundModel, TrackNetV3


def detector():
    model = TrackNetV3.__new__(TrackNetV3)
    model.seq_len, model.in_dim, model.batch, model.threshold = 8, 27, 2, 0.5
    model.bg = BackgroundModel(every=1, capacity=4, refresh=1)
    observed = []

    def forward(inputs):
        observed.extend(float(tensor[0, 0, 0]) * 255 for tensor in inputs)
        return np.zeros((len(inputs), 8, HEIGHT, WIDTH), np.float32)

    model._forward = forward
    return model, observed


def frame(value):
    return np.full((36, 64, 3), value, np.uint8)


@pytest.mark.parametrize("first_shot, count", [(0, 12), (10**12, 64)])
def test_completed_camera_shots_do_not_accumulate_background_images(first_shot, count) -> None:
    model, _ = detector()
    for offset in range(count):
        shot = first_shot + 17 * offset
        model.detect([frame(offset + 10)], shots=[shot])
        for history in (model.bg._samples, model.bg._median, model.bg._since, model.bg._count):
            assert set(history) <= {shot}, "Background state retained an unreachable completed camera shot"


def test_live_shot_history_and_cut_chunk_backgrounds_are_preserved() -> None:
    model, observed = detector()
    model.detect([frame(10), frame(20)], shots=[7, 7])
    assert observed[-1] == pytest.approx(15)
    model.detect([frame(30), frame(40)], shots=[7, 7])
    assert observed[-1] == pytest.approx(25)
    # Both shot backgrounds are needed until all windows in this call finish.
    model.detect([frame(50), frame(200)], shots=[7, 8])
    assert observed[-2:] == pytest.approx([35, 200])
    model.detect([frame(210)], shots=[8])
    assert observed[-1] == pytest.approx(205)


def test_first_shot_keeps_its_seeded_background() -> None:
    model, observed = detector()
    model.bg.seed(0, [np.full((HEIGHT, WIDTH, 3), 90, np.uint8)] * 3)
    model.detect([frame(10)], shots=[0])
    assert observed == pytest.approx([90])
