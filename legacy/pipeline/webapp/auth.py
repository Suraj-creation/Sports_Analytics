"""
auth.py
-------
Session-cookie auth for the webapp. Simple local accounts (admin +
interns) -- this is an internal LAN tool, not internet-facing, so
werkzeug's password hashing + Flask's signed session cookie is sufficient
without pulling in an external identity provider.
"""
import os
from functools import wraps
from pathlib import Path

from flask import abort, jsonify, redirect, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import db

_SECRET_KEY_PATH = Path(__file__).resolve().parent / ".secret_key"


def get_secret_key():
    """Stable across restarts so a redeploy doesn't silently log everyone
    out -- read from env first, else a cached random key on disk."""
    env_key = os.environ.get("FLASK_SECRET_KEY")
    if env_key:
        return env_key
    if _SECRET_KEY_PATH.exists():
        return _SECRET_KEY_PATH.read_text().strip()
    key = os.urandom(32).hex()
    _SECRET_KEY_PATH.write_text(key)
    return key


def hash_password(pw):
    return generate_password_hash(pw)


def verify_password(pw, pw_hash):
    return check_password_hash(pw_hash, pw)


def current_user():
    uid = session.get("user_id")
    if uid is None:
        return None
    return db.users_get(uid)


def _is_api_request():
    return request.path.startswith("/api/")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            if _is_api_request():
                abort(401)
            return redirect("/login")
        return view(*args, **kwargs)
    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if session.get("user_id") is None:
            if _is_api_request():
                abort(401)
            return redirect("/login")
        if session.get("role") != "admin":
            abort(403)
        return view(*args, **kwargs)
    return wrapped
