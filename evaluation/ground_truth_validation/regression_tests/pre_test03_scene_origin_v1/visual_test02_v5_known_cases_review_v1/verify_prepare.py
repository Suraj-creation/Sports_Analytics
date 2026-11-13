"""Prepare only after frozen renderer genuinely completed; no pipeline imports/NN."""
from pathlib import Path
import hashlib,json
import cv2
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parent;PKG=P.parent/'visual_test02_v5_known_cases_v1';cache={}
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
 with(P/n).open('x')as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
d=read(PKG/'completion.json');assert d['status']=='completed'and len(d['frames'])==108 and not d['physical_gt_created']and not d['metrics_recomputed']and not d['neural_inference_performed']
for rel,h in d['artifact_sha256'].items():assert sha(PKG/rel)==h,rel
for r in d['input_bindings']:assert sha(r['path'])==r['sha256'],r['path']
rows=[]
for frame in d['frames']:
 f=PKG/f'frame_{frame:07d}';e=read(f/'evidence.json');im=cv2.imread(str(f/'source_original.png'));assert hashlib.sha256(im.tobytes()).hexdigest()==e['source_decode']['pixels_sha256']and list(im.shape)==e['source_decode']['shape']
 row={'frame':frame,'seconds':e['seconds_rational'],'source':e['source_decode'],'arms':{}}
 for arm in ['baseline','current']:
  a=e['arms'][arm];im=cv2.imread(str(f/f'{arm}_proxy.png'));assert hashlib.sha256(im.tobytes()).hexdigest()==a['proxy_decode']['pixels_sha256']and list(im.shape)==a['proxy_decode']['shape'];assert a['proxy_decode']['seconds_rational']==e['seconds_rational']
  for k in ['cache_original','cache_snapshot']:assert sha(a[k]['path'])==a[k]['sha256']
  raw=read(f/f'{arm}_raw_frame.json');row['arms'][arm]={'epoch':raw['ce'],'detector_observed':raw['do'],'perception_stride':raw['ps'],'players':[{'track':x['t'],'bbox':x['b'],'detector_matched':x['dm'],'pose_source':x.get('pf')}for x in raw['p']],'shuttle':raw['s'],'shuttle_support':raw['c'],'association':raw.get('sa'),'raw_scene':raw.get('cc'),'decision':raw.get('cd'),'models':a['models']}
 rows.append(row)
sheets=[]
for i in range(0,108,6):
 selected=d['frames'][i:i+6];im=Image.new('RGB',(1440,34+len(selected)*296),(12,12,12));dr=ImageDraw.Draw(im);dr.text((8,8),'SOURCE | BASELINE original dacc improved_v1 | CURRENT actual5ae | diagnostic only',fill='white')
 for j,frame in enumerate(selected):
  for col,n in enumerate(['source_original.png','baseline_source_overlay.png','current_source_overlay.png']):
   src=Image.open(PKG/f'frame_{frame:07d}'/n).convert('RGB');t=ImageOps.contain(src,(480,270));im.paste(t,(col*480+(480-t.width)//2,34+j*296+24+(270-t.height)//2));dr.text((col*480+8,34+j*296+5),str(frame)+' '+['source','dacc baseline','current5ae'][col],fill='white')
 name=f'sheet_{i//6+1:02d}.jpg';im.save(P/name,quality=95);sheets.append({'path':name,'frames':selected,'sha256':sha(P/name)})
save('frame_register.json',rows);save('sheet_index.json',sheets)
save('verification.json',{'status':'passed_all_closed_source_and_prediction_bindings','source_sha256':d['source_sha256'],'package_completion_sha256':sha(PKG/'completion.json'),'artifacts_verified':len(d['artifact_sha256']),'input_bindings_verified':len(d['input_bindings']),'source_proxy_pixel_receipts_verified':324,'input_sha256':{str(p):h for p,h in cache.items()if not p.is_relative_to(P)},'frames':d['frames'],'new_NN':False,'physical_gt':None,'visual_review_complete':False})
print('PASS',len(d['artifact_sha256']),'artifacts',len(d['input_bindings']),'inputs324pixels;18sheetsreadyforactualreview')
