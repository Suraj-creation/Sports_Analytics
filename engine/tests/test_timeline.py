from fractions import Fraction

import pytest
from hypothesis import given
from hypothesis import strategies as st

from bai_engine.timeline import TimeFormatError, Timeline, format_clock, parse_clock

NTSC = Fraction(30000, 1001)


class TestConversions:
    def test_integer_fps_exact(self) -> None:
        tl = Timeline(Fraction(30), 54_000)
        assert tl.frame_to_pts_us(0) == 0
        assert tl.frame_to_pts_us(30) == 1_000_000
        assert tl.pts_us_to_frame(1_000_000) == 30
        assert tl.duration_us == 1_800_000_000

    def test_ntsc_no_drift_over_long_match(self) -> None:
        tl = Timeline(NTSC, 200_000)
        # 30-minute mark is frame 53_946 at 29.97 fps
        frame = tl.pts_us_to_frame(30 * 60 * 1_000_000)
        assert tl.frame_to_pts_us(frame) <= 30 * 60 * 1_000_000 < tl.frame_to_pts_us(frame + 1)

    def test_from_rate_parses_ffprobe_strings(self) -> None:
        assert Timeline.from_rate("30000/1001", 10).fps == NTSC
        assert Timeline.from_rate("25", 10).fps == 25
        assert Timeline.from_rate(29.97, 10).fps == NTSC

    def test_seconds_to_frame_rounds_media_time(self) -> None:
        tl = Timeline(Fraction(30), 1000)
        assert tl.seconds_to_frame(1 / 30 * 10 - 1e-9) == 10
        assert tl.seconds_to_frame(-1) == 0
        assert tl.seconds_to_frame(10_000) == 999  # clamped

    def test_invalid(self) -> None:
        with pytest.raises(ValueError):
            Timeline(Fraction(0), 10)
        with pytest.raises(ValueError):
            Timeline(Fraction(30), 10).frame_to_pts_us(-1)

    @given(
        st.integers(min_value=0, max_value=500_000),
        st.sampled_from([Fraction(25), Fraction(30), NTSC, Fraction(50), Fraction(60)]),
    )
    def test_frame_pts_roundtrip(self, frame: int, fps: Fraction) -> None:
        tl = Timeline(fps, 500_001)
        assert tl.pts_us_to_frame(tl.frame_to_pts_us(frame)) == frame

    @given(st.integers(min_value=0, max_value=500_000))
    def test_seconds_roundtrip(self, frame: int) -> None:
        tl = Timeline(NTSC, 500_001)
        assert tl.seconds_to_frame(tl.frame_to_seconds(frame)) == frame


class TestClock:
    @pytest.mark.parametrize(
        ("text", "seconds"),
        [
            ("07:00", 420),
            ("7:05", 425),
            ("45", 45),
            ("1:05:30", 3930),  # real H:MM:SS with seconds > 23 (rejected by the legacy validator)
            ("75:10", 4510),  # minutes > 59 are fine in M:SS form
        ],
    )
    def test_standard_forms(self, text: str, seconds: int) -> None:
        assert parse_clock(text) == seconds * 1_000_000

    def test_first_field_above_23_is_minutes(self) -> None:
        # 28:58:00 means 28 m 58 s — the legacy video_highlight_processor read it as 28 h.
        assert parse_clock("28:58:00") == (28 * 60 + 58) * 1_000_000

    def test_legacy_mmss00_only_when_requested(self) -> None:
        assert parse_clock("10:15:00") == (10 * 3600 + 15 * 60) * 1_000_000
        assert parse_clock("10:15:00", legacy_mmss00=True) == (10 * 60 + 15) * 1_000_000

    def test_fraction(self) -> None:
        assert parse_clock("1:02.5") == 62_500_000

    @pytest.mark.parametrize("bad", ["", "ab", "1:60", "1:2:3:4", "1:61:00"])
    def test_rejects(self, bad: str) -> None:
        with pytest.raises(TimeFormatError):
            parse_clock(bad)

    def test_format(self) -> None:
        assert format_clock(0) == "0:00"
        assert format_clock(62_500_000, millis=True) == "1:02.500"
        assert format_clock(3_930_000_000) == "1:05:30"

    @given(st.integers(min_value=0, max_value=10 * 3600 * 1_000_000))
    def test_format_parse_roundtrip_to_ms(self, pts_us: int) -> None:
        text = format_clock(pts_us, millis=True)
        assert parse_clock(text) == (pts_us // 1000) * 1000
