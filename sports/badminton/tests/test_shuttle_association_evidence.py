"""Association contracts; synthetic objects are not independent sporting labels."""

from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.perception.association import CausalShuttleAssociation, ShuttleObservationEvidence
from bai_badminton.perception.diagnostics import HeatmapCandidate, ShuttleDiagnostic


def diagnostic(primary, competing=(), *, support=0.8, spread=6.0):
    points = (() if primary is None else (primary,)) + tuple(competing)
    candidates = tuple(
        HeatmapCandidate(i + 1, point, point, support if i == 0 else 0.4, 30, spread, True, i == 0, i == 0)
        for i, point in enumerate(points)
    )
    return ShuttleDiagnostic(
        candidates,
        support if points else 0.0,
        support if primary else 0.0,
        0.5,
        0.1,
        "accepted" if primary else "below_threshold",
        1,
        decoded_xy=primary,
        selected_masked_peak_xy=primary,
    )


def update(provider, frame, point, competitors=(), **kwargs):
    return provider.update(
        frame,
        epoch=0,
        raw_xy=point,
        raw_support=0.8 if point else 0.0,
        diagnostic=diagnostic(point, competitors),
        image_valid=True,
        **kwargs,
    )


def teach(provider, *, offset=0, matrix=None):
    for i in range(15):
        point = (100.0 + 12 * i, 150.0 - 6 * i)
        update(provider, offset + i, point, ((500.0 + i % 2, 400.0 - i % 2),), image_to_reference=matrix)


def test_persistent_competing_static_peak_is_ambiguous_not_landing_or_contact():
    provider = CausalShuttleAssociation(fps=30)
    teach(provider)
    result = update(provider, 15, (500.0, 400.0))
    assert result.status == "ambiguous"
    assert result.association_status == "static_candidate"
    assert result.raw_xy == (500.0, 400.0) and result.selected_xy is None
    assert len(result.competing_motion_frames) >= 3
    assert max(result.competing_motion_frames) < 15
    assert result.support_semantics == "association_support_not_calibrated_probability"


def test_real_stationary_or_floor_shuttle_is_not_rejected_without_coexistence():
    provider = CausalShuttleAssociation(fps=30)
    for i in range(150):
        result = update(provider, i, (500.0 + i % 2, 400.0))
        assert result.status == "observed" and result.selected_xy == result.raw_xy


def test_weak_stationary_launch_and_apex_are_not_incoming_speed_filtered():
    provider = CausalShuttleAssociation(fps=30)
    points = [(200.0, 200.0)] * 15 + [(200.0 + i, 200.0 - i * i / 5) for i in range(15)]
    for i, point in enumerate(points):
        result = update(provider, i, point)
        assert result.selected_xy == point


def test_missing_remains_missing_without_forecast_coordinates():
    provider = CausalShuttleAssociation(fps=30)
    teach(provider)
    for i in range(15, 35):
        result = update(provider, i, None)
        assert result.status == "missing" and result.selected_xy is None and result.raw_xy is None


def test_registration_does_not_relabel_raw_image_pixels_as_reference_coordinates():
    provider = CausalShuttleAssociation(fps=30)
    transform = np.array([[2.0, 0, 50], [0, 2.0, 20], [0, 0, 1]])
    result = update(provider, 0, (20.0, 30.0), image_to_reference=transform)
    assert result.raw_xy == result.selected_xy == (20.0, 30.0)
    assert result.coordinate_basis == "analysis_image_pixels"
    assert result.association_coordinate_basis == "registered_reference_pixels"


def test_reacquisition_is_a_new_observation_and_does_not_invent_a_contact():
    provider = CausalShuttleAssociation(fps=30)
    teach(provider)
    assert update(provider, 15, (500.0, 400.0)).status == "ambiguous"
    result = update(provider, 16, (290.0, 10.0))
    assert result.status == "observed" and result.selected_xy == (290.0, 10.0)
    assert result.association_status == "reacquisition"
    assert not hasattr(result, "contact")


def test_coobserved_motion_proofs_expire_even_when_static_track_keeps_refreshing():
    provider = CausalShuttleAssociation(fps=30)
    teach(provider)
    for frame in range(15, 100):
        result = update(provider, frame, (500.0, 400.0))
    assert result.status == "observed" and not result.competing_motion_frames


def test_one_peak_switch_or_large_jump_does_not_manufacture_airborne_witnesses():
    provider = CausalShuttleAssociation(fps=30)
    for frame in range(30):
        point = (100.0 if frame % 5 < 3 else 400.0, 150.0)
        update(provider, frame, point, ((500.0, 400.0),))
    assert update(provider, 30, (500.0, 400.0)).status == "observed"


def test_missing_candidate_provider_cannot_label_next_frame_as_continuously_tracked():
    provider = CausalShuttleAssociation(fps=30)
    update(provider, 0, (20.0, 20.0))
    provider.update(1, epoch=0, raw_xy=None, raw_support=0.0, diagnostic=None, image_valid=True)
    assert update(provider, 2, (30.0, 30.0)).association_status == "reacquisition"


@pytest.mark.parametrize("boundary", ["epoch", "invalid", "gap"])
def test_proofs_do_not_cross_content_view_or_nonsequential_context(boundary):
    provider = CausalShuttleAssociation(fps=30)
    teach(provider)
    if boundary == "epoch":
        result = provider.update(
            15, epoch=1, raw_xy=(500.0, 400.0), raw_support=0.8, diagnostic=diagnostic((500.0, 400.0)), image_valid=True
        )
    elif boundary == "invalid":
        result = provider.update(
            15,
            epoch=0,
            raw_xy=(500.0, 400.0),
            raw_support=0.8,
            diagnostic=diagnostic((500.0, 400.0)),
            image_valid=False,
        )
        assert result.status == "invalid"
        result = update(provider, 16, (500.0, 400.0))
    else:
        result = update(provider, 45, (500.0, 400.0))
    assert result.selected_xy == (500.0, 400.0)
    assert not result.competing_motion_frames


def test_mask_rejected_hypotheses_never_teach_a_static_competitor():
    provider = CausalShuttleAssociation(fps=30)
    for i in range(15):
        point = (100.0 + i * 12, 150.0 - i * 6)
        dg = diagnostic(point, ((500.0, 400.0),))
        dg = replace(dg, candidates=(dg.candidates[0], replace(dg.candidates[1], mask_allows_peak=False)))
        provider.update(i, epoch=0, raw_xy=point, raw_support=0.8, diagnostic=dg, image_valid=True)
    assert update(provider, 15, (500.0, 400.0)).status == "observed"


def test_bad_shape_or_unavailable_diagnostics_never_fabricate_support():
    provider = CausalShuttleAssociation(fps=30)
    result = provider.update(0, epoch=0, raw_xy=(500.0, 400.0), raw_support=0.9, diagnostic=None, image_valid=True)
    assert result.status == "observed" and result.association_status == "unknown"
    assert not result.competing_motion_frames
    with pytest.raises(ValueError):
        provider.update(1, epoch=0, raw_xy=(np.nan, 0), raw_support=0.9, diagnostic=None, image_valid=True)


def test_checkpoint_and_rollback_preserve_source_frames_and_bound_storage():
    provider = CausalShuttleAssociation(fps=30, maximum_tracks=8)
    teach(provider)
    checkpoint = provider.checkpoint()
    expected = update(provider, 15, (500.0, 400.0))
    provider.reset()
    provider.restore(checkpoint)
    assert update(provider, 15, (500.0, 400.0)) == expected
    with pytest.raises(ValueError):
        update(provider, 15, (500.0, 400.0))
    for i in range(16, 2000):
        update(provider, i, (float(i * 10), float(i)), ((float(i * 20), float(i * 2)),))
    assert provider.retained_tracks <= 8
    assert provider.retained_samples <= 8 * provider.history_frames
    provider.close()
    assert provider.retained_tracks == 0


def test_image_registration_is_separate_from_raw_observation_coordinates():
    provider = CausalShuttleAssociation(fps=30)
    for i in range(15):
        shift = i * 7.0
        matrix = np.array([[1.0, 0.0, -shift], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        update(
            provider, i, (100.0 + i * 12 + shift, 150.0 - i * 6), ((500.0 + shift, 400.0),), image_to_reference=matrix
        )
    matrix = np.array([[1.0, 0.0, -105.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
    result = update(provider, 15, (605.0, 400.0), image_to_reference=matrix)
    assert result.status == "ambiguous" and result.raw_xy == (605.0, 400.0)


def test_evidence_schema_roundtrip_and_immutable_source_identity():
    provider = CausalShuttleAssociation(fps=30)
    teach(provider)
    value = update(provider, 15, (500.0, 400.0))
    assert ShuttleObservationEvidence.from_dict(value.to_dict()) == value
    with pytest.raises(ValueError):
        ShuttleObservationEvidence.from_dict({**value.to_dict(), "schema": "unversioned"})
    with pytest.raises(ValueError):
        ShuttleObservationEvidence.from_dict({**value.to_dict(), "selected_xy": [500, 400]})
