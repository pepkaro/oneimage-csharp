# SPDX-License-Identifier: MIT
from pathlib import Path
import json,numpy as np
from PIL import Image
R=Path(__file__).resolve().parent
manifest=json.loads((R/"manifest.json").read_text());rows=[]
for c in manifest["cases"]:
 for dpi in c["dpis"]:
  scale=dpi/72;records={};arrays={}
  for engine in ["pdfium","mupdf","pdfjs"]:
   a=np.asarray(Image.open(R/f"references/{c['id']}-{dpi}-{engine}.png").convert("RGB"));arrays[engine]=a
   yy,xx=np.mgrid[0:a.shape[0],0:a.shape[1]];xp=(xx+.5)/scale;yp=c["height"]-(yy+.5)/scale;checked=[]
   for reg in c["expected_regions"]:
    x,y,w,h=reg["rect"];mask=(xp>=x)&(xp<x+w)&(yp>=y)&(yp<y+h);assert mask.any()
    d=np.abs(a[mask].astype(int)-np.array(reg["rgb"])).max(axis=1)
    checked.append(dict(id=reg["id"],pixels=int(mask.sum()),wrong=int((d>0).sum()),max_delta=int(d.max())))
   records[engine]=dict(regions=checked,pixels=sum(x["pixels"] for x in checked),wrong=sum(x["wrong"] for x in checked),status="passed" if all(x["wrong"]==0 for x in checked) else "failed")
  union=np.zeros((c["height"]*dpi//72,c["width"]*dpi//72),bool);yy,xx=np.mgrid[0:union.shape[0],0:union.shape[1]];xp=(xx+.5)/scale;yp=c["height"]-(yy+.5)/scale
  for reg in c["expected_regions"]:
   x,y,w,h=reg["rect"];union|=(xp>=x)&(xp<x+w)&(yp>=y)&(yp<y+h)
  pairs=[]
  for a,b in [("pdfium","mupdf"),("pdfium","pdfjs"),("mupdf","pdfjs")]:
   d=np.abs(arrays[a][union].astype(int)-arrays[b][union].astype(int)).max(axis=1);pairs.append(dict(engines=[a,b],pixels=int(union.sum()),different=int((d>0).sum()),max_delta=int(d.max())))
  rows.append(dict(id=c["id"],dpi=dpi,analytic=records,pairwise=pairs,accepted=all(v["status"]=="passed" for v in records.values()) and all(p["different"]==0 for p in pairs)))
accepted=[c["id"] for c in manifest["cases"] if all(v["accepted"] for v in rows if v["id"]==c["id"])]
held=[c["id"] for c in manifest["cases"] if c["id"] not in accepted]
assert len(accepted)==4 and held==[]
result=dict(rule="Authored24pt cells inset2PDFpoints before region measurements; exact RGB analytic/pairwise tolerance0; edge bands remain unscored.",accepted_fixture_ids=accepted,held_fixture_ids=held,accepted_fixtures=len(accepted),held_fixtures=len(held),rows=rows)
(R/"region-agreement.json").write_text(json.dumps(result,indent=2)+"\n")
print("4 reference-agreed predictor variants eligible; 0 held; boundaries unscored.")
