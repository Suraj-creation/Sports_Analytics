"""Exact-frame anonymous participant evidence for human review."""

from __future__ import annotations

import math
import re

from fastapi import APIRouter, HTTPException, Query, status

from bai_api.deps import Repo, SessionDep
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import EventStatus, TrackObject

router = APIRouter(prefix="/api/sessions", tags=["participant observations"])


@router.get("/{session_id}/participant-observations/{observation_id}/box")
def participant_box(session: SessionDep, observation_id: str, r: Repo, frame: int = Query(ge=0)) -> dict:
    media = session.media
    if (
        media is None
        or media.n_frames <= 0
        or frame >= media.n_frames
        or media.width <= 0
        or media.height <= 0
        or media.fps_num <= 0
        or media.fps_den <= 0
    ):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "A valid in-range media frame is required")
    result = {
        "available": False,
        "frame": frame,
        "bbox": None,
        "video_width": media.width,
        "video_height": media.height,
    }
    store = r.events(session.session_id)
    observations = store.query(types=["participant_observation"])
    obs = next((e for e in observations if e.event_id == observation_id), None)
    if not (
        obs
        and obs.status == EventStatus.PROVISIONAL
        and obs.provenance.model == "participant_tracker_v1"
        and obs.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
        and obs.frame_start <= frame
    ):
        return result
    participant = obs.payload.get("participant_id")
    track = obs.payload.get("track_id")
    if not (
        isinstance(participant, str)
        and re.fullmatch(r"participant-([A-Za-z0-9]+)-[0-9]{6}", participant)
        and isinstance(track, int)
        and not isinstance(track, bool)
        and track >= 0
    ):
        return result
    ledger = IdentityReviewLedger(store, (), max_frame=media.n_frames - 1, fps=media.fps)
    if ledger._episode_error(obs, frame) is not None:
        return result
    # Multiple episode births for the same track at the starting frame are ambiguous.
    if any(
        e.event_id != obs.event_id
        and e.frame_start == obs.frame_start
        and e.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
        and e.payload.get("track_id") == track
        for e in observations
    ):
        return result
    rows = [
        row
        for row in r.tracks(session.session_id).read([TrackObject.PLAYER], frame, frame).to_pylist()
        if row["track_id"] == track
    ]
    if (
        len(rows) != 1
        or rows[0]["visible"] is not True
        or rows[0].get("detector_observed") is not True
        or rows[0]["participant_observation_id"] != obs.event_id
    ):
        return result
    box = rows[0]["bbox"]
    if not (
        box is not None
        and len(box) == 4
        and all(isinstance(v, (int, float)) and math.isfinite(v) for v in box)
        and 0 <= box[0] < box[2] <= media.width
        and 0 <= box[1] < box[3] <= media.height
        and math.isfinite(rows[0]["conf"])
    ):
        return result
    return {**result, "available": True, "bbox": box}
