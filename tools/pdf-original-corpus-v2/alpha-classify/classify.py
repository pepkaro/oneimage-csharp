# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,json,hashlib,sys,subprocess
from PIL import Image
from pypdf import PdfReader
from model import alpha_byte,pdfium_rgb,mupdf_rgb
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);p.add_argument('--pdfjs',type=Path,required=True);p.add_argument('--output',type=Path,required=True);args=p.parse_args();repo=args.repo.resolve();out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
T=repo/'tools/pdf-original-corpus-v2';routes=json.loads((T/'routes.json').read_text());controls=json.loads((R/'controls/results.json').read_text())['records'];rows=[]
for c in [c for c in routes if c['family']=='alpha' and not c['accepted']]:
 src=repo/c['canonical_dir']/'original.pdf';assert hashlib.sha256(src.read_bytes()).hexdigest()==c['manifest']['sha256'];doc=PdfReader(src,strict=True);states=doc.pages[0]['/Resources']['/ExtGState'];kind='stroke' if 'stroke' in c['id'] else 'fill';key='/CA' if kind=='stroke' else '/ca';alpha=float(next(v[key] for v in states.values() if key in v));source=(0,0,255) if kind=='stroke' else (255,0,0);first=c['manifest']['expected_samples'][0]
 for dpi in c['manifest']['dpis']:
  for engine in ['pdfium','mupdf','pdfjs']:
   target=out/f'{c["id"]}-{dpi}-{engine}.png'
   if engine=='pdfjs':cmd=['node',str(repo/'tools/pdf-original-corpus-v2/alpha/render-pdfjs.mjs'),str(args.pdfjs.resolve()),str(src),str(target),str(dpi),'none']
   else:cmd=[sys.executable,str(T/'alpha/render-native.py'),engine,str(src),str(target),str(dpi)]
   subprocess.run(cmd,check=True,capture_output=True,text=True);im=Image.open(target).convert('RGB');point=(int(first['point'][0]*dpi/72),int((c['manifest']['height']-first['point'][1])*dpi/72));got=list(im.getpixel(point))
   model=pdfium_rgb(alpha,source) if engine=='pdfium' else mupdf_rgb(alpha,source) if engine=='mupdf' else next(v['actual'][:3] for v in controls if v['alpha']==alpha and v['kind']==kind and v['dpi']==dpi)
   assert got==model,(c['id'],engine,got,model)
   recorded=repo/c['canonical_dir']/f'references/{engine}-{dpi}.png';assert hashlib.sha256(target.read_bytes()).hexdigest()==hashlib.sha256(recorded.read_bytes()).hexdigest()
   rows.append(dict(id=c['id'],engine=engine,dpi=dpi,alpha=alpha,modeled_alpha_byte=alpha_byte(alpha),source=list(source),observed=got,predicted=model,prediction_matches=True,capture_bytes_match_prior=True,pdf_sha256=c['manifest']['sha256']))
result=dict(slice='ISO-ALPHA-QUANTIZATION-CLASSIFY-01',existing_original_pdfs=4,new_original_pdfs=0,new_goldens=0,fresh_pdf_reference_calls=24,predictions_matched=24,predictions_failed=0,pdf_reference_capture_bytes_unchanged=24,direct_canvas_controls=8,normative_oracle_established=False,held_cases_remain_held=True,upstream_credited=0,product_runs=0,scope='Opaque uniform RGB interiors on white; no edge/group/color-management/other-alpha conclusions',rows=rows)
(R/'classification-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
