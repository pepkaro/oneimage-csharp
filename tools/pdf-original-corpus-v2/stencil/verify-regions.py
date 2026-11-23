# SPDX-License-Identifier: MIT
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;m=json.loads((R/'manifest.json').read_text());rows=[]
for c in m['cases']:
 for dpi in c['dpis']:
  h=c['height']*dpi//72;w=c['width']*dpi//72;yy,xx=np.mgrid[:h,:w];xp=(xx+.5)*72/dpi;yp=c['height']-(yy+.5)*72/dpi;union=np.zeros((h,w),bool);arrays={};checks={}
  for e in ['pdfium','pdfjs','mupdf']:
   a=np.asarray(Image.open(R/f"references/{c['id']}-{dpi}-{e}.png").convert('RGB'));assert a.shape==(h,w,3);arrays[e]=a;regions=[]
   for reg in c['expected_regions']:
    x,y,rw,rh=reg['rect'];mask=(xp>=x)&(xp<x+rw)&(yp>=y)&(yp<y+rh);assert mask.any();union|=mask;d=np.abs(a[mask].astype(int)-reg['rgb']).max(axis=1);regions.append(dict(id=reg['id'],pixels=int(mask.sum()),wrong=int((d!=0).sum()),max_delta=int(d.max())))
   checks[e]=dict(regions=regions,pixels=sum(v['pixels'] for v in regions),wrong=sum(v['wrong'] for v in regions),passed=all(v['wrong']==0 for v in regions))
  pairs=[]
  for a,b in [('pdfium','pdfjs'),('pdfium','mupdf'),('pdfjs','mupdf')]:
   d=np.abs(arrays[a][union].astype(int)-arrays[b][union].astype(int)).max(axis=1);pairs.append(dict(engines=[a,b],pixels=int(union.sum()),different=int((d!=0).sum()),max_delta=int(d.max())))
  rows.append(dict(id=c['id'],dpi=dpi,analytic=checks,pairwise=pairs,accepted=all(v['passed'] for v in checks.values()) and all(v['different']==0 for v in pairs)))
accepted=[c['id'] for c in m['cases'] if all(v['accepted'] for v in rows if v['id']==c['id'])];held=[c['id'] for c in m['cases'] if c['id'] not in accepted]
(R/'region-agreement.json').write_text(json.dumps(dict(rule='Exact RGB analytic and pairwise equality on predeclared two-point-inset interiors; boundaries unscored',accepted_fixture_ids=accepted,held_fixture_ids=held,rows=rows),indent=2)+'\n');print(dict(agreed=len(accepted),held=len(held)));assert accepted==[] and len(held)==3
