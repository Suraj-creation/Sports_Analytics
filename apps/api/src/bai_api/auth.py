"""Single-user authentication.

* Loopback-only deployments (the default, ``BAI_BIND_HOST=127.0.0.1``) may run without a
  passphrase: only the local user can reach the server.
* Any non-loopback bind **requires** ``BAI_PASSPHRASE``; the server refuses to start otherwise.
* Login sets an HttpOnly, SameSite=Strict signed cookie.  Unsafe methods additionally require the
  ``X-CSRF-Token`` header matching the cookie-bound token (double submit), so a malicious page on
  another origin cannot drive the API through the user's browser.
"""

from __future__ import annotations

import hmac
import secrets
import time
from typing import Annotated

from fastapi import Cookie, Depends, Header, HTTPException, Request, WebSocket, status
from itsdangerous import BadSignature, URLSafeTimedSerializer

from bai_engine.config import Settings

COOKIE = "bai_session"
MAX_AGE_S = 14 * 24 * 3600
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


class Auth:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.enabled = settings.passphrase is not None and bool(settings.passphrase.get_secret_value())
        if not settings.is_loopback and not self.enabled:
            raise RuntimeError("BAI_PASSPHRASE is required when binding to a non-loopback address")
        self._ser = URLSafeTimedSerializer(settings.session_secret.get_secret_value(), salt="bai-auth")
        self._failures: list[float] = []

    # ------------------------------------------------------------------ tokens
    def issue(self) -> tuple[str, str]:
        csrf = secrets.token_urlsafe(24)
        return self._ser.dumps({"u": "local", "csrf": csrf}), csrf

    def verify_cookie(self, token: str | None) -> dict[str, str] | None:
        if not token:
            return None
        try:
            data = self._ser.loads(token, max_age=MAX_AGE_S)
        except BadSignature:
            return None
        return data if isinstance(data, dict) else None

    def check_passphrase(self, given: str) -> bool:
        now = time.monotonic()
        self._failures = [t for t in self._failures if now - t < 300]
        if len(self._failures) >= 10:  # brute-force throttle: 10 failures / 5 min
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "Too many attempts; try again in a few minutes")
        assert self.settings.passphrase is not None
        ok = hmac.compare_digest(given.encode(), self.settings.passphrase.get_secret_value().encode())
        if not ok:
            self._failures.append(now)
        return ok


def get_auth(request: Request) -> Auth:
    auth = request.app.state.auth
    assert isinstance(auth, Auth)
    return auth


def require_user(
    request: Request,
    auth: Annotated[Auth, Depends(get_auth)],
    bai_session: Annotated[str | None, Cookie()] = None,
    x_csrf_token: Annotated[str | None, Header()] = None,
) -> str:
    if not auth.enabled:
        return "local"
    data = auth.verify_cookie(bai_session)
    if data is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Sign in to continue")
    if request.method not in SAFE_METHODS and not (x_csrf_token and hmac.compare_digest(x_csrf_token, data["csrf"])):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Missing or invalid CSRF token")
    return data["u"]


def ws_user(ws: WebSocket) -> str | None:
    auth: Auth = ws.app.state.auth
    if not auth.enabled:
        return "local"
    data = auth.verify_cookie(ws.cookies.get(COOKIE))
    return None if data is None else data["u"]
