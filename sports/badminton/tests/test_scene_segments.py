"""Scene timeline: frame views become stable segments; flicker is absorbed; only final segments are emitted."""

from __future__ import annotations

from bai_badminton.events.scene import SceneSegmenter


def feed(seg: SceneSegmenter, runs: list[tuple[str, int | None, int]]) -> list[tuple[int, int, str, int | None]]:
    f, out = 0, []
    for view, head, n in runs:
        for _ in range(n):
            seg.add(f, view, head, 0.9 if view != "none" else None)
            f += 1
        out += [(s.start, s.end, s.view, s.head) for s in seg.drain()]
    return out + [(s.start, s.end, s.view, s.head) for s in seg.flush()]


def test_segments_follow_the_views() -> None:
    got = feed(SceneSegmenter(min_frames=5), [("main", 0, 20), ("none", None, 10), ("alt", 1, 8), ("main", 0, 6)])
    assert got == [(0, 19, "main", 0), (20, 29, "none", None), (30, 37, "alt", 1), (38, 43, "main", 0)]


def test_a_blip_is_absorbed_into_its_surroundings() -> None:
    got = feed(SceneSegmenter(min_frames=5), [("main", 0, 20), ("none", None, 2), ("main", 0, 10)])
    assert got == [(0, 31, "main", 0)]


def test_a_short_blip_before_a_real_change_does_not_split_the_timeline() -> None:
    got = feed(SceneSegmenter(min_frames=5), [("main", 0, 10), ("alt", 2, 2), ("none", None, 12)])
    assert got == [(0, 11, "main", 0), (12, 23, "none", None)]


def test_different_other_cameras_are_different_segments() -> None:
    got = feed(SceneSegmenter(min_frames=3), [("alt", 1, 6), ("alt", 2, 6)])
    assert got == [(0, 5, "alt", 1), (6, 11, "alt", 2)]


def test_segments_are_only_emitted_once_final() -> None:
    seg = SceneSegmenter(min_frames=5)
    for f in range(10):
        seg.add(f, "main", 0, 0.9)
    for f in range(10, 13):  # a change that has not lasted min_frames yet
        seg.add(f, "none", None, None)
    assert seg.drain() == []
    for f in range(13, 16):
        seg.add(f, "none", None, None)
    done = seg.drain()
    assert [(s.start, s.end, s.view) for s in done] == [(0, 9, "main")]
    assert done[0].quality == 0.9
