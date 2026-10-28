"""Conservative, uncalibrated episode-based *estimates*, not identity assertions.

A reviewed track seed is propagated briefly only where stored tracker samples
show bounded continuity. A tracker can still swap identities without recording a
boundary; every result remains a model estimate and is never added to reviewed
totals. No inference is made from court side or a roster's ordering.
"""

from __future__ import annotations

import re
from bisect import bisect_left, bisect_right
from collections import Counter
from functools import lru_cache
from itertools import pairwise
from math import hypot, isfinite
from typing import Any

from bai_badminton.analytics.individual import build_individual_analytics
from bai_badminton.analytics.rebuild import lineage_ids, rally_records
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import EventStatus, TrackObject
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore, TrackStore

MAX_SEED_AGE_SECONDS = 10
MAX_TRACK_SAMPLE_GAP_FRAMES = 6
MIN_TRACK_CONFIDENCE = 0.5
MAX_HEIGHT_RATIO = 2.0
MIN_DISPLACEMENT_LIMIT = 0.5
MAX_DISPLACEMENT_PER_GAP_FRAME = 0.25
MAX_COMPETING_BOX_IOU = 0.3


def _continuous(
    rows: list[dict[str, Any]],
    observation_id: str,
    track_id: int,
    start: int,
    end: int,
    frame_width: int,
    frame_height: int,
    *,
    require_detector_runs: bool = True,
    reject_competing_overlap: bool = True,
) -> bool:
    """Require bounded track continuity; detector runs are frame-level, not person matches."""
    competitors: dict[int, list[dict[str, Any]]] = {}
    if reject_competing_overlap:
        for row in rows:
            if row["track_id"] != track_id and start <= row["frame_idx"] <= end:
                competitors.setdefault(row["frame_idx"], []).append(row)
    rows = [row for row in rows if row["track_id"] == track_id and start <= row["frame_idx"] <= end]
    counts = Counter(row["frame_idx"] for row in rows)
    if not rows or any(count != 1 for count in counts.values()):
        return False
    rows.sort(key=lambda row: row["frame_idx"])
    frames = [row["frame_idx"] for row in rows]
    if frames[0] != start or frames[-1] != end or any(b - a > MAX_TRACK_SAMPLE_GAP_FRAMES for a, b in pairwise(frames)):
        return False
    for row in rows:
        box, conf = row["bbox"], row["conf"]
        if not (
            row["visible"] is True
            and row.get("participant_observation_id") == observation_id
            and isinstance(conf, (float, int))
            and isfinite(conf)
            and MIN_TRACK_CONFIDENCE <= conf <= 1
            and box is not None
            and len(box) == 4
            and all(isinstance(x, (int, float)) and not isinstance(x, bool) and isfinite(x) for x in box)
            and 0 <= box[0] < box[2] <= frame_width
            and 0 <= box[1] < box[3] <= frame_height
        ):
            return False
        for other in competitors.get(row["frame_idx"], []):
            b, score = other.get("bbox"), other.get("conf")
            if not (
                other.get("visible") is True
                and isinstance(score, (float, int))
                and not isinstance(score, bool)
                and isfinite(score)
                and MIN_TRACK_CONFIDENCE <= score <= 1
                and b is not None
                and len(b) == 4
                and all(isinstance(v, (int, float)) and not isinstance(v, bool) and isfinite(v) for v in b)
                and 0 <= b[0] < b[2] <= frame_width
                and 0 <= b[1] < b[3] <= frame_height
            ):
                continue
            intersection = max(0, min(box[2], b[2]) - max(box[0], b[0])) * max(0, min(box[3], b[3]) - max(box[1], b[1]))
            union = (box[2] - box[0]) * (box[3] - box[1]) + (b[2] - b[0]) * (b[3] - b[1]) - intersection
            # Overlap cannot prove an ID switch, but invalidates propagation of
            # a named seed through that ambiguous interval. It never merges IDs.
            if intersection / union >= MAX_COMPETING_BOX_IOU:
                return False
    if require_detector_runs:
        # None is legacy/unknown provenance; False means the detector explicitly did not run.
        flags = [row.get("detector_observed") for row in rows]
        if any(flag is not True and flag is not False for flag in flags):
            return False
        if flags[0] is not True or flags[-1] is not True:
            return False
        detector_frames = [row["frame_idx"] for row in rows if row["detector_observed"] is True]
        if any(b - a > MAX_TRACK_SAMPLE_GAP_FRAMES for a, b in pairwise(detector_frames)):
            return False
    for before, after in pairwise(rows):
        a, b = before["bbox"], after["bbox"]
        height_a, height_b = a[3] - a[1], b[3] - b[1]
        if max(height_a, height_b) / min(height_a, height_b) > MAX_HEIGHT_RATIO:
            return False
        delta = hypot((a[0] + a[2] - b[0] - b[2]) / 2, a[3] - b[3])
        limit = max(MIN_DISPLACEMENT_LIMIT, MAX_DISPLACEMENT_PER_GAP_FRAME * (after["frame_idx"] - before["frame_idx"]))
        if delta / ((height_a + height_b) / 2) > limit:
            return False
    return True


def build_estimated_individual_analytics(
    store: EventStore,
    tracks: TrackStore,
    roster: ParticipantRoster | None,
    *,
    max_frame: int,
    fps: float,
    frame_width: int,
    frame_height: int,
    include_events: bool = True,
) -> dict[str, Any]:
    """Read-only fold over official and explicitly separate preliminary rally scopes."""
    if not isfinite(float(fps)) or fps <= 0 or max_frame < 0 or frame_width <= 0 or frame_height <= 0:
        raise ValueError("a valid video timeline is required")
    people = {p.participant_id: p for p in roster.participants} if roster else {}
    # A short bounded cache reads all tracks in a ten-second window once, shared
    # across people and the official/all-linked scopes. LRU bounds memory use.
    bucket_size = max(1, int(float(fps) * MAX_SEED_AGE_SECONDS))

    @lru_cache(maxsize=16)
    def track_bucket(bucket: int) -> list[dict[str, Any]]:
        start = bucket * bucket_size
        end = min(max_frame, start + bucket_size - 1)
        return tracks.read([TrackObject.PLAYER], start, end).to_pylist()

    def track_interval(start: int, end: int) -> list[dict[str, Any]]:
        return [
            row
            for bucket in range(start // bucket_size, end // bucket_size + 1)
            for row in track_bucket(bucket)
            if start <= row["frame_idx"] <= end
        ]

    ledger = IdentityReviewLedger(store, people, max_frame=max_frame, fps=fps)
    observations = {e.event_id: e for e in store.query(types=["participant_observation"])}
    boundaries = sorted(
        store.query(types=["identity_ambiguity", "participant_observation"]), key=lambda e: e.frame_start
    )
    boundary_frames = [event.frame_start for event in boundaries]

    @lru_cache(maxsize=4096)
    def episode_error(observation_id: str, frame: int) -> str | None:
        obs = observations[observation_id]
        lo, hi = bisect_left(boundary_frames, obs.frame_start), bisect_right(boundary_frames, frame)
        return ledger._episode_error(obs, frame, boundary_events=boundaries[lo:hi])

    seeds = []
    for review in ledger.current(boundary_events=boundaries) if roster else []:
        obs = observations.get(review.payload.get("observation_id"))
        pid = review.actors.player_id
        track = review.actors.track_id
        episode = obs.payload.get("participant_id") if obs else None
        match = re.fullmatch(r"participant-([A-Za-z0-9]+)-[0-9]{6}", episode) if isinstance(episode, str) else None
        if (
            obs is not None
            and match is not None
            and review.payload.get("tracker_instance") == match.group(1)
            and obs.status == EventStatus.PROVISIONAL
            and obs.provenance.model == "participant_tracker_v1"
            and obs.payload.get("kind") in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
            and pid in people
            and isinstance(track, int)
            and not isinstance(track, bool)
            and track >= 0
            and obs.payload.get("track_id") == track
            and isinstance(obs.payload.get("participant_id"), str)
            and review.payload.get("participant_id") == obs.payload.get("participant_id")
            and obs.frame_start <= review.frame_start <= review.frame_end <= max_frame
        ):
            seeds.append((review, obs))
    strokes = {event.event_id: event for event in store.query(types=["stroke"])}
    verified = build_individual_analytics(store, roster, max_frame=max_frame, fps=fps, boundary_events=boundaries)
    verified_ids = {event_id for person in verified["participants"].values() for event_id in person["event_ids"]}
    all_linked: dict[str, str] = {}
    official: dict[str, str] = {}
    all_legacy = official_legacy = 0
    for rally in rally_records(store):
        rally_event = store.get(rally.rally_id)
        explicitly_official = rally_event is not None and rally_event.payload.get("official") is True
        for shot in rally.shots:
            event_id = shot.get("event_id")
            if not event_id:
                all_legacy += 1
                official_legacy += int(explicitly_official)
                continue
            all_linked.setdefault(event_id, rally.rally_id)
            if explicitly_official:
                official.setdefault(event_id, rally.rally_id)

    @lru_cache(maxsize=4096)
    def candidate(event_id: str) -> tuple[tuple[Any, dict[str, Any], Any, bool | None] | None, str | None]:
        event = strokes.get(event_id)
        h = event.payload.get("participant_hypothesis") if event else None
        if not event or not isinstance(h, dict) or h.get("status") != "provisional":
            return None, "no_unique_provisional_track_hypothesis"
        episode, track, frame = h.get("participant_id"), h.get("track_id"), event.frame_start
        if frame > max_frame:
            return None, "outside_video_timeline"
        if not isinstance(episode, str) or not isinstance(track, int) or isinstance(track, bool) or track < 0:
            return None, "no_unique_provisional_track_hypothesis"
        # A human correction may change a shot label, but may not synthesize or
        # replace the machine's participant evidence and call it a prediction.
        ancestry = lineage_ids(store, event)
        origin = store.get(ancestry[-1])
        if (
            origin is None
            or origin.supersedes is not None
            or origin.type != "stroke"
            or not origin.provenance.model
            or origin.provenance.model == "human"
            or origin.frame_start != frame
            or origin.payload.get("participant_hypothesis") != h
        ):
            return None, "changed_track_hypothesis"
        observation_id = h.get("observation_id")
        obs = observations.get(observation_id) if isinstance(observation_id, str) else None
        if (
            obs is None
            or obs.status != EventStatus.PROVISIONAL
            or obs.provenance.model != "participant_tracker_v1"
            or obs.payload.get("kind") not in ("PARTICIPANT_FIRST_OBSERVED", "PLAYER_ENTERED")
            or obs.frame_start > frame
            or obs.payload.get("participant_id") != episode
            or obs.payload.get("track_id") != track
        ):
            return None, "missing_matching_observation_provenance"
        if episode_error(obs.event_id, frame) is not None:
            return None, "episode_boundary"
        shot_rows = track_interval(frame, frame)
        if not _continuous(
            shot_rows,
            obs.event_id,
            track,
            frame,
            frame,
            frame_width,
            frame_height,
            require_detector_runs=False,
            reject_competing_overlap=False,
        ):
            return None, "shot_frame_track_unavailable"
        sample = next(row for row in shot_rows if row["track_id"] == track and row["frame_idx"] == frame)
        detector_run = sample.get("detector_observed")
        detector_run = detector_run if detector_run is True or detector_run is False else None
        return (event, h, obs, detector_run), None

    def estimate(event_id: str, rally_id: str) -> tuple[str | None, dict[str, Any] | str]:
        selected, reason = candidate(event_id)
        if selected is None:
            return None, str(reason)
        event, h, obs_for_shot, _detector_run = selected
        episode, track, frame = h["participant_id"], h["track_id"], event.frame_start
        observation_id = obs_for_shot.event_id
        relevant = [
            (r, obs)
            for r, obs in seeds
            if obs.event_id == observation_id
            and obs.payload.get("participant_id") == episode
            and obs.payload.get("track_id") == track
            and r.frame_start <= frame
        ]
        if not relevant:
            return None, "no_prior_reviewed_seed"
        if len({r.actors.player_id for r, _ in relevant}) != 1:
            return None, "conflicting_identity_seeds"
        seed, obs = max(relevant, key=lambda pair: (pair[0].frame_start, pair[0].seq or 0))
        person_id = seed.actors.player_id
        if frame - seed.frame_start > int(float(fps) * MAX_SEED_AGE_SECONDS):
            return None, "seed_expired"
        if episode_error(obs.event_id, frame) is not None:
            return None, "episode_boundary"
        # Other earlier seeds of the same person in concurrently live episodes are ambiguous.
        if any(
            other.actors.player_id == person_id
            and other_obs.event_id != obs.event_id
            and other.frame_start <= frame
            and episode_error(other_obs.event_id, frame) is None
            for other, other_obs in seeds
        ):
            return None, "person_has_conflicting_episode_seed"
        for boundary in boundaries:
            if not seed.frame_start <= boundary.frame_start <= frame:
                continue
            if boundary.frame_start == seed.frame_start and (
                boundary.seq is None or seed.seq is None or boundary.seq <= seed.seq
            ):
                continue
            if boundary.type == "identity_ambiguity":
                return None, "identity_ambiguity"
            kind = boundary.payload.get("kind")
            if kind in (
                "PLAYER_EXITED",
                "PLAYER_REIDENTIFICATION_UNCERTAIN",
                "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN",
            ) and (
                boundary.payload.get("participant_id") == episode
                or boundary.payload.get("related_participant_id") == episode
                or boundary.payload.get("track_id") == track
            ):
                return None, "identity_ambiguity"
        if not _continuous(
            track_interval(seed.frame_start, frame),
            obs.event_id,
            track,
            seed.frame_start,
            frame,
            frame_width,
            frame_height,
        ):
            return None, "track_continuity_unavailable"
        return person_id, {
            "event_id": event_id,
            "frame": frame,
            "stroke": str(event.payload.get("stroke") or "unknown"),
            "rally_id": rally_id,
            "track_id": track,
            "participant_id": episode,
            "seed_review_id": seed.event_id,
            "observation_id": obs.event_id,
            "status": "estimated",
            "detector_observed": True,
            "detector_observation_scope": "frame_only_not_person_match",
            "hypothesis_reason": h.get("reason"),
            "hypothesis_policy": h.get("policy"),
        }

    estimate_cache: dict[str, tuple[str | None, dict[str, Any] | str]] = {}

    def scope(refs: dict[str, str], legacy: int, *, official_only: bool) -> dict[str, Any]:
        result = {
            pid: {"name": p.name, "team_id": p.team_id, "estimated_shots": 0, "shot_distribution": {}, "events": []}
            for pid, p in people.items()
        }
        unresolved: dict[str, str] = {}
        verified_count = 0
        for event_id, rally_id in refs.items():
            if official_only and event_id in verified_ids:
                verified_count += 1
                continue
            if event_id not in estimate_cache:
                estimate_cache[event_id] = estimate(event_id, rally_id)
            person_id, evidence = estimate_cache[event_id]
            if person_id is None:
                unresolved[event_id] = str(evidence)
                continue
            person = result[person_id]
            person["estimated_shots"] += 1
            stroke = evidence["stroke"]
            person["shot_distribution"][stroke] = person["shot_distribution"].get(stroke, 0) + 1
            if include_events:
                person["events"].append({**evidence, "rally_id": rally_id})
        count = sum(person["estimated_shots"] for person in result.values())
        accounting = {"total_linked_shots": len(refs), "estimated_shots": count, "unresolved_shots": len(unresolved)}
        if official_only:
            accounting["verified_shots"] = verified_count
        return {
            "participants": result,
            "accounting": accounting,
            "unresolved_event_ids": list(unresolved) if include_events else [],
            "unresolved_reasons": unresolved if include_events else {},
            "legacy_unlinked_shots": legacy,
            "includes_official": True,
        }

    def episode_scope(refs: dict[str, str], legacy: int) -> dict[str, Any]:
        episodes: dict[tuple[str, str, int], dict[str, Any]] = {}
        unresolved: dict[str, str] = {}
        for event_id, rally_id in refs.items():
            selected, reason = candidate(event_id)
            if selected is None:
                unresolved[event_id] = str(reason)
                continue
            event, h, obs, detector_run = selected
            key = (obs.event_id, h["participant_id"], h["track_id"])
            episode = episodes.setdefault(
                key,
                {
                    "observation_id": obs.event_id,
                    "participant_id": h["participant_id"],
                    "track_id": h["track_id"],
                    "candidate_shots": 0,
                    "detector_run_counts": {"ran": 0, "not_run": 0, "unknown": 0},
                    "shot_distribution": {},
                    "events": [],
                    "status": "anonymous_track_episode",
                },
            )
            episode["candidate_shots"] += 1
            detector_status = "ran" if detector_run is True else "not_run" if detector_run is False else "unknown"
            episode["detector_run_counts"][detector_status] += 1
            shot = str(event.payload.get("stroke") or "unknown")
            episode["shot_distribution"][shot] = episode["shot_distribution"].get(shot, 0) + 1
            if include_events:
                episode["events"].append(
                    {
                        "event_id": event_id,
                        "frame": event.frame_start,
                        "stroke": shot,
                        "rally_id": rally_id,
                        "status": "anonymous_track_candidate",
                        "detector_observed": detector_run,
                        "detector_observation_scope": "frame_only_not_person_match",
                    }
                )
        return {
            "episodes": list(episodes.values()),
            "detector_run_counts": {
                key: sum(ep["detector_run_counts"][key] for ep in episodes.values())
                for key in ("ran", "not_run", "unknown")
            },
            "accounting": {
                "total_linked_shots": len(refs),
                "episode_candidate_shots": len(refs) - len(unresolved),
                "unresolved_shots": len(unresolved),
            },
            "unresolved_event_ids": list(unresolved) if include_events else [],
            "unresolved_reasons": unresolved if include_events else {},
            "legacy_unlinked_shots": legacy,
            "includes_official": True,
        }

    return {
        "available": roster is not None,
        "detail_included": include_events,
        "match_format": roster.match_format if roster else None,
        "official": scope(official, official_legacy, official_only=True),
        "all_linked": scope(all_linked, all_legacy, official_only=False),
        "episode_profiles": {
            "official": episode_scope(official, official_legacy),
            "all_linked": episode_scope(all_linked, all_legacy),
        },
        "unlinked_stroke_events": len(set(strokes) - set(all_linked)),
        "policy": {
            "kind": "uncalibrated_episode_estimate",
            "seed_max_seconds": MAX_SEED_AGE_SECONDS,
            "max_track_sample_gap_frames": MAX_TRACK_SAMPLE_GAP_FRAMES,
            "named_requires_detector_run_at_seed_and_shot": True,
            "max_detector_run_gap_frames": MAX_TRACK_SAMPLE_GAP_FRAMES,
            "detector_run_scope": "frame_only_not_person_match",
            "min_track_confidence": MIN_TRACK_CONFIDENCE,
            "max_box_height_ratio": MAX_HEIGHT_RATIO,
            "min_footpoint_jump_limit_body_heights": MIN_DISPLACEMENT_LIMIT,
            "max_footpoint_jump_per_frame_body_heights": MAX_DISPLACEMENT_PER_GAP_FRAME,
            "max_competing_box_iou": MAX_COMPETING_BOX_IOU,
            "overlap_policy": "abstain_named_propagation_preserve_anonymous_candidates",
            "warning": "A detector run is frame-level evidence, not proof that it matched this person. "
            "Estimates may be wrong if a tracker switches people without recording an ambiguity. "
            "All-linked counts include non-official rallies and are not match scores.",
        },
    }
