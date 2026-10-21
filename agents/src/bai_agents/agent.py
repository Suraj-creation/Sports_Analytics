"""Grounded match Q&A / insight agent.

Loop: the model calls read-only tools over the event store, then answers.  The answer contract:

* every statement about *this match* carries a citation ``[[ev:<event_id>]]`` to an event that a
  tool returned in this conversation; background facts cite ``[[kb:<doc#n>]]``;
* every number stated must appear in some tool result of the conversation (the real hallucination
  guard); references ("rally 50", "game 3", "the 50th") and numbers taken from the question are
  not claims, and negative / abstaining sentences need no citation;
* one repair round is attempted, after which unsupported sentences are marked rather than shown as
  fact.

Small local models (8B) are supported defensively (validation DEF-04/05): tool calls written as
JSON text are executed instead of being shown as the answer, identical repeated calls are answered
from cache with a nudge, and placeholder citations (``[[ev:P1_stats]]``) are mapped to the
evidence of the tool call they name — or dropped.

LLM failure never breaks the product: :func:`deterministic_answer` builds a plain answer from the
same tools.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any

from bai_agents.providers import LLMError, LLMProvider, ToolCall
from bai_agents.tools import TOOLS, ToolContext, run_tool
from bai_engine.obs import get_logger

log = get_logger(__name__)

SYSTEM = """You are the analyst inside a badminton match-analysis app. You answer questions about ONE match \
using only the tools provided. Tools read a verified event log produced by computer vision: rallies, strokes, \
points, scores, highlights, player statistics, and the match phase.

Rules:
- Facts about this match must come from tool results. Cite each one inline as [[ev:EVENT_ID]], copying an id \
character-for-character from the tool output (rally_event_id, stroke_event_id, event_id, score_event_id or \
evidence_ids). Never make up an id. Example: "Lee won 12 rallies [[ev:5e55b5a7-d5b4-42fe-8c0d-6a8e2f9ae5d3]]."
- Every number you state must appear in a tool result. Do not add up, estimate or convert unless asked.
- Only official rallies count. Warm-up, practice and replayed exchanges (official=false) are not part of the \
score or statistics.
- Check match_overview.observation: if the video starts mid-game, the match is unfinished, or analysis is still \
running, say that the numbers cover only the observed part of the match.
- Background knowledge (rules, player careers) must come from rules_and_background and is cited as [[kb:REF]]. \
Never present background knowledge as something that happened in this match.
- If the data does not answer the question, say so plainly and say what would be needed. That is a good answer.
- Labels with band "probable" or "uncertain" are model estimates: say "probably" or "the model suggests".
- Call tools through the tool interface only — never write a tool call as text in your answer.
- Refer to players by name. Keep answers short: lead with the answer, then the evidence. Use times like 12:34.
- Do not invent numbers, speeds, angles or player intentions."""

CITE = re.compile(r"\[\[(ev|kb):([^\]]+)\]\]")
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9\"'(])")
NUM = re.compile(r"(?<![\w.])\d+(?:[.,:]\d+)?")
# numbers that *refer* to something rather than state a quantity
REF = re.compile(
    r"(?i)\b(?:rally|rallies|game|games|set|player|p|no\.?|number|#)\s*#?\s*\d+\b|\b\d+(?:st|nd|rd|th)\b|\[\[[^\]]*\]\]"
)
NEG = re.compile(
    r"(?i)\b(?:no|not|none|never|cannot|can't|unable|unavailable|insufficient|unknown|isn't|aren't|wasn't|"
    r"weren't|doesn't|don't|didn't|without|n't)\b"
)


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


def _norm_num(n: str) -> str:
    n = n.replace(",", ".")
    try:
        f = float(n)
    except ValueError:
        return n  # times like 12:34
    return str(int(f)) if f == int(f) else str(round(f, 3)).rstrip("0").rstrip(".")


def _known_numbers(texts: list[str]) -> set[str]:
    """Numbers present in tool output, plus their usual renderings (percent, rounding)."""
    out: set[str] = set()
    for t in texts:
        for n in NUM.findall(t):
            out.add(_norm_num(n))
            if ":" in n:
                continue
            f = float(n.replace(",", "."))
            out.update({str(round(f)), _norm_num(str(round(f, 1)))})
            if 0 < f <= 1:
                out.update({_norm_num(str(round(f * 100, 1))), str(round(f * 100))})
    return out


def _claimed_numbers(sentence: str, question: str) -> list[str]:
    q = {_norm_num(n) for n in NUM.findall(REF.sub(" ", question))} | {_norm_num(n) for n in NUM.findall(question)}
    return [n for n in (_norm_num(x) for x in NUM.findall(REF.sub(" ", sentence))) if n not in q]


def validate(text: str, ctx: ToolContext, question: str = "") -> list[str]:
    issues = []
    for kind, ref in CITE.findall(text):
        if kind == "ev" and ref not in ctx.seen_ids:
            issues.append(f"cites unknown event {ref}")
        if kind == "kb" and ref not in ctx.kb_refs:
            issues.append(f"cites unknown knowledge passage {ref}")
    known = _known_numbers(ctx.outputs)
    for s in SENTENCE.split(text):
        plain = CITE.sub("", s)
        if re.fullmatch(r"\s*[-*]?\s*\d+[.)]\s*", plain):
            continue  # list marker
        nums = _claimed_numbers(plain, question)
        if not nums:
            continue
        unsupported = [n for n in nums if n not in known]
        if unsupported:
            issues.append(f"number not in any tool result ({', '.join(unsupported)}): {plain.strip()[:80]}")
        elif not CITE.search(s) and not NEG.search(plain):
            issues.append(f"uncited number in: {plain.strip()[:80]}")
    return issues


def text_tool_calls(text: str) -> list[ToolCall]:
    """Tool calls a model wrote as JSON text (``{"name": ..., "parameters": {...}}``)."""
    dec = json.JSONDecoder()
    out: list[ToolCall] = []
    i = text.find("{")
    while i != -1:
        try:
            obj, end = dec.raw_decode(text, i)
        except ValueError:
            i = text.find("{", i + 1)
            continue
        if isinstance(obj, dict) and obj.get("name") in TOOLS:
            args = obj.get("parameters", obj.get("arguments", {}))
            if isinstance(args, str):
                try:
                    args = json.loads(args)
                except ValueError:
                    args = {}
            out.append(ToolCall(f"text-{len(out)}", obj["name"], args if isinstance(args, dict) else {}))
        i = text.find("{", end)
    return out


def repair_citations(text: str, ctx: ToolContext, trace: list[dict[str, Any]]) -> str:
    """Map placeholder citations (``[[ev:P1_stats]]``) to the evidence of the tool call they name;
    drop citations that match nothing (the sentence then fails validation as uncited)."""

    def fix(m: re.Match[str]) -> str:
        kind, ref = m.group(1), m.group(2)
        if kind != "ev" or ref in ctx.seen_ids:
            return m.group(0)
        toks = {t for t in re.split(r"[^a-z0-9]+", ref.lower()) if t}
        best, best_score = None, 0
        for t in trace:
            if not t.get("evidence"):
                continue
            words = set(re.split(r"[^a-z0-9]+", t["tool"].lower())) | {
                str(v).lower() for v in t["args"].values() if v is not None
            }
            score = len(toks & words)
            if score > best_score:
                best, best_score = t, score
        return f"[[ev:{best['evidence'][0]}]]" if best is not None else ""

    return CITE.sub(fix, text)


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
    cache: dict[str, str] = {}
    turn = None

    def call(c: ToolCall) -> str:
        key = f"{c.name}:{json.dumps(c.arguments, sort_keys=True, default=str)}"
        if key in cache:
            return json.dumps(
                {"note": "same call as before; the result has not changed — use it or call with other arguments"}
            )
        result = cache[key] = run_tool(ctx, c.name, c.arguments)
        try:
            ev = json.loads(result).get("evidence_ids") or []
        except (ValueError, AttributeError):
            ev = []
        trace.append({"tool": c.name, "args": c.arguments, "bytes": len(result), "evidence": ev})
        return result

    for _ in range(max_rounds):
        turn = provider.complete(SYSTEM, msgs, tools, agent="qa")
        for k, v in turn.usage.items():
            usage[k] = usage.get(k, 0) + v
        msgs.append({"role": "assistant", "content": turn.text, "tool_calls": turn.tool_calls, "raw": turn.raw})
        if turn.tool_calls:
            for c in turn.tool_calls:
                msgs.append({"role": "tool", "tool_call_id": c.id, "name": c.name, "content": call(c)})
            continue
        written = text_tool_calls(turn.text)
        if not written:
            break
        # the model wrote its tool calls as text: run them and hand back the results as a user turn
        results = "\n".join(f"{c.name}({json.dumps(c.arguments)}) -> {call(c)}" for c in written)
        msgs.append(
            {
                "role": "user",
                "content": "You wrote tool calls as text; here are their results. Now answer the question "
                "(use the tool interface for any further calls):\n" + results,
            }
        )
    assert turn is not None
    text = repair_citations(turn.text.strip(), ctx, trace)
    if text_tool_calls(text):
        text = ""  # never show raw tool-call JSON as an answer
    issues = validate(text, ctx, question) if text else ["no answer was produced"]
    if issues and turn.stop_reason != "refusal":
        msgs.append(
            {
                "role": "user",
                "content": "Your answer has grounding problems: "
                + "; ".join(issues[:8])
                + ". Rewrite it so that every match fact cites an id copied from the tool results and every number "
                "comes from a tool result; remove anything you cannot support. If the data cannot answer the "
                "question, say so.",
            }
        )
        turn = provider.complete(SYSTEM, msgs, tools, agent="qa")
        for k, v in turn.usage.items():
            usage[k] = usage.get(k, 0) + v
        retry = repair_citations(turn.text.strip(), ctx, trace)
        if retry and not text_tool_calls(retry):
            text = retry
        issues = validate(text, ctx, question) if text else ["no answer was produced"]
    if not text:
        text = "I couldn't produce an answer grounded in this match's data."
    cits = [{"kind": k, "ref": r} for k, r in dict.fromkeys(CITE.findall(text))]
    return Answer(
        text=text,
        citations=cits,
        tool_trace=[{k: v for k, v in t.items() if k != "evidence"} for t in trace],
        grounded=not issues,
        issues=issues,
        provider=provider.name,
        model=turn.model or provider.model,
        usage=usage,
    )


def deterministic_answer(question: str, ctx: ToolContext) -> Answer:
    """No-LLM fallback: a factual summary with citations built directly from the tools."""
    ov = json.loads(run_tool(ctx, "match_overview", {}))
    parts = []
    st = ov.get("current_state") or {}
    names = ov["players"]
    sid = ov.get("score_event_id")
    if st and sid:
        sc = st.get("score", {})
        parts.append(
            f"Game {st.get('game_no')}: {names['P1']} {sc.get('P1')} – {sc.get('P2')} {names['P2']} [[ev:{sid}]]."
        )
    for g in ov.get("games", []):
        parts.append(
            f"Game {g['game_no']} won by {g['winner']} {g['score'][0]}–{g['score'][1]} [[ev:{g['event_id']}]]."
        )
    hl = json.loads(run_tool(ctx, "top_highlights", {"k": 3}))
    for h in hl["highlights"]:
        cats = ", ".join(c.replace("_", " ") for c in h["categories"]) or "notable rally"
        parts.append(f"Highlight at {h['time']}: {cats} [[ev:{h['rally_id']}]].")
    if ov.get("unofficial_rallies"):
        parts.append(f"{ov['unofficial_rallies']} warm-up or replayed exchanges were not counted.")
    if not ov.get("official_rallies"):
        parts.append("No official rallies have been observed yet.")
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
