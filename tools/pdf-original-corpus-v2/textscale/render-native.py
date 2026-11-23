# SPDX-License-Identifier: MIT
from pathlib import Path
import sys
engine,source,destination,dpi=sys.argv[1:];scale=int(dpi)/72
if engine=="pdfium":
 import pypdfium2 as p
 assert str(p.PDFIUM_INFO)=="153.0.7999.0" and str(p.PYPDFIUM_INFO)=="5.13.0"
 with p.PdfDocument(source) as doc:
  assert len(doc)==1
  page=doc[0];bmp=page.render(scale=scale,rotation=0,draw_annots=False,fill_color=(255,255,255,255));bmp.to_pil().convert("RGB").save(destination);bmp.close();page.close()
elif engine=="mupdf":
 import pymupdf as p
 assert p.version[:2]==("1.26.6","1.26.11")
 with p.open(source) as doc:
  assert len(doc)==1
  doc[0].get_pixmap(matrix=p.Matrix(scale,scale),alpha=False,annots=False).save(destination)
else:raise ValueError(engine)
