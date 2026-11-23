#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Score references against declared analytic scene regions, never against a product image."""
from pathlib import Path
import hashlib,json
import numpy as np
from PIL import Image
ROOT=Path(__file__).resolve().parent
def expected(case,dpi):
 scale=dpi/72;w=round(case["display_width_points"]*scale);h=round(case["display_height_points"]*scale);yy,xx=np.mgrid[:h,:w];x=(xx+.5)/scale;y=(h-yy-.5)/scale
 rgb=np.full((h,w,3),255,np.uint8);scored=np.ones((h,w),bool)
 for x0,y0,rw,rh,color in case["expected_regions"]:
  inside=(x>=x0)&(x<x0+rw)&(y>=y0)&(y<y0+rh);rgb[inside]=color
  # A fixed one-device-pixel boundary band is excluded before any renderer output is read.
  slack=1/scale
  vertical=((abs(x-x0)<slack)|(abs(x-x0-rw)<slack))&(y>=y0-slack)&(y<=y0+rh+slack)
  horizontal=((abs(y-y0)<slack)|(abs(y-y0-rh)<slack))&(x>=x0-slack)&(x<=x0+rw+slack)
  scored &= ~(vertical|horizontal)
 return rgb,scored
def main():
 cases={c["id"]:c for c in json.loads((ROOT/"manifest.json").read_text())["cases"]};records=json.loads((ROOT/"reference-renders.json").read_text())["records"];rows=[];out=ROOT/"analytic";out.mkdir(exist_ok=True)
 for case in cases.values():
  for dpi in case["dpis"]:
   rgb,mask=expected(case,dpi);Image.fromarray(rgb).save(out/(case["id"]+"-"+str(dpi)+"-expected.png"));Image.fromarray(mask.astype(np.uint8)*255).save(out/(case["id"]+"-"+str(dpi)+"-score-mask.png"))
 for record in records:
  case=cases[record["id"]];rgb,mask=expected(case,record["dpi"]);actual=np.asarray(Image.open(ROOT/record["output"]).convert("RGB"));dimension_match=actual.shape==rgb.shape
  if not dimension_match:
   rows.append(dict(id=case["id"],engine=record["engine"],dpi=record["dpi"],status="failed",reason="native dimensions disagree with declared physical viewport",expected_size=[rgb.shape[1],rgb.shape[0]],actual_size=[actual.shape[1],actual.shape[0]],pixel_comparison="unscored rather than resized",capability=case["required_capability"]));continue
  delta=np.abs(actual.astype(int)-rgb.astype(int)).max(axis=2);wrong=int(((delta>0)&mask).sum());samples=[]
  for sample in case["samples"]:
   x=int(sample["x"]*record["dpi"]/72);y=int((case["display_height_points"]-sample["y"])*record["dpi"]/72);got=actual[y,x].astype(int);err=int(np.abs(got-np.array(sample["rgb"])).max());samples.append(dict(id=sample["id"],actual=got.tolist(),delta=err,passed=err<=sample["tolerance"]))
  passed=wrong==0 and all(s["passed"] for s in samples)
  rows.append(dict(id=case["id"],engine=record["engine"],dpi=record["dpi"],status="passed" if passed else "failed",scored_pixels=int(mask.sum()),unscored_edge_pixels=int((~mask).sum()),wrong_scored_pixels=wrong,max_scored_channel_error=int(delta[mask].max()),samples=samples))
 summary={e:{s:sum(v["engine"]==e and v["status"]==s for v in rows) for s in ["passed","failed"]} for e in ["pdfium","mupdf","pdfjs"]}
 result=dict(unique_fixtures=len(cases),reference_runs=len(rows),sample_coordinate_system="upright visible display points",oracle="independent rectangle geometry, one device-pixel edge band unscored",summary=summary,rows=rows,upstream_inputs_executed=0,upstream_rows_validated=0,exact_upstream_mappings=0)
 (ROOT/"reference-results.json").write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
