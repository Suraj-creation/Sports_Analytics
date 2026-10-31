"""Measured paths and pair positions for explicitly reviewed track intervals.

No interpolation across reviews, episodes or missing frames. Camera quality,
official-rally membership and the existing court_path_v2 gates remain mandatory.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any

import numpy as np

from bai_badminton.analytics.match import MatchAnalytics
from bai_badminton.analytics.rebuild import _camera_validity, rally_records
from bai_badminton.analytics.spatial import court_point_valid
from bai_badminton.identity_review import IdentityReviewLedger
from bai_engine.schema import TrackObject
from bai_engine.schema.session import ParticipantRoster
from bai_engine.store import EventStore, TrackStore


def reviewed_motion(
    store: EventStore, tracks: TrackStore, roster: ParticipantRoster, max_frame: int, fps: float
) -> dict[str, Any]:
    people = {person.participant_id for person in roster.participants}
    reviews = IdentityReviewLedger(store, people, max_frame=max_frame, fps=fps).current()
    analytics = MatchAnalytics(fps)
    official_ids = {
        event.event_id for event in store.query(types=["rally_end"]) if event.payload.get("official") is True
    }
    records = [record for record in rally_records(store) if record.rally_id in official_ids]
    camera = _camera_validity(tracks, 0, max((record.end for record in records), default=0))
    positions: dict[int, dict[str, tuple[float, float]]] = defaultdict(dict)
    observed: dict[str, set[int]] = defaultdict(set)
    for record in records:
        rows = tracks.read([TrackObject.PLAYER], record.start, record.end).to_pylist()
        groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
        matches = []
        for row in rows:
            matching = [
                review
                for review in reviews
                if review.frame_start <= row["frame_idx"] <= review.frame_end
                and review.actors.track_id == row["track_id"]
                and row["participant_observation_id"] == review.payload.get("observation_id")
            ]
            if len(matching) == 1:
                review = matching[0]
                matches.append((review, row))
        counts = Counter((review.actors.player_id, row["frame_idx"]) for review, row in matches)
        for review, row in matches:
            person = review.actors.player_id
            frame = row["frame_idx"]
            valid = bool(
                counts[person, frame] == 1
                and camera.get(frame, False)
                and row["visible"]
                and row["conf"] is not None
                and np.isfinite(row["conf"])
                and row["conf"] >= 0.5
                and row["court_x"] is not None
                and row["court_y"] is not None
                and court_point_valid(row["court_x"], row["court_y"])
            )
            groups[person, review.event_id].append({**row, "eligible": valid})
            if valid:
                positions[frame][person] = (row["court_x"], row["court_y"])
                observed[person].add(frame)
        for (person, _), group in groups.items():
            group.sort(key=lambda row: row["frame_idx"])
            analytics.on_presence(
                person,
                [(row["court_x"], row["court_y"]) for row in group],
                frames=[row["frame_idx"] for row in group],
                track_ids=[row["track_id"] for row in group],
                valid=[row["eligible"] for row in group],
            )
    expected = sum(record.end - record.start + 1 for record in records)
    movement = {}
    for person in people:
        stats = analytics.players[person]
        stats.distance_expected = expected
        public = stats.to_public()
        movement[person] = {key: public[key] for key in ("distance_m", "travel")}
        movement[person]["observed_frames"] = len(observed[person])
        movement[person]["expected_frames"] = expected
    pairs = {}
    for team in roster.teams:
        members = sorted(person.participant_id for person in roster.participants if person.team_id == team.team_id)
        front = Counter()
        rear = Counter()
        frames, front_back, side_by_side = 0, 0, 0
        if len(members) == 2:
            for point in positions.values():
                if not all(member in point for member in members):
                    continue
                left, right = (point[member] for member in members)
                if left[1] * right[1] <= 0:
                    continue
                frames += 1
                difference = abs(left[1]) - abs(right[1])
                if abs(difference) >= 0.5:
                    front_back += 1
                    near, far = (members[0], members[1]) if difference < 0 else (members[1], members[0])
                    front[near] += 1
                    rear[far] += 1
                else:
                    side_by_side += 1
        pairs[team.team_id] = {
            "members": members,
            "observed_frames": frames,
            "front_back_frames": front_back,
            "side_by_side_frames": side_by_side,
            "front_seconds": {member: round(front[member] / fps, 3) for member in members},
            "rear_seconds": {member: round(rear[member] / fps, 3) for member in members},
            "meaning": "reviewed court positions; not tactical responsibility or body orientation",
        }
    return {"movement": movement, "pairs": pairs}
