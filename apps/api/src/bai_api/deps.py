"""Shared FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from bai_api.auth import require_user
from bai_engine.bus import Bus
from bai_engine.config import Settings
from bai_engine.schema import Session
from bai_engine.store import SessionRepository


def repo(request: Request) -> SessionRepository:
    r = request.app.state.repo
    assert isinstance(r, SessionRepository)
    return r


def bus(request: Request) -> Bus:
    b = request.app.state.bus
    assert isinstance(b, Bus)
    return b


def settings(request: Request) -> Settings:
    s = request.app.state.settings
    assert isinstance(s, Settings)
    return s


Repo = Annotated[SessionRepository, Depends(repo)]
BusDep = Annotated[Bus, Depends(bus)]
SettingsDep = Annotated[Settings, Depends(settings)]
User = Annotated[str, Depends(require_user)]


def get_session(session_id: str, r: Repo, _: User) -> Session:
    if not session_id.isalnum() or len(session_id) > 40:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    s = r.get(session_id)
    if s is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Session not found")
    return s


SessionDep = Annotated[Session, Depends(get_session)]
