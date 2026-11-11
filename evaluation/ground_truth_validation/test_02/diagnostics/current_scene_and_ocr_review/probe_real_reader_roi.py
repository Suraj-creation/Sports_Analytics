"""Bounded standalone CPU OCR acquisition probes, not live worker inspection."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
from fractions import Fraction
import sys

import av
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT / 'sports/badminton/src'), str(ROOT / 'engine/src')]
from bai_badminton.perception.scoreboard import ScoreboardReader, CORNERS, parse_scoreboard

OUT = Path(__file__).resolve().parent / 'real_roi_probe'
RUN = ROOT.parent / 'ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run'
PROXY = RUN / 'data/media/4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a/proxy.mp4'
FRAMES = (720, 8794, 8824, 8854, 8884, 8914, 11346, 12604, 22924)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def output(result):
    if result is None:
        return None
    return {'frame_idx': result.frame_idx, 'rows': result.rows, 'confidence': result.conf}


def raw_output(result):
    if result is None:
        return None
    return {'boxes': None if result.boxes is None else np.asarray(result.boxes).tolist(),
            'texts': None if result.txts is None else list(result.txts),
            'scores': None if result.scores is None else np.asarray(result.scores).tolist()}


def decode(container, stream, index):
    pts = Fraction(index, 30) / stream.time_base
    if pts.denominator != 1:
        raise ValueError('Source frame cannot be sought exactly')
    container.seek(int(pts), backward=True, any_frame=False, stream=stream)
    for frame in container.decode(stream):
        current = frame.pts * frame.time_base * 30
        if current < index:
            continue
        if current != index:
            raise ValueError('Actual frame does not match canonical requested frame')
        return frame.to_ndarray(format='bgr24'), {'pts': frame.pts, 'time_base': str(frame.time_base)}
    raise ValueError('Frame missing')


def main():
    OUT.mkdir(exist_ok=False)
    cv2.setNumThreads(1)
    reader = ScoreboardReader.load(every=30, backend='onnx-cpu', num_threads=2)
    actual_ocr = reader.ocr
    captured = []
    current_frame = None
    def traced(crop):
        result = actual_ocr(crop)
        path = OUT / f'frame_{current_frame:05d}_reader_crop.png'
        cv2.imwrite(str(path), crop)
        captured.append({'crop_shape': list(crop.shape), 'crop_pixels_sha256': sha(crop.tobytes()),
                         'crop': path.name, 'ocr': raw_output(result)})
        return result
    reader.ocr = traced
    rows = []
    with av.open(str(PROXY)) as container:
        stream = container.streams.video[0]
        stream.codec_context.thread_count = 1
        for index in FRAMES:
            current_frame = index
            image, pts = decode(container, stream, index)
            roi_before, misses_before, corner_before = reader.roi, reader._misses, reader._corner
            reading = reader.maybe_read(index, image)
            trace = captured[-1]
            h, w = image.shape[:2]
            x0, y0, x1, y1 = [int(v * bound) for v, bound in zip(CORNERS[0], (w, h, w, h), strict=True)]
            full_corner = image[y0:y1, x0:x1]
            full_result = actual_ocr(full_corner)
            parsed = None
            if full_result is not None and getattr(full_result, 'txts', None):
                parsed = parse_scoreboard(full_result.boxes, full_result.txts, full_result.scores, index)
            path = OUT / f'frame_{index:05d}_full_top_left_corner.png'
            cv2.imwrite(str(path), full_corner)
            marked = image.copy()
            if roi_before is not None:
                a, b, c, d = roi_before
                cv2.rectangle(marked, (a, b), (c, d), (0, 0, 255), 2)
            cv2.imwrite(str(OUT / f'frame_{index:05d}_roi_on_proxy.png'), marked)
            row = {'frame': index, 'pts': pts, 'proxy_pixels_sha256': sha(image.tobytes()),
                   'reader_roi_before': roi_before, 'reader_roi_after': reader.roi,
                   'reader_misses_before': misses_before, 'reader_misses_after': reader._misses,
                   'reader_corner_before': corner_before, 'reader_reading': output(reading),
                   'reader_input_and_ocr': trace, 'full_top_left_ocr': raw_output(full_result),
                   'full_top_left_parsed': None if parsed is None else output(parsed[0]),
                   'full_top_left_parsed_bounds': None if parsed is None else parsed[1]}
            rows.append(row)
            print(json.dumps({k: row[k] for k in ('frame', 'reader_roi_before', 'reader_roi_after',
                  'reader_reading', 'full_top_left_parsed')}), flush=True)
    result = {'schema': 'test02-standalone-real-proxy-roi-acquisition:v1',
              'scope': 'Sparse standalone sequence seeded with first cached successful frame; not replay of every worker call or live state',
              'source_sha256_from_verified_baseline': '4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a',
              'proxy': str(PROXY), 'runtime': reader.runtime, 'frames': rows,
              'live_sqlite_opened': False, 'production_modified': False,
              'complete_worker_roi_history_established': False,
              'physical_score_accuracy_established': False}
    with (OUT / 'report.json').open('x') as f:
        json.dump(result, f, indent=2)
        f.write('\n')


if __name__ == '__main__':
    main()
