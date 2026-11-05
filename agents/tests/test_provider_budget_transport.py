"""No clients or remote calls are real; inspect actual constructor arguments."""

from types import SimpleNamespace

import pytest

from bai_agents import providers


@pytest.mark.parametrize("name", ["openai", "azure_openai", "local", "anthropic"])
def test_provider_clients_have_one_bounded_transport_attempt(monkeypatch, name):
    import anthropic
    import openai

    import bai_engine.config

    monkeypatch.setattr(bai_engine.config, "get_settings", lambda: SimpleNamespace(model_fields_set=set()))

    calls = []

    def construct(**kwargs):
        calls.append(kwargs)
        return SimpleNamespace()

    monkeypatch.setattr(anthropic, "Anthropic", construct)
    monkeypatch.setattr(openai, "OpenAI", construct)
    monkeypatch.setattr(openai, "AzureOpenAI", construct)
    monkeypatch.setenv("BAI_LOCAL_LLM_KEY", "controlled-placeholder")
    monkeypatch.setenv("OPENAI_API_KEY", "controlled-placeholder")
    monkeypatch.setenv("AZURE_OPENAI_API_KEY", "controlled-placeholder")
    monkeypatch.setenv("AZURE_OPENAI_ENDPOINT", "https://controlled.invalid")
    providers.make_provider(name)
    assert len(calls) == 1
    assert calls[0].get("max_retries") == 0
    assert calls[0].get("timeout") == 30.0
