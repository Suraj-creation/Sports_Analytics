"""Agent grounding: scripted providers replay the failure modes seen with a local 8B model
(docs/testing/agent_evaluation_results.json) against a real engine-built event log."""

import json
from pathlib import Path
from typing import Any

import pytest

from bai_agents.agent import answer, text_tool_calls, validate
from bai_agents.providers import LLMTurn, ToolCall
from bai_agents.tools import ToolContext, run_tool
from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.perception_types import ChunkPerception
from bai_badminton.testing.synth import broadcast_homography, make_rally, to_frames
from bai_engine.schema import MediaInfo, PlayerInfo, Session, SessionStatus, Source, SourceKind
from bai_engine.store import EventStore

WARM = {"near_xy": (-1.5, -5.6), "far_xy": (-1.5, 5.6)}


@pytest.fixture
def ctx(tmp_path: Path) -> ToolContext:
    def rally(w: str, seed: int, **kw: Any):  # type: ignore[no-untyped-def]
        return make_rally(n_shots=5 if w == "P1" else 4, land_court=(0.5, 4.5 if w == "P1" else -4.5), seed=seed, **kw)

    rallies = [rally("P1", 1, **WARM), rally("P1", 2, lead_in=180), rally("P2", 3), rally("P1", 4)]
    frames = []
    for r in rallies:
        frames.extend(to_frames(r, len(frames)))
    store = EventStore(tmp_path / "e.sqlite", "S1")
    eng = BadmintonMatchEngine("S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store)
    eng.set_calibration(0, broadcast_homography())
    for s in range(0, len(frames), 64):
        part = frames[s : s + 64]
        eng.ingest(ChunkPerception(start=part[0].frame_idx, end=part[-1].frame_idx, frames=part))
    eng.flush()
    session = Session(
        title="t",
        source=Source(kind=SourceKind.UPLOAD, uri="none"),
        status=SessionStatus.ANALYSED,
        players=[PlayerInfo(player_id="P1", name="Axelsen"), PlayerInfo(player_id="P2", name="Lee")],
        media=MediaInfo(
            fps_num=30, fps_den=1, n_frames=len(frames), width=1280, height=720, duration_us=len(frames) * 33333
        ),
        frontier_frame=len(frames) - 1,
    )
    return ToolContext(session=session, store=store, tracks=None)


class Scripted:
    """Returns the scripted turns in order; a callable entry sees the messages so far."""

    name, model = "scripted", "s-1"

    def __init__(self, turns: list[Any]) -> None:
        self.turns = turns
        self.calls = 0

    def complete(self, system, messages, tools, *, max_tokens=4096, agent="agent"):  # type: ignore[no-untyped-def]
        t = self.turns[min(self.calls, len(self.turns) - 1)]
        self.calls += 1
        return t(messages) if callable(t) else t


def _last_tool(messages: list[dict[str, Any]]) -> dict[str, Any]:
    m = next(m for m in reversed(messages) if m["role"] in ("tool", "user"))
    content = m["content"]
    return json.loads(content.split(" -> ", 1)[1] if m["role"] == "user" else content)


# ---------------------------------------------------------------------- tools
def test_tools_separate_warmup_from_official_play(ctx: ToolContext) -> None:
    ov = json.loads(run_tool(ctx, "match_overview", {}))
    assert ov["official_rallies"] == 3 and ov["unofficial_rallies"] == 1
    assert ov["match_phase"]["phase"] == "match_play"
    assert ov["observation"]["score_basis"].startswith("counted from the first observed")
    assert ov["score_event_id"] in ov["evidence_ids"]
    rallies = json.loads(run_tool(ctx, "list_rallies", {}))["rallies"]
    assert [r["rally_no"] for r in rallies] == [1, 2, 3]
    every = json.loads(run_tool(ctx, "list_rallies", {"include_unofficial": True}))["rallies"]
    assert len(every) == 4 and every[0]["official"] is False and every[0]["winner"] is None
    st = json.loads(run_tool(ctx, "player_stats", {"player": "Axelsen"}))
    assert st["stats"]["points_won"] == 2 and "warm-up excluded" in st["scope"]


def test_get_rally_by_number_and_unknown_number(ctx: ToolContext) -> None:
    r = json.loads(run_tool(ctx, "get_rally", {"rally_no": 2}))
    assert r["rally_no"] == 2 and r["official"] is True
    missing = json.loads(run_tool(ctx, "get_rally", {"rally_no": 50}))
    assert missing["official_rallies"] == "numbered 1..3" and missing["evidence_ids"] == []
    fake = json.loads(run_tool(ctx, "get_rally", {"rally_event_id": "rally_event_id_50"}))
    assert "never construct" in fake["hint"]


# ---------------------------------------------------------------------- validator (DEF-04)
def test_validator_accepts_abstentions_and_references(ctx: ToolContext) -> None:
    run_tool(ctx, "get_rally", {"rally_no": 50})
    q = "Who won the 50th rally of this match?"
    text = (
        "I am unable to answer your question. The data does not contain the 50th rally. "
        "Game 3 was not played in this clip."
    )
    assert validate(text, ctx, q) == []


def test_validator_flags_hallucinated_and_uncited_numbers(ctx: ToolContext) -> None:
    ov = json.loads(run_tool(ctx, "match_overview", {}))
    sid = ov["score_event_id"]
    assert validate(f"There were 3 official rallies [[ev:{sid}]].", ctx) == []
    assert any(i.startswith("uncited number") for i in validate("There were 3 official rallies.", ctx))
    bad = validate(f"The top smash reached 412 km/h [[ev:{sid}]].", ctx)
    assert any("not in any tool result (412)" in i for i in bad)
    assert validate("Rally 2 was the longest [[ev:nope]].", ctx) == ["cites unknown event nope"]


# ---------------------------------------------------------------------- loop robustness (DEF-05)
def test_tool_calls_written_as_text_are_executed(ctx: ToolContext) -> None:
    def final(messages: list[dict[str, Any]]) -> LLMTurn:
        ov = _last_tool(messages)
        return LLMTurn(
            f"{ov['official_rallies']} official rallies were played [[ev:{ov['score_event_id']}]].", [], "stop"
        )

    p = Scripted([LLMTurn('Let me check. {"name": "match_overview", "parameters": {}}', [], "stop"), final])
    a = answer("How many rallies?", ctx, p)
    assert [t["tool"] for t in a.tool_trace] == ["match_overview"]
    assert a.grounded, a.issues
    assert a.text.startswith("3 official rallies") and "{" not in a.text


def test_raw_tool_json_is_never_the_answer(ctx: ToolContext) -> None:
    junk = LLMTurn('{"name": "list_rallies", "parameters": {"game": "game3"}}', [], "stop")
    a = answer("Who won game 3?", ctx, Scripted([junk]))
    assert "{" not in a.text and not a.grounded


def test_repeated_identical_calls_hit_the_cache(ctx: ToolContext) -> None:
    same = LLMTurn("", [ToolCall("a", "player_stats", {"player": "P1"})], "tool_use")

    def final(messages: list[dict[str, Any]]) -> LLMTurn:
        st = next(json.loads(m["content"]) for m in messages if m["role"] == "tool")
        return LLMTurn(f"Axelsen won {st['rallies_won']} rallies [[ev:P1_stats]].", [], "stop")

    a = answer("How many rallies did P1 win?", ctx, Scripted([same, same, same, final]))
    assert [t["tool"] for t in a.tool_trace] == ["player_stats"]  # executed once
    # the placeholder citation is mapped onto the player_stats evidence (DEF-05)
    assert a.grounded, a.issues
    assert a.citations and a.citations[0]["ref"] in ctx.seen_ids


def test_unrepairable_answer_is_marked_ungrounded(ctx: ToolContext) -> None:
    p = Scripted([LLMTurn("Axelsen hit 17 smashes at 400 km/h.", [], "stop")])
    a = answer("How many smashes?", ctx, p)
    assert not a.grounded and any("not in any tool result" in i for i in a.issues)


def test_text_tool_call_parser_handles_noise() -> None:
    calls = text_tool_calls('x {"name": "nope"} {"name": "momentum", "arguments": "{}"} {bad json')
    assert [(c.name, c.arguments) for c in calls] == [("momentum", {})]


def test_rally_tool_resolves_corrected_stroke_and_retraction(ctx: ToolContext) -> None:
    from bai_engine.schema import EventStatus, Provenance

    rally = next(r for r in ctx.store.query(types=["rally_end"]) if r.payload.get("official"))
    original = ctx.store.get(rally.payload["shots"][0]["event_id"])
    corrected = ctx.store.append(
        original.correct(
            payload={**original.payload, "stroke": "drop"},
            status=EventStatus.HUMAN_VERIFIED,
            provenance=Provenance(model="human"),
        )
    )
    result = json.loads(run_tool(ctx, "get_rally", {"rally_event_id": rally.event_id}))
    shot = next(s for s in result["shots"] if s["stroke_event_id"] == corrected.event_id)
    assert shot["stroke"] == "drop"
    ctx.store.append(corrected.correct(status=EventStatus.RETRACTED, provenance=Provenance(model="human")))
    result = json.loads(run_tool(ctx, "get_rally", {"rally_event_id": rally.event_id}))
    assert corrected.event_id not in {s["stroke_event_id"] for s in result["shots"]}
    assert original.event_id not in result["evidence_ids"]


def test_analyst_never_counts_unowned_candidate_stroke(ctx: ToolContext) -> None:
    from bai_engine.schema import Event, Provenance

    candidate = ctx.store.append(
        Event(
            session_id="S1",
            type="stroke",
            frame_start=99999,
            frame_end=99999,
            pts_us=3333300000,
            payload={"stroke": "smash"},
            provenance=Provenance(model="candidate"),
        )
    )
    result = json.loads(run_tool(ctx, "find_strokes", {}))
    assert candidate.event_id not in result["evidence_ids"]


def test_analyst_refreshes_cached_analytics_after_correction(ctx: ToolContext) -> None:
    from bai_engine.schema import EventStatus, Provenance

    ctx.analytics()
    rally = next(r for r in ctx.store.query(types=["rally_end"]) if r.payload.get("official"))
    stroke = ctx.store.get(rally.payload["shots"][0]["event_id"])
    ctx.store.append(
        stroke.correct(
            payload={**stroke.payload, "stroke": "audit_label"},
            status=EventStatus.HUMAN_VERIFIED,
            provenance=Provenance(model="human"),
        )
    )
    stats = json.loads(run_tool(ctx, "player_stats", {"player": stroke.actors.player_id}))
    assert stats["stats"]["strokes"].get("audit_label") == 1


def test_get_rally_keeps_one_revision_when_correction_arrives_during_read(
    ctx: ToolContext, monkeypatch: pytest.MonkeyPatch
) -> None:
    """An intervening append must not join newer rally IDs with older shot records."""
    rally = next(r for r in ctx.store.query(types=["rally_end"]) if r.payload.get("official"))
    original_query = EventStore.query
    replacement_ids: list[str] = []

    def query_with_intervening_correction(store: EventStore, *args: Any, **kwargs: Any) -> Any:
        result = original_query(store, *args, **kwargs)
        # rally_records has captured its rally versions before resolving strokes.
        # Append a real revision here; no threads or timing assumptions are needed.
        if store is ctx.store and kwargs.get("types") == ["stroke"] and not replacement_ids:
            replacement = store.append(
                rally.correct(payload={**rally.payload, "phase_reason": "concurrent reviewer revision"})
            )
            replacement_ids.append(replacement.event_id)
        return result

    monkeypatch.setattr(EventStore, "query", query_with_intervening_correction)
    result = json.loads(run_tool(ctx, "get_rally", {"rally_event_id": rally.event_id}))
    assert replacement_ids  # the correction actually happened inside this read
    assert result["rally_event_id"] == rally.event_id
    assert result["phase_reason"] == rally.payload["phase_reason"]
    assert result["shots"]
    assert rally.event_id in result["evidence_ids"]
    assert replacement_ids[0] not in result["evidence_ids"]
    # The next request observes the new complete revision, rather than staying stale.
    refreshed = json.loads(run_tool(ctx, "get_rally", {"rally_event_id": rally.event_id}))
    assert refreshed["rally_event_id"] == replacement_ids[0]
    assert refreshed["phase_reason"] == "concurrent reviewer revision"
