"""Bounded, provisional participant hypotheses, independent of team scoring.

A track is not a name or a proven identity. Entries, exits and substitutions are
video-derived hypotheses. Unknown coverage is never evidence of absence.
"""

from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from uuid import uuid4

import numpy as np

from bai_badminton.perception_types import PersonObs


@dataclass(frozen=True)
class ParticipantObservation:
    participant_id: str
    track_id: int
    side: str
    confidence: float
    user_identity: str | None = None
    certainty: str = "provisional"


@dataclass(frozen=True)
class ParticipationEvent:
    kind: str
    participant_id: str
    track_id: int
    frame_idx: int
    time_s: float
    side: str
    confidence: float
    related_participant_id: str | None = None
    certainty: str = "hypothesis"
    reason: str = ""
    appearance_similarity: float | None = None
    position_distance: float | None = None  # image distance in frame heights


@dataclass(frozen=True)
class ParticipantFrame:
    frame_idx: int
    tracker_instance: str
    participants: tuple[ParticipantObservation, ...] = ()
    events: tuple[ParticipationEvent, ...] = ()
    ambiguous_track_ids: tuple[int, ...] = ()
    capacity_limited: bool = False


@dataclass
class _Track:
    participant_id: str
    track_id: int
    side: str
    confidence: float
    missing: int = 0
    user_identity: str | None = None
    appearance: np.ndarray | None = None
    position: tuple[float, float] | None = None


@dataclass(frozen=True)
class _ReidMemory:
    frame_idx: int
    participant_id: str
    appearance: np.ndarray
    position: tuple[float, float]


@dataclass(frozen=True)
class _Exit:
    frame_idx: int
    side: str
    participant_id: str


@dataclass(frozen=True)
class _Entry:
    frame_idx: int
    side: str
    participant_id: str
    track_id: int


class ParticipantTracker:
    """Maintain visual-track hypotheses; callers should persist instance ID in provenance.

    IDs are unique across process restarts by default. For deterministic replay,
    supply the recorded instance_id to the constructor. Frame indices must increase.
    coverage_valid must only be true when detection coverage is usable on the
    intended court; one missed detection is not itself proof of a departure.
    """

    def __init__(
        self,
        frame_height: float,
        entry_frames: int = 3,
        exit_frames: int = 30,
        substitution_window_frames: int = 300,
        *,
        fps: float = 30.0,
        min_confidence: float = 0.5,
        max_tracks: int = 64,
        instance_id: str | None = None,
    ) -> None:
        if (
            frame_height <= 0
            or entry_frames < 1
            or exit_frames < 1
            or substitution_window_frames < 0
            or fps <= 0
            or not 0 <= min_confidence <= 1
            or max_tracks < 4
        ):
            raise ValueError("invalid participation tracker configuration")
        if instance_id is not None and (not instance_id or not instance_id.isalnum()):
            raise ValueError("instance_id must contain only letters and digits")
        self.frame_height = float(frame_height)
        self.entry_frames = entry_frames
        self.exit_frames = exit_frames
        self.substitution_window_frames = substitution_window_frames
        self.fps = float(fps)
        self.min_confidence = min_confidence
        self.max_tracks = max_tracks
        self.instance_id = instance_id or uuid4().hex
        self._next_id = 1
        self._last_frame = -1
        self._first_coverage_frame: int | None = None
        self._tracks: dict[int, _Track] = {}
        self._pending: dict[int, tuple[int, int, int]] = {}
        self._recent_exits: deque[_Exit] = deque(maxlen=max_tracks)
        self._recent_entries: deque[_Entry] = deque(maxlen=max_tracks)
        # Ephemeral visual descriptors, bounded and never emitted in events.
        self._reid_memory: deque[_ReidMemory] = deque(maxlen=max_tracks)
        self._reid_age_frames = round(600 * fps)

    def _side(self, obs: PersonObs) -> str:
        if obs.court_xy is not None and np.isfinite(obs.court_xy[1]):
            return "near" if obs.court_xy[1] < 0 else "far"
        return "near" if obs.bbox[3] > self.frame_height * 0.5 else "far"

    def _event(
        self,
        kind: str,
        track: _Track,
        frame: int,
        related: str | None = None,
        *,
        reason: str = "",
        appearance_similarity: float | None = None,
        position_distance: float | None = None,
    ) -> ParticipationEvent:
        return ParticipationEvent(
            kind,
            track.participant_id,
            track.track_id,
            frame,
            frame / self.fps,
            track.side,
            track.confidence,
            related,
            reason=reason,
            appearance_similarity=appearance_similarity,
            position_distance=position_distance,
        )

    @staticmethod
    def _appearance(obs: PersonObs) -> np.ndarray | None:
        if obs.appearance is None:
            return None
        try:
            value = np.asarray(obs.appearance, dtype=np.float32)
        except (TypeError, ValueError, OverflowError):
            return None
        if value.ndim != 1 or not 2 <= value.size <= 256 or not np.isfinite(value).all() or (value < 0).any():
            return None
        norm = float(np.linalg.norm(value))
        return value / norm if np.isfinite(norm) and norm > 1e-8 else None

    def _position(self, obs: PersonObs) -> tuple[float, float]:
        return (float((obs.bbox[0] + obs.bbox[2]) / (2 * self.frame_height)), float(obs.bbox[3] / self.frame_height))

    def _reid_candidate(self, track: _Track, frame: int) -> ParticipationEvent | None:
        if track.appearance is None or track.position is None:
            return None
        ranked = []
        for old in self._reid_memory:
            if frame - old.frame_idx > self._reid_age_frames or old.appearance.shape != track.appearance.shape:
                continue
            distance = float(np.linalg.norm(np.asarray(track.position) - old.position))
            similarity = float(np.clip(np.dot(track.appearance, old.appearance), 0, 1))
            if distance <= 0.5 and similarity >= 0.95:
                ranked.append((similarity, distance, old))
        ranked.sort(key=lambda v: (-v[0], v[1], v[2].participant_id))
        if not ranked or (len(ranked) > 1 and ranked[0][0] - ranked[1][0] < 0.1):
            return None
        score, distance, old = ranked[0]
        return self._event(
            "PLAYER_REIDENTIFICATION_UNCERTAIN",
            track,
            frame,
            old.participant_id,
            reason="weak_appearance_and_position",
            appearance_similarity=round(score, 4),
            position_distance=round(distance, 4),
        )

    def assign_user_identity(self, participant_id: str, name: str) -> None:
        if not name.strip():
            raise ValueError("name must not be empty")
        for track in self._tracks.values():
            if track.participant_id == participant_id:
                track.user_identity = name.strip()
                return
        raise KeyError(participant_id)

    def update(
        self,
        frame_idx: int,
        persons: list[PersonObs],
        *,
        coverage_valid: bool = False,
        absence_valid: bool | None = None,
    ) -> ParticipantFrame:
        """Only count absence on frames that actually ran a reliable detector.

        If absence_valid is omitted, coverage_valid supplies the legacy behavior.
        A true absence flag never overrides unavailable overall coverage.
        """
        if frame_idx <= self._last_frame:
            raise ValueError("frames must be strictly increasing")
        self._last_frame = frame_idx
        counts = Counter(p.track_id for p in persons)
        ambiguous = tuple(sorted(k for k, n in counts.items() if n > 1))
        # Capacity errors and unavailable coverage provide no negative evidence.
        limited = len(counts) > self.max_tracks
        if not coverage_valid or limited:
            self._pending.clear()
            return ParticipantFrame(
                frame_idx, self.instance_id, ambiguous_track_ids=ambiguous, capacity_limited=limited
            )
        if self._first_coverage_frame is None:
            self._first_coverage_frame = frame_idx
        seen_ids = set(counts)
        # Untracked or contradictory observations might be any missing person.
        # They do not prove that any participant left the selected court.
        if absence_valid is None:
            absence_valid = coverage_valid
        absence_usable = absence_valid and not ambiguous and all(track_id >= 0 for track_id in counts)
        valid = {
            p.track_id: p
            for p in persons
            if p.track_id >= 0
            and counts[p.track_id] == 1
            and np.isfinite(p.conf)
            and self.min_confidence <= p.conf <= 1.0
            and np.asarray(p.bbox).shape == (4,)
            and np.isfinite(p.bbox).all()
            and p.bbox[2] > p.bbox[0]
            and p.bbox[3] > p.bbox[1]
        }
        events: list[ParticipationEvent] = []
        exited = False
        for track_id, track in list(self._tracks.items()):
            if track_id in valid:
                p = valid[track_id]
                track.side, track.confidence, track.missing = self._side(p), float(p.conf), 0
                signature = self._appearance(p)
                if signature is not None:
                    track.appearance = signature
                track.position = self._position(p)
            elif absence_usable and track_id not in seen_ids:
                track.missing += 1
                if track.missing >= self.exit_frames:
                    events.append(self._event("PLAYER_EXITED", track, frame_idx))
                    self._recent_exits.append(_Exit(frame_idx, track.side, track.participant_id))
                    if track.appearance is not None and track.position is not None:
                        self._reid_memory.append(
                            _ReidMemory(frame_idx, track.participant_id, track.appearance.copy(), track.position)
                        )
                    del self._tracks[track_id]
                    exited = True
        # Only consecutive confident observations can establish a new hypothesis.
        self._pending = {tid: item for tid, item in self._pending.items() if tid in valid and tid not in self._tracks}
        entered: list[_Track] = []
        for tid in sorted(valid):
            if tid in self._tracks:
                continue
            count, last, first = self._pending.get(tid, (0, frame_idx - 1, frame_idx))
            if last == frame_idx - 1:
                count += 1
            else:
                count, first = 1, frame_idx
            self._pending[tid] = (count, frame_idx, first)
            if count < self.entry_frames or len(self._tracks) >= self.max_tracks:
                continue
            p = valid[tid]
            pid = f"participant-{self.instance_id}-{self._next_id:06d}"
            self._next_id += 1
            track = _Track(
                pid, tid, self._side(p), float(p.conf), appearance=self._appearance(p), position=self._position(p)
            )
            self._tracks[tid] = track
            self._pending.pop(tid, None)
            entered.append(track)
            initial = first < self._first_coverage_frame + self.entry_frames
            kind = "PARTICIPANT_FIRST_OBSERVED" if initial else "PLAYER_ENTERED"
            reason = "recording_initialization" if initial else "late_appearance"
            events.append(self._event(kind, track, frame_idx, reason=reason))
            if not initial:
                self._recent_entries.append(_Entry(frame_idx, track.side, track.participant_id, track.track_id))
        # Two simultaneous new tracks competing for the same old hypothesis
        # leave the association unresolved rather than asserting both.
        suggestions = [s for track in entered if (s := self._reid_candidate(track, frame_idx)) is not None]
        contenders = Counter(s.related_participant_id for s in suggestions)
        events.extend(s for s in suggestions if contenders[s.related_participant_id] == 1)
        while self._reid_memory and frame_idx - self._reid_memory[0].frame_idx > self._reid_age_frames:
            self._reid_memory.popleft()
        while self._recent_exits and frame_idx - self._recent_exits[0].frame_idx > self.substitution_window_frames:
            self._recent_exits.popleft()
        while self._recent_entries and frame_idx - self._recent_entries[0].frame_idx > self.substitution_window_frames:
            self._recent_entries.popleft()
        # A confirmed appearance may precede or follow an absence-based exit.
        # Keep only a bounded window and require a single plausible pair.
        if entered or exited:
            for side in ("near", "far"):
                new = [
                    x
                    for x in self._recent_entries
                    if x.side == side
                    and x.track_id in self._tracks
                    and self._tracks[x.track_id].participant_id == x.participant_id
                ]
                old = [x for x in self._recent_exits if x.side == side]
                if len(new) == len(old) == 1:
                    track = self._tracks[new[0].track_id]
                    events.append(
                        self._event(
                            "PLAYER_SUBSTITUTION_OR_IDENTITY_UNCERTAIN",
                            track,
                            frame_idx,
                            old[0].participant_id,
                            reason="same_side_temporal_candidate",
                        )
                    )
                    # Consuming both endpoints avoids repeated or conflicting claims.
                    self._recent_entries.remove(new[0])
                    self._recent_exits.remove(old[0])
        observations = tuple(
            ParticipantObservation(t.participant_id, tid, t.side, t.confidence, t.user_identity)
            for tid, t in sorted(self._tracks.items())
            if tid in valid
        )
        return ParticipantFrame(frame_idx, self.instance_id, observations, tuple(events), ambiguous, limited)
