"""Independent scene-provider integration with actual eight-frame NN grouping.

All ports are weightless/controlled. These tests validate frame ownership,
ordering, context and retention, not physical scene or sporting accuracy.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import replace

import numpy as np
import pytest

from bai_badminton.perception.components import (
    PERCEPTION_PORTS,
    PerceptionContext,
    TrackingContext,
    register_perception_components,
)
from bai_badminton.perception.pipeline import BadmintonPerception, _Scene
from bai_badminton.perception.scene_change import SceneChangeEvidence
from bai_badminton.perception.tracknet import HEIGHT, WIDTH, BackgroundModel, TrackNetV3
from bai_badminton.perception_types import PersonObs
from bai_engine.components import ComponentContract, ComponentRegistry
from bai_engine.config import ModelChoice, Profile
from bai_engine.decode import DecodedChunk
from bai_engine.runtime.registry import ModelRegistry

FORMATS = frozenset({"singles", "doubles", "unknown"})


class ControlledContent:
    def __init__(self, events, barrier):
        self.events = events
        self.barrier_enabled = barrier
        self.calls = []

    def observe(self, frame, pixels, **kwargs):
        self.events.append(("content", frame))
        self.calls.append((frame, deepcopy(kwargs)))
        proposal = frame == 3
        previous = frame - 1 if kwargs["previous_regions"] else None
        return SceneChangeEvidence(
            frame,
            previous,
            "hypothesis" if proposal else "measured" if previous is not None else "unknown",
            proposal,
            ("controlled_source_change" if proposal else "controlled_continuity",),
            appearance_hypothesis=proposal,
        )

    def reset(self):
        self.calls.clear()

    def close(self):
        pass

    def checkpoint(self):
        return deepcopy(self.calls)

    def restore(self, checkpoint):
        self.calls = deepcopy(checkpoint)


class ControlledTracking:
    detector = None
    pose = None
    reid = None
    last_capacity_limited = False
    last_identity_error = None

    def __init__(self, events, count):
        self.events, self.max_players = events, count
        self.identity_policy = {"method": "controlled_anonymous_tracks"}
        self.last_detector_observed = False
        self.resets = 0

    def process(self, frame, image, strides):
        self.events.append(("people", frame))
        self.last_detector_observed = frame % 2 == 0
        return [
            PersonObs(
                key,
                np.asarray([10.0 + frame + 30 * key, 10.0, 25.0 + frame + 30 * key, 100.0]),
                0.9,
                detector_matched=self.last_detector_observed,
            )
            for key in range(self.max_players)
        ]

    def set_roi(self, roi):
        self.roi = roi

    def on_cut(self):
        self.resets += 1

    def reset(self):
        self.on_cut()

    def close(self):
        pass


class ControlledShuttle:
    seq_len = 8

    def __init__(self, events):
        self.events = events
        self.shots = []
        self.windows = []
        self.model = TrackNetV3.__new__(TrackNetV3)
        self.model.seq_len, self.model.in_dim, self.model.batch, self.model.threshold = 8, 27, 4, 0.5
        self.model.bg = BackgroundModel(every=1, capacity=4, refresh=1)
        self.bg = self.model.bg

        def forward(inputs):
            self.windows.extend(
                [[round(float(tensor[(offset + 1) * 3, 0, 0]) * 255) - 10 for offset in range(8)] for tensor in inputs]
            )
            return np.zeros((len(inputs), 8, HEIGHT, WIDTH), np.float32)

        self.model._forward = forward

    def detect(self, frames, shots, *, step, masks):
        self.events.append(("shuttle", tuple(shots)))
        self.shots.append(list(shots))
        return self.model.detect(frames, shots, step=step, masks=masks)


def perception(tmp_path, monkeypatch, *, enabled=True, barrier=True, count=2):
    events = []
    ports = {
        "content_continuity": ControlledContent(events, barrier),
        "tracking": ControlledTracking(events, count),
        "shuttle": ControlledShuttle(events),
    }
    registry = ComponentRegistry()
    register_perception_components(registry)
    for kind, port in ports.items():
        registry.register(
            ComponentContract(
                kind=kind,
                implementation="controlled-content-test",
                version="1",
                input_schema=f"controlled-{kind}:v1",
                output_schema=f"controlled-{kind}:v1",
                interface=PERCEPTION_PORTS[kind],
                context_type=TrackingContext if kind == "tracking" else PerceptionContext,
                supported_formats=FORMATS,
                failure_policy="abstain",
                stateful=kind != "shuttle",
            ),
            lambda _context, _config, port=port: port,
        )
    models = tmp_path / "models"
    models.mkdir(exist_ok=True)
    (models / "manifest.yaml").write_text("models: {}\n")
    selected = {
        kind: ModelChoice(model="none", backend="none", implementation="controlled-content-test")
        for kind in ports
        if enabled or kind != "content_continuity"
    }
    p = BadmintonPerception(
        Profile(name="controlled-content-pipeline", components=selected),
        ModelRegistry(models),
        30.0,
        models,
        (180, 120),
        component_registry=registry,
        match_format="doubles" if count == 4 else "singles",
    )
    p.mode = "lines"
    p._H_ref = np.eye(3)
    polygon = np.asarray([[20.0, 20.0], [160.0, 20.0], [160.0, 110.0], [20.0, 110.0]])
    monkeypatch.setattr(
        p,
        "_scene",
        lambda chunk, cuts: _Scene(
            ["main"] * len(chunk.frames),
            [0] * len(chunk.frames),
            [0.99] * len(chunk.frames),
            [np.eye(3) for _ in chunk.frames],
            [polygon.copy() for _ in chunk.frames],
            [False] * len(chunk.frames),
        ),
    )

    class StableCamera:
        shot_id = 7

        def update(self, _pixels):
            return False

    p.cuts = StableCamera()
    return p, ports, events


def chunk(start, count):
    return DecodedChunk(start, [np.full((120, 180, 3), frame + 10, np.uint8) for frame in range(start, start + count)])


@pytest.mark.parametrize("count", [2, 4])
def test_only_immediately_previous_regions_reach_content_provider(tmp_path, monkeypatch, count):
    p, ports, _ = perception(tmp_path, monkeypatch, count=count)
    result = p.process(chunk(0, 8), in_play=True)
    calls = ports["content_continuity"].calls
    assert calls[0][1]["previous_regions"] == []
    for frame, arguments in calls[1:]:
        regions = arguments["previous_regions"]
        assert len(regions) == count
        assert all(region.frame == frame - 1 for region in regions)
        assert regions[0].bbox[0] == 10 + frame - 1
        assert all(region.detector_matched is ((frame - 1) % 2 == 0) for region in regions)
    assert [f.detector_observed for f in result.frames] == [True, False, True, False, True, False, True, False]
    assert [f.persons[0].detector_matched for f in result.frames] == [
        True,
        False,
        True,
        False,
        True,
        False,
        True,
        False,
    ]
    p.close()


def test_same_camera_content_barrier_retains_court_and_precedes_eight_frame_network_windows(tmp_path, monkeypatch):
    p, ports, events = perception(tmp_path, monkeypatch)
    original = p._H_ref.copy()
    result = p.process(chunk(0, 12), in_play=True)
    assert [frame.content_epoch for frame in result.frames] == [0, 0, 0, *([1] * 9)]
    assert [frame.shot_id for frame in result.frames] == [7] * 12
    np.testing.assert_array_equal(p._H_ref, original)
    assert result.frames[3].calibration_state.value == "VALID"
    assert not result.frames[3].cam_lost
    np.testing.assert_array_equal(result.frames[3].cam, np.eye(3))
    assert ports["tracking"].resets == 1
    assert all(max(window) < 3 or min(window) >= 3 for window in ports["shuttle"].windows)
    assert events.index(("content", 3)) < next(i for i, e in enumerate(events) if e[0] == "shuttle")
    assert result.frames[3].content_change.hypothesis and not result.frames[3].content_change.authoritative
    p.close()


def test_diagnostic_mode_keeps_original_shot_inputs_and_never_enables_barriers(tmp_path, monkeypatch):
    p, ports, _ = perception(tmp_path, monkeypatch, barrier=False)
    result = p.process(chunk(0, 8), in_play=True)
    assert [frame.content_epoch for frame in result.frames] == [0] * 8
    assert ports["tracking"].resets == 0
    assert ports["shuttle"].shots == [[7] * 8]
    assert result.frames[3].content_change.hypothesis
    p.close()


def test_absent_optional_provider_preserves_existing_stage_order(tmp_path, monkeypatch):
    p, ports, events = perception(tmp_path, monkeypatch, enabled=False)
    result = p.process(chunk(0, 8), in_play=True)
    assert events[0][0] == "shuttle"
    assert ports["content_continuity"].calls == []
    assert ports["shuttle"].shots == [[7] * 8]
    assert all(frame.content_change is None and frame.content_epoch == 0 for frame in result.frames)
    p.close()


def test_chunk_seam_preserves_previous_frame_but_seek_gap_discards_stale_rois(tmp_path, monkeypatch):
    p, ports, _ = perception(tmp_path, monkeypatch)
    p.process(chunk(0, 4), in_play=True)
    p.process(chunk(4, 4), in_play=True)
    arguments = next(arguments for frame, arguments in ports["content_continuity"].calls if frame == 4)
    assert arguments["previous_regions"][0].frame == 3
    p.process(chunk(12, 2), in_play=True)
    arguments = next(arguments for frame, arguments in ports["content_continuity"].calls if frame == 12)
    assert arguments["previous_regions"] == [] and arguments["previous_view_valid"] is False
    p.close()


@pytest.mark.parametrize("invalid", ["future_frame", "authoritative", "unsupported_source"])
def test_invalid_independent_scene_evidence_is_rejected_before_it_can_split_nn_context(tmp_path, monkeypatch, invalid):
    p, ports, _ = perception(tmp_path, monkeypatch)

    def observe(frame, _pixels, **_kwargs):
        result = SceneChangeEvidence(frame, None, "unknown", False, ("controlled_invalid_source",))
        if invalid == "future_frame":
            return replace(result, frame=frame + 1, previous_frame=frame, status="hypothesis", hypothesis=True)
        if invalid == "authoritative":
            return replace(result, authoritative=True)
        return replace(result, source_basis="future_or_stale_snapshot")

    ports["content_continuity"].observe = observe
    with pytest.raises((TypeError, ValueError)):
        p.process(chunk(0, 8), in_play=True)
    assert ports["shuttle"].shots == []
    p.close()
