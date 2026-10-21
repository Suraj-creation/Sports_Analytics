"""Camera-motion tracking: keeps the court calibration locked to a panning / tilting / zooming camera.

A court homography ``H`` (court metres → image px) is only valid for the camera pose it was fitted
on.  Broadcast badminton is shot by operators who follow the rally, so the pose changes all the
time and a fixed ``H`` slides off the court within seconds.  A pan/tilt/zoom camera rotates about
(almost exactly) its optical centre, and for a pure rotation the image motion between two frames is
a single homography **for every scene point regardless of depth** — so the crowd, the hoardings and
the floor all move together and the court's pose can be recovered from the background even while
players occlude the lines.

:class:`CameraTracker` estimates, per frame, ``G_t``: the homography mapping *reference-frame*
pixels to *frame-t* pixels (the reference being the frame the calibration was made on).  The
court→image mapping at frame ``t`` is then simply ``G_t · H``.

Estimators
----------
* **Direct keyframe alignment** (every frame) — the best-overlapping keyframe is warped by the
  predicted pose and Lucas-Kanade corners are tracked from that warp to the live frame; the residual
  is a small homography that refines the pose (two iterations).  Each frame is compared with a stored
  *image*, never with the previous estimate, so error does not accumulate frame after frame.
* **Keyframes** — the reference only overlaps the live frame where the camera still looks at the
  same area; after a big pan or zoom that is a thin strip and the fit is ill-conditioned.  Whenever
  no keyframe covers enough of the frame, the (confirmed) current frame becomes a keyframe with its
  known pose, so drift grows with the number of keyframes rather than the number of frames.
* **Reference anchor** — SIFT features matched against the keyframes + RANSAC.  Used to *acquire*
  the pose (chunk start, after a camera cut, after a loss) and, every so often, to pull the estimate
  back to the original reference (the one thing keyframes cannot do on their own).
* **Frame-to-frame chain** — corners tracked from the previous frame; only the fallback for a pan
  fast enough that the previous pose is too far off for the direct step.

* **Court-plane verification** — a pose is only accepted if the *floor* lines up: the reference's floor
  region, warped by the pose, must be visible and its edge structure must correlate with the live frame.
  This is what rejects the broadcast's *other cameras*: a pose estimated from the advertising boards or
  the crowd is a perfectly good homography of *that* plane and the wrong one for the court (a camera
  that has moved, rather than panned, no longer sees the court through the same homography), and a
  close-up shows no floor to verify.

Moving players are rejected as RANSAC outliers (they cover a small fraction of the frame), letterbox
bars and the frame border are masked, and every estimate is checked for plausibility (convex
footprint, bounded zoom and keystone, bounded jump from the previous frame) before it is used.
Frames that cannot be registered (close-ups, crowd shots, a different camera) get ``None`` — the
caller must treat the court as *not in view* there rather than fall back to a stale pose.
"""

from __future__ import annotations

import zlib
from collections.abc import Sequence
from dataclasses import dataclass, field

import cv2
import numpy as np
from numpy.typing import NDArray

Mat = NDArray[np.float64]
Frame = NDArray[np.uint8]
Gray = NDArray[np.uint8]

_LK = {"winSize": (21, 21), "maxLevel": 4, "criteria": (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 20, 0.03)}
_INF = 10**6
MIN_FLOOR_VISIBLE = 0.04  # fraction of the live frame the reference floor must cover to verify a pose
MIN_FLOOR_NCC = 0.2  # edge correlation (correct poses: 0.3-1.0, another camera's plane: ~0.03)
STATIC_FRAC = 0.03  # fraction of a 160x90 frame that may change before the camera counts as moving
MAX_FLOOR_SHIFT = 0.008  # residual floor misalignment, as a fraction of frame width (≈ 10 px at 1280)


def project(G: Mat, pts: NDArray[np.floating] | Sequence[Sequence[float]]) -> Mat:
    """Apply a 3×3 homography to ``(N, 2)`` points."""
    p = np.asarray(pts, dtype=np.float64).reshape(-1, 1, 2)
    return np.asarray(cv2.perspectiveTransform(p, G), dtype=np.float64).reshape(-1, 2)


def _norm(G: Mat) -> Mat:
    return np.asarray(G / G[2, 2], dtype=np.float64)


def _edges(gray: Gray) -> NDArray[np.float32]:
    g = cv2.GaussianBlur(gray, (0, 0), 1.2).astype(np.float32)
    return np.hypot(cv2.Sobel(g, cv2.CV_32F, 1, 0), cv2.Sobel(g, cv2.CV_32F, 0, 1))


@dataclass
class _Key:
    """A stored view with a known pose: ``G`` maps reference px → this view's px (work resolution)."""

    gray: Gray
    valid: Gray  # 255 where features may be taken
    G: Mat
    xy: Mat  # SIFT keypoints (work px)
    des: NDArray[np.float32]
    used: int = 0  # last frame that aligned against it (for pruning)


@dataclass
class _Last:
    frame: int
    gray: Gray
    G: Mat  # work px
    since: int  # frames since the pose was last confirmed against an image
    check: int  # frames since the last SIFT check against the original reference
    state: str  # verdict of the last frame ("ok" / "blind")


@dataclass
class _State:
    keys: list[_Key] = field(default_factory=list)  # keys[0] is the calibration reference (G = I)
    size: tuple[int, int] = (0, 0)  # work (w, h)
    full: tuple[int, int] = (0, 0)  # full resolution (w, h)
    scale: float = 1.0  # work px per full px
    ref_id: int = 0
    floor: Gray | None = None  # work-res mask of the court plane in the reference (None: unverified)
    edges: NDArray[np.float32] | None = None  # edge strength of the reference


class CameraTracker:
    def __init__(
        self,
        work_width: int = 640,
        anchor_every: int = 30,
        max_unanchored: int = 45,
        max_hold: int = 6,
        max_keys: int = 16,
        min_coverage: float = 0.8,
        verify_every: int = 4,
        realign_every: int = 6,
    ) -> None:
        self.work_width = work_width
        self.anchor_every = anchor_every  # frames between SIFT checks against the original reference
        self.max_unanchored = max_unanchored  # chained frames allowed without an image confirming the pose
        self.max_hold = max_hold  # frames a lost track is held at the last pose before giving up
        self.max_keys = max_keys
        self.min_coverage = min_coverage  # below this overlap with every keyframe, add a keyframe
        self.verify_every = verify_every  # frames between floor checks of a pose that was aligned to a verified one
        self.realign_every = realign_every  # frames a still camera is trusted before it is aligned again
        self._st: _State | None = None
        self._last: _Last | None = None
        self._rejected = False  # the current frame had a candidate pose that failed court verification
        self._sift = cv2.SIFT_create(nfeatures=1500)  # type: ignore[attr-defined]  # cv2 stubs
        self._bf = cv2.BFMatcher(cv2.NORM_L2)

    # ------------------------------------------------------------------ reference
    @property
    def ready(self) -> bool:
        return self._st is not None

    @property
    def ref_id(self) -> int | None:
        return self._st.ref_id if self._st else None

    def clear(self) -> None:
        self._st = self._last = None

    def set_reference(
        self, frame: Frame, floor: NDArray[np.floating] | Sequence[Sequence[float]] | None = None
    ) -> int | None:
        """Make ``frame`` the pose that ``G = I`` refers to.  ``floor`` is the court-plane region in
        ``frame`` (polygon, full-resolution px) that poses are verified against; without it poses
        are not verified.  Returns the reference's id (a content hash: cached perception made against
        another reference is recognisably stale), or ``None`` — and no tracking — when the frame has too
        little texture to register against."""
        gray, s = self._work(frame)
        valid = self._valid(gray)
        sift = cv2.SIFT_create(nfeatures=3000)  # type: ignore[attr-defined]  # cv2 stubs
        kp, des = sift.detectAndCompute(gray, valid)
        self._last = None
        if des is None or len(kp) < 60:
            self._st = None
            return None
        h, w = frame.shape[:2]
        ref_id = zlib.crc32(cv2.resize(gray, (64, 36), interpolation=cv2.INTER_AREA).tobytes())
        key = _Key(gray, valid, np.eye(3), np.array([k.pt for k in kp], dtype=np.float64), des)
        self._st = _State([key], (gray.shape[1], gray.shape[0]), (w, h), s, ref_id)
        if floor is not None:
            mask = np.zeros(gray.shape, np.uint8)
            cv2.fillPoly(mask, [np.round(np.asarray(floor, dtype=np.float64) * s).astype(np.int32)], 255)
            if mask.mean() / 255 >= 0.02:
                self._st.floor, self._st.edges = mask, _edges(gray)
        return ref_id

    # ------------------------------------------------------------------ per chunk
    def track(self, frames: Sequence[Frame], cuts: Sequence[bool], start: int) -> list[Mat | None]:
        """``G_t`` (reference px → frame px, full resolution) for each frame, ``None`` where the court
        is not verifiably in view.  ``cuts[i]`` marks a camera cut at frame ``i``.

        Each candidate pose gets a verdict: ``ok`` (the floor is visible and lines up), ``blind`` (too
        little floor in view to tell — the pose is still *tracked* so that it is there when the floor
        returns, but reported as no court) or ``bad`` (the floor is visible and does *not* line up: a
        different camera — the chain is dropped)."""
        n = len(frames)
        out: list[Mat | None] = [None] * n
        st = self._st
        if st is None or n == 0:
            return out
        grays = [self._work(f)[0] for f in frames]
        last = self._last
        if last is not None and (last.frame != start - 1 or cuts[0]):
            last = None  # out-of-order chunk (seek preview) or a cut at the seam: no chain
        poses: list[Mat | None] = [None] * n
        verdicts = ["bad"] * n
        prev_g: Gray | None = last.gray if last else None
        G_prev: Mat | None = last.G if last else None
        state_prev = last.state if last else "bad"
        since, check = (last.since, last.check) if last else (_INF, 0)
        hold, lost_for, since_key = 0, 0, _INF
        verify_age, still_age = _INF, _INF  # frames since the floor check / since the last alignment
        for i, gray in enumerate(grays):
            f = start + i
            if cuts[i]:
                prev_g, G_prev, since, hold, lost_for = None, None, _INF, 0, 0
                verify_age, still_age = _INF, _INF
            live: list[NDArray[np.float32]] = []  # this frame's edge map, computed on first use
            self._rejected = False

            def settle(
                cand: Mat | None,
                trusted: bool = False,
                gray: Gray = gray,
                live: list[NDArray[np.float32]] = live,
                state_prev: str = state_prev,
            ) -> tuple[Mat | None, str]:
                nonlocal verify_age
                if cand is None:
                    return None, "bad"
                if trusted and state_prev == "ok" and verify_age + 1 < self.verify_every:
                    verify_age += 1  # aligned to the previous (verified) pose: the floor check can wait
                    return cand, "ok"
                verify_age = 0
                v = self._judge(gray, live, cand)
                if v == "bad":
                    self._rejected = True
                    return None, v
                return cand, v

            G: Mat | None = None
            state = "bad"
            confirmed = False  # aligned against a stored image (not merely chained)
            if (
                G_prev is not None
                and prev_g is not None
                and state_prev == "ok"
                and still_age < self.realign_every
                and not cuts[i]
                and self._unchanged(prev_g, gray)
            ):
                G, state = G_prev, "ok"  # a locked-off camera: nothing to align (re-aligned every few frames)
                still_age += 1
                verify_age += 1
            elif G_prev is not None:
                still_age = 0
                G, state = settle(self._align(gray, G_prev, f), trusted=True)  # the pose barely moves per frame
                confirmed = G is not None
                if G is None and prev_g is not None:  # fast pan: chain from the previous frame first
                    g = self._step(prev_g, gray)
                    if g is not None and self._plausible(g @ G_prev):
                        chained = _norm(g @ G_prev)
                        G, state = settle(self._align(gray, chained, f))
                        confirmed = G is not None
                        if G is None and since < self.max_unanchored:
                            G, state = settle(chained)  # unconfirmed, but believable
                            since += 1
                if G is not None and self._disagreement(G, G_prev, gray.shape) > 0.12 * gray.shape[1]:
                    G, state, confirmed = None, "bad", False  # a jump no camera makes between two frames
            retry = 3 if lost_for < 30 else 10  # acquiring is dear: while lost, try every few frames
            if G is None and lost_for % retry == 0:
                a = self._anchor(gray, G_prev)
                if a is not None:
                    refined = self._align(gray, a, f)
                    G, state = settle(refined if refined is not None else a)
                    confirmed = G is not None
            lost_for = 0 if G is not None else lost_for + 1
            if G is not None and confirmed:
                since = 0
                if state == "ok":  # only a verified pose may seed keyframes or re-anchor the chain
                    check += 1
                    if check >= self.anchor_every:  # pull back to the original reference (limits keyframe drift)
                        check = 0
                        G = self._recheck(gray, G)
                    since_key += 1
                    if since_key >= 8 and self._coverage_best(G, gray.shape) < self.min_coverage:
                        self._add_key(gray, G, f)
                        since_key = 0
            held = G is None and G_prev is not None and hold < self.max_hold and not cuts[i] and not self._rejected
            if held:  # a blurred frame (tracking failed, nothing contradicts the pose): hold it briefly
                G, state, hold = G_prev, state_prev, hold + 1
            elif G is not None:
                hold = 0
            poses[i], verdicts[i] = G, state
            prev_g, G_prev, state_prev = gray, G, state
            if G is None:
                since = _INF
        # frames before the first registration (chunk starts mid-shot, out of order): chain backwards
        first = next((i for i, p in enumerate(poses) if p is not None), None)
        if first is not None:
            for i in range(first - 1, -1, -1):
                nxt = poses[i + 1]
                if cuts[i + 1] or poses[i] is not None or nxt is None:
                    break
                g = self._step(grays[i + 1], grays[i])
                if g is None or not self._plausible(g @ nxt):
                    break
                cand = _norm(g @ nxt)
                v = self._judge(grays[i], [], cand)
                if v == "bad":
                    break
                poses[i], verdicts[i] = cand, v
        S = np.diag([st.scale, st.scale, 1.0])
        Sinv = np.diag([1 / st.scale, 1 / st.scale, 1.0])
        for i, p in enumerate(poses):
            out[i] = _norm(Sinv @ p @ S) if p is not None and verdicts[i] == "ok" else None
        tail = poses[-1]
        self._last = _Last(start + n - 1, grays[-1], tail, since, check, verdicts[-1]) if tail is not None else None
        return out

    # ------------------------------------------------------------------ keyframes
    def _footprint(self, key: _Key, G: Mat) -> Mat:
        """Where ``key``'s frame lands in the live frame under pose ``G``."""
        assert self._st is not None
        w, h = self._st.size
        return project(G @ np.linalg.inv(key.G), [[0, 0], [w, 0], [w, h], [0, h]])

    def _coverage(self, key: _Key, G: Mat, shape: tuple[int, ...]) -> float:
        h, w = shape[:2]
        quad = self._footprint(key, G).astype(np.float32)
        if not np.isfinite(quad).all():
            return 0.0
        area, _ = cv2.intersectConvexConvex(quad, np.array([[0, 0], [w, 0], [w, h], [0, h]], np.float32))
        return float(area) / (w * h)

    def _coverage_best(self, G: Mat, shape: tuple[int, ...]) -> float:
        assert self._st is not None
        return max(self._coverage(k, G, shape) for k in self._st.keys)

    def _add_key(self, gray: Gray, G: Mat, frame: int) -> None:
        assert self._st is not None
        valid = self._valid(gray)
        kp, des = self._sift.detectAndCompute(gray, valid)
        if des is None or len(kp) < 40:
            return
        keys = self._st.keys
        keys.append(_Key(gray, valid, G.copy(), np.array([k.pt for k in kp], dtype=np.float64), des, frame))
        if len(keys) > self.max_keys:  # never drop the calibration reference
            keys.pop(min(range(1, len(keys)), key=lambda j: keys[j].used))

    # ------------------------------------------------------------------ alignment
    def _align(self, gray: Gray, G0: Mat, frame: int) -> Mat | None:
        """Refine the predicted pose ``G0`` against the best-overlapping stored views."""
        assert self._st is not None
        ranked = sorted(((self._coverage(k, G0, gray.shape), k) for k in self._st.keys), key=lambda t: -t[0])
        for cov, key in ranked[:2]:
            if cov < 0.15:
                break
            W = self._refine(gray, G0 @ np.linalg.inv(key.G), key)
            if W is None:
                continue
            G = _norm(W @ key.G)
            if self._plausible(G):
                key.used = frame
                return G
        return None

    def _refine(self, gray: Gray, W0: Mat, key: _Key) -> Mat | None:
        """Sharpen ``W0`` (key view → live frame) by tracking corners from the warped key view to the
        live frame; each iteration composes the residual homography.  ``None`` when too little of the
        key view is visible or matches (a different shot, a close-up, heavy blur)."""
        h, w = gray.shape
        W = W0
        live = self._valid(gray)
        for it in range(2):
            # The key view is magnified by ``zoom`` on its way to the live frame: its detail is as
            # blurred as that magnification (zoom in) or aliased (zoom out), and LK fails across a
            # sharpness mismatch — so bring the two to the same blur before tracking.
            zoom = float(np.sqrt(abs(np.linalg.det(W[:2, :2] - np.outer(W[:2, 2], W[2, :2])))))
            src = key.gray if zoom >= 1 else cv2.GaussianBlur(key.gray, (0, 0), 0.6 * np.sqrt(1 / zoom**2 - 1))
            warped = np.asarray(cv2.warpPerspective(src, W, (w, h), flags=cv2.INTER_LINEAR), dtype=np.uint8)
            cur: Gray = gray
            if zoom > 1:
                cur = np.asarray(cv2.GaussianBlur(gray, (0, 0), 0.6 * np.sqrt(zoom**2 - 1)), dtype=np.uint8)
            # Outside the key view's footprint the warp is black while the live frame has content; LK's
            # coarse pyramid levels see that mismatch and fail half the tracks.  Fill it with the live
            # frame itself so the two images agree there (and no corners are taken there: ``seen``).
            inside = cv2.warpPerspective(np.full_like(key.gray, 255), W, (w, h), flags=cv2.INTER_NEAREST)
            warped = np.where(inside > 0, warped, cur)
            seen = cv2.warpPerspective(key.valid, W, (w, h), flags=cv2.INTER_NEAREST)
            seen = cv2.erode(seen, np.ones((9, 9), np.uint8))
            mask = np.asarray(cv2.bitwise_and(seen, live), dtype=np.uint8)
            d = self._step(warped, cur, mask, min_inliers=25, min_ratio=0.45, min_spread=0.12)
            if d is None:
                return None if it == 0 else _norm(W)
            W = _norm(d @ W)
            if self._disagreement(d, np.eye(3), gray.shape) < 0.05:
                break
        return W

    def _recheck(self, gray: Gray, G: Mat) -> Mat:
        """SIFT-register against the *original* reference and adopt it when the keyframe chain drifted."""
        assert self._st is not None
        ref = self._st.keys[0]
        if self._coverage(ref, G, gray.shape) < 0.25:
            return G
        a = self._match_key(gray, ref, G)
        if a is None:
            return G
        W = self._refine(gray, a[0], ref)
        if W is None:
            return G
        G2 = _norm(W)
        return G2 if self._plausible(G2) and self._disagreement(G2, G, gray.shape) > 1.5 else G

    # ------------------------------------------------------------------ court-plane verification
    def floor_check(
        self, gray: Gray, G: Mat, live_edges: NDArray[np.float32] | None = None
    ) -> tuple[float, float] | None:
        """How well the reference floor, warped by ``G`` (work px), lines up with the live frame:
        ``(edge correlation, residual shift in px)`` — ``None`` when too little of the floor is in view
        to tell (or there is no floor to verify).  The shift is the phase-correlation peak between the
        two edge maps over the floor: a pose that merely fits another plane (the boards, the crowd)
        leaves the floor displaced, one that fits the floor leaves almost nothing."""
        st = self._st
        if st is None or st.floor is None or st.edges is None:
            return None
        h, w = gray.shape
        floor = cv2.warpPerspective(st.floor, G, (w, h), flags=cv2.INTER_NEAREST)
        wm = (cv2.erode(floor, np.ones((7, 7), np.uint8)) > 0) & (self._valid(gray) > 0)
        if float(wm.mean()) < MIN_FLOOR_VISIBLE:
            return None
        le = _edges(gray) if live_edges is None else live_edges
        we = cv2.warpPerspective(st.edges, G, (w, h))
        a, b = we[wm], le[wm]
        if a.std() < 1e-3 or b.std() < 1e-3:
            return None
        ncc = float(np.corrcoef(a, b)[0, 1])
        win = cv2.createHanningWindow((w, h), cv2.CV_32F)
        masked_ref, masked_live = (np.where(wm, im, 0).astype(np.float32) for im in (we, le))
        (dx, dy), _ = cv2.phaseCorrelate(masked_ref, masked_live, win)
        return ncc, float(np.hypot(dx, dy))

    def _judge(self, gray: Gray, live: list[NDArray[np.float32]], G: Mat) -> str:
        """``ok`` / ``blind`` / ``bad`` for pose ``G`` (always ``ok`` when there is no floor to check)."""
        st = self._st
        if st is None or st.floor is None:
            return "ok"
        if not live:
            live.append(_edges(gray))
        chk = self.floor_check(gray, G, live[0])
        if chk is None:
            return "blind"
        ncc, shift = chk
        return "ok" if ncc >= MIN_FLOOR_NCC and shift <= MAX_FLOOR_SHIFT * gray.shape[1] else "bad"

    # ------------------------------------------------------------------ low level
    def _work(self, frame: Frame) -> tuple[Gray, float]:
        h, w = frame.shape[:2]
        s = min(1.0, self.work_width / w)
        small = cv2.resize(frame, (round(w * s), round(h * s)), interpolation=cv2.INTER_AREA) if s < 1 else frame
        return np.asarray(cv2.cvtColor(small, cv2.COLOR_BGR2GRAY), dtype=np.uint8), s

    @staticmethod
    def _unchanged(a: Gray, b: Gray) -> bool:
        """The two frames are all but identical (a locked-off camera; players cover a small part of it)."""
        sa, sb = (cv2.resize(x, (160, 90), interpolation=cv2.INTER_AREA) for x in (a, b))
        return float((cv2.absdiff(sa, sb) > 10).mean()) < STATIC_FRAC

    @staticmethod
    def _valid(gray: Gray) -> Gray:
        """Where features may be taken: not letterbox bars, not the (often cropped / graphic-laden) border."""
        h, w = gray.shape
        m = cv2.erode((gray > 12).astype(np.uint8), np.ones((15, 15), np.uint8))
        b = max(4, int(0.03 * min(h, w)))
        m[:b], m[-b:], m[:, :b], m[:, -b:] = 0, 0, 0, 0
        return (m * 255).astype(np.uint8)

    def _step(
        self,
        prev: Gray,
        cur: Gray,
        mask: Gray | None = None,
        min_inliers: int = 15,
        min_ratio: float = 0.3,
        min_spread: float = 0.0,
    ) -> Mat | None:
        """Homography prev → cur from tracked corners (``None`` when unreliable)."""
        pts = cv2.goodFeaturesToTrack(prev, 500, 0.01, 8, mask=self._valid(prev) if mask is None else mask, blockSize=7)
        if pts is None or len(pts) < 25:
            return None
        nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, pts, None, **_LK)  # type: ignore[call-overload]  # cv2 stubs
        back, st2, _ = cv2.calcOpticalFlowPyrLK(cur, prev, nxt, None, **_LK)  # type: ignore[call-overload]
        fb = np.linalg.norm((back - pts).reshape(-1, 2), axis=1)
        ok = (st.ravel() == 1) & (st2.ravel() == 1) & (fb < 1.0)
        if int(ok.sum()) < min(20, min_inliers):
            return None
        g, inl = cv2.findHomography(pts[ok], nxt[ok], cv2.RANSAC, 2.0, maxIters=500, confidence=0.995)
        if g is None or inl is None:
            return None
        keep = inl.ravel().astype(bool)
        if int(keep.sum()) < min_inliers or float(keep.mean()) < min_ratio:
            return None
        if min_spread > 0:  # inliers clustered in a strip cannot pin down an 8-DOF homography
            p = pts[ok].reshape(-1, 2)[keep]
            ext = (p.max(axis=0) - p.min(axis=0)) / np.array([cur.shape[1], cur.shape[0]])
            if float(ext[0] * ext[1]) < min_spread:
                return None
        return np.asarray(g, dtype=np.float64)

    def _anchor(self, gray: Gray, guess: Mat | None) -> Mat | None:
        """Register ``gray`` against the stored views from scratch (or guided by ``guess``)."""
        assert self._st is not None
        kp, des = self._sift.detectAndCompute(gray, self._valid(gray))
        if des is None or len(kp) < 25:
            return None
        xy = np.array([k.pt for k in kp], dtype=np.float64)
        keys = self._st.keys
        pool = [keys[0], *sorted(keys[1:], key=lambda k: -k.used)[:3]]  # the reference + the freshest views
        best: tuple[Mat, int] | None = None
        for key in pool:
            guess_k = guess @ np.linalg.inv(key.G) if guess is not None else None
            r = self._match(xy, des, key, guess_k)
            if r is not None and (best is None or r[1] > best[1]):
                best = (_norm(r[0] @ key.G), r[1])
        return best[0] if best is not None and self._plausible(best[0]) else None

    def _match_key(self, gray: Gray, key: _Key, guess: Mat | None) -> tuple[Mat, int] | None:
        kp, des = self._sift.detectAndCompute(gray, self._valid(gray))
        if des is None or len(kp) < 25:
            return None
        xy = np.array([k.pt for k in kp], dtype=np.float64)
        r = self._match(xy, des, key, guess @ np.linalg.inv(key.G) if guess is not None else None)
        return None if r is None else (_norm(r[0] @ key.G), r[1])

    def _match(self, xy: Mat, des: NDArray[np.float32], key: _Key, guess_k: Mat | None) -> tuple[Mat, int] | None:
        """Homography key view → live frame from SIFT matches (``guess_k`` prunes implausible matches)."""
        pairs = self._bf.knnMatch(des, key.des, k=2)
        good = [m[0] for m in pairs if len(m) == 2 and m[0].distance < 0.75 * m[1].distance]
        if guess_k is not None and good:
            q = np.array([m.queryIdx for m in good])
            t = np.array([m.trainIdx for m in good])
            near = np.linalg.norm(project(guess_k, key.xy[t]) - xy[q], axis=1) < 60.0
            good = [m for m, k in zip(good, near, strict=True) if k]
        need = 12 if guess_k is not None else 18
        if len(good) < need:
            return None
        src = key.xy[[m.trainIdx for m in good]]
        dst = xy[[m.queryIdx for m in good]]
        W, inl = cv2.findHomography(src, dst, cv2.RANSAC, 3.0, maxIters=2000, confidence=0.995)
        if W is None or inl is None:
            return None  # type: ignore[unreachable]  # cv2 stubs: findHomography is typed non-optional
        mask = inl.ravel().astype(bool)
        n = int(mask.sum())
        if n < need or n / len(good) < 0.3:
            return None
        W2, _ = cv2.findHomography(src[mask], dst[mask], 0)  # least-squares polish on the inliers
        return _norm(np.asarray(W2 if W2 is not None else W, dtype=np.float64)), n

    def _plausible(self, G: Mat) -> bool:
        """A believable camera pose: finite, convex footprint, bounded zoom, mild keystone."""
        assert self._st is not None
        if not np.isfinite(G).all() or abs(G[2, 2]) < 1e-12:
            return False
        G = _norm(G)
        w, h = self._st.size
        q = project(G, [[0, 0], [w, 0], [w, h], [0, h]])
        if not np.isfinite(q).all():
            return False
        cross = [
            (q[(k + 1) % 4, 0] - q[k, 0]) * (q[(k + 2) % 4, 1] - q[(k + 1) % 4, 1])
            - (q[(k + 1) % 4, 1] - q[k, 1]) * (q[(k + 2) % 4, 0] - q[(k + 1) % 4, 0])
            for k in range(4)
        ]
        if not (all(c > 0 for c in cross) or all(c < 0 for c in cross)):
            return False  # self-intersecting / folded footprint
        area = 0.5 * abs(np.dot(q[:, 0], np.roll(q[:, 1], -1)) - np.dot(q[:, 1], np.roll(q[:, 0], -1)))
        return bool(0.06 <= area / (w * h) <= 16.0 and abs(G[2, 0]) * w < 0.35 and abs(G[2, 1]) * h < 0.35)

    @staticmethod
    def _disagreement(A: Mat, B: Mat, shape: tuple[int, ...]) -> float:
        """Mean px distance between two poses over a grid of the frame."""
        h, w = shape[:2]
        gx, gy = np.meshgrid(np.linspace(0.1 * w, 0.9 * w, 4), np.linspace(0.1 * h, 0.9 * h, 3))
        pts = np.stack([gx.ravel(), gy.ravel()], axis=1)
        return float(np.linalg.norm(project(A, pts) - project(B, pts), axis=1).mean())
