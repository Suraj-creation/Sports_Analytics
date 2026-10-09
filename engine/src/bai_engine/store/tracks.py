"""Columnar track storage: one Parquet file per (object, chunk) per session.

File names encode the inclusive frame range (``<obj>/f000000120-000000179.v<rev>.parquet``) so a
range read only opens overlapping files.  Refinement passes write a higher revision of the same
chunk atomically (write temp → rename); readers always take the highest revision per range.
"""

from __future__ import annotations

import re
import threading
from collections.abc import Iterable
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq

from bai_engine.schema.tracks import TRACK_ARROW_SCHEMA, TrackObject

_NAME_RE = re.compile(r"^f(\d{9})-(\d{9})\.v(\d+)\.parquet$")


class TrackStore:
    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()

    def _dir(self, obj: TrackObject) -> Path:
        d = self.root / obj.value
        d.mkdir(parents=True, exist_ok=True)
        return d

    def write_chunk(self, obj: TrackObject, frame_start: int, frame_end: int, table: pa.Table) -> Path:
        if frame_end < frame_start:
            raise ValueError("frame_end < frame_start")
        if not table.schema.equals(TRACK_ARROW_SCHEMA, check_metadata=False):
            table = table.cast(TRACK_ARROW_SCHEMA)
        if table.num_rows:
            fmin = pc.min(table["frame_idx"]).as_py()
            fmax = pc.max(table["frame_idx"]).as_py()
            if fmin < frame_start or fmax > frame_end:
                raise ValueError(f"rows [{fmin},{fmax}] outside chunk [{frame_start},{frame_end}]")
        d = self._dir(obj)
        with self._lock:
            rev = 1 + max((r for (s, e, r, _) in self._files(obj) if s == frame_start and e == frame_end), default=0)
            final = d / f"f{frame_start:09d}-{frame_end:09d}.v{rev}.parquet"
            tmp = final.with_suffix(".tmp")
            pq.write_table(table, tmp, compression="zstd")
            tmp.replace(final)
        return final

    def _files(self, obj: TrackObject) -> list[tuple[int, int, int, Path]]:
        d = self.root / obj.value
        if not d.exists():
            return []
        out = []
        for p in d.iterdir():
            m = _NAME_RE.match(p.name)
            if m:
                out.append((int(m.group(1)), int(m.group(2)), int(m.group(3)), p))
        return out

    def _latest(self, obj: TrackObject) -> list[tuple[int, int, Path]]:
        best: dict[tuple[int, int], tuple[int, Path]] = {}
        for s, e, r, p in self._files(obj):
            if (s, e) not in best or r > best[(s, e)][0]:
                best[(s, e)] = (r, p)
        return sorted((s, e, p) for (s, e), (_, p) in best.items())

    def read(self, objs: Iterable[TrackObject], frame_from: int, frame_to: int) -> pa.Table:
        tables: list[pa.Table] = []
        for obj in objs:
            for s, e, p in self._latest(obj):
                if e < frame_from or s > frame_to:
                    continue
                t = pq.read_table(p)
                mask = pc.and_(pc.greater_equal(t["frame_idx"], frame_from), pc.less_equal(t["frame_idx"], frame_to))
                tables.append(t.filter(mask))
        if not tables:
            return TRACK_ARROW_SCHEMA.empty_table()
        out = pa.concat_tables([t.cast(TRACK_ARROW_SCHEMA) for t in tables])
        return out.sort_by([("frame_idx", "ascending"), ("track_id", "ascending")])

    def covered_ranges(self, obj: TrackObject) -> list[tuple[int, int]]:
        """Merged inclusive frame ranges that have track data for ``obj``."""
        ranges = [(s, e) for s, e, _ in self._latest(obj)]
        merged: list[tuple[int, int]] = []
        for s, e in sorted(ranges):
            if merged and s <= merged[-1][1] + 1:
                merged[-1] = (merged[-1][0], max(merged[-1][1], e))
            else:
                merged.append((s, e))
        return merged
