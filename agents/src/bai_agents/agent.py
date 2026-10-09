"""Grounded match Q&A / insight agent.

Loop: the model calls read-only tools over the event store, then answers.  The answer contract:

* every statement about *this match* carries a citation ``[[ev:<event_id>]]`` to an event that a
  tool returned in this conversation; background facts cite ``[[kb:<doc#n>]]``;
* the validator rejects citations to unseen ids and sentences with numbers but no citation; one
  repair round is attempted, after which unsupported sentences are marked rather than shown as fact.

LLM failure never breaks the product: :func:`deterministic_answer` builds a plain answer from the
same tools.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from bai_agents.providers import LLMError, LLMProvider
from bai_agents.tools import TOOLS, ToolContext, run_tool
from bai_engine.obs import get_logger

log = get_logger(__name__)

SYSTEM = """You are the analyst inside a badminton match-analysis app. You answer questions about ONE match \
using only the tools provided. Tools read a verified event log produced by computer vision: rallies, strokes, \
points, scores, highlights, player statistics.

Rules:
- Facts about this match must come from tool results. Cite each one inline as [[ev:EVENT_ID]] using an id that \
appears in the tool output (rally_event_id, stroke_event_id, event_id or evidence_ids).
- Background knowledge (rules, player careers) must come from rules_and_background and is cited as [[kb:REF]]. \
Never present background knowledge as something that happened in this match.
- If the data does not answer the question, say so plainly and say what would be needed.
- Labels with band "probable" or "uncertain" are model estimates: say "probably" or "the model suggests".
- Refer to players by name. Keep answers short: lead with the answer, then the evidence. Use times like 12:34.
- Do not invent numbers, speeds, angles or player intentions."""

CITE = re.compile(r"\[\[(ev|kb):([^\]]+)\]\]")
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")


@dataclass
class Answer:
    text: str
    citations: list[dict[str, str]]
    tool_trace: list[dict[str, Any]] = field(default_factory=list)
    grounded: bool = True
    issues: list[str] = field(default_factory=list)
    provider: str = ""
    model: str = ""
    usage: dict[str, int] = field(default_factory=dict)


def validate(text: str, ctx: ToolContext) -> list[str]:
    issues = []
    for kind, ref in CITE.findall(text):
        if kind == "ev" and ref not in ctx.seen_ids:
            issues.append(f"cites unknown event {ref}")
        if kind == "kb" and ref not in ctx.kb_refs:
            issues.append(f"cites unknown knowledge passage {ref}")
    for s in SENTENCE.split(text):
        plain = CITE.sub("", s)
        if re.search(r"\d", plain) and not CITE.search(s) and not re.fullmatch(r"\s*[-*]?\s*\d+[.)]\s*", plain):
            # times/scores/counts must be evidenced
            issues.append(f"uncited number in: {plain.strip()[:80]}")
    return issues


def ask(
    question: str,
    ctx: ToolContext,
    provider: LLMProvider,
    history: list[dict[str, Any]] | None = None,
    max_rounds: int = 6,
) -> Answer:
    tools = [spec for spec, _ in TOOLS.values()]
    msgs: list[dict[str, Any]] = [*(history or []), {"role": "user", "content": question}]
    trace: list[dict[str, Any]] = []
    usage: dict[str, int] = {}
    turn = None
    for _ in range(max_rounds):
        turn = provider.complete(SYSTEM, msgs, tools, agent="qa")
        for k, v in turn.usage.items():
            usage[k] = usage.get(k, 0) + v
        msgs.append({"role": "assistant", "content": turn.text, "tool_calls": turn.tool_calls, "raw": turn.raw})
        if not turn.tool_calls:
            break
        for call in turn.tool_calls:
            result = run_tool(ctx, call.name, call.arguments)
            trace.append({"tool": call.name, "args": call.arguments, "bytes": len(result)})
            msgs.append({"role": "tool", "tool_call_id": call.id, "name": call.name, "content": result})
    assert turn is not None
    text = turn.text.strip()
    issues = validate(text, ctx)
    if issues and turn.stop_reason != "refusal":
        msgs.append(
            {
                "role": "user",
                "content": "Your answer has grounding problems: "
                + "; ".join(issues[:8])
                + ". Rewrite it so that every match fact cites an id from the tool results, and remove anything "
                "you cannot support.",
            }
        )
        turn = provider.complete(SYSTEM, msgs, tools, agent="qa")
        text = turn.text.strip() or text
        issues = validate(text, ctx)
    cits = [{"kind": k, "ref": r} for k, r in dict.fromkeys(CITE.findall(text))]
    return Answer(
        text=text,
        citations=cits,
        tool_trace=trace,
        grounded=not issues,
        issues=issues,
        provider=provider.name,
        model=turn.model or provider.model,
        usage=usage,
    )


def deterministic_answer(question: str, ctx: ToolContext) -> Answer:
    """No-LLM fallback: a factual summary with citations built directly from the tools."""
    import json

    ov = json.loads(run_tool(ctx, "match_overview", {}))
    parts = []
    st = ov.get("current_state") or {}
    names = ov["players"]
    if st:
        sc = st.get("score", {})
        parts.append(f"Game {st.get('game_no')}: {names['P1']} {sc.get('P1')} – {sc.get('P2')} {names['P2']}.")
    for g in ov.get("games", []):
        parts.append(
            f"Game {g['game_no']} won by {g['winner']} {g['score'][0]}–{g['score'][1]} [[ev:{g['event_id']}]]."
        )
    hl = json.loads(run_tool(ctx, "top_highlights", {"k": 3}))
    for h in hl["highlights"]:
        cats = ", ".join(c.replace("_", " ") for c in h["categories"]) or "notable rally"
        parts.append(f"Highlight at {h['time']}: {cats} [[ev:{h['rally_id']}]].")
    if not parts:
        parts.append("Analysis has not produced any rallies yet.")
    text = " ".join(parts) + " (The AI assistant is unavailable, so this is an automatic summary.)"
    return Answer(
        text=text,
        citations=[{"kind": k, "ref": r} for k, r in CITE.findall(text)],
        grounded=True,
        provider="deterministic",
        model="rules",
    )


def answer(
    question: str, ctx: ToolContext, provider: LLMProvider | None, history: list[dict[str, Any]] | None = None
) -> Answer:
    if provider is None:
        return deterministic_answer(question, ctx)
    try:
        return ask(question, ctx, provider, history)
    except LLMError as e:
        log.warning("agent.llm_failed", error=str(e))
        a = deterministic_answer(question, ctx)
        a.issues.append(str(e))
        return a
