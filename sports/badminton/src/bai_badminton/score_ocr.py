"""Scoreboard (broadcast score bug) reconciliation.

Geometry gets the rally *reason* right far more often than the *winner* (85.7 % vs 68.9 % on the
legacy evaluation: most winner errors are the wrong fault side). A corroborated broadcast
score change is independent evidence for the winner, so the engine uses it as a cross-check:

* the bug's rows are names, not near/far — the row→player mapping is learned online from the
  first points where geometry and OCR agree (or from typed player names);
* the winning *row* comes from the board itself: the last stable reading (same value twice)
  before the rally vs one unambiguous stable change inside the waiting window after it — exactly one
  row +1 (``source="ocr"``). A reset cannot reveal an unobserved final point. Comparing the board with itself
  keeps OCR useful when a video starts mid-match and the engine's own score is not the board's;
* a board that did not change across a rally means it was not scored (:meth:`board_change`);
* disagreements are surfaced as correction evidence, never silently dropped.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass, field

from bai_badminton.perception_types import ScoreReading


def _norm(s: str) -> str:
    return "".join(c for c in s.lower() if c.isalpha())


def _name_tokens(value: str) -> tuple[str, ...]:
    """Comparison tokens only; original OCR spelling remains observation evidence."""
    folded = unicodedata.normalize("NFKD", value.casefold())
    folded = "".join(c for c in folded if not unicodedata.combining(c))
    folded = folded.replace("'", "").replace("\u2019", "")
    return tuple(re.findall(r"[^\W\d_]+", folded))


def _initials_match(full: tuple[str, ...], short: tuple[str, ...]) -> bool:
    """Require a whole first/last token and every remaining name or initial."""
    for anchor in (0, len(full) - 1):
        token = full[anchor]
        if len(token) < 2:
            continue
        remaining = full[:anchor] + full[anchor + 1 :]
        for i, observed in enumerate(short):
            if observed != token:
                continue
            rest = short[:i] + short[i + 1 :]
            if len(rest) == len(remaining) and all(
                actual == expected or (len(actual) == 1 and expected.startswith(actual))
                for expected, actual in zip(remaining, rest, strict=True)
            ):
                return True
    return False


def _person_matches(configured: tuple[str, ...], observed: tuple[str, ...]) -> bool:
    if not configured or not observed:
        return False
    if sorted(configured) == sorted(observed):
        return True  # full names may appear surname-first or given-name-first
    if len(observed) == 1 and len(observed[0]) > 1 and observed[0] in (configured[0], configured[-1]):
        return True
    if len(configured) == 1 and len(configured[0]) > 1 and configured[0] in (observed[0], observed[-1]):
        return True
    return _initials_match(configured, observed) or _initials_match(observed, configured)


def _label_matches(configured: str, observed: str) -> bool:
    """Match one score competitor, requiring both partners in a paired team label.

    Configured pairs use an explicit separator. OCR can preserve it or flatten
    both partners into one row; only one complete partition/assignment may match.
    A single partner's name cannot stand in for the configured pair.
    """
    separator = r"\s*(?:[/&+]|\band\b)\s*"
    expected = tuple(_name_tokens(part) for part in re.split(separator, configured, flags=re.IGNORECASE))
    actual = tuple(_name_tokens(part) for part in re.split(separator, observed, flags=re.IGNORECASE))
    if any(not part for part in (*expected, *actual)):
        return False
    if len(expected) == len(actual) == 1:
        return _person_matches(expected[0], actual[0])
    if len(expected) != 2:
        return False
    if len(actual) == 2:
        partitions = [actual]
    elif len(actual) == 1:
        tokens = actual[0]
        partitions = [(tokens[:i], tokens[i:]) for i in range(1, len(tokens))]
    else:
        return False
    matches = sum(
        all(_person_matches(want, got) for want, got in zip(expected, ordering, strict=True))
        for parts in partitions
        for ordering in (parts, parts[::-1])
    )
    return matches == 1


def _point_increment(prev: tuple[int, int], after: tuple[int, int]) -> int | None:
    """One observed legal increment; a reset is never a missing final point."""
    if max(prev) >= 30 or (max(prev) >= 21 and abs(prev[0] - prev[1]) >= 2):
        return None
    for i in (0, 1):
        if after[i] == prev[i] + 1 and after[1 - i] == prev[1 - i]:
            return i
    return None


type ScoreRows = tuple[tuple[str, int], tuple[str, int]]


def _canonical_rows(reading: ScoreReading) -> ScoreRows:
    # These comparison labels do not replace the original OCR observations.
    rows = sorted((_norm(name).upper(), points) for name, points in reading.rows)
    return rows[0], rows[1]


@dataclass(frozen=True)
class ScoreTransitionRef:
    """Source-only evidence for one corroborated scoreboard increment.

    Rows are normalized competitor labels ordered independently of broadcast
    rows and P1/P2 bindings. Frames retain the first two observations of each
    global corroborated value run. Repeated boards do not create another point.
    This reference associates observations; it is not a rally decision.
    """

    transition_id: str
    before_frames: tuple[int, int]
    after_frames: tuple[int, int]
    before_rows: ScoreRows
    after_rows: ScoreRows
    version: int = 1

    def __post_init__(self) -> None:
        if not self._valid():
            raise ValueError("invalid source score-transition reference")

    def _content(self) -> dict[str, object]:
        return {
            "version": self.version,
            "before_frames": list(self.before_frames),
            "after_frames": list(self.after_frames),
            "before_rows": [list(row) for row in self.before_rows],
            "after_rows": [list(row) for row in self.after_rows],
        }

    @staticmethod
    def _digest(content: dict[str, object]) -> str:
        encoded = json.dumps(content, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
        return hashlib.sha256(encoded.encode("utf-8")).hexdigest()

    def _valid(self) -> bool:
        if type(self.version) is not int or self.version != 1:
            return False
        for frames in (self.before_frames, self.after_frames):
            if (
                type(frames) is not tuple
                or len(frames) != 2
                or any(type(frame) is not int or not 0 <= frame < 2**63 for frame in frames)
                or frames[0] >= frames[1]
            ):
                return False
        if self.before_frames[1] >= self.after_frames[0]:
            return False
        for rows in (self.before_rows, self.after_rows):
            if type(rows) is not tuple or len(rows) != 2:
                return False
            for row in rows:
                if (
                    type(row) is not tuple
                    or len(row) != 2
                    or type(row[0]) is not str
                    or not row[0]
                    or _norm(row[0]).upper() != row[0]
                    or type(row[1]) is not int
                    or not 0 <= row[1] <= 30
                ):
                    return False
            if rows[0][0] >= rows[1][0]:
                return False
        if tuple(name for name, _ in self.before_rows) != tuple(name for name, _ in self.after_rows):
            return False
        if (
            _point_increment(
                (self.before_rows[0][1], self.before_rows[1][1]),
                (self.after_rows[0][1], self.after_rows[1][1]),
            )
            is None
        ):
            return False
        return type(self.transition_id) is str and self.transition_id == self._digest(self._content())

    def to_public(self) -> dict[str, object]:
        return {"transition_id": self.transition_id, **self._content()}

    @classmethod
    def from_public(cls, value: object) -> ScoreTransitionRef | None:
        """Reject malformed, incompatible or altered persisted references."""
        fields = {"transition_id", "version", "before_frames", "after_frames", "before_rows", "after_rows"}
        if type(value) is not dict or set(value) != fields:
            return None
        array_fields = ("before_frames", "after_frames", "before_rows", "after_rows")
        if any(type(value[key]) is not list for key in array_fields):
            return None
        if any(type(row) is not list for key in ("before_rows", "after_rows") for row in value[key]):
            return None
        try:
            return cls(
                transition_id=value["transition_id"],
                version=value["version"],
                before_frames=tuple(value["before_frames"]),
                after_frames=tuple(value["after_frames"]),
                before_rows=tuple(tuple(row) for row in value["before_rows"]),
                after_rows=tuple(tuple(row) for row in value["after_rows"]),
            )
        except (ValueError, TypeError):
            return None

    @classmethod
    def _from_observations(
        cls,
        before_frames: tuple[int, int],
        after_frames: tuple[int, int],
        before_rows: ScoreRows,
        after_rows: ScoreRows,
    ) -> ScoreTransitionRef:
        content = {
            "version": 1,
            "before_frames": list(before_frames),
            "after_frames": list(after_frames),
            "before_rows": [list(row) for row in before_rows],
            "after_rows": [list(row) for row in after_rows],
        }
        return cls(cls._digest(content), before_frames, after_frames, before_rows, after_rows)


@dataclass
class _CorroboratedBoardRun:
    rows: ScoreRows
    frames: tuple[int, int]
    latest_confirmed: int


@dataclass
class ScoreReconciler:
    player_names: dict[str, str | None] = field(default_factory=dict)  # P1 → "Axelsen"
    readings: list[ScoreReading] = field(default_factory=list)
    row_map: dict[int, str] | None = None  # bug row index → player id
    _votes: dict[tuple[int, str], int] = field(default_factory=dict)
    _transition_claims: dict[str, str] = field(default_factory=dict, repr=False)

    def _corroborated_runs(self, until: int) -> list[_CorroboratedBoardRun]:
        runs: list[_CorroboratedBoardRun] = []
        previous: ScoreReading | None = None
        previous_rows: ScoreRows | None = None
        for observation in self.readings:
            if observation.frame_idx > until:
                break
            rows = _canonical_rows(observation)
            if previous is not None and rows == previous_rows:
                if runs and runs[-1].rows == rows:
                    runs[-1].latest_confirmed = observation.frame_idx
                else:
                    runs.append(
                        _CorroboratedBoardRun(
                            rows,
                            (previous.frame_idx, observation.frame_idx),
                            observation.frame_idx,
                        )
                    )
            previous, previous_rows = observation, rows

        return runs

    def _before_state(self, start: int, since: int, until: int) -> ScoreReading | None:
        """Use a value visible before start and corroborated by this decision.

        Confirmation can arrive after the exchange starts. Its first image must
        already precede start, and no observation after ``until`` is consulted.
        """
        chosen: _CorroboratedBoardRun | None = None
        for run in self._corroborated_runs(until):
            if run.frames[0] >= start:
                continue
            if any(
                since <= reading.frame_idx < start
                and reading.frame_idx <= until
                and _canonical_rows(reading) == run.rows
                for reading in self.readings
            ):
                chosen = run
        if chosen is None:
            return None
        return next((reading for reading in self.readings if reading.frame_idx == chosen.frames[1]), None)

    def source_transition(self, start: int, end: int, until: int, lookback: int) -> ScoreTransitionRef | None:
        """Query evidence without claiming it for an accepted scoring rally.

        Query-local windows select the same corroborated change used by
        ``winner_from_ocr``. Its identity comes from the whole observation
        history, so delayed identical boards or row reordering cannot represent
        separate source increments. Uncorroborated noise does not split a run.
        """
        prior = self._before_state(start, start - lookback, until)
        reading, change = self._after_rally(prior, end, until)
        if prior is None or reading is None or change != "changed":
            return None
        prev = self._aligned(prior, reading)
        if prev is None or _point_increment(prev, self._points(reading)) is None:
            return None

        runs = self._corroborated_runs(until)

        for index, run in enumerate(runs):
            if not run.frames[1] <= reading.frame_idx <= run.latest_confirmed:
                continue
            if index == 0 or run.rows != _canonical_rows(reading) or runs[index - 1].rows != _canonical_rows(prior):
                return None
            before = runs[index - 1]
            try:
                return ScoreTransitionRef._from_observations(before.frames, run.frames, before.rows, run.rows)
            except ValueError:
                return None
        return None

    def claim_transition(self, ref: ScoreTransitionRef, owner: str) -> bool:
        """Claim only when a rally becomes an accepted scoring decision.

        Validated durable references rebuild claims without perception history.
        The same owner's retry is idempotent; another owner is rejected.
        """
        if not isinstance(ref, ScoreTransitionRef) or not ref._valid() or type(owner) is not str or not owner.strip():
            return False
        existing = self._transition_claims.get(ref.transition_id)
        if existing is not None:
            return existing == owner
        self._transition_claims[ref.transition_id] = owner
        return True

    def clear_transition_claims(self) -> None:
        self._transition_claims.clear()

    def add(self, r: ScoreReading) -> ScoreReading | None:
        """Return a corroborated broadcast observation, independent of player mapping.

        Names and points must agree in two distinct, ordered observations. This
        supports displaying the source board without assigning its rows to P1/P2.
        """
        if r.context is not None and r.context.actual_replay_status == "replay":
            return None
        if (
            not math.isfinite(r.conf)
            or not 0.5 <= r.conf <= 1
            or r.frame_idx < 0
            or len(r.rows) != 2
            or any(
                not isinstance(name, str) or not _norm(name) or type(points) is not int or not 0 <= points <= 30
                for name, points in r.rows
            )
            or _norm(r.rows[0][0]) == _norm(r.rows[1][0])
        ):
            return None
        previous = self.readings[-1] if self.readings else None
        if previous is not None and r.frame_idx <= previous.frame_idx:
            return None
        self.readings.append(r)
        if previous is not None and self._names(previous) != self._names(r):
            self.row_map = None
            self._votes.clear()
        if self.row_map is None:
            self._try_names(r)
        if previous is not None and all(
            _norm(name) == _norm(old_name) and points == old_points
            for (name, points), (old_name, old_points) in zip(r.rows, previous.rows, strict=True)
        ):
            return r
        return None

    def _try_names(self, r: ScoreReading) -> None:
        names = {pid: name for pid, name in self.player_names.items() if name}
        if len(names) != 2:
            return
        m: dict[int, str] = {}
        for i, (row_name, _) in enumerate(r.rows):
            candidates = [pid for pid, name in names.items() if _label_matches(name, row_name)]
            if len(candidates) != 1:
                return
            m[i] = candidates[0]
        if len(set(m.values())) == 2:
            self.row_map = m

    @staticmethod
    def _names(reading: ScoreReading) -> tuple[str, str]:
        return _norm(reading.rows[0][0]), _norm(reading.rows[1][0])

    def _stable(self, lo: int, hi: int, *, first: bool) -> ScoreReading | None:
        readings = self._stable_readings(lo, hi)
        return readings[0 if first else -1] if readings else None

    def _stable_readings(self, lo: int, hi: int) -> list[ScoreReading]:
        """Corroborated values in observation order, retaining later changes."""
        previous: ScoreReading | None = None
        stable: list[ScoreReading] = []
        for r in self.readings:
            if not lo <= r.frame_idx <= hi:
                continue
            if (
                previous is not None
                and self._names(previous) == self._names(r)
                and self._points(previous) == self._points(r)
            ):
                stable.append(r)
            previous = r
        return stable

    @staticmethod
    def _points(reading: ScoreReading) -> tuple[int, int]:
        return reading.rows[0][1], reading.rows[1][1]

    def _aligned(self, before: ScoreReading, after: ScoreReading) -> tuple[int, int] | None:
        if self._names(before) == self._names(after):
            return self._points(before)
        if self._names(before)[::-1] == self._names(after):
            return self._points(before)[::-1]
        return None

    def stable_after(self, frame: int, until: int) -> tuple[int, int] | None:
        """First name-and-score value read twice within ``(frame, until]``."""
        reading = self._stable(frame + 1, until, first=True)
        return self._points(reading) if reading is not None else None

    def stable_before(self, frame: int, since: int) -> tuple[int, int] | None:
        """Last value read identically twice in a row within ``[since, frame)``."""
        reading = self.stable_reading_before(frame, since)
        return self._points(reading) if reading is not None else None

    def stable_reading_before(self, frame: int, since: int) -> ScoreReading | None:
        """Keep row names alongside historical points so later row swaps are harmless."""
        return self._stable(since, frame - 1, first=False)

    def mapping_at(self, reading: ScoreReading) -> dict[int, str] | None:
        if self.row_map is None or not self.readings:
            return None
        latest_names = self._names(self.readings[-1])
        if self._names(reading) == latest_names:
            return dict(self.row_map)
        if self._names(reading)[::-1] == latest_names:
            return {0: self.row_map[1], 1: self.row_map[0]}
        return None

    def _after_rally(self, prior: ScoreReading | None, end: int, until: int) -> tuple[ScoreReading | None, str | None]:
        """Wait past the old board, but never select one of conflicting stable changes.

        An unchanged board can persist for a while after the shuttle lands. Once
        it changes, every corroborated reading in this window must describe the
        same board (allowing row reorder and a completed game's reset to 0-0).
        A second sporting change or incompatible names makes the association
        unresolved.
        """
        stable = self._stable_readings(end + 1, until)
        if not stable:
            return None, None
        chosen: ScoreReading | None = None
        for reading in stable:
            if chosen is not None:
                aligned = self._aligned(chosen, reading)
                if aligned == self._points(reading):
                    continue
                # A displayed final score followed by the new game's 0-0 is
                # still the same point. Never allow an additional increment.
                before = self._aligned(prior, chosen) if prior is not None else None
                points = self._points(chosen)
                completed = max(points) >= 30 or (max(points) >= 21 and abs(points[0] - points[1]) >= 2)
                if (
                    aligned is not None
                    and self._points(reading) == (0, 0)
                    and completed
                    and before is not None
                    and self._winning_row(before, points) is not None
                ):
                    continue
                return None, "ambiguous"
            if prior is not None:
                before = self._aligned(prior, reading)
                if before is None:
                    return None, "ambiguous"
                if before == self._points(reading):
                    continue
            chosen = reading
        if chosen is None:
            return stable[-1], "unchanged"
        return chosen, "changed" if prior is not None else None

    def board_change(self, start: int, end: int, until: int, lookback: int) -> str | None:
        """Did the scoreboard change across a rally? ``"changed"`` / ``"unchanged"`` / ``None``
        (no stable reading on one side). Independent of the row→player mapping, so it works from
        the first rally — a rally the board did not count was warm-up, a let or a replay."""
        before = self._before_state(start, start - lookback, until)
        if before is None:
            return None
        _, change = self._after_rally(before, end, until)
        if change == "changed":
            ref = self.source_transition(start, end, until, lookback)
            if ref is not None and ref.after_frames[0] < start:
                return None  # already visible before this candidate began
        return change if change in ("changed", "unchanged") else None

    def winner_from_ocr(
        self,
        before: dict[str, int],
        start: int,
        end: int,
        until: int,
        geometry_winner: str | None,
        lookback: int,
    ) -> tuple[str | None, str]:
        """Return winner plus OCR, geometric, unmapped or ambiguous provenance.

        The winning *row* is read from the board itself (stable reading before the rally vs after
        it), so it works when the video starts mid-match and the engine's own score is not the
        board's. Falls back to the engine score when there is no reading before the rally."""
        prior = self._before_state(start, start - lookback, until)
        reading, change = self._after_rally(prior, end, until)
        if change == "ambiguous":
            return None, "ocr_ambiguous"
        if reading is None:
            return geometry_winner, "geometry"
        ref = self.source_transition(start, end, until, lookback)
        if ref is not None and ref.after_frames[0] < start:
            return geometry_winner, "geometry" if geometry_winner is not None else "ocr_preexisting"
        after = self._points(reading)
        mapping = self.mapping_at(reading)
        latest_names = self._names(self.readings[-1])
        if prior is not None:
            prev = self._aligned(prior, reading)
            if prev is None:
                return geometry_winner, "ocr_unmapped"
            row = self._winning_row(prev, after)
        elif mapping is not None:
            row = self._winning_row((before.get(mapping[0], 0), before.get(mapping[1], 0)), after)
        else:
            row = self._incremented_rows(after, before)
        if row is None:
            return geometry_winner, "geometry"
        if mapping is None:
            if geometry_winner is not None and self._names(reading) == latest_names:
                self._votes[(row, geometry_winner)] = self._votes.get((row, geometry_winner), 0) + 1
                self._maybe_fix_map()
                mapping = self.row_map
            if mapping is None:
                return geometry_winner, "ocr_unmapped"
        return mapping[row], "ocr"

    @staticmethod
    def _winning_row(prev: tuple[int, int], after: tuple[int, int]) -> int | None:
        """One observed +1, with the other row unchanged and game unfinished.

        A reset from game point does not reveal the missing point's winner.
        An observed final increment remains selectable by ``_after_rally``.
        """
        return _point_increment(prev, after)

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
