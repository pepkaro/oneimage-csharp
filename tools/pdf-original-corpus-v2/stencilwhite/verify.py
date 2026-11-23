# SPDX-License-Identifier: MIT
from pathlib import Path
import json,hashlib
from PIL import Image
from pypdf import PdfReader
from pypdf.generic import ContentStream
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text());r=json.loads((R/'reference-results.json').read_text());g=json.loads((R/'region-agreement.json').read_text())
assert len(m['cases'])==3 and len({c['sha256'] for c in m['cases']})==3
assert len(r['rows'])==18 and (r['passed'],r['failed'],r['skipped'])==(18,0,0)
assert g['accepted_fixtures']==3 and g['held_fixtures']==0
raw_expected=bytes.fromhex('65003a809700')
expected_bits=[[0,1,1,0,0,1,0,1,0],[0,0,1,1,1,0,1,0,1],[1,0,0,1,0,1,1,1,0]]
bit_checks=0
for c in m['cases']:
 f=R/c['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==c['sha256']==c['sha']
 assert c['id']==c['fixture_id'] and c['id'].startswith('stencil-white-')
 assert (c['page'],c['page_count'],c['width'],c['height'],c['dpis'])==(0,1,240,180,[72,144])
 d=PdfReader(f,strict=True);assert len(d.pages)==1;page=d.pages[0];resources=page['/Resources']
 assert set(resources)=={'/XObject'} and set(resources['/XObject'])=={'/M'}
 ref=resources['/XObject'].raw_get('/M');assert ref.idnum==5
 im=ref.get_object();assert im['/ImageMask'].value is True
 assert (im['/Width'],im['/Height'],im['/BitsPerComponent'])==(9,3,1)
 assert im['/Interpolate'].value is False and im.get_data()==raw_expected
 assert all(k not in im for k in ['/ColorSpace','/Mask','/SMask','/Matte','/SMaskInData','/Filter'])
 assert page.get('/Group') is None and page.get('/Annots') is None
 inverse=c['id']=='stencil-white-inverse-red'
 assert (list(im['/Decode']) if '/Decode' in im else None)==([1,0] if inverse else None)
 assert all(raw_expected[2*row+1]&127==0 for row in range(3))
 # Independently interpret q/Q, current nonstroking color, backdrop fills and image placement.
 color=[0,0,0];ctm=[1,0,0,1,0,0];stack=[];draws=[];fills=[];pending=None
 for args,op in ContentStream(page.get_contents(),d).operations:
  if op==b'q':stack.append((list(color),list(ctm)))
  elif op==b'Q':color,ctm=stack.pop()
  elif op==b'rg':
   assert all(float(x) in [0,1] for x in args);color=[int(float(x)*255) for x in args]
  elif op==b're':pending=list(map(int,args))
  elif op==b'f':
   assert color==[255]*3 and ctm==[1,0,0,1,0,0] and pending is not None
   fills.append(pending);pending=None
  elif op==b'cm':assert ctm==[1,0,0,1,0,0];ctm=list(map(int,args))
  elif op==b'Do':
   assert args[0]=='/M' and len(stack)==1 and ctm[:4]==[144,0,0,48]
   assert color in [[255,0,0],[0,255,0]];draws.append(dict(x=ctm[4],y=ctm[5],tint=list(color),object=ref.idnum))
  else:raise AssertionError(op)
 assert not stack and color==[0,0,0] and ctm==[1,0,0,1,0,0]
 expected_draws=([(32,104,[255,0,0]),(32,24,[0,255,0])] if c['id']=='stencil-white-reuse-red-green' else [(32,80,[255,0,0])])
 assert [(v['x'],v['y'],v['tint']) for v in draws]==expected_draws
 assert fills==[[x-8,y-8,160,64] for x,y,tint in expected_draws]
 assert len({v['object'] for v in draws})==1 # same image object, tint changes per draw
 regions={v['id']:v for v in c['expected_regions']};samples={v['id']:v for v in c['expected_samples']}
 for n,(x,y,tint) in enumerate(expected_draws):
  for row in range(3):
   for col in range(9):
    bit=(raw_expected[row*2+col//8]>>(7-col%8))&1;assert bit==expected_bits[row][col];bit_checks+=1
    unmarked=bit==(0 if inverse else 1);expected=[255]*3 if unmarked else tint
    ident=f'draw-{n}-cell-{col}-{row}';s=samples[ident];reg=regions[ident]
    assert s['rgb']==reg['rgb']==expected and s['source_bit']==bit and s['painted']==(not unmarked)
    assert reg['rect']==[x+col*16+2,y+(2-row)*16+2,12,12] and s['point']==[x+col*16+8,y+(2-row)*16+8]
    assert s['tolerance']==reg['tolerance']==0
  for side,rect in [('left',[x-6,y-6,4,60]),('right',[x+146,y-6,4,60]),('bottom',[x+2,y-6,140,4]),('top',[x+2,y+50,140,4])]:
   ident=f'draw-{n}-white-frame-{side}';assert regions[ident]['rect']==rect and regions[ident]['rgb']==[255]*3
 assert regions['paper']['rect']==[4,4,16,16] and samples['paper']['point']==[12,12] and samples['paper']['rgb']==[255]*3
 assert c['association']['upstream_id'] is None and not c['association']['upstream_entry_validated']
assert bit_checks==108
for row in r['rows']:
 f=R/row['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
 c=next(c for c in m['cases'] if c['id']==row['id']);assert row['source_sha256']==c['sha256'];im=Image.open(f).convert('RGB')
 assert im.size==(c['width']*row['dpi']//72,c['height']*row['dpi']//72)
 for s,record in zip(c['expected_samples'],row['checks'],strict=True):
  actual=list(im.getpixel((int(s['point'][0]*row['dpi']/72),int((c['height']-s['point'][1])*row['dpi']/72))))
  assert actual==s['rgb']==record['actual'] and record['passed']
for f in (R/'logs').glob('*pdfjs.log'):
 v=json.loads(f.read_text().splitlines()[-1]);assert (v['pdfjs'],v['build'],v['canvasVersion'],v['node'])==('6.5.438','0a4153349','1.1.1','v24.22.3');assert not v['diagnostics']
assert len(list((R/'logs').glob('*pdfjs.log')))==6
events=[json.loads(line) for line in (R/'reference-invocations.jsonl').read_text().splitlines()]
starts=[v for v in events if v['event']=='capture_start'];finishes=[v for v in events if v['event']=='capture_finish'];runs=[v for v in events if v['event']=='run_start'];ends=[v for v in events if v['event']=='run_finish']
assert len(runs)>=1 and len(runs)==len(ends) and len(starts)==len(finishes)==18*len(runs)
assert all(v['returncode']==0 for v in finishes) and all(v['reference_runs']==v['passed']==18 and v['failed']==0 for v in ends)
keys=lambda v:(v['run_id'],v['fixture_id'],v['engine'],v['dpi'])
assert {keys(v) for v in starts}=={keys(v) for v in finishes}
assert all(v['source_sha256']==next(c['sha256'] for c in m['cases'] if c['id']==v['fixture_id']) for v in starts)
print('3 WHITE-backed stencils /6DPI views /18 refs:18 pass,0 fail/skip;108 independent draw/cell bit checks; checkerboard holds stay separate.')
