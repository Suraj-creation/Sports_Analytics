"""Provisional track-episode evidence for an existing shuttle-contact hypothesis.

Episode IDs are not durable session player IDs. The proximity policy is an
uncalibrated cue; this module never promotes its output to a named player.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from bai_badminton.court import HALF_LEN, WIDTH_DOUBLES
from bai_badminton.events.contact import ATTRIBUTION_POLICY, score_frame
from bai_badminton.observations import PlayerSeries, WindowObs


@dataclass(frozen=True)
class ParticipantSnapshot:
    track_id: int
    bbox: NDArray[np.float64]
    kps: NDArray[np.float64] | None
    court_xy: tuple[float, float] | None
    observation_id: str | None = None
    # Frame-level detector execution, not evidence that this person was matched.
    detector_observed: bool | None = None
    detector_matched: bool | None = None


def has_target_court_provenance(snapshot: ParticipantSnapshot) -> bool:
    """Check current episode provenance and the selected-court runoff bounds."""
    court = snapshot.court_xy
    return bool(
        snapshot.observation_id
        and court is not None
        and len(court) == 2
        and np.isfinite(court).all()
        and abs(court[0]) <= WIDTH_DOUBLES / 2 + 0.35
        and abs(court[1]) <= HALF_LEN + 0.75
    )


def participant_window(
    window: WindowObs, frames: list[dict[str, ParticipantSnapshot]], *, restrict_target_court: bool = False
) -> WindowObs:
    """Build temporal series for each provisional episode, not a named roster person.

    The restricted path uses the same court-plus-runoff bounds as CourtROI and
    requires a current birth-event ID. No geometry is evidence of no candidate.
    """
    if len(frames) != window.n:
        raise ValueError("participant observations must align with the window")

    def usable(snapshot: ParticipantSnapshot) -> bool:
        if not restrict_target_court:
            return True
        return has_target_court_provenance(snapshot)

    track_ids: dict[str, set[int]] = {}
    births: dict[str, set[str | None]] = {}
    for frame in frames:
        for participant_id, snapshot in frame.items():
            if usable(snapshot):
                track_ids.setdefault(participant_id, set()).add(snapshot.track_id)
                births.setdefault(participant_id, set()).add(snapshot.observation_id)
    series = {
        participant_id: PlayerSeries.empty(window.n)
        for participant_id, ids in track_ids.items()
        if len(ids) == 1 and (not restrict_target_court or len(births[participant_id]) == 1)
    }
    for i, frame in enumerate(frames):
        for participant_id, snapshot in frame.items():
            item = series.get(participant_id)
            if item is None or not usable(snapshot):
                continue
            item.bbox[i] = snapshot.bbox
            if snapshot.kps is not None:
                item.kps[i] = snapshot.kps
            if snapshot.court_xy is not None:
                item.court_xy[i] = snapshot.court_xy
    return WindowObs(
        frame0=window.frame0,
        fps=window.fps,
        shuttle=window.shuttle,
        players=series,
        replay=window.replay,
        pose_stride=window.pose_stride,
    )


def participant_contact_evidence(
    window: WindowObs,
    frames: list[dict[str, ParticipantSnapshot]],
    index: int,
    *,
    restrict_target_court: bool = False,
) -> dict[str, Any]:
    """Score only episodes observed at this frame; never link across track IDs.

    Returns a provisional track hypothesis or an explicitly unresolved result.
    Input frames must be aligned to the supplied shuttle observation window.
    """
    if len(frames) != window.n or not 0 <= index < window.n:
        raise ValueError("participant observations must align with the window")
    active = frames[index]
    visual = participant_window(window, frames, restrict_target_court=restrict_target_court)
    candidate = score_frame(visual, index)
    if candidate is None:
        return {
            "status": "unresolved",
            "participant_id": None,
            "track_id": None,
            "observation_id": None,
            "reason": "insufficient_shuttle_trajectory",
            "policy": ATTRIBUTION_POLICY,
            "components": {},
        }
    participant_id = candidate.player_id
    unmatched = participant_id is not None and active[participant_id].detector_matched is False
    if unmatched:
        participant_id = None
    return {
        "status": "provisional" if participant_id is not None else "unresolved",
        "participant_id": participant_id,
        "track_id": active[participant_id].track_id if participant_id is not None else None,
        "observation_id": active[participant_id].observation_id if participant_id is not None else None,
        "reason": "player_not_detector_matched" if unmatched else candidate.attribution_reason,
        "policy": ATTRIBUTION_POLICY,
        "components": candidate.components,
    }
