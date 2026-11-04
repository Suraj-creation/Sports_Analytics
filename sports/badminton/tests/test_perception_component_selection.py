"""Configured providers execute through perception, without weights or video.

Scene and independent tracker outputs are controlled where needed. These tests
exercise component selection, data flow and lifecycle, not labelled accuracy.
"""

import json
from importlib import import_module
from types import SimpleNamespace

import numpy as np
import pytest

from bai_badminton.perception.pipeline import BadmintonPerception, _Scene
from bai_badminton.perception.scoreboard import ScoreboardReader
from bai_badminton.perception.tracknet import BackgroundModel, ShuttleDetection
from bai_badminton.perception_types import RacketObservation, ScoreReading
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.config import ModelChoice, Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry


FORMATS = frozenset({"singles", "doubles", "unknown"})


def _registry():
    module = import_module("bai_badminton.perception.components")
    registry = ComponentRegistry()
    module.register_perception_components(registry)
    return registry


def _register(registry, kind, factory, *, implementation="controlled", formats=FORMATS, stateful=False):
    module = import_module("bai_badminton.perception.components")
    registry.register(
        ComponentContract(
            kind=kind,
            implementation=implementation,
            version="controlled-v1",
            input_schema=f"badminton-{kind}-input:v1",
            output_schema=f"badminton-{kind}-output:v1",
            interface=module.PERCEPTION_PORTS[kind],
            context_type=module.PerceptionContext,
            supported_formats=formats,
            failure_policy="unavailable",
            stateful=stateful,
        ),
        factory,
    )


def _choice(kind, **params):
    return ModelChoice(
        model=f"configured-{kind}-artifact", backend="torch-cpu", implementation="controlled", params=params
    )


def _perception(tmp_path, monkeypatch, profile, registry, *, match_format="singles", fps=30.0, identity=None):
    models = tmp_path / "models"
    models.mkdir(exist_ok=True)
    (models / "manifest.yaml").write_text("models: {}\n", encoding="utf-8")
    perception = BadmintonPerception(
        profile,
        ModelRegistry(models),
        fps,
        models,
        (180, 120),
        match_format=match_format,
        component_registry=registry,
        context_identity=identity,
    )
    monkeypatch.setattr(
        perception,
        "_scene",
        lambda chunk, cuts: _Scene(
            ["main"] * len(chunk.frames), [0] * len(chunk.frames), [1.0] * len(chunk.frames),
            None, [None] * len(chunk.frames),
        ),
    )
    return perception


def _chunk(start=0, count=1):
    return DecodedChunk(start, [np.zeros((120, 180, 3), dtype=np.uint8) for _ in range(count)])


class RawShuttle:
    seq_len = 3

    def __init__(self, x=23.0):
        self.x = x
        self.bg = BackgroundModel()
        self.runtime = {"checkpoint_sha256": "a" * 64}
        self.model_ref = "controlled-shuttle@1"

    def detect(self, frames, shots, *, step, masks):
        return [ShuttleDetection(self.x + step, 17.0, 0.9) for _ in frames]


class StatefulShuttle(RawShuttle):
    def __init__(self, x=23.0):
        super().__init__(x)
        self.resets = 0
        self.closes = 0

    def reset(self):
        self.resets += 1
        self.bg = BackgroundModel()

    def close(self):
        self.closes += 1


@pytest.mark.parametrize("match_format,capacity", [("singles", 2), ("doubles", 4), ("unknown", 4)])
def test_selected_shuttle_runs_in_process_with_its_own_configuration_and_uncertain_format_capacity(
    tmp_path, monkeypatch, match_format, capacity
):
    registry = _registry()

    def build(context, config):
        assert context.fps == 30.0 and context.frame_size == (180, 120)
        assert context.registry.models_dir == tmp_path / "models"
        assert context.cache.is_dir()
        return StatefulShuttle(config["params"]["x"])

    _register(registry, "shuttle", build, stateful=True)
    choice = _choice("shuttle", x=23.0, step=1)
    profile = Profile(
        name="selected-perception",
        shuttle=ModelChoice(model="legacy-artifact", backend="torch-cpu", params={"step": 9}),
        components={"shuttle": choice},
    )
    perception = _perception(tmp_path, monkeypatch, profile, registry, match_format=match_format)
    choice.params["step"] = 8  # Later caller mutation cannot change this session.
    result = perception.process(_chunk(100, 2), in_play=True)

    assert [frame.shuttle_xy for frame in result.frames] == [(24.0, 17.0), (24.0, 17.0)]
    assert [frame.frame_idx for frame in result.frames] == [100, 101]
    assert perception.effective_choices["shuttle"].model == "configured-shuttle-artifact"
    assert perception.players.max_players == capacity
    assert perception.match_format == match_format


def test_profile_component_override_reaches_the_existing_baseline_loader(tmp_path, monkeypatch):
    registry = None  # Default construction must register the real baseline factories.

    def load(self, choice, model_registry, cache):
        return RawShuttle(41.0 if choice.model == "replacement-artifact" else -100.0)

    monkeypatch.setattr(BadmintonPerception, "_load_shuttle", load)
    profile = Profile(
        name="baseline-selection",
        shuttle=ModelChoice(model="legacy-artifact", backend="torch-cpu"),
        components={"shuttle": ModelChoice(model="replacement-artifact", backend="torch-cpu", params={"step": 2})},
    )
    perception = _perception(tmp_path, monkeypatch, profile, registry)
    assert perception.process(_chunk(), in_play=True).frames[0].shuttle_xy == (43.0, 17.0)


def test_explicit_weightless_provider_runs_while_legacy_disable_flags_remain_disabled(tmp_path, monkeypatch):
    registry = _registry()
    _register(
        registry, "shuttle", lambda context, config: StatefulShuttle(config["params"]["x"]), stateful=True,
    )

    def forbidden_baseline(*args, **kwargs):
        raise AssertionError("weightless custom or disabled legacy choice constructed a baseline model")

    monkeypatch.setattr(BadmintonPerception, "_load_shuttle", forbidden_baseline)
    profile = Profile(name="weightless-component", components={"shuttle": ModelChoice(
        model="none", backend="none", implementation="controlled", params={"x": 5.0, "step": 2},
    )})
    selected = _perception(tmp_path, monkeypatch, profile, registry)
    legacy = _perception(tmp_path, monkeypatch, Profile(name="disabled-legacy"), registry)
    assert selected.process(_chunk(), in_play=True).frames[0].shuttle_xy == (7.0, 17.0)
    assert legacy.process(_chunk(), in_play=True).frames[0].shuttle_xy is None


def test_all_six_selected_ports_feed_actual_process_observations(tmp_path, monkeypatch):
    from bai_badminton.perception import players

    class Tracker:
        def __init__(self, fps):
            pass

        def update(self, boxes, scores, frame):
            return [(index + 10, box, float(scores[index])) for index, box in enumerate(boxes)]

        def reset(self):
            pass

    class Detector:
        def __call__(self, image):
            return np.array([[10.0 + i * 40, 10.0, 30.0 + i * 40, 110.0] for i in range(4)]), np.full(4, 0.95)

    class Pose:
        def __call__(self, image, boxes):
            return [np.tile([31.0, 42.0, 0.9], (17, 1)) for _ in boxes]

    class ReID:
        fingerprint = "controlled-appearance@1"

        def __init__(self):
            self.crops = 0

        def embed(self, image, boxes):
            self.crops += len(boxes)
            return np.eye(512, dtype=np.float32)[:len(boxes)]

    class Racket:
        def detect(self, image, persons):
            return {p.track_id: RacketObservation((55.0, 20.0), (12.0, 18.0), 0.0, 0.9, 9) for p in persons}

    class OCR:
        def __init__(self):
            self.calls = 0

        def maybe_read(self, frame, image):
            self.calls += 1
            return ScoreReading(frame_idx=frame, rows=(("ALPHA", 9), ("BETA", 8)), conf=0.95)

        def reset(self):
            self.calls = 0

        def close(self):
            pass

    monkeypatch.setattr(players, "PlayerTracker", Tracker)
    registry = _registry()
    providers = {"shuttle": StatefulShuttle, "player_detector": Detector, "pose": Pose,
                 "player_reid": ReID, "racket": Racket, "ocr": OCR}
    for kind, provider in providers.items():
        _register(registry, kind, lambda context, config, provider=provider: provider(),
                  stateful=kind in {"shuttle", "ocr"})
    profile = Profile(name="all-selected-ports", components={kind: _choice(kind) for kind in providers})
    perception = _perception(tmp_path, monkeypatch, profile, registry, match_format="doubles")
    result = perception.process(_chunk(100), in_play=True)

    assert result.frames[0].shuttle_xy == (26.0, 17.0)
    assert len(result.frames[0].persons) == 4
    assert all(person.detector_matched for person in result.frames[0].persons)
    assert all(np.array_equal(person.kps[9], [31.0, 42.0, 0.9]) for person in result.frames[0].persons)
    assert all(person.racket.center == (55.0, 20.0) for person in result.frames[0].persons)
    assert perception.players.reid.crops == 4
    assert result.ocr[0].rows == (("ALPHA", 9), ("BETA", 8))
    assert set(perception.component_metadata) == set(providers)


@pytest.mark.parametrize("failure,match_format", [
    ("missing", "doubles"), ("unsupported", "doubles"),
    ("unsupported", "unknown"), ("wrong-interface", "doubles"),
])
def test_unavailable_selected_provider_is_reported_without_baseline_fallback(
    tmp_path, monkeypatch, failure, match_format
):
    registry = _registry()
    implementation = "missing" if failure == "missing" else "controlled"
    if failure != "missing":
        _register(
            registry, "shuttle", lambda context, config: object() if failure == "wrong-interface" else RawShuttle(),
            formats=frozenset({"singles"}) if failure == "unsupported" else FORMATS,
        )

    def forbidden_baseline(*args, **kwargs):
        raise AssertionError("unavailable selected provider fell back to baseline")

    monkeypatch.setattr(BadmintonPerception, "_load_shuttle", forbidden_baseline)
    profile = Profile(name="unavailable-selected-port", components={"shuttle": ModelChoice(
        model="configured-artifact", backend="torch-cpu", implementation=implementation,
    )})
    perception = _perception(tmp_path, monkeypatch, profile, registry, match_format=match_format)
    assert perception.process(_chunk(), in_play=True).frames[0].shuttle_xy is None
    reason = {"missing": "missing", "unsupported": "format", "wrong-interface": "interface"}[failure]
    assert any(item.stage == "shuttle" and reason in item.reason for item in perception.degraded)


def test_stateful_selected_components_are_session_scoped_and_reset_closed_explicitly(tmp_path, monkeypatch):
    registry = _registry()
    _register(registry, "shuttle", lambda context, config: StatefulShuttle(), stateful=True)
    profile = Profile(name="component-lifecycle", components={"shuttle": _choice("shuttle")})
    first = _perception(tmp_path, monkeypatch, profile, registry)
    second = _perception(tmp_path, monkeypatch, profile, registry)
    first_model, second_model = first.shuttle, second.shuttle
    assert first_model is not second_model
    first.reset_components()
    first.close()
    first.close()
    assert (first_model.resets, first_model.closes) == (1, 1)
    assert (second_model.resets, second_model.closes) == (0, 0)
    with pytest.raises(RuntimeError, match="closed"):
        first.component_handles["shuttle"].reset()


def _recognized_board(crop):
    return SimpleNamespace(
        boxes=[[[2, 2], [48, 2], [48, 8], [2, 8]], [[2, 12], [48, 12], [48, 18], [2, 18]]],
        txts=["ALPHA 9", "BETA 8"], scores=[0.95, 0.95],
    )


def test_baseline_stateful_adapters_expose_raw_models_and_reset_their_temporal_evidence(tmp_path, monkeypatch):
    registry = _registry()
    shuttle = RawShuttle()
    reader = ScoreboardReader(_recognized_board, every=3)
    monkeypatch.setattr(BadmintonPerception, "_load_shuttle", lambda *args: shuttle)
    monkeypatch.setattr(BadmintonPerception, "_load_ocr", lambda *args: reader)
    profile = Profile(name="baseline-lifecycle", components={
        "shuttle": ModelChoice(model="controlled-shuttle", backend="torch-cpu"),
        "ocr": ModelChoice(model="controlled-ocr", backend="onnx-cpu"),
    })
    perception = _perception(tmp_path, monkeypatch, profile, registry)
    assert perception.shuttle.raw_model is shuttle
    assert perception.scoreboard.raw_model is reader
    with pytest.raises(AttributeError):
        perception.shuttle.raw_model = object()
    fallback = np.zeros((2, 2, 3), np.uint8)
    shuttle.bg.seed(0, [np.ones_like(fallback)])
    assert perception._read_scoreboard(_chunk(0), [False], True)[0].frame_idx == 0
    assert perception._read_scoreboard(_chunk(1), [False], True) == []
    perception.reset_components()
    assert shuttle.bg.get(0, fallback) is fallback
    assert perception._read_scoreboard(_chunk(1), [False], True)[0].frame_idx == 1


def test_component_metadata_is_detached_json_and_records_actual_artifacts_after_factory(tmp_path, monkeypatch):
    registry = _registry()
    artifact = {"digest": "a" * 64}

    def build(context, config):
        context.record_model("shuttle", "configured-artifact@2")
        context.record_runtime("shuttle", {"checkpoint_sha256": artifact["digest"], "actual_backend": "torch-cpu"})
        return StatefulShuttle()

    _register(registry, "shuttle", build, stateful=True)
    profile = Profile(name="component-provenance", components={"shuttle": _choice("shuttle")})
    first = _perception(tmp_path, monkeypatch, profile, registry, identity={"input": "source-a", "calibration": 1})
    metadata = first.component_metadata
    assert json.loads(json.dumps(metadata)) == metadata
    assert metadata["shuttle"]["runtime"]["checkpoint_sha256"] == "a" * 64
    assert metadata["shuttle"]["model"] == "configured-artifact@2"
    assert metadata["shuttle"]["contract"]["implementation"] == "controlled"
    metadata["shuttle"]["runtime"]["checkpoint_sha256"] = "caller-mutation"
    assert first.component_metadata["shuttle"]["runtime"]["checkpoint_sha256"] == "a" * 64
    artifact["digest"] = "b" * 64
    second = _perception(tmp_path, monkeypatch, profile, registry, identity={"input": "source-a", "calibration": 1})
    assert first.component_metadata != second.component_metadata
    changed_input = _perception(tmp_path, monkeypatch, profile, registry, identity={"input": "source-b", "calibration": 1})
    changed_fps = _perception(tmp_path, monkeypatch, profile, registry, fps=25.0,
                              identity={"input": "source-a", "calibration": 1})
    fingerprints = [value.component_metadata["shuttle"]["fingerprint"] for value in (first, changed_input, changed_fps)]
    assert len(set(fingerprints)) == 3
