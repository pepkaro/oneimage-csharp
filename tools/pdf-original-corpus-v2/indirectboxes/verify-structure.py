#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
from pathlib import Path
import json,hashlib
import pypdf
from pypdf import PdfReader
from pypdf.generic import ArrayObject,IndirectObject,NumberObject
R=Path(__file__).resolve().parent
assert pypdf.__version__=='6.21.4'
m=json.loads((R/'manifest.json').read_text());rows=[]
assert len(m['cases'])==3 and len({c['sha256'] for c in m['cases']})==3
for c in m['cases']:
 p=R/c['file'];assert hashlib.sha256(p.read_bytes()).hexdigest()==c['sha256'];doc=PdfReader(p,strict=True);assert len(doc.pages)==1;page=doc.pages[0];result={};raw_details={}
 for name,expected in [('/MediaBox',[0,0,220,180]),('/CropBox',[24,18,184,138])]:
  raw=page.raw_get(name);whole=isinstance(raw,IndirectObject);arr=raw.get_object();assert isinstance(arr,ArrayObject) and len(arr)==4
  elements=list(arr);refs=[isinstance(v,IndirectObject) for v in elements];resolved=[v.get_object() for v in elements];assert all(isinstance(v,NumberObject) for v in resolved);values=[int(v) for v in resolved];assert values==expected
  if c['box_form']=='direct':assert not whole and not any(refs)
  elif c['box_form']=='arrays':assert whole and not any(refs)
  elif c['box_form']=='coordinates':assert not whole and all(refs)
  else:raise AssertionError(c['box_form'])
  result[name]=values;raw_details[name]=dict(whole_array_indirect=whole,element_indirect=refs,whole_object_number=raw.idnum if whole else None,element_object_numbers=[v.idnum if isinstance(v,IndirectObject) else None for v in elements])
 media=result['/MediaBox'];crop=result['/CropBox'];assert all(media[k]<=crop[k] for k in [0,1]) and all(crop[k]<=media[k] for k in [2,3]);origin=crop[:2];size=[crop[2]-crop[0],crop[3]-crop[1]];assert origin==[24,18] and size==[160,120];assert c['width']==160 and c['height']==120
 assert '/Rotate' not in page and '/UserUnit' not in page and '/Annots' not in page
 assert '/MediaBox' not in page['/Parent'] and '/CropBox' not in page['/Parent'];assert not page['/Resources'];assert page.get_contents().get_data().endswith(b'195 30 15 90 re f\n')
 rows.append(dict(id=c['id'],fixture_id=c['fixture_id'],page=0,passed=True,resolved_boxes=result,raw_structure=raw_details,visible_origin=origin,visible_size=size))
(R/'structure-results.json').write_text(json.dumps(dict(passed=3,failed=0,rows=rows,independent_parser='pypdf6.21.4',claim='Raw reference shape and independently resolved numeric boxes, not renderer ownership'),indent=2)+'\n');print('3 independent raw/resolved page-box structure checks passed')
