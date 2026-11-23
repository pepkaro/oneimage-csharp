# SPDX-License-Identifier: MIT
from pathlib import Path
import argparse,json,hashlib
import numpy as np
from PIL import Image
from model import pdfium_rgb,mupdf_rgb
R=Path(__file__).resolve().parent
p=argparse.ArgumentParser();p.add_argument('--repo',type=Path,required=True);args=p.parse_args();repo=args.repo.resolve();routes=json.loads((repo/'tools/pdf-original-corpus-v2/routes.json').read_text());result=json.loads((R/'classification-results.json').read_text());controls=json.loads((R/'controls/results.json').read_text())['records'];assert len(result['rows'])==24 and len(controls)==8
pixels=0
for row in result['rows']:
 route=next(r for r in routes if r['id']==row['id']);assert not route['accepted'] and route['family']=='alpha';c=route['manifest'];a=np.asarray(Image.open(repo/route['canonical_dir']/f'references/{row["engine"]}-{row["dpi"]}.png').convert('RGB'));scale=row['dpi']/72;yy,xx=np.mgrid[:a.shape[0],:a.shape[1]];xp=(xx+.5)/scale;yp=c['height']-(yy+.5)/scale;x,y,w,h=c['expected_regions'][0]['rect'];mask=(xp>=x)&(xp<x+w)&(yp>=y)&(yp<y+h)
 predicted=pdfium_rgb(row['alpha'],row['source']) if row['engine']=='pdfium' else mupdf_rgb(row['alpha'],row['source']) if row['engine']=='mupdf' else next(v['actual'][:3] for v in controls if v['alpha']==row['alpha'] and v['kind']==('stroke' if 'stroke' in row['id'] else 'fill') and v['dpi']==row['dpi'])
 assert (a[mask]==predicted).all();row.update(scored_interior_pixels=int(mask.sum()),different_interior_pixels=0);pixels+=int(mask.sum())
 for dpi in [72,144]:assert not (repo/route['canonical_dir']/f'expected-{dpi}.png').exists()
for row in controls:
 s=row['dpi']/72;a=Image.open(R/'controls'/row['file']).convert('RGBA');assert list(a.getpixel((int(40*s),int(30*s))))==row['actual']
assert pdfium_rgb(.6,(255,0,0))!=mupdf_rgb(.6,(255,0,0));assert next(v['actual'][:3] for v in controls if v['alpha']==.25 and v['kind']=='fill')!=pdfium_rgb(.25,(255,0,0))
result.update(interior_pixel_checks=pixels,interior_pixel_mismatches=0,source_backed_explanation='Different8bitalphaweightsandintegerblendroutespredictallmeasureduniforminteriors; directCanvasreproducesPDF.jsbackendvalues',oracle_status='Unresolved normativepixeloracle; allfourcasesstillheld');(R/'classification-results.json').write_text(json.dumps(result,indent=2)+'\n');print('24source-backedpredictions and',pixels,'interiorpixels match;8directCanvascontrols match;4originals stayheld')
