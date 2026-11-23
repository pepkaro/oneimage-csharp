# SPDX-License-Identifier: MIT
from pathlib import Path
import os,sys,subprocess,json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
runtime=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path("/workspace/scratch/ee1a2fb9052d/pdf-checkpoint-20261123/references/node_modules/pdfjs-dist")
manifest=json.loads((R/"manifest.json").read_text());out=R/"references";out.mkdir(exist_ok=True);logs=R/"logs";logs.mkdir(exist_ok=True)
rows=[]
for c in manifest["cases"]:
 for dpi in c["dpis"]:
  for engine in ["pdfium","mupdf","pdfjs"]:
   target=out/f"{c['id']}-{dpi}-{engine}.png"
   if engine=="pdfjs":cmd=["node",str(R/"render-pdfjs.mjs"),str(runtime),str(R/c["file"]),str(target),str(dpi),"none"]
   else:cmd=[sys.executable,str(R/"render-native.py"),engine,str(R/c["file"]),str(target),str(dpi)]
   with (logs/(target.stem+".log")).open("w") as log:subprocess.run(cmd,stdout=log,stderr=subprocess.STDOUT,check=True)
   im=Image.open(target).convert("RGB");assert im.size==(c["width"]*dpi//72,c["height"]*dpi//72);checks=[]
   for s in c["expected_samples"]:
    x=int(s["point"][0]*dpi/72);y=int((c["height"]-s["point"][1])*dpi/72);actual=list(im.getpixel((x,y)));delta=max(abs(a-b) for a,b in zip(actual,s["rgb"]));checks.append(dict(id=s["id"],expected=s["rgb"],actual=actual,delta=delta,passed=delta<=s["tolerance"]))
   rows.append(dict(id=c["id"],dpi=dpi,engine=engine,file=str(target.relative_to(R)),sha256=hashlib.sha256(target.read_bytes()).hexdigest(),sample_count=len(checks),status="passed" if all(s["passed"] for s in checks) else "failed",checks=checks))
result=dict(fixture_count=len(manifest["cases"]),unique_pdfs=len({c["sha256"] for c in manifest["cases"]}),reference_runs=len(rows),passed=sum(r["status"]=="passed" for r in rows),failed=sum(r["status"]=="failed" for r in rows),skipped=0,unscored_edge_regions="Glyph ink/counter boundaries and all undeclared page regions are unscored; independent declared interior centers only in this report.",rows=rows,versions=dict(pdfium="153.0.7999.0",pypdfium2="5.13.0",mupdf="1.26.11",pymupdf="1.26.6",pdfjs="6.5.438",pdfjs_build="0a4153349",node="24.22.3",node_canvas="1.1.1"))
(R/"reference-results.json").write_text(json.dumps(result,indent=2)+"\n")
print(json.dumps({k:v for k,v in result.items() if k not in ["rows"]},indent=2))
