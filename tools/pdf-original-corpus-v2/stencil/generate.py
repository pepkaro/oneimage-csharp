# SPDX-License-Identifier: MIT
"""Own valid1bpc image stencils: decode polarity and current-colour reuse."""
from pathlib import Path
import json,hashlib,zlib
R=Path(__file__).resolve().parent
BITS=[[0,1,0,1,1,0,0,1,0],[1,1,0,0,1,0,1,0,1],[0,0,1,1,0,1,1,0,0]]
sha=lambda b:hashlib.sha256(b).hexdigest()
MODES=[('stencil-default-red',None,[(24,[255,0,0])],160,'Default Decode marks stored0 bits with current red; stored1 bits leave opaque backdrop unchanged.'),('stencil-inverse-red',[1,0],[(24,[255,0,0])],160,'Reversed Decode marks stored1 bits with current red; stored0 bits leave opaque backdrop unchanged.'),('stencil-current-color-reuse',[0,1],[(24,[255,0,0]),(152,[0,255,0])],280,'One stencil XObject reused twice paints each mark in the current nonstroking colour, independently red then green.')]
def packed():
 out=bytearray()
 for row in BITS:
  v=0
  for bit in row:v=(v<<1)|bit
  out.extend((v<<7).to_bytes(2,'big'))
 assert len(out)==6;return bytes(out)
def stream(data,entries=''):return ('<< '+entries+' /Length '+str(len(data))+' >>\nstream\n').encode()+data+b'\nendstream'
def pdf(raw,decode,placements,width):
 commands=[]
 for left,color in placements:
  commands.append(f'0 0 1 rg {left-4} 36 116 44 re f')
  for y in range(3):
   for x in range(9):commands.append(('1 1 1' if (x+y)%2==0 else '0 0 0')+f' rg {left+x*12} {40+(2-y)*12} 12 12 re f')
  commands.append('q '+' '.join(str(v//255) for v in color)+f' rg 108 0 0 36 {left} 40 cm /Im Do Q')
 body='\n'.join(commands).encode();entry='/Type /XObject /Subtype /Image /Width 9 /Height 3 /BitsPerComponent 1 /ImageMask true /Interpolate false /Filter /FlateDecode'
 if decode is not None:entry+=' /Decode ['+' '.join(map(str,decode))+']'
 objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',f'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 {width} 110] /Resources << /XObject << /Im 5 0 R >> >> /Contents 4 0 R >>'.encode(),stream(body),stream(zlib.compress(raw,9),entry)]
 out=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offsets=[]
 for n,obj in enumerate(objs,1):offsets.append(len(out));out.extend(f'{n} 0 obj\n'.encode()+obj+b'\nendobj\n')
 pos=len(out);out.extend(b'xref\n0 6\n0000000000 65535 f \n')
 for off in offsets:out.extend(f'{off:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n'.encode());return bytes(out)
def main():
 (R/'inputs').mkdir(exist_ok=True);raw=packed();cases=[]
 for cid,decode,placements,width,contract in MODES:
  data=pdf(raw,decode,placements,width);p=R/'inputs'/(cid+'.pdf');p.write_bytes(data);samples=[];regions=[];marks=[]
  for k,(left,color) in enumerate(placements):
   for y,row in enumerate(BITS):
    for x,bit in enumerate(row):
     mark=bit==(1 if decode==[1,0] else 0);expected=color if mark else ([255,255,255] if (x+y)%2==0 else [0,0,0]);label=f'placement-{k}-cell-{x}-{y}';cx=left+(x+.5)*12;cy=40+(2-y+.5)*12
     samples.append(dict(id=label,point=[cx,cy],rgb=expected,tolerance=0));regions.append(dict(id=label,rect=[cx-4,cy-4,8,8],rgb=expected,tolerance=0))
     if mark:marks.append(label)
   label=f'frame-{k}';rect=[left-3,37,2,2];samples.append(dict(id=label,point=[rect[0]+1,rect[1]+1],rgb=[0,0,255],tolerance=0));regions.append(dict(id=label,rect=rect,rgb=[0,0,255],tolerance=0))
  samples.append(dict(id='paper',point=[8,8],rgb=[255,255,255],tolerance=0));regions.append(dict(id='paper',rect=[4,4,8,8],rgb=[255,255,255],tolerance=0))
  cases.append(dict(id=cid,fixture_id=cid,file='inputs/'+p.name,sha256=sha(data),license='MIT',fixture_version='1.7',contract=contract,width=width,height=110,page=0,page_count=1,dpis=[72,144],rotation=0,user_unit=1,background=[255,255,255],annotations='none',route='Opaque checkerboard and shared1bpc ImageMask XObject using current DeviceRGB nonstroking colour',spec='ISO 32000-1:2008',spec_clauses=['8.9.6.2 Stencil Masking','8.9.3 Sample Representation','8.9.5.2 Decode Arrays'],bits=BITS,image=dict(width=9,height=3,bpc=1,image_mask=True,color_space=None,decode=decode,raw_sha256=sha(raw),raw_hex=raw.hex(),row_bytes=2,unused_row_bits=7),placements=[dict(left=left,bottom=40,paint_rgb=color,ctm=[108,0,0,36,left,40],xobject='/Im') for left,color in placements],marked_cell_ids=marks,expected_samples=samples,expected_regions=regions,scope_limits=['EndpointRGB foreground and opaque checkerboard only','Two-point cell-edge inset; boundaries unscored','No soft masks, alpha, image interpolation or external image data'],association=dict(scope='spec-derived-only',upstream_id=None,upstream_entry_validated=False)))
 (R/'manifest.json').write_text(json.dumps(dict(schema_version=1,slice='ISO-IMAGE-STENCIL-01',owner='root',unique_pdfs=3,cases=cases),indent=2)+'\n');print('3 original stencil PDFs;6 authored packed bytes; shared XObject current-color control')
if __name__=='__main__':main()
