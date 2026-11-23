# SPDX-License-Identifier: MIT
from pathlib import Path
import json,hashlib
from pypdf import PdfReader
R=Path(__file__).resolve().parent;m=json.loads((R/'manifest.json').read_text());rows=[]
for c in m['cases']:
 p=R/c['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'];doc=PdfReader(p);assert len(doc.pages)==1
 im=doc.pages[0]['/Resources']['/XObject']['/Im'].get_object();raw=im.get_data();assert len(raw)==36 and hashlib.sha256(raw).hexdigest()==c['image']['raw_sha256']
 assert raw==bytes(v for row in c['raw_cells'] for cell in row for v in cell)
 assert im['/Width']==4 and im['/Height']==3 and im['/BitsPerComponent']==8 and im['/ColorSpace']=='/DeviceRGB'
 assert '/Decode' not in im and '/SMask' not in im and im['/Interpolate'].value is False
 mask=c['image']['mask'];assert (list(im['/Mask'])==mask) if mask else ('/Mask' not in im)
 masked=[]
 for y,row in enumerate(c['raw_cells']):
  for x,cell in enumerate(row):
   keyed=mask is not None and all(mask[2*k]<=cell[k]<=mask[2*k+1] for k in range(3))
   if keyed:masked.append(f'cell-{x}-{y}')
   expected=([0,255,0] if (x+y)%2==0 else [0,0,255]) if keyed else cell
   sample=next(s for s in c['expected_samples'] if s['id']==f'cell-{x}-{y}');assert sample['rgb']==expected
 assert masked==c['masked_cell_ids'];rows.append(dict(id=c['id'],raw_bytes=len(raw),mask=mask,masked_cell_ids=masked,passed=True))
assert [len(x['masked_cell_ids']) for x in rows]==[0,1,5]
(R/'structure-results.json').write_text(json.dumps(dict(passed=len(rows),failed=0,rows=rows),indent=2)+'\n')
print('3 parsed valid RGB cases; original bytes and analytic masks verified')
