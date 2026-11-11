"""Deterministic parser history check; no OCR inference or annotation input."""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'sports/badminton/src'))
sys.path.insert(0, str(ROOT / 'engine/src'))
from bai_badminton.perception.scoreboard import PARSER_POLICY, parse_scoreboard

SOURCE = 'sports/badminton/src/bai_badminton/perception/scoreboard.py'
REPORT = ROOT / 'artifacts/benchmarking/experiments/next_test2_fresh_association_scene_v1/ort_ocr_node_probe_v1/report.json'
FIXTURE = ROOT / 'sports/badminton/tests/test_scoreboard_spatial_board.py'


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_old(revision: str):
    source = subprocess.check_output(['git', 'show', f'{revision}:{SOURCE}'], cwd=ROOT)
    module = types.ModuleType('parser_history_' + revision.replace('^', '_parent'))
    sys.modules[module.__name__] = module
    exec(compile(source, f'{revision}:{SOURCE}', 'exec'), module.__dict__)
    return module.parse_scoreboard, source


def summarize(result):
    if result is None:
        return {'status': 'abstained', 'reading': None, 'bounds': None}
    reading, bounds = result
    return {'status': 'reading', 'reading': {'rows': reading.rows, 'conf': reading.conf,
            'frame_idx': reading.frame_idx}, 'bounds': bounds}


def main():
    report = json.loads(REPORT.read_text())
    observation = report['ocr_observations'][0]
    # Existing committed deterministic fixture uses axis-aligned bounding
    # rectangles for the retained model tokens, not original quadrilaterals.
    bounds = [(511, 1, 575, 66), (87, 43, 165, 66), (284, 45, 350, 61),
              (412, 43, 477, 64), (87, 64, 166, 87), (284, 66, 362, 83),
              (411, 65, 493, 84), (353, 136, 437, 165), (90, 148, 160, 174)]
    boxes = [[[x0, y0], [x1, y0], [x1, y1], [x0, y1]]
             for x0, y0, x1, y1 in bounds]
    assert len(boxes) == len(observation['texts']) == len(observation['scores'])
    recorded = summarize(parse_scoreboard(boxes, observation['texts'], observation['scores'], 22924))
    assert recorded['status'] == 'abstained'
    versions = {}
    for revision in ('caa9176', 'b124f42^'):
        parser, source = load_old(revision)
        snapshot = OUT / ('historical_parser_' + revision.replace('^', '_parent') + '.py')
        with snapshot.open('xb') as stream:
            stream.write(source)
        versions[revision] = {'source_sha256': digest(source),
                             'result': summarize(parser(boxes, observation['texts'], observation['scores'], 22924))}
    result = {
        'schema': 'test02-existing-parser-history-diagnostic:v1',
        'no_neural_inference': True,
        'no_annotations_used': True,
        'original_source_sha256': report['source']['original_source_sha256'],
        'source_frame': 22924,
        'source_time_seconds': 22924 / 30,
        'historical_probe_sha256': digest(REPORT.read_bytes()),
        'existing_fixture_sha256': digest(FIXTURE.read_bytes()),
        'geometry_limitation': 'Existing committed regression bounding rectangles; not original OCR quadrilaterals',
        'fixture': {'boxes': boxes, 'texts': observation['texts'], 'scores': observation['scores']},
        'historical_probe_recorded_result': report['parsed_scoreboard_model_observation'],
        'historical_parser_versions': versions,
        'current_parser_policy': PARSER_POLICY,
        'current_parser_sha256': digest((ROOT / SOURCE).read_bytes()),
        'current_parser_result': recorded,
        'conclusion': 'Previously identified logo/athlete score theft is already guarded in current source; no new fix justified from this fixture',
        'physical_score_accuracy_established': False,
        'current_fullvideo_effect_established': False,
    }
    with (OUT / 'parser_history_evidence.json').open('x') as stream:
        json.dump(result, stream, indent=2)
        stream.write('\n')
    print(json.dumps({'current': recorded, 'historical': versions}, indent=2))


if __name__ == '__main__':
    main()
