"""Read-only supplemental source overlays for changed Test2 semantic anchors."""
from pathlib import Path
import collections
import hashlib
import json
import av
import cv2
import msgpack
import numpy as np
from review_semantic_effects import HERE, EXTERNAL, sha, read, live, draw

def main():
    cv2.setNumThreads(1)
    baseline = EXTERNAL / 'test_02/baseline_v1'
    experiment = EXTERNAL / 'test_02/test2_semantic_regression_v1'
    completion = read(experiment / 'completion.json')
    assert completion['status'] == 'completed_controlled_semantic_regression' and completion['test'] == 2
    manifest_path = experiment / 'replay/replay_manifest.json'
    events_path = experiment / 'replay/current-events.jsonl'
    for path in (manifest_path, events_path):
        assert sha(path) == completion['artifact_sha256'][str(path.relative_to(experiment))]
    manifest = read(manifest_path)
    source_sha = read(baseline / 'run/inference.json')['source_sha256']
    assert source_sha == '4d687b4240fd501fb723c50588ecd095b9d9863299108c9d43b77c9587ba3c0a'
    frames = {12456, 22656, 27618, 28828}
    output = HERE / 'semantic_effect_evidence/test_02_supplement'
    assert not output.exists()
    warnings = collections.defaultdict(list)
    for event in live(events_path):
        if event['type'] == 'racket_observation_ambiguity' and event['frame_start'] in frames:
            warnings[event['frame_start']].append(event)
    sid = read(baseline / 'run/session.json')['session_id']
    raw_frames = {}
    hashes = {str(path): sha(path) for path in (Path(__file__), HERE/'review_semantic_effects.py', experiment/'completion.json', manifest_path, events_path)}
    for path in sorted((baseline / 'run/data/sessions' / sid / 'perception').glob('*.msgpack')):
        chunk = msgpack.unpackb(path.read_bytes(), raw=False)
        if any(chunk['start'] <= f <= chunk['end'] for f in frames):
            assert sha(path) == manifest['cache_sha256'][path.name]
            hashes[str(path)] = sha(path)
            raw_frames.update({row['f']: row for row in chunk['frames'] if row['f'] in frames})
    assert raw_frames.keys() == frames
    proxy = baseline / 'run/data/media' / source_sha / 'proxy.mp4'
    hashes[str(proxy)] = sha(proxy)
    output.mkdir()
    (output/'executed_renderer.py').write_bytes(Path(__file__).read_bytes())
    results = []
    with av.open(str(proxy)) as container:
        container.streams.video[0].thread_count = 1
        for index, frame in enumerate(container.decode(video=0)):
            if index in frames:
                pixels = frame.to_ndarray(format='bgr24')
                raw = raw_frames[index]
                withheld = {e['payload']['owner_track_id'] for e in warnings[index]}
                overlay = np.concatenate((draw(pixels, raw, set(), 'Original raw geometric racket candidates'), draw(pixels, raw, withheld, 'New semantic admission (same raw pixels/observations)')), axis=1)
                path = output / f'frame_{index:05d}_raw_vs_semantic.png'
                cv2.imwrite(str(path), overlay)
                (output/f'frame_{index:05d}_raw_and_admission.json').write_text(json.dumps({'raw': raw, 'ambiguity_events': warnings[index]}, indent=2)+'\n')
                results.append({'frame': index, 'seconds': index/30, 'overlay': path.name, 'sha256': sha(path), 'source_pixels_sha256': hashlib.sha256(pixels.tobytes()).hexdigest(), 'withheld_tracks': sorted(withheld)})
            if index >= max(frames):
                break
    assert len(results) == len(frames)
    assert all(sha(path) == value for path, value in hashes.items())
    (output/'receipt.json').write_text(json.dumps({'status': 'completed', 'scope': 'Supplemental unchanged-source overlays; no inference or physical GT', 'input_sha256': hashes, 'images': results}, indent=2)+'\n')
    print(json.dumps({'status': 'completed', 'output': str(output), 'images': len(results)}))

if __name__ == '__main__':
    main()
