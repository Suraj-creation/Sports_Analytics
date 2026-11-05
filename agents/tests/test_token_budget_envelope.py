"""Known byte-envelope violations cannot become reported-mode unknown identity."""

import pytest

from bai_agents.accounting import ReportedTokenUsage
from bai_agents.budget import (
    BudgetedProvider,
    InputTokenBound,
    TokenBudgetContract,
    TokenBudgetError,
    TokenBudgetLedger,
    token_request_sha256,
)
from bai_agents.providers import LLMTurn


class Controlled:
    name, model = "controlled", "finite-token-protocol"
    contract = TokenBudgetContract()

    def __init__(self):
        self.calls = 0
        self.token_budget_capability = self

    def input_token_upper_bound(self, system, messages, tools):
        return InputTokenBound(1, token_request_sha256(self, system, messages, tools), "controlled_exact_protocol")

    def total_usage_tokens(self, turn):
        return 2

    def complete(self, *args, **kwargs):
        self.calls += 1
        return LLMTurn(
            "A",
            [],
            "stop",
            token_accounting=ReportedTokenUsage("controlled:v1", (("input", 1), ("output", 1)), 2, True),
        )


@pytest.mark.parametrize("mode", ["reported", "strict"])
@pytest.mark.parametrize("shape", ["large_system", "combined_history", "escaped_json", "opaque_history"])
def test_known_oversize_is_rejected_before_dispatch_and_charge(tmp_path, mode, shape):
    provider = Controlled()
    if shape == "large_system":
        system, messages = "x" * 1_000_001, []
    elif shape == "combined_history":
        system, messages = (
            "S",
            [{"role": "user", "content": "x" * 600_000}, {"role": "assistant", "content": "y" * 600_000}],
        )
    elif shape == "escaped_json":
        system, messages = (
            "\n" * 600_000,
            [],
        )  # UTF-8 literal bound is small, exact serialized bytes exceed the envelope.
    else:
        system, messages = "x" * 1_000_001, [{"role": "assistant", "raw": object()}]
    with TokenBudgetLedger(tmp_path / "b.sqlite", "S1") as ledger:
        with pytest.raises(TokenBudgetError) as raised:
            BudgetedProvider(provider, ledger, 50_000, mode=mode).complete(system, messages, [])
        assert getattr(raised.value, "code", None) == "request_too_large"
        assert provider.calls == 0
        assert ledger.snapshot()["spent"] == 0
        assert ledger.snapshot()["pending"] == {}
