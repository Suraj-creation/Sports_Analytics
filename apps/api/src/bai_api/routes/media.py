"""HLS playback and scrubber sprites (the browser plays exactly the frames the engine analyses)."""

from __future__ import annotations

import re

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse, Response

from bai_api.deps import Repo, SessionDep

router = APIRouter(prefix="/api/sessions", tags=["media"])

_HLS_NAME = re.compile(r"^(index\.m3u8|init\.mp4|seg_\d{5}\.m4s)$")
_SPRITE_NAME = re.compile(r"^(sprite_\d{3}\.jpg|sprite\.json)$")


def _media(session, r):  # type: ignore[no-untyped-def]
    if not session.source.sha256:
        raise HTTPException(status.HTTP_409_CONFLICT, "The video is still downloading")
    return r.media_paths(session.source.sha256)


@router.get("/{session_id}/hls/{name}")
def hls(session: SessionDep, name: str, r: Repo) -> Response:
    if not _HLS_NAME.match(name):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    mp = _media(session, r)
    f = mp.hls / name
    if not f.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not ready yet")
    if name.endswith(".m3u8"):
        # event playlists grow while transcoding — never cache them
        return Response(
            f.read_text(encoding="utf-8"),
            media_type="application/vnd.apple.mpegurl",
            headers={"Cache-Control": "no-cache"},
        )
    media_type = "video/mp4" if name.endswith(".mp4") else "video/iso.segment"
    return FileResponse(f, media_type=media_type, headers={"Cache-Control": "public, max-age=31536000, immutable"})


@router.get("/{session_id}/sprite/{name}")
def sprite(session: SessionDep, name: str, r: Repo) -> FileResponse:
    if not _SPRITE_NAME.match(name):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not found")
    f = _media(session, r).root / name
    if not f.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Thumbnails are not ready yet")
    return FileResponse(f)


@router.get("/{session_id}/proxy.mp4")
def proxy(session: SessionDep, r: Repo) -> FileResponse:
    f = _media(session, r).proxy
    if not f.exists():
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Not ready yet")
    return FileResponse(f, media_type="video/mp4")
