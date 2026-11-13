"""Configuration/metadata boundaries require no media decoding or external tools."""

from dataclasses import replace
from fractions import Fraction

import pytest

from bai_engine.decode import FileDecoder, SegmentDecoder
from bai_engine.media.ffmpeg import MediaError
from bai_engine.media.probe import ProbeResult, validate
from bai_engine.runtime.device import ort_runtime
from bai_engine.store.sessions import MediaPaths


@pytest.mark.parametrize("invalid", [0, -1, True, 2.5])
def test_decoder_buffer_sizes_are_positive_integer_limits(tmp_path, invalid):
    with pytest.raises(ValueError, match="chunk_frames"):
        FileDecoder(tmp_path / "never-opened.mp4", invalid)
    with pytest.raises(ValueError, match="frames_per_segment"):
        SegmentDecoder(MediaPaths(tmp_path), invalid)
    with pytest.raises(ValueError, match="threads"):
        SegmentDecoder(MediaPaths(tmp_path), 60, threads=invalid)


@pytest.mark.parametrize("duration", [float("nan"), float("inf"), -1.0, 0.0])
def test_nonfinite_or_nonpositive_duration_cannot_pass_validation(duration):
    metadata = ProbeResult("mov,mp4,m4a,3gp,3g2,mj2", duration, 640, 360, "h264",
                           Fraction(30), Fraction(30), 300, False)
    with pytest.raises(MediaError, match="finite positive duration"):
        validate(metadata, 1000)


def test_duration_limit_itself_must_be_finite_and_positive():
    metadata = ProbeResult("mov,mp4,m4a,3gp,3g2,mj2", 10.0, 640, 360, "h264",
                           Fraction(30), Fraction(30), 300, False)
    validate(metadata, 1000)
    for maximum in (float("nan"), float("inf"), 0):
        with pytest.raises(MediaError, match="duration limit"):
            validate(replace(metadata), maximum)


def test_provider_priority_is_distinct_from_verified_node_placement():
    class Session:
        def get_providers(self):
            return ["CUDAExecutionProvider", "CPUExecutionProvider"]

    runtime = ort_runtime("onnx-cuda", Session())
    assert runtime["backend_fallback"] is False
    assert runtime["node_placement_verified"] is False
    assert runtime["execution_evidence"] == "initialized_provider_priority"
