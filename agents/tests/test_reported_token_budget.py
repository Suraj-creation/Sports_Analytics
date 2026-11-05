from types import SimpleNamespace

import pytest

from bai_agents.accounting import ReportedTokenUsage, anthropic_usage, openai_usage
from bai_agents.budget import BudgetedProvider, TokenBudgetError, TokenBudgetLedger
from bai_agents.providers import AnthropicProvider, LLMError, LLMTurn, OpenAICompatProvider


class ReportedProvider:
    name, model = "reported-control", "finite-token-protocol"
    default_output_tokens = 16000

    def __init__(self, accounting=None, failure=False):
        self.accounting, self.failure = accounting, failure
        self.calls = []

    def complete(self, system, messages, tools, *, max_tokens=16000, agent="agent"):
        self.calls.append(max_tokens)
        if self.failure:
            raise LLMError("controlled uncertain dispatch")
        return LLMTurn("Insufficient evidence to answer.", [], "stop", token_accounting=self.accounting)


def usage(total=3):
    return ReportedTokenUsage("controlled-total:v1", (("input", total - 1), ("output", 1)), total, True)


def test_reported_preserves_adapter_output_default_and_records_input_beyond_reservation(tmp_path):
    provider = ReportedProvider(usage(20001))
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 20_000, mode="reported")
        assert guard.complete("S", [], []).text
        assert provider.calls == [16000]
        state = ledger.snapshot()
        assert state["spent"] == 20001 and not state["blocked"]
        assert state["components"]["controlled-total:v1:input"] == 20000
        with pytest.raises(TokenBudgetError):
            guard.complete("S", [], [])
        assert provider.calls == [16000]
        # This explicit one-response overshoot is why reported mode is not a total hard cap.


def test_reported_unknown_usage_keeps_reservation_and_blocks_future_calls(tmp_path):
    provider = ReportedProvider()
    path = tmp_path / "b.sqlite"
    with TokenBudgetLedger(path, "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 20, mode="reported")
        assert guard.complete("S", [], []).text
        state = ledger.snapshot()
        assert state["blocked"] and len(state["pending"]) == 1
        assert next(iter(state["pending"].values()))["uncertain"] is True
        assert not state["closed"]  # No invented zero-token settlement.
    with TokenBudgetLedger(path, "S1") as ledger:
        with pytest.raises(TokenBudgetError):
            BudgetedProvider(provider, ledger, 20_000, mode="reported").complete("S", [], [])
        assert provider.calls == [20]


def test_reported_failure_retains_uncertain_budget_and_has_no_automatic_retry(tmp_path):
    provider = ReportedProvider(failure=True)
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 20, mode="reported")
        with pytest.raises(TokenBudgetError):
            guard.complete("S", [], [])
        with pytest.raises(TokenBudgetError):
            guard.complete("S", [], [])
        assert provider.calls == [20]
        assert ledger.snapshot()["blocked"]


def test_reported_inflight_unknown_input_blocks_other_connection_without_holding_writer_lock(tmp_path):
    provider = ReportedProvider(usage())
    path = tmp_path / "b.sqlite"
    with TokenBudgetLedger(path, "S1") as first, TokenBudgetLedger(path, "S1") as second:
        original = provider.complete

        def complete(*args, **kwargs):
            with second.store.transaction():
                second.store.set_meta("concurrent_writer", "unblocked")
            with pytest.raises(TokenBudgetError):
                BudgetedProvider(ReportedProvider(usage()), second, 30_000, mode="reported").complete("S", [], [])
            return original(*args, **kwargs)

        provider.complete = complete
        BudgetedProvider(provider, first, 30_000, mode="reported").complete("S", [], [])
        assert first.snapshot()["spent"] == 3
        assert second.store.get_meta("concurrent_writer") == "unblocked"


def test_openai_total_includes_cache_subsets_without_double_counting():
    raw = SimpleNamespace(
        prompt_tokens=12,
        completion_tokens=3,
        total_tokens=15,
        prompt_tokens_details=SimpleNamespace(cached_tokens=7, cache_write_tokens=2),
    )
    record = openai_usage(raw)
    assert record.complete and record.total == 15
    assert dict(record.components) == {
        "input": 12,
        "output": 3,
        "provider_total": 15,
        "cache_read_subset": 7,
        "cache_write_subset": 2,
    }
    assert ReportedTokenUsage.from_dict(record.to_dict()) == record


def test_anthropic_disjoint_caches_are_counted_and_missing_not_zero():
    raw = SimpleNamespace(
        input_tokens=10, output_tokens=3, cache_read_input_tokens=20, cache_creation_input_tokens=5, iterations=None
    )
    record = anthropic_usage(raw)
    assert record.complete and record.total == 38
    raw.cache_creation_input_tokens = None
    record = anthropic_usage(raw)
    assert not record.complete and record.total is None
    assert record.missing == ("cache_write",)
    assert "cache_write" not in dict(record.components)


@pytest.mark.parametrize(
    "raw",
    [
        None,
        SimpleNamespace(prompt_tokens=12, completion_tokens=3, total_tokens=14),
        SimpleNamespace(prompt_tokens=True, completion_tokens=3, total_tokens=4),
    ],
)
def test_missing_or_inconsistent_vendor_usage_is_unknown(raw):
    assert openai_usage(raw).complete is False
    assert openai_usage(raw).total is None


def test_partial_anthropic_usage_is_persisted_but_blocks_future_generation(tmp_path):
    partial = anthropic_usage(SimpleNamespace(input_tokens=2, output_tokens=3, cache_read_input_tokens=4))
    provider = ReportedProvider(partial)
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        BudgetedProvider(provider, ledger, 20, mode="reported").complete("S", [], [])
        state = ledger.snapshot()
        assert state["blocked"]
        assert state["components"]["anthropic-disjoint-input-cache-output:v1:cache_read"] == 4
        pending = next(iter(state["pending"].values()))
        assert pending["usage"]["missing"] == ["cache_write"]


def test_actual_compat_adapter_carries_typed_usage_without_real_client_calls(tmp_path):
    response = SimpleNamespace(
        usage=SimpleNamespace(prompt_tokens=12, completion_tokens=3, total_tokens=15),
        model="controlled",
        choices=[
            SimpleNamespace(
                message=SimpleNamespace(content="Insufficient evidence to answer.", tool_calls=[]), finish_reason="stop"
            )
        ],
    )
    captured = []

    def create(**kwargs):
        captured.append(kwargs)
        return response

    client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=create)))
    provider = OpenAICompatProvider(client, "controlled", "openai")
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        turn = BudgetedProvider(provider, ledger, 100, mode="reported").complete("S", [], [])
        assert turn.token_accounting.total == 15
        assert ledger.snapshot()["spent"] == 15
        assert captured[0]["max_tokens"] == 100


def test_actual_anthropic_refusal_retains_usage_and_cache_write_without_remote_calls(tmp_path):
    response = SimpleNamespace(
        usage=SimpleNamespace(
            input_tokens=10, output_tokens=3, cache_read_input_tokens=20, cache_creation_input_tokens=5
        ),
        model="controlled",
        stop_reason="refusal",
        content=[],
    )
    provider = AnthropicProvider.__new__(AnthropicProvider)
    provider._anthropic = SimpleNamespace()
    provider.client = SimpleNamespace(beta=SimpleNamespace(messages=SimpleNamespace(create=lambda **kwargs: response)))
    provider.model, provider.effort, provider.fallbacks = "controlled", "medium", False
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        turn = BudgetedProvider(provider, ledger, 100, mode="reported").complete("S", [], [])
        assert turn.stop_reason == "refusal" and turn.usage["cache_write"] == 5
        assert ledger.snapshot()["spent"] == 38


def test_reported_accepts_native_sdk_history_without_claiming_strict_bound(tmp_path):
    from anthropic.types import TextBlock

    provider = ReportedProvider(usage())
    history = [{"role": "assistant", "content": "A", "raw": [TextBlock(type="text", text="A")]}]
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        BudgetedProvider(provider, ledger, 20, mode="reported").complete("S", history, [])
        assert ledger.snapshot()["spent"] == 3
        assert ledger.snapshot()["closed"][0]["mode"] == "reported"


@pytest.mark.parametrize("subset", ["cached_tokens", "cache_write_tokens"])
def test_cache_subset_exceeding_prompt_is_unknown_and_never_invented_zero(tmp_path, subset):
    raw = SimpleNamespace(
        prompt_tokens=12, completion_tokens=3, total_tokens=15, prompt_tokens_details=SimpleNamespace(**{subset: 13})
    )
    record = openai_usage(raw)
    assert record.complete is False and record.total is None
    key = "cache_read_subset" if subset == "cached_tokens" else "cache_write_subset"
    assert dict(record.components)[key] == 13
    assert f"{key}_exceeds_input" in record.missing
    provider = ReportedProvider(record)
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        guard = BudgetedProvider(provider, ledger, 100, mode="reported")
        guard.complete("S", [], [])
        assert ledger.snapshot()["blocked"] and len(ledger.snapshot()["pending"]) == 1
        with pytest.raises(TokenBudgetError):
            guard.complete("S", [], [])
        assert len(provider.calls) == 1
