#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;m=json.loads((R/'manifest.json').read_text());rows=[]
for c in m['cases']:
 for dpi in c['dpis']:
  scale=dpi/72;h=c['height']*dpi//72;w=c['width']*dpi//72;yy,xx=np.mgrid[:h,:w];xp=(xx+.5)/scale;yp=c['height']-(yy+.5)/scale;union=np.zeros((h,w),bool);arrays={};checks={}
  for e in ['pdfium','pdfjs','mupdf']:
   p=R/f"references/{c['id']}-{dpi}-{e}.png"
   if not p.exists():checks[e]=dict(passed=False,reason='missing reference');continue
   a=np.asarray(Image.open(p).convert('RGB'));arrays[e]=a
   if a.shape!=(h,w,3):checks[e]=dict(passed=False,reason='dimensions',actual_shape=list(a.shape));continue
   regions=[]
   for reg in c['expected_regions']:
    x,y,rw,rh=reg['rect'];mask=(xp>=x)&(xp<x+rw)&(yp>=y)&(yp<y+rh);union|=mask;assert mask.any();d=np.abs(a[mask].astype(int)-reg['rgb']).max(axis=1);regions.append(dict(id=reg['id'],pixels=int(mask.sum()),wrong=int((d!=0).sum()),max_delta=int(d.max())))
   checks[e]=dict(regions=regions,pixels=sum(v['pixels'] for v in regions),wrong=sum(v['wrong'] for v in regions),passed=all(v['wrong']==0 for v in regions))
  pairs=[]
  for a,b in [('pdfium','pdfjs'),('pdfium','mupdf'),('pdfjs','mupdf')]:
   if a not in arrays or b not in arrays or arrays[a].shape!=(h,w,3) or arrays[b].shape!=(h,w,3):pairs.append(dict(engines=[a,b],passed=False,reason='missing/different dimensions'));continue
   d=np.abs(arrays[a][union].astype(int)-arrays[b][union].astype(int)).max(axis=1);pairs.append(dict(engines=[a,b],pixels=int(union.sum()),different=int((d!=0).sum()),max_delta=int(d.max()),passed=bool((d==0).all())))
  rows.append(dict(id=c['id'],dpi=dpi,analytic=checks,pairwise=pairs,accepted=all(v['passed'] for v in checks.values()) and all(v['passed'] for v in pairs)))
accepted=[c['id'] for c in m['cases'] if all(v['accepted'] for v in rows if v['id']==c['id'])];held=[c['id'] for c in m['cases'] if c['id'] not in accepted]
result=dict(rule='Exact analytic and pairwise RGB on eight independently declared inset regions; exact160x120pt viewport; all boundaries unscored',accepted_fixture_ids=accepted,held_fixture_ids=held,rows=rows)
(R/'region-agreement.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(agreed=len(accepted),held=len(held),analytic_variants=sum(len(v['analytic']) for v in rows),pairwise_variants=sum(len(v['pairwise']) for v in rows))))
