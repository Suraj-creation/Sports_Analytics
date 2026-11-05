"""Durable reported-usage admission and optional strict input-bound admission.

Reported mode requests an output cap, charges complete vendor-reported totals,
and blocks future calls after unknown usage. It is not a total billing hard cap.
Strict mode requires the provider's verified full-request upper-bound contract;
no character estimate is substituted. Historical unmetered usage stays unknown.
"""

from __future__ import annotations

import copy
import hashlib
import json
import logging
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Protocol, runtime_checkable
from uuid import uuid4

from bai_agents.accounting import ReportedTokenUsage
from bai_agents.providers import LLMError, LLMProvider, LLMTurn, ToolCall, ToolSpec
from bai_engine.store import EventStore

LEDGER_KEY = "llm-token-admission:v1"
MAX_PENDING = 64
MAX_RECEIPTS = 256
MAX_REQUEST_BYTES = 1_000_000
MAX_OUTPUT_TOKENS = 4096
log = logging.getLogger(__name__)


class TokenBudgetError(LLMError):
    """No unreserved model request may be sent after this failure."""


class TokenRequestTooLargeError(TokenBudgetError):
    """A known byte-envelope violation, never an unknown-identity fallback."""

    code = "request_too_large"


def _integer(value: Any, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum or value > 2**63 - 1:
        raise TokenBudgetError("Token accounting requires nonnegative canonical integers.")
    return value


@dataclass(frozen=True)
class TokenBudgetContract:
    """Explicit provider attestation; no current vendor adapter supplies it.

    A capability must bound the exact serialized prompt including tool/framing
    overhead and enforce its output cap. Hidden generation retries are forbidden;
    each explicitly retried wrapper call receives another durable reservation.
    """

    version: str = "total-token-upper-bound:v1"
    input_semantics: str = "verified_conservative_upper_bound"
    completion_cap_enforced: bool = True
    automatic_generation_retries: int = 0

    def __post_init__(self) -> None:
        if (
            self.version != "total-token-upper-bound:v1"
            or self.input_semantics != "verified_conservative_upper_bound"
            or self.completion_cap_enforced is not True
            or type(self.automatic_generation_retries) is not int
            or self.automatic_generation_retries != 0
        ):
            raise TokenBudgetError("Unsupported provider token-admission contract.")


@dataclass(frozen=True)
class InputTokenBound:
    tokens: int
    request_sha256: str
    basis: str

    def __post_init__(self) -> None:
        _integer(self.tokens)
        if (
            not isinstance(self.request_sha256, str)
            or len(self.request_sha256) != 64
            or any(c not in "0123456789abcdef" for c in self.request_sha256)
            or not isinstance(self.basis, str)
            or not self.basis.strip()
            or len(self.basis) > 160
        ):
            raise TokenBudgetError("Invalid provider input-bound evidence.")


@runtime_checkable
class TokenBudgetCapability(Protocol):
    contract: TokenBudgetContract

    def input_token_upper_bound(
        self, system: str, messages: list[dict[str, Any]], tools: list[ToolSpec]
    ) -> InputTokenBound | None: ...

    def total_usage_tokens(self, turn: LLMTurn) -> int | None:
        """A nonoverlapping total, or None when usage is incomplete/unknown."""
        ...


def token_request_sha256(
    provider: LLMProvider,
    system: str,
    messages: list[dict[str, Any]],
    tools: list[ToolSpec],
    *,
    allow_native: bool = False,
) -> str:
    """Bind a declared provider/model and full neutral request without storing text.

    Opaque native/raw objects and nonfinite data have no generic exact request
    contract here; those providers need an explicit compatible adapter.
    """

    known_bytes = 0
    active: set[int] = set()

    def check_known_literals(value: Any) -> None:
        # A lower bound on serialized bytes still catches oversized known text
        # when an unrelated opaque history object has no exact JSON identity.
        nonlocal known_bytes
        if isinstance(value, str):
            known_bytes += len(value.encode("utf-8"))
            if known_bytes > MAX_REQUEST_BYTES:
                raise TokenRequestTooLargeError("Provider request exceeds the bounded byte envelope.")
        elif isinstance(value, ToolCall):
            for field in (value.id, value.name, value.arguments):
                check_known_literals(field)
        elif isinstance(value, (dict, list, tuple)) and id(value) not in active:
            active.add(id(value))
            for field in (*value.keys(), *value.values()) if isinstance(value, dict) else value:
                check_known_literals(field)
            active.remove(id(value))

    payload = {
        "provider": provider.name,
        "model": provider.model,
        "system": system,
        "messages": messages,
        "tools": [asdict(tool) for tool in tools],
    }
    check_known_literals(payload)

    def encode_neutral(value: Any) -> Any:
        if isinstance(value, ToolCall):
            return asdict(value)
        if allow_native and type(value).__module__.startswith(("anthropic.", "openai.")):
            dump = getattr(value, "model_dump", None)
            if callable(dump):
                return dump(mode="json")
        raise TypeError("No exact neutral representation exists for this object")

    try:
        encoded = json.dumps(
            payload,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
            default=encode_neutral,
        ).encode("utf-8")
    except (TypeError, ValueError, OverflowError, RecursionError) as exc:
        raise TokenBudgetError("Provider request cannot be bounded by this token contract.") from exc
    if len(encoded) > MAX_REQUEST_BYTES:
        raise TokenRequestTooLargeError("Provider request exceeds the bounded byte envelope.")
    return hashlib.sha256(encoded).hexdigest()


class TokenBudgetLedger:
    """One dedicated session DB outside resettable sporting analysis storage.

    Only public EventStore transactions/meta are used. No lock or transaction is
    held over token counting or generation. Outstanding crash reservations are
    retained, never refunded by time or analysis-generation reset.
    """

    def __init__(self, path: Path, session_id: str) -> None:
        self.store = EventStore(path, session_id)

    def close(self) -> None:
        self.store.close()

    def __enter__(self) -> TokenBudgetLedger:
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    def _load(self) -> dict[str, Any]:
        raw = self.store.get_meta(LEDGER_KEY)
        if raw is None:
            return {
                "v": 1,
                "spent": 0,
                "blocked": False,
                "pending": {},
                "closed": [],
                "components": {},
                "scope": "from_ledger_creation;prior_usage_unknown",
            }
        if len(raw) > 1_000_000:
            raise TokenBudgetError("Token ledger exceeds its bounded schema.")
        try:
            state = json.loads(raw)
            if not isinstance(state, dict) or set(state) != {
                "v",
                "spent",
                "blocked",
                "pending",
                "closed",
                "components",
                "scope",
            }:
                raise ValueError
            if type(state["v"]) is not int or state["v"] != 1 or type(state["blocked"]) is not bool:
                raise ValueError
            if state["scope"] != "from_ledger_creation;prior_usage_unknown":
                raise ValueError
            _integer(state["spent"])
            pending, closed, components = state["pending"], state["closed"], state["components"]
            if not isinstance(pending, dict) or len(pending) > MAX_PENDING:
                raise ValueError
            if not isinstance(closed, list) or len(closed) > MAX_RECEIPTS:
                raise ValueError
            if not isinstance(components, dict) or len(components) > 128:
                raise ValueError
            for key, value in components.items():
                if not isinstance(key, str) or len(key) > 225:
                    raise ValueError
                _integer(value)
            for key, value in pending.items():
                if (
                    not isinstance(key, str)
                    or len(key) != 32
                    or any(c not in "0123456789abcdef" for c in key)
                    or set(value) != {"reserved", "request_sha256", "mode", "uncertain", "usage"}
                ):
                    raise ValueError
                _integer(value["reserved"], minimum=1)
                digest = value["request_sha256"]
                if not isinstance(digest, str) or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
                    raise ValueError
                if value["mode"] not in {"strict", "reported"} or type(value["uncertain"]) is not bool:
                    raise ValueError
                if value["usage"] is not None:
                    ReportedTokenUsage.from_dict(value["usage"])
            for receipt in closed:
                if set(receipt) != {"id", "charged", "basis", "reserved", "mode", "usage"}:
                    raise ValueError
                if not isinstance(receipt["id"], str) or len(receipt["id"]) != 32:
                    raise ValueError
                _integer(receipt["charged"])
                _integer(receipt["reserved"], minimum=1)
                if receipt["basis"] not in {"reported_total", "reserved_unknown", "overrun"}:
                    raise ValueError
                if receipt["mode"] not in {"strict", "reported"}:
                    raise ValueError
                if receipt["usage"] is not None:
                    ReportedTokenUsage.from_dict(receipt["usage"])
        except (TypeError, ValueError, KeyError) as exc:
            raise TokenBudgetError("Token ledger is malformed; model admission is withheld.") from exc
        return state

    def _save(self, state: dict[str, Any]) -> None:
        self.store.set_meta(LEDGER_KEY, json.dumps(state, allow_nan=False, separators=(",", ":")))

    @staticmethod
    def _add_components(state: dict[str, Any], usage: ReportedTokenUsage | None) -> None:
        if usage is None:
            return
        for key, value in usage.components:
            identity = f"{usage.semantics}:{key}"
            if identity not in state["components"] and len(state["components"]) >= 128:
                raise TokenBudgetError("Token accounting categories exceed their bounded schema.")
            state["components"][identity] = state["components"].get(identity, 0) + value

    def available(self, limit: int) -> int:
        limit = _integer(limit)
        state = self._load()
        if state["blocked"] or any(item["mode"] == "reported" for item in state["pending"].values()):
            raise TokenBudgetError("Session token usage is pending or uncertain; further model calls are withheld.")
        return max(0, limit - state["spent"] - sum(item["reserved"] for item in state["pending"].values()))

    def reserve(self, tokens: int, *, limit: int, request_sha256: str | None, mode: str = "strict") -> str:
        tokens, limit = _integer(tokens, minimum=1), _integer(limit)
        if mode not in {"strict", "reported"}:
            raise TokenBudgetError("Unknown token admission mode.")
        if request_sha256 is not None:
            InputTokenBound(0, request_sha256, "request_identity")
        elif mode != "reported":
            raise TokenBudgetError("Strict admission requires exact request identity.")
        with self.store.transaction():
            state = self._load()
            used = state["spent"] + sum(item["reserved"] for item in state["pending"].values())
            pending_unknown = any(item["mode"] == "reported" for item in state["pending"].values())
            if (
                state["blocked"]
                or pending_unknown
                or (mode == "reported" and state["pending"])
                or len(state["pending"]) >= MAX_PENDING
                or used + tokens > limit
            ):
                raise TokenBudgetError("The session token budget cannot admit another model call.")
            identifier = uuid4().hex
            state["pending"][identifier] = {
                "reserved": tokens,
                "request_sha256": request_sha256,
                "mode": mode,
                "uncertain": False,
                "usage": None,
            }
            self._save(state)
        return identifier

    def settle(self, identifier: str, total: int | None, *, usage: ReportedTokenUsage | None = None) -> dict[str, Any]:
        if total is not None:
            total = _integer(total)
        if usage is not None and not isinstance(usage, ReportedTokenUsage):
            raise TokenBudgetError("Invalid reported usage contract.")
        with self.store.transaction():
            state = self._load()
            existing = next((row for row in state["closed"] if row["id"] == identifier), None)
            if existing is not None:
                return copy.deepcopy(existing)
            reservation = state["pending"].get(identifier)
            if reservation is None:
                raise TokenBudgetError("Unknown token reservation; no settlement was applied.")
            if reservation["uncertain"]:
                raise TokenBudgetError("Uncertain token usage requires explicit accounting review, not a refund.")
            self._add_components(state, usage)
            if total is None and reservation["mode"] == "reported":
                reservation["uncertain"], reservation["usage"], state["blocked"] = (
                    True,
                    usage.to_dict() if usage else None,
                    True,
                )
                self._save(state)
                return {
                    "id": identifier,
                    "charged": None,
                    "basis": "unresolved_usage",
                    "reserved": reservation["reserved"],
                    "mode": "reported",
                    "usage": reservation["usage"],
                }
            state["pending"].pop(identifier)
            reserved = reservation["reserved"]
            charged, basis = (reserved, "reserved_unknown") if total is None else (total, "reported_total")
            if reservation["mode"] == "strict" and charged > reserved:
                state["blocked"], basis = True, "overrun"
            state["spent"] += charged
            receipt = {
                "id": identifier,
                "charged": charged,
                "basis": basis,
                "reserved": reserved,
                "mode": reservation["mode"],
                "usage": usage.to_dict() if usage else None,
            }
            state["closed"] = [*state["closed"], receipt][-MAX_RECEIPTS:]
            self._save(state)
        return copy.deepcopy(receipt)

    def snapshot(self) -> dict[str, Any]:
        return copy.deepcopy(self._load())


class BudgetedProvider:
    """Preserve provider injection while refusing undeclared strict bounds."""

    def __init__(
        self,
        provider: LLMProvider,
        ledger: TokenBudgetLedger,
        limit: int,
        *,
        mode: str = "strict",
        output_limit: int | None = None,
    ) -> None:
        self.provider, self.ledger, self.limit = provider, ledger, _integer(limit)
        if mode not in {"strict", "reported"}:
            raise TokenBudgetError("Unknown token admission mode.")
        self.mode = mode
        self.output_limit = _integer(
            output_limit if output_limit is not None else getattr(provider, "default_output_tokens", MAX_OUTPUT_TOKENS),
            minimum=1,
        )
        self.name, self.model = provider.name, provider.model
        self.reported_usage: dict[str, int] = {}
        self.receipts: list[dict[str, Any]] = []

    def complete(
        self,
        system: str,
        messages: list[dict[str, Any]],
        tools: list[ToolSpec],
        *,
        max_tokens: int | None = None,
        agent: str = "agent",
    ) -> LLMTurn:
        maximum = min(
            _integer(max_tokens, minimum=1) if max_tokens is not None else self.output_limit, self.output_limit
        )
        if self.limit == 0:
            raise TokenBudgetError("The session model-token budget is zero; deterministic summary remains available.")
        capability = getattr(self.provider, "token_budget_capability", None)
        capable = isinstance(capability, TokenBudgetCapability) and isinstance(capability.contract, TokenBudgetContract)
        if self.mode == "strict" and not capable:
            raise TokenBudgetError(
                "This provider has no verified total-token input bound; deterministic summary is used."
            )
        try:
            detached_messages, detached_tools = copy.deepcopy(messages), copy.deepcopy(tools)
        except Exception as exc:
            if self.mode == "strict":
                raise TokenBudgetError("Strict provider request cannot be detached exactly.") from exc
            detached_messages, detached_tools = messages, tools
        try:
            digest = token_request_sha256(
                self.provider, system, detached_messages, detached_tools, allow_native=self.mode == "reported"
            )
        except TokenRequestTooLargeError:
            raise
        except TokenBudgetError:
            if self.mode == "strict":
                raise
            digest = None  # Truthful unknown identity; never used as a strict input-bound proof.
        input_bound = 0
        if self.mode == "strict":
            try:
                bound = capability.input_token_upper_bound(system, detached_messages, detached_tools)
            except Exception as exc:
                raise TokenBudgetError("Provider input-token bound is unavailable; no model request was sent.") from exc
            if not isinstance(bound, InputTokenBound) or bound.request_sha256 != digest:
                raise TokenBudgetError("Provider input-token bound does not match this exact request.")
            if digest != token_request_sha256(self.provider, system, detached_messages, detached_tools):
                raise TokenBudgetError("Provider input counting mutated the admitted request.")
            input_bound = bound.tokens
        maximum = min(maximum, self.ledger.available(self.limit) - input_bound)
        if maximum < 1:
            raise TokenBudgetError("The session token budget cannot admit another response.")
        identifier = self.ledger.reserve(input_bound + maximum, limit=self.limit, request_sha256=digest, mode=self.mode)
        try:
            turn = self.provider.complete(system, detached_messages, detached_tools, max_tokens=maximum, agent=agent)
        except Exception as exc:
            # Once dispatched, a network/status exception does not establish no billing.
            # If settlement itself fails, the durable pending reservation remains held.
            try:
                self.receipts.append(self.ledger.settle(identifier, None))
            except Exception:
                log.warning("Token settlement failed; its durable pending reservation remains held.")
            raise TokenBudgetError("Provider call failed; its token reservation is retained or charged.") from exc
        if not isinstance(turn, LLMTurn):
            self.receipts.append(self.ledger.settle(identifier, None))
            raise TokenBudgetError("Provider returned no valid turn; reserved tokens were charged.")
        accounting = turn.token_accounting if isinstance(turn.token_accounting, ReportedTokenUsage) else None
        try:
            if capable:
                total = capability.total_usage_tokens(turn)
            else:
                total = accounting.total if accounting and accounting.complete else None
            if total is not None:
                total = _integer(total)
        except Exception:
            total = None
        receipt = self.ledger.settle(identifier, total, usage=accounting)
        self.receipts.append(receipt)
        clean_usage = (
            {key: value for key, value in turn.usage.items() if type(value) is int and value >= 0}
            if isinstance(turn.usage, dict)
            else {}
        )
        for key, value in clean_usage.items():
            self.reported_usage[key] = self.reported_usage.get(key, 0) + value
        if receipt["basis"] == "overrun":
            raise TokenBudgetError("Provider usage exceeded its admitted bound; further model calls are blocked.")
        return replace(turn, usage=clean_usage)
