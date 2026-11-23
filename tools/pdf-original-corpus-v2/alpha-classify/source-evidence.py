# SPDX-License-Identifier: MIT
"""Read only pinned renderer implementation sources; never fetch PDF/test assets.
Stores hashes and original summaries, not third-party source files.
"""
from pathlib import Path
import urllib.request,json,hashlib
import pypdfium2,pypdfium2_raw,pymupdf
R=Path(__file__).resolve().parent
PDFIUM='e9fc01804a0c5224ea780ad782abb8cfede628ef';MUPDF='d189cc13194a1e32026b6161b543df02c120aac2';PDFJS='0a4153349dc473ba950fc17941c5ca7eda43c1de'
sources=[
 ('pdfium-alpha','https://raw.githubusercontent.com/chromium/pdfium/'+PDFIUM+'/core/fpdfapi/render/cpdf_renderstatus.cpp','GetFillArgbForType3/GetStrokeArgb','Fill/stroke alpha is converted to an integer after multiplication by255, without rounding.'),
 ('pdfium-blend','https://raw.githubusercontent.com/chromium/pdfium/'+PDFIUM+'/core/fxge/dib/fx_dib.h','AlphaMerge','RGB channels use integer weighted source/backdrop blending over255.'),
 ('pdfium-route','https://raw.githubusercontent.com/chromium/pdfium/'+PDFIUM+'/core/fxge/dib/cfx_scanlinecompositor.cpp','AlphaMergeToDest','The RGB scanline route calls the same channel blend helper.'),
 ('mupdf-alpha','https://raw.githubusercontent.com/ArtifexSoftware/mupdf/'+MUPDF+'/source/fitz/draw-device.c','resolve_color','The solid-color alpha byte receives alpha multiplied by255.'),
 ('mupdf-blend','https://raw.githubusercontent.com/ArtifexSoftware/mupdf/'+MUPDF+'/source/fitz/draw-paint.c','template_solid_color_N_sa / fz_get_solid_color_painter','Opaque RGB interiors select a solid-color painter with an expanded alpha weight.'),
 ('mupdf-weight','https://raw.githubusercontent.com/ArtifexSoftware/mupdf/'+MUPDF+'/include/mupdf/fitz/geometry.h','FZ_EXPAND / FZ_BLEND','Alpha is expanded to a256-step weight; channel blending uses a right-shift integer result.'),
 ('pdfjs-canvas','https://raw.githubusercontent.com/mozilla/pdf.js/'+PDFJS+'/src/display/canvas.js','CanvasGraphics.setGState / stroke','PDF alpha is assigned to Canvas globalAlpha rather than converted through these native integer helpers.')]
rows=[]
for id,url,symbol,summary in sources:
 data=urllib.request.urlopen(url,timeout=30).read();rows.append(dict(id=id,url=url,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data),symbol=symbol,summary=summary,third_party_source_redistributed=False))
files=[]
for root in [Path(pypdfium2_raw.__file__).parent,Path(pymupdf.__file__).parent]:
 for f in root.glob('*'):
  if f.is_file() and (f.name=='libpdfium.so' or ('mupdf' in f.name and '.so' in f.name)):
   files.append(dict(name=f.name,sha256=hashlib.sha256(f.read_bytes()).hexdigest(),bytes=f.stat().st_size))
result=dict(pdfium_version=str(pypdfium2.PDFIUM_INFO),pdfium_source_snapshot=PDFIUM,pdfium_source_basis='Official immutable153.0.7999.0 release notes saychromium/7999; officialGitilesbranch resolvedto snapshot. Installedmetadata has no sourcehash.',pdfium_release='https://github.com/bblanchon/pdfium-binaries/releases/tag/chromium%2F7999',mupdf_version=pymupdf.version[1],mupdf_tag='1.26.11',mupdf_source_commit=MUPDF,pdfjs_version='6.5.438',pdfjs_source_commit=PDFJS,sources=rows,runtime_binaries=files,limitations=['Sourcesmatchreportedruntimeversions; no completebinaryrebuild/sourceattestation or in-processbranchtracingwasperformed.','Modelsareconsistentwithall24measuredinteriors; theydo notestablisha normativeISO8bitroundingrule.','DirectCanvascontrols isolate the Nodebackend withoutPDF.js parsing; browserCanvas andotherbackends remainuntested.'],oracle_status='Notestablished; fractionalPDFgoldens remainabsent')
(R/'source-evidence.json').write_text(json.dumps(result,indent=2)+'\n');print('Pinned7rendererimplementationfiles; hashesonlypublished; no test/PDFassetdownload')
