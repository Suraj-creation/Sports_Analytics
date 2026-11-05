"""Process-owned GPU lease for this existing benchmark executor, not a job scheduler."""

from __future__ import annotations

import fcntl
import os
import re
import subprocess
from contextlib import contextmanager
from pathlib import Path


def gpu_uuid(index: int) -> str:
    if type(index) is not int or index < 0:
        raise ValueError("physical GPU index must be a nonnegative integer")
    row = subprocess.check_output(
        [
            "nvidia-smi",
            f"--id={index}",
            "--query-gpu=uuid",
            "--format=csv,noheader,nounits",
        ],
        text=True,
        timeout=5,
    ).strip()
    if re.fullmatch(r"GPU-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", row) is None:
        raise RuntimeError("GPU UUID could not be verified")
    return row


def compute_pids(rows: str, uuid: str) -> list[int]:
    result = []
    for line in rows.splitlines():
        parts = [part.strip() for part in line.split(",")]
        if len(parts) != 2 or not parts[1].isdigit():
            raise ValueError("unrecognized GPU process evidence")
        if parts[0] == uuid:
            result.append(int(parts[1]))
    return sorted(set(result))


@contextmanager
def gpu_lease(directory: Path, uuid: str):
    if re.fullmatch(r"GPU-[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}", uuid) is None:
        raise ValueError("lease requires a verified physical GPU UUID")
    directory.mkdir(parents=True, exist_ok=True)
    # Keep the file: unlinking it would let another process lock a new inode.
    with (directory / f"{uuid}.lock").open("a+") as stream:
        try:
            fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("this GPU already has a benchmark executor lease") from exc
        try:
            stream.seek(0)
            stream.truncate()
            stream.write(str(os.getpid()) + "\n")
            stream.flush()
            rows = subprocess.check_output(
                [
                    "nvidia-smi",
                    "--query-compute-apps=gpu_uuid,pid",
                    "--format=csv,noheader,nounits",
                ],
                text=True,
                timeout=5,
            )
            pids = compute_pids(rows, uuid)
            if pids:
                raise RuntimeError(f"GPU already has compute processes: {pids}")
            yield
        finally:
            fcntl.flock(stream, fcntl.LOCK_UN)
