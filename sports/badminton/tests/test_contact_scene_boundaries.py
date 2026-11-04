"""Contact cues must not combine frames from different camera/replay segments."""

import numpy as np
import pytest

import bai_badminton.events.contact as contact
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.participant_contact import participant_window
from bai_badminton.perception.keypoints import KP
from bai_badminton.perception.shuttle_post import Track


def _window(*, breaks=None, replay=None):
    x = np.array([40, 60, 80, 100, 100, 100, 100], dtype=float)
    y = np.array([100, 100, 100, 100, 120, 140, 160], dtype=float)
    return WindowObs(
        frame0=0,
        fps=30.0,
        shuttle=Track.from_arrays(x, y, np.ones(len(x), dtype=bool)),
        players={},
        replay=np.zeros(len(x), dtype=bool) if replay is None else replay,
        break_before=breaks,
    )


def test_shot_boundary_prevents_cross_shot_velocity_fit():
    baseline = _window()
    assert contact.score_frame(baseline, 3) is not None

    breaks = np.zeros(7, dtype=bool)
    breaks[3] = True
    window = _window(breaks=breaks)
    assert contact.score_frame(window, 3) is None  # no incoming same-shot velocity
    assert contact.score_frame(window, 4) is not None  # sufficient same-shot samples


def test_replay_boundaries_apply_without_an_explicit_shot_mask():
    replay = np.array([False, False, False, True, True, False, False])
    window = _window(replay=replay)
    assert window.break_before.tolist() == [False, False, False, True, False, True, False]
    assert contact.score_frame(window, 2) is None  # no post-contact sample before replay
    assert contact.score_frame(window, 3) is None  # replay never produces a contact
    assert contact.score_frame(window, 5) is None  # no pre-contact sample after replay


def test_wrist_speed_does_not_use_pose_from_a_previous_shot():
    x = np.array([0, 10, 20, 30, 40, 80, 90, 100, 100, 100], dtype=float)
    y = np.array([100, 100, 100, 100, 100, 100, 100, 100, 110, 120], dtype=float)
    breaks = np.zeros(10, dtype=bool)
    breaks[5] = True
    player = PlayerSeries.empty(10)
    player.bbox[:] = [90, 85, 110, 185]
    player.kps[:, KP.L_WRIST] = [100, 100, 1]
    player.kps[3, KP.L_WRIST] = [40, 100, 1]
    player.kps[4, KP.L_WRIST] = [80, 100, 1]
    window = WindowObs(0, 30, Track.from_arrays(x, y, np.ones(10, bool)), {"P1": player}, break_before=breaks)
    candidate = contact.score_frame(window, 7)
    assert candidate is not None
    assert candidate.scores["swing"] == 0.0


def test_nms_and_same_player_suppression_do_not_cross_segments(monkeypatch):
    n = 16
    track = Track.from_arrays(np.arange(n, dtype=float), np.zeros(n), np.ones(n, bool))
    breaks = np.zeros(n, dtype=bool)
    breaks[8] = True
    window = WindowObs(0, 30, track, {}, break_before=breaks)
    candidates = {
        i: contact.ContactCandidate(frame=i, player_id="P1", p=p)
        for i, p in ((6, 0.8), (10, 0.9))
    }
    monkeypatch.setattr(contact, "score_frame", lambda _window, i: candidates.get(i))
    assert [c.frame for c in contact.detect_contacts(window, nms_s=0.3)] == [6, 10]
    continuous = WindowObs(0, 30, track, {})
    assert [c.frame for c in contact.detect_contacts(continuous, nms_s=0.3)] == [10]


@pytest.mark.parametrize("invalid", [np.zeros(6, bool), np.zeros((7, 1), bool), np.zeros(7, int)])
def test_boundary_mask_must_be_boolean_and_aligned(invalid):
    with pytest.raises(ValueError, match="break_before"):
        _window(breaks=invalid)


def test_participant_window_preserves_scene_boundaries():
    breaks = np.zeros(7, dtype=bool)
    breaks[3] = True
    source = _window(breaks=breaks)
    visual = participant_window(source, [{} for _ in range(source.n)])
    assert visual.break_before.tolist() == source.break_before.tolist()
    assert contact.score_frame(visual, 3) is None


def test_combining_replay_boundaries_does_not_mutate_caller_mask():
    breaks = np.zeros(7, dtype=bool)
    replay = np.array([False, False, False, True, True, False, False])
    window = _window(breaks=breaks, replay=replay)
    assert not breaks.any()
    assert window.break_before.tolist() == [False, False, False, True, False, True, False]
