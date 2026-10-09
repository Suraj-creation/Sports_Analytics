import numpy as np
import pytest

from bai_badminton.court import CalibrationError, fit_homography, in_court, zone
from bai_badminton.events.contact import detect_contacts
from bai_badminton.events.rally_fsm import RallyParams, segment_offline
from bai_badminton.events.rally_outcome import CourtImageGeometry, Outcome, analyze_rally_end
from bai_badminton.events.stroke import RuleStrokeClassifier, StrokeContext, assess_smash, jump_features
from bai_badminton.ontology import get_ontology
from bai_badminton.perception.keypoints import FLIP, KP, lr_consistency_fix
from bai_badminton.perception.shuttle_post import Track, fill_gaps, remove_spikes
from bai_badminton.testing.synth import broadcast_homography, make_rally


# ------------------------------------------------------------------ court
def test_homography_roundtrip_and_ransac() -> None:
    h = broadcast_homography()
    assert h.reprojection_error_px < 1e-3
    court = np.array([[0.0, 0.0], [2.0, -3.0], [-1.5, 5.5]])
    back = h.image_to_court(h.court_to_image(court))
    assert np.allclose(back, court, atol=1e-6)
    # RANSAC rejects one corrupted point
    pts = {
        n: tuple(h.court_to_image(np.array([c]))[0])
        for n, c in [
            ("far_left", (-3.05, 6.7)),
            ("far_right", (3.05, 6.7)),
            ("near_right", (3.05, -6.7)),
            ("near_left", (-3.05, -6.7)),
            ("net_left", (-3.05, 0.0)),
            ("net_right", (3.05, 0.0)),
        ]
    }
    pts["net_right"] = (pts["net_right"][0] + 80, pts["net_right"][1] - 40)
    h2 = fit_homography(pts)  # type: ignore[arg-type]
    assert h2.n_points == 5 and h2.reprojection_error_px < 1.0


def test_calibration_errors() -> None:
    with pytest.raises(CalibrationError):
        fit_homography({"far_left": (0, 0), "far_right": (1, 0), "near_left": (0, 1)})
    with pytest.raises(CalibrationError):
        fit_homography(
            {"bogus": (0, 0), "far_left": (0, 0), "far_right": (1, 0), "near_left": (0, 1), "near_right": (1, 1)}
        )


def test_zones_and_in_court() -> None:
    assert zone(0.0, -1.0) == ("front", "centre")
    assert zone(2.0, -6.0) == ("rear", "right")  # near player's right is +x
    assert zone(2.0, 6.0) == ("rear", "left")  # far player faces the other way
    assert in_court(2.5, 6.6) and not in_court(2.8, 0.0)  # singles width 5.18
    assert in_court(2.8, 0.0, singles=False)


# ------------------------------------------------------------------ keypoints / ontology
def test_keypoint_indices_are_coco() -> None:
    assert (KP.L_WRIST, KP.R_WRIST, KP.L_ANKLE, KP.R_ANKLE) == (9, 10, 15, 16)
    assert sorted(FLIP) == list(range(17))


def test_lr_swap_fix() -> None:
    prev = np.zeros((17, 3), np.float32)
    prev[:, 0] = np.arange(17) * 10
    prev[:, 2] = 1
    swapped = prev[list(FLIP)].copy()
    fixed = lr_consistency_fix(swapped, prev)
    assert np.allclose(fixed, prev)


def test_ontology_mapping() -> None:
    ont = get_ontology()
    assert ont.normalize_stroke("Top wrist smash") == "smash"
    assert ont.normalize_stroke("bottom_short service") == "short_serve"
    assert ont.normalize_stroke("kill", source="finebadminton") == "smash"
    assert ont.normalize_stroke("net_shot", source="legacy") == "net_shot"
    assert ont.normalize_stroke("???") == "unknown"
    assert ont.band(0.9).value == "confirmed"


# ------------------------------------------------------------------ shuttle post
def test_spike_removal_and_gap_fill() -> None:
    n = 40
    x = np.linspace(100, 500, n)
    y = np.linspace(600, 300, n)
    vis = np.ones(n, bool)
    x[10] += 400  # spike
    vis[20:26] = False  # occlusion gap
    t = remove_spikes(Track.from_arrays(x, y, vis))
    assert not t.vis[10]
    f = fill_gaps(t)
    assert f.vis[20:26].all() and f.interp[20:26].all()
    assert np.allclose(f.x[20:26], np.linspace(100, 500, n)[20:26], atol=1.0)
    assert f.vis[10]  # single-frame gap after spike also filled


def test_gap_fill_gates() -> None:
    n = 80
    x = np.full(n, 300.0)
    y = np.full(n, 500.0)
    vis = np.ones(n, bool)
    vis[30:40] = False
    stationary = fill_gaps(Track.from_arrays(x, y, vis))
    assert not stationary.vis[30:40].any()  # stationary shuttle on the floor is not bridged
    x2 = np.linspace(0, 800, n)
    vis2 = np.ones(n, bool)
    vis2[10:50] = False  # too long
    assert not fill_gaps(Track.from_arrays(x2, y, vis2)).vis[10:50].any()


# ------------------------------------------------------------------ contact
def test_contacts_on_synthetic_rally() -> None:
    r = make_rally(n_shots=6)
    found = detect_contacts(r.obs)
    gt = r.contacts
    matched = 0
    for f, p in gt:
        hits = [c for c in found if abs(c.frame - f) <= 3]
        if hits:
            matched += 1
            assert hits[0].player_id == p, (f, p, hits[0])
    assert matched >= len(gt) - 1  # the serve (no incoming flight) may be missed by redirect cue
    # no spurious contacts far from any ground-truth contact or the landing
    for c in found:
        assert min(abs(c.frame - f) for f, _ in gt + [(r.landing_frame, "")]) <= 4, c
    # alternation holds
    pids = [c.player_id for c in found if c.player_id]
    assert all(a != b for a, b in zip(pids, pids[1:], strict=False))


def test_contact_evidence_components_present() -> None:
    r = make_rally(n_shots=4)
    c = detect_contacts(r.obs)[0]
    assert {"redirect", "impulse", "proximity", "swing"} <= set(c.components)
    assert 0 <= c.p <= 1


# ------------------------------------------------------------------ rally FSM
def test_rally_segmentation_with_contacts() -> None:
    r = make_rally(n_shots=6, lead_in=40, tail=80)
    t = r.obs.shuttle
    spd = np.zeros(len(t))
    spd[1:] = np.nan_to_num(np.hypot(np.diff(t.x), np.diff(t.y)))
    frames = list(range(len(t)))
    segs = segment_offline(frames, list(t.vis), list(spd), RallyParams(fps=30), contacts={f for f, _ in r.contacts})
    assert len(segs) == 1
    s = segs[0]
    assert s.serve_frame == r.contacts[0][0]
    assert abs(s.start - r.start_frame) <= 2
    assert abs(s.end - r.landing_frame) <= 12


def test_rally_too_short_is_dropped_and_gaps_merge() -> None:
    p = RallyParams(fps=30)
    frames = list(range(400))
    vis = [False] * 400
    spd = [0.0] * 400
    for i in range(50, 70):  # 20 frames < 2 s
        vis[i], spd[i] = True, 10.0
    for i in list(range(150, 220)) + list(range(232, 300)):  # 12-frame gap (< merge 22) inside a long rally
        vis[i], spd[i] = True, 10.0
    segs = segment_offline(frames, vis, spd, p)
    assert len(segs) == 1
    assert segs[0].start == 150 and segs[0].end >= 290


def test_replay_ends_rally() -> None:
    p = RallyParams(fps=30)
    n = 300
    vis = [True] * n
    spd = [10.0] * n
    replay = [False] * 150 + [True] * 150
    segs = segment_offline(list(range(n)), vis, spd, p, replay=replay)
    assert len(segs) == 1 and segs[0].reason == "cut" and segs[0].end == 149


# ------------------------------------------------------------------ outcome
def _geom(h: object) -> CourtImageGeometry:
    return CourtImageGeometry.from_homography(h)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("land", "expected_outcome", "expected_fault"),
    [
        ((1.0, -4.0), Outcome.WINNER, "near"),  # lands in near half → near player failed to return
        ((0.5, 4.5), Outcome.WINNER, "far"),
        ((1.0, -7.6), Outcome.OUT, "far"),  # past the near baseline → far player hit it out
    ],
)
def test_outcome_cascade(land: tuple[float, float], expected_outcome: Outcome, expected_fault: str) -> None:
    n_shots = 5 if land[1] < 0 else 6  # last hitter must be the far player for a near landing
    r = make_rally(n_shots=n_shots, land_court=land)
    t = r.obs.shuttle
    g = _geom(r.homography)
    res = analyze_rally_end(r.obs.frames, t.x, t.y, t.vis, r.landing_frame + 10, g, 30.0)
    assert res.outcome is expected_outcome, res
    assert res.fault == expected_fault, res


# ------------------------------------------------------------------ stroke / smash / jump
def test_rule_classifier_cases() -> None:
    clf = RuleStrokeClassifier()
    base = dict(frame=0, player_id="P1", hitter_side="near", vy_after_px_s=None, frame_height_px=720.0)
    serve = clf.predict(
        StrokeContext(
            is_serve=True,
            hitter_court_xy=(0.3, -2.2),
            speed_after_px_s=400,
            flight_time_s=0.5,
            contact_above_head=False,
            **base,
        )
    )  # type: ignore[arg-type]
    assert serve.top[0] == "short_serve" and serve.top[1] <= 0.7
    smash = clf.predict(
        StrokeContext(
            is_serve=False,
            hitter_court_xy=(0.0, -6.0),
            speed_after_px_s=2400,
            flight_time_s=0.4,
            contact_above_head=True,
            **base,
        )
    )  # type: ignore[arg-type]
    assert smash.top[0] == "smash"
    clear = clf.predict(
        StrokeContext(
            is_serve=False,
            hitter_court_xy=(0.0, -6.0),
            speed_after_px_s=800,
            flight_time_s=1.4,
            contact_above_head=True,
            **base,
        )
    )  # type: ignore[arg-type]
    assert clear.top[0] == "clear"
    net = clf.predict(
        StrokeContext(
            is_serve=False,
            hitter_court_xy=(0.0, -1.5),
            speed_after_px_s=300,
            flight_time_s=0.8,
            contact_above_head=False,
            **base,
        )
    )  # type: ignore[arg-type]
    assert net.top[0] == "net_shot"
    assert abs(sum(net.probs.values()) - 1) < 1e-9


def test_jump_smash_evidence() -> None:
    r = make_rally(n_shots=5, jump_at_shot=2)
    cf, pid = r.contacts[2]
    s = r.obs.players[pid]
    ank = s.kps[:, [KP.L_ANKLE, KP.R_ANKLE], 1]
    hips = s.kps[:, [KP.L_HIP, KP.R_HIP], 1].mean(axis=1)
    feats = jump_features(ank, hips, s.height, cf)
    assert feats is not None and feats["lift_min"] > 0.1
    a = assess_smash(0.9, 2400, 720, True, feats)
    assert a.p_smash > 0.8 and a.p_jump is not None and a.p_jump > 0.7
    # a grounded smash
    cf0, pid0 = r.contacts[0]
    s0 = r.obs.players[pid0]
    f0 = jump_features(
        s0.kps[:, [KP.L_ANKLE, KP.R_ANKLE], 1], s0.kps[:, [KP.L_HIP, KP.R_HIP], 1].mean(axis=1), s0.height, cf0 + 30
    )
    assert f0 is not None
    a0 = assess_smash(0.9, 2400, 720, True, f0)
    assert a0.p_jump is not None and a0.p_jump < 0.2
