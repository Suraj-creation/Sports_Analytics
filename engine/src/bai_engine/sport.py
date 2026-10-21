"""Sport plugin protocol — the boundary between the sport-agnostic platform and a sport.

The platform owns media, decoding, scheduling, storage, transport and observability; a sport
plugin owns perception models, the temporal/semantic engine, rules and analytics.  Badminton is
the only implementation (``bai_badminton.plugin``); a new sport implements these two protocols.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Protocol

from bai_engine.config import Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import Event, Session, TrackSample
from bai_engine.store import EventStore

EmitFn = Callable[[list[Event]], None]


class SportSession(Protocol):
    """One session's sport-specific runtime (perception + temporal engine)."""

    def seed(self, keyframes: list[Any]) -> None:
        """Warm start from frames sampled across the video (background models, calibration proposal)."""

    def perceive(self, chunk: DecodedChunk) -> Any:
        """Run perception on a decoded chunk (GPU-heavy, may run out of order for seek previews)."""

    def ingest(self, perception: Any) -> None:
        """Feed perception **in frame order** to the temporal engine."""

    def flush(self) -> None: ...

    def drain_tracks(self) -> list[TrackSample]: ...

    def tracks_from_perception(self, perception: Any) -> list[TrackSample]:
        """Overlay tracks for a perception result without semantics (seek previews)."""

    def handle(self, command: dict[str, Any]) -> dict[str, Any]:
        """Session commands: calibrate, correct, … Returns a JSON-able result."""

    def encode_perception(self, perception: Any) -> bytes: ...

    def decode_perception(self, data: bytes) -> Any: ...

    @property
    def in_play(self) -> bool: ...

    def public_state(self) -> dict[str, Any]: ...

    def analytics(self) -> dict[str, Any]: ...

    def degraded(self) -> list[dict[str, str]]: ...


class SportPlugin(Protocol):
    name: str

    def create_session(
        self,
        session: Session,
        store: EventStore,
        profile: Profile,
        registry: ModelRegistry,
        emit: EmitFn,
    ) -> SportSession: ...


_REGISTRY: dict[str, SportPlugin] = {}


def register(plugin: SportPlugin) -> None:
    _REGISTRY[plugin.name] = plugin


def get_plugin(name: str) -> SportPlugin:
    """Resolve a sport plugin, discovering installed plugins via the ``bai.sports`` entry point."""
    if name not in _REGISTRY:
        from importlib.metadata import entry_points

        for ep in entry_points(group="bai.sports"):
            if ep.name == name:
                plugin = ep.load()
                register(plugin() if isinstance(plugin, type) else plugin)
    if name not in _REGISTRY:
        raise KeyError(f"no sport plugin registered for {name!r} (install its package)")
    return _REGISTRY[name]
