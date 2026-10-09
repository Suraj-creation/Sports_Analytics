"""Synthetic broadcast-view rallies with exact ground truth.

Used by unit tests, the golden pipeline test and the CPU development profile (a synthetic
"video" exercises the whole engine without model weights).  Geometry: a 1280×720 behind-the-
baseline broadcast view built from a real-looking homography; players are boxes with plausible
COCO-17 skeletons; the shuttle follows parabolic image arcs between the players' hands.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from bai_badminton.court import HALF_LEN, Homography, fit_homography
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.keypoints import KP
from bai_badminton.perception.shuttle_post import Track
from bai_badminton.perception_types import ChunkPerception, FramePerception, PersonObs

W, H = 1280, 720


def broadcast_homography() -> Homography:
    """Exact 4-corner fit of a typical behind-the-baseline broadcast view (1280×720)."""
    return fit_homography(
        {
            "far_left": (470.0, 205.0),
            "far_right": (810.0, 205.0),
            "near_right": (1010.0, 655.0),
            "near_left": (270.0, 655.0),
        }
    )


@dataclass
class SynthShot:
    hitter: str  # P1 near / P2 far
    frame: int  # contact frame
    target_court: tuple[float, float]  # where the receiver is / shuttle lands (m)
    duration: int  # frames until next contact / landing


@dataclass
class SynthRally:
    obs: WindowObs
    contacts: list[tuple[int, str]]  # (frame, player) ground truth
    landing_frame: int
    landing_court: tuple[float, float]
    start_frame: int
    end_frame: int
    homography: Homography
    meta: dict[str, object] = field(default_factory=dict)


def _skeleton(feet: np.ndarray, h: float, hand: np.ndarray | None, raise_left: bool = False) -> np.ndarray:
    """Upright COCO-17 skeleton of height ``h`` standing at ``feet``; optional hand target."""
    x, y = feet
    k = np.zeros((17, 3))
    k[:, 2] = 0.9
    top = y - h
    k[KP.NOSE] = (x, top + 0.07 * h, 0.9)
    k[KP.L_EYE] = (x - 0.03 * h, top + 0.05 * h, 0.9)
    k[KP.R_EYE] = (x + 0.03 * h, top + 0.05 * h, 0.9)
    k[KP.L_EAR] = (x - 0.06 * h, top + 0.06 * h, 0.9)
    k[KP.R_EAR] = (x + 0.06 * h, top + 0.06 * h, 0.9)
    k[KP.L_SHOULDER] = (x - 0.12 * h, top + 0.2 * h, 0.9)
    k[KP.R_SHOULDER] = (x + 0.12 * h, top + 0.2 * h, 0.9)
    k[KP.L_ELBOW] = (x - 0.16 * h, top + 0.35 * h, 0.9)
    k[KP.R_ELBOW] = (x + 0.16 * h, top + 0.35 * h, 0.9)
    k[KP.L_WRIST] = (x - 0.18 * h, top + 0.48 * h, 0.9)
    k[KP.R_WRIST] = (x + 0.18 * h, top + 0.48 * h, 0.9)
    k[KP.L_HIP] = (x - 0.08 * h, top + 0.52 * h, 0.9)
    k[KP.R_HIP] = (x + 0.08 * h, top + 0.52 * h, 0.9)
    k[KP.L_KNEE] = (x - 0.08 * h, top + 0.75 * h, 0.9)
    k[KP.R_KNEE] = (x + 0.08 * h, top + 0.75 * h, 0.9)
    k[KP.L_ANKLE] = (x - 0.08 * h, y, 0.9)
    k[KP.R_ANKLE] = (x + 0.08 * h, y, 0.9)
    if hand is not None:
        wr = KP.L_WRIST if raise_left else KP.R_WRIST
        el = KP.L_ELBOW if raise_left else KP.R_ELBOW
        sh = k[KP.L_SHOULDER if raise_left else KP.R_SHOULDER, :2]
        k[wr, :2] = hand
        k[el, :2] = (sh + hand) / 2
    return k


def make_rally(
    n_shots: int = 6,
    fps: float = 30.0,
    lead_in: int = 30,
    tail: int = 45,
    land_court: tuple[float, float] = (1.0, -4.0),
    shot_frames: int = 24,
    jump_at_shot: int | None = None,
    noise_px: float = 0.0,
    seed: int = 0,
) -> SynthRally:
    rng = np.random.default_rng(seed)
    hom = broadcast_homography()
    near_court = np.array([0.3, -HALF_LEN + 1.8])
    far_court = np.array([-0.2, HALF_LEN - 1.8])
    total = lead_in + n_shots * shot_frames + tail
    sx = np.full(total, np.nan)
    sy = np.full(total, np.nan)
    vis = np.zeros(total, bool)

    players = {"P1": PlayerSeries.empty(total), "P2": PlayerSeries.empty(total)}
    feet_img = {
        "P1": hom.court_to_image(near_court[None])[0],
        "P2": hom.court_to_image(far_court[None])[0],
    }
    heights = {"P1": 230.0, "P2": 115.0}

    def hand_point(pid: str) -> np.ndarray:
        f = feet_img[pid]
        return np.array([f[0] + 0.18 * heights[pid], f[1] - 1.05 * heights[pid]])

    contacts: list[tuple[int, str]] = []
    frame = lead_in
    hitter = "P1"
    for s in range(n_shots):
        a = hand_point(hitter)
        last = s == n_shots - 1
        if last:
            b = hom.court_to_image(np.array([land_court]))[0]
        else:
            b = hand_point("P2" if hitter == "P1" else "P1")
        contacts.append((frame, hitter))
        for t in range(shot_frames + 1):
            u = t / shot_frames
            px = a[0] + (b[0] - a[0]) * u
            arc = 160.0 if hitter == "P1" else 120.0
            py = a[1] + (b[1] - a[1]) * u - arc * 4 * u * (1 - u)
            i = frame + t
            if i < total:
                sx[i], sy[i], vis[i] = px, py, True
        frame += shot_frames
        hitter = "P2" if hitter == "P1" else "P1"
    landing_frame = frame
    land_img = hom.court_to_image(np.array([land_court]))[0]
    for i in range(landing_frame, min(total, landing_frame + 12)):  # resting on the floor briefly
        sx[i], sy[i], vis[i] = land_img[0], land_img[1], True

    if noise_px:
        sx[vis] += rng.normal(0, noise_px, vis.sum())
        sy[vis] += rng.normal(0, noise_px, vis.sum())

    contact_frames = {f: p for f, p in contacts}
    for pid in ("P1", "P2"):
        s = players[pid]
        f = feet_img[pid]
        h = heights[pid]
        for i in range(total):
            lift = 0.0
            if jump_at_shot is not None and pid == contacts[jump_at_shot][1]:
                cf = contacts[jump_at_shot][0]
                if abs(i - cf) <= 6:
                    lift = 0.22 * h * (1 - abs(i - cf) / 7)
            feet = np.array([f[0], f[1] - lift])
            s.bbox[i] = (feet[0] - 0.3 * h, feet[1] - h, feet[0] + 0.3 * h, feet[1])
            near_contact = any(abs(i - cf) <= 2 and p == pid for cf, p in contact_frames.items())
            hand = np.array([sx[i], sy[i]]) if near_contact and vis[i] else None
            s.kps[i] = _skeleton(feet, h, hand)
            s.court_xy[i] = near_court if pid == "P1" else far_court

    obs = WindowObs(
        frame0=0, fps=fps, shuttle=Track.from_arrays(sx, sy, vis, np.where(vis, 0.95, 0.0)), players=players
    )
    return SynthRally(
        obs=obs,
        contacts=contacts,
        landing_frame=landing_frame,
        landing_court=land_court,
        start_frame=contacts[0][0],
        end_frame=landing_frame,
        homography=hom,
    )


@dataclass
class SynthMatch:
    chunks: list[ChunkPerception]
    rallies: list[SynthRally]
    offsets: list[int]
    winners: list[str]
    homography: Homography
    n_frames: int
    fps: float


def to_frames(r: SynthRally, offset: int) -> list[FramePerception]:
    out: list[FramePerception] = []
    t = r.obs.shuttle
    for i in range(r.obs.n):
        persons = []
        for tid, pid in ((1, "P1"), (2, "P2")):
            s = r.obs.players[pid]
            if np.isfinite(s.bbox[i, 0]):
                persons.append(PersonObs(track_id=tid, bbox=s.bbox[i].copy(), conf=0.9, kps=s.kps[i].copy()))
        xy = (float(t.x[i]), float(t.y[i])) if t.vis[i] else None
        out.append(
            FramePerception(frame_idx=offset + i, shuttle_xy=xy, shuttle_conf=0.95 if xy else 0.0, persons=persons)
        )
    return out


def make_match(winners: list[str], fps: float = 30.0, chunk: int = 64, seed: int = 0) -> SynthMatch:
    """A sequence of rallies (all in game 1, P1 near) whose geometric outcome yields ``winners``."""
    frames: list[FramePerception] = []
    rallies: list[SynthRally] = []
    offsets: list[int] = []
    rng = np.random.default_rng(seed)
    for k, w in enumerate(winners):
        # winner P1 → far player (P2) fails: last shot by P1 (odd shot count) lands in the far half
        n_shots = int(rng.integers(2, 5)) * 2 + (1 if w == "P1" else 0)
        land = (float(rng.uniform(-1.5, 1.5)), 4.5 if w == "P1" else -4.5)
        r = make_rally(n_shots=n_shots, fps=fps, land_court=land, seed=seed + k)
        offsets.append(len(frames))
        frames.extend(to_frames(r, len(frames)))
        rallies.append(r)
    chunks = []
    for s in range(0, len(frames), chunk):
        part = frames[s : s + chunk]
        chunks.append(
            ChunkPerception(
                start=part[0].frame_idx, end=part[-1].frame_idx, frames=part, models={"synthetic": "synth@1"}
            )
        )
    return SynthMatch(chunks, rallies, offsets, winners, broadcast_homography(), len(frames), fps)
