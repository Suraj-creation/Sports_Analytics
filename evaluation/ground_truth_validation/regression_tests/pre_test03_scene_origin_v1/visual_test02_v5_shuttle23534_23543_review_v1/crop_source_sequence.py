from pathlib import Path
import cv2,hashlib,json
from PIL import Image,ImageDraw,ImageOps
P=Path(__file__).resolve().parent;B=P.parent/'visual_test02_v5_shuttle23534_23543_v1'
regions={'upper_airborne_branch':[1070,60,1230,285],'lower_model_branch_floor_logo':[780,580,940,740]}
out=Image.new('RGB',(1250,1240),(12,12,12));draw=ImageDraw.Draw(out);draw.text((8,8),'SOURCE ONLY fixed regions: upper moving object / lower static floor mark; agent diagnosis, not new GT',fill='white');rows=[]
for role_idx,(role,(x1,y1,x2,y2)) in enumerate(regions.items()):
 for i,f in enumerate(range(23534,23544)):
  srcpath=B/f'frame_{f:07d}'/'source_original.png';a=cv2.imread(str(srcpath));crop=a[y1:y2,x1:x2].copy();name=f'{role}_{f}.png';cv2.imwrite(str(P/name),crop);assert (cv2.imread(str(P/name))==crop).all()
  t=ImageOps.contain(Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB)),(245,270),method=Image.Resampling.NEAREST);col=i%5;row=role_idx*2+i//5;out.paste(t,(col*250+(250-t.width)//2,34+row*300+25));draw.text((col*250+5,34+row*300+5),str(f)+' '+('UPPER'if role_idx==0 else'FLOOR'),fill='white')
  rows.append({'frame':f,'role':role,'source_png':str(srcpath),'source_png_sha256':hashlib.sha256(srcpath.read_bytes()).hexdigest(),'source_crop_xyxy':[x1,y1,x2,y2],'crop_png':name,'crop_png_sha256':hashlib.sha256((P/name).read_bytes()).hexdigest(),'native_crop_BGR_sha256':hashlib.sha256(crop.tobytes()).hexdigest(),'native_crop_shape':list(crop.shape),'display_resampling':'nearest neighbor; no invented coordinates or GT marks'})
out.save(P/'fixed_source_regions.jpg',quality=97)
with(P/'source_crop_bindings.json').open('x')as f:json.dump(rows,f,indent=2);f.write('\n')
