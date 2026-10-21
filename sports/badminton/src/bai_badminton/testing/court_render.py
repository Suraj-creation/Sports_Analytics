"""Synthetic broadcast frames of a badminton court seen by a known pinhole camera.

The court plane is rendered as a texture in court metres (mat, run-off, surround, painted lines,
white decals and lettering as distractors) and warped into the image by the camera's exact court →
image homography; the sky above the floor's horizon is a busy "crowd".  Used to test court-line
calibration, camera identification and tracking against ground truth.
"""

from __future__ import annotations

from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray

from bai_badminton.court import COURT_LINES, HALF_LEN, WIDTH_DOUBLES

Mat = NDArray[np.float64]
SIZE = (1280, 720)
_M_PER_PX = 0.015  # texture resolution
_EXTENT = (11.0, 16.0)  # texture half-size (m): x, y
LINE_M = 0.04  # painted line width


@dataclass(frozen=True)
class Camera:
    """A camera at ``centre`` (court metres, z up) looking at ``target`` with focal length ``f`` px."""

    centre: tuple[float, float, float]
    target: tuple[float, float, float]
    f: float
    size: tuple[int, int] = SIZE

    @property
    def R(self) -> Mat:
        c, t = np.asarray(self.centre, float), np.asarray(self.target, float)
        z = (t - c) / np.linalg.norm(t - c)
        x = np.cross(z, [0.0, 0.0, 1.0])
        x /= np.linalg.norm(x)
        y = np.cross(z, x)
        return np.stack([x, y, z])  # world → camera (rows)

    @property
    def K(self) -> Mat:
        w, h = self.size
        return np.array([[self.f, 0, w / 2], [0, self.f, h / 2], [0, 0, 1.0]])

    @property
    def H(self) -> Mat:
        """Court plane (metres) → image px."""
        R = self.R
        t = -R @ np.asarray(self.centre, float)
        Hm = self.K @ np.stack([R[:, 0], R[:, 1], t], axis=1)
        return np.asarray(Hm / Hm[2, 2], dtype=np.float64)


def _texture(seed: int) -> tuple[NDArray[np.uint8], Mat]:
    """The floor texture and its texture-px → court-metre map."""
    rng = np.random.default_rng(seed)
    ex, ey = _EXTENT
    w, h = int(2 * ex / _M_PER_PX), int(2 * ey / _M_PER_PX)
    T = np.array([[_M_PER_PX, 0, -ex], [0, -_M_PER_PX, ey], [0, 0, 1.0]])  # px → m (y up the texture)
    Tinv = np.linalg.inv(T)

    def px(x: float, y: float) -> tuple[int, int]:
        p = Tinv @ np.array([x, y, 1.0])
        return int(round(p[0])), int(round(p[1]))

    tex = np.empty((h, w, 3), np.uint8)
    tex[:] = (150, 95, 40)  # surround (blue-ish in BGR)
    hw, hl = WIDTH_DOUBLES / 2 + 1.6, HALF_LEN + 2.2
    cv2.rectangle(tex, px(-hw, hl), px(hw, -hl), (70, 160, 60), -1)  # green mat with run-off
    for word, (x, y) in (("ODENSE", (-2.6, -8.2)), ("VICTOR", (0.4, -8.2)), ("ODENSE", (-2.6, 9.0))):
        cv2.putText(tex, word, px(x, y), cv2.FONT_HERSHEY_SIMPLEX, 3.0, (245, 245, 245), 9)
    cv2.putText(tex, "HSBC", px(-0.9, 0.9), cv2.FONT_HERSHEY_SIMPLEX, 2.4, (240, 240, 240), 8)
    for _ in range(25):  # random white stripes on the surround (hoarding feet, tape, decals)
        x, y = rng.uniform(-ex, ex), rng.uniform(-ey, ey)
        if abs(x) < hw + 0.3 and abs(y) < hl + 0.3:
            continue
        cv2.line(tex, px(x, y), px(x + rng.uniform(-2, 2), y + rng.uniform(-1, 1)), (235, 235, 235), 4)
    lw = max(1, int(round(LINE_M / _M_PER_PX)))
    for a, b in COURT_LINES[:-1]:  # every painted line (the last entry is the net's ground line)
        cv2.line(tex, px(*a), px(*b), (250, 250, 250), lw, cv2.LINE_AA)
    noise = rng.integers(0, 8, tex.shape, dtype=np.uint8)
    return np.asarray(cv2.add(tex, noise), dtype=np.uint8), T


_TEX_CACHE: dict[int, tuple[NDArray[np.uint8], Mat]] = {}
_CROWD_CACHE: dict[int, NDArray[np.uint8]] = {}


def render(
    cam: Camera,
    seed: int = 0,
    players: list[tuple[float, float]] | None = None,
    blur: float = 0.6,
) -> NDArray[np.uint8]:
    """A frame of the court seen by ``cam``; ``players`` are dark figures standing at court positions."""
    if seed not in _TEX_CACHE:
        _TEX_CACHE[seed] = _texture(seed)
    tex, T = _TEX_CACHE[seed]
    w, h = cam.size
    M = cam.H @ T  # texture px → image px
    img = cv2.warpPerspective(tex, M, (w, h), flags=cv2.INTER_AREA, borderMode=cv2.BORDER_CONSTANT)
    # the crowd: everything whose viewing ray does not hit the floor in front of the camera — a texture fixed
    # in the world (indexed by the ray's azimuth / elevation), so it moves with a panning camera as in reality
    uu, vv = np.meshgrid(np.arange(w), np.arange(h))
    rays = np.stack([uu, vv, np.ones_like(uu)], axis=-1).reshape(-1, 3).astype(np.float64) @ np.linalg.inv(cam.K).T
    world = rays @ cam.R  # ray directions in the world (z up)
    down = world[:, 2].reshape(h, w) < -1e-6
    if seed not in _CROWD_CACHE:
        rng = np.random.default_rng(seed + 1)
        small = rng.integers(0, 255, (128, 1024, 3), dtype=np.uint8)
        _CROWD_CACHE[seed] = (cv2.resize(small, (8192, 1024), interpolation=cv2.INTER_NEAREST) * 0.45).astype(np.uint8)
    sky = _CROWD_CACHE[seed]
    az = np.arctan2(world[:, 0], world[:, 1]).reshape(h, w)
    el = np.arctan2(world[:, 2], np.hypot(world[:, 0], world[:, 1])).reshape(h, w)
    mx = ((az + np.pi) / (2 * np.pi) * (sky.shape[1] - 1)).astype(np.float32)
    my = ((0.5 - el / np.pi) * (sky.shape[0] - 1)).astype(np.float32)
    crowd = cv2.remap(sky, mx, my, cv2.INTER_LINEAR)
    hit = down & (img.sum(axis=2) > 0)
    img = np.where(hit[..., None], img, crowd)
    for x, y in players or []:
        foot = cam.H @ np.array([x, y, 1.0])
        if foot[2] <= 0:
            continue
        u, v = foot[:2] / foot[2]
        top = cam.K @ (cam.R @ (np.array([x, y, 1.8]) - np.asarray(cam.centre)))
        if top[2] <= 0:
            continue
        hh = max(4.0, v - top[1] / top[2])
        cv2.rectangle(img, (int(u - 0.18 * hh), int(v - hh)), (int(u + 0.18 * hh), int(v)), (40, 30, 160), -1)
    if blur > 0:
        img = cv2.GaussianBlur(img, (0, 0), blur)
    return np.asarray(img, dtype=np.uint8)


def noise_frame(seed: int = 0, size: tuple[int, int] = SIZE) -> NDArray[np.uint8]:
    """A frame with no court (a crowd / close-up stand-in)."""
    rng = np.random.default_rng(seed)
    w, h = size
    small = rng.integers(0, 255, (h // 16, w // 16, 3), dtype=np.uint8)
    return np.asarray(cv2.GaussianBlur(cv2.resize(small, (w, h)), (0, 0), 3), dtype=np.uint8)


MAIN = Camera((0.0, -21.6, 7.5), (0.0, 0.0, 0.0), 1900.0)
FOLLOW = Camera((0.0, -21.0, 5.2), (0.0, 3.0, 0.0), 4500.0)  # a lower, tighter camera behind the baseline
SIDE = Camera((-12.0, -2.7, 7.3), (0.5, 0.0, 0.0), 2600.0)
