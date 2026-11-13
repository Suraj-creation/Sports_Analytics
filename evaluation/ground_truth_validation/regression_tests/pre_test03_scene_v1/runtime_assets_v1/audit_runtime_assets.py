"""Read-only live asset snapshot; never import OCR, load a model, or use network."""

from pathlib import Path
from hashlib import file_digest, sha256
import base64
import csv
import datetime
import email.parser
import importlib.metadata
import json
import os
import re
import sys
import zipfile

import msgpack
import yaml


ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
ART = ROOT / 'ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2'
OUT = Path(__file__).resolve().parent
SITE = MAIN / '.venv/lib/python3.12/site-packages'
RAPID = SITE / 'rapidocr'


def sha(path):
    with Path(path).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def write(name, value):
    with (OUT / name).open('x') as stream:
        json.dump(value, stream, indent=2, allow_nan=False)
        stream.write('\n')


def main():
    assert not (OUT / 'metadata_receipt.json').exists()
    now = datetime.datetime.now(datetime.timezone.utc).isoformat()
    log_path = ART / 'run.execution.log'
    with log_path.open('rb') as stream:
        before = os.fstat(stream.fileno())
        snapshot = stream.read(before.st_size)
        after = os.fstat(stream.fileno())
    assert len(snapshot) == before.st_size
    with (OUT / 'run.execution.asof_v2.log').open('xb') as target:
        target.write(snapshot)
    log = snapshot.decode(errors='replace')
    snapshot_sha = sha256(snapshot).hexdigest()
    inputs = {}

    def bind(path):
        path = Path(path)
        inputs[str(path)] = sha(path)
        return {'path': str(path), 'resolved_path': str(path.resolve()), 'sha256': inputs[str(path)], 'size_bytes': path.stat().st_size}

    cache = ART / 'run/data/sessions/UPLOADTEST1/perception/seg_00000.msgpack'
    packet_bytes = cache.read_bytes()
    packet = msgpack.unpackb(packet_bytes, raw=False)
    assert packet['v'] == 22 and packet['start'] == 0 and packet['end'] == 59
    cache_binding = bind(cache)
    assert cache_binding['sha256'] == sha256(packet_bytes).hexdigest()
    runtimes = packet['ci']['runtimes']
    write('first_closed_cache_runtime_metadata_v2.json', {'cache': cache_binding, 'codec': packet['v'], 'frame_range': [packet['start'], packet['end']], 'models': packet['models'], 'runtimes': runtimes, 'profile': packet['ci']['profile'], 'scope': 'One immutable closed cache segment while overall worker is still live; no completed-run or accuracy claim'})
    plan = read(ART / 'protocol/plan.json')
    plan_binding = bind(ART / 'protocol/plan.json')
    ocr_runtime = runtimes['ocr']
    dist = SITE / 'rapidocr-3.10.0.dist-info'
    metadata = email.parser.Parser().parsestr((dist / 'METADATA').read_text())
    assert metadata['Name'] == 'rapidocr' and metadata['Version'] == ocr_runtime['package_version'] == '3.10.0'
    record = {row[0]: row[1:] for row in csv.reader((dist / 'RECORD').open())}
    package_files = {}
    for path in [dist / 'METADATA', dist / 'RECORD', dist / 'WHEEL', dist / 'INSTALLER', RAPID / 'default_models.yaml', RAPID / 'config.yaml', RAPID / 'utils/download_file.py', RAPID / 'ch_ppocr_rec/main.py', RAPID / 'inference_engine/onnxruntime/main.py']:
        bound = bind(path)
        entry = record.get(str(path.relative_to(SITE)))
        if entry and entry[0]:
            scheme, digest = entry[0].split('=', 1)
            assert scheme == 'sha256'
            assert base64.urlsafe_b64decode(digest + '=' * (-len(digest) % 4)).hex() == bound['sha256']
            assert int(entry[1]) == bound['size_bytes']
        bound['installed_RECORD_entry'] = entry
        bound['RECORD_digest_verified'] = bool(entry and entry[0])
        package_files[str(path.relative_to(SITE))] = bound
    defaults = yaml.safe_load((RAPID / 'default_models.yaml').read_text())
    releases = []

    def walk(value, path=()):
        if isinstance(value, dict):
            if isinstance(value.get('model_dir'), str) and value.get('SHA256'):
                releases.append({'registry_key': list(path), 'release_url_from_local_bundle': value['model_dir'], 'sha256': value['SHA256']})
            for key, child in value.items():
                walk(child, (*path, str(key)))
        elif isinstance(value, list):
            for index, child in enumerate(value):
                walk(child, (*path, str(index)))

    walk(defaults)
    assets = []
    ocr_assets = {}
    for stage, declaration in ocr_runtime['stages'].items():
        path = RAPID / 'models' / declaration['model_file']
        assert str(path) in log
        bound = bind(path)
        assert bound['sha256'] == declaration['sha256']
        entry = record[str(path.relative_to(SITE))]
        scheme, digest = entry[0].split('=', 1)
        assert scheme == 'sha256' and base64.urlsafe_b64decode(digest + '=' * (-len(digest) % 4)).hex() == bound['sha256']
        assert int(entry[1]) == bound['size_bytes']
        declared_release = [row for row in releases if Path(row['release_url_from_local_bundle']).name == path.name and row['sha256'] == bound['sha256']]
        assert declared_release
        value = {'stage': f'ocr_{stage}', 'kind': 'executed_ONNX_model', **bound, 'runtime_declaration': declaration, 'installed_RECORD_entry': entry, 'RECORD_digest_verified': True, 'bundled_release_checksums': declared_release, 'bundled_release_checksum_verified': True, 'external_release_retrieved': False, 'evidence': ['live_log_snapshot', 'closed_cache_runtime', 'current_file', 'installed_RECORD', 'local_default_models_registry']}
        assets.append(value)
        ocr_assets[stage] = value
    manifest_path = ART / 'run/models/manifest.yaml'
    manifest = yaml.safe_load(manifest_path.read_text())['models']
    pins = read(ART / 'run/models/cache/lock.json')
    bind(manifest_path)
    bind(ART / 'run/models/cache/lock.json')
    primary = {}
    for model in ['rfdetr_small', 'rtmpose_m_body7', 'tracknetv3']:
        spec = manifest[model]
        name = Path(spec['source'].get('file') or spec['source']['url']).name
        path = ART / 'run/models/cache' / model / name
        bound = bind(path)
        expected = spec['sha256'] if spec['sha256'] != 'pin-on-first-fetch' else pins[model]
        assert bound['sha256'] == expected
        value = {'stage': model, 'kind': 'verified_archive_container' if path.suffix == '.zip' else 'executed_checkpoint_or_graph', **bound, 'manifest_version': spec['version'], 'expected_registry_or_lock_sha256': expected, 'evidence': ['staged_manifest_and_lock', 'loaded_cache_model_declaration', 'current_file']}
        assets.append(value)
        primary[model] = value
    pose_root = ART / 'run/models/cache/rtmpose_m_body7'
    extractions = list(pose_root.rglob('manifest.json'))
    assert len(extractions) == 1
    extraction_path = extractions[0]
    extraction = read(extraction_path)
    assert extraction['archive_sha256'] == primary['rtmpose_m_body7']['sha256']
    bind(extraction_path)
    extraction_files = []
    with zipfile.ZipFile(primary['rtmpose_m_body7']['path']) as archive:
        assert {row.filename for row in archive.infolist() if not row.is_dir()} == set(extraction['files'])
        for name, expected in extraction['files'].items():
            path = extraction_path.parent / 'files' / name
            bound = bind(path)
            assert bound['sha256'] == expected
            with archive.open(name) as source:
                assert file_digest(source, 'sha256').hexdigest() == expected
            extraction_files.append(bound)
    graph = extraction_path.parent / 'files' / extraction['graph']
    assert str(graph) in log
    graph_binding = bind(graph)
    assets.append({'stage': 'pose_actual_graph', 'kind': 'executed_ONNX_model', **graph_binding, 'parent_archive_sha256': extraction['archive_sha256'], 'archive_member': extraction['graph'], 'archive_member_sha256_verified': True, 'evidence': ['live_log_snapshot', 'verified_extraction_manifest', 'exact_pinned_ZIP_member', 'current_file']})
    histories = []
    for name, relative in [
        ('Test1_baseline', 'ground-truth-validation-artifacts-20261110/test_01/baseline_v1'),
        ('Test1_improved', 'ground-truth-validation-artifacts-20261110/test_01/improved_v1'),
        ('Test2_baseline', 'ground-truth-validation-artifacts-20261110/test_02/baseline_v1'),
        ('Test2_improved', 'ground-truth-validation-artifacts-20261110/test_02/improved_v1'),
        ('Test1_c7_failed_acceptance_control', 'ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01'),
    ]:
        directory = ROOT / relative
        worker_path, analysis_path = directory / 'run/inference.json', directory / 'analysis/technical_analysis.json'
        row = {'run': name, 'path': str(directory), 'ocr': {}, 'extracted_pose_graph': None}
        if worker_path.exists():
            worker = read(worker_path)
            bind(worker_path)
            runtime = worker.get('execution_backends', {}).get('ocr', {})
            row['worker_ocr_package_version'] = runtime.get('package_version')
            for stage, actual in ocr_assets.items():
                declared = runtime.get('stages', {}).get(stage)
                row['ocr'][stage] = {'historical_runtime_declaration': declared, 'historical_model_byte_identity': 'stored_runtime_sha256_matches_current' if declared and declared.get('sha256') == actual['sha256'] else 'UNAVAILABLE_historical_model_hash_absent' if not declared or not declared.get('sha256') else 'DIFFERENT_recorded_model_bytes'}
        else:
            row['worker_metadata_status'] = 'UNAVAILABLE_preserved_worker_not_present_at_this_path'
        if analysis_path.exists():
            analysis = read(analysis_path)
            bind(analysis_path)
            for stage, actual in ocr_assets.items():
                old = analysis.get('models_verified_during_analysis', {}).get('package_ocr_artifacts', {}).get(stage)
                row['ocr'].setdefault(stage, {})['historical_independent_asset_verification'] = old
                row['ocr'][stage]['historical_verified_hash_matches_current'] = old.get('sha256') == actual['sha256'] if old else None
            old_graphs = {path: digest for path, digest in analysis.get('consumed_files_sha256', {}).items() if path.endswith('/end2end.onnx')}
            row['extracted_pose_graph'] = {'stored_graph_fingerprints': old_graphs, 'historical_model_byte_identity': 'stored_graph_sha256_matches_current' if graph_binding['sha256'] in old_graphs.values() else 'UNAVAILABLE_historical_graph_hash_absent'}
        else:
            row['analysis_status'] = 'UNAVAILABLE_preserved_analysis_not_present_at_this_path'
        row['historical_full_package_RECORD_or_code_byte_identity'] = 'UNAVAILABLE_not_established_by_stored_model_hashes_or_version_string'
        histories.append(row)
    versions = {}
    for name in ['rapidocr', 'onnxruntime-gpu', 'torch', 'rtmlib', 'trackers', 'numpy', 'opencv-python', 'opencv-contrib-python']:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    assert all(sha(path) == expected for path, expected in inputs.items())
    with log_path.open('rb') as source:
        assert sha256(source.read(len(snapshot))).hexdigest() == snapshot_sha
    write('metadata_receipt.json', {
        'status': 'read_only_actual_runtime_asset_snapshot_during_live_Test1',
        'captured_utc': now,
        'run_root': str(ART), 'run_still_active_at_capture': True,
        'source_plan_binding': plan_binding, 'recorded_source_commit': plan.get('code_commit'),
        'live_log_snapshot': {'source_path': str(log_path), 'snapshot_path': str(OUT / 'run.execution.asof_v2.log'), 'captured_prefix_bytes': len(snapshot), 'sha256': snapshot_sha, 'source_inode': before.st_ino, 'size_before': before.st_size, 'size_after': after.st_size, 'mtime_ns_before': before.st_mtime_ns, 'mtime_ns_after': after.st_mtime_ns, 'source_prefix_unchanged_at_end': True, 'whole_growing_log_hash_claimed': False},
        'actual_assets': assets,
        'runtime_declarations_from_first_closed_segment': runtimes,
        'loaded_models_from_first_closed_segment': packet['models'],
        'rapidocr_package': {'name': metadata['Name'], 'version': metadata['Version'], 'package_root': str(RAPID), 'dist_info': str(dist), 'record_and_supporting_files': package_files, 'external_release_network_verification': 'NOT_PERFORMED', 'checksum_scope': 'Current local installed RECORD plus RECORD-bound bundled release checksums; not an external signature or independent online release verification'},
        'pose_archive_extraction_members': extraction_files,
        'historical_comparisons': histories,
        'current_package_versions': versions, 'python': {'executable': sys.executable, 'version': sys.version},
        'weightless_or_unavailable_components': {'weightless_loaded': [key for key, value in runtimes.items() if value.get('weights', 'not_explicitly_none') is None] + ['racket_opencv_geometry', 'court_line_calibration', 'rule_contacts_strokes_rallies_scoring'], 'not_claimed_loaded': ['osnet_ain_x0_25', 'racketvision_balltrack', 'wasb_badminton', 'inpaintnet']},
        'recognition_dictionary_scope': 'Current ONNX recognition graph hash covers its embedded metadata. Package source selects embedded character metadata when present; no separate dictionary path is declared in this run runtime receipt. No OCR session was instantiated by this audit; historical standalone dictionary identity is UNAVAILABLE if not separately recorded.',
        'all_bound_asset_and_metadata_inputs_unchanged': True,
        'input_sha256': inputs,
        'new_model_import_inference_download_or_network_by_audit': False,
        'candidate_or_environment_or_asset_or_lock_modified': False,
        'fresh_evaluation_or_metric_claim': False, 'Test3_accessed': False,
        'executed_audit_sha256': sha(__file__),
    })
    print(json.dumps({'status': 'completed_read_only_asset_snapshot', 'model_and_container_assets': len(assets), 'ocr_graphs': len(ocr_assets), 'historical_runs_checked': len(histories), 'log_prefix_bytes': len(snapshot)}))


if __name__ == '__main__':
    main()
