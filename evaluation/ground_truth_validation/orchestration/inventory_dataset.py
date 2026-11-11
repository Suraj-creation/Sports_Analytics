from pathlib import Path
import csv,json,hashlib,math,collections,subprocess,datetime,zipfile,xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[3];W=R/'evaluation/ground_truth_validation';root=R/'Part2'
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
items=[]
for p in sorted(root.rglob('*')):
 if not p.is_file():continue
 x={'path':str(p),'relative':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':sha(p)}
 if p.suffix.lower()=='.csv':
  with p.open(encoding='utf-8-sig',newline='') as f:
   rd=csv.DictReader(f);fields=rd.fieldnames or [];stats={k:{'missing':0,'numeric_count':0,'nonfinite':0,'minimum':None,'maximum':None,'examples':[],'categories':collections.Counter()} for k in fields};rows=blank=malformed=0;first=[];last=[]
   for row in rd:
    rows+=1;blank+=not any(str(v or '').strip() for v in row.values());malformed+=None in row
    if len(first)<3:first.append(row)
    last=(last+[row])[-3:]
    for k in fields:
     v=row.get(k);s=stats[k]
     if v is None or not str(v).strip():s['missing']+=1;continue
     if v not in s['examples'] and len(s['examples'])<5:s['examples'].append(v)
     if v in s['categories'] or len(s['categories'])<64:s['categories'][v]+=1
     try:
      num=float(v)
      if not math.isfinite(num):s['nonfinite']+=1;continue
      s['numeric_count']+=1;s['minimum']=num if s['minimum'] is None else min(s['minimum'],num);s['maximum']=num if s['maximum'] is None else max(s['maximum'],num)
     except (ValueError,TypeError):pass
  x.update(kind='csv',columns=fields,rows=rows,blank_rows=blank,malformed_rows=malformed,column_profiles=stats,first_rows=first,last_rows=last,category_count_scope='First 64 distinct values retained per column; frequency counts for those retained values only; examples not exhaustive')
 elif p.suffix.lower()=='.json':x.update(kind='json',content=json.loads(p.read_text()))
 elif p.suffix.lower()=='.docx':
  with zipfile.ZipFile(p) as z:
   xml=ET.fromstring(z.read('word/document.xml'));text='\n'.join(''.join(t.itertext()) for t in xml.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}p'))
  q=W/'dataset_inventory/reference_documents'/p.with_suffix('.txt').name;q.parent.mkdir(exist_ok=True);q.write_text(text);x.update(kind='reference_document',extracted_text=str(q))
 items.append(x)
out={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'root':str(root),'originals_read_only':True,'files':items,'tests':[]}
for n in range(1,11):
 files=[x['relative'] for x in items if x['relative'].startswith(f'dataset/Test{n}_Full/')]
 out['tests'].append({'test':n,'dataset_directory':str(root/f'dataset/Test{n}_Full'),'available':bool(files),'files':files,'status':'annotation semantics under review' if files else 'missing annotations; cannot claim evaluation complete'})
(W/'dataset_inventory/dataset_manifest.json').write_text(json.dumps(out,indent=2,allow_nan=False)+'\n')
for n in range(1,11):
 d=W/f'test_{n:02d}'
 for k in ('inputs','references','predictions','metrics','visual_evidence','diagnostics','logs','metadata'): (d/k).mkdir(parents=True,exist_ok=True)
 p=root/f'dataset/Test{n}_Full'
 if p.exists():
  q=d/'references/original_annotations'
  if not q.exists():q.symlink_to(p,target_is_directory=True)
(W/'orchestration/initial_working_tree.patch').write_bytes(subprocess.check_output(['git','diff','--binary'],cwd=R))
(W/'orchestration/initial_git_status.txt').write_bytes(subprocess.check_output(['git','status','--short'],cwd=R))
(W/'orchestration/initial_revision.json').write_text(json.dumps({'commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=R,text=True).strip(),'branch':subprocess.check_output(['git','branch','--show-current'],cwd=R,text=True).strip(),'note':'Inherited modified/untracked improvements are part of actual baseline; commit alone does not reproduce them. Baseline preparation snapshots exact current production source/config/model bindings.'},indent=2)+'\n')
print(json.dumps({'files':len(items),'csvs':sum(x.get('kind')=='csv' for x in items),'missing_annotation_tests':[x['test'] for x in out['tests'] if not x['available']]}))
