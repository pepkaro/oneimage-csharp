# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
# Original adapter. Install dependencies separately under their own licenses.
from pathlib import Path
import sys,json,hashlib,subprocess
import fitz,pypdfium2 as pdfium
from PIL import Image
if len(sys.argv)!=4:raise SystemExit('Usage: python render-references.py input.pdf output-dir /external/node_modules/pdfjs-dist')
pdf=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir(parents=True,exist_ok=True);dpi=144;records={}
fitz.TOOLS.set_aa_level(8)
with fitz.open(pdf) as doc:
 assert len(doc)==1 and doc[0].rotation==0
 assert tuple(doc[0].mediabox)==(0,0,192,128) and tuple(doc[0].cropbox)==(0,0,192,128)
 doc[0].get_pixmap(matrix=fitz.Matrix(2,2),alpha=False,annots=True).save(str(out/(pdf.stem+'-mupdf.png')))
doc=pdfium.PdfDocument(pdf);page=doc[0];bitmap=page.render(scale=2,fill_color=(255,255,255,255),draw_annots=True);bitmap.to_pil().save(out/(pdf.stem+'-pdfium.png'));bitmap.close();page.close();doc.close()
cmd=['node',str(Path(__file__).with_name('render-pdfjs.mjs')),sys.argv[3],str(pdf),str(out/(pdf.stem+'-pdfjs.png')),str(dpi)]
r=subprocess.run(cmd,capture_output=True,text=True,check=True);records['pdfjs']=json.loads(r.stdout.strip().splitlines()[-1]);records['versions']={'pypdfium2':str(pdfium.PYPDFIUM_INFO),'pdfium':str(pdfium.PDFIUM_INFO),'pymupdf':fitz.VersionBind,'mupdf':fitz.VersionFitz}
for engine in ['mupdf','pdfium','pdfjs']:
 p=out/(pdf.stem+'-'+engine+'.png');im=Image.open(p);records[engine+'Image']={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'width':im.width,'height':im.height}
records['settings']={'dpi':dpi,'page':0,'rotation':0,'MediaBox':[0,0,192,128],'CropBox':[0,0,192,128],'background':'opaque white','annotations':'enabled (none in these fixtures)','MuPDFGraphicsAA':8,'MuPDFTextAA':8,'PDFiumAA':'default','PDFjsBackend':'Node Canvas; not browser Canvas','noPixelResizingOrEditing':True}
(out/(pdf.stem+'-reference-settings.json')).write_text(json.dumps(records,indent=2)+'\n')
