"""Small exact-PTS source samples; one decoder thread, read-only input."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import av
import cv2

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent / 'extra_source_panels'
SOURCE = ROOT / 'evaluation/ground_truth_validation/test_02/inputs/Test2_Full_Rev.mp4'
TARGETS = (7701, 7704, 7705, 11344, 11347, 11348, 23637, 23638, 23639, 23640, 23641)
OUT.mkdir(exist_ok=False)
cv2.setNumThreads(1)
records = []
before = SOURCE.stat()
with av.open(str(SOURCE)) as container:
    stream = container.streams.video[0]
    stream.codec_context.thread_count = 1
    for target in TARGETS:
        pts = Fraction(target, 30) / stream.time_base
        if pts.denominator != 1:
            raise ValueError('Non-exact target PTS')
        container.seek(int(pts), backward=True, any_frame=False, stream=stream)
        captured = False
        for frame in container.decode(stream):
            index = frame.pts * frame.time_base * 30
            if index.denominator != 1:
                raise ValueError('Non-CFR source frame')
            if index < target:
                continue
            if index != target:
                raise ValueError('Seek missed exact source target')
            source = frame.to_ndarray(format='bgr24')
            panel = cv2.resize(source, (1280, 720), interpolation=cv2.INTER_AREA)
            path = OUT / f'frame_{target:05d}_source_resized.png'
            cv2.imwrite(str(path), panel)
            records.append({'source_frame': target, 'pts': frame.pts,
                'time_base_num': frame.time_base.numerator, 'time_base_den': frame.time_base.denominator,
                'source_time_seconds': float(frame.pts * frame.time_base),
                'source_shape': list(source.shape), 'source_pixels_sha256': hashlib.sha256(source.tobytes()).hexdigest(),
                'panel': path.name, 'panel_sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'transform': 'Original BGR1920x1080 to1280x720 cv2.INTER_AREA'})
            captured = True
            break
        if not captured:
            raise ValueError('Target not decoded')
after = SOURCE.stat()
if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
    raise ValueError('Source changed during read-only sample extraction')
with (OUT / 'metadata.json').open('x') as f:
    json.dump({'source': str(SOURCE), 'source_bytes': before.st_size,
               'source_sha256_from_verified_download': '4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a',
               'hash_scope': 'Download identity asserted by root receipt; no redundant full-file hash during active inference',
               'no_neural_inference': True, 'frames': records}, f, indent=2)
    f.write('\n')
print('Retained exact-PTS source panels:', len(records))
