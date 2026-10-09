import asyncio
import threading

import pytest

from bai_engine.bus import LocalBus, topic
from bai_engine.config import REPO_ROOT, load_profile


async def test_local_bus_fanout_from_thread() -> None:
    bus = LocalBus()
    ch = topic("S1", "events")
    got: list[dict[str, object]] = []

    async def consume() -> None:
        async for m in bus.subscribe(ch):
            got.append(m)
            if len(got) == 3:
                return

    task = asyncio.create_task(consume())
    while bus.subscriber_count(ch) == 0:
        await asyncio.sleep(0.001)
    t = threading.Thread(target=lambda: [bus.publish(ch, {"i": i, "bin": b"\x00\x01"}) for i in range(3)])
    t.start()
    await asyncio.wait_for(task, 2)
    t.join()
    assert [m["i"] for m in got] == [0, 1, 2]
    assert got[0]["bin"] == b"\x00\x01"
    await asyncio.sleep(0)
    assert bus.subscriber_count(ch) == 0  # unsubscribed on exit


async def test_slow_subscriber_drops_oldest() -> None:
    bus = LocalBus(max_queue=2)
    ch = "c"
    agen = bus.subscribe(ch).__aiter__()
    first = asyncio.create_task(agen.__anext__())
    while bus.subscriber_count(ch) == 0:
        await asyncio.sleep(0.001)
    for i in range(5):
        bus.publish(ch, {"i": i})
    await asyncio.sleep(0.01)
    # queue capped at 2 → only the newest two survive, in order
    assert (await first)["i"] == 3
    assert (await agen.__anext__())["i"] == 4
    await agen.aclose()


def test_commands_queue() -> None:
    bus = LocalBus()
    assert bus.next_command(timeout=0.01) is None
    bus.send_command({"cmd": "seek", "frame": 10})
    assert bus.next_command(timeout=0.1) == {"cmd": "seek", "frame": 10}


@pytest.mark.parametrize("name", ["cpu-dev", "gpu-rtx4000", "gpu-high"])
def test_profiles_load(name: str) -> None:
    p = load_profile(name, REPO_ROOT / "config" / "profiles")
    assert p.name == name
    assert p.chunk_frames % p.shuttle.params.get("seq_len", 8) == 0
    assert 0 <= p.escalation_budget <= 1


def test_unknown_profile() -> None:
    with pytest.raises(FileNotFoundError):
        load_profile("nope", REPO_ROOT / "config" / "profiles")
