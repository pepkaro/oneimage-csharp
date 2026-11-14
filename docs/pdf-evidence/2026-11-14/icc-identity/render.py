# SPDX-License-Identifier: MIT
from pathlib import Path
import subprocess,json,hashlib,os
from PIL import Image
import numpy as np
import fitz,pypdfium2 as pdfium
ROOT=Path(__file__).resolve().parent
log=[]
for label in ('wide-original','wide-renamed'):
 pdf=ROOT/'fixtures'/f'{label}.pdf'
 for arm in ('baseline','candidate'):
  out=ROOT/'renders'/f'{label}-{arm}.png'
  cmd=[os.environ['DOTNET_ROOT']+'/dotnet',str(ROOT.parent/'engines'/arm/'IccEvidence.dll'),'render',str(pdf),str(out)]
  p=subprocess.run(cmd,text=True,capture_output=True,timeout=30);log.append({'command':cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr})
  assert p.returncode==0,p.stderr
 for engine in ('pdfium','mupdf'):
  out=ROOT/'renders'/f'{label}-{engine}.png'
  if engine=='pdfium':
   doc=pdfium.PdfDocument(str(pdf));page=doc[0];bitmap=page.render(scale=96/72);bitmap.to_pil().save(out);bitmap.close();page.close();doc.close()
  else:
   doc=fitz.open(pdf);pix=doc[0].get_pixmap(matrix=fitz.Matrix(96/72,96/72),alpha=False);pix.save(out);doc.close()
def compare(a,b):
 a=np.asarray(Image.open(ROOT/'renders'/a).convert('RGB'),dtype=np.int16);b=np.asarray(Image.open(ROOT/'renders'/b).convert('RGB'),dtype=np.int16);d=abs(a-b)
 return {'max_channel_difference':int(d.max()),'mean_absolute_channel_difference':float(d.mean()),'different_pixels':int(np.any(d,axis=2).sum())}
metrics={engine:compare(f'wide-original-{engine}.png',f'wide-renamed-{engine}.png') for engine in ('baseline','candidate','pdfium','mupdf')}
metrics['original_baseline_vs_candidate']=compare('wide-original-baseline.png','wide-original-candidate.png')
metrics['renamed_baseline_vs_candidate']=compare('wide-renamed-baseline.png','wide-renamed-candidate.png')
manifest={'render_options':{'dpi':96,'page_index':0,'full_page':True,'cropped':False,'retouched':False,'png_dimensions':{p.name:list(Image.open(p).size) for p in sorted((ROOT/'renders').glob('*.png'))},'OneImage_DOTNET_PROCESSOR_COUNT':os.environ.get('DOTNET_PROCESSOR_COUNT')},'versions':{'pymupdf_wrapper':fitz.VersionBind,'mupdf_engine':fitz.VersionFitz,'pypdfium2_wrapper':str(pdfium.PYPDFIUM_INFO),'pdfium_engine':str(pdfium.PDFIUM_INFO)},'commands':log,'metrics':metrics,'png_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'renders').glob('*.png'))},'binary_sha256':{arm:{name:hashlib.sha256((ROOT.parent/'engines'/arm/name).read_bytes()).hexdigest() for name in ('OneImage.dll','OneImage.Pdf.dll','OnePdf.dll')} for arm in ('baseline','candidate')}}
(ROOT/'render-manifest.json').write_text(json.dumps(manifest,indent=2));print(json.dumps(metrics,indent=2))
