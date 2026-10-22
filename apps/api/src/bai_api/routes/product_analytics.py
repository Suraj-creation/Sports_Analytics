"""Authorized product projections; all numerical derivations stay on the server."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Query, Request

from bai_api.deps import Repo, SessionDep, User
from bai_api.product_analytics import Overview, insights, overview

router = APIRouter(tags=["product analytics"])


@router.get("/api/analytics/overview", response_model=Overview)
def product_overview(
    r: Repo,
    _: User,
    request: Request,
    limit: Annotated[int, Query(ge=1, le=500)] = 500,
) -> Overview:
    return overview(r, request.app.state.analytics, limit)


@router.get("/api/sessions/{session_id}/insights")
def session_insights(session: SessionDep, r: Repo, request: Request) -> dict[str, Any]:
    return insights(r, request.app.state.analytics, session)
