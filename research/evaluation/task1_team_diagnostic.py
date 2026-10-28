"""Read-only cached-observation doubles-gate diagnostic; JSON on stdout.

From the repository root, after sourcing ../gpu-env.sh, run with the existing venv:

  PYTHONPATH="$PWD/sports/badminton/src:$PWD/engine/src" \
    ../Sports_Analytics/.venv/bin/python research/evaluation/task1_team_diagnostic.py \
    --data-dir ../Sports_Analytics/data --session SESSION_ID --frames 600

The tool creates a fresh temporary event store, never writes to source sessions,
and removes its temporary results when it exits. It replays old cached model
observations, not fresh GPU inference or human annotations; the aggregate counts
are diagnostic observations, never player, team, or event accuracy. The cache
hash covers every source cache file, including any beyond the selected frames.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
import sys
import tempfile
from collections import Counter, deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "research"))

import replay_cached_observations as replay  # noqa: E402

from bai_badminton.teams import DoublesTeamTracker  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--session", required=True)
    parser.add_argument("--frames", type=int, default=600)
    args = parser.parse_args()
    if not args.session.isalnum() or args.frames < 1:
        parser.error("session must be alphanumeric and frames must be positive")
    data_dir = args.data_dir.resolve()
    catalogue = (data_dir / "sessions.sqlite").resolve()
    with sqlite3.connect(f"{catalogue.as_uri()}?mode=ro", uri=True) as connection:
        row = connection.execute("SELECT body FROM sessions WHERE session_id=?", (args.session,)).fetchone()
    if row is None:
        parser.error("unknown session")
    session = json.loads(row[0])
    media = session.get("media")
    if not media or args.frames > media["n_frames"]:
        parser.error("requested frames exceed canonical media")
    fps = media["fps_num"] / media["fps_den"]
    media["n_frames"] = args.frames
    window_frames, threshold = max(1, round(5 * fps)), max(1, round(2 * fps))
    counters: Counter[str] = Counter()
    simulations = {
        gap: {"key": None, "last": None, "good": deque(), "max": 0, "would_emit": 0}
        for gap in (max(1, round(0.5 * fps)), max(1, round(fps)), max(1, round(2 * fps)))
    }
    max_support = 0
    max_four_active = 0
    four_active_run = 0
    original = DoublesTeamTracker.update

    def inspect(self, frame, *, court_valid, active_play_evidence):
        nonlocal max_support, max_four_active, four_active_run
        people = frame.participants
        count = len(people)
        sides = Counter(p.side for p in people)
        counters["frames"] += 1
        counters[f"participants_{count}"] += 1
        if court_valid:
            counters["court_valid"] += 1
        if active_play_evidence:
            counters["active_play"] += 1
        if court_valid and active_play_evidence:
            counters["court_and_activity"] += 1
            counters[f"side_split_{sides.get('near', 0)}_{sides.get('far', 0)}"] += 1
        complete = court_valid and count == 4 and sides.get("near", 0) == sides.get("far", 0) == 2
        key = (
            tuple(tuple(sorted(p.participant_id for p in people if p.side == side)) for side in ("near", "far"))
            if complete
            else None
        )
        for gap, state in simulations.items():
            if state["last"] is not None and frame.frame_idx - state["last"] > gap:
                state.update(key=None, last=None, good=deque())
            if key is not None and state["key"] is not None and key != state["key"]:
                state.update(key=None, last=None, good=deque())
            if key is not None and active_play_evidence:
                if state["key"] is None:
                    state["key"] = key
                state["last"] = frame.frame_idx
                state["good"].append(frame.frame_idx)
                while state["good"] and frame.frame_idx - state["good"][0] >= window_frames:
                    state["good"].popleft()
                state["max"] = max(state["max"], len(state["good"]))
                if len(state["good"]) >= threshold:
                    state["would_emit"] += 1
        result = original(self, frame, court_valid=court_valid, active_play_evidence=active_play_evidence)
        counters[f"status_{result.status}"] += 1
        max_support = max(max_support, result.supporting_frames)
        if court_valid and active_play_evidence and count == 4:
            four_active_run += 1
            max_four_active = max(max_four_active, four_active_run)
        else:
            four_active_run = 0
        return result

    DoublesTeamTracker.update = inspect
    try:
        with tempfile.TemporaryDirectory(prefix="task1-team-diagnostic-") as tmp:
            result = replay.replay_session(session, data_dir, Path(tmp))
    finally:
        DoublesTeamTracker.update = original
    if result is None:
        parser.error("session has no cached observations")
    source_files = {
        "engine": ROOT / "sports/badminton/src/bai_badminton/engine.py",
        "activity": ROOT / "sports/badminton/src/bai_badminton/events/activity.py",
        "teams": ROOT / "sports/badminton/src/bai_badminton/teams.py",
        "participation": ROOT / "sports/badminton/src/bai_badminton/participation.py",
    }
    output = {
        "source_cache_sha256": result["cached_observations_sha256"],
        "cached_codec_versions": result["cached_codec_versions"],
        "source_sha256": {name: hashlib.sha256(path.read_bytes()).hexdigest() for name, path in source_files.items()},
        "fps": fps,
        "simulation_window_frames": window_frames,
        "simulation_support_threshold_frames": threshold,
        "frames": result["frames"],
        "counts": dict(counters),
        "gap_simulations": {
            str(gap): {"max_support": state["max"], "would_emit_frames": state["would_emit"]}
            for gap, state in simulations.items()
        },
        "max_stable_candidate": max_support,
        "max_four_and_active_streak": max_four_active,
        "replay_events": {k: result[k] for k in ("rallies", "official", "points")},
        "accuracy_measured": False,
        "limitations": (
            "Cached perception replay; candidate simulations are hypothetical, not actual output or ground truth."
        ),
    }
    print(json.dumps(output, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
