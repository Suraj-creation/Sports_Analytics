"""Conservative court-plane summaries for temporary anonymous track episodes.

Coordinates are sampled estimates, not complete player trajectories or named
identity. A valid camera row and episode provenance are required at every frame.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from contextlib import suppress
from math import isfinite
from typing import Any

import numpy as np

from bai_badminton.analytics.spatial import MIN_COURT_QUALITY, court_point_valid, movement
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import EventStatus, TrackObject
from bai_engine.store import EventStore, TrackStore

MAX_WINDOW_SECONDS = 120
MIN_TRACK_CONFIDENCE = 0.5


def build_episode_movement(
    store: EventStore,
    tracks: TrackStore,
    *,
    start_frame: int,
    end_frame: int,
    max_frame: int,
    fps: float,
    frame_width: int,
    frame_height: int,
) -> dict[str, Any]:
    """Summarize at most two minutes of anonymous, camera-qualified track data."""
    if (
        not all(
            isinstance(v, int) and not isinstance(v, bool)
            for v in (start_frame, end_frame, max_frame, frame_width, frame_height)
        )
        or not isinstance(fps, (float, int))
        or isinstance(fps, bool)
        or not isfinite(fps)
        or fps <= 0
        or frame_width <= 0
        or frame_height <= 0
        or not 0 <= start_frame <= end_frame <= max_frame
        or end_frame - start_frame + 1 > fps * MAX_WINDOW_SECONDS
    ):
        raise ValueError("invalid or overlong episode movement window")
    rows = tracks.read([TrackObject.PLAYER], start_frame, end_frame).to_pylist()
    camera_rows = tracks.read([TrackObject.CAMERA], start_frame, end_frame).to_pylist()
    camera_counts = Counter(row["frame_idx"] for row in camera_rows)
    camera = {}
    for row in camera_rows:
        transform, quality, frame = row.get("cam"), row.get("conf"), row["frame_idx"]
        valid_cam = False
        if (
            camera_counts[frame] == 1
            and row["visible"] is True
            and row["track_id"] == 0
            and isinstance(quality, (int, float))
            and not isinstance(quality, bool)
            and isfinite(quality)
            and MIN_COURT_QUALITY <= quality <= 1
            and transform is not None
            and len(transform) == 9
            and np.isfinite(transform).all()
        ):
            with suppress(np.linalg.LinAlgError):
                valid_cam = bool(np.linalg.cond(np.asarray(transform).reshape(3, 3)) < 1e12)
        camera[frame] = valid_cam
    boundaries = store.query(types=["identity_ambiguity", "participant_observation"])
    observations = {e.event_id: e for e in boundaries if e.type == "participant_observation"}
    ledger = IdentityReviewLedger(store, (), max_frame=max_frame, fps=fps)
    duplicate_tracks = Counter((row["frame_idx"], row["track_id"]) for row in rows)
    grouped: dict[tuple[str, int], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        obs_id, track = row.get("participant_observation_id"), row.get("track_id")
        if isinstance(obs_id, str) and isinstance(track, int) and not isinstance(track, bool) and track >= 0:
            grouped[obs_id, track].append(row)
    episodes = []
    for (obs_id, track), group in grouped.items():
        obs = observations.get(obs_id)
        if not (
            obs
            and obs.status == EventStatus.PROVISIONAL
            and obs.provenance.model == "participant_tracker_v1"
            and obs.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
            and obs.payload.get("track_id") == track
            and isinstance(obs.payload.get("participant_id"), str)
        ):
            continue
        # Episode validity is monotonic in time: once an exit, reset or reuse
        # appears, no later row can inherit the old birth event.
        first = max(start_frame, obs.frame_start)
        cutoff = end_frame + 1
        if first > end_frame:
            continue
        if ledger._episode_error(obs, first, boundary_events=boundaries) is not None:
            cutoff = first
        elif ledger._episode_error(obs, end_frame, boundary_events=boundaries) is not None:
            lo, hi = first + 1, end_frame
            while lo < hi:
                mid = (lo + hi) // 2
                if ledger._episode_error(obs, mid, boundary_events=boundaries) is None:
                    lo = mid + 1
                else:
                    hi = mid
            cutoff = lo
        # Other explicit uncertainty also ends this episode's usable path.
        episode_id = obs.payload["participant_id"]
        for boundary in boundaries:
            frame = boundary.frame_start
            if not obs.frame_start <= frame < cutoff:
                continue
            if (
                frame == obs.frame_start
                and boundary.seq is not None
                and obs.seq is not None
                and boundary.seq <= obs.seq
            ):
                continue
            if boundary.type == "identity_ambiguity" or (
                boundary.type == "participant_observation"
                and boundary.payload.get("kind")
                in ("PLAYER_REIDENTIFICATION_UNCERTAIN", "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN")
                and (
                    boundary.payload.get("participant_id") == episode_id
                    or boundary.payload.get("related_participant_id") == episode_id
                    or boundary.payload.get("track_id") == track
                )
            ):
                cutoff = frame
        group.sort(key=lambda row: row["frame_idx"])
        xs, frames, ids, valid = [], [], [], []
        for row in group:
            frame = row["frame_idx"]
            x, y, conf, box = row.get("court_x"), row.get("court_y"), row.get("conf"), row.get("bbox")
            coordinates = (
                isinstance(x, (float, int))
                and isinstance(y, (float, int))
                and not isinstance(x, bool)
                and not isinstance(y, bool)
                and court_point_valid(x, y)
            )
            rectangle = (
                box is not None
                and len(box) == 4
                and all(isinstance(v, (float, int)) and not isinstance(v, bool) and isfinite(v) for v in box)
                and 0 <= box[0] < box[2] <= frame_width
                and 0 <= box[1] < box[3] <= frame_height
            )
            ok = bool(
                obs.frame_start <= frame < cutoff
                and duplicate_tracks[frame, track] == 1
                and row["visible"] is True
                and isinstance(conf, (float, int))
                and not isinstance(conf, bool)
                and isfinite(conf)
                and MIN_TRACK_CONFIDENCE <= conf <= 1
                and camera.get(frame, False)
                and coordinates
                and rectangle
            )
            xs.append((float(x), float(y)) if coordinates else (np.nan, np.nan))
            frames.append(frame)
            ids.append(track)
            valid.append(ok)
        m = movement(np.asarray(xs), frames, ids, valid, float(fps))
        # The flag means the detector ran on that frame; it does not establish
        # that this particular track was matched to a fresh detection.
        source_counts = Counter(
            "detector" if row.get("detector_observed") is True
            else "carried" if row.get("detector_observed") is False
            else "unknown"
            for row, accepted in zip(group, valid, strict=True) if accepted
        )
        episodes.append(
            {
                "observation_id": obs_id,
                "participant_id": episode_id,
                "track_id": track,
                "status": "anonymous_track_episode",
                "distance_m": round(m.distance_m, 3) if m.segments else None,
                "valid_frames": m.accepted_samples,
                "detector_observed_frames": source_counts["detector"],
                "carried_frames": source_counts["carried"],
                "unknown_source_frames": source_counts["unknown"],
                "coverage_fraction": m.accepted_samples / (end_frame - start_frame + 1),
                "observed_seconds": round(m.observed_s, 3),
                "segments": m.segments,
                "positions_m": sorted([[round(float(x), 3), round(float(y), 3)] for x, y in m.xy]),
                "positions_semantics": "unordered_samples_do_not_connect",
            }
        )
    episodes.sort(key=lambda row: (row["observation_id"], row["track_id"]))
    available = any(episode["distance_m"] is not None for episode in episodes)
    return {
        "available": available,
        "reason": None if available else "no_valid_calibrated_movement_segments",
        "scope": "anonymous_track_episodes_not_people",
        "window": {"from": start_frame, "to": end_frame, "fps": float(fps)},
        "episodes": episodes,
        "warning": "Partial heuristic court-plane paths; tracking switches, "
        "calibration error and jitter can affect estimates. "
        "Coverage excludes unavailable frames and is not complete-match distance or named-player movement. "
        "Observed seconds refer to accepted tracker samples, which may include predictions.",
    }
