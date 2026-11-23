# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Original PDF corpus contributors
"""ISO-IMAGE-FILTER-CONTROL-01: original numeric RGB samples, three lossless routes."""
from pathlib import Path
import hashlib,json,zlib
R=Path(__file__).resolve().parent
OUT=R/'inputs';OUT.mkdir(exist_ok=True)
def sha(x):return hashlib.sha256(x).hexdigest()
def stream(x,entries=''):
 return f'<< {entries} /Length {len(x)} >>\nstream\n'.encode()+x+b'\nendstream'
def pdf(image):
 content=b'q 144 0 0 72 32 40 cm /Im Do Q\n'
 objects=[b'<< /Type /Catalog /Pages 2 0 R >>',b'<< /Type /Pages /Kids [3 0 R] /Count 1 >>',b'<< /Type /Page /Parent 2 0 R /MediaBox [0 0 240 180] /CropBox [0 0 240 180] /Rotate 0 /Resources << /XObject << /Im 5 0 R >> >> /Contents 4 0 R >>',stream(content),image]
 b=bytearray(b'%PDF-1.7\n%\xe2\xe3\xcf\xd3\n');offset=[]
 for i,obj in enumerate(objects,1):
  offset.append(len(b));b.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
 start=len(b);b.extend(b'xref\n0 6\n0000000000 65535 f \n')
 for n in offset:b.extend(f'{n:010d} 00000 n \n'.encode())
 b.extend(f'trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n'.encode());return bytes(b)
def run_length(raw):
 out=bytearray();i=0;packets=[]
 while i<len(raw):
  end=i+1
  while end<len(raw) and raw[end]==raw[i] and end-i<128:end+=1
  count=end-i
  if count>=3:
   out.extend([257-count,raw[i]]);packets.append(dict(kind='repeat',decoded_bytes=count));i=end
  else:
   start=i;i=end
   while i<len(raw) and i-start<128:
    end=i+1
    while end<len(raw) and raw[end]==raw[i] and end-i<128:end+=1
    if end-i>=3:break
    i=min(end,start+128)
   chunk=raw[start:i];out.append(len(chunk)-1);out.extend(chunk);packets.append(dict(kind='literal',decoded_bytes=len(chunk)))
 out.append(128);return bytes(out),packets
GRID=[[[0,0,0],[255,255,255],[51,51,51],[17,85,221],[238,68,136],[119,204,34]],[[170,170,170],[34,153,238],[85,85,85],[221,17,187],[0,255,119],[255,0,204]],[[255,255,255],[17,17,17],[68,221,102],[136,51,255],[204,204,204],[0,0,0]]]
raw=bytes(v for row in GRID for rgb in row for v in rgb);assert len(raw)==54
rl,packets=run_length(raw)
samples=[]
for y,row in enumerate(GRID):
 for x,rgb in enumerate(row):samples.append(dict(id=f'cell-{x}-{y}',point=[32+(x+.5)*24,40+(3-y-.5)*24],rgb=rgb,tolerance=0))
samples.append(dict(id='paper',point=[12,12],rgb=[255,255,255],tolerance=0))
regions=[dict(id=s['id'],rect=[4,4,16,16] if s['id']=='paper' else [s['point'][0]-10,s['point'][1]-10,20,20],rgb=s['rgb'],tolerance=0) for s in samples]
cases=[]
for name,filter_name,encoded in [('raw',None,raw),('flate','FlateDecode',zlib.compress(raw,9)),('runlength','RunLengthDecode',rl)]:
 fid='img-filter-equivalence-'+name
 entries='/Type /XObject /Subtype /Image /Width 6 /Height 3 /BitsPerComponent 8 /ColorSpace /DeviceRGB /Interpolate false'
 if filter_name:entries+=' /Filter /'+filter_name
 data=pdf(stream(encoded,entries));(OUT/(fid+'.pdf')).write_bytes(data)
 cases.append(dict(id=fid,file='inputs/'+fid+'.pdf',license='MIT',contract='Identical authored RGB sample grid survives the '+name+' image stream route unchanged.',spec='ISO 32000-1:2008',spec_clauses=['8.9.3 Sample Representation','8.9.5.1 General']+(['7.4.4.1 General (Flate)'] if name=='flate' else ['7.4.5 RunLengthDecode Filter'] if name=='runlength' else ['7.3.8 Stream Objects']),route='page image XObject /'+(filter_name or 'no Filter')+' /Interpolate false',width=240,height=180,page=0,dpis=[72,144],rotation=0,annotations='none',background=[255,255,255],image=dict(width=6,height=3,bpc=8,color_space='/DeviceRGB',decode=None,ctm=[144,0,0,72,32,40],filter=filter_name,raw_sha256=sha(raw),encoded_sha256=sha(encoded),encoded_bytes=len(encoded)),sha256=sha(data),expected_samples=samples,expected_regions=regions,region_rule='Each authored 24-point cell inset 2 points; all boundaries unscored. Paper rectangle [4,4,16,16].',association=dict(scope='standard-contract-only',upstream_id=None,upstream_entry_validated=False,reason='No exact upstream metadata-only scene assertion established.')))
(R/'manifest.json').write_text(json.dumps(dict(schema_version=1,batch='ISO-IMAGE-FILTER-CONTROL-01',purpose='One family, three encoding-route variants; not three distinct global behaviors or upstream passes.',fixture_count=3,decoded_bytes_hex=raw.hex(),runlength_packets=packets,cases=cases),indent=2)+'\n')
print('Generated 3 byte-unique PDFs, one 54-byte numeric sample grid; raw/Flate/RunLength.')
