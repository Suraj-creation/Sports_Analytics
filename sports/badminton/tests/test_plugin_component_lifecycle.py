"""The sport session owns component shutdown; repositories own their stores."""

from types import SimpleNamespace

import pytest

from bai_badminton.plugin import BadmintonSession


def _session(calls, *, with_format=False, format_fails=False):
    session = BadmintonSession.__new__(BadmintonSession)
    session.perception = SimpleNamespace(close=lambda: calls.append("perception"))
    session.engine = SimpleNamespace(close=lambda: calls.append("engine"))
    if with_format:

        def close_format():
            calls.append("format")
            if format_fails:
                raise RuntimeError("controlled format close failure")

        session._format_handle = SimpleNamespace(close=close_format)
    return session


def test_sport_session_closes_components_once_without_closing_external_store():
    calls = []
    session = _session(calls)
    session.close()
    session.close()
    assert calls == ["engine", "perception"]


def test_format_provider_lifecycle_is_included():
    calls = []
    session = _session(calls, with_format=True)
    session.close()
    assert calls == ["engine", "format", "perception"]


def test_component_failure_still_closes_remaining_models():
    calls = []
    session = _session(calls, with_format=True, format_fails=True)
    with pytest.raises(RuntimeError, match="controlled"):
        session.close()
    assert calls == ["engine", "format", "perception"]
