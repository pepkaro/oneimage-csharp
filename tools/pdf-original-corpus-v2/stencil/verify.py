# SPDX-License-Identifier: MIT
from pathlib import Path
import json,hashlib
from pypdf import PdfReader
from pypdf.generic import ContentStream
R=Path(__file__).resolve().parent;m=json.loads((R/'manifest.json').read_text());rows=[]
for c in m['cases']:
 p=R/c['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'];doc=PdfReader(p,strict=True);assert len(doc.pages)==1;page=doc.pages[0];assert list(page.mediabox)==[0,0,c['width'],110]
 xobjs=page['/Resources']['/XObject'];assert len(xobjs)==1;ref=xobjs.raw_get('/Im');assert ref.idnum==5;im=ref.get_object();assert im['/ImageMask'].value is True and im['/BitsPerComponent']==1 and '/ColorSpace' not in im and '/SMask' not in im and im['/Interpolate'].value is False and im['/Width']==9 and im['/Height']==3
 raw=im.get_data();assert len(raw)==6 and hashlib.sha256(raw).hexdigest()==c['image']['raw_sha256'];assert all((raw[y*2+1]&127)==0 for y in range(3));bits=[[(raw[y*2+x//8]>>(7-x%8))&1 for x in range(9)] for y in range(3)];assert bits==c['bits'];decode=list(im['/Decode']) if '/Decode' in im else None;assert decode==c['image']['decode'];marked=[]
 for k,placement in enumerate(c['placements']):
  for y,line in enumerate(bits):
   for x,bit in enumerate(line):
    mark=bit==(1 if decode==[1,0] else 0);label=f'placement-{k}-cell-{x}-{y}';bg=[255,255,255] if (x+y)%2==0 else [0,0,0];expected=placement['paint_rgb'] if mark else bg;assert next(s for s in c['expected_samples'] if s['id']==label)['rgb']==expected
    if mark:marked.append(label)
 assert marked==c['marked_cell_ids'];rgb=[0,0,0];ctm=[1,0,0,1,0,0];stack=[];draws=[]
 for args,op in ContentStream(page['/Contents'].get_object(),doc).operations:
  if op==b'q':stack.append((rgb[:],ctm[:]))
  elif op==b'Q':rgb,ctm=stack.pop()
  elif op==b'rg':rgb=[round(float(v)*255) for v in args]
  elif op==b'cm':assert ctm==[1,0,0,1,0,0];ctm=[float(v) for v in args]
  elif op==b'Do':assert str(args[0])=='/Im';draws.append(dict(paint_rgb=rgb[:],ctm=ctm[:],resource=str(args[0])))
 assert not stack and len(draws)==len(c['placements'])
 for a,b in zip(draws,c['placements']):assert a['paint_rgb']==b['paint_rgb'] and a['ctm']==b['ctm']
 rows.append(dict(id=c['id'],raw_bytes=len(raw),row_bytes=2,ignored_padding_bits=7,draw_count=len(draws),draws=draws,marks=len(marked),passed=True))
(R/'structure-results.json').write_text(json.dumps(dict(passed=3,failed=0,rows=rows),indent=2)+'\n');print('3 valid stencil cases; packed bits, Decode polarity and shared-image current colours independently verified')
