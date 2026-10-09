from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from pydantic import BaseModel

from bai_api.auth import COOKIE, MAX_AGE_S, Auth, get_auth

router = APIRouter(prefix="/api/auth", tags=["auth"])


class Login(BaseModel):
    passphrase: str


@router.get("/me")
def me(
    auth: Annotated[Auth, Depends(get_auth)], bai_session: Annotated[str | None, Cookie()] = None
) -> dict[str, object]:
    if not auth.enabled:
        return {"authenticated": True, "auth_required": False, "csrf": None}
    data = auth.verify_cookie(bai_session)
    return {"authenticated": data is not None, "auth_required": True, "csrf": data["csrf"] if data else None}


@router.post("/login")
def login(body: Login, response: Response, auth: Annotated[Auth, Depends(get_auth)]) -> dict[str, object]:
    if not auth.enabled:
        return {"authenticated": True, "csrf": None}
    if not auth.check_passphrase(body.passphrase):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "That passphrase is not correct")
    token, csrf = auth.issue()
    response.set_cookie(
        COOKIE, token, max_age=MAX_AGE_S, httponly=True, samesite="strict", secure=not auth.settings.is_loopback
    )
    return {"authenticated": True, "csrf": csrf}


@router.post("/logout")
def logout(response: Response) -> dict[str, bool]:
    response.delete_cookie(COOKIE)
    return {"ok": True}
