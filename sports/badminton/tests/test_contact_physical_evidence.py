"""Physical reliability contracts; controlled fixtures are not reviewed hit labels."""

from dataclasses import FrozenInstanceError, replace

import pytest

from bai_badminton.events.contact_evidence import (
    ContactEvidenceInputs,
    ContactMotionEvidence,
    ContactReview,
    Reliability,
    assess_contact_evidence,
)


def inputs(**changes):
    motion = ContactMotionEvidence(
        before_frames=(97, 98, 99, 100),
        after_frames=(100, 101, 102, 103),
        speed_before=12.0,
        speed_after=14.0,
        spatial_sigma_px=0.7,
        incoming_direction_support=0.9,
        outgoing_direction_support=0.9,
        redirect_support=0.9,
        speed_gain_support=0.0,
    )
    base = ContactEvidenceInputs(
        frame=100,
        available_through=103,
        context_start=96,
        context_stop=104,
        provider="controlled_contact_provider",
        motion=motion,
        observation_status="fresh_observed",
        association_status="tracked",
        context_valid=True,
        player_observed=True,
        pose_observed=True,
        racket_observed=False,
        proximity_support=0.8,
        swing_support=0.8,
        racket_overlap_support=None,
        attribution_target="episode-4",
        attribution_reason="nearest_proximity",
    )
    return replace(base, **changes)


def test_automatic_supported_impact_is_probable_never_confirmed():
    evidence = assess_contact_evidence(inputs())
    assert evidence.trajectory.reliability is Reliability.PROBABLE
    assert evidence.impact.reliability is Reliability.PROBABLE
    assert evidence.attribution.reliability is Reliability.PROBABLE
    assert evidence.score_semantics == "uncalibrated_heuristic_support"


def test_ledger_finality_has_no_input_to_physical_assessment():
    assert "status" not in ContactEvidenceInputs.__dataclass_fields__
    assert "event_status" not in ContactEvidenceInputs.__dataclass_fields__
    assert assess_contact_evidence(inputs()).impact.reliability is not Reliability.CONFIRMED


def test_legacy_provenance_remains_unknown_even_with_high_motion_scores():
    result = assess_contact_evidence(inputs(observation_status=None, association_status=None, player_observed=None))
    assert result.impact.reliability is Reliability.INSUFFICIENT
    assert "observation_provenance_unknown" in result.impact.reasons


@pytest.mark.parametrize("status", ["missing", "reconstructed", "stale", "carried", "occluded", "out_of_view"])
def test_unobserved_points_cannot_establish_physical_contact(status):
    result = assess_contact_evidence(inputs(observation_status=status))
    assert result.impact.reliability is Reliability.INSUFFICIENT


@pytest.mark.parametrize("status", ["invalid", "rejected"])
def test_rejected_observation_rejects_candidate_evidence(status):
    result = assess_contact_evidence(inputs(observation_status=status))
    assert result.impact.reliability is Reliability.REJECTED


def test_body_proximity_and_trajectory_change_alone_remain_ambiguous():
    result = assess_contact_evidence(inputs(pose_observed=False, swing_support=None))
    assert result.trajectory.reliability is Reliability.PROBABLE
    assert result.impact.reliability is Reliability.AMBIGUOUS
    assert "no_fresh_swing_or_racket_overlap" in result.impact.reasons


def test_racket_box_observation_without_overlap_does_not_confirm_impact():
    result = assess_contact_evidence(
        inputs(pose_observed=False, swing_support=None, racket_observed=True, racket_overlap_support=0.0)
    )
    assert result.impact.reliability is Reliability.AMBIGUOUS


def test_fresh_geometric_overlap_supports_probable_not_confirmed_contact():
    result = assess_contact_evidence(
        inputs(pose_observed=False, swing_support=None, racket_observed=True, racket_overlap_support=0.8)
    )
    assert result.impact.reliability is Reliability.PROBABLE


def test_stale_equipment_and_pose_cannot_be_independent_confirmation():
    result = assess_contact_evidence(inputs(pose_observed=False, racket_observed=False, racket_overlap_support=1.0))
    assert result.impact.reliability is Reliability.AMBIGUOUS


def test_zero_incoming_weak_serve_is_supported_by_coherent_launch_and_fresh_swing():
    base = inputs(association_status="static_candidate")
    motion = replace(
        base.motion,
        speed_before=0.0,
        speed_after=2.0,
        incoming_direction_support=0.0,
        outgoing_direction_support=0.4,
        redirect_support=0.0,
        speed_gain_support=0.3,
    )
    result = assess_contact_evidence(replace(base, motion=motion))
    assert result.impact.reliability is Reliability.PROBABLE
    assert "supported_launch" in result.trajectory.reasons


def test_static_to_airborne_switch_without_fresh_contact_cue_is_ambiguous():
    base = inputs(association_status="static_candidate", pose_observed=False, swing_support=None)
    motion = replace(
        base.motion,
        speed_before=0.1247,
        speed_after=122.1241,
        incoming_direction_support=0.0,
        outgoing_direction_support=0.0,
        redirect_support=0.0,
        speed_gain_support=0.0,
    )
    result = assess_contact_evidence(replace(base, motion=motion))
    assert result.impact.reliability is Reliability.AMBIGUOUS
    assert result.trajectory.reliability is Reliability.AMBIGUOUS
    assert "static_candidate_without_independent_contact_cue" in result.impact.reasons


@pytest.mark.parametrize("association", ["reacquisition", "ambiguous", "unknown", None])
def test_unresolved_association_is_not_repaired_by_large_motion_score(association):
    result = assess_contact_evidence(inputs(association_status=association))
    assert result.impact.reliability is Reliability.AMBIGUOUS


def test_scene_invalidity_rejects_candidate_without_claiming_no_real_hit():
    result = assess_contact_evidence(inputs(context_valid=False))
    assert result.impact.reliability is Reliability.REJECTED
    assert result.impact.reasons == ("invalid_temporal_context",)


def test_doubles_attribution_ambiguity_does_not_erase_supported_impact():
    result = assess_contact_evidence(inputs(attribution_target=None, attribution_reason="ambiguous_proximity"))
    assert result.impact.reliability is Reliability.PROBABLE
    assert result.attribution.reliability is Reliability.AMBIGUOUS
    assert result.inputs.attribution_target is None


def test_no_declared_spatial_sensitivity_is_not_precise_motion_evidence():
    base = inputs()
    result = assess_contact_evidence(replace(base, motion=replace(base.motion, spatial_sigma_px=None)))
    assert result.trajectory.reliability is Reliability.INSUFFICIENT
    assert result.impact.reliability is Reliability.AMBIGUOUS


def test_review_is_separate_source_bound_physical_evidence():
    review = ContactReview(
        frame=100,
        source_sha256="a" * 64,
        reviewer="controlled-test-fixture",
        review_id="fixture-review",
        physical_impact=True,
    )
    result = assess_contact_evidence(inputs(review=review))
    assert result.impact.reliability is Reliability.CONFIRMED
    assert result.attribution.reliability is Reliability.PROBABLE
    assert "source_bound_external_review" in result.impact.reasons


def test_negative_review_does_not_erase_observed_trajectory_turn():
    review = ContactReview(
        frame=100,
        source_sha256="b" * 64,
        reviewer="controlled-test-fixture",
        review_id="fixture-negative",
        physical_impact=False,
    )
    result = assess_contact_evidence(inputs(review=review))
    assert result.impact.reliability is Reliability.REJECTED
    assert result.trajectory.reliability is Reliability.PROBABLE


def test_review_from_another_frame_cannot_confirm_this_candidate():
    with pytest.raises(ValueError, match="review"):
        inputs(
            review=ContactReview(
                frame=99, source_sha256="a" * 64, reviewer="fixture", review_id="fixture", physical_impact=True
            )
        )


def test_confirmed_status_cannot_be_constructed_from_ledger_or_model_support():
    from bai_badminton.events.contact_evidence import ReliabilityAssessment

    evidence = assess_contact_evidence(inputs())
    with pytest.raises(ValueError, match="external review"):
        replace(evidence, impact=ReliabilityAssessment(Reliability.CONFIRMED, ("ledger_finalized",)))


def test_smooth_apex_with_player_motion_does_not_establish_physical_impact():
    base = inputs()
    motion = replace(base.motion, redirect_support=0.0, speed_gain_support=0.0)
    result = assess_contact_evidence(replace(base, motion=motion))
    assert result.impact.reliability is Reliability.AMBIGUOUS
    assert result.trajectory.reliability is Reliability.INSUFFICIENT


@pytest.mark.parametrize("field", ["incoming_direction_support", "outgoing_direction_support", "redirect_support"])
def test_quantization_unresolved_direction_cannot_support_turn(field):
    base = inputs()
    result = assess_contact_evidence(replace(base, motion=replace(base.motion, **{field: 0.0})))
    assert result.impact.reliability is Reliability.AMBIGUOUS


def test_model_support_is_not_a_calibrated_physical_probability():
    assert "raw_model_support" not in ContactEvidenceInputs.__dataclass_fields__
    assert "probability" not in ContactEvidenceInputs.__dataclass_fields__
    assert assess_contact_evidence(inputs()).score_semantics == "uncalibrated_heuristic_support"


@pytest.mark.parametrize("changes", [{"available_through": 102}, {"context_stop": 103}, {"context_start": 98}])
def test_future_or_outside_context_samples_are_rejected(changes):
    with pytest.raises(ValueError, match="sample"):
        inputs(**changes)


def test_evidence_is_immutable_and_json_serializable():
    import json

    result = assess_contact_evidence(inputs())
    with pytest.raises(FrozenInstanceError):
        result.policy = "changed"
    encoded = json.loads(json.dumps(result.to_payload(), allow_nan=False))
    assert encoded["impact"]["reliability"] == "probable"
    assert encoded["schema"] == "badminton-contact-evidence:v1"


def _window(*, before=(12.0, -2.0), after=(-14.0, 3.0), scale=1.0):
    import numpy as np

    from bai_badminton.observations import PlayerSeries, WindowObs
    from bai_badminton.perception.shuttle_post import Track

    xy = np.asarray([np.asarray(before) * (i - 4) if i <= 4 else np.asarray(after) * (i - 4) for i in range(9)]) * scale
    player = PlayerSeries.empty(9)
    player.bbox[:] = np.asarray([-10, -15, 10, 85]) * scale
    return WindowObs(96, 30.0, Track.from_arrays(xy[:, 0], xy[:, 1], np.ones(9, bool)), {"episode-4": player})


def test_candidate_evidence_is_additive_and_preserves_legacy_support():
    import bai_badminton.events.contact as contact

    w = _window()
    kept = contact.detect_contacts(w, enforce_alternation=False)
    # Existing legacy ratio scoring selects 101 on this controlled flight.
    # The explanation must preserve that numerical selection.
    assert [c.frame for c in kept] == [101]
    original = contact.score_frame(w, 5)
    assert kept[0].p == original.p
    assert kept[0].scores == original.scores
    assert kept[0].shuttle_xy == original.shuttle_xy
    assert kept[0].model == original.model
    assert kept[0].evidence.impact.reliability is Reliability.INSUFFICIENT
    assert kept[0].evidence.inputs.motion.spatial_sigma_px is None


def test_diagnostic_sensitivity_does_not_replace_selected_legacy_contact_model():
    import bai_badminton.events.contact as contact

    w = _window(before=(0.02, 0), after=(-0.6, 0))
    candidate = contact.score_frame(w, 4)
    evidence = contact.build_contact_evidence(w, candidate, motion_reliability=contact.ContactMotionReliability(0.7))
    assert candidate.p > 0.97
    assert candidate.model == contact.CONTACT_MODEL
    assert evidence.inputs.provider == contact.CONTACT_MODEL
    assert evidence.inputs.motion.redirect_support == 0.0
    assert evidence.inputs.motion.speed_gain_support == 0.0


def test_evidence_consumes_only_bounded_same_scene_samples():
    import bai_badminton.events.contact as contact

    w = _window()
    w.break_before[6] = True
    candidate = contact.score_frame(w, 4)
    evidence = contact.build_contact_evidence(w, candidate, motion_reliability=contact.ContactMotionReliability(0.7))
    assert evidence.inputs.motion.after_frames == (100, 101)
    assert evidence.inputs.context_stop == 102
    assert evidence.inputs.available_through == 101


def test_evidence_keeps_missing_samples_missing():
    import bai_badminton.events.contact as contact

    w = _window()
    w.shuttle.vis[5] = False
    w.shuttle.interp[6] = True
    candidate = contact.score_frame(w, 4)
    evidence = contact.build_contact_evidence(w, candidate)
    assert evidence.inputs.motion.after_frames == (100, 103)


@pytest.mark.parametrize("scale", [0.5, 1.0, 1.5, 2.0])
def test_evidence_sensitivity_uses_declared_image_scale(scale):
    import bai_badminton.events.contact as contact

    def evidence(size):
        w = _window(scale=size)
        return contact.build_contact_evidence(
            w, contact.score_frame(w, 4), motion_reliability=contact.ContactMotionReliability(0.7 * size)
        )

    base, scaled = evidence(1.0).inputs.motion, evidence(scale).inputs.motion
    assert scaled.incoming_direction_support == pytest.approx(base.incoming_direction_support)
    assert scaled.outgoing_direction_support == pytest.approx(base.outgoing_direction_support)
    assert scaled.redirect_support == pytest.approx(base.redirect_support)
    assert scaled.speed_gain_support == pytest.approx(base.speed_gain_support)


def test_partitioned_nms_preserves_evidence_frame_identity():
    import bai_badminton.events.contact as contact

    w = _window()
    kwargs = {"enforce_alternation": False, "motion_reliability": contact.ContactMotionReliability(0.7)}
    whole = contact.detect_contacts(w, **kwargs)
    split = contact.detect_contacts(w, start=0, stop=4, **kwargs) + contact.detect_contacts(w, start=4, **kwargs)
    assert whole[0].evidence == split[0].evidence
    assert whole[0].evidence.inputs.frame == whole[0].frame == 100
