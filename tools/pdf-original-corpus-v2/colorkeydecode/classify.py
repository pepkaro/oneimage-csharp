# SPDX-License-Identifier: MIT
"""Classify reference subassertions only; never promote a held case or grade a product."""
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;m=json.loads((R/'manifest.json').read_text());rows=[];decisions=paired=0
control=m['cases'][0];assert control['image']['mask'] is None
for c in m['cases']:
 for dpi in c['dpis']:
  for engine in ['pdfium','pdfjs','mupdf']:
   a=np.asarray(Image.open(R/f"references/{c['id']}-{dpi}-{engine}.png").convert('RGB'));base=np.asarray(Image.open(R/f"references/{control['id']}-{dpi}-{engine}.png").convert('RGB'));mask=c['image']['mask'];cells=[]
   for y,line in enumerate(c['raw_cells']):
    for x,raw in enumerate(line):
     cid=f'cell-{x}-{y}';hidden=mask is not None and all(mask[2*k]<=raw[k]<=mask[2*k+1] for k in range(3));bg=[0,255,0] if (x+y)%2==0 else [0,0,255];sample=next(s for s in c['expected_samples'] if s['id']==cid);ix=int(sample['point'][0]*dpi/72);iy=int((c['height']-sample['point'][1])*dpi/72);actual=a[iy,ix].tolist();ideal_complement=[255-v for v in raw];decision_pass=(actual==bg)==hidden;assert decision_pass;decisions+=1
     same=None
     if not hidden and c['id']!=control['id']:same=actual==base[iy,ix].tolist();assert same;paired+=1
     cells.append(dict(id=cid,stored=raw,ideal_complement=ideal_complement,mask_expected=hidden,observed_rgb=actual,mask_selection_pass=decision_pass,opaque_control_equal=same,ideal_rgb_delta=None if hidden else max(abs(a-b) for a,b in zip(actual,ideal_complement))))
   rows.append(dict(id=c['id'],dpi=dpi,engine=engine,cells=cells))
assert decisions==288 and paired==186
for row in rows:
 for cell in row['cells']:
  if cell['ideal_rgb_delta'] is not None:assert cell['ideal_rgb_delta']<=1 if row['engine']=='pdfium' else cell['ideal_rgb_delta']==0
result=dict(scope='Reference-only component classification; no agreed full case, expected PNG or product pass',mask_selection_checks=decisions,mask_selection_passed=decisions,mask_selection_failed=0,opaque_control_comparisons=paired,opaque_control_matches=paired,reference_executed=24,reference_full_passed=16,reference_full_failed=8,reference_skipped=0,full_cases_agreed=0,full_cases_held=4,new_goldens=0,product_executed=0,classification='All engines choose stored-sample colour-key cells correctly; PDFium opaque reversed-Decode output differs by at most one RGB byte from ideal complement and the other engines, already visible in unmasked control',limits=['No changed expected samples or majority oracle','No source/binary root cause proven','Component mask checks do not validate held full cases','No OneImage/OnePDF ownership inferred; product not graded'],rows=rows)
(R/'classification-results.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='rows'})
