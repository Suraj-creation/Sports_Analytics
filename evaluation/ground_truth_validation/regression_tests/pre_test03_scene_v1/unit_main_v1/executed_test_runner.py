"""Record an immutable source-bound run of the existing regression suites."""
import argparse, hashlib, importlib.metadata, json, os, platform, shutil, subprocess, sys, time
from pathlib import Path
import xml.etree.ElementTree as ET

parser=argparse.ArgumentParser()
parser.add_argument('--root',type=Path,required=True)
parser.add_argument('--suite',choices=['main','research'],required=True)
parser.add_argument('--output',type=Path,required=True)
a=parser.parse_args();root=a.root.resolve();out=a.output.resolve()
assert root.is_dir() and not out.exists()
status=subprocess.check_output(['git','status','--porcelain'],cwd=root,text=True)
assert not status,'Freeze and commit the candidate before tests'
files=[root/p for p in subprocess.check_output(['git','ls-files'],cwd=root,text=True).splitlines() if p.endswith(('.py','.toml','.yaml','.yml'))]
def hashes():return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
env=os.environ.copy();env['PYTHONPATH']=os.pathsep.join(str(root/p) for p in ['sports/badminton/src','engine/src','agents/src','apps/api/src','.'])
probe='import bai_badminton.engine,bai_engine;print(bai_badminton.engine.__file__);print(bai_engine.__file__)'
imports=subprocess.check_output([str(root/'.venv/bin/python'),'-c',probe],cwd=root,env=env,text=True).splitlines()
assert len(imports)==2 and all(Path(p).resolve().is_relative_to(root) for p in imports)
scopes=['engine/tests','sports/badminton/tests','agents/tests','apps/api/tests','tests/benchmarking'] if a.suite=='main' else ['research/tests']
out.mkdir(parents=True);shutil.copy2(__file__,out/'executed_test_runner.py')
cmd=[str(root/'.venv/bin/python'),'-m','pytest',*scopes,'-q','--junitxml='+str(out/'junit.xml')]
before=hashes();started=time.time()
meta={'argv':cmd,'cwd':str(root),'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'git_status':status,'PYTHONPATH':env['PYTHONPATH'],'CUDA_VISIBLE_DEVICES':env.get('CUDA_VISIBLE_DEVICES'),'imports':imports,'python':sys.version,'platform':platform.platform(),'pytest':importlib.metadata.version('pytest'),'started_epoch':started,'files_sha256':before}
(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
print(json.dumps({'started':a.suite,'output':str(out),'head':meta['head'],'source_files':len(before)}),flush=True)
with (out/'pytest.log').open('xb') as log:
 result=subprocess.run(cmd,cwd=root,env=env,stdout=log,stderr=subprocess.STDOUT,check=False)
after=hashes();changed=[p for p in before if before[p]!=after[p]]
stats={}
if (out/'junit.xml').exists():
 tree=ET.parse(out/'junit.xml');stats={k:sum(int(x.get(k,'0')) for x in tree.iter('testsuite')) for k in ['tests','failures','errors','skipped']}
completion={'suite':a.suite,'head':meta['head'],'exit_code':result.returncode,'elapsed_seconds':time.time()-started,'changed_source_files':changed,'source_hashes_unchanged':not changed,'junit_counts':stats,'manifest_sha256':hashlib.sha256((out/'manifest.json').read_bytes()).hexdigest(),'log_sha256':hashlib.sha256((out/'pytest.log').read_bytes()).hexdigest(),'after_files_sha256':after}
(out/'completion.json').write_text(json.dumps(completion,indent=2)+'\n');print(json.dumps({k:v for k,v in completion.items() if k!='after_files_sha256'}),flush=True)
sys.exit(result.returncode if not changed else 2)
