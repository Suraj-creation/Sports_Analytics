"""All requested cases survive partitioning; reuse needs a genuine completed source bundle."""

import pytest

from partition_pending_visuals import partition, validate_bundle


def test_complete_plan_partition_preserves_all_and_excludes_existing_frames():
    frames = [{"frame": frame, "reasons": ["synthetic source diagnostic"]} for frame in range(300)]
    batches, reused = partition(frames, set(range(25, 200)))
    assert reused == list(range(25, 200))
    assert all(len(batch) <= 128 for batch in batches)
    assert {x["frame"] for batch in batches for x in batch} | set(reused) == set(range(300))
    assert sum(map(len, batches)) == 125


@pytest.mark.parametrize(
    "frames,limit",
    [([{"frame": 1}, {"frame": 1}], 128), ([{"frame": True}], 128), ([{"frame": 1}], 129), ([{"frame": 1}], 0)],
)
def test_duplicate_or_invalid_source_plan_cannot_hide_cases(frames, limit):
    with pytest.raises(ValueError):
        partition(frames, set(), limit)


def test_pending_bundle_must_not_be_used_to_skip_requested_cases(tmp_path):
    with pytest.raises(ValueError, match="not complete"):
        validate_bundle(tmp_path, {})
