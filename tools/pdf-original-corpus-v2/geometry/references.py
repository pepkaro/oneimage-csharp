#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json,subprocess,os
import pypdfium2 as pdfium
import pymupdf
ROOT=Path(__file__).resolve().parent
assert str(pdfium.PDFIUM_INFO)=="153.0.7999.0" and str(pdfium.PYPDFIUM_INFO)=="5.13.0"
assert pymupdf.version[:2]==("1.26.6","1.26.11")
PDFJS_ROOT=Path(os.environ["PDFJS_ROOT"]).resolve()
def hashfile(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 manifest=json.loads((ROOT/"manifest.json").read_text());records=[];out=ROOT/"references";out.mkdir(exist_ok=True)
 for case in manifest["cases"]:
  src=ROOT/case["file"];assert hashfile(src)==case["sha256"]
  for dpi in case["dpis"]:
   scale=dpi/72
   for engine in ["pdfium","mupdf","pdfjs"]:
    target=out/(case["id"]+"-"+str(dpi)+"-"+engine+".png")
    if engine=="pdfium":
     with pdfium.PdfDocument(src) as doc:
      assert len(doc)==1
      pg=doc[0];bmp=pg.render(scale=scale*case.get("user_unit",1),draw_annots=False,fill_color=(255,255,255,255));image=bmp.to_pil().convert("RGB");image.save(target);size=image.size;bmp.close();pg.close()
     meta=dict(engine="PDFium",version=str(pdfium.PDFIUM_INFO),binding=str(pdfium.PYPDFIUM_INFO),width=size[0],height=size[1],rotation="page-declared",pixels_per_canvas_unit=scale*case.get("user_unit",1),authored_user_unit=case.get("user_unit",1))
    elif engine=="mupdf":
     with pymupdf.open(src) as doc:
      assert len(doc)==1
      pg=doc[0];pix=pg.get_pixmap(matrix=pymupdf.Matrix(scale,scale),alpha=False,annots=False);pix.save(target)
     meta=dict(engine="MuPDF",version=pymupdf.version[1],binding=pymupdf.version[0],width=pix.width,height=pix.height,rotation="page-declared")
    else:
     result=subprocess.run(["node",str(ROOT/"render-pdfjs.mjs"),str(PDFJS_ROOT),str(src),str(target),str(dpi)],text=True,capture_output=True,check=True)
     (out/(target.stem+".stderr")).write_text(result.stderr);meta=json.loads(result.stdout.splitlines()[-1])
    records.append(dict(id=case["id"],engine=engine,dpi=dpi,page=0,settings=dict(background="white",annotations="none",page_box="CropBox falling back to MediaBox",physical_scale="dpi/72 with declared page transform"),input_sha256=case["sha256"],output=str(target.relative_to(ROOT)),sha256=hashfile(target),metadata=meta))
 (ROOT/"reference-renders.json").write_text(json.dumps(dict(render_count=len(records),records=records),indent=2)+"\n")
 print(json.dumps(dict(reference_renders=len(records),unique_inputs=len(manifest["cases"])),indent=2))
if __name__=="__main__":main()
