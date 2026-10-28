"""Canonical visual tracks use neural evidence and motion, never shirt colour."""

import numpy as np
import pytest

from bai_badminton.perception.player_association import PersistentPlayerAssociator


def feature(index):
    vector = np.zeros(512, dtype=np.float32)
    vector[index] = 1
    return vector


def track(raw_id, x, *, width=40, height=100, confidence=0.9):
    return raw_id, np.array([x, 10, x + width, 10 + height], dtype=float), confidence


def update(associator, frame, rows, identities, *, observed=None):
    vectors = None if identities is None else np.asarray([feature(i) for i in identities])
    return associator.update(frame, rows, vectors, observed=[True] * len(rows) if observed is None else observed)


def test_births_are_frame_namespaced_and_input_order_independent():
    first, second = PersistentPlayerAssociator(fps=30), PersistentPlayerAssociator(fps=30)
    assert update(first, 5, [track(8, 100), track(3, 300)], [0, 1]) == [82, 81]
    assert update(second, 5, [track(3, 300), track(8, 100)], [1, 0]) == [81, 82]
    first.reset()
    assert update(first, 7, [track(8, 100)], [0]) == [113]


def test_same_jersey_crossing_corrects_swapped_raw_ids():
    # Both jerseys could have identical HSV. Only these neural vectors identify A/B.
    associator = PersistentPlayerAssociator(fps=30)
    before = update(associator, 0, [track(1, 50), track(2, 150)], [0, 1])
    assert min(before) > 0 and len(set(before)) == 2
    assert update(associator, 2, [track(1, 70), track(2, 130)], [0, 1]) == before
    assert update(associator, 4, [track(1, 95), track(2, 105)], [0, 1]) == before
    after = update(associator, 6, [track(1, 80), track(2, 120)], [1, 0])
    assert after == before[::-1]


@pytest.mark.parametrize("left,right", [(50, 150), (45, 155)])
def test_indistinguishable_crossing_stays_unresolved_after_separation(left, right):
    associator = PersistentPlayerAssociator(fps=30)
    assert min(update(associator, 0, [track(1, left), track(2, right)], [0, 0])) > 0
    assert update(associator, 2, [track(1, 95), track(2, 105)], [0, 0]) == [-1, -1]
    assert update(associator, 4, [track(1, left), track(2, right)], [0, 0]) == [-1, -1]


def test_ambiguous_crossing_recovers_when_distinctive_neural_evidence_returns():
    associator = PersistentPlayerAssociator(fps=30)
    original = update(associator, 0, [track(1, 45), track(2, 155)], [0, 1])
    assert min(original) > 0
    assert update(associator, 2, [track(1, 95), track(2, 105)], None) == [-1, -1]
    assert update(associator, 4, [track(1, 105), track(2, 95)], [1, 0]) == original[::-1]


def test_ambiguous_crossing_expires_into_new_identities():
    associator = PersistentPlayerAssociator(fps=30)
    original = update(associator, 0, [track(1, 45), track(2, 155)], [0, 0])
    assert update(associator, 2, [track(1, 95), track(2, 105)], [0, 0]) == [-1, -1]
    returned = update(associator, 31, [track(1, 45), track(2, 155)], [0, 0])
    assert min(returned) > 0 and set(returned).isdisjoint(original)


def test_short_occlusion_and_new_raw_id_preserve_identity():
    associator = PersistentPlayerAssociator(fps=25)
    identity = update(associator, 0, [track(1, 100)], [0])[0]
    assert identity > 0
    update(associator, 5, [], [])
    assert update(associator, 12, [track(90, 130)], [0]) == [identity]


def test_substitute_with_same_raw_id_gets_new_identity():
    associator = PersistentPlayerAssociator(fps=30)
    old = update(associator, 0, [track(1, 100)], [0])[0]
    new = update(associator, 2, [track(1, 100)], [1])[0]
    assert new != old and new > 0


def test_expired_return_does_not_reuse_identity():
    associator = PersistentPlayerAssociator(fps=25)
    old = update(associator, 0, [track(1, 100)], [0])[0]
    assert update(associator, 26, [track(9, 100)], [0]) == [417]
    assert old != 417


def test_disabled_or_empty_features_cannot_link_new_raw_id():
    associator = PersistentPlayerAssociator(fps=30)
    old = update(associator, 0, [track(1, 100)], [0])[0]
    assert update(associator, 1, [track(1, 101)], None) == [old]
    replacement = update(associator, 2, [track(7, 102)], None)[0]
    assert replacement > 0 and replacement != old
    zero = np.zeros((1, 512), dtype=np.float32)
    newer = associator.update(3, [track(8, 103)], zero, observed=[True])[0]
    assert newer > 0 and newer not in (old, replacement)


def test_missing_descriptors_cannot_resolve_two_motion_plausible_identities_by_raw_id():
    associator = PersistentPlayerAssociator(fps=30)
    identities = update(associator, 0, [track(1, 80), track(2, 130)], [0, 1])
    assert identities == [1, 2]
    # Neither box overlaps; both previous identities are within the motion gate.
    assert update(associator, 2, [track(1, 130), track(2, 80)], None) == [-1, -1]
    assert update(associator, 4, [track(1, 130), track(2, 80)], [1, 0]) == identities[::-1]


def test_first_descriptor_does_not_claim_a_neural_comparison():
    associator = PersistentPlayerAssociator(fps=30)
    identity = update(associator, 0, [track(1, 100)], None)[0]
    assert identity > 0
    assert update(associator, 1, [track(1, 100)], [0]) == [identity]
    assert associator.last_reason == ["raw_continuity"]
    assert update(associator, 2, [track(1, 100)], [0]) == [identity]
    assert associator.last_reason == ["neural_motion_match"]


def test_unknown_gallery_cannot_establish_distinctiveness_during_overlap():
    associator = PersistentPlayerAssociator(fps=30)
    features = np.asarray([feature(0), np.zeros(512)])
    assert associator.update(0, [track(1, 50), track(2, 150)], features, observed=[True, True]) == [1, 2]
    assert update(associator, 2, [track(1, 95), track(2, 105)], [0, 0]) == [-1, -1]


def test_distant_unknown_gallery_does_not_block_isolated_raw_continuity():
    associator = PersistentPlayerAssociator(fps=30)
    features = np.asarray([feature(0), np.zeros(512)])
    assert associator.update(0, [track(1, 50), track(2, 500)], features, observed=[True, True]) == [1, 2]
    assert update(associator, 2, [track(1, 51)], [0]) == [1]


def test_unobserved_samples_cannot_create_relink_or_extend_lifetime():
    associator = PersistentPlayerAssociator(fps=10)
    old = update(associator, 0, [track(1, 100)], [0])[0]
    assert update(associator, 1, [track(1, 400)], [1], observed=[False]) == [old]
    assert update(associator, 2, [track(9, 100)], [0], observed=[False]) == [-1]
    assert update(associator, 11, [track(1, 100)], [0], observed=[False]) == [-1]


def test_overlap_does_not_pollute_descriptor_gallery():
    associator = PersistentPlayerAssociator(fps=30)
    identities = update(associator, 0, [track(1, 50), track(2, 150)], [0, 1])
    # A mixed crop should be ignored for learning, even though its dominant cue still matches A.
    mixed = feature(0) * 0.9 + feature(2) * 0.4
    vectors = np.asarray([mixed, feature(1)])
    assert associator.update(2, [track(1, 95), track(2, 105)], vectors, observed=[True, True]) == identities
    # This second mixed crop resembles the first, but not A's original descriptor.
    # Learning from the overlap would incorrectly let it continue as A.
    more_mixed = feature(0) * 0.6 + feature(2) * 0.8
    after = associator.update(
        4, [track(1, 95), track(2, 105)], np.asarray([more_mixed, feature(1)]), observed=[True, True]
    )
    assert after == [-1, identities[1]]


def test_one_canonical_identity_cannot_be_assigned_to_two_lookalikes():
    associator = PersistentPlayerAssociator(fps=30)
    update(associator, 0, [track(1, 100)], [0])
    assert update(associator, 2, [track(8, 90), track(9, 110)], [0, 0]) == [-1, -1]


def test_row_margin_rejects_one_observation_equally_matching_two_identities():
    associator = PersistentPlayerAssociator(fps=30)
    update(associator, 0, [track(1, 50), track(2, 150)], [0, 0])
    assert update(associator, 2, [track(8, 100)], [0]) == [-1]


def test_motion_gate_prevents_appearance_only_teleport():
    associator = PersistentPlayerAssociator(fps=30)
    old = update(associator, 0, [track(1, 50)], [0])[0]
    assert update(associator, 1, [track(9, 1000)], [0])[0] != old


def test_carried_and_observed_tracks_cannot_duplicate_canonical_id():
    associator = PersistentPlayerAssociator(fps=30)
    old = update(associator, 0, [track(1, 100)], [0])[0]
    values = update(associator, 1, [track(1, 100), track(9, 100)], [0, 0], observed=[False, True])
    assert values.count(old) == 1


def test_gallery_and_canonical_history_are_bounded():
    associator = PersistentPlayerAssociator(fps=30)
    for frame in range(20):
        rows = [track(i, i * 100) for i in range(16)]
        assert len({value for value in update(associator, frame, rows, list(range(16))) if value >= 0}) == 16
    assert len(associator._tracks) <= 16
    assert all(len(state.gallery) <= 4 for state in associator._tracks.values())


@pytest.mark.parametrize("bad", [np.zeros((1, 64)), np.full((1, 512), np.nan), np.zeros((2, 512))])
def test_malformed_embeddings_are_rejected_without_advancing_state(bad):
    associator = PersistentPlayerAssociator(fps=30)
    with pytest.raises(ValueError):
        associator.update(0, [track(1, 100)], bad, observed=[True])
    assert update(associator, 0, [track(1, 100)], [0]) == [1]


@pytest.mark.parametrize(
    "rows,flags",
    [
        ([track(1, 100)], []),
        ([track(1, 100)], [1]),
        ([track(1, 100), track(1, 150)], [True, True]),
        ([track(1, np.nan)], [True]),
        ([track(1, 100, width=0)], [True]),
        ([track(1, 100, confidence=np.inf)], [True]),
        ([track(1, 100, confidence=1.1)], [True]),
        ([track(i, i * 100) for i in range(17)], [True] * 17),
    ],
)
def test_invalid_observations_fail_closed(rows, flags):
    with pytest.raises(ValueError):
        PersistentPlayerAssociator(fps=30).update(0, rows, None, observed=flags)


def test_frames_increase_even_across_reset_and_birth_ids_fit_int32():
    associator = PersistentPlayerAssociator(fps=30)
    update(associator, 5, [track(1, 100)], [0])
    associator.reset()
    with pytest.raises(ValueError):
        update(associator, 5, [track(1, 100)], [0])
    with pytest.raises(ValueError):
        update(associator, 2**31 // 16, [track(1, 100)], [0])


@pytest.mark.parametrize("fps", [0, -1, np.nan, True])
def test_invalid_frame_rates_are_rejected(fps):
    with pytest.raises(ValueError):
        PersistentPlayerAssociator(fps=fps)


def test_policy_fingerprint_records_matching_policy():
    associator = PersistentPlayerAssociator(fps=30)
    assert isinstance(associator.policy_fingerprint, str) and associator.policy_fingerprint
    assert associator.policy_fingerprint == PersistentPlayerAssociator(fps=30).policy_fingerprint
