#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
import sys,json
from pathlib import Path
engine,input,output,dpi=sys.argv[1:];dpi=float(dpi)
if engine=='pdfium':
 import pypdfium2 as p
 from pypdfium2.version import PYPDFIUM_INFO,PDFIUM_INFO
 assert str(PYPDFIUM_INFO)=='5.13.0' and str(PDFIUM_INFO)=='153.0.7999.0'
 doc=p.PdfDocument(input);assert len(doc)==1;page=doc[0];im=page.render(scale=dpi/72,fill_color=(255,255,255,255),draw_annots=False).to_pil().convert('RGB');im.save(output);meta=dict(engine='PDFium',version=str(PDFIUM_INFO),binding=str(PYPDFIUM_INFO));page.close();doc.close()
elif engine=='mupdf':
 import pymupdf as p
 assert p.VersionBind=='1.26.6' and p.VersionFitz=='1.26.11'
 doc=p.open(input);assert len(doc)==1;im=doc[0].get_pixmap(matrix=p.Matrix(dpi/72,dpi/72),alpha=False,annots=False);im.save(output);meta=dict(engine='MuPDF',version=p.VersionFitz,binding=p.VersionBind);doc.close()
else:raise ValueError(engine)
meta.update(dpi=dpi,page=0,annotations='none',background='white',page_bounds='visibleCropBox',rotation=0,user_unit=1);print(json.dumps(meta))
