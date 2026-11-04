"""Failed sport construction releases selected providers and preserves cause."""

from io import StringIO

import pytest

from bai_badminton import plugin as plugin_module
from bai_badminton.components import BASELINE_IMPLEMENTATIONS, DOMAIN_PORTS, DomainContext, register_domain_components
from bai_badminton.format_understanding import FormatContext, FormatUnderstanding, register_format_components
from bai_badminton.perception.components import register_perception_components
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.config import ModelChoice, Profile
from bai_engine.runtime.registry import ModelRegistry
from bai_engine.schema import MediaInfo, Session, Source, SourceKind
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore


class _Resource:
    def __init__(self):
        self.stream = StringIO("provider-owned resource")
        self.close_count = 0

    def close(self):
        self.close_count += 1
        self.stream.close()


def _tracked_registry(resources, *, fail_score):
    baseline = ComponentRegistry()
    register_domain_components(baseline)
    register_format_components(baseline)
    selected = ComponentRegistry()
    register_perception_components(selected)
    choices = {}
    implementations = {"format": "sustained-court-v1", **BASELINE_IMPLEMENTATIONS}
    for kind, implementation in implementations.items():
        def factory(context, configuration, *, kind=kind, implementation=implementation):
            original_handle = baseline.create(
                kind, implementation, context=context, configuration={}, match_format="singles",
                context_identity={"test": "construction-cleanup"},
            )
            provider = original_handle.instance
            resource = _Resource()
            resources[kind] = resource
            original_close = getattr(provider, "close", None)

            def close():
                resource.close()
                if original_close is not None:
                    original_close()
                if fail_score and kind == "contact":
                    raise RuntimeError("secondary cleanup failure")

            provider.close = close
            if fail_score and kind == "scoring":
                def initial(config):
                    raise ValueError("primary score initialization failure")
                provider.initial = initial
            return provider

        selected.register(ComponentContract(
            kind=kind, implementation=f"tracked-{kind}", version="1",
            input_schema=f"tracked-{kind}-input:v1", output_schema=f"tracked-{kind}-output:v1",
            interface=FormatUnderstanding if kind == "format" else DOMAIN_PORTS[kind],
            context_type=FormatContext if kind == "format" else DomainContext,
            supported_formats=frozenset({"singles", "doubles", "unknown"}), failure_policy="abstain",
            stateful=kind in {"format", "activity", "rally", "analytics"},
        ), factory)
        choices[kind] = ModelChoice(model="none", backend="none", implementation=f"tracked-{kind}")
    return selected, Profile(name="construction-cleanup", components=choices)


@pytest.mark.parametrize("failure", ["score_initial", "perception_constructor"])
def test_partial_construction_closes_every_created_resource_once_without_masking_original_failure(
    tmp_path, monkeypatch, failure,
):
    resources = {}
    registry, profile = _tracked_registry(resources, fail_score=failure == "score_initial")
    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "manifest.yaml").write_text("models: {}\n")
    session = Session(
        title="Construction lifecycle", source=Source(kind=SourceKind.UPLOAD, uri="controlled-input"),
        media=MediaInfo(fps_num=30, fps_den=1, n_frames=30, width=1280, height=720, duration_us=1_000_000),
        roster=ParticipantRoster(match_format="singles"),
    )
    if failure == "perception_constructor":
        def fail_perception(*args, **kwargs):
            raise ValueError("primary perception construction failure")
        monkeypatch.setattr(plugin_module, "BadmintonPerception", fail_perception)
    expected = "primary score initialization failure" if failure == "score_initial" else "primary perception construction failure"
    with EventStore(tmp_path / "construction.sqlite", session.session_id) as store:
        with pytest.raises(ValueError, match=expected):
            plugin_module.BadmintonSession(
                session, store, profile, ModelRegistry(model_dir), lambda events: None, component_registry=registry,
            )
        assert set(resources) == {"format", *BASELINE_IMPLEMENTATIONS}
        assert all(resource.stream.closed for resource in resources.values())
        assert all(resource.close_count == 1 for resource in resources.values())
        # The store is caller-owned and remains usable after constructor failure.
        assert store.query() == []
