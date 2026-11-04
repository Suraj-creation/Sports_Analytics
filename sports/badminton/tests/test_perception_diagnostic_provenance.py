"""Diagnostic metadata stays bound to its canonical observation and optional provider."""

import msgpack
import pytest

from bai_badminton.perception.calibration_state import CalibrationState
from bai_badminton.perception.diagnostics import FrameDiagnostic
from bai_badminton.perception_types import ChunkPerception, FramePerception
from bai_badminton.plugin import BadmintonSession, StaleCacheError
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore


def _non30_cache_session(tmp_path):
    from pathlib import Path

    from test_plugin_discipline import PROFILE

    session = Session(
        title="non30-cache-contract",
        source=Source(kind=SourceKind.UPLOAD, uri="test.mp4"),
        media=MediaInfo(fps_num=25, fps_den=1, n_frames=100, width=1280, height=720, duration_us=4000000),
        roster=ParticipantRoster(match_format="singles"),
    )
    return BadmintonSession(
        session,
        EventStore(tmp_path / "events.sqlite", session.session_id),
        PROFILE,
        ModelRegistry(Path("models").resolve()),
        lambda _: None,
    )


def _non30_payload(session):
    diagnostic = FrameDiagnostic(25, 1.0, 2, "main", "VALID", None, "model_ran", "stub-shuttle@1")
    frame = FramePerception(
        25,
        None,
        0.0,
        shot_id=2,
        view="main",
        calibration_state=CalibrationState.VALID,
        detector_observed=False,
        pose_stride=0,
        diagnostic=diagnostic,
    )
    return session.encode_perception(ChunkPerception(25, 25, [frame], models={"shuttle": "stub-shuttle@1"}))


def test_valid_non30_diagnostic_timestamp_roundtrip(tmp_path):
    session = _non30_cache_session(tmp_path)
    try:
        decoded = session.decode_perception(_non30_payload(session), diagnostic=True)
        assert decoded.frames[0].diagnostic.canonical_time_sec == 1.0
        assert decoded.frames[0].diagnostic.provider == "stub-shuttle@1"
    finally:
        session.close()


@pytest.mark.parametrize(
    "field,value",
    [
        ("canonical_time_sec", 99.0),
        ("view", "alt"),
        ("calibration_state", "LOST"),
        ("provider", "other-shuttle@9"),
    ],
)
def test_finite_diagnostic_metadata_cannot_disagree_with_its_observation(tmp_path, field, value):
    session = _non30_cache_session(tmp_path)
    try:
        record = msgpack.unpackb(_non30_payload(session), raw=False)
        record["frames"][0]["dg"][field] = value
        with pytest.raises(StaleCacheError):
            session.decode_perception(msgpack.packb(record, use_bin_type=True), diagnostic=True)
    finally:
        session.close()


def test_legacy_baseline_loader_adapter_remains_usable_with_diagnostics_enabled(tmp_path, monkeypatch):
    from test_perception_component_selection import RawShuttle, _chunk, _perception

    from bai_badminton.perception.pipeline import BadmintonPerception
    from bai_engine.config import ModelChoice, Profile

    monkeypatch.setattr(BadmintonPerception, "_load_shuttle", lambda *args: RawShuttle(41.0))
    profile = Profile(
        name="legacy-diag",
        shuttle=ModelChoice(
            model="legacy-stub",
            backend="torch-cpu",
            params={"step": 2, "diagnostics": {"ranges": [[0, 0]]}},
        ),
    )
    perception = _perception(tmp_path, monkeypatch, profile, None)
    result = perception.process(_chunk(), in_play=True)
    assert result.frames[0].shuttle_xy == (43.0, 17.0)
    assert result.frames[0].diagnostic.acquisition_reason == "provider_diagnostics_unsupported"
    assert result.frames[0].diagnostic.shuttle is None
    perception.close()


def test_independent_legacy_shuttle_remains_usable_with_diagnostics_enabled(tmp_path, monkeypatch):
    from test_perception_component_selection import StatefulShuttle, _choice, _chunk, _perception, _register, _registry

    from bai_engine.config import Profile

    registry = _registry()
    _register(registry, "shuttle", lambda context, config: StatefulShuttle(41.0), stateful=True)
    profile = Profile(
        name="independent-legacy-diag",
        components={
            "shuttle": _choice(
                "shuttle",
                step=2,
                diagnostics={"ranges": [[0, 0]]},
            )
        },
    )
    perception = _perception(tmp_path, monkeypatch, profile, registry)
    result = perception.process(_chunk(), in_play=True)
    assert result.frames[0].shuttle_xy == (43.0, 17.0)
    assert result.frames[0].diagnostic.acquisition_reason == "provider_diagnostics_unsupported"
    perception.close()


def test_explicit_false_optional_diagnostic_capability_is_respected(tmp_path, monkeypatch):
    from test_perception_component_selection import StatefulShuttle, _choice, _chunk, _perception, _register, _registry

    from bai_engine.config import Profile

    class Provider(StatefulShuttle):
        supports_diagnostics = False

        def detect_with_diagnostics(self, *args, **kwargs):
            raise AssertionError("disabled optional diagnostics called")

    registry = _registry()
    _register(registry, "shuttle", lambda context, config: Provider(41.0), stateful=True)
    profile = Profile(
        name="independent-false-diag",
        components={
            "shuttle": _choice(
                "shuttle",
                step=2,
                diagnostics={"ranges": [[0, 0]]},
            )
        },
    )
    perception = _perception(tmp_path, monkeypatch, profile, registry)
    result = perception.process(_chunk(), in_play=True)
    assert result.frames[0].shuttle_xy == (43.0, 17.0)
    assert result.frames[0].diagnostic.acquisition_reason == "provider_diagnostics_unsupported"
    perception.close()
