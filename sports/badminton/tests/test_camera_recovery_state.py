"""Camera-loss behaviour is independent of perception chunk boundaries."""

import numpy as np

from bai_badminton.perception.camera import CameraTracker


def test_held_pose_expires_across_chunks(monkeypatch):
    rng = np.random.default_rng(123)
    frame = rng.integers(0, 255, (200, 320, 3), dtype=np.uint8)
    tracker = CameraTracker(work_width=320, max_hold=2)
    assert tracker.set_reference(frame) is not None
    attempts = iter([np.eye(3), None, None, None, None, None, None])
    monkeypatch.setattr(tracker, "_anchor", lambda gray, guess: next(attempts, None))
    monkeypatch.setattr(tracker, "_align", lambda *args: None)
    monkeypatch.setattr(tracker, "_step", lambda *args: None)
    monkeypatch.setattr(tracker, "_unchanged", lambda *args: False)
    assert tracker.track([frame], [False], 0)[0] is not None
    held = tracker.track([frame, frame], [False, False], 1)
    assert all(p is not None for p in held)
    assert tracker.track([frame], [False], 3)[0] is None
