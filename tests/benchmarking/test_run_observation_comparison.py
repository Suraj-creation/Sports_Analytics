import json

import msgpack
import pytest

from research.next_evidence_compare_runs import folded_events, frame_rows


def write_cache(run, frames, *, start=None, end=None, name="seg_00000.msgpack"):
    root = run / "runtime/sessions/test/perception"
    root.mkdir(parents=True, exist_ok=True)
    (root / name).write_bytes(
        msgpack.packb(
            {
                "start": frames[0]["f"] if start is None else start,
                "end": frames[-1]["f"] if end is None else end,
                "frames": frames,
            },
            use_bin_type=True,
        )
    )


def test_recorded_cache_comparison_retains_missing_and_rejected_fields(tmp_path):
    frames = [{"f": 0, "s": None, "diagnostic": {"rejection": "mask"}}, {"f": 1, "s": [5, 8]}]
    write_cache(tmp_path, frames)
    assert list(frame_rows(tmp_path)) == frames


@pytest.mark.parametrize("indices", [[0, 2], [0, 0], [1, 2]])
def test_cache_gaps_duplicates_and_nonzero_origin_are_not_hidden(tmp_path, indices):
    write_cache(tmp_path, [{"f": index, "s": None} for index in indices])
    with pytest.raises(ValueError, match="duplicate/gap"):
        list(frame_rows(tmp_path))


def test_cache_header_and_observation_frame_identity_must_agree(tmp_path):
    write_cache(tmp_path, [{"f": 0, "s": None}], end=1)
    with pytest.raises(ValueError, match="cache range"):
        list(frame_rows(tmp_path))


def test_event_comparison_folds_repeated_supersession_and_retraction(tmp_path):
    events = [
        {"event_id": "a", "type": "contact", "frame_start": 40, "status": "confirmed"},
        {"event_id": "b", "type": "contact", "frame_start": 41, "status": "corrected", "supersedes": "a"},
        {"event_id": "c", "type": "contact", "frame_start": 41, "status": "retracted", "supersedes": "b"},
        {"event_id": "d", "type": "contact", "frame_start": 60, "status": "confirmed"},
    ]
    (tmp_path / "events.jsonl").write_text("".join(json.dumps(event) + "\n" for event in events))
    assert folded_events(tmp_path) == [events[-1]]
