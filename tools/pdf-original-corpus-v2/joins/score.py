#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent signed-distance analytic controls; renderer output never defines expectation."""
from pathlib import Path
from itertools import combinations
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def expected(case,dpi):
 scale=dpi/72;w=round(120*scale);h=round(100*scale);yy,xx=np.mgrid[:h,:w];x=(xx+.5)/scale;y=(h-yy-.5)/scale
 def rectangle(x0,y0,x1,y1):return (x>=x0)&(x<=x1)&(y>=y0)&(y<=y1)
 body=rectangle(30,20,70,40)|rectangle(60,30,80,70)
 quadrant=rectangle(70,20,80,30);dx=x-70;dy=y-30
 if case['join_style']==0:extension=quadrant
 elif case['join_style']==1:extension=quadrant&(dx*dx+dy*dy<=100)
 else:extension=quadrant&(dx-dy<=10)
 inside=body|extension;rgb=np.full((h,w,3),255,np.uint8);rgb[inside]=[255,0,0]
 # One conservative, identical mask across variants; not learned from images.
 mask=np.ones((h,w),bool);slack=1/scale
 for x0,y0,x1,y1 in [(30,20,70,40),(60,30,80,70),(70,20,80,30)]:
  vertical=((abs(x-x0)<slack)|(abs(x-x1)<slack))&(y>=y0-slack)&(y<=y1+slack)
  horizontal=((abs(y-y0)<slack)|(abs(y-y1)<slack))&(x>=x0-slack)&(x<=x1+slack)
  mask &= ~(vertical|horizontal)
 sector=(x>=70-slack)&(x<=80+slack)&(y>=20-slack)&(y<=30+slack)
 mask &= ~(sector&(abs(np.hypot(dx,dy)-10)<slack))
 mask &= ~(sector&(abs(dx-dy-10)/np.sqrt(2)<slack))
 return rgb,mask

def main():
 cases={c['id']:c for c in json.loads((ROOT/'manifest.json').read_text())['cases']};renders=json.loads((ROOT/'reference-renders.json').read_text())['records'];out=ROOT/'analytic';out.mkdir(exist_ok=True);rows=[];images={}
 for c in cases.values():
  for dpi in c['dpis']:
   rgb,mask=expected(c,dpi);Image.fromarray(rgb).save(out/f'{c["id"]}-{dpi}-expected.png');Image.fromarray(mask.astype(np.uint8)*255).save(out/f'{c["id"]}-{dpi}-score-mask.png')
 for r in renders:
  c=cases[r['id']];rgb,mask=expected(c,r['dpi']);a=np.asarray(Image.open(ROOT/r['output']).convert('RGB'));dimensions=a.shape==rgb.shape;samples=[]
  if dimensions:
   images[(r['id'],r['dpi'],r['engine'])]=a
   wrong=int(np.any(a!=rgb,axis=2)[mask].sum())
   for s in c['samples']:
    got=a[int((100-s['y'])*r['dpi']/72),int(s['x']*r['dpi']/72)].tolist();samples.append(dict(id=s['id'],actual=got,expected=s['rgb'],passed=got==s['rgb']))
  else:wrong=None
  passed=dimensions and wrong==0 and all(s['passed'] for s in samples)
  rows.append(dict(id=r['id'],engine=r['engine'],dpi=r['dpi'],dimensions_match=dimensions,status='passed' if passed else 'failed',scored_pixels=int(mask.sum()),unscored_boundary_pixels=int((~mask).sum()),wrong_scored_pixels=wrong,samples=samples))
 pairs=[]
 for c in cases.values():
  for dpi in c['dpis']:
   _,mask=expected(c,dpi)
   for a,b in combinations(['pdfium','mupdf','pdfjs'],2):
    keys=[(c['id'],dpi,e) for e in (a,b)]
    wrong=int(np.any(images[keys[0]]!=images[keys[1]],axis=2)[mask].sum()) if all(k in images for k in keys) else None
    pairs.append(dict(id=c['id'],dpi=dpi,engines=[a,b],disagreeing_scored_pixels=wrong,status='passed' if wrong==0 else 'failed'))
 result=dict(unique_original_pdfs=len(cases),executed=len(rows),passed=sum(r['status']=='passed' for r in rows),failed=sum(r['status']=='failed' for r in rows),skipped=0,sample_checks=sum(len(r['samples']) for r in rows),sample_passes=sum(s['passed'] for r in rows for s in r['samples']),pairwise_passes=sum(p['status']=='passed' for p in pairs),pairwise_failures=sum(p['status']=='failed' for p in pairs),upstream_inputs_executed=0,upstream_entries_validated=0,rows=rows,pairwise=pairs)
 (ROOT/'reference-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rows','pairwise']},indent=2))
if __name__=='__main__':main()
