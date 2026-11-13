"""Verify closed rendered inputs, produce letterboxed review sheets; no source imports."""
from pathlib import Path
import hashlib,json
import cv2
from PIL import Image,ImageDraw,ImageOps
OUT=Path(__file__).resolve().parent;MAIN=OUT.parents[4]
BASE=MAIN/'evaluation/ground_truth_validation/regression_tests/pre_test03_contract_v1'
names=['visual_test02_delayed_start_row03_v1','visual_test02_lost_short_event_v1']
cache={}
def sha(p):
 p=Path(p).resolve()
 if p not in cache:
  h=hashlib.sha256()
  with p.open('rb') as f:
   for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
  cache[p]=h.hexdigest()
 return cache[p]
def save(n,d):
 with (OUT/n).open('x') as f:json.dump(d,f,indent=2,allow_nan=False);f.write('\n')
counts={};sheets=[];rows=[]
for name in names:
 p=BASE/name;d=json.loads((p/'completion.json').read_text());assert d['status']=='completed'
 assert d['physical_gt_created'] is False and d['metrics_recomputed'] is False
 for rel,h in d['artifact_sha256'].items():assert sha(p/rel)==h,(name,rel)
 for item in d['input_bindings']:assert sha(item['path'])==item['sha256'],item['path']
 for frame in d['frames']:
  f=p/f'frame_{frame:07d}';e=json.loads((f/'evidence.json').read_text());assert e['frame']==frame
  im=cv2.imread(str(f/'source_original.png'));assert list(im.shape)==e['source_decode']['shape'];assert hashlib.sha256(im.tobytes()).hexdigest()==e['source_decode']['pixels_sha256']
  r={'frame':frame,'seconds':e['seconds_rational'],'source_pts':e['source_decode']['pts'],'source_pixels_sha256':e['source_decode']['pixels_sha256'],'package':name,'arms':{}}
  for arm in ['baseline','current']:
   a=e['arms'][arm];im=cv2.imread(str(f/f'{arm}_proxy.png'));assert list(im.shape)==a['proxy_decode']['shape'];assert hashlib.sha256(im.tobytes()).hexdigest()==a['proxy_decode']['pixels_sha256']
   assert a['proxy_decode']['seconds_rational']==e['seconds_rational']
   for key in ['cache_original','cache_snapshot']:assert sha(a[key]['path'])==a[key]['sha256']
   raw=json.loads((f/f'{arm}_raw_frame.json').read_text());assert raw['f']==frame
   r['arms'][arm]={'epoch':raw.get('ce'),'detector_observed':raw.get('do'),'perception_stride':raw.get('ps'),'players':len(raw['p']),'shuttle_xy':raw.get('s'),'association_status':raw.get('sa',{}).get('association_status'),'barrier':bool(raw.get('cd',{}) and raw['cd'].get('decision')=='barrier'),'models':a['models']}
  rows.append(r)
 for start in range(0,len(d['frames']),8):
  selected=d['frames'][start:start+8];im=Image.new('RGB',(1440,34+len(selected)*296),(12,12,12));dr=ImageDraw.Draw(im)
  dr.text((8,8),f'{name} | SOURCE / BASELINE improved_v1 / CURRENT 2418 | diagnostic only',fill='white')
  for i,frame in enumerate(selected):
   f=p/f'frame_{frame:07d}'
   for col,n in enumerate(['source_original.png','baseline_source_overlay.png','current_source_overlay.png']):
    src=Image.open(f/n).convert('RGB');thumb=ImageOps.contain(src,(480,270));x=col*480+(480-thumb.width)//2;y=34+i*296+24+(270-thumb.height)//2;im.paste(thumb,(x,y));dr.text((col*480+8,34+i*296+4),f'{frame} @ {frame/30:.3f}s | '+['source','baseline','current'][col],fill='white')
  dest=OUT/f'{"row03" if "row03" in name else "short"}_{start//8+1:02d}.jpg';im.save(dest,quality=92);sheets.append({'path':dest.name,'frames':selected,'source_package':str(p),'dimensions':list(im.size),'sha256':sha(dest)})
 counts[name]={'artifacts':len(d['artifact_sha256']),'input_bindings':len(d['input_bindings']),'frames':len(d['frames']),'pixels':3*len(d['frames']),'completion_sha256':sha(p/'completion.json')}
save('input_verification.json',{'status':'passed_closed_packages_and_pixels','packages':counts,'unique_hashed_paths':len(cache),'input_sha256':{str(k):v for k,v in cache.items() if not k.is_relative_to(OUT)},'source_frames':len(rows),'pixel_observations':len(rows)*3,'candidate_imports':False,'neural_inference':False})
save('frame_register.json',rows);save('sheet_index.json',sheets)
print(json.dumps({'packages':counts,'sheets':len(sheets),'frames':len(rows),'hashed_unique':len(cache)}))
