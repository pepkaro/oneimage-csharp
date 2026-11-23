#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent

def main():
 cases={c['id']:c for c in json.loads((ROOT/'manifest.json').read_text())['cases']};rows=[]
 for r in json.loads((ROOT/'reference-renders.json').read_text())['records']:
  c=cases[r['id']];a=np.asarray(Image.open(ROOT/r['output']).convert('RGB'));scale=r['dpi']/72;h,w=a.shape[:2];yy,xx=np.mgrid[:h,:w];x=(xx+.5)/scale;y=(h-yy-.5)/scale;regions=[]
  for region in c['expected_regions']:
   x0,y0,rw,rh=region['rect'];mask=(x>=x0)&(x<x0+rw)&(y>=y0)&(y<y0+rh);count=int(mask.sum());wrong=int(np.any(a!=region['rgb'],axis=2)[mask].sum());assert count>0
   regions.append(dict(id=region['id'],pixels=count,wrong_pixels=wrong,passed=wrong==0))
  rows.append(dict(id=c['id'],fixture_id=c['fixture_id'],page=c['page'],dpi=r['dpi'],engine=r['engine'],passed=all(region['passed'] for region in regions),regions=regions))
 result=dict(executed_reference_variants=len(rows),passed=sum(r['passed'] for r in rows),failed=sum(not r['passed'] for r in rows),region_checks=sum(len(r['regions']) for r in rows),region_passes=sum(v['passed'] for r in rows for v in r['regions']),rows=rows)
 (ROOT/'region-agreement.json').write_text(json.dumps(result,indent=2)+'\n');assert result['passed']==30 and result['region_passes']==180;print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
if __name__=='__main__':main()
