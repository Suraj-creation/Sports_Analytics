"""A configured one-observation track activates on its first source detection."""

import numpy as np
import pytest

from bai_badminton.perception.players import PlayerPerception, PlayerTracker


def boxes(count=2, offset=0):
    return np.array([[10 + 50 * i + offset, 10, 35 + 50 * i + offset, 95] for i in range(count)], float)


@pytest.mark.parametrize("count", [1, 2, 4, 6])
def test_initial_detection_counts_toward_minimum(count):
    tracker = PlayerTracker(30)
    detections = boxes(count)
    observed = tracker.update(detections, np.full(count, 0.9), 0)
    assert len(observed) == count
    assert len({row[0] for row in observed}) == count
    for (_, actual, confidence), expected in zip(observed, detections, strict=True):
        np.testing.assert_array_equal(actual, expected)
        assert confidence == pytest.approx(0.9)


@pytest.mark.parametrize("minimum", [2, 3])
def test_larger_activation_minimum_retains_backend_confirmation(minimum):
    tracker = PlayerTracker(30)
    tracker._tracker.minimum_consecutive_frames = minimum
    for observation in range(1, minimum + 1):
        result = tracker.update(boxes(1), np.array([0.9]), observation * 2)
        assert len(result) == (1 if observation >= minimum else 0)


def test_births_mixed_with_existing_tracks_follow_returned_detection_order():
    tracker = PlayerTracker(30)
    initial = tracker.update(boxes(1), np.array([0.9]), 0)
    assert len(initial) == 1
    detections = boxes(4)[[2, 0, 3, 1]]
    result = tracker.update(detections, np.full(4, 0.9), 6)
    assert len(result) == 4 and len({r[0] for r in result}) == 4
    old = next(row for row in result if np.array_equal(row[1], boxes(1)[0]))
    assert old[0] == initial[0][0]
    assert {tuple(r[1]) for r in result} == {tuple(b) for b in detections}


@pytest.mark.parametrize("confidence", [0.2, 0.39, 0.45])
def test_unmatched_low_confidence_does_not_spawn_track(confidence):
    tracker = PlayerTracker(30)
    assert tracker.update(boxes(1), np.array([confidence]), 0) == []
    assert tracker._tracker.tracks == []


def test_existing_low_confidence_match_keeps_episode():
    tracker = PlayerTracker(30)
    first = tracker.update(boxes(1), np.array([0.9]), 0)
    assert len(first) == 1
    low = tracker.update(boxes(1), np.array([0.35]), 6)
    assert len(low) == 1 and low[0][0] == first[0][0]


def test_unseen_frame_does_not_emit_predicted_observation():
    tracker = PlayerTracker(30)
    assert len(tracker.update(boxes(1), np.array([0.9]), 0)) == 1
    assert tracker.update(np.empty((0, 4)), np.empty(0), 6) == []


def test_elapsed_time_expiry_and_reset_keep_episode_lifecycle():
    tracker = PlayerTracker(30)
    first = tracker.update(boxes(1), np.array([0.9]), 0)
    assert len(first) == 1
    assert tracker.update(np.empty((0, 4)), np.empty(0), 45) == []
    later = tracker.update(boxes(1), np.array([0.9]), 46)
    assert len(later) == 1 and later[0][0] != first[0][0]
    tracker.reset()
    after_reset = tracker.update(boxes(1), np.array([0.9]), 47)
    assert len(after_reset) == 1 and after_reset[0][0] == 0


def test_independent_providers_have_no_global_id_allocator():
    one, two = PlayerTracker(30), PlayerTracker(30)
    a = one.update(boxes(2), np.array([0.9, 0.9]), 0)
    b = two.update(boxes(2), np.array([0.9, 0.9]), 0)
    assert len(a) == len(b) == 2
    assert [p[0] for p in a] == [p[0] for p in b]
    one.reset()
    again = two.update(boxes(2), np.array([0.9, 0.9]), 6)
    assert [p[0] for p in again] == [p[0] for p in b]


@pytest.mark.parametrize("count", [2, 4])
def test_fresh_people_survive_perception_then_carry_is_explicitly_unobserved(count):
    detections = boxes(count)
    perception = PlayerPerception(lambda _: (detections.copy(), np.full(count, 0.9)), None, 30, max_players=count)
    image = np.zeros((120, 350, 3), np.uint8)
    first = perception.process(0, image, (2, 0))
    assert len(first) == count and all(p.detector_matched is True for p in first)
    carried = perception.process(1, image, (2, 0))
    assert len(carried) == count and all(p.detector_matched is False for p in carried)
    assert [p.track_id for p in first] == [p.track_id for p in carried]


def test_unmatched_high_below_activation_keeps_birth_output_binding():
    tracker = PlayerTracker(30)
    tracker._tracker.track_activation_threshold = 0.8
    detections = boxes(3)
    result = tracker.update(detections, np.array([0.7, 0.9, 0.85]), 0)
    assert len(result) == 2 and len({p[0] for p in result}) == 2
    np.testing.assert_array_equal(np.array([p[1] for p in result]), detections[1:])


def test_duplicate_birth_boxes_have_distinct_backend_episode_ids():
    tracker = PlayerTracker(30)
    detections = np.repeat(boxes(1), 2, axis=0)
    result = tracker.update(detections, np.array([0.9, 0.85]), 0)
    assert len(result) == 2 and result[0][0] != result[1][0]
    np.testing.assert_array_equal(np.array([p[1] for p in result]), detections)


def test_tracking_contract_and_cache_identity_record_new_algorithm(tmp_path):
    from bai_badminton.perception.pipeline import BadmintonPerception
    from bai_engine.config import Profile
    from bai_engine.runtime.registry import ModelRegistry

    model_dir = tmp_path / "models"
    model_dir.mkdir()
    (model_dir / "manifest.yaml").write_text("models: {}\n", encoding="utf-8")
    perception = BadmintonPerception(
        Profile(name="birth-contract"), ModelRegistry(model_dir), 30.0, model_dir, match_format="unknown"
    )
    try:
        # The birth policy is retained, while the scene-only foreground policy
        # changes the registered component/cache identity independently.
        assert perception.component_metadata["tracking"]["contract"]["version"] == "5"
        assert perception.models["tracking"] == "court-player-episodes-v1@5"
        assert perception.identity_policy["policy"] == "bytetrack_birth_activation_v2"
        assert perception.identity_policy["tracking_activation"] == "initial_observation_counts_v2"
        assert perception.identity_policy["court_membership"] == "court_origin_observed_continuity_v3"
        assert perception.identity_policy["scene_foreground"] == "court_origin_image_continuity_v2"
    finally:
        perception.close()
