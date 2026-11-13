"""Read-only Git/source/symlink preflight. No Git mutation or deletion."""
from pathlib import Path
import hashlib,json,os,subprocess,difflib,collections
OUT=Path(__file__).resolve().parent;MAIN=OUT.parents[4];ROOT=MAIN.parent;FINAL='5ae614826e6f909defb02445386962ac13b4641a'
ENV={**os.environ,'GIT_OPTIONAL_LOCKS':'0'}
def git(p,*args):return subprocess.check_output(['git',*args],cwd=p,env=ENV)
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb')as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def save(n,d):
 with(OUT/n).open('x')as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
def split(z):return[x.decode()for x in z.split(b'\0')if x]
records=[]
for block in git(MAIN,'worktree','list','--porcelain').decode().strip().split('\n\n'):
 d=dict(line.split(' ',1)for line in block.splitlines());p=Path(d['worktree'])
 if p==MAIN:continue
 head=git(p,'rev-parse','HEAD').decode().strip();ancestor=subprocess.run(['git','merge-base','--is-ancestor',head,FINAL],cwd=MAIN,env=ENV).returncode==0
 status=git(p,'status','--porcelain=v1','--untracked-files=all').decode();ignored=split(git(p,'ls-files','--others','--ignored','--exclude-standard','-z'));links=[];extra=[];cats=collections.Counter()
 for rel in ignored:
  f=p/rel
  if f.is_symlink():
   links.append({'path':str(f),'link_text':os.readlink(f),'resolved_target':str(f.resolve()),'target_exists':f.exists(),'target_must_not_be_deleted':True});cats['shared_symlink']+=1
  elif f.suffix=='.pyc':cats['regenerable_pyc']+=1
  elif rel.startswith('.pytest_cache/'):cats['pytest_cache']+=1
  else:
   cats['other_ignored_file']+=1;extra.append({'path':rel,'bytes':f.stat().st_size,'sha256':sha(f)})
 records.append({'path':str(p),'head':head,'branch':d.get('branch'),'ancestor_of_final':ancestor,'status_porcelain':status,'tracked_and_nonignored_untracked_clean':status=='','ignored_total':len(ignored),'ignored_categories':dict(cats),'all_ignored_paths':ignored,'ignored_noncache_nonsymlink_files':extra,'protected_shared_links':links})
assert len(records)==5 and all(r['ancestor_of_final']and r['tracked_and_nonignored_untracked_clean']for r in records)
# Main overlap with incoming tracked delta; hash but never move or modify originals.
changed=split(git(MAIN,'diff','--name-only','main',FINAL,'-z'));mainstatus=git(MAIN,'status','--porcelain=v1','--untracked-files=all').decode();modified=split(git(MAIN,'diff','--name-only','-z'));untracked=split(git(MAIN,'ls-files','--others','--exclude-standard','-z'))
tracked=set(split(git(MAIN,'ls-files','-z')));overlap=[]
for rel in changed:
 p=MAIN/rel
 if rel not in modified and rel not in untracked:continue
 native=ROOT/'test03-scene-overlap-20261112'/rel;row={'path':rel,'main_status':'tracked_modified'if rel in modified else'untracked_incoming_addition','main_sha256':sha(p),'incoming_sha256':sha(native),'byte_equal':p.read_bytes()==native.read_bytes(),'main_bytes':p.stat().st_size,'incoming_bytes':native.stat().st_size}
 if not row['byte_equal']:
  diff=''.join(difflib.unified_diff(p.read_text().splitlines(True),native.read_text().splitlines(True),fromfile='MAIN-current/'+rel,tofile='5ae-incoming/'+rel));name=rel.replace('/','__')+'.diff';(OUT/name).write_text(diff);row['diff_artifact']=name;row['diff_sha256']=sha(OUT/name)
 overlap.append(row)
# Verify every actual recorded source has its exact permanent executed-source archive.
archive_roots=[ROOT/'ground-truth-validation-artifacts-20261111/pre_test03_v1/test_01',ROOT/'ground-truth-validation-artifacts-20261112/pre_test03_v2/test01_candidate_v2',ROOT/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test01_candidate_v4',ROOT/'ground-truth-validation-artifacts-20261112/pre_test03_v4/test02_candidate_v4',ROOT/'ground-truth-validation-artifacts-20261112/pre_test03_v5/test01_candidate_v5']
archives=[]
for run in archive_roots:
 plans=list((run/'protocol').glob('*plan*.json'))
 if not plans:
  for p in (run/'protocol').glob('*.json'):
   try:
    if 'source_files_sha256'in json.loads(p.read_text()):plans.append(p)
   except(ValueError,UnicodeError):pass
 if not plans:archives.append({'root':str(run),'status':'plan_not_found','protocol_exists':(run/'protocol').exists()});continue
 # The worker plan uses absolute original producer source paths.
 plans=[p for p in plans if 'source_files_sha256'in json.loads(p.read_text())]
 for plan in plans:
  d=json.loads(plan.read_text());sources=d['source_files_sha256'];missing=[];bad=[];verified=0;population=[]
  for source,h in sources.items():
   original=Path(source)
   producer=next((Path(r['path'])for r in records if original.is_relative_to(r['path'])),MAIN if original.is_relative_to(MAIN)else None)
   if producer is None:missing.append({'source':source,'reason':'unknown_source_root'});continue
   archive=run/'executed_source'/original.relative_to(producer)
   if not archive.exists():missing.append({'source':source,'expected_archive':str(archive)})
   elif sha(archive)!=h:bad.append({'source':source,'archive':str(archive),'expected_sha256':h,'actual_sha256':sha(archive)})
   else:verified+=1
   population.append({'original':source,'archive':str(archive),'expected_sha256':h})
  archives.append({'root':str(run),'plan':str(plan),'plan_sha256':sha(plan),'status':'all_recorded_sources_archived_exact'if not missing and not bad else'gap','expected_sources':len(sources),'verified':verified,'missing':missing,'hash_mismatches':bad,'population':population})
# Main findings remain in MAIN; excluded new output prevents self-recursive listing.
remaining=[r for r in untracked if not r.startswith(str(OUT.relative_to(MAIN))+'/')]
save('worktree_inventory.json',{'status':'completed_read_only_preflight','final_commit':FINAL,'main_head':git(MAIN,'rev-parse','HEAD').decode().strip(),'main_ancestor_of_final':subprocess.run(['git','merge-base','--is-ancestor','main',FINAL],cwd=MAIN,env=ENV).returncode==0,'auxiliary_worktrees':records,'no_git_mutation':True,'no_deletion':True})
save('main_merge_overlap.json',{'incoming_tracked_delta_paths':changed,'main_tracked_modified_paths':modified,'main_nonignored_untracked_count_excluding_this_output':len(remaining),'main_nonignored_untracked_paths_excluding_this_output':remaining,'main_status_porcelain':mainstatus,'overlaps':overlap,'nonoverlap_modified':[p for p in modified if p not in changed],'source_preservation_executed':False})
save('executed_archive_verification.json',{'recorded_source_archives':archives,'historical_absolute_ROOT_paths_become_unavailable_after_worktree_removal':True,'git_commit_history_preserved_only_after_real_merge_push':True,'no_original_archives_modified':True})
print(json.dumps({'aux_worktrees':len(records),'all_clean':True,'overlaps':len(overlap),'byte_equal':sum(x['byte_equal']for x in overlap),'byte_different':[x['path']for x in overlap if not x['byte_equal']],'archives':[{k:a[k]for k in ['root','status','expected_sources','verified']if k in a}for a in archives]}))
