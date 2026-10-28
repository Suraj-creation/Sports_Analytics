"""Bounded provisional movement of anonymous visual track episodes."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from bai_api.deps import Repo, SessionDep
from bai_badminton.analytics.episode_movement import build_episode_movement

router = APIRouter(prefix="/api/sessions", tags=["episode movement"])


@router.get("/{session_id}/episode-movement")
def episode_movement(
    session: SessionDep,
    r: Repo,
    frame_from: Annotated[int, Query(alias="from", ge=0)],
    frame_to: Annotated[int, Query(alias="to", ge=0)],
) -> dict:
    media = session.media
    if media is None or media.n_frames <= 0 or media.fps_num <= 0 or media.fps_den <= 0:
        raise HTTPException(status.HTTP_409_CONFLICT, "Video timeline is not available")
    try:
        return build_episode_movement(
            r.events(session.session_id),
            r.tracks(session.session_id),
            start_frame=frame_from,
            end_frame=frame_to,
            max_frame=media.n_frames - 1,
            fps=float(media.fps),
            frame_width=media.width,
            frame_height=media.height,
        )
    except ValueError as exc:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(exc)) from exc
