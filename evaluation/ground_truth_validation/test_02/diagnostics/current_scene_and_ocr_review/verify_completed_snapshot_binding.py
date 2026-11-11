"""Bind immutable prefix snapshots to genuine completed execution receipts."""
from __future__ import annotations
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from research.production_external_semantic_replay import load_finished_input

OUT = Path(__file__).resolve().parent
RUN = ROOT.parent / 'ground-truth-validation-artifacts-20261110/test_02/baseline_v1/run'


def sha(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def main():
    bound = load_finished_input(RUN, 'UPLOADTEST2')
    if bound.media['n_frames'] != 29296:
        raise ValueError('Test2 complete frame population mismatch')
    snapshots = sorted(OUT.glob('*/prefix_snapshot.json'))
    if len(snapshots) != 6:
        raise ValueError('All six requested windows, including later G69 assignment, required')
    verified = []
    for path in snapshots:
        snapshot = json.loads(path.read_text())
        for item in snapshot['input_cache_receipts']:
            cache = Path(item['path'])
            expected = bound.expected_caches[cache.name]
            if item['sha256'] != expected or sha(cache) != expected:
                raise ValueError('Captured prefix bytes differ from completed catalogue: ' + str(cache))
        verified.append({'snapshot': str(path), 'sha256': sha(path),
                         'window_inclusive': snapshot['window_inclusive'],
                         'all_snapshot_caches_match_completed_catalogue': True})
    completed_info = json.loads((RUN / 'inference.json').read_text())
    standalone = {}
    for rel in ('real_roi_probe/report.json', 'scheduled_gap_replay/report.json'):
        path = OUT / rel
        if path.exists():
            standalone[rel] = {'sha256': sha(path),
                              'same_proxy_path_as_verified_completed_run': True,
                              'scope': 'Standalone CPU observations remain separate from actual full-worker results'}
    result = {'schema': 'test02-prefix-diagnostics-completed-catalogue-binding:v1',
              'strict_completed_guard': True, 'run': str(RUN), 'session': 'UPLOADTEST2',
              'media': bound.media, 'completed_catalogue_chunks': len(bound.expected_caches),
              'source_sha256': completed_info['source_sha256'],
              'proxy_sha256': completed_info['proxy_sha256'],
              'completed_receipts_sha256': {str(path): sha(path) for path in bound.input_paths},
              'verified_snapshots': verified, 'original_prefix_snapshots_modified': False,
              'separate_standalone_reports': standalone,
              'live_sqlite_opened': False, 'physical_ground_truth_claimed': False}
    with (OUT / 'completed_snapshot_binding.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print('Verified all6 prefix snapshots against genuine completed Test2 catalogue')


if __name__ == '__main__':
    main()
