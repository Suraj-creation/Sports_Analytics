"""Weightless provider replacement, bounded codec and explicit policy controls."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict

import numpy as np
import pytest

from bai_badminton.perception.components import ContentContinuityPort, PerceptionContext, register_perception_components
from bai_badminton.perception.content import (
    CONTENT_IMPLEMENTATION,
    ContentContinuityProvider,
    scene_change_from_dict,
    scene_change_to_dict,
)
from bai_badminton.perception.scene_change import ForegroundRegion, RegionContinuity, SceneChangeEvidence
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.runtime.registry import ModelRegistry


def context(tmp_path):
    model_dir = tmp_path / "models"
    model_dir.mkdir(exist_ok=True)
    (model_dir / "manifest.yaml").write_text("models: {}\n")
    model_events, runtime_events = [], []

    def forbidden(*_):
        raise AssertionError("weightless scene provider must never load models")

    return (
        PerceptionContext(
            ModelRegistry(model_dir),
            tmp_path / "cache",
            30.0,
            (1280, 720),
            forbidden,
            forbidden,
            forbidden,
            forbidden,
            forbidden,
            forbidden,
            lambda *args: model_events.append(args),
            lambda *args: runtime_events.append(args),
        ),
        model_events,
        runtime_events,
    )


def evidence():
    region = ForegroundRegion(9, "track:anonymous", (20.0, 40.0, 60.0, 120.0), False, True)
    measurement = RegionContinuity(region, 20, 0.5, 30.0, 2.0, 15.0, 1.0, 15.0, 2.0, 15.0)
    return SceneChangeEvidence(
        10,
        9,
        "hypothesis",
        True,
        ("appearance_discontinuity",),
        (measurement,),
        80,
        0.95,
        1.0,
        15.0,
        1.0,
        0.0,
        appearance_hypothesis=True,
        appearance_discontinuity=30.0,
    )


@pytest.mark.parametrize("match_format", ["singles", "doubles", "unknown"])
@pytest.mark.parametrize("mode", ["diagnostic", "barrier_hypothesis_v1"])
def test_explicit_registry_provider_is_weightless_and_policy_changes_fingerprint(tmp_path, match_format, mode):
    registry = ComponentRegistry()
    register_perception_components(registry)
    ctx, models, runtime = context(tmp_path)
    config = {"model": "none", "backend": "opencv-cpu", "params": {"mode": mode}}
    handle = registry.create(
        "content_continuity", CONTENT_IMPLEMENTATION, context=ctx, configuration=config, match_format=match_format
    )
    other_mode = "diagnostic" if mode != "diagnostic" else "barrier_hypothesis_v1"
    other = registry.create(
        "content_continuity",
        CONTENT_IMPLEMENTATION,
        context=ctx,
        configuration={**config, "params": {"mode": other_mode}},
        match_format=match_format,
    )
    assert isinstance(handle.instance, ContentContinuityPort)
    assert handle.instance.barrier_enabled is (mode == "barrier_hypothesis_v1")
    assert handle.fingerprint != other.fingerprint
    assert models[-1] == ("content_continuity", f"{CONTENT_IMPLEMENTATION}@1")
    assert runtime[-1][1]["weights"] is None and runtime[-1][1]["backend"] == "opencv-cpu"
    declared = next(row for row in registry.describe() if row["kind"] == "content_continuity")
    assert declared["declaration"]["default_enabled"] is False
    assert declared["declaration"]["bounded_evidence"]["regions"] == 8
    handle.close()
    other.close()


def test_an_independent_structural_provider_can_replace_the_baseline(tmp_path):
    class Independent:
        barrier_enabled = False

        def observe(self, frame, *_args, **_kwargs):
            return SceneChangeEvidence(frame, None, "unknown", False, ("independent_unknown",))

        def reset(self):
            pass

        def close(self):
            pass

        def checkpoint(self):
            return None

        def restore(self, _checkpoint):
            pass

    registry = ComponentRegistry()
    register_perception_components(registry)
    registry.register(
        ComponentContract(
            kind="content_continuity",
            implementation="independent",
            version="1",
            input_schema="independent-current-pixels:v1",
            output_schema="foreground-scene-hypothesis:v2",
            interface=ContentContinuityPort,
            context_type=PerceptionContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="abstain",
            stateful=True,
        ),
        lambda *_: Independent(),
    )
    ctx, _, _ = context(tmp_path)
    handle = registry.create("content_continuity", "independent", context=ctx, configuration={}, match_format="doubles")
    result = handle.instance.observe(5, None, previous_regions=[], previous_view_valid=False, current_view_valid=False)
    assert not result.hypothesis and scene_change_from_dict(scene_change_to_dict(result), frame_idx=5) == result
    handle.close()


def test_provider_checkpoint_reset_close_and_policy_never_rewrite_evidence():
    provider = ContentContinuityProvider(mode="barrier_hypothesis_v1")
    with pytest.raises(AttributeError):
        provider.mode = "diagnostic"
    image = np.arange(90 * 160 * 3, dtype=np.uint8).reshape(90, 160, 3)
    saved = provider.checkpoint()
    first = provider.observe(0, image, previous_regions=[], previous_view_valid=False, current_view_valid=False)
    provider.restore(saved)
    repeated = provider.observe(0, image, previous_regions=[], previous_view_valid=False, current_view_valid=False)
    assert first == repeated and first.authoritative is False
    provider.reset()
    provider.close()
    provider.close()
    with pytest.raises(RuntimeError, match="closed"):
        provider.observe(1, image, previous_regions=[], previous_view_valid=False, current_view_valid=False)


def test_codec_retains_carried_region_and_is_detached():
    source = evidence()
    encoded = scene_change_to_dict(source)
    decoded = scene_change_from_dict(encoded, frame_idx=10)
    assert decoded == source and decoded.regions[0].region.detector_matched is False
    encoded["regions"][0]["region"]["key"] = "mutated"
    assert decoded.regions[0].region.key == "track:anonymous"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda row: row.update(frame=11),
        lambda row: row.update(previous_frame=10),
        lambda row: row.update(authoritative=True),
        lambda row: row.update(version="unknown:v99"),
        lambda row: row.update(source_basis="future_boxes"),
        lambda row: row.update(support_semantics="calibrated_probability"),
        lambda row: row.update(discontinuity=float("nan")),
        lambda row: row.update(background_consistent_fraction=2.0),
        lambda row: row.update(regions=row["regions"] * 9),
        lambda row: row.update(reasons=["x"] * 9),
        lambda row: row.update(status=[]),
        lambda row: row.update(unknown_key=True),
        lambda row: row["regions"][0]["region"].update(frame=10),
        lambda row: row["regions"][0]["region"].update(bbox=[0, 0, float("inf"), 10]),
        lambda row: row["regions"][0]["region"].update(key="x" * 161),
        lambda row: row["regions"][0].update(features=4097),
        lambda row: row["regions"][0].update(appearance_adaptive_ratio=float("inf")),
    ],
)
def test_malformed_or_unbounded_codec_evidence_is_rejected(mutation):
    row = deepcopy(asdict(evidence()))
    mutation(row)
    with pytest.raises((TypeError, ValueError)):
        scene_change_from_dict(row, frame_idx=10)


def test_boolean_frame_identity_is_never_an_integer_alias():
    with pytest.raises(ValueError):
        scene_change_from_dict(asdict(SceneChangeEvidence(1, 0, "unknown", False, ("unknown",))), frame_idx=True)


@pytest.mark.parametrize(
    "params",
    [
        {"mode": "automatic"},
        {"mode": []},
        {"analysis_width": True},
        {"analysis_width": 10000},
        {"analysis_width": None},
        {"unknown": 1},
    ],
)
def test_provider_rejects_unsupported_or_unbounded_configuration(params):
    with pytest.raises(ValueError):
        ContentContinuityProvider(**params)
