import hashlib

import pytest

from research.production_external_semantic_replay import capture_core_source_snapshot, verify_core_source_snapshot
from research.test2_failure_package import content_transition_summary


def test_core_source_capture_preserves_actual_bytes_and_detects_later_mutation(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    code = source / "engine/src/component.py"
    code.parent.mkdir(parents=True)
    code.write_bytes(b"actual = 1\n")
    expected = {"engine/src/component.py": hashlib.sha256(code.read_bytes()).hexdigest()}
    output = tmp_path / "experiment"
    receipt = capture_core_source_snapshot(expected, output, root=source)
    verify_core_source_snapshot(output, receipt)
    archived = output / "executed_core_source/engine/src/component.py"
    assert archived.read_bytes() == code.read_bytes()
    archived.write_bytes(b"actual = 2\n")
    with pytest.raises(ValueError, match="snapshot bytes changed"):
        verify_core_source_snapshot(output, receipt)


def test_source_change_during_capture_cannot_be_reported_as_executed_source(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    (source / "component.py").write_bytes(b"changed")
    with pytest.raises(ValueError, match="before snapshot capture"):
        capture_core_source_snapshot({"component.py": "0" * 64}, tmp_path / "output", root=source)


def test_negative_or_withheld_scene_evidence_does_not_count_as_a_cut():
    rows = [
        {"f": 8, "ce": 2, "cc": {"hypothesis": False}, "cd": None},
        {"f": 9, "ce": 2, "cc": {"hypothesis": True}, "cd": {"decision": "no_barrier"}},
        {"f": 10, "ce": 3, "cc": {"hypothesis": True}, "cd": {"decision": "unknown"}},
    ]
    result = content_transition_summary(rows, {r["f"]: r for r in rows})
    assert result["content_evidence_frames"] == [8, 9, 10]
    assert result["content_hypothesis_frames"] == [9, 10]
    assert result["content_change_frames"] == [10]
    assert result["layout_no_barrier_frames"] == [9]
    assert result["layout_unknown_frames"] == [10]  # explicit raw fallback can reset tracking, not certify a cut
