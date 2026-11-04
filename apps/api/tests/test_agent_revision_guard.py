"""Answer publication must use the same analysis as its tool reads."""

import asyncio
from contextlib import suppress

import pytest

from bai_agents.agent import Answer
from bai_agents.tools import run_tool
from bai_api.routes import agents
from bai_engine.schema import Event, Provenance, Session, Source, SourceKind
from bai_engine.store import SessionRepository


@pytest.mark.parametrize("reset_at", [None, "before_tool", "after_tool"])
async def test_answer_revision_is_checked_at_tool_read_and_publication(tmp_path, monkeypatch, reset_at):
    repo = SessionRepository(tmp_path / "data")
    session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
    event = repo.events(session.session_id).append(Event(
        session_id=session.session_id, type="contact", frame_start=30, frame_end=30,
        pts_us=1_000_000, provenance=Provenance(model="controlled-test"),
    ))
    monkeypatch.setattr(agents, "_provider", lambda: None)

    def answer(question, context, provider, history):
        if reset_at == "before_tool":
            repo.reset_analysis(session.session_id)
        run_tool(context, "match_overview", {})
        if reset_at == "after_tool":
            repo.reset_analysis(session.session_id)
        return Answer(text="Controlled result", citations=[{"kind": "ev", "ref": event.event_id}],
                      grounded=True, issues=[])

    monkeypatch.setattr(agents, "answer", answer)
    # This restricted executor does not reliably wake an idle selector from a
    # worker thread; retain a periodic task while exercising the real to_thread.
    async def heartbeat():
        while True:
            await asyncio.sleep(0.01)

    tick = asyncio.create_task(heartbeat())
    try:
        result = await asyncio.wait_for(agents.ask(session, agents.Ask(question="What happened?"), repo), 5)
        if reset_at is None:
            assert result["grounded"] is True
            assert result["analysis_revision"] == 0
            assert result["citations"] == [{"kind": "ev", "ref": event.event_id,
                                            "frame": 30, "type": "contact"}]
        else:
            assert result["grounded"] is False
            assert result["citations"] == []
            assert result["issues"] == ["analysis changed during answer"]
    finally:
        await asyncio.get_running_loop().shutdown_default_executor()
        tick.cancel()
        with suppress(asyncio.CancelledError):
            await tick
        repo.close()
