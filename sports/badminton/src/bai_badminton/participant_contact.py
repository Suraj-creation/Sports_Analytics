"""Provisional track-episode evidence for an existing shuttle-contact hypothesis.

Episode IDs are not durable session player IDs. The proximity policy is an
uncalibrated cue; this module never promotes its output to a named player.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from numpy.typing import NDArray

from bai_badminton.events.contact import ATTRIBUTION_POLICY, score_frame
from bai_badminton.observations import PlayerSeries, WindowObs


@dataclass(frozen=True)
class ParticipantSnapshot:
    track_id: int
    bbox: NDArray[np.float64]
    kps: NDArray[np.float64] | None
    court_xy: tuple[float, float] | None


def participant_contact_evidence(
    window: WindowObs, frames: list[dict[str, ParticipantSnapshot]], index: int
) -> dict[str, Any]:
    """Score only episodes observed at this frame; never link across track IDs.

    Returns a provisional track hypothesis or an explicitly unresolved result.
    Input frames must be aligned to the supplied shuttle observation window.
    """
    if len(frames) != window.n or not 0 <= index < window.n:
        raise ValueError("participant observations must align with the window")
    active = frames[index]
    series: dict[str, PlayerSeries] = {}
    for participant_id, current in active.items():
        item = PlayerSeries.empty(window.n)
        for i, frame in enumerate(frames):
            observed = frame.get(participant_id)
            if observed is None or observed.track_id != current.track_id:
                continue
            item.bbox[i] = observed.bbox
            if observed.kps is not None:
                item.kps[i] = observed.kps
            if observed.court_xy is not None:
                item.court_xy[i] = observed.court_xy
        series[participant_id] = item
    visual = WindowObs(
        frame0=window.frame0, fps=window.fps, shuttle=window.shuttle, players=series, replay=window.replay
    )
    candidate = score_frame(visual, index)
    if candidate is None:
        return {
            "status": "unresolved",
            "participant_id": None,
            "track_id": None,
            "reason": "insufficient_shuttle_trajectory",
            "policy": ATTRIBUTION_POLICY,
            "components": {},
        }
    participant_id = candidate.player_id
    return {
        "status": "provisional" if participant_id is not None else "unresolved",
        "participant_id": participant_id,
        "track_id": active[participant_id].track_id if participant_id is not None else None,
        "reason": candidate.attribution_reason,
        "policy": ATTRIBUTION_POLICY,
        "components": candidate.components,
    }
