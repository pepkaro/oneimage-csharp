# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""ISO-IMAGE-COLORKEY-01: original RGB samples with ordinary color-key masks."""
from pathlib import Path
import hashlib,json,zlib
R=Path(__file__).resolve().parent
OUT=R/'inputs';OUT.mkdir(exist_ok=True)
def sha(x):return hashlib.sha256(x).hexdigest()
def stream(x,entries=''):
 return f'<< {entries} /Length {len(x)} >>\nstream\n'.encode()+x+b'\nendstream'
def pdf(image):
 content=b'q 120 0 0 96 32 40 cm /Im Do Q\n'
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 180] /CropBox [0 0 240 180] /Rotate 0 /Resources << /XObject << /Im 5 0 R >> >> /Contents 4 0 R >>',stream(content),image]
 b=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offset=[]
 for i,obj in enumerate(objects,1):
  offset.append(len(b));b.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(b);b.extend(b'xref\n0 6\n0000000000 65535 f \n')
 for n in offset:b.extend(f'{n:010d} 00000 n \n'.encode())
 b.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(b)
GRID=[[[34,85,136],[68,119,170],[51,102,153],[33,85,136],[69,119,170]],[[34,84,136],[68,120,170],[34,85,135],[68,119,171],[51,102,152]],[[51,101,153],[50,102,153],[0,0,0],[238,221,204],[17,204,85]],[[68,85,170],[34,119,136],[85,85,136],[34,136,136],[34,85,187]]]
raw=bytes(v for row in GRID for rgb in row for v in rgb);assert len(raw)==60
encoded=zlib.compress(raw,9);cases=[]
for name,mask in [('control',None),('exact',[51,51,102,102,153,153]),('range',[34,68,85,119,136,170])]:
 fid='img-colorkey-'+name
 entries='/Type /XObject /Subtype /Image /Width 5 /Height 4 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Interpolate false /Filter /FlateDecode'
 if mask is not None:entries+=' /Mask ['+' '.join(map(str,mask))+']'
 data=pdf(stream(encoded,entries));(OUT/(fid+'.pdf')).write_bytes(data)
 samples=[]
 for y,row in enumerate(GRID):
  for x,rgb in enumerate(row):
   masked=mask is not None and all(mask[i*2]<=rgb[i]<=mask[i*2+1] for i in range(3))
   samples.append(dict(id=f'cell-{x}-{y}',point=[32+(x+.5)*24,40+(4-y-.5)*24],rgb=[255,255,255] if masked else rgb,source_rgb=rgb,masked=masked,tolerance=0))
 samples.append(dict(id='paper',point=[12,12],rgb=[255,255,255],tolerance=0))
 regions=[dict(id=s['id'],rect=[4,4,16,16] if s['id']=='paper' else [s['point'][0]-10,s['point'][1]-10,20,20],rgb=s['rgb'],tolerance=0) for s in samples]
 cases.append(dict(id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract='Original RGB8 '+name+' color-key masking; inclusive per-component intersection over authored source samples, composited on white.',spec='ISO 32000-1:2008',spec_clauses=['8.9.6.4 Colour Key Masking','8.9.5.1 General, Table 89','8.9.3 Sample Representation'],route='page image XObject /FlateDecode /Mask '+('absent' if mask is None else 'color-key array')+' /Interpolate false',width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],image=dict(width=5,height=4,bpc=8,color_space='/DeviceRGB',decode=None,ctm=[120,0,0,96,32,40],filter='FlateDecode',mask=mask,raw_sha256=sha(raw),encoded_sha256=sha(encoded),masked_cells=sum(s.get('masked',False) for s in samples)),sha256=sha(data),expected_samples=samples,expected_regions=regions,region_rule='Each authored 24-point cell inset 2 points; all boundaries unscored. Paper rectangle [4,4,16,16].',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No exact upstream metadata-only scene assertion established.')))
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-IMAGE-COLORKEY-01',purpose='One ordinary color-key family, three variants; no upstream-entry or net-new global-behavior claim.',fixture_count=3,decoded_bytes_hex=raw.hex(),cases=cases),indent=2)+'\n')
print('Generated 3 unique original PDFs; one 60-byte RGB grid; masked cells control/exact/range:',[x['image']['masked_cells'] for x in cases])
