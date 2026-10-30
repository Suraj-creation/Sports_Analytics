"""Long white rafters must not become court-line evidence above a visible mat."""
import cv2
import numpy as np
import pytest

from bai_badminton.perception.court_lines import line_features


@pytest.mark.parametrize("floor", [(70, 160, 60), (160, 90, 30), (120, 55, 120), (50, 120, 190)])
def test_only_lines_on_large_playing_surface_survive(floor):
    img = np.full((360, 640, 3), 45, np.uint8)
    img[210:] = floor
    # Long structural rafters, visually similar to white painted lines.
    cv2.line(img, (20, 50), (620, 80), (240, 240, 240), 3)
    cv2.line(img, (180, 5), (180, 180), (240, 240, 240), 3)
    # Real painted floor lines remain available, including the mat edge.
    cv2.line(img, (50, 250), (610, 270), (250, 250, 250), 3)
    cv2.line(img, (300, 215), (340, 359), (250, 250, 250), 3)
    feat = line_features(img, 640)
    assert not feat.mask[:180].any(), "roof rafters are not painted court lines"
    assert feat.mask[240:280].any()
    assert feat.mask[300:350].any()


def test_small_coloured_objects_do_not_define_a_playing_surface():
    img = np.full((360, 640, 3), 70, np.uint8)
    cv2.line(img, (30, 240), (620, 270), (250, 250, 250), 3)
    img[50:70, 50:70] = (40, 180, 40)
    # No large coloured mat: preserve the legacy line evidence for neutral courts.
    assert line_features(img, 640).mask[235:275].any()


def test_line_cache_without_surface_filter_policy_is_stale(tmp_path):
    import msgpack
    from test_plugin_court_lines import chunk, make_session

    from bai_badminton.court import Homography
    from bai_badminton.plugin import StaleCacheError
    from bai_badminton.testing.court_render import MAIN

    session, _ = make_session(tmp_path)
    session._apply_calibration(Homography(MAIN.H, 0.0, 4), mode="lines")
    cached = msgpack.unpackb(session.encode_perception(session.perceive(chunk(0, 4))), raw=False)
    cached["ci"].pop("court_line_surface", None)
    with pytest.raises(StaleCacheError):
        session.decode_perception(msgpack.packb(cached, use_bin_type=True))


def test_plain_coloured_wall_does_not_hide_neutral_floor_lines():
    img = np.full((360, 640, 3), 70, np.uint8)
    cv2.line(img, (30, 240), (620, 270), (250, 250, 250), 3)
    baseline = line_features(img, 640).mask
    img[:100] = (40, 180, 40)
    assert np.array_equal(line_features(img, 640).mask[200:], baseline[200:])
