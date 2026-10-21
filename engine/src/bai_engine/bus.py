"""Message bus between the API process and the engine.

Two channels of communication:

* **Pub/sub** (engine → API → browsers): per-session topics such as ``session.<id>.events``.
  Publishing is synchronous and thread-safe because the engine runs perception on worker
  threads; subscribing is async because the API fans out over WebSockets.
* **Commands** (API → engine): an ordered queue of control messages (start, playhead, seek,
  stop).  The engine consumes them on a blocking thread.

``LocalBus`` is used in single-process mode (development, tests); ``RedisBus`` when the engine
runs in its own container (``BAI_REDIS_URL`` set).  Messages are plain JSON-compatible dicts;
binary payloads (track windows) are passed as ``bytes`` values and survive both transports
(msgpack encoding on Redis).
"""

from __future__ import annotations

import asyncio
import contextlib
import queue
import threading
from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from typing import Any

import msgpack

Message = dict[str, Any]


def topic(session_id: str, kind: str) -> str:
    return f"session.{session_id}.{kind}"


class Bus(ABC):
    @abstractmethod
    def publish(self, channel: str, message: Message) -> None: ...

    @abstractmethod
    def subscribe(self, channel: str) -> AsyncIterator[Message]: ...

    @abstractmethod
    def send_command(self, command: Message) -> None: ...

    @abstractmethod
    def next_command(self, timeout: float | None = None) -> Message | None: ...

    def close(self) -> None:  # noqa: B027 - optional hook
        pass


class LocalBus(Bus):
    def __init__(self, max_queue: int = 2048) -> None:
        self._subs: dict[str, set[tuple[asyncio.AbstractEventLoop, asyncio.Queue[Message]]]] = {}
        self._lock = threading.Lock()
        self._commands: queue.Queue[Message] = queue.Queue()
        self._max_queue = max_queue

    def publish(self, channel: str, message: Message) -> None:
        with self._lock:
            targets = list(self._subs.get(channel, ()))
        for loop, q in targets:
            if loop.is_closed():
                continue
            with contextlib.suppress(RuntimeError):
                loop.call_soon_threadsafe(_offer, q, message)

    async def subscribe(self, channel: str) -> AsyncIterator[Message]:  # type: ignore[override]
        loop = asyncio.get_running_loop()
        q: asyncio.Queue[Message] = asyncio.Queue(maxsize=self._max_queue)
        entry = (loop, q)
        with self._lock:
            self._subs.setdefault(channel, set()).add(entry)
        try:
            while True:
                yield await q.get()
        finally:
            with self._lock:
                subs = self._subs.get(channel)
                if subs is not None:
                    subs.discard(entry)
                    if not subs:
                        del self._subs[channel]

    def subscriber_count(self, channel: str) -> int:
        with self._lock:
            return len(self._subs.get(channel, ()))

    def send_command(self, command: Message) -> None:
        self._commands.put(command)

    def next_command(self, timeout: float | None = None) -> Message | None:
        try:
            return self._commands.get(timeout=timeout)
        except queue.Empty:
            return None


def _offer(q: asyncio.Queue[Message], message: Message) -> None:
    """Drop the oldest message when a slow subscriber's queue is full (live data, not a log).

    Subscribers that need completeness (the event stream) recover via ``last_seq`` replay.
    """
    if q.full():
        with contextlib.suppress(asyncio.QueueEmpty):
            q.get_nowait()
    q.put_nowait(message)


class RedisBus(Bus):
    COMMAND_KEY = "bai:engine:commands"

    def __init__(self, url: str) -> None:
        import redis
        import redis.asyncio as aredis

        self._url = url
        self._sync = redis.Redis.from_url(url)
        self._aredis = aredis
        self._sync.ping()

    @staticmethod
    def _pack(m: Message) -> bytes:
        return msgpack.packb(m, use_bin_type=True)

    @staticmethod
    def _unpack(b: bytes) -> Message:
        out = msgpack.unpackb(b, raw=False)
        assert isinstance(out, dict)
        return out

    def publish(self, channel: str, message: Message) -> None:
        self._sync.publish(channel, self._pack(message))

    async def subscribe(self, channel: str) -> AsyncIterator[Message]:  # type: ignore[override]
        client = self._aredis.Redis.from_url(self._url)
        pubsub = client.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for item in pubsub.listen():
                if item.get("type") == "message":
                    yield self._unpack(item["data"])
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()
            await client.aclose()

    def send_command(self, command: Message) -> None:
        self._sync.rpush(self.COMMAND_KEY, self._pack(command))

    def next_command(self, timeout: float | None = None) -> Message | None:
        res = self._sync.blpop([self.COMMAND_KEY], timeout=int(timeout) if timeout else 0)
        if res is None:
            return None
        return self._unpack(res[1])

    def close(self) -> None:
        self._sync.close()


def make_bus(redis_url: str | None) -> Bus:
    return RedisBus(redis_url) if redis_url else LocalBus()
