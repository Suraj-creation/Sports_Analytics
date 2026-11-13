"""Independent18frame closed-render verifier; no pipeline imports or NN."""
from pathlib import Path
import hashlib,json,math
import cv2
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parent;PKG=P.parent/'visual_test01_v5_secondary_deltas_v1';cache={}
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
d=read(PKG/'completion.json');assert d['status']=='completed'and len(d['frames'])==18 and not d['physical_gt_created']and not d['metrics_recomputed']and not d['neural_inference_performed']
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
 old,new=row['arms']['baseline']['shuttle'],row['arms']['current']['shuttle'];row['shuttle_xy_delta_canonical_px']=math.dist(old,new)if old is not None and new is not None else None;rows.append(row)
for i in range(0,18,3):
 selected=d['frames'][i:i+3];im=Image.new('RGB',(1920,1186),(12,12,12));dr=ImageDraw.Draw(im);dr.text((8,8),'SOURCE | BASELINE secondary actual2418 | CURRENT actual5ae | diagnostic only',fill='white')
 for j,frame in enumerate(selected):
  for col,n in enumerate(['source_original.png','baseline_source_overlay.png','current_source_overlay.png']):
   src=Image.open(PKG/f'frame_{frame:07d}'/n).convert('RGB');t=ImageOps.contain(src,(640,360));im.paste(t,(col*640+(640-t.width)//2,34+j*384+24+(360-t.height)//2));dr.text((col*640+8,34+j*384+5),str(frame)+' '+['source','secondary2418','current5ae'][col],fill='white')
 im.save(P/f'sheet_{i//3+1:02d}.jpg',quality=95)
# Source-only enlarged neighborhoods selected from model locations, without GT marks.
for frame in [14242,14306]:
 row=next(x for x in rows if x['frame']==frame);xy=row['arms']['current']['shuttle'];assert xy is not None
 source=Image.open(PKG/f'frame_{frame:07d}'/'source_original.png').convert('RGB');x,y=[v*1.5 for v in xy];box=(int(x)-100,int(y)-100,int(x)+100,int(y)+100);crop=source.crop(box).resize((800,800));crop.save(P/f'source_neighborhood_{frame}.png');row['source_only_crop']={'crop_source_xyxy':box,'resize':'4x Pillow default visual enlargement; no additional source information','center_selected_from_current_model':'not a physical location label'}
save('frame_register.json',rows)
save('verification.json',{'status':'passed_all_closed_source_and_prediction_bindings','source_sha256':d['source_sha256'],'package_completion_sha256':sha(PKG/'completion.json'),'artifacts_verified':len(d['artifact_sha256']),'input_bindings_verified':len(d['input_bindings']),'source_proxy_pixel_receipts_verified':54,'input_sha256':{str(p):h for p,h in cache.items()},'frames':d['frames'],'new_NN':False,'physical_gt':None})
print('PASS',len(d['artifact_sha256']),'artifacts',len(d['input_bindings']),'inputs54pixels')
