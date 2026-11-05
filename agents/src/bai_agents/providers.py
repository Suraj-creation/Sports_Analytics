"""LLM providers behind one neutral interface — closed models by direct API call *and* local models.

Supported backends (``BAI_LLM_PROVIDER``):

* ``anthropic``     — Claude via the official ``anthropic`` SDK (default model ``claude-opus-5-5``,
  adaptive thinking, effort control, server-side refusal fallbacks enabled).
* ``openai``        — OpenAI via the official ``openai`` SDK.
* ``azure_openai``  — Azure OpenAI via ``openai.AzureOpenAI`` (reuses the legacy ``AZURE_OPENAI_*`` env).
* ``local``         — any OpenAI-compatible local server: LM Studio, Ollama (``/v1``), vLLM, llama.cpp.
  On the GPU host a local LLM competes with perception for VRAM — keep it on another device or
  budget its memory (report §11).

The agent loop speaks a neutral message format::

    {"role": "user", "content": str}
    {"role": "assistant", "content": str, "tool_calls": [ToolCall, ...], "raw": <provider-native>}
    {"role": "tool", "tool_call_id": str, "name": str, "content": str}

Each provider translates it to its own wire format, so tools, validation and budgets are shared.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Protocol

from bai_agents.accounting import ReportedTokenUsage, anthropic_usage, openai_usage
from bai_engine.obs import LLM_TOKENS, get_logger

log = get_logger(__name__)


@dataclass
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]  # JSON Schema (object)


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict[str, Any]


@dataclass
class LLMTurn:
    text: str
    tool_calls: list[ToolCall]
    stop_reason: str
    usage: dict[str, int] = field(default_factory=dict)
    raw: Any = None  # provider-native assistant content (replayed unchanged next turn)
    model: str = ""
    token_accounting: ReportedTokenUsage | None = None


class LLMError(RuntimeError):
    pass


class LLMProvider(Protocol):
    # Strict session admission is an optional separate TokenBudgetCapability.
    # Existing native adapters have no verified input upper bound for their exact
    # requests, so budgeted application calls fail closed rather than estimating.

    name: str
    model: str

    def complete(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[ToolSpec],
        *,
        max_tokens: int = 4096,
        agent: str = "agent",
    ) -> LLMTurn: ...


def _count(agent: str, provider: str, usage: dict[str, int]) -> None:
    for kind, n in usage.items():
        if type(n) is int and n > 0:
            LLM_TOKENS.labels(agent=agent, provider=provider, kind=kind).inc(n)


# ---------------------------------------------------------------------- Anthropic (official SDK)
class AnthropicProvider:
    name = "anthropic"
    default_output_tokens = 16000
    FALLBACK_BETA = "server-side-fallback-2026-07-01"

    def __init__(self, model: str | None = None, effort: str = "medium", fallbacks: bool = True) -> None:
        import anthropic

        self._anthropic = anthropic
        self.client = anthropic.Anthropic(timeout=30.0, max_retries=0)  # Explicit bounded single transport attempt.
        self.model = model or os.getenv("ANTHROPIC_MODEL", "claude-opus-5-5")
        self.effort = effort
        self.fallbacks = fallbacks

    def _messages(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = []
        for m in messages:
            if m["role"] == "user":
                out.append({"role": "user", "content": m["content"]})
            elif m["role"] == "assistant":
                # replay the provider-native content unchanged (thinking blocks must round-trip)
                out.append({"role": "assistant", "content": m.get("raw") or m["content"]})
            elif m["role"] == "tool":
                block = {"type": "tool_result", "tool_use_id": m["tool_call_id"], "content": m["content"]}
                if m.get("is_error"):
                    block["is_error"] = True
                # all tool results of one turn go back in a single user message
                if (
                    out
                    and out[-1]["role"] == "user"
                    and isinstance(out[-1]["content"], list)
                    and all(b.get("type") == "tool_result" for b in out[-1]["content"])
                ):
                    out[-1]["content"].append(block)
                else:
                    out.append({"role": "user", "content": [block]})
        return out

    def complete(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[ToolSpec],
        *,
        max_tokens: int = 16000,
        agent: str = "agent",
    ) -> LLMTurn:
        a = self._anthropic
        kwargs: dict[str, Any] = {
            "model": self.model,
            "max_tokens": max_tokens,
            "system": system,
            "messages": self._messages(messages),
            "output_config": {"effort": self.effort},
        }
        if tools:
            kwargs["tools"] = [
                {"name": t.name, "description": t.description, "input_schema": t.parameters, "strict": True}
                for t in tools
            ]
        if self.fallbacks:
            kwargs["betas"] = [self.FALLBACK_BETA]
            kwargs["fallbacks"] = "default"
        try:
            resp = self.client.beta.messages.create(**kwargs)
        except a.BadRequestError as e:
            raise LLMError(f"Claude rejected the request: {e.message}") from e
        except a.RateLimitError as e:
            raise LLMError("Claude rate limit reached; try again shortly") from e
        except a.APIStatusError as e:
            raise LLMError(f"Claude API error {e.status_code}") from e
        except a.APIConnectionError as e:
            raise LLMError("Could not reach the Claude API") from e
        accounting = anthropic_usage(resp.usage)
        components = dict(accounting.components)
        usage = {
            legacy: components[source]
            for legacy, source in (
                ("input", "input_uncached"),
                ("output", "output"),
                ("cache_read", "cache_read"),
                ("cache_write", "cache_write"),
            )
            if source in components
        }
        _count(agent, self.name, usage)
        if resp.stop_reason == "refusal":
            return LLMTurn(
                text="I can't help with that request.",
                tool_calls=[],
                stop_reason="refusal",
                raw=resp.content,
                model=resp.model,
                usage=usage,
                token_accounting=accounting,
            )
        text = "".join(b.text for b in resp.content if b.type == "text")
        calls = [ToolCall(b.id, b.name, dict(b.input)) for b in resp.content if b.type == "tool_use"]
        return LLMTurn(
            text=text,
            tool_calls=calls,
            stop_reason=resp.stop_reason or "end_turn",
            usage=usage,
            raw=resp.content,
            model=resp.model,
            token_accounting=accounting,
        )


# ---------------------------------------------------------------------- OpenAI-compatible (official SDK)
class OpenAICompatProvider:
    default_output_tokens = 4096

    def __init__(self, client: Any, model: str, name: str) -> None:
        self.client = client
        self.model = model
        self.name = name

    @staticmethod
    def _messages(system: str, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        out: list[dict[str, Any]] = [{"role": "system", "content": system}]
        for m in messages:
            if m["role"] == "assistant":
                msg: dict[str, Any] = {"role": "assistant", "content": m.get("content") or ""}
                if m.get("tool_calls"):
                    msg["tool_calls"] = [
                        {
                            "id": c.id,
                            "type": "function",
                            "function": {"name": c.name, "arguments": json.dumps(c.arguments)},
                        }
                        for c in m["tool_calls"]
                    ]
                out.append(msg)
            elif m["role"] == "tool":
                out.append({"role": "tool", "tool_call_id": m["tool_call_id"], "content": m["content"]})
            else:
                out.append({"role": "user", "content": m["content"]})
        return out

    def complete(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[ToolSpec],
        *,
        max_tokens: int = 4096,
        agent: str = "agent",
    ) -> LLMTurn:
        import openai

        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": self._messages(system, messages),
            "max_tokens": max_tokens,
        }
        if tools:
            kwargs["tools"] = [
                {
                    "type": "function",
                    "function": {"name": t.name, "description": t.description, "parameters": t.parameters},
                }
                for t in tools
            ]
        try:
            resp = self.client.chat.completions.create(**kwargs)
        except openai.APIConnectionError as e:
            raise LLMError(f"Could not reach the {self.name} endpoint") from e
        except openai.APIStatusError as e:
            raise LLMError(f"{self.name} error {e.status_code}") from e
        choice = resp.choices[0]
        msg = choice.message
        calls = []
        for tc in msg.tool_calls or []:
            try:
                args = json.loads(tc.function.arguments or "{}")
            except json.JSONDecodeError:
                args = {"_invalid_json": tc.function.arguments}
            calls.append(ToolCall(tc.id, tc.function.name, args))
        accounting = openai_usage(resp.usage)
        components = dict(accounting.components)
        usage = {key: components[key] for key in ("input", "output") if key in components}
        _count(agent, self.name, usage)
        return LLMTurn(
            text=msg.content or "",
            tool_calls=calls,
            stop_reason=choice.finish_reason or "stop",
            usage=usage,
            model=getattr(resp, "model", self.model),
            token_accounting=accounting,
        )


def make_provider(name: str | None = None) -> LLMProvider:
    """Build the configured provider from environment variables / .env (via pydantic-settings)."""
    try:
        from bai_engine.config import get_settings

        cfg = get_settings()
    except Exception:
        cfg = None  # outside the server process: raw env vars only

    def pick(field: str, *envs: str, default: str) -> str:
        # Explicit BAI_* settings (env or .env) win; otherwise honour the legacy unprefixed env vars.
        if cfg is not None and field in cfg.model_fields_set:
            return str(getattr(cfg, field))
        return next((v for e in envs if (v := os.getenv(e))), default)

    _name = (name or pick("llm_provider", "BAI_LLM_PROVIDER", "LLM_PROVIDER", default="azure_openai")).lower()
    _local_url = pick("local_llm_url", "BAI_LOCAL_LLM_URL", "LM_STUDIO_BASE_URL", default="http://127.0.0.1:1234/v1")
    _local_model = pick("local_llm_model", "BAI_LOCAL_LLM_MODEL", "LM_STUDIO_MODEL", default="local-model")
    _local_key = pick("local_llm_key", "BAI_LOCAL_LLM_KEY", default="local")

    if _name in ("anthropic", "claude"):
        return AnthropicProvider(effort=os.getenv("ANTHROPIC_EFFORT", "medium"))
    import openai

    if _name in ("azure", "azure_openai"):
        endpoint, key = os.getenv("AZURE_OPENAI_ENDPOINT"), os.getenv("AZURE_OPENAI_API_KEY")
        if not endpoint or not key:
            raise LLMError("Azure OpenAI is selected but AZURE_OPENAI_ENDPOINT / AZURE_OPENAI_API_KEY are not set")
        client = openai.AzureOpenAI(
            azure_endpoint=endpoint,
            api_key=key,
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-04-01-preview"),
            timeout=30.0,
            max_retries=0,
        )
        return OpenAICompatProvider(client, os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1-mini"), "azure_openai")
    if _name in ("openai", "chatgpt"):
        if not os.getenv("OPENAI_API_KEY"):
            raise LLMError("OpenAI is selected but OPENAI_API_KEY is not set")
        return OpenAICompatProvider(
            openai.OpenAI(timeout=30.0, max_retries=0), os.getenv("OPENAI_MODEL", "gpt-4o-mini"), "openai"
        )
    if _name in ("local", "lm_studio", "ollama", "vllm"):
        client = openai.OpenAI(base_url=_local_url, api_key=_local_key, timeout=30.0, max_retries=0)
        return OpenAICompatProvider(client, _local_model, "local")
    raise LLMError(f"unknown LLM provider {_name!r} (anthropic | openai | azure_openai | local)")
