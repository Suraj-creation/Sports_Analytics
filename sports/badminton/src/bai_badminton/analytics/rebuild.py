"""Canonical analytics replay with correction lineage and spatial evidence gates."""

from __future__ import annotations

from collections import Counter
from typing import Any

import numpy as np

from bai_badminton.analytics.match import MatchAnalytics, RallyRecord
from bai_badminton.analytics.spatial import MIN_COURT_QUALITY, observed_player_row
from bai_badminton.rules import PLAYERS
from bai_engine.schema import Event, EventStatus, TrackObject
from bai_engine.store import EventStore, TrackStore


def lineage_ids(store: EventStore, ev: Event) -> list[str]:
    """Event and superseded ancestors, newest first, guarded against malformed cycles."""
    ids = [ev.event_id]
    cur: Event | None = ev
    while cur is not None and cur.supersedes and cur.supersedes not in ids:
        ids.append(cur.supersedes)
        cur = store.get(cur.supersedes)
    return ids


def _current_strokes(store: EventStore) -> dict[str, Event]:
    by_ancestor: dict[str, Event] = {}
    for event in store.query(types=["stroke"]):
        for ancestor in lineage_ids(store, event):
            by_ancestor[ancestor] = event
    return by_ancestor


def rally_records(store: EventStore) -> list[RallyRecord]:
    rallies = store.query(types=["rally_end"])
    points = {
        p.parent_id: p
        for p in store.query(types=["point"])
        if p.status in (EventStatus.CONFIRMED, EventStatus.CORRECTED, EventStatus.HUMAN_VERIFIED)
        and p.payload.get("winner") in PLAYERS
    }
    strokes = _current_strokes(store)
    out: list[RallyRecord] = []
    for r in rallies:
        p = next((points[i] for i in lineage_ids(store, r) if i in points), None)
        pay = r.payload
        if p is not None:
            after = p.payload["state_after"]
            before = p.payload["state_before"]
            if "game_end" in p.payload.get("transitions", []):
                g = after["completed_games"][-1]
                score_after = {"P1": g[0], "P2": g[1]}
            else:
                score_after = dict(after["score"])
            game_no, flags = int(before["game_no"]), dict(p.payload.get("flags_before", {}))
        else:
            score_after, game_no, flags = {"P1": 0, "P2": 0}, 1, {}
        shots: list[dict[str, Any]] = []
        seen: set[str] = set()
        for embedded in pay.get("shots", []):
            ident = embedded.get("event_id")
            if not ident:
                shots.append(dict(embedded))  # legacy records without canonical references
                continue
            stroke = strokes.get(ident)
            if stroke is None or stroke.event_id in seen:
                continue  # retracted, missing or duplicate reference
            seen.add(stroke.event_id)
            # Use the replacement payload wholesale: stale subtype/serve fields must disappear.
            shots.append(
                {
                    **stroke.payload,
                    "event_id": stroke.event_id,
                    "frame": stroke.frame_start,
                    "player_id": stroke.actors.player_id,
                }
            )
        shots.sort(key=lambda shot: shot.get("frame", r.frame_start))
        out.append(
            RallyRecord(
                rally_id=r.event_id,
                rally_no=int(pay.get("rally_no") or 0),
                start=r.frame_start,
                end=r.frame_end,
                winner=pay.get("winner"),
                loser=pay.get("loser"),
                outcome=str(pay.get("outcome", "unknown")),
                shots=shots,
                score_after=score_after,
                score_available=p is not None,
                game_no=game_no,
                flags_before=flags,
                duration_s=float(pay.get("duration_s", 0.0)),
                official=bool(pay.get("official", True)),
            )
        )
    return out


def _camera_validity(
    tracks: TrackStore, start: int, end: int, *, contexts: dict[int, str | None] | None = None,
    detector_runs: dict[int, bool | None] | None = None,
) -> dict[int, bool]:
    rows = tracks.read([TrackObject.CAMERA], start, end).to_pylist()
    counts = Counter(row["frame_idx"] for row in rows)
    if contexts is not None:
        contexts.update({
            row["frame_idx"]: row.get("context_id") if counts[row["frame_idx"]] == 1 else None
            for row in rows
        })
    if detector_runs is not None:
        detector_runs.update({
            row["frame_idx"]: row.get("detector_observed") if counts[row["frame_idx"]] == 1 else None
            for row in rows
        })
    return {
        row["frame_idx"]: bool(
            counts[row["frame_idx"]] == 1
            and row["visible"]
            and row["track_id"] == 0
            and row["cam"] is not None
            and len(row["cam"]) == 9
            and np.isfinite(row["cam"]).all()
            and np.isfinite(row["conf"])
            and row["conf"] >= MIN_COURT_QUALITY
        )
        for row in rows
    }


def _path_continuity(
    rows: list[dict[str, Any]], camera: dict[int, bool], contexts: dict[int, str | None],
    detector_runs: dict[int, bool | None],
) -> list[bool]:
    """Only bridge explicitly unsampled frames with continuous valid geometry.

    No person row on a detector tick is missing evidence, not a sampling gap.
    Missing camera/freshness metadata is likewise a barrier, including legacy data.
    """
    result = [False] * len(rows)
    for i in range(1, len(rows)):
        previous, current = rows[i - 1], rows[i]
        context = current.get("context_id")
        result[i] = bool(
            context is not None and context == previous.get("context_id")
            and current["frame_idx"] > previous["frame_idx"]
            and all(
                camera.get(frame, False) and contexts.get(frame) == context and detector_runs.get(frame) is False
                for frame in range(previous["frame_idx"] + 1, current["frame_idx"])
            )
        )
    return result


def build(store: EventStore, tracks: TrackStore | None, fps: float) -> MatchAnalytics:
    a = MatchAnalytics(fps)
    records = rally_records(store)
    end = max((r.end for r in records), default=0)
    camera_contexts: dict[int, str | None] = {}
    detector_runs: dict[int, bool | None] = {}
    camera = _camera_validity(
        tracks, 0, end, contexts=camera_contexts, detector_runs=detector_runs
    ) if tracks is not None else {}
    official = {s.get("event_id") for r in records if r.official for s in r.shots}
    # A stroke hypothesis is a match statistic only once an official rally owns it.
    for ev in store.query(types=["stroke"]):
        if ev.event_id in official:
            spatial_valid = camera.get(ev.frame_start, False)
            a.on_stroke(ev, spatial_valid=spatial_valid)
    for rec in records:
        if tracks is not None and rec.official:
            rows = tracks.read([TrackObject.PLAYER], rec.start, rec.end).to_pylist()
            # Calibration rows are read once above, then shared by contacts and paths.
            # Preserve missing and rejected rows so a path can never bridge them.
            for player in sorted({row["player_id"] for row in rows if row["player_id"] is not None}):
                # Scheduled carries are renderable estimates, not new feet samples.
                # Explicit failed detector matches stay as path barriers.
                selected = [
                    row for row in rows
                    if row["player_id"] == player and row.get("detector_observed") is not False
                ]
                counts = Counter(row["frame_idx"] for row in selected)
                a.on_presence(
                    player,
                    [(row["court_x"], row["court_y"]) for row in selected],
                    frames=[row["frame_idx"] for row in selected],
                    track_ids=[row["track_id"] for row in selected],
                    valid=[
                        bool(
                            counts[row["frame_idx"]] == 1
                            and observed_player_row(row)
                            and camera.get(row["frame_idx"], False)
                            and row.get("context_id") is not None
                            and row["context_id"] == camera_contexts.get(row["frame_idx"])
                        )
                        for row in selected
                    ],
                    expected_frames=rec.end - rec.start + 1,
                    contexts=[
                        (row["context_id"], row["participant_observation_id"])
                        if row.get("context_id") is not None and row.get("participant_observation_id") is not None
                        else None
                        for row in selected
                    ],
                    continuous_from_previous=_path_continuity(selected, camera, camera_contexts, detector_runs),
                )
        a.on_rally(rec)
    # Include official intervals with no player rows in the availability denominator.
    expected = sum(r.end - r.start + 1 for r in records if r.official)
    for stats in a.players.values():
        stats.distance_expected = expected
    return a
