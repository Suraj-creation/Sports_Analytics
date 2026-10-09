"""Compact columnar wire format for track windows (engine → API → browser).

A window of per-frame samples is sent as one msgpack map of parallel arrays — ~10× smaller than
a list of objects and trivially decoded into typed arrays in the browser::

    {"v": 1, "from": 1200, "to": 1259,
     "shuttle": {"f": [...], "x": [...], "y": [...], "c": [...]},          # visible frames only
     "players": {"P1": {"f": [...], "b": [x1,y1,x2,y2,...], "k": [x,y,s × 17 ...] | null,
                        "cx": [...], "cy": [...]}, "P2": {...}}}

Coordinates are rounded to 0.1 px / 1 cm to keep payloads small.
"""

from __future__ import annotations

from typing import Any

import msgpack

from bai_engine.schema.tracks import TrackObject, TrackSample

VERSION = 1


def _r(v: float | None, nd: int = 1) -> float | None:
    return None if v is None else round(float(v), nd)


def encode_tracks(samples: list[TrackSample], frame_from: int, frame_to: int) -> bytes:
    shuttle: dict[str, list[Any]] = {"f": [], "x": [], "y": [], "c": []}
    players: dict[str, dict[str, list[Any]]] = {}
    for s in samples:
        if s.obj is TrackObject.SHUTTLE:
            if s.visible and s.x is not None and s.y is not None:
                shuttle["f"].append(s.frame_idx)
                shuttle["x"].append(_r(s.x))
                shuttle["y"].append(_r(s.y))
                shuttle["c"].append(_r(s.conf, 2))
        elif s.obj is TrackObject.PLAYER and s.player_id:
            p = players.setdefault(s.player_id, {"f": [], "b": [], "k": [], "cx": [], "cy": [], "t": []})
            p["f"].append(s.frame_idx)
            p["t"].append(s.track_id)
            p["b"].extend(_r(v) for v in (s.bbox or (0, 0, 0, 0)))
            if s.keypoints is not None:
                for x, y, sc in s.keypoints:
                    p["k"].extend((_r(x), _r(y), _r(sc, 2)))
            else:
                p["k"].extend([0.0] * 51)
            p["cx"].append(_r(s.court_x, 2))
            p["cy"].append(_r(s.court_y, 2))
    payload = {"v": VERSION, "from": frame_from, "to": frame_to, "shuttle": shuttle, "players": players}
    out = msgpack.packb(payload, use_bin_type=True)
    assert isinstance(out, bytes)
    return out


def decode_tracks(data: bytes) -> dict[str, Any]:
    out = msgpack.unpackb(data, raw=False)
    assert isinstance(out, dict)
    return out
