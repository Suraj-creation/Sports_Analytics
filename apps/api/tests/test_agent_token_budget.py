from fastapi.testclient import TestClient

from bai_agents.budget import InputTokenBound, TokenBudgetContract, TokenBudgetLedger, token_request_sha256
from bai_agents.providers import LLMTurn, ToolCall
from bai_api.app import create_app
from bai_api.routes import agents
from bai_engine.config import REPO_ROOT, Settings
from bai_engine.schema import Event, Provenance, Session, Source, SourceKind


class Controlled:
    name, model = "controlled", "finite-token-protocol"
    contract = TokenBudgetContract()

    def __init__(self):
        self.calls = 0
        self.token_budget_capability = self
        self.action = None

    def input_token_upper_bound(self, system, messages, tools):
        return InputTokenBound(1, token_request_sha256(self, system, messages, tools), "controlled_exact_protocol")

    def total_usage_tokens(self, turn):
        return 2

    def complete(self, system, messages, tools, *, max_tokens=4096, agent="agent"):
        self.calls += 1
        assert max_tokens >= 1
        if self.action:
            return self.action()
        return LLMTurn("Insufficient evidence to answer.", [], "stop", usage={"input": 1, "output": 1})


def settings(tmp_path, limit=5, mode="strict"):
    return Settings(
        data_dir=tmp_path / "data",
        models_dir=REPO_ROOT / "models",
        llm_budget_tokens_per_session=limit,
        llm_budget_mode=mode,
        _env_file=None,
    )


def test_real_http_budget_exhaustion_and_unsupported_provider_fall_back(tmp_path, monkeypatch):
    config = settings(tmp_path)
    with TestClient(create_app(config, start_engine=False)) as client:
        repo = client.app.state.repo
        session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
        provider = Controlled()
        monkeypatch.setattr(agents, "_provider", lambda: provider)
        for _ in range(2):
            response = client.post(f"/api/sessions/{session.session_id}/ask", json={"question": "What happened?"})
            assert response.status_code == 200 and response.json()["provider"] == "controlled"
        response = client.post(f"/api/sessions/{session.session_id}/ask", json={"question": "What happened?"})
        assert response.status_code == 200 and response.json()["provider"] == "deterministic"
        assert provider.calls == 2
        path = repo.data_dir / "llm_budget" / f"{session.session_id}.sqlite"
        with TokenBudgetLedger(path, session.session_id) as ledger:
            assert ledger.snapshot()["spent"] == 4
        provider.token_budget_capability = None
        response = client.post(f"/api/sessions/{session.session_id}/ask", json={"question": "What happened?"})
        assert response.json()["provider"] == "deterministic" and provider.calls == 2


def test_withheld_stale_answer_keeps_all_model_calls_charged(tmp_path, monkeypatch):
    config = settings(tmp_path, 100)
    with TestClient(create_app(config, start_engine=False)) as client:
        repo = client.app.state.repo
        session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
        provider = Controlled()

        def action():
            if provider.calls == 1:
                return LLMTurn(
                    "", [ToolCall("read", "match_overview", {})], "tool_use", usage={"input": 1, "output": 1}
                )
            repo.events(session.session_id).append(
                Event(
                    session_id=session.session_id,
                    type="contact",
                    frame_start=1,
                    frame_end=1,
                    pts_us=33334,
                    provenance=Provenance(model="controlled"),
                )
            )
            return LLMTurn("Insufficient evidence to answer.", [], "stop", usage={"input": 1, "output": 1})

        provider.action = action
        monkeypatch.setattr(agents, "_provider", lambda: provider)
        response = client.post(f"/api/sessions/{session.session_id}/ask", json={"question": "What happened?"})
        assert response.status_code == 200 and response.json()["grounded"] is False
        assert response.json()["issues"] == ["analysis changed during answer"]
        with TokenBudgetLedger(
            repo.data_dir / "llm_budget" / f"{session.session_id}.sqlite", session.session_id
        ) as ledger:
            assert ledger.snapshot()["spent"] == 4
            assert ledger.snapshot()["pending"] == {}


def test_default_reported_mode_keeps_noncapable_provider_and_discloses_policy(tmp_path, monkeypatch):
    from bai_agents.accounting import ReportedTokenUsage

    config = settings(tmp_path, 40_000, mode="reported")
    provider = Controlled()
    provider.token_budget_capability = None
    provider.default_output_tokens = 16000
    captured = []

    def complete(system, messages, tools, *, max_tokens=16000, agent="agent"):
        captured.append(max_tokens)
        return LLMTurn(
            "Insufficient evidence to answer.",
            [],
            "stop",
            usage={"input": 1, "output": 1},
            token_accounting=ReportedTokenUsage("controlled-native:v1", (("input", 1), ("output", 1)), 2, True),
        )

    provider.complete = complete
    with TestClient(create_app(config, start_engine=False)) as client:
        repo = client.app.state.repo
        session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
        monkeypatch.setattr(agents, "_provider", lambda: provider)
        info = client.get(f"/api/sessions/{session.session_id}/ask/provider").json()
        assert info["available"] and not info["token_budget"]["strict_input_bound_available"]
        assert info["token_budget"]["output_limit"] == 16000
        assert "not_a_total_billing_hard_cap" in info["token_budget"]["semantics"]
        result = client.post(f"/api/sessions/{session.session_id}/ask", json={"question": "What happened?"}).json()
        assert result["provider"] == "controlled" and captured == [16000]


def test_strict_policy_availability_is_explicit_for_unsupported_native(tmp_path, monkeypatch):
    config = settings(tmp_path, 100, mode="strict")
    provider = Controlled()
    provider.token_budget_capability = None
    with TestClient(create_app(config, start_engine=False)) as client:
        repo = client.app.state.repo
        session = repo.save(Session(title="Controlled", source=Source(kind=SourceKind.UPLOAD, uri="unused")))
        monkeypatch.setattr(agents, "_provider", lambda: provider)
        info = client.get(f"/api/sessions/{session.session_id}/ask/provider").json()
        assert not info["available"] and info["configured_available"]
        result = client.post(f"/api/sessions/{session.session_id}/ask", json={"question": "What happened?"}).json()
        assert result["provider"] == "deterministic" and provider.calls == 0
