"""Source-bound scene quorum/layout evidence, never target-player or GT authority."""

from dataclasses import asdict, replace

import numpy as np
import pytest
from test_scene_decision_cache import source_frame as legacy_source_frame

from bai_badminton.perception import scene_change
from bai_badminton.perception.content import (
    ContentContinuityProviderV2,
    scene_change_from_dict,
    scene_decision_from_dict,
    validate_scene_decision_binding,
)
from bai_badminton.perception.players import PlayerDetectionProbe


def make_v3_raw(monkeypatch, *, adaptive_ratio=3.0, minimum_discontinuity=15.0):
    """Actual observer produces a valid two-witness plus static-third record."""
    calls = 0

    def flow(*_args):
        nonlocal calls
        pair, region = divmod(calls, 4)
        calls += 1
        if region == 0:
            return 80, 1.0, 1.0, 0.0
        changed = pair == 2 and region in (2, 3)
        return 40, 0.1 if changed else 0.95, 100.0 if changed else 3.0, 0.1

    monkeypatch.setattr(
        scene_change, "_flow_groups",
        lambda previous, current, masks: [flow(previous, current, mask) for mask in masks],
    )
    observer = scene_change.SceneContinuityDetectorV3(
        adaptive_ratio=adaptive_ratio, minimum_discontinuity=minimum_discontinuity
    )
    image = np.random.default_rng(14812).integers(20, 220, (720, 1280, 3), dtype=np.uint8)
    boxes = ((50.0, 100.0, 110.0, 300.0), (250.0, 100.0, 310.0, 300.0), (450.0, 100.0, 510.0, 300.0))
    for frame in range(22, 26):
        regions = (
            tuple(
                scene_change.ForegroundRegion(frame - 1, key, box, True, True)
                for key, box in zip(("scene:static", "scene:A", "scene:B"), boxes, strict=True)
            )
            if frame != 22
            else ()
        )
        raw = observer.observe(
            frame, image, previous_regions=regions, previous_view_valid=True, current_view_valid=True
        )
    assert raw.frame == 25 and raw.hypothesis
    assert raw.supporting_region_keys == ("scene:A", "scene:B")
    return raw


def make_probe(raw, *, admitted=(0,), ambiguous=False, discontinuity=False):
    static, a, b = (item.region.bbox for item in raw.regions)
    extra = (800.0, 100.0, 860.0, 300.0)
    boxes = (b, a if ambiguous else extra, static, a)
    if discontinuity:
        boxes = ((650.0, 400.0, 710.0, 600.0), extra, static, (1000.0, 400.0, 1060.0, 600.0))
    return PlayerDetectionProbe(25, (720, 1280, 3), "b" * 64, boxes, (0.9,) * 4, (0, 0, 1280, 720), admitted)


def decision_for(raw, probe):
    provider = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")
    return provider.layout_decision(raw, probe, detector_model="detector@1", geometry_valid=True)


def test_v3_parser_retains_actual_custom_witness_parameters(monkeypatch):
    raw = make_v3_raw(monkeypatch, adaptive_ratio=4.0, minimum_discontinuity=19.0)
    decoded = scene_change_from_dict(asdict(raw), frame_idx=25)
    assert decoded.witness_parameters == (4.0, 19.0)
    assert decoded.supporting_region_keys == ("scene:A", "scene:B")
    assert not decoded.authoritative


@pytest.mark.parametrize(
    "case",
    ["invented", "duplicate", "one", "empty", "flags", "features", "overlap", "split_channels"],
)
def test_v3_claimed_cohort_requires_actual_independent_channel_evidence(monkeypatch, case):
    value = asdict(make_v3_raw(monkeypatch))
    if case == "invented":
        value["supporting_region_keys"] = ("scene:A", "invented")
    elif case == "duplicate":
        value["supporting_region_keys"] = ("scene:A", "scene:A")
    elif case == "one":
        value["supporting_region_keys"] = ("scene:A",)
    elif case == "empty":
        value["supporting_region_keys"] = ()
    elif case == "flags":
        value["correspondence_hypothesis"] = value["appearance_hypothesis"] = False
    elif case == "features":
        value["regions"][1]["features"] = 0
    elif case == "overlap":
        value["regions"][1]["region"]["bbox"] = value["regions"][2]["region"]["bbox"]
    else:
        # One correspondence-only and one appearance-only region do not form
        # two witnesses in either independent signal channel.
        value["regions"][1]["appearance_adaptive_ratio"] = 1.0
        value["regions"][2]["adaptive_ratio"] = 1.0
    with pytest.raises(ValueError):
        scene_change_from_dict(value, frame_idx=25)


@pytest.mark.parametrize("parameters", [None, (), (3.0,), (True, 15.0), (float("nan"), 15.0)])
def test_v3_requires_finite_typed_witness_parameter_provenance(monkeypatch, parameters):
    value = asdict(make_v3_raw(monkeypatch))
    value["witness_parameters"] = parameters
    with pytest.raises(ValueError):
        scene_change_from_dict(value, frame_idx=25)


@pytest.mark.parametrize("admitted", [(0,), (), (0, 1, 2, 3)])
def test_complete_raw_layout_veto_uses_two_witnesses_despite_static_and_current_extra(monkeypatch, admitted):
    raw = make_v3_raw(monkeypatch)
    probe = make_probe(raw, admitted=admitted)
    decision = decision_for(raw, probe)
    assert decision.decision == "no_barrier"
    assert decision.version == "detector-layout-scene-decision:v2"
    assert decision.previous_region_count == 3
    assert decision.supporting_region_keys == ("scene:A", "scene:B")
    assert decision.admitted_indices == admitted  # No invented athlete admission.
    assert decision.layout_indices == (0, 1, 2, 3)
    assert decision.matched_pairs == ((1, 3), (2, 0))  # FULL raw-region indices.
    validate_scene_decision_binding(decision, raw)


def test_full_raw_layout_discontinuity_retains_static_nonwitness_without_veto(monkeypatch):
    raw = make_v3_raw(monkeypatch)
    decision = decision_for(raw, make_probe(raw, discontinuity=True))
    assert decision.decision == "barrier"
    assert decision.previous_region_count == 3
    assert decision.matched_pairs == ()
    validate_scene_decision_binding(decision, raw)


@pytest.mark.parametrize("pairs", [((0, 3), (1, 0)), ((1, 0), (2, 3))])
def test_witness_local_indices_and_wrong_geometry_cannot_forge_correspondence(monkeypatch, pairs):
    raw = make_v3_raw(monkeypatch)
    decision = decision_for(raw, make_probe(raw))
    with pytest.raises(ValueError):
        validate_scene_decision_binding(replace(decision, matched_pairs=pairs), raw)


def test_decision_witness_keys_must_match_exact_raw_cohort(monkeypatch):
    raw = make_v3_raw(monkeypatch)
    decision = decision_for(raw, make_probe(raw))
    with pytest.raises(ValueError):
        validate_scene_decision_binding(replace(decision, supporting_region_keys=("scene:static", "scene:B")), raw)


@pytest.mark.parametrize("indices", [(0, 3), (0, 0, 2, 3), (0, 1, 2, 4), (False, 1, 2, 3)])
def test_v2_layout_indices_cannot_hide_raw_detections_or_invent_indices(monkeypatch, indices):
    raw = make_v3_raw(monkeypatch)
    decision = decision_for(raw, make_probe(raw))
    value = asdict(decision)
    value["layout_indices"] = indices
    with pytest.raises(ValueError):
        decoded = scene_decision_from_dict(value, frame_idx=25)
        validate_scene_decision_binding(decoded, raw)


def test_extra_raw_duplicate_is_ambiguous_even_when_not_athlete_admitted(monkeypatch):
    raw = make_v3_raw(monkeypatch)
    decision = decision_for(raw, make_probe(raw, admitted=(0,), ambiguous=True))
    assert decision.decision == "unknown"
    assert decision.matched_pairs == ()
    assert decision.admitted_indices == (0,)
    for forged in ("barrier", "no_barrier"):
        pairs = ((1, 3), (2, 0)) if forged == "no_barrier" else ()
        with pytest.raises(ValueError):
            validate_scene_decision_binding(replace(decision, decision=forged, matched_pairs=pairs), raw)


def test_raw_v2_and_decision_v1_historical_dictionary_fields_remain_readable():
    frame = legacy_source_frame()
    raw, decision = asdict(frame.content_change), asdict(frame.content_decision)
    raw.pop("supporting_region_keys", None)
    raw.pop("witness_parameters", None)
    decision.pop("supporting_region_keys", None)
    decision.pop("layout_indices", None)
    decoded_raw = scene_change_from_dict(raw, frame_idx=25)
    decoded_decision = scene_decision_from_dict(decision, frame_idx=25)
    assert decoded_raw.version == "foreground-scene-hypothesis:v2"
    assert decoded_decision.version == "detector-layout-scene-decision:v1"
    validate_scene_decision_binding(decoded_decision, decoded_raw)
