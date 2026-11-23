# SPDX-License-Identifier: MIT
"""Original small valid PDFs: colour-key masking acts on stored samples before Decode."""
from pathlib import Path
import json,hashlib,zlib
R=Path(__file__).resolve().parent
GRID=[[[40,90,140],[215,165,115],[70,120,170],[185,135,85]],[[39,90,140],[71,120,170],[40,89,140],[70,121,170]],[[40,90,139],[70,120,171],[55,105,155],[200,150,100]]]
MODES=[('opaque',None,'Reversed Decode complements normalized RGB samples; ideal byte complements are the declared raster acceptance criterion.'),('stored-key',[40,40,90,90,140,140],'An exact key masks the stored sample before reversed Decode; a sample whose ideal complemented bytes equal that key remains painted.'),('decoded-key-control',[215,215,165,165,115,115],'A key equal to the decoded colour of the first sample instead masks the different stored complement sample.'),('stored-range',[40,70,90,120,140,170],'Inclusive stored-component ranges mask low/high/interior samples before reversed Decode; one-component-outside and decoded-only matches remain opaque.')]
sha=lambda b:hashlib.sha256(b).hexdigest()
def stream(data,entries=''):return ('<< '+entries+' /Length '+str(len(data))+' >>\nstream\n').encode()+data+b'\nendstream'
def pdf(raw,mask):
 commands=['1 0 0 rg 28 36 104 80 re f']
 for y in range(3):
  for x in range(4):commands.append(('0 1 0' if (x+y)%2==0 else '0 0 1')+f' rg {32+x*24} {40+(2-y)*24} 24 24 re f')
 commands.append('q 96 0 0 72 32 40 cm /Im Do Q');body='\n'.join(commands).encode()
 entries='/Type /XObject /Subtype /Image /Width 4 /Height 3 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Decode [1 0 1 0 1 0] /Interpolate false /Filter /FlateDecode'
 if mask is not None:entries+=' /Mask ['+' '.join(map(str,mask))+']'
 objs=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 180 140] /Resources << /XObject << /Im 5 0 R >> >> /Contents 4 0 R >>',stream(body),stream(zlib.compress(raw,9),entries)]
 out=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offsets=[]
 for n,o in enumerate(objs,1):offsets.append(len(out));out.extend(f'{n} 0 obj\n'.encode()+o+b'\nendobj\n')
 pos=len(out);out.extend(b'xref\n0 6\n0000000000 65535 f \n')
 for off in offsets:out.extend(f'{off:010d} 00000 n \n'.encode())
 out.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{pos}\n%%EOF\n'.encode());return bytes(out)
def main():
 (R/'inputs').mkdir(exist_ok=True);raw=bytes(v for row in GRID for cell in row for v in cell);assert len(raw)==36;cases=[]
 for name,mask,contract in MODES:
  cid='img-colorkey-decode-'+name;data=pdf(raw,mask);p=R/'inputs'/(cid+'.pdf');p.write_bytes(data);regions=[];samples=[];masked=[];decoded_only=[]
  for y,row in enumerate(GRID):
   for x,color in enumerate(row):
    decoded=[255-v for v in color];hidden=mask is not None and all(mask[2*k]<=color[k]<=mask[2*k+1] for k in range(3));decoded_match=mask is not None and all(mask[2*k]<=decoded[k]<=mask[2*k+1] for k in range(3));cidcell=f'cell-{x}-{y}';background=[0,255,0] if (x+y)%2==0 else [0,0,255];expected=background if hidden else decoded;cx=32+(x+.5)*24;cy=40+(2-y+.5)*24
    if hidden:masked.append(cidcell)
    if decoded_match and not hidden:decoded_only.append(cidcell)
    regions.append(dict(id=cidcell,rect=[cx-10,cy-10,20,20],rgb=expected,tolerance=0));samples.append(dict(id=cidcell,point=[cx,cy],rgb=expected,tolerance=0))
  for label,rect,color in [('frame',[29,37,2,2],[255,0,0]),('paper',[4,4,12,12],[255,255,255])]:
   regions.append(dict(id=label,rect=rect,rgb=color,tolerance=0));samples.append(dict(id=label,point=[rect[0]+rect[2]/2,rect[1]+rect[3]/2],rgb=color,tolerance=0))
  cases.append(dict(id=cid,fixture_id=cid,file='inputs/'+p.name,sha256=sha(data),license='MIT',fixture_version='1.7',contract=contract,width=180,height=140,page=0,page_count=1,dpis=[72,144],rotation=0,user_unit=1,background=[255,255,255],annotations='none',route='Opaque checkerboard then FlateDecode RGB8 image with reversed Decode and optional colour-key array',spec='ISO 32000-1:2008',spec_clauses=['8.9.6.4 Colour Key Masking','8.9.5.2 Decode Arrays','8.9.3 Sample Representation'],image=dict(width=4,height=3,bpc=8,color_space='DeviceRGB',decode=[1,0,1,0,1,0],mask=mask,raw_sha256=sha(raw)),raw_cells=GRID,masked_cell_ids=masked,decoded_only_match_ids=decoded_only,expected_samples=samples,expected_regions=regions,scope_limits=['RGB8 and fully reversed component Decode only','No interpolation boundary assertion','Opaque endpoint checkerboard; no soft mask/fractional alpha','Not persistent document cache or performance testing'],association=dict(scope='spec-derived-only',upstream_id=None,upstream_entry_validated=False)))
 (R/'manifest.json').write_text(json.dumps(dict(schema_version=1,slice='ISO-IMAGE-COLORKEY-DECODE-03',owner='root',unique_pdfs=4,cases=cases),indent=2)+'\n');print('4 original PDFs; 36 authored RGB bytes; stored-key versus decoded-only controls')
if __name__=='__main__':main()
