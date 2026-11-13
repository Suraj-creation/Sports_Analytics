"""Same selected points and LK statistics with bounded grouped execution."""

import time

import cv2
import numpy as np
import pytest

from bai_badminton.perception import scene_change as scene


@pytest.fixture(autouse=True)
def bounded_cv_threads():
    previous = cv2.getNumThreads()
    cv2.setNumThreads(1)
    yield
    cv2.setNumThreads(previous)


def masks(shape):
    height, width = shape
    result = [np.full(shape, 255, np.uint8)]
    for x0, y0, x1, y1 in ((0, 0, width // 2, height), (width // 3, 10, width, height - 10),
                           (0, 0, 20, 20), (width - 20, height - 20, width, height)):
        mask = np.zeros(shape, np.uint8)
        mask[y0:y1, x0:x1] = 255
        result.append(mask)
    result.append(np.zeros(shape, np.uint8))
    return result


def pair(kind, seed):
    previous = np.random.default_rng(seed).integers(0, 256, (120, 160), dtype=np.uint8)
    if kind == "identical":
        current = previous.copy()
    elif kind == "translated":
        current = cv2.warpAffine(previous, np.array([[1, 0, 1.25], [0, 1, -0.75]], float), (160, 120))
    elif kind == "illumination":
        current = np.clip(previous.astype(float) * 0.9 + 12, 0, 255).astype(np.uint8)
    elif kind == "noise":
        current = np.random.default_rng(seed + 77).integers(0, 256, previous.shape, dtype=np.uint8)
    else:
        previous[:] = 0
        current = previous.copy()
    return previous, current


def assert_stats_equal(actual, expected):
    assert len(actual) == len(expected)
    for got, reference in zip(actual, expected, strict=True):
        assert got[0] == reference[0]
        for a, b in zip(got[1:], reference[1:], strict=True):
            if b is None:
                assert a is None
            else:
                assert a == pytest.approx(b, rel=0, abs=1e-7)


@pytest.mark.parametrize("kind", ["identical", "translated", "illumination", "noise", "blank"])
@pytest.mark.parametrize("seed", [1, 7, 41])
def test_grouped_point_execution_matches_unchanged_single_mask_reference(kind, seed):
    previous, current = pair(kind, seed)
    regions = masks(previous.shape)
    before = [previous.copy(), current.copy(), *[mask.copy() for mask in regions]]
    expected = [scene._flow(previous, current, mask) for mask in regions]
    actual = scene._flow_groups(previous, current, regions)
    assert_stats_equal(actual, expected)
    for original, retained in zip([previous, current, *regions], before, strict=True):
        np.testing.assert_array_equal(original, retained)


def test_features_are_selected_independently_and_only_two_lk_calls_execute(monkeypatch):
    previous, current = pair("translated", 3)
    regions = masks(previous.shape)
    expected_points = [cv2.goodFeaturesToTrack(previous, 80, 0.01, 3, mask=mask) for mask in regions]
    original_features, original_lk = cv2.goodFeaturesToTrack, cv2.calcOpticalFlowPyrLK
    selection_masks, calls = [], []

    def features(*args, **kwargs):
        selection_masks.append(kwargs["mask"].copy())
        return original_features(*args, **kwargs)

    def lk(a, b, points, *args, **kwargs):
        calls.append(points.copy())
        return original_lk(a, b, points, *args, **kwargs)

    monkeypatch.setattr(cv2, "goodFeaturesToTrack", features)
    monkeypatch.setattr(cv2, "calcOpticalFlowPyrLK", lk)
    scene._flow_groups(previous, current, regions)
    assert len(calls) == 2 and len(selection_masks) == len(regions)
    np.testing.assert_array_equal(calls[0], np.concatenate([p for p in expected_points if p is not None]))
    for selected, original in zip(selection_masks, regions, strict=True):
        np.testing.assert_array_equal(selected, original)


@pytest.mark.parametrize("failed_call", [1, 2])
def test_missing_group_outputs_fall_back_to_independent_reference(monkeypatch, failed_call):
    previous, current = pair("translated", 5)
    regions = masks(previous.shape)
    expected = [scene._flow(previous, current, mask) for mask in regions]
    original, calls = cv2.calcOpticalFlowPyrLK, []

    def lk(*args, **kwargs):
        calls.append(True)
        if len(calls) == failed_call:
            return None, None, None
        return original(*args, **kwargs)

    monkeypatch.setattr(cv2, "calcOpticalFlowPyrLK", lk)
    assert_stats_equal(scene._flow_groups(previous, current, regions), expected)
    assert len(calls) > 2


def test_empty_feature_groups_do_not_execute_lk(monkeypatch):
    image = np.zeros((120, 160), np.uint8)
    monkeypatch.setattr(cv2, "calcOpticalFlowPyrLK", lambda *_args, **_kwargs: pytest.fail("no points need LK"))
    assert scene._flow_groups(image, image, masks(image.shape)) == [(0, None, None, None)] * 6
    assert scene._flow_groups(image, image, []) == []


def test_controlled_wall_measurement_emits_both_reference_and_grouped_samples(record_property):
    """Diagnostic synthetic timings only; never assert a noisy speed threshold."""
    previous, current = pair("translated", 9)
    regions = masks(previous.shape)
    samples = {}
    for name, execute in (
        ("reference", lambda: [scene._flow(previous, current, mask) for mask in regions]),
        ("grouped", lambda: scene._flow_groups(previous, current, regions)),
    ):
        execute()
        durations = []
        for _ in range(5):
            started = time.perf_counter()
            execute()
            durations.append((time.perf_counter() - started) * 1000)
        samples[name] = durations
        record_property(f"synthetic_{name}_wall_ms", durations)
    assert set(samples) == {"reference", "grouped"}
