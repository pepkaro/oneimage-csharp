#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Offline validation, deterministic regeneration, pinned reference capture and product grading."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile,shutil,os,importlib.util
import numpy as np
from PIL import Image
T=Path(__file__).resolve().parent;REPO=T.parents[1]
sys.path.insert(0,str(T/'geometry'))
from score import expected
spec=importlib.util.spec_from_file_location('stroke_score',T/'stroke/score.py');stroke=importlib.util.module_from_spec(spec);spec.loader.exec_module(stroke)
jspec=importlib.util.spec_from_file_location('join_score',T/'joins/score.py');joins=importlib.util.module_from_spec(jspec);jspec.loader.exec_module(joins)
dspec=importlib.util.spec_from_file_location('dash_score',T/'dash/score.py');dash=importlib.util.module_from_spec(dspec);dspec.loader.exec_module(dash)
read=lambda p:json.loads(p.read_text())
write=lambda p,d:p.write_text(json.dumps(d,indent=2)+'\n')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def rgb(p):return np.asarray(Image.open(p).convert('RGB'))
def mask_for(r,dpi):
 c=r['manifest']
 if r['family']=='geometry':return expected(c,dpi)
 if r['family']=='stroke':return stroke.expected(c,dpi)
 if r['family']=='joins':return joins.expected(c,dpi)
 if r['family']=='dash':return dash.expected(c,dpi)
 scale=dpi/72;w=c['width']*dpi//72;h=c['height']*dpi//72;a=np.full((h,w,3),255,np.uint8);mask=np.zeros((h,w),bool);yy,xx=np.mgrid[:h,:w];xp=(xx+.5)/scale;yp=c['height']-(yy+.5)/scale
 for reg in c['expected_regions']:
  x,y,rw,rh=reg['rect'];m=(xp>=x)&(xp<x+rw)&(yp>=y)&(yp<y+rh);a[m]=reg['rgb'];mask|=m
 return a,mask
def compare(a,b,m):
 if a.shape!=b.shape:return dict(passed=False,shape=list(a.shape),expected_shape=list(b.shape),reason='dimensions')
 d=np.abs(a.astype(int)-b.astype(int)).max(axis=2)[m]
 return dict(passed=bool((d==0).all()),scored_pixels=int(m.sum()),different_pixels=int((d!=0).sum()),max_delta=int(d.max()))
def verify():
 routes=read(T/'routes.json');ledger=read(T/'cases.json');assert len(routes)==len(ledger['cases'])
 assert len(read(T/'inventory.json')['rows'])==2811;assert len({r['manifest']['sha256'] for r in routes})==len(routes)
 rows=[]
 for r in routes:
  folder=REPO/r['canonical_dir'];assert sha(folder/'original.pdf')==r['manifest']['sha256']
  for dpi in r['manifest']['dpis']:
   analytic,mask=mask_for(r,dpi);arrays={e:rgb(folder/f'references/{e}-{dpi}.png') for e in ['pdfium','pdfjs','mupdf']}
   checks={e:compare(a,analytic,mask) for e,a in arrays.items()};pairs={a+'-'+b:compare(arrays[a],arrays[b],mask) for a,b in [('pdfium','pdfjs'),('pdfium','mupdf'),('pdfjs','mupdf')]}
   agreed=all(c['passed'] for c in checks.values()) and all(c['passed'] for c in pairs.values());assert agreed==r['accepted'],r['id']
   target=folder/f'expected-{dpi}.png'
   if agreed:
    assert target.exists();assert any(sha(target)==sha(folder/f'references/{e}-{dpi}.png') for e in arrays);assert compare(rgb(target),analytic,mask)['passed']
   else:assert not target.exists()
   rows.append(dict(id=r['id'],dpi=dpi,accepted=agreed,analytic=checks,pairwise=pairs))
 result=dict(originals=len(routes),agreed=sum(r['accepted'] for r in routes),held=sum(not r['accepted'] for r in routes),reference_runs=len(rows)*3,passed=sum(c['passed'] for r in rows for c in r['analytic'].values()),failed=sum(not c['passed'] for r in rows for c in r['analytic'].values()),skipped=0,upstream_executed=0,upstream_credited=0,rows=rows)
 write(T/'reference-verification.json',result);return result

def generate():
 for family in sorted({r['family'] for r in read(T/'routes.json')}):
  with tempfile.TemporaryDirectory() as tmp:
   dest=Path(tmp);shutil.copy(T/family/'generate.py',dest/'generate.py');subprocess.run([sys.executable,str(dest/'generate.py')],check=True)
   produced=read(dest/'manifest.json')
   for r in [r for r in read(T/'routes.json') if r['family']==family]:
    c=next(c for c in produced['cases'] if c['id']==r['id']);assert sha(dest/c['file'])==sha(REPO/r['canonical_dir']/'original.pdf')
 return {'regenerated_pdf_hash_matches':len(read(T/'routes.json'))}

def references(out,pdfjs):
 # Rebuild the adapters' staging layout in the caller-selected output, never overwrite accepted assets.
 out=out.resolve();assert not out.exists(),'Choose a new output directory';out.mkdir(parents=True)
 for family in sorted({r['family'] for r in read(T/'routes.json')}):
  d=out/family;shutil.copytree(T/family,d);(d/'inputs').mkdir(exist_ok=True)
  for r in [r for r in read(T/'routes.json') if r['family']==family]:shutil.copy(REPO/r['canonical_dir']/'original.pdf',d/r['manifest']['file'])
  env=dict(os.environ,PDFJS_ROOT=str(pdfjs.resolve()))
  commands=[['references.py'],['score.py'],['verify.py']] if family in ['geometry','stroke','joins','dash'] else [['run-references.py',str(pdfjs.resolve())],['verify.py'],['verify-regions.py']]
  for cmd in commands:subprocess.run([sys.executable,str(d/cmd[0]),*cmd[1:]],check=True,env=env)
 return {'captures':sum(len(r['manifest']['dpis'])*3 for r in read(T/'routes.json')),'output':str(out),'promotion':'manual review required; disagreement never auto-promotes'}

def grade(args):
 verify();commit=args.acceptance_commit
 # The accepted PDF+expected image must already be committed, before executing the product.
 for r in read(T/'routes.json'):
  if r['accepted']:
   for name in ['original.pdf',*[f'expected-{d}.png' for d in r['manifest']['dpis']]]:
    path=str(Path(r['canonical_dir'])/name);saved=subprocess.check_output(['git','show',commit+':'+path],cwd=REPO);assert hashlib.sha256(saved).hexdigest()==sha(REPO/path),path
 out=args.output.resolve();out.mkdir(parents=True,exist_ok=True);rows=[]
 for r in read(T/'routes.json'):
  if not r['accepted']:continue
  for dpi in r['manifest']['dpis']:
   folder=REPO/r['canonical_dir'];target=out/f"{r['id']}-{dpi}.png";cmd=[args.dotnet,str(args.renderer_dll.resolve()),'render',str(folder/'original.pdf'),str(target),str(dpi),'0'];p=subprocess.run(cmd,text=True,capture_output=True)
   row=dict(id=r['id'],dpi=dpi,command=cmd,exit_code=p.returncode,stderr=p.stderr,expected_sha256=sha(folder/f'expected-{dpi}.png'))
   if p.returncode==0 and target.exists():
    _,mask=mask_for(r,dpi);row.update(compare(rgb(target),rgb(folder/f'expected-{dpi}.png'),mask));row['output_sha256']=sha(target)
    a=rgb(target);c=r['manifest'];height=c.get('display_height_points',c.get('height'));samples=c.get('samples',c.get('expected_samples',[]));row['assertions']=[]
    for sample in samples:
     x,y=sample.get('point',[sample.get('x'),sample.get('y')]);got=a[int((height-y)*dpi/72),int(x*dpi/72)].tolist();row['assertions'].append(dict(id=sample['id'],expected=sample['rgb'],actual=got,passed=got==sample['rgb']))
    row['passed']=row['passed'] and all(v['passed'] for v in row['assertions'])
   else:row.update(passed=False,reason='renderer execution failed')
   rows.append(row)
 result=dict(acceptance_commit=commit,oneimage_source_head=args.source_head,onepdf_declared_package='RecursiveAI.OnePdf/Fonts1.18.0',executed=len(rows),passed=sum(r['passed'] for r in rows),failed=sum(not r['passed'] for r in rows),skipped=2,skip_reason='Held RGB8 Decode reference disagreement: both DPIs ungraded',rows=rows)
 write(out/'results.json',result);return result

def catalog():
 cases=read(T/'cases.json')['cases'];inv=read(T/'inventory.json')['rows'];lines=['# Original PDF behavior catalog','','ISO32000-2:2020 index. Heading verification and full-text limitations are in the clause records. PDF1.7 image contracts use separately verified2008 clauses. Exact raster quantization is an observed acceptance rule, not a normative ISO pixel requirement.','','One canonical fixture root; no duplicated fixture copies. Boundaries outside declared masks are unscored. Every upstream mapping is currently empty; no source input was executed.','']
 for clause in sorted({c['primary_iso_2020_directory'] for c in cases}):
  lines+=['## '+clause,'']
  for c in [c for c in cases if c['primary_iso_2020_directory']==clause]:
   rel='../../'+c['fixture'];lines+=['### '+c['use_case_id'],'',c['expected_behavior'],'',f"Stage: **{c['stage']}**; page0,72/144DPI, white, annotations off. [Original]({rel}); [clause evidence]({c['family']}/clause-index.json).",'','Expected: '+(', '.join(f'[{Path(p).name}](../../{p})' for p in c['expected_images']) or 'withheld: reference disagreement')+'.','', 'Executable: `python tools/pdf-original-corpus-v2/pipeline.py verify`'+'. Upstream pinned IDs: none; standard-contract-only.','']
 (T/'CATALOG.md').write_text('\n'.join(lines).rstrip()+'\n')
 lines=['# Subsystem view','','Cross-tags describe pipeline participation, not proven root-cause ownership. Cases and assets remain canonical in the ISO view.','']
 groups=['OnePDF/object-xref-streams','OnePDF/page-resources','OnePDF/font-text-interpretation','OnePDF/content-interpretation','OnePDF/image-color-decoding','OneImage/paths-clipping','OneImage/glyph-rasterization','OneImage/image-sampling','OneImage/color-conversion','OneImage/transparency-compositing','OneImage.Pdf/bridge-integration']
 for group in groups:
  lines+=['## '+group,'']
  selected=[c for c in cases if group in c['subsystems']];lines += [f"- [{c['use_case_id']}](CATALOG.md#{c['use_case_id']}) — {c['stage']}; owner unresolved." for c in selected] or ['No focused case in this batch.'];lines+=['']
 (T/'SUBSYSTEMS.md').write_text('\n'.join(lines).rstrip()+'\n')
 suites={s:{'inventory':sum(r['suite']==s for r in inv),'qualified':0,'mapped':0,'executed':0,'credited':0,'pending':sum(r['suite']==s for r in inv)} for s in sorted({r['suite'] for r in inv})};write(T/'suite-coverage.json',suites);return suites

def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['verify','generate','references','grade','catalog']);p.add_argument('--output',type=Path);p.add_argument('--pdfjs',type=Path);p.add_argument('--dotnet',default='dotnet');p.add_argument('--renderer-dll',type=Path);p.add_argument('--acceptance-commit');p.add_argument('--source-head');a=p.parse_args()
 if a.stage=='grade':assert all([a.output,a.renderer_dll,a.acceptance_commit,a.source_head]);result=grade(a)
 elif a.stage=='references':assert a.output and a.pdfjs;result=references(a.output,a.pdfjs)
 else:result=globals()[a.stage]()
 print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2));return 1 if a.stage=='grade' and result['failed'] else 0
if __name__=='__main__':sys.exit(main())
