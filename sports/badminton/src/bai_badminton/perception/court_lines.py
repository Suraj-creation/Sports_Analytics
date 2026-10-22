"""Automatic court calibration from the painted court lines — any camera, any angle, every frame.

A badminton court is a fixed, fully known pattern: six lines across the court (both back boundary
lines, both doubles long-service lines, both short-service lines) and five along it (two doubles and
two singles sidelines, the centre line).  Wherever enough of that pattern is in view, the court →
image homography can be *measured* from the frame itself — no click, no reference frame, no
assumption that the camera holds still or that the broadcast uses one camera.

Pipeline (one frame)
--------------------
1. **Line pixels** — white top-hat of the brightness (thin bright structures), low saturation (the
   lines are white, the mat is not), then specks and letters are dropped by size; the centre ridge
   of what is left is the line-pixel set (a line 12 px wide in a close view counts once, at its
   centre).
2. **Line candidates** — Hough lines on the ridge, refined by a robust fit to their own pixels and
   de-duplicated.
3. **Families** — lines parallel on the floor meet at one vanishing point in the image; the two
   strongest vanishing points split the candidates into the two court directions.
4. **Search** — every pair of lines from one family × every pair from the other, matched to every
   ordered pair of model lines, gives a homography from four intersections (both family↔direction
   assignments and both left/right orders).  Hypotheses are filtered by *physics*: the homography
   must be explainable by a real camera (one focal length, square pixels, centred principal point,
   above the floor, within a stadium's distance) — this rejects nearly all wrong correspondences
   before they are scored.  Survivors are scored by how much of the projected court-line pattern
   lands on line pixels, minus the pattern that lands on bare floor.
5. **Refinement** — ICP: the projected model lines are pulled onto the nearest line pixels
   (shrinking acceptance radius), solving for the homography each round.
6. **Quality** — precision (fraction of the visible model-line length that is painted), support
   (painted length in view), number of supported lines per direction, residual; a fit is only
   ``ok`` if both directions are pinned by at least two lines each.

The fitted homography is decomposed into a camera (focal length, rotation, optical centre in court
metres).  The optical centre identifies the *physical camera*: a pan/tilt/zoom head keeps its centre
while it rotates and zooms, so frames from the broadcast's main camera share it and a cut to the
low side camera, a reverse angle or a slow-motion replay camera does not.

:class:`CourtTracker` runs this per frame: a still camera re-uses the last fit (re-verified every few
frames), a moving one is refined from the previous fit (optical-flow prediction for fast pans) and the
full search re-acquires after cuts and losses.  A frame whose court cannot be verified gets ``None`` —
"court not in view" — never a stale pose.
"""

from __future__ import annotations

import itertools
import math
from collections.abc import Sequence
from dataclasses import dataclass, field, replace

import cv2
import numpy as np
from numpy.typing import NDArray

from bai_badminton.court import (
    DOUBLES_LONG_SERVICE_INSET,
    HALF_LEN,
    NET_HEIGHT_POSTS,
    SHORT_SERVICE,
    WIDTH_DOUBLES,
    WIDTH_SINGLES,
)

Mat = NDArray[np.float64]
Frame = NDArray[np.uint8]

METHOD = "court_lines_v1"

# ---------------------------------------------------------------------------------------- court model
ACROSS_Y: tuple[float, ...] = (
    -HALF_LEN,
    -(HALF_LEN - DOUBLES_LONG_SERVICE_INSET),
    -SHORT_SERVICE,
    SHORT_SERVICE,
    HALF_LEN - DOUBLES_LONG_SERVICE_INSET,
    HALF_LEN,
)
ALONG_X: tuple[float, ...] = (-WIDTH_DOUBLES / 2, -WIDTH_SINGLES / 2, 0.0, WIDTH_SINGLES / 2, WIDTH_DOUBLES / 2)


def _segments() -> list[tuple[tuple[float, float], tuple[float, float], str]]:
    """Painted segments (court metres) with their direction ("across" / "along")."""
    hw = WIDTH_DOUBLES / 2
    segs = [((-hw, y), (hw, y), "across") for y in ACROSS_Y]
    segs += [((x, -HALF_LEN), (x, HALF_LEN), "along") for x in ALONG_X if x != 0.0]
    segs += [((0.0, -HALF_LEN), (0.0, -SHORT_SERVICE), "along"), ((0.0, SHORT_SERVICE), (0.0, HALF_LEN), "along")]
    return segs


SEGMENTS = _segments()


@dataclass(frozen=True)
class _Samples:
    """Points along the painted lines: ``xy`` (N, 2) court metres, ``seg`` segment index, ``nxt`` the
    index of the next point on the same segment (-1 at a segment end; used for per-point length)."""

    xy: Mat
    seg: NDArray[np.int64]
    nxt: NDArray[np.int64]


def _samples(step: float) -> _Samples:
    xy: list[tuple[float, float]] = []
    seg: list[int] = []
    nxt: list[int] = []
    for k, (a, b, _) in enumerate(SEGMENTS):
        n = max(2, int(math.ceil(math.dist(a, b) / step)) + 1)
        base = len(xy)
        for i in range(n):
            u = i / (n - 1)
            xy.append((a[0] + u * (b[0] - a[0]), a[1] + u * (b[1] - a[1])))
            seg.append(k)
            nxt.append(base + i + 1 if i < n - 1 else -1)
    return _Samples(np.array(xy, np.float64), np.array(seg, np.int64), np.array(nxt, np.int64))


COARSE = _samples(0.5)
FINE = _samples(0.1)
_SEG_DIR = np.array([0 if s[2] == "across" else 1 for s in SEGMENTS])


# ---------------------------------------------------------------------------------------- camera
@dataclass(frozen=True)
class CameraPose:
    """A pinhole camera explaining a court homography (square pixels, principal point at the frame
    centre).  ``centre`` is the optical centre in court metres (x across, y along towards the far end,
    z up); a pan/tilt/zoom camera keeps it while it rotates and zooms."""

    focal_px: float
    R: Mat  # world → camera rotation (columns r1, r2, r3)
    t: Mat  # (3,)
    size: tuple[int, int]  # frame (w, h) the pose is expressed in

    @property
    def centre(self) -> Mat:
        return np.asarray(-self.R.T @ self.t, dtype=np.float64)

    @property
    def K(self) -> Mat:
        w, h = self.size
        return np.array([[self.focal_px, 0, w / 2], [0, self.focal_px, h / 2], [0, 0, 1]], dtype=np.float64)

    def project(self, pts3d: NDArray[np.floating] | Sequence[Sequence[float]]) -> Mat:
        """Court points (metres, z up) → image px."""
        p = np.asarray(pts3d, dtype=np.float64).reshape(-1, 3)
        cam = p @ self.R.T + self.t
        uv = cam @ self.K.T
        return np.asarray(uv[:, :2] / uv[:, 2:3], dtype=np.float64)

    def net_top(self) -> tuple[tuple[float, float], tuple[float, float]]:
        """Image positions of the tops of the net posts (left, right as seen from the near end)."""
        hw = WIDTH_DOUBLES / 2
        a, b = self.project([[-hw, 0.0, NET_HEIGHT_POSTS], [hw, 0.0, NET_HEIGHT_POSTS]])
        return (float(a[0]), float(a[1])), (float(b[0]), float(b[1]))

    def to_json(self) -> dict[str, object]:
        c = self.centre
        return {
            "focal_px": round(self.focal_px, 2),
            "centre_m": [round(float(v), 3) for v in c],
            "R": [[round(float(v), 6) for v in row] for row in self.R],
            "t": [round(float(v), 6) for v in self.t],
            "size": list(self.size),
        }


_F_RANGE = (0.3, 12.0)  # focal length in frame widths (ultra-wide … long telephoto)
_ASPECT_TOL = 0.2  # the two court axes must scale alike once the focal length is applied
_ORTHO_TOL = 0.15  # … and stay perpendicular
_HEIGHT_RANGE = (0.8, 60.0)  # camera height above the floor (m)
_MIN_ELEVATION = math.radians(3.0)  # grazing views squeeze the court into a sliver that fits anything
_REACH = (70.0, 90.0)  # |x|, |y| of the camera (m): inside the arena


def _pose_terms(H: NDArray[np.float64], size: tuple[int, int]) -> dict[str, NDArray[np.float64]]:
    """Vectorised decomposition of court→image homographies ``H`` (..., 3, 3) (full or work px of a frame
    of ``size``) into focal length (frame widths), axis aspect/orthogonality residuals and camera centre."""
    w, h = size
    T = np.array([[1 / w, 0, -w / 2 / w], [0, 1 / w, -h / 2 / w], [0, 0, 1]], dtype=np.float64)
    Hn = T @ H
    h1, h2, h3 = Hn[..., :, 0], Hn[..., :, 1], Hn[..., :, 2]
    a1 = h1[..., 0] * h2[..., 0] + h1[..., 1] * h2[..., 1]
    b1 = h1[..., 2] * h2[..., 2]
    a2 = h1[..., 0] ** 2 + h1[..., 1] ** 2 - h2[..., 0] ** 2 - h2[..., 1] ** 2
    b2 = h1[..., 2] ** 2 - h2[..., 2] ** 2
    with np.errstate(divide="ignore", invalid="ignore"):
        winv = -(a1 * b1 + a2 * b2) / (a1**2 + a2**2)  # 1 / f²
        f = 1.0 / np.sqrt(np.where(winv > 0, winv, np.nan))
        f3 = f[..., None]
        k1 = np.concatenate([h1[..., :2] / f3, h1[..., 2:]], axis=-1)
        k2 = np.concatenate([h2[..., :2] / f3, h2[..., 2:]], axis=-1)
        k3 = np.concatenate([h3[..., :2] / f3, h3[..., 2:]], axis=-1)
        n1 = np.linalg.norm(k1, axis=-1)
        n2 = np.linalg.norm(k2, axis=-1)
        r1 = k1 / n1[..., None]
        r2 = k2 / n2[..., None]
        lam = np.sqrt(n1 * n2)
        t = k3 / lam[..., None]
        sgn = np.where(t[..., 2] < 0, -1.0, 1.0)[..., None]  # the court is in front of the camera
        r1, r2, t = r1 * sgn, r2 * sgn, t * sgn
        r3 = np.cross(r1, r2)
        C = -np.stack([(r1 * t).sum(-1), (r2 * t).sum(-1), (r3 * t).sum(-1)], axis=-1)
        aspect = n1 / n2
        ortho = np.abs((r1 * r2).sum(-1))
    return {"f": f, "aspect": aspect, "ortho": ortho, "C": C, "r1": r1, "r2": r2, "t": t}


def _plausible(terms: dict[str, NDArray[np.float64]]) -> NDArray[np.bool_]:
    f, C = terms["f"], terms["C"]
    with np.errstate(invalid="ignore"):
        ok = (
            np.isfinite(f)
            & (f >= _F_RANGE[0])
            & (f <= _F_RANGE[1])
            & (np.abs(terms["aspect"] - 1.0) <= _ASPECT_TOL)
            & (terms["ortho"] <= _ORTHO_TOL)
            & (C[..., 2] >= _HEIGHT_RANGE[0])  # above the floor: also rejects mirrored correspondences
            & (C[..., 2] <= _HEIGHT_RANGE[1])
            & (np.abs(C[..., 0]) <= _REACH[0])
            & (np.abs(C[..., 1]) <= _REACH[1])
            & (np.arctan2(C[..., 2], np.hypot(C[..., 0], C[..., 1])) >= _MIN_ELEVATION)
        )
    return np.asarray(ok, dtype=bool)


def camera_pose(H: Mat, size: tuple[int, int]) -> CameraPose | None:
    """The camera explaining court→image homography ``H`` in a frame of ``size`` (``None``: no plausible
    pinhole camera — a near-affine view, or a wrong homography)."""
    terms = _pose_terms(np.asarray(H, np.float64)[None], size)
    if not bool(_plausible(terms)[0]):
        return None
    r1, r2 = terms["r1"][0], terms["r2"][0]
    # re-orthogonalise (the two axes are only approximately perpendicular): nearest rotation via SVD
    R0 = np.stack([r1, r2, np.cross(r1, r2)], axis=1)
    U, _, Vt = np.linalg.svd(R0)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        return None
    return CameraPose(float(terms["f"][0]) * size[0], R, terms["t"][0], size)


def _norm_px(size: tuple[int, int]) -> Mat:
    """px → centred coordinates in frame widths."""
    w, h = size
    return np.array([[1 / w, 0, -0.5], [0, 1 / w, -h / (2 * w)], [0, 0, 1]], dtype=np.float64)


def rotation_residual(ref: CameraPose, H_ref: Mat, H: Mat, size: tuple[int, int]) -> float:
    """How far the view change reference → this frame is from a pure pan / tilt / zoom of the reference
    camera (0 = exactly one; ≳ 0.1 = a camera at another position).

    The court plane induces the homography ``G = H·H_ref⁻¹`` between the two frames.  A camera that only
    rotates and zooms about its optical centre gives ``G ∝ K·R·K_ref⁻¹``, so ``diag(1/f, 1/f, 1)·G·K_ref``
    must be a scaled rotation for some focal length ``f`` — a linear least-squares problem in ``1/f²``.
    This needs no distance estimate (which a telephoto view pins only loosely)."""
    Tr, Tt = _norm_px(ref.size), _norm_px(size)
    fr = ref.focal_px / ref.size[0]
    G = Tt @ np.asarray(H, np.float64) @ np.linalg.inv(Tr @ np.asarray(H_ref, np.float64))
    M = G @ np.diag([fr, fr, 1.0])
    M = M / np.linalg.norm(M)
    A = np.outer(M[0], M[0]) + np.outer(M[1], M[1])
    B = np.outer(M[2], M[2])
    # w·A + B = λ·I  (w = 1/f²): 9 linear equations in (w, λ)
    X = np.stack([A.ravel(), -np.eye(3).ravel()], axis=1)
    (w, lam), *_ = np.linalg.lstsq(X, -B.ravel(), rcond=None)
    if w <= 0 or lam <= 0:
        return float("inf")
    return float(np.linalg.norm(w * A + B - lam * np.eye(3)) / lam)


_TURN = np.diag([-1.0, -1.0, 1.0])  # the court's 180° symmetry (swaps the ends)
SAME_HEAD_TOL = 0.2  # rotation residual: same head ≤ 0.08 measured, another camera ≥ 0.35
TRACK_CONTINUITY = 0.1  # consecutive frames of one camera: a pure pan / tilt / zoom (residual ≈ 0)


def head_residual(ref: CameraPose, H_ref: Mat, H: Mat, size: tuple[int, int]) -> float:
    """:func:`rotation_residual`, allowing for the court's 180° symmetry (a side-on view whose ends are
    undetermined may be fitted turned round)."""
    return min(rotation_residual(ref, H_ref, H, size), rotation_residual(ref, H_ref, H @ _TURN, size))


@dataclass
class Head:
    """One physical camera: a reference fit and its pose."""

    id: int
    H: Mat
    pose: CameraPose
    frames: int = 0


@dataclass
class CameraRig:
    """The cameras of a production, told apart by the rotation test (:func:`rotation_residual`).  Head 0 is
    the *main* camera — the one the calibration reference was taken from and the only one whose frames
    are analysed (the others are replays, reverse angles, close-ups)."""

    heads: list[Head] = field(default_factory=list)
    max_heads: int = 8
    tol: float = SAME_HEAD_TOL

    @classmethod
    def from_main(cls, H: Mat, pose: CameraPose) -> CameraRig:
        return cls([Head(0, np.asarray(H, np.float64), pose)])

    @property
    def main(self) -> Head | None:
        return self.heads[0] if self.heads else None

    def classify(self, fit: CourtFit) -> int | None:
        """The head that shot ``fit`` (a new head is registered for an unseen camera); ``None`` without a pose."""
        if fit.pose is None or not self.heads:
            return None
        res = [head_residual(h.pose, h.H, fit.H, fit.pose.size) for h in self.heads]
        k = int(np.argmin(res))
        if res[k] <= self.tol or len(self.heads) >= self.max_heads:
            self.heads[k].frames += 1
            return self.heads[k].id
        self.heads.append(Head(len(self.heads), fit.H, fit.pose, 1))
        return len(self.heads) - 1


def group_heads(fits: Sequence[CourtFit], tol: float = SAME_HEAD_TOL) -> list[list[int]]:
    """Indices of ``fits`` grouped by physical camera (greedy, each group led by its best-supported fit)."""
    order = sorted(range(len(fits)), key=lambda i: -fits[i].support)
    groups: list[list[int]] = []
    for i in order:
        f = fits[i]
        if f.pose is None:
            continue
        for g in groups:
            lead = fits[g[0]]
            assert lead.pose is not None
            if head_residual(lead.pose, lead.H, f.H, f.pose.size) <= tol:
                g.append(i)
                break
        else:
            groups.append([i])
    return groups


def choose_main(fits: Sequence[CourtFit]) -> CourtFit | None:
    """The calibration reference for a video from fits of sampled frames: the camera seen most often
    (ties: the one seeing more of the court), represented by its widest view."""
    good = [f for f in fits if f.ok and f.pose is not None]
    if not good:
        return None
    groups = group_heads(good)
    best = max(groups, key=lambda g: (len(g), sum(good[i].support for i in g)))
    return good[best[0]]


def bearing(pose: CameraPose) -> tuple[float, float, float]:
    """(azimuth°, elevation°, distance m) of the camera seen from the court centre; azimuth 0 = behind the
    near baseline, ±90 = level with the net on either side."""
    x, y, z = (float(v) for v in pose.centre)
    return (
        math.degrees(math.atan2(x, -y)),
        math.degrees(math.atan2(z, math.hypot(x, y))),
        math.sqrt(x * x + y * y + z * z),
    )


def same_camera(a: CameraPose, b: CameraPose, angle_tol: float = 8.0, dist_ratio: float = 1.4) -> bool:
    """Are two poses the same physical camera head (same optical centre, any pan / tilt / zoom)?

    Compared by direction and distance from the court centre: a telephoto view pins the camera's
    direction well but its distance (and so its height) only loosely."""
    az_a, el_a, d_a = bearing(a)
    az_b, el_b, d_b = bearing(b)
    daz = abs((az_a - az_b + 180.0) % 360.0 - 180.0)
    return daz <= angle_tol and abs(el_a - el_b) <= angle_tol and max(d_a, d_b) <= dist_ratio * min(d_a, d_b)


# ---------------------------------------------------------------------------------------- fit result
@dataclass(frozen=True)
class CourtFit:
    """A court → image homography measured in one frame, with its evidence."""

    H: Mat  # court metres → frame px (full resolution)
    precision: float  # fraction of the visible model-line length that lies on painted lines
    support: float  # painted model-line length in view, in frame widths
    lines: tuple[int, int]  # supported model lines (across, along)
    rms_px: float  # residual of the matched line points (full-resolution px)
    pose: CameraPose | None
    method: str = "search"  # search | track | static | hold | seed
    ambiguous_end: bool = False  # side-on view: which end is "near" is not determined by the lines
    area: float = 1.0  # fraction of the frame covered by the (doubles) court

    @property
    def ok(self) -> bool:
        return is_valid(self.precision, self.support, self.lines, self.area)

    def to_json(self) -> dict[str, object]:
        return {
            "H": self.H.tolist(),
            "precision": round(self.precision, 4),
            "support": round(self.support, 3),
            "lines": list(self.lines),
            "area": round(self.area, 4),
            "rms_px": round(self.rms_px, 3),
            "pose": self.pose.to_json() if self.pose else None,
            "method": self.method,
            "ambiguous_end": self.ambiguous_end,
            "ok": self.ok,
        }


MIN_PRECISION = 0.6
MIN_SUPPORT = 0.9  # painted length in view ≥ 0.9 frame widths
MIN_LINES = (2, 2)
MIN_AREA = 0.04  # the court must cover ≥ 4 % of the frame (a sliver of collapsed lines fits anything)


def is_valid(precision: float, support: float, lines: tuple[int, int], area: float = 1.0) -> bool:
    return (
        precision >= MIN_PRECISION
        and support >= MIN_SUPPORT
        and lines[0] >= MIN_LINES[0]
        and lines[1] >= MIN_LINES[1]
        and area >= MIN_AREA
    )


# ---------------------------------------------------------------------------------------- line pixels
@dataclass
class LineFeatures:
    """Line-pixel evidence of one frame at work resolution."""

    scale: float  # work px per full px
    size: tuple[int, int]  # work (w, h)
    mask: NDArray[np.uint8]  # 0/255 line pixels
    ridge: NDArray[np.uint8]  # 0/255 line centre pixels
    dt: NDArray[np.float32]  # distance to the nearest ridge pixel
    ridge_xy: NDArray[np.float64]  # (N, 2) ridge pixel coordinates in raster order
    _labels: NDArray[np.int32] | None = None

    @property
    def density(self) -> float:
        return float(self.mask.mean() / 255.0)

    @property
    def labels(self) -> NDArray[np.int32]:
        """Nearest ridge pixel of every pixel, as ``ridge_xy`` row + 1 (computed on first use)."""
        if self._labels is None:
            _, lab = cv2.distanceTransformWithLabels(255 - self.ridge, cv2.DIST_L2, 3, labelType=cv2.DIST_LABEL_PIXEL)
            self._labels = np.asarray(lab, dtype=np.int32)
        return self._labels


def _odd(v: float) -> int:
    k = max(3, int(round(v)))
    return k if k % 2 else k + 1


def downscale(frame: Frame, work_width: int) -> tuple[Frame, float]:
    """``frame`` at ≤ ``work_width`` px wide and the scale (an exact integer ratio uses fast area averaging)."""
    h, w = frame.shape[:2]
    if w <= work_width:
        return frame, 1.0
    s = work_width / w
    interp = cv2.INTER_AREA if w % work_width == 0 else cv2.INTER_LINEAR
    return np.asarray(cv2.resize(frame, (work_width, round(h * s)), interpolation=interp), dtype=np.uint8), s


def line_features(frame: Frame, work_width: int = 960, *, scaled: tuple[Frame, float] | None = None) -> LineFeatures:
    """``scaled``: ``frame`` already downscaled (image, scale) — saves a second resize."""
    img, s = scaled if scaled is not None else downscale(frame, work_width)
    ww, wh = img.shape[1], img.shape[0]
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    sat, val = hsv[..., 1], hsv[..., 2]
    k = _odd(0.016 * ww)
    tophat = cv2.morphologyEx(val, cv2.MORPH_TOPHAT, cv2.getStructuringElement(cv2.MORPH_RECT, (k, k)))
    m = ((tophat >= 22) & (sat <= 115) & (val >= 105)).astype(np.uint8)
    # specks, letters and logo glyphs are short; court lines (even cut by a player) are long
    _, lab, stats, _ = cv2.connectedComponentsWithStats(m, connectivity=8)
    longest = np.maximum(stats[:, cv2.CC_STAT_WIDTH], stats[:, cv2.CC_STAT_HEIGHT])
    keep = (longest >= 0.025 * ww).astype(np.uint8) * 255
    keep[0] = 0
    mask = keep[lab]
    # centre ridge: local maxima of the distance to the line's border (a thick line counts once)
    inner = cv2.distanceTransform(mask, cv2.DIST_L2, 3)
    ridge = ((mask > 0) & (inner >= cv2.dilate(inner, np.ones((3, 3), np.uint8)) - 1e-3)).astype(np.uint8) * 255
    dt = cv2.distanceTransform(255 - ridge, cv2.DIST_L2, 3)
    zy, zx = np.nonzero(ridge)  # raster order == label order (labels number the input's zero pixels)
    ridge_xy = np.stack([zx, zy], axis=1).astype(np.float64)
    return LineFeatures(s, (ww, wh), mask, ridge, np.asarray(dt, np.float32), ridge_xy)


# ---------------------------------------------------------------------------------------- line candidates
@dataclass(frozen=True)
class _Line:
    abc: NDArray[np.float64]  # a x + b y + c = 0, a² + b² = 1
    mid: NDArray[np.float64]  # midpoint of the supporting pixels
    support: float  # supporting ridge pixels

    @property
    def direction(self) -> NDArray[np.float64]:
        return np.array([-self.abc[1], self.abc[0]])


def _fit_line(pts: NDArray[np.float64]) -> NDArray[np.float64] | None:
    if len(pts) < 8:
        return None
    vx, vy, x0, y0 = cv2.fitLine(pts.astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    a, b = float(vy), float(-vx)
    return np.array([a, b, -(a * x0 + b * y0)])


def _canon_line(abc: NDArray[np.float64], c: tuple[float, float]) -> tuple[float, float]:
    """(angle in [0, π), signed offset at point ``c``) — the same line gives the same pair whatever the
    sign of its normal."""
    a, b, k = abc
    if b < 0 or (b == 0 and a < 0):
        a, b, k = -a, -b, -k
    return math.atan2(b, a) % math.pi, a * c[0] + b * c[1] + k


def _same_line(p: tuple[float, float], q: tuple[float, float], ang_tol: float, off_tol: float) -> bool:
    d = abs(p[0] - q[0])
    if min(d, math.pi - d) >= ang_tol:
        return False
    off_q = q[1] if d < math.pi / 2 else -q[1]  # wrapped through 0/π: the normal flipped
    return abs(p[1] - off_q) < off_tol


def detect_lines(feat: LineFeatures, max_lines: int = 28) -> list[_Line]:
    """Long straight structures among the line pixels (refined, de-duplicated, strongest first)."""
    ww, wh = feat.size
    pts = feat.ridge_xy
    if len(pts) < 50:
        return []
    thr = max(25, int(0.06 * ww))
    hough = getattr(cv2, "HoughLinesWithAccumulator", None)
    raw = (hough or cv2.HoughLines)(feat.ridge, 1, np.pi / 360, thr)
    if raw is None:
        return []
    raw = raw.reshape(-1, raw.shape[-1])[:500]
    c = (ww / 2, wh / 2)
    off_tol = max(4.0, 0.005 * ww)
    # 1. non-maximum suppression in Hough space (votes are sorted strongest first)
    seeds: list[tuple[float, float]] = []
    seed_abc: list[NDArray[np.float64]] = []
    for row in raw:
        rho, theta = float(row[0]), float(row[1])
        abc = np.array([math.cos(theta), math.sin(theta), -rho])
        key = _canon_line(abc, c)
        if any(_same_line(key, s, math.radians(2.0), 2 * off_tol) for s in seeds):
            continue
        seeds.append(key)
        seed_abc.append(abc)
        if len(seeds) >= 2 * max_lines:
            break
    # 2. robust refit on each line's own pixels, then de-duplicate the refined lines
    out: list[_Line] = []
    taken: list[tuple[float, float]] = []
    for a0 in seed_abc:
        near = pts[np.abs(pts @ a0[:2] + a0[2]) <= 2.5]
        fitted = _fit_line(near)
        if fitted is None:
            continue
        on = near[np.abs(near @ fitted[:2] + fitted[2]) <= 1.5]
        key = _canon_line(fitted, c)
        if len(on) < thr * 0.7 or any(_same_line(key, t, math.radians(1.5), off_tol) for t in taken):
            continue
        taken.append(key)
        out.append(_Line(fitted, on.mean(axis=0), float(len(on))))
        if len(out) >= max_lines:
            break
    out.sort(key=lambda ln: -ln.support)
    return out


def _vanishing_family(lines: list[_Line], tol: float) -> NDArray[np.bool_] | None:
    """The lines (mask) through the best-supported vanishing point (pairwise intersections and points at
    infinity), or ``None``."""
    n = len(lines)
    if n < 2:
        return None
    L = np.array([ln.abc for ln in lines])
    D = np.array([ln.direction for ln in lines])
    M = np.array([ln.mid for ln in lines])
    w = np.array([ln.support for ln in lines])
    i, j = np.triu_indices(n, 1)
    V = np.concatenate([np.cross(L[i], L[j]), np.concatenate([D, np.zeros((n, 1))], axis=1)])
    V = V / np.maximum(np.linalg.norm(V, axis=1, keepdims=True), 1e-12)
    U = V[:, None, :2] - M[None] * V[:, None, 2:3]  # (cands, lines, 2): line midpoint → vanishing point
    nu = np.linalg.norm(U, axis=2)
    sin = np.abs(D[None, :, 0] * U[..., 1] - D[None, :, 1] * U[..., 0]) / np.maximum(nu, 1e-9)
    sel = (sin <= tol) & (nu > 1e-9)
    score = np.where(sel.sum(1) >= 2, (sel * w[None]).sum(1), 0.0)
    k = int(np.argmax(score))
    return sel[k] if score[k] > 0 else None


def line_families(lines: list[_Line], tol_deg: float = 1.5, apart_deg: float = 8.0) -> tuple[list[_Line], list[_Line]]:
    """Split lines into the two floor directions by their vanishing points (strongest first).  The second
    family may not contain lines (nearly) parallel to the first: tilted copies of the first direction (net
    tape, board edges) must not out-vote the real second direction."""
    tol = math.sin(math.radians(tol_deg))
    first = _vanishing_family(lines, tol)
    if first is None:
        return [], []
    fa = [ln for ln, b in zip(lines, first, strict=True) if b]
    dirs = np.array([ln.direction for ln in fa])
    apart = math.sin(math.radians(apart_deg))
    rest = [
        ln
        for ln, b in zip(lines, first, strict=True)
        if not b and float(np.abs(dirs[:, 0] * ln.direction[1] - dirs[:, 1] * ln.direction[0]).min()) > apart
    ]
    second = _vanishing_family(rest, tol)
    fb = [ln for ln, b in zip(rest, second, strict=True) if b] if second is not None else []
    return fa, fb


def _order(fam: list[_Line], size: tuple[int, int]) -> list[_Line]:
    """Lines of one family in order across the frame (along a transversal through the centre)."""
    if len(fam) < 2:
        return fam
    ref = fam[0].direction
    dirs = np.array([d if d @ ref >= 0 else -d for d in (ln.direction for ln in fam)])
    md = dirs.mean(axis=0)
    n = np.array([-md[1], md[0]]) / (np.linalg.norm(md) or 1.0)
    c = np.array([size[0] / 2, size[1] / 2])
    keys = []
    for ln in fam:
        den = float(ln.abc[:2] @ n)
        keys.append(-(ln.abc[:2] @ c + ln.abc[2]) / den if abs(den) > 1e-9 else 0.0)
    return [fam[i] for i in np.argsort(keys)]


# ---------------------------------------------------------------------------------------- hypotheses
def _square_to_quad(q: NDArray[np.float64]) -> NDArray[np.float64]:
    """Batched homographies mapping the unit square (0,0),(1,0),(1,1),(0,1) → quads ``q`` (N, 4, 2)."""
    x0, y0, x1, y1, x2, y2, x3, y3 = (q[:, i // 2, i % 2] for i in range(8))
    dx1, dx2, dx3 = x1 - x2, x3 - x2, x0 - x1 + x2 - x3
    dy1, dy2, dy3 = y1 - y2, y3 - y2, y0 - y1 + y2 - y3
    den = dx1 * dy2 - dx2 * dy1
    with np.errstate(divide="ignore", invalid="ignore"):
        g = (dx3 * dy2 - dx2 * dy3) / den
        hh = (dx1 * dy3 - dx3 * dy1) / den
    M = np.empty((len(q), 3, 3))
    M[:, 0] = np.stack([x1 - x0 + g * x1, x3 - x0 + hh * x3, x0], axis=1)
    M[:, 1] = np.stack([y1 - y0 + g * y1, y3 - y0 + hh * y3, y0], axis=1)
    M[:, 2] = np.stack([g, hh, np.ones_like(g)], axis=1)
    return M


def _model_to_square() -> tuple[NDArray[np.float64], NDArray[np.int64]]:
    """Affine maps model rectangle → unit square for every ordered model pair; ``(N, 3, 3)`` and the
    (p, q, a, b) indices (across lines p<q, along lines a, b in the image's left→right order)."""
    mats, idx = [], []
    for p, q in itertools.combinations(range(len(ACROSS_Y)), 2):
        for r, s in itertools.combinations(range(len(ALONG_X)), 2):
            for a, b in ((r, s), (s, r)):
                xa, xb, yp, yq = ALONG_X[a], ALONG_X[b], ACROSS_Y[p], ACROSS_Y[q]
                mats.append([[1 / (xb - xa), 0, -xa / (xb - xa)], [0, 1 / (yq - yp), -yp / (yq - yp)], [0, 0, 1]])
                idx.append((p, q, a, b))
    return np.array(mats, np.float64), np.array(idx, np.int64)


_MODEL_SQ, _MODEL_IDX = _model_to_square()


def _project_batch(H: NDArray[np.float64], xy: Mat) -> tuple[NDArray[np.float32], NDArray[np.float32]]:
    """(N,3,3) homographies × (P,2) points → x, y each (N,P) (float32; BLAS matmul)."""
    p = np.concatenate([xy, np.ones((len(xy), 1))], axis=1).T.astype(np.float32)  # (3,P)
    q = np.matmul(H.astype(np.float32), p)  # (N,3,P)
    with np.errstate(divide="ignore", invalid="ignore", over="ignore"):
        inv = 1.0 / q[:, 2]
        return q[:, 0] * inv, q[:, 1] * inv


def _score_batch(H: NDArray[np.float64], feat: LineFeatures, smp: _Samples, tau: float) -> NDArray[np.float64]:
    """Painted length − ½ unpainted length of the projected model lines (work px) for each hypothesis."""
    ww, wh = feat.size
    x, y = _project_batch(H, smp.xy)
    has = np.flatnonzero(smp.nxt >= 0)
    nxt = smp.nxt[has]
    seg = np.zeros_like(x)
    with np.errstate(invalid="ignore", over="ignore"):
        seg[:, has] = np.minimum(np.hypot(x[:, nxt] - x[:, has], y[:, nxt] - y[:, has]), ww)
        vis = (x >= 2) & (x < ww - 2) & (y >= 2) & (y < wh - 2) & np.isfinite(seg)
    seg = np.where(vis, seg, 0.0)
    with np.errstate(invalid="ignore"):
        flat = np.where(vis, y.astype(np.int32) * ww + x.astype(np.int32), 0)
    hit = vis & (feat.dt.ravel()[flat] <= tau)
    good = (seg * hit).sum(1)
    return np.asarray(good - 0.5 * (seg.sum(1) - good), dtype=np.float64)


# a handful of points per painted segment: cheap first pass over all hypotheses
PRE = _samples(1.5)


def _hypotheses(across: list[_Line], along: list[_Line], size: tuple[int, int]) -> NDArray[np.float64]:
    """Plausible court→work-px homographies from every line-pair × model-pair correspondence."""
    if len(across) < 2 or len(along) < 2:
        return np.empty((0, 3, 3))
    quads = []
    for (i, j), (k, m) in itertools.product(
        itertools.combinations(range(len(across)), 2), itertools.combinations(range(len(along)), 2)
    ):
        pts = []
        for u, v in ((i, k), (i, m), (j, m), (j, k)):
            p = np.cross(across[u].abc, along[v].abc)
            if abs(p[2]) < 1e-9:
                break
            pts.append(p[:2] / p[2])
        if len(pts) == 4:
            quads.append(pts)
    if not quads:
        return np.empty((0, 3, 3))
    q = np.array(quads, np.float64)
    w, h = size
    # the four intersections must form a convex quad not absurdly far outside the frame
    far = (np.abs(q[..., 0] - w / 2) > 6 * w) | (np.abs(q[..., 1] - h / 2) > 6 * w)
    cross = []
    for k in range(4):
        a, b, c = q[:, k], q[:, (k + 1) % 4], q[:, (k + 2) % 4]
        cross.append((b[:, 0] - a[:, 0]) * (c[:, 1] - b[:, 1]) - (b[:, 1] - a[:, 1]) * (c[:, 0] - b[:, 0]))
    cr = np.stack(cross, axis=1)
    convex = (cr > 0).all(1) | (cr < 0).all(1)
    q = q[convex & ~far.any(1)]
    if not len(q):
        return np.empty((0, 3, 3))
    M = _square_to_quad(q)
    H = (M[:, None] @ _MODEL_SQ[None]).reshape(-1, 3, 3)
    terms = _pose_terms(H, size)
    return np.asarray(H[_plausible(terms)], dtype=np.float64)


# ---------------------------------------------------------------------------------------- refinement
def _project(H: Mat, xy: Mat) -> Mat:
    p = np.asarray(cv2.perspectiveTransform(xy.reshape(-1, 1, 2), H), dtype=np.float64)
    return p.reshape(-1, 2)


def icp_refine(H: Mat, feat: LineFeatures, taus: Sequence[float] = (8.0, 5.0, 3.0, 2.0, 2.0)) -> Mat | None:
    """Pull the projected model lines onto the nearest line pixels (work px)."""
    ww, wh = feat.size
    src = FINE.xy
    for tau in taus:
        p = _project(H, src)
        if not np.isfinite(p).all():
            return None
        vis = (p[:, 0] >= 1) & (p[:, 0] < ww - 1) & (p[:, 1] >= 1) & (p[:, 1] < wh - 1)
        pi = np.round(p[vis]).astype(np.int32)
        d = feat.dt[pi[:, 1], pi[:, 0]]
        sel = d <= tau
        if int(sel.sum()) < 20:
            return None
        lab = feat.labels[pi[sel, 1], pi[sel, 0]]
        tgt = feat.ridge_xy[np.clip(lab - 1, 0, len(feat.ridge_xy) - 1)]
        H2, _ = cv2.findHomography(src[vis][sel], tgt, 0)
        if H2 is None or not np.isfinite(H2).all():
            return None
        H = np.asarray(H2 / H2[2, 2], dtype=np.float64)
    return H


def visible_area(H: Mat, size: tuple[int, int]) -> float:
    """Fraction of a ``size`` frame covered by the doubles court under court→image ``H``."""
    w, h = size
    hw = WIDTH_DOUBLES / 2
    # clip the court to the camera's half-space first: corners behind the camera project nonsensically
    corners = np.array([[-hw, HALF_LEN], [hw, HALF_LEN], [hw, -HALF_LEN], [-hw, -HALF_LEN]])
    q = np.asarray(H, np.float64) @ np.concatenate([corners, np.ones((4, 1))], axis=1).T
    if (q[2] <= 0).any():
        return 0.0
    poly = [tuple(p) for p in (q[:2] / q[2]).T]
    # Sutherland–Hodgman clip against the frame (well-defined for any quad, unlike OpenCV's convex-convex
    # intersection, which a wrong homography's folded quad can send astray)
    for axis, bound, keep_low in ((0, 0.0, False), (0, float(w), True), (1, 0.0, False), (1, float(h), True)):
        out: list[tuple[float, float]] = []
        for k in range(len(poly)):
            a, b = poly[k - 1], poly[k]
            ina = a[axis] <= bound if keep_low else a[axis] >= bound
            inb = b[axis] <= bound if keep_low else b[axis] >= bound
            if ina != inb:
                t = (bound - a[axis]) / (b[axis] - a[axis])
                out.append((a[0] + t * (b[0] - a[0]), a[1] + t * (b[1] - a[1])))
            if inb:
                out.append(b)
        poly = out
        if not poly:
            return 0.0
    xs, ys = np.array([p[0] for p in poly]), np.array([p[1] for p in poly])
    area = 0.5 * abs(float(np.dot(xs, np.roll(ys, -1)) - np.dot(ys, np.roll(xs, -1))))
    return area / (w * h)


def measure(H: Mat, feat: LineFeatures, tau: float | None = None) -> tuple[float, float, tuple[int, int], float]:
    """(precision, support in frame widths, supported lines (across, along), rms px) of ``H`` (work px)."""
    ww, wh = feat.size
    tau = max(2.0, 2.5 * ww / 960) if tau is None else tau
    p = _project(H, FINE.xy)
    if not np.isfinite(p).all():
        return 0.0, 0.0, (0, 0), float("inf")
    seg_len = np.zeros(len(p))
    has = FINE.nxt >= 0
    seg_len[has] = np.linalg.norm(p[FINE.nxt[has]] - p[has], axis=1)
    vis = (p[:, 0] >= 2) & (p[:, 0] < ww - 2) & (p[:, 1] >= 2) & (p[:, 1] < wh - 2)
    seg_len = np.where(vis, np.minimum(seg_len, ww), 0.0)
    pi = np.clip(np.round(p), 0, [ww - 1, wh - 1]).astype(np.int32)
    d = feat.dt[pi[:, 1], pi[:, 0]].astype(np.float64)
    hit = vis & (d <= tau)
    vis_len = float(seg_len.sum())
    hit_len = float((seg_len * hit).sum())
    precision = hit_len / vis_len if vis_len > 0 else 0.0
    lines = [0, 0]
    for k in range(len(SEGMENTS)):
        sel = FINE.seg == k
        vl, hl = float(seg_len[sel].sum()), float((seg_len * hit)[sel].sum())
        if hl >= 0.04 * ww and hl >= 0.5 * vl:
            lines[_SEG_DIR[k]] += 1
    rms = float(np.sqrt(np.mean(d[hit] ** 2))) if hit.any() else float("inf")
    return precision, hit_len / ww, (lines[0], lines[1]), rms


def _canonical(H: Mat, size: tuple[int, int]) -> tuple[Mat, CameraPose | None, bool]:
    """Resolve the court's 180° symmetry: the near end (y < 0) is the end on the camera's side.
    Returns (H, pose, ambiguous) — ambiguous when the camera sits level with the net (side view)."""
    pose = camera_pose(H, size)
    if pose is None:
        return H, None, True
    c = pose.centre
    if c[1] > 0:
        H = H @ np.diag([-1.0, -1.0, 1.0])
        pose = camera_pose(H, size)
        if pose is None:
            return H, None, True
        c = pose.centre
    return H, pose, bool(abs(c[1]) < max(2.0, 0.35 * abs(c[0])))


def _to_full(H_work: Mat, s: float) -> Mat:
    S_inv = np.diag([1 / s, 1 / s, 1.0])
    H = S_inv @ H_work
    return np.asarray(H / H[2, 2], dtype=np.float64)


def _to_work(H_full: Mat, s: float) -> Mat:
    H = np.diag([s, s, 1.0]) @ H_full
    return np.asarray(H / H[2, 2], dtype=np.float64)


def _fit(H_work: Mat, feat: LineFeatures, full: tuple[int, int], method: str, prev: CourtFit | None = None) -> CourtFit:
    """``prev``: the fit this one was tracked from — its end assignment is kept (continuity beats the
    near-end rule, which is undecided for a side-on camera); otherwise the near end is canonical."""
    prec, sup, lines, rms = measure(H_work, feat)
    if prev is None:
        H, pose, amb = _canonical(_to_full(H_work, feat.scale), full)
    else:
        H = _to_full(H_work, feat.scale)
        pose, amb = camera_pose(H, full), prev.ambiguous_end
    return CourtFit(H, prec, sup, lines, rms / feat.scale, pose, method, amb, visible_area(H, full))


# ---------------------------------------------------------------------------------------- one frame
MAX_DENSITY = 0.2  # more line pixels than this: crowd / texture, not a court view
TOP_LINES = 7  # strongest lines per family taken into the search
PRE_KEEP = 600  # hypotheses kept after the sparse pre-score
REFINE_TOP = 8


def search(feat: LineFeatures, full: tuple[int, int]) -> CourtFit | None:
    """Full court search in one frame (no prior)."""
    if feat.density > MAX_DENSITY:
        return None
    lines = detect_lines(feat)
    fa, fb = line_families(lines)
    fa, fb = (_order(f[:TOP_LINES], feat.size) for f in (fa, fb))
    hyps = [_hypotheses(fa, fb, feat.size), _hypotheses(fb, fa, feat.size)]
    H = np.concatenate([h for h in hyps if len(h)], axis=0) if any(len(h) for h in hyps) else np.empty((0, 3, 3))
    if not len(H):
        return None
    # two passes: a sparse pre-score over every hypothesis, the full coarse score over the best few hundred
    pre = np.concatenate([_score_batch(H[i : i + 8192], feat, PRE, 5.0) for i in range(0, len(H), 8192)])
    keep = np.argsort(-pre)[:PRE_KEEP]
    H = H[keep]
    scores = _score_batch(H, feat, COARSE, 4.0)
    order = np.argsort(-scores)
    candidates: list[CourtFit] = []
    seen: list[Mat] = []
    for i in order[: REFINE_TOP * 3]:
        if scores[i] <= 0 or len(seen) >= REFINE_TOP:
            break
        Hi = H[i] / H[i][2, 2]
        if any(_close(Hi, s, feat.size) for s in seen):
            continue
        seen.append(Hi)
        Hr = icp_refine(Hi, feat)
        if Hr is None or camera_pose(Hr, feat.size) is None:
            continue
        fit = _fit(Hr, feat, full, "search")
        candidates.append(fit)
    return select_primary(candidates, full)


def select_primary(fits: Sequence[CourtFit], size: tuple[int, int]) -> CourtFit | None:
    """Choose the dominant visible court, after rejecting weak geometric fits.

    Area and centrality only break near-quality ties: otherwise a spurious
    quadrilateral spanning several courts could defeat a measured court.
    """
    valid = [f for f in fits if f.ok]
    if not valid:
        return None
    precision = max(f.precision for f in valid)
    valid = [f for f in valid if f.precision >= precision - 0.05]
    w, h = size

    def score(f: CourtFit) -> float:
        centre = _project(f.H, np.array([[0.0, 0.0]]))[0]
        distance = float(np.linalg.norm((centre - [w / 2, h / 2]) / [w, h]))
        centrality = max(0.0, 1.0 - distance)
        return f.support * f.precision**2 * (1.0 + 0.5 * f.area + 0.3 * centrality)

    return max(valid, key=score)


def _rank(f: CourtFit) -> tuple[bool, float]:
    return f.ok, f.support * f.precision**2


def _close(A: Mat, B: Mat, size: tuple[int, int], tol: float = 3.0) -> bool:
    pts = np.array([[x, y] for x in (-3.05, 3.05) for y in (-6.7, 0.0, 6.7)])
    pa, pb = _project(A, pts), _project(B, pts)
    if not (np.isfinite(pa).all() and np.isfinite(pb).all()):
        return False
    return float(np.linalg.norm(pa - pb, axis=1).max()) < tol


def detect_court(frame: Frame, work_width: int = 960) -> CourtFit | None:
    """Measure the court in a single frame (``None``: no court found)."""
    feat = line_features(frame, work_width)
    return search(feat, (frame.shape[1], frame.shape[0]))


def refine_court(frame: Frame, H: Mat, work_width: int = 960, method: str = "seed") -> CourtFit | None:
    """Refine a given court→image homography (e.g. a human calibration) against this frame's lines."""
    feat = line_features(frame, work_width)
    Hr = icp_refine(_to_work(np.asarray(H, np.float64), feat.scale), feat, taus=(12.0, 8.0, 5.0, 3.0, 2.0, 2.0))
    if Hr is None:
        return None
    return _fit(Hr, feat, (frame.shape[1], frame.shape[0]), method)


# ---------------------------------------------------------------------------------------- per frame tracking
_LK = {"winSize": (21, 21), "maxLevel": 4, "criteria": (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03)}


def _flow(prev: NDArray[np.uint8], cur: NDArray[np.uint8]) -> Mat | None:
    """Global image motion prev → cur (homography) from tracked corners; ``None`` when unreliable."""
    pts = cv2.goodFeaturesToTrack(prev, 400, 0.01, 8, blockSize=7)
    if pts is None or len(pts) < 25:
        return None
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, pts, None, **_LK)  # type: ignore[call-overload]
    ok = st.ravel() == 1
    if int(ok.sum()) < 20:
        return None
    g, inl = cv2.findHomography(pts[ok], nxt[ok], cv2.RANSAC, 2.0, maxIters=500, confidence=0.995)
    if g is None or inl is None or float(inl.mean()) < 0.3:
        return None
    return np.asarray(g, dtype=np.float64)


def _thumb(gray: NDArray[np.uint8]) -> NDArray[np.uint8]:
    return np.asarray(cv2.resize(gray, (160, 90), interpolation=cv2.INTER_AREA), dtype=np.uint8)


def _still(a: NDArray[np.uint8], b: NDArray[np.uint8]) -> bool:
    return float((cv2.absdiff(a, b) > 10).mean()) < 0.03


@dataclass
class _TrackState:
    frame: int
    gray: NDArray[np.uint8]  # work-res grey (optical-flow prediction)
    thumb: NDArray[np.uint8]  # 160×90 (still-camera test)
    fit: CourtFit
    since_verify: int = 0
    held: int = 0


@dataclass
class TrackerStats:
    frames: int = 0
    searches: int = 0
    refined: int = 0
    static: int = 0
    held: int = 0
    found: int = 0
    seconds: float = 0.0


@dataclass
class CourtTracker:
    """Per-frame court fits for a video, in frame order.

    Cost model: a still camera costs a thumbnail comparison (re-verified every ``verify_every`` frames);
    a moving one a line-pixel pass and an ICP refinement at ``track_width``; the full search (at the
    sharper ``search_width``, for thin far lines) runs only at cuts and, backing off, while the court is lost.
    """

    search_width: int = 960
    track_width: int = 640
    search_every: int = 4  # frames between full searches while the court is lost
    verify_every: int = 8  # a still camera's fit is re-verified this often
    max_hold: int = 3  # blurred frames bridged with the previous fit
    min_run: int = 4  # a newly acquired court must hold this many frames (a one-frame fit is a fluke)
    stats: TrackerStats = field(default_factory=TrackerStats)
    _st: _TrackState | None = None
    _lost: int = 0
    _run: int = 0  # length of the current run of fits (continues across chunks)
    _locked: Mat | None = None

    def reset(self) -> None:
        self._st, self._lost, self._run = None, 0, 0
        self._locked = None

    def lock(self, H: Mat) -> None:
        """Keep the selected court for a fixed camera; loss must not select a neighbor."""
        self.reset()
        self._locked = np.array(H, dtype=np.float64, copy=True)

    def track(self, frames: Sequence[Frame], cuts: Sequence[bool], start: int) -> list[CourtFit | None]:
        """The court fit of each frame (``None``: court not verifiably in view).  ``cuts[i]``: a camera
        cut at frame ``i``.  Chunks must be fed in frame order for continuity (an out-of-order chunk —
        a seek preview — simply starts from a search)."""
        import time

        t0 = time.perf_counter()
        out: list[CourtFit | None] = []
        st = self._st
        run = self._run
        if st is not None and st.frame != start - 1:
            st, run = None, 0
        for i, frame in enumerate(frames):
            f = start + i
            if cuts[i]:
                st, self._lost = None, 0
            fit, st = self._one(frame, f, st)
            # a run ends at a cut, a loss, or a re-acquisition straight after a fit (an undetected cut)
            ended = cuts[i] or fit is None or (fit.method == "search" and run > 0)
            if ended and 0 < run < self.min_run:
                # the run that just ended was too short to trust (a fluke fit): drop what is in this chunk
                for j in range(max(0, i - run), i):
                    out[j] = None
            run = 0 if ended else run
            run = run + 1 if fit is not None else 0
            out.append(fit)
            self._lost = 0 if fit is not None else self._lost + 1
        self._st = st
        self._run = run
        self.stats.frames += len(frames)
        self.stats.found += sum(1 for x in out if x is not None)
        self.stats.seconds += time.perf_counter() - t0
        return out

    def _one(self, frame: Frame, f: int, st: _TrackState | None) -> tuple[CourtFit | None, _TrackState | None]:
        full = (frame.shape[1], frame.shape[0])
        small = downscale(frame, self.track_width)
        gray = np.asarray(cv2.cvtColor(small[0], cv2.COLOR_BGR2GRAY), dtype=np.uint8)
        thumb = _thumb(gray)
        fit: CourtFit | None
        if self._locked is not None:
            if st is not None and _still(st.thumb, thumb) and st.since_verify < self.verify_every:
                self.stats.static += 1
                return replace(st.fit, method="static"), _TrackState(f, gray, st.thumb, st.fit, st.since_verify + 1, 0)
            fit = refine_court(frame, self._locked, self.search_width)
            # A moving camera, changed scene or mismatched lines invalidate the
            # lock. Do not search the frame for another equally plausible court.
            if fit is None or not fit.ok or not _close(fit.H, self._locked, full, tol=0.02 * full[0]):
                return None, None
            self.stats.refined += 1
            # Preserve the reference geometry instead of accumulating line jitter.
            fit = replace(fit, H=self._locked, pose=camera_pose(self._locked, full))
            return fit, _TrackState(f, gray, thumb, fit)
        if st is not None and _still(st.thumb, thumb) and st.since_verify < self.verify_every:
            self.stats.static += 1
            return replace(st.fit, method="static"), _TrackState(f, gray, st.thumb, st.fit, st.since_verify + 1, 0)
        if st is not None:
            feat = line_features(frame, scaled=small)
            fit, connected = self._follow(feat, full, st, gray)
            if fit is not None:
                self.stats.refined += 1
                return fit, _TrackState(f, gray, thumb, fit)
            # the image still connects to the previous frame (motion blur, a player over the lines): bridge
            # briefly; it does not (a cut the histogram missed — e.g. green court to green court): search now
            if connected and st.held < self.max_hold:
                self.stats.held += 1
                # keep the last *verified* view for the still-camera test: an unverified frame (possibly an
                # undetected cut) must never become the image a stale fit is matched against
                return replace(st.fit, method="hold"), _TrackState(
                    f, gray, st.thumb, st.fit, self.verify_every, st.held + 1
                )
            st = None  # lost: search this very frame
        elif not self._search_due():
            return None, None
        self.stats.searches += 1
        fit = search(line_features(frame, self.search_width), full)
        if fit is None or not fit.ok:
            return None, None
        return fit, _TrackState(f, gray, thumb, fit)

    def _search_due(self) -> bool:
        """While the court is lost, search often at first (a cut back to the court), then back off (a long
        close-up or crowd shot costs little)."""
        n = self._lost
        return n % self.search_every == 0 if n < 4 * self.search_every else n % (4 * self.search_every) == 0

    def _follow(
        self, feat: LineFeatures, full: tuple[int, int], st: _TrackState, gray: NDArray[np.uint8]
    ) -> tuple[CourtFit | None, bool]:
        """Refine the previous fit onto this frame's lines.  The court is a repetitive pattern, so a prediction
        that is off by half a line spacing converges onto the *neighbouring* lines and still scores well —
        hence (1) the camera motion is predicted from the whole image (optical flow; the crowd and boards move
        with a panning camera too) before the lines are trusted, and (2) a fit is only accepted if the change
        from the previous frame is a pure pan / tilt / zoom of the same camera (a fit on the wrong lines implies
        a camera that jumped position).  Returns (fit or None, whether the image motion from the previous frame
        could be measured at all — if not, the content changed: a cut)."""
        prev = _to_work(st.fit.H, feat.scale)
        g = _flow(st.gray, gray)
        starts = [g @ prev] if g is not None else []
        starts.append(prev)  # flow failed, or a shaky estimate: try the previous pose as well
        for H0 in starts:
            Hr = icp_refine(H0, feat, taus=(6.0, 4.0, 2.5, 2.0))
            if Hr is None:
                continue
            fit = _fit(Hr, feat, full, "track", prev=st.fit)
            if (
                fit.ok
                and fit.pose is not None
                and st.fit.pose is not None
                and rotation_residual(st.fit.pose, st.fit.H, fit.H, full) <= TRACK_CONTINUITY
            ):
                return fit, True
        return None, g is not None

    def seed(self, frame: Frame, frame_idx: int, H: Mat) -> CourtFit | None:
        """Start tracking from a known calibration of ``frame`` (e.g. a human one)."""
        fit = refine_court(frame, H, self.search_width)
        if fit is None or not fit.ok:
            return None
        gray = np.asarray(cv2.cvtColor(downscale(frame, self.track_width)[0], cv2.COLOR_BGR2GRAY), dtype=np.uint8)
        self._st, self._lost, self._run = _TrackState(frame_idx, gray, _thumb(gray), fit), 0, self.min_run
        return fit
