"""Controlled token protocol and real SQLite concurrency; no neural/API calls."""

import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from bai_agents.agent import answer
from bai_agents.budget import (
    LEDGER_KEY,
    BudgetedProvider,
    InputTokenBound,
    TokenBudgetContract,
    TokenBudgetError,
    TokenBudgetLedger,
    token_request_sha256,
)
from bai_agents.providers import LLMError, LLMTurn, ToolCall
from bai_agents.tools import ToolContext
from bai_engine.schema import Session, Source, SourceKind
from bai_engine.store import EventStore, SessionRepository


class ControlledProvider:
    """Its finite token protocol is exact by construction, not a real tokenizer."""

    name, model = "controlled", "finite-token-protocol"
    contract = TokenBudgetContract()

    def __init__(self, turns=None, *, total=3, bound=2):
        self.token_budget_capability = self
        self.turns = turns or [LLMTurn("Insufficient evidence to answer.", [], "stop", usage={"input": 2, "output": 1})]
        self.calls = []
        self.total, self.bound = total, bound

    def input_token_upper_bound(self, system, messages, tools):
        return InputTokenBound(
            self.bound, token_request_sha256(self, system, messages, tools), "controlled_exact_protocol"
        )

    def total_usage_tokens(self, turn):
        return self.total

    def complete(self, system, messages, tools, *, max_tokens=4096, agent="agent"):
        self.calls.append(max_tokens)
        turn = self.turns[min(len(self.calls) - 1, len(self.turns) - 1)]
        if isinstance(turn, Exception):
            raise turn
        return turn


@pytest.fixture
def context(tmp_path):
    session = Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="unused"))
    with EventStore(tmp_path / "events.sqlite", session.session_id) as store:
        yield ToolContext(session=session, store=store, tracks=None)


@pytest.mark.parametrize("value", [-1, True, 1.5, "4000"])
def test_invalid_limits_never_dispatch(tmp_path, value):
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger, pytest.raises(TokenBudgetError):
        BudgetedProvider(ControlledProvider(), ledger, value)


def test_zero_and_unsupported_capability_use_actual_deterministic_fallback(tmp_path, context):
    for zero, unsupported in [(True, False), (False, True)]:
        provider = ControlledProvider()
        if unsupported:
            provider.token_budget_capability = None
        with TokenBudgetLedger(tmp_path / f"b{zero}.sqlite", "S1") as ledger:
            result = answer("What happened?", context, BudgetedProvider(provider, ledger, 0 if zero else 100))
            assert result.provider == "deterministic"
            assert provider.calls == []
            assert ledger.snapshot()["spent"] == 0
            assert ledger.snapshot()["pending"] == {}


def test_atomic_reservation_two_independent_connections(tmp_path):
    stores = [TokenBudgetLedger(tmp_path / "same.sqlite", "S1") for _ in range(2)]
    barrier = threading.Barrier(2)

    def reserve(ledger):
        barrier.wait()
        try:
            return ledger.reserve(10, limit=10, request_sha256="a" * 64)
        except TokenBudgetError:
            return None

    try:
        with ThreadPoolExecutor(max_workers=2) as pool:
            admitted = list(pool.map(reserve, stores))
        assert sum(value is not None for value in admitted) == 1
        assert stores[0].available(10) == 0
    finally:
        for store in stores:
            store.close()


def test_reopen_preserves_crash_reservation_and_unknown_settlement(tmp_path):
    path = tmp_path / "b.sqlite"
    with TokenBudgetLedger(path, "S1") as ledger:
        identifier = ledger.reserve(10, limit=10, request_sha256="a" * 64)
    with TokenBudgetLedger(path, "S1") as ledger:
        assert ledger.available(10) == 0
        receipt = ledger.settle(identifier, None)
        assert receipt["charged"] == 10 and receipt["basis"] == "reserved_unknown"
        assert ledger.snapshot()["spent"] == 10 and ledger.snapshot()["pending"] == {}
        assert ledger.settle(identifier, 0) == receipt
        assert ledger.snapshot()["spent"] == 10


def test_receipt_settlement_releases_only_verified_unused_envelope(tmp_path):
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        identifier = ledger.reserve(10, limit=10, request_sha256="a" * 64)
        assert ledger.settle(identifier, 3)["charged"] == 3
        assert ledger.available(10) == 7
        with pytest.raises(TokenBudgetError):
            ledger.settle("unknown", 0)
        assert ledger.available(10) == 7


def test_all_six_rounds_and_grounding_repair_are_reserved(tmp_path, context):
    tool = LLMTurn("", [ToolCall("tool", "match_overview", {})], "tool_use", usage={"input": 2, "output": 1})
    final = LLMTurn("Insufficient evidence to answer.", [], "stop", usage={"input": 2, "output": 1})
    provider = ControlledProvider([*([tool] * 6), final])
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 50_000)
        answer("What happened?", context, guard)
        assert provider.calls == [4096] * 7
        assert ledger.snapshot()["spent"] == 21
        assert ledger.snapshot()["pending"] == {}
        assert guard.reported_usage == {"input": 14, "output": 7}


def test_later_failure_keeps_earlier_usage_and_charges_uncertain_attempt(tmp_path, context):
    tool = LLMTurn("", [ToolCall("tool", "match_overview", {})], "tool_use", usage={"input": 2, "output": 1})
    provider = ControlledProvider([tool, LLMError("controlled timeout after dispatch")])
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 50_000)
        result = answer("What happened?", context, guard)
        assert result.provider == "deterministic"
        assert ledger.snapshot()["spent"] == 3 + 4098
        assert guard.reported_usage == {"input": 2, "output": 1}
        assert len(provider.calls) == 2


@pytest.mark.parametrize("total", [None, True, -1, 1.5])
def test_unknown_or_invalid_usage_debits_reservation_never_zero(tmp_path, total):
    provider = ControlledProvider(total=total)
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 10)
        guard.complete("S", [], [])
        assert provider.calls == [8]
        assert ledger.snapshot()["spent"] == 10
        with pytest.raises(TokenBudgetError):
            guard.complete("S", [], [])
        assert len(provider.calls) == 1


def test_usage_overrun_is_recorded_and_blocks_more_admission(tmp_path):
    provider = ControlledProvider(total=11)
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 10)
        with pytest.raises(TokenBudgetError, match="exceeded"):
            guard.complete("S", [], [])
        assert ledger.snapshot()["spent"] == 11
        assert ledger.snapshot()["blocked"] is True
        with pytest.raises(TokenBudgetError):
            BudgetedProvider(provider, ledger, 1000).complete("S", [], [])
        assert len(provider.calls) == 1


def test_stale_bound_and_mutating_counter_never_dispatch(tmp_path):
    for mutate in [False, True]:
        provider = ControlledProvider()

        def bound(system, messages, tools, _provider=provider, _mutate=mutate):
            digest = token_request_sha256(_provider, system, messages, tools)
            if _mutate:
                messages.append({"role": "user", "content": "changed"})
            return InputTokenBound(2, digest if _mutate else "b" * 64, "controlled_bad_counter")

        provider.input_token_upper_bound = bound
        with TokenBudgetLedger(tmp_path / f"b{mutate}.sqlite", "S1") as ledger:
            with pytest.raises(TokenBudgetError):
                BudgetedProvider(provider, ledger, 10).complete("S", [], [])
            assert provider.calls == [] and ledger.snapshot()["pending"] == {}


def test_provider_network_wait_holds_no_database_lock(tmp_path):
    provider = ControlledProvider()
    with (
        TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger,
        TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as independent,
    ):
        original = provider.complete

        def complete(*args, **kwargs):
            # A separate connection can take BEGIN IMMEDIATE while generation runs.
            with independent.store.transaction():
                independent.store.set_meta("concurrent_writer", "ran")
            return original(*args, **kwargs)

        provider.complete = complete
        BudgetedProvider(provider, ledger, 10).complete("S", [], [])
        assert independent.store.get_meta("concurrent_writer") == "ran"


def test_analysis_reset_does_not_replenish_budget_and_sessions_are_independent(tmp_path):
    repo = SessionRepository(tmp_path / "data")
    session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
    path = repo.data_dir / "llm_budget" / f"{session.session_id}.sqlite"
    with TokenBudgetLedger(path, session.session_id) as ledger:
        identifier = ledger.reserve(10, limit=10, request_sha256="a" * 64)
        ledger.settle(identifier, 7)
    repo.reset_analysis(session.session_id)
    with TokenBudgetLedger(path, session.session_id) as ledger:
        assert ledger.available(10) == 3
    with TokenBudgetLedger(repo.data_dir / "llm_budget/OTHER.sqlite", "OTHER") as ledger:
        assert ledger.available(10) == 10
    repo.close()


def test_malformed_ledger_never_defaults_to_fresh_budget(tmp_path):
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        ledger.store.set_meta(LEDGER_KEY, '{"v":2,"spent":0}')
        with pytest.raises(TokenBudgetError):
            ledger.available(1000)


def test_explicit_retry_is_a_separately_reserved_attempt(tmp_path):
    provider = ControlledProvider([LLMError("uncertain first attempt"), LLMTurn("A", [], "stop")])
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 20)
        with pytest.raises(TokenBudgetError):
            guard.complete("S", [], [], max_tokens=4)
        guard.complete("S", [], [], max_tokens=4)
        assert provider.calls == [4, 4]
        assert ledger.snapshot()["spent"] == 6 + 3
        assert len(ledger.snapshot()["closed"]) == 2


def test_reservations_are_atomic_between_independent_processes(tmp_path):
    import subprocess
    import sys

    path = tmp_path / "b.sqlite"
    with TokenBudgetLedger(path, "S1") as ledger:
        assert ledger.available(10) == 10
    code = """
from pathlib import Path
import sys
from bai_agents.budget import TokenBudgetLedger, TokenBudgetError
with TokenBudgetLedger(Path(sys.argv[1]), 'S1') as ledger:
    try:
        ledger.reserve(10, limit=10, request_sha256='a'*64)
        print('admitted')
    except TokenBudgetError:
        print('denied')
"""

    def request(_):
        return subprocess.run(
            [sys.executable, "-c", code, str(path)], check=True, capture_output=True, text=True, timeout=20
        ).stdout.strip()

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(request, range(2))) == ["admitted", "denied"]
    with TokenBudgetLedger(path, "S1") as ledger:
        assert ledger.available(10) == 0
