# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""ISO-IMAGE-PREDICTOR-CONTROL-01: original RGB rows, four predictor routes."""
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
GRID=[[[17,68,221],[51,102,204],[238,34,85],[0,170,255],[187,255,34]],[[34,85,238],[68,119,221],[221,51,102],[17,187,0],[204,0,51]],[[51,102,255],[85,136,238],[204,68,119],[34,204,17],[221,17,68]],[[238,51,17],[0,255,136],[170,17,204],[255,102,34],[68,221,187]]]
raw_rows=[bytes(v for rgb in row for v in rgb) for row in GRID]
raw=b''.join(raw_rows);assert len(raw)==60
# Encoding uses original neighboring bytes, never in-place residual bytes.
def predict(kind):
 if kind==1:return raw
 result=bytearray();previous=bytes(15)
 for row in raw_rows:
  if kind>=10:result.append({11:1,12:2}[kind])
  for i,value in enumerate(row):
   predictor=(row[i-3] if i>=3 else 0) if kind in [2,11] else previous[i]
   result.append((value-predictor)%256)
  previous=row
 return bytes(result)
samples=[]
for y,row in enumerate(GRID):
 for x,rgb in enumerate(row):samples.append(dict(id=f'cell-{x}-{y}',point=[32+(x+.5)*24,40+(4-y-.5)*24],rgb=rgb,tolerance=0))
samples.append(dict(id='paper',point=[12,12],rgb=[255,255,255],tolerance=0))
regions=[dict(id=s['id'],rect=[4,4,16,16] if s['id']=='paper' else [s['point'][0]-10,s['point'][1]-10,20,20],rgb=s['rgb'],tolerance=0) for s in samples]
cases=[]
for name,kind in [('none',1),('tiff-sub',2),('png-sub',11),('png-up',12)]:
 fid='img-predictor-'+name;predicted=predict(kind);encoded=zlib.compress(predicted,9)
 params=f'/Predictor {kind}'+(' /Colors 3 /BitsPerComponent 8 /Columns 5' if kind>1 else '')
 entries='/Type /XObject /Subtype /Image /Width 5 /Height 4 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Interpolate false /Filter /FlateDecode /DecodeParms << '+params+' >>'
 data=pdf(stream(encoded,entries));(OUT/(fid+'.pdf')).write_bytes(data)
 cases.append(dict(id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract='Authored RGB8 sample rows recover exactly through Flate with '+name+' prediction.',spec='ISO 32000-1:2008',spec_clauses=['7.4.4.3 LZWDecode and FlateDecode Parameters, Table 8','7.4.4.4 LZW and Flate Predictor Functions, Tables 9 and 10','8.9.3 Sample Representation'],route=f'page image XObject /FlateDecode /Predictor {kind} /Interpolate false',width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],image=dict(width=5,height=4,bpc=8,color_space='/DeviceRGB',decode=None,ctm=[120,0,0,96,32,40],filter='FlateDecode',predictor=kind,colors=3,columns=5,raw_sha256=sha(raw),predicted_sha256=sha(predicted),encoded_sha256=sha(encoded),predicted_bytes=len(predicted),encoded_bytes=len(encoded)),sha256=sha(data),expected_samples=samples,expected_regions=regions,region_rule='Each authored 24-point cell inset 2 points; all boundaries unscored. Paper rectangle [4,4,16,16].',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No exact upstream metadata-only scene assertion established.')))
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-IMAGE-PREDICTOR-CONTROL-01',purpose='One predictor family, four encoding variants; no distinct global-behavior or upstream pass count.',fixture_count=4,decoded_bytes_hex=raw.hex(),decoded_row_bytes=15,cases=cases),indent=2)+'\n')
print('Generated 4 unique original PDFs from one 60-byte RGB grid; Predictor 1/2/11/12.')
