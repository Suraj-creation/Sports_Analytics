"""Network response projections; persistence retains the authoritative source URI."""

from __future__ import annotations

from bai_engine.schema import Session


def public_session(session: Session) -> Session:
    """Media is accessed by session ID through authorized routes, never filesystem URIs."""
    return session.model_copy(update={"source": session.source.model_copy(update={"uri": ""})})
