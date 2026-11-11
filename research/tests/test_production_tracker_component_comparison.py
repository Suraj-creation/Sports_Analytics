from __future__ import annotations

import copy
import json

import pytest

from research.production_tracker_component_comparison import bounded_windows, compare, sha, validate_row


def row(frame, raw_path):
    return {
        "origin": "fresh_person_detector_postprocess",
        "segment": "doubles_0",
        "frame_idx": frame,
        "pts": frame * 512,
        "time_base": "1/15360",
        "fps": "30",
        "boxes": [[10 + frame, 20, 40 + frame, 90], [100, 25, 140, 95]],
        "scores": [0.9, 0.8],
        "raw_path": str(raw_path),
        "raw_sha256": sha(raw_path),
    }


def test_uniform_windows_are_disjoint_and_not_label_selected():
    assert bounded_windows(900) == [(240, 360), (540, 660)]
    with pytest.raises(ValueError):
        bounded_windows(119)


@pytest.mark.parametrize("origin", ["tracker_estimate", "carried_detection", None])
def test_tracking_and_carried_boxes_are_rejected_as_raw_detector_inputs(tmp_path, origin):
    raw = tmp_path / "raw.npz"
    raw.write_bytes(b"raw evidence")
    item = row(0, raw)
    item["origin"] = origin
    with pytest.raises(ValueError, match="fresh detector"):
        validate_row(item)


def test_source_frame_timestamp_mismatch_is_rejected(tmp_path):
    raw = tmp_path / "raw.npz"
    raw.write_bytes(b"raw evidence")
    item = row(4, raw)
    item["pts"] += 1
    with pytest.raises(ValueError, match="PTS mismatch"):
        validate_row(item)


def test_actual_four_trackers_share_immutable_inputs_and_replay_exactly(tmp_path):
    raw = tmp_path / "raw.npz"
    raw.write_bytes(b"raw evidence")
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    rows = [row(frame, raw) for frame in (0, 2, 4, 6, 20, 22, 24)]
    before = copy.deepcopy(rows)
    manifest = {"completed": True, "annotations_loaded": False, "frame_rows": rows}
    (inputs / "inputs_manifest.json").write_text(json.dumps(manifest))
    output = tmp_path / "output"
    compare(inputs, output)
    result = json.loads((output / "comparison.json").read_text())
    assert set(result["trackers"]) == {"bytetrack", "ocsort", "botsort", "cbiou"}
    for value in result["trackers"].values():
        assert value["exact_output_replay"] is True
        assert value["fresh_input_rows"] == 7
        assert value["HOTA"] is None and value["IDF1"] is None
    assert rows == before
    assert json.loads((inputs / "inputs_manifest.json").read_text()) == manifest


def test_changed_detector_evidence_is_rejected_before_comparison(tmp_path):
    raw = tmp_path / "raw.npz"
    raw.write_bytes(b"raw evidence")
    item = row(0, raw)
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    (inputs / "inputs_manifest.json").write_text(
        json.dumps(
            {
                "completed": True,
                "annotations_loaded": False,
                "frame_rows": [item],
            }
        )
    )
    raw.write_bytes(b"changed")
    with pytest.raises(ValueError, match="evidence changed"):
        compare(inputs, tmp_path / "output")
