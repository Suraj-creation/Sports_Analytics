"""Read-only completion provenance and legitimate format transition ordering."""
from pathlib import Path
from hashlib import file_digest
import json
import xml.etree.ElementTree as ET
import msgpack
import numpy as np

OUT=Path(__file__).resolve().parent
CONFIG=json.loads((OUT/'review_config.json').read_text())
ART=Path(CONFIG['artifact_root']);NATIVE=Path(CONFIG['native_root']);MAIN=Path(CONFIG['main_root'])
INPUTS={}

def sha(path):
    with Path(path).open('rb') as f:return file_digest(f,'sha256').hexdigest()

def read(path):INPUTS[str(path)]=sha(path);return json.loads(Path(path).read_text())

def save(name,value):
    with (OUT/name).open('x') as f:json.dump(value,f,indent=2,allow_nan=False);f.write('\n')


def main():
    guard=read(OUT/'native_guard_receipt.json');assert guard['status']=='passed_actual_candidate_native_strict_completion_guard'
    events=ART/'run/events.jsonl';INPUTS[str(events)]=sha(events)
    decisions=[e for e in map(json.loads,events.open()) if e['type']=='format_decision']
    decision=next(e for e in decisions if e['frame_start']==96)
    assert decision['payload']['match_format']=='singles' and decision['payload']['known'] is True
    chunks=[]
    for i in [0,1,2]:
        p=ART/f'run/data/sessions/UPLOADTEST1/perception/seg_{i:05d}.msgpack';INPUTS[str(p)]=sha(p);packet=msgpack.unpackb(p.read_bytes(),raw=False)
        chunks.append({'start':packet['start'],'end':packet['end'],'cached_match_format':packet['ci']['match_format'],'cached_format_confirmed':packet['ci']['layout_format_confirmed'],'context':packet['ci']['layout_format_context']})
    assert chunks[1]['context']=={'match_format':'unknown','confirmed':False}
    assert chunks[2]['context']=={'match_format':'singles','confirmed':True}
    runner=NATIVE/'engine/src/bai_engine/runtime/runner.py';source=runner.read_text();INPUTS[str(runner)]=sha(runner)
    assert 'tmp.write_bytes(self.sport.encode_perception(p))' in source and 'p = self._perceive(dec, k)\n            self.sport.ingest(p)' in source
    save('format_context_transition_review.json',{'status':'explained_valid_transition_no_unresolved_context_mismatch','source_format_confirmation_frame':96,'confirmation_source':'inferred sustained_target_court_format_v1, not annotation or current detector count','chunks':chunks,'ordering':'_perceive writes the cache before _analyse calls sport.ingest. Ingest60–119 establishes singles at96; next perception chunk120 starts with confirmed singles.','raw_audit_field_caveat':'The earlier previous_post_chunk_state comparison uses a stored PRE-INGEST cache identity; its one difference is a legitimate transition, not a proof violation.','weak_barriers_before_confirmation':0,'input_sha256':dict(INPUTS)})
    suites=[]
    for name in ['unit_main_v1','unit_research_v1']:
        directory=OUT.parent/name;complete=read(directory/'completion.json');manifest=read(directory/'manifest.json')
        assert complete['head']==manifest['head']==CONFIG['expected_commit'] and complete['exit_code']==0 and complete['source_hashes_unchanged'] is True
        assert sha(directory/'manifest.json')==complete['manifest_sha256'] and sha(directory/'pytest.log')==complete['log_sha256']
        assert manifest['files_sha256']==complete['after_files_sha256']
        for path,digest in manifest['files_sha256'].items():assert sha(path)==digest
        p=directory/'junit.xml';INPUTS[str(p)]=sha(p);xml=ET.parse(p);counts=[x.attrib for x in xml.findall('.//testsuite')]
        assert all(int(row['failures'])==int(row['errors'])==0 for row in counts)
        suites.append({'suite':name,'test_count':sum(int(row['tests']) for row in counts),'source_files_rehashed':len(manifest['files_sha256']),'head':complete['head'],'failures':0,'errors':0})
    # The registry pins the pose ZIP; additionally fingerprint its one actual
    # staged ONNX graph without importing a model or altering extracted files.
    worker=read(ART/'run/inference.json');assets=[]
    for name,row in worker['models']['artifacts'].items():
        if row.get('status')=='verified_copy':
            p=Path(row['staged_path']);assert sha(p)==row['sha256'];INPUTS[str(p)]=row['sha256'];assets.append({'name':name,'path':str(p),'sha256':row['sha256'],'bytes':p.stat().st_size})
    graphs=list((ART/'run/models/cache/rtmpose_m_body7').rglob('*.onnx'));assert len(graphs)==1
    graph=graphs[0];expected='5c0a4bf67953e6d2ac43ce15e77dc9d5d354ae18430a47d2c5963a7bc5683e3c';assert sha(graph)==expected;INPUTS[str(graph)]=expected
    assets.append({'name':'actual_staged_rtmpose_onnx','path':str(graph),'sha256':expected,'bytes':graph.stat().st_size})
    analysis=read(ART/'analysis/technical_analysis.json')
    for name,row in analysis['models_verified_during_analysis']['package_ocr_artifacts'].items():
        p=Path(row['path']);assert sha(p)==row['sha256'];INPUTS[str(p)]=row['sha256'];assets.append({'name':'RapidOCR_'+name,'path':str(p),'sha256':row['sha256'],'bytes':p.stat().st_size})
    assert all(sha(p)==h for p,h in INPUTS.items())
    save('additional_reproducibility_review.json',{'status':'passed_unit_source_model_and_format_order_review','unit_suites':suites,'total_tests':sum(s['test_count'] for s in suites),'actual_staged_assets':assets,'model_loading_or_new_inference':False,'Test3_content_analysis':False,'input_sha256':INPUTS})

if __name__=='__main__':main()
