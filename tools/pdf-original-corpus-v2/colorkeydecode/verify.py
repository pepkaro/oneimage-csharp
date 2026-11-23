# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json
from pypdf import PdfReader
R=Path(__file__).resolve().parent;m=json.loads((R/'manifest.json').read_text());rows=[]
for c in m['cases']:
 p=R/c['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'];doc=PdfReader(p);assert len(doc.pages)==1
 page=doc.pages[0];assert list(page.mediabox)==[0,0,180,140];im=page['/Resources']['/XObject']['/Im'].get_object();raw=im.get_data();assert len(raw)==36 and hashlib.sha256(raw).hexdigest()==c['image']['raw_sha256']
 assert im['/Width']==4 and im['/Height']==3 and im['/ColorSpace']=='/DeviceRGB' and im['/BitsPerComponent']==8
 assert list(im['/Decode'])==[1,0,1,0,1,0] and im['/Interpolate'].value is False and '/SMask' not in im and im['/Filter']=='/FlateDecode'
 mask=list(im['/Mask']) if '/Mask' in im else None;assert mask==c['image']['mask'];masked=[];decoded_only=[]
 for n in range(12):
  y,x=divmod(n,4);cell=list(raw[3*n:3*n+3]);assert cell==c['raw_cells'][y][x];decoded=[255-v for v in cell]
  hidden=mask is not None and all(mask[2*k]<=cell[k]<=mask[2*k+1] for k in range(3));after=mask is not None and all(mask[2*k]<=decoded[k]<=mask[2*k+1] for k in range(3));label=f'cell-{x}-{y}'
  if hidden:masked.append(label)
  if after and not hidden:decoded_only.append(label)
  expected=([0,255,0] if (x+y)%2==0 else [0,0,255]) if hidden else decoded
  assert next(v for v in c['expected_samples'] if v['id']==label)['rgb']==expected
 assert masked==c['masked_cell_ids'] and decoded_only==c['decoded_only_match_ids']
 rows.append(dict(id=c['id'],raw_bytes=len(raw),masked_cell_ids=masked,decoded_only_match_ids=decoded_only,passed=True))
assert [len(r['masked_cell_ids']) for r in rows]==[0,1,1,3]
assert [len(r['decoded_only_match_ids']) for r in rows]==[0,1,1,3]
(R/'structure-results.json').write_text(json.dumps(dict(passed=4,failed=0,rows=rows),indent=2)+'\n');print('4 parsed RGB8 Decode/key cases; stored-sample decisions and exact complement controls verified')
