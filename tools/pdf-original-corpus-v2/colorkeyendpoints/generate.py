# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""Endpoint-only stored-sample color-key selection with reversed Decode; original numeric sources."""
from pathlib import Path
import hashlib,json,zlib
R=Path(__file__).resolve().parent
OUT=R/'inputs';OUT.mkdir(exist_ok=True)
def sha(x):return hashlib.sha256(x).hexdigest()
def stream(x,entries=''):
 return f'<< {entries} /Length {len(x)} >>\nstream\n'.encode()+x+b'\nendstream'
COLORS={'red':[255,0,0],'cyan':[0,255,255],'magenta':[255,0,255],'green':[0,255,0],'blue':[0,0,255],'yellow':[255,255,0]}
GRID=[['red','cyan','magenta'],['green','blue','yellow'],['cyan','red','magenta']]
RAW=bytes(v for row in GRID for color in row for v in COLORS[color]);assert len(RAW)==27
# The checker is opaque page graphics, not image alpha: 36 ordinary 12-point fills.
checker=[]
for y in range(6):
 for x in range(6):checker.append(dict(top_row=y,column=x,gray=(x+y)%2,rect=[32+x*12,40+(5-y)*12,12,12]))
content=''.join(f"{q['gray']} g {' '.join(map(str,q['rect']))} re f\n" for q in checker)+'q 72 0 0 72 32 40 cm /Im Do Q\n'
def pdf(image):
 objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 180] /CropBox [0 0 240 180] /Rotate 0 /Resources << /XObject << /Im 5 0 R >> >> /Contents 4 0 R >>',stream(content.encode()),image]
 b=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offset=[]
 for i,obj in enumerate(objs,1):offset.append(len(b));b.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(b);b.extend(b'xref\n0 6\n0000000000 65535 f \n')
 for n in offset:b.extend(f'{n:010d} 00000 n \n'.encode())
 b.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(b)
encoded=zlib.compress(RAW,9);cases=[]
for name,key in [('control',None),('stored-red',[255,255,0,0,0,0]),('stored-red-magenta-range',[255,255,0,0,0,255])]:
 fid='img-colorkey-endpoint-'+name
 entries='/Type /XObject /Subtype /Image /Width 3 /Height 3 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Filter /FlateDecode /Interpolate false /Decode [1 0 1 0 1 0]'
 if key is not None:entries+=' /Mask ['+' '.join(map(str,key))+']'
 data=pdf(stream(encoded,entries));(OUT/(fid+'.pdf')).write_bytes(data);regions=[];samples=[];cells=[]
 for row in range(3):
  for col in range(3):
   name_color=GRID[row][col];stored=COLORS[name_color];decoded=[255-v for v in stored]
   masked=key is not None and all(key[2*i]<=stored[i]<=key[2*i+1] for i in range(3))
   decoded_key_match=key is not None and all(key[2*i]<=decoded[i]<=key[2*i+1] for i in range(3))
   cellid=f'cell-{col}-{row}';cells.append(dict(id=cellid,color=name_color,stored_rgb=stored,decoded_rgb=decoded,masked=masked,decoded_key_match=decoded_key_match))
   for quarter,qx,qy,gray in [('NW',0,1,0),('NE',1,1,1),('SW',0,0,1),('SE',1,0,0)]:
    rect=[32+col*24+qx*12+2,40+(2-row)*24+qy*12+2,8,8];expected=[gray*255]*3 if masked else decoded
    ident=cellid+'-'+quarter
    regions.append(dict(id=ident,rect=rect,rgb=expected,tolerance=0))
    samples.append(dict(id=ident,point=[rect[0]+4,rect[1]+4],rgb=expected,tolerance=0,cell_id=cellid,stored_rgb=stored,decoded_rgb=decoded,masked=masked,background_rgb=[gray*255]*3))
 regions.append(dict(id='paper',rect=[4,4,16,16],rgb=[255,255,255],tolerance=0));samples.append(dict(id='paper',point=[12,12],rgb=[255,255,255],tolerance=0))
 cases.append(dict(id=fid,fixture_id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract='Endpoint-only reversed RGB Decode; '+('unmasked control' if key is None else 'mask selection on stored components, before Decode')+' over an opaque checkerboard.',scope='Endpoint-only RGB8 components0/255; does not resolve non-endpoint quantization holds.',spec='ISO 32000-1:2008',spec_clauses=['8.9.6.4 Colour Key Masking','8.9.5.2 Decode Arrays'],route='page RGB8 image XObject, lossless Flate, reversed Decode and optional color-key array; opaque checkerboard page graphics',width=240,height=180,page=0,page_count=1,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],sha256=sha(data),sha=sha(data),image=dict(width=3,height=3,bpc=8,color_space='/DeviceRGB',filter='FlateDecode',decode=[1,0,1,0,1,0],mask=key,ctm=[72,0,0,72,32,40],raw_sha256=sha(RAW),encoded_sha256=sha(encoded)),cells=cells,checkerboard=checker,expected_samples=samples,expected_regions=regions,region_rule='Each 12-point checker quadrant within each24-point source-image cell is inset2points to an8x8-point region; image/cell/checker edges are unscored.',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No exact upstream scene scope established.')))
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-IMAGE-COLORKEY-DECODE-03-ENDPOINT-CONTROLS',fixture_count=3,scope='Endpoint-only control sub-slice, separate from all held non-endpoint fixtures.',raw_sample_bytes_hex=RAW.hex(),color_names=GRID,cases=cases),indent=2)+'\n')
print('Generated exactly3 original endpoint PDFs; stored-red/exact2 cells, stored-red-magenta/range4 cells; no non-endpoint bytes.')
