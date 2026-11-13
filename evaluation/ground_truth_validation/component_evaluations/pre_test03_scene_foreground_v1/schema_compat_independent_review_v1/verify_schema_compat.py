"""Independent read-only byte/AST/pin verification of the three schema helpers.

Original annotations are hashed as opaque bytes only. No inference, evaluation,
annotation inventory, original output, tested helper or production edit occurs.
"""

from pathlib import Path
from hashlib import file_digest, sha256
import ast
import copy
import datetime
import json
import subprocess


ROOT = Path('/home/administrator/Desktop/sport-analytics')
MAIN = ROOT / 'Sports_Analytics'
CANDIDATE = ROOT / 'test03-scene-continuity-20261112'
OUT = Path(__file__).resolve().parent
PROPOSAL = OUT.parent / 'catalogue_codec22_proposal_v1'
REVISIONS = ('dacc05e', 'c7cf871')
EVALUATORS = [
    'scripts/benchmarking/evaluate_rallies.py',
    'research/test2_evaluation.py',
    'research/pipeline_repair_evaluation.py',
    'research/pipeline_repair_run_analysis.py',
    'research/production_external_semantic_replay.py',
    'evaluation/ground_truth_validation/orchestration/evaluate_test01_components.py',
    'evaluation/ground_truth_validation/orchestration/evaluate_test02_components.py',
]


def sha(path):
    with Path(path).open('rb') as stream:
        return file_digest(stream, 'sha256').hexdigest()


def read(path):
    return json.loads(Path(path).read_text())


def git_blob(revision, relative):
    return subprocess.check_output(['/usr/bin/git', '-C', str(CANDIDATE), 'show', f'{revision}:{relative}'])


def dump(node):
    return ast.dump(node, include_attributes=False)


def functions(tree):
    return {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}


class OldContext(ast.NodeTransformer):
    def visit_Compare(self, node):
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.NotIn) and isinstance(node.comparators[0], ast.Name) and node.comparators[0].id == 'accepted_versions':
            node.ops = [ast.NotEq()]
            node.comparators = [ast.Constant(21)]
        return self.generic_visit(node)

    def visit_JoinedStr(self, node):
        if any(isinstance(item, ast.FormattedValue) and isinstance(item.value, ast.Name) and item.value.id == 'context_label' for item in node.values):
            return ast.Constant('codec21 source profile/model/media identity mismatch')
        return self.generic_visit(node)


class OldCodecTest(ast.NodeTransformer):
    def visit_Compare(self, node):
        if len(node.ops) == 1 and isinstance(node.ops[0], ast.In) and isinstance(node.comparators[0], ast.Tuple) and ast.literal_eval(node.comparators[0]) == (21, 22):
            assert dump(node.left) == dump(ast.parse('value["v"]', mode='eval').body)
            node.ops = [ast.Eq()]
            node.comparators = [ast.Constant(21)]
        return self.generic_visit(node)


class OldNormalCall(ast.NodeTransformer):
    def visit_Name(self, node):
        if node.id == 'validate_completed_cache':
            node.id = 'validate_cache21'
        return node

    def visit_ImportFrom(self, node):
        for alias in node.names:
            if alias.name == 'validate_completed_cache':
                alias.name = 'validate_cache21'
        return node


def main():
    receipt_path = OUT / 'receipt_final.json'
    assert not receipt_path.exists()
    applied = read(PROPOSAL / 'applied_receipt.json')
    inputs = {str(PROPOSAL / name): sha(PROPOSAL / name) for name in ['applied_receipt.json', 'schema_only_codec22.patch']}
    assert inputs[str(PROPOSAL / 'schema_only_codec22.patch')] == applied['exact_patch_sha256']
    candidate_head = subprocess.check_output(['/usr/bin/git', '-C', str(CANDIDATE), 'rev-parse', 'HEAD'], text=True).strip()
    requested_head = '0af9f40dfdae23fd3428b7f02cbfcd0faa2e9c8e'
    revision_delta = subprocess.check_output(['/usr/bin/git', '-C', str(CANDIDATE), 'diff', '--name-only', requested_head, candidate_head], text=True).splitlines()
    assert revision_delta in [[], ['sports/badminton/tests/test_player_tracker_birth_activation.py']]
    unchanged = []
    for relative in EVALUATORS:
        data = (MAIN / relative).read_bytes()
        fingerprint = sha256(data).hexdigest()
        original_ast = dump(ast.parse(data))
        bindings = {'main': fingerprint, 'candidate': sha(CANDIDATE / relative)}
        assert bindings['candidate'] == fingerprint
        for revision in REVISIONS:
            blob = git_blob(revision, relative)
            bindings[revision] = sha256(blob).hexdigest()
            assert blob == data and dump(ast.parse(blob)) == original_ast
        unchanged.append({'file': relative, 'sha256': bindings, 'complete_AST_equal': True})
        inputs[str(MAIN / relative)] = fingerprint
        inputs[str(CANDIDATE / relative)] = fingerprint
    helper_checks = []
    parsed = {}
    for relative, record in applied['files'].items():
        original = (PROPOSAL / 'original_sources' / relative).read_bytes()
        current = (MAIN / relative).read_bytes()
        assert sha256(original).hexdigest() == record['original_sha256']
        assert sha256(current).hexdigest() == record['proposed_sha256'] == sha(CANDIDATE / relative)
        assert current == (PROPOSAL / 'proposed_sources' / relative).read_bytes()
        for revision in REVISIONS:
            assert git_blob(revision, relative) == original
        old, new = ast.parse(original), ast.parse(current)
        parsed[relative] = old, new
        old_functions, new_functions = functions(old), functions(new)
        changed = [name for name in old_functions.keys() & new_functions.keys() if dump(old_functions[name]) != dump(new_functions[name])]
        helper_checks.append({'file': relative, **record, 'main_candidate_proposed_bytes_equal': True, 'dacc05e_c7_original_bytes_equal': True, 'changed_existing_functions': sorted(changed), 'new_functions': sorted(new_functions.keys() - old_functions.keys())})
        for base in [MAIN, CANDIDATE]:
            inputs[str(base / relative)] = record['proposed_sha256']
    old, new = parsed['research/pipeline_repair_completion.py']
    a, b = functions(old), functions(new)
    context = OldContext().visit(copy.deepcopy(b['_validate_cache_context']))
    context.name, context.args = a['validate_cache21'].name, copy.deepcopy(a['validate_cache21'].args)
    assert dump(context) == dump(a['validate_cache21'])
    assert all(dump(a[name]) == dump(b[name]) for name in a if name != 'validate_cache21')
    for name, accepted in [('validate_cache21', (21,)), ('validate_completed_cache', (21, 22))]:
        body = b[name].body
        assert isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant)
        call = body[1].value
        assert isinstance(body[1], ast.Return) and isinstance(call, ast.Call) and call.func.id == '_validate_cache_context'
        assert next(ast.literal_eval(item.value) for item in call.keywords if item.arg == 'accepted_versions') == accepted
    for name in ['decode_source_pts', 'verify_proxy', 'cache_catalog']:
        assert dump(a[name]) == dump(b[name])
    old, new = parsed['research/normal_timestamp_audit.py']
    assert dump(OldNormalCall().visit(copy.deepcopy(new))) == dump(old)
    old, new = parsed['research/production_external_stress.py']
    a, b = functions(old), functions(new)
    assert dump(OldCodecTest().visit(copy.deepcopy(b['perception_catalog']))) == dump(a['perception_catalog'])
    assert all(dump(a[name]) == dump(b[name]) for name in a if name not in ['perception_catalog', 'verify_perception_catalog'])
    # Prove that only the historical-policy normalization block changed in the
    # catalogue verifier; hash/population/header/receipt guards stay exact.
    verifier = copy.deepcopy(b['verify_perception_catalog'])
    old_verifier = a['verify_perception_catalog']
    old_blocks = [node for node in old_verifier.body if (isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'legacy_limits' for t in node.targets)) or (isinstance(node, ast.If) and 'legacy_limits' in ast.unparse(node.test))]
    assert len(old_blocks) == 2
    loop = next(node for node in verifier.body if isinstance(node, ast.For) and isinstance(node.target, ast.Name) and node.target.id == 'historical_versions')
    assert ast.literal_eval(loop.iter) == ([20], [20, 21])
    index = verifier.body.index(loop)
    verifier.body[index:index + 1] = copy.deepcopy(old_blocks)
    assert dump(verifier) == dump(old_verifier)
    # Exercise only that pure metadata-normalization block on synthetic values.
    limit_node = next(node.value for node in new.body if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == 'PERCEPTION_CATALOG_LIMITS' for t in node.targets))
    # This inspected module constant contains only strings, lists and integer
    # arithmetic (byte limits). Do not import the tested helper or execute I/O.
    assert all(isinstance(node, (ast.Dict, ast.List, ast.Constant, ast.BinOp, ast.Mult, ast.Pow, ast.Load)) for node in ast.walk(limit_node))
    limits = eval(compile(ast.Expression(limit_node), '<inspected_literal_byte_limits>', 'eval'), {'__builtins__': {}}, {})
    code = compile(ast.fix_missing_locations(ast.Module(body=[copy.deepcopy(loop)], type_ignores=[])), '<isolated_historical_catalogue_normalization>', 'exec')
    populations = [(20,), (21,), (20, 21), (22,), (20, 22)]
    normalization = []
    for recorded_versions in [[20], [20, 21]]:
        for population in populations:
            recorded = {'schema': 'perception-cache-catalog:v1', 'limits': {**limits, 'accepted_codec_versions': recorded_versions}}
            observed = {'limits': copy.deepcopy(limits), 'files': [{'codec_version': version} for version in population]}
            environment = {'PERCEPTION_CATALOG_LIMITS': limits, 'PERCEPTION_CATALOG_SCHEMA': recorded['schema'], 'recorded': recorded, 'observed': observed}
            exec(code, environment)
            normalized = observed['limits']['accepted_codec_versions'] == recorded_versions
            assert normalized == all(version in recorded_versions for version in population)
            normalization.append({'published_versions': recorded_versions, 'actual_population': population, 'historical_policy_normalized': normalized})
    manifest_path = MAIN / 'evaluation/ground_truth_validation/dataset_inventory/dataset_manifest.json'
    inventory = read(manifest_path)
    assert len(inventory['files']) == 62
    annotations = []
    for entry in inventory['files']:
        # Opaque byte hashing only: no Test3 annotation parsing or inventory.
        assert sha(entry['path']) == entry['sha256'] and Path(entry['path']).stat().st_size == entry['bytes']
        annotations.append({key: entry[key] for key in ['relative', 'bytes', 'sha256']})
        inputs[entry['path']] = entry['sha256']
    inputs[str(manifest_path)] = sha(manifest_path)
    pin_files = subprocess.check_output(['/usr/bin/git', '-C', str(CANDIDATE), 'ls-files', 'config', 'models/manifest.yaml'], text=True).splitlines()
    pins = []
    for relative in pin_files:
        data = (MAIN / relative).read_bytes()
        digest = sha256(data).hexdigest()
        assert (CANDIDATE / relative).read_bytes() == data
        assert all(git_blob(revision, relative) == data for revision in REVISIONS)
        pins.append({'file': relative, 'sha256': digest, 'main_candidate_dacc05e_c7_bytes_equal': True})
        inputs[str(MAIN / relative)] = inputs[str(CANDIDATE / relative)] = digest
    lock_path = MAIN / 'models/cache/lock.json'
    lock_hash = sha(lock_path)
    assert sha(CANDIDATE / 'models/cache/lock.json') == lock_hash
    old_worker_path = ROOT / 'ground-truth-validation-artifacts-20261110/test_01/improved_v1/run/inference.json'
    old_worker = read(old_worker_path)
    baseline_plan_path = old_worker_path.parents[1] / 'protocol/plan.json'
    baseline_plan = read(baseline_plan_path)
    baseline_lock_key = str(lock_path)
    assert baseline_plan['input_files_sha256'][baseline_lock_key] == lock_hash
    canonical_pin_value_hash = sha256(json.dumps(read(lock_path), sort_keys=True).encode()).hexdigest()
    assert old_worker['models']['pins_sha256'] == canonical_pin_value_hash
    staged_lock_path = old_worker_path.parent / 'models/cache/lock.json'
    staged_lock_hash = sha(staged_lock_path)
    staged_pins = read(staged_lock_path)
    current_pins = read(lock_path)
    assert staged_pins == current_pins and len(current_pins) == 8
    assert old_worker['models']['manifest_sha256'] == sha(MAIN / 'models/manifest.yaml')
    actual_weights = []
    for model in ['rfdetr_small', 'rtmpose_m_body7', 'tracknetv3']:
        entry = old_worker['models']['artifacts'][model]
        candidate_path = CANDIDATE / Path(entry['source_path']).relative_to(MAIN)
        assert sha(entry['source_path']) == sha(candidate_path) == entry['sha256']
        actual_weights.append({'model': model, 'sha256': entry['sha256'], 'main_candidate_saved_completed_run_equal': True})
        inputs[entry['source_path']] = inputs[str(candidate_path)] = entry['sha256']
    inputs[str(lock_path)] = inputs[str(CANDIDATE / 'models/cache/lock.json')] = lock_hash
    inputs[str(staged_lock_path)] = staged_lock_hash
    inputs[str(old_worker_path)] = sha(old_worker_path)
    inputs[str(baseline_plan_path)] = sha(baseline_plan_path)
    assert all(sha(path) == value for path, value in inputs.items())
    result = {
        'status': 'passed_independent_schema_only_compatibility_review',
        'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'candidate_commit': candidate_head,
        'requested_candidate_commit': requested_head,
        'committed_delta_since_requested_candidate': revision_delta,
        'committed_production_helper_profile_delta_since_requested_candidate': False,
        'main_head': subprocess.check_output(['/usr/bin/git', '-C', str(MAIN), 'rev-parse', 'HEAD'], text=True).strip(),
        'unchanged_evaluator_byte_and_AST_bindings': unchanged,
        'three_helper_byte_bindings': helper_checks,
        'old_validation_context_preserved_except_version_parameter_and_error_label': True,
        'historical_cache21_wrapper_accepts_only': [21],
        'normal_completed_cache_wrapper_accepts_only': [21, 22],
        'source_PTS_proxy_and_recovery_catalogue_function_AST_unchanged': True,
        'normal_timestamp_module_AST_identical_after_validator_rename_only': True,
        'catalogue_other_guards_function_AST_unchanged_after_normalization_block_substitution': True,
        'historical_catalogue_normalization_controls': normalization,
        'original_dataset_manifest_files': annotations,
        'original_file_count': 62,
        'Test3_access_scope': 'Only opaque byte-hash/size integrity of paths already in the existing62-file manifest; no annotation content parsing or new inventory',
        'unchanged_profile_and_model_registry_pins': pins,
        'model_lock_sha256': lock_hash,
        'model_lock_serialization_scope': {
            'current_main_candidate_bytes_equal': True,
            'baseline_plan_path': str(baseline_plan_path),
            'baseline_plan_input_files_absolute_lock_key': baseline_lock_key,
            'baseline_plan_raw_source_lock_sha256': baseline_plan['input_files_sha256'][baseline_lock_key],
            'old_worker_recorded_canonical_pin_value_sha256': old_worker['models']['pins_sha256'],
            'recomputed_canonical_pin_value_sha256': canonical_pin_value_hash,
            'retained_original_staged_lock_sha256': staged_lock_hash,
            'current_lock_sha256': lock_hash,
            'old_staged_current_eight_model_pin_maps_equal': True,
            'original_plan_MAIN_candidate_source_lock_bytes_equal': True,
            'reason': 'Original plan raw input bytes and both current source locks agree. Worker pins_sha256 hashes the sorted JSON pin values; staged JSON is a third separately hashed serialization of the same eight pins.',
        },
        'actual_saved_model_artifact_hashes': actual_weights,
        'all_consumed_inputs_unchanged': True,
        'neural_inference_or_evaluation_run_performed': False,
        'production_helpers_tests_or_annotations_modified_by_review': False,
        'numeric_scoring_matching_thresholds_changed': False,
        'input_sha256': inputs,
        'executed_review_sha256': sha(__file__),
    }
    with receipt_path.open('x') as stream:
        json.dump(result, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps({'status': result['status'], 'unchanged_evaluators': len(unchanged), 'helpers': len(helper_checks), 'opaque_original_hashes': len(annotations), 'profile_model_pin_files': len(pins), 'normalization_controls': len(normalization)}))


if __name__ == '__main__':
    main()
