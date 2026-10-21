"""
frame_picker.py
----------------
Shared "find a frame that actually shows the standard broadcast court view"
logic, used by both annotate_court.py (manual) and auto_court.py (fully
automatic). Pulled out on its own so both can import it without triggering
annotate_court.py's top-level argparse/server-startup code.

A fixed early frame number (e.g. frame 90, ~3s in) is a bad default for a
full broadcast -- it's very likely still intro/sponsor/graphics, not rally
footage (verified: on a real 31-minute match video, frame 90 was a drone
shot of the arena exterior). And ranking candidates by "biggest detected
green area" alone is also a bad metric -- it rewards zoomed-in/cropped
shots over the standard, centered, fully-framed broadcast wide shot every
match actually annotated this way uses. This scores candidates on area
(gate only), centering, and edge margin together.
"""
import os
import sys

import cv2


def center_score(corners, w, h):
    """1.0 = court centroid dead-center in frame, 0.0 = at the edge."""
    cx, cy = corners[:, 0].mean(), corners[:, 1].mean()
    fx, fy = w / 2.0, h / 2.0
    max_dist = ((w / 2.0) ** 2 + (h / 2.0) ** 2) ** 0.5
    dist = ((cx - fx) ** 2 + (cy - fy) ** 2) ** 0.5
    return max(0.0, 1.0 - dist / max_dist)


def margin_score(corners, w, h):
    """1.0 = clear breathing room on all sides (a wide shot), drops toward
    0 as the polygon approaches actually touching a frame edge (a sign of
    a zoomed/cropped shot, not the standard wide broadcast angle)."""
    margin_x = min(corners[:, 0].min(), w - corners[:, 0].max()) / w
    margin_y = min(corners[:, 1].min(), h - corners[:, 1].max()) / h
    return max(0.0, min(1.0, margin_x * 10)) * max(0.0, min(1.0, margin_y * 10))


def _stable_enough(cap, fno, corners, w, h, frame_area, fps, total,
                   court_type='singles', window_sec=8.0, sample_stride_sec=1.0,
                   min_present_sec=3.0, max_reproj_error_m=0.6,
                   green_threshold=0.55, quiet=True):
    """
    Is this candidate frame part of a genuinely sustained court view, or a
    one-off (e.g. a single well-composed frame mid-camera-pan, or a
    promotional freeze-frame that happens to score well in isolation)?

    A frame that merely LOOKS well-framed isn't enough to annotate from --
    the whole point of the reference frame is that court_presence.py
    checks every other frame in the video against it, so if the reference
    itself isn't representative of the sustained rally angle, that
    (correct) check would wrongly reject most of the real match. This
    samples a window around fno and requires a contiguous run of frames
    that pass the SAME green-fraction + homography checks
    court_presence.py uses for the real segmentation pass, centered on
    fno -- not just fno trivially passing against its own corners.

    Returns (stable: bool, run_sec: float). Cheap: ~2*window_sec/stride
    frame reads, only for candidates that already cleared the area/shape
    gate, so this never runs on most rejected frames.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extract_features import _try_detect_corners
    from court_presence import reference_homography, green_fraction, geometric_reproj_error_m
    import numpy as np

    H_ref, real_rect = reference_homography(corners.astype('float32'), court_type)
    mask = np.zeros((h, w), dtype='uint8')
    cv2.fillPoly(mask, [corners.astype('int32')], 255)

    stride_f = max(1, int(sample_stride_sec * fps))
    window_f = int(window_sec * fps)
    offsets = list(range(-window_f, window_f + 1, stride_f))
    present = []
    for off in offsets:
        t = fno + off
        if t < 0 or t >= total:
            present.append(False)
            continue
        cap.set(cv2.CAP_PROP_POS_FRAMES, t)
        ok, frame = cap.read()
        if not ok:
            present.append(False)
            continue
        gf = green_fraction(frame, mask)
        if gf < green_threshold:
            present.append(False)
            continue
        err = geometric_reproj_error_m(frame, H_ref, real_rect, frame_area, _try_detect_corners)
        present.append(err is not None and err <= max_reproj_error_m)

    center_idx = offsets.index(0)
    if not present[center_idx]:
        return False, 0.0
    lo = center_idx
    while lo > 0 and present[lo - 1]:
        lo -= 1
    hi = center_idx
    while hi < len(present) - 1 and present[hi + 1]:
        hi += 1
    run_sec = (offsets[hi] - offsets[lo]) / fps
    if not quiet:
        print(f'    frame {fno}: ~{run_sec:.1f}s of consistent court around it '
             f'(need {min_present_sec:.1f}s)')
    return run_sec >= min_present_sec, run_sec


def rank_candidate_frames(video_path, step_sec=5.0, max_candidates=400,
                          start_frame=0, min_area_frac=0.15, court_type='singles',
                          verify_stable=True):
    """
    Scan the video (from start_frame onward) and score every candidate
    frame for how well it shows a centered, fully-framed court view.

    Returns a list of (frame_no, score, (area_frac, center, margin)),
    best-scoring first. Never empty on success; raises if nothing in the
    scanned range shows a plausible court at all.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from extract_features import _try_detect_corners

    cap = cv2.VideoCapture(video_path)
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_area = w * h

    step = max(1, int(step_sec * fps))
    candidates = list(range(start_frame, total, step))[:max_candidates]

    print(f'  Scanning {len(candidates)} candidate frames (every {step_sec}s, '
          f'starting at frame {start_frame} / {start_frame/fps:.0f}s, across '
          f'{total/fps:.0f}s total) for a centered, fully-framed, SUSTAINED '
          f'court view...')
    scored = []
    for fno in candidates:
        cap.set(cv2.CAP_PROP_POS_FRAMES, fno)
        ok, frame = cap.read()
        if not ok:
            continue
        corners, area = _try_detect_corners(frame, frame_area)
        if corners is None:
            continue
        area_frac = area / frame_area
        # area is a gate (must be a substantial, plausible court view), not
        # the ranking signal -- center/margin decide between candidates
        # that all clear that bar.
        if area_frac < min_area_frac:
            continue
        if verify_stable:
            stable, run_sec = _stable_enough(cap, fno, corners, w, h, frame_area,
                                             fps, total, court_type)
            if not stable:
                continue
        center = center_score(corners, w, h)
        margin = margin_score(corners, w, h)
        score = center * margin * min(1.0, area_frac / 0.30)
        scored.append((fno, score, (area_frac, center, margin)))
    cap.release()

    if not scored:
        raise RuntimeError('No frame with a centered, fully-framed court view '
                           'found in the scanned range -- try a different '
                           '--search_start_frame, or specify a frame manually.')
    scored.sort(key=lambda t: t[1], reverse=True)
    fno, score, (area_frac, center, margin) = scored[0]
    print(f'  Best candidate: frame {fno} ({fno/fps:.1f}s) -- '
         f'area={area_frac*100:.1f}% center={center:.2f} margin={margin:.2f} '
         f'({len(scored)} viable candidates total)')
    return scored


GOOD_ENOUGH_SCORE = 0.5  # center * margin * area_ratio -- see rank_candidate_frames


def _score_one(cap, fno, w, h, frame_area, min_area_frac, fps=None, total=None,
               court_type='singles', verify_stable=True):
    from extract_features import _try_detect_corners
    cap.set(cv2.CAP_PROP_POS_FRAMES, fno)
    ok, frame = cap.read()
    if not ok:
        return None
    corners, area = _try_detect_corners(frame, frame_area)
    if corners is None:
        return None
    area_frac = area / frame_area
    if area_frac < min_area_frac:
        return None
    if verify_stable:
        stable, run_sec = _stable_enough(cap, fno, corners, w, h, frame_area,
                                         fps, total, court_type)
        if not stable:
            print(f'    frame {fno}: well-framed but only ~{run_sec:.1f}s of '
                 f'consistent court around it (need 3.0s) -- likely a transitional '
                 f'shot, not sustained rally footage, skipping')
            return None
    center = center_score(corners, w, h)
    margin = margin_score(corners, w, h)
    score = center * margin * min(1.0, area_frac / 0.30)
    return (fno, score, (area_frac, center, margin))


def pick_frame_fast(video_path, step_sec=5.0, max_fallback_frames=20,
                    start_frame=None, min_area_frac=0.15, court_type='singles',
                    verify_stable=True):
    """
    Cheap alternative to rank_candidate_frames' full-video scan (which can
    be hundreds of frame reads on a long broadcast and take minutes).

    Tries ONE candidate first -- the middle of the video by default (a
    strong prior: broadcasts are front/back-loaded with intro, walk-ins,
    and post-match ceremony, so the midpoint is very likely mid-match rally
    play), or start_frame if you already know roughly where play starts.
    If that single frame already clears GOOD_ENOUGH_SCORE, return it
    immediately -- one frame read, no scanning. Only if it doesn't does
    this fall back to checking up to max_fallback_frames more candidates
    spaced step_sec apart from that same point, and returns the best of
    those (bounded cost: at most 1 + max_fallback_frames frame reads,
    vs. up to hundreds for rank_candidate_frames).

    Returns a list of (frame_no, score, (area_frac, center, margin)) like
    rank_candidate_frames, best-scoring first, so callers don't need to
    know which path was taken.
    """
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

    cap = cv2.VideoCapture(video_path)
    fps   = cap.get(cv2.CAP_PROP_FPS) or 30.0
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    w     = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h     = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_area = w * h

    anchor = start_frame if start_frame is not None else total // 2
    print(f'  Trying frame {anchor} ({anchor/fps:.0f}s, '
         f'{"video midpoint" if start_frame is None else "given start frame"}) first...')

    result = _score_one(cap, anchor, w, h, frame_area, min_area_frac,
                        fps, total, court_type, verify_stable)
    if result is not None and result[1] >= GOOD_ENOUGH_SCORE:
        cap.release()
        fno, score, (area_frac, center, margin) = result
        print(f'  Good on first try: frame {fno} ({fno/fps:.1f}s) -- '
             f'area={area_frac*100:.1f}% center={center:.2f} margin={margin:.2f}'
             + (' (verified sustained)' if verify_stable else ''))
        return [result]

    print(f'  Frame {anchor} not centered/framed/sustained enough -- checking up to '
         f'{max_fallback_frames} more, every {step_sec}s from there...')
    step = max(1, int(step_sec * fps))
    scored = [result] if result is not None else []
    checked = {anchor}
    fno = anchor
    while len(checked) <= max_fallback_frames:
        fno = fno + step
        if fno >= total:
            break
        checked.add(fno)
        r = _score_one(cap, fno, w, h, frame_area, min_area_frac,
                       fps, total, court_type, verify_stable)
        if r is not None:
            scored.append(r)
            if r[1] >= GOOD_ENOUGH_SCORE:
                break
    cap.release()

    if not scored:
        raise RuntimeError(f'No frame with a centered, fully-framed, SUSTAINED '
                           f'court view found near frame {anchor} (checked '
                           f'{len(checked)} candidates) -- try --search_start_frame '
                           f'near a timestamp you know shows real rally play, '
                           f'specify --frame manually, or pass verify_stable=False '
                           f'if the video genuinely never holds one angle for 3s.')
    scored.sort(key=lambda t: t[1], reverse=True)
    fno, score, (area_frac, center, margin) = scored[0]
    print(f'  Best of {len(scored)} checked: frame {fno} ({fno/fps:.1f}s) -- '
         f'area={area_frac*100:.1f}% center={center:.2f} margin={margin:.2f}')
    return scored
