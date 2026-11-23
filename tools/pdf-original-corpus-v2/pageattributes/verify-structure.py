#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Parse only original page-tree MediaBox bindings and vector operands, before flattening."""
from pathlib import Path
import json,hashlib,pypdf
from pypdf import PdfReader
from pypdf.generic import ContentStream
ROOT=Path(__file__).resolve().parent
assert pypdf.__version__=='6.21.4'

def main():
 m=json.loads((ROOT/'manifest.json').read_text());fixture_rows=[];rows=[]
 for fixture in m['fixtures']:
  src=ROOT/fixture['file'];assert hashlib.sha256(src.read_bytes()).hexdigest()==fixture['sha256'];reader=PdfReader(src,strict=True);pages=[];seen=set();nodes=[]
  def walk(ref,parent=None,effective=None):
   number=ref.idnum;assert number not in seen;seen.add(number);node=ref.get_object()
   if parent is None:assert '/Parent' not in node
   else:assert node.raw_get('/Parent').idnum==parent
   local=node.get('/MediaBox')
   if local is not None:effective=(number,[float(v) for v in local])
   assert effective is not None
   assert all(key not in node for key in ['/CropBox','/Rotate','/UserUnit'])
   if node['/Type']=='/Pages':
    count=sum(walk(child,number,effective) for child in node['/Kids']);assert count==node['/Count'];nodes.append(dict(object=number,count=count,has_local_media_box=local is not None));return count
   assert node['/Type']=='/Page' and len(node['/Resources'])==0;owner,media=effective;x0,y0,x1,y1=media;assert x1>x0 and y1>y0
   operations=ContentStream(node['/Contents'],reader).operations
   assert [op for _,op in operations]==[b'rg',b're',b'f',b'rg',b're',b'f']
   rects=[];color=None
   for operands,op in operations:
    if op==b'rg':color=[round(float(v)*255) for v in operands]
    if op==b're':x,y,w,h=map(float,operands);rects.append([x-x0,y-y0,w,h,color])
   pages.append(dict(page=len(pages),page_object=number,media_owner_object=owner,media_box=media,visible_width=x1-x0,visible_height=y1-y0,has_explicit_page_media_box=local is not None,transformed_rectangles=rects));return 1
  count=walk(reader.trailer['/Root'].raw_get('/Pages'));assert count==fixture['page_count'];fixture_rows.append(dict(fixture_id=fixture['id'],file=fixture['file'],page_count=count,page_tree_nodes=nodes,parsed_pages=pages))
  for case in [c for c in m['cases'] if c['fixture_id']==fixture['id']]:
   actual=pages[case['page']];assert actual['media_owner_object']==case['expected_media_owner_object'] and actual['media_box']==case['expected_media_box'];assert actual['visible_width']==case['width'] and actual['visible_height']==case['height'];assert actual['transformed_rectangles']==case['shape_rectangles'];assert actual['has_explicit_page_media_box']==(case['id']=='mediabox-explicit-page')
   rows.append(dict(id=case['id'],fixture_id=case['fixture_id'],file=case['file'],page=case['page'],passed=True,**{k:v for k,v in actual.items() if k!='page'}))
 result=dict(parser='pypdf',parser_version=pypdf.__version__,unique_pdfs=3,page_views=5,passed=len(rows),failed=0,fixtures=fixture_rows,rows=rows);assert len(rows)==5;(ROOT/'structure-results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['rows','fixtures']},indent=2))
if __name__=='__main__':main()
