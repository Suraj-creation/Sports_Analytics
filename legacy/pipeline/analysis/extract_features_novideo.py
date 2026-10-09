"""
extract_features_novideo.py
===========================
Badminton rally feature extraction — NO VIDEO REQUIRED.
Reads court geometry directly from your court.json (1280x720).

KEY FACTS from data analysis:
  player_1_y avg ≈ 558px  → NEAR player (close to court_bottom 655px)
  player_2_y avg ≈ 368px  → FAR player  (far from court_bottom)
  FAR player = Player A (top of image, small Y)
  NEAR player = Player B (bottom of image, large Y)

  net_top_Y (cable) = 306px = actual net barrier
  net_ground_Y      = 430px = ground reference only

  Shuttle Y < 306  → above cable → crossed net → wins_by_landing
  Shuttle Y >= 306 → at/below cable → hits_net
"""

import os, sys, json, math, argparse
import numpy as np
import pandas as pd
import cv2

if sys.stdout.encoding is None or sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")

ANALYSIS_SEC     = 3.0
HIGH_SPEED       = 350
MED_SPEED        = 150
RELIABLE_SPD_MIN = 40

_WIN_STR  = {
    'out_of_bounds':   'opponent goes out of bounds',
    'hits_net':        'opponent hits the net',
    'wins_by_landing': 'wins_by_landing',
    'unknown':         'unknown'
}
_LOSE_STR = {
    'out_of_bounds':   'goes out of bounds',
    'hits_net':        'hits the net',
    'wins_by_landing': 'opponent wins by landing',
    'unknown':         'unknown'
}


# ══════════════════════════════════════════════════════════════
# STEP 1 — LOAD COURT GEOMETRY
# ══════════════════════════════════════════════════════════════

def load_court_from_json(path: str) -> dict:
    with open(path) as f:
        ann = json.load(f)

    corners = ann["corners"]
    net     = ann["net"]

    TL = corners["TL"];  TR = corners["TR"]
    BR = corners["BR"];  BL = corners["BL"]

    # net_top_Y = cable = actual barrier
    if "net_top_Y" in net:
        net_top_Y = float(net["net_top_Y"])
    else:
        cl = net["cable_left"];  cr = net["cable_right"]
        net_top_Y = float((cl[1] + cr[1]) / 2)

    # net_ground_Y = ground reference line (left_bottom/right_bottom)
    # left_bottom/right_bottom also give the net's actual horizontal span --
    # narrower than the full court width, since net posts sit inside the
    # doubles sidelines. A shuttle near net_ground_Y in depth but outside
    # this X span (e.g. near a sideline) cannot physically have hit the
    # net -- needed because net_top_Y collapses almost onto the far
    # baseline in this camera's perspective (see net_top_Y/court_top_y
    # below), so depth alone doesn't reliably distinguish "near the net"
    # from "near the far baseline."
    if "net_Y" in net:
        net_ground_Y = float(net["net_Y"])
    else:
        lb = net["left_bottom"];  rb = net["right_bottom"]
        net_ground_Y = float((lb[1] + rb[1]) / 2)

    if "left_bottom" in net and "right_bottom" in net:
        net_x_min = float(min(net["left_bottom"][0], net["right_bottom"][0]))
        net_x_max = float(max(net["left_bottom"][0], net["right_bottom"][0]))
    else:
        net_x_min = float(min(TL[0], BL[0]))
        net_x_max = float(max(TR[0], BR[0]))

    court_top_y    = min(TL[1], TR[1])
    court_bottom_y = max(BL[1], BR[1])
    net_tol_px     = 720 * 0.020   # ~18px

    court_corners = np.float32([TL, TR, BR, BL])
    court_poly_cv = court_corners.reshape(-1, 1, 2)

    print(f"  Court loaded:")
    print(f"    TL={[round(x,1) for x in TL]}  TR={[round(x,1) for x in TR]}")
    print(f"    BL={[round(x,1) for x in BL]}  BR={[round(x,1) for x in BR]}")
    print(f"    net_top_Y={net_top_Y:.1f} (cable=barrier)  "
          f"net_ground_Y={net_ground_Y:.1f} (reference)")
    print(f"    court_top={court_top_y:.1f}  court_bottom={court_bottom_y:.1f}")

    return {
        "TL": TL, "TR": TR, "BR": BR, "BL": BL,
        "corners":        court_corners,
        "court_poly_cv":  court_poly_cv,
        "net_top_Y":      net_top_Y,
        "net_ground_Y":   net_ground_Y,
        "net_x_min":      net_x_min,
        "net_x_max":      net_x_max,
        "net_tol_px":     net_tol_px,
        "court_top_y":    court_top_y,
        "court_bottom_y": court_bottom_y,
    }


# ══════════════════════════════════════════════════════════════
# STEP 2 — PLAYER SIDE ASSIGNMENT
#
# Uses court_bottom_y (from left_bottom/right_bottom annotation)
# as the near baseline reference.
#
# Player whose centre Y is CLOSEST to court_bottom_y = NEAR = Player B
# Player whose centre Y is FARTHEST from court_bottom_y = FAR  = Player A
#
# From data: player_1 avg_y≈558 (near), player_2 avg_y≈368 (far)
# → far_slot = player_2, near_slot = player_1
#
# IMPORTANT: FAR player is ALWAYS Player A regardless of slot number.
# ══════════════════════════════════════════════════════════════

def assign_player_sides(player_csv: str, court: dict):
    df   = pd.read_csv(player_csv)
    avg1 = df['player_1_y'].dropna().mean()
    avg2 = df['player_2_y'].dropna().mean()

    near_baseline_Y = court["court_bottom_y"]
    dist1 = abs(avg1 - near_baseline_Y)
    dist2 = abs(avg2 - near_baseline_Y)

    if dist1 < dist2:
        # player_1 closer to near baseline → NEAR → Player B
        far_slot, near_slot = 'player_2', 'player_1'
        far_avg,  near_avg  = avg2, avg1
    else:
        # player_2 closer to near baseline → NEAR → Player B
        far_slot, near_slot = 'player_1', 'player_2'
        far_avg,  near_avg  = avg1, avg2

    print(f"  near_baseline_Y={near_baseline_Y:.0f}px")
    print(f"  FAR  slot={far_slot}  avg_y={far_avg:.0f}px  "
          f"dist={abs(far_avg-near_baseline_Y):.0f}px → Player A")
    print(f"  NEAR slot={near_slot}  avg_y={near_avg:.0f}px  "
          f"dist={abs(near_avg-near_baseline_Y):.0f}px → Player B")

    return far_slot, near_slot


# ══════════════════════════════════════════════════════════════
# STEP 2b — PLAYER POSITIONS AT END FRAME
# ══════════════════════════════════════════════════════════════

def extract_player_features(player_df, end_frame, far_slot, window=10):
    nearby = player_df[
        (player_df['frame_no'] >= end_frame - window) &
        (player_df['frame_no'] <= end_frame)
    ]
    if nearby.empty:
        return {'far_cx': None, 'far_cy': None,
                'near_cx': None, 'near_cy': None,
                'far_bottom': None, 'near_bottom': None}

    last = nearby.iloc[-1]
    if far_slot == 'player_1':
        far_cx,  far_cy  = float(last['player_1_x']), float(last['player_1_y'])
        near_cx, near_cy = float(last['player_2_x']), float(last['player_2_y'])
    else:
        far_cx,  far_cy  = float(last['player_2_x']), float(last['player_2_y'])
        near_cx, near_cy = float(last['player_1_x']), float(last['player_1_y'])

    BBOX_HALF_H = 50
    return {
        'far_cx':     round(far_cx,  1),
        'far_cy':     round(far_cy,  1),
        'far_bottom': round(far_cy  + BBOX_HALF_H, 1),
        'near_cx':    round(near_cx, 1),
        'near_cy':    round(near_cy, 1),
        'near_bottom':round(near_cy + BBOX_HALF_H, 1),
    }


# ══════════════════════════════════════════════════════════════
# STEP 3 — RALLY END EVENT DETECTION
#
# Priority order:
#   0. Shuttle stationary   → most reliable
#   1. Cable crossing       → shuttle passes net_top_Y and continues = wins_by_landing
#   2. At cable + stopping  → hits_net
#   3. OOB extrapolation    → shuttle exits court boundary
#   4. Baseline proximity   → shuttle near baseline and moving out
#   5. Above cable in court → wins_by_landing
#   6. OOB fallback
#   7. Final fallback       → wins_by_landing
# ══════════════════════════════════════════════════════════════

def _frame_col(df):
    for c in ("Frame","frame_no","frame","index"):
        if c in df.columns: return c
    raise ValueError(f"No frame column. Columns: {list(df.columns)}")


def _fault_side(vx, vy, prev_y, net_top_Y):
    """
    Determine which player hit the shuttle last (who is at fault).
    vy > 0 = shuttle moving down (toward near baseline) = far player hit it
    vy < 0 = shuttle moving up (toward far baseline) = near player hit it
    """
    if abs(vx) > abs(vy):
        return 'near' if prev_y > net_top_Y else 'far'
    return 'far' if vy > 0 else 'near'


def _oob_fault_side(last_y, court, net_ground_Y):
    """
    Determine OOB fault side using all 4 court boundary lines + net_ground_Y.

    Which boundary was crossed tells us who hit it last:
      Y > court_bottom_y  → past NEAR baseline → far player hit it  → fault='far'  → Player B wins
      Y < court_top_y     → past FAR baseline  → near player hit it → fault='near' → Player A wins
      between baselines   → sideline exit; use net_ground_Y depth divider:
          Y > net_ground_Y → NEAR-half sideline → far player  → fault='far'
          Y < net_ground_Y → FAR-half sideline  → near player → fault='near'
    """
    if last_y > court['court_bottom_y']:
        return 'far'
    if last_y < court['court_top_y']:
        return 'near'
    return 'far' if last_y > net_ground_Y else 'near'


def _hits_net_fault(last_y, net_mid_Y):
    """
    Landing-side fallback for hits_net fault detection.
    Used when the approach-velocity method cannot determine direction.
    """
    return 'near' if last_y < net_mid_Y else 'far'


def _near_net_x(x, net_x_min, net_x_max, tol):
    """Is x within the net's actual horizontal span (+ tolerance)? The net
    posts sit inside the doubles sidelines, so this is narrower than the
    full court width -- a shuttle near net_ground_Y in depth but past a
    sideline cannot physically have hit the net."""
    return net_x_min - tol <= x <= net_x_max + tol


def _extrapolate_exit(lx, ly, vx, vy, court_poly, fps, line_tol=0.0, max_frames=45):
    # A line belongs to the court it bounds (real badminton rule) -- only
    # call it an exit once the point is more than line_tol past the edge.
    dt = 1.0 / fps
    for t in range(1, max_frames + 1):
        ex = float(lx + vx * dt * t)
        ey = float(ly + vy * dt * t)
        if cv2.pointPolygonTest(court_poly, (ex, ey), True) < -line_tol:
            return True, (ex, ey)
    return False, None


def _smoothed_velocities(pos, fps, win=3):
    """Rolling-average velocity over `win` frames, far less sensitive to
    single-frame pixel jitter than raw frame-to-frame deltas -- needed
    because soft net taps move only a few px/frame, where noise and
    signal are the same order of magnitude."""
    out = []
    for i in range(win, len(pos)):
        f0,x0,y0 = pos[i-win]
        f1,x1,y1 = pos[i]
        dt = (f1-f0)/fps
        if dt <= 0:
            out.append((0.0,0.0,i)); continue
        out.append(((x1-x0)/dt, (y1-y0)/dt, i))
    return out


def _last_hit_index(pos, fps, win=3, angle_thresh_deg=60, min_disp=8):
    """Find the most recent index where the smoothed velocity direction
    changes sharply -- a racket redirect, soft or hard. Smoothing over
    `win` frames (rather than comparing raw single-frame deltas) keeps
    this sensitive to slow net taps without being dominated by pixel
    jitter. min_disp filters out windows too short to have a meaningful
    direction at all."""
    svels = _smoothed_velocities(pos, fps, win)
    last_hit = 0
    for i in range(1, len(svels)):
        ax,ay,_ = svels[i-1]; bx,by,idx = svels[i]
        na = math.hypot(ax,ay); nb = math.hypot(bx,by)
        if na*(win/fps) < min_disp or nb*(win/fps) < min_disp:
            continue
        cos_ang = (ax*bx+ay*by)/(na*nb)
        cos_ang = max(-1.0, min(1.0, cos_ang))
        ang = math.degrees(math.acos(cos_ang))
        if ang > angle_thresh_deg:
            last_hit = idx
    return last_hit


def analyze_rally_end(shuttle_df, end_frame, court, fps, player_feats=None):
    fc           = _frame_col(shuttle_df)
    N            = int(fps * ANALYSIS_SEC)
    net_top_Y    = court["net_top_Y"]
    net_ground_Y = court["net_ground_Y"]
    net_mid_Y    = (net_top_Y + net_ground_Y) / 2   # ~368px — landing-side divider
    net_x_min    = court["net_x_min"]
    net_x_max    = court["net_x_max"]
    net_tol_px   = court["net_tol_px"]
    court_poly   = court["court_poly_cv"]
    corners      = court["corners"]

    # Tried extending the window past end_frame (FORWARD_SEC, 1.0 and 1.5
    # both tested) on the theory that the labeled end_time's second-level
    # precision often cuts off a still-falling shuttle -- A/B tested,
    # severe regression both times (64.9% -> 53.4% / 50.4% win-reason):
    # out_of_bounds recall collapsed (67% -> 45%), because shuttles that
    # are genuinely out keep moving/rolling further away from the court
    # after exiting, so looking further forward gives a WORSE read on
    # where they actually landed, not a better one. Reverted to the
    # original backward-only window.
    win = shuttle_df[
        (shuttle_df[fc] >= end_frame - N) &
        (shuttle_df[fc] <= end_frame) &
        (shuttle_df['Visibility'] == 1)
    ].sort_values(fc)

    if len(win) < 3:
        return 'unknown', 'unknown', 'LOW', {}

    conf = 'HIGH' if len(win) >= 10 else 'MEDIUM'
    pos  = list(zip(win[fc].values, win['X'].values, win['Y'].values))

    vels = []
    for i in range(1, len(pos)):
        f0,x0,y0 = pos[i-1];  f1,x1,y1 = pos[i]
        dt = (f1-f0)/fps
        if dt <= 0: continue
        vx,vy = (x1-x0)/dt,(y1-y0)/dt
        vels.append({'vx':vx,'vy':vy,'speed':math.hypot(vx,vy),'x':x1,'y':y1})

    if not vels:
        return 'unknown', 'unknown', 'LOW', {}

    last_x = float(pos[-1][1])
    last_y = float(pos[-1][2])
    prev_y = float(pos[-4][2]) if len(pos) >= 4 else float(pos[0][2])

    all_spd    = [v['speed'] for v in vels]
    mid_all    = max(1, len(all_spd)//2)
    decel_rate = (np.mean(all_spd[:mid_all]) - np.mean(all_spd[mid_all:])) / \
                  max(np.mean(all_spd[:mid_all]), 1.0)

    reliable   = [v for v in vels if v['speed'] > RELIABLE_SPD_MIN] or vels
    mid        = max(1, len(reliable)//2)
    early_vels = reliable[:mid]
    pred_vx    = float(np.mean([v['vx']    for v in early_vels]))
    pred_vy    = float(np.mean([v['vy']    for v in early_vels]))
    pred_speed = float(np.mean([v['speed'] for v in early_vels]))
    last_few   = reliable[-3:] if len(reliable) >= 3 else reliable
    fault_vx   = float(np.mean([v['vx'] for v in last_few]))
    fault_vy   = float(np.mean([v['vy'] for v in last_few]))
    rel_x      = float(next((v['x'] for v in reversed(vels)
                             if v['speed'] > RELIABLE_SPD_MIN), last_x))
    rel_y      = float(next((v['y'] for v in reversed(vels)
                             if v['speed'] > RELIABLE_SPD_MIN), last_y))

    feats = dict(
        speed=pred_speed, vx=pred_vx, vy=pred_vy,
        last_y=last_y, contact_y=rel_y,
        net_top_Y=net_top_Y, net_ground_Y=net_ground_Y,
        net_tol_px=net_tol_px, decel_rate=decel_rate,
        early_speed=float(np.mean([v['speed'] for v in early_vels])),
        analysis_start_frame=int(pos[0][0]),
        analysis_end_frame=int(pos[-1][0])
    )

    # Tried using the last-hit segment's velocity DIRECTION as the OOB
    # fault signal (instead of _fault_side() below) on the theory that
    # it's more reliable for wide/sideline shots -- A/B tested, it was a
    # clear regression on winner accuracy (58.0% -> 53.4%), so NOT adopted.
    # final_seg is still needed below for the net-related checks
    # (hits_net/wins_by_landing).
    last_hit_idx = _last_hit_index(pos, fps)
    final_seg    = pos[last_hit_idx:]

    # Which side was the shuttle on at the last detected hit?
    # 'far'  → FAR player hit it last  (y < net_top_Y)
    # 'near' → NEAR player hit it last (y ≥ net_top_Y)
    feats['last_hit_side'] = (
        'far' if final_seg and float(final_seg[0][2]) < net_top_Y else 'near'
    )

    # ── Hits-net fault side from approach velocity ────────────
    # For net faults the shuttle may bounce off the tape and land on the
    # same side it was hit from, making last_y an unreliable fault signal.
    # Instead: find the frame in final_seg closest to the cable (net_top_Y)
    # and look at vy just BEFORE it — negative vy (going toward FAR) means
    # Player B hit it → fault='near'; positive vy means Player A → 'far'.
    # Falls back to the landing-side rule if the cable never comes close.
    _net_fault = _hits_net_fault(last_y, net_mid_Y)  # default fallback
    if len(final_seg) >= 3:
        _nc_i, _nc_dist = 0, float('inf')
        for _i, (_f, _x, _y) in enumerate(final_seg):
            _d = abs(_y - net_top_Y)
            if _d < _nc_dist:
                _nc_dist, _nc_i = _d, _i
        if _nc_i > 0 and _nc_dist < 80:
            _approach_vys = []
            for _j in range(max(0, _nc_i - 4), _nc_i):
                if _j + 1 < len(final_seg):
                    _p0, _p1 = final_seg[_j], final_seg[_j + 1]
                    _dt = (_p1[0] - _p0[0]) / fps
                    if _dt > 0:
                        _approach_vys.append((_p1[2] - _p0[2]) / _dt)
            if _approach_vys and abs(float(np.mean(_approach_vys))) > 20:
                _net_fault = 'near' if float(np.mean(_approach_vys)) < 0 else 'far'
    feats['net_fault'] = _net_fault  # expose for extract_T4_exp.py overrides

    # Also tried combining last-hit POSITION (which side of the net the
    # shuttle was on at the moment of the last hit) with landing side as
    # the OOB fault signal -- A/B tested, also a regression (59.5% ->
    # 55.0% winner accuracy), so also NOT adopted. _fault_side() (defined
    # above) remains the OOB fault signal everywhere below.

    # ── CHECK 0: Shuttle stationary ───────────────────────────
    # A stationary shuttle has LANDED — its image Y is a floor position,
    # so "near the net" must be judged against net_ground_Y (the net's
    # floor footprint), not net_top_Y (the elevated cable's image Y,
    # which sits almost on top of the far baseline in this camera's
    # perspective and is meaningless for a grounded point).
    # A line belongs to the court it bounds (real badminton rule) -- a
    # point within net_tol_px of the boundary still counts as in bounds.
    static = [v for v in vels[-6:] if v['speed'] < 15]
    if len(static) >= 3:
        gx = float(np.mean([v['x'] for v in static]))
        gy = float(np.mean([v['y'] for v in static]))
        _gy_past_baseline = (gy > court['court_bottom_y'] or gy < court['court_top_y'])
        if (cv2.pointPolygonTest(court_poly, (gx, gy), True) < -net_tol_px
                or _gy_past_baseline):
            return 'out_of_bounds', _oob_fault_side(gy, court, net_ground_Y), 'HIGH', feats
        if abs(gy - net_ground_Y) < net_tol_px * 2 and _near_net_x(gx, net_x_min, net_x_max, net_tol_px):
            return 'hits_net', _net_fault, 'HIGH', feats
        lh = 'far' if gy < net_ground_Y else 'near'
        return 'wins_by_landing', lh, 'HIGH', feats

    # ── CHECK 1/2 (combined): isolate the FINAL shot's flight segment
    # (after the last racket redirect, soft or hard) and judge the
    # landing using only that segment's own direction/side/cable-cross.
    #
    # A naive whole-window "did it cross the cable" check fails on net
    # rallies: a 3s window often contains several real net taps, and any
    # one of them can look like "it crossed and stayed crossed to the
    # end of the window" even when the truly final touch caught the net.
    # Restricting to the segment after the last detected redirect avoids
    # picking up an earlier, incidental crossing.
    if len(final_seg) >= 2:
        fvels = []
        for i in range(1, len(final_seg)):
            f0,x0,y0 = final_seg[i-1]; f1,x1,y1 = final_seg[i]
            dt = (f1-f0)/fps
            if dt <= 0: continue
            fvels.append({'vy':(y1-y0)/dt,
                          'speed':math.hypot((x1-x0)/dt,(y1-y0)/dt)})
        if fvels:
            seg_vy    = float(np.mean([v['vy'] for v in fvels]))
            seg_speed = float(np.mean([v['speed'] for v in fvels]))
            seg_start_y = float(final_seg[0][2])
            seg_end_y   = float(final_seg[-1][2])
            seg_start_side = 'far' if seg_start_y < net_top_Y else 'near'
            seg_end_side   = 'far' if seg_end_y   < net_top_Y else 'near'
            crossed_in_seg = seg_start_side != seg_end_side

            if crossed_in_seg:
                # Crossed the cable height -- but settling close to the
                # net afterward does NOT by itself mean it touched the
                # net. A clean, tight net shot that clears the tape and
                # drops immediately on the far side is a legal winner,
                # not a fault -- only an actual tape contact is. The
                # distinguishing signal is whether the trajectory lingers
                # at cable height (dragging along the tape) rather than
                # passing through it briefly.
                frames_near_cable = sum(
                    1 for _, _, y in final_seg if abs(y - net_top_Y) < net_tol_px * 3
                )
                lingered = frames_near_cable >= max(8, len(final_seg) * 0.4)
                if (lingered and abs(seg_end_y - net_ground_Y) < net_tol_px * 2
                        and seg_speed < HIGH_SPEED
                        and _near_net_x(last_x, net_x_min, net_x_max, net_tol_px)):
                    return 'hits_net', _net_fault, conf, feats
                in_court = cv2.pointPolygonTest(court_poly, (last_x, last_y), True) >= -net_tol_px
                if in_court:
                    return 'wins_by_landing', seg_end_side, conf, feats
                return 'out_of_bounds', \
                       _oob_fault_side(last_y, court, net_ground_Y), conf, feats
            else:
                # never crossed within the final segment -- if it died
                # near the net's floor line, that's a net fault.
                #
                # Shuttle may have reached/passed cable height mid-segment
                # (start and end both on same side) -- classic bounce-off-tape.
                _min_y_in_seg = min(p[2] for p in final_seg)
                if _min_y_in_seg < net_top_Y + net_tol_px:
                    # Rule A: shuttle crossed above cable AND landed outside
                    # court → OOB (bounced off cable, flew out past sideline)
                    if (_min_y_in_seg < net_top_Y
                            and cv2.pointPolygonTest(
                                court_poly, (last_x, last_y), True) < -net_tol_px):
                        return ('out_of_bounds',
                                _oob_fault_side(last_y, court, net_ground_Y),
                                conf, feats)
                    # Rule B: approached cable + steep vertical fall toward
                    # net_ground_Y → hits_net (shuttle lost horizontal speed
                    # on tape contact, dropped straight down)
                    if (abs(last_y - net_ground_Y) < net_tol_px * 2.5
                            and _near_net_x(last_x, net_x_min, net_x_max, net_tol_px)):
                        _nc_i = min(range(len(final_seg)),
                                    key=lambda i: final_seg[i][2])
                        _fvxs, _fvys = [], []
                        for _k in range(_nc_i, len(final_seg) - 1):
                            _p0, _p1 = final_seg[_k], final_seg[_k + 1]
                            _dt = (_p1[0] - _p0[0]) / fps
                            if _dt > 0:
                                _fvxs.append(abs((_p1[1] - _p0[1]) / _dt))
                                _fvys.append((_p1[2] - _p0[2]) / _dt)
                        _mean_fall_vy = float(np.mean(_fvys)) if _fvys else 0.0
                        _mean_fall_vx = float(np.mean(_fvxs)) if _fvxs else 1.0
                        if _fvys and _mean_fall_vy / max(_mean_fall_vx, 1.0) > 2.0:
                            return 'hits_net', _net_fault, conf, feats

                if (abs(seg_end_y - net_ground_Y) < net_tol_px * 2.5 and seg_speed < HIGH_SPEED
                        and _near_net_x(last_x, net_x_min, net_x_max, net_tol_px)
                        and _min_y_in_seg < net_top_Y + net_tol_px * 2):
                    return 'hits_net', _net_fault, conf, feats

    # ── CHECK 2b: Clear positional baseline OOB ───────────────
    # If the shuttle's last tracked position is past a baseline, it is
    # unambiguously OOB regardless of velocity or deceleration.  Catching
    # this here prevents CHECK 3's backward extrapolation (which can point
    # in the wrong direction when the window spans two shots) from
    # misclassifying these as hits_net.
    if last_y > court['court_bottom_y']:
        return 'out_of_bounds', 'far',  conf, feats
    if last_y < court['court_top_y']:
        return 'out_of_bounds', 'near', conf, feats

    # ── CHECK 3: OOB via extrapolation ────────────────────────
    # Guard: if pred_vy < 0 (upward) but the shuttle is already in the NEAR
    # zone and within court tolerance, the early-window velocities came from
    # a previous UP shot inside the 3-second window.  Extrapolating backward
    # through the net would produce a false hits_net call, so skip CHECK 3
    # and let CHECK 7 handle the wins_by_landing correctly.
    _backward_extrap = (pred_vy < 0 and last_y > net_top_Y
                        and cv2.pointPolygonTest(court_poly, (float(rel_x), float(rel_y)), True) >= -net_tol_px * 2)
    if decel_rate < 0.35 and not _backward_extrap:
        extrap, pt = _extrapolate_exit(rel_x, rel_y, pred_vx, pred_vy,
                                        court_poly, fps, line_tol=net_tol_px)
        if extrap:
            ey = float(pt[1]) if pt else rel_y
            ex = float(pt[0]) if pt else rel_x
            if abs(ey - net_top_Y) < net_tol_px * 3 and _near_net_x(ex, net_x_min, net_x_max, net_tol_px):
                return 'hits_net', _net_fault, conf, feats
            return 'out_of_bounds', \
                   _oob_fault_side(ey, court, net_ground_Y), conf, feats

    # ── CHECK 4: Baseline proximity ───────────────────────────
    near_base_y = court["court_bottom_y"]
    far_base_y  = court["court_top_y"]
    if decel_rate < 0.35:
        if fault_vy > 10 and last_y > near_base_y - 40:
            return 'out_of_bounds', 'far',  conf, feats
        if fault_vy < -10 and last_y < far_base_y + 40:
            return 'out_of_bounds', 'near', conf, feats

    # ── CHECK 5: Shuttle above cable and in court → wins_by_landing
    above_cable  = last_y < net_top_Y
    inside_court = cv2.pointPolygonTest(court_poly,(last_x,last_y),True) > -30

    if above_cable and inside_court:
        lh = 'far' if last_y < net_ground_Y else 'near'
        # Player reach check
        REACH_THRESHOLD = 300
        if player_feats:
            px = player_feats.get('far_cx' if lh=='far' else 'near_cx')
            py = player_feats.get('far_bottom' if lh=='far' else 'near_bottom')
            if px is not None and py is not None:
                dist = math.hypot(last_x-px, last_y-py)
                feats['player_dist'] = round(dist, 1)
                if dist > REACH_THRESHOLD:
                    feats['failed_to_return'] = True
        return 'wins_by_landing', lh, conf, feats

    # ── CHECK 6: OOB fallback ─────────────────────────────────
    # Skip for backward-extrapolation cases (margin < 2×tol) — the shuttle
    # is barely outside due to tracking noise, not a genuine OOB event.
    if (not _backward_extrap
            and cv2.pointPolygonTest(court_poly,(float(rel_x),float(rel_y)),True) < -net_tol_px):
        if abs(rel_y - net_top_Y) < net_tol_px * 3 and _near_net_x(rel_x, net_x_min, net_x_max, net_tol_px):
            return 'hits_net', _net_fault, conf, feats
        return 'out_of_bounds', \
               _oob_fault_side(last_y, court, net_ground_Y), conf, feats

    # ── CHECK 7: Final fallback ────────────────────────────────
    # Nothing else matched — most often this is a soft/dying net shot
    # that never registered enough speed or deceleration to trip the
    # explicit hits_net checks above. Only assume a clean winner if the
    # shuttle actually ended up away from the net's floor footprint.
    # Require both: landed near net_ground_Y AND trajectory reached cable
    # height — if landed far from net_ground, or never approached the
    # cable, it's a winner not a fault.
    _seg_apex_y = min(p[2] for p in final_seg) if final_seg else last_y
    if (abs(last_y - net_ground_Y) < net_tol_px * 2
            and _near_net_x(last_x, net_x_min, net_x_max, net_tol_px)
            and _seg_apex_y < net_ground_Y):
        return 'hits_net', _net_fault, conf, feats
    lh = 'far' if last_y < net_ground_Y else 'near'
    return 'wins_by_landing', lh, conf, feats


# ══════════════════════════════════════════════════════════════
# STEP 4 — WINNER + SHOT + SCORE
# ══════════════════════════════════════════════════════════════

def determine_winner(event, fault_side, name_far, name_near):
    """
    fault_side = player who made the fault (hit out, hit net, etc)
    That player LOSES → the other player wins.
    fault='far'  → far player faulted  → near player (Player B) wins
    fault='near' → near player faulted → far player  (Player A) wins
    """
    if event == 'unknown' or fault_side == 'unknown':
        return 'unknown'
    return name_far if fault_side == 'near' else name_near


def classify_shot(feats, event):
    speed     = feats.get('speed', 0)
    vy        = feats.get('vy', 0)
    vx        = feats.get('vx', 0)
    contact_y = feats.get('contact_y', 0)
    net_top_Y = feats.get('net_top_Y', 0)
    net_tol   = feats.get('net_tol_px', 18)
    early_spd = feats.get('early_speed', speed)
    near_net  = abs(contact_y - net_top_Y) < net_tol * 3
    lateral   = abs(vx) / max(abs(vy), 1.0)

    if early_spd > HIGH_SPEED and vy > 15 and near_net: return 'net smash'
    if early_spd > HIGH_SPEED and vy > 15:              return 'smash'
    if near_net and early_spd < MED_SPEED and vy > 0:   return 'drop'
    if vy < -30 and early_spd < HIGH_SPEED:             return 'lift'
    if lateral > 1.2 and early_spd > 100:               return 'hook'
    if lateral > 0.7 and early_spd > 80:                return 'slice'
    if abs(vy) < 40 and early_spd > MED_SPEED:          return 'drive'
    if near_net:                                         return 'push'
    return 'push'


def track_scores(winners, name_a, name_b):
    sa, sb, scores = 0, 0, []
    for w in winners:
        if w == name_a: sa += 1
        elif w == name_b: sb += 1
        scores.append((sa, sb))
        if (sa >= 21 and sa-sb >= 2) or sa == 30: sa, sb = 0, 0
        if (sb >= 21 and sb-sa >= 2) or sb == 30: sa, sb = 0, 0
    return scores


def _mmss(s):
    return f"{int(s//60):02d}:{int(s%60):02d}"

def _frame_col_rally(df):
    if 'End_Frame' in df.columns: return 'End_Frame'
    if 'end_frame' in df.columns: return 'end_frame'
    return None


# ══════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════

def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--rally",    required=True)
    p.add_argument("--shuttle",  required=True)
    p.add_argument("--court",    required=True)
    p.add_argument("--out",      required=True)
    p.add_argument("--fps",      type=float, default=30.0)
    p.add_argument("--player_a", default="Player A")
    p.add_argument("--player_b", default="Player B")
    p.add_argument("--player",   default=None)
    p.add_argument("--swap_players", action="store_true",
                    help="By default the FAR (top-of-frame) side is "
                         "labeled player_a and NEAR (bottom-of-frame) is "
                         "player_b. Camera placement varies by recording "
                         "session, so this isn't always correct for a "
                         "given match — pass this flag to swap it.")
    return p.parse_args()


def main():
    args = parse_args()

    print("=" * 60)
    print("  BADMINTON FEATURE EXTRACTION (no video)")
    print("=" * 60)
    print(f"  Rally:   {args.rally}")
    print(f"  Shuttle: {args.shuttle}")
    print(f"  Court:   {args.court}")
    print(f"  Output:  {args.out}")
    print(f"  FPS:     {args.fps}")

    rally_df   = pd.read_csv(args.rally)
    shuttle_df = pd.read_csv(args.shuttle)
    fps        = args.fps
    print(f"\n  {len(rally_df)} rallies | {len(shuttle_df)} shuttle rows")

    print("\n[1] Loading court geometry...")
    court = load_court_from_json(args.court)

    # ── Player side assignment ─────────────────────────────────
    # FAR (top-of-frame) / NEAR (bottom-of-frame) is purely a screen-
    # geometry label. Which named player ends up on which side depends
    # on where the camera was set up for THIS recording — that varies
    # per match, so it can't be hardcoded. Use --swap_players to flip it
    # once you've checked the orientation for a given match (e.g. against
    # the first known rally, or your own setup notes).
    if args.swap_players:
        far_name, near_name = args.player_b, args.player_a
    else:
        far_name, near_name = args.player_a, args.player_b
    far_slot  = 'player_1'      # default

    if args.player and os.path.exists(args.player):
        print("\n[2] Assigning player sides from court geometry...")
        far_slot, near_slot = assign_player_sides(args.player, court)
        print(f"  FAR  = {far_slot} = {far_name}")
        print(f"  NEAR = {near_slot} = {near_name}")
        player_df = pd.read_csv(args.player)
    else:
        print(f"\n[2] No player CSV — FAR={far_name} / NEAR={near_name} (default)")
        player_df = None

    ef_col = _frame_col_rally(rally_df)

    print("\n[3] Analysing rallies...")
    results = []

    for idx, row in rally_df.iterrows():
        def to_sec(val):
            val = str(val).strip()
            if ":" in val:
                p = val.split(":")
                return int(p[0])*60 + int(p[1])
            try: return float(val)
            except: return 0.0

        s_sec = to_sec(row.get("start_time", row.get("Start_Time_sec", 0)))
        e_sec = to_sec(row.get("end_time",   row.get("End_Time_sec",   0)))
        ef    = int(row[ef_col]) if ef_col and ef_col in row else int(e_sec * fps)

        player_feats = None
        if player_df is not None:
            player_feats = extract_player_features(player_df, ef, far_slot)

        event, fault_side, conf, feats = analyze_rally_end(
            shuttle_df, ef, court, fps, player_feats
        )
        winner   = determine_winner(event, fault_side, far_name, near_name)
        win_str  = _WIN_STR.get(event,  'unknown')
        lose_str = _LOSE_STR.get(event, 'unknown')
        shot     = classify_shot(feats, event)

        results.append(dict(start_sec=s_sec, end_sec=e_sec,
                            winner=winner, win_reason=win_str,
                            lose_reason=lose_str, shot=shot,
                            conf=conf, feats=feats))

        print(f"  R{idx+1:>3}: {_mmss(s_sec)}->{_mmss(e_sec)}  "
              f"{event:<18}  fault={fault_side:<5}  "
              f"winner={winner:<14}  [{conf}]")

    scores = track_scores([r['winner'] for r in results],
                          args.player_a, args.player_b)

    print(f"\n[4] Saving to {args.out}...")
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)

    rows = []
    for i, r in enumerate(results):
        sa, sb = scores[i]
        rows.append({
            'start_time':           _mmss(r['start_sec']),
            'end_time':             _mmss(r['end_sec']),
            'win_point_player':     r['winner'],
            'win_reason':           r['win_reason'],
            'ball_types':           r['shot'],
            'lose_reason':          r['lose_reason'],
            'roundscore_A':         sa,
            'roundscore_B':         sb,
            'detection_confidence': r['conf'],
        })

    pd.DataFrame(rows).to_csv(args.out, index=False)

    unknowns  = sum(1 for r in rows if r['win_point_player'] == 'unknown')
    low_conf  = sum(1 for r in results if r['conf'] == 'LOW')
    high_conf = sum(1 for r in results if r['conf'] == 'HIGH')

    print(f"\n  Total:     {len(rows)}")
    print(f"  HIGH conf: {high_conf}")
    print(f"  LOW conf:  {low_conf}")
    print(f"  Unknown:   {unknowns}")
    print(f"\n  Saved -> {args.out}")
    print("\nDone.")


if __name__ == "__main__":
    main()
