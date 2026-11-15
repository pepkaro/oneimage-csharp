# SPDX-License-Identifier: MIT
# Copyright (c) 2026 OneImage contributors
import json, hashlib, platform, argparse
from pathlib import Path
import pypdfium2 as pdfium
import pymupdf
from PIL import Image, __version__ as pillow_version
parser=argparse.ArgumentParser(); parser.add_argument("output",type=Path); r=parser.parse_args().output
cases=json.loads((r/'cases.json').read_text())
for dpi in (72,144):
    for engine in ('pdfium','mupdf'): (r/f'{engine}-{dpi}').mkdir(exist_ok=True)
    for case in cases:
        data=(r/'pdf'/(case['name']+'.pdf')).read_bytes()
        assert hashlib.sha256(data).hexdigest()==case['input_sha256']
        with pdfium.PdfDocument(data) as doc:
            page=doc[0]; bitmap=page.render(scale=dpi/72,rotation=0,fill_color=(255,255,255,255),draw_annots=False)
            bitmap.to_pil().convert('RGB').save(r/f'pdfium-{dpi}'/(case['name']+'.png')); bitmap.close(); page.close()
        with pymupdf.open(stream=data,filetype='pdf') as doc:
            pix=doc[0].get_pixmap(matrix=pymupdf.Matrix(dpi/72,dpi/72),alpha=False,annots=False)
            Image.frombytes('RGB',(pix.width,pix.height),pix.samples).save(r/f'mupdf-{dpi}'/(case['name']+'.png'))
(r/'reference-settings.json').write_text(json.dumps(dict(pypdfium2=pdfium.PYPDFIUM_INFO.version,pdfium=pdfium.PDFIUM_INFO.version,pymupdf=pymupdf.VersionBind,mupdf=pymupdf.VersionFitz,pillow=pillow_version,python=platform.python_version(),dpi=[72,144],cropbox='MediaBox = CropBox = [0 0 192 144]',rotation=0,background='opaque white',annotations=False,edits='none'),indent=2)+'\n')
print(f'Rendered {len(cases)} original controls with both references at both DPI settings.')
