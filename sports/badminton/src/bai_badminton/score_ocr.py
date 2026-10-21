"""Scoreboard (broadcast score bug) reconciliation.

Geometry gets the rally *reason* right far more often than the *winner* (85.7 % vs 68.9 % on the
legacy evaluation: most winner errors are the wrong fault side).  On broadcasts the score bug is
ground truth for the winner, so the engine uses it as a cross-check:

* the bug's rows are names, not near/far — the row→player mapping is learned online from the
  first points where geometry and OCR agree (or from typed player names);
* the winning *row* comes from the board itself: the last stable reading (same value twice)
  before the rally vs the first stable reading inside the waiting window after it — exactly one
  row +1, or a reset to 0-0 from game point (``source="ocr"``).  Comparing the board with itself
  keeps OCR useful when a video starts mid-match and the engine's own score is not the board's;
* a board that did not change across a rally means it was not scored (:meth:`board_change`);
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

    def stable_before(self, frame: int, since: int) -> tuple[int, int] | None:
        """Last value read identically twice in a row within ``[since, frame)``."""
        prev: tuple[int, int] | None = None
        last: tuple[int, int] | None = None
        for r in self.readings:
            if r.frame_idx < since or r.frame_idx >= frame:
                continue
            val = (r.rows[0][1], r.rows[1][1])
            if val == prev:
                last = val
            prev = val
        return last

    def board_change(self, start: int, end: int, until: int, lookback: int) -> str | None:
        """Did the scoreboard change across a rally? ``"changed"`` / ``"unchanged"`` / ``None``
        (no stable reading on one side). Independent of the row→player mapping, so it works from
        the first rally — a rally the board did not count was warm-up, a let or a replay."""
        a = self.stable_before(start, start - lookback)
        b = self.stable_after(end, until)
        if a is None or b is None:
            return None
        return "unchanged" if a == b else "changed"

    def winner_from_ocr(
        self,
        before: dict[str, int],
        start: int,
        end: int,
        until: int,
        geometry_winner: str | None,
        lookback: int,
    ) -> tuple[str | None, str]:
        """Return ``(winner, source)``; source in {"ocr", "geometry", "ocr_unmapped"}.

        The winning *row* is read from the board itself (stable reading before the rally vs after
        it), so it works when the video starts mid-match and the engine's own score is not the
        board's. Falls back to the engine score when there is no reading before the rally."""
        after = self.stable_after(end, until)
        if after is None:
            return geometry_winner, "geometry"
        prev = self.stable_before(start, start - lookback)
        if prev is not None:
            row = self._winning_row(prev, after)
        elif self.row_map is not None:
            row = self._winning_row((before.get(self.row_map[0], 0), before.get(self.row_map[1], 0)), after)
        else:
            row = self._incremented_rows(after, before)
        if row is None:
            return geometry_winner, "geometry"
        if self.row_map is None:
            if geometry_winner is not None:  # learn which row is which player from agreement
                self._votes[(row, geometry_winner)] = self._votes.get((row, geometry_winner), 0) + 1
                self._maybe_fix_map()
            if self.row_map is None:
                return geometry_winner, "ocr_unmapped"
        return self.row_map[row], "ocr"

    @staticmethod
    def _winning_row(prev: tuple[int, int], after: tuple[int, int]) -> int | None:
        """Row that won the rally: +1 with the other row unchanged, or - when the board reset to
        0-0 for a new game - the row that was leading on game point."""
        for i in (0, 1):
            if after[i] == prev[i] + 1 and after[1 - i] == prev[1 - i]:
                return i
        if after == (0, 0) and max(prev) >= 20 and prev[0] != prev[1]:
            return 0 if prev[0] > prev[1] else 1
        return None

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
        """Fix the row mapping once one hypothesis clearly leads: geometry alone is right ~2/3 of
        the time, so a single disagreeing vote must not block the mapping forever."""
        a = self._votes.get((0, "P1"), 0) + self._votes.get((1, "P2"), 0)  # row 0 = P1
        b = self._votes.get((0, "P2"), 0) + self._votes.get((1, "P1"), 0)  # row 0 = P2
        if a >= 3 and a >= 2 * b:
            self.row_map = {0: "P1", 1: "P2"}
        elif b >= 3 and b >= 2 * a:
            self.row_map = {0: "P2", 1: "P1"}
