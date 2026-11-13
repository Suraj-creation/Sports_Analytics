"""Geometry proof memoization never caches measurements or mutable masks."""

from dataclasses import FrozenInstanceError, replace
from hashlib import sha256
from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.perception import scene_change as scene


@pytest.fixture(autouse=True)
def isolated_records():
    scene._expected_origin_records.cache_clear()
    yield
    scene._expected_origin_records.cache_clear()


def regions(boxes, *, keys=None):
    return [scene.ForegroundRegion(3, keys[i] if keys else str(i), tuple(box), True, True)
            for i, box in enumerate(boxes)]


def evidence(items):
    return [scene.RegionContinuity(item, 0, None, None, None, None, None, None) for item in items]


def legacy_reference(items, source, analysis):
    """Frozen original raster arithmetic, independent of refactored helpers."""
    width, height = analysis
    scale = width / source[0]
    masks = []
    for item in items:
        x0, y0, x1, y1 = np.asarray(item.bbox) * scale
        x0, x1 = np.clip([int(x0), int(np.ceil(x1))], 0, width)
        y0, y1 = np.clip([int(y0), int(np.ceil(y1))], 0, height)
        mask = np.zeros((height, width), np.uint8)
        mask[y0:y1, x0:x1] = 255
        masks.append(mask)
    if not masks:
        return (), ()
    occupancy = np.sum([mask > 0 for mask in masks], axis=0)
    exclusive = tuple(np.where((mask > 0) & (occupancy == 1), 255, 0).astype(np.uint8) for mask in masks)
    records = tuple(scene.FeatureOriginMask(item.key, int(np.count_nonzero(mask)), sha256(mask.tobytes()).hexdigest())
                    for item, mask in zip(items, exclusive, strict=True))
    return exclusive, records


@pytest.mark.parametrize("boxes", [[], [(1.1, 2.2, 70.3, 90.4)],
                                      [(-20.1, -5.1, 150.8, 160.4), (90.2, 80.8, 300.1, 280.9)]])
@pytest.mark.parametrize("source,analysis", [((640, 480), (320, 240)), ((1943, 1080), (1189, 661))])
def test_measurement_and_cached_records_preserve_original_raster_bytes(boxes, source, analysis):
    items = regions(boxes)
    masks, records = scene.exclusive_feature_origin_masks(items, source, analysis)
    expected_masks, expected = legacy_reference(items, source, analysis)
    for actual, reference in zip(masks, expected_masks, strict=True):
        np.testing.assert_array_equal(actual, reference)
    assert records == expected
    for _ in range(2):
        scene.validate_feature_origin_basis(evidence(items), scene.FEATURE_ORIGIN_POLICY, source, analysis, records)
    assert scene._expected_origin_records.cache_info().hits == 1


@pytest.mark.parametrize("damage", ["digest", "pixels", "key", "order"])
def test_cache_hits_never_authorize_forged_proof_records(damage):
    items = regions([(1, 2, 100, 150), (70, 20, 130, 160)])
    _, records = scene.exclusive_feature_origin_masks(items, (640, 480), (320, 240))
    scene.validate_feature_origin_basis(evidence(items), scene.FEATURE_ORIGIN_POLICY, (640, 480), (320, 240), records)
    bad = list(records)
    if damage == "digest":
        bad[0] = replace(bad[0], sha256="0" * 64)
    elif damage == "pixels":
        bad[0] = replace(bad[0], pixels=bad[0].pixels + 1)
    elif damage == "key":
        bad[0] = replace(bad[0], key="wrong")
    else:
        bad.reverse()
    with pytest.raises(ValueError, match="disagree"):
        scene.validate_feature_origin_basis(evidence(items), scene.FEATURE_ORIGIN_POLICY, (640, 480), (320, 240), bad)
    assert scene._expected_origin_records.cache_info().hits == 1


def test_every_geometry_dependency_participates_in_cache_key():
    boxes = [(1, 2, 100, 150), (70, 20, 130, 160)]
    cases = [(regions(boxes), (640, 480), (320, 240)),
             (regions([(2, 2, 100, 150), boxes[1]]), (640, 480), (320, 240)),
             (regions(boxes, keys=("other", "1")), (640, 480), (320, 240)),
             (list(reversed(regions(boxes))), (640, 480), (320, 240)),
             (regions(boxes), (1280, 960), (320, 240)),
             (regions(boxes), (640, 480), (480, 360))]
    for items, source, analysis in cases:
        _, records = scene.exclusive_feature_origin_masks(items, source, analysis)
        scene.validate_feature_origin_basis(evidence(items), scene.FEATURE_ORIGIN_POLICY, source, analysis, records)
    info = scene._expected_origin_records.cache_info()
    assert info.misses == len(cases) and info.hits == 0


@pytest.mark.parametrize("source,analysis", [((True, 480), (320, 240)), ((640, 480), (320, 241)),
                                            ((640, 480), (1281, 961)), ((640, 480), (0, 0))])
def test_invalid_dimensions_fail_before_cache_lookup(source, analysis):
    with pytest.raises(ValueError):
        scene.validate_feature_origin_basis([], scene.FEATURE_ORIGIN_POLICY, source, analysis, [])
    assert scene._expected_origin_records.cache_info().misses == 0


@pytest.mark.parametrize("box", [(np.nan, 0, 10, 20), (1, 2, 1, 20), (True, 2, 10, 20)])
def test_invalid_geometry_cannot_enter_hashable_cache(box):
    item = SimpleNamespace(key="0", bbox=box)
    with pytest.raises(ValueError, match="geometry requires"):
        scene.validate_feature_origin_basis(evidence([item]), scene.FEATURE_ORIGIN_POLICY,
                                            (640, 480), (320, 240), [])
    assert scene._expected_origin_records.cache_info().misses == 0


def test_cache_is_bounded_and_recomputes_evicted_geometry():
    retained = None
    for i in range(129):
        items = regions([(float(i), 2, float(i + 20), 30)])
        _, records = scene.exclusive_feature_origin_masks(items, (640, 480), (320, 240))
        scene.validate_feature_origin_basis(
            evidence(items), scene.FEATURE_ORIGIN_POLICY, (640, 480), (320, 240), records
        )
        if i == 0:
            retained = items, records
    info = scene._expected_origin_records.cache_info()
    assert info.maxsize == 128 and info.currsize == 128
    items, records = retained
    scene.validate_feature_origin_basis(evidence(items), scene.FEATURE_ORIGIN_POLICY, (640, 480), (320, 240), records)
    assert scene._expected_origin_records.cache_info().misses == 130


def test_measurement_masks_are_fresh_and_cannot_mutate_cached_records():
    items = regions([(1, 2, 100, 150)])
    masks, records = scene.exclusive_feature_origin_masks(items, (640, 480), (320, 240))
    scene.validate_feature_origin_basis(evidence(items), scene.FEATURE_ORIGIN_POLICY, (640, 480), (320, 240), records)
    masks[0][:] = 0
    again, new_records = scene.exclusive_feature_origin_masks(items, (640, 480), (320, 240))
    assert again[0].any() and new_records == records
    with pytest.raises(FrozenInstanceError):
        records[0].pixels = 1
    scene.validate_feature_origin_basis(evidence(items), scene.FEATURE_ORIGIN_POLICY, (640, 480), (320, 240), records)
