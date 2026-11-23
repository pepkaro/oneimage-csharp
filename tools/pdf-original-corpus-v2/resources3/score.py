#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Independent rectangle analytic controls; renderer output never defines expectation."""
from pathlib import Path
from itertools import combinations
import json,hashlib
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def expected(case,dpi):
 scale=dpi/72;w=round(case['width']*scale);h=round(case['height']*scale);yy,xx=np.mgrid[:h,:w];x=(xx+.5)/scale;y=(h-yy-.5)/scale
 rgb=np.full((h,w,3),255,np.uint8);mask=np.ones((h,w),bool);slack=1/scale
 for x0,y0,rw,rh,color in case['shape_rectangles']:
  x1,y1=x0+rw,y0+rh
  rgb[(x>=x0)&(x<x1)&(y>=y0)&(y<y1)]=color
  vertical=((abs(x-x0)<slack)|(abs(x-x1)<slack))&(y>=y0-slack)&(y<=y1+slack)
  horizontal=((abs(y-y0)<slack)|(abs(y-y1)<slack))&(x>=x0-slack)&(x<=x1+slack)
  mask &= ~(vertical|horizontal)
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
  rows.append(dict(id=r['id'],fixture_id=c['fixture_id'],page=c['page'],engine=r['engine'],dpi=r['dpi'],dimensions_match=dimensions,status='passed' if passed else 'failed',scored_pixels=int(mask.sum()),unscored_boundary_pixels=int((~mask).sum()),wrong_scored_pixels=wrong,samples=samples))
 pairs=[]
 for c in cases.values():
  for dpi in c['dpis']:
   _,mask=expected(c,dpi)
   for a,b in combinations(['pdfium','mupdf','pdfjs'],2):
    keys=[(c['id'],dpi,e) for e in (a,b)]
    wrong=int(np.any(images[keys[0]]!=images[keys[1]],axis=2)[mask].sum()) if all(k in images for k in keys) else None
    pairs.append(dict(id=c['id'],fixture_id=c['fixture_id'],page=c['page'],dpi=dpi,engines=[a,b],disagreeing_scored_pixels=wrong,status='passed' if wrong==0 else 'failed'))
 result=dict(unique_original_pdfs=len({c["file"] for c in cases.values()}),page_view_count=len(cases),executed=len(rows),passed=sum(r['status']=='passed' for r in rows),failed=sum(r['status']=='failed' for r in rows),skipped=0,sample_checks=sum(len(r['samples']) for r in rows),sample_passes=sum(s['passed'] for r in rows for s in r['samples']),pairwise_passes=sum(p['status']=='passed' for p in pairs),pairwise_failures=sum(p['status']=='failed' for p in pairs),upstream_inputs_executed=0,upstream_entries_validated=0,rows=rows,pairwise=pairs)
 (ROOT/'reference-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rows','pairwise']},indent=2))
if __name__=='__main__':main()
