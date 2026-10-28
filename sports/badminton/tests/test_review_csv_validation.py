"""Review input must not become ground truth without complete, source-bound labels."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[3] / "research/evaluation/validate_review_csv.py"


def _module():
    spec = importlib.util.spec_from_file_location("task1_review_validator", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _write(tmp_path, rows):
    fields = [
        "clip",
        "session_id",
        "media_sha256",
        "canonical_start_s",
        "canonical_end_s",
        "clip_start_s",
        "clip_end_s",
        "activity",
        "match_status",
        "participant_changes",
        "reviewer",
        "notes",
    ]
    manifest = {
        "schema_version": 1,
        "timebase": "canonical_media_seconds",
        "clips": [
            {
                "clip": "c.mp4",
                "session_id": "S1",
                "media_sha256": "a" * 64,
                "canonical_start_s": 10,
                "canonical_end_s": 30,
            }
        ],
    }
    mp = tmp_path / "manifest.json"
    mp.write_text(json.dumps(manifest))
    cp = tmp_path / "review.csv"
    with cp.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            base = {
                "clip": "c.mp4",
                "session_id": "S1",
                "media_sha256": "a" * 64,
                "canonical_start_s": "10",
                "canonical_end_s": "30",
                "reviewer": "reviewer",
                "activity": "rally",
                "match_status": "unknown",
            }
            writer.writerow({**base, **row})
    return cp, mp


def test_complete_review_maps_clip_seconds_to_source(tmp_path):
    cp, mp = _write(
        tmp_path,
        [{"clip_start_s": "0", "clip_end_s": "5"}, {"clip_start_s": "5", "clip_end_s": "20", "activity": "unknown"}],
    )
    result = _module().validate_review(cp, mp)
    assert result["status"] == "reviewer_provided"
    assert result["clips"][0]["intervals"][0]["canonical_start_s"] == 10
    assert result["clips"][0]["intervals"][1]["canonical_end_s"] == 30
    assert result["clips"][0]["intervals"][1]["activity"] == "unknown"


@pytest.mark.parametrize(
    "rows",
    [
        [{"clip_start_s": "", "clip_end_s": "20"}],
        [{"clip_start_s": "0", "clip_end_s": "19"}],
        [{"clip_start_s": "0", "clip_end_s": "10"}, {"clip_start_s": "9", "clip_end_s": "20"}],
        [{"clip_start_s": "0", "clip_end_s": "20", "reviewer": ""}],
        [{"clip_start_s": "0", "clip_end_s": "20", "media_sha256": "b" * 64}],
    ],
)
def test_incomplete_overlapping_or_unbound_review_is_rejected(tmp_path, rows):
    cp, mp = _write(tmp_path, rows)
    with pytest.raises(ValueError):
        _module().validate_review(cp, mp)
