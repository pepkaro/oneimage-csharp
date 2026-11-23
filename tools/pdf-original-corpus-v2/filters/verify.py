# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json,zlib
import numpy as np
from PIL import Image
from pypdf import PdfReader
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text());r=json.loads((R/'reference-results.json').read_text());g=json.loads((R/'region-agreement.json').read_text())
assert len(m['cases'])==3 and len({c['sha256'] for c in m['cases']})==3
raw=bytes.fromhex(m['decoded_bytes_hex']);assert len(raw)==54
assert len(r['rows'])==18 and (r['passed'],r['failed'],r['skipped'])==(18,0,0)
assert g['accepted_fixtures']==3 and g['held_fixtures']==0
# A separately written literal/repeat decoder checks the new ordinary stream only.
def decode_runlength(encoded):
 out=bytearray();pos=0;types=[]
 while True:
  n=encoded[pos];pos+=1
  if n==128:
   assert pos==len(encoded);return bytes(out),types
  if n<128:
   length=n+1;assert pos+length<=len(encoded)
   out.extend(encoded[pos:pos+length]);pos+=length;types.append('literal')
  else:
   assert pos<len(encoded);out.extend([encoded[pos]]*(257-n));pos+=1;types.append('repeat')
for c in m['cases']:
 data=(R/c['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==c['sha256']
 doc=PdfReader(R/c['file'],strict=True);assert len(doc.pages)==1
 im=doc.pages[0]['/Resources']['/XObject']['/Im'].get_object()
 assert im['/Width']==6 and im['/Height']==3 and im['/BitsPerComponent']==8 and im['/ColorSpace']=='/DeviceRGB'
 assert im.get('/Decode') is None and im['/Interpolate'].value is False
 assert doc.pages[0].get('/Annots') is None
 encoded=im._data;assert hashlib.sha256(encoded).hexdigest()==c['image']['encoded_sha256']
 assert im.get_data()==raw  # independent public decoder, not generator's encoder
 if c['image']['filter']=='RunLengthDecode':
  decoded,types=decode_runlength(encoded);assert decoded==raw and set(types)=={'literal','repeat'}
 elif c['image']['filter']=='FlateDecode':assert zlib.decompress(encoded)==raw
 else:assert encoded==raw and '/Filter' not in im
 assert c['association']['upstream_id'] is None and not c['association']['upstream_entry_validated']
for row in r['rows']:
 f=R/row['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
 c=next(c for c in m['cases'] if c['id']==row['id']);im=Image.open(f).convert('RGB')
 assert im.size==(c['width']*row['dpi']//72,c['height']*row['dpi']//72)
 for s,record in zip(c['expected_samples'],row['checks'],strict=True):
  got=list(im.getpixel((int(s['point'][0]*row['dpi']/72),int((c['height']-s['point'][1])*row['dpi']/72))))
  assert got==s['rgb']==record['actual'] and record['passed']
# Same source samples must render identically across encoding variants, using the same engine/DPI.
for dpi in [72,144]:
 for engine in ['pdfium','mupdf','pdfjs']:
  images=[np.asarray(Image.open(R/f"references/{c['id']}-{dpi}-{engine}.png").convert('RGB')) for c in m['cases']]
  assert all(np.array_equal(images[0],im) for im in images[1:])
for f in (R/'logs').glob('*pdfjs.log'):
 d=json.loads(f.read_text().splitlines()[-1]);assert (d['pdfjs'],d['build'],d['canvasVersion'],d['node'])==('6.5.438','0a4153349','1.1.1','v24.22.3')
assert len(list((R/'logs').glob('*pdfjs.log')))==6
print('3 unique PDFs; 1 lossless-filter family; 18/18 reference runs passed; 342/342 analytic centers; 0 failed/skipped; 0 upstream-entry passes.')
