"""Prefix-only actual-pixel OCR replay and isolated full-corner comparison."""
from __future__ import annotations
import hashlib
import json
import sys
import time
from pathlib import Path
from fractions import Fraction

import av
import msgpack

ROOT = Path(__file__).resolve().parents[5]
sys.path[:0] = [str(ROOT / 'sports/badminton/src'), str(ROOT / 'engine/src'), str(Path(__file__).resolve().parent)]
from bai_badminton.perception.scoreboard import ScoreboardReader
from full_corner_candidate import FullCornerValidationReader
from probe_real_reader_roi import decode, output

OUT = Path(__file__).resolve().parent / 'scheduled_gap_replay'
RUN = ROOT.parent / 'ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run'
PROXY = RUN / 'data/media/4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a/proxy.mp4'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    OUT.mkdir(exist_ok=False)
    caches, expected, views = [], {}, {}
    directory = RUN / 'data/sessions/UPLOADTEST2/perception'
    for path in sorted(directory.glob('seg_*.msgpack')):
        number = int(path.stem.rsplit('_', 1)[1])
        if number * 60 > 12634 or (number + 1) * 60 <= 9484:
            continue
        data = path.read_bytes()
        chunk = msgpack.unpackb(data, raw=False)
        caches.append({'path': str(path.resolve()), 'sha256': sha(data)})
        views.update({f['f']: not bool(f['r']) for f in chunk['frames']})
        expected.update({r['f']: r for r in chunk.get('ocr', [])})
    if not set(range(9484, 12635)) <= views.keys():
        raise ValueError('Completed prefix through12634 required')
    legacy = ScoreboardReader.load(every=30, backend='onnx-cpu', num_threads=2)
    candidate = FullCornerValidationReader(legacy.ocr, every=30)
    readers = {'current': legacy, 'full_corner_candidate': candidate}
    rows = []

    def process(index, image, stage):
        row = {'frame': index, 'stage': stage, 'actual_cached_ocr': expected.get(index), 'arms': {}}
        for name, reader in readers.items():
            before = {'roi': reader.roi, 'corner': reader._corner, 'misses': reader._misses,
                      'last_call': reader._last, 'calls': reader.calls}
            started = time.perf_counter()
            result = reader.maybe_read(index, image)
            elapsed = time.perf_counter() - started
            row['arms'][name] = {'before': before,
                 'after': {'roi': reader.roi, 'corner': reader._corner, 'misses': reader._misses,
                           'last_call': reader._last, 'calls': reader.calls},
                 'elapsed_seconds': elapsed, 'reading': output(result),
                 'ocr_called': reader.calls != before['calls']}
        if any(a['ocr_called'] for a in row['arms'].values()):
            rows.append(row)
            if stage == 'seed' or any(a['reading'] is not None for a in row['arms'].values()):
                print(json.dumps({'frame': index, 'stage': stage,
                      'cached': None if expected.get(index) is None else expected[index]['r'],
                      'current': row['arms']['current']['reading'],
                      'candidate': row['arms']['full_corner_candidate']['reading']}), flush=True)

    with av.open(str(PROXY)) as container:
        stream = container.streams.video[0]
        stream.codec_context.thread_count = 1
        for index in (720, 8794, 9484):
            image, _ = decode(container, stream, index)
            process(index, image, 'seed')
        start_pts = Fraction(9485, 30) / stream.time_base
        container.seek(int(start_pts), backward=True, any_frame=False, stream=stream)
        for frame in container.decode(stream):
            value = frame.pts * frame.time_base * 30
            if value.denominator != 1:
                raise ValueError('Non-CFR input')
            index = int(value)
            if index < 9485:
                continue
            if index > 12634:
                break
            if views[index] and any(index - reader._last >= reader.every for reader in readers.values()):
                process(index, frame.to_ndarray(format='bgr24'), 'scheduled_main_camera_prefix')
    summaries = {}
    for name in readers:
        arm = [r for r in rows if r['stage'] != 'seed' and r['arms'][name]['ocr_called']]
        values = [r for r in arm if r['arms'][name]['reading'] is not None]
        actual_f = {f for f in expected if 9485 <= f <= 12634}
        predicted_f = {r['frame'] for r in values}
        mismatches = []
        for row in arm:
            actual = expected.get(row['frame'])
            got = row['arms'][name]['reading']
            if (actual is None) != (got is None) or (actual is not None and got is not None and actual['r'] != [list(v) for v in got['rows']]):
                mismatches.append({'frame': row['frame'], 'cached': actual, 'probe': got})
        summaries[name] = {'scheduled_calls': len(arm), 'readouts': len(values),
              'first_readouts': [{'frame': r['frame'], 'reading': r['arms'][name]['reading']} for r in values[:6]],
              'total_call_seconds_shared_host': sum(r['arms'][name]['elapsed_seconds'] for r in arm),
              'missing_cached_readout_frames': sorted(actual_f - predicted_f),
              'extra_readout_frames': sorted(predicted_f - actual_f), 'cached_row_mismatches': mismatches}
    report = {'schema': 'test02-scheduled-ocr-gap-prefix-counterfactual:v1',
          'scope': 'Actual proxy pixels, current cached main-view gating, seed720/8794/9484 then all eligible calls9485–12634; not worker introspection',
          'seed_state_limitation': 'State is reconstructed from successful actual frame observations; intermediate pre9484 calls/ROI state not recorded by worker',
          'runtime': legacy.runtime, 'input_cache_receipts': caches, 'rows': rows, 'summary': summaries,
          'prefix_only': True, 'complete_worker_roi_history_established': False,
          'production_changed': False, 'live_sqlite_opened': False,
          'latency_limit': 'Sequential shared CPU2 recognizer; current called first; concurrent GPU worker shares host; not controlled production speed benchmark'}
    with (OUT / 'report.json').open('x') as f:
        json.dump(report, f, indent=2)
        f.write('\n')
    print(json.dumps(summaries, indent=2), flush=True)


if __name__ == '__main__':
    main()
