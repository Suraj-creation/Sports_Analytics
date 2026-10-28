"""Heuristic estimates are separate from reviewed participant analytics."""

from fastapi import APIRouter, HTTPException, status

from bai_api.deps import Repo, SessionDep
from bai_badminton.analytics.automatic_individual import build_estimated_individual_analytics

router = APIRouter(prefix="/api/sessions", tags=["estimated individual analytics"])


@router.get("/{session_id}/estimated-individual-analytics")
def estimated_individual_analytics(session: SessionDep, r: Repo, include_events: bool = False) -> dict:
    if (
        session.media is None
        or session.media.n_frames <= 0
        or session.media.fps_num <= 0
        or session.media.fps_den <= 0
        or session.media.width <= 0
        or session.media.height <= 0
    ):
        raise HTTPException(status.HTTP_409_CONFLICT, "Video timeline is not available")
    return build_estimated_individual_analytics(
        r.events(session.session_id),
        r.tracks(session.session_id),
        session.roster,
        max_frame=session.media.n_frames - 1,
        fps=float(session.media.fps),
        frame_width=session.media.width,
        frame_height=session.media.height,
        include_events=include_events,
    )
