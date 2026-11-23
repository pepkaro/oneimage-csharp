# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF Corpus contributors
"""Original color-key reveal over an opaque checkerboard; no external input."""
from pathlib import Path
import json,zlib,hashlib
R=Path(__file__).resolve().parent
GRID=[[[34,85,136],[68,119,170],[51,102,153],[33,85,136]],[[69,119,170],[34,84,136],[68,120,170],[34,85,135]],[[68,119,171],[51,101,153],[51,102,152],[255,0,0]]]
MODES=[('control',None),('exact',[51,51,102,102,153,153]),('range',[34,68,85,119,136,170])]
def sha(b):return hashlib.sha256(b).hexdigest()
def stream(b,entries=''):return f'<< {entries} /Length {len(b)} >>\nstream\n'.encode()+b+b'\nendstream'
def pdf(mask,raw):
 commands=['1 0 0 rg 28 36 104 80 re f']
 for y,row in enumerate(GRID):
  for x,_ in enumerate(row):commands.append(('0 1 0' if (x+y)%2==0 else '0 0 1')+f' rg {32+24*x} {40+24*(2-y)} 24 24 re f')
 commands.append('q 96 0 0 72 32 40 cm /Im Do Q');body='\n'.join(commands).encode()
 entries='/Type /XObject /Subtype /Image /Width 4 /Height 3 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Interpolate false /Filter /FlateDecode'
 if mask is not None:entries+=' /Mask ['+' '.join(map(str,mask))+']'
 objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 180 140] /Resources << /XObject << /Im 5 0 R >> >> /Contents 4 0 R >>',stream(body),stream(zlib.compress(raw,9),entries)]
 out=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offsets=[]
 for n,o in enumerate(objs,1):offsets.append(len(out));out.extend(f'{n} 0 obj\n'.encode()+o+b'\nendobj\n')
 pos=len(out);out.extend(b'xref\n0 6\n0000000000 65535 f \n')
 for off in offsets:out.extend(f'{off:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n'.encode());return bytes(out)
def main():
 (R/'inputs').mkdir(exist_ok=True);raw=bytes(v for row in GRID for color in row for v in color);assert len(raw)==36;cases=[]
 for name,mask in MODES:
  id='img-colorkey-bg-'+name;data=pdf(mask,raw);p=R/'inputs'/(id+'.pdf');p.write_bytes(data);regions=[];samples=[];masked=[]
  for y,row in enumerate(GRID):
   for x,color in enumerate(row):
    hidden=mask is not None and all(mask[2*i]<=v<=mask[2*i+1] for i,v in enumerate(color));bg=[0,255,0] if (x+y)%2==0 else [0,0,255];expected=bg if hidden else color;key=f'cell-{x}-{y}';px=32+(x+.5)*24;py=40+(2-y+.5)*24
    if hidden:masked.append(key)
    samples.append(dict(id=key,point=[px,py],rgb=expected,tolerance=0));regions.append(dict(id=key,rect=[px-10,py-10,20,20],rgb=expected,tolerance=0))
  for key,rect,color in [('frame',[29,37,2,2],[255,0,0]),('paper',[4,4,12,12],[255,255,255])]:
   regions.append(dict(id=key,rect=rect,rgb=color,tolerance=0));samples.append(dict(id=key,point=[rect[0]+rect[2]/2,rect[1]+rect[3]/2],rgb=color,tolerance=0))
  contract={'control':'An unmasked opaque RGB image covers its previously painted green/blue checkerboard.','exact':'An exact RGB color key leaves its matched pixel unpainted, revealing the existing green backdrop.','range':'Inclusive RGB component ranges reveal the prior green/blue cells; one-value-outside controls remain opaque.'}[name]
  cases.append(dict(id=id,file='inputs/'+p.name,sha256=sha(data),license='MIT',fixture_version='1.7',contract=contract,width=180,height=140,page=0,page_count=1,dpis=[72,144],rotation=0,user_unit=1,background=[255,255,255],annotations='none',route='Opaque checkerboard then /FlateDecode RGB8 image /Mask array /Interpolate false',spec='ISO 32000-1:2008',spec_clauses=['8.9.6.4 Colour Key Masking','8.9.3 Sample Representation','8.9.5.2 Decode Arrays (default only)'],image=dict(width=4,height=3,bpc=8,color_space='DeviceRGB',mask=mask,raw_sha256=sha(raw)),raw_cells=GRID,masked_cell_ids=masked,expected_samples=samples,expected_regions=regions,scope_limits=['DefaultDecode only','RGB page output, not RGBA export','No soft masks or fractional alpha','Two-point cell-edge inset; boundaries unscored'],association=dict(scope='spec-derived-only',upstream_id=None,upstream_entry_validated=False)))
 (R/'manifest.json').write_text(json.dumps(dict(schema_version=1,slice='ISO-IMAGE-COLORKEY-COMPOSITE-02',owner='root',unique_pdfs=3,cases=cases),indent=2)+'\n')
if __name__=='__main__':main()
