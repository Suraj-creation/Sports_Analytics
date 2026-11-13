"""Observed candidate recovery; synthetic trajectories are not physical labels."""

from collections import deque
from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.perception.association import (
    CURRENT_ASSOCIATION_SCHEMA,
    CausalShuttleAssociation,
    ShuttleObservationEvidence,
    _Hypothesis,
)
from bai_badminton.perception.diagnostics import HeatmapCandidate, ShuttleDiagnostic

FLOOR = (500.0, 400.0)


def candidate(rank, point, *, support=0.7, above=True, mask=True, selected=False):
    return HeatmapCandidate(rank, point, (point[0] + 0.1, point[1] + 0.1), support, 30, 6.0, mask, above, selected)


def update(provider, frame, point, others=(), *, epoch=0, valid=True):
    values = (() if point is None else (candidate(1, point, support=0.95, selected=True),)) + tuple(
        candidate(i + 2, xy) if isinstance(xy, tuple) else xy for i, xy in enumerate(others)
    )
    d = ShuttleDiagnostic(
        values,
        0.95,
        0.95 if point else 0.0,
        0.5,
        0.1,
        "accepted" if point else "below_threshold",
        1,
        decoded_xy=point,
        selected_masked_peak_xy=point,
    )
    return provider.update(
        frame, epoch=epoch, raw_xy=point, raw_support=0.95 if point else 0.0, diagnostic=d, image_valid=valid
    )


def taught():
    provider = CausalShuttleAssociation(fps=30)
    for frame in range(15):
        update(provider, frame, (100.0 + 12 * frame, 100.0), (FLOOR,))
    return provider


def recovered():
    provider = taught()
    return provider, update(provider, 15, FLOOR, ((280.0, 100.0),))


def test_recent_configured_ten_not_old_outliers_define_current_stationarity():
    samples = deque([(i, 510.0, 400.0, 1.0) for i in range(3)] + [(i, 500.0, 400.0, 1.0) for i in range(3, 13)])
    h = _Hypothesis(1, samples)
    assert h.compact(10)
    assert not _Hypothesis(1, deque(list(samples)[-9:])).compact(10)
    h.samples.append((13, 520.0, 400.0, 1.0))
    assert not h.compact(10)


def test_static_contradiction_recovers_exact_current_peak_not_floor_centroid():
    _, result = recovered()
    assert result.schema == CURRENT_ASSOCIATION_SCHEMA
    assert result.raw_xy == FLOOR and result.raw_model_support == 0.95
    assert result.selected_xy == (280.0, 100.0) and result.selected_model_support == 0.7
    assert result.selected_candidate_rank == 2
    assert result.selection_coordinate_source == "current_candidate_peak"
    assert result.selection_model_threshold == 0.5
    assert result.selection_witness_frames == (12, 13, 14)
    assert len(result.competing_motion_frames) >= 3
    assert result.hypothesis_id != result.selection_hypothesis_id
    assert ShuttleObservationEvidence.from_dict(result.to_dict()) == result


def test_quantized_zero_motion_continues_current_footprint_without_new_motion_credit():
    provider, first = recovered()
    track = next(t for t in provider._tracks if t.identity == first.hypothesis_id)
    witnesses = list(track.witnesses)
    second = update(provider, 16, FLOOR, ((280.0, 100.0),))
    assert second.selected_xy == (280.0, 100.0)
    assert second.selection_hypothesis_id == first.selection_hypothesis_id
    assert second.selection_witness_frames == (12, 13, 14, 15)
    assert list(track.witnesses) == witnesses


def test_two_coherent_paths_cannot_choose_by_confidence_or_candidate_order():
    result = update(taught(), 15, FLOOR, ((280.0, 100.0), (280.0, 110.0)))
    assert result.status == "ambiguous" and result.selected_xy is None


def test_one_footprint_split_into_two_current_peaks_is_ambiguous_even_with_greedy_track_id():
    provider, _ = recovered()
    result = update(provider, 16, FLOOR, ((282.0, 100.0), (280.0, 102.0)))
    assert result.status == "ambiguous" and result.selected_xy is None
    assert result.reasons == ("competing_moving_branches_ambiguous",)


@pytest.mark.parametrize(
    "other",
    [
        candidate(2, (280.0, 100.0), above=False),
        candidate(2, (280.0, 100.0), support=0.49),
        candidate(2, (280.0, 100.0), mask=False),
    ],
)
def test_current_alternative_needs_actual_threshold_and_mask(other):
    assert update(taught(), 15, FLOOR, (other,)).selected_xy is None


def test_real_floor_without_contradiction_is_not_replaced_by_unrelated_peak():
    provider = CausalShuttleAssociation(fps=30)
    for f in range(20):
        result = update(provider, f, FLOOR, ((100.0 + 12 * f, 100.0),))
        assert result.selected_xy == FLOOR and result.selection_coordinate_source == "raw_model_coordinate"


@pytest.mark.parametrize("break_kind", ["missing", "gap", "epoch", "invalid"])
def test_new_recovery_authority_does_not_cross_missing_source_or_epoch(break_kind):
    provider, _ = recovered()
    if break_kind == "missing":
        assert update(provider, 16, None).selected_xy is None
        result = update(provider, 17, FLOOR, ((280.0, 100.0),))
    elif break_kind == "gap":
        result = update(provider, 17, FLOOR, ((280.0, 100.0),))
    elif break_kind == "epoch":
        result = update(provider, 16, FLOOR, ((280.0, 100.0),), epoch=1)
    else:
        assert update(provider, 16, FLOOR, ((280.0, 100.0),), valid=False).status == "invalid"
        result = update(provider, 17, FLOOR, ((280.0, 100.0),))
    assert result.selection_coordinate_source != "current_candidate_peak"


def test_registration_context_change_resets_new_branch_memory_and_invalid_matrix_refuses():
    provider, _ = recovered()
    with pytest.raises(ValueError):
        provider.update(
            16,
            epoch=0,
            raw_xy=FLOOR,
            raw_support=0.9,
            diagnostic=None,
            image_valid=True,
            image_to_reference=np.zeros((3, 3)),
        )
    result = provider.update(
        16, epoch=0, raw_xy=FLOOR, raw_support=0.9, diagnostic=None, image_valid=True, image_to_reference=np.eye(3)
    )
    assert result.selection_coordinate_source == "raw_model_coordinate"
    assert not provider._candidate_history and not provider._moving_footprints


def test_checkpoint_restores_every_new_branch_state_and_bounds():
    provider = taught()
    checkpoint = provider.checkpoint()
    first = update(provider, 15, FLOOR, ((280.0, 100.0),))
    provider.restore(checkpoint)
    assert update(provider, 15, FLOOR, ((280.0, 100.0),)).to_dict() == first.to_dict()
    for f in range(16, 150):
        update(provider, f, FLOOR, ((280.0, 100.0),))
        assert len(provider._candidate_history) <= 3
        assert len(provider._moving_footprints) <= provider.maximum_tracks
        assert provider.retained_tracks <= provider.maximum_tracks
        assert provider.retained_samples <= provider.maximum_tracks * provider.history_frames
    provider.reset()
    assert not provider._candidate_history and not provider._moving_footprints


def test_fast_positive_motion_is_not_capped_by_interpolation_fill_speed():
    provider = CausalShuttleAssociation(fps=30)
    for f in range(15):
        update(provider, f, (100.0 + 100 * f, 100.0), (FLOOR,))
    result = update(provider, 15, FLOOR, ((1600.0, 100.0),))
    assert result.selection_coordinate_source == "current_candidate_peak"


@pytest.mark.parametrize(
    "field,value",
    [
        ("selected_xy", (280.1, 100.1)),
        ("selected_model_support", 0.95),
        ("selection_model_threshold", 0.8),
        ("selected_candidate_rank", 1),
        ("selection_witness_frames", (12, 12, 14)),
        ("selection_witness_frames", (13, 14, 15)),
        ("selection_hypothesis_id", None),
    ],
)
def test_forged_v3_recovery_is_rejected(field, value):
    _, good = recovered()
    with pytest.raises(ValueError):
        replace(good, **{field: value})


def test_legacy_default_and_wire_stay_strict_and_do_not_silently_gain_v3_fields():
    legacy = ShuttleObservationEvidence(0, 0, "observed", "tracked", FLOOR, FLOOR, 0.9)
    wire = legacy.to_dict()
    assert wire["schema"] == "badminton-shuttle-association:v2"
    assert "selection_coordinate_source" not in wire
    assert ShuttleObservationEvidence.from_dict(wire) == legacy
    with pytest.raises(ValueError):
        replace(legacy, selected_xy=(1.0, 2.0))
    with pytest.raises(ValueError):
        ShuttleObservationEvidence.from_dict({**wire, "selected_candidate_rank": None})
    _, current = recovered()
    with pytest.raises(ValueError):
        ShuttleObservationEvidence.from_dict({**current.to_dict(), "schema": legacy.schema, "method": legacy.method})


def test_raw_source_cannot_forge_candidate_or_motion_authority():
    raw = update(CausalShuttleAssociation(fps=30), 0, FLOOR)
    with pytest.raises(ValueError):
        replace(raw, selected_candidate_rank=1)
    with pytest.raises(ValueError):
        replace(raw, selection_hypothesis_id=1)


def test_masked_raw_target_is_retained_even_when_not_a_retained_candidate_peak():
    target = (15.0, 20.0)
    d = ShuttleDiagnostic(
        (candidate(1, (500.0, 400.0), mask=False),),
        0.9,
        0.7,
        0.5,
        0.1,
        "accepted",
        1,
        decoded_xy=target,
        selected_masked_peak_xy=target,
    )
    value = CausalShuttleAssociation(fps=30).update(
        0, epoch=0, raw_xy=target, raw_support=0.7, diagnostic=d, image_valid=True
    )
    assert value.raw_masked_peak_xy == target
    assert value.selected_xy == target and value.selected_candidate_rank is None
    assert ShuttleObservationEvidence.from_dict(value.to_dict()).raw_masked_peak_xy == target


def test_missing_diagnostic_keeps_unknown_raw_mask_target_and_legacy_cannot_claim_it():
    value = CausalShuttleAssociation(fps=30).update(
        0, epoch=0, raw_xy=FLOOR, raw_support=0.7, diagnostic=None, image_valid=True
    )
    assert value.raw_masked_peak_xy is None
    legacy = ShuttleObservationEvidence(0, 0, "observed", "tracked", FLOOR, FLOOR, 0.7)
    assert "raw_masked_peak_xy" not in legacy.to_dict()
    with pytest.raises(ValueError):
        replace(legacy, raw_masked_peak_xy=FLOOR)
    with pytest.raises(ValueError):
        ShuttleObservationEvidence.from_dict({**legacy.to_dict(), "raw_masked_peak_xy": None})


@pytest.mark.parametrize("point", [(True, 3.0), (float("nan"), 3.0), (1.0, 2.0, 3.0)])
def test_invalid_retained_mask_target_refuses(point):
    value = update(CausalShuttleAssociation(fps=30), 0, FLOOR)
    with pytest.raises(ValueError):
        replace(value, raw_masked_peak_xy=point)


def test_current_wire_cannot_drop_explicit_mask_target_or_duplicate_motion_proof():
    _, value = recovered()
    wire = value.to_dict()
    del wire["raw_masked_peak_xy"]
    with pytest.raises(ValueError):
        ShuttleObservationEvidence.from_dict(wire)
    with pytest.raises(ValueError):
        replace(value, competing_motion_frames=(8, 9, 9, 10))


def test_current_masked_global_max_support_cannot_be_exceeded_by_forged_alternative():
    _, value = recovered()
    candidates = tuple(replace(c, peak_support=.99) if c.rank == 2 else c for c in value.candidates)
    with pytest.raises(ValueError):
        replace(value, candidates=candidates, selected_model_support=.99)


def test_alternative_cannot_drop_actual_masked_raw_target_needed_by_its_static_proof():
    _, value = recovered()
    with pytest.raises(ValueError):
        replace(value, raw_masked_peak_xy=None)
