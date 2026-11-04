"""Mocked Redis adapter contract; these tests do not exercise a Redis service."""

from types import SimpleNamespace

import pytest

from bai_engine.bus import RedisBus


@pytest.mark.parametrize("timeout", [0.01, 0.5, 1.5])
def test_redis_finite_command_timeout_is_not_rounded_to_infinite_wait(timeout):
    recorded = []
    bus = object.__new__(RedisBus)
    bus._sync = SimpleNamespace(blpop=lambda keys, **kwargs: recorded.append((keys, kwargs)))
    assert bus.next_command(timeout=timeout) is None
    assert recorded == [([bus.COMMAND_KEY], {"timeout": timeout})]
