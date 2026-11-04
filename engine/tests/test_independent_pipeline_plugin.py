"""Run an independent analytics pipeline through the unchanged generic host.

Only decoded pixels/HLS availability are controlled. Configuration loading,
plugin selection, component factories, cache handling, ordered ingestion, event
storage, progress and transport all execute through their production paths.
There are no badminton model settings, sport imports or physical contact claims.
"""

import builtins
import json
from dataclasses import dataclass
from fractions import Fraction
from typing import Protocol, runtime_checkable

import numpy as np
import pytest

from bai_engine import sport
from bai_engine.bus import LocalBus
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.config import Settings
from bai_engine.decode import DecodedChunk
from bai_engine.media.proxy import HlsStatus, ProxyPlan
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.runtime.runner import SessionRunner
from bai_engine.schema import Event, MediaInfo, Provenance, Session, SessionStatus, Source, SourceKind
from bai_engine.store import SessionRepository


@runtime_checkable
class _IntensityPort(Protocol):
    def measure(self, image: np.ndarray) -> float: ...


@dataclass
class _Context:
    fps: float


class _Intensity:
    def __init__(self, use_peak):
        self.use_peak = use_peak
        self.calls = 0

    def measure(self, image):
        self.calls += 1
        return float(image.max() if self.use_peak else image.mean())


@dataclass
class _SensorChunk:
    start: int
    end: int
    values: list[float]


class _MachineSession:
    requires_sequential_perception = False

    def __init__(self, session, store, profile, registry, emit, components):
        self.session, self.store, self.emit = session, store, emit
        assert session.media is not None
        self.fps = float(session.media.fps)
        choice = profile.components["intensity"]
        self.threshold = float(choice.params["threshold"])
        self.component_handle = components.create(
            "intensity",
            choice.implementation,
            context=_Context(self.fps),
            configuration=choice.model_dump(mode="json"),
            match_format="video",
            context_identity={"source": session.source.sha256, "fps": self.fps},
        )
        self.ingested = []
        self.activity_frames = []
        self.flushed = False

    def seed(self, keyframes):
        assert keyframes == []

    def perceive(self, chunk):
        return _SensorChunk(
            chunk.start, chunk.end, [self.component_handle.instance.measure(frame) for frame in chunk.frames]
        )

    def ingest(self, perception):
        assert perception.start == len(self.ingested)
        events = []
        for index, value in enumerate(perception.values, perception.start):
            self.ingested.append(index)
            if value >= self.threshold:
                self.activity_frames.append(index)
                events.append(
                    self.store.append(
                        Event(
                            session_id=self.session.session_id,
                            type="machine.illumination",
                            frame_start=index,
                            frame_end=index,
                            pts_us=round(index / self.fps * 1_000_000),
                            payload={"intensity": value, "component": self.component_handle.contract.implementation},
                            provenance=Provenance(
                                model="sensor-component@1", params_hash=self.component_handle.fingerprint
                            ),
                        )
                    )
                )
        if events:
            self.emit(events)

    def flush(self):
        self.flushed = True

    def drain_tracks(self):
        return []

    def tracks_from_perception(self, perception):
        return []

    def handle(self, command):
        return {"ok": False, "error": "unsupported sensor command"}

    def encode_perception(self, perception):
        return json.dumps(
            {
                "start": perception.start,
                "end": perception.end,
                "values": perception.values,
                "fingerprint": self.component_handle.fingerprint,
            }
        ).encode()

    def decode_perception(self, data):
        raw = json.loads(data)
        if raw.pop("fingerprint") != self.component_handle.fingerprint:
            raise ValueError("sensor component configuration changed")
        return _SensorChunk(**raw)

    @property
    def in_play(self):
        return False

    def public_state(self):
        return {"activity_frames": list(self.activity_frames)}

    def analytics(self):
        return {"illuminated_frames": len(self.activity_frames)}

    def degraded(self):
        return []

    def capabilities(self):
        return {
            "pipeline": {
                "name": "machine-sensor",
                "version": "1",
                "format": "video",
                "stages": [{"id": "intensity", "depends_on": []}, {"id": "threshold", "depends_on": ["intensity"]}],
            },
            "intensity": {
                "contract": self.component_handle.contract.describe(),
                "fingerprint": self.component_handle.fingerprint,
            },
        }


class _MachinePlugin:
    name = "machine-sensor"

    def __init__(self):
        self.instances = []
        self.components = ComponentRegistry()
        for implementation, use_peak in (("mean", False), ("peak", True)):
            self.components.register(
                ComponentContract(
                    kind="intensity",
                    implementation=implementation,
                    version="1",
                    input_schema="bgr-analysis-frame:v1",
                    output_schema="scalar-intensity:v1",
                    interface=_IntensityPort,
                    context_type=_Context,
                    supported_formats=frozenset({"video"}),
                    failure_policy="unavailable",
                ),
                lambda context, config, use_peak=use_peak: _Intensity(use_peak),
            )

    def create_session(self, session, store, profile, registry, emit):
        created = _MachineSession(session, store, profile, registry, emit, self.components)
        self.instances.append(created)
        return created


def _runner(tmp_path, monkeypatch, plugin, implementation):
    tmp_path.mkdir(parents=True, exist_ok=True)
    profiles = tmp_path / "profiles"
    profiles.mkdir()
    (profiles / "sensor.yaml").write_text(
        "name: sensor\ncomponents:\n  intensity:\n    model: none\n    backend: none\n"
        f"    implementation: {implementation}\n    params: {{threshold: 128}}\n",
        encoding="utf-8",
    )
    settings = Settings(data_dir=tmp_path / "data", profiles_dir=profiles, _env_file=None)
    repo = SessionRepository(settings.data_dir)
    saved = repo.save(
        Session(
            title="Independent sensor",
            sport=plugin.name,
            profile="sensor",
            players=[],
            source=Source(kind=SourceKind.UPLOAD, uri="controlled-frames", sha256="f" * 64),
            media=MediaInfo(fps_num=2, fps_den=1, n_frames=4, width=4, height=4, duration_us=2_000_000),
        )
    )
    bus = LocalBus()
    messages = []
    monkeypatch.setattr(bus, "publish", lambda channel, message: messages.append((channel, message)))
    models = tmp_path / "models"
    models.mkdir()
    (models / "manifest.yaml").write_text("models: {}\n", encoding="utf-8")
    runner = SessionRunner(saved.session_id, repo, bus, settings, ModelRegistry(models))
    runner.plan = ProxyPlan(Fraction(2), 4, 2, "controlled", False)
    monkeypatch.setattr(runner, "_sample_keyframes", lambda: [])
    return runner, repo, messages


def _control_media(monkeypatch):
    class Decoder:
        def __init__(self, paths, frames_per_segment):
            assert frames_per_segment == 2

        def decode_segment(self, index):
            frame = np.zeros((4, 4, 3), dtype=np.uint8)
            frame[0, 0] = 255
            return DecodedChunk(index * 2, [frame.copy(), frame.copy()])

    monkeypatch.setattr("bai_engine.runtime.runner.SegmentDecoder", Decoder)
    monkeypatch.setattr("bai_engine.runtime.runner.hls_status", lambda paths: HlsStatus(2, True, (1.0, 1.0)))
    real_import = builtins.__import__

    def no_domain_import(name, *args, **kwargs):
        assert not name.startswith("bai_badminton"), "the generic host imported a specific sport"
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", no_domain_import)


@pytest.mark.parametrize("implementation,expected", [("mean", []), ("peak", [0, 1, 2, 3])])
def test_non_sport_pipeline_executes_from_profile_through_host_and_persists_results(
    tmp_path, monkeypatch, implementation, expected
):
    plugin = _MachinePlugin()
    monkeypatch.setitem(sport._REGISTRY, plugin.name, plugin)
    runner, repo, messages = _runner(tmp_path, monkeypatch, plugin, implementation)
    _control_media(monkeypatch)
    try:
        runner._analyse()
        saved = repo.get(runner.session_id)
        assert saved.status is SessionStatus.ANALYSED
        assert saved.analysed_frames == 4 and saved.frontier_frame == 3
        assert saved.players == [] and saved.roster is None
        assert saved.meta["capabilities"]["pipeline"]["name"] == plugin.name
        assert runner.sport.ingested == [0, 1, 2, 3] and runner.sport.flushed
        assert runner.sport.component_handle.instance.calls == 4
        assert [event.frame_start for event in repo.events(saved.session_id).query()] == expected
        state = [message for _, message in messages if message.get("type") == "state"][-1]
        assert state["state"] == {"activity_frames": expected}
        assert state["analytics"] == {"illuminated_frames": len(expected)}
    finally:
        repo.close()


def test_replacing_component_changes_host_output_and_rejects_old_cached_results(tmp_path, monkeypatch):
    plugin = _MachinePlugin()
    monkeypatch.setitem(sport._REGISTRY, plugin.name, plugin)
    mean, first_repo, _ = _runner(tmp_path / "mean", monkeypatch, plugin, "mean")
    peak, second_repo, _ = _runner(tmp_path / "peak", monkeypatch, plugin, "peak")
    _control_media(monkeypatch)
    try:
        mean._analyse()
        # Reusing the same host cache API must invoke the plugin's version check.
        for index in (0, 1):
            peak._cache_path(index).write_bytes(mean._cache_path(index).read_bytes())
        peak._analyse()
        assert mean.sport.component_handle.instance is not peak.sport.component_handle.instance
        assert mean.sport.component_handle.fingerprint != peak.sport.component_handle.fingerprint
        assert mean.sport.public_state() == {"activity_frames": []}
        assert peak.sport.public_state() == {"activity_frames": [0, 1, 2, 3]}
        assert peak.sport.component_handle.instance.calls == 4
        assert len(second_repo.events(peak.session_id).query()) == 4
    finally:
        first_repo.close()
        second_repo.close()
