"""Verify closed small source comparison; no pipeline import, NN or source edits."""
from pathlib import Path
import hashlib,json
import cv2
from PIL import Image,ImageOps,ImageDraw
P=Path(__file__).resolve().parent;PKG=P.parent/'visual_test02_v5_additional_cut13452_v1';EXPECTED=[13449,13450,13451,13452,13453,13454,13455];cache={}
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
d=read(PKG/'completion.json');assert d['status']=='completed'and d['frames']==EXPECTED
for rel,h in d['artifact_sha256'].items():assert sha(PKG/rel)==h,rel
for x in d['input_bindings']:assert sha(x['path'])==x['sha256'],x['path']
rows=[]
for n in EXPECTED:
 f=PKG/f'frame_{n:07d}';e=read(f/'evidence.json');im=cv2.imread(str(f/'source_original.png'));assert hashlib.sha256(im.tobytes()).hexdigest()==e['source_decode']['pixels_sha256']and list(im.shape)==e['source_decode']['shape']
 row={'frame':n,'seconds':e['seconds_rational'],'source':e['source_decode'],'arms':{}}
 for a in ['baseline','current']:
  ev=e['arms'][a];im=cv2.imread(str(f/f'{a}_proxy.png'));assert hashlib.sha256(im.tobytes()).hexdigest()==ev['proxy_decode']['pixels_sha256']and list(im.shape)==ev['proxy_decode']['shape'];assert ev['proxy_decode']['seconds_rational']==e['seconds_rational']
  for k in ['cache_original','cache_snapshot']:assert sha(ev[k]['path'])==ev[k]['sha256']
  raw=read(f/f'{a}_raw_frame.json');row['arms'][a]={'epoch':raw['ce'],'players':raw['p'],'foreground':raw.get('fg'),'raw_scene':raw.get('cc'),'decision':raw.get('cd'),'detector_observed':raw['do'],'stride':raw['ps'],'models':ev['models']}
  if raw.get('cd')and raw['cd'].get('detector_image_sha256'):assert raw['cd']['detector_image_sha256']==ev['proxy_decode']['pixels_sha256']
 rows.append(row)
for start in range(0,len(EXPECTED),3):
 sel=EXPECTED[start:start+3];im=Image.new('RGB',(1920,34+384*len(sel)),(12,12,12));draw=ImageDraw.Draw(im);draw.text((8,8),'SOURCE | BASELINE explicit producer in invocation | CURRENT actual5ae | diagnostic only',fill='white')
 for i,n in enumerate(sel):
  for j,f in enumerate(['source_original.png','baseline_source_overlay.png','current_source_overlay.png']):
   src=Image.open(PKG/f'frame_{n:07d}'/f).convert('RGB');t=ImageOps.contain(src,(640,360));im.paste(t,(j*640+(640-t.width)//2,34+i*384+24+(360-t.height)//2));draw.text((j*640+8,34+i*384+5),str(n)+' '+['source','baseline','current5ae'][j],fill='white')
 im.save(P/f'sheet_{start//3+1:02d}.jpg',quality=95)
save('frame_register.json',rows);save('verification.json',{'status':'passed_all_closed_hash_and_pixel_bindings','frames':EXPECTED,'artifact_count':len(d['artifact_sha256']),'input_binding_count':len(d['input_bindings']),'source_proxy_pixel_count':3*len(EXPECTED),'package_completion_sha256':sha(PKG/'completion.json'),'input_sha256':{str(p):h for p,h in cache.items()},'physical_gt':None,'new_NN':False})
print(len(EXPECTED),'frames',len(d['artifact_sha256']),'artifacts',len(d['input_bindings']),'inputs',3*len(EXPECTED),'pixelreceiptsPASS')
