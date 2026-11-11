"""Own-source preparation and rejection of borrowed/tampered image caches."""

import csv
import json
from fractions import Fraction

import av
import cv2
import numpy as np
import pytest

from research.test2_failure_package import sha, verified_pts
from research.test2_source_frame_cache import prepare, verified_cache


@pytest.fixture
def prepared(tmp_path):
    source = tmp_path / "source.mp4"
    encoder = cv2.VideoWriter(str(source), cv2.VideoWriter_fourcc(*"mp4v"), 30, (32, 24))
    assert encoder.isOpened()
    for color in (25, 120, 225):
        encoder.write(np.full((24, 32, 3), color, np.uint8))
    encoder.release()
    pts = tmp_path / "source_frame_pts.csv"
    with av.open(str(source)) as container, pts.open("w", newline="") as stream:
        video = container.streams.video[0]
        writer = csv.writer(stream)
        writer.writerow(["source_frame", "pts", "time_base_num", "time_base_den", "source_time_sec"])
        for index, frame in enumerate(container.decode(video)):
            writer.writerow(
                [
                    index,
                    frame.pts,
                    video.time_base.numerator,
                    video.time_base.denominator,
                    float(frame.pts * video.time_base),
                ]
            )
    output = tmp_path / "source_frames"
    manifest = prepare(source, pts, output, 3, Fraction(30))
    return source, pts, output, manifest


def checked(prepared, **changes):
    source, pts, output, _ = prepared
    kwargs = {
        "source_sha256": sha(source),
        "pts_csv": pts,
        "n_frames": 3,
        "rate": Fraction(30),
        "source_size": [32, 24],
        "mapping": verified_pts(pts, 3, Fraction(30)),
        "selected": [0, 2],
    }
    kwargs.update(changes)
    return verified_cache(output, **kwargs)


def test_label_free_preparation_preserves_exact_frames_and_verifies_every_selected_image(prepared):
    manifest, images = checked(prepared)
    assert manifest["labels_or_predictions_accessed"] is False
    assert manifest["source_sha256_before_after_equal"] is True
    assert list(images) == [0, 2]
    assert len(manifest["frames"]) == 3


def test_borrowed_source_cache_is_rejected(prepared):
    with pytest.raises(ValueError, match="provenance"):
        checked(prepared, source_sha256="different match")


def test_selected_image_tampering_is_rejected(prepared):
    (_, _, output, _) = prepared
    (output / "frames/2.jpg").write_bytes(b"tampered")
    with pytest.raises(ValueError, match="image bytes"):
        checked(prepared)


def test_selected_image_symlink_cannot_borrow_other_file(prepared, tmp_path):
    (_, _, output, _) = prepared
    image = output / "frames/2.jpg"
    original = tmp_path / "saved.jpg"
    image.rename(original)
    image.symlink_to(original)
    with pytest.raises(ValueError, match="symlinked"):
        checked(prepared)


@pytest.mark.parametrize(
    "field,value",
    [
        ("source_pts_sha256", "wrong"),
        ("fps", "25"),
        ("source_size", [64, 48]),
        ("labels_or_predictions_accessed", True),
    ],
)
def test_mixed_pts_rate_size_or_label_provenance_is_rejected(prepared, field, value):
    _, _, output, manifest = prepared
    manifest[field] = value
    (output / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="provenance"):
        checked(prepared)


def test_reordered_or_edited_pts_catalogue_is_rejected(prepared):
    _, _, output, manifest = prepared
    manifest["frames"][1]["pts"] += 1
    (output / "manifest.json").write_text(json.dumps(manifest))
    with pytest.raises(ValueError, match="row/PTS"):
        checked(prepared)
