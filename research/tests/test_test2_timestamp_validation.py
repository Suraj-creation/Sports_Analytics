from fractions import Fraction

import pytest

from research.test2_timestamp_validation import compare_timestamps


def test_different_time_bases_can_represent_same_presentation_times():
    source = [Fraction(i * 512, 15360) for i in range(10)]
    proxy = [Fraction(i, 30) for i in range(10)]
    assert compare_timestamps(source, proxy)["every_source_proxy_timestamp_equal"]


@pytest.mark.parametrize("proxy", [[Fraction(0)], [Fraction(0), Fraction(1, 29)], []])
def test_missing_or_shifted_proxy_frames_are_rejected(proxy):
    with pytest.raises(ValueError):
        compare_timestamps([Fraction(0), Fraction(1, 30)], proxy)


def test_equal_but_nonmonotonic_timelines_are_rejected():
    with pytest.raises(ValueError, match="nonmonotonic"):
        compare_timestamps([Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)])
