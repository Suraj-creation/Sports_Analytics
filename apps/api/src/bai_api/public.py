"""Network response projections; persistence retains the authoritative source URI."""

from __future__ import annotations

from typing import Any

from bai_engine.schema import Session, SessionStatus

PUBLIC_FAILURE_DETAIL = (
    "Analysis stopped before completion. Review the recording and try again. "
    "Detailed diagnostics are retained on the server."
)


def public_status_message(message: dict[str, Any]) -> dict[str, Any]:
    """Project live failure messages without mutating the internal bus payload."""
    if message.get("type") == "status" and message.get("status") == SessionStatus.FAILED:
        return {**message, "detail": PUBLIC_FAILURE_DETAIL}
    return message


def public_session(session: Session) -> Session:
    """Media is accessed by session ID through authorized routes, never filesystem URIs."""
    return session.model_copy(
        update={
            "source": session.source.model_copy(update={"uri": ""}),
            "status_detail": PUBLIC_FAILURE_DETAIL if session.status == SessionStatus.FAILED else session.status_detail,
        }
    )
