import numpy as np
import pytest

from bai_badminton.perception.player_association import PersistentPlayerAssociator


def rows(ids):
    return [(tid, np.array([i * 100.0, 10, i * 100.0 + 40, 110]), 0.95) for i, tid in enumerate(ids)]


def test_four_distinct_people_keep_identity_across_longer_gap_and_raw_id_swap():
    tracker = PersistentPlayerAssociator(30, retention_seconds=8)
    features = np.eye(4, 512)
    original = tracker.update(0, rows([1, 2, 3, 4]), features, observed=[True] * 4)
    order = [1, 0, 3, 2]
    found = tracker.update(90, rows([100, 200, 300, 400]), features[order], observed=[True] * 4)
    assert found == [original[i] for i in order]
    assert len(set(found)) == 4
    tracker.reset()
    assert set(tracker.update(91, rows([1, 2, 3, 4]), features, observed=[True] * 4)).isdisjoint(original)


def test_dormant_identity_requires_distinctive_neural_evidence_and_expires():
    tracker = PersistentPlayerAssociator(30, retention_seconds=8)
    features = np.eye(4, 512)
    original = tracker.update(0, rows([1, 2, 3, 4]), features, observed=[True] * 4)
    # Recycled raw IDs without appearance do not prove continuity after a gap.
    assert tracker.update(90, rows([1, 2, 3, 4]), None, observed=[True] * 4) == [-1] * 4
    assert tracker.update(100, rows([9, 8, 7, 6]), features, observed=[True] * 4) == original
    returned = tracker.update(341, rows([9, 8, 7, 6]), features, observed=[True] * 4)
    assert set(returned).isdisjoint(original)


@pytest.mark.parametrize("retention", [0, -1, True, float("inf"), 301])
def test_retention_is_explicit_finite_and_bounded(retention):
    with pytest.raises(ValueError):
        PersistentPlayerAssociator(30, retention_seconds=retention)


def test_dormant_near_tie_cannot_disappear_below_the_absolute_similarity_threshold():
    tracker = PersistentPlayerAssociator(30, retention_seconds=8)
    gallery = np.zeros((2, 512))
    gallery[0, 0] = gallery[1, 0] = 0.9
    gallery[0, 1] = np.sqrt(1 - 0.9**2)
    gallery[1, 1] = -np.sqrt(1 - 0.9**2)
    tracker.update(0, rows([1, 2]), gallery, observed=[True, True])
    returned = np.zeros((1, 512))
    returned[0, 0], returned[0, 1] = 0.9, 0.02
    returned[0, 2] = np.sqrt(1 - 0.9**2 - 0.02**2)
    # Similarities around .81 are both below .9: no candidate may claim the person.
    assert tracker.update(90, rows([99]), returned, observed=[True]) == [-1]
    # A high absolute score still cannot erase a close competitor from the margin.
    tracker = PersistentPlayerAssociator(30, retention_seconds=8)
    returned[0] = 0
    returned[0, 0] = 1
    gallery[0, 0], gallery[1, 0] = 0.91, 0.89
    gallery[0, 1], gallery[1, 1] = np.sqrt(1 - 0.91**2), -np.sqrt(1 - 0.89**2)
    tracker.update(0, rows([1, 2]), gallery, observed=[True, True])
    assert tracker.update(90, rows([99]), returned, observed=[True]) == [-1]
