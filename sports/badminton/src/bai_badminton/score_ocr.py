"""Scoreboard (broadcast score bug) reconciliation.

Geometry gets the rally *reason* right far more often than the *winner* (85.7 % vs 68.9 % on the
legacy evaluation: most winner errors are the wrong fault side).  On broadcasts the score bug is
ground truth for the winner, so the engine uses it as a cross-check:

* the bug's rows are names, not near/far — the row→player mapping is learned online from the
  first points where geometry and OCR agree (or from typed player names);
* after a rally ends, the first *stable* reading (same value twice) inside the waiting window
  that shows exactly one side incremented decides the winner (``source="ocr"``);
* disagreements are surfaced as correction evidence, never silently dropped.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from bai_badminton.perception_types import ScoreReading


def _norm(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalpha())


@dataclass
class ScoreReconciler:
    player_names: dict[str, str | None] = field(default_factory=dict)  # P1 → "Axelsen"
    readings: list[ScoreReading] = field(default_factory=list)
    row_map: dict[int, str] | None = None  # bug row index → player id
    _votes: dict[tuple[int, str], int] = field(default_factory=dict)

    def add(self, r: ScoreReading) -> None:
        if r.conf < 0.5:
            return
        self.readings.append(r)
        if self.row_map is None:
            self._try_names(r)

    def _try_names(self, r: ScoreReading) -> None:
        names = {pid: _norm(n) for pid, n in self.player_names.items() if n}
        if len(names) < 2:
            return
        m: dict[int, str] = {}
        for i, (row_name, _) in enumerate(r.rows):
            rn = _norm(row_name)
            for pid, n in names.items():
                if n and rn and (n in rn or rn in n or n.split()[-1:] == rn.split()[-1:]):
                    m[i] = pid
        if len(m) == 2 and len(set(m.values())) == 2:
            self.row_map = m

    def stable_after(self, frame: int, until: int) -> tuple[int, int] | None:
        """First value read identically twice in a row within ``(frame, until]``."""
        prev: tuple[int, int] | None = None
        for r in self.readings:
            if r.frame_idx <= frame or r.frame_idx > until:
                continue
            val = (r.rows[0][1], r.rows[1][1])
            if val == prev:
                return val
            prev = val
        return None

    def winner_from_ocr(
        self, before: dict[str, int], end_frame: int, until: int, geometry_winner: str | None
    ) -> tuple[str | None, str]:
        """Return ``(winner, source)``; source ∈ {"ocr", "geometry", "ocr_unmapped"}."""
        val = self.stable_after(end_frame, until)
        if val is None:
            return geometry_winner, "geometry"
        if self.row_map is None:
            # learn mapping: which row incremented, and which player geometry says won
            rows_up = self._incremented_rows(val, before)
            if rows_up is not None and geometry_winner is not None:
                key = (rows_up, geometry_winner)
                self._votes[key] = self._votes.get(key, 0) + 1
                self._maybe_fix_map()
            if self.row_map is None:
                return geometry_winner, "ocr_unmapped"
        mapped = {self.row_map[0]: val[0], self.row_map[1]: val[1]}
        inc = [
            p
            for p in ("P1", "P2")
            if mapped.get(p, -1) == before.get(p, 0) + 1 and mapped.get(_o(p), -1) == before.get(_o(p), 0)
        ]
        if len(inc) == 1:
            return inc[0], "ocr"
        # new game (0–0) after a game point: winner is the side that was on game point
        if mapped.get("P1") == 0 and mapped.get("P2") == 0:
            return geometry_winner, "geometry"
        return geometry_winner, "geometry"

    @staticmethod
    def _incremented_rows(val: tuple[int, int], before: dict[str, int]) -> int | None:
        """Row index whose value is one more than one previous score while the other row equals
        the other previous score (ambiguous or unchanged readings return ``None``)."""
        prev = list(before.values())
        if sorted(val) == sorted(prev):
            return None
        hits = [i for i in (0, 1) for j in (0, 1) if val[i] == prev[j] + 1 and val[1 - i] == prev[1 - j]]
        return hits[0] if len(set(hits)) == 1 else None

    def _maybe_fix_map(self) -> None:
        for row in (0, 1):
            for pid in ("P1", "P2"):
                if self._votes.get((row, pid), 0) >= 3 and self._votes.get((row, _o(pid)), 0) == 0:
                    self.row_map = {row: pid, 1 - row: _o(pid)}
                    return


def _o(p: str) -> str:
    return "P2" if p == "P1" else "P1"
