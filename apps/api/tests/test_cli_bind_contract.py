"""CLI bind overrides must reach the application's authentication configuration."""

from argparse import Namespace

import pytest

from bai_api.auth import Auth
from bai_api.cli import _serve
from bai_engine.config import Settings


def test_nonloopback_cli_override_cannot_bypass_passphrase_guard(monkeypatch):
    import uvicorn

    import bai_api.app
    import bai_engine.config

    settings = Settings(bind_host="127.0.0.1", passphrase=None, _env_file=None)
    monkeypatch.setattr(bai_engine.config, "get_settings", lambda: settings)
    launched = []

    def app(effective):
        Auth(effective)  # the same guard invoked by the real app lifespan
        return object()

    monkeypatch.setattr(bai_api.app, "create_app", app)
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: launched.append(kwargs))
    with pytest.raises(RuntimeError, match="BAI_PASSPHRASE"):
        _serve(Namespace(host="0.0.0.0", port=None))
    assert launched == []


def test_cli_app_and_listener_use_the_same_explicit_host_and_port(monkeypatch):
    import uvicorn

    import bai_api.app
    import bai_engine.config

    settings = Settings(bind_host="127.0.0.1", port=8000, passphrase="fixture-only", _env_file=None)
    monkeypatch.setattr(bai_engine.config, "get_settings", lambda: settings)
    captured = []
    monkeypatch.setattr(bai_api.app, "create_app", lambda effective: captured.append(effective) or object())
    listener = []
    monkeypatch.setattr(uvicorn, "run", lambda *args, **kwargs: listener.append(kwargs))
    _serve(Namespace(host="0.0.0.0", port=8111))
    assert captured[0].bind_host == listener[0]["host"] == "0.0.0.0"
    assert captured[0].port == listener[0]["port"] == 8111
    assert not captured[0].is_loopback
    assert Auth(captured[0]).enabled
