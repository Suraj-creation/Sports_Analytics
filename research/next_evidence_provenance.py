"""Source-bound executor records for fixed-input experiments.

Trace-generator metadata describes an input artifact. It is never proof of the
source or dirty state that executed a later ablation.
"""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def file_sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def snapshot_executor(root: Path, output: Path, paths: list[Path], harness: Path) -> dict:
    """Copy the exact relevant source bytes, including untracked/dirty files."""
    root = root.resolve()
    paths = sorted({path.resolve() for path in paths})
    names = [str(path.relative_to(root)) for path in paths]
    snapshot = output / "executor_source"
    snapshot.mkdir()
    hashes = {}
    for path, name in zip(paths, names, strict=True):
        content = path.read_bytes()
        hashes[name] = hashlib.sha256(content).hexdigest()
        target = snapshot / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)

    def git(*args):
        return subprocess.check_output(["git", *args], cwd=root)

    diff = git("diff", "HEAD", "--", *names)
    (output / "executor.diff").write_bytes(diff)
    status = git("status", "--porcelain", "--", *names).decode().splitlines()
    return {
        "schema_version": "fixed-input-executor:v1",
        "git_commit": git("rev-parse", "HEAD").decode().strip(),
        "branch": git("branch", "--show-current").decode().strip(),
        "working_tree_status": status,
        "source_dirty": bool(status),
        "source_sha256": hashes,
        "harness": str(harness.resolve().relative_to(root)),
        "harness_sha256": hashes[str(harness.resolve().relative_to(root))],
        "source_snapshot_directory": str(snapshot.relative_to(output)),
        "record_directory": str(output.resolve()),
        "dirty_diff_sha256": hashlib.sha256(diff).hexdigest(),
        "scope": "exact relevant executor sources; separate from trace-generator provenance",
    }


def executor_sources_unchanged(root: Path, executor: dict) -> bool:
    return all(
        (root / name).is_file() and file_sha256(root / name) == expected
        for name, expected in executor["source_sha256"].items()
    )


def trace_epoch_reset_indices(rows: list[dict], *, format_events: list[dict] | None = None) -> set[int]:
    """Infer recorded provider replacement after a nonterminal flush.

    Recorded format decisions explicitly establish replacement, even if both
    visible state snapshots are idle. Without that event stream, only a visible
    reset can be inferred; equal snapshots never establish private-state reset.
    """
    resets = set()
    empty = {
        "state": "idle",
        "start": None,
        "closed": None,
        "moving_run": 0,
        "invisible_run": 0,
        "last_contact": None,
    }
    if format_events is not None:
        superseded = {event["supersedes"] for event in format_events if event.get("supersedes")}
        boundaries = {
            event["frame_start"]
            for event in format_events
            if event["type"] == "format_decision"
            and event["status"] != "retracted"
            and event["event_id"] not in superseded
            and event["frame_start"] > 0
        }
        for boundary in sorted(boundaries):
            candidates = [
                index
                for index, row in enumerate(rows[:-1])
                if row["call"] == "flush" and row["frame"] == boundary - 1 and rows[index + 1]["frame"] >= boundary
            ]
            if len(candidates) != 1:
                raise ValueError(f"recorded format boundary {boundary} lacks a unique trace flush")
            resets.add(candidates[0])
        return resets
    for index, row in enumerate(rows[:-1]):
        if row["call"] != "flush":
            continue
        following = rows[index + 1]
        before, after = following.get("before"), row.get("after")
        if not all(isinstance(state, dict) and all(key in state for key in empty) for state in (before, after)):
            raise ValueError("nonterminal flush lacks the adjacent provider state snapshots")
        if following["frame"] < row["frame"]:
            raise ValueError("trace frame identity decreases across a flush")
        changed = any(before[key] != after[key] for key in empty)
        if changed and all(before[key] == value for key, value in empty.items()):
            resets.add(index)
        elif changed:
            raise ValueError("nonterminal flush has an unexplained provider-state change")
    return resets
