"""Preliminary research-scope regression with explicit evolving-source disclosure."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,xml.etree.ElementTree as ET

OUT=Path(__file__).resolve().parent
ROOT=Path('/home/administrator/Desktop/sport-analytics/test03-scene-overlap-20261112')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def source_hashes():
    paths=subprocess.check_output(['rg','--files','--hidden','-g','*.py','-g','*.toml','-g','*.yaml','-g','*.yml','-g','!.git','-g','!.venv'],cwd=ROOT,text=True).splitlines()
    return {p:sha(ROOT/p) for p in paths if (ROOT/p).is_file()}
def save(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2,allow_nan=False);f.write('\n')
env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']='';env['OMP_NUM_THREADS']='1';env['OPENBLAS_NUM_THREADS']='1';env['PYTHONPATH']=os.pathsep.join(str(ROOT/p) for p in ['sports/badminton/src','engine/src','agents/src','apps/api/src','.'])
imports=subprocess.check_output([str(ROOT/'.venv/bin/python'),'-c','import bai_badminton.engine,bai_engine; print(bai_badminton.engine.__file__); print(bai_engine.__file__)'],cwd=ROOT,env=env,text=True).splitlines()
assert len(imports)==2 and all(Path(x).resolve().is_relative_to(ROOT) for x in imports)
cmd=[str(ROOT/'.venv/bin/python'),'-m','pytest','-c',str(ROOT/'pyproject.toml'),'--rootdir',str(ROOT),'--import-mode=importlib','research/tests','-q','--junitxml='+str(OUT/'junit.xml')]
started=time.time();before=source_hashes();status=subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True)
save(OUT/'manifest.json',{'status':'preliminary_not_authoritative_source_freeze','root':str(ROOT),'scope':['research/tests'],'same_scope_as_prior705_suite':True,'previous705_manifest':'evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1/unit_research_v1/manifest.json','argv':cmd,'PYTHONPATH':env['PYTHONPATH'],'imports':imports,'CUDA_VISIBLE_DEVICES':env['CUDA_VISIBLE_DEVICES'],'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'dirty_status_before':status,'source_sha256_before':before,'started_epoch':started,'python':sys.version,'new_NN':False})
with (OUT/'pytest.log').open('xb') as log:result=subprocess.run(cmd,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,check=False)
after=source_hashes();changed=[p for p in set(before)|set(after) if before.get(p)!=after.get(p)]
stats={}
if (OUT/'junit.xml').exists():
    tree=ET.parse(OUT/'junit.xml');stats={k:sum(int(x.get(k,'0')) for x in tree.iter('testsuite')) for k in ['tests','failures','errors','skipped']}
completion={'status':'preliminary_completed','exit_code':result.returncode,'elapsed_seconds':time.time()-started,'counts':stats,'source_changed_during_run':sorted(changed),'dirty_status_after':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT,text=True),'source_sha256_after':after,'whole_source_frozen_acceptance':False,'log_sha256':sha(OUT/'pytest.log'),'manifest_sha256':sha(OUT/'manifest.json')}
save(OUT/'completion.json',completion)
print(json.dumps({k:v for k,v in completion.items() if k not in ['source_sha256_after','dirty_status_after']},indent=2))
sys.exit(result.returncode)
