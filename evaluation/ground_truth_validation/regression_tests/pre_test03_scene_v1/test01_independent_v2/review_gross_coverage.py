"""Account for every reduced-population frame, beyond scored legacy pairs."""

from pathlib import Path
from collections import Counter
import json

import msgpack
import numpy as np

from bai_badminton.court import Homography
from bai_badminton.perception.players import CourtROI
from review_coverage_tradeoffs import ROOT, MAIN, CANDIDATE, ART, OLD, OUT, sha, read, write, iou, groups


def main():
    import bai_badminton.perception.players as native

    assert Path(native.__file__).resolve().is_relative_to(CANDIDATE)
    prior = read(OUT / 'coverage_tradeoffs.json')
    inputs = dict(prior['input_sha256'])
    inputs[str(OUT / 'coverage_tradeoffs.json')] = sha(OUT / 'coverage_tradeoffs.json')
    inputs[str(Path(__file__))] = sha(__file__)
    sets = {}
    for name, base in [('original', OLD), ('fresh', ART)]:
        rows = []
        for entry in read(base / 'run/perception_completion_catalog.json')['files']:
            rows.extend(msgpack.unpackb((base / 'run' / entry['path']).read_bytes(), raw=False)['frames'])
        sets[name] = rows
    events = [json.loads(line) for line in (ART / 'run/events.jsonl').open()]
    calibration = next(row for row in events if row['type'] == 'calibration')
    H = np.asarray(calibration['payload']['H'])
    anchors, last_fg, entries = {}, {}, []
    for old, current in zip(sets['original'], sets['fresh'], strict=True):
        number = current['f']
        h = Homography(np.asarray(current['g']).reshape(3, 3) @ H, 0., 4) if current['g'] is not None else None
        roi = CourtROI(np.zeros((4, 2), np.float32), homography=h) if h is not None else None
        for person in current['p']:
            if roi is not None and person['dm'] is True and roi.contains_feet(np.asarray(person['b'])):
                anchors[(current['sh'], current['ce'], person['rt'])] = number
        for region in current['fg']:
            if region['detector_matched'] is True and region['detector_observed'] is True:
                last_fg[region['key']] = number
        if len(old['p']) <= len(current['p']):
            continue
        unmatched = [person for person in old['p'] if max([iou(person['b'], other['b']) for other in current['p']], default=0.) < .5]
        assert len(unmatched) == 1
        person = unmatched[0]
        overlap, region = max([(iou(person['b'], candidate['bbox']), candidate) for candidate in current['fg']], key=lambda item: item[0])
        assert overlap > .99
        anchor = anchors.get((current['sh'], current['ce'], person['rt']))
        assert anchor is not None and number - anchor > 30
        support = [{'support': item['support'], 'bbox': item['bbox']} for item in ((current.get('dg') or {}).get('players') or {}).get('roi_rejected', []) if iou(item['bbox'], region['bbox']) > .99]
        entries.append({'frame': number, 'seconds': number / 30, 'old_withheld_region': {key: person[key] for key in ['t', 'rt', 'b', 'c', 'dm']}, 'fresh_fg': region, 'same_region_iou': overlap, 'last_padded_court_anchor_reconstruction': anchor, 'court_anchor_age_frames': number - anchor, 'floor_projection_of_old_box_bottom_m': h.image_to_court(np.asarray([[(person['b'][0] + person['b'][2]) / 2, person['b'][3]]]))[0].tolist() if h is not None else None, 'fg_last_fresh_frame_reconstruction': last_fg[region['key']], 'fg_age_frames': number - last_fg[region['key']], 'current_diagnostic_uncalibrated_support': support or None, 'current_fg_confidence': None, 'confidence_scope': 'Foreground schema has no confidence; current proposal support retained only on detailed diagnostic frames. Old person confidence is historical, not copied as fresh confidence.'})
    assert len(entries) == 182
    intervals = groups([row['frame'] for row in entries])
    grouped = []
    frames = set()
    for start, end in intervals:
        rows = [row for row in entries if start <= row['frame'] <= end]
        grouped.append({'frames': [start, end], 'count': len(rows), 'last_padded_court_anchor_reconstructions': sorted({row['last_padded_court_anchor_reconstruction'] for row in rows}), 'minimum_court_anchor_age_frames': min(row['court_anchor_age_frames'] for row in rows), 'foreground_matched_counts': dict(Counter(str(row['fresh_fg']['detector_matched']) for row in rows)), 'foreground_observed_counts': dict(Counter(str(row['fresh_fg']['detector_observed']) for row in rows)), 'minimum_scene_region_iou': min(row['same_region_iou'] for row in rows), 'confidence_available_diagnostic_frames': [row['frame'] for row in rows if row['current_diagnostic_uncalibrated_support']], 'provisional_cause': 'Bounded last-observed-padded-court participant lease expires; fresh/missing image context separately retained', 'physical_role': 'Requires agent source review; no independently labelled identity or recall inferred'})
        frames.update([start - 1, start, end])
    write('gross_coverage_all_182_rows.json', {'scope': 'All original-vs-fresh reduced participant frames, not physical false negatives or identity metrics', 'total_withheld_person_rows': 182, 'groups': grouped, 'all_rows': entries, 'private_state_scope': 'Court/foreground timestamps reconstructed from recorded fresh observations and exact candidate-native CourtROI, not serialized private state', 'original_vs_fresh_common_raw_shuttle_equal': all(a['s'] == b['s'] and a['c'] == b['c'] for a, b in zip(sets['original'], sets['fresh'], strict=True)), 'input_sha256': inputs})
    write('all_coverage_frame_plan.json', {'source_sha256': read(OUT / 'summary.json')['source_sha256'], 'proxy_sha256': read(ART / 'run/inference.json')['proxy_sha256'], 'frames': [{'frame': frame, 'reasons': ['Every gross participant-coverage loss interval: before/start/end source control']} for frame in sorted(frames)], 'scope': 'Complements the immutable45-frame actual-change plan; no physical FN labels'})
    assert all(sha(path) == digest for path, digest in inputs.items())
    print(json.dumps({'groups': grouped, 'raw_shuttle_all_frames_exact': all(a['s'] == b['s'] and a['c'] == b['c'] for a, b in zip(sets['original'], sets['fresh'], strict=True))}))


if __name__ == '__main__':
    main()
