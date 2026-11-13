"""Extract exact source controls from the completed candidate proxy, no inference."""

from pathlib import Path
from fractions import Fraction
from hashlib import file_digest, sha256
import json

import av

ROOT = Path('/home/administrator/Desktop/sport-analytics')
ART = ROOT / 'ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2'
OUT = Path(__file__).resolve().parent


def sha(path):
    with Path(path).open('rb') as source:
        return file_digest(source, 'sha256').hexdigest()


def main():
    summary = json.loads((OUT / 'summary.json').read_text())
    assert summary['status'] == 'completed_independent_fresh_Test1_review_pending_source_classification'
    native = json.loads((OUT / 'native_guard_receipt.json').read_text())
    assert native['status'] == 'passed_actual_candidate_native_strict_completion_guard'
    proxy = ART / 'run/data/media' / native['source_sha256'] / 'proxy.mp4'
    assert sha(proxy) == native['proxy_sha256']
    target = OUT / 'source_evidence'
    target.mkdir(exist_ok=False)
    frames = [753, 3413, 6365, 7801, 7812, 7857, 7859, 8087, 8106, 11333, 13153, 13467, 14103]
    records = []
    for number in frames:
        with av.open(str(proxy)) as container:
            stream = container.streams.video[0]
            stream.thread_count = 1
            pts = int(Fraction(number, 30) / stream.time_base)
            container.seek(pts, stream=stream)
            for frame in container.decode(stream):
                if frame.pts < pts:
                    continue
                assert frame.pts == pts and Fraction(frame.pts) * frame.time_base == Fraction(number, 30)
                path = target / f'frame_{number:05d}.png'
                frame.to_image().save(path)
                records.append({'frame': number, 'seconds': number / 30, 'pts': pts, 'time_base': str(frame.time_base), 'bgr_pixels_sha256': sha256(frame.to_ndarray(format='bgr24').tobytes()).hexdigest(), 'file': path.name, 'sha256': sha(path)})
                break
            else:
                raise ValueError(number)
    assert sha(proxy) == native['proxy_sha256']
    receipt = {'source_sha256': native['source_sha256'], 'proxy_sha256': native['proxy_sha256'], 'proxy_path': str(proxy), 'frames': records, 'source_unchanged': True, 'scope': 'Source-bound agent diagnostic images; no physical ground truth, model inference or image generation'}
    with (target / 'receipt.json').open('x') as output:
        json.dump(receipt, output, indent=2)
        output.write('\n')
    print(json.dumps({'source_controls_extracted': len(records)}))


if __name__ == '__main__':
    main()
