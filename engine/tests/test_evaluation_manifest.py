"""Evaluation must bind labels to actual media and preserve review uncertainty."""

import json

import pytest

from bai_engine.schema.session import MediaInfo, Session, Source, SourceKind
from research.evaluate_session import load_annotations


@pytest.fixture
def sample(tmp_path):
    session = Session(
        session_id="EVAL",
        title="Evaluation",
        source=Source(kind=SourceKind.UPLOAD, uri="source.mp4", sha256="a" * 64),
        media=MediaInfo(fps_num=30000, fps_den=1001, n_frames=300, width=1280, height=720, duration_us=10010000),
    )
    labels = {
        "schema_version": 1,
        "media_sha256": "a" * 64,
        "timebase": "canonical_media_seconds",
        "status": "draft",
        "split": "diagnostic",
        "population": "all_exchanges",
        "exhaustive": True,
        "window_s": [0, 10],
        "rallies": [{"start_s": 1, "end_s": 8}],
    }
    return session, labels, tmp_path / "annotations.json"


def test_draft_cannot_silently_become_accuracy_evidence(sample):
    session, labels, path = sample
    path.write_text(json.dumps(labels))
    with pytest.raises(ValueError, match="draft annotations"):
        load_annotations(path, session)
    assert load_annotations(path, session, allow_draft=True)["status"] == "draft"


@pytest.mark.parametrize(
    "key,value,error",
    [
        ("media_sha256", "b" * 64, "hash"),
        ("timebase", "wall_clock", "canonical"),
        ("window_s", [0, 11], "exceeds"),
        ("exhaustive", False, "exhaustively"),
        ("split", "", "split"),
        ("population", "everything", "population"),
        ("rallies", [{"start_s": 1, "end_s": 12}], "outside"),
    ],
)
def test_incompatible_evidence_is_rejected(sample, key, value, error):
    session, labels, path = sample
    labels[key] = value
    path.write_text(json.dumps(labels))
    with pytest.raises(ValueError, match=error):
        load_annotations(path, session, allow_draft=True)


def test_reviewed_heldout_manifest_accepts_rational_media_timebase(sample):
    session, labels, path = sample
    labels.update(status="reviewed", split="held_out")
    path.write_text(json.dumps(labels))
    assert load_annotations(path, session)["window_s"] == [0, 10]
