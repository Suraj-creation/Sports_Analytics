"""Pure synthetic/model-observation checks; no new OCR, video decoding or GT."""

import json
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from observation_scope_proposal import capture_scope

from bai_badminton.perception.scoreboard import ScoreboardReader, parse_scoreboard

HERE = Path(__file__).resolve().parent
FIXTURE = json.loads((HERE / "fixtures/retained_observations.json").read_text())


def box(x, y, width=60, height=20):
    return [[x, y], [x + width, y], [x + width, y + height], [x, y + height]]


class SyntheticVisibleFields:
    """Deterministic fields inside crop, not learned OCR or sporting labels."""

    def __call__(self, image):
        fields = [(box(10, 10), "ALPHA"), (box(120, 10, 20), "21"), (box(10, 40), "BETA"), (box(120, 40, 20), "19")]
        if image[0, 0, 0]:
            fields += [(box(200, 10, 20), "1"), (box(200, 40, 20), "0")]
        h, w = image.shape[:2]
        fields = [(b, t) for b, t in fields if b[2][0] <= w and b[2][1] <= h]
        return SimpleNamespace(boxes=[b for b, _ in fields], txts=[t for _, t in fields], scores=[0.99] * len(fields))


def parse(raw, frame):
    return parse_scoreboard(raw["boxes"], raw["texts"], raw["scores"], frame)


def test_successful_stale_parse_never_reaches_miss_unlock():
    image = np.zeros((720, 1280, 3), np.uint8)
    reader = ScoreboardReader(SyntheticVisibleFields(), every=30)
    assert reader.maybe_read(0, image).rows == (("ALPHA", 21), ("BETA", 19))
    original_roi = reader.roi
    expanded = image.copy()
    expanded[0, 0] = 255
    for frame in range(30, 391, 30):
        assert reader.maybe_read(frame, expanded).rows == (("ALPHA", 21), ("BETA", 19))
        assert reader._misses == 0 and reader.roi == original_roi
    assert reader.calls == 14


def test_same_crop_observations_cannot_certify_outside_column_absence():
    stub = SyntheticVisibleFields()
    old = np.zeros((56, 165, 3), np.uint8)
    new = old.copy()
    new[0, 0] = 255
    a, b = stub(old), stub(new)
    assert a.boxes == b.boxes and a.txts == b.txts and a.scores == b.scores
    complete = np.zeros((180, 576, 3), np.uint8)
    complete[0, 0] = 255
    full = stub(complete)
    assert parse_scoreboard(full.boxes, full.txts, full.scores, 30)[0].rows == (("ALPHA", 1), ("BETA", 0))


def test_actual12604_sparse_narrow_and_full_differ_without_changing_parser():
    row = FIXTURE["observations"]["12604"]
    assert parse(row["reader_input_and_ocr"]["ocr"], 12604)[0].rows == (("AXELSEN", 16), ("ANTONSEN", 21))
    assert parse(row["full_top_left_ocr"], 12604)[0].rows == (("AXELSEN", 13), ("ANTONSEN", 2))


def test_changes_entirely_outside_crop_have_identical_observed_pixels():
    old = np.zeros((720, 1280, 3), np.uint8)
    changed_outside = old.copy()
    changed_outside[10:60, 200:220] = 255
    # This is a mathematical crop counterexample, not OCR-rendered sporting GT.
    assert not np.array_equal(old, changed_outside)
    assert np.array_equal(old[:56, :165], changed_outside[:56, :165])
    stub = SyntheticVisibleFields()
    assert stub(old[:56, :165]).txts == stub(changed_outside[:56, :165]).txts


def test_actual11346_fused_tokens_stay_unresolved():
    raw = FIXTURE["observations"]["11346"]["full_top_left_ocr"]
    assert "165" in raw["texts"] and "211" in raw["texts"]
    assert parse(raw, 11346) is None


def test_actual22924_full_corner_cannot_replace_positive_primary_read():
    row = FIXTURE["observations"]["22924"]
    assert parse(row["full_top_left_ocr"], 22924) is None
    positive = FIXTURE["cached_positive22924"]
    assert positive["r"] == [["AXELSEN", 9], ["ANTONSEN", 12]]
    assert positive["c"] == 0.96547


def test_recorded_gap_unlocked_and_has_no_full_corner_gain():
    gap = FIXTURE["gap"]
    row = next(x for x in gap["rows"] if x["frame"] == 9604)
    assert row["arms"]["current"]["after"]["roi"] is None
    for arm in ("current", "full_corner_candidate"):
        summary = gap["summary"][arm]
        assert summary["scheduled_calls"] == 105 and summary["readouts"] == 2
        assert [x["frame"] for x in summary["first_readouts"]] == [12604, 12634]
        assert not summary["missing_cached_readout_frames"]
        assert not summary["extra_readout_frames"]
        assert not summary["cached_row_mismatches"]


def scope(reading=None, raw=None, **override):
    values = dict(
        frame=22924,
        image_sha256="a" * 64,
        image_shape=(720, 1280, 3),
        crop=(274, 34, 504, 95),
        raw=raw,
        primary_reading=reading,
    )
    return capture_scope(**(values | override))


def test_proposal_preserves_positive_and_absent_raw_without_forging_tokens():
    positive = FIXTURE["cached_positive22924"]
    reading = {"frame_idx": 22924, "rows": positive["r"], "confidence": positive["c"]}
    got = scope(reading=reading)
    assert got["primary_reading"] == reading and got["raw_ocr"] is None
    assert got["current_column_status"] == "unknown" and got["layout_evidence"] is None
    assert got["additional_ocr_calls"] == 0 and got["physical_ground_truth"] is None


def test_proposal_retains_fused_raw_tokens_without_aliasing_or_splitting():
    raw = FIXTURE["observations"]["11346"]["full_top_left_ocr"]
    got = scope(frame=11346, raw=raw)
    assert got["raw_ocr"] == raw and got["raw_ocr"] is not raw
    assert got["primary_reading"] is None and got["current_column_status"] == "unknown"


@pytest.mark.parametrize(
    "override",
    [
        {"frame": True},
        {"image_sha256": "unknown"},
        {"crop": (-1, 0, 100, 100)},
        {"image_shape": (720, 1280)},
        {"primary_reading": {"frame_idx": 3}},
    ],
)
def test_proposal_rejects_foreign_or_invalid_evidence_binding(override):
    with pytest.raises(ValueError):
        scope(**override)


def test_test1_ordinary_corroboration_remains_distinct_from_source_frame_call():
    ordinary = json.loads((HERE / "fixtures/test1_ordinary_observations.json").read_text())
    assert ordinary["source_frame"] == 8634
    assert [x["f"] for x in ordinary["readings"]] == [8582, 8612]
    assert all(x["r"] == [["AN S.Y.", 20], ["INTANON", 20]] for x in ordinary["readings"])
