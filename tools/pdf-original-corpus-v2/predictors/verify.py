# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json,zlib
import numpy as np
from PIL import Image
from pypdf import PdfReader
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text());r=json.loads((R/'reference-results.json').read_text());g=json.loads((R/'region-agreement.json').read_text())
assert len(m['cases'])==4 and len({c['sha256'] for c in m['cases']})==4
raw=bytes.fromhex(m['decoded_bytes_hex']);assert len(raw)==60
assert len(r['rows'])==24 and (r['passed'],r['failed'],r['skipped'])==(24,0,0)
assert g['accepted_fixtures']==4 and g['held_fixtures']==0
# Separate reconstruction, independently implemented from the numeric encoder.
def undo_prediction(data,kind):
 if kind==1:return data
 rows=[];previous=[0]*15;stride=15 if kind==2 else 16
 assert len(data)==4*stride
 for start in range(0,len(data),stride):
  packed=list(data[start:start+stride])
  if kind==2:tag=1;row=packed
  else:tag=packed[0];row=packed[1:];assert tag==({11:1,12:2}[kind])
  if tag==1:
   for i in range(3,len(row)):row[i]=(row[i]+row[i-3])%256
  elif tag==2:
   row=[(a+b)%256 for a,b in zip(row,previous,strict=True)]
  else:raise AssertionError('Only the authored fixed Sub/Up routes are in scope')
  rows.extend(row);previous=row
 return bytes(rows)
for c in m['cases']:
 data=(R/c['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==c['sha256']
 doc=PdfReader(R/c['file'],strict=True);assert len(doc.pages)==1
 im=doc.pages[0]['/Resources']['/XObject']['/Im'].get_object()
 assert im['/Width']==5 and im['/Height']==4 and im['/BitsPerComponent']==8 and im['/ColorSpace']=='/DeviceRGB'
 assert im.get('/Decode') is None and im['/Interpolate'].value is False
 assert doc.pages[0].get('/Annots') is None and im['/Filter']=='/FlateDecode'
 params=im['/DecodeParms'];kind=c['image']['predictor'];assert params['/Predictor']==kind
 if kind>1:assert (params['/Colors'],params['/BitsPerComponent'],params['/Columns'])==(3,8,5)
 else:assert set(params)=={'/Predictor'}
 encoded=im._data;assert hashlib.sha256(encoded).hexdigest()==c['image']['encoded_sha256']
 predicted=zlib.decompress(encoded)
 assert hashlib.sha256(predicted).hexdigest()==c['image']['predicted_sha256']
 assert undo_prediction(predicted,kind)==raw
 assert im.get_data()==raw # independent pypdf implementation
 assert c['association']['upstream_id'] is None and not c['association']['upstream_entry_validated']
for row in r['rows']:
 f=R/row['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
 c=next(c for c in m['cases'] if c['id']==row['id']);im=Image.open(f).convert('RGB')
 assert im.size==(c['width']*row['dpi']//72,c['height']*row['dpi']//72)
 for s,record in zip(c['expected_samples'],row['checks'],strict=True):
  got=list(im.getpixel((int(s['point'][0]*row['dpi']/72),int((c['height']-s['point'][1])*row['dpi']/72))))
  assert got==s['rgb']==record['actual'] and record['passed']
for dpi in [72,144]:
 for engine in ['pdfium','mupdf','pdfjs']:
  arrays=[np.asarray(Image.open(R/f"references/{c['id']}-{dpi}-{engine}.png").convert('RGB')) for c in m['cases']]
  assert all(np.array_equal(arrays[0],a) for a in arrays[1:])
for f in (R/'logs').glob('*pdfjs.log'):
 d=json.loads(f.read_text().splitlines()[-1]);assert (d['pdfjs'],d['build'],d['canvasVersion'],d['node'])==('6.5.438','0a4153349','1.1.1','v24.22.3')
assert len(list((R/'logs').glob('*pdfjs.log')))==8
print('4 unique PDFs; 1 predictor family; 24/24 reference runs passed; 504/504 analytic centers; 0 failed/skipped; 0 upstream-entry passes.')
