"""Independent source-bound pixel and whole native24 structural review; CPU only."""
from pathlib import Path
import hashlib,json,subprocess
import numpy as np,cv2
from PIL import Image,ImageOps,ImageDraw
from evaluation.ground_truth_validation.orchestration.analyse_native_completed_run import load_native_interfaces,require_recorded_producer
OUT=Path(__file__).resolve().parent;MAIN=OUT.parents[4];NATIVE=MAIN.parent/'test03-scene-overlap-20261112';RUN=MAIN.parent/'ground-truth-validation-artifacts-20261112/pre_test03_v5/test01_candidate_v5/run';PKG=OUT.parent/'visual_test01_v5_new_reset_v1'
cache={}
def sha(p):
 p=Path(p).resolve()
 if p not in cache:
  h=hashlib.sha256()
  with p.open('rb')as f:
   for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
  cache[p]=h.hexdigest()
 return cache[p]
def read(p):return json.loads(Path(p).read_text())
def save(n,d):
 with(OUT/n).open('x')as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=NATIVE,text=True).strip()=='5ae614826e6f909defb02445386962ac13b4641a';assert subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=NATIVE,text=True)==''
d=read(PKG/'completion.json');assert d['status']=='completed'and d['frames']==list(range(14110,14119))
for rel,h in d['artifact_sha256'].items():assert sha(PKG/rel)==h,(rel,h)
for row in d['input_bindings']:assert sha(row['path'])==row['sha256'],row['path']
observations=[]
for frame in d['frames']:
 p=PKG/f'frame_{frame:07d}';e=read(p/'evidence.json');im=cv2.imread(str(p/'source_original.png'));assert list(im.shape)==e['source_decode']['shape']and hashlib.sha256(im.tobytes()).hexdigest()==e['source_decode']['pixels_sha256']
 out={'frame':frame,'source':e['source_decode'],'seconds':e['seconds_rational'],'arms':{}}
 for arm in ['baseline','current']:
  a=e['arms'][arm];im=cv2.imread(str(p/f'{arm}_proxy.png'));assert hashlib.sha256(im.tobytes()).hexdigest()==a['proxy_decode']['pixels_sha256']and list(im.shape)==a['proxy_decode']['shape'];assert a['proxy_decode']['seconds_rational']==e['seconds_rational']
  for k in ['cache_original','cache_snapshot']:assert sha(a[k]['path'])==a[k]['sha256']
  raw=read(p/f'{arm}_raw_frame.json');out['arms'][arm]={'epoch':raw['ce'],'players':raw['p'],'foreground':raw.get('fg'),'raw_scene':raw.get('cc'),'decision':raw.get('cd'),'models':a['models'],'cache_original':a['cache_original']}
 observations.append(out)
for start in [0,3,6]:
 select=d['frames'][start:start+3];im=Image.new('RGB',(1920,34+3*384),(12,12,12));dr=ImageDraw.Draw(im);dr.text((8,8),'SOURCE | BASELINE original improved_v1 | CURRENT actual5ae fullNN | diagnostic only',fill='white')
 for i,f in enumerate(select):
  for j,n in enumerate(['source_original.png','baseline_source_overlay.png','current_source_overlay.png']):
   a=Image.open(PKG/f'frame_{f:07d}'/n).convert('RGB');t=ImageOps.contain(a,(640,360));im.paste(t,(j*640+(640-t.width)//2,34+i*384+24+(360-t.height)//2));dr.text((j*640+8,34+i*384+5),f'{f} {f/30:.6f}s '+['source','baseline','current'][j],fill='white')
 im.save(OUT/f'sheet_{start//3+1:02d}.jpg',quality=95)
save('source_verification.json',{'status':'passed','package_completion_sha256':sha(PKG/'completion.json'),'artifacts_verified':len(d['artifact_sha256']),'input_bindings_verified':len(d['input_bindings']),'source_proxy_pixel_receipts':27,'frame_evidence':observations,'input_sha256':{str(p):h for p,h in cache.items()},'physical_gt':None})
# Source-native interfaces: no ROOT rebasing, no modified numerical helper, all frames/chunks decoded.
original,auditor,decoder,prov=load_native_interfaces(NATIVE,NATIVE)
assert auditor.AUDIT_VERSION=='source-native-scene-epoch-audit:v4'
bound=original.load_analysis_input(RUN,None);require_recorded_producer(bound,NATIVE,original)
consumed={};chunks,frames=original.load_chunks(Path(bound['cache_dir']),bound['cache_sha256'],consumed)
assert bound['media']['n_frames']==17268 and all(c['v']==24 for c in chunks)
report,rows,proof=auditor.audit_frames(frames,17268,packets=chunks,decode_packet=decoder)
for path,digest in prov['source_sha256'].items():assert sha(path)==digest
assert subprocess.check_output(['git','diff','--name-only','HEAD'],cwd=NATIVE,text=True)==''
save('whole_native_structural_review.json',{'status':'passed_actual_native_complete_frame_proof','producer_root':str(NATIVE),'producer_commit':'5ae614826e6f909defb02445386962ac13b4641a','bound_completion_mode':bound['completion_mode'],'all_packets_codec24':True,'packet_count':len(chunks),'frame_count':len(frames),'structural_proof':proof,'frame_report':report,'native_interface_provenance':prov,'original_input_sha256':{**{str(p):original.sha(Path(p))for p in bound['input_paths']},**consumed},'geometry_source_invariant_rejections':[],'original_ROOT_reassigned':False,'new_NN':False,'candidate_source_unchanged':True,'physical_scene_accuracy':None})
print('all142 artifacts612inputs27pixels; native24 whole17268 proofPASS',len(chunks),'packets')
