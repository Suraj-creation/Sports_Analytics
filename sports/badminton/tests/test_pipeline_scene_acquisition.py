"""New acquisition runs through the normal tracking/reset path exactly once."""

import cv2
import numpy as np
import pytest
from test_content_pipeline_integration import chunk, perception

from bai_badminton.perception.content import ContentContinuityProviderV2
from bai_badminton.perception.players import PlayerPerception
from bai_badminton.perception.scene_change import (
    SCENE_CONTINUITY_VERSION_V4,
    RegionContinuity,
    SceneChangeEvidence,
)


@pytest.mark.parametrize("count", [2, 4])
@pytest.mark.parametrize("match_format", ["known", "unknown", "unconfirmed_placeholder"])
def test_relative_probe_is_causal_consumed_once_and_reset_requires_known_complete_format(
    tmp_path, monkeypatch, count, match_format
):
    pipeline, ports, events = perception(tmp_path, monkeypatch, count=count)
    pipeline.match_format = ("singles" if count == 2 else "doubles") if match_format != "unknown" else "unknown"
    pipeline.match_format_confirmed = match_format == "known"
    pipeline.models["player_detector"] = "controlled-detector@1"
    world = np.array([[-3.05, 6.7], [3.05, 6.7], [3.05, -6.7], [-3.05, -6.7]], np.float32)
    polygon = np.array([[20.0, 20.0], [160.0, 20.0], [160.0, 110.0], [20.0, 110.0]], np.float32)
    pipeline._H_ref = cv2.getPerspectiveTransform(world, polygon)
    calls = []

    def detector(image):
        frame = int(image[0, 0, 0]) - 10
        calls.append(frame)
        events.append(("probe_detector", frame))
        base = 100 if frame >= 3 else 20
        return np.array([[base + 16 * i, 30.0, base + 16 * i + 12, 100.0] for i in range(count)]), np.full(count, 0.95)

    players = PlayerPerception(detector, None, 30, det_stride=2, pose_stride=0, max_players=count)
    original_reset = players.on_cut

    def reset():
        events.append(("tracking_reset", int(len(calls))))
        original_reset()

    players.on_cut = reset
    pipeline.players = players
    content = ContentContinuityProviderV2(mode="barrier_detector_layout_v2")

    def observe(frame, image, **context):
        prior = context["previous_regions"]
        changed = frame == 3
        regions = tuple(
            RegionContinuity(
                r,
                20,
                0.1,
                6.0 if changed else 1.0,
                0.1,
                4.0 if changed else 0.1,
                1.0,
                4.0 if changed else 0.1,
                1.0,
                6.0 if changed else 1.0,
            )
            for r in prior
        )
        keys = tuple(r.key for r in prior) if changed else ()
        return SceneChangeEvidence(
            frame,
            frame - 1 if frame else None,
            "measured" if frame else "unknown",
            False,
            ("controlled_relative_acquisition",),
            regions=regions,
            background_features=80,
            background_consistent_fraction=1.0,
            version=SCENE_CONTINUITY_VERSION_V4,
            witness_parameters=(3.0, 15.0),
            acquisition_region_keys=keys,
            relative_region_keys=keys,
        )

    content.observe = observe
    pipeline.content_continuity = content
    result = pipeline.process(chunk(0, 5), in_play=True)
    assert calls.count(3) == 1
    assert result.frames[3].detector_observed
    assert all(p.detector_matched is True for p in result.frames[3].persons)
    assert len(result.frames[3].persons) == count
    assert result.frames[3].content_change.hypothesis is False
    decision = result.frames[3].content_decision
    assert decision.expected_participants == (count if match_format == "known" else None)
    assert decision.previous_camera == tuple(np.eye(3).ravel())
    assert decision.previous_to_current == tuple(np.eye(3).ravel())
    assert decision.decision == ("barrier" if match_format == "known" else "unknown")
    assert result.frames[3].content_epoch == int(match_format == "known")
    resets = [event for event in events if event[0] == "tracking_reset"]
    assert len(resets) == int(match_format == "known")
    if resets:
        assert events.index(("probe_detector", 3)) < events.index(resets[0])
    # The previous chunk was processed before any new format inference. There
    # is no current-person-count shortcut from unknown into singles/doubles.
    assert pipeline.match_format == ("unknown" if match_format == "unknown" else "singles" if count == 2 else "doubles")
    pipeline.close()
