# SPDX-License-Identifier: MIT
from pathlib import Path
import hashlib,json
from PIL import Image
from pypdf import PdfReader
from pypdf.generic import ContentStream
R=Path(__file__).resolve().parent
m=json.loads((R/'manifest.json').read_text());r=json.loads((R/'reference-results.json').read_text());g=json.loads((R/'region-agreement.json').read_text())
assert len(m['cases'])==3 and len({c['sha256'] for c in m['cases']})==3
assert len(r['rows'])==18 and (r['passed'],r['failed'],r['skipped'])==(18,0,0)
assert g['accepted_fixtures']==3 and g['held_fixtures']==0
expected_grid=[(255,0,0),(0,255,255),(255,0,255),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,0),(255,0,255)]
raw_expected=bytes(v for rgb in expected_grid for v in rgb)
assert len(raw_expected)==27 and set(raw_expected)=={0,255}
key_map={'img-colorkey-endpoint-control':None,'img-colorkey-endpoint-stored-red':[255,255,0,0,0,0],'img-colorkey-endpoint-stored-red-magenta-range':[255,255,0,0,0,255]}
masked_map={'img-colorkey-endpoint-control':set(),'img-colorkey-endpoint-stored-red':{'cell-0-0','cell-1-2'},'img-colorkey-endpoint-stored-red-magenta-range':{'cell-0-0','cell-2-0','cell-1-2','cell-2-2'}}
decoded_only_map={'img-colorkey-endpoint-control':set(),'img-colorkey-endpoint-stored-red':{'cell-1-0','cell-0-2'},'img-colorkey-endpoint-stored-red-magenta-range':{'cell-1-0','cell-0-1','cell-0-2'}}
structural_mask_checks=0
for c in m['cases']:
 f=R/c['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==c['sha256']==c['sha']
 assert c['fixture_id']==c['id'] and c['id'].startswith('img-colorkey-endpoint-')
 assert (c['width'],c['height'],c['page'],c['page_count'],c['dpis'])==(240,180,0,1,[72,144])
 doc=PdfReader(f,strict=True);assert len(doc.pages)==1;page=doc.pages[0]
 assert set(page['/Resources'])=={'/XObject'} and page.get('/Annots') is None and page.get('/Group') is None
 im=page['/Resources']['/XObject']['/Im'].get_object()
 assert (im['/Width'],im['/Height'],im['/BitsPerComponent'],im['/ColorSpace'])==(3,3,8,'/DeviceRGB')
 assert im['/Filter']=='/FlateDecode' and im['/Interpolate'].value is False
 assert list(im['/Decode'])==[1,0,1,0,1,0]
 assert all(k not in im for k in ['/SMask','/Matte','/SMaskInData','/ImageMask'])
 assert im.get_data()==raw_expected
 assert hashlib.sha256(raw_expected).hexdigest()==c['image']['raw_sha256']
 assert hashlib.sha256(im._data).hexdigest()==c['image']['encoded_sha256']
 key=key_map[c['id']];assert (list(im['/Mask']) if '/Mask' in im else None)==key==c['image']['mask']
 # Interpret ordinary page checker graphics independently of generator code.
 ops=ContentStream(page.get_contents(),doc).operations;assert len(ops)==112
 squares={}
 for n in range(36):
  (color,go),(rect,ro),(empty,fo)=ops[n*3:n*3+3]
  assert go==b'g' and ro==b're' and fo==b'f' and len(color)==1 and not empty
  x,y,w,h=map(int,rect);gray=int(color[0]);assert (w,h)==(12,12) and gray in [0,1]
  col=(x-32)//12;top_row=5-(y-40)//12
  assert x==32+col*12 and y==40+(5-top_row)*12 and 0<=col<6 and 0<=top_row<6
  assert gray==(col+top_row)%2;squares[(col,top_row)]=gray
 assert len(squares)==36
 assert [(list(a),o) for a,o in ops[-4:]]==[([],b'q'),([72,0,0,72,32,40],b'cm'),(['/Im'],b'Do'),([],b'Q')]
 actual_masked=set();decoded_only=set()
 for index,cell in enumerate(c['cells']):
  col=index%3;row=index//3;ident=f'cell-{col}-{row}';stored=list(expected_grid[index]);decoded=[v^255 for v in stored]
  assert cell['id']==ident and cell['stored_rgb']==stored and cell['decoded_rgb']==decoded
  # Reject a key match on any out-of-range STORED component; XOR complement is independent of generator subtraction.
  masked=key is not None and not any(v<key[2*k] or v>key[2*k+1] for k,v in enumerate(stored))
  decoded_match=key is not None and not any(v<key[2*k] or v>key[2*k+1] for k,v in enumerate(decoded))
  assert cell['masked']==masked and cell['decoded_key_match']==decoded_match;structural_mask_checks+=1
  if masked:actual_masked.add(ident)
  if decoded_match and not masked:decoded_only.add(ident)
 assert actual_masked==masked_map[c['id']] and decoded_only==decoded_only_map[c['id']]
 assert len(c['expected_samples'])==37 and len(c['expected_regions'])==37
 regions={q['id']:q for q in c['expected_regions']}
 for s in c['expected_samples']:
  if s['id']=='paper':assert s['point']==[12,12] and s['rgb']==[255]*3;continue
  _,col,row,quarter=s['id'].split('-');col=int(col);row=int(row)
  dx,dy,gray={'NW':(6,18,0),'NE':(18,18,1),'SW':(6,6,1),'SE':(18,6,0)}[quarter]
  point=[32+col*24+dx,40+(2-row)*24+dy];index=row*3+col;decoded=[v^255 for v in expected_grid[index]]
  masked=f'cell-{col}-{row}' in masked_map[c['id']];expected=[gray*255]*3 if masked else decoded
  assert s['point']==point and s['rgb']==expected and s['masked']==masked and s['background_rgb']==[gray*255]*3
  q=regions[s['id']];assert q['rect']==[point[0]-4,point[1]-4,8,8] and q['rgb']==expected and q['tolerance']==0
 assert c['association']['upstream_id'] is None and not c['association']['upstream_entry_validated']
assert structural_mask_checks==27
for row in r['rows']:
 f=R/row['file'];assert hashlib.sha256(f.read_bytes()).hexdigest()==row['sha256']
 c=next(c for c in m['cases'] if c['id']==row['id']);assert row['source_sha256']==c['sha256'];im=Image.open(f).convert('RGB')
 assert im.size==(c['width']*row['dpi']//72,c['height']*row['dpi']//72)
 for s,record in zip(c['expected_samples'],row['checks'],strict=True):
  actual=list(im.getpixel((int(s['point'][0]*row['dpi']/72),int((c['height']-s['point'][1])*row['dpi']/72))))
  assert actual==s['rgb']==record['actual'] and record['passed']
for f in (R/'logs').glob('*pdfjs.log'):
 d=json.loads(f.read_text().splitlines()[-1]);assert (d['pdfjs'],d['build'],d['canvasVersion'],d['node'])==('6.5.438','0a4153349','1.1.1','v24.22.3');assert not d['diagnostics']
assert len(list((R/'logs').glob('*pdfjs.log')))==6
print('Exactly3 endpoint PDFs /6DPI views /18 reference runs:18 passed,0 failed/skipped;27 stored-sample mask checks passed; non-endpoint holds remain separate.')
