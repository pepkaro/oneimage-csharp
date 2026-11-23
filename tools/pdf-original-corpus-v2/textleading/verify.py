# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json,math
from PIL import Image
from pypdf import PdfReader
from pypdf.generic import ContentStream,ArrayObject
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text());r=json.loads((R/'reference-results.json').read_text());g=json.loads((R/'region-agreement.json').read_text());design=json.loads((R/'original-font.json').read_text())
assert len(m['cases'])==4 and len({x['sha256'] for x in m['cases']})==4
assert len(r['rows'])==24 and (r['passed'],r['failed'],r['skipped'])==(24,0,0)
assert g['accepted_fixtures']==4 and g['held_fixtures']==0

def layout(page,reader,font):
 tm=lm=[1.,0.,0.,1.,0.,0.];fs=0.;tc=tw=0.;h=1.;rise=0.;leading=0.;glyphs=[]
 widths=list(map(float,font['/Widths']));first=int(font['/FirstChar'])
 def show(text):
  nonlocal tm
  for code in text.original_bytes:
   if code!=32:
    a,b,c,d,e,f=tm;glyphs.append(dict(glyph=chr(code),text_matrix=list(tm),glyph_matrix=[a*h,b*h,c,d,e+c*rise,f+d*rise],horizontal_scale=h,text_rise=rise,leading=leading))
   advance=(widths[code-first]*fs/1000+tc+(tw if code==32 else 0))*h
   a,b,c,d,e,f=tm;tm=[a,b,c,d,e+a*advance,f+b*advance]
 for args,op in ContentStream(page.get_contents(),reader).operations:
  if op==b'BT':tm=[1.,0.,0.,1.,0.,0.];lm=list(tm)
  elif op==b'Tf':assert args[0]=='/F0';fs=float(args[1])
  elif op==b'Tc':tc=float(args[0])
  elif op==b'Tw':tw=float(args[0])
  elif op==b'Tz':h=float(args[0])/100
  elif op==b'Ts':rise=float(args[0])
  elif op==b'TL':leading=float(args[0])
  elif op==b'Tm':tm=list(map(float,args));lm=list(tm)
  elif op in [b'Td',b'TD',b'T*']:
   x,y=(0.,-leading) if op==b'T*' else map(float,args)
   if op==b'TD':leading=-y
   a,b,c,d,e,f=lm;lm=[a,b,c,d,e+a*x+c*y,f+b*x+d*y];tm=list(lm)
  elif op==b'Tj':show(args[0])
  elif op==b'TJ':
   assert isinstance(args[0],ArrayObject)
   for item in args[0]:
    if hasattr(item,'original_bytes'):show(item)
    else:
     move=-float(item)*fs/1000*h;a,b,c,d,e,f=tm;tm=[a,b,c,d,e+a*move,f+b*move]
  else:assert op in [b'ET',b'g'],op
 return glyphs
for c in m['cases']:
 f=R/c['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==c['sha256']
 doc=PdfReader(f,strict=True);assert len(doc.pages)==1
 page=doc.pages[0];resources=page['/Resources'];assert set(resources)=={'/Font'}
 assert page.get('/Annots') is None
 font=resources['/Font']['/F0'].get_object()
 assert font['/Subtype']=='/Type3' and list(font['/FontBBox'])==[0,0,600,700]
 assert list(map(float,font['/FontMatrix']))==[.001,0,0,.001,0,0]
 assert set(font['/Resources'])==set() and font['/FirstChar']==32 and font['/LastChar']==66
 assert list(font['/Encoding']['/Differences'])==[32,'/space',65,'/gA','/gB']
 for key in ['A','B','space']:
  name={'A':'/gA','B':'/gB','space':'/space'}[key];body=font['/CharProcs'][name].get_object().get_data()
  assert hashlib.sha256(body).hexdigest()==c['font']['glyph_stream_sha256'][key]
  if key!='space':
   expected=design['glyphs'][key]
   ops=ContentStream(font['/CharProcs'][name].get_object(),doc).operations
   assert ops[0][1]==b'd1' and list(ops[0][0])==[expected['width'],0,*expected['bbox']]
   assert [(list(a),o) for a,o in ops[1:]]==[(a,o) for rect in expected['ink'] for a,o in [(rect,b're'),([],b'f')]]
   assert font['/Widths'][expected['code']-32]==expected['width']
 assert font['/Widths'][0]==250
 got=layout(page,doc,font);assert len(got)==len(c['expected_glyphs'])
 for a,b in zip(got,c['expected_glyphs'],strict=True):
  assert a['glyph']==b['glyph'] and a['horizontal_scale']==b['horizontal_scale'] and a['text_rise']==b['text_rise'] and a['leading']==b['leading']
  for key in ['text_matrix','glyph_matrix']:assert all(math.isclose(x,y,abs_tol=1e-9) for x,y in zip(a[key],b[key],strict=True))
 assert c['association']['upstream_id'] is None and not c['association']['upstream_entry_validated']
for row in r['rows']:
 f=R/row['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
 c=next(c for c in m['cases'] if c['id']==row['id']);im=Image.open(f).convert('RGB')
 assert im.size==(c['width']*row['dpi']//72,c['height']*row['dpi']//72)
 for s,record in zip(c['expected_samples'],row['checks'],strict=True):
  got=list(im.getpixel((int(s['point'][0]*row['dpi']/72),int((c['height']-s['point'][1])*row['dpi']/72))))
  assert got==s['rgb']==record['actual'] and record['passed']
for f in (R/'logs').glob('*pdfjs.log'):
 d=json.loads(f.read_text().splitlines()[-1]);assert (d['pdfjs'],d['build'],d['canvasVersion'],d['node'])==('6.5.438','0a4153349','1.1.1','v24.22.3')
 assert not d['diagnostics'],d['diagnostics']
assert len(list((R/'logs').glob('*pdfjs.log')))==8
print('4 leading PDFs; 24/24 references; all analytic centers, independent glyph matrices and per-glyph leading states passed; 0 upstream-entry passes.')
