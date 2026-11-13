"""Explicit controlled-provider evidence for classification contract fixtures.

These are synthetic declared observations, not reviewed real-video labels. Keep
endpoint reliability separate from the hitter geometry being tested.
"""

from bai_badminton.events.contact import ContactCandidate
from bai_badminton.events.contact_evidence import (
    ContactEvidenceInputs,
    ContactMotionEvidence,
    assess_contact_evidence,
)


def supported_endpoint(frame=35):
    inputs = ContactEvidenceInputs(
        frame=frame,
        available_through=frame + 2,
        context_start=frame - 2,
        context_stop=frame + 3,
        provider="controlled_synthetic_endpoint",
        motion=ContactMotionEvidence(
            before_frames=(frame - 2, frame - 1, frame),
            after_frames=(frame, frame + 1, frame + 2),
            speed_before=10.0,
            speed_after=10.0,
            spatial_sigma_px=0.5,
            incoming_direction_support=0.9,
            outgoing_direction_support=0.9,
            redirect_support=0.9,
        ),
        observation_status="fresh_observed",
        association_status="tracked",
        context_valid=True,
        player_observed=True,
        pose_observed=True,
        swing_support=0.8,
        proximity_support=0.8,
    )
    return ContactCandidate(frame=frame, player_id=None, p=0.9, evidence=assess_contact_evidence(inputs))


def endpoint_position(frame, endpoint=35):
    """The declared synthetic endpoint has observed incoming/outgoing segments."""
    if endpoint - 2 <= frame <= endpoint:
        return (100.0 + 10.0 * (frame - endpoint), 100.0)
    if endpoint < frame <= endpoint + 2:
        return (100.0, 100.0 + 10.0 * (frame - endpoint))
    return None
