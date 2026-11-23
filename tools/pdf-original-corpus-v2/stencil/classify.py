# SPDX-License-Identifier: MIT
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent;m=json.loads((R/'manifest.json').read_text());rows=[];decisions=0;blackmarked=0
for c in m['cases']:
 for dpi in c['dpis']:
  for e in ['pdfium','pdfjs','mupdf']:
   a=np.asarray(Image.open(R/f"references/{c['id']}-{dpi}-{e}.png").convert('RGB'));checks=[]
   for k,p in enumerate(c['placements']):
    for y,line in enumerate(c['bits']):
     for x,bit in enumerate(line):
      mark=bit==(1 if c['image']['decode']==[1,0] else 0);bg=[255,255,255] if (x+y)%2==0 else [0,0,0];label=f'placement-{k}-cell-{x}-{y}';sample=next(s for s in c['expected_samples'] if s['id']==label);ix=int(sample['point'][0]*dpi/72);iy=int((c['height']-sample['point'][1])*dpi/72);actual=a[iy,ix].tolist();ideal=p['paint_rgb'] if mark else bg;delta=max(abs(v-w) for v,w in zip(actual,ideal));selection=(actual!=bg)==mark;assert selection;decisions+=1
      if e=='mupdf' and mark and bg==[0,0,0]:assert delta==1;blackmarked+=1
      else:assert delta==0
      checks.append(dict(id=label,stored_bit=bit,expected_mark=mark,background=bg,ideal_rgb=ideal,actual_rgb=actual,max_delta=delta,mask_selection_pass=selection))
   rows.append(dict(id=c['id'],dpi=dpi,engine=e,cells=checks))
assert decisions==648 and blackmarked==42
result=dict(scope='Reference-only component classification; no held full-case or product credit',reference_executed=18,reference_full_passed=12,reference_full_disagreed=6,reference_skipped=0,full_cases_agreed=0,full_cases_held=3,selected_expected_png=0,product_executed=0,mask_selection_checks=decisions,mask_selection_passes=decisions,mupdf_marked_black_centres_with_delta1=blackmarked,classification='MuPDF is one RGB byte below ideal foreground channels on marks over black at both DPIs; white-backed marks and all unmarked cells match the independent ideal. Polarity and current-colour decisions agree. Source/binary cause and normative8bit oracle not established.',limits=['Whole checkerboard cases remain held; no majority golden','Component decisions do not validate a full case','Independent white-backed controls are separate originals and close none of these holds','No OnePDF/OneImage ownership inferred; product not graded'],rows=rows)
(R/'classification-results.json').write_text(json.dumps(result,indent=2)+'\n');print({k:v for k,v in result.items() if k!='rows'})
