"""Read-only schema23 helper review; no labels, predictions, worker or inference."""
from pathlib import Path
from hashlib import file_digest
import ast
import json

ROOT=Path('/home/administrator/Desktop/sport-analytics')
MAIN=ROOT/'Sports_Analytics'
CANDIDATE=ROOT/'test03-scene-acquisition-20261112'
OUT=Path(__file__).resolve().parent
PRIOR=MAIN/'evaluation/ground_truth_validation/component_evaluations/pre_test03_scene_foreground_v1'
RECEIPT=PRIOR/'schema_compat_independent_review_v1/receipt_final.json'
PROPOSED=PRIOR/'catalogue_codec22_proposal_v1/proposed_sources'


def sha(path):
    with path.open('rb') as f:return file_digest(f,'sha256').hexdigest()


def syntax(s):return ast.dump(ast.parse(s),include_attributes=False)


def main():
    prior=json.loads(RECEIPT.read_text());assert prior['status']=='passed_independent_schema_only_compatibility_review'
    methods=[]
    for row in prior['unchanged_evaluator_byte_and_AST_bindings']:
        rel=row['file'];expected=row['sha256']['main'];a,b=MAIN/rel,CANDIDATE/rel
        assert sha(a)==sha(b)==expected
        assert syntax(a.read_text())==syntax(b.read_text())
        methods.append({'file':rel,'main_candidate_prior_sha256':expected,'complete_AST_unchanged':True})
    helper=[]
    for name in ['normal_timestamp_audit.py','pipeline_repair_completion.py','production_external_stress.py']:
        rel='research/'+name;old=(PROPOSED/rel).read_text();a,b=MAIN/rel,CANDIDATE/rel
        assert sha(a)==sha(b)
        current=a.read_text();normalized=current
        if name=='pipeline_repair_completion.py':
            normalized=normalized.replace('accepted_versions=(21, 22, 23), context_label="completed codec21/22/23"', 'accepted_versions=(21, 22), context_label="completed codec21/22"')
        if name=='production_external_stress.py':
            normalized=normalized.replace('"accepted_codec_versions": [20, 21, 22, 23]', '"accepted_codec_versions": [20, 21, 22]')
            normalized=normalized.replace('if value["v"] in (21, 22, 23):','if value["v"] in (21, 22):')
            normalized=normalized.replace('for historical_versions in ([20], [20, 21], [20, 21, 22]):','for historical_versions in ([20], [20, 21]):')
        assert normalized==old and syntax(normalized)==syntax(old)
        helper.append({'file':rel,'main_candidate_sha256':sha(a),'prior_codec22_sha256':sha(PROPOSED/rel),'identical_after_only_predeclared_schema23_edits':True})
    result={'status':'passed_independent_schema23_helper_math_review','prior_receipt_sha256':sha(RECEIPT),'methods':methods,'helpers':helper,'scoring_matching_tolerances_unchanged':True,'PTS_proxy_alignment_functions_unchanged':True,'historical_validate_cache21_still21_only':True,'normal_completed_versions':[21,22,23],'catalogue_versions':[20,21,22,23],'historical_limit_normalization_still_requires_actual_population_subset':True,'Test3_data_access':False,'new_inference_or_evaluation':False,'review_script_sha256':sha(Path(__file__))}
    with (OUT/'helper_review.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'methods_unchanged':len(methods),'helpers_schema_only':len(helper)}))

if __name__=='__main__':main()
