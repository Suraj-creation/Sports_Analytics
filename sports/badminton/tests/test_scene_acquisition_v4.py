"""Relative acquisition is distinct from strong scene or sporting authority."""

from dataclasses import asdict, replace

import numpy as np
import pytest

from bai_badminton.perception import scene_change as scene
from bai_badminton.perception.content import (
    ContentContinuityProviderV2,
    scene_change_from_dict,
    scene_change_to_dict,
    scene_decision_from_dict,
    scene_decision_to_dict,
    validate_scene_decision_binding,
)
from bai_badminton.perception.players import PlayerDetectionProbe, strict_court_indices

POLYGON = ((0.0, 0.0), (1000.0, 0.0), (1000.0, 220.0), (0.0, 220.0))


def raw_relative(count=2, changed=None):
    changed = count if changed is None else changed
    regions = tuple(
        scene.RegionContinuity(
            scene.ForegroundRegion(11, f"image:{i}", (20.0 + i * 60, 20.0, 50.0 + i * 60, 100.0), True, True),
            20,
            0.1,
            6.0 if i < changed else 1.0,
            0.1,
            4.0 if i < changed else 0.1,
            1.0,
            4.0 if i < changed else 0.1,
            1.0,
            6.0 if i < changed else 1.0,
        )
        for i in range(count)
    )
    keys = tuple(f"image:{i}" for i in range(changed))
    return scene_change_from_dict(
        asdict(
            scene.SceneChangeEvidence(
                12,
                11,
                "measured",
                False,
                ("controlled_relative_below_strong_floor",),
                regions=regions,
                background_features=80,
                background_consistent_fraction=1.0,
                background_patch_error=1.0,
                version=scene.SCENE_CONTINUITY_VERSION_V4,
                witness_parameters=(3.0, 15.0),
                acquisition_region_keys=keys,
                relative_region_keys=keys if changed >= 2 else (),
            )
        )
    )


def probe_for(raw, count=None, boxes=None, polygon=POLYGON):
    count = len(raw.regions) if count is None else count
    boxes = tuple((400.0 + i * 100, 20.0, 430.0 + i * 100, 100.0) for i in range(count)) if boxes is None else boxes
    return PlayerDetectionProbe(
        12,
        (240, 1280, 3),
        "0" * 64,
        boxes,
        (0.95,) * len(boxes),
        (0, 0, 1280, 240),
        (),
        polygon,
        strict_court_indices(boxes, polygon),
    )


def decide(
    raw,
    probe,
    expected=2,
    geometry=True,
    transform=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
    previous_camera=(1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
):
    return ContentContinuityProviderV2(mode="barrier_detector_layout_v2").layout_decision(
        raw,
        probe,
        detector_model="controlled-detector@1",
        geometry_valid=geometry,
        expected_participants=expected,
        previous_to_current=transform,
        previous_camera=previous_camera,
    )


@pytest.mark.parametrize("count", [2, 4])
def test_relative_only_requires_complete_confirmed_format_court_replacement(count):
    raw = raw_relative(count, changed=2)
    p = probe_for(raw)
    assert not raw.hypothesis and raw.relative_region_keys == ("image:0", "image:1")
    d = decide(raw, p, count)
    assert d.version == "detector-layout-scene-decision:v3" and d.decision == "barrier"
    assert d.raw_hypothesis is False and d.admitted_indices == ()
    assert d.expected_participants == count and d.geometry_valid is True
    assert d.court_indices == tuple(range(count))
    assert scene_decision_from_dict(scene_decision_to_dict(d)) == d
    assert scene_change_from_dict(scene_change_to_dict(raw)) == raw
    validate_scene_decision_binding(d, raw)
    assert ContentContinuityProviderV2(mode="barrier_detector_layout_v2").tracking_barrier_for_decision(d)


@pytest.mark.parametrize("expected", [None, 4])
def test_unknown_format_or_partial_doubles_cannot_force_weak_barrier(expected):
    raw = raw_relative()
    d = decide(raw, probe_for(raw), expected)
    assert d.decision == "unknown"
    assert not ContentContinuityProviderV2(mode="barrier_detector_layout_v2").tracking_barrier_for_decision(d)
    validate_scene_decision_binding(d, raw)


@pytest.mark.parametrize(
    "case",
    [
        "one_relative",
        "few_prior",
        "missing_probe",
        "no_polygon",
        "geometry_false",
        "more_court",
        "fewer_court",
        "duplicate_current",
        "prior_overlap",
        "nonwitness_prior_overlap",
    ],
)
def test_weak_path_abstains_on_incomplete_or_positive_continuity_evidence(case):
    raw = raw_relative(3 if case == "nonwitness_prior_overlap" else 2, changed=1 if case == "one_relative" else 2)
    p = probe_for(raw, 2)
    expected = 2
    geometry = True
    if case == "few_prior":
        expected = 4
        p = probe_for(raw, 4)
    if case == "missing_probe":
        p = None
    if case == "no_polygon":
        p = probe_for(raw, polygon=())
    if case == "geometry_false":
        geometry = False
    if case == "more_court":
        p = probe_for(raw, 3)
    if case == "fewer_court":
        p = probe_for(raw, 1)
    if case == "duplicate_current":
        p = probe_for(raw, boxes=((400.0, 20.0, 430.0, 100.0),) * 2)
    if case == "prior_overlap":
        p = probe_for(raw, boxes=(raw.regions[0].region.bbox, (500.0, 20.0, 530.0, 100.0)))
    if case == "nonwitness_prior_overlap":
        p = probe_for(raw, boxes=(raw.regions[2].region.bbox, (500.0, 20.0, 530.0, 100.0)))
    d = decide(raw, p, expected, geometry)
    assert d.decision == "unknown"
    assert not ContentContinuityProviderV2(mode="barrier_detector_layout_v2").tracking_barrier_for_decision(d)
    validate_scene_decision_binding(d, raw)


def test_outside_bystander_is_retained_but_cannot_change_strict_court_count():
    raw = raw_relative()
    p = probe_for(raw, boxes=((400.0, 20.0, 430.0, 100.0), (500.0, 20.0, 530.0, 100.0), (1100.0, 20.0, 1130.0, 100.0)))
    d = decide(raw, p)
    assert d.decision == "barrier" and len(d.detector_boxes) == 3 and d.court_indices == (0, 1)
    validate_scene_decision_binding(d, raw)


@pytest.mark.parametrize(
    "case",
    [
        "keys",
        "single_quorum",
        "split_channels",
        "missing_history",
        "missing_ratio",
        "missing_appearance_history",
        "ratio_arithmetic",
        "background",
        "features",
        "overlap",
    ],
)
def test_raw_relative_cohorts_cannot_be_forged(case):
    v = asdict(raw_relative())
    if case == "keys":
        v["relative_region_keys"] = ("image:0", "invented")
    if case == "single_quorum":
        v["relative_region_keys"] = ("image:0",)
    if case == "split_channels":
        v["regions"][0]["appearance_adaptive_ratio"] = 1.0
        v["regions"][0]["median_patch_error"] = 1.0
        v["regions"][1]["adaptive_ratio"] = 0.1
        v["regions"][1]["discontinuity"] = 0.1
    if case == "missing_history":
        v["regions"][0]["previous_mean"] = None
    if case == "missing_ratio":
        v["regions"][0]["adaptive_ratio"] = None
    if case == "missing_appearance_history":
        v["regions"][0]["appearance_previous_mean"] = None
    if case == "ratio_arithmetic":
        v["regions"][0]["adaptive_ratio"] = 4.1
    if case == "background":
        v["background_features"] = 0
    if case == "features":
        v["regions"][0]["features"] = 0
    if case == "overlap":
        v["regions"][1]["region"]["bbox"] = v["regions"][0]["region"]["bbox"]
    with pytest.raises(ValueError):
        scene_change_from_dict(v)


@pytest.mark.parametrize(
    "case",
    [
        "court_index",
        "bool_index",
        "polygon",
        "geometry",
        "format",
        "keys",
        "prior_box",
        "decision_version",
        "raw_version",
    ],
)
def test_binding_and_codec_reject_forged_weak_proofs(case):
    raw = raw_relative()
    d = decide(raw, probe_for(raw))
    v = asdict(d)
    if case == "court_index":
        v["court_indices"] = (0,)
    if case == "bool_index":
        v["court_indices"] = (False, 1)
    if case == "polygon":
        v["court_polygon"] = ((0.0, 0.0), (1000.0, 220.0), (1000.0, 0.0), (0.0, 220.0))
    if case == "geometry":
        v["geometry_valid"] = False
    if case == "format":
        v["expected_participants"] = 4
    if case == "keys":
        v["relative_region_keys"] = ("image:0",)
    if case == "prior_box":
        raw = replace(
            raw,
            regions=(
                replace(raw.regions[0], region=replace(raw.regions[0].region, bbox=d.detector_boxes[0])),
                raw.regions[1],
            ),
        )
    if case == "decision_version":
        v["version"] = "detector-layout-scene-decision:v2"
    if case == "raw_version":
        raw = replace(raw, version=scene.SCENE_CONTINUITY_VERSION_V3)
    with pytest.raises(ValueError):
        validate_scene_decision_binding(scene_decision_from_dict(v), raw)


def test_actual_observer_acquires_relative_change_without_lowering_strong_floor(monkeypatch):
    calls = 0

    def flow(*_args):
        nonlocal calls
        pair, region = divmod(calls, 3)
        calls += 1
        return (80, 1.0, 1.0, 0.0) if region == 0 else (40, 0.0 if pair == 2 else 0.95, 6.0 if pair == 2 else 1.0, 0.1)

    monkeypatch.setattr(scene, "_flow", flow)
    observer = scene.SceneContinuityDetectorV4()
    image = np.random.default_rng(44).integers(20, 220, (240, 600, 3), dtype=np.uint8)
    for f in range(4):
        previous = (
            tuple(
                scene.ForegroundRegion(f - 1, f"image:{i}", (20.0 + i * 60, 20.0, 50.0 + i * 60, 100.0), True, True)
                for i in range(2)
            )
            if f
            else ()
        )
        raw = observer.observe(f, image, previous_regions=previous, previous_view_valid=True, current_view_valid=True)
    assert raw.version == scene.SCENE_CONTINUITY_VERSION_V4
    assert raw.acquisition_region_keys == raw.relative_region_keys == ("image:0", "image:1")
    assert not raw.hypothesis and raw.supporting_region_keys == () and not raw.authoritative
    assert scene_change_from_dict(asdict(raw)) == raw
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    assert isinstance(provider._observer, scene.SceneContinuityDetectorV4) and provider.supports_relative_layout


@pytest.mark.parametrize("shift,scale", [(380.0, 1.0), (360.0, 2.0)])
def test_pan_or_zoom_explaining_current_layout_cannot_be_weak_edit(shift, scale):
    raw = raw_relative()
    transform = (scale, 0.0, shift, 0.0, scale, 0.0, 0.0, 0.0, 1.0)
    boxes = tuple(
        tuple(v for v in (b[0] * scale + shift, b[1] * scale, b[2] * scale + shift, b[3] * scale))
        for b in (r.region.bbox for r in raw.regions)
    )
    d = decide(raw, probe_for(raw, boxes=boxes), transform=transform)
    assert d.decision == "unknown"
    validate_scene_decision_binding(d, raw)


def test_missing_camera_alignment_cannot_prove_weak_edit():
    raw = raw_relative()
    d = decide(raw, probe_for(raw), transform=None)
    assert d.decision == "unknown"
    assert not ContentContinuityProviderV2(mode="barrier_detector_layout_v2").tracking_barrier_for_decision(d)


@pytest.mark.parametrize(
    "transform",
    [
        (0.0,) * 9,
        (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, float("nan")),
        (True, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0),
        (1.0,) * 8,
    ],
)
def test_invalid_camera_transform_rejected(transform):
    raw = raw_relative()
    with pytest.raises(ValueError):
        decide(raw, probe_for(raw), transform=transform)


def test_projective_horizon_crossing_abstains_without_silent_clipping():
    raw = raw_relative()
    transform = (1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.05, 0.0, -1.5)
    d = decide(raw, probe_for(raw), transform=transform)
    assert d.decision == "unknown"
    validate_scene_decision_binding(d, raw)


def test_missing_previous_camera_source_proof_cannot_support_weak_reset():
    raw = raw_relative()
    d = decide(raw, probe_for(raw), previous_camera=None)
    assert d.decision == "unknown"
    validate_scene_decision_binding(d, raw)


def test_previous_camera_proof_requires_invertible_finite_matrix():
    raw = raw_relative()
    with pytest.raises(ValueError):
        decide(raw, probe_for(raw), previous_camera=(0.0,) * 9)
