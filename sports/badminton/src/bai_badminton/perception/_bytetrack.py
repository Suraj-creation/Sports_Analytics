"""Keep the backend's configured observation-count activation contract.

ByteTrack counts a newborn box as its first successful observation, but its
birth hook emits only unassigned IDs. For a one-observation configuration that
loses current detections until a second match. This adapter changes only that
birth boundary, retaining backend association, timestamps, pruning and allocator.
"""

from __future__ import annotations

import numpy as np
from trackers import ByteTrackTracker


class ObservationCountByteTrack(ByteTrackTracker):
    """Activate eligible newly spawned episodes on the current detection."""

    def _spawn_new_tracks(
        self,
        detection_boxes: np.ndarray,
        confidences: np.ndarray,
        unmatched_high_local: list[int],
        high_indices: np.ndarray,
        out_det_indices: list[int],
        out_tracker_ids: list[int],
    ) -> None:
        first_track, first_output = len(self.tracks), len(out_det_indices)
        super()._spawn_new_tracks(
            detection_boxes,
            confidences,
            unmatched_high_local,
            high_indices,
            out_det_indices,
            out_tracker_ids,
        )
        # The protected backend hook appends each unmatched-high detection in
        # order and creates tracklets only for its existing activation cutoff.
        # Verify that binding explicitly; an incompatible backend must not assign
        # an episode to another detection, including when boxes are duplicates.
        outputs = [
            position
            for position in range(first_output, len(out_det_indices))
            if float(confidences[out_det_indices[position]]) >= self.track_activation_threshold
        ]
        created = self.tracks[first_track:]
        if len(outputs) != len(created):
            raise RuntimeError("ByteTrack birth-output contract changed")
        for position, track in zip(outputs, created, strict=True):
            index = out_det_indices[position]
            if not np.array_equal(track.get_state_bbox(), detection_boxes[index]):
                raise RuntimeError("ByteTrack birth box differs from its current detection")
            if track.tracker_id < 0 and (
                track.number_of_successful_consecutive_updates >= self.minimum_consecutive_frames
            ):
                track.tracker_id = self._allocate_tracker_id()
                out_tracker_ids[position] = track.tracker_id
