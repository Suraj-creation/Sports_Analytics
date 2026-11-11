"""Read finalized cache files only; never inspect or open live SQLite.

Snapshots remain prefix diagnostics until strict completed-run verification.
Run again as targets mature; existing snapshots are immutable.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import time
from pathlib import Path

import cv2
import msgpack

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
RUN = ROOT.parent / 'ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run'
CACHE = RUN / 'data/sessions/UPLOADTEST2/perception'
SOURCE_PANELS = ROOT / 'evaluation/ground_truth_validation/test_02/diagnostics/annotation_visual_review'
TARGETS = {'startup': (0, 120), 'false_barrier_7703': (7698, 7708),
           'missed_edit_11346': (11335, 11358), 'branding_22924': (22890, 22960),
           'false_barrier_23639': (23634, 23644),
           'g69_gap_extended': (27290, 27400)}


def sha(data):
    return hashlib.sha256(data).hexdigest()


def stable_chunk(path):
    before = path.stat()
    data = path.read_bytes()
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise RuntimeError('Cache changed while reading: ' + str(path))
    decoded = msgpack.unpackb(data, raw=False)
    ids = [row['f'] for row in decoded['frames']]
    if ids != list(range(decoded['start'], decoded['end'] + 1)):
        raise ValueError('Cache chunk frame sequence is incomplete')
    return decoded, {'path': str(path.resolve()), 'bytes': len(data), 'sha256': sha(data),
                     'start': decoded['start'], 'end': decoded['end']}


def overlay(frame, folder):
    source = SOURCE_PANELS / f"frame_{frame['f']:05d}_source_resized.png"
    if not source.exists():
        return None
    data = source.read_bytes()
    image = cv2.imread(str(source))
    if image.shape[:2] != (720, 1280):
        raise ValueError('Unexpected source annotation panel coordinates')
    for person in frame.get('p', []):
        x0, y0, x1, y1 = map(round, person['b'])
        color = (0, 255, 0) if person.get('dm') else (0, 165, 255)
        cv2.rectangle(image, (x0, y0), (x1, y1), color, 2)
        cv2.putText(image, f"track {person['t']}; fresh={person.get('dm')}",
                    (x0, max(15, y0 - 5)), cv2.FONT_HERSHEY_SIMPLEX, .45, color, 1)
    for point, color, label in [(frame.get('s'), (0, 0, 255), 'raw'),
                                ((frame.get('sa') or {}).get('selected_xy'), (255, 0, 255), 'selected')]:
        if point is not None:
            xy = tuple(map(round, point))
            cv2.circle(image, xy, 7, color, 2)
            cv2.putText(image, label, (xy[0] + 8, xy[1]), cv2.FONT_HERSHEY_SIMPLEX, .45, color, 1)
    decision = frame.get('cd') or {}
    label = f"PREFIX ONLY f={frame['f']} epoch={frame.get('ce')} view={frame.get('v')} cal={frame.get('cs')} cd={decision.get('decision')}"
    cv2.rectangle(image, (0, 680), (1280, 720), (0, 0, 0), -1)
    cv2.putText(image, label, (8, 707), cv2.FONT_HERSHEY_SIMPLEX, .54, (255, 255, 255), 1)
    dest = folder / f"frame_{frame['f']:05d}_current_prefix_overlay.png"
    if dest.exists():
        raise ValueError('Overlay would overwrite retained output')
    cv2.imwrite(str(dest), image)
    return {'frame': frame['f'], 'source_panel': str(source), 'source_panel_sha256': sha(data),
            'overlay': str(dest), 'overlay_sha256': sha(dest.read_bytes()),
            'scope': 'Current720p coordinates over resized original source PNG, not inference proxy pixel equality'}


def snapshot_once():
    paths = sorted(CACHE.glob('seg_*.msgpack'))
    if not paths:
        return {'state': 'waiting_for_first_cache', 'ready': [], 'pending': list(TARGETS)}
    last, _ = stable_chunk(paths[-1])
    frontier = last['end']
    ready, pending = [], []
    for name, (lo, hi) in TARGETS.items():
        folder = OUT / name
        if (folder / 'prefix_snapshot.json').exists():
            ready.append(name)
            continue
        if frontier < hi:
            pending.append(name)
            continue
        chunks, receipts, frames = [], [], []
        for path in paths:
            # Current plan's published chunks span60 canonical frames. Use the
            # filename only to bound reads, then verify actual decoded ranges.
            number = int(path.stem.rsplit('_', 1)[1])
            if number * 60 > hi or (number + 1) * 60 <= lo:
                continue
            chunk, receipt = stable_chunk(path)
            receipts.append(receipt)
            chunks.append(chunk)
            frames.extend(row for row in chunk['frames'] if lo <= row['f'] <= hi)
        if [row['f'] for row in frames] != list(range(lo, hi + 1)):
            raise ValueError('Selected source window is not complete; no snapshot saved')
        ocr = [row for chunk in chunks for row in chunk.get('ocr', [])]
        folder.mkdir(exist_ok=False)
        overlays = [item for frame in frames if (item := overlay(frame, folder))]
        payload = {'schema': 'test02-atomic-cache-prefix-scene-ocr-diagnostic:v1',
                   'scope': 'PREFIX ONLY; not completed inference, full-video metrics or independent accuracy',
                   'captured_epoch': time.time(), 'run': str(RUN),
                   'highest_published_chunk_end_at_capture': frontier,
                   'window_inclusive': [lo, hi], 'input_cache_receipts': receipts,
                   'frames': frames, 'ocr_from_overlapping_chunks': ocr, 'overlays': overlays,
                   'live_sqlite_opened': False, 'neural_inference_performed': False,
                   'completion_verified': False}
        with (folder / 'prefix_snapshot.json').open('x') as stream:
            json.dump(payload, stream, indent=2, allow_nan=False)
            stream.write('\n')
        print('SNAPSHOT ' + name + ' through published frame ' + str(frontier), flush=True)
        ready.append(name)
    return {'state': 'all_requested_prefix_windows_retained' if not pending else 'waiting_for_later_prefix',
            'highest_published_chunk_end': frontier, 'ready': ready, 'pending': pending,
            'completion_verified': False, 'epoch': time.time()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--watch', action='store_true')
    parser.add_argument('--max-seconds', type=int, default=7200)
    args = parser.parse_args()
    started = time.monotonic()
    while True:
        result = snapshot_once()
        tmp = OUT / 'prefix_status.tmp'
        tmp.write_text(json.dumps(result, indent=2) + '\n')
        tmp.replace(OUT / 'prefix_status.json')
        print(json.dumps(result), flush=True)
        if not args.watch or not result['pending'] or time.monotonic() - started >= args.max_seconds:
            break
        time.sleep(45)


if __name__ == '__main__':
    main()
