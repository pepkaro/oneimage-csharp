# SPDX-License-Identifier: MIT
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent; m=json.loads((R/'manifest.json').read_text());rows=[]
for c in m['cases']:
 for dpi in c['dpis']:
  scale=dpi/72;h=c['height']*dpi//72;w=c['width']*dpi//72;yy,xx=np.mgrid[:h,:w];xp=(xx+.5)/scale;yp=c['height']-(yy+.5)/scale;union=np.zeros((h,w),bool);arrays={};checks={}
  for e in ['pdfium','pdfjs','mupdf']:
   a=np.asarray(Image.open(R/f"references/{c['id']}-{dpi}-{e}.png").convert('RGB'));assert a.shape==(h,w,3);arrays[e]=a;regions=[]
   for reg in c['expected_regions']:
    x,y,rw,rh=reg['rect'];mask=(xp>=x)&(xp<x+rw)&(yp>=y)&(yp<y+rh);union|=mask;assert mask.any();d=np.abs(a[mask].astype(int)-reg['rgb']).max(axis=1)
    regions.append(dict(id=reg['id'],pixels=int(mask.sum()),wrong=int((d!=0).sum()),max_delta=int(d.max())))
   checks[e]=dict(regions=regions,pixels=sum(v['pixels'] for v in regions),wrong=sum(v['wrong'] for v in regions),passed=all(v['wrong']==0 for v in regions))
  pairs=[]
  for a,b in [('pdfium','pdfjs'),('pdfium','mupdf'),('pdfjs','mupdf')]:
   d=np.abs(arrays[a][union].astype(int)-arrays[b][union].astype(int)).max(axis=1);pairs.append(dict(engines=[a,b],pixels=int(union.sum()),different=int((d!=0).sum()),max_delta=int(d.max())))
  rows.append(dict(id=c['id'],dpi=dpi,analytic=checks,pairwise=pairs,accepted=all(v['passed'] for v in checks.values()) and all(v['different']==0 for v in pairs)))
accepted=[c['id'] for c in m['cases'] if all(v['accepted'] for v in rows if v['id']==c['id'])];assert len(accepted)==3
(R/'region-agreement.json').write_text(json.dumps(dict(rule='Exact RGB on independently declared cell interiors inset2pt, frame and paper regions; boundaries unscored',accepted_fixture_ids=accepted,held_fixture_ids=[],rows=rows),indent=2)+'\n')
print('3 agreed cases;18 analytic and18 pairwise checks pass')
