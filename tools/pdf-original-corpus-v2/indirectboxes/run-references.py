#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import sys,os,json,subprocess,hashlib
from PIL import Image
R=Path(__file__).resolve().parent;pdfjs=Path(sys.argv[1] if len(sys.argv)>1 else os.environ['PDFJS_ROOT']).resolve();m=json.loads((R/'manifest.json').read_text());rows=[];calls=[]
(R/'references').mkdir(exist_ok=True);(R/'logs').mkdir(exist_ok=True)
for c in m['cases']:
 for dpi in c['dpis']:
  for engine in ['pdfium','mupdf','pdfjs']:
   out=R/f"references/{c['id']}-{dpi}-{engine}.png"
   cmd=['node',str(R/'render-pdfjs.mjs'),str(pdfjs),str(R/c['file']),str(out),str(dpi)] if engine=='pdfjs' else [sys.executable,str(R/'render-native.py'),engine,str(R/c['file']),str(out),str(dpi)]
   p=subprocess.run(cmd,capture_output=True,text=True);(R/f"logs/{c['id']}-{dpi}-{engine}.log").write_text(p.stdout+p.stderr);call=dict(id=c['id'],dpi=dpi,engine=engine,argv=cmd,exit_code=p.returncode);calls.append(call)
   row=dict(id=c['id'],fixture_id=c['fixture_id'],page=0,dpi=dpi,engine=engine,file=str(out.relative_to(R)),input_sha256=c['sha256'],exit_code=p.returncode,checks=[])
   if p.returncode==0 and out.exists():
    meta=json.loads(p.stdout.strip().splitlines()[-1]);row['renderer_metadata']=meta;row['sha256']=hashlib.sha256(out.read_bytes()).hexdigest();im=Image.open(out).convert('RGB');row['dimensions']=list(im.size);row['dimensions_match']=im.size==(c['width']*dpi//72,c['height']*dpi//72)
    if row['dimensions_match']:
     for sample in c['expected_samples']:
      x,y=sample['point'];actual=list(im.getpixel((int(x*dpi/72),int((c['height']-y)*dpi/72))));row['checks'].append(dict(id=sample['id'],expected=sample['rgb'],actual=actual,passed=actual==sample['rgb']))
    row['status']='passed' if row['dimensions_match'] and len(row['checks'])==8 and all(v['passed'] for v in row['checks']) else 'failed'
   else:row.update(status='failed',reason='renderer subprocess failed or no PNG')
   rows.append(row)
result=dict(unique_pdfs=3,page_views=3,reference_runs=len(rows),passed=sum(v['status']=='passed' for v in rows),failed=sum(v['status']!='passed' for v in rows),skipped=0,sample_checks=sum(len(v['checks']) for v in rows),sample_passes=sum(v['passed'] for r in rows for v in r['checks']),rows=rows,upstream_inputs_executed=0,upstream_credited=0)
(R/'reference-results.json').write_text(json.dumps(result,indent=2)+'\n');(R/'invocations.json').write_text(json.dumps(dict(renderer_subprocess_invocations=len(calls),by_engine={e:sum(v['engine']==e for v in calls) for e in ['pdfium','mupdf','pdfjs']},other_render_invocations=0,product_invocations=0,calls=calls),indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='rows'}))
