"""Acquisition evidence contracts; synthetic trajectories are not sporting GT."""

import json
from dataclasses import replace

import pytest

from bai_badminton.perception.acquisition import MotionAcquisitionProof, ObservedMotionAcquisition


def provider():
    return ObservedMotionAcquisition(minimum_motion_px_per_frame=3.0, maximum_age_frames=60)


def sample(p, frame, point, *, epoch=7, valid=True, observed=True):
    p.observe(frame, epoch, point, context_valid=valid, observed=observed)


def chunk(p, start=0, end=59, *, moving_end=51, epoch=7):
    for frame in range(start, end + 1):
        moving = moving_end - 3 <= frame <= moving_end
        sample(p, frame, (4.0 * frame, float(frame)) if moving else None, epoch=epoch, observed=moving)
    p.complete_chunk(start, end)


def test_completed_chunk_source_proof_and_json_roundtrip():
    p = provider()
    chunk(p)
    proof = p.request(60, 7)
    assert proof.source_frames == (48, 49, 50, 51)
    assert proof.decision_frame == 60
    assert proof.completed_chunk_start == 0 and proof.completed_chunk_end == 59
    assert proof.coordinate_basis == "registered_reference_pixels"
    assert proof.authority == "configured_sampling_request_only"
    assert MotionAcquisitionProof.from_dict(json.loads(json.dumps(proof.to_dict()))) == proof
    assert p.request(60, 7) == proof  # application never grants fresh evidence


def test_current_pending_chunk_cannot_be_consumed():
    p = provider()
    for frame in range(4):
        sample(p, frame, (4.0 * frame, 0.0))
    with pytest.raises(ValueError, match="incomplete"):
        p.request(4, 7)
    p.complete_chunk(0, 3)
    assert p.request(4, 7).source_frames == (0, 1, 2, 3)
    with pytest.raises(ValueError, match="follow"):
        p.request(3, 7)


def test_ordinary_missing_breaks_run_but_does_not_renew_existing_lease():
    p = provider()
    chunk(p, moving_end=3)
    assert p.request(60, 7).source_frames[-1] == 3
    chunk(p, start=60, end=62, moving_end=-10)
    assert p.request(63, 7).source_frames[-1] == 3  # existing TTL, boundary inclusive
    chunk(p, start=63, end=63, moving_end=-10)
    assert p.request(64, 7) is None


@pytest.mark.parametrize("kind", ["missing", "carried", "reconstructed", "rejected", "ambiguous"])
def test_nonobserved_points_never_join_a_motion_run(kind):
    p = provider()
    for frame in range(7):
        sample(p, frame, (4.0 * frame, 0.0), observed=frame != 3)
    p.complete_chunk(0, 6)
    assert p.request(7, 7) is None


@pytest.mark.parametrize("points", [
    [(0, 0), (0, 0), (0, 0), (0, 0)],
    [(0, 0), (0, 0), (100, 0), (100, 0)],
    [(0, 0), (4, 0), (0, 0), (4, 0)],
    [(0, 0), (3, 0), (6, 0), (9, 0)],
    [(0, 0), (4, 0), (4, 4), (8, 4)],
])
def test_static_jump_reversal_boundary_speed_and_orthogonal_steps_abstain(points):
    p = provider()
    for frame, point in enumerate(points):
        sample(p, frame, point)
    p.complete_chunk(0, 3)
    assert p.request(4, 7) is None


@pytest.mark.parametrize("transition", ["cut", "invalid_geometry", "invalid_view", "unobserved_frame_gap"])
def test_context_or_epoch_invalidations_revoke_published_and_pending_proof(transition):
    p = provider()
    chunk(p)
    assert p.request(60, 7)
    if transition == "cut":
        sample(p, 60, None, epoch=8, observed=False)
        epoch = 8
    elif transition == "unobserved_frame_gap":
        sample(p, 61, None, observed=False)
        epoch = 7
    else:
        sample(p, 60, None, valid=False, observed=False)
        epoch = 7
    p.complete_chunk(61 if transition == "unobserved_frame_gap" else 60,
                     61 if transition == "unobserved_frame_gap" else 60)
    assert p.request(62 if transition == "unobserved_frame_gap" else 61, epoch) is None


def test_changed_request_epoch_revokes_proof_without_observing_new_chunk():
    p = provider()
    chunk(p)
    assert p.request(60, 8) is None
    assert p.request(60, 7) is None


def test_skipped_completed_chunk_cannot_reuse_a_published_lease():
    p = provider()
    chunk(p)
    assert p.request(61, 7) is None
    assert p.request(60, 7) is None


def test_duplicate_or_rewound_observation_and_invalid_completion_refused():
    p = provider()
    sample(p, 10, (10, 10))
    for frame in (10, 9):
        with pytest.raises(ValueError, match="chronological"):
            sample(p, frame, (20, 20))
    for start, end in ((0, 10), (10, 11), (11, 10)):
        with pytest.raises(ValueError, match="completion"):
            p.complete_chunk(start, end)


def test_reset_and_owner_bound_checkpoint_restore_pending_transaction():
    p = provider()
    chunk(p)
    before = p.checkpoint()
    sample(p, 60, None, valid=False, observed=False)
    p.restore(before)
    assert p.request(60, 7)
    with pytest.raises(ValueError, match="incompatible"):
        provider().restore(before)
    p.reset()
    assert p.request(60, 7) is None


@pytest.mark.parametrize("field,value", [
    ("version", "unknown"), ("coordinate_basis", "court_meters"),
    ("authority", "rally_active"), ("source_frames", (48, 49, 51, 52)),
    ("source_frames", (48, 49, 50, True)), ("decision_frame", 59),
    ("completed_chunk_end", 60), ("decision_frame", 112),
    ("epoch", True), ("reference_xy", ((0, 0), (4, 0), (8, 0), (float("nan"), 0))),
    ("reference_xy", ((0, 0), (4, 0), (8, 0), (8, 0))),
])
def test_forged_proof_rejected(field, value):
    p = provider()
    chunk(p)
    with pytest.raises(ValueError):
        replace(p.request(60, 7), **{field: value})


def test_schema_cannot_omit_or_add_fields():
    p = provider()
    chunk(p)
    data = p.request(60, 7).to_dict()
    data.pop("version")
    with pytest.raises(ValueError):
        MotionAcquisitionProof.from_dict(data)
    data["version"] = "observed-motion-acquisition:v1"
    data["physical_contact"] = True
    with pytest.raises(ValueError):
        MotionAcquisitionProof.from_dict(data)


@pytest.mark.parametrize("kwargs", [
    {"minimum_motion_px_per_frame": 0, "maximum_age_frames": 60},
    {"minimum_motion_px_per_frame": True, "maximum_age_frames": 60},
    {"minimum_motion_px_per_frame": float("nan"), "maximum_age_frames": 60},
    {"minimum_motion_px_per_frame": 3, "maximum_age_frames": True},
    {"minimum_motion_px_per_frame": 3, "maximum_age_frames": 0},
])
def test_configuration_requires_explicit_existing_finite_bounds(kwargs):
    with pytest.raises(ValueError):
        ObservedMotionAcquisition(**kwargs)


def test_long_running_state_remains_bounded_and_has_no_participant_format_authority():
    p = provider()
    for start in range(0, 6000, 60):
        for frame in range(start, start + 60):
            sample(p, frame, (4.0 * frame, 0.0))
        p.complete_chunk(start, start + 59)
        assert len(p._run) == 4
        assert len(p.request(start + 60, 7).source_frames) == 4


@pytest.mark.parametrize("start,last_motion,epoch", [(13440, 13491, (4 << 32) | 29),
                                                    (25620, 25678, (11 << 32) | 44)])
def test_documented_chunk_timeline_requests_configured_rates_at_start_only(start, last_motion, epoch):
    # Timing regression only: coordinates here are synthetic, not video labels.
    p = provider()
    chunk(p, start=start, end=start + 59, moving_end=last_motion, epoch=epoch)
    proof = p.request(start + 60, epoch)
    assert proof.source_frames == tuple(range(last_motion - 3, last_motion + 1))
    assert proof.decision_frame - proof.source_frames[-1] in (9, 2)
    # This is a chunk-start lease, not an assertion that every later frame moves.
    assert proof.decision_frame == start + 60
    assert proof.completed_chunk_end < proof.decision_frame
    assert p.request(start + 60, epoch) == proof


def test_invalid_selected_coordinate_never_advances_or_clears_valid_state():
    p = provider()
    chunk(p)
    for point in ((float("nan"), 0), (0, float("inf")), (True, 0), (0,)):
        with pytest.raises(ValueError, match="finite pixel"):
            sample(p, 60, point)
    assert p.request(60, 7).source_frames == (48, 49, 50, 51)


def test_reference_basis_may_contain_negative_registered_coordinates():
    p = provider()
    for frame in range(4):
        sample(p, frame, (-100 + 4 * frame, -50.0))
    p.complete_chunk(0, 3)
    proof = p.request(4, 7)
    assert proof.reference_xy[0] == (-100.0, -50.0)


def test_source_run_spanning_chunks_remains_causal_and_does_not_require_future_data():
    p = provider()
    for frame in range(2):
        sample(p, frame, (4.0 * frame, 0.0))
    p.complete_chunk(0, 1)
    assert p.request(2, 7) is None
    for frame in range(2, 4):
        sample(p, frame, (4.0 * frame, 0.0))
    p.complete_chunk(2, 3)
    assert p.request(4, 7).source_frames == (0, 1, 2, 3)
