"""Source-cadence and uncertainty regressions, without rally labels or models."""

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from bai_badminton.perception.content import ContentContinuityProvider, ContentContinuityProviderV2
from bai_badminton.perception.scene_change import ForegroundRegion, SceneChangeEvidence


def measurements(monkeypatch, provider, errors, *, consistency=0.95, count=2):
    # Background is static and reliable. Each actor's LK intensity residual is
    # specified independently of source pixels so the sampling defect is exact.
    call = 0

    def flow(*args):
        nonlocal call
        frame, region = divmod(call, count + 1)
        call += 1
        return (80, 1.0, 1.0, 0.0) if region == 0 else (40, consistency, errors[frame], 0.1)

    monkeypatch.setattr(
        "bai_badminton.perception.scene_change._flow_groups",
        lambda previous, current, masks: [flow(previous, current, mask) for mask in masks],
    )
    image = np.random.default_rng(3).integers(20, 220, (120, 180, 3), dtype=np.uint8)
    results = []
    for frame in range(len(errors) + 1):
        regions = (
            [ForegroundRegion(frame - 1, str(i), (20 + i * 45, 20, 50 + i * 45, 90), True, True) for i in range(count)]
            if frame
            else []
        )
        results.append(
            provider.observe(frame, image, previous_regions=regions, previous_view_valid=True, current_view_valid=True)
        )
    return results


def test_subquantization_pair_does_not_halve_prior_appearance_innovation(monkeypatch):
    errors = [10.0, 10.0, 0.1, 16.5]
    legacy = measurements(monkeypatch, ContentContinuityProvider(mode="barrier_hypothesis_v1"), errors)
    current = measurements(monkeypatch, ContentContinuityProviderV2(mode="barrier_correspondence_v2"), errors)
    assert legacy[-1].appearance_hypothesis and legacy[-1].hypothesis
    assert legacy[-1].regions[0].appearance_previous_mean == pytest.approx(5.05)
    assert current[-1].regions[0].appearance_previous_mean == 10.0
    assert current[-1].regions[0].median_patch_error == 16.5
    assert current[-2].regions[0].median_patch_error == 0.1
    assert not current[-1].appearance_hypothesis


def test_appearance_residual_alone_remains_visible_without_a_barrier(monkeypatch):
    provider = ContentContinuityProviderV2(mode="barrier_correspondence_v2")
    result = measurements(monkeypatch, provider, [3.0, 3.0, 45.0])[-1]
    assert result.appearance_hypothesis and result.hypothesis
    assert not result.correspondence_hypothesis
    assert result.authoritative is False
    assert not provider.barrier_for(result)


def test_joint_correspondence_loss_can_reset_tracking_without_authority(monkeypatch):
    provider = ContentContinuityProviderV2(mode="barrier_correspondence_v2")
    result = measurements(monkeypatch, provider, [3.0, 3.0, 100.0], consistency=0.1)[-1]
    assert result.correspondence_hypothesis
    assert provider.barrier_for(result)
    assert result.authoritative is False


def test_single_region_is_measured_but_cannot_prove_a_multi_actor_edit(monkeypatch):
    provider = ContentContinuityProviderV2(mode="barrier_correspondence_v2")
    result = measurements(monkeypatch, provider, [3.0, 3.0, 100.0], consistency=0.1, count=1)[-1]
    assert len(result.regions) == 1
    assert result.correspondence_hypothesis and result.hypothesis
    assert not provider.barrier_for(result)


def test_diagnostic_policy_cannot_erect_a_barrier():
    evidence = SceneChangeEvidence(10, 9, "hypothesis", True, ("raw",), correspondence_hypothesis=True)
    provider = ContentContinuityProviderV2()
    assert not provider.barrier_for(evidence)
    with pytest.raises(ValueError, match="policy"):
        ContentContinuityProviderV2(mode="barrier_hypothesis_v1")


def test_legacy_barrier_contract_is_preserved():
    result = SceneChangeEvidence(10, 9, "hypothesis", True, ("raw",), appearance_hypothesis=True)
    assert ContentContinuityProvider(mode="barrier_hypothesis_v1").barrier_for(result)
    assert not ContentContinuityProvider().barrier_for(result)


@pytest.mark.parametrize("case_index", [0, 1, 2])
def test_bound_source_windows_keep_true_edits_and_reject_duplicate_cadence_false_barrier(case_index):
    fixture = Path(__file__).parent / "fixtures/scene_cadence_source_windows.npz"
    metadata = json.loads(fixture.with_suffix(".json").read_text())
    assert hashlib.sha256(fixture.read_bytes()).hexdigest() == metadata["npz_sha256"]
    case = metadata["cases"][case_index]
    windows = np.load(fixture)
    legacy = ContentContinuityProvider(mode="barrier_hypothesis_v1")
    candidate = ContentContinuityProviderV2(mode="barrier_hypothesis_cadence_v2")
    control = ContentContinuityProviderV2(mode="barrier_correspondence_v2")
    for source, gray in zip(case["frames"], windows[case["name"]], strict=True):
        assert hashlib.sha256(gray.tobytes()).hexdigest() == source["derived_gray_sha256"]
        image = np.repeat(gray[:, :, None], 3, axis=2)
        arguments = {key: source[key] for key in ("previous_view_valid", "current_view_valid", "hard_cut")}
        arguments["previous_regions"] = [ForegroundRegion(**region) for region in source["previous_regions"]]
        old = legacy.observe(source["frame"], image, **arguments)
        new = candidate.observe(source["frame"], image, **arguments)
        rejected = control.observe(source["frame"], image, **arguments)
    assert legacy.barrier_for(old)
    assert candidate.barrier_for(new) is (case["agent_source_review"] == "visible_same_camera_edit")
    # This control was rejected because it suppresses real edits as well.
    assert not control.barrier_for(rejected)
