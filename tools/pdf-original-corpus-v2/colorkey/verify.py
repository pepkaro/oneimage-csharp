# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json
from PIL import Image
from pypdf import PdfReader
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text());r=json.loads((R/'reference-results.json').read_text());g=json.loads((R/'region-agreement.json').read_text())
assert len(m['cases'])==3 and len({c['sha256'] for c in m['cases']})==3
raw=bytes.fromhex(m['decoded_bytes_hex']);assert len(raw)==60
assert len(r['rows'])==18 and (r['passed'],r['failed'],r['skipped'])==(18,0,0)
assert g['accepted_fixtures']==3 and g['held_fixtures']==0
# Independently enumerated from authored source coordinates, before reference scoring.
masked_ids={'img-colorkey-control':set(),'img-colorkey-exact':{'cell-2-0'},'img-colorkey-range':{'cell-0-0','cell-1-0','cell-2-0','cell-4-1','cell-0-2','cell-1-2','cell-0-3','cell-1-3'}}
for c in m['cases']:
 data=(R/c['file']).read_bytes();assert hashlib.sha256(data).hexdigest()==c['sha256']
 doc=PdfReader(R/c['file'],strict=True);assert len(doc.pages)==1
 im=doc.pages[0]['/Resources']['/XObject']['/Im'].get_object()
 assert (im['/Width'],im['/Height'],im['/BitsPerComponent'],im['/ColorSpace'])==(5,4,8,'/DeviceRGB')
 assert im['/Interpolate'].value is False and im.get('/Decode') is None
 assert all(k not in im for k in ['/SMask','/Matte','/SMaskInData','/ImageMask'])
 assert doc.pages[0].get('/Annots') is None and im.get_data()==raw
 assert hashlib.sha256(im._data).hexdigest()==c['image']['encoded_sha256']
 mask=c['image']['mask']
 assert (list(im['/Mask']) if '/Mask' in im else None)==mask
 actual_masked=set()
 for index in range(20):
  rgb=list(raw[index*3:index*3+3]);s=c['expected_samples'][index]
  # Component-range rejection is independent of generator's all-in-range expression.
  visible=mask is None or any(value<mask[2*k] or value>mask[2*k+1] for k,value in enumerate(rgb))
  if not visible:actual_masked.add(s['id'])
  assert s['source_rgb']==rgb and s['masked']==(not visible)
  assert s['rgb']==(rgb if visible else [255,255,255])
 assert actual_masked==masked_ids[c['id']] and len(actual_masked)==c['image']['masked_cells']
 assert c['association']['upstream_id'] is None and not c['association']['upstream_entry_validated']
for row in r['rows']:
 f=R/row['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
 c=next(c for c in m['cases'] if c['id']==row['id']);im=Image.open(f).convert('RGB')
 assert im.size==(c['width']*row['dpi']//72,c['height']*row['dpi']//72)
 for s,record in zip(c['expected_samples'],row['checks'],strict=True):
  got=list(im.getpixel((int(s['point'][0]*row['dpi']/72),int((c['height']-s['point'][1])*row['dpi']/72))))
  assert got==s['rgb']==record['actual'] and record['passed']
for f in (R/'logs').glob('*pdfjs.log'):
 d=json.loads(f.read_text().splitlines()[-1]);assert (d['pdfjs'],d['build'],d['canvasVersion'],d['node'])==('6.5.438','0a4153349','1.1.1','v24.22.3')
assert len(list((R/'logs').glob('*pdfjs.log')))==6
print('3 unique PDFs; 1 color-key family; 18/18 reference runs and 378/378 analytic centers pass; 0 failed/skipped; 0 upstream-entry passes.')
