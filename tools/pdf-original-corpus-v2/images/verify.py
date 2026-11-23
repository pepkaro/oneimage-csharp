# SPDX-License-Identifier: MIT
from pathlib import Path
import json,hashlib
from PIL import Image
R=Path(__file__).resolve().parent
m=json.loads((R/"manifest.json").read_text());r=json.loads((R/"reference-results.json").read_text())
assert m["fixture_count"]==8 and len(m["cases"])==8 and len({c["sha256"] for c in m["cases"]})==8
for c in m["cases"]:
 assert hashlib.sha256((R/c["file"]).read_bytes()).hexdigest()==c["sha256"]
 assert c["association"]["upstream_id"] is None and not c["association"]["upstream_entry_validated"]
 assert c["width"]==240 and c["height"]==180 and c["dpis"]==[72,144]
assert len(r["rows"])==48 and r["passed"]==46 and r["failed"]==2 and r["skipped"]==0
for row in r["rows"]:
 f=R/row["file"];assert hashlib.sha256(f.read_bytes()).hexdigest()==row["sha256"]
 c=next(c for c in m["cases"] if c["id"]==row["id"]);im=Image.open(f).convert("RGB")
 for expected,recorded in zip(c["expected_samples"],row["checks"],strict=True):
  x=int(expected["point"][0]*row["dpi"]/72);y=int((c["height"]-expected["point"][1])*row["dpi"]/72)
  got=list(im.getpixel((x,y)));delta=max(abs(a-b) for a,b in zip(got,expected["rgb"]));assert got==recorded["actual"] and delta==recorded["delta"]
 if row["status"]=="failed":
  assert row["engine"]=="pdfium" and row["id"]=="img-rgb8-channel-decode"
  bad=[s for s in row["checks"] if not s["passed"]];assert len(bad)==4 and all(s["delta"]==1 for s in bad)
for f in (R/"logs").glob("*pdfjs.log"):
 d=json.loads(f.read_text().splitlines()[-1]);assert (d["pdfjs"],d["build"],d["canvasVersion"],d["node"])==("6.5.438","0a4153349","1.1.1","v24.22.3")
print("8 unique originals; 48 reference runs:46 exact passes,2 preserved PDFium quantization disagreements;0 upstream-entry passes.")
