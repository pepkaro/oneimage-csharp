# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""White-backed ordinary stencil controls; original numeric9x3 bit grid, no external bytes."""
from pathlib import Path
import json,hashlib
R=Path(__file__).resolve().parent
OUT=R/'inputs';OUT.mkdir(exist_ok=True)
ROWS=[[0,1,1,0,0,1,0,1,0],[0,0,1,1,1,0,1,0,1],[1,0,0,1,0,1,1,1,0]]
RAW=bytes(int((''.join(map(str,row))+'0000000')[i:i+8],2) for row in ROWS for i in [0,8]);assert RAW==bytes.fromhex('65003a809700')
def sha(x):return hashlib.sha256(x).hexdigest()
def stream(x,entries=''):return f'<< {entries} /Length {len(x)} >>\nstream\n'.encode()+x+b'\nendstream'
def pdf(content,image):
 objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 180] /CropBox [0 0 240 180] /Rotate 0 /Resources << /XObject << /M 5 0 R >> >> /Contents 4 0 R >>',stream(content.encode()),image]
 b=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offset=[]
 for i,obj in enumerate(objs,1):offset.append(len(b));b.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(b);b.extend(b'xref\n0 6\n0000000000 65535 f \n')
 for n in offset:b.extend(f'{n:010d} 00000 n \n'.encode())
 b.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(b)
cases=[]
for name,inverse,draws in [('default-red',False,[(32,80,[255,0,0])]),('inverse-red',True,[(32,80,[255,0,0])]),('reuse-red-green',False,[(32,104,[255,0,0]),(32,24,[0,255,0])])]:
 fid='stencil-white-'+name;content='';regions=[];samples=[];placements=[]
 for n,(x,y,tint) in enumerate(draws):
  frame=[x-8,y-8,160,64];ctm=[144,0,0,48,x,y]
  content+='q\n1 1 1 rg '+' '.join(map(str,frame))+' re f\n'+' '.join(str(v//255) for v in tint)+' rg\n'+' '.join(map(str,ctm))+' cm /M Do\nQ\n'
  placements.append(dict(id=f'draw-{n}',x=x,y=y,tint_rgb=tint,ctm=ctm,backdrop_rect=frame,mask_resource='M',mask_object_number=5))
  for row in range(3):
   for col in range(9):
    bit=ROWS[row][col];painted=bit==(1 if inverse else 0);rgb=tint if painted else [255]*3;ident=f'draw-{n}-cell-{col}-{row}'
    rect=[x+col*16+2,y+(2-row)*16+2,12,12]
    regions.append(dict(id=ident,rect=rect,rgb=rgb,tolerance=0));samples.append(dict(id=ident,point=[rect[0]+6,rect[1]+6],rgb=rgb,tolerance=0,draw=n,source_bit=bit,painted=painted))
  for side,rect in [('left',[x-6,y-6,4,60]),('right',[x+146,y-6,4,60]),('bottom',[x+2,y-6,140,4]),('top',[x+2,y+50,140,4])]:
   ident=f'draw-{n}-white-frame-{side}';regions.append(dict(id=ident,rect=rect,rgb=[255]*3,tolerance=0));samples.append(dict(id=ident,point=[rect[0]+rect[2]/2,rect[1]+rect[3]/2],rgb=[255]*3,tolerance=0))
 regions.append(dict(id='paper',rect=[4,4,16,16],rgb=[255]*3,tolerance=0));samples.append(dict(id='paper',point=[12,12],rgb=[255]*3,tolerance=0))
 entries='/Type /XObject /Subtype /Image /Width 9 /Height 3 /ImageMask true /BitsPerComponent 1 /Interpolate false'+(' /Decode [1 0]' if inverse else '')
 data=pdf(content,stream(RAW,entries));(OUT/(fid+'.pdf')).write_bytes(data)
 cases.append(dict(id=fid,fixture_id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract='WHITE-backed ordinary stencil '+name+'; default0 paints/inverse1 paints; reuse tint comes from each draw current color.',scope='Opaque WHITE backdrops only; closes none of root checkerboard holds.',spec='ISO 32000-1:2008',spec_clauses=['8.9.6.2 Stencil Masking','8.9.3 Sample Representation'],route='page ImageMask9x3 BPC1 with no ColorSpace, q/Q-separated placements and current nonstroking tint',width=240,height=180,page=0,page_count=1,dpis=[72,144],rotation=0,annotations='none',background=[255]*3,sha256=sha(data),sha=sha(data),image=dict(width=9,height=3,bpc=1,image_mask=True,decode=[1,0] if inverse else None,raw_sha256=sha(RAW),raw_hex=RAW.hex(),row_bytes=2,color_space=None,object_count=1),placements=placements,expected_samples=samples,expected_regions=regions,region_rule='Each16pt source cell inset2pt; white-frame strips and paper independently inset2pt; all boundaries unscored.',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No exact upstream stencil scene scope established.')))
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-IMAGE-STENCIL-01-WHITE-CONTROLS',logical_parent_family='ISO-IMAGE-STENCIL-01',fixture_count=3,scope='WHITE-backed only; held checkerboard originals remain separate.',raw_bits=ROWS,raw_hex=RAW.hex(),cases=cases),indent=2)+'\n')
print('Generated exactly 3 white-backed stencil PDFs; one original six-byte grid; no held checker fixtures read.')
