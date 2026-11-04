"""Numerical reliability controls; synthetic trajectories are not sporting labels."""

import math

import numpy as np
import pytest

import bai_badminton.events.contact as contact
from bai_badminton.observations import PlayerSeries, WindowObs
from bai_badminton.perception.shuttle_post import Track


def window(before=(0.02, 0), after=(-0.6, 0), *, scale=1.0, count=1):
    xy = np.array([np.array(before) * (i - 4) if i <= 4 else np.array(after) * (i - 4) for i in range(9)]) * scale
    players = {}
    for index in range(count):
        p = PlayerSeries.empty(9)
        p.bbox[:] = np.array([-10, -15, 10, 85]) * scale + np.array([index * 300, 0, index * 300, 0]) * scale
        players[str(index)] = p
    return WindowObs(0, 30, Track.from_arrays(xy[:, 0], xy[:, 1], np.ones(9, bool)), players)


def policy(scale=1.0):
    return contact.ContactMotionReliability(2.5 / math.sqrt(12) * scale)


def test_jitter_no_longer_saturates_motion_evidence():
    w = window()
    legacy = contact.score_frame(w, 4)
    reliable = contact.score_frame(w, 4, motion_reliability=policy())
    assert legacy.p > 0.97
    assert reliable.p < 0.35
    assert reliable.scores["redirect"] == 0
    assert reliable.scores["impulse"] == 0
    assert reliable.model == contact.CONTACT_RELIABILITY_MODEL
    assert legacy.model == contact.CONTACT_MODEL


@pytest.mark.parametrize("outgoing", [2.0, 10.0, 30.0])
def test_zero_incoming_serve_launch_is_not_rejected(outgoing):
    c = contact.score_frame(window(before=(0, 0), after=(outgoing, 0)), 4, motion_reliability=policy())
    assert c is not None and c.p > 0.35
    assert c.scores["incoming_direction_reliability"] == 0
    assert c.scores["impulse"] > 0
    assert all(math.isfinite(x) for x in c.scores.values())


def test_fast_redirect_retains_support():
    c = contact.score_frame(window(before=(12, -2), after=(-14, 3)), 4, motion_reliability=policy())
    assert c is not None and c.p > 0.85


def test_smooth_apex_and_terminal_stop_have_no_unresolved_redirect():
    for vb, va in [((0.6, -0.2), (0.6, 0.2)), ((0.6, 0), (0, 0))]:
        c = contact.score_frame(window(before=vb, after=va), 4, motion_reliability=policy())
        assert c is not None and c.scores["redirect"] == 0
        assert c.p < 0.35


@pytest.mark.parametrize("scale", [0.5, 1.0, 1.5, 2.0])
def test_declared_spatial_scale_preserves_feature_values(scale):
    base = contact.score_frame(window(before=(12, -2), after=(-14, 3)), 4, motion_reliability=policy())
    scaled = contact.score_frame(
        window(before=(12, -2), after=(-14, 3), scale=scale), 4, motion_reliability=policy(scale)
    )
    assert scaled.p == pytest.approx(base.p)
    assert scaled.scores["redirect"] == pytest.approx(base.scores["redirect"])
    assert scaled.scores["impulse"] == pytest.approx(base.scores["impulse"])


@pytest.mark.parametrize("sigma", [0.0, -1.0, math.inf, math.nan])
def test_invalid_sensitivity_scale_is_rejected(sigma):
    with pytest.raises(ValueError):
        contact.ContactMotionReliability(sigma)


def test_four_person_context_is_retained():
    w = window(before=(12, -2), after=(-14, 3), count=4)
    c = contact.score_frame(w, 4, motion_reliability=policy())
    assert c is not None and c.scores["proximity_candidates"] == 4


def test_scene_break_prevents_velocity_leak():
    w = window(before=(12, -2), after=(-14, 3))
    w.break_before[4] = True
    assert contact.score_frame(w, 4, motion_reliability=policy()) is None


def test_interpolation_does_not_become_contact_observation():
    w = window(before=(12, -2), after=(-14, 3))
    w.shuttle.interp[4] = True
    assert contact.score_frame(w, 4, motion_reliability=policy()) is None


def test_missing_endpoints_keep_observed_count():
    w = window(before=(12, -2), after=(-14, 3))
    w.shuttle.vis[[1, 3, 5, 7]] = False
    c = contact.score_frame(w, 4, motion_reliability=policy())
    assert c is not None
    assert c.scores["incoming_fit_samples"] == 2
    assert c.scores["outgoing_fit_samples"] == 2


def test_bad_line_fit_is_not_treated_as_precise_acceleration():
    w = window(before=(0.05, 0), after=(0, 0))
    w.shuttle.x[5:] = [-123, -121, -120, -118]
    w.shuttle.y[5:] = [-355, -344, -330, -310]
    c = contact.score_frame(w, 4, motion_reliability=policy())
    assert c is not None
    assert c.scores["outgoing_slope_sigma_sensitivity"] > 10
    assert c.scores["impulse"] == 0
    assert c.scores["redirect"] == 0


def test_legacy_path_matches_known_numeric_control():
    c = contact.score_frame(window(), 4)
    assert c.p == pytest.approx(0.9781187290638694, abs=1e-15)
    assert "incoming_direction_reliability" not in c.scores


def test_contextual_nms_is_partition_invariant_under_new_policy():
    w = window(before=(12, -2), after=(-14, 3))
    kwargs = dict(enforce_alternation=False, motion_reliability=policy())
    full = contact.detect_contacts(w, **kwargs)
    partition = contact.detect_contacts(w, start=0, stop=4, **kwargs) + contact.detect_contacts(w, start=4, **kwargs)
    assert [c.frame for c in full] == [4]
    assert [c.frame for c in full] == [c.frame for c in partition]


@pytest.mark.parametrize(
    "which", ["all_missing", "incoming_missing", "outgoing_missing", "interpolated_incoming", "excluded_view"]
)
def test_missing_and_invalid_context_abstains(which):
    w = window(before=(12, -2), after=(-14, 3))
    if which == "all_missing":
        w.shuttle.vis[:] = False
    if which == "incoming_missing":
        w.shuttle.vis[:4] = False
    if which == "outgoing_missing":
        w.shuttle.vis[5:] = False
    if which == "interpolated_incoming":
        w.shuttle.interp[:4] = True
    if which == "excluded_view":
        w.replay[4] = True
    assert contact.score_frame(w, 4, motion_reliability=policy()) is None


@pytest.mark.parametrize("index", [0, 8])
def test_no_unavailable_observations_beyond_window_edges(index):
    assert contact.score_frame(window(before=(12, -2), after=(-14, 3)), index, motion_reliability=policy()) is None


def test_score_does_not_consult_future_beyond_declared_local_context():
    n = 35
    center = 17
    xy = np.array(
        [np.array((12, -2)) * (i - center) if i <= center else np.array((-14, 3)) * (i - center) for i in range(n)],
        dtype=float,
    )
    p = PlayerSeries.empty(n)
    p.bbox[:] = [-10, -15, 10, 85]
    w = WindowObs(0, 30, Track.from_arrays(xy[:, 0], xy[:, 1], np.ones(n, bool)), {"anonymous": p})
    original = contact.score_frame(w, center, motion_reliability=policy())
    w.shuttle.x[center + 4 :] = 1e5
    w.shuttle.y[center + 4 :] = -1e5
    w.players["anonymous"].bbox[center + 4 :] = 1e6
    w.players["anonymous"].kps[center + 4 :] = 1e4
    same = contact.score_frame(w, center, motion_reliability=policy())
    assert same.p == original.p
    assert same.scores == original.scores


def test_scale_sensitivity_does_not_relabel_coordinate_bounds():
    # WindowObs has no image dimensions. A large finite coordinate is not
    # automatically out-of-view; scene/visibility authority belongs upstream.
    w = window(before=(12, -2), after=(-14, 3))
    base = contact.score_frame(w, 4, motion_reliability=policy())
    w.shuttle.x += 2000
    w.shuttle.y += 3000
    w.players["0"].bbox += np.array([2000, 3000, 2000, 3000])
    c = contact.score_frame(w, 4, motion_reliability=policy())
    assert c.p == pytest.approx(base.p)
    w.replay[:] = True  # explicit analysis-excluded context must still abstain
    assert contact.score_frame(w, 4, motion_reliability=policy()) is None


def test_nonfinite_raw_position_does_not_become_valid_contact():
    w = window(before=(12, -2), after=(-14, 3))
    x = w.shuttle.x.copy()
    x[4] = np.nan
    w.shuttle = Track.from_arrays(x, w.shuttle.y, w.shuttle.vis)
    assert contact.score_frame(w, 4, motion_reliability=policy()) is None


def test_new_policy_nms_keeps_close_contacts_in_separate_scenes():
    n = 16
    x = np.array(
        [
            12 * (i - 6) if i <= 6 else -14 if i == 7 else 12 * (i - 8) if i <= 10 else 24 - 14 * (i - 10)
            for i in range(n)
        ],
        dtype=float,
    )
    y = np.zeros(n)
    p = PlayerSeries.empty(n)
    p.bbox[:] = [-10, -15, 10, 85]
    breaks = np.zeros(n, bool)
    breaks[8] = True
    w = WindowObs(0, 30, Track.from_arrays(x, y, np.ones(n, bool)), {"anonymous": p}, break_before=breaks)
    hits = contact.detect_contacts(w, enforce_alternation=False, motion_reliability=policy())
    assert [x.frame for x in hits] == [6, 10]
