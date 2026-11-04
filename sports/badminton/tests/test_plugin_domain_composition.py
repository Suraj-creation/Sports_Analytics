"""Profile-selected decision providers execute in the actual badminton pipeline."""

from bai_badminton.components import DOMAIN_PORTS, DomainContext, register_domain_components
from bai_badminton.events.stroke import StrokePrediction
from bai_badminton.format_understanding import register_format_components
from bai_badminton.perception.components import register_perception_components
from bai_badminton.perception_types import ChunkPerception
from bai_badminton.plugin import BadmintonSession
from bai_badminton.testing.synth import make_rally, to_frames
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.config import ModelChoice, Profile
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore


def _registry(kind, provider, *, stateful=False):
    registry = ComponentRegistry()
    register_perception_components(registry)
    register_format_components(registry)
    register_domain_components(registry)
    registry.register(
        ComponentContract(
            kind=kind,
            implementation="controlled",
            version="1",
            input_schema=f"controlled-{kind}-input:v1",
            output_schema=f"controlled-{kind}-output:v1",
            interface=DOMAIN_PORTS[kind],
            context_type=DomainContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="abstain",
            stateful=stateful,
        ),
        lambda context, config: provider,
    )
    return registry


def _session(tmp_path, kind, provider, *, stateful=False):
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "manifest.yaml").write_text("models: {}\n", encoding="utf-8")
    session = Session(
        title="Controlled domain pipeline",
        source=Source(kind=SourceKind.UPLOAD, uri="controlled-frames"),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=1000, width=1280, height=720, duration_us=33333333),
        roster=ParticipantRoster(match_format="singles"),
    )
    profile = Profile(
        name="configured-domain",
        components={
            kind: ModelChoice(
                model="none",
                backend="none",
                implementation="controlled",
            )
        },
    )
    store = EventStore(tmp_path / "composed.sqlite", session.session_id)
    plugin = BadmintonSession(
        session,
        store,
        profile,
        ModelRegistry(model_dir),
        lambda events: None,
        component_registry=_registry(kind, provider, stateful=stateful),
    )
    return plugin, store


def _run(plugin):
    rally = make_rally()
    plugin._apply_calibration(rally.homography, emit=False, mode="static")
    frames = to_frames(rally, 0)
    plugin.ingest(
        ChunkPerception(0, frames[-1].frame_idx, frames, models={"player_detector": "synthetic-person-observations@1"})
    )
    plugin.flush()


def test_profile_selected_contact_method_changes_full_pipeline_output_and_capabilities(tmp_path):
    class Silent:
        def __init__(self):
            self.calls = 0

        def detect(self, window, **kwargs):
            self.calls += 1
            return []

    provider = Silent()
    plugin, store = _session(tmp_path, "contact", provider)
    try:
        _run(plugin)
        assert provider.calls > 0
        assert not store.query(types=["contact", "stroke"])
        assert plugin.capabilities()["contact"]["active_implementation"] == "controlled"
        assert plugin._isolation_id()["domain_components"]["contact"]["contract"]["implementation"] == "controlled"
    finally:
        plugin.close()
        store.close()


def test_profile_selected_classifier_changes_full_pipeline_stroke_labels(tmp_path):
    class Controlled:
        name = "controlled-classifier@1"

        def __init__(self):
            self.calls = 0

        def predict(self, context):
            self.calls += 1
            return StrokePrediction({"drop": 1.0}, self.name)

    provider = Controlled()
    plugin, store = _session(tmp_path, "stroke", provider)
    try:
        _run(plugin)
        assert provider.calls > 0
        strokes = store.query(types=["stroke"])
        assert strokes and all(event.payload["stroke"] == "drop" for event in strokes)
        assert plugin.capabilities()["stroke"]["active_implementation"] == "controlled"
    finally:
        plugin.close()
        store.close()
