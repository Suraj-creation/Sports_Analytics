"""Domain providers are replaceable at the actual engine decision boundaries."""

from importlib import import_module

import pytest

from bai_badminton.engine import BadmintonMatchEngine, EngineConfig
from bai_badminton.events.contact import detect_contacts
from bai_badminton.events.stroke import StrokePrediction
from bai_badminton.perception_types import ChunkPerception
from bai_badminton.rules import MatchConfig
from bai_badminton.testing.synth import make_rally, to_frames
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.schema import Event, Provenance
from bai_engine.store import EventStore


def _setup():
    api = import_module("bai_badminton.components")
    registry = ComponentRegistry()
    api.register_domain_components(registry)
    context = api.DomainContext(fps=30.0, frame_width=1280, frame_height=720, match_config=MatchConfig())
    return api, registry, context


def _create(registry, context, kind, implementation, match_format="singles", params=None):
    return registry.create(
        kind,
        implementation,
        context=context,
        configuration={"params": params or {}},
        match_format=match_format,
        context_identity={"source": "a" * 64},
    )


@pytest.mark.parametrize("match_format", ["singles", "doubles", "unknown"])
def test_baseline_composition_declares_and_constructs_all_decision_ports(match_format):
    api, registry, context = _setup()
    for kind, implementation in api.BASELINE_IMPLEMENTATIONS.items():
        handle = _create(registry, context, kind, implementation, match_format)
        assert isinstance(handle.instance, api.DOMAIN_PORTS[kind])
        assert handle.contract.input_schema and handle.contract.output_schema
        handle.reset()
        handle.close()
        handle.close()


def test_configured_contact_port_preserves_the_baseline_and_can_change_contact_selection():
    api, registry, context = _setup()
    baseline = _create(registry, context, "contact", api.BASELINE_IMPLEMENTATIONS["contact"])
    window = make_rally().obs
    assert [x.frame for x in baseline.instance.detect(window, enforce_alternation=False)] == [
        x.frame for x in detect_contacts(window, enforce_alternation=False)
    ]
    strict = _create(registry, context, "contact", api.BASELINE_IMPLEMENTATIONS["contact"], params={"p_min": 1.1})
    assert strict.instance.detect(window, enforce_alternation=False) == []
    assert strict.fingerprint != baseline.fingerprint


def test_contact_factory_replacement_changes_emitted_engine_events(tmp_path):
    api, registry, context = _setup()

    class Silent:
        def __init__(self):
            self.calls = 0

        def detect(self, window, **kwargs):
            self.calls += 1
            return []

    registry.register(
        ComponentContract(
            kind="contact",
            implementation="silent",
            version="1",
            input_schema="contact-window:v1",
            output_schema="contact-candidates:v1",
            interface=api.DOMAIN_PORTS["contact"],
            context_type=api.DomainContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="abstain",
        ),
        lambda context, config: Silent(),
    )
    selected = _create(registry, context, "contact", "silent")
    rally = make_rally()
    frames = to_frames(rally, 0)
    with EventStore(tmp_path / "selected.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store, contact_inference=selected.instance
        )
        engine.set_calibration(0, rally.homography)
        engine.ingest(
            ChunkPerception(
                0, frames[-1].frame_idx, frames, models={"player_detector": "synthetic-person-observations@1"}
            )
        )
        engine.flush()
        assert selected.instance.calls > 0
        assert not store.query(types=["contact", "stroke"])


def test_classifier_factory_replacement_reaches_actual_stroke_events(tmp_path):
    api, registry, context = _setup()

    class Controlled:
        name = "controlled-classifier@1"

        def predict(self, context):
            return StrokePrediction({"drop": 1.0}, self.name)

    registry.register(
        ComponentContract(
            kind="stroke",
            implementation="controlled",
            version="1",
            input_schema="stroke-context:v1",
            output_schema="stroke-prediction:v1",
            interface=api.DOMAIN_PORTS["stroke"],
            context_type=api.DomainContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}),
            failure_policy="abstain",
        ),
        lambda context, config: Controlled(),
    )
    selected = _create(registry, context, "stroke", "controlled")
    rally = make_rally()
    frames = to_frames(rally, 0)
    with EventStore(tmp_path / "classified.sqlite", "S1") as store:
        engine = BadmintonMatchEngine(
            "S1", EngineConfig(fps=30, frame_width=1280, frame_height=720), store, stroke_classifier=selected.instance
        )
        engine.set_calibration(0, rally.homography)
        engine.ingest(
            ChunkPerception(
                0, frames[-1].frame_idx, frames, models={"player_detector": "synthetic-person-observations@1"}
            )
        )
        engine.flush()
        strokes = store.query(types=["stroke"])
        assert strokes
        assert all(event.payload["stroke"] == "drop" for event in strokes)


def test_analytics_has_explicit_data_checkpoint_restore_even_after_reset():
    api, registry, context = _setup()
    analytics = _create(registry, context, "analytics", api.BASELINE_IMPLEMENTATIONS["analytics"]).instance
    initial = analytics.to_public()
    before = analytics.checkpoint()
    analytics.on_stroke(
        Event(
            session_id="S1",
            type="stroke",
            frame_start=10,
            frame_end=10,
            pts_us=333333,
            payload={"stroke": "drop"},
            provenance=Provenance(model="controlled"),
        )
    )
    changed = analytics.to_public()
    assert changed != initial
    after = analytics.checkpoint()
    analytics.reset()
    analytics.restore(after)
    assert analytics.to_public() == changed
    analytics.restore(before)
    assert analytics.to_public() == initial
    with pytest.raises(ValueError, match="checkpoint"):
        analytics.restore(object())


@pytest.mark.parametrize("kind", ["activity", "rally"])
def test_temporal_provider_has_explicit_checkpoint_restore_for_format_transactions(kind):
    from bai_badminton.events.activity import ActivityObservation
    from bai_badminton.events.rally_fsm import RallyState

    api, registry, context = _setup()
    provider = _create(registry, context, kind, api.BASELINE_IMPLEMENTATIONS[kind]).instance
    assert callable(getattr(provider, "checkpoint", None))
    assert callable(getattr(provider, "restore", None))
    if kind == "rally":
        provider.on_contact(3)
        saved = provider.checkpoint()
        provider.reset()
        assert provider.state is RallyState.IDLE
        provider.restore(saved)
        assert provider.state is RallyState.IN_PLAY
    else:
        provider.update(ActivityObservation(frame_idx=3, view_valid=True))
        saved = provider.checkpoint()
        provider.reset()
        provider.restore(saved)
        assert provider.checkpoint() == saved
