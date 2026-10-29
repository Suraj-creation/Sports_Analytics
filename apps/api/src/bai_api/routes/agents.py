"""Ask the match: grounded Q&A over the event store (closed API models or a local LLM)."""

from __future__ import annotations

import asyncio
import functools
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import asdict
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from bai_agents.agent import Answer, answer
from bai_agents.providers import LLMError, LLMProvider, make_provider
from bai_agents.tools import ToolContext
from bai_api.deps import Repo, SessionDep

router = APIRouter(prefix="/api/sessions", tags=["agents"])


@functools.cache
def _provider() -> LLMProvider | None:
    try:
        return make_provider()
    except (LLMError, ImportError) as e:
        import structlog

        structlog.get_logger(__name__).warning("agents.provider_unavailable", error=str(e))
        return None


class Ask(BaseModel):
    question: str = Field(min_length=1, max_length=1000)
    history: list[dict[str, str]] = Field(default_factory=list, max_length=12)


@router.post("/{session_id}/ask")
async def ask(session: SessionDep, body: Ask, r: Repo) -> dict[str, Any]:
    ctx = ToolContext(session=session, store=r.events(session.session_id), tracks=r.tracks(session.session_id))
    revision = int(session.meta.get("analysis_revision", 0))

    class AnalysisChangedError(Exception):
        pass

    @contextmanager
    def read_scope() -> Iterator[None]:
        with r.analysis_snapshot(session.session_id) as (current, store, tracks):
            if int(current.meta.get("analysis_revision", 0)) != revision:
                raise AnalysisChangedError
            ctx.session, ctx.store, ctx.tracks = current, store, tracks
            yield

    ctx.read_scope = read_scope
    history = [
        {"role": h["role"], "content": h["content"]}
        for h in body.history
        if h.get("role") in ("user", "assistant") and isinstance(h.get("content"), str)
    ]
    try:
        a = await asyncio.to_thread(answer, body.question, ctx, _provider(), history)
        out = asdict(a)
        # A slow model request must not publish claims from a replaced analysis.
        with read_scope():
            for c in out["citations"]:
                if c["kind"] == "ev":
                    ev = ctx.store.get(c["ref"])
                    if ev is not None:
                        c.update({"frame": ev.frame_start, "type": ev.type})
        out["analysis_revision"] = revision
        return out
    except (AnalysisChangedError, KeyError):
        return asdict(
            Answer(
                text="The analysis changed while I was answering. Please ask again using the updated results.",
                citations=[],
                grounded=False,
                issues=["analysis changed during answer"],
            )
        )


@router.get("/{session_id}/ask/provider")
def provider_info(session: SessionDep) -> dict[str, Any]:
    p = _provider()
    return {"available": p is not None, "provider": p.name if p else None, "model": p.model if p else None}
